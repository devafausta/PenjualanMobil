import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman Website
st.set_page_config(page_title="Dashboard Penjualan Mobil", layout="wide")

# DESAIN
st.markdown("""
<style>
/* Mengubah background kotak metrik menjadi biru gelap dengan efek 3D shadow */
[data-testid="stMetric"] {
    background-color: #1A5276; 
    padding: 15px;
    border-radius: 12px;
    box-shadow: 4px 6px 12px rgba(0, 0, 0, 0.5), 
                inset -2px -2px 6px rgba(0, 0, 0, 0.3), 
                inset 2px 2px 6px rgba(255, 255, 255, 0.2);
}
/* Mengubah warna label (judul) metrik menjadi putih */
[data-testid="stMetricLabel"] {
    color: #ffffff !important; 
    font-weight: bold;
}
/* Mengubah warna nilai (angka) metrik menjadi putih */
[data-testid="stMetricValue"] {
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

st.title("Dashboard Penjualan Mobil GAIKINDO (2018-2025)")
st.markdown("Visualisasi interaktif ini menampilkan tren distribusi kendaraan roda empat di Indonesia.")

# 2. Memanggil Data
@st.cache_data
def load_data():
    df = pd.read_csv("Data_Total_Penjualan_Gaikindo_2018_2025.csv")
    df['Total Penjualan'] = pd.to_numeric(df['Total Penjualan'].astype(str).str.replace(r'\D', '', regex=True), errors='coerce').fillna(0)
    return df

df = load_data()

# FITUR SEARCH BAR & TOMBOL HOME

# Membuat state default untuk pencarian
if 'search_brand' not in st.session_state:
    st.session_state.search_brand = "-- Tampilkan Semua (Home) --"

def reset_home():
    st.session_state.search_brand = "-- Tampilkan Semua (Home) --"

# Tata letak kolom pencarian dan tombol home
col_search, col_btn = st.columns([8, 2])
with col_search:
    daftar_merek = sorted(df['Brand'].unique().tolist())
    pilihan_cari = st.selectbox(
        "🔍 Cari Statistik Merek Mobil:", 
        options=["-- Tampilkan Semua (Home) --"] + daftar_merek, 
        key='search_brand'
    )

with col_btn:
    st.write("") # Memberikan jarak spasi kosong agar sejajar dengan selectbox
    st.write("")
    st.button("🏠 Kembali ke Home", on_click=reset_home, use_container_width=True)

st.divider()

# LOGIKA TAMPILAN DASHBOARD
if st.session_state.search_brand == "-- Tampilkan Semua (Home) --":
    # TAMPILAN DASHBOARD UTAMA (JIKA TIDAK ADA YANG DICARI)
    
    st.markdown("### Ringkasan Penjualan (2018-2025)")
    metrik1, metrik2, metrik3, metrik4 = st.columns(4)

    # Menghitung data untuk metrik
    merek_terlaris = df.groupby('Brand')['Total Penjualan'].sum().idxmax()
    total_seluruh_penjualan = df['Total Penjualan'].sum()
    total_per_tahun = df.groupby('Tahun')['Total Penjualan'].sum().reset_index()
    tahun_terbaik = total_per_tahun.loc[total_per_tahun['Total Penjualan'].idxmax(), 'Tahun']
    tahun_terburuk = total_per_tahun.loc[total_per_tahun['Total Penjualan'].idxmin(), 'Tahun']

    # Menampilkan metrik
    with metrik1:
        st.metric("Merek Terlaris", merek_terlaris)
    with metrik2:
        st.metric("Total Penjualan Keseluruhan", f"{total_seluruh_penjualan:,.0f}".replace(',', '.'))
    with metrik3:
        st.metric("Tahun Penjualan Terbaik", int(tahun_terbaik))
    with metrik4:
        st.metric("Tahun Penjualan Terburuk", int(tahun_terburuk))

    st.divider() 

    # Membagi Layar Menjadi Dua Kolom untuk Grafik Atas
    col1, col2 = st.columns(2)

    # Kolom 1: Tren Total Penjualan Seluruh Merek
    with col1:
        st.subheader("Tren Total Penjualan per Tahun")
        fig_trend = px.line(total_per_tahun, x='Tahun', y='Total Penjualan', markers=True, 
                            line_shape='spline',
                            labels={'Total Penjualan': 'Total Unit terjual'})
        fig_trend.update_layout(dragmode=False)
        st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})

    # Kolom 2: Top 10 Merek Penjualan Terbanyak
    with col2:
        st.subheader("Top 10 Merek Terlaris (Keseluruhan 2018-2025)")
        top_brands = df.groupby('Brand')['Total Penjualan'].sum().reset_index()
        top_10 = top_brands.sort_values('Total Penjualan', ascending=False).head(10)
        
        fig_bar = px.bar(top_10, x='Brand', y='Total Penjualan', text='Total Penjualan')
        fig_bar.update_traces(marker_color='#1f77b4', texttemplate='%{text:,.0f}', textposition='outside')
        fig_bar.update_layout(
            xaxis_title="Merek Mobil",
            yaxis_title="Total Penjualan (Unit)",
            xaxis_tickangle=-45,
            xaxis={'categoryorder':'total descending'}, 
            dragmode=False
        )
        fig_bar.update_yaxes(range=[0, top_10['Total Penjualan'].max() * 1.25])
        st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

    # Membuat Top 10 Berdasarkan Tahun Pilihan
    st.divider() 
    st.subheader("Top 10 Merek Terlaris Berdasarkan Tahun")

    daftar_tahun = sorted(df['Tahun'].unique(), reverse=True)
    pilihan_tahun = st.selectbox("Pilih Tahun Analisis:", options=daftar_tahun)

    df_tahun = df[df['Tahun'] == pilihan_tahun]
    top_10_tahun = df_tahun.groupby('Brand')['Total Penjualan'].sum().reset_index()
    top_10_tahun = top_10_tahun.sort_values('Total Penjualan', ascending=False).head(10)

    fig_bar_tahun = px.bar(top_10_tahun, x='Brand', y='Total Penjualan', text='Total Penjualan')
    fig_bar_tahun.update_traces(marker_color='#ff7f0e', texttemplate='%{text:,.0f}', textposition='outside')
    fig_bar_tahun.update_layout(
        xaxis_title="Merek Mobil",
        yaxis_title="Total Penjualan (Unit)",
        xaxis_tickangle=-45,
        xaxis={'categoryorder':'total descending'},
        dragmode=False
    )
    fig_bar_tahun.update_yaxes(range=[0, top_10_tahun['Total Penjualan'].max() * 1.25])
    st.plotly_chart(fig_bar_tahun, use_container_width=True, config={'displayModeBar': False})

    # Bagian Bawah: Grafik Interaktif Pembanding Merek
    st.divider()
    st.subheader("Bandingkan Performa Penjualan Antar Merek")

    pilihan_merek = st.multiselect(
        "Pilih merek mobil yang ingin dibandingkan:", 
        options=df['Brand'].unique(), 
        default=['TOYOTA', 'DAIHATSU', 'HONDA']
    )

    df_filter = df[df['Brand'].isin(pilihan_merek)]

    if not df_filter.empty:
        fig_compare = px.line(df_filter, x='Tahun', y='Total Penjualan', color='Brand', markers=True)
        fig_compare.update_layout(dragmode=False) 
        st.plotly_chart(fig_compare, use_container_width=True, config={'displayModeBar': False})
    else:
        st.warning("Silakan pilih minimal satu merek mobil untuk melihat grafiknya.")

else:
    # TAMPILAN HALAMAN PENCARIAN (JIKA MEREK DIPILIH)
    merek_dipilih = st.session_state.search_brand
    st.subheader(f"Statistik Penjualan: {merek_dipilih}")
    df_brand_detail = df[df['Brand'] == merek_dipilih].sort_values('Tahun')

    # Menampilkan Line Chart Detail
    fig_detail = px.line(df_brand_detail, x='Tahun', y='Total Penjualan', markers=True, text='Total Penjualan')
    fig_detail.update_traces(textposition='top center', texttemplate='%{text:,.0f}', marker_color='#ff7f0e', line_color='#ff7f0e')
    fig_detail.update_layout(
        yaxis_title="Total Penjualan (Unit)",
        xaxis_title="Tahun",
        dragmode=False
    )

    fig_detail.update_yaxes(range=[0, df_brand_detail['Total Penjualan'].max() * 1.3])
    st.plotly_chart(fig_detail, use_container_width=True, config={'displayModeBar': False})

    # Menampilkan Tabel Data yang Sudah Dirapikan
    st.markdown("#### Tabel Data Penjualan")
    
    # Mengambil kolom yang dibutuhkan
    tabel_rapi = df_brand_detail[['Tahun', 'Brand', 'Total Penjualan']].copy()
    total_keseluruhan = tabel_rapi['Total Penjualan'].sum()
    baris_total = pd.DataFrame([{'Tahun': '', 'Brand': 'TOTAL PENJUALAN', 'Total Penjualan': total_keseluruhan}])
    tabel_rapi = pd.concat([tabel_rapi, baris_total], ignore_index=True)
    indeks_baru = list(range(1, len(tabel_rapi))) + ['']
    tabel_rapi.index = indeks_baru
    st.dataframe(tabel_rapi, use_container_width=True)
