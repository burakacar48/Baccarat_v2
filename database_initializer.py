"""
bbaccarat uygulaması için veritabanı başlatma araçları.
Bu modül, test verisi oluşturarak adaptif öğrenme ve veritabanı modellerini başlatır.
"""
import random
import sqlite3
from collections import Counter

from config import DB_FILE, GRID_SIZE
from models.adaptive_learning import AdaptiveLearningModel
from models.database import DatabaseManager

def initialize_adaptive_learning_data():
    """Adaptif öğrenme modelini test verileriyle başlatır."""
    model = AdaptiveLearningModel()
    
    # Bazı yaygın desenler için hatalı tahminler ekleyelim
    test_patterns = [
        ("PBPB", "P"),  # PBPB deseni sonrası P tahmini yanlış olsun
        ("BPBP", "B"),  # BPBP deseni sonrası B tahmini yanlış olsun
        ("PPPP", "P"),  # PPPP deseni sonrası P tahmini yanlış olsun
        ("BBBB", "B"),  # BBBB deseni sonrası B tahmini yanlış olsun
        ("PBPP", "B"),  # PBPP deseni sonrası B tahmini yanlış olsun
        ("BPPB", "P")   # BPPB deseni sonrası P tahmini yanlış olsun
    ]
    
    for pattern, wrong_pred in test_patterns:
        # Her deseni birkaç kez kaydet (frekansı artırmak için)
        for _ in range(3):
            model.record_mistake(pattern, wrong_pred)
    
    print("Adaptif öğrenme modeli test verileriyle başlatıldı.")
    model.close()

def initialize_grid_mistake_patterns():
    """Grid tabanlı adaptif öğrenme modeli için test verileri oluşturur."""
    model = AdaptiveLearningModel()
    
    # Örnek grid verileri oluştur
    all_p_grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    all_b_grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    
    # Grid'leri doldur - sağ alt 3x3 bölgeler
    for r in range(GRID_SIZE-3, GRID_SIZE):
        for c in range(GRID_SIZE-3, GRID_SIZE):
            all_p_grid[r][c] = "P"
            all_b_grid[r][c] = "B"
    
    # Hatalı tahminleri kaydet
    for _ in range(3):  # Frekansı artırmak için birkaç kez kaydet
        model.record_grid_mistake(all_p_grid, 3, "B")  # Tamamen P grid için B yanlış
        model.record_grid_mistake(all_b_grid, 3, "P")  # Tamamen B grid için P yanlış
    
    print("Grid adaptif model test verileriyle başlatıldı.")
    model.close()

def seed_database_with_test_data():
    """Veritabanını test sonuçlarıyla doldurur."""
    db_manager = DatabaseManager()
    
    # Rastgele sonuçlar oluştur
    test_results = []
    for _ in range(100):
        result = 'P' if random.random() > 0.5 else 'B'
        test_results.append(result)
    
    # Bazı tekrarlayan desenler ekle (tahmin için)
    patterns = [
        ['P', 'B', 'P', 'B', 'P'],
        ['B', 'B', 'P', 'P', 'B'],
        ['P', 'P', 'P', 'B', 'B'],
        ['B', 'P', 'B', 'P', 'B']
    ]
    
    for pattern in patterns:
        test_results.extend(pattern)
    
    # Veritabanına ekle
    for result in test_results:
        db_manager.add_result(result)
    
    db_manager.flush_buffer()
    print(f"{len(test_results)} test sonucu veritabanına eklendi.")
    db_manager.close()

def initialize_all_data():
    """Tüm veritabanı ve model verilerini başlatır."""
    print("Veritabanı ve model verilerini başlatma işlemi başlıyor...")
    seed_database_with_test_data()
    initialize_adaptive_learning_data()
    initialize_grid_mistake_patterns()
    print("Veritabanı ve model verileri başarıyla başlatıldı.")

if __name__ == "__main__":
    initialize_all_data()