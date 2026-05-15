# PhishRisk Intelligence System

**PhishRisk Intelligence System** adalah project Data Science dan Machine Learning untuk membantu memeriksa indikasi phishing dari **alamat URL** dan **file** secara defensif. Sistem ini tidak hanya memberi hasil `Terlihat Aman`, `Perlu Tinjauan`, atau `Berisiko`, tetapi juga menampilkan **skor risiko, alasan pemeriksaan, rekomendasi tindakan, dan sinyal intelligence** agar hasilnya mudah dipahami oleh pengguna umum.

Project ini dibuat sebagai sistem pembelajaran dan implementasi Data Science yang berfokus pada deteksi phishing, bukan sebagai alat untuk menyerang, membuat phishing, atau menjalankan file mencurigakan.

---

## Preview Singkat

PhishRisk dapat digunakan untuk:

- Memeriksa satu URL secara manual.
- Memeriksa banyak URL dari teks bebas.
- Memeriksa banyak URL dari file CSV.
- Memeriksa file dari berbagai ekstensi secara statis.
- Membaca URL yang tertanam di dalam file.
- Memberikan rekomendasi tindakan berdasarkan tingkat risiko.
- Menyimpan hasil pemeriksaan dalam bentuk CSV.
- Menjelaskan alasan kenapa alamat resmi bisa saja masuk kategori perlu tinjauan.

---

## Tujuan Project

Tujuan utama project ini adalah membangun sistem pendeteksi phishing yang:

1. **Mudah digunakan**  
   User dapat memasukkan URL atau file tanpa harus memahami kode program.

2. **Mudah dipahami**  
   Hasil tidak hanya berupa angka, tetapi juga alasan dan saran tindakan.

3. **Lebih aman**  
   File diperiksa secara statis tanpa dijalankan.

4. **Lebih realistis**  
   Sistem membedakan antara website resmi, domain tiruan, domain mirip brand, kata mencurigakan, dan file berisiko.

5. **Layak untuk portfolio Data Science**  
   Memiliki alur data, model, evaluasi, engine, CLI, dan dashboard Streamlit.

---

## Masalah yang Diselesaikan

Phishing sering menggunakan alamat web yang terlihat mirip dengan website resmi. Contohnya:

- Domain mirip brand resmi.
- Huruf diganti angka, misalnya `micros0ft`.
- Domain palsu memakai kata `login`, `verify`, `update`, `secure`, atau `account`.
- Link dikirim dalam file PDF, Word, ZIP, TXT, HTML, atau APK.
- Website resmi tertentu bisa terbaca berisiko karena bentuk URL-nya panjang atau memiliki banyak subdomain.

Karena itu, sistem ini dibuat bukan hanya untuk memprediksi URL, tetapi juga memberi konteks agar user tidak salah membaca hasil.

---

## Dataset

Dataset utama yang digunakan:

**PhiUSIIL Phishing URL Dataset**

