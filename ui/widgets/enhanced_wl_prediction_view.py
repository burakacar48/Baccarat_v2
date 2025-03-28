"""
Geliştirilmiş WL tahmin sonuçlarını gösteren widget modülü.
"""
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QSizePolicy, QVBoxLayout, QGridLayout
from PyQt6.QtCore import Qt
from config import PREDICTION_BG_COLOR, BORDER_COLOR, TEXT_COLOR_DIM, WL_WIN_BG_COLOR, WL_LOSS_BG_COLOR

class EnhancedWLPredictionWidget(QWidget):
    """Yatay ve dikey Win/Loss tahmin sonuçlarını gösteren widget."""
    
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
        
        # Prediction grid layout
        self.pred_grid = QGridLayout()
        self.pred_grid.setContentsMargins(0, 0, 0, 0)
        self.pred_grid.setSpacing(5)
        
        # Horizontal prediction
        self.h_label = QLabel("Yatay:")
        self.h_label.setObjectName("WLTypeLabel")
        
        self.h_prediction = QLabel("?")
        self.h_prediction.setObjectName("WLHorizontalPredLabel")
        self.h_prediction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.h_accuracy = QLabel("N/A")
        self.h_accuracy.setObjectName("WLAccuracyLabel")
        self.h_accuracy.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Vertical prediction
        self.v_label = QLabel("Dikey:")
        self.v_label.setObjectName("WLTypeLabel")
        
        self.v_prediction = QLabel("?")
        self.v_prediction.setObjectName("WLVerticalPredLabel")
        self.v_prediction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.v_accuracy = QLabel("N/A")
        self.v_accuracy.setObjectName("WLAccuracyLabel")
        self.v_accuracy.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Final prediction
        self.f_label = QLabel("Final:")
        self.f_label.setObjectName("WLFinalLabel")
        
        self.f_prediction = QLabel("?")
        self.f_prediction.setObjectName("WLFinalPredLabel")
        self.f_prediction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Action label
        self.action_label = QLabel("Normal Bahis")
        self.action_label.setObjectName("WLActionLabel")
        self.action_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.action_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Grid layout'a widgetları ekle
        self.pred_grid.addWidget(self.h_label, 0, 0)
        self.pred_grid.addWidget(self.h_prediction, 0, 1)
        self.pred_grid.addWidget(self.h_accuracy, 0, 2)
        
        self.pred_grid.addWidget(self.v_label, 1, 0)
        self.pred_grid.addWidget(self.v_prediction, 1, 1)
        self.pred_grid.addWidget(self.v_accuracy, 1, 2)
        
        self.pred_grid.addWidget(self.f_label, 2, 0)
        self.pred_grid.addWidget(self.f_prediction, 2, 1, 1, 2)
        
        # Ana layout'a ekle
        self.layout.addWidget(self.title_label)
        self.layout.addLayout(self.pred_grid)
        self.layout.addWidget(self.action_label)
        
        # Default stilleri uygula
        self._apply_default_styles()
    
    def _apply_default_styles(self):
        """Varsayılan stilleri uygular."""
        # Prediction labels
        for label in [self.h_prediction, self.v_prediction, self.f_prediction]:
            label.setStyleSheet(
                f"QLabel {{ "
                f"background-color: {PREDICTION_BG_COLOR.name()}; "
                f"color: {TEXT_COLOR_DIM.name()}; "
                f"border: 1px solid {BORDER_COLOR.name()}; "
                f"border-radius: 5px; "
                f"padding: 4px; "
                f"min-width: 30px; "
                f"}}"
            )
        
        # Action label
        self.action_label.setStyleSheet(
            f"QLabel#WLActionLabel {{ "
            f"background-color: {PREDICTION_BG_COLOR.name()}; "
            f"color: {TEXT_COLOR_DIM.name()}; "
            f"border: 1px solid {BORDER_COLOR.name()}; "
            f"border-radius: 5px; "
            f"padding: 4px; "
            f"}}"
        )
        
        # Final label
        self.f_label.setStyleSheet(
            f"QLabel#WLFinalLabel {{ "
            f"font-weight: bold; "
            f"}}"
        )
    
    def _set_prediction_style(self, label, prediction):
        """Tahmin etiketine uygun stili uygular.
        
        Args:
            label (QLabel): Stil uygulanacak etiket.
            prediction (str): Tahmin değeri ('W', 'L' veya '?').
        """
        bg_color = PREDICTION_BG_COLOR.name()
        text_color = TEXT_COLOR_DIM.name()
        
        if prediction == 'W':
            bg_color = WL_WIN_BG_COLOR.name()
            text_color = 'white'
        elif prediction == 'L':
            bg_color = WL_LOSS_BG_COLOR.name()
            text_color = 'white'
        
        label.setStyleSheet(
            f"QLabel {{ "
            f"background-color: {bg_color}; "
            f"color: {text_color}; "
            f"border: 1px solid {BORDER_COLOR.name()}; "
            f"border-radius: 5px; "
            f"padding: 4px; "
            f"min-width: 30px; "
            f"}}"
        )
    
    def update_prediction(self, final_prediction, horizontal_pred='?', vertical_pred='?', 
                         reverse_bet=False, h_accuracy=None, v_accuracy=None):
        """Tahmin değerlerini günceller.
        
        Args:
            final_prediction (str): Final tahmin değeri ('W', 'L' veya '?').
            horizontal_pred (str): Yatay tahmin değeri ('W', 'L' veya '?').
            vertical_pred (str): Dikey tahmin değeri ('W', 'L' veya '?').
            reverse_bet (bool): Ters bahis yapılıp yapılmayacağı.
            h_accuracy (float): Yatay tahmin doğruluk oranı.
            v_accuracy (float): Dikey tahmin doğruluk oranı.
        """
        # Tahmin etiketlerini güncelle
        self.h_prediction.setText(horizontal_pred)
        self.v_prediction.setText(vertical_pred)
        self.f_prediction.setText(final_prediction)
        
        # Doğruluk oranlarını güncelle
        if h_accuracy is not None:
            self.h_accuracy.setText(f"{h_accuracy:.1f}%")
        
        if v_accuracy is not None:
            self.v_accuracy.setText(f"{v_accuracy:.1f}%")
        
        # Stilleri uygula
        self._set_prediction_style(self.h_prediction, horizontal_pred)
        self._set_prediction_style(self.v_prediction, vertical_pred)
        self._set_prediction_style(self.f_prediction, final_prediction)
        
        # Eylem etiketini güncelle
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