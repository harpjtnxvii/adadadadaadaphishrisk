
from pathlib import Path
from urllib.parse import urlparse
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


def muat_model_dan_fitur(direktori_project):
    direktori_project = Path(direktori_project)

    lokasi_model = direktori_project / "models" / "model_rf_url_manual.pkl"
    lokasi_fitur = direktori_project / "reports" / "outputs" / "daftar_fitur_url_manual.json"

    if not lokasi_model.exists():
        raise FileNotFoundError(f"Model URL manual tidak ditemukan: {lokasi_model}")

    if not lokasi_fitur.exists():
        raise FileNotFoundError(f"Daftar fitur URL manual tidak ditemukan: {lokasi_fitur}")

    model = joblib.load(lokasi_model)

    with open(lokasi_fitur, "r", encoding="utf-8") as file:
        daftar_fitur = json.load(file)

    return model, daftar_fitur


def ekstrak_fitur_url_manual(url, daftar_fitur):
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
    jumlah_tanya = url_untuk_hitung.count("?")
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
        "NoOfQMarkInURL": jumlah_tanya,
        "NoOfAmpersandInURL": jumlah_ampersand,
        "NoOfOtherSpecialCharsInURL": jumlah_karakter_khusus,
        "SpacialCharRatioInURL": (jumlah_karakter_khusus / panjang_url) if panjang_url > 0 else 0,
        "IsHTTPS": int(url.lower().startswith("https://"))
    }

    for nama_fitur in daftar_fitur:
        if nama_fitur.startswith("TLD_"):
            nama_tld = nama_fitur.replace("TLD_", "")
            fitur[nama_fitur] = int(tld == nama_tld)

    if f"TLD_{tld}" not in daftar_fitur and "TLD_lainnya" in daftar_fitur:
        fitur["TLD_lainnya"] = 1

    data_fitur = pd.DataFrame([fitur])
    data_fitur = data_fitur.reindex(columns=daftar_fitur, fill_value=0)

    return data_fitur, domain, tld


def kategori_dari_skor(skor):
    skor = float(skor)

    if skor < 25:
        return "Rendah"

    if skor < 50:
        return "Sedang"

    if skor < 75:
        return "Tinggi"

    return "Sangat Tinggi"


def hasil_akhir_dari_skor(skor, status_intelligence):
    if status_intelligence == "resmi_terlihat_aman":
        return "Terlihat Aman"

    if status_intelligence == "resmi_perlu_tinjauan":
        return "Perlu Tinjauan"

    if status_intelligence in [
        "tiruan_brand_berisiko",
        "domain_mirip_brand_berisiko",
        "kata_mencurigakan_tinggi"
    ]:
        return "Berisiko"

    if status_intelligence in [
        "domain_mirip_brand",
        "punycode_perlu_tinjauan",
        "domain_ip_perlu_tinjauan",
        "brand_tidak_resmi_perlu_tinjauan",
        "kata_mencurigakan_perlu_tinjauan"
    ]:
        return "Perlu Tinjauan" if skor < 75 else "Berisiko"

    if skor < 25:
        return "Terlihat Aman"

    if skor < 50:
        return "Perlu Tinjauan"

    return "Berisiko"


def gabungkan_skor_model_dan_intelligence(skor_model, sinyal_intelligence):
    skor_awal = float(skor_model)
    status = sinyal_intelligence.get("intelligence_status", "")

    if status == "resmi_terlihat_aman":
        return min(skor_awal, 20)

    if status == "resmi_perlu_tinjauan":
        return max(min(skor_awal, 60), 35)

    if status == "tiruan_brand_berisiko":
        return max(skor_awal, 85)

    if status == "domain_mirip_brand_berisiko":
        return max(skor_awal, 85)

    if status == "domain_mirip_brand":
        return max(skor_awal, 65)

    if status == "kata_mencurigakan_tinggi":
        return max(skor_awal, 75)

    if status == "punycode_perlu_tinjauan":
        return max(skor_awal, 60)

    if status == "domain_ip_perlu_tinjauan":
        return max(skor_awal, 60)

    if status == "brand_tidak_resmi_perlu_tinjauan":
        return max(skor_awal, 55)

    if status == "kata_mencurigakan_perlu_tinjauan":
        return max(skor_awal, 45)

    return skor_awal