- Sumber utama: [UCI Machine Learning Repository - PhiUSIIL Phishing URL Dataset](https://archive.ics.uci.edu/dataset/967/phiusiil%2Bphishing%2Burl%2Bdataset)
- Alternatif: [Kaggle - PhiUSIIL Phishing URL Dataset](https://www.kaggle.com/datasets/ndarvind/phiusiil-phishing-url-dataset)
- Jumlah data: 235.795 URL
- Legitimate: 134.850 URL
- Phishing: 100.945 URL
- Jenis data: tabular
- Target:
  - `0` = Phishing pada dataset asli
  - `1` = Legitimate pada dataset asli

Pada project ini target kemudian disesuaikan menjadi:

```text
target_phishing = 1 berarti Phishing
target_phishing = 0 berarti Legitimate
```

---

## Fitur Utama

### 1. Pemeriksaan URL

Sistem dapat memeriksa URL dan menghasilkan:

- Domain
- TLD
- Skor model
- Skor final
- Kategori risiko
- Hasil akhir
- Status intelligence
- Brand terdeteksi
- Domain mirip brand
- Kata mencurigakan
- Alasan pemeriksaan
- Rekomendasi tindakan

Kategori hasil:

| Hasil Akhir | Makna |
|---|---|
| Terlihat Aman | Tidak ditemukan sinyal risiko kuat |
| Perlu Tinjauan | Perlu dicek manual sebelum digunakan |
| Berisiko | Sebaiknya tidak dibuka atau digunakan |

---

### 2. Pemeriksaan Banyak URL

User dapat memeriksa banyak URL sekaligus melalui:

- Paste teks bebas
- CSV dengan kolom URL
- Contoh daftar URL yang sudah disediakan

Output dapat diunduh sebagai CSV.

---

### 3. URL Intelligence

Komponen URL Intelligence membantu sistem membaca pola yang tidak cukup hanya dipahami oleh model awal.

Fitur intelligence yang digunakan:

- `is_official_domain`
- `brand_keyword_detected`
- `brand_but_not_official`
- `suspicious_keyword_count`
- `suspicious_keyword_score`
- `lookalike_brand_detected`
- `lookalike_score`
- `uses_punycode`
- `uses_digit_substitution`
- `hyphen_count`

Contoh status intelligence:

| Status | Penjelasan |
|---|---|
| `resmi_terlihat_aman` | Domain cocok dengan daftar resmi |
| `tiruan_brand_berisiko` | Mengandung nama brand tetapi bukan domain resmi |
| `domain_mirip_brand` | Domain terlihat mirip brand resmi |
| `domain_mirip_brand_berisiko` | Domain mirip brand dan memiliki sinyal tambahan |
| `kata_mencurigakan_tinggi` | URL mengandung kata yang sering dipakai dalam phishing |

---

### 4. File Static Analyzer

Sistem juga dapat memeriksa file secara statis.

File yang dapat diunggah:

- TXT
- HTML
- PDF
- DOCX
- XLSX
- PPTX
- ZIP
- APK
- EXE
- LNK
- BAT
- CMD
- PS1
- VBS
- CSV
- JSON
- XML
- File lain yang ingin diuji

Pemeriksaan file meliputi:

- Ekstensi file
- Ukuran file
- Hash file
- URL yang ditemukan di dalam file
- Kata mencurigakan
- Indikasi file berisiko
- Indikasi macro
- Indikasi JavaScript pada PDF
- File berbahaya di dalam arsip
- Permission berisiko pada APK
- Skor risiko file
- Rekomendasi tindakan

Catatan penting:

> Sistem tidak menjalankan file. Pemeriksaan dilakukan secara statis agar lebih aman.

---

### 5. PhishRisk Engine V3

Engine V3 adalah gabungan dari:

- Model Random Forest Intelligence V2
- URL manual feature extractor
- URL Intelligence
- Official Domain Checker
- Brand Impersonation Detector
- Lookalike Domain Detector
- Suspicious Keyword Detector
- File Static Analyzer
- Safety Calibration Engine

Engine ini digunakan oleh:

- Streamlit dashboard
- CLI utility
- Pemeriksaan URL
- Pemeriksaan file
- Pemeriksaan URL di dalam file

---

### 6. Streamlit Dashboard

Dashboard Streamlit dibuat agar sistem dapat digunakan tanpa membuka notebook.

Halaman utama yang tersedia:

- Beranda
- Input Alamat Link
- Input File
- Rekomendasi dan Antisipasi
- Ciri-Ciri
- Beta dan Salah Deteksi
- Panduan
- Riwayat
- Tentang Project
- Informasi Sistem

Fitur dashboard:

- Tema gelap profesional
- Input satu URL
- Input banyak URL
- Input CSV
- Upload satu atau banyak file
- Riwayat pemeriksaan
- Download hasil CSV
- Rekomendasi tindakan
- Penjelasan kenapa website resmi bisa terbaca perlu tinjauan
- Informasi author

---

### 7. CLI Utility

Selain dashboard, project juga menyediakan CLI agar pemeriksaan dapat dilakukan melalui terminal.

Contoh perintah:

```powershell
python src\run_phishrisk.py --mode url --input "https://praktikum.gunadarma.ac.id"
```

Cek banyak URL dari CSV:

```powershell
python src\run_phishrisk.py --mode urls --input "examples\input_url_step10.csv" --url-column url
```

Cek satu file:

```powershell
python src\run_phishrisk.py --mode file --input "data\samples_metadata\file_samples\contoh_catatan_aman.txt"
```

Cek semua file dalam folder:

```powershell
python src\run_phishrisk.py --mode folder --input "data\samples_metadata\file_samples"
```

Menentukan output sendiri:

```powershell
python src\run_phishrisk.py --mode url --input "https://www.bca.co.id" --output "reports\outputs\hasil_bca.csv"
```

---

## Hasil Model

Model terbaik pada pengujian lokal:

| Model | Accuracy | Precision Phishing | Recall Phishing | F1 Phishing | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Random Forest Intelligence V2 | 0.9977 | 0.9992 | 0.9955 | 0.9973 | 0.9990 |
| XGBoost Intelligence V2 | 0.9976 | 0.9997 | 0.9948 | 0.9973 | 0.9991 |

Model final yang digunakan:

```text
Random Forest Intelligence V2
```

File model:

```text
models/model_terbaik_intelligence_v2.pkl
```

---

## Struktur Folder

```text
PHISHING/
│
├── app/
│   └── app_streamlit.py
│
├── data/
│   ├── raw/
│   │   └── PhiUSIIL_Phishing_URL_Dataset.csv
│   │
│   ├── processed/
│   │   ├── dataset_training_intelligence_v2.csv
│   │   ├── X_train.csv
│   │   ├── X_test.csv
│   │   ├── y_train.csv
│   │   └── y_test.csv
│   │
│   ├── intelligence/
│   │   ├── official_domains_global.csv
│   │   ├── brand_keywords_global.csv
│   │   ├── suspicious_keywords_global.csv
│   │   ├── suspicious_file_rules.csv
│   │   └── generated_suspicious_urls.csv
│   │
│   ├── corrections/
│   │   ├── url_corrections.csv
│   │   └── file_corrections.csv
│   │
│   ├── samples_metadata/
│   │   └── file_samples/
│   │
│   └── uploads_streamlit/
│
├── examples/
│   └── input_url_step10.csv
│
├── models/
│   ├── model_rf_intelligence_v2.pkl
│   ├── model_xgb_intelligence_v2.pkl
│   ├── model_terbaik_intelligence_v2.pkl
│   └── model_rf_url_manual.pkl
│
├── notebooks/
│   ├── 01_load_dan_validasi_data.ipynb
│   ├── 02_analisis_data_awal.ipynb
│   ├── 03_pra_proses_data.ipynb
│   ├── 04_pelatihan_dan_evaluasi_model.ipynb
│   ├── 05_skor_risiko_dan_interpretasi.ipynb
│   └── 06_intelligence_global_dan_file_rules.ipynb
│
├── reports/
│   ├── figures/
│   └── outputs/
│
├── src/
│   ├── phishrisk_engine_v3.py
│   ├── run_phishrisk.py
│   ├── url_intelligence.py
│   └── file_static_analyzer.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Instalasi Lokal

### 1. Clone repository

```bash
git clone https://github.com/username/phishrisk-intelligence-system.git
cd phishrisk-intelligence-system
```

### 2. Buat virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Linux atau macOS:

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependency

```bash
pip install -r requirements.txt
```

Jika `requirements.txt` belum dibuat, gunakan dependency dasar berikut:

```bash
pip install streamlit pandas numpy scikit-learn xgboost joblib python-docx PyPDF2 openpyxl
```

### 4. Jalankan Streamlit

```bash
python -m streamlit run app/app_streamlit.py
```

Windows PowerShell:

```powershell
python -m streamlit run app\app_streamlit.py
```

---

## Cara Menjalankan Dashboard

Pastikan posisi terminal berada di root project:

```powershell
cd C:\Users\ASUS\PHISHING
.\venv\Scripts\Activate.ps1
python -m streamlit run app\app_streamlit.py
```

Setelah berjalan, buka browser:

```text
http://localhost:8501
```

---

## Cara Upload ke GitHub

### 1. Siapkan `.gitignore`

Saran isi `.gitignore`:

```gitignore
venv/
__pycache__/
.ipynb_checkpoints/
*.pyc
.DS_Store

data/uploads_streamlit/
reports/figures/
reports/outputs/*.csv
reports/outputs/*.txt
reports/outputs/*.json

# Dataset besar bisa diabaikan jika tidak ingin masuk GitHub
data/raw/*.csv
data/processed/*.csv

# Model boleh diupload jika ukurannya masih aman.
# Jika terlalu besar, gunakan Git LFS atau simpan di release/cloud storage.
# models/*.pkl
```

### 2. Inisialisasi Git

```bash
git init
git add .
git commit -m "Initial commit: PhishRisk Intelligence System"
```

### 3. Hubungkan ke GitHub

```bash
git branch -M main
git remote add origin https://github.com/username/phishrisk-intelligence-system.git
git push -u origin main
```

---

## Catatan Deployment

### Rekomendasi utama untuk versi Streamlit

Untuk versi project saat ini, deployment paling cocok adalah:

- Streamlit Community Cloud
- Render
- Railway
- Hugging Face Spaces
- Docker VPS

Alasannya sederhana: Streamlit membutuhkan proses Python server yang berjalan terus selama aplikasi digunakan.

### Deploy ke Streamlit Community Cloud

1. Push project ke GitHub.
2. Buka Streamlit Community Cloud.
3. Pilih repository.
4. Pilih branch `main`.
5. Isi entry file:

```text
app/app_streamlit.py
```

6. Pastikan file model dan file intelligence tersedia di repository atau bisa diunduh saat app berjalan.
7. Deploy.

### Catatan untuk Vercel dan Netlify

Project ini bisa dipush ke GitHub, tetapi versi Streamlit saat ini tidak ideal untuk langsung dideploy sebagai aplikasi utama di Vercel atau Netlify.

Jika tetap ingin menggunakan Vercel atau Netlify, pilihan yang lebih realistis:

#### Opsi 1: Vercel atau Netlify untuk landing page

Gunakan Vercel atau Netlify untuk:

- Halaman portfolio
- Dokumentasi project
- Landing page
- Link menuju dashboard Streamlit

#### Opsi 2: Ubah arsitektur

Ubah project menjadi:

```text
Frontend: Next.js / React
Backend: FastAPI
Model: dimuat di backend
Deployment frontend: Vercel / Netlify
Deployment backend: Render / Railway / VPS
```

Dengan arsitektur ini, Vercel atau Netlify menjadi tempat frontend, sedangkan model Python berjalan di backend yang memang mendukung proses Python.

---

## Komponen Sistem

### 1. Model Machine Learning

Model digunakan untuk membaca pola URL berdasarkan fitur:

- Panjang URL
- Panjang domain
- Penggunaan HTTPS
- Jumlah angka
- Rasio angka
- Jumlah karakter khusus
- Rasio karakter khusus
- Jumlah subdomain
- TLD
- Tanda hubung
- Sinyal intelligence tambahan

### 2. URL Intelligence

Komponen ini membaca:

- Domain resmi
- Brand keyword
- Brand tiruan
- Domain mirip brand
- Kata mencurigakan
- Punycode
- Pengganti huruf dengan angka
- Jumlah tanda hubung

### 3. File Static Analyzer

Komponen ini membaca file tanpa menjalankannya.

Tujuannya:

- Mengurangi risiko saat memeriksa file mencurigakan.
- Mendeteksi URL di dalam file.
- Membaca kata mencurigakan.
- Mengenali ekstensi yang perlu diwaspadai.
- Memberi skor risiko file.

### 4. Safety Calibration

Komponen ini menyesuaikan skor agar hasil tidak terlalu kaku.

Contoh:

- Website resmi yang cocok dengan daftar resmi tidak langsung ditandai phishing.
- Domain tiruan brand tetap dianggap berisiko walaupun tampilannya terlihat sederhana.
- File dengan URL berbahaya diberi prioritas lebih tinggi.

---

## Contoh Hasil

### Website resmi

```text
Input:
https://praktikum.gunadarma.ac.id

Output:
Terlihat Aman
Kategori: Rendah
Status: resmi_terlihat_aman
```

### Domain tiruan

```text
Input:
http://rricrosoft.com

Output:
Berisiko
Kategori: Sangat Tinggi
Status: domain_mirip_brand
```

### URL dengan kata mencurigakan

```text
Input:
http://bca-login-update.test

Output:
Berisiko
Kategori: Sangat Tinggi
Status: tiruan_brand_berisiko
```

### File mencurigakan

```text
Input:
contoh_dokumen_link.docx

Output:
Berisiko
Kategori: Sangat Tinggi
Alasan: file mengandung URL berisiko dan kata mencurigakan
```

---

## Batasan Sistem

Sistem ini memiliki batasan yang harus dipahami:

- Tidak membuka website secara langsung.
- Tidak menjalankan file.
- Tidak menggantikan antivirus.
- Tidak menggantikan forensik digital.
- Tidak menjamin 100% benar.
- Sangat bergantung pada dataset, fitur, dan daftar intelligence yang tersedia.
- Website resmi baru bisa saja belum masuk daftar pembanding.
- Domain resmi dengan struktur tidak umum bisa masuk kategori perlu tinjauan.

---

## Rencana Pengembangan

Pengembangan berikutnya yang disarankan:

- Menambah daftar domain resmi Indonesia, ASEAN, Eropa, dan Amerika.
- Menambah data kampus, bank, e-commerce, instansi, dan perusahaan resmi.
- Menambah mekanisme koreksi user.
- Menambah API dengan FastAPI.
- Membuat frontend Next.js untuk deployment di Vercel atau Netlify.
- Menambah Dockerfile.
- Menambah validasi file yang lebih kuat.
- Menambah log audit pemeriksaan.
- Menambah halaman admin untuk mengelola domain resmi.
- Menambah integrasi database.
- Menambah mode laporan PDF.

---

## Keamanan dan Etika

Project ini dibuat untuk:

- Edukasi Data Science.
- Deteksi awal phishing.
- Analisis defensif.
- Membantu user memahami risiko URL dan file.

Project ini tidak dibuat untuk:

- Membuat halaman phishing.
- Menjalankan malware.
- Mengambil data orang lain.
- Mengakses sistem tanpa izin.
- Melakukan tindakan ofensif.

Gunakan project ini secara bertanggung jawab.

---

## Author

**Harbangan Panjaitan**

Fokus:

- Data Science
- Machine Learning
- Software Engineering
- Cybersecurity awareness
- Phishing detection

Kontak:

- WhatsApp: `08158883565`
- Instagram: [https://www.instagram.com/qe.harpjtn/](https://www.instagram.com/qe.harpjtn/)
- LinkedIn: [https://www.linkedin.com/in/harbanganpjtn/](https://www.linkedin.com/in/harbanganpjtn/)
- GitHub: [https://github.com/harpjtnxvii](https://github.com/harpjtnxvii)

---

## Disclaimer

Hasil sistem ini adalah bantuan awal untuk mendeteksi risiko. Jangan menjadikan hasil model sebagai satu-satunya keputusan keamanan. Untuk kebutuhan organisasi, bank, kampus, atau instansi resmi, tetap lakukan validasi manual dan pemeriksaan keamanan lanjutan.

---

## License

Project ini dapat digunakan untuk pembelajaran, portfolio, dan riset. Jika ingin menggunakan untuk kebutuhan publik atau produksi, pastikan dataset, model, dan dependency sudah diperiksa dari sisi lisensi dan keamanan.
