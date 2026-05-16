# PhishRisk Intelligence System

PhishRisk Intelligence System adalah project **Data Science, Machine Learning, dan Cyber Security defensif** untuk membantu memeriksa indikasi phishing pada **alamat URL** dan **file**. Sistem ini tidak hanya memberi hasil `Terlihat Aman`, `Perlu Tinjauan`, atau `Berisiko`, tetapi juga menampilkan alasan, skor risiko, rekomendasi, dan sinyal tambahan dari engine lokal serta Public Threat Intelligence.

Project ini dibuat sebagai sistem pembelajaran dan implementasi portofolio untuk deteksi phishing secara defensif. Project ini **bukan alat untuk membuat phishing, menyerang website, mencuri data, atau menjalankan file berbahaya**.

---

## Preview Singkat

PhishRisk dapat digunakan untuk:

- Memeriksa satu URL secara manual.
- Memeriksa banyak URL dari input teks atau CSV.
- Memeriksa file secara statis tanpa menjalankan file.
- Membaca URL yang tertanam di file.
- Memberikan skor risiko dan kategori risiko.
- Memberikan rekomendasi tindakan yang mudah dipahami.
- Membandingkan URL dengan daftar domain resmi.
- Mendeteksi domain mirip brand resmi.
- Mendeteksi kata mencurigakan seperti `login`, `verify`, `update`, `secure`, dan `account`.
- Menggunakan Public Threat Intelligence melalui PhishTank dan URLhaus.
- Menampilkan dashboard Streamlit dengan halaman edukasi, rekomendasi, game cyber security, laporan, dan riwayat.

---

## Tujuan Project

Tujuan utama project ini adalah membangun sistem pendeteksi phishing yang:

1. **Mudah digunakan**  
   User dapat memasukkan URL atau file tanpa harus memahami kode program.

2. **Mudah dipahami**  
   Hasil tidak hanya berupa angka, tetapi juga alasan, status, dan saran tindakan.

3. **Lebih aman**  
   File diperiksa secara statis tanpa dijalankan.

4. **Lebih realistis**  
   Sistem membedakan website resmi, domain tiruan, domain mirip brand, kata mencurigakan, URL dalam file, dan catatan dari sumber threat intelligence publik.

5. **Layak untuk portofolio Data Science dan Cyber Security**  
   Project memiliki alur data, model, evaluasi, engine, CLI, Streamlit dashboard, dan dokumentasi.

---

## Masalah yang Diselesaikan

Phishing sering menggunakan alamat web yang terlihat mirip dengan website resmi. Contohnya:

- Domain mirip brand resmi, seperti `rricrosoft.com`.
- Huruf diganti angka, seperti `micros0ft`.
- Domain berisi kata mendesak seperti `login`, `verify`, `update`, `secure`, atau `account`.
- Link dikirim di dalam file PDF, Word, ZIP, TXT, HTML, atau APK.
- Website resmi tertentu bisa terbaca berisiko jika bentuk URL panjang atau memiliki banyak subdomain.

Karena itu, PhishRisk tidak hanya membaca hasil model, tetapi juga menambahkan konteks agar user tidak salah membaca hasil.

---

## Dataset

Dataset utama yang digunakan:

**PhiUSIIL Phishing URL Dataset**

Ringkasan dataset:

- Jumlah data: 235.795 URL
- Legitimate: 134.850 URL
- Phishing: 100.945 URL
- Jenis data: tabular
- Target awal:
  - `0` = Phishing pada dataset asli
  - `1` = Legitimate pada dataset asli

Pada project ini target kemudian disesuaikan menjadi:

```text
target_phishing = 1 berarti Phishing
target_phishing = 0 berarti Legitimate
```

Catatan: file dataset besar tidak disarankan untuk dimasukkan langsung ke GitHub. Simpan dataset besar secara lokal, gunakan `.gitignore`, atau gunakan penyimpanan eksternal jika diperlukan.

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
- Rekomendasi tindakan

Contoh hasil:

```text
URL: http://bca-login-update.test
Hasil V4: Berisiko
Kategori V4: Sangat Tinggi
Skor V4: 99.6
Public TI: tidak_ditemukan_di_public_ti
```

---

### 2. Pemeriksaan Banyak URL

User dapat memeriksa banyak URL melalui:

- Input teks bebas
- File CSV
- Contoh URL bawaan
- CLI

Output dapat disimpan sebagai CSV.

