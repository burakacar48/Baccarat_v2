"""
Sonuçları ızgara görünümünde gösteren widget modülü.
"""
from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel
from PyQt6.QtCore import Qt
from config import CELL_SIZE, GRID_SIZE, BORDER_COLOR, EMPTY_COLOR, TEXT_COLOR_DIM, PLAYER_COLOR, BANKER_COLOR, WL_WIN_BG_COLOR, WL_LOSS_BG_COLOR

class ResultGridWidget(QWidget):
    """Oyun sonuçlarını ızgara şeklinde gösteren widget."""
    
    def __init__(self, parent=None):
        """
        Args:
            parent (QWidget, optional): Ebeveyn widget.
        """
        super().__init__(parent)
        
        self.grid_layout = QGridLayout(self)
        self.grid_layout.setSpacing(4)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        
        self.grid_labels = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        self._init_grid()
    
    def _init_grid(self):
        """Izgara etiketlerini başlatır."""
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                label = QLabel("")
                label.setObjectName("GridLabel")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                self.grid_labels[r][c] = label
                self.grid_layout.addWidget(label, r, c)
    
    def update_display(self, grid_data):
        """Izgara görünümünü günceller.
        
        Args:
            grid_data (list): 2D grid verileri.
        """
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                label = self.grid_labels[r][c]
                if not label:
                    continue
                    
                value = grid_data[r][c]
                cell_style = self._get_grid_cell_style(value)
                
                label.setText(cell_style['text'])
                label.setStyleSheet(
                    f"QLabel#GridLabel {{ "
                    f"background-color: {cell_style['bg_color']}; "
                    f"color: {cell_style['text_color']}; "
                    f"border: 1px solid {BORDER_COLOR.name()}; "
                    f"border-radius: 4px; "
                    f"}}"
                )
    
    def _get_grid_cell_style(self, value):
        """Grid hücresi için stil değerleri döndürür."""
        if value == 'P':
            return {
                'text': 'P',
                'bg_color': PLAYER_COLOR.name(),
                'text_color': 'white'
            }
        elif value == 'B':
            return {
                'text': 'B',
                'bg_color': BANKER_COLOR.name(),
                'text_color': 'white'
            }
        else:
            return {
                'text': '',
                'bg_color': EMPTY_COLOR.name(),
                'text_color': TEXT_COLOR_DIM.name()
            }

class WinLossGridWidget(QWidget):
    """Kazanma/Kaybetme geçmişini ızgara şeklinde gösteren widget."""
    
    def __init__(self, rows, cols, parent=None):
        """
        Args:
            rows (int): Satır sayısı.
            cols (int): Sütun sayısı.
            parent (QWidget, optional): Ebeveyn widget.
        """
        super().__init__(parent)
        
        self.rows = rows
        self.cols = cols
        
        self.layout = QGridLayout(self)
        self.layout.setSpacing(3)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.grid_labels = [[None for _ in range(cols)] for _ in range(rows)]
        
        self._init_grid()
    
    def _init_grid(self):
        """Izgara etiketlerini başlatır."""
        for r in range(self.rows):
            for c in range(self.cols):
                label = QLabel("")
                label.setObjectName("WlGridLabel")
                
                self.grid_labels[r][c] = label
                self.layout.addWidget(label, r, c)
    
    def update_display(self, wl_history, max_display):
        """Izgara görünümünü günceller.
        
        Args:
            wl_history (list): Kazanma/Kaybetme geçmişi.
            max_display (int): Maksimum gösterilecek öğe sayısı.
        """
        # Tüm hücreleri temizle
        for r in range(self.rows):
            for c in range(self.cols):
                label = self.grid_labels[r][c]
                if label:
                    label.setText("")
                    label.setStyleSheet(
                        f"QLabel#WlGridLabel {{ "
                        f"background-color: {EMPTY_COLOR.name()}; "
                        f"color: {TEXT_COLOR_DIM.name()}; "
                        f"border: 1px solid {BORDER_COLOR.name()}; "
                        f"border-radius: 3px; "
                        f"}}"
                    )
        
        # Geçmiş verilerini alıp görüntüle
        wl_slice = list(wl_history)[-max_display:]
        slice_idx = 0
        
        for r in range(self.rows):
            for c in range(self.cols):
                if slice_idx >= len(wl_slice):
                    break
                    
                label = self.grid_labels[r][c]
                value = wl_slice[slice_idx]
                cell_style = self._get_wl_cell_style(value)
                
                if label:
                    label.setText(cell_style['text'])
                    label.setStyleSheet(
                        f"QLabel#WlGridLabel {{ "
                        f"background-color: {cell_style['bg_color']}; "
                        f"color: {cell_style['text_color']}; "
                        f"border: 1px solid {BORDER_COLOR.name()}; "
                        f"border-radius: 3px; "
                        f"}}"
                    )
                
                slice_idx += 1
                
            if slice_idx >= len(wl_slice):
                break
    
    def _get_wl_cell_style(self, value):
        """Kazanma/Kaybetme hücresi için stil değerleri döndürür."""
        if value == 'W':
            return {
                'text': 'W',
                'bg_color': WL_WIN_BG_COLOR.name(),
                'text_color': 'white'
            }
        elif value == 'L':
            return {
                'text': 'L',
                'bg_color': WL_LOSS_BG_COLOR.name(),
                'text_color': 'white'
            }
        else:
            return {
                'text': '',
                'bg_color': EMPTY_COLOR.name(),
                'text_color': TEXT_COLOR_DIM.name()
            }