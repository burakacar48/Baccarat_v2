"""
Baccarat Analiz Uygulaması için yapılandırma sabitleri.
Bu dosya, uygulamanın tüm yapılandırma ayarlarını ve sabitlerini içerir.
"""
from PyQt6.QtGui import QColor

# --- Genel Ayarlar ---
GRID_SIZE = 5
CELL_SIZE = 60
WINDOW_TITLE = "Modern Baccarat Analiz & Tahmin (Martingale+DB)"
MAX_HISTORY_IN_GRID = GRID_SIZE * GRID_SIZE
WL_GRID_ROWS = 12
WL_GRID_COLS = 2
WL_CELL_SIZE = int(CELL_SIZE * 0.55)
MAX_WL_DISPLAY = WL_GRID_ROWS * WL_GRID_COLS
DB_FILE = 'baccarat_history.db'
DB_LOOKBACK = 4  # Veritabanı modelinde ne kadar geriye bakılacağı (dizi uzunluğu)
DB_WRITE_INTERVAL = 5000  # DB'ye yazma aralığı (milisaniye)

# --- Emojiler ---
UNDO_EMOJI = "↩️"
CLEAR_EMOJI = "🗑️"
RESET_EMOJI = "🔄"
SIMULATE_EMOJI = "▶️"
SIMULATE_MULTI_EMOJI = "🎮"  # Yeni emoji
STATS_EMOJI = "📊"

# --- Renkler ---
DARK_BACKGROUND = QColor("#1e1e1e")
WIDGET_BACKGROUND = QColor("#2b2b2b")
GROUP_BOX_BG = QColor("#333333")
TEXT_COLOR = QColor("#dcdcdc")
TEXT_COLOR_DIM = QColor("#888888")
TEXT_COLOR_ACCENT = QColor("#569cd6")
TEXT_COLOR_POSITIVE = QColor("#28a745")
TEXT_COLOR_NEGATIVE = QColor("#dc3545")
BORDER_COLOR = QColor("#444444")
PLAYER_COLOR = QColor("#0d6efd")
BANKER_COLOR = QColor("#dc3545")
EMPTY_COLOR = WIDGET_BACKGROUND
PREDICTION_BG_COLOR = QColor("#3c3c3c")
BUTTON_ACCENT_COLOR = QColor("#0078d4")
BUTTON_HOVER_COLOR = QColor("#106ebe")
BUTTON_PRESSED_COLOR = QColor("#005a9e")
ACTION_BUTTON_COLOR = QColor("#4a4a4a")
ACTION_BUTTON_HOVER = QColor("#5a5a5a")
ACTION_BUTTON_PRESSED = QColor("#3a3a3a")
WL_WIN_BG_COLOR = QColor("#198754")
WL_LOSS_BG_COLOR = QColor("#dc3545")
WL_TEXT_COLOR = QColor("white")

# --- Martingale Ayarları ---
INITIAL_KASA = 5000.00
MARTINGALE_SEQUENCE = [4.00, 12.00, 32.00, 68.00, 144.00, 300.00, 620.00, 1300.00, 2660.00]