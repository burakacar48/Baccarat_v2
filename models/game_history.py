"""
Oyun geçmişini ve istatistiklerini yöneten modül.
Bu modül, oyun sonuçlarını, kasa durumunu ve Martingale stratejisi takibini içerir.
"""
from config import INITIAL_KASA, MARTINGALE_SEQUENCE, GRID_SIZE, MAX_HISTORY_IN_GRID
from baccarat_simulator import is_new_shoe_detected

class GameHistory:
    """Oyun geçmişini ve istatistiklerini yöneten sınıf."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Tüm geçmiş ve istatistikleri sıfırlar."""
        self.history = []
        self.win_loss_history = []
        self.kasa = INITIAL_KASA
        self.current_bet_index = 0
        self.current_win_streak = 0
        self.current_loss_streak = 0
        self.longest_win_streak = 0
        self.longest_loss_streak = 0
        self.grid_data = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.new_shoe_detected = False
        
        # Reverse betting statistics
        self.reverse_bet_count = 0
        self.reverse_bet_wins = 0
        self.normal_bet_count = 0
        self.normal_bet_wins = 0
        
        # Yatay ve dikey tahmin istatistikleri
        self.horizontal_wl_predictions = 0
        self.horizontal_wl_correct = 0
        self.vertical_wl_predictions = 0
        self.vertical_wl_correct = 0
        
        # Son tahminleri saklama
        self.last_horizontal_wl_pred = '?'
        self.last_vertical_wl_pred = '?'
        
        # Son N tahmin için sonuçları tutma
        self.recent_horizontal_results = []  # 1: doğru, 0: yanlış
        self.recent_vertical_results = []    # 1: doğru, 0: yanlış
        self.max_recent_results = 20  # Son kaç tahmini saklanacak
        
        # Desen tipine göre tahmin başarısı
        self.pattern_type_stats = {
            "streak": {"h_correct": 0, "v_correct": 0, "total": 0},
            "alternating": {"h_correct": 0, "v_correct": 0, "total": 0},
            "mixed": {"h_correct": 0, "v_correct": 0, "total": 0}
        }
        
        # Son tahmin edilen desen tipi
        self.last_pattern_type = None
    
    def clear_histories(self):
        """Sadece geçmiş verilerini sıfırlar, kasa durumunu korur."""
        self.history = []
        self.win_loss_history = []
        self.current_win_streak = 0
        self.current_loss_streak = 0
        self.grid_data = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.new_shoe_detected = False
        
        # Reverse betting statistics reset
        self.reverse_bet_count = 0
        self.reverse_bet_wins = 0
        self.normal_bet_count = 0
        self.normal_bet_wins = 0
        
        # Yatay ve dikey tahmin istatistiklerini sıfırla
        self.horizontal_wl_predictions = 0
        self.horizontal_wl_correct = 0
        self.vertical_wl_predictions = 0
        self.vertical_wl_correct = 0
        
        # Son tahminleri sıfırla
        self.last_horizontal_wl_pred = '?'
        self.last_vertical_wl_pred = '?'
        
        # Son tahmin sonuçlarını temizle
        self.recent_horizontal_results = []
        self.recent_vertical_results = []
        
        # Desen tipi istatistiklerini sıfırla
        for pattern_type in self.pattern_type_stats:
            self.pattern_type_stats[pattern_type] = {"h_correct": 0, "v_correct": 0, "total": 0}
        
        self.last_pattern_type = None
    
    def add_result(self, winner, is_win=None, is_reverse_bet=False):
        """Yeni bir sonuç ekler ve gerekli istatistikleri günceller.
        
        Args:
            winner (str): 'P' veya 'B' değeri.
            is_win (bool, optional): Tahmin sonucu. Belirtilmezse sadece sonuç eklenir.
            is_reverse_bet (bool, optional): Ters bahis yapılıp yapılmadığı.
        
        Returns:
            dict: Güncelleme bilgilerini içeren sözlük.
        """
        # Yeni ayakkabı başlayıp başlamadığını kontrol et
        self.new_shoe_detected = is_new_shoe_detected()
        
        self.history.append(winner)
        
        bet_index = min(self.current_bet_index, len(MARTINGALE_SEQUENCE) - 1)
        current_bet = MARTINGALE_SEQUENCE[bet_index]
        
        result_info = {
            'winner': winner,
            'current_bet': current_bet,
            'is_win': is_win,
            'bet_change': 0,
            'is_reverse_bet': is_reverse_bet
        }
        
        if is_win is not None:
            if is_win:  # Kazanç
                result_info['bet_change'] = current_bet
                self.win_loss_history.append('W')
                self.kasa += current_bet
                self.current_win_streak += 1
                self.current_loss_streak = 0
                self.longest_win_streak = max(self.longest_win_streak, self.current_win_streak)
                self.current_bet_index = 0
                
                # Update reverse betting statistics
                if is_reverse_bet:
                    self.reverse_bet_wins += 1
                else:
                    self.normal_bet_wins += 1
                    
                # WL tahmin doğruluğunu güncelle
                h_correct = self.last_horizontal_wl_pred == 'W'
                v_correct = self.last_vertical_wl_pred == 'W'
                
                if self.last_horizontal_wl_pred != '?':
                    self.horizontal_wl_correct += 1 if h_correct else 0
                    self.recent_horizontal_results.append(1 if h_correct else 0)
                    self._trim_recent_results(self.recent_horizontal_results)
                
                if self.last_vertical_wl_pred != '?':
                    self.vertical_wl_correct += 1 if v_correct else 0
                    self.recent_vertical_results.append(1 if v_correct else 0)
                    self._trim_recent_results(self.recent_vertical_results)
                
                # Desen tipine göre istatistikleri güncelle
                if self.last_pattern_type:
                    stats = self.pattern_type_stats.get(self.last_pattern_type)
                    if stats:
                        stats["total"] += 1
                        if h_correct:
                            stats["h_correct"] += 1
                        if v_correct:
                            stats["v_correct"] += 1
                
            else:  # Kayıp
                result_info['bet_change'] = -current_bet
                self.win_loss_history.append('L')
                self.kasa -= current_bet
                self.current_loss_streak += 1
                self.current_win_streak = 0
                self.longest_loss_streak = max(self.longest_loss_streak, self.current_loss_streak)
                self.current_bet_index += 1
                if self.current_bet_index >= len(MARTINGALE_SEQUENCE):
                    self.current_bet_index = 0
                    print("Martingale sonu! Başa dönülüyor.")
                    
                # WL tahmin doğruluğunu güncelle
                h_correct = self.last_horizontal_wl_pred == 'L'
                v_correct = self.last_vertical_wl_pred == 'L'
                
                if self.last_horizontal_wl_pred != '?':
                    self.horizontal_wl_correct += 1 if h_correct else 0
                    self.recent_horizontal_results.append(1 if h_correct else 0)
                    self._trim_recent_results(self.recent_horizontal_results)
                
                if self.last_vertical_wl_pred != '?':
                    self.vertical_wl_correct += 1 if v_correct else 0
                    self.recent_vertical_results.append(1 if v_correct else 0)
                    self._trim_recent_results(self.recent_vertical_results)
                
                # Desen tipine göre istatistikleri güncelle
                if self.last_pattern_type:
                    stats = self.pattern_type_stats.get(self.last_pattern_type)
                    if stats:
                        stats["total"] += 1
                        if h_correct:
                            stats["h_correct"] += 1
                        if v_correct:
                            stats["v_correct"] += 1
            
            # Increment betting counters
            if is_reverse_bet:
                self.reverse_bet_count += 1
            else:
                self.normal_bet_count += 1
                
            # WL tahmin sayaçlarını güncelle
            if self.last_horizontal_wl_pred != '?':
                self.horizontal_wl_predictions += 1
            if self.last_vertical_wl_pred != '?':
                self.vertical_wl_predictions += 1
            
            # Tahminleri temizle
            self.last_horizontal_wl_pred = '?'
            self.last_vertical_wl_pred = '?'
            self.last_pattern_type = None
        
        self._rebuild_grid_from_history()
        
        return result_info
    
    def _trim_recent_results(self, results_list):
        """Son sonuçlar listesini belirli bir uzunlukta tutar."""
        while len(results_list) > self.max_recent_results:
            results_list.pop(0)
    
    def set_wl_predictions(self, horizontal_pred, vertical_pred, pattern_type=None):
        """Yeni WL tahminlerini kaydeder.
        
        Args:
            horizontal_pred (str): Yatay WL tahmini ('W', 'L' veya '?').
            vertical_pred (str): Dikey WL tahmini ('W', 'L' veya '?').
            pattern_type (str, optional): Tahmin edilen desen türü.
        """
        self.last_horizontal_wl_pred = horizontal_pred
        self.last_vertical_wl_pred = vertical_pred
        self.last_pattern_type = pattern_type
    
    def get_recent_wl_success_rates(self):
        """Son tahminlerin başarı oranlarını hesaplar.
        
        Returns:
            tuple: (horizontal_rate, vertical_rate) - Son tahminlerin başarı oranları.
        """
        h_rate = sum(self.recent_horizontal_results) / len(self.recent_horizontal_results) if self.recent_horizontal_results else 0.5
        v_rate = sum(self.recent_vertical_results) / len(self.recent_vertical_results) if self.recent_vertical_results else 0.5
        return h_rate, v_rate
    
    def get_pattern_type_success_rates(self, pattern_type):
        """Belirli bir desen tipi için başarı oranlarını hesaplar.
        
        Args:
            pattern_type (str): Desen tipi.
            
        Returns:
            tuple: (horizontal_rate, vertical_rate) - Belirli bir desen tipi için başarı oranları.
        """
        stats = self.pattern_type_stats.get(pattern_type)
        if not stats or stats["total"] == 0:
            return 0.5, 0.5
            
        h_rate = stats["h_correct"] / stats["total"]
        v_rate = stats["v_correct"] / stats["total"]
        return h_rate, v_rate
    
    def undo_last_action(self):
        """Son eklenen sonucu geri alır.
        
        Returns:
            bool: İşlemin başarılı olup olmadığı.
        """
        if not self.history:
            return False
        
        removed_result = self.history.pop()
        if self.win_loss_history:
            removed_wl = self.win_loss_history.pop()
            
            # Adjust statistics if we're removing a tracked bet
            if removed_wl == 'W':
                if self.current_win_streak > 0:
                    self.current_win_streak -= 1
            elif removed_wl == 'L':
                if self.current_loss_streak > 0:
                    self.current_loss_streak -= 1
            
            # Note: We're not adjusting the reverse bet statistics as we can't easily know
            # if it was a reverse bet without additional tracking
        
        self._rebuild_grid_from_history()
        return True
    
    def _rebuild_grid_from_history(self):
        """Geçmişteki sonuçlara göre grid verilerini yeniden oluşturur."""
        start_index = max(0, len(self.history) - MAX_HISTORY_IN_GRID)
        grid_relevant_history = self.history[start_index:]
        
        self.grid_data = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        current_r, current_c = 0, 0
        
        for item in grid_relevant_history:
            if current_c < GRID_SIZE:
                self.grid_data[current_r][current_c] = item
                current_r += 1
                if current_r >= GRID_SIZE:
                    current_r = 0
                    current_c += 1
            else:
                break
    
    def get_current_bet(self):
        """Mevcut bahis miktarını döndürür.
        
        Returns:
            float: Mevcut bahis miktarı.
        """
        bet_index = min(self.current_bet_index, len(MARTINGALE_SEQUENCE) - 1)
        return MARTINGALE_SEQUENCE[bet_index]
    
    def get_statistics(self):
        """Oyun istatistiklerini döndürür.
        
        Returns:
            dict: İstatistikleri içeren sözlük.
        """
        total_hands = len(self.history)
        p_wins = self.history.count('P')
        b_wins = self.history.count('B')
        
        # Calculate reverse betting effectiveness
        reverse_accuracy = 0
        if self.reverse_bet_count > 0:
            reverse_accuracy = (self.reverse_bet_wins / self.reverse_bet_count) * 100
            
        normal_accuracy = 0
        if self.normal_bet_count > 0:
            normal_accuracy = (self.normal_bet_wins / self.normal_bet_count) * 100
            
        # Calculate WL prediction accuracies
        h_accuracy = 0
        if self.horizontal_wl_predictions > 0:
            h_accuracy = (self.horizontal_wl_correct / self.horizontal_wl_predictions) * 100
            
        v_accuracy = 0
        if self.vertical_wl_predictions > 0:
            v_accuracy = (self.vertical_wl_correct / self.vertical_wl_predictions) * 100
        
        # Calculate recent success rates
        h_recent_rate, v_recent_rate = self.get_recent_wl_success_rates()
        h_recent_accuracy = h_recent_rate * 100
        v_recent_accuracy = v_recent_rate * 100
        
        stats = {
            'total_hands': total_hands,
            'player_wins': p_wins,
            'banker_wins': b_wins,
            'player_percentage': (p_wins / total_hands * 100) if total_hands > 0 else 0,
            'banker_percentage': (b_wins / total_hands * 100) if total_hands > 0 else 0,
            'kasa': self.kasa,
            'current_bet': self.get_current_bet(),
            'current_bet_index': self.current_bet_index,
            'longest_win_streak': self.longest_win_streak,
            'longest_loss_streak': self.longest_loss_streak,
            'current_win_streak': self.current_win_streak,
            'current_loss_streak': self.current_loss_streak,
            'reverse_bet_count': self.reverse_bet_count,
            'reverse_bet_wins': self.reverse_bet_wins,
            'reverse_accuracy': reverse_accuracy,
            'normal_bet_count': self.normal_bet_count,
            'normal_bet_wins': self.normal_bet_wins,
            'normal_accuracy': normal_accuracy,
            'horizontal_wl_predictions': self.horizontal_wl_predictions,
            'horizontal_wl_correct': self.horizontal_wl_correct,
            'horizontal_wl_accuracy': h_accuracy,
            'vertical_wl_predictions': self.vertical_wl_predictions,
            'vertical_wl_correct': self.vertical_wl_correct,
            'vertical_wl_accuracy': v_accuracy,
            'recent_horizontal_accuracy': h_recent_accuracy,
            'recent_vertical_accuracy': v_recent_accuracy,
            'pattern_type_stats': self.pattern_type_stats
        }
        
        return stats