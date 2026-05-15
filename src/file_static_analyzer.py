
from pathlib import Path
import hashlib
import re
import zipfile
import pandas as pd

try:
    import url_intelligence
except Exception:
    url_intelligence = None


EKSTENSI_BERBAHAYA = {
    ".exe", ".msi", ".bat", ".cmd", ".ps1", ".vbs", ".js", ".jse",
    ".lnk", ".scr", ".com", ".pif", ".apk", ".jar", ".docm", ".xlsm"
}

EKSTENSI_DOKUMEN = {
    ".pdf", ".doc", ".docx", ".docm", ".xls", ".xlsx", ".xlsm",
    ".ppt", ".pptx", ".txt", ".html", ".htm", ".js"
}

IZIN_APK_BERISIKO = {
    "android.permission.READ_SMS",
    "android.permission.RECEIVE_SMS",
    "android.permission.SEND_SMS",
    "android.permission.READ_CONTACTS",
    "android.permission.WRITE_CONTACTS",
    "android.permission.CALL_PHONE",
    "android.permission.READ_PHONE_STATE",
    "android.permission.SYSTEM_ALERT_WINDOW",
    "android.permission.REQUEST_INSTALL_PACKAGES",
    "android.permission.BIND_ACCESSIBILITY_SERVICE",
    "android.permission.RECORD_AUDIO",
    "android.permission.CAMERA",
    "android.permission.ACCESS_FINE_LOCATION"
}

STATUS_URL_BERISIKO = {
    "tiruan_brand_berisiko",
    "domain_mirip_brand_berisiko",
    "domain_mirip_brand",
    "kata_mencurigakan_tinggi",
    "punycode_perlu_tinjauan",
    "domain_ip_perlu_tinjauan"
}


def baca_bytes_aman(lokasi_file, batas_mb=30):
    lokasi_file = Path(lokasi_file)
    ukuran_mb = lokasi_file.stat().st_size / (1024 * 1024)

    if ukuran_mb > batas_mb:
        raise ValueError(f"Ukuran file terlalu besar untuk analisis aman: {ukuran_mb:.2f} MB")

    return lokasi_file.read_bytes()


def buat_hash_sha256(data_bytes):
    return hashlib.sha256(data_bytes).hexdigest()


def decode_bytes(data_bytes):
    for encoding in ["utf-8", "latin-1", "cp1252"]:
        try:
            return data_bytes.decode(encoding, errors="ignore")
        except Exception:
            continue

    return data_bytes.decode("latin-1", errors="ignore")


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


def cek_ekstensi_ganda(nama_file):
    nama_file = str(nama_file).lower()
    bagian = [item for item in nama_file.split(".") if item]

    if len(bagian) < 3:
        return 0

    ekstensi_akhir = "." + bagian[-1]
    ekstensi_sebelumnya = "." + bagian[-2]

    if ekstensi_sebelumnya in EKSTENSI_DOKUMEN and ekstensi_akhir in EKSTENSI_BERBAHAYA:
        return 1

    return 0


def cek_magic_file(data_bytes):
    if data_bytes.startswith(b"%PDF"):
        return "pdf"

    if data_bytes.startswith(b"PK\x03\x04") or data_bytes.startswith(b"PK\x05\x06") or data_bytes.startswith(b"PK\x07\x08"):
        return "zip"

    if data_bytes.startswith(b"MZ"):
        return "exe"

    return "tidak_diketahui"


def muat_aturan_file(direktori_project):
    direktori_project = Path(direktori_project)
    lokasi_rules = direktori_project / "data" / "intelligence" / "suspicious_file_rules.csv"

    if not lokasi_rules.exists():
        return pd.DataFrame(columns=["ekstensi", "tingkat_risiko_awal", "keterangan"])

    data_rules = pd.read_csv(lokasi_rules)
    data_rules["ekstensi"] = data_rules["ekstensi"].astype(str).str.lower().str.strip()

    return data_rules


def ambil_risiko_awal(ekstensi, data_rules):
    ekstensi = str(ekstensi).lower().strip()
    cocok = data_rules[data_rules["ekstensi"] == ekstensi]

    if cocok.empty:
        return "tidak_diketahui", "Ekstensi belum memiliki aturan khusus"

    baris = cocok.iloc[0]
    return str(baris["tingkat_risiko_awal"]), str(baris["keterangan"])


