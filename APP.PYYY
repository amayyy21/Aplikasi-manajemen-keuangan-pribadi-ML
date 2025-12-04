import streamlit as st
import pandas as pd
import datetime
import base64
from PIL import Image
import pytesseract

st.set_page_config(page_title="May & Lili Money Tracker", page_icon="💜", layout="wide")

# --- DATA TEMP ---
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Tanggal", "Jenis", "Kategori", "Nominal", "Keterangan"])

st.markdown("""
    <h1 style='text-align:center;color:#7b2cbf;'>💜 May & Lili Money Tracker 💜</h1>
    <p style='text-align:center;color:#5a189a;font-size:18px;margin-top:-10px;'>
        Aplikasi modern untuk mencatat pemasukan, pengeluaran, dan tabungan harian.
    </p>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "💸 Tambah Transaksi", "🏦 Tabungan", "📜 History"])

# === 1. DASHBOARD ===
with tab1:
    st.subheader("📊 Ringkasan Keuangan")
    total_in = st.session_state.data[st.session_state.data["Jenis"] == "Pemasukan"]["Nominal"].sum()
    total_out = st.session_state.data[st.session_state.data["Jenis"] == "Pengeluaran"]["Nominal"].sum()
    saldo = total_in - total_out
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Pemasukan", f"Rp {total_in:,.0f}")
    c2.metric("Total Pengeluaran", f"Rp {total_out:,.0f}")
    c3.metric("Saldo Akhir", f"Rp {saldo:,.0f}")

    st.bar_chart(st.session_state.data[["Nominal"]])

# === 2. TAMBAH TRANSAKSI ===
with tab2:
    st.subheader("💸 Tambah Transaksi")

    jenis = st.selectbox("Jenis Transaksi", ["Pemasukan", "Pengeluaran"])
    kategori = st.selectbox("Kategori", ["Makanan", "Transport", "Belanja", "Hiburan", "Gaji", "Lainnya"])
    nominal = st.number_input("Nominal (Rp)", min_value=0)
    keterangan = st.text_input("Keterangan")
    tanggal = st.date_input("Tanggal", datetime.date.today())

    # --- SCAN STRUK (OCR) ---
    uploaded = st.file_uploader("Scan dari Foto/Struk (Optional)", type=["jpg","png"])

    if uploaded:
        img = Image.open(uploaded)
        text = pytesseract.image_to_string(img)
        st.write("Hasil Scan:")
        st.code(text)

    if st.button("Simpan Transaksi"):
        st.session_state.data.loc[len(st.session_state.data)] = [tanggal, jenis, kategori, nominal, keterangan]
        st.success("Transaksi berhasil ditambahkan! 💜")

# === 3. TABUNGAN ===
with tab3:
    st.subheader("🏦 Tabungan May & Lili")

    target = st.number_input("Target Tabungan (Rp)", min_value=0)
    total_tabungan = st.session_state.data[st.session_state.data["Jenis"] == "Pemasukan"]["Nominal"].sum()

    progress = 0 if target == 0 else total_tabungan / target
    st.progress(progress)

    st.write(f"Total tabungan: **Rp {total_tabungan:,.0f}**")
    st.write(f"Progress: **{progress*100:.2f}%**")

# === 4. HISTORY ===
with tab4:
    st.subheader("📜 Riwayat Transaksi")
    st.dataframe(st.session_state.data)

    csv = st.session_state.data.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "history.csv", "text/csv")
