import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman Website
st.set_page_config(page_title="Dashboard Penjualan Mobil", layout="wide")
st.title("Dashboard Penjualan Mobil GAIKINDO (2018-2025)")
st.markdown("Visualisasi interaktif ini menampilkan tren distribusi kendaraan roda empat di Indonesia.")

# 2. Memanggil Data
@st.cache_data
def load_data():
    df = pd.read_csv("Data_Total_Penjualan_Gaikindo_2018_2025.csv")

    df['Total Penjualan'] = pd.to_numeric(df['Total Penjualan'].astype(str).str.replace(r'\D', '', regex=True), errors='coerce').fillna(0)
    
    return df

df = load_data()

# 3. Membagi Layar Menjadi Dua Kolom untuk Grafik Atas
col1, col2 = st.columns(2)

# Kolom 1: Tren Total Penjualan Seluruh Merek (Line Chart)
with col1:
    st.subheader("Tren Total Penjualan per Tahun")
    total_per_tahun = df.groupby('Tahun')['Total Penjualan'].sum().reset_index()
    fig_trend = px.line(total_per_tahun, x='Tahun', y='Total Penjualan', markers=True, 
                        line_shape='spline',
                        labels={'Total Penjualan': 'Total Unit terjual'})
    st.plotly_chart(fig_trend, use_container_width=True)

# Kolom 2: Top 10 Merek Penjualan Terbanyak (Bar Chart Keseluruhan)
with col2:
    st.subheader("Top 10 Merek Terlaris (Keseluruhan 2018-2025)")
    top_brands = df.groupby('Brand')['Total Penjualan'].sum().reset_index()
    top_10 = top_brands.sort_values('Total Penjualan', ascending=False).head(10)
    
    # Bikin barchart vertikal
    fig_bar = px.bar(top_10, x='Brand', y='Total Penjualan', text='Total Penjualan')
    
    # Setting
    fig_bar.update_traces(marker_color='#1f77b4', texttemplate='%{text:,.0f}', textposition='outside')
    fig_bar.update_layout(
        xaxis_title="Merek Mobil",
        yaxis_title="Total Penjualan (Unit)",
        xaxis_tickangle=-45,
        xaxis={'categoryorder':'total descending'} # Urutkan dari yang paling laris
    )
    
    fig_bar.update_yaxes(range=[0, top_10['Total Penjualan'].max() * 1.25])
    
    st.plotly_chart(fig_bar, use_container_width=True)

# 4. Membuat Top 10 Berdasarkan Tahun Pilihan
st.divider() # Garis pembatas
st.subheader("Top 10 Merek Terlaris Berdasarkan Tahun")

# Dropdown untuk memilih tahun (diurutkan otomatis dari tahun terbaru)
daftar_tahun = sorted(df['Tahun'].unique(), reverse=True)
pilihan_tahun = st.selectbox("Pilih Tahun Analisis:", options=daftar_tahun)

# Memfilter data hanya untuk tahun yang dipilih
df_tahun = df[df['Tahun'] == pilihan_tahun]

# Mengambil top 10 merek di tahun tersebut
top_10_tahun = df_tahun.groupby('Brand')['Total Penjualan'].sum().reset_index()
top_10_tahun = top_10_tahun.sort_values('Total Penjualan', ascending=False).head(10)

# Membuat Bar Chart dengan warna berbeda (oranye) agar kontras dengan grafik di atas
fig_bar_tahun = px.bar(top_10_tahun, x='Brand', y='Total Penjualan', text='Total Penjualan')
fig_bar_tahun.update_traces(marker_color='#ff7f0e', texttemplate='%{text:,.0f}', textposition='outside')
fig_bar_tahun.update_layout(
    xaxis_title="Merek Mobil",
    yaxis_title=f"Total Penjualan (Unit)",
    xaxis_tickangle=-45,
    xaxis={'categoryorder':'total descending'}
)
# Menyesuaikan tinggi atap grafik
fig_bar_tahun.update_yaxes(range=[0, top_10_tahun['Total Penjualan'].max() * 1.25])

st.plotly_chart(fig_bar_tahun, use_container_width=True)

# 5. Bagian Bawah: Grafik Interaktif Pembanding Merek
st.divider() # Garis pembatas
st.subheader("Bandingkan Performa Penjualan Antar Merek")

# Membuat filter multiselect 
pilihan_merek = st.multiselect(
    "Pilih merek mobil yang ingin dibandingkan:", 
    options=df['Brand'].unique(), 
    default=['TOYOTA', 'DAIHATSU', 'HONDA']
)

# Memfilter data sesuai merek yang dipilih
df_filter = df[df['Brand'].isin(pilihan_merek)]

# Menampilkan Line Chart untuk merek yang dipilih
if not df_filter.empty:
    fig_compare = px.line(df_filter, x='Tahun', y='Total Penjualan', color='Brand', markers=True)
    st.plotly_chart(fig_compare, use_container_width=True)
else:
    st.warning("Silakan pilih minimal satu merek mobil untuk melihat grafiknya.")