---

### 3. Pemeriksaan File Statis

Sistem dapat memeriksa file tanpa menjalankannya.

Jenis file yang didukung untuk pemeriksaan statis:

- TXT
- HTML
- PDF
- DOCX
- ZIP
- APK
- File lain tetap dibaca metadata dasarnya jika memungkinkan

Pemeriksaan file dapat mendeteksi:

- URL di dalam file
- Kata mencurigakan
- Ekstensi berisiko
- File berbahaya di dalam arsip
- Indikasi macro
- Indikasi JavaScript pada PDF
- Izin APK yang berisiko
- Skor risiko file

---

### 4. URL Intelligence

URL Intelligence menambahkan sinyal tambahan seperti:

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

Tujuannya adalah membantu sistem membedakan domain resmi dengan domain tiruan.

---

### 5. Public Threat Intelligence

Engine V4 menambahkan Public Threat Intelligence sebagai lapisan tambahan.

API yang digunakan:

1. **PhishTank**  
   Digunakan untuk melihat apakah URL pernah tercatat sebagai phishing.

2. **URLhaus**  
   Digunakan untuk melihat apakah URL pernah tercatat sebagai URL malware atau payload berbahaya.

Catatan:

- PhishTank dapat memberi catatan jika URL pernah muncul tetapi belum valid.
- URLhaus membutuhkan `URLHAUS_AUTH_KEY` agar aktif penuh.
- Public Threat Intelligence hanya sinyal tambahan, bukan satu-satunya keputusan keamanan.

---

### 6. AI Explainer Layer

Project memiliki AI Explainer Layer untuk membuat penjelasan hasil lebih mudah dipahami.

Mode kerja:

- Jika API eksternal aktif, sistem dapat menggunakan AI eksternal.
- Jika API eksternal gagal atau quota habis, sistem tetap berjalan dengan fallback lokal.

Catatan penting:

- Jangan menaruh API key di source code.
- Jangan push file `.env` ke GitHub.
- Simpan API key di environment variable atau file `.env` lokal.

---

### 7. Streamlit Dashboard

Dashboard Streamlit digunakan sebagai antarmuka utama untuk user.

Fitur website:

- Beranda ringkas
- Pemeriksaan URL
- Pemeriksaan file
- Pemeriksaan banyak URL
- Public Threat Intelligence
- Rekomendasi tindakan
- Panduan penggunaan
- Halaman edukasi phishing
- Halaman beta dan salah deteksi
- Game Cyber Security
- Laporan mini
- Riwayat pemeriksaan
- Informasi sistem
- Informasi author

Dashboard dibuat dengan tema gelap, layout responsif, dan container yang rapi agar nyaman digunakan di desktop, laptop, tablet, dan mobile.

---

### 8. Game Cyber Security

Website memiliki halaman game edukasi untuk melatih user membaca risiko phishing.

Mode game:

- Tebak Risiko
- Cari Sinyal
- Domain Surgery
- Incident Sprint
- File Triage
- Public Threat Intelligence Drill
- Laporan Mini
- Badge dan Scoreboard

Tujuan game adalah membuat user memahami ciri phishing tanpa membaca teori terlalu panjang.

---

## Arsitektur Program

Alur utama sistem:

```text
Input URL atau File
        ↓
Feature Extraction
        ↓
Model Machine Learning
        ↓
URL Intelligence
        ↓
File Static Analyzer
        ↓
Public Threat Intelligence
        ↓
AI Explainer / Fallback Lokal
        ↓
Streamlit Dashboard / CLI / CSV Report
```

---

## Struktur Folder

Struktur utama project:

