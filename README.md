# MayFinance - Streamlit Personal Finance App

## Fitur
- Tambah / hapus transaksi
- Upload bukti (receipt)
- (Opsional) Ekstraksi teks dari gambar via pytesseract (jika tersedia)
- Dashboard, grafik, filter, export CSV
- Bisa dibungkus menjadi APK via WebView Android

## Cara jalankan lokal
1. Clone repo
2. Buat virtualenv (opsional)
   - `python -m venv venv`
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
3. Install dependency:
   - `pip install -r requirements.txt`
   - Jika ingin OCR lokal: install Tesseract binary (OS-specific)
4. Jalankan:
   - `streamlit run app.py`

## Deploy ke Streamlit Cloud
- Push repo ke GitHub
- Buka https://share.streamlit.io → New app → pilih repo, branch main, file app.py
