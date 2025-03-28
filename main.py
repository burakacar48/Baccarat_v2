"""
Baccarat Analiz Uygulaması ana başlatma dosyası.
"""
import sys
import argparse
from PyQt6.QtWidgets import QApplication

# Modülleri doğrudan içe aktar
from models.game_history import GameHistory
from models.prediction import PredictionModel
from models.database import DatabaseManager
from ui.main_window import MainWindow

# Veritabanı başlatıcıyı içe aktar
from database_initializer import initialize_all_data

def main():
    """Uygulamayı başlatır."""
    # Komut satırı argümanlarını işle
    parser = argparse.ArgumentParser(description='Baccarat Analiz & Tahmin Uygulaması')
    parser.add_argument('--init-db', action='store_true', help='Veritabanını test verileriyle başlat')
    args = parser.parse_args()
    
    # Veritabanını başlat (istenirse)
    if args.init_db:
        initialize_all_data()
    
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