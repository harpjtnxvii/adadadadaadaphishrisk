
from pathlib import Path
from urllib.parse import urlparse
from difflib import SequenceMatcher
import re
import pandas as pd


DAFTAR_AKHIRAN_DOMAIN_KHUSUS = [
    "co.id", "ac.id", "go.id", "or.id", "sch.id", "web.id", "my.id",
    "com.sg", "edu.sg", "gov.sg",
    "com.my", "edu.my", "gov.my",
    "co.th", "ac.th", "go.th",
    "co.uk", "ac.uk", "gov.uk",
    "com.au", "edu.au", "gov.au",
    "co.jp", "ac.jp", "go.jp"
]


def ambil_domain_dari_url(url):
    url = str(url).strip()

    if not url:
        return ""

    hasil_parse = urlparse(url)

    if hasil_parse.netloc:
        return hasil_parse.netloc.lower().split("@")[-1].split(":")[0]

    hasil_parse = urlparse("http://" + url)
    return hasil_parse.netloc.lower().split("@")[-1].split(":")[0]


def bersihkan_domain(domain):
    domain = str(domain).lower().strip()
    domain = domain.replace("http://", "").replace("https://", "")
    domain = domain.split("/")[0]
    domain = domain.split("@")[-1]
    domain = domain.split(":")[0]

    if domain.startswith("www."):
        domain = domain[4:]

    return domain


def ambil_akar_domain(domain):
    domain = bersihkan_domain(domain)
    bagian = [item for item in domain.split(".") if item]

    if len(bagian) <= 2:
        return domain

    for akhiran in DAFTAR_AKHIRAN_DOMAIN_KHUSUS:
        if domain.endswith("." + akhiran) and len(bagian) >= 3:
            return ".".join(bagian[-3:])

    return ".".join(bagian[-2:])


def ambil_label_domain_utama(domain):
    akar_domain = ambil_akar_domain(domain)
    bagian = [item for item in akar_domain.split(".") if item]

    if not bagian:
        return ""

    return bagian[0]


def ambil_teks_domain_tanpa_tld(domain):
    domain = bersihkan_domain(domain)
    bagian = [item for item in domain.split(".") if item]

    if len(bagian) <= 1:
        return domain

    return ".".join(bagian[:-1])


def pecah_token_domain(domain):
    domain = bersihkan_domain(domain)
    teks_tanpa_tld = ambil_teks_domain_tanpa_tld(domain)

    token = re.split(r"[^a-zA-Z0-9]+", teks_tanpa_tld)
    token = [item.lower().strip() for item in token if item.strip()]

    return token


def cek_domain_ip(domain):
    domain = bersihkan_domain(domain)
    pola_ip = r"^\d{1,3}(\.\d{1,3}){3}$"

    return int(bool(re.match(pola_ip, domain)))


def cek_punycode(domain):
    domain = bersihkan_domain(domain)

    return int("xn--" in domain)


def normalisasi_pengganti_angka(teks):
    teks = str(teks).lower()

    peta_utama = {
        "0": "o",
        "1": "i",
        "3": "e",
        "4": "a",
        "5": "s",
        "7": "t",
        "8": "b"
    }

    hasil = teks

    for angka, huruf in peta_utama.items():
        hasil = hasil.replace(angka, huruf)

    return hasil


def variasi_normalisasi_pengganti_angka(teks):
    teks = str(teks).lower()

    peta_utama = {
        "0": "o",
        "1": "i",
        "3": "e",
        "4": "a",
        "5": "s",
        "7": "t",
        "8": "b"
    }

    peta_alternatif = {
        "0": "o",
        "1": "l",
        "3": "e",
        "4": "a",
        "5": "s",
        "7": "t",
        "8": "b"
    }

    hasil_utama = teks
    hasil_alternatif = teks

    for angka, huruf in peta_utama.items():
        hasil_utama = hasil_utama.replace(angka, huruf)

    for angka, huruf in peta_alternatif.items():
        hasil_alternatif = hasil_alternatif.replace(angka, huruf)

    return list(set([teks, hasil_utama, hasil_alternatif]))


def cek_pengganti_angka(teks):
    teks = str(teks).lower()

    daftar_angka_pengganti = ["0", "1", "3", "4", "5", "7", "8"]
    jumlah = sum(teks.count(angka) for angka in daftar_angka_pengganti)

    return int(jumlah > 0), jumlah


