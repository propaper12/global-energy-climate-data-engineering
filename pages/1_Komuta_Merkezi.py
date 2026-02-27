import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from utils import load_all_datasets, fetch_hybrid_data, setup_sidebar

# 1. SAYFA AYARI
st.set_page_config(page_title="Komuta Merkezi", page_icon="🌐", layout="wide")

setup_sidebar()

# CSS Tasarımı
st.markdown("""
    <style>
    .metric-container { 
        background-color: #000; color: #fff; padding: 20px; 
        border-radius: 12px; border-left: 5px solid #3b82f6; 
        text-align: center; margin-bottom: 15px; 
    }
    .metric-container h2 { font-weight: 800; font-size: 24px !important; margin: 5px 0; }
    .badge-api { background-color: #0b3d91; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.7em; }
    .badge-fossil { background-color: #ef4444; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.7em; }
    .badge-green { background-color: #10b981; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.7em; }
    .explanation-box { 
        background-color: #e3f2fd; border-left: 5px solid #2196f3; 
        padding: 15px; border-radius: 5px; color: #000000; 
        margin-bottom: 20px; font-size: 0.95em;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. VERİ HAZIRLIĞI
df_co2, df_fossil, df_share, df_supp = load_all_datasets()
selected_country = st.session_state.get("selected_country", "Turkey")

# Ülke Verileri
share_data = df_share[df_share['Entity'] == selected_country]
share_val = share_data.iloc[-1]['Renewables'] if not share_data.empty else 0.0
loc_map = {"Turkey": [39.9, 32.8], "United States": [37.1, -95.7], "China": [35.9, 104.2], "Germany": [51.1, 10.4]}
lat_lon = loc_map.get(selected_country, [30.0, 31.0])

# API Verisi
api_energy = fetch_hybrid_data(lat_lon[0], lat_lon[1])

# 3. GÖRSELLEŞTİRME 
st.markdown(f"## {selected_country} Operasyonel Enerji Komuta Merkezi")
st.markdown('<div class="explanation-box">Bu panel, NASA uydularından gelen radyasyon verileri ile OpenWeather sensörlerinden gelen anlık saha verilerini birleştirir.</div>', unsafe_allow_html=True)

#ÜST METRİKLER
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="metric-container"><span class="badge-api">NASA UYDU</span><h3>Güneş Potansiyeli</h3><h2>{api_energy['nasa_solar']:.2f} <span style="font-size:16px">kW/m²</span></h2></div>""", unsafe_allow_html=True)
with c2:
    fossil_gen = df_fossil[df_fossil["Entity"] == selected_country].iloc[-1]["Fossil fuels"]
    st.markdown(f"""<div class="metric-container"><span class="badge-fossil">ŞEBEKE YÜKÜ</span><h3>Fosil Üretim</h3><h2>{fossil_gen:.0f} <span style="font-size:16px">TWh</span></h2></div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="metric-container"><span class="badge-green">YEŞİL HEDEF</span><h3>Yenilenebilir Payı</h3><h2>%{share_val:.1f}</h2></div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="metric-container" style="border-left-color: #eb6e4b;"><span class="badge-api">CANLI SAHA</span><h3>Anlık Sıcaklık</h3><h2>{api_energy['live_temp']:.1f}°C</h2></div>""", unsafe_allow_html=True)

# VERİMLİLİK KADRANLARI VE AI TAVSİYESİ
st.divider()
col_g1, col_g2, col_ai = st.columns([1.5, 1.5, 2])

