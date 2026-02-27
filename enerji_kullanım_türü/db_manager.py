from sqlalchemy import create_engine, text
import pandas as pd
from config import DB_USER, DB_PASS, DB_HOST, DB_NAME, logger

def get_db_engine():
    try:
        engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}")
        return engine
    except Exception as e:
        logger.error(f"DB Engine Hatası: {str(e)}", exc_info=True)
        return None

def load_filtered_data(table_name, columns=None, entity=None):
    """SQL Filtreleme ile optimize ve GÜVENLİ veri çekme"""
    engine = get_db_engine()
    col_str = "*" if not columns else ", ".join([f'"{c}"' for c in columns])
    
    # SENIOR DOKUNUŞU: SQL Injection'ı engellemek için parametrik sorgu (Bind Parameters)
    if entity:
        query = text(f"SELECT {col_str} FROM {table_name} WHERE \"Entity\" = :entity_param")
        logger.info(f"Parametrik sorgu çalıştırılıyor: Tablo={table_name}, Filtre={entity}")
        return pd.read_sql(query, engine, params={"entity_param": entity})
    else:
        query = text(f"SELECT {col_str} FROM {table_name}")
        logger.info(f"Tüm veriler çekiliyor: Tablo={table_name}")
        return pd.read_sql(query, engine)