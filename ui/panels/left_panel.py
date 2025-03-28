"""
Uygulama arayüzünün sol paneli.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QGroupBox, QSizePolicy, QLabel
)
from config import UNDO_EMOJI, CLEAR_EMOJI, RESET_EMOJI, SIMULATE_EMOJI, STATS_EMOJI, SIMULATE_MULTI_EMOJI
from ui.widgets.prediction_view import PredictionLabel
from ui.widgets.enhanced_wl_prediction_view import EnhancedWLPredictionWidget  # Yeni geliştirilmiş WL tahmin widgeti
from PyQt6.QtCore import Qt

class StatRowWidget(QWidget):
    """Basit istatistik satırı"""
    def __init__(self, label_text, value_object_name="StatValueLabel", parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel(label_text)
        self.label.setObjectName("StatLabel")
        
        self.value_label = QLabel("N/A")
        self.value_label.setObjectName(value_object_name)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.value_label)
    
    def set_value(self, value):
        self.value_label.setText(str(value))

class KasaStatWidget(QWidget):
    """Kasa durumunu gösteren basit widget."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)
        
        self.kasa_row = StatRowWidget("Kasa:", "KasaValueLabel")
        self.bet_row = StatRowWidget("Bet:", "BetValueLabel")
        self.win_streak_row = StatRowWidget("En Uzun W Serisi:", "WinStreakValueLabel")
        self.loss_streak_row = StatRowWidget("En Uzun L Serisi:", "LossStreakValueLabel")
        
        # Yeni eklenen satırlar - WL tahmin sistemi performansı
        self.wl_reverse_row = StatRowWidget("Ters Bahis Başarı:", "WLReverseValueLabel")
        self.wl_normal_row = StatRowWidget("Normal Bahis Başarı:", "WLNormalValueLabel")
        
        # Yeni eklenen satırlar - Yatay/Dikey tahmin performansı
        self.horizontal_wl_row = StatRowWidget("Yatay WL Başarı:", "HorizontalWLValueLabel")
        self.vertical_wl_row = StatRowWidget("Dikey WL Başarı:", "VerticalWLValueLabel")
        
        self.layout.addWidget(self.kasa_row)
        self.layout.addWidget(self.bet_row)
        self.layout.addWidget(self.win_streak_row)
        self.layout.addWidget(self.loss_streak_row)
        self.layout.addWidget(self.wl_reverse_row)
        self.layout.addWidget(self.wl_normal_row)
        self.layout.addWidget(self.horizontal_wl_row)
        self.layout.addWidget(self.vertical_wl_row)
    
    def update_stats(self, stats):
        self.kasa_row.set_value(f"{stats['kasa']:,.2f} TL")
        self.bet_row.set_value(f"{stats['current_bet']:,.2f} TL")
        self.win_streak_row.set_value(str(stats['longest_win_streak']))
        self.loss_streak_row.set_value(str(stats['longest_loss_streak']))
        
        # WL tahmin performans verilerini güncelle
        if 'reverse_accuracy' in stats:
            self.wl_reverse_row.set_value(f"{stats['reverse_accuracy']:.1f}% ({stats['reverse_bet_wins']}/{stats['reverse_bet_count']})")
        if 'normal_accuracy' in stats:
            self.wl_normal_row.set_value(f"{stats['normal_accuracy']:.1f}% ({stats['normal_bet_wins']}/{stats['normal_bet_count']})")
            
        # Yatay/Dikey WL tahmin performansını güncelle
        if 'horizontal_wl_accuracy' in stats:
            self.horizontal_wl_row.set_value(f"{stats['horizontal_wl_accuracy']:.1f}% ({stats['horizontal_wl_correct']}/{stats['horizontal_wl_predictions']})")
        if 'vertical_wl_accuracy' in stats:
            self.vertical_wl_row.set_value(f"{stats['vertical_wl_accuracy']:.1f}% ({stats['vertical_wl_correct']}/{stats['vertical_wl_predictions']})")

