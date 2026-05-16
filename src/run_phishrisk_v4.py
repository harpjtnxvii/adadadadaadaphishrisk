from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
except Exception:
    pass

from phishrisk_engine_v4 import PhishRiskEngineV4


def cari_direktori_project() -> Path:
    return Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="PhishRisk Best Engine - Public Threat Intelligence")
    parser.add_argument("--mode", choices=["url", "urls", "file"], default="url")
    parser.add_argument("--input", required=True)
    parser.add_argument("--url-column", default="url")
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    direktori_project = cari_direktori_project()
    engine = PhishRiskEngineV4(direktori_project)

    if args.mode == "url":
        hasil = engine.analisis_url(args.input)
        data = pd.DataFrame([hasil])

        output = Path(args.output) if args.output else direktori_project / "reports" / "outputs" / "hasil_cli_engine_v4_url.csv"
        output.parent.mkdir(parents=True, exist_ok=True)
        data.to_csv(output, index=False)

        print("Hasil Best Engine")
        print("=" * 60)
        print("URL:", hasil.get("url"))
        print("Hasil V4:", hasil.get("hasil_akhir_v4"))
        print("Kategori V4:", hasil.get("kategori_risiko_v4"))
        print("Skor V4:", hasil.get("skor_final_v4"))
        print("Public TI:", hasil.get("public_ti_status"))
        print("Output:", output)

    elif args.mode == "urls":
        data_input = pd.read_csv(args.input)

        if args.url_column not in data_input.columns:
            raise ValueError(f"Kolom URL tidak ditemukan: {args.url_column}")

        daftar_url = data_input[args.url_column].dropna().astype(str).tolist()
        data = engine.analisis_banyak_url(daftar_url)

        output = Path(args.output) if args.output else direktori_project / "reports" / "outputs" / "hasil_cli_engine_v4_banyak_url.csv"
        output.parent.mkdir(parents=True, exist_ok=True)
        data.to_csv(output, index=False)

        print("Ringkasan Best Engine")
        print("=" * 60)
        print(data["hasil_akhir_v4"].value_counts().to_string())
        print("Output:", output)

    else:
        hasil_file, data_url = engine.analisis_file(args.input)

        output = Path(args.output) if args.output else direktori_project / "reports" / "outputs" / "hasil_cli_engine_v4_file.csv"
        output_url = output.with_name(output.stem + "_url_dalam_file.csv")

        output.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame([hasil_file]).to_csv(output, index=False)

        if isinstance(data_url, pd.DataFrame) and not data_url.empty:
            data_url.to_csv(output_url, index=False)

        print("Hasil File Best Engine")
        print("=" * 60)
        print("File:", hasil_file.get("nama_file"))
        print("Hasil:", hasil_file.get("hasil_akhir_file_v4"))
        print("Kategori:", hasil_file.get("kategori_final_file_v4"))
        print("Skor:", hasil_file.get("skor_final_file_v4"))
        print("Output:", output)


if __name__ == "__main__":
    main()
