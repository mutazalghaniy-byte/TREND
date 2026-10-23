import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

# Konfigurasi Halaman Streamlit (Harus menjadi perintah st pertama)
st.set_page_config(
    page_title="Dashboard Analisis UKT Mahasiswa", page_icon="📊", layout="wide"
)

# Judul Utama Dashboard
st.title("📊 Dashboard Analisis Kelayakan Keringanan UKT Mahasiswa")
st.markdown(
    "Aplikasi web interaktif untuk menganalisis data sosial-ekonomi dan"
    " kelayakan keringanan UKT mahasiswa."
)


@st.cache_data
def generate_mock_data():
  """Membuat data tiruan untuk simulasi jika file csv asli tidak tersedia."""
  data = {
      "Tempat Tinggal": [0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1],
      "Pekerjaan Orang Tua": [
          "PNS",
          "TNI/POLRI",
          "Petani",
          "Nelayan",
          "Buruh",
          "Wiraswasta",
          "Guru",
          "Ibu Rumah Tangga",
          "Petani",
          "Buruh",
          "PNS",
          "Wiraswasta",
      ],
      "Penghasilan Orang Tua": [
          10000000,
          8000000,
          4000000,
          3000000,
          2000000,
          6000000,
          7000000,
          3000000,
          1500000,
          2500000,
          9000000,
          5000000,
      ],
      "Jumlah Tanggungan Orang Tua": [3, 2, 4, 5, 2, 1, 2, 4, 3, 2, 3, 2],
      "Kendaraan": [1, 2, 0, 1, 1, 1, 1, 1, 0, 1, 2, 1],
      "Kelayakan Keringanan UKT": [0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1],
  }
  return pd.DataFrame(data)


# 1. BACA & BERSIHKAN DATASET
file_path = "klasifikasimhs.csv"

if os.path.exists(file_path):
  df = pd.read_csv(file_path)
  st.sidebar.success("✅ Dataset berhasil dibaca dari file lokal.")
else:
  st.sidebar.warning(
      "⚠️ File 'klasifikasimhs.csv' tidak ditemukan. Menggunakan dataset buatan"
      " (mock data) untuk demo."
  )
  df = generate_mock_data()

# Cleaning data sesuai notebook
df_clean = df.copy()
df_clean.columns = df_clean.columns.str.strip().str.replace(r"\s+", " ", regex=True)

kolom_target = "Kelayakan Keringanan UKT"

# Merapikan data teks & target
if df_clean[kolom_target].dtype == "object":
  df_clean[kolom_target] = (
      df_clean[kolom_target].astype(str).str.strip().replace({"1 1": "1"})
  )

df_clean[kolom_target] = pd.to_numeric(df_clean[kolom_target], errors="coerce")
df_clean = df_clean.dropna(subset=[kolom_target])
df_clean = df_clean.drop_duplicates().reset_index(drop=True)

# Format tipe data
kolom_numerik = [
    "Tempat Tinggal",
    "Penghasilan Orang Tua",
    "Jumlah Tanggungan Orang Tua",
    "Kendaraan",
]
for col in kolom_numerik:
  df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce").astype("int64")
df_clean[kolom_target] = df_clean[kolom_target].astype("int64")

# Tampilkan preview data dalam bentuk tabel interaktif
with st.expander("🔍 Lihat Preview Data"):
  st.dataframe(df_clean)

# 2. MEMBUAT DASHBOARD VISUALISASI DATA
sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle(
    "Dashboard Analisis Kelayakan Keringanan UKT Mahasiswa",
    fontsize=18,
    fontweight="bold",
)

# Grafik 1: Distribusi Kelayakan UKT
sns.countplot(
    data=df_clean,
    x=kolom_target,
    ax=axes[0, 0],
    hue=kolom_target,
    palette="Set2",
    legend=False,
)
axes[0, 0].set_title(
    "Distribusi Kelayakan Keringanan UKT", fontsize=14, fontweight="bold"
)
axes[0, 0].set_xlabel("Kelayakan UKT (0 = Tidak Layak, 1 = Layak)", fontsize=12)
axes[0, 0].set_ylabel("Jumlah Mahasiswa", fontsize=12)

# Grafik 2: Distribusi Pekerjaan Orang Tua
order_pekerjaan = df_clean["Pekerjaan Orang Tua"].value_counts().index
sns.countplot(
    data=df_clean,
    y="Pekerjaan Orang Tua",
    order=order_pekerjaan,
    ax=axes[0, 1],
    hue="Pekerjaan Orang Tua",
    palette="viridis",
    legend=False,
)
axes[0, 1].set_title(
    "Distribusi Pekerjaan Orang Tua", fontsize=14, fontweight="bold"
)
axes[0, 1].set_xlabel("Jumlah Mahasiswa", fontsize=12)
axes[0, 1].set_ylabel("Pekerjaan Orang Tua", fontsize=12)

# Grafik 3: Boxplot Penghasilan Orang Tua vs Kelayakan UKT
sns.boxplot(
    data=df_clean,
    x=kolom_target,
    y="Penghasilan Orang Tua",
    ax=axes[1, 0],
    hue=kolom_target,
    palette="Set2",
    legend=False,
)
axes[1, 0].set_title(
    "Penghasilan Orang Tua vs Kelayakan UKT", fontsize=14, fontweight="bold"
)
axes[1, 0].set_xlabel("Kelayakan UKT (0 = Tidak Layak, 1 = Layak)", fontsize=12)
axes[1, 0].set_ylabel("Penghasilan Orang Tua (Rp)", fontsize=12)
axes[1, 0].ticklabel_format(axis="y", style="plain")

# Grafik 4: Jumlah Tanggungan vs Kelayakan UKT
sns.barplot(
    data=df_clean,
    x=kolom_target,
    y="Jumlah Tanggungan Orang Tua",
    ax=axes[1, 1],
    hue=kolom_target,
    palette="Set2",
    errorbar=None,
    legend=False,
)
axes[1, 1].set_title(
    "Rata-rata Jumlah Tanggungan vs Kelayakan UKT", fontsize=14, fontweight="bold"
)
axes[1, 1].set_xlabel("Kelayakan UKT (0 = Tidak Layak, 1 = Layak)", fontsize=12)
axes[1, 1].set_ylabel("Rata-rata Jumlah Tanggungan", fontsize=12)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])

# Tampilkan plot ke Streamlit (menggantikan plt.show())
st.pyplot(fig)