
from pathlib import Path
import argparse
import sys

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from phishrisk_engine_v5 import PhishRiskEngineV5


def simpan_output(data, lokasi_output):
    lokasi_output = Path(lokasi_output)
    lokasi_output.parent.mkdir(parents=True, exist_ok=True)

    if isinstance(data, pd.DataFrame):
        data.to_csv(lokasi_output, index=False, encoding="utf-8")
    else:
        pd.DataFrame([data]).to_csv(lokasi_output, index=False, encoding="utf-8")

    return lokasi_output


def baca_url_dari_input(input_value, url_column="url"):
    lokasi = Path(input_value)

    if lokasi.exists() and lokasi.suffix.lower() == ".csv":
        data = pd.read_csv(lokasi)

        if url_column not in data.columns:
            raise ValueError(f"Kolom URL tidak ditemukan: {url_column}")

        return data[url_column].dropna().astype(str).tolist()

    if lokasi.exists() and lokasi.suffix.lower() in [".txt", ".log"]:
        return [
            baris.strip()
            for baris in lokasi.read_text(encoding="utf-8", errors="ignore").splitlines()
            if baris.strip()
        ]

    return [input_value]


def main():
    parser = argparse.ArgumentParser(description="PhishRisk Engine V5 CLI")
    parser.add_argument("--mode", choices=["url", "urls", "file", "folder"], required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="")
    parser.add_argument("--url-column", default="url")
    parser.add_argument("--model-mode", choices=["best", "rf", "xgb"], default="best")

    args = parser.parse_args()
    engine = PhishRiskEngineV5(direktori_project=PROJECT_DIR, prefer_model=args.model_mode)

    if args.mode == "url":
        hasil = pd.DataFrame([engine.analisis_url(args.input)])
        output_default = PROJECT_DIR / "reports" / "outputs" / "hasil_cli_url_engine_v5.csv"
    elif args.mode == "urls":
        hasil = engine.analisis_banyak_url(baca_url_dari_input(args.input, args.url_column))
        output_default = PROJECT_DIR / "reports" / "outputs" / "hasil_cli_banyak_url_engine_v5.csv"
    elif args.mode == "file":
        hasil = pd.DataFrame([engine.analisis_file(args.input)])
        output_default = PROJECT_DIR / "reports" / "outputs" / "hasil_cli_file_engine_v5.csv"
    else:
        folder = Path(args.input)
        if not folder.exists():
            raise FileNotFoundError(f"Folder tidak ditemukan: {folder}")
        hasil = engine.analisis_banyak_file([item for item in folder.iterdir() if item.is_file()])
        output_default = PROJECT_DIR / "reports" / "outputs" / "hasil_cli_folder_engine_v5.csv"

    lokasi_output = Path(args.output) if args.output else output_default
    simpan_output(hasil, lokasi_output)

    print("PhishRisk Engine V5 selesai.")
    print("Mode:", args.mode)
    print("Output:", lokasi_output)

    kolom_ringkas = [kolom for kolom in ["hasil_akhir_v5", "kategori_risiko_v5", "skor_final_v5", "engine_version"] if kolom in hasil.columns]
    if kolom_ringkas:
        print(hasil[kolom_ringkas].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
