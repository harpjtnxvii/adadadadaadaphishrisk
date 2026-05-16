from __future__ import annotations
# Auto-load environment lokal PhishRisk.
try:
    from pathlib import Path as _PhishRiskPath
    from dotenv import load_dotenv as _phishrisk_load_dotenv
    _phishrisk_load_dotenv(_PhishRiskPath(__file__).resolve().parents[1] / ".env")
except Exception:
    pass

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_explainer import PhishRiskAIExplainer
from ai_report_generator import buat_laporan_url_markdown, simpan_laporan
from phishrisk_engine_v3 import PhishRiskEngineV3


def main() -> None:
    parser = argparse.ArgumentParser(description="PhishRisk AI Explainer CLI")
    parser.add_argument("--input", required=True, help="URL yang ingin diperiksa")
    parser.add_argument("--output", default="reports/outputs/laporan_ai_url.md", help="Lokasi output laporan Markdown")
    args = parser.parse_args()

    engine = PhishRiskEngineV3(direktori_project=ROOT)
    explainer = PhishRiskAIExplainer()

    hasil_url = engine.analisis_url(args.input)
    data_url = pd.DataFrame([hasil_url])
    ringkasan_ai = explainer.buat_ringkasan_batch(data_url, jenis="url")
    penjelasan = explainer.jelaskan_hasil_url(hasil_url)

    laporan = buat_laporan_url_markdown(data_url, ringkasan_ai=ringkasan_ai)
    laporan += "\n\n## Penjelasan URL\n\n"
    laporan += penjelasan.get("ringkasan", "")
    if penjelasan.get("alasan_sederhana"):
        laporan += "\n\n" + penjelasan.get("alasan_sederhana", "")
    if penjelasan.get("rekomendasi"):
        laporan += "\n\nRekomendasi: " + penjelasan.get("rekomendasi", "")

    output = ROOT / args.output
    simpan_laporan(laporan, output)

    print("Hasil AI Explainer")
    print("=" * 60)
    print("URL:", args.input)
    print("Hasil:", hasil_url.get("hasil_akhir"))
    print("Kategori:", hasil_url.get("kategori_risiko"))
    print("Laporan:", output)


if __name__ == "__main__":
    main()
