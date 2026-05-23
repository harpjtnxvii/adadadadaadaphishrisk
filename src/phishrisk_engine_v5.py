
from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse
from difflib import SequenceMatcher
from typing import Any, Dict, Iterable
import ipaddress
import json
import re
import sys

import joblib
import pandas as pd


class PhishRiskEngineV5:
    def __init__(self, direktori_project: str | Path | None = None, prefer_model: str = "best"):
        self.direktori_project = Path(direktori_project) if direktori_project else Path.cwd()
        if self.direktori_project.name.lower() == "src":
            self.direktori_project = self.direktori_project.parent

        self.direktori_src = self.direktori_project / "src"
        self.direktori_models = self.direktori_project / "models"
        self.direktori_outputs = self.direktori_project / "reports" / "outputs"
        self.direktori_intelligence = self.direktori_project / "data" / "intelligence"

        if str(self.direktori_src) not in sys.path:
            sys.path.insert(0, str(self.direktori_src))

        self.prefer_model = prefer_model
        self.daftar_fitur = self._load_json_list(self.direktori_outputs / "daftar_fitur_multi_dataset_v5.json")
        self.threshold_info = self._load_threshold()
        self.model_path, self.model = self._load_model()
        self.base_engine = self._load_engine_v4()
        self._load_intelligence_tables()

    def _load_json_list(self, lokasi: Path):
        with open(lokasi, "r", encoding="utf-8") as file:
            data = json.load(file)
        if isinstance(data, list):
            return data
        for key in ["features", "daftar_fitur", "feature_names"]:
            if isinstance(data, dict) and isinstance(data.get(key), list):
                return data[key]
        raise ValueError("Format daftar fitur V5 tidak dikenali.")

    def _load_threshold(self):
        lokasi = self.direktori_outputs / "threshold_model_terbaik_v5.json"
        if not lokasi.exists():
            return {"threshold_terbaik": 0.5}
        with open(lokasi, "r", encoding="utf-8") as file:
            return json.load(file)

    def _load_model(self):
        if self.prefer_model == "xgb":
            kandidat = ["model_xgb_multi_dataset_v5.pkl", "model_terbaik_multi_dataset_v5.pkl"]
        elif self.prefer_model == "rf":
            kandidat = ["model_rf_multi_dataset_v5.pkl", "model_terbaik_multi_dataset_v5.pkl"]
        else:
            kandidat = [
                "model_terbaik_multi_dataset_v5.pkl",
                "model_xgb_multi_dataset_v5.pkl",
                "model_rf_multi_dataset_v5.pkl",
            ]

        for nama in kandidat:
            lokasi = self.direktori_models / nama
            if lokasi.exists():
                return lokasi, joblib.load(lokasi)

        raise FileNotFoundError("Model V5 tidak ditemukan.")

    def _load_engine_v4(self):
        try:
            import phishrisk_engine_v4
            try:
                return phishrisk_engine_v4.PhishRiskEngineV4(direktori_project=self.direktori_project)
            except TypeError:
                return phishrisk_engine_v4.PhishRiskEngineV4(str(self.direktori_project))
        except Exception:
            return None

    def _load_intelligence_tables(self):
        self.official_domains = []
        self.brand_keywords = []
        self.brand_map = {}
        self.suspicious_weights = {}
        self.trusted_safe_domains = []

        lokasi_official = self.direktori_intelligence / "official_domains_global.csv"
        lokasi_brand = self.direktori_intelligence / "brand_keywords_global.csv"
        lokasi_suspicious = self.direktori_intelligence / "suspicious_keywords_global.csv"

        if lokasi_official.exists():
            data = pd.read_csv(lokasi_official)
            if "domain" in data.columns:
                self.official_domains = data["domain"].dropna().astype(str).str.lower().str.strip().unique().tolist()

        if lokasi_brand.exists():
            data = pd.read_csv(lokasi_brand)
            if "keyword" in data.columns:
                self.brand_keywords = data["keyword"].dropna().astype(str).str.lower().str.strip().unique().tolist()
            for _, row in data.iterrows():
                keyword = str(row.get("keyword", "")).strip().lower()
                brand = str(row.get("brand", keyword)).strip()
                if keyword:
                    self.brand_map[keyword] = brand

        if lokasi_suspicious.exists():
            data = pd.read_csv(lokasi_suspicious)
            for _, row in data.iterrows():
                keyword = str(row.get("keyword", "")).strip().lower()
                try:
                    bobot = int(row.get("bobot", 1))
                except Exception:
                    bobot = 1
                if keyword:
                    self.suspicious_weights[keyword] = bobot


        lokasi_trusted = self.direktori_intelligence / "trusted_safe_domains_global.csv"

        if lokasi_trusted.exists():
            data = pd.read_csv(lokasi_trusted)
            if "domain" in data.columns:
                self.trusted_safe_domains = (
                    data["domain"]
                    .dropna()
                    .astype(str)
                    .str.lower()
                    .str.strip()
                    .unique()
                    .tolist()
                )

    def bersihkan_url(self, url: Any) -> str:
        if url is None or pd.isna(url):
            return ""
        return re.sub(r"\s+", "", str(url).strip().replace("\x00", ""))

    def normalisasi_url(self, url: Any) -> str:
        url = self.bersihkan_url(url)
        if not url:
            return ""
        if not re.match(r"^https?://", url, flags=re.I):
            return "https://" + url
        return url

    def ambil_domain(self, url: Any) -> str:
        url = self.bersihkan_url(url)
        if not url:
            return ""
        try:
            url_parse = url if re.match(r"^https?://", url, flags=re.I) else "http://" + url
            parsed = urlparse(url_parse)
            domain = parsed.netloc.lower()
            domain = domain.split("@")[-1].split(":")[0]
            return domain.replace("www.", "", 1)
        except Exception:
            return ""

    def ambil_tld(self, domain: str) -> str:
        bagian = str(domain).split(".")
        return bagian[-1].lower() if len(bagian) >= 2 else ""

    def cek_domain_ip(self, domain: str) -> int:
        try:
            ipaddress.ip_address(domain)
            return 1
        except Exception:
            return 0

    def hitung_subdomain(self, domain: str) -> int:
        bagian = str(domain).split(".")
        return max(0, len(bagian) - 2) if len(bagian) > 2 else 0

    def cek_domain_resmi(self, domain: str) -> int:
        domain = str(domain).lower().strip()
        for official in self.official_domains:
            if domain == official or domain.endswith("." + official):
                return 1
        return 0

    def cek_brand(self, url: str, domain: str):
        teks = f"{url} {domain}".lower()
        for keyword in self.brand_keywords:
            if keyword and keyword in teks:
                return 1, self.brand_map.get(keyword, keyword)
        return 0, ""

    def cek_suspicious_keywords(self, url: str):
        teks = str(url).lower()
        ketemu = []
        skor = 0
        for keyword, bobot in self.suspicious_weights.items():
            if keyword in teks:
                ketemu.append(keyword)
                skor += bobot
        return len(ketemu), skor, ", ".join(ketemu)

    def ubah_digit_mirip(self, teks: str) -> str:
        return str(teks).translate(str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t"}))

    def cek_lookalike(self, domain: str, is_official: int):
        if is_official:
            return 0, 0.0, ""
        domain_bersih = self.ubah_digit_mirip(re.sub(r"[^a-z0-9]", "", str(domain).lower()))
        skor_terbaik = 0.0
        brand_terbaik = ""
        for keyword in self.brand_keywords:
            keyword_bersih = re.sub(r"[^a-z0-9]", "", keyword.lower())
            if len(keyword_bersih) <= 2:
                continue
            skor = SequenceMatcher(None, domain_bersih, keyword_bersih).ratio()
            if keyword_bersih in domain_bersih and keyword_bersih != domain_bersih:
                skor = max(skor, 1.0)
            if skor > skor_terbaik:
                skor_terbaik = skor
                brand_terbaik = self.brand_map.get(keyword, keyword)
        return int(skor_terbaik >= 0.82), round(float(skor_terbaik), 4), brand_terbaik


    def cek_trusted_safe_domain(self, domain: str) -> int:
        domain = str(domain).lower().strip()

        for trusted in getattr(self, "trusted_safe_domains", []):
            if domain == trusted or domain.endswith("." + trusted):
                return 1

        return 0

    def ekstrak_fitur_satu_url(self, url: Any) -> Dict[str, Any]:
        url = self.normalisasi_url(url)
        domain = self.ambil_domain(url)
        tld = self.ambil_tld(domain)

        panjang_url = len(url)
        jumlah_huruf = sum(karakter.isalpha() for karakter in url)
        jumlah_digit = sum(karakter.isdigit() for karakter in url)
        jumlah_spesial = sum(not karakter.isalnum() for karakter in url)

        fitur = {
            "URLLength": panjang_url,
            "DomainLength": len(domain),
            "TLDLength": len(tld),
            "NoOfSubDomain": self.hitung_subdomain(domain),
            "IsHTTPS": int(url.lower().startswith("https://")),
            "IsDomainIP": self.cek_domain_ip(domain),
            "NoOfLettersInURL": jumlah_huruf,
            "NoOfDegitsInURL": jumlah_digit,
            "NoOfDigitsInURL": jumlah_digit,
            "NoOfOtherSpecialCharsInURL": jumlah_spesial,
            "SpacialCharRatioInURL": jumlah_spesial / panjang_url if panjang_url else 0,
            "SpecialCharRatioInURL": jumlah_spesial / panjang_url if panjang_url else 0,
            "LetterRatioInURL": jumlah_huruf / panjang_url if panjang_url else 0,
            "DegitRatioInURL": jumlah_digit / panjang_url if panjang_url else 0,
            "DigitRatioInURL": jumlah_digit / panjang_url if panjang_url else 0,
            "NoOfEqualsInURL": url.count("="),
            "NoOfQMarkInURL": url.count("?"),
            "NoOfAmpersandInURL": url.count("&"),
            "NoOfSlashInURL": url.count("/"),
            "NoOfDotInURL": url.count("."),
            "NoOfDashInURL": url.count("-"),
            "NoOfAtInURL": url.count("@"),
        }

        for kolom in self.daftar_fitur:
            if kolom.startswith("TLD_"):
                fitur[kolom] = 0

        kolom_tld = f"TLD_{tld}"
        if kolom_tld in fitur:
            fitur[kolom_tld] = 1
        elif "TLD_lainnya" in fitur:
            fitur["TLD_lainnya"] = 1

        is_official = self.cek_domain_resmi(domain)
        is_trusted_safe = self.cek_trusted_safe_domain(domain)
        brand_detected_flag, brand_detected = self.cek_brand(url, domain)
        suspicious_count, suspicious_score, suspicious_keywords = self.cek_suspicious_keywords(url)
        lookalike_flag, lookalike_score, lookalike_brand = self.cek_lookalike(domain, is_official)

        fitur.update({
            "is_official_domain": is_official,
            "trusted_safe_domain": is_trusted_safe,
            "brand_keyword_detected": brand_detected_flag,
            "brand_but_not_official": int(brand_detected_flag == 1 and is_official == 0),
            "suspicious_keyword_count": suspicious_count,
            "suspicious_keyword_score": suspicious_score,
            "lookalike_brand_detected": lookalike_flag,
            "lookalike_score": lookalike_score,
            "uses_punycode": int("xn--" in domain),
            "uses_digit_substitution": int(any(karakter.isdigit() for karakter in domain)),
            "hyphen_count": domain.count("-"),
        })

        fitur_final = {nama: fitur.get(nama, 0) for nama in self.daftar_fitur}
        fitur_final["_url"] = url
        fitur_final["_domain"] = domain
        fitur_final["_brand_detected"] = brand_detected
        fitur_final["_suspicious_keywords"] = suspicious_keywords
        fitur_final["_lookalike_brand"] = lookalike_brand
        fitur_final["_trusted_safe_domain"] = is_trusted_safe
        return fitur_final

    def prediksi_model_v5(self, url: Any) -> Dict[str, Any]:
        fitur = self.ekstrak_fitur_satu_url(url)
        fitur_model = {nama: fitur.get(nama, 0) for nama in self.daftar_fitur}
        data_input = pd.DataFrame([fitur_model], columns=self.daftar_fitur)
        if hasattr(self.model, "predict_proba"):
            probabilitas = float(self.model.predict_proba(data_input)[0][1])
        else:
            probabilitas = float(self.model.predict(data_input)[0])
        return {
            "url": fitur["_url"],
            "domain": fitur["_domain"],
            "probabilitas_berisiko_v5": probabilitas,
            "skor_model_v5": round(probabilitas * 100, 2),
            "label_model_v5": "Berisiko" if probabilitas >= 0.5 else "Aman",
            "trusted_safe_domain": fitur.get("_trusted_safe_domain", 0),
            "brand_detected_v5": fitur["_brand_detected"],
            "suspicious_keywords_v5": fitur["_suspicious_keywords"],
            "lookalike_brand_v5": fitur["_lookalike_brand"],
            **fitur_model,
        }

    def analisis_base(self, url: str) -> Dict[str, Any]:
        if self.base_engine is None:
            return {"url": url, "domain": self.ambil_domain(url), "intelligence_status": "base_engine_tidak_tersedia"}
        try:
            hasil = self.base_engine.analisis_url(url)
            if isinstance(hasil, pd.Series):
                return hasil.to_dict()
            if isinstance(hasil, dict):
                return hasil
            return dict(hasil)
        except Exception as error:
            return {
                "url": url,
                "domain": self.ambil_domain(url),
                "intelligence_status": "base_engine_gagal",
                "base_error": str(error)[:300],
            }

    def kategori_dari_skor(self, skor: float):
        if skor < 30:
            return "Rendah", "Terlihat Aman"
        if skor < 60:
            return "Sedang", "Perlu Tinjauan"
        if skor < 80:
            return "Tinggi", "Berisiko"
        return "Sangat Tinggi", "Berisiko"

    def kalibrasi_final(self, hasil: Dict[str, Any]) -> Dict[str, Any]:
        skor_model = float(hasil.get("skor_model_v5", 0))
        skor_final = skor_model
        alasan = []

        intelligence_status = str(hasil.get("intelligence_status", "")).lower()
        public_ti_status = str(hasil.get("public_ti_status", "")).lower()

        is_official = int(float(hasil.get("is_official_domain", 0) or 0))
        is_trusted_safe = int(float(hasil.get("trusted_safe_domain", 0) or 0))
        brand_but_not_official = int(float(hasil.get("brand_but_not_official", 0) or 0))
        suspicious_score = int(float(hasil.get("suspicious_keyword_score", 0) or 0))
        lookalike_detected = int(float(hasil.get("lookalike_brand_detected", 0) or 0))
        uses_punycode = int(float(hasil.get("uses_punycode", 0) or 0))

        if "terindikasi" in public_ti_status or "ancaman" in public_ti_status:
            skor_final = max(skor_final, 95)
            alasan.append("Public Threat Intelligence menemukan sinyal ancaman kuat.")
        elif "perlu_tinjauan" in public_ti_status:
            skor_final = max(skor_final, 60)
            alasan.append("Public Threat Intelligence memberi sinyal perlu tinjauan.")
        elif "catatan" in public_ti_status:
            alasan.append("Public Threat Intelligence memberi catatan ringan.")

        if "tiruan_brand_berisiko" in intelligence_status:
            skor_final = max(skor_final, 92)
            alasan.append("URL memakai nama brand tetapi bukan domain resmi.")
        elif "domain_mirip_brand_berisiko" in intelligence_status:
            skor_final = max(skor_final, 90)
            alasan.append("Domain terlihat mirip dengan brand resmi dan memiliki sinyal tambahan.")
        elif "domain_mirip_brand" in intelligence_status:
            skor_final = max(skor_final, 82)
            alasan.append("Domain terlihat mirip dengan brand resmi.")
        elif "kata_mencurigakan_tinggi" in intelligence_status:
            skor_final = max(skor_final, 72)
            alasan.append("URL mengandung kata yang sering muncul pada serangan phishing.")

        if is_trusted_safe and suspicious_score == 0 and not uses_punycode:
            public_ti_kuat = (
                "terindikasi" in public_ti_status
                or "ancaman" in public_ti_status
                or "malware" in public_ti_status
            )
            intelligence_kuat = (
                "tiruan_brand_berisiko" in intelligence_status
                or "domain_mirip_brand_berisiko" in intelligence_status
                or "kata_mencurigakan_tinggi" in intelligence_status
            )

            if not public_ti_kuat and not intelligence_kuat:
                skor_final = min(skor_final, 24)
                brand_but_not_official = 0
                lookalike_detected = 0
                alasan.append("Domain masuk daftar trusted safe dan tidak memiliki sinyal phishing kuat.")

        if brand_but_not_official:
            skor_final = max(skor_final, 82)
            alasan.append("Brand terdeteksi tetapi domain tidak cocok dengan daftar resmi.")

        if suspicious_score >= 6:
            skor_final = max(skor_final, 72)
            alasan.append("Skor kata mencurigakan tinggi.")
        elif suspicious_score >= 3:
            skor_final = max(skor_final, 45)
            alasan.append("Ada kata yang perlu diwaspadai.")

        if lookalike_detected:
            skor_final = max(skor_final, 78)
            alasan.append("Domain memiliki pola mirip brand.")

        if uses_punycode:
            skor_final = max(skor_final, 85)
            alasan.append("Domain memakai punycode yang perlu diperiksa manual.")

        if is_official and "resmi_terlihat_aman" in intelligence_status:
            if suspicious_score == 0 and not lookalike_detected and not uses_punycode:
                skor_final = min(skor_final, 24)
                alasan.append("Domain cocok dengan daftar resmi dan tidak punya sinyal mencurigakan kuat.")
            else:
                skor_final = min(max(skor_final, 35), 59)
                alasan.append("Domain resmi tetapi tetap memiliki sinyal yang perlu ditinjau.")

        skor_final = round(max(0, min(100, float(skor_final))), 2)
        kategori, hasil_akhir = self.kategori_dari_skor(skor_final)

        if hasil_akhir == "Terlihat Aman":
            rekomendasi = "Alamat terlihat rendah risiko. Tetap pastikan sumber link tepercaya dan buka dari kanal resmi."
        elif hasil_akhir == "Perlu Tinjauan":
            rekomendasi = "Jangan langsung login atau memasukkan data pribadi. Cek domain resmi dan sumber link terlebih dahulu."
        else:
            rekomendasi = "Alamat berisiko. Jangan login, jangan isi data pribadi, jangan unduh file, dan laporkan jika perlu."

        return {
            "skor_final_v5": skor_final,
            "kategori_risiko_v5": kategori,
            "hasil_akhir_v5": hasil_akhir,
            "alasan_v5": " ".join(alasan) if alasan else "Keputusan berdasarkan skor model V5 dan sinyal intelligence.",
            "rekomendasi_v5": rekomendasi,
        }

    def analisis_url(self, url: Any) -> Dict[str, Any]:
        url_normal = self.normalisasi_url(url)
        hasil = {}
        hasil.update(self.analisis_base(url_normal))
        hasil.update(self.prediksi_model_v5(url_normal))
        hasil.update(self.kalibrasi_final(hasil))
        hasil["engine_version"] = "V5"
        hasil["model_path_v5"] = str(self.model_path)
        hasil["threshold_referensi_v5"] = self.threshold_info.get("threshold_terbaik", 0.5)
        return hasil

    def analisis_banyak_url(self, daftar_url: Iterable[Any]) -> pd.DataFrame:
        return pd.DataFrame([self.analisis_url(url) for url in daftar_url if str(url).strip()])

    def _fallback_hasil_file(self, lokasi_file: str | Path, pesan: str) -> Dict[str, Any]:
        lokasi_file = Path(lokasi_file)

        return {
            "nama_file": lokasi_file.name,
            "ekstensi": lokasi_file.suffix.lower(),
            "engine_version": "V5",
            "hasil_akhir_file_v5": "Perlu Tinjauan",
            "kategori_final_file_v5": "Sedang",
            "skor_final_file_v5": 50,
            "rekomendasi_final_file_v5": pesan,
        }

    def _dataframe_file_ke_dict(self, data: pd.DataFrame, lokasi_file: str | Path) -> Dict[str, Any]:
        if data.empty:
            return self._fallback_hasil_file(lokasi_file, "Hasil file analyzer kosong. Periksa file secara manual.")

        nama_file = Path(lokasi_file).name
        data_pilih = data.copy()

        if "nama_file" in data_pilih.columns:
            cocok = data_pilih[data_pilih["nama_file"].astype(str) == nama_file]
            if not cocok.empty:
                data_pilih = cocok

        return data_pilih.iloc[0].to_dict()

    def _hasil_file_ke_dict(self, hasil: Any, lokasi_file: str | Path) -> Dict[str, Any]:
        if hasil is None:
            return self._fallback_hasil_file(lokasi_file, "File analyzer tidak mengembalikan hasil.")

        if isinstance(hasil, dict):
            return dict(hasil)

        if isinstance(hasil, pd.Series):
            return hasil.to_dict()

        if isinstance(hasil, pd.DataFrame):
            return self._dataframe_file_ke_dict(hasil, lokasi_file)

        if isinstance(hasil, (list, tuple)):
            if len(hasil) == 0:
                return self._fallback_hasil_file(lokasi_file, "File analyzer mengembalikan list kosong.")

            if all(isinstance(item, dict) for item in hasil):
                return self._dataframe_file_ke_dict(pd.DataFrame(hasil), lokasi_file)

            for item in hasil:
                if isinstance(item, (dict, pd.Series, pd.DataFrame)):
                    return self._hasil_file_ke_dict(item, lokasi_file)

            return self._fallback_hasil_file(
                lokasi_file,
                "Format hasil file analyzer tidak dikenali. Periksa file secara manual.",
            )

        try:
            return dict(hasil)
        except Exception:
            return self._fallback_hasil_file(
                lokasi_file,
                f"Format hasil file analyzer tidak bisa dikonversi: {type(hasil).__name__}.",
            )

    def _selaraskan_kolom_file_v5(self, hasil: Dict[str, Any]) -> Dict[str, Any]:
        hasil = dict(hasil)

        pasangan_kolom = {
            "hasil_akhir_file_v3": "hasil_akhir_file_v5",
            "kategori_final_file_v3": "kategori_final_file_v5",
            "skor_final_file_v3": "skor_final_file_v5",
            "rekomendasi_final_file_v3": "rekomendasi_final_file_v5",
            "jumlah_url_berisiko_v3": "jumlah_url_berisiko_v5",
            "jumlah_url_perlu_tinjauan_v3": "jumlah_url_perlu_tinjauan_v5",
        }

        for kolom_lama, kolom_baru in pasangan_kolom.items():
            if kolom_lama in hasil and kolom_baru not in hasil:
                hasil[kolom_baru] = hasil[kolom_lama]

        if "hasil_akhir_file" in hasil and "hasil_akhir_file_v5" not in hasil:
            hasil["hasil_akhir_file_v5"] = hasil["hasil_akhir_file"]

        if "kategori_final_file" in hasil and "kategori_final_file_v5" not in hasil:
            hasil["kategori_final_file_v5"] = hasil["kategori_final_file"]

        if "rekomendasi_file" in hasil and "rekomendasi_final_file_v5" not in hasil:
            hasil["rekomendasi_final_file_v5"] = hasil["rekomendasi_file"]

        hasil.setdefault("hasil_akhir_file_v5", hasil.get("hasil_akhir_file_v3", "Perlu Tinjauan"))
        hasil.setdefault("kategori_final_file_v5", hasil.get("kategori_final_file_v3", "Sedang"))
        hasil.setdefault("rekomendasi_final_file_v5", "Periksa sumber file dan jangan menjalankan file mencurigakan di perangkat utama.")

        return hasil

    def analisis_file(self, lokasi_file: str | Path) -> Dict[str, Any]:
        lokasi_file = Path(lokasi_file)

        if self.base_engine is None or not hasattr(self.base_engine, "analisis_file"):
            return self._fallback_hasil_file(
                lokasi_file,
                "File analyzer base tidak tersedia. Periksa file secara manual.",
            )

        try:
            hasil_base = self.base_engine.analisis_file(lokasi_file)
            hasil = self._hasil_file_ke_dict(hasil_base, lokasi_file)
        except Exception as error:
            hasil = self._fallback_hasil_file(
                lokasi_file,
                f"File analyzer gagal dijalankan: {str(error)[:250]}",
            )

        hasil.setdefault("nama_file", lokasi_file.name)
        hasil.setdefault("ekstensi", lokasi_file.suffix.lower())
        hasil = self._selaraskan_kolom_file_v5(hasil)
        hasil["engine_version"] = "V5"
        hasil["catatan_v5"] = "Analisis file memakai static analyzer yang sudah ada. The Best Engine dipakai untuk kalibrasi URL secara terpisah."

        return hasil

    def analisis_banyak_file(self, daftar_file: Iterable[str | Path]) -> pd.DataFrame:
        hasil = []

        for file in daftar_file:
            try:
                hasil.append(self.analisis_file(file))
            except Exception as error:
                hasil.append(
                    self._fallback_hasil_file(
                        file,
                        f"Analisis file gagal: {str(error)[:250]}",
                    )
                )

        return pd.DataFrame(hasil)

    def analisis_url_di_dalam_file(self, lokasi_file: str | Path) -> pd.DataFrame:
        if self.base_engine is None or not hasattr(self.base_engine, "analisis_url_di_dalam_file"):
            return pd.DataFrame()

        try:
            data_url = self.base_engine.analisis_url_di_dalam_file(lokasi_file)

            if isinstance(data_url, list):
                data_url = pd.DataFrame(data_url)

            if not isinstance(data_url, pd.DataFrame) or data_url.empty or "url" not in data_url.columns:
                return pd.DataFrame()

            hasil = []
            for url in data_url["url"].dropna().astype(str).tolist():
                item = self.analisis_url(url)
                item["nama_file_sumber"] = Path(lokasi_file).name
                hasil.append(item)

            return pd.DataFrame(hasil)
        except Exception:
            return pd.DataFrame()
