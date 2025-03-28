"""
Geliştirilmiş Win/Loss pattern prediction module.
Bu modül hem yatay hem de dikey win/loss desenlerini analiz ederek daha başarılı tahminler üretir.
"""
from collections import Counter, deque

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
        
        # Son tahminlerin sonuçlarını tutmak için kuyruklar (son 20 tahmin)
        self.horizontal_results = deque(maxlen=20)
        self.vertical_results = deque(maxlen=20)
        
        # Tahmin tiplerine göre başarı sayaçları
        self.pattern_type_successes = {
            "streak": {"horizontal": 0, "vertical": 0, "total": 0},
            "alternating": {"horizontal": 0, "vertical": 0, "total": 0},
            "mixed": {"horizontal": 0, "vertical": 0, "total": 0}
        }
        
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
                best_prediction = 'W' if last_pair[-1] == 'L' else 'L'
            elif len(wl_history) > 0:
                best_prediction = 'W' if wl_history[-1] == 'L' else 'L'
        
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
                # Son 3 eleman ile 4'lü gruplar için tahminler yapalım (genişletilmiş analiz)
                if len(col) >= 4:
                    last_four = col[-4:]
                    # 4'lü özel desenler
                    if last_four == ['W', 'L', 'W', 'L']:
                        predictions.append('W')  # WLWL -> W
                    elif last_four == ['L', 'W', 'L', 'W']:
                        predictions.append('L')  # LWLW -> L
                
                # Orijinal 3'lü analiz
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
    
    def _classify_pattern(self, wl_history):
        """
        Mevcut WL dizisinin desen türünü sınıflandırır.
        
        Args:
            wl_history (list): 'W' ve 'L' değerlerinden oluşan kazanç/kayıp geçmişi.
            
        Returns:
            str: "streak", "alternating" veya "mixed"
        """
        if len(wl_history) < 4:
            return "mixed"
            
        # Son 4 elemana bakalım
        last_four = wl_history[-4:]
        
        # Streak (WWWW veya LLLL)
        if all(x == 'W' for x in last_four) or all(x == 'L' for x in last_four):
            return "streak"
            
        # Alternating (WLWL veya LWLW)
        if (last_four == ['W', 'L', 'W', 'L'] or 
            last_four == ['L', 'W', 'L', 'W']):
            return "alternating"
            
        # Diğer tüm durumlar
        return "mixed"
    
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
        
        # Desen türünü belirle
        pattern_type = self._classify_pattern(wl_history)
        
        # Desen türüne göre ağırlıklandırma yap
        if pattern_type in self.pattern_type_successes:
            type_stats = self.pattern_type_successes[pattern_type]
            if type_stats["total"] > 0:
                # Desen türüne özgü başarı oranlarına göre ağırlıkları belirle
                h_success_rate = type_stats["horizontal"] / type_stats["total"] if type_stats["total"] > 0 else 0.5
                v_success_rate = type_stats["vertical"] / type_stats["total"] if type_stats["total"] > 0 else 0.5
                
                # Minimum 0.2 başarı oranı garantisi
                h_success_rate = max(0.2, h_success_rate)
                v_success_rate = max(0.2, v_success_rate)
                
                # Başarı oranlarını normalize et
                total_rate = h_success_rate + v_success_rate
                h_weight = h_success_rate / total_rate if total_rate > 0 else 0.5
                v_weight = v_success_rate / total_rate if total_rate > 0 else 0.5
                
                # Desen türüne özgü ağırlıklandırma kullan
                return horizontal_pred if h_weight > v_weight else vertical_pred
        
        # Varsayılan olarak genel ağırlıkları kullan
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
    
    def update_weights(self, horizontal_success, vertical_success, momentum=0.7):
        """
        Tahmin ağırlıklarını başarı oranlarına göre günceller, momentum faktörü ile.
        
        Args:
            horizontal_success (float): Yatay tahmin başarı oranı (0-1 arasında).
            vertical_success (float): Dikey tahmin başarı oranı (0-1 arasında).
            momentum (float): Önceki değerlerin ağırlığı (0-1 arasında).
        """
        total = horizontal_success + vertical_success
        if total > 0:
            new_h_weight = horizontal_success / total
            new_v_weight = vertical_success / total
            
            # Momentum faktörü ile güncelleme
            self.horizontal_weight = (momentum * self.horizontal_weight) + ((1-momentum) * new_h_weight)
            self.vertical_weight = (momentum * self.vertical_weight) + ((1-momentum) * new_v_weight)
            
            # Değerleri normalize et (toplamları 1.0 olmalı)
            total_weight = self.horizontal_weight + self.vertical_weight
            self.horizontal_weight /= total_weight
            self.vertical_weight /= total_weight
        else:
            # Veri yoksa varsayılan ağırlıklara dön
            self.horizontal_weight = 0.6
            self.vertical_weight = 0.4
    
    def record_prediction_result(self, is_horizontal_correct, is_vertical_correct, pattern_type=None):
        """
        Bir tahmin sonucunu kaydeder ve istatistikleri günceller.
        
        Args:
            is_horizontal_correct (bool): Yatay tahmin doğru muydu?
            is_vertical_correct (bool): Dikey tahmin doğru muydu?
            pattern_type (str, optional): Tahmin edilen desen türü.
        """
        # Son sonuçları güncelle
        self.horizontal_results.append(1 if is_horizontal_correct else 0)
        self.vertical_results.append(1 if is_vertical_correct else 0)
        
        # Desen türüne göre başarı istatistiklerini güncelle
        if pattern_type in self.pattern_type_successes:
            stats = self.pattern_type_successes[pattern_type]
            stats["total"] += 1
            if is_horizontal_correct:
                stats["horizontal"] += 1
            if is_vertical_correct:
                stats["vertical"] += 1
    
    def get_recent_success_rates(self):
        """
        Son tahminlerin başarı oranlarını hesaplar.
        
        Returns:
            tuple: (horizontal_rate, vertical_rate) - Son tahminlerin başarı oranları.
        """
        h_rate = sum(self.horizontal_results) / len(self.horizontal_results) if self.horizontal_results else 0.5
        v_rate = sum(self.vertical_results) / len(self.vertical_results) if self.vertical_results else 0.5
        return h_rate, v_rate