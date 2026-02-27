import os
from pyspark.sql import SparkSession
from minio import Minio
from config import MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_ENDPOINT, DB_CONFIG, logger

def get_spark_session():
    return SparkSession.builder \
        .appName("GECI_Spark_Dynamic_Pipeline") \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,org.postgresql:postgresql:42.5.4") \
        .config("spark.hadoop.fs.s3a.endpoint", MINIO_ENDPOINT) \
        .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY) \
        .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY) \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .getOrCreate()

def run_dynamic_etl():
    logger.info("🚀 Dinamik Boru Hattı Başlatıldı: Bronze -> Silver -> Gold")

    # 1. MinIO'ya bağlanıp Bronze içindeki TÜM dosyaları listele
    try:
        minio_client = Minio(MINIO_ENDPOINT.replace("http://", ""), 
                             access_key=MINIO_ACCESS_KEY, 
                             secret_key=MINIO_SECRET_KEY, 
                             secure=False)
        
        objects = minio_client.list_objects("raw-data", prefix="bronze/", recursive=True)
        csv_files = [obj.object_name for obj in objects if obj.object_name.endswith('.csv')]
    except Exception as e:
        logger.error(f"❌ MinIO bağlantı hatası: {e}")
        return

    if not csv_files:
        logger.warning("⚠️ Bronze klasöründe işlenecek CSV bulunamadı. Lütfen Ingest işlemini çalıştırın.")
        return

    spark = get_spark_session()
    logger.info(f"📦 MinIO'da {len(csv_files)} adet dosya bulundu. İşlem başlıyor...")

    # 2. Bulunan her bir dosyayı sırayla işle
    for file_path in csv_files:
        # Dosya adını temizleyip tablo adı üretiyoruz (örn: "bronze/veri.csv" -> "veri")
        base_name = file_path.split('/')[-1].replace('.csv', '')
        table_name = base_name.replace('-', '_').replace(' ', '_').lower()
        
        bronze_s3_path = f"s3a://raw-data/{file_path}"
        
        try:
            df = spark.read.option("header", "true").option("inferSchema", "true").csv(bronze_s3_path)
            logger.info(f"📥 Okundu: {base_name}.csv")
        except Exception as e:
            logger.error(f"❌ Spark okuma hatası ({bronze_s3_path}): {e}")
            continue

        # Kolon isimlerindeki boşluk ve parantezleri temizle (Parquet ve Postgres kuralları)
        for c in df.columns:
            clean_col = c.replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_").replace("%", "pct")
            df = df.withColumnRenamed(c, clean_col)
        
        # 3. SILVER'A YAZ (Parquet formatında)
        silver_path = f"s3a://raw-data/silver/{table_name}.parquet"
        df.write.mode("overwrite").parquet(silver_path) 
        logger.info(f"🥈 Silver (Parquet) Yazıldı: {table_name}.parquet")

        # 4. GOLD'A YAZ (Postgres) - Her CSV kendi adıyla tablo olur
        df.write \
            .format("jdbc") \
            .option("url", f"jdbc:postgresql://{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}") \
            .option("dbtable", table_name) \
            .option("user", DB_CONFIG['user']) \
            .option("password", DB_CONFIG['password']) \
            .option("driver", "org.postgresql.Driver") \
            .mode("overwrite") \
            .save() 
        
        logger.info(f"🏆 Gold (Postgres) Güncellendi: Tablo Adı -> {table_name}")

    spark.stop()
    logger.info("🎉 Tüm veriler başarıyla işlendi ve veri ambarına aktarıldı!")

if __name__ == "__main__":
    run_dynamic_etl()