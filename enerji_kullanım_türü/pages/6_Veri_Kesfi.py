import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_all_datasets

# 1. SAYFA AYARI
st.set_page_config(page_title="Veri Keşfi", page_icon="📂", layout="wide")

st.markdown("""
    <style>
    .explanation-box {
        background-color: #f1f5f9;
        border-left: 5px solid #64748b;
        padding: 15px;
        margin-bottom: 20px;
        color: #334155;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. VERİ YÜKLEME VE HAZIRLIK
df_co2, df_fossil, df_share, df_supp = load_all_datasets()

df_master = pd.merge(df_fossil, df_co2[['Entity', 'Year', 'Per capita emissions']], on=['Entity', 'Year'], how='inner')
df_master['Total_Gen'] = df_master['Fossil fuels'] + df_master['Nuclear'] + df_master['Renewables']
df_master = df_master[df_master['Total_Gen'] > 5] 
df_master['Share_Fossil'] = (df_master['Fossil fuels'] / df_master['Total_Gen']) * 100
df_master['Share_Nuclear'] = (df_master['Nuclear'] / df_master['Total_Gen']) * 100
df_master['Share_Renewables'] = (df_master['Renewables'] / df_master['Total_Gen']) * 100

# 3. ARAYÜZ
st.markdown("##  Global Veri Keşfi ve Liderlik Tabloları")

year_select = st.slider("Analiz Yılı", 2000, 2022, 2022)
df_year = df_master[df_master['Year'] == year_select]

col_top1, col_top2 = st.columns(2)
with col_top1:
    st.markdown("###  En Yeşil 10 Ülke")
    top_green = df_year.sort_values("Share_Renewables", ascending=False).head(10)
    st.plotly_chart(px.bar(top_green, x="Share_Renewables", y="Entity", orientation='h', color="Share_Renewables", color_continuous_scale="Greens"), use_container_width=True)
with col_top2:
    st.markdown("###  En Fosil Bağımlı 10 Ülke")
    top_fossil = df_year.sort_values("Share_Fossil", ascending=False).head(10)
    st.plotly_chart(px.bar(top_fossil, x="Share_Fossil", y="Entity", orientation='h', color="Share_Fossil", color_continuous_scale="Reds"), use_container_width=True)

st.divider()
st.subheader(" İstatistik Laboratuvarı")
corr_matrix = df_master[['Share_Fossil', 'Share_Nuclear', 'Share_Renewables', 'Per capita emissions']].corr()
st.plotly_chart(px.imshow(corr_matrix, text_auto=".2f", color_continuous_scale="RdBu_r", title="Korelasyon Matrisi"), use_container_width=True)

st.divider()
st.subheader(" Stratejik Kadrant Analizi")
fig_quad = px.scatter(df_year, x="Share_Fossil", y="Share_Renewables", size="Total_Gen", color="Share_Nuclear", hover_name="Entity")
fig_quad.add_hline(y=50, line_dash="dash")
fig_quad.add_vline(x=50, line_dash="dash")
st.plotly_chart(fig_quad, use_container_width=True)

#5. VERİ İNDİRME VE DIŞA AKTARIM 
st.divider()
st.subheader(" Veri Setini Dışa Aktar")

# İndirme işlemi için veriyi CSV formatına çeviriyoruz
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv_data = convert_df(df_master)

col_dl1, col_dl2 = st.columns([1, 2])

with col_dl1:
    st.download_button(
        label=" Tüm Veriyi CSV Olarak İndir",
        data=csv_data,
        file_name=f'global_energy_data_master.csv',
        mime='text/csv',
        help="Analiz edilen tüm ülkelerin birleştirilmiş master veri setini indirir."
    )

with col_dl2:
    st.info("""
    **💡 Bilgi:** İndirdiğiniz dosya; Fosil, Nükleer, Yenilenebilir payları ve Kişi Başı Emisyon verilerinin 
    tüm yıllar için birleştirilmiş (merged) halini içerir. Excel veya Python ile analiz edebilirsiniz.
    """)