```text
PHISHING/
├── app/
│   └── app_streamlit.py
├── data/
│   ├── raw/
│   ├── processed/
│   ├── intelligence/
│   ├── corrections/
│   └── samples_metadata/
├── examples/
│   ├── input_url_step10.csv
│   └── input_url_step13_public_ti.csv
├── models/
│   ├── model_terbaik_intelligence_v2.pkl
│   ├── model_rf_intelligence_v2.pkl
│   └── model_xgb_intelligence_v2.pkl
├── notebooks/
│   ├── 01_load_dan_validasi_data.ipynb
│   ├── 02_analisis_data_awal.ipynb
│   ├── 03_pra_proses_data.ipynb
│   ├── 04_pelatihan_dan_evaluasi_model.ipynb
│   ├── 05_skor_risiko_dan_interpretasi.ipynb
│   ├── 06_intelligence_global_dan_file_rules.ipynb
│   ├── 07_retraining_model_v2_intelligence.ipynb
│   ├── 08_integrasi_engine_v3.ipynb
│   ├── 09_final_program_utility.ipynb
│   ├── 10_ai_explainer_layer.ipynb
│   ├── 11_ai_activation_layer.ipynb
│   └── 12_public_threat_intelligence_step13.ipynb
├── reports/
│   └── outputs/
├── src/
│   ├── url_intelligence.py
│   ├── file_static_analyzer.py
│   ├── phishrisk_engine_v3.py
│   ├── phishrisk_engine_v4.py
│   ├── public_threat_intelligence.py
│   ├── run_phishrisk.py
│   ├── run_phishrisk_v4.py
│   ├── ai_safety_guard.py
│   ├── ai_explainer.py
│   ├── ai_report_generator.py
│   └── ai_feedback_manager.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Versi Engine

### Engine V3

Engine V3 menggabungkan:

- Model Intelligence V2
- URL Intelligence
- File Static Analyzer
- Kalibrasi hasil akhir
- Analisis URL dalam file

### Engine V4

Engine V4 menambahkan:

- Public Threat Intelligence
- PhishTank
- URLhaus
- Kalibrasi tambahan dari sumber eksternal
- CLI V4

Engine V4 tetap memakai Engine V3 sebagai dasar utama.

---

## Model Machine Learning

Model yang digunakan:

- Random Forest Intelligence V2
- XGBoost Intelligence V2

Model terbaik:

```text
Random Forest Intelligence V2
```

Ringkasan hasil evaluasi:

| Model | Accuracy | Precision Phishing | Recall Phishing | F1 Phishing | ROC AUC |
|---|---:|---:|---:|---:|---:|
| Random Forest Intelligence V2 | 0.9977 | 0.9992 | 0.9955 | 0.9973 | 0.9990 |
| XGBoost Intelligence V2 | 0.9976 | 0.9997 | 0.9948 | 0.9973 | 0.9991 |

Catatan: hasil evaluasi tinggi tidak berarti sistem sempurna. Sistem tetap membutuhkan validasi manual untuk kasus tertentu, terutama website resmi dengan struktur URL yang tidak umum.

---

## Instalasi

### 1. Clone Repository

```bash
git clone https://github.com/harpjtnxvii/adadadadaadaphishrisk.git
cd adadadadaadaphishrisk
```

### 2. Buat Virtual Environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Linux / macOS:

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Environment Variable

Buat file `.env` berdasarkan `.env.example`.

Contoh:

```text
OPENAI_API_KEY=
OPENAI_MODEL=
PHISHTANK_APP_KEY=
URLHAUS_AUTH_KEY=
PHISHRISK_PUBLIC_TI_ENABLE_PHISHTANK=1
PHISHRISK_PUBLIC_TI_ENABLE_URLHAUS=1
PHISHRISK_PUBLIC_TI_TIMEOUT=12
```

Catatan:

- `.env` tidak boleh di-push ke GitHub.
- `.env.example` boleh di-push.
- Jika tidak punya API key, sistem tetap berjalan dengan fallback lokal.

---

## Menjalankan Streamlit

```bash
python -m streamlit run app/app_streamlit.py
```

Atau di Windows PowerShell:

```powershell
python -m streamlit run app\app_streamlit.py
```

Setelah berjalan, buka:

```text
http://localhost:8501
```

---

## Menjalankan CLI Engine V3

Cek satu URL:

```bash
python src/run_phishrisk.py --mode url --input "https://praktikum.gunadarma.ac.id"
```

Cek banyak URL dari CSV:

```bash
python src/run_phishrisk.py --mode urls --input "examples/input_url_step10.csv" --url-column url
```

Cek satu file:

```bash
python src/run_phishrisk.py --mode file --input "data/samples_metadata/file_samples/contoh_catatan_aman.txt"
```

Cek folder file:

```bash
python src/run_phishrisk.py --mode folder --input "data/samples_metadata/file_samples"
```

---

## Menjalankan CLI Engine V4

Cek satu URL:

```bash
python src/run_phishrisk_v4.py --mode url --input "http://bca-login-update.test"
```

Cek banyak URL:

```bash
python src/run_phishrisk_v4.py --mode urls --input "examples/input_url_step13_public_ti.csv" --url-column url
```

Cek file:

```bash
python src/run_phishrisk_v4.py --mode file --input "data/samples_metadata/file_samples/contoh_catatan_aman.txt"
```

Contoh output:

```text
Hasil Engine V4
============================================================
URL: http://bca-login-update.test
Hasil V4: Berisiko
Kategori V4: Sangat Tinggi
Skor V4: 99.6
Public TI: tidak_ditemukan_di_public_ti
```

---

## Cara Membaca Hasil

### Terlihat Aman

Artinya sistem tidak menemukan sinyal kuat yang berbahaya.

Tetap lakukan:

- Cek ejaan domain.
- Buka website penting dari bookmark atau ketik manual.
- Jangan mengisi data sensitif jika link berasal dari pesan acak.

### Perlu Tinjauan

Artinya sistem menemukan sinyal yang perlu diperiksa ulang.

Lakukan:

- Bandingkan dengan website resmi.
- Hubungi admin resmi jika berkaitan dengan kampus, bank, perusahaan, atau instansi.
- Jangan masukkan OTP, PIN, password, atau data pembayaran sebelum yakin.

### Berisiko

Artinya sistem menemukan sinyal kuat yang berbahaya.

Lakukan:

- Jangan buka link.
- Jangan login.
- Jangan isi data pribadi.
- Jangan unduh atau jalankan file.
- Laporkan ke pihak terkait.
- Simpan bukti jika berasal dari chat, email, SMS, atau DM.

---

## Deployment

### Rekomendasi Deployment

Untuk aplikasi Streamlit, deployment yang paling sesuai:

- Streamlit Community Cloud
- Render
- Railway
- Hugging Face Spaces
- VPS

### Catatan untuk Vercel dan Netlify

Vercel dan Netlify lebih cocok untuk website frontend statis atau frontend JavaScript seperti Next.js dan React. Streamlit membutuhkan server Python yang berjalan terus, sehingga **tidak ideal langsung dideploy ke Vercel atau Netlify** tanpa perubahan arsitektur.

Jika ingin tetap memakai Vercel atau Netlify, opsi yang lebih rapi adalah:

```text
Frontend Next.js / React di Vercel atau Netlify
Backend PhishRisk API di Render / Railway / VPS
Model dan engine berjalan di backend Python
```

---

## File Besar dan GitHub

GitHub membatasi ukuran file besar. Karena itu file seperti dataset besar, hasil preprocessing besar, dan model besar sebaiknya tidak dipaksa masuk repo.

Disarankan ignore:

```text
venv/
.env
data/raw/
data/processed/
data/uploads_streamlit/
reports/outputs/
*.pkl
*.joblib
```

Jika model harus dibagikan, gunakan:

- Git LFS
- Google Drive
- Hugging Face Model Hub
- Release GitHub
- Cloud storage

---

## Keamanan

Project ini dibuat untuk kebutuhan defensif.

Yang boleh dilakukan:

- Deteksi phishing.
- Edukasi keamanan.
- Analisis URL.
- Analisis file secara statis.
- Membuat laporan keamanan.
- Memberi rekomendasi pencegahan.

Yang tidak boleh dilakukan:

- Membuat phishing kit.
- Mencuri password.
- Menjalankan malware.
- Membuat payload berbahaya.
- Melakukan serangan ke website atau akun.
- Menyalahgunakan data user.

---

## Batasan Sistem

PhishRisk bukan pengganti penuh sistem keamanan profesional.

Batasan:

- Sistem tidak membuktikan kepemilikan domain.
- Sistem tidak membaca seluruh perilaku website secara dinamis.
- Sistem tidak menjalankan file.
- Sistem tidak menjamin semua phishing pasti terdeteksi.
- Public Threat Intelligence bisa terkena rate limit.
- URLhaus membutuhkan Auth-Key.
- AI eksternal membutuhkan quota atau billing aktif.

Gunakan hasil sistem sebagai bantuan awal, lalu validasi manual untuk kasus penting.

---

## Author

**Harbangan Panjaitan**

- WhatsApp: 08158883565
- Instagram: https://www.instagram.com/qe.harpjtn/
- LinkedIn: https://www.linkedin.com/in/harbanganpjtn/
- GitHub: https://github.com/harpjtnxvii

---

## License

Project ini dibuat untuk pembelajaran, portofolio, dan pengembangan sistem deteksi phishing defensif.

Gunakan secara bertanggung jawab.
