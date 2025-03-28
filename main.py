"""
Baccarat Analiz Uygulaması ana başlatma dosyası.
"""
import sys
from PyQt6.QtWidgets import QApplication

# Modülleri doğrudan içe aktar
from models.game_history import GameHistory
from models.prediction import PredictionModel
from models.database import DatabaseManager
from ui.main_window import MainWindow

def main():
    """Uygulamayı başlatır."""
    # QApplication oluştur
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Model nesnelerini oluştur
    game_history = GameHistory()
    prediction_model = PredictionModel()
    db_manager = DatabaseManager()
    
    # Veritabanı tahmin işlevini PredictionModel'e bağla
    prediction_model.set_db_prediction_function(
        lambda history: db_manager.predict_from_history(history)
    )
    
    # Ana pencereyi oluştur ve göster
    main_window = MainWindow(game_history, prediction_model, db_manager)
    main_window.show()
    
    # Uygulamayı çalıştır
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
