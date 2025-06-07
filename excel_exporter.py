import pandas as pd
import os
from datetime import datetime
import logging
from utils import setup_logger

logger = setup_logger("excel_exporter")

class ExcelExporter:
    def __init__(self, output_dir=None):
        """Excel verilerini dışa aktaracak sınıf"""
        if output_dir is None:
            self.output_dir = os.path.dirname(os.path.abspath(__file__))
        else:
            self.output_dir = output_dir
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
    
    def export_to_excel(self, data, filename=None):
        """Verileri Excel dosyasına aktarır"""
        if not data:
            logger.warning("Aktarılacak veri yok!")
            return None
            
        try:
            # Varsayılan dosya adı oluştur
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"firma_verileri_{timestamp}.xlsx"
            
            # Excel yolu oluştur
            excel_path = os.path.join(self.output_dir, filename)
            
            # DataFrame oluştur
            df = pd.DataFrame(data)
            
            # Excel'e aktar
            df.to_excel(excel_path, index=False, engine='openpyxl')
            
            logger.info(f"Veriler başarıyla {excel_path} dosyasına kaydedildi.")
            return excel_path
            
        except Exception as e:
            logger.error(f"Excel'e aktarma sırasında hata: {str(e)}")
            return None
