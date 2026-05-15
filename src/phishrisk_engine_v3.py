
from pathlib import Path
from urllib.parse import urlparse
import hashlib
import json
import re
import sys

import joblib
import pandas as pd


DIREKTORI_SRC = Path(__file__).resolve().parent

if str(DIREKTORI_SRC) not in sys.path:
    sys.path.append(str(DIREKTORI_SRC))

import url_intelligence
import file_static_analyzer


FITUR_INTELLIGENCE_V2 = [
    "is_official_domain",
    "brand_keyword_detected",
    "brand_but_not_official",
    "suspicious_keyword_count",
    "suspicious_keyword_score",
    "lookalike_brand_detected",
    "lookalike_score",
    "uses_punycode",
    "uses_digit_substitution",
    "hyphen_count"
]


def ambil_domain_dari_url(url):
    url = str(url).strip()
    hasil_parse = urlparse(url)

    if hasil_parse.netloc:
        return hasil_parse.netloc.lower().split("@")[-1].split(":")[0]

    hasil_parse = urlparse("http://" + url)
    return hasil_parse.netloc.lower().split("@")[-1].split(":")[0]


def cek_domain_ip(domain):
    pola_ip = r"^\d{1,3}(\.\d{1,3}){3}$"
    return int(bool(re.match(pola_ip, str(domain).strip())))


def ambil_tld(domain):
    bagian = [item for item in str(domain).lower().split(".") if item]

    if not bagian:
        return "tidak_diketahui"

    return bagian[-1]


def hitung_subdomain(domain):
    domain = str(domain).lower().strip()
    bagian = [item for item in domain.split(".") if item]

    if cek_domain_ip(domain):
        return 0

    if len(bagian) <= 2:
        return 0

    return len(bagian) - 2


def hapus_skema_url(url):
    return re.sub(r"^https?://", "", str(url).strip(), flags=re.IGNORECASE)


def hapus_www_awal(teks):
    return re.sub(r"^www\.", "", str(teks).strip(), flags=re.IGNORECASE)


def hitung_obfuscation(url):
    pola = r"%[0-9a-fA-F]{2}"
    return len(re.findall(pola, str(url)))


def kategori_dari_skor(skor):
    skor = float(skor)

    if skor < 25:
        return "Rendah"

    if skor < 50:
        return "Sedang"

    if skor < 75:
        return "Tinggi"

    return "Sangat Tinggi"


def ekstrak_url_dari_teks(teks):
    teks = str(teks)
    pola_url = r"https?://[^\s<>'\"\\)\]\}]+"
    daftar_url = re.findall(pola_url, teks, flags=re.IGNORECASE)

    daftar_bersih = []

    for url in daftar_url:
        url = url.strip().rstrip(".,;:")
        if url not in daftar_bersih:
            daftar_bersih.append(url)

    return daftar_bersih


