import os
import pandas as pd
import streamlit as st
import plotly.express as px

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Dashboard Analisis UKT Mahasiswa", 
    page_icon="📊", 
    layout="wide"
)

# Judul Utama & Sumber Data
st.title("📊 Dashboard Analisis Kelayakan Keringanan UKT Mahasiswa")
st.markdown("**Sumber Dataset:** `klasifikasimhs.csv` (Data Internal Kemahasiswaan / Simulasi Mock Data)")
st.markdown(
    "Dashboard interaktif ini menyajikan KPI, visualisasi distribusi demografi, "
    "serta filter dinamis untuk menganalisis data sosial-ekonomi dan kelayakan keringanan UKT."
)

@st.cache_data
def generate_mock_data():
    data = {
        "Tempat Tinggal": [0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        "Pekerjaan Orang Tua": [
            "PNS", "TNI/POLRI", "Petani", "Nelayan", "Buruh", "Wiraswasta",
            "Guru", "Ibu Rumah Tangga", "Petani", "Buruh", "PNS", "Wiraswasta"
        ],
        "Penghasilan Orang Tua": [
            10000000, 8000000, 4000000, 3000000, 2000000, 6000000,
            7000000, 3000000, 1500000, 2500000, 9000000, 5000000
        ],
        "Jumlah Tanggungan Orang Tua": [3, 2, 4, 5, 2, 1, 2, 4, 3, 2, 3, 2],
        "Kendaraan": [1, 2, 0, 1, 1, 1, 1, 1, 0, 1, 2, 1],
        "Kelayakan Keringanan UKT": [0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1],
    }
    return pd.DataFrame(data)

# 1. BACA & BERSIHKAN DATASET
file_path = "klasifikasimhs.csv"

if os.path.exists(file_path):
    df_raw = pd.read_csv(file_path)
else:
    df_raw = generate_mock_data()

# Cleaning data 
df_clean = df_raw.copy()
df_clean.columns = df_clean.columns.str.strip().str.replace(r"\s+", " ", regex=True)

kolom_target = "Kelayakan Keringanan UKT"

if df_clean[kolom_target].dtype == "object":
    df_clean[kolom_target] = df_clean[kolom_target].astype(str).str.strip().replace({"1 1": "1"})

df_clean[kolom_target] = pd.to_numeric(df_clean[kolom_target], errors="coerce")
df_clean = df_clean.dropna(subset=[kolom_target])
df_clean = df_clean.drop_duplicates().reset_index(drop=True)

kolom_numerik = [
    "Tempat Tinggal", "Penghasilan Orang Tua", 
    "Jumlah Tanggungan Orang Tua", "Kendaraan",
]
for col in kolom_numerik:
    df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce").astype("int64")
df_clean[kolom_target] = df_clean[kolom_target].astype("int64")
df_clean["Status UKT"] = df_clean[kolom_target].map({0: "Tidak Layak", 1: "Layak"})

# 2. FILTER SIDEBAR
st.sidebar.header("🎛️ Filter Data")
pekerjaan_filter = st.sidebar.multiselect(
    "Pilih Pekerjaan Orang Tua:",
    options=df_clean["Pekerjaan Orang Tua"].unique(),
    default=df_clean["Pekerjaan Orang Tua"].unique()
)

status_filter = st.sidebar.multiselect(
    "Pilih Status UKT:",
    options=df_clean["Status UKT"].unique(),
    default=df_clean["Status UKT"].unique()
)

# Terapkan Filter
df_filtered = df_clean[
    (df_clean["Pekerjaan Orang Tua"].isin(pekerjaan_filter)) &
    (df_clean["Status UKT"].isin(status_filter))
]

# 3. INDIKATOR KINERJA UTAMA (KPI)
st.subheader("📈 Key Performance Indicators (KPI)")
total_mhs = len(df_filtered)
total_layak = df_filtered[df_filtered["Status UKT"] == "Layak"].shape[0]
persentase_layak = (total_layak / total_mhs) * 100 if total_mhs > 0 else 0
rata_penghasilan = df_filtered["Penghasilan Orang Tua"].mean() if total_mhs > 0 else 0
rata_tanggungan = df_filtered["Jumlah Tanggungan Orang Tua"].mean() if total_mhs > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Mahasiswa (Terfilter)", total_mhs)
col2.metric("Layak Keringanan UKT", f"{total_layak} ({persentase_layak:.1f}%)")
col3.metric("Rata-rata Penghasilan", f"Rp {rata_penghasilan:,.0f}")
col4.metric("Rata-rata Tanggungan", f"{rata_tanggungan:.1f} Orang")

st.markdown("---")

# 4. TAB TABEL DATA
st.subheader("🔍 Pratinjau Data")
tab1, tab2 = st.tabs(["Data Bersih & Terfilter", "Data Mentah (Original)"])

with tab1:
    st.dataframe(df_filtered, use_container_width=True)
with tab2:
    st.dataframe(df_raw, use_container_width=True)

st.markdown("---")

# 5. VISUALISASI INTERAKTIF DENGAN PLOTLY
st.subheader("📊 Visualisasi Interaktif")

if total_mhs > 0:
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        fig1 = px.pie(
            df_filtered, 
            names="Status UKT", 
            title="Distribusi Kelayakan Keringanan UKT",
            color="Status UKT",
            color_discrete_map={"Layak": "#00CC96", "Tidak Layak": "#EF553B"}
        )
        fig1.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig1, use_container_width=True)

    with col_chart2:
        pekerjaan_counts = df_filtered["Pekerjaan Orang Tua"].value_counts().reset_index()
        pekerjaan_counts.columns = ["Pekerjaan", "Jumlah"]
        fig2 = px.bar(
            pekerjaan_counts, 
            y="Pekerjaan", 
            x="Jumlah", 
            orientation='h',
            title="Distribusi Pekerjaan Orang Tua",
            color="Jumlah",
            color_continuous_scale="Viridis"
        )
        fig2.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig2, use_container_width=True)

    col_chart3, col_chart4 = st.columns(2)

    with col_chart3:
        fig3 = px.box(
            df_filtered, 
            x="Status UKT", 
            y="Penghasilan Orang Tua", 
            color="Status UKT",
            title="Penghasilan Orang Tua vs Kelayakan",
            color_discrete_map={"Layak": "#00CC96", "Tidak Layak": "#EF553B"}
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col_chart4:
        rata_tanggungan_df = df_filtered.groupby("Status UKT")["Jumlah Tanggungan Orang Tua"].mean().reset_index()
        fig4 = px.bar(
            rata_tanggungan_df, 
            x="Status UKT", 
            y="Jumlah Tanggungan Orang Tua",
            color="Status UKT",
            title="Rata-rata Tanggungan vs Kelayakan",
            color_discrete_map={"Layak": "#00CC96", "Tidak Layak": "#EF553B"}
        )
        st.plotly_chart(fig4, use_container_width=True)
else:
    st.warning("⚠️ Tidak ada data yang sesuai dengan filter yang dipilih.")

st.markdown("---")

# 6. INSIGHT & REKOMENDASI
st.subheader("💡 Insight & Rekomendasi")
st.markdown("""
**3 Insight Utama:**
1. Mahasiswa yang layak menerima keringanan UKT sebagian besar berasal dari keluarga dengan latar belakang pekerjaan non-formal seperti petani dan buruh.
2. Terdapat batas konsisten di mana mahasiswa dari keluarga dengan penghasilan di bawah rata-rata mendominasi status "Layak".
3. Jumlah tanggungan yang lebih tinggi memperbesar probabilitas mahasiswa untuk masuk dalam kategori penerima keringanan UKT.

**Rekomendasi:**
Universitas disarankan untuk membuat jalur afirmasi otomatis bagi pendaftar yang memiliki kombinasi penghasilan di bawah rata-rata (misal < Rp 4 juta) dengan jumlah tanggungan lebih dari 3 orang, guna mempercepat proses penyaluran keringanan UKT tepat sasaran.
""")