def hitung_tanda_hubung(domain):
    domain = bersihkan_domain(domain)

    return domain.count("-")


def hitung_kemiripan(teks_1, teks_2):
    teks_1 = str(teks_1).lower().strip()
    teks_2 = str(teks_2).lower().strip()

    if not teks_1 or not teks_2:
        return 0.0

    return SequenceMatcher(None, teks_1, teks_2).ratio()


def muat_data_intelligence(direktori_project):
    direktori_project = Path(direktori_project)
    direktori_intelligence = direktori_project / "data" / "intelligence"

    lokasi_domain_resmi = direktori_intelligence / "official_domains_global.csv"
    lokasi_brand_keyword = direktori_intelligence / "brand_keywords_global.csv"
    lokasi_suspicious_keyword = direktori_intelligence / "suspicious_keywords_global.csv"

    data_domain_resmi = pd.read_csv(lokasi_domain_resmi)
    data_brand_keyword = pd.read_csv(lokasi_brand_keyword)
    data_suspicious_keyword = pd.read_csv(lokasi_suspicious_keyword)

    data_domain_resmi["domain_bersih"] = data_domain_resmi["domain"].astype(str).apply(bersihkan_domain)
    data_domain_resmi["akar_domain"] = data_domain_resmi["domain_bersih"].apply(ambil_akar_domain)

    data_brand_keyword["keyword"] = data_brand_keyword["keyword"].astype(str).str.lower().str.strip()
    data_suspicious_keyword["keyword"] = data_suspicious_keyword["keyword"].astype(str).str.lower().str.strip()

    return data_domain_resmi, data_brand_keyword, data_suspicious_keyword


def cek_domain_resmi(domain, data_domain_resmi):
    domain_bersih = bersihkan_domain(domain)
    akar_domain = ambil_akar_domain(domain_bersih)

    hasil = {
        "is_official_domain": 0,
        "official_match_type": "tidak_cocok",
        "official_domain": "",
        "official_brand": "",
        "official_category": "",
        "official_region": "",
        "official_country": "",
        "official_confidence": ""
    }

    for _, baris in data_domain_resmi.iterrows():
        domain_resmi = str(baris["domain_bersih"]).lower().strip()
        akar_resmi = str(baris["akar_domain"]).lower().strip()

        cocok_penuh = domain_bersih == domain_resmi
        cocok_subdomain = domain_bersih.endswith("." + domain_resmi)
        cocok_akar = akar_domain == akar_resmi

        if cocok_penuh or cocok_subdomain or cocok_akar:
            hasil["is_official_domain"] = 1
            hasil["official_match_type"] = "domain_penuh" if cocok_penuh else "subdomain_atau_akar"
            hasil["official_domain"] = domain_resmi
            hasil["official_brand"] = str(baris["brand"])
            hasil["official_category"] = str(baris["kategori"])
            hasil["official_region"] = str(baris["wilayah"])
            hasil["official_country"] = str(baris["negara"])
            hasil["official_confidence"] = str(baris["tingkat_kepercayaan"])
            return hasil

    return hasil


def cek_brand_keyword(url, domain, data_brand_keyword):
    teks_asli = f"{url} {domain}".lower()
    teks_normal = normalisasi_pengganti_angka(teks_asli)

    daftar_brand = []

    for _, baris in data_brand_keyword.iterrows():
        keyword = str(baris["keyword"]).lower().strip()

        if len(keyword) <= 2:
            pola = r"(^|[^a-z0-9])" + re.escape(keyword) + r"([^a-z0-9]|$)"
            cocok = bool(re.search(pola, teks_asli)) or bool(re.search(pola, teks_normal))
        else:
            cocok = keyword in teks_asli or keyword in teks_normal

        if cocok:
            daftar_brand.append({
                "keyword": keyword,
                "brand": str(baris["brand"]),
                "kategori": str(baris["kategori"]),
                "wilayah": str(baris["wilayah"])
            })

    return daftar_brand


