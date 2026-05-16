from __future__ import annotations
# Auto-load environment lokal PhishRisk.
try:
    from pathlib import Path as _PhishRiskPath
    from dotenv import load_dotenv as _phishrisk_load_dotenv
    _phishrisk_load_dotenv(_PhishRiskPath(__file__).resolve().parents[1] / ".env")
except Exception:
    pass

import json
import os
from typing import Any, Dict, Iterable, Optional

import pandas as pd

from ai_safety_guard import (
    amankan_konteks_dict,
    bersihkan_teks,
    deteksi_permintaan_berbahaya,
    potong_daftar_teks,
)


KOLOM_URL_PENTING = [
    "url",
    "domain",
    "label_model",
    "skor_model",
    "skor_final",
    "kategori_risiko",
    "hasil_akhir",
    "intelligence_status",
    "official_brand",
    "brand_detected",
    "suspicious_keywords",
    "lookalike_brand",
    "lookalike_score",
    "rekomendasi",
]

KOLOM_FILE_PENTING = [
    "nama_file",
    "ekstensi",
    "ukuran_kb",
    "jumlah_url",
    "jumlah_url_berisiko_v3",
    "jumlah_url_perlu_tinjauan_v3",
    "jumlah_kata_mencurigakan",
    "kata_mencurigakan",
    "skor_final_file_v3",
    "kategori_final_file_v3",
    "hasil_akhir_file_v3",
    "alasan_file",
    "rekomendasi_final_file_v3",
]


