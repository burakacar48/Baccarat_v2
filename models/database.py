"""
Veritabanı işlemlerini yöneten modül.
Bu modül, SQLite veritabanı bağlantısını ve ilgili işlemleri yönetir.
"""
import sqlite3
import time
from collections import Counter
from config import DB_FILE, DB_LOOKBACK

class DatabaseManager:
    """Veritabanı bağlantısını ve işlemlerini yöneten sınıf."""
    
    def __init__(self):
        """Veritabanı bağlantısını başlatır."""
        self.connection = None
        self.write_buffer = []
        self._initialize_database()
    
    def _initialize_database(self):
        """Veritabanını başlatır ve gerekli tabloları oluşturur."""
        try:
            self.connection = sqlite3.connect(DB_FILE)
            cursor = self.connection.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    winner TEXT NOT NULL
                )
            ''')
            self.connection.commit()
            print(f"Veritabanı '{DB_FILE}' başarıyla başlatıldı.")
        except sqlite3.Error as e:
            print(f"Veritabanı hatası: {e}")
            self.connection = None
    
    def add_result(self, winner):
        """Sonucu veritabanı tamponuna ekler.
        
        Args:
            winner (str): Kazananı temsil eden 'P' veya 'B' değeri.
        """
        if not self.connection:
            return
        self.write_buffer.append((winner,))
    
    def flush_buffer(self):
        """Tamponlanmış sonuçları veritabanına yazar."""
        if not self.connection or not self.write_buffer:
            return
        try:
            cursor = self.connection.cursor()
            cursor.executemany("INSERT INTO results (winner) VALUES (?)", self.write_buffer)
            self.connection.commit()
            self.write_buffer.clear()
        except sqlite3.Error as e:
            print(f"DB Yazma Hatası: {e}")
    
    def predict_from_history(self, current_sequence):
        """Veritabanındaki geçmiş verilerine göre tahmin yapar.
        
        Args:
            current_sequence (list): Mevcut sonuç dizisi.
            
        Returns:
            str: Tahmin edilen değer ('P', 'B' veya '?').
        """
        if not self.connection or len(current_sequence) < DB_LOOKBACK:
            return '?'
        
        lookup_sequence = "".join(current_sequence[-DB_LOOKBACK:])
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT winner FROM results ORDER BY id")
            all_results = [row[0] for row in cursor.fetchall()]
            
            if len(all_results) <= DB_LOOKBACK:
                return '?'
            
            next_outcomes = []
            for i in range(len(all_results) - DB_LOOKBACK):
                current_seq = "".join(all_results[i: i + DB_LOOKBACK])
                if current_seq == lookup_sequence:
                    next_outcome = all_results[i + DB_LOOKBACK]
                    next_outcomes.append(next_outcome)
            
            if not next_outcomes:
                return '?'
                
            most_common = Counter(next_outcomes).most_common(1)
            return most_common[0][0] if most_common else '?'
            
        except sqlite3.Error as e:
            print(f"DB Okuma Hatası: {e}")
            return '?'
        except Exception as e:
            print(f"DB Tahmin Hatası: {e}")
            return '?'
    
    def clear_table(self):
        """Veritabanındaki results tablosunu temizler."""
        if not self.connection:
            return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM results")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='results'")
            self.connection.commit()
            print("'results' tablosu temizlendi.")
            return True
        except sqlite3.Error as e:
            print(f"DB Temizleme Hatası: {e}")
            return False
    
    def close(self):
        """Veritabanı bağlantısını kapatır."""
        self.flush_buffer()
        if self.connection:
            self.connection.close()
            print("Veritabanı bağlantısı kapatıldı.")
