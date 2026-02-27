import os
import logging
from dotenv import load_dotenv

load_dotenv() # .env dosyasını yükle

# ---------------------------------------------------------
# 1. GELİŞMİŞ LOGLAMA AYARLARI 
# ---------------------------------------------------------
def setup_logging():
    logger = logging.getLogger("GECI_Hub")
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    info_handler = logging.FileHandler("info.log")
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)

    error_handler = logging.FileHandler("error.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    logger.addHandler(info_handler)
    logger.addHandler(error_handler)
    logger.addHandler(logging.StreamHandler())
    
    return logger

logger = setup_logging()

# ---------------------------------------------------------
# 2. MINIO (DATA LAKE) KİMLİKLERİ (Spark ve Ingest İçin)
# ---------------------------------------------------------
MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER", "admin_geci")
MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD", "geci_password_2026")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "geci_datalake:9000")

# ---------------------------------------------------------
# 3. STREAMLIT İÇİN BİREYSEL VERİTABANI DEĞİŞKENLERİ (utils.py arıyor)
# ---------------------------------------------------------
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "admin123")
DB_HOST = os.getenv("DB_HOST", "geci_warehouse")
DB_NAME = os.getenv("DB_NAME", "gecidb")

# ---------------------------------------------------------
# 4. SPARK İÇİN VERİTABANI PAKETİ (etl_spark_to_db.py arıyor)
# ---------------------------------------------------------
DB_CONFIG = {
    "host": DB_HOST,
    "port": "5432", 
    "database": DB_NAME,
    "user": DB_USER,
    "password": DB_PASS
}