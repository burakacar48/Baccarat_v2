"""
AdaptiveLearningModel için shoe takibi iyileştirmesi.
Bu değişiklikler, farklı shoe'larda yapılan hataları ayrı şekilde izleyecektir.
"""

import sqlite3
from collections import Counter, defaultdict
from config import DB_FILE

class AdaptiveLearningModel:
    """Hatalı tahminlerden öğrenen tahmin modeli."""
    
    def __init__(self, lookback=4):
        """
        Args:
            lookback (int): Dikkate alınacak önceki sonuç sayısı.
        """
        self.lookback = lookback
        self.connection = None
        self.current_shoe_id = 1
        self._initialize_database()
        self.mistake_memory = defaultdict(Counter)  # Hataları saklayacak hafıza yapısı
        self._load_mistake_memory()
    
    def _initialize_database(self):
        """Veritabanı bağlantısını ve gerekli tabloları başlatır."""
        try:
            self.connection = sqlite3.connect(DB_FILE)
            cursor = self.connection.cursor()
            
            # Tahmin hafızası tablosu - shoe_id eklenmiş
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS adaptive_learning (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    shoe_id INTEGER NOT NULL,
                    pattern TEXT NOT NULL,
                    wrong_prediction TEXT NOT NULL,
                    frequency INTEGER DEFAULT 1,
                    UNIQUE(shoe_id, pattern, wrong_prediction)
                )
            ''')
            
            # Grid tabanlı hata desenler tablosu - shoe_id eklenmiş
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS grid_mistake_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    shoe_id INTEGER NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    grid_pattern TEXT NOT NULL,   
                    grid_size INTEGER NOT NULL,   
                    wrong_prediction TEXT NOT NULL,
                    frequency INTEGER DEFAULT 1,
                    UNIQUE(shoe_id, grid_pattern, grid_size, wrong_prediction)
                )
            ''')
            
            # İndeksler
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_pattern ON adaptive_learning(shoe_id, pattern)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_grid_pattern ON grid_mistake_patterns(shoe_id, grid_pattern, grid_size)')
            
            self.connection.commit()
            print("Adaptif öğrenme tablosu başarıyla başlatıldı.")
        except sqlite3.Error as e:
            print(f"Veritabanı hatası: {e}")
            self.connection = None
    
    def _load_mistake_memory(self):
        """Veritabanından hata hafızasını yükler."""
        if not self.connection:
            return
            
        try:
            cursor = self.connection.cursor()
            
            # Mevcut shoe_id değerini veritabanından al
            cursor.execute("SELECT MAX(shoe_id) FROM shoe_tracker")
            result = cursor.fetchone()
            if result and result[0] is not None:
                self.current_shoe_id = result[0]
            
            # Mevcut shoe için hata kayıtlarını yükle
            cursor.execute("""
                SELECT pattern, wrong_prediction, frequency 
                FROM adaptive_learning
                WHERE shoe_id = ?
            """, (self.current_shoe_id,))
            
            results = cursor.fetchall()
            
            for pattern, wrong_pred, freq in results:
                self.mistake_memory[pattern][wrong_pred] = freq
                
            print(f"Shoe ID {self.current_shoe_id} için {len(results)} hata kaydı hafızaya yüklendi.")
        except sqlite3.Error as e:
            print(f"Hata hafızası yükleme hatası: {e}")
    
    def set_shoe_id(self, shoe_id):
        """Mevcut shoe ID'sini ayarlar ve hafızayı yeniden yükler.
        
        Args:
            shoe_id (int): Yeni shoe ID'si.
        """
        if self.current_shoe_id == shoe_id:
            return  # Değişiklik yok, işlem yapma
            
        self.current_shoe_id = shoe_id
        # Hafızayı temizle ve yeni shoe için hafızayı yükle
        self.mistake_memory.clear()
        self._load_mistake_memory()
        print(f"Adaptif öğrenme modeli için shoe ID {shoe_id} olarak ayarlandı.")
    
    def predict(self, history):
        """Mevcut durum için tahmin üretir.
        
        Args:
            history (list): Oyun geçmişi.
            
        Returns:
            str: Tahmin edilen değer ('P' veya 'B').
        """
        if len(history) < self.lookback:
            return '?'
            
        # Son N sonucu al
        pattern = "".join(history[-self.lookback:])
        
        # Bu desen için yapılan hataları kontrol et
        mistake_counter = self.mistake_memory.get(pattern, Counter())
        
        if not mistake_counter:
            return '?'  # Henüz bu desen için hata kaydı yok
        
        # En çok hata yapılan tahmini bul
        most_common_mistake = mistake_counter.most_common(1)[0][0]
        
        # Yanlış olduğunu öğrendiğimiz tahminin tersini yap
        return 'B' if most_common_mistake == 'P' else 'P'
    
    def record_mistake(self, pattern, wrong_prediction):
        """Yapılan tahmin hatasını kaydeder.
        
        Args:
            pattern (str): Hatanın yapıldığı durum/desen.
            wrong_prediction (str): Yanlış tahmin ('P' veya 'B').
        """
        # Hafızaya kaydet
        self.mistake_memory[pattern][wrong_prediction] += 1
        
        # Veritabanına kaydet
        if not self.connection:
            return
            
        try:
            cursor = self.connection.cursor()
            
            # Varsa güncelle, yoksa ekle
            cursor.execute("""
                INSERT INTO adaptive_learning (shoe_id, pattern, wrong_prediction, frequency)
                VALUES (?, ?, ?, 1)
                ON CONFLICT(shoe_id, pattern, wrong_prediction) 
                DO UPDATE SET frequency = frequency + 1
            """, (self.current_shoe_id, pattern, wrong_prediction))
            
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Hata kaydı yazma hatası: {e}")
    
    def update_from_result(self, history, prediction, actual_result):
        """Tahmin sonucuna göre modeli günceller.
        
        Args:
            history (list): Tahmin anındaki oyun geçmişi.
            prediction (str): Yapılan tahmin ('P' veya 'B').
            actual_result (str): Gerçekleşen sonuç ('P' veya 'B').
        """
        if len(history) < self.lookback or prediction == '?':
            return
            
        # Tahmin yanlışsa kaydet
        if prediction != actual_result:
            pattern = "".join(history[-self.lookback:])
            self.record_mistake(pattern, prediction)
    
    def record_grid_mistake(self, grid_data, grid_size, wrong_prediction):
        """Grid deseninde yapılan hatayı kaydeder.
        
        Args:
            grid_data (list): Grid verisi.
            grid_size (int): Grid boyutu (3, 4, 5 vb.).
            wrong_prediction (str): Yanlış tahmin ('P' veya 'B').
        """
        if not self.connection:
            return
            
        # Grid desenini düzleştir
        pattern = self._flatten_grid(grid_data, grid_size)
        
        try:
            cursor = self.connection.cursor()
            
            # Varsa güncelle, yoksa ekle
            cursor.execute("""
                INSERT INTO grid_mistake_patterns 
                (shoe_id, grid_pattern, grid_size, wrong_prediction, frequency)
                VALUES (?, ?, ?, ?, 1)
                ON CONFLICT(shoe_id, grid_pattern, grid_size, wrong_prediction) 
                DO UPDATE SET frequency = frequency + 1
            """, (self.current_shoe_id, pattern, grid_size, wrong_prediction))
            
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Grid hatası kaydetme hatası: {e}")
    
    def _flatten_grid(self, grid_data, size):
        """Grid'i dizi olarak düzleştirir.
        
        Args:
            grid_data (list): 2D grid.
            size (int): Grid boyutu.
            
        Returns:
            str: Düzleştirilmiş grid.
        """
        result = ""
        rows = len(grid_data)
        cols = len(grid_data[0]) if rows > 0 else 0
        
        # Sağ alt köşeden grid'i al
        for r in range(max(0, rows - size), rows):
            for c in range(max(0, cols - size), cols):
                if r < rows and c < cols and grid_data[r][c] is not None:
                    result += grid_data[r][c]
                else:
                    result += "X"
        
        return result
    
    def predict_from_grid(self, grid_data, grid_size=3):
        """Grid desenine göre tahmin yapar.
        
        Args:
            grid_data (list): Grid verisi.
            grid_size (int): Grid boyutu.
            
        Returns:
            str: Tahmin edilen değer ('P' veya 'B').
        """
        if not self.connection:
            return '?'
            
        pattern = self._flatten_grid(grid_data, grid_size)
        
        try:
            cursor = self.connection.cursor()
            
            # En çok hata yapılan tahmini bul
            cursor.execute("""
                SELECT wrong_prediction, SUM(frequency) as total_freq
                FROM grid_mistake_patterns
                WHERE shoe_id = ? AND grid_pattern = ? AND grid_size = ?
                GROUP BY wrong_prediction
                ORDER BY total_freq DESC
                LIMIT 1
            """, (self.current_shoe_id, pattern, grid_size))
            
            result = cursor.fetchone()
            if result:
                wrong_prediction = result[0]
                # Yanlış olduğunu öğrendiğimiz tahminin tersini yap
                return 'B' if wrong_prediction == 'P' else 'P'
            
            return '?'
        except sqlite3.Error as e:
            print(f"Grid tahmin hatası: {e}")
            return '?'
    
    def clear_memory(self):
        """Hata hafızasını temizler."""
        self.mistake_memory.clear()
        
        if not self.connection:
            return
            
        try:
            cursor = self.connection.cursor()
            # Sadece mevcut shoe için temizle
            cursor.execute("DELETE FROM adaptive_learning WHERE shoe_id = ?", (self.current_shoe_id,))
            cursor.execute("DELETE FROM grid_mistake_patterns WHERE shoe_id = ?", (self.current_shoe_id,))
            self.connection.commit()
            print(f"Shoe ID {self.current_shoe_id} için adaptif öğrenme hafızası temizlendi.")
        except sqlite3.Error as e:
            print(f"Hafıza temizleme hatası: {e}")
    
    def close(self):
        """Veritabanı bağlantısını kapatır."""
        if self.connection:
            self.connection.close()
            print("Adaptif öğrenme veritabanı bağlantısı kapatıldı.")