def skor_dasar_dari_risiko(risiko_awal):
    peta_skor = {
        "rendah": 8,
        "sedang": 25,
        "tinggi": 50,
        "sangat_tinggi": 75,
        "tidak_diketahui": 20
    }

    return peta_skor.get(str(risiko_awal), 20)


def kategori_dari_skor(skor):
    if skor < 25:
        return "Rendah"

    if skor < 50:
        return "Sedang"

    if skor < 75:
        return "Tinggi"

    return "Sangat Tinggi"


def analisis_url_tertanam(daftar_url, direktori_project):
    if url_intelligence is None or len(daftar_url) == 0:
        return pd.DataFrame()

    data_domain_resmi, data_brand_keyword, data_suspicious_keyword = url_intelligence.muat_data_intelligence(
        direktori_project
    )

    return url_intelligence.analisis_banyak_url(
        daftar_url,
        data_domain_resmi,
        data_brand_keyword,
        data_suspicious_keyword
    )


def hitung_kata_mencurigakan_teks(teks, direktori_project):
    lokasi_keyword = Path(direktori_project) / "data" / "intelligence" / "suspicious_keywords_global.csv"

    if not lokasi_keyword.exists():
        return [], 0

    data_keyword = pd.read_csv(lokasi_keyword)
    teks_lower = str(teks).lower()

    daftar_kata = []
    total_bobot = 0

    for _, baris in data_keyword.iterrows():
        keyword = str(baris["keyword"]).lower().strip()
        bobot = int(baris["bobot"])

        if keyword in teks_lower:
            daftar_kata.append(keyword)
            total_bobot += bobot

    return sorted(set(daftar_kata)), total_bobot


def analisis_pdf(data_bytes):
    teks = decode_bytes(data_bytes)

    indikator = {
        "pdf_javascript": int("/JavaScript" in teks or "/JS" in teks),
        "pdf_open_action": int("/OpenAction" in teks or "/AA" in teks),
        "pdf_launch_action": int("/Launch" in teks),
        "pdf_embedded_file": int("/EmbeddedFile" in teks or "/Filespec" in teks)
    }

    return indikator, teks


def analisis_zip_atau_office(lokasi_file):
    lokasi_file = Path(lokasi_file)

    hasil = {
        "jumlah_file_dalam_arsip": 0,
        "file_berbahaya_dalam_arsip": [],
        "memiliki_macro_indicator": 0,
        "memiliki_embedded_object": 0,
        "teks_arsip": ""
    }

    try:
        with zipfile.ZipFile(lokasi_file, "r") as arsip:
            daftar_nama = arsip.namelist()
            hasil["jumlah_file_dalam_arsip"] = len(daftar_nama)

            teks_gabungan = []

            for nama in daftar_nama:
                nama_lower = nama.lower()
                suffix = Path(nama_lower).suffix

                if suffix in EKSTENSI_BERBAHAYA or cek_ekstensi_ganda(nama_lower):
                    hasil["file_berbahaya_dalam_arsip"].append(nama)

                if "vbaproject.bin" in nama_lower:
                    hasil["memiliki_macro_indicator"] = 1

                if "embeddings/" in nama_lower or "oleobject" in nama_lower:
                    hasil["memiliki_embedded_object"] = 1

                boleh_baca = (
                    suffix in [".xml", ".rels", ".txt", ".html", ".htm", ".js", ".json", ".smali"]
                    or nama_lower.endswith("androidmanifest.xml")
                )

                if boleh_baca:
                    info = arsip.getinfo(nama)

                    if info.file_size <= 2_000_000:
                        try:
                            isi = arsip.read(nama)
                            teks_gabungan.append(decode_bytes(isi))
                        except Exception:
                            pass

            hasil["teks_arsip"] = "\n".join(teks_gabungan)

    except zipfile.BadZipFile:
        pass

    return hasil


