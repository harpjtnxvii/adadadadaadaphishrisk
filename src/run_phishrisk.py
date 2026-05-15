
from pathlib import Path
import argparse
import sys
import pandas as pd


DIREKTORI_FILE = Path(__file__).resolve()
DIREKTORI_SRC = DIREKTORI_FILE.parent
DIREKTORI_PROJECT = DIREKTORI_SRC.parent

if str(DIREKTORI_SRC) not in sys.path:
    sys.path.append(str(DIREKTORI_SRC))

import phishrisk_engine_v3


def buat_folder_output(direktori_project):
    direktori_output = Path(direktori_project) / "reports" / "outputs"
    direktori_output.mkdir(parents=True, exist_ok=True)
    return direktori_output


def simpan_dataframe(dataframe, lokasi_output):
    lokasi_output = Path(lokasi_output)
    lokasi_output.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(lokasi_output, index=False, encoding="utf-8")
    return lokasi_output


def cetak_ringkasan_url(data_hasil):
    if data_hasil.empty:
        print("Tidak ada hasil URL.")
        return

    print("\nRINGKASAN HASIL URL")
    print("=" * 60)

    ringkasan = data_hasil.groupby(
        ["hasil_akhir", "kategori_risiko"]
    ).size().reset_index(name="jumlah_data")

    print(ringkasan.to_string(index=False))

    print("\nHASIL DETAIL")
    kolom = [
        "url",
        "domain",
        "label_model",
        "skor_model",
        "skor_final",
        "kategori_risiko",
        "hasil_akhir",
        "intelligence_status",
        "rekomendasi"
    ]

    kolom_tersedia = [item for item in kolom if item in data_hasil.columns]
    print(data_hasil[kolom_tersedia].to_string(index=False))


def cetak_ringkasan_file(data_hasil_file):
    if data_hasil_file.empty:
        print("Tidak ada hasil file.")
        return

    print("\nRINGKASAN HASIL FILE")
    print("=" * 60)

    ringkasan = data_hasil_file.groupby(
        ["hasil_akhir_file_v3", "kategori_final_file_v3"]
    ).size().reset_index(name="jumlah_data")

    print(ringkasan.to_string(index=False))

    print("\nHASIL DETAIL FILE")
    kolom = [
        "nama_file",
        "ekstensi",
        "jumlah_url",
        "jumlah_url_berisiko_v3",
        "jumlah_kata_mencurigakan",
        "skor_final_file_v3",
        "kategori_final_file_v3",
        "hasil_akhir_file_v3",
        "rekomendasi_final_file_v3"
    ]

    kolom_tersedia = [item for item in kolom if item in data_hasil_file.columns]
    print(data_hasil_file[kolom_tersedia].to_string(index=False))


def baca_csv_url(lokasi_csv, nama_kolom_url=None):
    lokasi_csv = Path(lokasi_csv)

    if not lokasi_csv.exists():
        raise FileNotFoundError(f"File CSV tidak ditemukan: {lokasi_csv}")

    data = pd.read_csv(lokasi_csv)

    if nama_kolom_url and nama_kolom_url in data.columns:
        kolom_url = nama_kolom_url
    else:
        kandidat_kolom = ["url", "URL", "alamat", "Alamat", "link", "Link"]

        kolom_url = None
        for kandidat in kandidat_kolom:
            if kandidat in data.columns:
                kolom_url = kandidat
                break

        if kolom_url is None:
            raise ValueError("Kolom URL tidak ditemukan. Gunakan nama kolom: url, URL, alamat, atau link.")

    daftar_url = (
        data[kolom_url]
        .dropna()
        .astype(str)
        .str.strip()
        .tolist()
    )

    daftar_url = [url for url in daftar_url if url]

    return daftar_url


def ambil_file_dari_folder(lokasi_folder):
    lokasi_folder = Path(lokasi_folder)

    if not lokasi_folder.exists():
        raise FileNotFoundError(f"Folder tidak ditemukan: {lokasi_folder}")

    daftar_file = [
        item
        for item in lokasi_folder.iterdir()
        if item.is_file()
    ]

    return daftar_file


