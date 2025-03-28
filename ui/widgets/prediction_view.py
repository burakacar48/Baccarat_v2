"""
Tahmin sonuçlarını gösteren widget modülü.
"""
from PyQt6.QtWidgets import QLabel, QSizePolicy
from PyQt6.QtCore import Qt
from config import PREDICTION_BG_COLOR, BORDER_COLOR, TEXT_COLOR_DIM, PLAYER_COLOR, BANKER_COLOR

class PredictionLabel(QLabel):
    """Tahmin sonucunu gösteren özel etiket."""
    
    def __init__(self, parent=None):
        """
        Args:
            parent (QWidget, optional): Ebeveyn widget.
        """
        super().__init__("?", parent)
        
        self.setObjectName("PredictionLabel")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Varsayılan stil
        self.setStyleSheet(
            f"QLabel#PredictionLabel {{ "
            f"background-color: {PREDICTION_BG_COLOR.name()}; "
            f"color: {TEXT_COLOR_DIM.name()}; "
            f"border: 1px solid {BORDER_COLOR.name()}; "
            f"border-radius: 5px; "
            f"padding: 8px; "
            f"}}"
        )
    
    def update_prediction(self, prediction):
        """Tahmin değerini günceller.
        
        Args:
            prediction (str): Tahmin değeri ('P', 'B' veya '?').
        """
        self.setText(prediction)
        
        bg_color = PREDICTION_BG_COLOR.name()
        text_color = TEXT_COLOR_DIM.name()
        
        if prediction == 'P':
            bg_color = PLAYER_COLOR.name()
            text_color = 'white'
        elif prediction == 'B':
            bg_color = BANKER_COLOR.name()
            text_color = 'white'
        
        self.setStyleSheet(
            f"QLabel#PredictionLabel {{ "
            f"background-color: {bg_color}; "
            f"color: {text_color}; "
            f"border: 1px solid {BORDER_COLOR.name()}; "
            f"border-radius: 5px; "
            f"padding: 8px; "
            f"}}"
        )