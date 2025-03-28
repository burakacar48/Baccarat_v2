"""
Tahmin algoritmalarını ve model istatistiklerini içeren modül.
"""
from config import GRID_SIZE
from models.adaptive_learning import AdaptiveLearningModel
from models.enhanced_wl_prediction import EnhancedWLPredictionModel

class PredictionModel:
    """Tahmin modellerini ve ilgili istatistikleri yöneten sınıf."""
    
    def __init__(self, grid_data=None):
        """
        Args:
            grid_data (list, optional): Grid verileri için referans.
        """
        self.grid_data = grid_data if grid_data else [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.adaptive_model = AdaptiveLearningModel()
        self.wl_model = EnhancedWLPredictionModel(lookback_pairs=5)  # Geliştirilmiş WL tahmin modeli
        self.models = self._initialize_models()
        self.current_wl_prediction = '?'
        self.current_horizontal_wl_pred = '?' 
        self.current_vertical_wl_pred = '?'
        self.should_reverse_bet = False
    
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
            {'name': 'Adaptif Öğr.', 'wins': 0, 'total': 0, 'accuracy': 0.0, 'predict_func': self.predict_adaptive},
            {'name': 'Grid Adaptif', 'wins': 0, 'total': 0, 'accuracy': 0.0, 'predict_func': self.predict_grid_adaptive},
            {'name': 'WL Tersine', 'wins': 0, 'total': 0, 'accuracy': 0.0, 'predict_func': self.predict_wl_reverse},
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
    
    def get_predictions(self, history, wl_history=None):
        """Tüm modeller için tahminleri döndürür.
        
        Args:
            history (list): Oyun geçmişi.
            wl_history (list, optional): Kazanç/kayıp geçmişi.
            
        Returns:
            dict: Model adı-tahmin çiftlerini içeren sözlük.
        """
        # Geçmiş kopyasını saklayalım (adaptif model için kullanacağız)
        self.history_snapshot = history.copy()
        
        # WL tahmini yap (geliştirilmiş model kullanılıyor)
        if wl_history:
            should_reverse, wl_pred, h_pred, v_pred = self.wl_model.should_reverse_bet(wl_history, None)
            self.should_reverse_bet = should_reverse
            self.current_wl_prediction = wl_pred
            self.current_horizontal_wl_pred = h_pred
            self.current_vertical_wl_pred = v_pred
        
        predictions = {}
        for model in self.models:
            if model['predict_func']:
                predictions[model['name']] = model['predict_func'](history)
            else:
                predictions[model['name']] = '?'
        return predictions
    
    def get_best_model_prediction(self, history, wl_history=None, min_predictions=5):
        """En yüksek doğruluk oranına sahip modelin tahminini döndürür.
        
        Args:
            history (list): Oyun geçmişi.
            wl_history (list, optional): Kazanç/kayıp geçmişi.
            min_predictions (int, optional): Minimum tahmin sayısı.
            
        Returns:
            tuple: (tahmin, ters_bahis_yapılmalı) - Tahmin ('P', 'B' veya '?') ve ters bahis yapılıp yapılmayacağı.
        """
        # WL tahmini güncelle
        if wl_history:
            best_model_pred = None
            
            # En iyi modeli bul
            ranked_models = sorted(
                [m for m in self.models if m['total'] >= min_predictions],
                key=lambda m: m['accuracy'],
                reverse=True
            )
            
            if ranked_models:
                best_model = ranked_models[0]
                best_model_pred = best_model['predict_func'](history)
            else:
                # Yeterli veri yoksa varsayılan olarak son sonucu takip et
                best_model_pred = self.predict_follow_last(history)
            
            should_reverse, wl_pred, h_pred, v_pred = self.wl_model.should_reverse_bet(wl_history, best_model_pred)
            self.should_reverse_bet = should_reverse
            self.current_wl_prediction = wl_pred
            self.current_horizontal_wl_pred = h_pred
            self.current_vertical_wl_pred = v_pred
            
            # Ters bahis yapılacaksa tahminimizi tersine çevir
            if should_reverse and best_model_pred != '?':
                reversed_pred = 'P' if best_model_pred == 'B' else 'B'
                return reversed_pred, True
            
            return best_model_pred, False
        
        # WL geçmişi yoksa normal tahmin yap
        ranked_models = sorted(
            [m for m in self.models if m['total'] >= min_predictions],
            key=lambda m: m['accuracy'],
            reverse=True
        )
        
        if ranked_models:
            best_model = ranked_models[0]
            return best_model['predict_func'](history), False
        
        # Yeterli veri yoksa varsayılan olarak son sonucu takip et
        return self.predict_follow_last(history), False
    
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
        self.current_wl_prediction = '?'
        self.current_horizontal_wl_pred = '?'
        self.current_vertical_wl_pred = '?'
        self.should_reverse_bet = False
    
    def close(self):
        """Kaynakları serbest bırakır."""
        if hasattr(self, 'adaptive_model'):
            self.adaptive_model.close()
    
    def update_wl_weights(self, h_accuracy, v_accuracy):
        """WL tahmin ağırlıklarını günceller.
        
        Args:
            h_accuracy (float): Yatay tahmin doğruluk oranı.
            v_accuracy (float): Dikey tahmin doğruluk oranı.
        """
        if hasattr(self, 'wl_model') and hasattr(self.wl_model, 'update_weights'):
            self.wl_model.update_weights(h_accuracy/100.0, v_accuracy/100.0)
    
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
    
    def predict_wl_reverse(self, current_history):
        """WL modeline göre tersine tahmin yapar.
        
        Args:
            current_history (list): Oyun geçmişi.
            
        Returns:
            str: Tahmin ('P', 'B' veya '?').
        """
        # Eğer normal tahminimiz ve WL tahmini varsa
        if hasattr(self, 'current_wl_prediction') and self.current_wl_prediction == 'L':
            # En iyi modelin tahmininin tersini al
            ranked_models = sorted(
                [m for m in self.models if m['name'] != 'WL Tersine' and m['total'] > 0],
                key=lambda m: m['accuracy'],
                reverse=True
            )
            
            if ranked_models:
                best_model = ranked_models[0]
                best_pred = best_model['predict_func'](current_history)
                
                if best_pred != '?':
                    return 'P' if best_pred == 'B' else 'B'
        
        return '?'
    
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
    
    def _check_grid_pattern(self, size):
        """Esnek grid desen algılama.
        
        Args:
            size (int): Kare boyutu.
            
        Returns:
            str: Çoğunluk değeri ('P', 'B' veya None).
        """
        start_row = GRID_SIZE - size
        start_col = GRID_SIZE - size
        
        if start_row < 0 or start_col < 0:
            return None
        
        # Desenin kaç P ve B içerdiğini say
        p_count = 0
        b_count = 0
        empty_count = 0
        
        for r in range(start_row, GRID_SIZE):
            for c in range(start_col, GRID_SIZE):
                if r >= len(self.grid_data) or c >= len(self.grid_data[r]):
                    return None
                    
                val = self.grid_data[r][c]
                if val == 'P':
                    p_count += 1
                elif val == 'B':
                    b_count += 1
                else:
                    empty_count += 1
        
        # Eğer boş hücre yoksa ve bir değer baskınsa
        total_cells = size * size
        threshold = total_cells * 0.75  # %75 eşik değeri
        
        if empty_count == 0:
            if p_count >= threshold:
                return 'P'
            elif b_count >= threshold:
                return 'B'
        
        return None
    
    def _check_line_pattern(self, length):
        """Yatay ve dikey çizgilerde desen arar.
        
        Args:
            length (int): Çizgi uzunluğu.
            
        Returns:
            str: Çizgi değeri ('P', 'B' veya None).
        """
        # Yatay çizgileri kontrol et
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE - length + 1):
                first_val = self.grid_data[r][c]
                if first_val is None:
                    continue
                    
                all_same = True
                for i in range(1, length):
                    if self.grid_data[r][c+i] != first_val:
                        all_same = False
                        break
                
                if all_same:
                    return first_val
        
        # Dikey çizgileri kontrol et
        for c in range(GRID_SIZE):
            for r in range(GRID_SIZE - length + 1):
                first_val = self.grid_data[r][c]
                if first_val is None:
                    continue
                    
                all_same = True
                for i in range(1, length):
                    if self.grid_data[r+i][c] != first_val:
                        all_same = False
                        break
                
                if all_same:
                    return first_val
        
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
        # Sıkı kare desen kontrolü
        pattern = self._check_grid_square(3)
        if pattern:
            return 'B' if pattern == 'P' else 'P'  # Tersini tahmin et
            
        # Esnek desen kontrolü
        flexible_pattern = self._check_grid_pattern(3)
        if flexible_pattern:
            return 'B' if flexible_pattern == 'P' else 'P'  # Tersini tahmin et
            
        # Çizgi desen kontrolü
        line_pattern = self._check_line_pattern(4)  # 4 uzunluğunda çizgi
        if line_pattern:
            return 'B' if line_pattern == 'P' else 'P'  # Tersini tahmin et
        
        return '?'
    
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