class PhishRiskAIExplainer:
    """Lapisan AI untuk menjelaskan hasil PhishRisk tanpa mengganti keputusan engine."""

    def __init__(
        self,
        aktifkan_ai: Optional[bool] = None,
        model_ai: Optional[str] = None,
        batas_karakter: int = 3500,
    ) -> None:
        self.model_ai = model_ai or os.getenv("PHISHRISK_AI_MODEL", "gpt-5.5-mini")
        self.batas_karakter = batas_karakter

        if aktifkan_ai is None:
            aktifkan_ai = bool(os.getenv("OPENAI_API_KEY"))

        self.aktifkan_ai = aktifkan_ai
        self._client = None

        if self.aktifkan_ai:
            self._client = self._siapkan_client()

    def _siapkan_client(self) -> Any:
        """Menyiapkan client AI jika paket dan API key tersedia."""
        try:
            from openai import OpenAI

            return OpenAI()
        except Exception:
            self.aktifkan_ai = False
            return None

    def _panggil_ai(self, prompt: str) -> str:
        """Memanggil AI jika aktif. Jika gagal, gunakan fallback lokal."""
        if not self.aktifkan_ai or self._client is None:
            return ""

        try:
            response = self._client.responses.create(
                model=self.model_ai,
                input=prompt,
            )
            return bersihkan_teks(getattr(response, "output_text", ""), batas_karakter=self.batas_karakter)
        except Exception:
            self.aktifkan_ai = False
            return ""

    def _prompt_sistem(self) -> str:
        return (
            "Anda adalah asisten keamanan defensif untuk PhishRisk. "
            "Tugas Anda hanya menjelaskan hasil deteksi URL/file secara aman, ringkas, dan mudah dipahami. "
            "Jangan memberi langkah menyerang, membuat phishing, membuat malware, bypass keamanan, atau mencuri data. "
            "Jangan mengganti keputusan engine. Gunakan hasil engine sebagai sumber utama. "
            "Bahasa wajib Indonesia yang sederhana."
        )

    def _fallback_url(self, hasil_url: Dict[str, Any]) -> Dict[str, str]:
        data = amankan_konteks_dict(hasil_url, KOLOM_URL_PENTING)
        hasil = data.get("hasil_akhir", "-")
        kategori = data.get("kategori_risiko", "-")
        status = data.get("intelligence_status", "-")
        brand = data.get("brand_detected") or data.get("official_brand") or data.get("lookalike_brand") or "-"
        kata = data.get("suspicious_keywords", "")
        rekomendasi_engine = data.get("rekomendasi", "")

        alasan = []

        if status == "resmi_terlihat_aman":
            alasan.append("Domain cocok dengan daftar pembanding resmi.")
        if "tiruan_brand" in status:
            alasan.append("Alamat terlihat memakai nama brand, tetapi bukan domain resmi.")
        if "domain_mirip_brand" in status:
            alasan.append("Domain terlihat mirip dengan brand resmi.")
        if kata:
            alasan.append(f"Ada kata yang perlu diwaspadai: {kata}.")
        if data.get("skor_final"):
            alasan.append(f"Skor akhir sistem adalah {data.get('skor_final')}.")

        if not alasan:
            alasan.append("Sistem tidak menemukan sinyal utama yang cukup kuat dari data yang tersedia.")

        if hasil == "Berisiko":
            tindakan = "Jangan buka link, jangan login, jangan isi data pribadi, dan cek domain resmi dari sumber tepercaya."
        elif hasil == "Perlu Tinjauan":
            tindakan = "Cek ulang domain dari sumber resmi. Jangan gunakan link dari pesan asing."
        else:
            tindakan = "Tetap cek ulang alamat sebelum login atau transaksi."

        return {
            "mode": "fallback_lokal",
            "ringkasan": f"Hasil engine: {hasil} dengan kategori {kategori}.",
            "alasan_sederhana": " ".join(alasan),
            "rekomendasi": rekomendasi_engine or tindakan,
            "brand_terkait": brand,
            "batasan": "Penjelasan ini membantu membaca hasil engine, bukan jaminan keamanan mutlak.",
        }

    def _fallback_file(self, hasil_file: Dict[str, Any], jumlah_url_berisiko: int = 0) -> Dict[str, str]:
        data = amankan_konteks_dict(hasil_file, KOLOM_FILE_PENTING)
        hasil = data.get("hasil_akhir_file_v3", "-")
        kategori = data.get("kategori_final_file_v3", "-")
        ekstensi = data.get("ekstensi", "-")
        jumlah_url = data.get("jumlah_url", "0")
        kata = data.get("kata_mencurigakan", "")
        rekomendasi_engine = data.get("rekomendasi_final_file_v3", "")

        alasan = [
            f"File berjenis {ekstensi}.",
            f"Sistem menemukan {jumlah_url} URL di dalam file.",
        ]

        if jumlah_url_berisiko:
            alasan.append(f"Ada {jumlah_url_berisiko} URL yang dinilai berisiko.")
        if kata:
            alasan.append(f"Ada kata yang perlu diwaspadai: {kata}.")

        if hasil == "Berisiko":
            tindakan = "Jangan buka file di perangkat utama. Periksa di lingkungan aman atau minta bantuan pihak yang memahami keamanan."
        elif hasil == "Perlu Tinjauan":
            tindakan = "Cek sumber file dan URL di dalamnya sebelum dibuka."
        else:
            tindakan = "File terlihat rendah risiko, tetapi tetap buka hanya jika sumbernya tepercaya."

        return {
            "mode": "fallback_lokal",
            "ringkasan": f"Hasil engine file: {hasil} dengan kategori {kategori}.",
            "alasan_sederhana": " ".join(alasan),
            "rekomendasi": rekomendasi_engine or tindakan,
            "batasan": "Sistem hanya membaca file secara statis dan tidak menjalankan isi file.",
        }

    def jelaskan_hasil_url(self, hasil_url: Dict[str, Any]) -> Dict[str, str]:
        """Menjelaskan hasil URL dari engine."""
        data = amankan_konteks_dict(hasil_url, KOLOM_URL_PENTING)

        prompt = f"""
{self._prompt_sistem()}

Buat jawaban dalam 4 bagian:
1. Ringkasan
2. Alasan sederhana
3. Rekomendasi tindakan
4. Batasan

Data hasil engine:
{json.dumps(data, ensure_ascii=False, indent=2)}
""".strip()

        jawaban_ai = self._panggil_ai(prompt)

        if jawaban_ai:
            return {
                "mode": "ai",
                "ringkasan": jawaban_ai,
                "alasan_sederhana": "",
                "rekomendasi": "",
                "batasan": "AI menjelaskan hasil engine. Keputusan utama tetap dari PhishRisk Engine.",
            }

        return self._fallback_url(hasil_url)

    def jelaskan_hasil_file(
        self,
        hasil_file: Dict[str, Any],
        hasil_url_dalam_file: Optional[pd.DataFrame] = None,
    ) -> Dict[str, str]:
        """Menjelaskan hasil file dari engine."""
        data_file = amankan_konteks_dict(hasil_file, KOLOM_FILE_PENTING)

        jumlah_url_berisiko = 0
        contoh_url = []

        if hasil_url_dalam_file is not None and not hasil_url_dalam_file.empty:
            if "hasil_akhir" in hasil_url_dalam_file.columns:
                jumlah_url_berisiko = int((hasil_url_dalam_file["hasil_akhir"] == "Berisiko").sum())

            if "url" in hasil_url_dalam_file.columns:
                contoh_url = potong_daftar_teks(hasil_url_dalam_file["url"].head(5).tolist(), batas_item=5)

        prompt = f"""
{self._prompt_sistem()}

Jelaskan hasil pemeriksaan file dalam 4 bagian:
1. Ringkasan
2. Alasan sederhana
3. Rekomendasi tindakan
4. Batasan

Data hasil file:
{json.dumps(data_file, ensure_ascii=False, indent=2)}

Jumlah URL berisiko di dalam file: {jumlah_url_berisiko}
Contoh URL yang ditemukan:
{json.dumps(contoh_url, ensure_ascii=False, indent=2)}
""".strip()

        jawaban_ai = self._panggil_ai(prompt)

        if jawaban_ai:
            return {
                "mode": "ai",
                "ringkasan": jawaban_ai,
                "alasan_sederhana": "",
                "rekomendasi": "",
                "batasan": "AI menjelaskan hasil engine. File tidak dijalankan.",
            }

        return self._fallback_file(hasil_file, jumlah_url_berisiko=jumlah_url_berisiko)

    def buat_ringkasan_batch(self, data_hasil: pd.DataFrame, jenis: str = "url") -> Dict[str, str]:
        """Meringkas banyak hasil URL atau file."""
        if data_hasil is None or data_hasil.empty:
            return {
                "mode": "fallback_lokal",
                "ringkasan": "Tidak ada data yang bisa diringkas.",
                "rekomendasi": "Jalankan pemeriksaan terlebih dahulu.",
            }

        total = len(data_hasil)
        kolom_hasil = "hasil_akhir" if jenis == "url" else "hasil_akhir_file_v3"
        kolom_kategori = "kategori_risiko" if jenis == "url" else "kategori_final_file_v3"

        hitung_hasil = data_hasil[kolom_hasil].value_counts().to_dict() if kolom_hasil in data_hasil.columns else {}
        hitung_kategori = data_hasil[kolom_kategori].value_counts().to_dict() if kolom_kategori in data_hasil.columns else {}

        konteks = {
            "jenis": jenis,
            "total_data": total,
            "ringkasan_hasil": hitung_hasil,
            "ringkasan_kategori": hitung_kategori,
        }

        prompt = f"""
{self._prompt_sistem()}

Buat ringkasan singkat dari hasil batch.
Gunakan bahasa sederhana.
Berikan kesimpulan dan tindakan yang disarankan.

Data ringkasan:
{json.dumps(konteks, ensure_ascii=False, indent=2)}
""".strip()

        jawaban_ai = self._panggil_ai(prompt)

        if jawaban_ai:
            return {
                "mode": "ai",
                "ringkasan": jawaban_ai,
                "rekomendasi": "Gunakan hasil detail untuk mengecek item paling berisiko.",
            }

        return {
            "mode": "fallback_lokal",
            "ringkasan": f"Total data diperiksa: {total}. Hasil: {hitung_hasil}. Kategori: {hitung_kategori}.",
            "rekomendasi": "Utamakan pemeriksaan pada item dengan kategori Tinggi atau Sangat Tinggi.",
        }

    def jawab_copilot(self, pertanyaan: str, konteks: Dict[str, Any] | None = None) -> Dict[str, str]:
        """Menjawab pertanyaan user berdasarkan konteks hasil PhishRisk."""
        berbahaya, alasan = deteksi_permintaan_berbahaya(pertanyaan)

        if berbahaya:
            return {
                "mode": "safety_guard",
                "jawaban": (
                    "Saya tidak bisa membantu permintaan yang mengarah ke penyalahgunaan. "
                    "Saya bisa membantu menjelaskan deteksi phishing, membuat rekomendasi aman, atau membuat laporan defensif."
                ),
                "alasan": alasan,
            }

        konteks_aman = konteks or {}

        prompt = f"""
{self._prompt_sistem()}

Jawab pertanyaan user berdasarkan konteks PhishRisk.
Jika informasi tidak cukup, jawab dengan jujur dan beri saran pemeriksaan aman.

Pertanyaan user:
{bersihkan_teks(pertanyaan, batas_karakter=1000)}

Konteks:
{json.dumps(konteks_aman, ensure_ascii=False, indent=2)}
""".strip()

        jawaban_ai = self._panggil_ai(prompt)

        if jawaban_ai:
            return {
                "mode": "ai",
                "jawaban": jawaban_ai,
                "alasan": "Jawaban dibuat berdasarkan konteks hasil PhishRisk.",
            }

        return {
            "mode": "fallback_lokal",
            "jawaban": (
                "Mode AI eksternal belum aktif. Berdasarkan konsep PhishRisk, gunakan hasil engine sebagai acuan utama, "
                "cek domain resmi, jangan klik link dari sumber asing, dan jangan membuka file mencurigakan di perangkat utama."
            ),
            "alasan": "Fallback lokal aktif karena API key tidak tersedia atau client AI gagal dipakai.",
        }
