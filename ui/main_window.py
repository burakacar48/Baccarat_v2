"""
Ana uygulama penceresi modülü.
"""
import sys
import random
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QMessageBox
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont

from config import WINDOW_TITLE, INITIAL_KASA, DB_WRITE_INTERVAL
from ui.panels.left_panel import LeftPanel
from ui.panels.right_panel import RightPanel
from ui.dialogs.model_details import ModelDetailsWindow

# Import the baccarat simulator
from baccarat_simulator import get_next_result, is_new_shoe_detected

# Geçici stil fonksiyonları
def get_modern_font():
    """Platform'a göre modern bir font döndürür."""
    if sys.platform == "darwin":
        font = QFont("San Francisco", 11)
    elif sys.platform.startswith("linux"):
        font = QFont("Noto Sans", 10)
    else:
        font = QFont("Segoe UI", 10)
    return font

def get_application_style(font):
    """Basitleştirilmiş stil döndürür."""
    return """
    QMainWindow { 
        background-color: #1e1e1e; 
    }
    
    QWidget { 
        color: #dcdcdc; 
    }
    
    QLabel {
        background-color: transparent;
        border: none;
    }
    
    QGroupBox {
        background-color: #333333;
        border: 1px solid #444444;
        border-radius: 6px;
        margin-top: 18px;
        font-weight: bold;
    }
    
    QPushButton {
        border: none;
        padding: 10px 15px;
        border-radius: 5px;
        font-weight: bold;
        min-height: 28px;
    }
    
    QPushButton#PlayerButton {
        background-color: #0d6efd;
        color: white;
    }
    
    QPushButton#BankerButton {
        background-color: #dc3545;
        color: white;
    }
    """

