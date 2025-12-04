# app.py
import streamlit as st
import pandas as pd
import io
import base64
import re
from datetime import datetime
from PIL import Image
import plotly.express as px

# Optional OCR import (only used if available in environment)
try:
    import pytesseract
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False

# -----------------------
# Page config & CSS
# -----------------------
st.set_page_config(page_title="MayFinance • Mobile", page_icon="💸", layout="wide")

st.markdown("""
<style>
.title {
  font-size:28px;
  font-weight:800;
  background: linear-gradient(90deg,#4f46e5,#06b6d4);
  -webkit-background-clip: text;
  color: transparent;
}
.card {
  background: white;
  padding:14px;
  border-radius:12px;
  box-shadow: 0 6px 18px rgba(2,6,23,0.06);
}
.small-muted { color: #6b7280; font-size:13px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>💸 MayFinance — Personal Finance Manager</div>", unsafe_allow_html=True)
st.markdown("<div class='small-muted'>Kelola pemasukan & pengeluaran, simpan bukti pembayaran, dan ekspor laporan.</div>", unsafe_allow_html=True)
st.write("")

# -----------------------
# Session state init
# -----------------------
if "tx" not in st.session_state:
    st.session_state.tx = pd.DataFrame(columns=["id","date","type","category","amount","note","receipt"])

# helper: generate id
def gen_id():
    return int(datetime.utcnow().timestamp() * 1000)

# -----------------------
# Sidebar: controls
# -----------------------
with st.sidebar:
    st.header("Menu")
    page = st.radio("", ["Dashboard", "Tambah Transaksi", "Bukti / Scan", "Laporan & Export", "Pengaturan"])
    st.markdown("---")
    st.markdown("📌 **Tips**: Jika ingin langsung jadi APK, deploy dulu app ke Streamlit Cloud lalu bungkus WebView di Android Studio.")
    st.markdown("---")
    st.markdown(f"OCR tersedia: **{OCR_AVAILABLE}**")
    st.markdown("Made with ❤️ by May")

# -----------------------
# Page: Tambah Transaksi
# -----------------------
if page == "Tambah Transaksi":
    st.subheader("➕ Tambah Transaksi Baru")
    with st.form("form_add"):
        col1, col2 = st.columns([2,1])
        with col1:
            date = st.date_input("Tanggal", value=datetime.today())
            typ = st.selectbox("Jenis", ["Pemasukan","Pengeluaran"])
            category = st.text_input("Kategori (mis. Gaji, Makan, Transport)")
            amount = st.number_input("Jumlah (Rp)", min_value=0.0, step=1000.0, format="%f")
            note = st.text_input("Keterangan (opsional)")
        with col2:
            uploaded = st.file_uploader("Lampirkan bukti (foto/scan) — opsional", type=["png","jpg","jpeg","pdf"])
            st.caption("Gunakan foto struk/bukti; apabila ingin ekstraksi otomatis, pakai gambar teks yang jelas.")
        submitted = st.form_submit_button("Simpan Transaksi")

    if submitted:
        rid = gen_id()
        # convert amount to float rounded
        amt = float(round(amount,2))
        # store image as base64 if uploaded
        receipt_b64 = None
        if uploaded is not None:
            raw = uploaded.read()
            receipt_b64 = base64.b64encode(raw).decode("utf-8")
        new = {
            "id": rid,
            "date": pd.to_datetime(date).date(),
            "type": typ,
            "category": category or "Lainnya",
            "amount": amt,
            "note": note,
            "receipt": receipt_b64
        }
        st.session_state.tx = pd.concat([st.session_state.tx, pd.DataFrame([new])], ignore_index=True)
        st.success("Transaksi tersimpan ✅")

# -----------------------
# Page: Bukti / Scan
# -----------------------
elif page == "Bukti / Scan":
    st.subheader("📷 Upload / Scan Bukti Pembayaran")
    st.info("Fitur ekstraksi teks dari gambar (OCR) bersifat opsional — bergantung pada environment (pytesseract). Jika tidak tersedia, hasil hanya menampilkan gambar.")
    file = st.file_uploader("Unggah foto struk / receipt (jpg/png) untuk mencoba ekstraksi", type=["png","jpg","jpeg"])
    if file is not None:
        img = Image.open(file).convert("RGB")
        st.image(img, caption="Preview bukti", use_column_width=True)
        if OCR_AVAILABLE:
            try:
                text = pytesseract.image_to_string(img, lang='eng+ind')
            except Exception as e:
                text = f"[OCR error: {e}]"
            st.subheader("Hasil Ekstraksi (OCR)")
            st.text_area("Teks hasil OCR", value=text, height=200)
            # try to detect amounts (numbers)
            amounts = re.findall(r"(?:(?:Rp\.?\s?)|)(\d{1,3}(?:[\.,]\d{3})*(?:[\.,]\d{2})?)", text.replace(" ",""))
            # amounts fallback: find numbers with decimals or grouping
            if amounts:
                st.markdown("**Kemungkinan angka yang ditemukan:**")
                st.write(amounts)
                # let user pick probable amount to auto-add transaction
                pick = st.selectbox("Pilih angka sebagai jumlah (jika sesuai)", options=["-"]+amounts)
                if pick and pick != "-":
                    # normalize number string to float
                    cleaned = re.sub(r"[^\d]", "", pick)
                    try:
                        val = float(cleaned)/100 if len(cleaned)>2 else float(cleaned)
                    except:
                        val = float(cleaned)
                    if st.button("Tambahkan sebagai Pengeluaran"):
                        rid = gen_id()
                        new = {
                            "id": rid,
                            "date": datetime.today().date(),
                            "type": "Pengeluaran",
                            "category": "Tidak diketahui",
                            "amount": val,
                            "note": "Tambah via OCR",
                            "receipt": base64.b64encode(file.read()).decode("utf-8")
                        }
                        st.session_state.tx = pd.concat([st.session_state.tx, pd.DataFrame([new])], ignore_index=True)
                        st.success("Transaksi dari OCR disimpan ✅")
        else:
            st.warning("OCR (pytesseract) tidak terpasang di environment ini. Kamu masih bisa menyimpan gambar sebagai bukti saat menambah transaksi manual.")

# -----------------------
# Page: Dashboard
# -----------------------
elif page == "Dashboard":
    st.subheader("📊 Dashboard Ringkas")
    df = st.session_state.tx.copy()
    if df.empty:
        st.info("Belum ada data. Tambahkan transaksi terlebih dahulu.")
    else:
        # convert date column to datetime if not
        df['date'] = pd.to_datetime(df['date'])
        # filters
        c1, c2, c3 = st.columns([3,2,2])
        with c1:
            sel_cat = st.multiselect("Filter Kategori", options=sorted(df['category'].unique()), default=sorted(df['category'].unique()))
        with c2:
            sel_type = st.multiselect("Jenis", options=["Pemasukan","Pengeluaran"], default=["Pemasukan","Pengeluaran"])
        with c3:
            month = st.selectbox("Bulan", options=["Semua"] + sorted(df['date'].dt.strftime("%Y-%m").unique().tolist(), reverse=True))
        # apply filters
        df_filtered = df[df['category'].isin(sel_cat) & df['type'].isin(sel_type)]
        if month != "Semua":
            df_filtered = df_filtered[df_filtered['date'].dt.strftime("%Y-%m")==month]
        # metrics
        income = df_filtered[df_filtered['type']=="Pemasukan"]['amount'].sum()
        expense = df_filtered[df_filtered['type']=="Pengeluaran"]['amount'].sum()
        balance = income - expense
        m1,m2,m3 = st.columns(3)
        m1.metric("Total Pemasukan", f"Rp {income:,.0f}")
        m2.metric("Total Pengeluaran", f"Rp {expense:,.0f}")
        m3.metric("Saldo", f"Rp {balance:,.0f}")
        # chart
        st.markdown("### Tren Harian")
        chart = df_filtered.groupby(['date','type'])['amount'].sum().reset_index()
        if not chart.empty:
            fig = px.bar(chart, x='date', y='amount', color='type', barmode='group', labels={'amount':'Jumlah (Rp)','date':'Tanggal'})
            st.plotly_chart(fig, use_container_width=True)
        # table
        st.markdown("### Daftar Transaksi")
        st.dataframe(df_filtered.sort_values(by='date', ascending=False).reset_index(drop=True), use_container_width=True)
        # allow deletion per id
        st.markdown("### Hapus transaksi (pilih ID)")
        ids = df_filtered['id'].astype(int).astype(str).tolist()
        if ids:
            pick = st.selectbox("Pilih ID untuk hapus", options=["-"]+ids)
            if pick and pick != "-":
                if st.button("Hapus"):
                    st.session_state.tx = st.session_state.tx[st.session_state.tx['id'].astype(str) != pick].reset_index(drop=True)
                    st.success("Transaksi dihapus ✅")

# -----------------------
# Page: Laporan & Export
# -----------------------
elif page == "Laporan & Export":
    st.subheader("📦 Export Data & Laporan")
    df = st.session_state.tx.copy()
    if df.empty:
        st.info("Belum ada data untuk diekspor.")
    else:
        # CSV download
        def to_csv_bytes(df_):
            return df_.to_csv(index=False).encode('utf-8')
        csv_bytes = to_csv_bytes(df)
        b64 = base64.b64encode(csv_bytes).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="mayfinance_transactions.csv">⬇️ Download CSV</a>'
        st.markdown(href, unsafe_allow_html=True)

        # simple summary report
        st.markdown("### Ringkasan")
        df['date'] = pd.to_datetime(df['date'])
        summary = df.groupby('type')['amount'].sum().rename('total').reset_index()
        st.table(summary)

        # Export individual receipts as ZIP (if any)
        if df['receipt'].notna().sum() > 0:
            st.markdown("📎 Bukti tersedia pada beberapa transaksi (disimpan ter-encode). Untuk men-download individual, buka row di table (export CSV lalu decode di lokal).")

# -----------------------
# Page: Pengaturan
# -----------------------
elif page == "Pengaturan":
    st.subheader("⚙️ Pengaturan")
    st.markdown("Reset data, preferensi, dan info aplikasi.")
    if st.button("Reset semua data transaksi (hapus permanen)"):
        st.session_state.tx = pd.DataFrame(columns=["id","date","type","category","amount","note","receipt"])
        st.success("Data dihapus.")

# -----------------------
# Footer
# -----------------------
st.markdown("<br><small class='small-muted'>Note: OCR fitur (pytesseract) mungkin tidak tersedia di hosting Streamlit Cloud — gunakan upload manual atau jalankan lokal jika butuh OCR.</small>", unsafe_allow_html=True)
