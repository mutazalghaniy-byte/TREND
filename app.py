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
    # Menambahkan sedikit data duplikat dan kosong buatan untuk demonstrasi fitur ceklis
    df_mock = pd.DataFrame(data)
    df_mock.loc[12] = df_mock.loc[11] # Duplikat
    df_mock.loc[13] = [0, "Petani", None, 3, 1, 1] # Data Kosong
    return df_mock

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
    df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce").astype("Int64") # Menggunakan Int64 agar aman jika ada NaN

df_clean = df_clean.dropna() # Drop sisa missing value di numerik jika ada
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

# ==========================================
# 4. TABS MENU UTAMA
# ==========================================
tab_data, tab_viz, tab_insight = st.tabs([
    "🔍 Pratinjau Data", 
    "📊 Visualisasi Interaktif", 
    "💡 Insight & Rekomendasi"
])

# ----------------- TAB 1: PRATINJAU DATA -----------------
with tab_data:
    col_title, col_download = st.columns([4, 1])
    with col_title:
        st.subheader("Data Bersih & Terfilter")
    with col_download:
        csv_clean = df_clean.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Unduh File Data Bersih",
            data=csv_clean,
            file_name="data_bersih_ukt.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    st.dataframe(df_filtered, use_container_width=True)

    st.markdown("---")
    st.subheader("Data Mentah (Original)")
    st.dataframe(df_raw, use_container_width=True)
    
    # Ceklis untuk mengecek data kosong (clon/duplikat dan null)
    cek_kualitas = st.checkbox("Lihat Pengecekan Data Kosong & Klon/Duplikat")
    if cek_kualitas:
        col_cek1, col_cek2 = st.columns(2)
        with col_cek1:
            st.markdown("**Data Kosong (Missing Values) per Kolom:**")
            st.dataframe(df_raw.isna().sum().reset_index().rename(columns={"index": "Kolom", 0: "Jumlah Data Kosong"}), use_container_width=True)
        with col_cek2:
            st.markdown("**Data Klon / Duplikat:**")
            jumlah_duplikat = df_raw.duplicated().sum()
            if jumlah_duplikat > 0:
                st.warning(f"⚠️ Terdapat **{jumlah_duplikat}** baris data yang duplikat pada data mentah.")
            else:
                st.success("✅ Tidak ada data duplikat pada data mentah.")

