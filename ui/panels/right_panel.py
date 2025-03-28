"""
Uygulama arayüzünün sağ paneli.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QFrame
)
from PyQt6.QtCore import Qt
from config import WL_GRID_ROWS, WL_GRID_COLS, MAX_WL_DISPLAY
from ui.widgets.grid_display import ResultGridWidget, WinLossGridWidget

class ModelStatRowWidget(QWidget):
    """Model istatistik satırını gösteren widget."""
    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.name_label = QLabel(f"{index+1}. Model:")
        self.name_label.setObjectName("MainModelNameLabel")
        
        self.accuracy_label = QLabel("N/A")
        self.accuracy_label.setObjectName("MainModelAccuracyLabel")
        self.accuracy_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.accuracy_label)
    
    def update(self, model_name, accuracy):
        self.name_label.setText(model_name)
        self.accuracy_label.setText(accuracy)

class ModelStatWidget(QWidget):
    """Model istatistiklerini gösteren widget."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(6)
        
        self.model_rows = []
        
        for i in range(3):
            row = ModelStatRowWidget(i)
            self.model_rows.append(row)
            self.layout.addWidget(row)
    
    def update_models(self, models, min_predictions=5):
        # Yeterli tahmini olan modelleri sırala
        ranked_models = sorted(
            [m for m in models if m['total'] >= min_predictions],
            key=lambda m: m['accuracy'],
            reverse=True
        )
        
        # Model satırlarını güncelle
        for i, row in enumerate(self.model_rows):
            if i < len(ranked_models):
                model = ranked_models[i]
                row.update(f"{i+1}. {model['name']}:", f"{model['accuracy']:.1f}%")
            else:
                row.update(f"{i+1}. Model:", "N/A")

class RightPanel(QWidget):
    """Uygulamanın sağ panel bileşeni."""
    
    def __init__(self, parent=None):
        """
        Args:
            parent (QWidget, optional): Ebeveyn widget.
        """
        super().__init__(parent)
        self.setObjectName("RightPanel")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(15)
        
        # Alt bileşenler
        self.model_stat_widget = None
        self.result_grid_widget = None
        self.wl_grid_widget = None
        
        self._init_ui()
    
    def _init_ui(self):
        """Kullanıcı arayüzünü başlatır."""
        self._create_model_stats_ui()
        self._create_results_history_ui()
        
        # Alt boşluk ekle
        self.layout.addStretch(1)
    
    def _create_model_stats_ui(self):
        """Model istatistikleri bölümünü oluşturur."""
        model_group_box = QGroupBox("Başarılı Modeller")
        model_layout = QVBoxLayout(model_group_box)
        model_layout.setContentsMargins(10, 10, 10, 10)
        
        self.model_stat_widget = ModelStatWidget()
        model_layout.addWidget(self.model_stat_widget)
        
        self.layout.addWidget(model_group_box)
    
    def _create_results_history_ui(self):
        """Sonuç geçmişi bölümünü oluşturur."""
        results_group_box = QGroupBox("Geçmiş & Performans")
        results_group_layout = QHBoxLayout(results_group_box)
        results_group_layout.setContentsMargins(10, 10, 10, 10)
        results_group_layout.setSpacing(10)
        
        # Sonuç ızgarası
        grid_container = QWidget()
        grid_container_layout = QVBoxLayout(grid_container)
        grid_container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.result_grid_widget = ResultGridWidget()
        grid_container_layout.addWidget(self.result_grid_widget)
        
        results_group_layout.addWidget(grid_container, 4)
        
        # Ayırıcı çizgi
        separator = QFrame()
        separator.setObjectName("SeparatorLine")
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        results_group_layout.addWidget(separator, 0)
        
        # W/L ızgarası
        wl_container = QWidget()
        wl_v_layout = QVBoxLayout(wl_container)
        wl_v_layout.setContentsMargins(0, 0, 0, 0)
        wl_v_layout.setSpacing(5)
        
        # W/L başlığı
        wl_title = QLabel("W / L")
        wl_title.setObjectName("WlTitleLabel")
        wl_v_layout.addWidget(wl_title)
        
        # W/L ızgarası
        self.wl_grid_widget = WinLossGridWidget(WL_GRID_ROWS, WL_GRID_COLS)
        wl_v_layout.addWidget(self.wl_grid_widget)
        wl_v_layout.addStretch(1)
        
        results_group_layout.addWidget(wl_container, 1)
        
        self.layout.addWidget(results_group_box)
    
    def update_models(self, models, min_predictions=5):
        """Model istatistiklerini günceller.
        
        Args:
            models (list): Model verileri listesi.
            min_predictions (int, optional): Minimum tahmin sayısı.
        """
        self.model_stat_widget.update_models(models, min_predictions)
    
    def update_result_grid(self, grid_data):
        """Sonuç ızgarasını günceller.
        
        Args:
            grid_data (list): 2D grid verileri.
        """
        self.result_grid_widget.update_display(grid_data)
    
    def update_wl_grid(self, wl_history):
        """Kazanma/Kaybetme ızgarasını günceller.
        
        Args:
            wl_history (list): Kazanma/Kaybetme geçmişi.
        """
        self.wl_grid_widget.update_display(wl_history, MAX_WL_DISPLAY)