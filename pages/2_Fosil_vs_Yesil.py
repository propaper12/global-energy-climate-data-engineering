import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from utils import load_all_datasets

# 1. SAYFA KONFİGÜRASYONU
st.set_page_config(page_title="Fosil vs Yeşil", page_icon="🔥", layout="wide")

st.markdown("""
    <style>
    .metric-container {
        background-color: #000000;
        color: #ffffff !important;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #3b82f6;
        text-align: center;
        margin-bottom: 15px;
    }
    .metric-container h2 { margin: 5px 0; font-weight: 800; font-size: 24px !important; }
    .badge-fossil { background-color: #ef4444; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.7em; }
    .badge-green { background-color: #10b981; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.7em; }
    .badge-ai { background-color: #8b5cf6; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.7em; }
    .explanation-box {
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
        color: #0d47a1;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. VERİ YÜKLEME VE FİLTRELEME
df_co2, df_fossil, df_share, df_supp = load_all_datasets()

# Hafızadan (Session State) seçili ülkeyi al
if "selected_country" in st.session_state:
    selected_country = st.session_state["selected_country"]
else:
    selected_country = "Turkey"

entities = sorted(df_fossil['Entity'].unique())
selected_country = st.sidebar.selectbox("📍 Bölge Değiştir", entities, index=entities.index(selected_country))
st.session_state["selected_country"] = selected_country

st.markdown(f"## 🔥 {selected_country}: Enerji Geçiş Savaşı (The Transition Battlefield)")
st.markdown('<div class="explanation-box">Bu bölümde, fosil yakıtların hakimiyetini kaybetme sürecini ve yeşil enerjinin yükseliş ivmesini "Makas Analizi" ve "Momentum İndeksi" ile inceliyoruz.</div>', unsafe_allow_html=True)

# Veri Hazırlığı
df_target = df_fossil[df_fossil['Entity'] == selected_country].sort_values('Year')

# KPI Hesaplamaları
if not df_target.empty:
    latest_data = df_target.iloc[-1]
    fossil_share = latest_data['Fossil fuels']
    green_share = latest_data['Renewables']
    gap = fossil_share - green_share # Pozitifse Fosil önde, Negatifse Yeşil önde
    
    # Crossover Tahmini (Basit Lineer Regresyon ile Makasın Kapanacağı Yıl)
    if gap > 0:
        # Son 10 yılın trendine bak
        df_trend = df_target.tail(10)
        trend_gap = df_trend['Fossil fuels'] - df_trend['Renewables']
        
        # Model kurmak için yeterli veri var mı?
        if len(df_trend) > 1:
            model_gap = LinearRegression().fit(df_trend[['Year']], trend_gap)
            if model_gap.coef_[0] != 0:
                crossover_year = int(-model_gap.intercept_ / model_gap.coef_[0])
                if 2024 <= crossover_year <= 2100:
                    status_text = f"Tahmini Geçiş: {crossover_year}"
                    status_color = "#f59e0b" 
                else:
                    status_text = "Dönüşüm Çok Yavaş"
                    status_color = "#ef4444" 
            else:
                status_text = "Değişim Yok"
                status_color = "#ef4444"
        else:
            status_text = "Yetersiz Veri"
            status_color = "#94a3b8"
    else:
        status_text = " YEŞİL HAKİMİYETİ SAĞLANDI"
        status_color = "#10b981" # Yeşil

    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(f"""
        <div class="metric-container">
            <span class="badge-fossil">FOSİL GÜCÜ</span>
            <h3>Mevcut Üretim</h3>
            <h2>{fossil_share:.0f} TWh</h2>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="metric-container">
            <span class="badge-green">YEŞİL GÜCÜ</span>
            <h3>Mevcut Üretim</h3>
            <h2>{green_share:.0f} TWh</h2>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="metric-container" style="border-left: 5px solid {status_color};">
            <span class="badge-ai">AI TAHMİNİ</span>
            <h3>Kritik Eşik</h3>
            <h2>{status_text}</h2>
        </div>""", unsafe_allow_html=True)

    st.divider()
    col_battle, col_gap = st.columns([2, 1])
    
    with col_battle:
        st.subheader("⚔️ Üretim Sahası: Kim Kazanıyor?")
        fig_battle = px.area(df_target, x="Year", y=["Fossil fuels", "Renewables"],
                             color_discrete_map={"Fossil fuels": "#334155", "Renewables": "#10b981"},
                             title="TWh Bazında Pazar Payı Savaşı")
        # Son yıl işaretlemesi
        fig_battle.add_annotation(x=latest_data['Year'], y=latest_data['Fossil fuels'],
                                  text="Fosil", showarrow=False, yshift=10)
        st.plotly_chart(fig_battle, use_container_width=True)
        st.markdown('<div class="explanation-box">Gri alan fosil yakıtları, yeşil alan yenilenebilir enerjiyi temsil eder. Yeşil alanın griyi ne zaman ve nasıl baskıladığını izleyin.</div>', unsafe_allow_html=True)

    with col_gap:
        st.subheader("✂️ Makas Analizi (The Gap)")
        # Makas (Gap) Verisi
        df_target['Gap'] = df_target['Fossil fuels'] - df_target['Renewables']
        df_target['Leader'] = df_target['Gap'].apply(lambda x: 'Fosil Önde' if x > 0 else 'Yeşil Önde')
        
        fig_gap = px.bar(df_target, x='Year', y='Gap', color='Leader',
                         color_discrete_map={'Fosil Önde': '#ef4444', 'Yeşil Önde': '#10b981'},
                         title="Fark Analizi (Fosil - Yeşil)")
        fig_gap.update_layout(showlegend=False)
        st.plotly_chart(fig_gap, use_container_width=True)
        st.markdown('<div class="explanation-box">Çubuklar sıfırın altına indiğinde, o yıl ülkenin yeşil devrimi gerçekleştirdiği yıldır.</div>', unsafe_allow_html=True)

    #MOMENTUM İNDEKSİ (BÜYÜME HIZI)
    st.divider()
    st.subheader(" Momentum İndeksi (2000 Yılı = 100)")
    
    base_year_data = df_target[df_target['Year'] == 2000]
    
    if not base_year_data.empty:
        base_fossil = base_year_data['Fossil fuels'].values[0]
        base_green = base_year_data['Renewables'].values[0]
        
        base_fossil = base_fossil if base_fossil > 0 else 1
        base_green = base_green if base_green > 0 else 1
        
        df_target['Fossil_Index'] = (df_target['Fossil fuels'] / base_fossil) * 100
        df_target['Green_Index'] = (df_target['Renewables'] / base_green) * 100
        
        fig_momentum = go.Figure()
        fig_momentum.add_trace(go.Scatter(x=df_target['Year'], y=df_target['Fossil_Index'], name='Fosil İvmesi', line=dict(color='gray', dash='dot')))
        fig_momentum.add_trace(go.Scatter(x=df_target['Year'], y=df_target['Green_Index'], name='Yeşil Enerji İvmesi', line=dict(color='#10b981', width=4)))
        
        fig_momentum.update_layout(title="Büyüme Hızı Karşılaştırması (Kümülatif Artış)", yaxis_title="Endeks Puanı (2000=100)")
        st.plotly_chart(fig_momentum, use_container_width=True)
        st.markdown('<div class="explanation-box">Bu grafik hacmi değil, <b>hızı</b> ölçer. Yeşil çizginin ne kadar dik yükseldiği, yatırımların agresifliğini gösterir.</div>', unsafe_allow_html=True)
    else:
        st.warning("Momentum hesabı için 2000 yılı verisi eksik (Verisetinde bulunamadı).")

else:
    st.error(f"Seçilen ülke ({selected_country}) için veri bulunamadı.")