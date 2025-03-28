"""
Tahmin algoritmalarını ve model istatistiklerini içeren modül.
"""
from config import GRID_SIZE
from models.adaptive_learning import AdaptiveLearningModel  # Yeni eklediğimiz modül

class PredictionModel:
    """Tahmin modellerini ve ilgili istatistikleri yöneten sınıf."""
    
    def __init__(self, grid_data=None):
        """
        Args:
            grid_data (list, optional): Grid verileri için referans.
        """
        self.grid_data = grid_data if grid_data else [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.adaptive_model = AdaptiveLearningModel()  # Yeni adaptif öğrenme modeli
        self.models = self._initialize_models()
    
    def _initialize_models(self):
        """Tahmin modellerini başlatır.
        
        Returns:
            list: Tahmin modellerinin listesi.
        """
        return [
            {'name': 'Sonu Takip', 'wins': 0, 'total': 0, 'accuracy': 0.0, 'predict_func': self.predict_follow_last},
            {'name': 'Tersi Takip', 'wins': 0, 'total': 0, 'accuracy': 0.0, 'predict_func': self.predict_follow_opposite},
            {'name': 'Hep Player', 'wins': 0, 'total': 0, 'accuracy': 0.0, 'predict_func': self.predict_always_player},
            {'name': 'Hep Banker', 'wins': 0, 'total': 0, 'accuracy': 0.0, 'predict_func': self.predict_always_banker},
            {'name': 'Basit Zigzag', 'wins': 0, 'total': 0, 'accuracy': 0.0, 'predict_func': self.predict_simple_zigzag},
            {'name': 'Grid 2x2', 'wins': 0, 'total': 0, 'accuracy': 0.0, 'predict_func': self.predict_grid_pattern_2x2},
            {'name': 'Grid 3x3', 'wins': 0, 'total': 0, 'accuracy': 0.0, 'predict_func': self.predict_grid_pattern_3x3},
            {'name': 'Veritabanı', 'wins': 0, 'total': 0, 'accuracy': 0.0, 'predict_func': None},  # DB tahmin işlevi dışarıdan atanacak
            {'name': 'Adaptif Öğr.', 'wins': 0, 'total': 0, 'accuracy': 0.0, 'predict_func': self.predict_adaptive},  # Yeni model
            {'name': 'Grid Adaptif', 'wins': 0, 'total': 0, 'accuracy': 0.0, 'predict_func': self.predict_grid_adaptive},  # Yeni grid tabanlı adaptif model
        ]
    
    def set_db_prediction_function(self, db_predict_func):
        """Veritabanı tahmin fonksiyonunu ayarlar.
        
        Args:
            db_predict_func (callable): Veritabanı tahmin fonksiyonu.
        """
        for model in self.models:
            if model['name'] == 'Veritabanı':
                model['predict_func'] = db_predict_func
                break
    
    def update_grid_data(self, grid_data):
        """Grid verilerini günceller.
        
        Args:
            grid_data (list): Yeni grid verileri.
        """
        self.grid_data = grid_data
    
    def get_predictions(self, history):
        """Tüm modeller için tahminleri döndürür.
        
        Args:
            history (list): Oyun geçmişi.
            
        Returns:
            dict: Model adı-tahmin çiftlerini içeren sözlük.
        """
        # Geçmiş kopyasını saklayalım (adaptif model için kullanacağız)
        self.history_snapshot = history.copy()
        
        predictions = {}
        for model in self.models:
            if model['predict_func']:
                predictions[model['name']] = model['predict_func'](history)
            else:
                predictions[model['name']] = '?'
        return predictions
    
    def get_best_model_prediction(self, history, min_predictions=5):
        """En yüksek doğruluk oranına sahip modelin tahminini döndürür.
        
        Args:
            history (list): Oyun geçmişi.
            min_predictions (int, optional): Minimum tahmin sayısı.
            
        Returns:
            str: Tahmin ('P', 'B' veya '?').
        """
        ranked_models = sorted(
            [m for m in self.models if m['total'] >= min_predictions],
            key=lambda m: m['accuracy'],
            reverse=True
        )
        
        if ranked_models:
            best_model = ranked_models[0]
            return best_model['predict_func'](history)
        
        # Yeterli veri yoksa varsayılan olarak son sonucu takip et
        return self.predict_follow_last(history)
    
    def update_model_accuracy(self, winner, predictions):
        """Model doğruluk oranlarını günceller.
        
        Args:
            winner (str): Gerçek sonuç ('P' veya 'B').
            predictions (dict): Model adı-tahmin çiftlerini içeren sözlük.
        """
        for model in self.models:
            model_pred = predictions.get(model['name'], '?')
            if model_pred != '?':
                model['total'] += 1
                if model_pred == winner:
                    model['wins'] += 1
                else:
                    # Adaptif model için hatalı tahmini kaydet
                    if model['name'] == 'Adaptif Öğr.':
                        self.adaptive_model.update_from_result(
                            self.history_snapshot.copy() if hasattr(self, 'history_snapshot') else [], 
                            model_pred, 
                            winner
                        )
                    # Grid Adaptif model için hatalı tahmini kaydet
                    elif model['name'] == 'Grid Adaptif' and self.grid_data:
                        for size in [3, 4, 5]:  # 3x3, 4x4, 5x5 grid desenleri
                            self.adaptive_model.record_grid_mistake(
                                self.grid_data,
                                size,
                                model_pred
                            )
                
                model['accuracy'] = (model['wins'] / model['total'] * 100) if model['total'] > 0 else 0.0
    
    def reset_models(self):
        """Model istatistiklerini sıfırlar."""
        self.models = self._initialize_models()
        if hasattr(self, 'adaptive_model'):
            self.adaptive_model.clear_memory()
    
    def close(self):
        """Kaynakları serbest bırakır."""
        if hasattr(self, 'adaptive_model'):
            self.adaptive_model.close()
    
    # Tahmin algoritmaları
    def predict_follow_last(self, current_history):
        """Son sonucu takip et.
        
        Args:
            current_history (list): Oyun geçmişi.
            
        Returns:
            str: Tahmin ('P', 'B' veya '?').
        """
        if not current_history:
            return '?'
        return current_history[-1]
    
    def predict_follow_opposite(self, current_history):
        """Son sonucun tersini takip et.
        
        Args:
            current_history (list): Oyun geçmişi.
            
        Returns:
            str: Tahmin ('P', 'B' veya '?').
        """
        if not current_history:
            return '?'
        last = current_history[-1]
        return 'B' if last == 'P' else 'P'
    
    def predict_always_player(self, current_history):
        """Her zaman Player tahmin et.
        
        Args:
            current_history (list): Oyun geçmişi.
            
        Returns:
            str: 'P'.
        """
        return 'P'
    
    def predict_always_banker(self, current_history):
        """Her zaman Banker tahmin et.
        
        Args:
            current_history (list): Oyun geçmişi.
            
        Returns:
            str: 'B'.
        """
        return 'B'
    
    def predict_simple_zigzag(self, current_history):
        """Basit zigzag tahmin stratejisi.
        
        Args:
            current_history (list): Oyun geçmişi.
            
        Returns:
            str: 'P' veya 'B'.
        """
        n = len(current_history)
        return 'P' if n % 2 == 0 else 'B'
    
    def _check_grid_square(self, size):
        """Grid içinde belirli bir boyutta kare desenini kontrol eder.
        
        Args:
            size (int): Kare boyutu.
            
        Returns:
            str: Desen değeri ('P', 'B' veya None).
        """
        start_row = GRID_SIZE - size
        start_col = GRID_SIZE - size
        
        if start_row < 0 or start_col < 0:
            return None
        
        try:
            first_val = self.grid_data[start_row][start_col]
            if first_val is None:
                return None
                
            for r in range(start_row, GRID_SIZE):
                for c in range(start_col, GRID_SIZE):
                    # Grid verisinin geçerliliğini kontrol et
                    if r >= len(self.grid_data) or c >= len(self.grid_data[r]) or self.grid_data[r][c] != first_val:
                        return None
            
            return first_val
        except IndexError:
            return None
    
    def predict_grid_pattern_2x2(self, current_history):
        """2x2 grid deseni tahmini.
        
        Args:
            current_history (list): Oyun geçmişi.
            
        Returns:
            str: Tahmin ('P', 'B' veya '?').
        """
        pattern = self._check_grid_square(2)
        return pattern if pattern else '?'
    
    def predict_grid_pattern_3x3(self, current_history):
        """3x3 grid deseni tahmini.
        
        Args:
            current_history (list): Oyun geçmişi.
            
        Returns:
            str: Tahmin ('P', 'B' veya '?').
        """
        pattern = self._check_grid_square(3)
        return pattern if pattern else '?'
    
    def predict_adaptive(self, current_history):
        """Adaptif öğrenme modelinden tahmin alır.
        
        Args:
            current_history (list): Oyun geçmişi.
            
        Returns:
            str: Tahmin ('P', 'B' veya '?').
        """
        return self.adaptive_model.predict(current_history)
    
    def predict_grid_adaptive(self, current_history):
        """Grid tabanlı adaptif öğrenme modelinden tahmin alır.
        
        Args:
            current_history (list): Oyun geçmişi.
            
        Returns:
            str: Tahmin ('P', 'B' veya '?').
        """
        # Önce 3x3 deseni dene
        pred_3x3 = self.adaptive_model.predict_from_grid(self.grid_data, 3)
        if pred_3x3 != '?':
            return pred_3x3
            
        # Sonra 4x4 ve 5x5 dene
        for size in [4, 5]:
            pred = self.adaptive_model.predict_from_grid(self.grid_data, size)
            if pred != '?':
                return pred
        
        # Grid desenine dayalı tahmin yoksa adaptif model kullan
        return self.adaptive_model.predict(current_history)