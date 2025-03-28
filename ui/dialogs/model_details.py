"""
Model detayları iletişim kutusu modülü.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout,
    QGroupBox, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt
from config import DARK_BACKGROUND, GROUP_BOX_BG, BORDER_COLOR, TEXT_COLOR, TEXT_COLOR_DIM, TEXT_COLOR_ACCENT

class ModelDetailsWindow(QDialog):
    """Tüm modellerin detaylarını gösteren ayrı pencere."""
    
    def __init__(self, models_data, parent=None):
        """
        Args:
            models_data (list): Model verileri listesi.
            parent (QWidget, optional): Ebeveyn widget.
        """
        super().__init__(parent)
        self.models_data = models_data
        self.setWindowTitle("Model Performans Detayları")
        self.setMinimumSize(450, 400)
        self.setModal(True)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("ModelDetailsScroll")
        
        self.scroll_content_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_content_widget)
        
        self.scroll_layout = QVBoxLayout(self.scroll_content_widget)
        self.scroll_layout.setContentsMargins(15, 15, 15, 15)
        self.scroll_layout.setSpacing(15)

        self.main_layout.addWidget(self.scroll_area)

        self._populate_models()
        self._apply_styles()

    def _apply_styles(self):
        """İletişim kutusuna stil uygular."""
        style = f"""
            QDialog {{ 
                background-color: {DARK_BACKGROUND.name()}; 
            }}
            
            QScrollArea#ModelDetailsScroll {{ 
                border: none; 
            }}
            
            QWidget {{ 
                background-color: {DARK_BACKGROUND.name()}; 
                color: {TEXT_COLOR.name()}; 
            }}
            
            QGroupBox {{ 
                background-color: {GROUP_BOX_BG.name()}; 
                border: 1px solid {BORDER_COLOR.name()}; 
                border-radius: 6px; 
                margin-top: 15px; 
                padding: 10px; 
                font-weight: bold; 
            }}
            
            QGroupBox::title {{ 
                subcontrol-origin: margin; 
                subcontrol-position: top left; 
                padding: 2px 8px; 
                margin-left: 10px; 
                background-color: {GROUP_BOX_BG.name()}; 
                border-radius: 4px; 
                color: {TEXT_COLOR.name()}; 
            }}
            
            QLabel#DetailLabel {{ 
                color: {TEXT_COLOR_DIM.name()}; 
                font-size: 9pt; 
            }}
            
            QLabel#DetailValue {{ 
                color: {TEXT_COLOR.name()}; 
                font-weight: bold; 
                font-size: 10pt; 
            }}
            
            QLabel#AccuracyValue {{ 
                color: {TEXT_COLOR_ACCENT.name()}; 
                font-weight: bold; 
                font-size: 11pt; 
            }}
        """
        self.setStyleSheet(style)

    def _populate_models(self):
        """Model verilerine göre arayüzü doldurur."""
        sorted_models = sorted(self.models_data, key=lambda m: m['accuracy'], reverse=True)
        
        for model in sorted_models:
            model_group = QGroupBox(model['name'])
            model_layout = QGridLayout(model_group)
            model_layout.setSpacing(8)
            
            # Toplam tahmin
            lbl_total = QLabel("Toplam Tahmin:")
            lbl_total.setObjectName("DetailLabel")
            val_total = QLabel(str(model['total']))
            val_total.setObjectName("DetailValue")
            model_layout.addWidget(lbl_total, 0, 0)
            model_layout.addWidget(val_total, 0, 1, Qt.AlignmentFlag.AlignRight)
            
            # Doğru tahmin
            lbl_wins = QLabel("Doğru Tahmin:")
            lbl_wins.setObjectName("DetailLabel")
            val_wins = QLabel(str(model['wins']))
            val_wins.setObjectName("DetailValue")
            model_layout.addWidget(lbl_wins, 1, 0)
            model_layout.addWidget(val_wins, 1, 1, Qt.AlignmentFlag.AlignRight)
            
            # Başarı oranı
            lbl_acc = QLabel("Başarı Oranı:")
            lbl_acc.setObjectName("DetailLabel")
            val_acc = QLabel(f"{model['accuracy']:.1f}%")
            val_acc.setObjectName("AccuracyValue")
            model_layout.addWidget(lbl_acc, 2, 0)
            model_layout.addWidget(val_acc, 2, 1, Qt.AlignmentFlag.AlignRight)
            
            self.scroll_layout.addWidget(model_group)
            
        self.scroll_layout.addStretch(1)