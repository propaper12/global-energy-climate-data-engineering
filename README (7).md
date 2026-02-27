
# 🌍 GECI: Global Energy & Climate Intelligence Hub

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![Apache Spark](https://img.shields.io/badge/Apache_Spark-PySpark-orange?style=flat-square&logo=apachespark)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Data_Warehouse-336791?style=flat-square&logo=postgresql)
![MinIO](https://img.shields.io/badge/MinIO-Data_Lake-C7202C?style=flat-square&logo=minio)
![Docker](https://img.shields.io/badge/Docker-Containerization-2496ED?style=flat-square&logo=docker)
![Streamlit](https://img.shields.io/badge/Streamlit-Web_App-FF4B4B?style=flat-square&logo=streamlit)
![Machine Learning](https://img.shields.io/badge/Machine_Learning-XGBoost_%7C_Sklearn-yellow?style=flat-square)

## 📌 Projenin Amacı (About The Project)
**
**GECI (Global Energy & Climate Intelligence Hub)**, küresel ölçekte enerji tüketimi, yenilenebilir enerji dönüşümü ve karbon emisyonu verilerini analiz eden, uçtan uca tasarlanmış kapsamlı bir **Veri Mühendisliği ve Yapay Zeka platformudur**.

Bu proje, yalnızca görselleştirme odaklı bir dashboard sunmakla kalmaz; aynı zamanda ham verinin toplanmasından (**Data Ingestion**), işlenmesine (**ETL**), veri ambarına aktarılmasına ve makine öğrenmesi modelleri ile ileriye dönük tahminler üretilmesine kadar tüm **veri yaşam döngüsünü (Data Lifecycle)** otomatik hale getiren ölçeklenebilir bir mimari sunar.

## 🏗️ Veri Mimarisi (Data Architecture)

Proje altyapısı, modern veri mühendisliği standartlarına uygun olarak **Madalyon Mimarisi (Medallion Architecture)** yaklaşımıyla tasarlanmıştır.

1.  🥉 **Bronze Layer (MinIO / S3)**  
    Ham CSV veri setleri (Our World in Data, Kaggle vb.) yapısal olmayan formatta veri gölüne (Data Lake) aktarılır. Bu süreç `ingest_to_s3.py` scripti ile otomatik olarak gerçekleştirilir.
    
2.  🥈 **Silver Layer (Apache Spark)**  
    PySpark kullanılarak ham veriler okunur, şema düzeltmeleri ve veri temizliği uygulanır. Performanslı okuma ve analiz için `Parquet` formatında tekrar MinIO üzerine yazılır (`etl_spark_to_db.py`).
    
3.  🥇 **Gold Layer (PostgreSQL)**  
    Temizlenmiş ve iş kuralları uygulanmış veri, veri ambarına (Data Warehouse) ilişkisel tablolar halinde aktarılır. Makine öğrenmesi modelleri ve Streamlit tabanlı BI uygulamaları yalnızca bu katmandan beslenir.

## 
## Temel Özellikler (Key Features)

-   **⚡ PySpark ETL Motoru:**  
    Milyonlarca satırlık veriyi yüksek performansla işleyebilen, idempotent ve ölçeklenebilir veri boru hattı.
    
-   **📡 Hibrit Veri Füzyonu:**  
    Tarihsel veri setlerinin, **NASA POWER API** ve meteorolojik sensör verileriyle gerçek zamanlı olarak birleştirilmesi.
    
-   **🔮 AI 2040 Projeksiyonu (XGBoost & Ridge):**  
    Ülke bazlı eğitilen modeller ile 2040 yılına kadar yenilenebilir enerji üretim tahminleri.
    
-   **🎛️ Politika Simülatörü (Random Forest):**  
    Enerji üretim miksindeki değişimlerin karbon ayak izine etkisini anlık olarak simüle eden karar destek sistemi.
    
-   **🧪 Otomatik Kalite Kontrol (Unit Testing):**  
    `unittest` altyapısı ile API bağlantıları, veri doğruluğu ve sistem sağlığının otomatik test edilmesi.


## 🛠️ Teknoloji Yığını (Tech Stack)

-   **Veri İşleme:** Apache Spark (PySpark), Pandas, PyArrow
    
-   **Altyapı & Depolama:** Docker, Docker Compose, PostgreSQL, MinIO
    
-   **Makine Öğrenmesi:** Scikit-Learn, XGBoost, Joblib
    
-   **Görselleştirme:** Streamlit, Plotly
    
-   **Diğer Araçlar:** SQLAlchemy, Requests, Python-Dotenv
## 📂 Proje Yapısı (Directory Structure)
```text
📦 GECI_Project
 ┣ 📜 docker-compose.yml       # DB ve MinIO konteyner altyapısı
 ┣ 📜 requirements.txt         # Python bağımlılıkları
 ┣ 📜 .env                     # Gizli ortam değişkenleri
 ┣ 📜 config.py                # Konfigürasyon ve Loglama yönetimi
 ┣ 📜 utils.py                 # DB bağlantıları ve NASA API yardımcı fonksiyonları
 ┣ 📜 test_app.py              # Kalite Kontrol (QA) Unit Testleri
 ┃ # --- Veri Boru Hattı (Data Pipeline) ---
 ┣ 📜 ingest_to_s3.py          # Lokalden MinIO Bronze katmanına veri aktarımı
 ┣ 📜 etl_spark_to_db.py       # PySpark ETL motoru (Bronze -> Silver -> Gold)
 ┣ 📜 train_models.py          # Toplu ve spesifik AI model eğitim scripti
 ┃ # --- Kullanıcı Arayüzü (Streamlit) ---
 ┣ 📜 Home.py                  # Ana gösterge paneli ve Pipeline Kontrolcüsü
 ┣ 📂 pages/                   # Modüler arayüz sayfaları
 ┃ ┣ 📜 1_Komuta_Merkezi.py    # Operasyonel İzleme & NASA verileri
 ┃ ┣ 📜 2_Fosil_vs_Yesil.py    # Makas analizi ve geçiş momentumu
 ┃ ┣ 📜 3_Hava_ve_Enerji.py    # Atmosferik Zeka
 ┃ ┣ 📜 4_AI_Projeksiyonu.py   # AI ile 2040 tahminleri
 ┃ ┣ 📜 5_Politika_Simulatoru.py # Random Forest destekli karbon simülatörü
 ┃ ┣ 📜 6_Veri_Kesfi.py        # Küresel korelasyonlar ve Liderlik tabloları
 ┃ ┣ 📜 7_Kalite_Kontrol.py    # Sistem sağlık paneli ve test arayüzü
 ┃ ┗ 📜 8_Proje_Ozeti.py       # Dokümantasyon
 ┗ 📂 models/                  # Eğitilmiş .pkl formatlı yapay zeka modelleri
 ```
 ## ⚙️ Kurulum ve Çalıştırma (Quick Start)

**1. Repoyu Klonlayın**

Bash

```
git clone [https://github.com/kullanici_adiniz/GECI-Energy-Hub.git](https://github.com/kullanici_adiniz/GECI-Energy-Hub.git)
cd GECI-Energy-Hub

```

**2. Gerekli Paketleri Yükleyin**

Bash

```
pip install -r requirements.txt

```

**3. Altyapıyı Ayağa Kaldırın (Docker)** PostgreSQL ve MinIO sunucularını başlatmak için:

Bash

```
docker-compose up -d

```
## 
## 📥 Veri Yükleme – MinIO (Data Lake) Kullanımı

Projede yer alan tüm **ham veri setleri**, MinIO üzerinde oluşturulan **`raw-data` bucket’ı** içerisine yüklenmelidir. Bu yapı, veri gölü mimarisinin Bronze katmanını temsil eder.

### Adım Adım Veri Yükleme Süreci

1.  MinIO web arayüzüne giriş yapın.
    
    -   **Kullanıcı adı:** admin
        
    -   **Şifre:** minio_password
        
2.  `raw-data` isimli bucket’ı oluşturun.
### 4. Adım: Spark ETL Sürecini Başlat


 Şimdi MinIO'daki o ham verileri alıp, temizleyip Postgres veritabanına atacağız.

Bash

```
docker exec -it geci_dashboard python ingest_to_s3.py

 docker exec -it geci_dashboard python etl_spark_to_db.py

docker restart geci_dashboard

docker-compose down ile sistemi durdurun.
```

## ♻️ Sistemi Sıfırlama ve Yeniden Kurulum

Docker, PostgreSQL ve MinIO verileri kalıcı hale getirmek için **volume** yapısını kullanır. Sistemi tamamen sıfırlamak ve temiz kurulum yapmak için:
```
docker-compose down -v
```

Ardından sistemi tekrar başlatmak için:
```
docker-compose up -d
```

Bu işlem, ortamı temiz bir şekilde yeniden oluşturmanıza olanak tanır.

```
