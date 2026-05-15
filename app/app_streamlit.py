from pathlib import Path
from datetime import datetime
import hashlib
import html as html_escape
import json
import re
import sys

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="PhishRisk App",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_FILE = Path(__file__).resolve()

# Default aman untuk struktur: C:\\Users\\ASUS\\PHISHING\\app\\app_streamlit.py
# Jika file dipindah ke folder lain, bagian ini tetap mencoba mencari root project yang memiliki folder src dan models.
def cari_direktori_project(file_path):
    kandidat = [file_path.parent, *file_path.parents]
    for folder in kandidat:
        if (folder / "src").exists() and (folder / "models").exists():
            return folder
    return file_path.resolve().parents[1]

DIREKTORI_PROJECT = cari_direktori_project(APP_FILE)
DIREKTORI_SRC = DIREKTORI_PROJECT / "src"
DIREKTORI_OUTPUT = DIREKTORI_PROJECT / "reports" / "outputs"
DIREKTORI_UPLOAD = DIREKTORI_PROJECT / "data" / "uploads_streamlit"
DIREKTORI_EXAMPLES = DIREKTORI_PROJECT / "examples"

for folder in [DIREKTORI_OUTPUT, DIREKTORI_UPLOAD, DIREKTORI_EXAMPLES]:
    folder.mkdir(parents=True, exist_ok=True)

if str(DIREKTORI_SRC) not in sys.path:
    sys.path.append(str(DIREKTORI_SRC))

import phishrisk_engine_v3


LOKASI_RIWAYAT_STREAMLIT = DIREKTORI_OUTPUT / "riwayat_streamlit_ultra_v2.csv"
LOKASI_METADATA_STEP10 = DIREKTORI_OUTPUT / "metadata_step10_cli_utility.json"
LOKASI_METADATA_ENGINE = DIREKTORI_OUTPUT / "metadata_phishrisk_engine_v3.json"
LOKASI_VALIDASI_STEP10 = DIREKTORI_OUTPUT / "validasi_step10_cli_utility.csv"

AUTHOR_INFO = {
    "Nama": "Harbangan Panjaitan",
    "WhatsApp": "08158883565",
    "Instagram": "https://www.instagram.com/qe.harpjtn/",
    "LinkedIn": "https://www.linkedin.com/in/harbanganpjtn/",
    "GitHub": "https://github.com/harpjtnxvii",
}

CONTOH_URL = [
    "https://praktikum.gunadarma.ac.id",
    "https://baak.gunadarma.ac.id",
    "https://www.bca.co.id",
    "https://www.shopee.co.id",
    "https://www.microsoft.com",
    "http://rricrosoft.com",
    "http://rnicrosoft.com",
    "http://micros0ft-login-update.test",
    "http://bca-login-update.test",
    "http://paypal-verify-account.test",
    "http://praktikum-gunadarma-login-update.test",
    "https://xn--micrsoft-q4a.test",
]


DATASET_UJI_CEPAT = {
    "Website resmi Indonesia": [
        "https://praktikum.gunadarma.ac.id",
        "https://baak.gunadarma.ac.id",
        "https://www.bca.co.id",
        "https://www.bni.co.id",
        "https://www.bri.co.id",
        "https://www.mandiri.co.id",
        "https://www.shopee.co.id",
        "https://www.tokopedia.com",
        "https://www.tni.mil.id",
        "https://www.kominfo.go.id",
    ],
    "Brand global resmi": [
        "https://www.google.com",
        "https://www.microsoft.com",
        "https://www.apple.com",
        "https://www.amazon.com",
        "https://www.netflix.com",
        "https://www.paypal.com",
        "https://www.linkedin.com",
        "https://github.com",
    ],
    "Contoh tiruan berisiko": [
        "http://rricrosoft.com",
        "http://rnicrosoft.com",
        "http://micros0ft-login-update.test",
        "http://bca-login-update.test",
        "http://paypal-verify-account.test",
        "http://praktikum-gunadarma-login-update.test",
        "https://xn--micrsoft-q4a.test",
        "http://155.94.163.206/ai/?authenticated=true&account=login",
    ],
}



