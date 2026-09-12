import streamlit as st
from google import genai
import pypdf

# Config Halaman
st.set_page_config(page_title="AI Diskusi Mahasiswa", layout="wide")
st.title("🤖 AI Diskusi & Parafrase Mahasiswa")
st.caption("Menghasilkan argumen berbobot, mencari jurnal kredibel, dan memparafrase gaya tulisan manusia.")

# Inisialisasi API Key secara otomatis dari Secrets
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = st.sidebar.text_input("Gemini API Key (Lokal)", type="password")

if api_key:
    client = genai.Client(api_key=api_key)

# --- FORM INPUT ---
st.subheader("📋 Data Mahasiswa")
col1, col2 = st.columns(2)
with col1:
    nama = st.text_input("Nama Lengkap", value="Ashad Bayu Saputra")
    upbjj = st.text_input("UPBJJ", value="Palangkaraya")
with col2:
    prodi = st.selectbox(
        "Program Studi", 
        ["Sistem Informasi", "Manajemen", "Ilmu Komunikasi", "Akuntansi", "Lainnya"]
    )
    tutor = st.text_input("Nama Tutor/Dosen")

st.subheader("1️⃣ Topik / Bahan Diskusi")
soal = st.text_area("Masukkan pertanyaan tugas atau topik diskusi di sini...", height=150)

st.subheader("2️⃣ Upload Modul (PDF)")
pdf_file = st.file_uploader("Upload modul versi PDF", type=["pdf"])

pdf_text = ""
if pdf_file:
    reader = pypdf.PdfReader(pdf_file)
    for page in reader.pages:
        pdf_text += page.extract_text() or ""
    st.success(f"Berhasil membaca file: {pdf_file.name}")

# --- PROSES GENERATE JAWABAN ---
if st.button("🚀 Buat Jawaban Diskusi", type="primary"):
    if not api_key:
        st.error("API Key belum terkonfigurasi!")
    elif not soal:
        st.warning("Mohon masukkan topik/bahan diskusi.")
    else:
        with st.spinner("Mengekstrak teks & menganalisis jawaban..."):
            prompt = f"""
            Kamu adalah mahasiswa aktif UT (Universitas Terbuka) yang cerdas dan akademis. 
            Buatkan jawaban diskusi tutorial online berdasarkan informasi berikut:

            DATA MAHASISWA:
            - Nama: {nama}
            - Program Studi: {prodi}
            - UPBJJ: {upbjj}
            - Dosen/Tutor: {tutor}

            TOPIK / SOAL DISKUSI:
            {soal}

            REFERENSI MODUL UT:
            {pdf_text[:12000]}

            INSTRUKSI JAWABAN (WAJIB MENGGUNAKAN SITASI & REFERENSI):
            1. Awali dengan sapaan sopan kepada tutor dan perkenalan singkat.
            2. TESIS UTAMA: Jawab inti pertanyaan secara langsung.
            3. ANALISIS & PEMBAHASAN: Jelaskan secara terstruktur menggunakan bahasa akademis. 
               - Wajib menyertakan sitasi dalam paragraf (contoh: Menurut Modul UT / Penulis, ...).
               - Kaitkan dengan materi dari Modul UT yang diupload (jika ada).
            4. STUDI KASUS / CONTOH REALISTIS: Berikan contoh konkret di dunia nyata.
            5. KESIMPULAN: Ringkasan singkat 1-2 kalimat.
            6. DAFTAR PUSTAKA: 
               - Wajib cantumkan Buku Materi Pokok (BMP) / Modul UT terkait (Edisi, Penulis/Penerbit UT).
               - Wajib cantumkan minimal 1-2 Referensi Jurnal Ilmiah / Buku Pendukung yang relevan beserta tahun dan judulnya.
            """

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )

            st.session_state["jawaban"] = response.text

# --- TAMPILAN HASIL & FITUR PARAFRASE ---
if "jawaban" in st.session_state:
    st.markdown("---")
    st.subheader("Hasil Jawaban")
    
    with st.container(border=True):
        st.markdown(st.session_state["jawaban"])

    if st.button("🔄 Parafrase Sekarang (Humanise)"):
        with st.spinner("Memparafrase tulisan agar lebih natural..."):
            para_prompt = f"Ubah gaya bahasa dari teks berikut agar terasa sangat alami, manusiawi, dan lolos uji AI checker tanpa mengubah esensi isinya:\n\n{st.session_state['jawaban']}"
            
            para_response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=para_prompt
            )
            st.session_state["jawaban"] = para_response.text
            st.rerun()