def buat_rekomendasi_url(hasil_akhir, kategori_risiko, status_intelligence):
    if hasil_akhir == "Terlihat Aman":
        return "Alamat terlihat aman berdasarkan model dan pemeriksaan intelligence. Tetap pastikan alamat diketik langsung dari sumber resmi."

    if hasil_akhir == "Perlu Tinjauan":
        return "Alamat perlu diperiksa manual. Jangan langsung memasukkan kata sandi, OTP, data pribadi, atau informasi pembayaran."

    if status_intelligence in ["tiruan_brand_berisiko", "domain_mirip_brand_berisiko", "domain_mirip_brand"]:
        return "Alamat terindikasi meniru brand atau domain resmi. Jangan digunakan untuk login atau transaksi."

    return "Alamat berisiko. Jangan dibuka, jangan diisi, dan laporkan jika berasal dari pesan mencurigakan."


def analisis_url_v2(url, direktori_project):
    direktori_project = Path(direktori_project)

    model, daftar_fitur = muat_model_dan_fitur(direktori_project)
    data_fitur, domain, tld = ekstrak_fitur_url_manual(url, daftar_fitur)

    probabilitas_phishing = float(model.predict_proba(data_fitur)[0][1])
    skor_model = round(probabilitas_phishing * 100, 2)

    data_domain_resmi, data_brand_keyword, data_suspicious_keyword = url_intelligence.muat_data_intelligence(
        direktori_project
    )

    sinyal = url_intelligence.analisis_url_intelligence(
        url,
        data_domain_resmi,
        data_brand_keyword,
        data_suspicious_keyword
    )

    skor_final = round(gabungkan_skor_model_dan_intelligence(skor_model, sinyal), 2)
    kategori_final = kategori_dari_skor(skor_final)
    hasil_akhir = hasil_akhir_dari_skor(skor_final, sinyal["intelligence_status"])
    rekomendasi = buat_rekomendasi_url(
        hasil_akhir,
        kategori_final,
        sinyal["intelligence_status"]
    )

    hasil = {
        "url": url,
        "domain": domain,
        "tld": tld,
        "skor_model": skor_model,
        "probabilitas_model": round(probabilitas_phishing, 6),
        "skor_final": skor_final,
        "kategori_risiko": kategori_final,
        "hasil_akhir": hasil_akhir,
        "rekomendasi": rekomendasi,
        "intelligence_status": sinyal["intelligence_status"],
        "intelligence_reason": sinyal["intelligence_reason"],
        "is_official_domain": sinyal["is_official_domain"],
        "official_brand": sinyal["official_brand"],
        "official_domain": sinyal["official_domain"],
        "brand_detected": sinyal["brand_detected"],
        "brand_but_not_official": sinyal["brand_but_not_official"],
        "suspicious_keywords": sinyal["suspicious_keywords"],
        "suspicious_keyword_score": sinyal["suspicious_keyword_score"],
        "lookalike_brand_detected": sinyal["lookalike_brand_detected"],
        "lookalike_brand": sinyal["lookalike_brand"],
        "lookalike_score": sinyal["lookalike_score"],
        "uses_punycode": sinyal["uses_punycode"],
        "uses_digit_substitution": sinyal["uses_digit_substitution"],
        "hyphen_count": sinyal["hyphen_count"]
    }

    return hasil


def analisis_banyak_url_v2(daftar_url, direktori_project):
    hasil = []

    for url in daftar_url:
        hasil.append(analisis_url_v2(url, direktori_project))

    return pd.DataFrame(hasil)


def analisis_file_v2(lokasi_file, direktori_project):
    hasil_file, hasil_url = file_static_analyzer.analisis_file_statis(
        lokasi_file,
        direktori_project
    )

    skor = float(hasil_file["skor_risiko_file"])

    if hasil_file["jumlah_url_berisiko_intelligence"] > 0:
        skor = max(skor, 75)

    if hasil_file["jumlah_izin_apk_berisiko"] > 0:
        skor = max(skor, 85)

    if hasil_file["pdf_javascript"] == 1 or hasil_file["pdf_open_action"] == 1:
        skor = max(skor, 85)

    skor = int(min(100, max(0, skor)))
    kategori = kategori_dari_skor(skor)

    if skor < 25:
        hasil_akhir = "Terlihat Aman"
    elif skor < 50:
        hasil_akhir = "Perlu Tinjauan"
    else:
        hasil_akhir = "Berisiko"

    hasil_file["skor_final_file"] = skor
    hasil_file["kategori_final_file"] = kategori
    hasil_file["hasil_akhir_file"] = hasil_akhir

    return hasil_file, hasil_url