def analisis_apk(lokasi_file):
    hasil_zip = analisis_zip_atau_office(lokasi_file)
    teks = hasil_zip.get("teks_arsip", "")

    daftar_izin = sorted(set(re.findall(r"android\.permission\.[A-Z_]+", teks)))
    izin_berisiko = sorted(set([izin for izin in daftar_izin if izin in IZIN_APK_BERISIKO]))

    return {
        "jumlah_permission_apk": len(daftar_izin),
        "izin_apk_berisiko": izin_berisiko,
        "jumlah_izin_apk_berisiko": len(izin_berisiko),
        "teks_apk": teks,
        "hasil_zip": hasil_zip
    }


def buat_alasan_file(hasil):
    alasan = []

    if hasil["ekstensi_ganda"] == 1:
        alasan.append("Nama file memakai ekstensi ganda yang sering dipakai untuk menyamarkan file.")

    if hasil["magic_mismatch"] == 1:
        alasan.append("Tipe isi file tidak sesuai dengan ekstensi file.")

    if hasil["jumlah_url"] > 0:
        alasan.append("File mengandung URL.")

    if hasil["jumlah_url_berisiko_intelligence"] > 0:
        alasan.append("Ada URL di dalam file yang terdeteksi berisiko oleh URL Intelligence.")

    if hasil["jumlah_kata_mencurigakan"] > 0:
        alasan.append("File mengandung kata yang sering muncul pada penipuan.")

    if hasil["memiliki_macro_indicator"] == 1:
        alasan.append("File memiliki indikator macro.")

    if hasil["memiliki_embedded_object"] == 1:
        alasan.append("File memiliki objek tertanam.")

    if hasil["pdf_javascript"] == 1:
        alasan.append("PDF mengandung indikator JavaScript.")

    if hasil["pdf_open_action"] == 1 or hasil["pdf_launch_action"] == 1:
        alasan.append("PDF memiliki aksi otomatis yang perlu diperiksa.")

    if hasil["pdf_embedded_file"] == 1:
        alasan.append("PDF memiliki indikator lampiran tertanam.")

    if hasil["jumlah_file_berbahaya_dalam_arsip"] > 0:
        alasan.append("Arsip berisi file dengan ekstensi berisiko.")

    if hasil["jumlah_izin_apk_berisiko"] > 0:
        alasan.append("APK meminta izin yang sensitif atau berisiko.")

    if not alasan:
        alasan.append("Belum ditemukan indikator risiko kuat dari analisis statis.")

    return " ".join(alasan)


def buat_rekomendasi_file(kategori):
    if kategori == "Rendah":
        return "File terlihat rendah risiko berdasarkan pemeriksaan statis. Tetap buka hanya jika sumbernya tepercaya."

    if kategori == "Sedang":
        return "File perlu diperiksa lebih lanjut sebelum dibuka, terutama jika berasal dari pesan atau email tidak dikenal."

    if kategori == "Tinggi":
        return "Jangan langsung membuka file. Periksa sumber, URL di dalamnya, dan pindai dengan keamanan tambahan."

    return "File sangat berisiko. Jangan dibuka atau dijalankan sebelum dianalisis di lingkungan aman."


