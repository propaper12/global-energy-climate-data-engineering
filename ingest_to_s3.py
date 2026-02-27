import os
from minio import Minio
from config import MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_ENDPOINT, logger

def run_ingestion():
    logger.info("📥 Veri Çekme (Ingest) İşlemi Başladı...")
    
    # MinIO'ya bağlan
    client = Minio(
        MINIO_ENDPOINT.replace("http://", ""),
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

    # Bucket yoksa oluştur
    if not client.bucket_exists("raw-data"):
        client.make_bucket("raw-data")

    # 🎯 HEDEF KLASÖR: Senin verilerin olduğu klasör
    data_folder = "Veri_Setleri"
    
    # Klasör gerçekten orada mı kontrol et
    if not os.path.exists(data_folder):
        logger.error(f"❌ '{data_folder}' klasörü konteyner içinde bulunamadı! Docker ayarlarını kontrol et.")
        return

    # Veri_Setleri klasörünün içindeki TÜM CSV dosyalarını bul
    csv_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
    
    if not csv_files:
        logger.error(f"❌ '{data_folder}' klasörünün içinde hiç .csv dosyası bulunamadı!")
        return

    logger.info(f"🔍 Toplam {len(csv_files)} adet CSV dosyası bulundu. MinIO'ya aktarılıyor...")

    # Her bir dosyayı MinIO'ya yükle
    for file_name in csv_files:
        # Bilgisayardaki tam yol (Örn: Veri_Setleri/dosya.csv)
        local_file_path = os.path.join(data_folder, file_name)
        
        # MinIO'daki dümdüz yol (Örn: bronze/dosya.csv)
        minio_path = f"bronze/{file_name}"
        
        try:
            # fput_object yerel dosyayı MinIO'ya yükler
            client.fput_object("raw-data", minio_path, local_file_path)
            logger.info(f"✅ Başarılı: {file_name} -> {minio_path}")
        except Exception as e:
            logger.error(f"❌ Hata ({file_name}): {e}")

    logger.info("🎉 Tüm veriler Bronze katmanına başarıyla yüklendi!")

if __name__ == "__main__":
    run_ingestion()