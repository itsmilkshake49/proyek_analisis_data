import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import numpy as np
from babel.numbers import format_currency

sns.set(style='dark')

#Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv(r"C:\Users\Dell\Desktop\DICODING\Python\proyek_andat1\Dashboard\all_df.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df

all_df = load_data()

#Fungsi untuk visualisasi data
## Fungsi menentukan musim berdasarkan bulan
def get_season(month):
    if month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    elif month in [9, 10, 11]:
        return 'Autumn'
    else:
        return 'Winter'

## Tambahkan kolom musim
all_df["season"] = all_df["date"].dt.month.apply(get_season)

# Fungsi untuk kategori PM2.5
def categorize_pm25(value):
    if value <= 50:
        return "Rendah"
    elif value <= 100:
        return "Sedang"
    elif value <= 150:
        return "Tinggi"
    else:
        return "Sangat Tinggi"

all_df['Kategori_PM2.5'] = all_df['PM2.5'].apply(categorize_pm25)

#Menambah header
st.title("Air Quality Dashboard 🌬️")

#Sidebar untuk filter
st.sidebar.header("Filter")
station = st.sidebar.selectbox("Pilih Stasiun", ["Semua"] + list(all_df['station'].unique()))
start_date = st.sidebar.date_input("Tanggal Mulai", all_df['date'].min())
end_date = st.sidebar.date_input("Tanggal Akhir", all_df['date'].max())

#Filter dataset
if station == "Semua":
    filtered_df = all_df[(all_df['date'] >= str(start_date)) & (all_df['date'] <= str(end_date))]
else:
    filtered_df = all_df[(all_df['station'] == station) & (all_df['date'] >= str(start_date)) & (all_df['date'] <= str(end_date))]

#Menampilkan data yang sudah difilter
st.write(f"### Data Kualitas Udara: {station}")
st.dataframe(filtered_df.head())

# Menampilkan metrik untuk Tingkat Polusi
st.subheader("Informasi Tingkat Polusi")
polutants = ["PM2.5", "PM10"]
status_colors = {"Rendah": "green", "Sedang": "yellow", "Tinggi": "red", "Sangat Tinggi": "black"}

for polutant in polutants:
    col1, col2 = st.columns(2)
    with col1:
        value = round(filtered_df[polutant].mean(), 2)
        status = "Rendah" if value <= 50 else "Sedang" if value <= 100 else "Tinggi" if value <=200 else "Sangat Tinggi"
        color = status_colors.get(status, "gray")
        st.markdown(f"""
            <div style="background-color:{color};padding:15px;border-radius:10px;text-align:center;">
                <h2 style="color:white;">{polutant} Level: {value} µg/m³</h2>
                <h3 style="color:white;">Status: {status}</h3>
            </div>
        """, unsafe_allow_html=True)

# Visualisasi 1
st.subheader("Distribusi Polusi perMusim di 5 Daerah")
fig, ax = plt.subplots(figsize=(16, 8))
palette_colors = {'Spring': 'lightgray', 'Summer': 'lightgray', 'Autumn': 'lightgray', 'Winter': 'lightblue'}
sns.boxplot(x='season', y='PM2.5', data=all_df, hue='season', palette=palette_colors, dodge=False, ax=ax)
plt.xlabel("Musim")
plt.ylabel("PM2.5")
plt.grid(True)
st.pyplot(fig)

# Visualisasi 2
st.subheader("Distribusi Tingkat Polusi Berdasarkan Kategori")
fig, ax = plt.subplots(figsize=(16, 8))
sns.countplot(x="station", hue="Kategori_PM2.5", data=all_df, palette="coolwarm", ax=ax)
plt.xlabel("Lokasi")
plt.ylabel("Jumlah Observasi")
plt.legend(title="Kategori Polusi")
st.pyplot(fig)

# Visualisasi 3
st.subheader("Tren Rata-rata Polusi di 5 Daerah Periode 2013-2017")
all_df["year"] = all_df["date"].dt.year
pm25_per_year = all_df.groupby(['year', 'station'])['PM2.5'].mean().unstack()
fig, ax = plt.subplots(figsize=(16, 8))
for area in pm25_per_year.columns:
    ax.plot(pm25_per_year.index, pm25_per_year[area], marker="o", label=area)
ax.set_xlabel("Tahun")
ax.set_ylabel("Rata-rata PM2.5")
ax.legend()
ax.grid(True)
st.pyplot(fig)

# Visualisasi 4: Heatmap Korelasi
st.subheader("Heatmap Korelasi Data Polusi Udara")
corr_matrix = all_df.select_dtypes(include=[np.number]).corr()
fig, ax = plt.subplots(figsize=(16, 8))
sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", linewidths=0.5, ax=ax)
st.pyplot(fig)

# Ringkasan Statistik per Daerah
st.write("## Ringkasan Statistik per Daerah")
if station == "Semua":
    summary_df = all_df.groupby('station')[['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'wd', 'WSPM']].describe().round(2)
else:
    summary_df = filtered_df[['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'wd', 'WSPM']].describe().round(2)
st.write(summary_df)

