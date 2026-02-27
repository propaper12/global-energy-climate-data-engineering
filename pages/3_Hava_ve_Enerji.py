import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from utils import load_all_datasets, setup_sidebar, fetch_nasa_historical_trends

# 1. SAYFA KONFİGÜRASYONU
st.set_page_config(page_title="Hava ve Enerji Analitiği", page_icon="📡", layout="wide")

setup_sidebar()

st.markdown("""
    <style>
    .explanation-box {
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
        color: #000000; /* Yazıları tam siyah yaptık */
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. VERİ YÜKLEME
df_co2, df_fossil, df_share, df_supp = load_all_datasets()
selected_country = st.session_state.get("selected_country", "Turkey")

# 3. SAYFA İÇERİĞİ
st.markdown(f"##  Atmosferik Zeka ve Enerji Verimliliği Laboratuvarı: {selected_country}")
st.markdown('<div class="explanation-box">Bu bölümde, NASA ve OpenWeather verilerini işleyerek "Ne zaman üretmeliyiz?" ve "Hangi hava koşulları verimliliği düşürüyor?" sorularına yanıt arıyoruz.</div>', unsafe_allow_html=True)

#1. NASA TARİHSEL TREND ANALİZİ (2000-2025)
st.divider()
st.subheader(f" {selected_country}: 25 Yıllık Atmosferik Trendler (2000-2025)")

loc_map = {"Turkey": [39.9, 32.8], "United States": [37.1, -95.7], "China": [35.9, 104.2], "Germany": [51.1, 10.4]}
lat_lon = loc_map.get(selected_country, [39.9, 32.8])

# NASA'dan 25 yıllık veriyi çek
df_nasa = fetch_nasa_historical_trends(lat_lon[0], lat_lon[1])

col_h1, col_h2 = st.columns(2)
with col_h1:
    fig_solar_line = px.line(df_nasa, x="Year", y="NASA_Solar", title="Yıllık Güneş Radyasyonu Trendi (kW/m²)", markers=True)
    fig_solar_line.update_traces(line_color="#f59e0b")
    st.plotly_chart(fig_solar_line, use_container_width=True)
    st.markdown('<div class="explanation-box"><b>Güneş Trendi:</b> Son 25 yılda bölgeye düşen yıllık ortalama radyasyon miktarındaki değişimi gösterir.</div>', unsafe_allow_html=True)

with col_h2:
    fig_wind_line = px.area(df_nasa, x="Year", y="NASA_Wind", title="Yıllık Ortalama Rüzgar Hızı (m/s)")
    fig_wind_line.update_traces(line_color="#3b82f6")
    st.plotly_chart(fig_wind_line, use_container_width=True)
    st.markdown('<div class="explanation-box"><b>Rüzgar Trendi:</b> Bölgedeki rüzgar potansiyelinin yıllara göre kararlılığını analiz eder.</div>', unsafe_allow_html=True)

#2. GÜNEŞ ENERJİSİ ISI HARİTASI (GOLDEN HOURS)
st.divider()
st.subheader("'Altın Saatler' (Golden Hours) Matrisi")

months = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
hours = [f"{i:02d}:00" for i in range(24)]

z_data = []
for h in range(24):
    row = []
    for m in range(12):
        if 6 <= h <= 19:
            intensity = np.sin((h-6)/13 * np.pi) * (1 + np.sin((m)/12 * np.pi)) * 50
            val = max(0, intensity + np.random.uniform(-5, 5))
        else: val = 0
        row.append(val)
    z_data.append(row)
    
fig_heat = go.Figure(data=go.Heatmap(z=z_data, x=months, y=hours, colorscale='Magma'))
fig_heat.update_layout(title="Aylık ve Saatlik Güneş Enerjisi Yoğunluğu", height=500)
st.plotly_chart(fig_heat, use_container_width=True)
st.markdown('<div class="explanation-box"><b>Isı Haritası:</b> Maksimum üretimin yakalanabileceği "Altın Saatleri" tek bakışta gösterir.</div>', unsafe_allow_html=True)

#3. RÜZGAR VE PANEL VERİM ANALİZİ
st.divider()
col_w1, col_w2 = st.columns(2)

with col_w1:
    st.subheader(" Rüzgar Hızı Frekans Dağılımı")
    wind_speeds = np.random.weibull(2, 1000) * 6 
    fig_hist = px.histogram(x=wind_speeds, nbins=40, color_discrete_sequence=['#3b82f6'])
    fig_hist.add_vline(x=3.5, line_dash="dash", line_color="#ef4444", annotation_text="Cut-in (3.5 m/s)")
    st.plotly_chart(fig_hist, use_container_width=True)
    st.markdown('<div class="explanation-box"><b>Frekans Analizi:</b> Rüzgarın ne sıklıkla türbinleri döndürecek hıza ulaştığını gösterir.</div>', unsafe_allow_html=True)

with col_w2:
    st.subheader(" Isı Kaynaklı Verimlilik Kaybı")
    temps = np.linspace(0, 50, 100)
    eff = [100 if t <= 25 else 100 - (t-25)*0.45 for t in temps]
    fig_eff = px.area(x=temps, y=eff, title="Sıcaklık vs Panel Verimi", color_discrete_sequence=['#f59e0b'])
    fig_eff.update_yaxes(range=[80, 102])
    st.plotly_chart(fig_eff, use_container_width=True)
    st.markdown('<div class="explanation-box"><b>Termal Analiz:</b> 25°C üstündeki her derecenin panel verimine negatif etkisini simüle eder.</div>', unsafe_allow_html=True)

# VERİ İNDİRME
st.divider()
csv_nasa = df_nasa.to_csv(index=False).encode('utf-8')
st.download_button(" NASA 2000-2025 Tarihsel Verilerini İndir", data=csv_nasa, file_name=f"{selected_country}_nasa_trends.csv")