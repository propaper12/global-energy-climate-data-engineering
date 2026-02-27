import streamlit as st

# 1. SAYFA AYARI
st.set_page_config(
    page_title="GECI | Proje Özeti", 
    page_icon="📜", 
    layout="wide"
)

# Junior Stil Yazım ve Markdown Tasarımı
st.markdown("""
# 🌍 Global Energy & Climate Intelligence Hub (GECI)

### 👋 Selam! Ben bir Veri Mühendisi Adayıyım.
Bu proje, ham verinin bir API'den veya CSV'den çıkıp, temizlenip, bir veritabanına girmesini ve sonunda bir **Yapay Zeka** modeline dönüşme sürecini bizzat deneyimlemek için kurduğum bir "Veri Boru Hattı" (Data Pipeline) çalışmasıdır.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![Apache Spark](https://img.shields.io/badge/Engine-PySpark-orange?style=flat-square&logo=apachespark)](https://spark.apache.org/docs/latest/api/python/index.html)
[![PostgreSQL](https://img.shields.io/badge/Warehouse-Postgres-blue?style=flat-square&logo=postgresql)](https://www.postgresql.org/)
[![MinIO](https://img.shields.io/badge/Lake-MinIO-red?style=flat-square&logo=minio)](https://min.io/)
""")

st.divider()

# --- MIMARI VE MUHENDISLIK ---
st.header("🏗️ Veri Mimari ve Mühendislik Detayları")


col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    #### 1. 🏗️ Madalyon Mimarisi (Medallion Architecture)
    * **Bronze Katmanı:** NASA ve Our World in Data'dan gelen ham CSV verileri MinIO (S3) üzerinde saklanır.
    * **Silver Katmanı:** PySpark ile şema tanımları yapılan ve temizlenen veriler Parquet formatına dönüştürülür.
    * **Gold Katmanı:** Analize hazır, joinlenmiş tablolar PostgreSQL veri ambarına aktarılır.

    #### 2. ⚙️ ETL & Spark Motoru
    * **Veri Tesisatı:** Dağıtık işleme mantığı (Spark) kullanılarak milyonlarca satır veritabanına jilet gibi aktarılır.
    * **Otomatik Kontrol:** Dashboard üzerindeki "Admin" butonları ile tüm pipeline manuel tetiklenebilir.
    """)

with col2:
    st.markdown(f"""
    #### 3. ✅ Kalite Kontrol (QA / Testing)
    * **Unit Testing:** `unittest` kütüphanesi ile veritabanı bağlantısı ve veri bütünlüğü her adımda doğrulanır.
    * **Schema Check:** Spark işlemleri sırasında kolon çakışmaları ve tip hataları kod seviyesinde çözülür.

    #### 4. 🔮 AI & Analitik Zeka
    * **2040 Projeksiyonu:** XGBoost ve Random Forest ile ülkelerin enerji dönüşüm hızını tahmin eden modeller eğitilir.
    * **Politika Simülatörü:** Enerji miksi değişimlerinin karbon ayak izine etkisini anlık olarak hesaplayan bir "on-demand" motor mevcuttur.
    """)

st.divider()

# --- TEKNOLOJI YIGINI ---
st.subheader("🛠️ Teknoloji Yığını (Tech Stack)")
tech_cols = st.columns(5)
tech_data = [
    ("Infrastructure", "Docker & Postgres"),
    ("Data Engine", "Apache Spark"),
    ("Data Lake", "MinIO (S3)"),
    ("ML Framework", "XGBoost & Sklearn"),
    ("Frontend", "Streamlit")
]

for col, (title, tech) in zip(tech_cols, tech_data):
    col.metric(title, tech)

st.divider()

# --- PROJE YAPISI (DIRECTORY TREE) ---
st.subheader("📁 Proje Dosya Yapısı")

st.code("""
C:.
│   docker-compose.yml          # Konteyner orkestrasyonu (Postgres, MinIO, App)
│   Dockerfile                  # Spark & Java bağımlı uygulama imajı
│   etl_spark_to_db.py          # PySpark ETL motoru (Silver -> Gold)
│   train_models.py             # Ülke bazlı AI eğitim scripti
│   Home.py                     # Ana giriş ve Pipeline kontrol merkezi
│   utils.py                    # DB ve API bağlantı yönetimi
│   test_app.py                 # Birim testleri (QA)
├───models/                     # Eğitilmiş .pkl modelleri
└───pages/                      # Uygulama modülleri
        1_Komuta_Merkezi.py     # Operasyonel izleme
        2_Fosil_vs_Yesil.py     # Geçiş savaşı analizi
        3_Hava_ve_Enerji.py      # NASA atmosferik zeka
        4_AI_Projeksiyonu.py    # 2040 Vizyonu
        5_Politika_Simulatoru.py # Enerji miksi simülatörü
        6_Veri_Kesfi.py         # Global veri keşfi
        7_Kalite_Kontrol.py     # Sistem sağlık paneli
        8_Proje_Ozeti.py        # Dokümantasyon
""", language="text")

st.divider()

# --- FINAL NOTU ---
st.markdown("""
### 🏁 Sonuç ve Kazanımlar
Bu proje ile sadece kod yazmayı değil; Docker ağlarını yönetmeyi, büyük veriyi (Spark) temizlemeyi ve mülakatlarda anlatabileceğim jilet gibi bir "Veri Boru Hattı" kurmayı öğrendim. 

**"Veri sadece bir rakam değil, doğru işlendiğinde bir istihbarattır."**
""")