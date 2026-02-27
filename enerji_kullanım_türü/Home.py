import streamlit as st
import subprocess
import os
import pandas as pd
from utils import load_all_datasets, setup_sidebar

# 1. SAYFA KONFİGÜRASYONU
st.set_page_config(page_title="GECI | Komuta Merkezi", page_icon="⚡", layout="wide")
setup_sidebar()

# Session state'den o anki ülkeyi alıyoruz
selected_country = st.session_state.get("selected_country", "Turkey")

st.title("⚡ GECI Enerji Yönetim ve Kontrol Merkezi")
st.markdown("---")

# 2. ETL KONTROL PANELİ (ADMİN SİDEBAR)
st.sidebar.markdown("### 🛠️ Sistem Yönetimi")
st.sidebar.caption(f"Seçili Bölge: {selected_country}")

def run_pipeline_script(script_name, success_message, args=None):
    """Scriptleri opsiyonel argümanlarla çalıştırır."""
    command = ["python", script_name]
    if args:
        command.append(args)
        
    with st.spinner(f"{script_name} çalışıyor..."):
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode == 0:
                st.sidebar.success(success_message)
                with st.expander("İşlem Logları"):
                    st.code(result.stdout)
            else:
                st.sidebar.error(f"Hata: {script_name}")
                st.code(result.stderr)
        except Exception as e:
            st.sidebar.error(f"Sistem Hatası: {e}")

# BUTONLAR
if st.sidebar.button("📥 1. Veri Çek (Ingest)"):
    run_pipeline_script("ingest_to_s3.py", "Veriler çekildi!")

if st.sidebar.button("⚙️ 2. Veri İşle (Spark)"):
    run_pipeline_script("etl_spark_to_db.py", "Veri ambarı güncellendi!")

if st.sidebar.button(f"🔮 3. {selected_country} Modelini Eğit"):
    run_pipeline_script("train_models.py", f"{selected_country} Vizyonu güncellendi!", selected_country)

if st.sidebar.button("🌍 Tüm Dünyayı Eğit (Uzun Sürer)"):
    run_pipeline_script("train_models.py", "Küresel modeller güncellendi!")

# 3. ANA EKRAN: VERİ AMBARI ÖZETİ (GOLD LAYER)
try:
    df_co2, df_fossil, df_share, df_master = load_all_datasets()
    
    if df_master is not None:
        # --- ÜST KPI BÖLÜMÜ ---
        st.markdown("### 🏛️ Veri Ambarı (Gold Layer) Genel Durumu")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        total_records = len(df_master)
        total_entities = df_master['Entity'].nunique()
        year_range = f"{df_master['Year'].min()} - {df_master['Year'].max()}"
        
        kpi1.metric("Toplam Kayıt Sayısı", f"{total_records:,}")
        kpi2.metric("İşlenen Ülke/Bölge", total_entities)
        kpi3.metric("Zaman Ölçeği", year_range)
        kpi4.metric("Veri Ambarı Sağlığı", "✅ Stabil")

        st.markdown("---")

        # --- ORTA BÖLÜM: ÜLKE BAZLI VERİ DAĞILIMI ---
        col_left, col_right = st.columns([1, 1.5])
        
        with col_left:
            st.subheader("📍 Ülke Bazlı Kayıt Sayıları")
            # Ülkelere göre veri sayılarını hesaplıyoruz
            country_counts = df_master['Entity'].value_counts().reset_index()
            country_counts.columns = ['Ülke/Bölge', 'Kayıt Sayısı']
            
            # Etkileşimli Tablo
            st.dataframe(
                country_counts, 
                use_container_width=True, 
                height=400,
                hide_index=True
            )

        with col_right:
            st.subheader(f"📊 {selected_country} Detaylı Analizi")
            country_data = df_master[df_master['Entity'] == selected_country]
            
            if not country_data.empty:
                latest = country_data.iloc[-1]
                
                # Seçili ülke için mini metrikler
                m1, m2 = st.columns(2)
                m1.metric("Mevcut Yenilenebilir (TWh)", f"{latest['Renewables']:.2f}")
                m2.metric("Fosil Bağımlılığı", f"%{(latest['Fossil fuels']/latest['Total_Gen']*100):.1f}")
                
                # Grafik: Üretim Dağılımı
                st.area_chart(
                    country_data.set_index('Year')[['Renewables', 'Fossil fuels', 'Nuclear']],
                    height=250
                )
            else:
                st.warning(f"{selected_country} için Gold katmanında veri bulunamadı.")

        # --- ALT BÖLÜM: MASTER VERİ ÖNİZLEME ---
        st.markdown("---")
        st.subheader("🔍 Master Veri Seti Önizlemesi (İlk 100 Satır)")
        st.dataframe(df_master.head(100), use_container_width=True)

    else:
        st.warning("⚠️ Veri ambarı şu an boş. Lütfen sol taraftaki butonlarla Pipeline'ı başlatın.")

except Exception as e:
    st.error(f"Ana sayfa yüklenirken bir hata oluştu: {e}")