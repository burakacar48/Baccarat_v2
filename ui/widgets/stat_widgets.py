"""
İstatistik gösterimi için özel widget'lar modülü.
"""
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt
from utils.helpers import create_stat_row, format_currency, format_percentage
from config import INITIAL_KASA, TEXT_COLOR_POSITIVE, TEXT_COLOR_NEGATIVE

class KasaStatWidget(QWidget):
    """Kasa durumu ve ilgili istatistikleri gösteren widget."""
    
    def __init__(self, parent=None):
        """
        Args:
            parent (QWidget, optional): Ebeveyn widget.
        """
        super().__init__(parent)
        
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # Durum etiketleri
        _, self.kasa_label = create_stat_row("Kasa:", "KasaValueLabel")
        _, self.bet_label = create_stat_row("Bet:", "BetValueLabel")
        _, self.win_streak_label = create_stat_row("En Uzun W Serisi:", "WinStreakValueLabel")
        _, self.loss_streak_label = create_stat_row("En Uzun L Serisi:", "LossStreakValueLabel")
        
        # Etiketleri yerleştir
        self.layout.addWidget(self.kasa_label.parent())
        self.layout.addWidget(self.bet_label.parent())
        self.layout.addWidget(self.win_streak_label.parent())
        self.layout.addWidget(self.loss_streak_label.parent())
    
    def update_stats(self, stats):
        """İstatistikleri günceller.
        
        Args:
            stats (dict): İstatistik verileri.
        """
        # Kasa durumu
        kasa_color = TEXT_COLOR_POSITIVE.name() if stats['kasa'] >= INITIAL_KASA else TEXT_COLOR_NEGATIVE.name()
        self.kasa_label.setText(format_currency(stats['kasa']))
        self.kasa_label.setStyleSheet(f"QLabel#KasaValueLabel {{ color: {kasa_color}; font-weight: bold; }}")
        
        # Bahis
        self.bet_label.setText(format_currency(stats['current_bet']))
        
        # Serileri güncelle
        self.win_streak_label.setText(str(stats['longest_win_streak']))
        self.loss_streak_label.setText(str(stats['longest_loss_streak']))

class TableStatWidget(QWidget):
    """Masa istatistiklerini gösteren widget."""
    
    def __init__(self, parent=None):
        """
        Args:
            parent (QWidget, optional): Ebeveyn widget.
        """
        super().__init__(parent)
        
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # İstatistik etiketleri
        _, self.total_hands_label = create_stat_row("Toplam El:")
        _, self.player_wins_label = create_stat_row("Player Kazanç:")
        _, self.banker_wins_label = create_stat_row("Banker Kazanç:")
        _, self.player_perc_label = create_stat_row("Player Yüzde:")
        _, self.banker_perc_label = create_stat_row("Banker Yüzde:")
        
        # Etiketleri yerleştir
        self.layout.addWidget(self.total_hands_label.parent())
        self.layout.addWidget(self.player_wins_label.parent())
        self.layout.addWidget(self.banker_wins_label.parent())
        self.layout.addWidget(self.player_perc_label.parent())
        self.layout.addWidget(self.banker_perc_label.parent())
    
    def update_stats(self, stats):
        """İstatistikleri günceller.
        
        Args:
            stats (dict): İstatistik verileri.
        """
        total_hands = stats['total_hands']
        p_wins = stats['player_wins']
        b_wins = stats['banker_wins']
        p_perc = stats['player_percentage']
        b_perc = stats['banker_percentage']
        
        # Etiketleri güncelle
        self.total_hands_label.setText(str(total_hands))
        self.player_wins_label.setText(str(p_wins))
        self.banker_wins_label.setText(str(b_wins))
        self.player_perc_label.setText(format_percentage(p_perc))
        self.banker_perc_label.setText(format_percentage(b_perc))

class ModelStatWidget(QWidget):
    """Model istatistiklerini gösteren widget."""
    
    def __init__(self, parent=None):
        """
        Args:
            parent (QWidget, optional): Ebeveyn widget.
        """
        super().__init__(parent)
        
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(6)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        self.model_rows = []
        
        # Üç model için satır oluştur
        for i in range(3):
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            
            name_label = QLabel(f"{i+1}. Model:")
            name_label.setObjectName("MainModelNameLabel")
            
            accuracy_label = QLabel("N/A")
            accuracy_label.setObjectName("MainModelAccuracyLabel")
            accuracy_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            row_layout.addWidget(name_label)
            row_layout.addWidget(accuracy_label)
            
            self.layout.addWidget(row)
            self.model_rows.append({'name': name_label, 'accuracy': accuracy_label})
    
    def update_models(self, models, min_predictions=5):
        """Model istatistiklerini günceller.
        
        Args:
            models (list): Model verileri listesi.
            min_predictions (int, optional): Minimum tahmin sayısı.
        """
        # Yeterli tahmini olan modelleri al ve doğruluk oranına göre sırala
        ranked_models = sorted(
            [m for m in models if m['total'] >= min_predictions],
            key=lambda m: m['accuracy'],
            reverse=True
        )
        
        # Her bir model satırını güncelle
        for i in range(3):
            if i >= len(self.model_rows):
                break
                
            label_set = self.model_rows[i]
            
            if i < len(ranked_models):
                model = ranked_models[i]
                label_set['name'].setText(f"{i+1}. {model['name']}:")
                label_set['accuracy'].setText(format_percentage(model['accuracy']))
                label_set['name'].setVisible(True)
                label_set['accuracy'].setVisible(True)
            else:
                label_set['name'].setText(f"{i+1}. Model:")
                label_set['accuracy'].setText("N/A")
