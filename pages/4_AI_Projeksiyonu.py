import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import joblib
import os
from utils import load_all_datasets, setup_sidebar

st.set_page_config(page_title="AI Projeksiyonu", page_icon="🔮", layout="wide")
setup_sidebar()

st.markdown("""
    <style>
    .metric-container { background-color: #000000; color: #ffffff !important; padding: 20px; border-radius: 12px; border-left: 5px solid #10b981; text-align: center; margin-bottom: 15px; }
    .error-container { background-color: #f8f9fa; color: #000; padding: 15px; border-radius: 8px; border: 1px solid #dee2e6; text-align: center; }
    .analysis-card { background-color: #ffffff; border: 1px solid #e0e0e0; padding: 15px; border-radius: 10px; margin-top: 10px; color: #000; }
    </style>
    """, unsafe_allow_html=True)

# Veriyi çekiyoruz
df_co2, df_fossil, df_share, df_master = load_all_datasets()
selected_country = st.session_state.get("selected_country", "Turkey")

# JUNIOR-FIX: Renewables_TWh yerine artık sadece 'Renewables' kullanıyoruz (utils.py uyumu)
df_target = df_master[(df_master['Entity'] == selected_country)].dropna(
    subset=['Renewables', 'Year', 'Fossil fuels', 'Nuclear', 'Per capita emissions']
)

st.markdown(f"## 🔮 AI Model Laboratuvarı: {selected_country} 2040 Vizyonu")

MODEL_PATH = f"models/ai_vision_{selected_country}.pkl"

if not os.path.exists(MODEL_PATH):
    st.warning(f"⚠️ {selected_country} için eğitilmiş model bulunamadı. Lütfen ML Pipeline'ı çalıştırın.")
else:
    # Paketi açıyoruz
    model_pkg = joblib.load(MODEL_PATH)
    best_model = model_pkg["champion_model"]
    metrics = model_pkg["metrics"]
    poly_model = model_pkg["poly_model"]
    poly_transformer = model_pkg["poly_transformer"]
    
    r2, mae, rmse, mse = metrics['r2'], metrics['mae'], metrics['rmse'], metrics['mse']
    
    # ML modelinin beklediği özellik isimleri
    feature_cols = ["Year", "Fossil fuels", "Nuclear", "Per capita emissions"]

    # Üst Metrikler
    c_m1, c_m2, c_m3 = st.columns(3)
    with c_m1: st.markdown(f'<div class="metric-container"><h3> Şampiyon Model</h3><h2>{metrics["name"]}</h2><p>Doğruluk: %{r2*100:.2f}</p></div>', unsafe_allow_html=True)
    with c_m2: st.markdown(f'<div class="metric-container"><h3> Hedef</h3><h2>Yenilenebilir (TWh)</h2></div>', unsafe_allow_html=True)
    with c_m3: st.markdown(f'<div class="metric-container"><h3> Değişkenler</h3><h2>{len(feature_cols)} Faktör</h2></div>', unsafe_allow_html=True)

    # Teknik Metrik Kartları
    st.subheader(" Teknik Performans Skorları")
    e1, e2, e3, e4 = st.columns(4)
    with e1: st.markdown(f'<div class="error-container"><b>MSE</b><br><span style="font-size:18px; color:#d9534f;">{mse:.4f}</span></div>', unsafe_allow_html=True)
    with e2: st.markdown(f'<div class="error-container"><b>RMSE</b><br><span style="font-size:18px; color:#f0ad4e;">{rmse:.4f}</span></div>', unsafe_allow_html=True)
    with e3: st.markdown(f'<div class="error-container"><b>MAE</b><br><span style="font-size:18px; color:#5bc0de;">{mae:.4f}</span></div>', unsafe_allow_html=True)
    with e4: st.markdown(f'<div class="error-container"><b>R² (Skor)</b><br><span style="font-size:18px; color:#5cb85c;">{r2:.4f}</span></div>', unsafe_allow_html=True)

    st.divider()
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader(" Özellik Önemi")
        importance_df = pd.DataFrame({'Feature': feature_cols, 'Importance': metrics['importance']})
        fig_imp = px.bar(importance_df.sort_values('Importance'), x='Importance', y='Feature', orientation='h', color='Importance', color_continuous_scale='Greens')
        st.plotly_chart(fig_imp, use_container_width=True)

    with col_g2:
        st.subheader(" Gerçek vs. Tahmin (Tüm Veri)")
        X_all = df_target[feature_cols]
        preds = best_model.predict(X_all)
        # Renewables_TWh -> Renewables düzeltmesi
        fig_acc = px.scatter(x=df_target['Renewables'], y=preds, labels={'x': 'Gerçek', 'y': 'Tahmin'}, trendline="ols", trendline_color_override="red")
        st.plotly_chart(fig_acc, use_container_width=True)

    # --- 2040 VİZYONU (Inference) ---
    st.divider()
    st.subheader(f" {selected_country} 2040 Projeksiyonu")
    
    future_years = np.arange(df_target['Year'].max() + 1, 2041).reshape(-1, 1)
    future_preds = poly_model.predict(poly_transformer.transform(future_years)).clip(0, None)
    
    # Renewables_TWh -> Renewables düzeltmesi
    df_viz = pd.concat([
        df_target[['Year', 'Renewables']].assign(Type='Gerçek Veri'),
        pd.DataFrame({'Year': future_years.flatten(), 'Renewables': future_preds, 'Type': 'AI Projeksiyonu'})
    ])
    
    st.plotly_chart(px.line(df_viz, x='Year', y='Renewables', color='Type', markers=True, color_discrete_map={'Gerçek Veri': '#64748b', 'AI Projeksiyonu': '#10b981'}), use_container_width=True)