def cek_kata_mencurigakan(url, data_suspicious_keyword):
    teks_asli = str(url).lower()
    teks_normal = normalisasi_pengganti_angka(teks_asli)

    daftar_kata = []
    total_bobot = 0

    for _, baris in data_suspicious_keyword.iterrows():
        keyword = str(baris["keyword"]).lower().strip()
        bobot = int(baris["bobot"])

        pola = r"(^|[^a-z0-9])" + re.escape(keyword) + r"([^a-z0-9]|$)"

        cocok_dengan_batas = bool(re.search(pola, teks_asli)) or bool(re.search(pola, teks_normal))
        cocok_dalam_teks = keyword in teks_asli or keyword in teks_normal

        if cocok_dengan_batas or cocok_dalam_teks:
            daftar_kata.append(keyword)
            total_bobot += bobot

    daftar_kata = sorted(set(daftar_kata))

    return daftar_kata, total_bobot


def cek_domain_mirip_brand(domain, data_brand_keyword, ambang_kemiripan=0.82):
    domain_bersih = bersihkan_domain(domain)
    token_domain = pecah_token_domain(domain_bersih)

    kandidat = set()

    for token in token_domain:
        for variasi in variasi_normalisasi_pengganti_angka(token):
            kandidat.add(variasi)

    gabungan_token = "".join(token_domain)

    for variasi in variasi_normalisasi_pengganti_angka(gabungan_token):
        kandidat.add(variasi)

    label_utama = ambil_label_domain_utama(domain_bersih)

    for variasi in variasi_normalisasi_pengganti_angka(label_utama):
        kandidat.add(variasi)

    hasil_terbaik = {
        "lookalike_brand_detected": 0,
        "lookalike_brand": "",
        "lookalike_keyword": "",
        "lookalike_score": 0.0
    }

    for _, baris in data_brand_keyword.iterrows():
        keyword = str(baris["keyword"]).lower().strip()

        if len(keyword) < 3:
            continue

        for item in kandidat:
            if not item:
                continue

            skor = hitung_kemiripan(item, keyword)

            if skor > hasil_terbaik["lookalike_score"]:
                hasil_terbaik["lookalike_score"] = round(float(skor), 4)
                hasil_terbaik["lookalike_brand"] = str(baris["brand"])
                hasil_terbaik["lookalike_keyword"] = keyword

    if hasil_terbaik["lookalike_score"] >= ambang_kemiripan:
        hasil_terbaik["lookalike_brand_detected"] = 1
    else:
        hasil_terbaik["lookalike_brand"] = ""
        hasil_terbaik["lookalike_keyword"] = ""

    return hasil_terbaik


def buat_status_intelligence(sinyal):
    if sinyal["is_official_domain"] == 1 and sinyal["suspicious_keyword_score"] == 0:
        return "resmi_terlihat_aman"

    if sinyal["is_official_domain"] == 1 and sinyal["suspicious_keyword_score"] > 0:
        return "resmi_perlu_tinjauan"

    if sinyal["brand_but_not_official"] == 1 and sinyal["suspicious_keyword_score"] > 0:
        return "tiruan_brand_berisiko"

    if sinyal["brand_but_not_official"] == 1 and sinyal["lookalike_brand_detected"] == 1:
        return "tiruan_brand_berisiko"

    if sinyal["lookalike_brand_detected"] == 1 and sinyal["uses_digit_substitution"] == 1:
        return "domain_mirip_brand_berisiko"

    if sinyal["lookalike_brand_detected"] == 1 and sinyal["uses_punycode"] == 1:
        return "domain_mirip_brand_berisiko"

    if sinyal["lookalike_brand_detected"] == 1:
        return "domain_mirip_brand"

    if sinyal["brand_but_not_official"] == 1:
        return "brand_tidak_resmi_perlu_tinjauan"

    if sinyal["suspicious_keyword_score"] >= 5:
        return "kata_mencurigakan_tinggi"

    if sinyal["suspicious_keyword_score"] > 0:
        return "kata_mencurigakan_perlu_tinjauan"

    if sinyal["uses_punycode"] == 1:
        return "punycode_perlu_tinjauan"

    if sinyal["is_domain_ip"] == 1:
        return "domain_ip_perlu_tinjauan"

    return "belum_ada_sinyal_kuat"