def mode_url(engine, nilai_input, lokasi_output):
    hasil = engine.analisis_url(nilai_input)
    data_hasil = pd.DataFrame([hasil])

    cetak_ringkasan_url(data_hasil)
    simpan_dataframe(data_hasil, lokasi_output)

    print("\nOutput disimpan:")
    print(lokasi_output)


def mode_urls(engine, nilai_input, lokasi_output, nama_kolom_url=None):
    daftar_url = baca_csv_url(nilai_input, nama_kolom_url)
    data_hasil = engine.analisis_banyak_url(daftar_url)

    cetak_ringkasan_url(data_hasil)
    simpan_dataframe(data_hasil, lokasi_output)

    print("\nOutput disimpan:")
    print(lokasi_output)


def mode_file(engine, nilai_input, lokasi_output):
    hasil_file, data_url = engine.analisis_file(nilai_input)
    data_hasil_file = pd.DataFrame([hasil_file])

    cetak_ringkasan_file(data_hasil_file)
    simpan_dataframe(data_hasil_file, lokasi_output)

    if not data_url.empty:
        lokasi_url_file = lokasi_output.with_name(lokasi_output.stem + "_url_dalam_file.csv")
        simpan_dataframe(data_url, lokasi_url_file)
        print("\nOutput URL dalam file disimpan:")
        print(lokasi_url_file)

    print("\nOutput file disimpan:")
    print(lokasi_output)


def mode_folder(engine, nilai_input, lokasi_output):
    daftar_file = ambil_file_dari_folder(nilai_input)
    data_hasil_file, data_url = engine.analisis_banyak_file(daftar_file)

    cetak_ringkasan_file(data_hasil_file)
    simpan_dataframe(data_hasil_file, lokasi_output)

    if not data_url.empty:
        lokasi_url_file = lokasi_output.with_name(lokasi_output.stem + "_url_dalam_file.csv")
        simpan_dataframe(data_url, lokasi_url_file)
        print("\nOutput URL dalam file disimpan:")
        print(lokasi_url_file)

    print("\nOutput folder disimpan:")
    print(lokasi_output)


def main():
    parser = argparse.ArgumentParser(
        description="PhishRisk CLI untuk analisis URL dan file phishing secara defensif."
    )

    parser.add_argument(
        "--mode",
        required=True,
        choices=["url", "urls", "file", "folder"],
        help="Mode analisis: url, urls, file, atau folder."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Input berupa URL, file CSV, file dokumen, atau folder."
    )

    parser.add_argument(
        "--output",
        default=None,
        help="Lokasi output CSV. Jika kosong, output otomatis masuk reports/outputs."
    )

    parser.add_argument(
        "--url-column",
        default=None,
        help="Nama kolom URL jika mode urls memakai CSV."
    )

    direktori_output = buat_folder_output(DIREKTORI_PROJECT)

    if parser.parse_args().output:
        lokasi_output = Path(parser.parse_args().output)
    else:
        nama_default = {
            "url": "hasil_cli_url.csv",
            "urls": "hasil_cli_banyak_url.csv",
            "file": "hasil_cli_file.csv",
            "folder": "hasil_cli_folder.csv"
        }[parser.parse_args().mode]

        lokasi_output = direktori_output / nama_default

    args = parser.parse_args()

    engine = phishrisk_engine_v3.buat_engine(DIREKTORI_PROJECT)

    if args.mode == "url":
        mode_url(engine, args.input, lokasi_output)

    elif args.mode == "urls":
        mode_urls(engine, args.input, lokasi_output, args.url_column)

    elif args.mode == "file":
        mode_file(engine, args.input, lokasi_output)

    elif args.mode == "folder":
        mode_folder(engine, args.input, lokasi_output)


if __name__ == "__main__":
    main()
