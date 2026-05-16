from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

import pandas as pd

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except Exception:
    pass

from phishrisk_engine_v3 import PhishRiskEngineV3
from public_threat_intelligence import PublicThreatIntelligence


class PhishRiskEngineV4:
    """Best Engine yang menggabungkan hasil analisis dari Engine dan Public Threat Intelligence untuk memberikan penilaian risiko yang lebih komprehensif pada URL dan file."""

    def __init__(self, direktori_project: str | Path) -> None:
        self.direktori_project = Path(direktori_project)
        self.engine_v3 = PhishRiskEngineV3(self.direktori_project)
        self.public_ti = PublicThreatIntelligence()

    def analisis_url(self, url: str) -> Dict[str, Any]:
        hasil_v3 = self.engine_v3.analisis_url(url)
        hasil_public = self.public_ti.cek_url(url)
        return self.public_ti.gabungkan_dengan_hasil_engine(hasil_v3, hasil_public)

    def analisis_banyak_url(self, daftar_url: Iterable[str]) -> pd.DataFrame:
        hasil = []
        for url in daftar_url:
            hasil.append(self.analisis_url(url))
        return pd.DataFrame(hasil)

    def analisis_file(self, lokasi_file: str | Path) -> Tuple[Dict[str, Any], pd.DataFrame]:
        hasil_file_v3, data_url_dalam_file_v3 = self.engine_v3.analisis_file(lokasi_file)

        hasil_file_v4 = dict(hasil_file_v3)
        data_url_dalam_file_v4 = data_url_dalam_file_v3.copy() if isinstance(data_url_dalam_file_v3, pd.DataFrame) else pd.DataFrame()

        if not data_url_dalam_file_v4.empty and "url" in data_url_dalam_file_v4.columns:
            hasil_public = []

            for url in data_url_dalam_file_v4["url"].dropna().astype(str).tolist():
                hasil_public.append(self.public_ti.cek_url(url))

            data_public = pd.DataFrame(hasil_public)

            if not data_public.empty:
                kolom_gabung = [
                    "url",
                    "public_ti_score",
                    "public_ti_status",
                    "public_ti_result",
                    "public_ti_sources",
                    "public_ti_reason",
                    "phishtank_status",
                    "urlhaus_query_status",
                ]

                kolom_gabung = [kolom for kolom in kolom_gabung if kolom in data_public.columns]

                data_url_dalam_file_v4 = data_url_dalam_file_v4.merge(
                    data_public[kolom_gabung],
                    on="url",
                    how="left",
                )

                skor_public_maks = float(data_public["public_ti_score"].max()) if "public_ti_score" in data_public.columns else 0
                jumlah_temuan_public = int((data_public.get("public_ti_score", pd.Series(dtype=float)) >= 70).sum())

                skor_file_v3 = float(hasil_file_v3.get("skor_final_file_v3", hasil_file_v3.get("skor_risiko_file", 0)) or 0)
                skor_file_v4 = max(skor_file_v3, 95 if jumlah_temuan_public > 0 else skor_file_v3)

                hasil_file_v4["jumlah_url_terdeteksi_public_ti"] = jumlah_temuan_public
                hasil_file_v4["skor_public_ti_maks_file"] = skor_public_maks
                hasil_file_v4["skor_final_file_v4"] = round(skor_file_v4, 2)

                if jumlah_temuan_public > 0:
                    hasil_file_v4["kategori_final_file_v4"] = "Sangat Tinggi"
                    hasil_file_v4["hasil_akhir_file_v4"] = "Berisiko"
                    hasil_file_v4["rekomendasi_final_file_v4"] = "File mengandung URL yang ditemukan pada threat intelligence publik. Jangan dibuka langsung."
                else:
                    hasil_file_v4["kategori_final_file_v4"] = hasil_file_v3.get("kategori_final_file_v3", hasil_file_v3.get("kategori_risiko_file", ""))
                    hasil_file_v4["hasil_akhir_file_v4"] = hasil_file_v3.get("hasil_akhir_file_v3", hasil_file_v3.get("hasil_akhir_file", ""))
                    hasil_file_v4["rekomendasi_final_file_v4"] = hasil_file_v3.get("rekomendasi_final_file_v3", hasil_file_v3.get("rekomendasi_file", ""))

        if "skor_final_file_v4" not in hasil_file_v4:
            hasil_file_v4["jumlah_url_terdeteksi_public_ti"] = 0
            hasil_file_v4["skor_public_ti_maks_file"] = 0
            hasil_file_v4["skor_final_file_v4"] = hasil_file_v3.get("skor_final_file_v3", hasil_file_v3.get("skor_risiko_file", 0))
            hasil_file_v4["kategori_final_file_v4"] = hasil_file_v3.get("kategori_final_file_v3", hasil_file_v3.get("kategori_risiko_file", ""))
            hasil_file_v4["hasil_akhir_file_v4"] = hasil_file_v3.get("hasil_akhir_file_v3", hasil_file_v3.get("hasil_akhir_file", ""))
            hasil_file_v4["rekomendasi_final_file_v4"] = hasil_file_v3.get("rekomendasi_final_file_v3", hasil_file_v3.get("rekomendasi_file", ""))

        return hasil_file_v4, data_url_dalam_file_v4
