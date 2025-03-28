"""
Geliştirilmiş Win/Loss pattern prediction module.
Bu modül hem yatay hem de dikey win/loss desenlerini analiz ederek daha başarılı tahminler üretir.
"""
from collections import Counter

class EnhancedWLPredictionModel:
    """Yatay ve dikey win/loss desenlerini analiz eden tahmin modeli."""
    
    def __init__(self, lookback_pairs=5, grid_rows=12, grid_cols=2):
        """
        Args:
            lookback_pairs (int): Patern eşleştirmede geriye doğru bakılacak çift sayısı.
            grid_rows (int): WL ızgara satır sayısı.
            grid_cols (int): WL ızgara sütun sayısı.
        """
        self.lookback_pairs = lookback_pairs
        self.grid_rows = grid_rows
        self.grid_cols = grid_cols
        self.horizontal_weight = 0.6  # Yatay tahmin ağırlığı
        self.vertical_weight = 0.4    # Dikey tahmin ağırlığı
        self.last_horizontal_pred = '?'
        self.last_vertical_pred = '?'
        
    def predict_horizontal(self, wl_history):
        """
        Yatay (kronolojik) win/loss desenlerini analiz ederek tahmin yapar.
        
        Args:
            wl_history (list): 'W' ve 'L' değerlerinden oluşan kazanç/kayıp geçmişi.
            
        Returns:
            str: Tahmin edilen değer ('W', 'L' veya '?').
        """
        if len(wl_history) < 2:
            return '?'
        
        # Çiftleri çıkar
        pairs = []
        for i in range(0, len(wl_history) - 1, 2):
            if i + 1 < len(wl_history):
                pairs.append(wl_history[i] + wl_history[i + 1])
        
        # Yetersiz çift varsa bilinmeyen döndür
        if len(pairs) < 2:
            return '?'
        
        # Son çiftleri al (lookback sınırına göre)
        recent_pairs = pairs[-min(self.lookback_pairs, len(pairs)):]
        
        # Her patern için sonraki sonucu say
        patterns = Counter()
        for i in range(len(recent_pairs) - 1):
            current_pair = recent_pairs[i]
            next_result = recent_pairs[i + 1][0]  # Sonraki çiftin ilk elemanı
            patterns[current_pair + next_result] += 1
        
        # Son çifti al ve tahmin yap
        last_pair = recent_pairs[-1]
        
        # Bu çiftten sonra en sık gelen sonucu bul
        best_prediction = '?'
        highest_count = 0
        
        for pattern, count in patterns.items():
            if pattern.startswith(last_pair) and count > highest_count:
                highest_count = count
                if len(pattern) > 2:
                    best_prediction = pattern[2]
        
        # Patern bulunamadıysa veya zayıf patern bulunduysa basit strateji kullan
        if best_prediction == '?' or highest_count <= 1:
            # Son sonucun tersini tahmin et
            if len(last_pair) > 1:
                return 'W' if last_pair[-1] == 'L' else 'L'
            elif len(wl_history) > 0:
                return 'W' if wl_history[-1] == 'L' else 'L'
        
        # Son yatay tahmini sakla
        self.last_horizontal_pred = best_prediction
        return best_prediction
    
    def predict_vertical(self, wl_history):
        """
        Dikey (grid formatında) win/loss desenlerini analiz ederek tahmin yapar.
        
        Args:
            wl_history (list): 'W' ve 'L' değerlerinden oluşan kazanç/kayıp geçmişi.
            
        Returns:
            str: Tahmin edilen değer ('W', 'L' veya '?').
        """
        if len(wl_history) < self.grid_cols * 2:
            return '?'
        
        # Son veriyi grid formatına dönüştür
        max_elements = min(len(wl_history), self.grid_rows * self.grid_cols)
        recent_history = wl_history[-max_elements:]
        
        # Grid oluştur
        grid = []
        for r in range(self.grid_rows):
            row = []
            for c in range(self.grid_cols):
                idx = r * self.grid_cols + c
                if idx < len(recent_history):
                    row.append(recent_history[idx])
                else:
                    row.append(None)
            grid.append(row)
        
        # Dikey desenleri analiz et
        column_patterns = []
        for c in range(self.grid_cols):
            col_values = [grid[r][c] for r in range(self.grid_rows) if grid[r][c] is not None]
            if len(col_values) >= 3:  # En az 3 eleman olan sütunları analiz et
                column_patterns.append(col_values)
        
        if not column_patterns:
            return '?'
        
        # Her sütun için son 3 elemanın desenini kontrol et ve tahmin yap
        predictions = []
        for col in column_patterns:
            if len(col) >= 3:
                last_three = col[-3:]
                
                # Tüm elemanlar aynıysa tersini tahmin et
                if all(x == 'W' for x in last_three):
                    predictions.append('L')
                elif all(x == 'L' for x in last_three):
                    predictions.append('W')
                # Alternatif desen: W-L-W -> L tahmin et, L-W-L -> W tahmin et
                elif last_three == ['W', 'L', 'W']:
                    predictions.append('L')
                elif last_three == ['L', 'W', 'L']:
                    predictions.append('W')
                # Son iki eleman aynıysa, devam edeceğini tahmin et
                elif last_three[-2:] == ['W', 'W']:
                    predictions.append('W')
                elif last_three[-2:] == ['L', 'L']:
                    predictions.append('L')
                # Son iki eleman farklıysa, alternatif devam edecek
                elif last_three[-2:] == ['W', 'L']:
                    predictions.append('W')
                elif last_three[-2:] == ['L', 'W']:
                    predictions.append('L')
        
        if not predictions:
            return '?'
        
        # En çok tahmin edilen sonucu döndür
        result = Counter(predictions).most_common(1)[0][0]
        
        # Son dikey tahmini sakla
        self.last_vertical_pred = result
        return result
    
    def predict(self, wl_history):
        """
        Hem yatay hem dikey desenleri analiz ederek ağırlıklı bir tahmin yapar.
        
        Args:
            wl_history (list): 'W' ve 'L' değerlerinden oluşan kazanç/kayıp geçmişi.
            
        Returns:
            str: Tahmin edilen değer ('W', 'L' veya '?').
        """
        horizontal_pred = self.predict_horizontal(wl_history)
        vertical_pred = self.predict_vertical(wl_history)
        
        # Eğer tahminlerden biri belirsizse, diğerini döndür
        if horizontal_pred == '?':
            return vertical_pred
        if vertical_pred == '?':
            return horizontal_pred
        
        # İki tahmin de aynıysa, kesin sonuç döndür
        if horizontal_pred == vertical_pred:
            return horizontal_pred
        
        # Eğer farklıysa, ağırlıklı seçim yap (son sonuçlardaki başarı oranlarına göre ayarlanabilir)
        # Bu uygulama, sabit ağırlıklar yerine dinamik olarak uyarlanabilir
        if self.horizontal_weight > self.vertical_weight:
            return horizontal_pred
        else:
            return vertical_pred
    
    def should_reverse_bet(self, wl_history, main_prediction):
        """
        Ana tahmine karşı bahis yapılması gerekip gerekmediğini belirler.
        
        Args:
            wl_history (list): 'W' ve 'L' değerlerinden oluşan kazanç/kayıp geçmişi.
            main_prediction (str): Ana tahmin ('P' veya 'B').
            
        Returns:
            tuple: (should_reverse, predicted_wl, horizontal_pred, vertical_pred) - Tersine bahis yapılmalı mı, WL tahmini ve ayrı tahminler.
        """
        if not wl_history:
            return False, '?', '?', '?'
            
        predicted_wl = self.predict(wl_history)
        
        # Tahmin kayıp veya belirsizse, bahsi tersine çevir
        should_reverse = predicted_wl == 'L'
        
        return should_reverse, predicted_wl, self.last_horizontal_pred, self.last_vertical_pred
    
    def update_weights(self, horizontal_success, vertical_success):
        """
        Tahmin ağırlıklarını başarı oranlarına göre günceller.
        
        Args:
            horizontal_success (float): Yatay tahmin başarı oranı (0-1 arasında).
            vertical_success (float): Dikey tahmin başarı oranı (0-1 arasında).
        """
        total = horizontal_success + vertical_success
        if total > 0:
            self.horizontal_weight = horizontal_success / total
            self.vertical_weight = vertical_success / total
        else:
            # Veri yoksa varsayılan ağırlıklara dön
            self.horizontal_weight = 0.6
            self.vertical_weight = 0.4