def analisis_file_statis(lokasi_file, direktori_project):
    lokasi_file = Path(lokasi_file)
    data_rules = muat_aturan_file(direktori_project)

    data_bytes = baca_bytes_aman(lokasi_file)
    teks_awal = decode_bytes(data_bytes[:5_000_000])

    ekstensi = lokasi_file.suffix.lower()
    risiko_awal, keterangan_risiko_awal = ambil_risiko_awal(ekstensi, data_rules)

    magic_file = cek_magic_file(data_bytes)

    magic_mismatch = 0

    if ekstensi == ".pdf" and magic_file != "pdf":
        magic_mismatch = 1
    elif ekstensi in [".docx", ".xlsx", ".pptx", ".docm", ".xlsm", ".zip", ".apk"] and magic_file != "zip":
        magic_mismatch = 1
    elif ekstensi == ".exe" and magic_file != "exe":
        magic_mismatch = 1

    daftar_url = ekstrak_url_dari_teks(teks_awal)
    kata_mencurigakan, skor_kata_mencurigakan = hitung_kata_mencurigakan_teks(teks_awal, direktori_project)

    hasil_url = analisis_url_tertanam(daftar_url, direktori_project)
    jumlah_url_berisiko = 0

    if not hasil_url.empty and "intelligence_status" in hasil_url.columns:
        jumlah_url_berisiko = int(hasil_url["intelligence_status"].isin(STATUS_URL_BERISIKO).sum())

    indikator_pdf = {
        "pdf_javascript": 0,
        "pdf_open_action": 0,
        "pdf_launch_action": 0,
        "pdf_embedded_file": 0
    }

    hasil_zip = {
        "jumlah_file_dalam_arsip": 0,
        "file_berbahaya_dalam_arsip": [],
        "memiliki_macro_indicator": 0,
        "memiliki_embedded_object": 0,
        "teks_arsip": ""
    }

    hasil_apk = {
        "jumlah_permission_apk": 0,
        "izin_apk_berisiko": [],
        "jumlah_izin_apk_berisiko": 0,
        "teks_apk": "",
        "hasil_zip": hasil_zip
    }

    teks_tambahan = ""

    if ekstensi == ".pdf":
        indikator_pdf, teks_pdf = analisis_pdf(data_bytes)
        teks_tambahan += "\n" + teks_pdf[:2_000_000]

    if ekstensi in [".docx", ".xlsx", ".pptx", ".docm", ".xlsm", ".zip"]:
        hasil_zip = analisis_zip_atau_office(lokasi_file)
        teks_tambahan += "\n" + hasil_zip.get("teks_arsip", "")

    if ekstensi == ".apk":
        hasil_apk = analisis_apk(lokasi_file)
        hasil_zip = hasil_apk["hasil_zip"]
        teks_tambahan += "\n" + hasil_apk.get("teks_apk", "")

    if teks_tambahan:
        daftar_url_tambahan = ekstrak_url_dari_teks(teks_tambahan)
        semua_url = list(dict.fromkeys(daftar_url + daftar_url_tambahan))

        kata_tambahan, skor_tambahan = hitung_kata_mencurigakan_teks(teks_tambahan, direktori_project)
        kata_mencurigakan = sorted(set(kata_mencurigakan + kata_tambahan))
        skor_kata_mencurigakan += skor_tambahan

        hasil_url = analisis_url_tertanam(semua_url, direktori_project)
        daftar_url = semua_url

        if not hasil_url.empty and "intelligence_status" in hasil_url.columns:
            jumlah_url_berisiko = int(hasil_url["intelligence_status"].isin(STATUS_URL_BERISIKO).sum())

    skor = skor_dasar_dari_risiko(risiko_awal)
    skor += min(len(daftar_url) * 4, 20)
    skor += min(jumlah_url_berisiko * 15, 45)
    skor += min(skor_kata_mencurigakan * 2, 30)
    skor += 20 if cek_ekstensi_ganda(lokasi_file.name) else 0
    skor += 20 if magic_mismatch else 0
    skor += 25 if hasil_zip["memiliki_macro_indicator"] else 0
    skor += 15 if hasil_zip["memiliki_embedded_object"] else 0
    skor += 20 if indikator_pdf["pdf_javascript"] else 0
    skor += 20 if indikator_pdf["pdf_open_action"] or indikator_pdf["pdf_launch_action"] else 0
    skor += 15 if indikator_pdf["pdf_embedded_file"] else 0
    skor += min(len(hasil_zip["file_berbahaya_dalam_arsip"]) * 15, 45)
    skor += min(hasil_apk["jumlah_izin_apk_berisiko"] * 10, 40)

    skor = int(max(0, min(100, skor)))
    kategori = kategori_dari_skor(skor)

    hasil = {
        "nama_file": lokasi_file.name,
        "lokasi_file": str(lokasi_file),
        "ekstensi": ekstensi if ekstensi else "tanpa_ekstensi",
        "ukuran_kb": round(lokasi_file.stat().st_size / 1024, 2),
        "sha256": buat_hash_sha256(data_bytes),
        "magic_file": magic_file,
        "magic_mismatch": magic_mismatch,
        "risiko_awal_file": risiko_awal,
        "keterangan_risiko_awal": keterangan_risiko_awal,
        "ekstensi_ganda": cek_ekstensi_ganda(lokasi_file.name),
        "jumlah_url": len(daftar_url),
        "url_terdeteksi": " | ".join(daftar_url[:20]),
        "jumlah_url_berisiko_intelligence": jumlah_url_berisiko,
        "jumlah_kata_mencurigakan": len(kata_mencurigakan),
        "kata_mencurigakan": ", ".join(kata_mencurigakan),
        "skor_kata_mencurigakan": skor_kata_mencurigakan,
        "jumlah_file_dalam_arsip": hasil_zip["jumlah_file_dalam_arsip"],
        "jumlah_file_berbahaya_dalam_arsip": len(hasil_zip["file_berbahaya_dalam_arsip"]),
        "file_berbahaya_dalam_arsip": " | ".join(hasil_zip["file_berbahaya_dalam_arsip"][:20]),
        "memiliki_macro_indicator": hasil_zip["memiliki_macro_indicator"],
        "memiliki_embedded_object": hasil_zip["memiliki_embedded_object"],
        "pdf_javascript": indikator_pdf["pdf_javascript"],
        "pdf_open_action": indikator_pdf["pdf_open_action"],
        "pdf_launch_action": indikator_pdf["pdf_launch_action"],
        "pdf_embedded_file": indikator_pdf["pdf_embedded_file"],
        "jumlah_permission_apk": hasil_apk["jumlah_permission_apk"],
        "jumlah_izin_apk_berisiko": hasil_apk["jumlah_izin_apk_berisiko"],
        "izin_apk_berisiko": ", ".join(hasil_apk["izin_apk_berisiko"]),
        "skor_risiko_file": skor,
        "kategori_risiko_file": kategori
    }

    hasil["alasan_file"] = buat_alasan_file(hasil)
    hasil["rekomendasi_file"] = buat_rekomendasi_file(kategori)

    return hasil, hasil_url


