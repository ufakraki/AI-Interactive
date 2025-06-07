import logging
import os
from datetime import datetime
from urllib.parse import urljoin
import re

def setup_logger(name):
    """Günlük (log) kaydı için bir logger ayarlar"""
    # Log klasörünü oluştur
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Logger'ı ayarla
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Dosya işleyici
        log_file = os.path.join(log_dir, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Konsol işleyici
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # İşleyicileri ekle
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

def validate_url(url):
    """URL'nin geçerli olup olmadığını kontrol eder"""
    if not url.startswith(('http://', 'https://')):
        return False
    return True

def clean_text(text):
    """Metni temizler ve düzenler"""
    if not text:
        return ""
    
    # Fazla boşlukları temizle
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Özel karakterleri temizle
    text = text.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')
    
    return text.strip()

def normalize_url(url, base_url):
    """URL'yi normalize eder (relative'dan absolute'a çevirir)"""
    if not url:
        return None
        
    # Zaten absolute URL ise
    if url.startswith(('http://', 'https://')):
        return url
    
    # Relative URL'i absolute'a çevir
    if base_url:
        return urljoin(base_url, url)
    
    return url