class MainWindow(QMainWindow):
    """Ana uygulama penceresi."""
    
    def __init__(self, game_history, prediction_model, db_manager):
        """
        Args:
            game_history (GameHistory): Oyun geçmişi modeli.
            prediction_model (PredictionModel): Tahmin modeli.
            db_manager (DatabaseManager): Veritabanı yöneticisi.
        """
        super().__init__()
        
        # Modeller
        self.game_history = game_history
        self.prediction_model = prediction_model
        self.db_manager = db_manager
        
        # Durum değişkenleri
        self.details_window = None
        
        # Simülasyon değişkenleri
        self.current_hand_in_shoe = 0
        self.pause_simulation = False
        self.simulation_running = False  # Simülasyonun çalışıp çalışmadığını takip etmek için
        
        # Simülasyon zamanlayıcısı
        self.simulation_timer = QTimer(self)
        self.simulation_timer.timeout.connect(self.simulate_step)
        
        # Veritabanı yazma zamanlayıcısı
        self.db_write_timer = QTimer(self)
        self.db_write_timer.timeout.connect(self.flush_db_buffer)
        self.db_write_timer.start(DB_WRITE_INTERVAL)
        
        # WL ağırlık güncelleme zamanlayıcısı
        self.wl_weight_timer = QTimer(self)
        self.wl_weight_timer.timeout.connect(self.update_wl_weights)
        self.wl_weight_timer.start(60000)  # Her 1 dakikada bir
        
        # Arayüz ayarları
        self.setWindowTitle(WINDOW_TITLE)
        self.resize(950, 650)
        
        self.modern_font = get_modern_font()
        self.setFont(self.modern_font)
        
        # Ana düzen
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # Paneller
        self.left_panel = LeftPanel()
        self.right_panel = RightPanel()
        
        self.main_layout.addWidget(self.left_panel, 3)
        self.main_layout.addWidget(self.right_panel, 5)
        
        # Uygulamaya stil uygula
        style_sheet = get_application_style(self.modern_font)
        self.setStyleSheet(style_sheet)
        
        # Sinyalleri bağla
        self._connect_signals()
        
        # İlk güncellemeleri yap
        self._full_ui_update()
        
    def _connect_signals(self):
        """Sinyal bağlantılarını kurar."""
        # Giriş düğmeleri
        self.left_panel.player_button.clicked.connect(lambda: self.add_result('P'))
        self.left_panel.banker_button.clicked.connect(lambda: self.add_result('B'))
        
        # Eylem düğmeleri
        self.left_panel.action_buttons["undo"].clicked.connect(self.undo_last_action)
        self.left_panel.action_buttons["clear"].clicked.connect(self.clear_histories)
        self.left_panel.action_buttons["reset"].clicked.connect(self.reset_all)
        self.left_panel.action_buttons["simulate"].clicked.connect(self.toggle_simulation)
        self.left_panel.action_buttons["stats"].clicked.connect(self.open_model_details_window)
    
    def add_result(self, winner):
        """Yeni bir sonuç ekler.
        
        Args:
            winner (str): Kazananı temsil eden 'P' veya 'B' değeri.
        """
        # Desen türünü belirle
        pattern_type = "mixed"
        if len(self.game_history.win_loss_history) >= 4:
            last_four = self.game_history.win_loss_history[-4:]
            
            # Streak (WWWW veya LLLL)
            if all(x == 'W' for x in last_four) or all(x == 'L' for x in last_four):
                pattern_type = "streak"
            # Alternating (WLWL veya LWLW)
            elif (last_four == ['W', 'L', 'W', 'L'] or last_four == ['L', 'W', 'L', 'W']):
                pattern_type = "alternating"
        
        # Mevcut tahmini al
        current_prediction, should_reverse_bet = self.get_current_prediction()
        
        # Tüm modellerin tahminlerini topla
        model_predictions = self.prediction_model.get_predictions(
            self.game_history.history, 
            self.game_history.win_loss_history
        )
        
        # Kazanç/kayıp durumunu belirle
        is_win = None
        if current_prediction not in ['?', None]:
            is_win = (current_prediction == winner)
        
        # WL tahminlerini game_history'ye kaydet (desen türünü de geçir)
        self.game_history.set_wl_predictions(
            self.prediction_model.wl_model.last_horizontal_pred,
            self.prediction_model.wl_model.last_vertical_pred,
            pattern_type
        )
        
        # Sonucu kaydet (reverse bet durumunu da belirt)
        result_info = self.game_history.add_result(winner, is_win, should_reverse_bet)
        
        # Yeni ayakkabı başlayıp başlamadığını kontrol et
        # Direkt baccarat_simulator'dan yeni shoe durumunu kontrol et
        new_shoe_detected = is_new_shoe_detected()
        
        if new_shoe_detected:
            print("Manuel girişte yeni shoe tespit edildi!")
            # Yeni shoe başladığında veritabanını da bilgilendir
            if self.db_manager:
                self.db_manager.new_shoe_detected()
                
            # Adaptif modeli de bilgilendir
            if hasattr(self.prediction_model, 'set_current_shoe_id'):
                self.prediction_model.set_current_shoe_id(self.db_manager.current_shoe_id)
            
            # Simülasyon için bahis yapma modunu sıfırla
            self.pause_simulation = False
        
        # Veritabanına ekle
        self.db_manager.add_result(winner)
        
        # Model doğruluk oranlarını güncelle
        self.prediction_model.update_model_accuracy(winner, model_predictions)
        
        # WL tahmin ağırlıklarını güncelle
        self.update_wl_weights()
        
        # UI'yi güncelle
        self._full_ui_update()
        
        # Sonuç bilgisi göster
        if is_win is not None:
            result_str = "Kazandı!" if is_win else "Kaybetti!"
            bet_change_str = f"+{result_info['current_bet']:.2f}" if is_win else f"-{result_info['current_bet']:.2f}"
            bet_type_str = "Ters bahis" if should_reverse_bet else "Normal bahis"
            print(f"{result_str} {bet_change_str} TL ({bet_type_str}). Yeni Kasa: {self.game_history.kasa:.2f}.")
    
    def get_current_prediction(self):
        """Mevcut tahmini döndürür.
        
        Returns:
            tuple: (prediction, should_reverse_bet) - Tahmin değeri ('P', 'B' veya '?') ve ters bahis yapılıp yapılmayacağı.
        """
        # Önce desen türünü belirle
        pattern_type = "mixed"
        if len(self.game_history.win_loss_history) >= 4:
            last_four = self.game_history.win_loss_history[-4:]
            
            # Streak (WWWW veya LLLL)
            if all(x == 'W' for x in last_four) or all(x == 'L' for x in last_four):
                pattern_type = "streak"
            # Alternating (WLWL veya LWLW)
            elif (last_four == ['W', 'L', 'W', 'L'] or last_four == ['L', 'W', 'L', 'W']):
                pattern_type = "alternating"
        
        # WL based prediction with possible reverse bet, desen türünü de geçir
        prediction, should_reverse_bet = self.prediction_model.get_best_model_prediction(
            self.game_history.history,
            self.game_history.win_loss_history,
            pattern_type=pattern_type
        )
        
        return prediction, should_reverse_bet
    
    def flush_db_buffer(self):
        """Veritabanı tamponunu temizler."""
        self.db_manager.flush_buffer()
    
    def update_wl_weights(self):
        """WL tahmin ağırlıklarını günceller."""
        stats = self.game_history.get_statistics()
        
        # Son tahminlerin başarı oranlarını kullan (daha dinamik güncelleme)
        h_rate, v_rate = self.game_history.get_recent_wl_success_rates()
        
        # Eğer son başarı oranları mevcutsa (yeterli tahmin yapıldıysa) onları kullan
        if len(self.game_history.recent_horizontal_results) >= 5 and len(self.game_history.recent_vertical_results) >= 5:
            self.prediction_model.wl_model.update_weights(h_rate, v_rate, momentum=0.7)
        # Değilse genel başarı oranlarını kullan
        elif 'horizontal_wl_accuracy' in stats and 'vertical_wl_accuracy' in stats:
            self.prediction_model.wl_model.update_weights(
                stats['horizontal_wl_accuracy'] / 100.0,
                stats['vertical_wl_accuracy'] / 100.0,
                momentum=0.7
            )
    
    def toggle_simulation(self):
        """Simülasyonu başlatır veya durdurur."""
        if self.simulation_running:
            # Eğer simülasyon çalışıyorsa, durdur
            self.simulation_timer.stop()
            self.simulation_running = False
            self.left_panel.action_buttons["simulate"].setText("▶️")
            self.left_panel.action_buttons["simulate"].setToolTip("Gerçek Baccarat Simüle Et")
            print("Simülasyon durduruldu.")
        else:
            # Eğer simülasyon çalışmıyorsa, başlat
            self.simulation_timer.start(100)  # 100ms aralıklarla simülasyon
            self.simulation_running = True
            self.left_panel.action_buttons["simulate"].setText("⏹️")
            self.left_panel.action_buttons["simulate"].setToolTip("Simülasyonu Durdur")
            # Pause durumunu sıfırla, kullanıcı başlattığında her zaman baştan bahis yapmasını sağlar
            self.pause_simulation = False
            print("Simülasyon başlatıldı, bahis yapma modu etkin.")
    
    def undo_last_action(self):
        """Son eklenen sonucu geri alır."""
        if self.game_history.undo_last_action():
            self._full_ui_update()
            print("Son hamle geri alındı (Kasa/Bet/Model Stats/DB etkilenmedi).")
        else:
            print("Geri alınacak hamle yok.")
    
    def clear_histories(self):
        """Geçmiş verilerini temizler."""
        confirm = QMessageBox.question(
            self,
            "Geçmişi Temizle",
            "Tüm geçmiş verileri temizlenecek. Devam etmek istiyor musunuz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            self.game_history.clear_histories()
            self.prediction_model.reset_models()
            
            # Mevcut shoe veritabanı verilerini temizle
            if self.db_manager:
                self.db_manager.clear_current_shoe_data()
                
            # Simülasyon değişkenlerini sıfırla
            self.current_hand_in_shoe = 0
            self.pause_simulation = False
            self._full_ui_update()
            print("Geçmişler temizlendi.")
    
    def reset_all(self):
        """Tüm verileri sıfırlar."""
        confirm = QMessageBox.question(
            self,
            "Her Şeyi Sıfırla",
            "Kasa dahil tüm veriler sıfırlanacak. Devam etmek istiyor musunuz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            self.game_history.reset()
            self.prediction_model.reset_models()
            
            # Tüm veritabanı verilerini temizle
            if self.db_manager:
                self.db_manager.clear_table()
                
            # Adaptif model için de shoe ID'yi sıfırla
            if hasattr(self.prediction_model, 'set_current_shoe_id'):
                self.prediction_model.set_current_shoe_id(1)
                
            # Simülasyon değişkenlerini sıfırla
            self.current_hand_in_shoe = 0
            self.pause_simulation = False
            self._full_ui_update()
            print("Her şey sıfırlandı.")
    
    def simulate_step(self):
        """Bir adım baccarat simülasyonu yapar."""
        # Use the enhanced baccarat simulator
        winner = get_next_result()  # This will return 'P' or 'B' according to proper baccarat rules
        
        # Shoe değişimini kontrol et - doğrudan baccarat_simulator'dan sorgula
        new_shoe_detected = is_new_shoe_detected()
        
        if new_shoe_detected:
            print("Simülasyonda yeni shoe tespit edildi! Bahis yapma modu etkinleştiriliyor.")
            # Yeni shoe başladığında veritabanını da bilgilendir
            if self.db_manager:
                self.db_manager.new_shoe_detected()
                
            # Adaptif modeli de bilgilendir
            if hasattr(self.prediction_model, 'set_current_shoe_id'):
                self.prediction_model.set_current_shoe_id(self.db_manager.current_shoe_id)
            
            # Yeni shoe başladığında geçmiş verileri temizle
            self.game_history.clear_histories()
            self.current_hand_in_shoe = 0
            
            # Yeni shoe'da her zaman bahis yapmalıyız
            self.pause_simulation = False
            print("Yeni shoe başladı, geçmiş temizlendi, simülasyon bahis yaparak devam ediyor.")
        
        # El sayısını arttır
        self.current_hand_in_shoe += 1
        
        # Bahis yapılıp yapılmayacağını belirle
        if self.pause_simulation:
            # Bahis yapmadan devam et
            self.game_history.history.append(winner)
            self.game_history._rebuild_grid_from_history()
            # Veritabanına ekle
            self.db_manager.add_result(winner)
            # UI'yi güncelle
            self._full_ui_update()
            print(f"Simülasyon: El #{self.current_hand_in_shoe} - Sonuç: {winner} - Bahis yapılmıyor (izleme modu)")
        else:
            # Desen türünü belirle
            pattern_type = "mixed"
            if len(self.game_history.win_loss_history) >= 4:
                last_four = self.game_history.win_loss_history[-4:]
                
                # Streak (WWWW veya LLLL)
                if all(x == 'W' for x in last_four) or all(x == 'L' for x in last_four):
                    pattern_type = "streak"
                # Alternating (WLWL veya LWLW)
                elif (last_four == ['W', 'L', 'W', 'L'] or last_four == ['L', 'W', 'L', 'W']):
                    pattern_type = "alternating"
            
            # Bahis yaparak devam et
            # Mevcut tahmini al (ve ters bahis yapılıp yapılmayacağını)
            current_prediction, should_reverse_bet = self.get_current_prediction()
            
            # WL tahminlerini kaydet
            self.game_history.set_wl_predictions(
                self.prediction_model.wl_model.last_horizontal_pred,
                self.prediction_model.wl_model.last_vertical_pred,
                pattern_type
            )
            
            # Tahmini kontrol et ve kazanıp kazanmadığını belirle
            is_win = None
            if current_prediction not in ['?', None]:
                is_win = (current_prediction == winner)
            
            # Sonucu ekle (bahisle birlikte)
            result_info = self.game_history.add_result(winner, is_win, should_reverse_bet)
            
            # Veritabanına ekle
            self.db_manager.add_result(winner)
            
            # Tüm modellerin tahminlerini topla
            model_predictions = self.prediction_model.get_predictions(
                self.game_history.history,
                self.game_history.win_loss_history
            )
            
            # Model doğruluk oranlarını güncelle
            self.prediction_model.update_model_accuracy(winner, model_predictions)
            
            # WL ağırlıklarını güncelle
            self.update_wl_weights()
            
            # UI'yi güncelle
            self._full_ui_update()
            
            # Sonuç bilgisi göster
            if is_win is not None:
                result_str = "Kazandı!" if is_win else "Kaybetti!"
                bet_change_str = f"+{result_info['current_bet']:.2f}" if is_win else f"-{result_info['current_bet']:.2f}"
                bet_type_str = "Ters bahis" if should_reverse_bet else "Normal bahis"
                print(f"Simülasyon: El #{self.current_hand_in_shoe} - Sonuç: {winner} - {result_str} {bet_change_str} TL ({bet_type_str}). Yeni Kasa: {self.game_history.kasa:.2f}.")
            
            # 35. elden sonra kazanç durumunda bahis duraklatılır
            if self.current_hand_in_shoe > 35 and is_win:
                self.pause_simulation = True
                print("35. elden sonra kazanç gerçekleşti. Bahis yapma duraklatıldı. Yeni shoe başlayana kadar izleme modunda.")
    
    def open_model_details_window(self):
        """Model detayları penceresini açar."""
        # Önceki pencereyi kapat
        if self.details_window is not None:
            self.details_window.close()
        
        # Yeni pencere oluştur
        self.details_window = ModelDetailsWindow(self.prediction_model.models, self)
        self.details_window.show()
    
    def _full_ui_update(self):
        """Tüm arayüzü günceller."""
        # Grid verilerini güncelle
        self.prediction_model.update_grid_data(self.game_history.grid_data)
        
        # Sol panel güncellemeleri
        stats = self.game_history.get_statistics()
        self.left_panel.update_kasa_stats(stats)
        self.left_panel.update_table_stats(stats)
        
        # Tahmin gösterimini güncelle
        current_prediction, should_reverse_bet = self.get_current_prediction()
        wl_prediction = self.prediction_model.current_wl_prediction
        h_pred = self.prediction_model.current_horizontal_wl_pred
        v_pred = self.prediction_model.current_vertical_wl_pred
        
        # İstatistikleri tahmin gösterimi için ilet
        self.left_panel.update_prediction(
            current_prediction, 
            wl_prediction, 
            should_reverse_bet,
            h_pred,
            v_pred,
            stats,
            stats
        )
        
        # Sağ panel güncellemeleri
        self.right_panel.update_result_grid(self.game_history.grid_data)
        self.right_panel.update_wl_grid(self.game_history.win_loss_history)
        self.right_panel.update_models(self.prediction_model.models)
    
    def closeEvent(self, event):
        """Uygulama kapatılırken çağrılır."""
        # Simülasyonu durdur
        if self.simulation_running:
            self.simulation_timer.stop()
        
        print("Uygulama kapanıyor, DB buffer flush ediliyor...")
        self.flush_db_buffer()
        
        # Adaptif model kaynaklarını serbest bırak
        if hasattr(self, 'prediction_model') and self.prediction_model:
            self.prediction_model.close()
        
        # Veritabanı bağlantısını kapat
        if self.db_manager:
            self.db_manager.close()
            print("Veritabanı bağlantısı kapatıldı.")
        
        super().closeEvent(event)