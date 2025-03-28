"""
WL tahmin sonuçlarını gösteren widget modülü.
"""
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QSizePolicy, QVBoxLayout
from PyQt6.QtCore import Qt
from config import PREDICTION_BG_COLOR, BORDER_COLOR, TEXT_COLOR_DIM, WL_WIN_BG_COLOR, WL_LOSS_BG_COLOR

class WLPredictionWidget(QWidget):
    """Win/Loss tahmin sonucunu gösteren özel widget."""
    
    def __init__(self, parent=None):
        """
        Args:
            parent (QWidget, optional): Ebeveyn widget.
        """
        super().__init__(parent)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 5, 0, 0)
        self.layout.setSpacing(5)
        
        # Title label
        self.title_label = QLabel("WL Tahmini:")
        self.title_label.setObjectName("WLTitleLabel")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Prediction layout
        self.pred_layout = QHBoxLayout()
        self.pred_layout.setContentsMargins(0, 0, 0, 0)
        self.pred_layout.setSpacing(5)
        
        # Prediction label
        self.prediction_label = QLabel("?")
        self.prediction_label.setObjectName("WLPredictionLabel")
        self.prediction_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.prediction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Action label
        self.action_label = QLabel("Normal Bahis")
        self.action_label.setObjectName("WLActionLabel")
        self.action_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.action_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Add widgets to layouts
        self.pred_layout.addWidget(self.prediction_label, 1)
        self.pred_layout.addWidget(self.action_label, 2)
        
        self.layout.addWidget(self.title_label)
        self.layout.addLayout(self.pred_layout)
        
        # Apply default styles
        self._apply_default_styles()
    
    def _apply_default_styles(self):
        """Varsayılan stilleri uygular."""
        self.prediction_label.setStyleSheet(
            f"QLabel#WLPredictionLabel {{ "
            f"background-color: {PREDICTION_BG_COLOR.name()}; "
            f"color: {TEXT_COLOR_DIM.name()}; "
            f"border: 1px solid {BORDER_COLOR.name()}; "
            f"border-radius: 5px; "
            f"padding: 4px; "
            f"}}"
        )
        
        self.action_label.setStyleSheet(
            f"QLabel#WLActionLabel {{ "
            f"background-color: {PREDICTION_BG_COLOR.name()}; "
            f"color: {TEXT_COLOR_DIM.name()}; "
            f"border: 1px solid {BORDER_COLOR.name()}; "
            f"border-radius: 5px; "
            f"padding: 4px; "
            f"}}"
        )
    
    def update_prediction(self, wl_prediction, reverse_bet=False):
        """Tahmin değerini günceller.
        
        Args:
            wl_prediction (str): Tahmin değeri ('W', 'L' veya '?').
            reverse_bet (bool): Ters bahis yapılıp yapılmayacağı
        """
        self.prediction_label.setText(wl_prediction)
        
        bg_color = PREDICTION_BG_COLOR.name()
        text_color = TEXT_COLOR_DIM.name()
        
        if wl_prediction == 'W':
            bg_color = WL_WIN_BG_COLOR.name()
            text_color = 'white'
        elif wl_prediction == 'L':
            bg_color = WL_LOSS_BG_COLOR.name()
            text_color = 'white'
        
        self.prediction_label.setStyleSheet(
            f"QLabel#WLPredictionLabel {{ "
            f"background-color: {bg_color}; "
            f"color: {text_color}; "
            f"border: 1px solid {BORDER_COLOR.name()}; "
            f"border-radius: 5px; "
            f"padding: 4px; "
            f"}}"
        )
        
        # Update action label
        if reverse_bet:
            self.action_label.setText("TERS BAHİS YAP!")
            self.action_label.setStyleSheet(
                f"QLabel#WLActionLabel {{ "
                f"background-color: #FF6B6B; "  # Light red for reverse betting
                f"color: white; "
                f"font-weight: bold; "
                f"border: 1px solid {BORDER_COLOR.name()}; "
                f"border-radius: 5px; "
                f"padding: 4px; "
                f"}}"
            )
        else:
            self.action_label.setText("Normal Bahis")
            self.action_label.setStyleSheet(
                f"QLabel#WLActionLabel {{ "
                f"background-color: #4CAF50; "  # Green for normal betting
                f"color: white; "
                f"border: 1px solid {BORDER_COLOR.name()}; "
                f"border-radius: 5px; "
                f"padding: 4px; "
                f"}}"
            )