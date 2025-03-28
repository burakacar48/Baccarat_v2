"""
Genel yardımcı fonksiyonlar modülü.
"""
import random
from PyQt6.QtWidgets import QLabel, QHBoxLayout, QWidget, QSizePolicy
from PyQt6.QtCore import Qt

def create_stat_row(label_text, value_object_name="StatValueLabel"):
    """İstatistik satırı widget'ı oluşturur.
    
    Args:
        label_text (str): Etiket metni.
        value_object_name (str, optional): Değer etiketi object name.
        
    Returns:
        tuple: (row_widget, value_label) çifti.
    """
    row = QWidget()
    row_layout = QHBoxLayout(row)
    row_layout.setContentsMargins(0, 0, 0, 0)
    
    label = QLabel(label_text)
    label.setObjectName("StatLabel")
    
    value_label = QLabel("N/A")
    value_label.setObjectName(value_object_name)
    value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    
    row_layout.addWidget(label)
    row_layout.addWidget(value_label)
    
    return row, value_label

def format_currency(value):
    """Para değerini formatlı bir şekilde döndürür.
    
    Args:
        value (float): Para değeri.
        
    Returns:
        str: Formatlanmış para değeri.
    """
    return f"{value:,.2f} TL"

def format_percentage(value):
    """Yüzde değerini formatlı bir şekilde döndürür.
    
    Args:
        value (float): Yüzde değeri.
        
    Returns:
        str: Formatlanmış yüzde değeri.
    """
    return f"{value:.1f}%"

def generate_random_result():
    """Rastgele bir oyun sonucu döndürür.
    
    Returns:
        str: 'P' veya 'B'.
    """
    return random.choice(['P', 'B'])

def truncate_list(lst, max_length):
    """Listeyi belirli bir uzunluğa kısaltır.
    
    Args:
        lst (list): Orijinal liste.
        max_length (int): Maksimum uzunluk.
        
    Returns:
        list: Kısaltılmış liste.
    """
    if len(lst) <= max_length:
        return lst.copy()
    return lst[-max_length:]
