"""
Bu güncellenmiş DatabaseManager sınıfı, yeni shoe tespitini işleyebilir
ve shoe değişimlerini veritabanında izler.
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
        self.current_shoe_id = 1  # Mevcut shoe ID'sini sakla
        self._initialize_database()
        self._load_current_shoe_id()
    
    def _initialize_database(self):
        """Veritabanını başlatır ve gerekli tabloları oluşturur."""
        try:
            self.connection = sqlite3.connect(DB_FILE)
            cursor = self.connection.cursor()
            
            # Sonuçlar tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    shoe_id INTEGER NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    winner TEXT NOT NULL
                )
            ''')
            
            # Shoe takip tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS shoe_tracker (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    shoe_id INTEGER NOT NULL UNIQUE
                )
            ''')
            
            self.connection.commit()
            print(f"Veritabanı '{DB_FILE}' başarıyla başlatıldı.")
        except sqlite3.Error as e:
            print(f"Veritabanı hatası: {e}")
            self.connection = None
    
    def _load_current_shoe_id(self):
        """Veritabanından mevcut shoe ID'sini yükler."""
        if not self.connection:
            return
            
        try:
            cursor = self.connection.cursor()
            
            # En son shoe ID'sini al
            cursor.execute("SELECT MAX(shoe_id) FROM shoe_tracker")
            result = cursor.fetchone()
            
            if result and result[0] is not None:
                self.current_shoe_id = result[0]
                print(f"Mevcut shoe ID: {self.current_shoe_id}")
            else:
                # İlk shoe kaydını oluştur
                self._create_new_shoe_record()
                
        except sqlite3.Error as e:
            print(f"Shoe ID yükleme hatası: {e}")
    
    def _create_new_shoe_record(self):
        """Yeni bir shoe kaydı oluşturur."""
        if not self.connection:
            return
            
        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO shoe_tracker (shoe_id) VALUES (?)", 
                          (self.current_shoe_id,))
            self.connection.commit()
            print(f"Yeni shoe kaydı oluşturuldu, ID: {self.current_shoe_id}")
        except sqlite3.Error as e:
            print(f"Yeni shoe kaydı oluşturma hatası: {e}")
    
    def new_shoe_detected(self):
        """Yeni shoe tespiti durumunda çağrılır, shoe ID'sini artırır."""
        self.current_shoe_id += 1
        self._create_new_shoe_record()
        print(f"Yeni shoe başladı! Shoe ID: {self.current_shoe_id}")
        
        # Tampon temizleme - yeni shoe için yeni işlemlere başla
        self.write_buffer.clear()
    
    def add_result(self, winner):
        """Sonucu veritabanı tamponuna ekler.
        
        Args:
            winner (str): Kazananı temsil eden 'P' veya 'B' değeri.
        """
        if not self.connection:
            return
        # Shoe ID ile birlikte sonucu tampona ekle
        self.write_buffer.append((self.current_shoe_id, winner))
    
    def flush_buffer(self):
        """Tamponlanmış sonuçları veritabanına yazar."""
        if not self.connection or not self.write_buffer:
            return
        try:
            cursor = self.connection.cursor()
            cursor.executemany("INSERT INTO results (shoe_id, winner) VALUES (?, ?)", self.write_buffer)
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
            
            # Sadece MEVCUT shoe_id için tahmin yap
            cursor.execute("""
                SELECT winner FROM results 
                WHERE shoe_id = ? 
                ORDER BY id
            """, (self.current_shoe_id,))
            
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
    
    def clear_current_shoe_data(self):
        """Sadece mevcut shoe için verileri temizler."""
        if not self.connection:
            return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM results WHERE shoe_id = ?", (self.current_shoe_id,))
            self.connection.commit()
            print(f"Shoe ID {self.current_shoe_id} için veriler temizlendi.")
            return True
        except sqlite3.Error as e:
            print(f"DB Temizleme Hatası: {e}")
            return False
    
    def clear_table(self):
        """Veritabanındaki results tablosunu temizler."""
        if not self.connection:
            return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM results")
            cursor.execute("DELETE FROM shoe_tracker")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='results'")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='shoe_tracker'")
            self.connection.commit()
            
            # Shoe ID'yi sıfırla
            self.current_shoe_id = 1
            self._create_new_shoe_record()
            
            print("Tüm tablolar temizlendi ve yeni shoe oluşturuldu.")
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