def pasang_css():
    st.markdown(
        """
        <style>
        :root {
            --bg-0: #0c0d0c;
            --bg-1: #10110f;
            --bg-2: #151613;
            --bg-3: #1b1b17;
            --text-0: #fffaf0;
            --text-1: #eee5d6;
            --text-2: #c7bca8;
            --text-3: #918777;
            --line-1: rgba(255,255,255,.08);
            --line-2: rgba(221,185,108,.34);
            --gold: #d9b66b;
            --gold-2: #ffe2a4;
            --green: #99c99f;
            --yellow: #d7bd75;
            --red: #e18478;
            --green-soft: rgba(153,201,159,.12);
            --yellow-soft: rgba(215,189,117,.14);
            --red-soft: rgba(225,132,120,.14);
            --gold-soft: rgba(217,182,107,.13);
            --shadow-1: 0 18px 55px rgba(0,0,0,.28);
            --shadow-2: 0 28px 90px rgba(0,0,0,.42);
            --r-sm: 12px;
            --r-md: 18px;
            --r-lg: 28px;
            --r-xl: 36px;
            --font-main: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
        }
        html, body, [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 8% 3%, rgba(217,182,107,.10), transparent 28%),
                radial-gradient(circle at 92% 6%, rgba(255,255,255,.045), transparent 22%),
                linear-gradient(135deg, #0c0d0c 0%, #10110f 42%, #171511 100%) !important;
            color: var(--text-0) !important;
            font-family: var(--font-main) !important;
            scroll-behavior: smooth;
        }
        [data-testid="stHeader"] { background: transparent !important; }
        #MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden !important; display: none !important; }
        .block-container { max-width: 1240px; padding: 1.05rem 1.25rem 3.5rem 1.25rem; }
        * { box-sizing: border-box; }
        h1, h2, h3, h4, p, div, span, label, li, button, input, textarea { font-family: var(--font-main) !important; }
        h1 { font-size: clamp(2.2rem, 5.6vw, 5.9rem) !important; line-height: .96 !important; letter-spacing: -.075em !important; color: var(--text-0) !important; margin: 0 0 .8rem 0 !important; }
        h2 { font-size: clamp(1.55rem, 2.6vw, 2.75rem) !important; line-height: 1.05 !important; letter-spacing: -.055em !important; color: var(--text-0) !important; margin: .3rem 0 .8rem 0 !important; }
        h3 { font-size: clamp(1.1rem, 1.5vw, 1.45rem) !important; line-height: 1.25 !important; letter-spacing: -.03em !important; color: var(--text-0) !important; }
        p, li, div, label { font-size: clamp(.94rem, .96vw, 1rem) !important; line-height: 1.72 !important; }
        .main .block-container { animation: fadeIn .34s ease-out; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        [data-testid="stSidebar"] { background: radial-gradient(circle at 0% 0%, rgba(217,182,107,.11), transparent 26%), linear-gradient(180deg, #171814 0%, #0f100f 100%) !important; border-right: 1px solid var(--line-1); }
        [data-testid="stSidebar"] * { color: var(--text-0) !important; }
        [data-testid="stSidebar"] .stRadio > label { display: none !important; }
        [data-testid="stSidebar"] [role="radiogroup"] { gap: .52rem !important; }
        [data-testid="stSidebar"] [role="radio"] { min-height: 46px; padding: .68rem .78rem; border-radius: 15px; border: 1px solid rgba(255,255,255,.075); background: rgba(255,255,255,.025); transition: 160ms ease; }
        [data-testid="stSidebar"] [role="radio"]:hover { border-color: rgba(217,182,107,.42); background: rgba(217,182,107,.085); transform: translateX(3px); }
        [data-testid="stSidebar"] [role="radio"][aria-checked="true"] { border-color: rgba(217,182,107,.72); background: linear-gradient(145deg, rgba(217,182,107,.18), rgba(255,255,255,.025)); box-shadow: inset 0 0 0 1px rgba(255,255,255,.035); }
        .hero { position: relative; overflow: hidden; border: 1px solid var(--line-1); border-radius: var(--r-xl); background: linear-gradient(135deg, rgba(255,255,255,.062), rgba(255,255,255,.015)), radial-gradient(circle at 100% 0%, rgba(217,182,107,.17), transparent 30%), radial-gradient(circle at 10% 100%, rgba(255,255,255,.04), transparent 30%), var(--bg-3); box-shadow: var(--shadow-2); padding: clamp(1.2rem, 3.6vw, 2.75rem); margin-bottom: 1rem; }
        .hero:before { content: ""; position: absolute; inset: 0; background-image: linear-gradient(rgba(255,255,255,.035) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.026) 1px, transparent 1px); background-size: 44px 44px; mask-image: linear-gradient(90deg, transparent, black 20%, black 80%, transparent); opacity: .25; pointer-events: none; }
        .hero > * { position: relative; z-index: 2; }
        .hero-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; margin-bottom: 1rem; }
        .eyebrow { display: inline-flex; align-items: center; width: fit-content; border: 1px solid var(--line-2); color: var(--gold-2); background: var(--gold-soft); border-radius: 999px; padding: .34rem .78rem; font-weight: 850; font-size: .78rem !important; letter-spacing: -.01em; }
        .hero-desc { max-width: 860px; color: var(--text-2); font-size: clamp(1rem, 1.14vw, 1.14rem) !important; margin: 0 !important; }
        .hero-actions { display: flex; flex-wrap: wrap; gap: .55rem; margin-top: 1.25rem; }
        .pill { border-radius: 999px; border: 1px solid rgba(255,255,255,.09); background: rgba(255,255,255,.035); color: var(--text-2); padding: .36rem .78rem; font-size: .8rem !important; font-weight: 700; }
        .section-title { margin: 1.3rem 0 .65rem 0; }
        .panel { border: 1px solid var(--line-1); border-radius: var(--r-lg); background: linear-gradient(145deg, rgba(255,255,255,.047), rgba(255,255,255,.014)), var(--bg-3); box-shadow: var(--shadow-1); padding: clamp(1rem, 2vw, 1.42rem); margin-bottom: 1rem; }
        .panel.compact { padding: 1rem; border-radius: var(--r-md); margin-bottom: .75rem; }
        .panel.gold { border-color: rgba(217,182,107,.34); background: linear-gradient(145deg, rgba(217,182,107,.14), rgba(255,255,255,.018)), var(--bg-3); }
        .panel.green { border-color: rgba(153,201,159,.34); background: linear-gradient(145deg, rgba(153,201,159,.13), rgba(255,255,255,.018)), var(--bg-3); }
        .panel.yellow { border-color: rgba(215,189,117,.38); background: linear-gradient(145deg, rgba(215,189,117,.14), rgba(255,255,255,.018)), var(--bg-3); }
        .panel.red { border-color: rgba(225,132,120,.38); background: linear-gradient(145deg, rgba(225,132,120,.15), rgba(255,255,255,.018)), var(--bg-3); }
        .panel.flat { box-shadow: none; background: rgba(255,255,255,.025); }
        .card-title { color: var(--text-0); font-weight: 900; font-size: clamp(1.04rem, 1.2vw, 1.26rem) !important; line-height: 1.23 !important; letter-spacing: -.03em; margin-bottom: .45rem; }
        .card-value { color: #fff5dc; font-size: clamp(1.55rem, 2.45vw, 2.35rem) !important; font-weight: 950; line-height: 1.03 !important; letter-spacing: -.055em; margin-bottom: .35rem; word-break: break-word; }
        .muted { color: var(--text-2); }
        .dim { color: var(--text-3); }
        .small { color: var(--text-3); font-size: .84rem !important; line-height: 1.58 !important; }
        .mini-list { margin: .35rem 0 0 0; padding: 0; list-style: none; }
        .mini-list li { border-top: 1px solid rgba(255,255,255,.065); padding: .72rem 0; color: var(--text-2); }
        .mini-list li:first-child { border-top: 0; }
        .callout { border: 1px solid rgba(255,255,255,.08); border-radius: var(--r-md); padding: 1rem; background: rgba(255,255,255,.025); margin: .55rem 0; }
        .callout.safe { border-color: rgba(153,201,159,.38); background: var(--green-soft); }
        .callout.review { border-color: rgba(215,189,117,.42); background: var(--yellow-soft); }
        .callout.danger { border-color: rgba(225,132,120,.42); background: var(--red-soft); }
        .score-line { height: 10px; border-radius: 999px; background: rgba(255,255,255,.08); overflow: hidden; border: 1px solid rgba(255,255,255,.06); margin: .75rem 0 .4rem 0; }
        .score-fill { height: 100%; border-radius: 999px; background: linear-gradient(90deg, var(--green), var(--yellow), var(--red)); }
        .risk-safe { border-color: rgba(153,201,159,.44) !important; background: radial-gradient(circle at 100% 0%, rgba(153,201,159,.18), transparent 28%), linear-gradient(145deg, rgba(153,201,159,.13), rgba(255,255,255,.015)), var(--bg-3) !important; }
        .risk-review { border-color: rgba(215,189,117,.48) !important; background: radial-gradient(circle at 100% 0%, rgba(215,189,117,.18), transparent 28%), linear-gradient(145deg, rgba(215,189,117,.14), rgba(255,255,255,.015)), var(--bg-3) !important; }
        .risk-danger { border-color: rgba(225,132,120,.5) !important; background: radial-gradient(circle at 100% 0%, rgba(225,132,120,.20), transparent 28%), linear-gradient(145deg, rgba(225,132,120,.15), rgba(255,255,255,.015)), var(--bg-3) !important; }
        .step-card { position: relative; padding-left: 4.2rem; min-height: 80px; }
        .step-number { position: absolute; left: 1rem; top: 1rem; width: 42px; height: 42px; border-radius: 14px; display: grid; place-items: center; background: rgba(217,182,107,.14); border: 1px solid rgba(217,182,107,.35); color: var(--gold-2); font-weight: 900; }
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div, .stNumberInput input { background: #131410 !important; color: var(--text-0) !important; border: 1px solid rgba(255,255,255,.13) !important; border-radius: var(--r-md) !important; min-height: 47px !important; font-size: clamp(.94rem, .95vw, 1rem) !important; box-shadow: inset 0 1px 0 rgba(255,255,255,.025) !important; }
        .stTextInput input:focus, .stTextArea textarea:focus { border-color: rgba(217,182,107,.72) !important; box-shadow: 0 0 0 3px rgba(217,182,107,.12) !important; }
        [data-testid="stFileUploader"] section { background: linear-gradient(135deg, rgba(255,255,255,.04), rgba(255,255,255,.015)), #131410 !important; border: 1px dashed rgba(217,182,107,.56) !important; border-radius: var(--r-lg) !important; min-height: 128px; }
        [data-testid="stFileUploader"] button { background: linear-gradient(145deg, #332a1b, #211d15) !important; color: #ffe6ae !important; border: 1px solid rgba(217,182,107,.50) !important; border-radius: 12px !important; font-weight: 850 !important; }
        .stButton > button, .stDownloadButton > button, button[kind="primary"] { width: 100%; min-height: 47px; border-radius: var(--r-md) !important; border: 1px solid rgba(217,182,107,.48) !important; background: linear-gradient(145deg, #342a1b, #211c15) !important; color: #ffe6ae !important; font-weight: 900 !important; box-shadow: 0 10px 24px rgba(0,0,0,.18) !important; transition: 160ms ease !important; }
        .stButton > button:hover, .stDownloadButton > button:hover, button[kind="primary"]:hover { border-color: rgba(217,182,107,.82) !important; background: linear-gradient(145deg, #3f321f, #2a2216) !important; transform: translateY(-1px); }
        [data-testid="stMetric"] { border: 1px solid var(--line-1); background: rgba(255,255,255,.025); border-radius: var(--r-md); padding: .75rem .85rem; }
        [data-testid="stMetricValue"] { color: #fff5dc !important; font-size: clamp(1.25rem, 1.85vw, 1.76rem) !important; font-weight: 950 !important; letter-spacing: -.04em !important; white-space: normal !important; overflow: visible !important; text-overflow: unset !important; }
        [data-testid="stDataFrame"] { border-radius: var(--r-lg); overflow: hidden; border: 1px solid rgba(255,255,255,.08); box-shadow: var(--shadow-1); }
        .stProgress > div > div > div > div { background: linear-gradient(90deg, var(--green), var(--yellow), var(--red)) !important; }
        .stAlert { border-radius: var(--r-lg) !important; border: 1px solid rgba(255,255,255,.08) !important; }
        .stTabs [data-baseweb="tab-list"] { gap: .45rem; flex-wrap: wrap; border-bottom: 0 !important; }
        .stTabs [data-baseweb="tab"] { border-radius: 999px; border: 1px solid rgba(255,255,255,.075); background: rgba(255,255,255,.025); padding: .42rem .85rem; color: var(--text-2) !important; }
        .stTabs [aria-selected="true"] { background: rgba(217,182,107,.15); border-color: rgba(217,182,107,.42); color: var(--text-0) !important; }
        div[data-testid="stExpander"] { border: 1px solid var(--line-1); background: rgba(255,255,255,.025); border-radius: var(--r-lg); overflow: hidden; }
        a { color: var(--gold-2) !important; text-decoration: none !important; }
        hr { border-color: var(--line-1); }
        @media (max-width: 1366px) { .block-container { max-width: 1120px; } }
        @media (max-width: 1024px) { .block-container { max-width: 940px; padding-left: .95rem; padding-right: .95rem; } .hero { border-radius: 26px; } }
        @media (max-width: 768px) { .block-container { padding: .82rem .62rem 2.4rem .62rem; } [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; } [data-testid="stSidebar"] { width: 18.5rem !important; } .hero, .panel { border-radius: 20px; padding: 1rem; } .hero-top { display: block; } h1 { font-size: clamp(2rem, 9vw, 3rem) !important; letter-spacing: -.065em !important; } .step-card { padding-left: 1rem; padding-top: 4.25rem; } .step-number { top: 1rem; } }
        @media (max-width: 520px) { .block-container { padding-left: .5rem; padding-right: .5rem; } p, li, div, label { font-size: .92rem !important; } .stButton > button, .stDownloadButton > button { min-height: 44px; } .eyebrow, .pill { font-size: .74rem !important; } .panel { margin-bottom: .75rem; } }

        div[data-baseweb="popover"], div[data-baseweb="popover"] * {
            font-family: var(--font-main) !important;
        }
        div[data-baseweb="popover"] [role="listbox"],
        div[data-baseweb="popover"] ul,
        [data-baseweb="menu"] {
            background: #11120f !important;
            color: var(--text-0) !important;
            border: 1px solid rgba(217,182,107,.35) !important;
            border-radius: 18px !important;
            box-shadow: 0 24px 70px rgba(0,0,0,.48) !important;
            padding: .35rem !important;
        }
        div[data-baseweb="popover"] li,
        div[data-baseweb="popover"] [role="option"],
        [data-baseweb="menu"] [role="option"] {
            color: var(--text-0) !important;
            background: transparent !important;
            border-radius: 12px !important;
            padding: .7rem .85rem !important;
        }
        div[data-baseweb="popover"] li:hover,
        div[data-baseweb="popover"] [role="option"]:hover,
        [data-baseweb="menu"] [role="option"]:hover {
            background: rgba(217,182,107,.14) !important;
            color: var(--gold-2) !important;
        }
        .input-lab { border: 1px solid rgba(217,182,107,.26); border-radius: var(--r-xl); background: linear-gradient(145deg, rgba(217,182,107,.10), rgba(255,255,255,.018)), rgba(18,19,16,.72); box-shadow: var(--shadow-1); padding: clamp(1rem, 2vw, 1.35rem); margin-bottom: 1rem; }
        .idea-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: .9rem; margin-top: .65rem; }
        .idea-card { border: 1px solid rgba(255,255,255,.075); border-radius: 20px; background: rgba(255,255,255,.025); padding: 1rem; min-height: 132px; }
        .idea-card b { color: var(--text-0); font-size: 1rem; }
        .idea-card p { color: var(--text-2); margin: .45rem 0 0 0 !important; font-size: .9rem !important; line-height: 1.58 !important; }
        .soft-divider { height: 1px; background: linear-gradient(90deg, transparent, rgba(217,182,107,.42), transparent); margin: 1rem 0; }
        @media (max-width: 900px) { .idea-grid { grid-template-columns: 1fr; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def aman_teks(nilai):
    return html_escape.escape(str(nilai))


def html(teks):
    st.markdown(teks, unsafe_allow_html=True)



def hero(label, judul, deskripsi, badges=None):
    badges = badges or []
    badge_html = "".join([f'<span class="pill">{aman_teks(item)}</span>' for item in badges])
    html(
        f"""
        <section class="hero">
            <div class="hero-top">
                <div class="eyebrow">{aman_teks(label)}</div>
                <div class="pill">ig: qe.harpjtn</div>
            </div>
            <h1>{aman_teks(judul)}</h1>
            <p class="hero-desc">{aman_teks(deskripsi)}</p>
            <div class="hero-actions">{badge_html}</div>
        </section>
        """
    )



def panel(judul, isi, warna="normal"):
    kelas = "panel"
    if warna in ["gold", "green", "red", "yellow", "flat"]:
        kelas += f" {warna}"
    html(
        f"""
        <section class="{kelas}">
            <div class="card-title">{aman_teks(judul)}</div>
            <div class="muted">{aman_teks(isi)}</div>
        </section>
        """
    )



def metrik_kartu(items, kolom=3):
    cols = st.columns(kolom)
    for index, item in enumerate(items):
        warna = item.get("warna", "normal")
        kelas = "panel compact"
        if warna in ["gold", "green", "red", "yellow", "flat"]:
            kelas += f" {warna}"
        with cols[index % kolom]:
            html(
                f"""
                <section class="{kelas}">
                    <div class="small">{aman_teks(item.get("label", ""))}</div>
                    <div class="card-value">{aman_teks(item.get("nilai", ""))}</div>
                    <div class="muted">{aman_teks(item.get("catatan", ""))}</div>
                </section>
                """
            )



def section_title(judul, deskripsi=""):
    """Judul antar bagian supaya layout tidak terlihat seperti catatan praktikum yang kabur dari lab."""
    html(
        f"""
        <div class="section-title">
            <h2>{aman_teks(judul)}</h2>
            <div class="small">{aman_teks(deskripsi)}</div>
        </div>
        """
    )


def status_to_class(status):
    teks = str(status).lower()
    if "aman" in teks:
        return "safe", "Terlihat Aman"
    if "tinjauan" in teks:
        return "review", "Perlu Tinjauan"
    return "danger", "Berisiko"


def score_bar(skor):
    try:
        nilai = max(0, min(100, float(skor)))
    except Exception:
        nilai = 0

    html(
        f"""
        <div class="score-line">
            <div class="score-fill" style="width:{nilai}%;"></div>
        </div>
        <div class="small">Skor akhir: {nilai:.2f} dari 100</div>
        """
    )


def callout(judul, isi, tipe="review"):
    if tipe not in ["safe", "review", "danger"]:
        tipe = "review"
    html(
        f"""
        <div class="callout {tipe}">
            <div class="card-title">{aman_teks(judul)}</div>
            <div class="muted">{aman_teks(isi)}</div>
        </div>
        """
    )


def bullet_panel(judul, daftar, warna="normal"):
    kelas = "panel"
    if warna in ["gold", "green", "red", "yellow", "flat"]:
        kelas += f" {warna}"
    isi = "".join([f"<li>{aman_teks(item)}</li>" for item in daftar])
    html(
        f"""
        <section class="{kelas}">
            <div class="card-title">{aman_teks(judul)}</div>
            <ul class="mini-list">{isi}</ul>
        </section>
        """
    )


def step_card(nomor, judul, isi):
    html(
        f"""
        <section class="panel step-card">
            <div class="step-number">{aman_teks(nomor)}</div>
            <div class="card-title">{aman_teks(judul)}</div>
            <div class="muted">{aman_teks(isi)}</div>
        </section>
        """
    )


def saran_berdasarkan_hasil_url(hasil):
    status = hasil.get("hasil_akhir", "")
    intelligence_status = str(hasil.get("intelligence_status", "")).lower()
    domain = hasil.get("domain", "-")

    if status == "Terlihat Aman":
        return [
            f"Domain {domain} terlihat rendah risiko berdasarkan pemeriksaan sistem.",
            "Tetap buka alamat dari bookmark atau ketik manual jika berkaitan dengan akun penting.",
            "Jangan memasukkan data sensitif jika link berasal dari pesan acak.",
            "Periksa ulang tampilan domain sebelum login atau transaksi.",
        ]

    if status == "Perlu Tinjauan":
        return [
            "Jangan langsung percaya. Periksa ulang domain utama dan sumber link.",
            "Bandingkan domain dengan website resmi dari kanal terpercaya.",
            "Hubungi admin resmi jika alamat berkaitan dengan kampus, bank, perusahaan, atau instansi.",
            "Jangan memasukkan kata sandi, OTP, PIN, atau data pembayaran sebelum yakin.",
        ]

    rekomendasi = [
        "Jangan buka link dari perangkat utama.",
        "Jangan isi username, password, OTP, PIN, nomor kartu, atau data pribadi.",
        "Laporkan link ke admin, kampus, bank, atau pihak terkait.",
        "Simpan bukti pesan jika link berasal dari SMS, WhatsApp, email, atau DM.",
    ]

    if "tiruan_brand" in intelligence_status or "domain_mirip" in intelligence_status:
        rekomendasi.append("Waspadai domain yang meniru brand resmi. Periksa huruf yang mirip, angka pengganti huruf, dan tanda hubung.")

    if "kata_mencurigakan" in intelligence_status:
        rekomendasi.append("Kata seperti login, verify, update, secure, account, reward, atau claim sering dipakai untuk membuat user terburu-buru.")

    return rekomendasi


@st.cache_resource
def muat_engine():
    return phishrisk_engine_v3.buat_engine(DIREKTORI_PROJECT)


@st.cache_data
def muat_metadata(lokasi):
    lokasi = Path(lokasi)
    if not lokasi.exists():
        return {}
    try:
        with open(lokasi, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}


@st.cache_data
def muat_validasi_step10():
    if not LOKASI_VALIDASI_STEP10.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(LOKASI_VALIDASI_STEP10)
    except Exception:
        return pd.DataFrame()


def muat_riwayat():
    if not LOKASI_RIWAYAT_STREAMLIT.exists():
        return []
    try:
        return pd.read_csv(LOKASI_RIWAYAT_STREAMLIT).fillna("-").to_dict("records")
    except Exception:
        return []


def siapkan_state():
    if "riwayat" not in st.session_state:
        st.session_state.riwayat = muat_riwayat()
    if "hasil_url_terakhir" not in st.session_state:
        st.session_state.hasil_url_terakhir = pd.DataFrame()
    if "hasil_file_terakhir" not in st.session_state:
        st.session_state.hasil_file_terakhir = pd.DataFrame()
    if "hasil_url_dalam_file_terakhir" not in st.session_state:
        st.session_state.hasil_url_dalam_file_terakhir = pd.DataFrame()


def simpan_riwayat():
    data = pd.DataFrame(st.session_state.riwayat)
    if not data.empty:
        data.to_csv(LOKASI_RIWAYAT_STREAMLIT, index=False, encoding="utf-8")


def tambah_riwayat_url(hasil):
    item = {
        "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "jenis": "URL",
        "input": hasil.get("url", "-"),
        "domain": hasil.get("domain", "-"),
        "hasil": hasil.get("hasil_akhir", "-"),
        "skor": hasil.get("skor_final", "-"),
        "kategori": hasil.get("kategori_risiko", "-"),
        "catatan": hasil.get("intelligence_status", "-"),
    }
    st.session_state.riwayat.insert(0, item)
    st.session_state.riwayat = st.session_state.riwayat[:500]
    simpan_riwayat()


def tambah_riwayat_file(hasil):
    item = {
        "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "jenis": "FILE",
        "input": hasil.get("nama_file", "-"),
        "domain": "-",
        "hasil": hasil.get("hasil_akhir_file_v3", "-"),
        "skor": hasil.get("skor_final_file_v3", "-"),
        "kategori": hasil.get("kategori_final_file_v3", "-"),
        "catatan": hasil.get("ekstensi", "-"),
    }
    st.session_state.riwayat.insert(0, item)
    st.session_state.riwayat = st.session_state.riwayat[:500]
    simpan_riwayat()


def kelas_status(hasil):
    teks = str(hasil).lower()
    if "aman" in teks:
        return "status-safe"
    if "tinjauan" in teks:
        return "status-review"
    return "status-danger"


def tampilkan_rekomendasi_kontekstual(hasil):
    status = hasil.get("hasil_akhir", "")

    with st.container(border=True):
        st.subheader("Rekomendasi tindakan")
        st.write(hasil.get("rekomendasi", "-"))

        if status == "Terlihat Aman":
            st.write("- Tetap cek ejaan domain sebelum login atau transaksi.")
            st.write("- Buka layanan penting dari bookmark atau ketik manual di browser.")
            st.write("- Jangan menganggap aman jika link berasal dari pesan yang menekan atau memaksa.")
        elif status == "Perlu Tinjauan":
            st.write("- Cek ulang sumber link sebelum membuka halaman.")
            st.write("- Bandingkan domain dengan website resmi dari kanal resmi.")
            st.write("- Jangan memasukkan OTP, kata sandi, atau data pembayaran sebelum yakin.")
        else:
            st.write("- Jangan buka link dari perangkat utama.")
            st.write("- Jangan isi formulir login, OTP, pembayaran, atau data pribadi.")
            st.write("- Laporkan link ke admin, kampus, bank, atau pihak terkait.")
            st.write("- Simpan bukti pesan jika link berasal dari SMS, WhatsApp, email, atau DM.")

    with st.container(border=True):
        st.subheader("Antisipasi lanjutan")
        st.write("- Gunakan autentikasi dua langkah pada akun penting.")
        st.write("- Pisahkan akun utama dan akun percobaan untuk membuka tautan tidak dikenal.")
        st.write("- Periksa domain utama, bukan hanya tulisan di tampilan halaman.")
        st.write("- Waspadai domain yang memakai nama brand ditambah kata login, verify, update, secure, atau account.")
        st.write("- Jangan menjalankan file dari sumber tidak jelas, terutama APK, EXE, ZIP, LNK, BAT, CMD, PS1, dan VBS.")



def tampilkan_status_url(hasil):
    hasil_akhir = hasil.get("hasil_akhir", "-")
    risiko_class, label_risiko = status_to_class(hasil_akhir)
    skor = hasil.get("skor_final", 0)
    kelas_panel = f"panel risk-{risiko_class}"

    html(
        f"""
        <section class="{kelas_panel}">
            <div class="eyebrow">Hasil Pemeriksaan URL</div>
            <h2>{aman_teks(label_risiko)}</h2>
            <p class="muted">{aman_teks(hasil.get("rekomendasi", "-"))}</p>
        </section>
        """
    )

    warna_kategori = "green" if risiko_class == "safe" else "yellow" if risiko_class == "review" else "red"
    metrik_kartu(
        [
            {"label": "Skor akhir", "nilai": f"{skor}/100", "catatan": "Skor setelah model dan intelligence digabung.", "warna": "gold"},
            {"label": "Kategori", "nilai": hasil.get("kategori_risiko", "-"), "catatan": "Kelas risiko yang mudah dibaca user.", "warna": warna_kategori},
            {"label": "Sinyal", "nilai": hasil.get("intelligence_status", "-"), "catatan": "Sinyal dari domain resmi, brand, dan pola URL.", "warna": "normal"},
        ],
        kolom=3,
    )

    score_bar(skor)

    tab_ringkas, tab_alasan, tab_saran, tab_pembanding, tab_teknis = st.tabs(
        ["Ringkasan", "Alasan", "Rekomendasi", "Pembanding", "Detail teknis"]
    )

    with tab_ringkas:
        kolom_1, kolom_2 = st.columns([1.25, .75])
        with kolom_1:
            data = pd.DataFrame(
                [
                    {"Bagian": "URL", "Nilai": hasil.get("url", "-")},
                    {"Bagian": "Domain", "Nilai": hasil.get("domain", "-")},
                    {"Bagian": "TLD", "Nilai": hasil.get("tld", "-")},
                    {"Bagian": "Hasil model", "Nilai": hasil.get("label_model", "-")},
                    {"Bagian": "Skor model", "Nilai": hasil.get("skor_model", "-")},
                    {"Bagian": "Hasil akhir", "Nilai": hasil.get("hasil_akhir", "-")},
                    {"Bagian": "Brand resmi", "Nilai": hasil.get("official_brand", "-") or "-"},
                    {"Bagian": "Brand terdeteksi", "Nilai": hasil.get("brand_detected", "-") or "-"},
                    {"Bagian": "Brand mirip", "Nilai": hasil.get("lookalike_brand", "-") or "-"},
                ]
            )
            st.dataframe(data, use_container_width=True, hide_index=True)
        with kolom_2:
            callout("Cara baca cepat", "Skor rendah bukan izin untuk asal klik. Skor tinggi berarti sebaiknya hindari dulu dan cek sumber resmi.", risiko_class)
            callout("Prioritas user", "Fokus utama bukan sekadar angka, tetapi apakah alamat meminta login, OTP, pembayaran, atau file unduhan.", "review")

    with tab_alasan:
        panel("Alasan sistem", hasil.get("intelligence_reason", "-"), "gold")
        data_alasan = pd.DataFrame(
            [
                {"Sinyal": "Domain resmi", "Nilai": hasil.get("is_official_domain", 0), "Makna": "Cocok dengan daftar pembanding resmi."},
                {"Sinyal": "Brand tidak resmi", "Nilai": hasil.get("brand_but_not_official", 0), "Makna": "Mengandung nama brand tetapi bukan domain resmi."},
                {"Sinyal": "Kata mencurigakan", "Nilai": hasil.get("suspicious_keywords", "-") or "-", "Makna": "Kata yang sering dipakai dalam penipuan."},
                {"Sinyal": "Skor kata mencurigakan", "Nilai": hasil.get("suspicious_keyword_score", 0), "Makna": "Semakin besar, semakin perlu dicek."},
                {"Sinyal": "Domain mirip brand", "Nilai": hasil.get("lookalike_brand_detected", 0), "Makna": "Domain terlihat seperti nama brand resmi."},
                {"Sinyal": "Punycode", "Nilai": hasil.get("uses_punycode", 0), "Makna": "Bisa menyamarkan karakter domain."},
                {"Sinyal": "Pengganti angka", "Nilai": hasil.get("uses_digit_substitution", 0), "Makna": "Contoh angka 0 mengganti huruf o."},
                {"Sinyal": "Jumlah tanda hubung", "Nilai": hasil.get("hyphen_count", 0), "Makna": "Terlalu banyak tanda hubung bisa menjadi sinyal tiruan."},
            ]
        )
        st.dataframe(data_alasan, use_container_width=True, hide_index=True)

    with tab_saran:
        bullet_panel("Rekomendasi tindakan", saran_berdasarkan_hasil_url(hasil), "gold")
        bullet_panel(
            "Antisipasi lanjutan",
            [
                "Aktifkan verifikasi dua langkah pada akun penting.",
                "Gunakan password berbeda untuk akun penting.",
                "Jangan kirim OTP kepada siapa pun.",
                "Jangan klik tombol login dari email atau pesan yang tidak jelas.",
                "Simpan bukti jika link dikirim melalui chat, email, atau SMS.",
            ],
            "normal",
        )

    with tab_pembanding:
        bullet_panel(
            "Pembanding manual",
            [
                "Cek domain utama, bukan hanya judul halaman.",
                "Bandingkan alamat dengan website resmi dari kanal resmi.",
                "Untuk kampus, gunakan domain resmi akademik atau portal yang biasa dipakai.",
                "Untuk bank dan e-commerce, gunakan aplikasi resmi atau bookmark.",
                "Jika domain memakai nama brand tetapi bukan domain resmi, anggap perlu dicurigai.",
            ],
            "yellow",
        )

    with tab_teknis:
        st.dataframe(pd.DataFrame([hasil]), use_container_width=True, hide_index=True)


def tampilkan_tabel_url(data):
    if data.empty:
        st.info("Belum ada hasil pemeriksaan.")
        return

    kolom = [
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
        "rekomendasi",
    ]
    kolom = [item for item in kolom if item in data.columns]

    st.dataframe(data[kolom], use_container_width=True, hide_index=True)

    st.download_button(
        "Unduh hasil URL",
        data=data.to_csv(index=False).encode("utf-8"),
        file_name="hasil_url_phishrisk_streamlit.csv",
        mime="text/csv",
    )


def tampilkan_tabel_file(data_file, data_url):
    if data_file.empty:
        st.info("Belum ada hasil pemeriksaan file.")
        return

    kolom_file = [
        "nama_file",
        "ekstensi",
        "ukuran_kb",
        "magic_file",
        "jumlah_url",
        "jumlah_url_berisiko_v3",
        "jumlah_url_perlu_tinjauan_v3",
        "jumlah_kata_mencurigakan",
        "kata_mencurigakan",
        "jumlah_file_berbahaya_dalam_arsip",
        "jumlah_izin_apk_berisiko",
        "skor_final_file_v3",
        "kategori_final_file_v3",
        "hasil_akhir_file_v3",
        "alasan_file",
        "rekomendasi_final_file_v3",
        "sha256_upload",
    ]
    kolom_file = [item for item in kolom_file if item in data_file.columns]

    st.subheader("Hasil file")
    st.dataframe(data_file[kolom_file], use_container_width=True, hide_index=True)

    st.download_button(
        "Unduh hasil file",
        data=data_file.to_csv(index=False).encode("utf-8"),
        file_name="hasil_file_phishrisk_streamlit.csv",
        mime="text/csv",
    )

    if not data_url.empty:
        st.subheader("URL yang ditemukan di dalam file")
        tampilkan_tabel_url(data_url)


def parse_url_bebas(teks, tambah_https=True, hapus_duplikat=True):
    pola = r"(?:https?://)?(?:[a-zA-Z0-9-]+\.)+[a-zA-Z0-9]{2,}(?:/[^\s<>'\"]*)?|https?://\d{1,3}(?:\.\d{1,3}){3}[^\s<>'\"]*"
    hasil = re.findall(pola, str(teks))
    daftar = []
    penanda = set()

    for url in hasil:
        url = str(url).strip().strip("'\"`.,;:)]}>")
        if tambah_https and not re.match(r"^https?://", url, flags=re.IGNORECASE):
            url = "https://" + url
        if "." not in url:
            continue
        kunci = url.lower()
        if hapus_duplikat and kunci in penanda:
            continue
        daftar.append(url)
        penanda.add(kunci)

    return daftar


def nama_file_aman(nama):
    nama = str(nama).strip()
    nama = re.sub(r"[^a-zA-Z0-9._-]", "_", nama)
    if not nama:
        nama = "file_upload"
    return nama


def simpan_file_upload(file_upload):
    waktu = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    nama = f"{waktu}_{nama_file_aman(file_upload.name)}"
    lokasi = DIREKTORI_UPLOAD / nama
    lokasi.write_bytes(file_upload.getbuffer())
    return lokasi


def hash_file(lokasi):
    h = hashlib.sha256()
    with open(lokasi, "rb") as file:
        for blok in iter(lambda: file.read(1024 * 1024), b""):
            h.update(blok)
    return h.hexdigest()



def tampilkan_ringkasan_url(data):
    if data.empty:
        return

    jumlah = len(data)
    jumlah_aman = int((data["hasil_akhir"] == "Terlihat Aman").sum()) if "hasil_akhir" in data.columns else 0
    jumlah_tinjauan = int((data["hasil_akhir"] == "Perlu Tinjauan").sum()) if "hasil_akhir" in data.columns else 0
    jumlah_risiko = int((data["hasil_akhir"] == "Berisiko").sum()) if "hasil_akhir" in data.columns else 0
    skor_maks = round(float(data["skor_final"].max()), 2) if "skor_final" in data.columns else 0

    metrik_kartu(
        [
            {"label": "Total URL", "nilai": jumlah, "catatan": "Jumlah alamat yang diperiksa.", "warna": "normal"},
            {"label": "Terlihat aman", "nilai": jumlah_aman, "catatan": "Tidak ditemukan sinyal kuat.", "warna": "green"},
            {"label": "Perlu tinjauan", "nilai": jumlah_tinjauan, "catatan": "Butuh cek manual.", "warna": "yellow"},
            {"label": "Berisiko", "nilai": jumlah_risiko, "catatan": "Sebaiknya dihindari.", "warna": "red"},
        ],
        kolom=4,
    )

    kolom_1, kolom_2 = st.columns([.9, 1.1])
    with kolom_1:
        with st.container(border=True):
            st.subheader("Sebaran hasil")
            ringkasan = data["hasil_akhir"].value_counts().reset_index()
            ringkasan.columns = ["hasil", "jumlah"]
            st.bar_chart(ringkasan.set_index("hasil"))
            st.dataframe(ringkasan, use_container_width=True, hide_index=True)
    with kolom_2:
        with st.container(border=True):
            st.subheader("Prioritas pengecekan")
            prioritas = data.sort_values("skor_final", ascending=False).head(10)
            kolom_prioritas = [kolom for kolom in ["url", "skor_final", "hasil_akhir", "kategori_risiko", "intelligence_status"] if kolom in prioritas.columns]
            st.dataframe(prioritas[kolom_prioritas], use_container_width=True, hide_index=True)

    if jumlah_risiko > 0:
        callout("Ada alamat berisiko", "Jangan gunakan alamat berisiko untuk login, transaksi, memasukkan OTP, atau mengunduh file.", "danger")
    elif jumlah_tinjauan > 0:
        callout("Ada alamat yang perlu tinjauan", "Periksa ulang sumber link dan domain utama sebelum digunakan.", "review")
    else:
        callout("Mayoritas terlihat aman", "Tetap gunakan kebiasaan aman karena sistem ini adalah pemeriksaan awal, bukan vonis mutlak.", "safe")



def tampilkan_ringkasan_file(data):
    if data.empty:
        return

    total = len(data)
    risiko = int((data["hasil_akhir_file_v3"] == "Berisiko").sum()) if "hasil_akhir_file_v3" in data.columns else 0
    aman = int((data["hasil_akhir_file_v3"] == "Terlihat Aman").sum()) if "hasil_akhir_file_v3" in data.columns else 0
    skor_maks = round(float(data["skor_final_file_v3"].max()), 2) if "skor_final_file_v3" in data.columns else 0

    metrik_kartu(
        [
            {"label": "Total file", "nilai": total, "catatan": "Jumlah file yang diperiksa.", "warna": "normal"},
            {"label": "Terlihat aman", "nilai": aman, "catatan": "Rendah risiko dari pemeriksaan statis.", "warna": "green"},
            {"label": "File berisiko", "nilai": risiko, "catatan": "Jangan dibuka langsung.", "warna": "red"},
            {"label": "Skor tertinggi", "nilai": f"{skor_maks}/100", "catatan": "Prioritas pemeriksaan manual.", "warna": "gold"},
        ],
        kolom=4,
    )

    kolom_1, kolom_2 = st.columns([.9, 1.1])
    with kolom_1:
        with st.container(border=True):
            st.subheader("Sebaran file")
            ringkasan = data["hasil_akhir_file_v3"].value_counts().reset_index()
            ringkasan.columns = ["hasil", "jumlah"]
            st.bar_chart(ringkasan.set_index("hasil"))
            st.dataframe(ringkasan, use_container_width=True, hide_index=True)
    with kolom_2:
        with st.container(border=True):
            st.subheader("File prioritas")
            prioritas = data.sort_values("skor_final_file_v3", ascending=False).head(10)
            kolom_prioritas = [kolom for kolom in ["nama_file", "ekstensi", "skor_final_file_v3", "kategori_final_file_v3", "hasil_akhir_file_v3"] if kolom in prioritas.columns]
            st.dataframe(prioritas[kolom_prioritas], use_container_width=True, hide_index=True)

    if risiko > 0:
        callout("Ada file berisiko", "Jangan membuka, mengekstrak, atau menjalankan file berisiko di perangkat utama.", "danger")
    elif aman == total:
        callout("File terlihat rendah risiko", "Tetap pastikan sumber file tepercaya karena sistem ini bukan forensik penuh.", "safe")


def tampilkan_bullets(judul, daftar):
    with st.container(border=True):
        st.subheader(judul)
        for item in daftar:
            st.write(f"- {item}")




def normalisasi_url_input(url, tambah_https=True):
    url = str(url).strip().strip("'\"`.,;:)]}>")
    if not url:
        return ""
    if tambah_https and not re.match(r"^https?://", url, flags=re.IGNORECASE):
        url = "https://" + url
    return url


def tampilkan_ide_uji():
    html(
        """
        <div class="idea-grid">
            <div class="idea-card"><b>Uji website resmi</b><p>Coba alamat kampus, bank, instansi, e-commerce, dan perusahaan yang benar-benar kamu pakai sehari-hari.</p></div>
            <div class="idea-card"><b>Uji domain mirip</b><p>Bandingkan domain resmi dengan variasi typo, angka pengganti huruf, atau nama brand ditambah kata login dan update.</p></div>
            <div class="idea-card"><b>Uji banyak alamat</b><p>Tempel daftar URL dari chat, email, CSV, atau catatan supaya sistem bisa membuat prioritas alamat paling berisiko.</p></div>
            <div class="idea-card"><b>Uji file lampiran</b><p>Unggah PDF, Word, ZIP, APK, TXT, atau HTML untuk melihat apakah ada URL atau kata yang perlu dicurigai.</p></div>
            <div class="idea-card"><b>Catat salah deteksi</b><p>Jika website resmi terbaca berisiko, simpan hasilnya agar bisa masuk daftar pembanding resmi pada update berikutnya.</p></div>
            <div class="idea-card"><b>Bandingkan hasil</b><p>Gunakan Batch Lab untuk melihat peringkat skor, kategori, alasan, dan rekomendasi secara lebih rapi.</p></div>
        </div>
        """
    )


def jalankan_uji_satu_url(engine, url, sumber="uji_bebas"):
    url = normalisasi_url_input(url)
    if not url:
        st.warning("Masukkan alamat web terlebih dahulu.")
        return None

    with st.spinner("Memeriksa alamat yang kamu masukkan..."):
        hasil = engine.analisis_url(url)

    tambah_riwayat_url(hasil)
    st.session_state.hasil_url_terakhir = pd.DataFrame([hasil])
    tampilkan_status_url(hasil)
    return hasil


def jalankan_uji_banyak_url(engine, daftar_url, pesan_kosong="Tidak ada alamat yang bisa diperiksa."):
    daftar_url = [normalisasi_url_input(item) for item in daftar_url]
    daftar_url = [item for item in daftar_url if item]

    if not daftar_url:
        st.warning(pesan_kosong)
        return pd.DataFrame()

    with st.spinner("Memeriksa semua alamat..."):
        data = engine.analisis_banyak_url(daftar_url)

    for _, baris in data.iterrows():
        tambah_riwayat_url(baris.to_dict())

    st.session_state.hasil_url_terakhir = data
    tampilkan_ringkasan_url(data)
    tampilkan_tabel_url(data)
    return data


def render_lab_uji_bebas_beranda(engine):
    section_title("Uji Coba", "Masukkan alamat sendiri tanpa harus mengikuti contoh bawaan. Ini bagian yang seharusnya ada dari awal, tapi rupanya umat manusia harus marah dulu agar tombol input muncul.")

    html('<div class="input-lab">')
    tab_satu, tab_banyak, tab_set, tab_ide = st.tabs(["Satu URL bebas", "Banyak URL bebas", "Paket uji cepat", "Ide pengujian"])

    with tab_satu:
        st.write("Masukkan alamat apa saja. Bisa domain resmi, link dari pesan, link aneh, atau domain yang ingin kamu bandingkan.")
        url_bebas = st.text_input(
            "Alamat bebas",
            value="",
            placeholder="Contoh: shopee.co.id, https://praktikum.gunadarma.ac.id, rricrosoft.com",
            key="beranda_url_bebas_custom",
        )
        kolom_a, kolom_b, kolom_c = st.columns([1, 1, 1])
        with kolom_a:
            tombol_bebas = st.button("Periksa URL bebas", key="beranda_tombol_url_bebas")
        with kolom_b:
            tombol_gunadarma = st.button("Coba Gunadarma", key="beranda_tombol_gunadarma")
        with kolom_c:
            tombol_tiruan = st.button("Coba domain tiruan", key="beranda_tombol_tiruan")

        if tombol_bebas:
            jalankan_uji_satu_url(engine, url_bebas)
        if tombol_gunadarma:
            jalankan_uji_satu_url(engine, "https://praktikum.gunadarma.ac.id")
        if tombol_tiruan:
            jalankan_uji_satu_url(engine, "http://rricrosoft.com")

        panel(
            "Saran uji",
            "Coba bandingkan website resmi dan versi tiruannya. Misalnya microsoft.com dibanding rricrosoft.com, bca.co.id dibanding bca-login-update.test, atau domain kampus resmi dibanding domain tiruan yang memakai kata login dan update.",
            "yellow",
        )

    with tab_banyak:
        st.write("Tempel banyak alamat sekaligus. Cocok untuk menguji link dari chat, email, log browser, atau catatan investigasi.")
        teks_bebas = st.text_area(
            "Daftar alamat bebas",
            value="",
            placeholder="Tempel satu URL per baris atau campur dalam teks biasa. Sistem akan mengambil URL yang ditemukan.",
            height=230,
            key="beranda_textarea_banyak_bebas",
        )
        kolom_a, kolom_b, kolom_c = st.columns([1, 1, 1])
        with kolom_a:
            tambah_https = st.checkbox("Tambahkan https:// otomatis", value=True, key="beranda_banyak_tambah_https")
        with kolom_b:
            hapus_duplikat = st.checkbox("Hapus duplikat", value=True, key="beranda_banyak_hapus_duplikat")
        with kolom_c:
            isi_contoh = st.button("Isi contoh campuran", key="beranda_isi_contoh_campuran")

        if isi_contoh:
            teks_bebas = "\n".join(DATASET_UJI_CEPAT["Website resmi Indonesia"][:5] + DATASET_UJI_CEPAT["Contoh tiruan berisiko"][:5])
            st.info("Contoh campuran dimuat untuk run ini. Salin ke kotak input jika ingin mengedit manual.")
            st.code(teks_bebas, language="text")

        daftar = parse_url_bebas(teks_bebas, tambah_https=tambah_https, hapus_duplikat=hapus_duplikat)
        st.caption(f"Alamat terdeteksi: {len(daftar)}")
        if daftar:
            st.dataframe(pd.DataFrame({"url": daftar}), use_container_width=True, hide_index=True)

        if st.button("Periksa daftar bebas", key="beranda_periksa_daftar_bebas"):
            jalankan_uji_banyak_url(engine, daftar)

    with tab_set:
        st.write("Pilih paket uji cepat untuk membandingkan website resmi dan contoh alamat berisiko.")
        nama_paket = st.selectbox("Pilih paket uji", list(DATASET_UJI_CEPAT.keys()), key="beranda_paket_uji")
        daftar_paket = DATASET_UJI_CEPAT[nama_paket]
        st.dataframe(pd.DataFrame({"url": daftar_paket}), use_container_width=True, hide_index=True)
        kolom_a, kolom_b = st.columns([1, 1])
        with kolom_a:
            if st.button("Jalankan paket uji", key="beranda_jalankan_paket_uji"):
                jalankan_uji_banyak_url(engine, daftar_paket)
        with kolom_b:
            st.download_button(
                "Unduh paket uji",
                data=pd.DataFrame({"url": daftar_paket}).to_csv(index=False).encode("utf-8"),
                file_name=f"paket_uji_{nama_paket.lower().replace(' ', '_')}.csv",
                mime="text/csv",
            )

    with tab_ide:
        tampilkan_ide_uji()
        panel(
            "Ide update berikutnya",
            "Tambahkan fitur laporan PDF, daftar whitelist domain resmi dari file CSV, catatan koreksi user, dan halaman evaluasi salah deteksi agar model makin kuat. Karena ternyata aplikasi yang berguna memang perlu fitur, bukan cuma tampilan tampan di layar.",
            "gold",
        )

    html('</div>')


def halaman_beranda(engine):
    hero(
        "PhishRisk System",
        "Pemeriksa URL dan File yang Nyaman Dipakai",
        "Sistem dapat memeriksa alamat web, banyak alamat, file, dan URL di dalam file tanpa menjalankan file tersebut.",
        ["URL", "CSV", "File", "Multi File"],
    )

    riwayat = pd.DataFrame(st.session_state.riwayat)
    total_riwayat = len(riwayat)
    hasil_url = st.session_state.hasil_url_terakhir
    hasil_file = st.session_state.hasil_file_terakhir

    metrik_kartu(
        [
            {"label": "Active", "nilai": "V.1", "catatan": "Menggunakan Model Terbaik.", "warna": "gold"},
            {"label": "URL terakhir", "nilai": len(hasil_url), "catatan": "Jumlah URL pada hasil terakhir.", "warna": "normal"},
            {"label": "File terakhir", "nilai": len(hasil_file), "catatan": "Jumlah file pada hasil terakhir.", "warna": "normal"},
            {"label": "Riwayat", "nilai": total_riwayat, "catatan": "Total pemeriksaan tersimpan.", "warna": "normal"},
        ],
        kolom=4,
    )

    section_title("Pusat Kendali", "Ringkasan fitur utama yang tersedia di aplikasi.")
    kolom_1, kolom_2 = st.columns([1.05, .95])
    with kolom_1:
        panel("Apa yang bisa diperiksa?", "Satu URL, banyak URL dari teks bebas, banyak URL dari CSV, satu file, banyak file, serta URL yang tertanam di dalam file.", "gold")
        panel("Jenis file", "TXT, HTML, PDF, DOCX, XLSX, PPTX, ZIP, APK, EXE, LNK, BAT, CMD, PS1, VBS, CSV, JSON, XML, dan file lain tetap dapat diunggah untuk pemeriksaan statis awal.", "normal")
    with kolom_2:
        panel("Batasan penting", "Sistem tidak membuka website langsung dan tidak menjalankan file. Hasilnya dipakai sebagai bantuan awal agar user tidak asal klik seperti sedang mengundang masalah ke ruang tamu.", "yellow")
        panel("Output laporan", "Setiap hasil dapat diunduh sebagai CSV untuk dokumentasi, laporan, atau analisis lanjutan.", "green")

    section_title("Alur Kerja", "Gunakan urutan ini untuk pemeriksaan yang rapi.")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        step_card("1", "Masukkan data", "Gunakan input URL, paste banyak alamat, unggah CSV, atau unggah file.")
    with col_b:
        step_card("2", "Baca hasil", "Lihat skor, kategori, alasan, dan rekomendasi tindakan.")
    with col_c:
        step_card("3", "Ambil keputusan", "Aman bisa dilanjutkan hati-hati, perlu tinjauan dicek manual, berisiko sebaiknya dihindari.")

    render_lab_uji_bebas_beranda(engine)

    section_title("Coba Cepat Template", "Template disediakan sebagai pembanding cepat, bukan sebagai satu-satunya cara uji. Tenang, akhirnya user boleh mengetik sendiri, revolusi kecil sudah terjadi.")
    with st.container(border=True):
        pilihan = st.selectbox("Pilih contoh URL", CONTOH_URL, key="beranda_selectbox_template")
        kolom_a, kolom_b = st.columns([1, 1])
        with kolom_a:
            tombol = st.button("Periksa contoh URL", key="beranda_cek_cepat")
        with kolom_b:
            st.download_button("Unduh contoh URL", data=pd.DataFrame({"url": CONTOH_URL}).to_csv(index=False).encode("utf-8"), file_name="contoh_url_phishrisk.csv", mime="text/csv")
        if tombol:
            jalankan_uji_satu_url(engine, pilihan, sumber="template")

    section_title("Kesiapan Sistem", "Sistem terus diperbarui dengan model terbaru dan daftar pembanding resmi. Berikut adalah hasil validasi internal untuk memastikan kualitas tetap terjaga.")
    validasi = muat_validasi_step10()
    if validasi.empty:
        st.info("File validasi STEP 10 belum ditemukan.")
    else:
        st.dataframe(validasi, use_container_width=True, hide_index=True)


def halaman_periksa_url(engine):
    hero(
        "Pemeriksaan URL",
        "Input Alamat Link",
        "Masukkan satu alamat bebas, paste banyak alamat, atau unggah CSV. Semua hasil memakai Engine V3 dari program final.",
    )

    panel("Mode uji bebas", "Halaman ini tidak memaksa user mengikuti template. Masukkan alamat sendiri, domain resmi, link mencurigakan, atau daftar URL dari sumber apa pun untuk menguji kualitas model.", "gold")

    tab_satu, tab_banyak, tab_csv = st.tabs(["Satu alamat", "Banyak alamat", "CSV"])

    with tab_satu:
        with st.container(border=True):
            url = st.text_input("Alamat web", value="", placeholder="Masukkan URL bebas, contoh: shopee.co.id atau https://baak.gunadarma.ac.id")
            kolom_a, kolom_b = st.columns([1, 1])

            with kolom_a:
                tombol = st.button("Periksa alamat", key="periksa_satu_url")

            with kolom_b:
                st.download_button(
                    "Unduh contoh URL",
                    data=pd.DataFrame({"url": CONTOH_URL}).to_csv(index=False).encode("utf-8"),
                    file_name="contoh_url_phishrisk.csv",
                    mime="text/csv",
                )

        if tombol:
            if not url.strip():
                st.warning("Alamat web tidak boleh kosong.")
            else:
                with st.spinner("Memeriksa alamat..."):
                    hasil = engine.analisis_url(normalisasi_url_input(url.strip()))

                tambah_riwayat_url(hasil)
                st.session_state.hasil_url_terakhir = pd.DataFrame([hasil])
                tampilkan_status_url(hasil)

    with tab_banyak:
        with st.container(border=True):
            st.subheader("Paste daftar alamat")
            teks = st.text_area(
                "Teks berisi alamat",
                value="\n".join(CONTOH_URL),
                height=230,
            )

            kolom_a, kolom_b = st.columns(2)

            with kolom_a:
                tambah_https = st.checkbox("Tambahkan https:// jika belum ada", value=True)

            with kolom_b:
                hapus_duplikat = st.checkbox("Hapus alamat duplikat", value=True)

            daftar = parse_url_bebas(teks, tambah_https=tambah_https, hapus_duplikat=hapus_duplikat)

            st.caption(f"Alamat terdeteksi: {len(daftar)}")
            st.dataframe(pd.DataFrame({"url": daftar}), use_container_width=True, hide_index=True)

            if st.button("Periksa semua alamat", key="periksa_banyak_url"):
                if not daftar:
                    st.warning("Tidak ada alamat yang bisa diperiksa.")
                else:
                    with st.spinner("Memeriksa banyak alamat..."):
                        data = engine.analisis_banyak_url(daftar)

                    for _, baris in data.iterrows():
                        tambah_riwayat_url(baris.to_dict())

                    st.session_state.hasil_url_terakhir = data
                    tampilkan_ringkasan_url(data)
                    tampilkan_tabel_url(data)

    with tab_csv:
        with st.container(border=True):
            st.subheader("Unggah CSV")
            st.write("File CSV cukup memiliki satu kolom berisi alamat web. Nama kolom bebas, nanti dipilih setelah file diunggah.")

            file_csv = st.file_uploader("Unggah CSV URL", type=["csv"], key="csv_url_uploader")

            st.download_button(
                "Unduh template CSV",
                data=pd.DataFrame({"url": CONTOH_URL}).to_csv(index=False).encode("utf-8"),
                file_name="template_url_phishrisk.csv",
                mime="text/csv",
            )

        if file_csv is not None:
            data_csv = pd.read_csv(file_csv)
            st.dataframe(data_csv.head(20), use_container_width=True, hide_index=True)

            kolom_url = st.selectbox("Pilih kolom URL", data_csv.columns.tolist())

            if st.button("Periksa URL dari CSV"):
                daftar = data_csv[kolom_url].dropna().astype(str).str.strip().tolist()
                daftar = [item for item in daftar if item]

                with st.spinner("Memeriksa CSV..."):
                    data = engine.analisis_banyak_url(daftar)

                for _, baris in data.iterrows():
                    tambah_riwayat_url(baris.to_dict())

                st.session_state.hasil_url_terakhir = data
                tampilkan_ringkasan_url(data)
                tampilkan_tabel_url(data)


def halaman_periksa_file(engine):
    hero(
        "Pemeriksaan File",
        "Input File Apa Saja",
        "Unggah file dari berbagai ekstensi. Sistem melakukan pemeriksaan statis, mencari URL di dalam file, membaca tanda berisiko, lalu memberi rekomendasi. File tidak dijalankan.",
    )

    panel(
        "Jenis file",
        "Sistem menerima file apa saja dari uploader. Pemeriksaan paling kuat untuk teks, HTML, PDF, Word, arsip ZIP, dan APK. Untuk file lain, sistem tetap membaca metadata dasar, ekstensi, hash, dan tanda yang bisa diperiksa.",
        "gold",
    )

    with st.container(border=True):
        daftar_file = st.file_uploader(
            "Unggah satu atau banyak file",
            accept_multiple_files=True,
            type=None,
            help="Bisa PDF, Word, APK, ZIP, TXT, HTML, CSV, EXE, script, dan file lain. Sistem tidak menjalankan file.",
        )

        if daftar_file:
            data_info = pd.DataFrame(
                [
                    {
                        "nama_file": file.name,
                        "ukuran_kb": round(file.size / 1024, 2),
                        "tipe_browser": file.type or "tidak_diketahui",
                    }
                    for file in daftar_file
                ]
            )
            st.dataframe(data_info, use_container_width=True, hide_index=True)

        tombol = st.button("Periksa file yang diunggah")

    if tombol:
        if not daftar_file:
            st.warning("Unggah minimal satu file terlebih dahulu.")
            return

        hasil_file = []
        hasil_url = []

        with st.spinner("Memeriksa file secara statis..."):
            for file in daftar_file:
                lokasi = simpan_file_upload(file)

                data_file, data_url = engine.analisis_file(lokasi)
                data_file["nama_file"] = file.name
                data_file["sha256_upload"] = hash_file(lokasi)

                hasil_file.append(data_file)
                tambah_riwayat_file(data_file)

                if isinstance(data_url, pd.DataFrame) and not data_url.empty:
                    if "nama_file_sumber" not in data_url.columns:
                        data_url.insert(0, "nama_file_sumber", file.name)
                    else:
                        data_url["nama_file_sumber"] = file.name

                    hasil_url.append(data_url)

        data_file_final = pd.DataFrame(hasil_file)
        data_url_final = pd.concat(hasil_url, ignore_index=True) if hasil_url else pd.DataFrame()

        st.session_state.hasil_file_terakhir = data_file_final
        st.session_state.hasil_url_dalam_file_terakhir = data_url_final

        tampilkan_ringkasan_file(data_file_final)
        tampilkan_tabel_file(data_file_final, data_url_final)

    if not st.session_state.hasil_file_terakhir.empty:
        with st.expander("Lihat hasil file terakhir"):
            tampilkan_tabel_file(
                st.session_state.hasil_file_terakhir,
                st.session_state.hasil_url_dalam_file_terakhir,
            )



def halaman_rekomendasi():
    hero(
        "Rekomendasi dan Antisipasi",
        "Panduan Tindakan Setelah Pemeriksaan",
        "Halaman ini membantu user mengambil keputusan setelah mendapat hasil aman, perlu tinjauan, atau berisiko.",
        ["Aman", "Perlu Tinjauan", "Berisiko", "File"],
    )

    tab_aman, tab_tinjauan, tab_risiko, tab_file, tab_kebiasaan = st.tabs(["Terlihat aman", "Perlu tinjauan", "Berisiko", "File", "Kebiasaan aman"])

    with tab_aman:
        callout("Bukan bebas mutlak", "Alamat terlihat aman tetap harus dicek jika meminta login, OTP, pembayaran, atau unduhan.", "safe")
        col_1, col_2 = st.columns(2)
        with col_1:
            bullet_panel("Yang boleh dilakukan", ["Buka dari bookmark atau ketik manual.", "Gunakan koneksi yang aman.", "Pastikan domain utama benar.", "Lanjutkan hanya jika sumber link jelas."], "green")
        with col_2:
            bullet_panel("Yang tetap dihindari", ["Jangan login dari link yang dikirim orang asing.", "Jangan kirim OTP.", "Jangan unduh file tambahan tanpa alasan.", "Jangan percaya hanya karena ada logo resmi."], "yellow")

    with tab_tinjauan:
        callout("Perlu dicek manual", "Perlu tinjauan berarti sistem melihat hal yang belum cukup kuat untuk disebut berisiko, tapi tidak cukup tenang untuk disebut aman sepenuhnya.", "review")
        bullet_panel("Langkah pengecekan", ["Bandingkan domain dengan kanal resmi.", "Cek apakah link dikirim dari alamat email resmi.", "Hubungi admin atau layanan pelanggan resmi.", "Gunakan browser search untuk mencari domain resmi, bukan menyalin link dari pesan.", "Jangan masukkan data sensitif sampai yakin."], "yellow")

    with tab_risiko:
        callout("Jangan lanjutkan", "Alamat berisiko sebaiknya tidak dibuka, tidak diisi, dan tidak digunakan untuk transaksi.", "danger")
        bullet_panel("Tindakan cepat", ["Tutup tab atau jangan buka link.", "Jangan isi username, password, OTP, PIN, nomor kartu, atau data pribadi.", "Laporkan ke admin, bank, kampus, perusahaan, atau penyedia layanan.", "Jika sudah terlanjur login, ganti password dari website resmi.", "Keluar dari semua sesi login akun penting."], "red")

    with tab_file:
        callout("File lebih berbahaya dari sekadar link", "File bisa berisi link, script, macro, shortcut, atau aplikasi yang berjalan setelah dibuka.", "danger")
        bullet_panel("Antisipasi file", ["Jangan jalankan EXE, MSI, APK, BAT, CMD, PS1, VBS, LNK, SCR, atau JAR dari sumber tidak jelas.", "Jangan aktifkan macro pada Word, Excel, atau PowerPoint.", "Jangan ekstrak ZIP/RAR/7Z sembarangan.", "Periksa hash dan sumber file jika file penting.", "Gunakan lingkungan aman untuk analisis lanjutan."], "red")

    with tab_kebiasaan:
        bullet_panel("Kebiasaan yang menyelamatkan akun", ["Pakai password manager agar domain palsu lebih mudah terlihat.", "Aktifkan autentikasi dua langkah.", "Pisahkan email utama dan email percobaan.", "Jangan klik link login dari pesan yang mendesak.", "Simpan daftar domain resmi yang sering dipakai.", "Update browser dan sistem operasi.", "Gunakan akun dengan hak akses rendah untuk membuka file tidak jelas."], "gold")


def halaman_ciri():
    hero(
        "Ciri-Ciri",
        "Mengenali Pola Aman dan Berisiko",
        "Sistem membaca pola. Halaman ini menjelaskan ciri umum dengan bahasa yang mudah dipahami.",
    )

    kolom_1, kolom_2 = st.columns(2)

    with kolom_1:
        tampilkan_bullets(
            "Ciri yang cenderung aman",
            [
                "Domain utama jelas dan sesuai nama layanan.",
                "Menggunakan HTTPS.",
                "Tidak penuh angka, tanda hubung, atau simbol.",
                "Tidak memakai IP sebagai alamat utama.",
                "Dibuka dari kanal resmi atau bookmark.",
                "Tidak meminta data sensitif dari tautan acak.",
            ],
        )

    with kolom_2:
        tampilkan_bullets(
            "Ciri yang perlu diwaspadai",
            [
                "Nama domain mirip brand resmi tetapi berbeda satu atau dua huruf.",
                "Mengandung kata login, verify, update, secure, account, reward, claim.",
                "Memakai angka untuk meniru huruf, misalnya angka 0 menggantikan o.",
                "Menggunakan punycode atau karakter aneh.",
                "Path URL sangat panjang dan penuh parameter.",
                "File lampiran meminta dijalankan, diekstrak, atau diaktifkan macro.",
            ],
        )

    with st.container(border=True):
        st.subheader("Contoh pola tiruan")
        data = pd.DataFrame(
            [
                {"Pola": "rricrosoft.com", "Masalah": "Mirip microsoft.com tetapi huruf awal berbeda."},
                {"Pola": "rnicrosoft.com", "Masalah": "Gabungan r dan n dapat terlihat seperti m."},
                {"Pola": "micros0ft-login-update.test", "Masalah": "Angka 0 mengganti huruf o dan memakai kata login update."},
                {"Pola": "bca-login-update.test", "Masalah": "Memakai nama brand tetapi bukan domain resmi."},
                {"Pola": "xn--micrsoft-q4a.test", "Masalah": "Punycode dapat menyamarkan bentuk domain."},
            ]
        )
        st.dataframe(data, use_container_width=True, hide_index=True)


def halaman_beta():
    hero(
        "Beta dan Salah Deteksi",
        "Kenapa Website Resmi Bisa Terlihat Berisiko?",
        "Model membaca pola alamat dan file. Ia tidak selalu tahu kepemilikan resmi sebuah website kecuali dibantu data intelligence.",
    )

    panel(
        "Contoh kasus",
        "Website resmi kampus, bank, instansi, atau perusahaan bisa memiliki subdomain panjang, path rumit, atau struktur URL yang jarang muncul di data. Karena itu hasil bisa menjadi perlu tinjauan, bukan otomatis tuduhan phishing.",
        "yellow",
    )

    metrik_kartu(
        [
            {"label": "Penyebab 1", "nilai": "Subdomain", "catatan": "Alamat resmi bisa punya banyak bagian seperti praktikum.gunadarma.ac.id."},
            {"label": "Penyebab 2", "nilai": "Path panjang", "catatan": "Layanan resmi kadang memakai link panjang untuk halaman tertentu."},
            {"label": "Penyebab 3", "nilai": "Data belum lengkap", "catatan": "Domain resmi baru bisa belum masuk daftar pembanding."},
        ],
        kolom=3,
    )

    tampilkan_bullets(
        "Cara membaca hasil beta",
        [
            "Terlihat Aman berarti sistem tidak menemukan sinyal risiko kuat.",
            "Perlu Tinjauan berarti jangan langsung panik, cek sumber dan domain utama.",
            "Berisiko berarti pola alamat sangat mirip phishing atau tiruan brand.",
            "Untuk website resmi yang sering salah terbaca, tambahkan ke data intelligence proyek pada tahap pengembangan berikutnya.",
        ],
    )

    panel(
        "Arah update berikutnya",
        "Versi berikutnya bisa menambah daftar domain resmi Indonesia, daftar kampus, perusahaan, marketplace, bank, instansi, serta mekanisme koreksi pengguna agar hasil makin stabil.",
        "gold",
    )


def halaman_panduan():
    hero(
        "Panduan",
        "Cara Menggunakan Website",
        "Ikuti langkah ini agar hasil pemeriksaan tidak dibaca secara membabi buta.",
    )

    tab_url, tab_file, tab_hasil = st.tabs(["Periksa URL", "Periksa file", "Membaca hasil"])

    with tab_url:
        tampilkan_bullets(
            "Langkah periksa URL",
            [
                "Buka halaman Input Alamat Link.",
                "Masukkan satu URL, paste banyak URL, atau unggah CSV.",
                "Klik tombol periksa.",
                "Baca hasil akhir, skor risiko, alasan, dan rekomendasi.",
                "Unduh CSV jika hasil perlu dilampirkan ke laporan.",
            ],
        )

    with tab_file:
        tampilkan_bullets(
            "Langkah periksa file",
            [
                "Buka halaman Input File.",
                "Unggah satu atau banyak file.",
                "Klik tombol periksa file.",
                "Baca hasil file dan URL yang ditemukan di dalam file.",
                "Jangan membuka file berisiko di perangkat utama.",
            ],
        )

    with tab_hasil:
        tampilkan_bullets(
            "Arti hasil",
            [
                "Terlihat Aman: sinyal risiko rendah berdasarkan pemeriksaan sistem.",
                "Perlu Tinjauan: perlu cek manual, biasanya karena pola tidak umum atau domain resmi dengan struktur panjang.",
                "Berisiko: jangan dibuka atau digunakan untuk login, transaksi, atau mengirim data pribadi.",
            ],
        )


def halaman_riwayat():
    hero(
        "Riwayat",
        "Riwayat Pemeriksaan",
        "Hasil pemeriksaan dari sesi Streamlit disimpan ke file CSV agar bisa dibaca ulang.",
    )

    data = pd.DataFrame(st.session_state.riwayat)

    if data.empty:
        st.info("Belum ada riwayat pemeriksaan.")
        return

    with st.container(border=True):
        st.dataframe(data, use_container_width=True, hide_index=True)

        kolom_a, kolom_b = st.columns(2)

        with kolom_a:
            st.download_button(
                "Unduh riwayat",
                data=data.to_csv(index=False).encode("utf-8"),
                file_name="riwayat_streamlit_phishrisk.csv",
                mime="text/csv",
            )

        with kolom_b:
            if st.button("Bersihkan riwayat"):
                st.session_state.riwayat = []
                if LOKASI_RIWAYAT_STREAMLIT.exists():
                    LOKASI_RIWAYAT_STREAMLIT.unlink()
                st.success("Riwayat berhasil dibersihkan.")
                st.rerun()


def halaman_tentang():
    hero(
        "Tentang Project",
        "PhishRisk System",
        "Project Data Science untuk mendeteksi indikasi phishing dari URL dan file secara defensif.",
    )

    panel(
        "Tujuan project",
        "Membangun sistem yang tidak hanya memberi label aman atau berisiko, tetapi juga menjelaskan alasan, memberikan rekomendasi, membaca file, membaca URL di dalam file, dan menyiapkan output yang bisa dipakai untuk laporan.",
        "gold",
    )

    metrik_kartu(
        [
            {"label": "Model", "nilai": "RF V2", "catatan": "Random Forest Intelligence V2 dari hasil retraining."},
            {"label": "Engine", "nilai": "V3", "catatan": "Gabungan model, URL intelligence, file analyzer, dan kalibrasi."},
            {"label": "Program", "nilai": "STEP 10", "catatan": "Sudah memiliki engine, CLI, dan Streamlit interface."},
        ],
        kolom=3,
    )

    tampilkan_bullets(
        "Alur program",
        [
            "Dataset phishing dibaca dan divalidasi.",
            "Model baseline dilatih dan diuji.",
            "Model URL manual dibuat agar bisa menerima URL baru.",
            "URL intelligence ditambahkan untuk domain resmi, brand tiruan, keyword mencurigakan, dan lookalike domain.",
            "File static analyzer ditambahkan untuk membaca file tanpa menjalankannya.",
            "Engine V3 dan CLI dibuat pada STEP 10.",
            "Streamlit ini menjadi antarmuka khusus yang berdiri sendiri dari penomoran step.",
        ],
    )

    with st.container(border=True):
        st.subheader("Author")

        kolom_1, kolom_2 = st.columns(2)

        with kolom_1:
            st.write(f"Nama: {AUTHOR_INFO['Nama']}")
            st.write("Bidang: Data Science, Machine Learning, dan Software Engineering")
            st.write("Fokus: sistem deteksi phishing yang mudah dipahami pengguna umum")

        with kolom_2:
            st.write(f"WhatsApp: {AUTHOR_INFO['WhatsApp']}")
            st.markdown(f"Instagram: [{AUTHOR_INFO['Instagram']}]({AUTHOR_INFO['Instagram']})")
            st.markdown(f"LinkedIn: [{AUTHOR_INFO['LinkedIn']}]({AUTHOR_INFO['LinkedIn']})")
            st.markdown(f"GitHub: [{AUTHOR_INFO['GitHub']}]({AUTHOR_INFO['GitHub']})")


def halaman_sistem():
    hero(
        "Informasi Sistem",
        "Kesiapan Komponen",
        "Halaman ini mengecek file penting agar user tahu aplikasi memakai program terbaru, bukan sisa kode lama yang pura-pura modern.",
    )

    daftar_file = [
        DIREKTORI_SRC / "phishrisk_engine_v3.py",
        DIREKTORI_SRC / "run_phishrisk.py",
        DIREKTORI_SRC / "url_intelligence.py",
        DIREKTORI_SRC / "file_static_analyzer.py",
        DIREKTORI_PROJECT / "models" / "model_terbaik_intelligence_v2.pkl",
        DIREKTORI_OUTPUT / "daftar_fitur_intelligence_v2.json",
        LOKASI_METADATA_STEP10,
        LOKASI_METADATA_ENGINE,
    ]

    data = []

    for lokasi in daftar_file:
        data.append(
            {
                "nama_file": lokasi.name,
                "lokasi": str(lokasi),
                "tersedia": lokasi.exists(),
                "ukuran_kb": round(lokasi.stat().st_size / 1024, 2) if lokasi.exists() else 0,
            }
        )

    data_validasi = pd.DataFrame(data)
    st.dataframe(data_validasi, use_container_width=True, hide_index=True)

    metadata_step10 = muat_metadata(LOKASI_METADATA_STEP10)
    metadata_engine = muat_metadata(LOKASI_METADATA_ENGINE)

    tab_step10, tab_engine = st.tabs(["Metadata STEP 10", "Metadata Engine V3"])

    with tab_step10:
        if metadata_step10:
            st.json(metadata_step10)
        else:
            st.info("Metadata STEP 10 belum ditemukan.")

    with tab_engine:
        if metadata_engine:
            st.json(metadata_engine)
        else:
            st.info("Metadata Engine V3 belum ditemukan.")


def halaman_batch_lab(engine):
    hero(
        "Batch Lab",
        "Ruang Analisis Banyak Data",
        "Halaman ini untuk membandingkan banyak URL atau banyak file secara lebih rapi, dengan prioritas, filter, dan ringkasan siap unduh.",
        ["Prioritas", "Filter", "Ringkasan", "Export CSV"],
    )

    tab_url, tab_file = st.tabs(["Batch URL", "Batch File terakhir"])

    with tab_url:
        data = st.session_state.hasil_url_terakhir
        if data.empty:
            panel("Belum ada data", "Periksa banyak URL terlebih dahulu dari halaman Input Alamat Link.", "yellow")
        else:
            tampilkan_ringkasan_url(data)
            with st.container(border=True):
                st.subheader("Filter hasil")
                daftar_status = sorted(data["hasil_akhir"].dropna().unique().tolist()) if "hasil_akhir" in data.columns else []
                status = st.multiselect("Pilih hasil", daftar_status, default=daftar_status)
                skor_min = st.slider("Skor minimum", 0, 100, 0)
                data_filter = data.copy()
                if status:
                    data_filter = data_filter[data_filter["hasil_akhir"].isin(status)]
                if "skor_final" in data_filter.columns:
                    data_filter = data_filter[data_filter["skor_final"] >= skor_min]
                tampilkan_tabel_url(data_filter)

    with tab_file:
        data_file = st.session_state.hasil_file_terakhir
        data_url = st.session_state.hasil_url_dalam_file_terakhir
        if data_file.empty:
            panel("Belum ada data", "Periksa file terlebih dahulu dari halaman Input File.", "yellow")
        else:
            tampilkan_ringkasan_file(data_file)
            tampilkan_tabel_file(data_file, data_url)



def buat_sidebar():
    st.sidebar.markdown(
        """
        <div class="panel compact gold">
            <div class="card-title">PhishRisk</div>
            <div class="muted">Pemeriksa URL dan file berbasis Engine V3.</div>
            <div class="small">Mode: URL, CSV, File, Multi File</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    halaman = st.sidebar.radio(
        "Menu",
        [
            "Beranda",
            "Input Alamat Link",
            "Input File",
            "Batch Lab",
            "Rekomendasi dan Antisipasi",
            "Ciri-Ciri",
            "Panduan",
            "Beta dan Salah Deteksi",
            "Riwayat",
            "Tentang Project",
            "Informasi Sistem",
        ],
        label_visibility="collapsed",
    )

    st.sidebar.markdown("---")
    st.sidebar.caption("Engine aktif: PhishRisk V3")
    st.sidebar.caption("Interface ini berdiri sendiri dari penomoran STEP.")

    return halaman



def main():
    pasang_css()
    siapkan_state()

    try:
        engine = muat_engine()
    except Exception as error:
        hero(
            "Aplikasi gagal dimuat",
            "Engine V3 Belum Siap",
            "Pastikan STEP 10 sudah selesai dan file phishrisk_engine_v3.py, model_terbaik_intelligence_v2.pkl, serta daftar_fitur_intelligence_v2.json tersedia.",
            ["Cek folder", "Cek model", "Cek src"],
        )
        st.exception(error)
        return

    halaman = buat_sidebar()

    if halaman == "Beranda":
        halaman_beranda(engine)
    elif halaman == "Input Alamat Link":
        halaman_periksa_url(engine)
    elif halaman == "Input File":
        halaman_periksa_file(engine)
    elif halaman == "Batch Lab":
        halaman_batch_lab(engine)
    elif halaman == "Rekomendasi dan Antisipasi":
        halaman_rekomendasi()
    elif halaman == "Ciri-Ciri":
        halaman_ciri()
    elif halaman == "Panduan":
        halaman_panduan()
    elif halaman == "Beta dan Salah Deteksi":
        halaman_beta()
    elif halaman == "Riwayat":
        halaman_riwayat()
    elif halaman == "Tentang Project":
        halaman_tentang()
    else:
        halaman_sistem()


if __name__ == "__main__":
    main()