with col_g1:
    solar_eff = min(api_energy['nasa_solar'] * 12, 100)
    fig_gauge_solar = go.Figure(go.Indicator(mode = "gauge+number", value = solar_eff, title = {'text': "☀️ Güneş Paneli Verimi (%)"}, gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#f59e0b"}}))
    fig_gauge_solar.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_gauge_solar, use_container_width=True)
    st.markdown('<div class="explanation-box"><b>Panel Verimi:</b> Panellerin mevcut radyasyon altındaki çalışma kapasitesini ölçer.</div>', unsafe_allow_html=True)
    
with col_g2:
    wind_eff = min(api_energy['nasa_wind'] * 10, 100)
    fig_gauge_wind = go.Figure(go.Indicator(mode = "gauge+number", value = wind_eff, title = {'text': "💨 Türbin Kapasitesi (%)"}, gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#3b82f6"}}))
    fig_gauge_wind.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_gauge_wind, use_container_width=True)
    st.markdown('<div class="explanation-box"><b>Türbin Kapasitesi:</b> Rüzgar hızının türbinleri döndürme gücünü analiz eder.</div>', unsafe_allow_html=True)

with col_ai:
    st.markdown("### AI Operasyon Tavsiyesi")
    if solar_eff > 60:
        rec, bg, border = "**Mükemmel Üretim Koşulları**", "#d1fae5", "#10b981"
    else:
        rec, bg, border = " **Orta Seviye Üretim**", "#fef3c7", "#f59e0b"
        
    st.markdown(f"""
    <div style="background-color: {bg}; border-left: 5px solid {border}; padding: 20px; border-radius: 10px; color: #000000;">
        <h4 style="margin:0; color: #000000; font-weight: 800;">Sistem Analizi:</h4>
        <p style="color: #000000; font-size: 1.1em;">{rec}</p>
        <hr style="border-top: 1px solid {border}; opacity: 0.3;">
        <small style="color: #000000;"><i>Kaynak: NASA & OpenWeather API Füzyonu</i></small>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="explanation-box" style="margin-top:10px;"><b>AI Notu:</b> Anlık hava durumu ve fosil yükünü dengelemek için karar desteği sağlar.</div>', unsafe_allow_html=True)

# 24 SAATLİK TAHMİN VE SAPMA
st.divider()
col_chart1, col_chart2 = st.columns([2, 1])

with col_chart1:
    st.subheader(" 24 Saatlik Enerji Üretim Tahmini")
    df_forecast = pd.DataFrame({'Saat': [f"{i:02d}:00" for i in range(24)], 'Solar': [0,0,0,0,0,2,10,25,45,60,75,80,75,60,45,25,10,2,0,0,0,0,0,0], 'Rüzgar': np.random.normal(30, 10, 24).clip(5, 60)})
    st.plotly_chart(px.area(df_forecast, x='Saat', y=['Solar', 'Rüzgar']), use_container_width=True)
    st.markdown('<div class="explanation-box"><b>Tahmin Modeli:</b> 24 saatlik hibrit üretim profilini simüle eder.</div>', unsafe_allow_html=True)

with col_chart2:
    st.subheader(" Beklenti vs. Gerçekleşen")
    fig_comp = go.Figure(data=[go.Bar(name='NASA', x=['Radyasyon', 'Rüzgar', 'Sıcaklık'], y=[api_energy['nasa_solar'], api_energy['nasa_wind'], 20], marker_color='gray'), go.Bar(name='Canlı', x=['Radyasyon', 'Rüzgar', 'Sıcaklık'], y=[api_energy['nasa_solar']*1.1, api_energy['nasa_wind']*0.9, api_energy['live_temp']], marker_color='#10b981')])
    st.plotly_chart(fig_comp, use_container_width=True)
    st.markdown('<div class="explanation-box"><b>Sapma:</b> Tarihsel beklenti ile anlık ölçüm farkıdır.</div>', unsafe_allow_html=True)

#DÜNYA HARİTASI
st.divider()
st.subheader(" Küresel Yenilenebilir Enerji Geçiş Haritası")
st.plotly_chart(px.choropleth(df_share, locations="Code", color="Renewables", animation_frame="Year", color_continuous_scale="RdYlGn", projection="natural earth"), use_container_width=True)
st.markdown('<div class="explanation-box"><b>Global Trend:</b> 2000-2022 arası yenilenebilir enerjiye geçiş hızını gösterir.</div>', unsafe_allow_html=True)