import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    df = pd.read_csv('dataset/day.csv')
    df['dteday'] = pd.to_datetime(df['dteday'])
    df = df.drop(columns=['yr', 'mnth', 'weekday', 'instant'])
    df['tahun'] = df['dteday'].dt.year
    df['bulan'] = df['dteday'].dt.month
    df['hari'] = df['dteday'].dt.day_name()

    # mapping kategori
    df['cuaca_name'] = df['weathersit'].map({
        1: "Cerah",
        2: "Mendung",
        3: "Buruk Ringan",
        4: "Buruk Ekstrim"
    })
    df['season_name'] = df['season'].map({
        1: "Semi",
        2: "Panas",
        3: "Gugur",
        4: "Dingin"
    })
    return df

df = load_data()

# Sidebar
st.sidebar.title("Filter Data")
st.sidebar.markdown("---")

tahun_options = ['Semua'] + sorted(df['tahun'].unique().tolist())
selected_tahun = st.sidebar.selectbox("Pilih Tahun" , tahun_options)

musim_options = ['Semua'] + sorted(df['season_name'].unique().tolist())
selected_musim = st.sidebar.selectbox("Pilih Musim" , musim_options)

st.sidebar.markdown("---")  # BUG 1: -- diganti ---

min_date = df['dteday'].min().date()
max_date = df['dteday'].max().date()
date_range = st.sidebar.date_input("Pilih Range Tanggal" , [min_date , max_date])

filtered_df = df.copy()

if selected_musim != 'Semua' : 
    filtered_df = filtered_df[filtered_df['season_name'] == selected_musim]  # BUG 2: season diganti season_name

if selected_tahun != 'Semua' : 
    filtered_df = filtered_df[filtered_df['tahun'] == selected_tahun]

# BUG 3: filter tanggal (typo dan tidak terapply)
if len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])  # staet_date diganti start_date
    end_date = pd.to_datetime(date_range[1])
    filtered_df = filtered_df[(filtered_df['dteday'] >= start_date) & (filtered_df['dteday'] <= end_date)]  # baris ini ditambahkan

# Konten
st.title("Dashboard Dataset Bike Sharing")
st.markdown("Analisis Rental Sepeda Milik Capital Bikeshare system, Washington D.C., USA  Berdasarkan Data Harian (2011-2012)")
st.markdown("---")

# row 1
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_rental = filtered_df['cnt'].sum()
    st.metric("Total Rental" , f"{total_rental:,.0f}")

with col2:
    mean_rental = filtered_df['cnt'].mean()
    st.metric("Rata-Rata Per Hari Rental" , f"{mean_rental:,.0f}")

with col3:
    cas_sum = filtered_df['casual'].sum()
    st.metric("Jumlah Pengguna Casual" , f"{cas_sum:,.0f}")

with col4:
    cas_reg = filtered_df['registered'].sum()
    st.metric("Jumlah Pengguna Terdaftar" , f"{cas_reg:,.0f}")

st.markdown("---")

# row 2 - pertanyaan bisnis nomor 1
st.subheader("Bagaimana dampak cuaca terhadap penurunan rental sepeda, dan apakah pola tersebut berubah dari tahun 2011 ke 2012?")
col1, col2 = st.columns(2)
palette_cuaca = ['gold', 'gray', 'skyblue']  # BUG 4: urutan warna disesuaikan (Cerah, Mendung, Buruk Ringan)

with col1:
    fig, ax = plt.subplots(figsize=(8,5))
    sns.barplot(data=filtered_df, x='tahun' , y='cnt', hue='cuaca_name', palette=palette_cuaca, ax=ax)
    ax.set_title("Perbandingan Rental Saat Cerah, Mendung, Dan Cuaca Buruk Ringan")
    ax.set_xlabel("Tahun")
    ax.set_ylabel("Rata-Rata Rental")
    ax.legend(title='Kondisi Cuaca')
    st.pyplot(fig)

