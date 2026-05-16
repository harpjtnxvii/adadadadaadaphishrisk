from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd


def _hitung_kolom(data: pd.DataFrame, nama_kolom: str) -> Dict[str, int]:
    if data is None or data.empty or nama_kolom not in data.columns:
        return {}

    return data[nama_kolom].value_counts().to_dict()


def _format_dict(data: Dict[str, Any]) -> str:
    if not data:
        return "- Tidak ada data."

    baris = []
    for kunci, nilai in data.items():
        baris.append(f"- {kunci}: {nilai}")

    return "\n".join(baris)


def buat_laporan_url_markdown(
    data_url: pd.DataFrame,
    ringkasan_ai: Optional[Dict[str, str]] = None,
    judul: str = "Laporan Pemeriksaan URL PhishRisk",
) -> str:
    """Membuat laporan URL dalam format Markdown."""
    total = 0 if data_url is None else len(data_url)
    hasil = _hitung_kolom(data_url, "hasil_akhir")
    kategori = _hitung_kolom(data_url, "kategori_risiko")
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    bagian_ai = ""
    if ringkasan_ai:
        bagian_ai = f"""
## Ringkasan Cerdas

{ringkasan_ai.get("ringkasan", "-")}

## Rekomendasi

{ringkasan_ai.get("rekomendasi", "-")}
""".strip()

    laporan = f"""
# {judul}

Waktu laporan: {waktu}

## Ringkasan Data

- Jumlah URL diperiksa: {total}

## Hasil Akhir

{_format_dict(hasil)}

## Kategori Risiko

{_format_dict(kategori)}

{bagian_ai}

## Catatan Keamanan

Hasil ini adalah bantuan awal. Jangan gunakan hasil model sebagai satu-satunya keputusan keamanan. 
Untuk URL yang masuk kategori Tinggi atau Sangat Tinggi, jangan login, jangan isi data pribadi, dan cek domain resmi dari sumber tepercaya.
""".strip()

    return laporan


def buat_laporan_file_markdown(
    data_file: pd.DataFrame,
    data_url_dalam_file: Optional[pd.DataFrame] = None,
    ringkasan_ai: Optional[Dict[str, str]] = None,
    judul: str = "Laporan Pemeriksaan File PhishRisk",
) -> str:
    """Membuat laporan file dalam format Markdown."""
    total_file = 0 if data_file is None else len(data_file)
    total_url = 0 if data_url_dalam_file is None else len(data_url_dalam_file)
    hasil_file = _hitung_kolom(data_file, "hasil_akhir_file_v3")
    kategori_file = _hitung_kolom(data_file, "kategori_final_file_v3")
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    bagian_ai = ""
    if ringkasan_ai:
        bagian_ai = f"""
## Ringkasan Cerdas

{ringkasan_ai.get("ringkasan", "-")}

## Rekomendasi

{ringkasan_ai.get("rekomendasi", "-")}
""".strip()

    laporan = f"""
# {judul}

Waktu laporan: {waktu}

## Ringkasan Data

- Jumlah file diperiksa: {total_file}
- Jumlah URL ditemukan di dalam file: {total_url}

## Hasil File

{_format_dict(hasil_file)}

## Kategori Risiko File

{_format_dict(kategori_file)}

{bagian_ai}

## Catatan Keamanan

Pemeriksaan file dilakukan secara statis. Sistem tidak menjalankan file. 
Untuk file berisiko tinggi, jangan dibuka di perangkat utama dan jangan klik URL di dalamnya.
""".strip()

    return laporan


def simpan_laporan(teks_laporan: str, lokasi_output: str | Path) -> Path:
    """Menyimpan laporan ke file Markdown."""
    path_output = Path(lokasi_output)
    path_output.parent.mkdir(parents=True, exist_ok=True)
    path_output.write_text(teks_laporan, encoding="utf-8")
    return path_output