def analisis_banyak_file(daftar_lokasi_file, direktori_project):
    hasil_file = []
    hasil_url_semua = []

    for lokasi_file in daftar_lokasi_file:
        hasil, hasil_url = analisis_file_statis(lokasi_file, direktori_project)
        hasil_file.append(hasil)

        if not hasil_url.empty:
            hasil_url = hasil_url.copy()
            hasil_url.insert(0, "nama_file_sumber", Path(lokasi_file).name)
            hasil_url_semua.append(hasil_url)

    data_hasil_file = pd.DataFrame(hasil_file)

    if hasil_url_semua:
        data_hasil_url = pd.concat(hasil_url_semua, ignore_index=True)
    else:
        data_hasil_url = pd.DataFrame()

    return data_hasil_file, data_hasil_url


# URL Cleaner V3.1
# Dokumentasi: membersihkan URL hasil ekstraksi dari teks/binary.

def bersihkan_url_terekstrak(url):
    url = str(url).strip()
    url = url.replace("\\x00", "")
    url = url.replace("\x00", "")

    pemotong = [
        "PK\x03\x04",
        "PK\\x03\\x04",
        "%%EOF",
        "<",
        ">",
        "\"",
        "'",
        "\\",
        "{",
        "}",
        "[",
        "]"
    ]

    for token in pemotong:
        if token in url:
            url = url.split(token)[0]

    pola_valid = r"^(https?://[a-zA-Z0-9\-._~:/?#\[\]@!$&()*+,;=%]+)"
    cocok = re.match(pola_valid, url)

    if cocok:
        url = cocok.group(1)

    url = url.rstrip(".,;:)")
    return url


def ekstrak_url_dari_teks(teks):
    teks = str(teks)
    pola_url = r"https?://[^\s<>'\"\\)\]\}]+"
    daftar_url = re.findall(pola_url, teks, flags=re.IGNORECASE)

    daftar_bersih = []

    for url in daftar_url:
        url_bersih = bersihkan_url_terekstrak(url)

        if not url_bersih:
            continue

        if "PK" in url_bersih[-6:]:
            url_bersih = url_bersih.split("PK")[0].rstrip(".,;:")

        if url_bersih not in daftar_bersih:
            daftar_bersih.append(url_bersih)

    return daftar_bersih