class PhishRiskEngineV3:
    def __init__(self, direktori_project):
        self.direktori_project = Path(direktori_project)

        self.lokasi_model = self.direktori_project / "models" / "model_terbaik_intelligence_v2.pkl"
        self.lokasi_fitur = self.direktori_project / "reports" / "outputs" / "daftar_fitur_intelligence_v2.json"

        if not self.lokasi_model.exists():
            raise FileNotFoundError(f"Model Intelligence V2 tidak ditemukan: {self.lokasi_model}")

        if not self.lokasi_fitur.exists():
            raise FileNotFoundError(f"Daftar fitur Intelligence V2 tidak ditemukan: {self.lokasi_fitur}")

        self.model = joblib.load(self.lokasi_model)

        with open(self.lokasi_fitur, "r", encoding="utf-8") as file:
            self.daftar_fitur_model = json.load(file)

        self.data_domain_resmi, self.data_brand_keyword, self.data_suspicious_keyword = url_intelligence.muat_data_intelligence(
            self.direktori_project
        )

    def ekstrak_fitur_url_manual(self, url):
        url = str(url).strip()
        domain = ambil_domain_dari_url(url)
        tld = ambil_tld(domain)

        url_tanpa_skema = hapus_skema_url(url)
        url_untuk_hitung = hapus_www_awal(url_tanpa_skema)

        panjang_url = len(url)
        panjang_domain = len(domain)

        jumlah_obfuscation = hitung_obfuscation(url)
        jumlah_huruf = sum(karakter.isalpha() for karakter in url_untuk_hitung)
        jumlah_angka = sum(karakter.isdigit() for karakter in url_untuk_hitung)

        jumlah_sama_dengan = url_untuk_hitung.count("=")
        jumlah_tanda_tanya = url_untuk_hitung.count("?")
        jumlah_ampersand = url_untuk_hitung.count("&")

        karakter_khusus = re.findall(r"[^a-zA-Z0-9]", url_untuk_hitung)
        jumlah_karakter_khusus = len(karakter_khusus)

        fitur = {
            "URLLength": panjang_url,
            "DomainLength": panjang_domain,
            "IsDomainIP": cek_domain_ip(domain),
            "TLDLength": len(tld),
            "NoOfSubDomain": hitung_subdomain(domain),
            "HasObfuscation": int(jumlah_obfuscation > 0),
            "NoOfObfuscatedChar": jumlah_obfuscation * 3,
            "ObfuscationRatio": (jumlah_obfuscation * 3 / panjang_url) if panjang_url > 0 else 0,
            "NoOfLettersInURL": jumlah_huruf,
            "LetterRatioInURL": (jumlah_huruf / panjang_url) if panjang_url > 0 else 0,
            "NoOfDegitsInURL": jumlah_angka,
            "DegitRatioInURL": (jumlah_angka / panjang_url) if panjang_url > 0 else 0,
            "NoOfEqualsInURL": jumlah_sama_dengan,
            "NoOfQMarkInURL": jumlah_tanda_tanya,
            "NoOfAmpersandInURL": jumlah_ampersand,
            "NoOfOtherSpecialCharsInURL": jumlah_karakter_khusus,
            "SpacialCharRatioInURL": (jumlah_karakter_khusus / panjang_url) if panjang_url > 0 else 0,
            "IsHTTPS": int(url.lower().startswith("https://"))
        }

        for nama_fitur in self.daftar_fitur_model:
            if nama_fitur.startswith("TLD_"):
                nama_tld = nama_fitur.replace("TLD_", "")
                fitur[nama_fitur] = int(tld == nama_tld)

        fitur_tld_tersedia = [fitur for fitur in self.daftar_fitur_model if fitur.startswith("TLD_")]
        daftar_tld_model = [fitur.replace("TLD_", "") for fitur in fitur_tld_tersedia if fitur != "TLD_lainnya"]

        if f"TLD_{tld}" not in fitur_tld_tersedia and "TLD_lainnya" in self.daftar_fitur_model:
            fitur["TLD_lainnya"] = 1

        return fitur, domain, tld

    def ekstrak_fitur_url_v3(self, url):
        fitur_manual, domain, tld = self.ekstrak_fitur_url_manual(url)

        sinyal_intelligence = url_intelligence.analisis_url_intelligence(
            url,
            self.data_domain_resmi,
            self.data_brand_keyword,
            self.data_suspicious_keyword
        )

        fitur_intelligence = {}

        for nama_fitur in FITUR_INTELLIGENCE_V2:
            fitur_intelligence[nama_fitur] = sinyal_intelligence.get(nama_fitur, 0)

        fitur_gabungan = {}
        fitur_gabungan.update(fitur_manual)
        fitur_gabungan.update(fitur_intelligence)

        data_fitur = pd.DataFrame([fitur_gabungan])
        data_fitur = data_fitur.reindex(columns=self.daftar_fitur_model, fill_value=0)
        data_fitur = data_fitur.fillna(0)

        return data_fitur, domain, tld, sinyal_intelligence

    def kalibrasi_skor_url(self, skor_model, sinyal_intelligence):
        skor_model = float(skor_model)
        status = sinyal_intelligence.get("intelligence_status", "")

        if status == "resmi_terlihat_aman":
            if skor_model >= 60:
                return 35.0
            if skor_model >= 50:
                return 28.0
            return min(skor_model, 24.0)

        if status == "resmi_perlu_tinjauan":
            return max(min(skor_model, 60.0), 35.0)

        if status == "tiruan_brand_berisiko":
            return max(skor_model, 85.0)

        if status == "domain_mirip_brand_berisiko":
            return max(skor_model, 85.0)

        if status == "domain_mirip_brand":
            return max(skor_model, 75.0)

        if status == "kata_mencurigakan_tinggi":
            return max(skor_model, 75.0)

        if status == "punycode_perlu_tinjauan":
            return max(skor_model, 65.0)

        if status == "domain_ip_perlu_tinjauan":
            return max(skor_model, 65.0)

        if status == "brand_tidak_resmi_perlu_tinjauan":
            return max(skor_model, 60.0)

        if status == "kata_mencurigakan_perlu_tinjauan":
            return max(skor_model, 45.0)

        return skor_model

    def tentukan_hasil_akhir_url(self, skor_final, sinyal_intelligence):
        status = sinyal_intelligence.get("intelligence_status", "")
        skor_final = float(skor_final)

        if status == "resmi_terlihat_aman":
            if skor_final < 25:
                return "Terlihat Aman"
            return "Perlu Tinjauan"

        if status == "resmi_perlu_tinjauan":
            return "Perlu Tinjauan"

        if status in [
            "tiruan_brand_berisiko",
            "domain_mirip_brand_berisiko",
            "kata_mencurigakan_tinggi"
        ]:
            return "Berisiko"

        if status in [
            "domain_mirip_brand",
            "punycode_perlu_tinjauan",
            "domain_ip_perlu_tinjauan",
            "brand_tidak_resmi_perlu_tinjauan",
            "kata_mencurigakan_perlu_tinjauan"
        ]:
            if skor_final >= 75:
                return "Berisiko"
            return "Perlu Tinjauan"

        if skor_final < 25:
            return "Terlihat Aman"

        if skor_final < 50:
            return "Perlu Tinjauan"

        return "Berisiko"

    def buat_rekomendasi_url(self, hasil_akhir, skor_model, skor_final, sinyal_intelligence):
        status = sinyal_intelligence.get("intelligence_status", "")

        if status == "resmi_terlihat_aman" and hasil_akhir == "Terlihat Aman":
            return "Alamat cocok dengan daftar domain resmi dan tidak menunjukkan sinyal kuat yang mencurigakan. Tetap pastikan alamat diketik langsung dari sumber resmi."

        if status == "resmi_terlihat_aman" and hasil_akhir == "Perlu Tinjauan":
            return "Alamat cocok dengan daftar domain resmi, tetapi pola URL perlu diperiksa. Jangan langsung dianggap phishing, namun tetap pastikan alamat berasal dari kanal resmi."

        if status == "resmi_perlu_tinjauan":
            return "Alamat berada pada domain resmi, tetapi memiliki pola yang perlu diperiksa. Pastikan tidak ada path, parameter, atau redirect mencurigakan."

        if status in ["tiruan_brand_berisiko", "domain_mirip_brand_berisiko", "domain_mirip_brand"]:
            return "Alamat terindikasi meniru brand atau domain resmi. Jangan digunakan untuk login, transaksi, atau memasukkan data pribadi."

        if hasil_akhir == "Terlihat Aman":
            return "Alamat terlihat aman berdasarkan model dan pemeriksaan intelligence. Tetap pastikan alamat berasal dari sumber tepercaya."

        if hasil_akhir == "Perlu Tinjauan":
            return "Alamat perlu diperiksa manual. Jangan langsung memasukkan kata sandi, OTP, data pribadi, atau informasi pembayaran."

        return "Alamat berisiko. Jangan dibuka, jangan diisi, dan laporkan jika berasal dari pesan mencurigakan."

    def analisis_url(self, url):
        data_fitur, domain, tld, sinyal = self.ekstrak_fitur_url_v3(url)

        probabilitas_phishing = float(self.model.predict_proba(data_fitur)[0][1])
        skor_model = round(probabilitas_phishing * 100, 2)

        prediksi_model = int(probabilitas_phishing >= 0.5)
        label_model = "Phishing" if prediksi_model == 1 else "Legitimate"

        skor_final = round(self.kalibrasi_skor_url(skor_model, sinyal), 2)
        kategori_risiko = kategori_dari_skor(skor_final)
        hasil_akhir = self.tentukan_hasil_akhir_url(skor_final, sinyal)
        rekomendasi = self.buat_rekomendasi_url(hasil_akhir, skor_model, skor_final, sinyal)

        hasil = {
            "url": str(url),
            "domain": domain,
            "tld": tld,
            "probabilitas_model": round(probabilitas_phishing, 6),
            "skor_model": skor_model,
            "label_model": label_model,
            "skor_final": skor_final,
            "kategori_risiko": kategori_risiko,
            "hasil_akhir": hasil_akhir,
            "rekomendasi": rekomendasi,
            "intelligence_status": sinyal.get("intelligence_status", ""),
            "intelligence_reason": sinyal.get("intelligence_reason", ""),
            "is_official_domain": sinyal.get("is_official_domain", 0),
            "official_brand": sinyal.get("official_brand", ""),
            "official_domain": sinyal.get("official_domain", ""),
            "brand_detected": sinyal.get("brand_detected", ""),
            "brand_but_not_official": sinyal.get("brand_but_not_official", 0),
            "suspicious_keywords": sinyal.get("suspicious_keywords", ""),
            "suspicious_keyword_score": sinyal.get("suspicious_keyword_score", 0),
            "lookalike_brand_detected": sinyal.get("lookalike_brand_detected", 0),
            "lookalike_brand": sinyal.get("lookalike_brand", ""),
            "lookalike_score": sinyal.get("lookalike_score", 0),
            "uses_punycode": sinyal.get("uses_punycode", 0),
            "uses_digit_substitution": sinyal.get("uses_digit_substitution", 0),
            "hyphen_count": sinyal.get("hyphen_count", 0)
        }

        return hasil

    def analisis_banyak_url(self, daftar_url):
        hasil = []

        for url in daftar_url:
            hasil.append(self.analisis_url(url))

        return pd.DataFrame(hasil)

    def analisis_file(self, lokasi_file):
        hasil_file_statis, hasil_url_intelligence = file_static_analyzer.analisis_file_statis(
            lokasi_file,
            self.direktori_project
        )

        daftar_url = []

        url_terdeteksi = hasil_file_statis.get("url_terdeteksi", "")

        if isinstance(url_terdeteksi, str) and url_terdeteksi.strip():
            daftar_url = [url.strip() for url in url_terdeteksi.split(" | ") if url.strip()]

        if len(daftar_url) > 0:
            data_url_v3 = self.analisis_banyak_url(daftar_url)
        else:
            data_url_v3 = pd.DataFrame()

        jumlah_url_berisiko_v3 = 0
        jumlah_url_tinjauan_v3 = 0

        if not data_url_v3.empty:
            jumlah_url_berisiko_v3 = int((data_url_v3["hasil_akhir"] == "Berisiko").sum())
            jumlah_url_tinjauan_v3 = int((data_url_v3["hasil_akhir"] == "Perlu Tinjauan").sum())

        skor_file_awal = float(hasil_file_statis.get("skor_risiko_file", 0))
        skor_final = skor_file_awal

        if jumlah_url_berisiko_v3 > 0:
            skor_final = max(skor_final, 80)

        if jumlah_url_tinjauan_v3 > 0:
            skor_final = max(skor_final, 55)

        if hasil_file_statis.get("jumlah_izin_apk_berisiko", 0) > 0:
            skor_final = max(skor_final, 85)

        if hasil_file_statis.get("pdf_javascript", 0) == 1:
            skor_final = max(skor_final, 85)

        if hasil_file_statis.get("pdf_open_action", 0) == 1 or hasil_file_statis.get("pdf_launch_action", 0) == 1:
            skor_final = max(skor_final, 85)

        if hasil_file_statis.get("jumlah_file_berbahaya_dalam_arsip", 0) > 0:
            skor_final = max(skor_final, 85)

        skor_final = int(min(100, max(0, skor_final)))
        kategori_final = kategori_dari_skor(skor_final)

        if skor_final < 25:
            hasil_akhir_file = "Terlihat Aman"
        elif skor_final < 50:
            hasil_akhir_file = "Perlu Tinjauan"
        else:
            hasil_akhir_file = "Berisiko"

        hasil_file_statis["jumlah_url_berisiko_v3"] = jumlah_url_berisiko_v3
        hasil_file_statis["jumlah_url_perlu_tinjauan_v3"] = jumlah_url_tinjauan_v3
        hasil_file_statis["skor_final_file_v3"] = skor_final
        hasil_file_statis["kategori_final_file_v3"] = kategori_final
        hasil_file_statis["hasil_akhir_file_v3"] = hasil_akhir_file

        if hasil_akhir_file == "Terlihat Aman":
            hasil_file_statis["rekomendasi_final_file_v3"] = "File terlihat rendah risiko berdasarkan pemeriksaan statis. Tetap buka hanya jika sumbernya tepercaya."
        elif hasil_akhir_file == "Perlu Tinjauan":
            hasil_file_statis["rekomendasi_final_file_v3"] = "File perlu diperiksa manual sebelum dibuka, terutama jika berasal dari pesan, email, atau sumber tidak dikenal."
        else:
            hasil_file_statis["rekomendasi_final_file_v3"] = "File berisiko. Jangan dibuka atau dijalankan sebelum diperiksa di lingkungan aman."

        return hasil_file_statis, data_url_v3

    def analisis_banyak_file(self, daftar_lokasi_file):
        hasil_file_semua = []
        hasil_url_semua = []

        for lokasi_file in daftar_lokasi_file:
            hasil_file, data_url_v3 = self.analisis_file(lokasi_file)
            hasil_file_semua.append(hasil_file)

            if not data_url_v3.empty:
                data_url_v3 = data_url_v3.copy()
                data_url_v3.insert(0, "nama_file_sumber", Path(lokasi_file).name)
                hasil_url_semua.append(data_url_v3)

        data_file = pd.DataFrame(hasil_file_semua)

        if hasil_url_semua:
            data_url = pd.concat(hasil_url_semua, ignore_index=True)
        else:
            data_url = pd.DataFrame()

        return data_file, data_url


def buat_engine(direktori_project):
    return PhishRiskEngineV3(direktori_project)


def analisis_url_v3(url, direktori_project):
    engine = PhishRiskEngineV3(direktori_project)
    return engine.analisis_url(url)


def analisis_banyak_url_v3(daftar_url, direktori_project):
    engine = PhishRiskEngineV3(direktori_project)
    return engine.analisis_banyak_url(daftar_url)


def analisis_file_v3(lokasi_file, direktori_project):
    engine = PhishRiskEngineV3(direktori_project)
    return engine.analisis_file(lokasi_file)


def analisis_banyak_file_v3(daftar_lokasi_file, direktori_project):
    engine = PhishRiskEngineV3(direktori_project)
    return engine.analisis_banyak_file(daftar_lokasi_file)