class TableStatWidget(QWidget):
    """Masa istatistiklerini gösteren basit widget."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)
        
        self.total_hands_row = StatRowWidget("Toplam El:")
        self.player_wins_row = StatRowWidget("Player Kazanç:")
        self.banker_wins_row = StatRowWidget("Banker Kazanç:")
        self.player_perc_row = StatRowWidget("Player Yüzde:")
        self.banker_perc_row = StatRowWidget("Banker Yüzde:")
        
        self.layout.addWidget(self.total_hands_row)
        self.layout.addWidget(self.player_wins_row)
        self.layout.addWidget(self.banker_wins_row)
        self.layout.addWidget(self.player_perc_row)
        self.layout.addWidget(self.banker_perc_row)
    
    def update_stats(self, stats):
        self.total_hands_row.set_value(str(stats['total_hands']))
        self.player_wins_row.set_value(str(stats['player_wins']))
        self.banker_wins_row.set_value(str(stats['banker_wins']))
        self.player_perc_row.set_value(f"{stats['player_percentage']:.1f}%")
        self.banker_perc_row.set_value(f"{stats['banker_percentage']:.1f}%")

class LeftPanel(QWidget):
    """Uygulamanın sol panel bileşeni."""
    
    def __init__(self, parent=None):
        """
        Args:
            parent (QWidget, optional): Ebeveyn widget.
        """
        super().__init__(parent)
        self.setObjectName("LeftPanel")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(15)
        
        # Alt bileşenler
        self.player_button = None
        self.banker_button = None
        self.kasa_widget = None
        self.prediction_label = None
        self.wl_prediction_widget = None  # Geliştirilmiş WL tahmin widget
        self.table_stat_widget = None
        self.action_buttons = {}
        
        self._init_ui()
    
    def _init_ui(self):
        """Kullanıcı arayüzünü başlatır."""
        self._create_input_buttons()
        self._create_kasa_stats_ui()
        self._create_prediction_label()
        self._create_table_stats_ui()
        self._create_action_buttons_ui()
        
        # Alt boşluk ekle
        self.layout.addStretch(1)
    
    def _create_input_buttons(self):
        """Player/Banker giriş düğmelerini oluşturur."""
        container = QWidget()
        button_layout = QHBoxLayout(container)
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # Player düğmesi
        self.player_button = QPushButton("Player")
        self.player_button.setObjectName("PlayerButton")
        self.player_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Banker düğmesi
        self.banker_button = QPushButton("Banker")
        self.banker_button.setObjectName("BankerButton")
        self.banker_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        button_layout.addWidget(self.player_button)
        button_layout.addWidget(self.banker_button)
        
        self.layout.addWidget(container)
    
    def _create_kasa_stats_ui(self):
        """Kasa istatistikleri bölümünü oluşturur."""
        kasa_group_box = QGroupBox("Kasa & Durum")
        kasa_layout = QVBoxLayout(kasa_group_box)
        kasa_layout.setContentsMargins(10, 10, 10, 10)
        
        self.kasa_widget = KasaStatWidget()
        kasa_layout.addWidget(self.kasa_widget)
        
        self.layout.addWidget(kasa_group_box)
    
    def _create_prediction_label(self):
        """Tahmin gösterimi bölümünü oluşturur."""
        pred_group_box = QGroupBox("Sıradaki Tahmin")
        pred_layout = QVBoxLayout(pred_group_box)
        pred_layout.setSpacing(8)
        pred_layout.setContentsMargins(10, 10, 10, 10)
        
        self.prediction_label = PredictionLabel()
        pred_layout.addWidget(self.prediction_label)
        
        # Geliştirilmiş WL tahmin widgeti oluştur ve ekle
        self.wl_prediction_widget = EnhancedWLPredictionWidget()
        pred_layout.addWidget(self.wl_prediction_widget)
        
        self.layout.addWidget(pred_group_box)
    
    def _create_table_stats_ui(self):
        """Masa istatistikleri bölümünü oluşturur."""
        table_stats_group_box = QGroupBox("Masa İstatistikleri")
        table_stats_layout = QVBoxLayout(table_stats_group_box)
        table_stats_layout.setContentsMargins(10, 10, 10, 10)
        
        self.table_stat_widget = TableStatWidget()
        table_stats_layout.addWidget(self.table_stat_widget)
        
        self.layout.addWidget(table_stats_group_box)
    
    def _create_action_buttons_ui(self):
        """Eylem düğmelerini oluşturur."""
        action_container = QWidget()
        action_layout = QHBoxLayout(action_container)
        action_layout.setSpacing(10)
        action_layout.setContentsMargins(0, 5, 0, 0)
        
        # Düğme tanımları
        button_definitions = [
            {"id": "undo", "emoji": UNDO_EMOJI, "tooltip": "Sonucu Geri Al (Stat Etkilenmez)"},
            {"id": "clear", "emoji": CLEAR_EMOJI, "tooltip": "Geçmişi Temizle"},
            {"id": "reset", "emoji": RESET_EMOJI, "tooltip": "Her Şeyi Sıfırla (Kasa Dahil)"},
            {"id": "simulate", "emoji": SIMULATE_EMOJI, "tooltip": "Gerçek Baccarat Simüle Et"},
            {"id": "stats", "emoji": STATS_EMOJI, "tooltip": "Model Detayları"}
        ]
        
        # Sol boşluk
        action_layout.addStretch(1)
        
        # Düğmeleri oluştur
        for btn_def in button_definitions:
            button = QPushButton(btn_def["emoji"])
            button.setObjectName("ActionButton")
            button.setToolTip(btn_def["tooltip"])
            self.action_buttons[btn_def["id"]] = button
            action_layout.addWidget(button)
        
        # Sağ boşluk
        action_layout.addStretch(1)
        
        self.layout.addWidget(action_container)
    
    def update_kasa_stats(self, stats):
        """Kasa istatistiklerini günceller.
        
        Args:
            stats (dict): İstatistik verileri.
        """
        self.kasa_widget.update_stats(stats)
    
    def update_table_stats(self, stats):
        """Masa istatistiklerini günceller.
        
        Args:
            stats (dict): İstatistik verileri.
        """
        self.table_stat_widget.update_stats(stats)
    
    def update_prediction(self, prediction, wl_prediction='?', reverse_bet=False, h_pred='?', v_pred='?', h_accuracy=None, v_accuracy=None):
        """Tahmin gösterimini günceller.
        
        Args:
            prediction (str): Tahmin değeri ('P', 'B' veya '?').
            wl_prediction (str): WL tahmin değeri ('W', 'L' veya '?').
            reverse_bet (bool): Ters bahis yapılıp yapılmayacağı.
            h_pred (str): Yatay WL tahmin değeri.
            v_pred (str): Dikey WL tahmin değeri.
            h_accuracy (float/dict): Yatay tahmin doğruluk oranı veya istatistik sözlüğü.
            v_accuracy (float/dict): Dikey tahmin doğruluk oranı veya istatistik sözlüğü.
        """
        self.prediction_label.update_prediction(prediction)
        
        # Son tahminlerin başarı oranlarını kullan (eğer istatistik sözlüğü verilmişse)
        recent_h_accuracy = h_accuracy
        recent_v_accuracy = v_accuracy
        
        if isinstance(h_accuracy, dict) and 'recent_horizontal_accuracy' in h_accuracy:
            recent_h_accuracy = h_accuracy['recent_horizontal_accuracy']
        
        if isinstance(v_accuracy, dict) and 'recent_vertical_accuracy' in v_accuracy:
            recent_v_accuracy = v_accuracy['recent_vertical_accuracy']
        
        # Geliştirilmiş WL tahmin widgetini güncelle
        self.wl_prediction_widget.update_prediction(
            wl_prediction, 
            h_pred, 
            v_pred, 
            reverse_bet,
            recent_h_accuracy if recent_h_accuracy is not None else h_accuracy,
            recent_v_accuracy if recent_v_accuracy is not None else v_accuracy
        )