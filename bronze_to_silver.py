import os
from pyspark.sql import SparkSession
from config import MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_ENDPOINT, DB_CONFIG, logger

def get_spark_session():
    return SparkSession.builder \
        .appName("GECI_Spark_Static_Pipeline") \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,org.postgresql:postgresql:42.5.4") \
        .config("spark.hadoop.fs.s3a.endpoint", MINIO_ENDPOINT) \
        .config("spark.hadoop.fs.s3a.access.key", MINIO_ACCESS_KEY) \
        .config("spark.hadoop.fs.s3a.secret.key", MINIO_SECRET_KEY) \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .getOrCreate()

def run_static_etl():
    spark = get_spark_session()
    
    datasets = {
        "energy_co2": "co2-per-capita-vs-renewable-electricity",
        "energy_fossil": "fossil-fuels-per-capita",
        "energy_share": "share-electricity-renewables"
    }

    logger.info("🚀 Sabit Boru Hattı Başlatıldı: bronze/latest -> silver/latest -> Gold")

    for table_name, file_name in datasets.items():
        # 1. BRONZE'DAN OKU (SABİT YOL)
        bronze_path = f"s3a://raw-data/bronze/latest/{file_name}.csv"
        
        try:
            df = spark.read.option("header", "true").option("inferSchema", "true").csv(bronze_path)
            logger.info(f"📥 Bronze okundu: {bronze_path}")
        except Exception as e:
            logger.error(f"❌ HATA: {bronze_path} bulunamadı! Ingest scriptini kontrol et.")
            continue

        # 2. SILVER'A YAZ (SABİT YOL - PARQUET)
        for c in df.columns:
            df = df.withColumnRenamed(c, c.replace(" ", "_").replace("(", "").replace(")", ""))
        
        silver_path = f"s3a://raw-data/silver/latest/{table_name}.parquet"
        df.write.mode("overwrite").parquet(silver_path)
        logger.info(f"🥈 Silver güncellendi: {silver_path}")

        # 3. GOLD'A YAZ (Postgres)
        df.write \
            .format("jdbc") \
            .option("url", f"jdbc:postgresql://{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}") \
            .option("dbtable", "energy_master") \
            .option("user", DB_CONFIG['user']) \
            .option("password", DB_CONFIG['password']) \
            .option("driver", "org.postgresql.Driver") \
            .mode("overwrite") \
            .save()
        
        logger.info(f"🏆 Gold (Postgres) güncellendi: {table_name}")

    spark.stop()

if __name__ == "__main__":
    run_static_etl()