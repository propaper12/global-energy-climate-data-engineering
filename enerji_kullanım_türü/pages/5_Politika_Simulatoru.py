import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import joblib
import os
from utils import load_all_datasets, setup_sidebar

# 1. SAYFA AYARI VE SIDEBAR
st.set_page_config(page_title="Politika Simülatörü", page_icon="🎛️", layout="wide")
setup_sidebar()

st.markdown("""
    <style>
    .metric-container { background-color: #000000; color: #ffffff !important; padding: 20px; border-radius: 12px; border-top: 5px solid #3b82f6; text-align: center; margin-bottom: 15px; }
    .explanation-box { background-color: #e3f2fd; border-left: 5px solid #2196f3; padding: 15px; border-radius: 5px; color: #0d47a1; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. VERİ YÜKLEME VE HESAPLAMA
df_co2, df_fossil, df_share, df_master = load_all_datasets()
selected_country = st.session_state.get("selected_country", "Turkey")

# JUNIOR-FIX: Postgres'ten gelen ham verilerle oranları (Share) burada hesaplıyoruz
# utils.py'den gelen df_master zaten 'Fossil fuels', 'Nuclear' ve 'Renewables' sütunlarına sahip
df_master['Total_Gen'] = df_master['Fossil fuels'] + df_master['Nuclear'] + df_master['Renewables']
df_master['Share_Renewables'] = (df_master['Renewables'] / df_master['Total_Gen']) * 100
df_master['Share_Nuclear'] = (df_master['Nuclear'] / df_master['Total_Gen']) * 100
df_master['Share_Fossil'] = (df_master['Fossil fuels'] / df_master['Total_Gen']) * 100

# 3. MODEL YÜKLEME
MODEL_PATH = "models/policy_simulator_rf.pkl"
if not os.path.exists(MODEL_PATH):
    st.error("🚨 Kritik Hata: ML Modelleri bulunamadı. Lütfen ana sayfadan 'AI Modelleri Eğit' butonuna basın.")
    st.stop()

rf_sim_model = joblib.load(MODEL_PATH)

# Mevcut Ülke Durumu (Yeni hesapladığımız sütunlarla çekiyoruz)
country_data = df_master[df_master['Entity'] == selected_country].dropna(subset=['Share_Renewables'])

if country_data.empty:
    st.warning(f"⚠️ {selected_country} için yeterli analiz verisi bulunamadı.")
    st.stop()

current_state = country_data.iloc[-1]
curr_ren = float(current_state['Share_Renewables'])
curr_nuc = float(current_state['Share_Nuclear'])
curr_fos = float(current_state['Share_Fossil'])
curr_co2 = float(current_state['Per capita emissions'])

st.markdown(f"## 🎛️ Stratejik Enerji Miksi Simülatörü: {selected_country}")
st.markdown('<div class="explanation-box">Bu simülatörde Yenilenebilir ve Nükleer hedeflerinizi belirleyin, Karbon Ayak İzini nasıl düşürebileceğinizi test edin.</div>', unsafe_allow_html=True)

col_inputs, col_results = st.columns([1, 2])

with col_inputs:
    st.subheader(" 🛡️ Politika Ayarları")
    target_ren = st.slider("Hedef: Yenilenebilir (%)", 0, 100, int(curr_ren))
    target_nuc = st.slider("Hedef: Nükleer (%)", 0, 100, int(curr_nuc))
    
    remaining = 100 - (target_ren + target_nuc)
    if remaining < 0:
        st.error(" ❌ Hata: Toplam %100'ü geçti! Lütfen değerleri düşürün.")
        target_fos, sim_valid = 0, False
    else:
        target_fos, sim_valid = remaining, True
        st.info(f" 📉 Kalan Fosil Payı: %{target_fos}")

with col_results:
    if sim_valid:
        # Saniyelik Tahmin (Modelin beklediği Share sütunları sırasıyla)
        pred_co2 = rf_sim_model.predict([[target_ren, target_nuc, target_fos]])[0]
        paris_goal = 2.0
        status_color = "#10b981" if pred_co2 < paris_goal else "#ef4444"
        
        st.markdown(f"""
        <div class="metric-container" style="border-top-color: {status_color};">
            <h3>TAHMİNİ KARBON AYAK İZİ (2040)</h3>
            <h2 style="font-size:48px;">{pred_co2:.2f} <span style="font-size:20px;">ton/kişi</span></h2>
            <p style="color:{status_color}; font-weight:bold;">{"✅ Paris Anlaşması Uyumlu" if pred_co2 < paris_goal else "⚠️ Emisyon Hedefi Dışı"}</p>
        </div>""", unsafe_allow_html=True)
        
        # Karşılaştırmalı Pie Chart
        fig_mix = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]], subplot_titles=['Mevcut Durum', 'Yeni Politika Hedefi'])
        fig_mix.add_trace(go.Pie(labels=["Yeşil", "Nükleer", "Fosil"], values=[curr_ren, curr_nuc, curr_fos], hole=0.6, marker=dict(colors=['#10b981', '#3b82f6', '#334155'])), 1, 1)
        fig_mix.add_trace(go.Pie(labels=["Yeşil", "Nükleer", "Fosil"], values=[target_ren, target_nuc, target_fos], hole=0.6, marker=dict(colors=['#10b981', '#3b82f6', '#334155'])), 1, 2)
        fig_mix.update_layout(height=400)
        st.plotly_chart(fig_mix, use_container_width=True)

st.divider()
st.caption("ℹ️ Not: Bu simülasyon, Random Forest Regressor modeli kullanılarak ülkelerin tarihsel enerji miksi ve emisyon korelasyonu üzerinden hesaplanmaktadır.")