def buat_ringkasan_alasan(sinyal):
    alasan = []

    if sinyal["is_official_domain"] == 1:
        alasan.append("Domain cocok dengan daftar domain resmi.")

    if sinyal["brand_but_not_official"] == 1:
        alasan.append("URL mengandung nama brand, tetapi tidak berada pada domain resmi.")

    if sinyal["lookalike_brand_detected"] == 1:
        alasan.append("Domain terlihat mirip dengan brand resmi.")

    if sinyal["suspicious_keyword_score"] > 0:
        alasan.append("URL mengandung kata yang sering muncul pada tautan penipuan.")

    if sinyal["uses_punycode"] == 1:
        alasan.append("Domain menggunakan pola punycode yang perlu diperiksa.")

    if sinyal["uses_digit_substitution"] == 1:
        alasan.append("Domain menggunakan angka yang menyerupai huruf.")

    if sinyal["hyphen_count"] >= 2:
        alasan.append("Domain memiliki banyak tanda hubung.")

    if sinyal["is_domain_ip"] == 1:
        alasan.append("Domain menggunakan alamat IP.")

    if not alasan:
        alasan.append("Belum ditemukan sinyal risiko kuat dari intelligence rule.")

    return " ".join(alasan)


def analisis_url_intelligence(url, data_domain_resmi, data_brand_keyword, data_suspicious_keyword):
    url = str(url).strip()
    domain = ambil_domain_dari_url(url)
    domain_bersih = bersihkan_domain(domain)
    akar_domain = ambil_akar_domain(domain_bersih)

    hasil_resmi = cek_domain_resmi(domain_bersih, data_domain_resmi)
    daftar_brand = cek_brand_keyword(url, domain_bersih, data_brand_keyword)
    daftar_kata_mencurigakan, skor_kata_mencurigakan = cek_kata_mencurigakan(url, data_suspicious_keyword)
    hasil_lookalike = cek_domain_mirip_brand(domain_bersih, data_brand_keyword)

    brand_terdeteksi = len(daftar_brand) > 0
    brand_but_not_official = int(brand_terdeteksi and hasil_resmi["is_official_domain"] == 0)

    uses_digit_substitution, jumlah_pengganti_angka = cek_pengganti_angka(domain_bersih)

    if hasil_resmi["is_official_domain"] == 1:
        hasil_lookalike["lookalike_brand_detected"] = 0
        hasil_lookalike["lookalike_brand"] = ""
        hasil_lookalike["lookalike_keyword"] = ""
        hasil_lookalike["lookalike_score"] = 0.0

    sinyal = {
        "url": url,
        "domain": domain_bersih,
        "root_domain": akar_domain,
        "is_domain_ip": cek_domain_ip(domain_bersih),
        "is_official_domain": hasil_resmi["is_official_domain"],
        "official_match_type": hasil_resmi["official_match_type"],
        "official_domain": hasil_resmi["official_domain"],
        "official_brand": hasil_resmi["official_brand"],
        "official_category": hasil_resmi["official_category"],
        "official_region": hasil_resmi["official_region"],
        "official_country": hasil_resmi["official_country"],
        "official_confidence": hasil_resmi["official_confidence"],
        "brand_keyword_detected": int(brand_terdeteksi),
        "brand_detected": ", ".join(sorted(set([item["brand"] for item in daftar_brand]))),
        "brand_but_not_official": brand_but_not_official,
        "suspicious_keywords": ", ".join(daftar_kata_mencurigakan),
        "suspicious_keyword_count": len(daftar_kata_mencurigakan),
        "suspicious_keyword_score": skor_kata_mencurigakan,
        "lookalike_brand_detected": hasil_lookalike["lookalike_brand_detected"],
        "lookalike_brand": hasil_lookalike["lookalike_brand"],
        "lookalike_keyword": hasil_lookalike["lookalike_keyword"],
        "lookalike_score": hasil_lookalike["lookalike_score"],
        "uses_punycode": cek_punycode(domain_bersih),
        "uses_digit_substitution": uses_digit_substitution,
        "digit_substitution_count": jumlah_pengganti_angka,
        "hyphen_count": hitung_tanda_hubung(domain_bersih)
    }

    sinyal["intelligence_status"] = buat_status_intelligence(sinyal)
    sinyal["intelligence_reason"] = buat_ringkasan_alasan(sinyal)

    return sinyal


def analisis_banyak_url(daftar_url, data_domain_resmi, data_brand_keyword, data_suspicious_keyword):
    hasil = []

    for url in daftar_url:
        hasil.append(
            analisis_url_intelligence(
                url,
                data_domain_resmi,
                data_brand_keyword,
                data_suspicious_keyword
            )
        )

    return pd.DataFrame(hasil)