# ----------------- TAB 2: VISUALISASI INTERAKTIF -----------------
with tab_viz:
    st.info("💡 **Tips:** Anda dapat mengunduh format interaktif via tombol di bawah tiap grafik, atau unduh gambar statis (PNG) dengan mengarahkan kursor ke grafik dan mengklik ikon kamera 📷 di pojok kanan atas.")
    
    if total_mhs > 0:
        
        # --- DIAGRAM 1 ---
        st.markdown("### 1. Distribusi Kelayakan Keringanan UKT")
        fig1 = px.pie(
            df_filtered, 
            names="Status UKT", 
            color="Status UKT",
            color_discrete_map={"Layak": "#00CC96", "Tidak Layak": "#EF553B"}
        )
        fig1.update_traces(textposition='inside', textinfo='percent+label')
        fig1.update_layout(height=500) # Memperbesar ukuran diagram
        st.plotly_chart(fig1, use_container_width=True)
        st.caption("📌 **Penjelasan:** Diagram ini menunjukkan persentase mahasiswa yang layak dan tidak layak menerima keringanan UKT berdasarkan data yang sedang difilter.")
        st.download_button(
            label="📥 Unduh Diagram 1 (Format HTML)",
            data=fig1.to_html(),
            file_name="diagram_distribusi_ukt.html",
            mime="text/html",
            key="dl_fig1"
        )
        st.markdown("---")

        # --- DIAGRAM 2 ---
        st.markdown("### 2. Distribusi Pekerjaan Orang Tua")
        pekerjaan_counts = df_filtered["Pekerjaan Orang Tua"].value_counts().reset_index()
        pekerjaan_counts.columns = ["Pekerjaan", "Jumlah"]
        fig2 = px.bar(
            pekerjaan_counts, 
            y="Pekerjaan", 
            x="Jumlah", 
            orientation='h',
            color="Jumlah",
            color_continuous_scale="Viridis"
        )
        fig2.update_layout(yaxis={'categoryorder':'total ascending'}, height=500)
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("📌 **Penjelasan:** Menampilkan frekuensi latar belakang pekerjaan orang tua. Semakin panjang bar, semakin banyak mahasiswa dengan latar belakang tersebut.")
        st.download_button(
            label="📥 Unduh Diagram 2 (Format HTML)",
            data=fig2.to_html(),
            file_name="diagram_pekerjaan.html",
            mime="text/html",
            key="dl_fig2"
        )
        st.markdown("---")

        # --- DIAGRAM 3 ---
        st.markdown("### 3. Penghasilan Orang Tua vs Kelayakan")
        fig3 = px.box(
            df_filtered, 
            x="Status UKT", 
            y="Penghasilan Orang Tua", 
            color="Status UKT",
            color_discrete_map={"Layak": "#00CC96", "Tidak Layak": "#EF553B"}
        )
        fig3.update_layout(height=500)
        st.plotly_chart(fig3, use_container_width=True)
        st.caption("📌 **Penjelasan:** Boxplot ini melihat sebaran gaji orang tua. Biasanya kategori 'Layak' akan mengelompok pada rentang penghasilan yang lebih rendah.")
        st.download_button(
            label="📥 Unduh Diagram 3 (Format HTML)",
            data=fig3.to_html(),
            file_name="diagram_penghasilan.html",
            mime="text/html",
            key="dl_fig3"
        )
        st.markdown("---")

        # --- DIAGRAM 4 ---
        st.markdown("### 4. Rata-rata Tanggungan vs Kelayakan")
        rata_tanggungan_df = df_filtered.groupby("Status UKT")["Jumlah Tanggungan Orang Tua"].mean().reset_index()
        fig4 = px.bar(
            rata_tanggungan_df, 
            x="Status UKT", 
            y="Jumlah Tanggungan Orang Tua",
            color="Status UKT",
            color_discrete_map={"Layak": "#00CC96", "Tidak Layak": "#EF553B"}
        )
        fig4.update_layout(height=500)
        st.plotly_chart(fig4, use_container_width=True)
        st.caption("📌 **Penjelasan:** Diagram batang ini membandingkan rata-rata jumlah tanggungan keluarga antara mahasiswa yang layak dan tidak layak mendapatkan keringanan.")
        st.download_button(
            label="📥 Unduh Diagram 4 (Format HTML)",
            data=fig4.to_html(),
            file_name="diagram_tanggungan.html",
            mime="text/html",
            key="dl_fig4"
        )

    else:
        st.warning("⚠️ Tidak ada data yang sesuai dengan filter yang dipilih.")

# ----------------- TAB 3: INSIGHT & REKOMENDASI -----------------
with tab_insight:
    st.markdown("""
    ### 💡 Insight Utama:
    1. **Demografi Pekerjaan:** Mahasiswa yang layak menerima keringanan UKT sebagian besar berasal dari keluarga dengan latar belakang pekerjaan non-formal seperti petani dan buruh.
    2. **Batas Penghasilan:** Terdapat batas konsisten di mana mahasiswa dari keluarga dengan penghasilan di bawah rata-rata mendominasi status "Layak".
    3. **Pengaruh Tanggungan:** Jumlah tanggungan yang lebih tinggi memperbesar probabilitas mahasiswa untuk masuk dalam kategori penerima keringanan UKT, meskipun penghasilan berada di kelas menengah.

    ---
    ### 🎯 Rekomendasi Aksi:
    - **Jalur Afirmasi Otomatis:** Universitas disarankan untuk membuat jalur afirmasi otomatis bagi pendaftar yang memiliki kombinasi penghasilan di bawah rata-rata (misal < Rp 4 juta) dengan jumlah tanggungan lebih dari 3 orang.
    - **Verifikasi Lanjutan:** Untuk calon penerima keringanan yang orang tuanya memiliki status pekerjaan formal (seperti PNS atau Wiraswasta), perlu dilakukan pengecekan dokumen tambahan agar bantuan tetap tepat sasaran.
    """)