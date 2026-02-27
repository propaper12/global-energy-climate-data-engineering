import unittest
import pandas as pd
from sqlalchemy import text
from utils import load_all_datasets, fetch_hybrid_data, get_db_engine, logger

class TestEnergyHub(unittest.TestCase):

    def test_1_database_connection(self):
        """Veritabanı bağlantısının aktif olduğunu doğrular."""
        engine = get_db_engine()
        self.assertIsNotNone(engine, "Veritabanı motoru başlatılamadı!")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).fetchone()
            self.assertEqual(result[0], 1, "DB bağlantısı başarısız!")
            logger.info("QA: DB Bağlantı Testi Geçti.")

    def test_2_data_integrity(self):
        """Master tablonun şemasını ve doluluğunu test eder."""
        try:
            _, df_fossil, _, _ = load_all_datasets()
            self.assertFalse(df_fossil.empty, "Hata: Master tablo boş!")
            self.assertIn('Entity', df_fossil.columns)
            self.assertIn('Year', df_fossil.columns)
            logger.info(f"QA: Veri Bütünlüğü Testi Geçti ({len(df_fossil)} satır).")
        except Exception as e:
            self.fail(f"Veri bütünlüğü testi hatası: {e}")

    def test_3_data_quality_logic(self):
        """İş kurallarına göre veri kalitesini test eder (Senior DE Dokunuşu)."""
        _, df, _, _ = load_all_datasets()
        
        # 1. Enerji üretimi negatif olamaz
        negatives = df[df['Fossil fuels'] < 0]
        self.assertTrue(negatives.empty, f"KRİTİK HATA: {len(negatives)} satırda negatif üretim verisi var!")
        
        # 2. Year kolonu mantıklı aralıkta mı?
        year_check = df[(df['Year'] < 1900) | (df['Year'] > 2025)]
        self.assertTrue(year_check.empty, "Hata: Geçersiz yıl verileri tespit edildi!")
        
        # 3. Kritik kolonlarda NULL kontrolü
        null_count = df['Entity'].isnull().sum()
        self.assertEqual(null_count, 0, "Hata: Entity kolonunda NULL değerler var!")
        logger.info("QA: Veri Kalite Mantık Testleri Geçti.")

    def test_4_api_simulation(self):
        """API motorunun beklenen JSON yapısını döndürdüğünü test eder."""
        data = fetch_hybrid_data(39.9, 32.8)
        required_keys = ['nasa_solar', 'nasa_wind', 'live_temp', 'source']
        for key in required_keys:
            self.assertIn(key, data, f"API Hatası: {key} alanı eksik!")
        logger.info("QA: API Protokol Testi Geçti.")

if __name__ == '__main__':
    unittest.main()