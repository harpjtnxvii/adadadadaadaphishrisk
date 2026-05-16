from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd


KOLOM_FEEDBACK = [
    "waktu",
    "tipe",
    "input_user",
    "hasil_sistem",
    "kategori_risiko",
    "feedback_user",
    "catatan_user",
]


def siapkan_file_feedback(lokasi_feedback: str | Path) -> Path:
    """Menyiapkan file feedback user."""
    path_feedback = Path(lokasi_feedback)
    path_feedback.parent.mkdir(parents=True, exist_ok=True)

    if not path_feedback.exists():
        pd.DataFrame(columns=KOLOM_FEEDBACK).to_csv(path_feedback, index=False)

    return path_feedback


def simpan_feedback(
    lokasi_feedback: str | Path,
    tipe: str,
    input_user: str,
    hasil_sistem: str,
    kategori_risiko: str,
    feedback_user: str,
    catatan_user: Optional[str] = "",
) -> Path:
    """Menyimpan feedback user untuk koreksi dan evaluasi berikutnya."""
    path_feedback = siapkan_file_feedback(lokasi_feedback)

    data_lama = pd.read_csv(path_feedback)

    data_baru = pd.DataFrame(
        [
            {
                "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "tipe": tipe,
                "input_user": input_user,
                "hasil_sistem": hasil_sistem,
                "kategori_risiko": kategori_risiko,
                "feedback_user": feedback_user,
                "catatan_user": catatan_user or "",
            }
        ]
    )

    data_final = pd.concat([data_lama, data_baru], ignore_index=True)
    data_final.to_csv(path_feedback, index=False)

    return path_feedback


def baca_feedback(lokasi_feedback: str | Path) -> pd.DataFrame:
    """Membaca data feedback user."""
    path_feedback = siapkan_file_feedback(lokasi_feedback)
    return pd.read_csv(path_feedback)


def ringkas_feedback(lokasi_feedback: str | Path) -> pd.DataFrame:
    """Membuat ringkasan feedback user."""
    data = baca_feedback(lokasi_feedback)

    if data.empty:
        return pd.DataFrame(columns=["feedback_user", "jumlah_data"])

    return (
        data.groupby("feedback_user")
        .size()
        .reset_index(name="jumlah_data")
        .sort_values("jumlah_data", ascending=False)
    )