with col2:
    cuaca_statistik = filtered_df.groupby(['tahun', 'cuaca_name'])['cnt'].mean().round(0).unstack()
    st.write('Rata-Rata Rental Harian Per Kondisi Cuaca')
    st.dataframe(cuaca_statistik)

    cerah_2011 = cuaca_statistik.loc[2011, 'Cerah'] if 2011 in cuaca_statistik.index else 0
    mendung_2011 = cuaca_statistik.loc[2011, 'Mendung'] if 2011 in cuaca_statistik.index else 0
    br_2011 = cuaca_statistik.loc[2011, 'Buruk Ringan'] if 2011 in cuaca_statistik.index else 0

    # 2012
    cerah_2012 = cuaca_statistik.loc[2012, 'Cerah'] if 2012 in cuaca_statistik.index else 0  # BUG 5: if 2011 diganti if 2012
    mendung_2012 = cuaca_statistik.loc[2012, 'Mendung'] if 2012 in cuaca_statistik.index else 0  # BUG 5: if 2011 diganti if 2012
    br_2012 = cuaca_statistik.loc[2012, 'Buruk Ringan'] if 2012 in cuaca_statistik.index else 0  # BUG 5: if 2011 diganti if 2012

    st.write("### 📉 Statistik Rental")
    col_kiri, col_kanan = st.columns(2)  # BUG 6: colo1,colo2 diganti col_kiri,col_kanan

    if cerah_2011 > 0:
        with col_kiri:
            st.metric("2011: Cerah → Mendung", 
                  f"{(cerah_2011 - mendung_2011):.0f}", 
                  delta=f"{((cerah_2011 - mendung_2011)/cerah_2011*100):.1f}%")
            st.metric("2011: Cerah → Buruk Ringan", 
                  f"{(cerah_2011 - br_2011):.0f}", 
                  delta=f"{((cerah_2011 - br_2011)/cerah_2011*100):.1f}%")

    if cerah_2012 > 0:
        with col_kanan:
            st.metric("2012: Cerah → Mendung", 
                  f"{(cerah_2012 - mendung_2012):.0f}", 
                  delta=f"{((cerah_2012 - mendung_2012)/cerah_2012*100):.1f}%")
            st.metric("2012: Cerah → Buruk Ringan", 
                  f"{(cerah_2012 - br_2012):.0f}",  # BUG 7: mendung_2012 - br_2012 diganti cerah_2012 - br_2012
                  delta=f"{((cerah_2012 - br_2012)/cerah_2012*100):.1f}%")


with st.expander("Lihat Kesimpulan"):
    st.markdown("""- Cuaca adalah faktor penentu peminjaman sepeda
- Cuaca mendung turun hingga ~17% dan untuk Buruk Ringan hingga ~65% di kedua tahun
- Pola ini konsisten di tahun 2011 dan 2012""")

st.markdown('---')

# row Pertanyaan 2
st.subheader("Bagaimana perbandingan tren rental sepeda pengguna casual dan registered di tahun 2011 ke 2012?")

# Siapkan data
trend_df = filtered_df.groupby(['tahun', 'bulan'])[['casual', 'registered']].mean().reset_index()

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Plot 2011
trend_2011 = trend_df[trend_df['tahun'] == 2011] if 2011 in trend_df['tahun'].values else pd.DataFrame()
if not trend_2011.empty:
    axes[0].plot(trend_2011['bulan'], trend_2011['casual'], marker='o', color='orange', label='Casual')
    axes[0].plot(trend_2011['bulan'], trend_2011['registered'], marker='s', color='steelblue', label='Registered')
axes[0].set_title('Tahun 2011', fontsize=12)
axes[0].set_xlabel('Bulan')
axes[0].set_ylabel('Rata-rata per Hari')
axes[0].set_xticks(range(1,13))
axes[0].set_xticklabels(['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Ags','Sep','Okt','Nov','Des'], rotation=45)
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Plot 2012
trend_2012 = trend_df[trend_df['tahun'] == 2012] if 2012 in trend_df['tahun'].values else pd.DataFrame()
if not trend_2012.empty:
    axes[1].plot(trend_2012['bulan'], trend_2012['casual'], marker='o', color='orange', label='Casual')
    axes[1].plot(trend_2012['bulan'], trend_2012['registered'], marker='s', color='steelblue', label='Registered')
axes[1].set_title('Tahun 2012', fontsize=12)
axes[1].set_xlabel('Bulan')
axes[1].set_ylabel('Rata-rata per Hari')
axes[1].set_xticks(range(1,13))
axes[1].set_xticklabels(['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Ags','Sep','Okt','Nov','Des'], rotation=45)
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.suptitle('Perbandingan Tren Casual vs Registered', fontsize=14)
plt.tight_layout()
st.pyplot(fig)

with st.expander('Lihat Kesimpulan'):
    st.markdown("""- Registered user mendominasi (80% dari total rental)
- Kedua segmen memiliki pola musiman/bulanan yang SAMA
- Casual lebih fluktuatif, Registered lebih stabil""")

st.markdown("---")