def analisis_banyak_file_v2(daftar_lokasi_file, direktori_project):
    hasil_file_semua = []
    hasil_url_semua = []

    for lokasi_file in daftar_lokasi_file:
        hasil_file, hasil_url = analisis_file_v2(lokasi_file, direktori_project)
        hasil_file_semua.append(hasil_file)

        if not hasil_url.empty:
            hasil_url = hasil_url.copy()
            hasil_url.insert(0, "nama_file_sumber", Path(lokasi_file).name)
            hasil_url_semua.append(hasil_url)

    data_file = pd.DataFrame(hasil_file_semua)

    if hasil_url_semua:
        data_url = pd.concat(hasil_url_semua, ignore_index=True)
    else:
        data_url = pd.DataFrame()

    return data_file, data_url


# Safety Calibration V2.1
# Fungsi ini mengganti keputusan final agar domain resmi tidak
# otomatis dianggap 100% aman jika model melihat pola tidak umum.

def gabungkan_skor_model_dan_intelligence(skor_model, sinyal_intelligence):
    skor_awal = float(skor_model)
    status = sinyal_intelligence.get("intelligence_status", "")

    if status == "resmi_terlihat_aman":
        if skor_awal >= 75:
            return 35
        if skor_awal >= 50:
            return 28
        return min(skor_awal, 20)

    if status == "resmi_perlu_tinjauan":
        return max(min(skor_awal, 60), 35)

    if status == "tiruan_brand_berisiko":
        return max(skor_awal, 85)

    if status == "domain_mirip_brand_berisiko":
        return max(skor_awal, 85)

    if status == "domain_mirip_brand":
        return max(skor_awal, 70)

    if status == "kata_mencurigakan_tinggi":
        return max(skor_awal, 75)

    if status == "punycode_perlu_tinjauan":
        return max(skor_awal, 65)

    if status == "domain_ip_perlu_tinjauan":
        return max(skor_awal, 65)

    if status == "brand_tidak_resmi_perlu_tinjauan":
        return max(skor_awal, 60)

    if status == "kata_mencurigakan_perlu_tinjauan":
        return max(skor_awal, 45)

    return skor_awal


def hasil_akhir_dari_skor(skor, status_intelligence):
    skor = float(skor)

    if status_intelligence == "resmi_terlihat_aman":
        if skor < 25:
            return "Terlihat Aman"
        return "Perlu Tinjauan"

    if status_intelligence == "resmi_perlu_tinjauan":
        return "Perlu Tinjauan"

    if status_intelligence in [
        "tiruan_brand_berisiko",
        "domain_mirip_brand_berisiko",
        "kata_mencurigakan_tinggi"
    ]:
        return "Berisiko"

    if status_intelligence in [
        "domain_mirip_brand",
        "punycode_perlu_tinjauan",
        "domain_ip_perlu_tinjauan",
        "brand_tidak_resmi_perlu_tinjauan",
        "kata_mencurigakan_perlu_tinjauan"
    ]:
        if skor >= 75:
            return "Berisiko"
        return "Perlu Tinjauan"

    if skor < 25:
        return "Terlihat Aman"

    if skor < 50:
        return "Perlu Tinjauan"

    return "Berisiko"


def buat_rekomendasi_url(hasil_akhir, kategori_risiko, status_intelligence):
    if status_intelligence == "resmi_terlihat_aman" and hasil_akhir == "Terlihat Aman":
        return "Alamat cocok dengan daftar domain resmi dan tidak menunjukkan sinyal kuat yang mencurigakan. Tetap pastikan alamat diketik langsung dari sumber resmi."

    if status_intelligence == "resmi_terlihat_aman" and hasil_akhir == "Perlu Tinjauan":
        return "Alamat cocok dengan daftar domain resmi, tetapi model melihat pola URL yang tidak umum. Jangan langsung dianggap phishing, namun tetap periksa sumber alamat dan pastikan berasal dari kanal resmi."

    if status_intelligence == "resmi_perlu_tinjauan":
        return "Alamat berada pada domain resmi, tetapi mengandung pola yang perlu diperiksa. Pastikan tidak ada path, parameter, atau redirect mencurigakan."

    if status_intelligence in ["tiruan_brand_berisiko", "domain_mirip_brand_berisiko", "domain_mirip_brand"]:
        return "Alamat terindikasi meniru brand atau domain resmi. Jangan digunakan untuk login, transaksi, atau memasukkan data pribadi."

    if hasil_akhir == "Terlihat Aman":
        return "Alamat terlihat aman berdasarkan model dan pemeriksaan intelligence. Tetap pastikan alamat berasal dari sumber tepercaya."

    if hasil_akhir == "Perlu Tinjauan":
        return "Alamat perlu diperiksa manual. Jangan langsung memasukkan kata sandi, OTP, data pribadi, atau informasi pembayaran."

    return "Alamat berisiko. Jangan dibuka, jangan diisi, dan laporkan jika berasal dari pesan mencurigakan."
