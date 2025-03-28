"""
Oyun geçmişini ve istatistiklerini yöneten modül.
Bu modül, oyun sonuçlarını, kasa durumunu ve Martingale stratejisi takibini içerir.
"""
from config import INITIAL_KASA, MARTINGALE_SEQUENCE, GRID_SIZE, MAX_HISTORY_IN_GRID

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
    
    def clear_histories(self):
        """Sadece geçmiş verilerini sıfırlar, kasa durumunu korur."""
        self.history = []
        self.win_loss_history = []
        self.current_win_streak = 0
        self.current_loss_streak = 0
        self.grid_data = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    
    def add_result(self, winner, is_win=None):
        """Yeni bir sonuç ekler ve gerekli istatistikleri günceller.
        
        Args:
            winner (str): 'P' veya 'B' değeri.
            is_win (bool, optional): Tahmin sonucu. Belirtilmezse sadece sonuç eklenir.
        
        Returns:
            dict: Güncelleme bilgilerini içeren sözlük.
        """
        self.history.append(winner)
        
        bet_index = min(self.current_bet_index, len(MARTINGALE_SEQUENCE) - 1)
        current_bet = MARTINGALE_SEQUENCE[bet_index]
        
        result_info = {
            'winner': winner,
            'current_bet': current_bet,
            'is_win': is_win,
            'bet_change': 0
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
        
        self._rebuild_grid_from_history()
        
        return result_info
    
    def undo_last_action(self):
        """Son eklenen sonucu geri alır.
        
        Returns:
            bool: İşlemin başarılı olup olmadığı.
        """
        if not self.history:
            return False
        
        removed_result = self.history.pop()
        if self.win_loss_history:
            self.win_loss_history.pop()
        
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
            'current_loss_streak': self.current_loss_streak
        }
        
        return stats
