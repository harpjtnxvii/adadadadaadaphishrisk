from __future__ import annotations

import re
from typing import Any, Dict, Iterable, Tuple


KATA_BERBAHAYA = [
    "buat phishing",
    "membuat phishing",
    "phishing kit",
    "clone login",
    "curi password",
    "steal password",
    "credential theft",
    "ambil kredensial",
    "bypass antivirus",
    "evade antivirus",
    "payload malware",
    "buat malware",
    "trojan",
    "ransomware",
    "keylogger",
    "exploit",
    "sql injection",
    "bruteforce",
    "brute force",
    "ddos",
    "menyerang",
    "hack akun",
    "ambil cookie",
    "session hijacking",
    "backdoor",
]


KATA_AMAN = [
    "deteksi",
    "analisis",
    "edukasi",
    "rekomendasi",
    "laporan",
    "defensif",
    "pencegahan",
    "antisipasi",
    "periksa",
    "jelaskan",
]


def bersihkan_teks(teks: Any, batas_karakter: int = 4000) -> str:
    """Membersihkan teks agar aman dipakai sebagai konteks AI."""
    if teks is None:
        return ""

    teks_bersih = str(teks)
    teks_bersih = teks_bersih.replace("\x00", " ")
    teks_bersih = re.sub(r"\s+", " ", teks_bersih).strip()

    if len(teks_bersih) > batas_karakter:
        teks_bersih = teks_bersih[:batas_karakter] + "..."

    return teks_bersih


def deteksi_permintaan_berbahaya(teks: Any) -> Tuple[bool, str]:
    """Mendeteksi permintaan yang mengarah ke penyalahgunaan."""
    teks_bersih = bersihkan_teks(teks, batas_karakter=2000).lower()

    for kata in KATA_BERBAHAYA:
        if kata in teks_bersih:
            return True, f"Permintaan mengandung pola berisiko: {kata}"

    return False, ""


def format_nilai_ringkas(nilai: Any) -> str:
    """Mengubah nilai menjadi teks pendek."""
    if nilai is None:
        return ""

    if isinstance(nilai, float):
        return f"{nilai:.2f}"

    return bersihkan_teks(nilai, batas_karakter=500)


def amankan_konteks_dict(data: Dict[str, Any], kolom_dipakai: Iterable[str] | None = None) -> Dict[str, str]:
    """Mengambil kolom penting dari dictionary hasil engine."""
    if data is None:
        return {}

    if kolom_dipakai is None:
        kolom_dipakai = data.keys()

    hasil: Dict[str, str] = {}

    for kolom in kolom_dipakai:
        if kolom in data:
            hasil[kolom] = format_nilai_ringkas(data.get(kolom))

    return hasil


def potong_daftar_teks(daftar_teks: Iterable[Any], batas_item: int = 20, batas_karakter_item: int = 400) -> list[str]:
    """Membatasi jumlah item agar konteks tetap ringan."""
    hasil = []

    for item in list(daftar_teks)[:batas_item]:
        hasil.append(bersihkan_teks(item, batas_karakter=batas_karakter_item))

    return hasil