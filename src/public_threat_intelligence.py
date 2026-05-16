from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Optional
from urllib.parse import urlparse

import pandas as pd
import requests

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except Exception:
    pass


def _bersihkan_url(url: Any) -> str:
    if url is None:
        return ""

    teks = str(url).strip()

    if teks and not teks.lower().startswith(("http://", "https://")):
        teks = "https://" + teks

    return teks


def _domain_dari_url(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def _nilai_bool(data: Any) -> bool:
    if isinstance(data, bool):
        return data
    if isinstance(data, str):
        return data.strip().lower() in ["true", "1", "yes", "y"]
    if isinstance(data, (int, float)):
        return data == 1
    return False


def _teks_pendek(nilai: Any, batas: int = 500) -> str:
    if nilai is None:
        return ""
    teks = str(nilai).replace("\x00", " ").strip()
    return teks[:batas]


@dataclass
class ThreatAPIConfig:
    timeout: int = 12
    jeda_request: float = 0.20
    aktifkan_phishtank: bool = True
    aktifkan_urlhaus: bool = True
    phishtank_app_key: str = ""
    urlhaus_auth_key: str = ""


class PhishTankClient:
    """Client defensif untuk mengecek URL ke PhishTank."""

    endpoint = "https://checkurl.phishtank.com/checkurl/"

    def __init__(self, app_key: str = "", timeout: int = 12) -> None:
        self.app_key = app_key or os.getenv("PHISHTANK_APP_KEY", "")
        self.timeout = timeout

    def cek_url(self, url: str) -> Dict[str, Any]:
        url = _bersihkan_url(url)

        hasil: Dict[str, Any] = {
            "phishtank_checked": 1,
            "phishtank_available": 0,
            "phishtank_found": 0,
            "phishtank_verified": 0,
            "phishtank_valid": 0,
            "phishtank_detail_url": "",
            "phishtank_status": "belum_dicek",
            "phishtank_error": "",
        }

        if not url:
            hasil["phishtank_status"] = "url_kosong"
            return hasil

        payload = {"url": url, "format": "json"}
        if self.app_key:
            payload["app_key"] = self.app_key

        headers = {"User-Agent": "phishtank/phishrisk-intelligence-system"}

        try:
            response = requests.post(
                self.endpoint,
                data=payload,
                headers=headers,
                timeout=self.timeout,
            )

            hasil["phishtank_available"] = 1

            if response.status_code == 509:
                hasil["phishtank_status"] = "rate_limit"
                hasil["phishtank_error"] = "PhishTank rate limit."
                return hasil

            if response.status_code >= 400:
                hasil["phishtank_status"] = f"http_{response.status_code}"
                hasil["phishtank_error"] = _teks_pendek(response.text)
                return hasil

            teks_response = response.text.strip()

            if not teks_response:
                hasil["phishtank_status"] = "respons_kosong"
                hasil["phishtank_error"] = "PhishTank mengembalikan respons kosong."
                return hasil

            try:
                data = response.json()
            except Exception:
                hasil["phishtank_status"] = "respons_bukan_json"
                hasil["phishtank_error"] = _teks_pendek(
                    f"HTTP {response.status_code} | Content-Type: {response.headers.get('Content-Type', '')} | Preview: {teks_response[:300]}"
                )
                return hasil

            result = data.get("results", data if isinstance(data, dict) else {})

            in_database = _nilai_bool(result.get("in_database"))
            verified = _nilai_bool(result.get("verified"))
            valid = _nilai_bool(result.get("valid"))

            hasil.update({
                "phishtank_found": int(in_database),
                "phishtank_verified": int(verified),
                "phishtank_valid": int(valid),
                "phishtank_detail_url": result.get("phish_detail_page", "") or str(result.get("phish_id", "")),
                "phishtank_status": "terdaftar" if in_database else "tidak_ditemukan",
            })

            if in_database and verified and valid:
                hasil["phishtank_status"] = "phishing_terverifikasi"
            elif in_database:
                hasil["phishtank_status"] = "terdaftar_belum_valid"

            return hasil

        except Exception as error:
            hasil["phishtank_status"] = "gagal"
            hasil["phishtank_error"] = _teks_pendek(error)
            return hasil


class URLhausClient:
    """Client defensif untuk mengecek URL ke URLhaus.

    URLhaus fokus pada URL malware/payload. API modern abuse.ch membutuhkan Auth-Key.
    """

    endpoint = "https://urlhaus-api.abuse.ch/v1/url/"

    def __init__(self, auth_key: str = "", timeout: int = 12) -> None:
        self.auth_key = auth_key or os.getenv("URLHAUS_AUTH_KEY", "")
        self.timeout = timeout

    def cek_url(self, url: str) -> Dict[str, Any]:
        url = _bersihkan_url(url)

        hasil: Dict[str, Any] = {
            "urlhaus_checked": 1,
            "urlhaus_available": 0,
            "urlhaus_found": 0,
            "urlhaus_query_status": "belum_dicek",
            "urlhaus_url_status": "",
            "urlhaus_threat": "",
            "urlhaus_tags": "",
            "urlhaus_reference": "",
            "urlhaus_error": "",
        }

        if not url:
            hasil["urlhaus_query_status"] = "url_kosong"
            return hasil

        if not self.auth_key:
            hasil["urlhaus_query_status"] = "auth_key_belum_tersedia"
            hasil["urlhaus_error"] = "URLhaus API membutuhkan Auth-Key gratis dari abuse.ch."
            return hasil

        headers = {
            "Auth-Key": self.auth_key,
            "User-Agent": "PhishRisk-Intelligence-System/1.0",
        }

        try:
            response = requests.post(
                self.endpoint,
                data={"url": url},
                headers=headers,
                timeout=self.timeout,
            )

            hasil["urlhaus_available"] = 1

            if response.status_code >= 400:
                hasil["urlhaus_query_status"] = f"http_{response.status_code}"
                hasil["urlhaus_error"] = _teks_pendek(response.text)
                return hasil

            data = response.json()
            query_status = data.get("query_status", "")

            hasil["urlhaus_query_status"] = query_status

            if query_status == "ok":
                hasil.update({
                    "urlhaus_found": 1,
                    "urlhaus_url_status": data.get("url_status", ""),
                    "urlhaus_threat": data.get("threat", ""),
                    "urlhaus_tags": ", ".join(data.get("tags", []) or []),
                    "urlhaus_reference": data.get("urlhaus_reference", ""),
                })
            elif query_status == "no_results":
                hasil["urlhaus_found"] = 0

            return hasil

        except Exception as error:
            hasil["urlhaus_query_status"] = "gagal"
            hasil["urlhaus_error"] = _teks_pendek(error)
            return hasil


class PublicThreatIntelligence:
    """Menggabungkan PhishTank dan URLhaus sebagai sinyal threat intelligence publik."""

    def __init__(self, config: Optional[ThreatAPIConfig] = None) -> None:
        timeout = int(os.getenv("PHISHRISK_PUBLIC_TI_TIMEOUT", "12") or "12")

        if config is None:
            config = ThreatAPIConfig(
                timeout=timeout,
                aktifkan_phishtank=os.getenv("PHISHRISK_PUBLIC_TI_ENABLE_PHISHTANK", "1") == "1",
                aktifkan_urlhaus=os.getenv("PHISHRISK_PUBLIC_TI_ENABLE_URLHAUS", "1") == "1",
                phishtank_app_key=os.getenv("PHISHTANK_APP_KEY", ""),
                urlhaus_auth_key=os.getenv("URLHAUS_AUTH_KEY", ""),
            )

        self.config = config
        self.phishtank = PhishTankClient(config.phishtank_app_key, config.timeout)
        self.urlhaus = URLhausClient(config.urlhaus_auth_key, config.timeout)

    def cek_url(self, url: str) -> Dict[str, Any]:
        url = _bersihkan_url(url)

        hasil: Dict[str, Any] = {
            "url": url,
            "domain": _domain_dari_url(url),
            "public_ti_checked_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        if self.config.aktifkan_phishtank:
            hasil.update(self.phishtank.cek_url(url))
            time.sleep(self.config.jeda_request)
        else:
            hasil.update({
                "phishtank_checked": 0,
                "phishtank_available": 0,
                "phishtank_found": 0,
                "phishtank_verified": 0,
                "phishtank_valid": 0,
                "phishtank_detail_url": "",
                "phishtank_status": "dinonaktifkan",
                "phishtank_error": "",
            })

        if self.config.aktifkan_urlhaus:
            hasil.update(self.urlhaus.cek_url(url))
            time.sleep(self.config.jeda_request)
        else:
            hasil.update({
                "urlhaus_checked": 0,
                "urlhaus_available": 0,
                "urlhaus_found": 0,
                "urlhaus_query_status": "dinonaktifkan",
                "urlhaus_url_status": "",
                "urlhaus_threat": "",
                "urlhaus_tags": "",
                "urlhaus_reference": "",
                "urlhaus_error": "",
            })

        hasil.update(self.hitung_skor_public_ti(hasil))
        return hasil

    def cek_banyak_url(self, daftar_url: Iterable[str]) -> pd.DataFrame:
        hasil = []
        for url in daftar_url:
            hasil.append(self.cek_url(url))
        return pd.DataFrame(hasil)

    @staticmethod
    def hitung_skor_public_ti(data: Dict[str, Any]) -> Dict[str, Any]:
        skor = 0
        sumber = []
        alasan = []

        phishtank_found = int(data.get("phishtank_found", 0) or 0)
        phishtank_verified = int(data.get("phishtank_verified", 0) or 0)
        phishtank_valid = int(data.get("phishtank_valid", 0) or 0)
        urlhaus_found = int(data.get("urlhaus_found", 0) or 0)

        if phishtank_found == 1:
            sumber.append("PhishTank")

            if phishtank_verified == 1 and phishtank_valid == 1:
                skor = max(skor, 100)
                alasan.append("URL terdaftar sebagai phishing aktif dan terverifikasi di PhishTank.")
            elif phishtank_verified == 1 and phishtank_valid == 0:
                skor = max(skor, 20)
                alasan.append("URL pernah muncul di PhishTank, tetapi statusnya tidak aktif atau belum valid saat ini.")
            else:
                skor = max(skor, 10)
                alasan.append("URL ditemukan di PhishTank, tetapi belum terverifikasi sebagai phishing aktif.")

        if urlhaus_found == 1:
            skor = max(skor, 100)
            sumber.append("URLhaus")
            alasan.append("URL ditemukan di URLhaus sebagai indikator malware atau payload berbahaya.")

        if skor >= 90:
            status = "terindikasi_ancaman_publik"
            kategori = "Sangat Tinggi"
            hasil = "Berisiko"
            rekomendasi = "URL ditemukan pada sumber threat intelligence publik. Jangan dibuka, jangan login, dan lakukan pengecekan manual."
        elif skor >= 60:
            status = "perlu_tinjauan_threat_intelligence"
            kategori = "Sedang"
            hasil = "Perlu Tinjauan"
            rekomendasi = "URL memiliki catatan kuat pada sumber eksternal, tetapi masih perlu validasi tambahan."
        elif skor > 0:
            status = "catatan_threat_intelligence_ringan"
            kategori = "Rendah"
            hasil = "Catatan Ringan"
            rekomendasi = "Ada catatan ringan dari sumber eksternal. Tetap gunakan hasil engine utama sebagai acuan."
        else:
            status = "tidak_ditemukan_di_public_ti"
            kategori = "Rendah"
            hasil = "Tidak Ada Temuan"
            rekomendasi = "Tidak ada temuan dari sumber threat intelligence publik yang aktif. Tetap gunakan hasil engine utama sebagai acuan."

        return {
            "public_ti_score": skor,
            "public_ti_status": status,
            "public_ti_category": kategori,
            "public_ti_result": hasil,
            "public_ti_sources": ", ".join(sorted(set(sumber))),
            "public_ti_reason": " ".join(alasan) if alasan else "Tidak ada temuan pada sumber threat intelligence publik yang aktif.",
            "public_ti_recommendation": rekomendasi,
        }

    @staticmethod
    def gabungkan_dengan_hasil_engine(hasil_engine: Dict[str, Any], hasil_public_ti: Dict[str, Any]) -> Dict[str, Any]:
        hasil = dict(hasil_engine)
        hasil.update(hasil_public_ti)

        skor_engine = float(hasil_engine.get("skor_final", 0) or 0)
        skor_public = float(hasil_public_ti.get("public_ti_score", 0) or 0)
        skor_final_v4 = max(skor_engine, skor_public)

        hasil_akhir_engine = hasil_engine.get("hasil_akhir", "")
        kategori_engine = hasil_engine.get("kategori_risiko", "")

        if skor_public >= 90:
            hasil_akhir_v4 = "Berisiko"
            kategori_v4 = "Sangat Tinggi"
            rekomendasi_v4 = hasil_public_ti.get("public_ti_recommendation", "")
        elif skor_public >= 70 and hasil_akhir_engine == "Terlihat Aman":
            hasil_akhir_v4 = "Perlu Tinjauan"
            kategori_v4 = "Tinggi"
            rekomendasi_v4 = hasil_public_ti.get("public_ti_recommendation", "")
        else:
            hasil_akhir_v4 = hasil_akhir_engine
            kategori_v4 = kategori_engine
            rekomendasi_v4 = hasil_engine.get("rekomendasi", "")

        hasil.update({
            "skor_final_v4": round(skor_final_v4, 2),
            "kategori_risiko_v4": kategori_v4,
            "hasil_akhir_v4": hasil_akhir_v4,
            "rekomendasi_v4": rekomendasi_v4,
        })

        return hasil
