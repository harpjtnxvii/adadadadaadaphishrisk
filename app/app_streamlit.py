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
    initial_sidebar_state="collapsed",
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
            --bg-0: #0b0c0b;
            --bg-1: #10110f;
            --bg-2: #151612;
            --bg-3: #1c1c18;
            --bg-4: #24221c;
            --text-0: #fff9ec;
            --text-1: #eee4d1;
            --text-2: #c8bda9;
            --text-3: #8f8677;
            --line: rgba(255,255,255,.075);
            --line-strong: rgba(222,184,107,.36);
            --gold: #d8b56d;
            --gold-soft: rgba(216,181,109,.13);
            --green: #9bc79f;
            --green-soft: rgba(155,199,159,.12);
            --yellow: #d6bd76;
            --yellow-soft: rgba(214,189,118,.13);
            --red: #e18478;
            --red-soft: rgba(225,132,120,.14);
            --shadow: 0 22px 70px rgba(0,0,0,.35);
            --shadow-soft: 0 14px 38px rgba(0,0,0,.25);
            --r-sm: 12px;
            --r-md: 18px;
            --r-lg: 24px;
            --r-xl: 34px;
            --font: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
        }

        html, body, [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 8% 0%, rgba(216,181,109,.12), transparent 30%),
                radial-gradient(circle at 100% 0%, rgba(255,255,255,.05), transparent 26%),
                linear-gradient(135deg, #0b0c0b 0%, #10110f 48%, #181510 100%) !important;
            color: var(--text-0) !important;
            font-family: var(--font) !important;
            scroll-behavior: smooth;
        }

        [data-testid="stHeader"], header { background: transparent !important; }
        #MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"], [data-testid="collapsedControl"] {
            visibility: hidden !important;
            display: none !important;
        }

        section[data-testid="stSidebar"] {
            display: none !important;
            width: 0 !important;
        }

        .block-container {
            max-width: 1180px;
            padding: .75rem 1.05rem 3rem 1.05rem;
        }

        * { box-sizing: border-box; }
        h1, h2, h3, h4, p, div, span, label, li, button, input, textarea { font-family: var(--font) !important; }
        h1 {
            font-size: clamp(2rem, 5vw, 4.7rem) !important;
            line-height: .97 !important;
            letter-spacing: -.065em !important;
            color: var(--text-0) !important;
            margin: 0 0 .65rem 0 !important;
        }
        h2 {
            font-size: clamp(1.35rem, 2.35vw, 2.25rem) !important;
            line-height: 1.08 !important;
            letter-spacing: -.045em !important;
            color: var(--text-0) !important;
            margin: .2rem 0 .55rem 0 !important;
        }
        h3 {
            font-size: clamp(1rem, 1.35vw, 1.25rem) !important;
            line-height: 1.23 !important;
            letter-spacing: -.025em !important;
            color: var(--text-0) !important;
        }
        p, li, div, label {
            font-size: clamp(.9rem, .92vw, .98rem) !important;
            line-height: 1.62 !important;
        }
        a { color: #ffe2a4 !important; text-decoration: none !important; }
        hr { border-color: var(--line) !important; }

        .main .block-container { animation: pageIn .28s ease-out; }
        @keyframes pageIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

        .top-nav-card {
            position: sticky;
            top: .45rem;
            z-index: 999;
            border: 1px solid rgba(255,255,255,.08);
            border-radius: 24px;
            background: rgba(14,15,13,.86);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            box-shadow: 0 18px 55px rgba(0,0,0,.38);
            padding: .72rem .78rem .38rem .78rem;
            margin: .15rem 0 1rem 0;
        }
        .top-nav-head {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: .75rem;
            padding: 0 .15rem .55rem .15rem;
        }
        .brand-block { display: flex; align-items: center; gap: .65rem; min-width: 0; }
        .brand-mark {
            width: 38px;
            height: 38px;
            border-radius: 14px;
            display: grid;
            place-items: center;
            border: 1px solid rgba(216,181,109,.45);
            background: linear-gradient(145deg, rgba(216,181,109,.20), rgba(255,255,255,.035));
            color: #ffe5aa;
            font-weight: 950;
            letter-spacing: -.08em;
        }
        .brand-title { color: var(--text-0); font-weight: 950; line-height: 1.05 !important; letter-spacing: -.045em; }
        .brand-sub { color: var(--text-3); font-size: .78rem !important; line-height: 1.1 !important; }
        .nav-badge {
            flex: 0 0 auto;
            border: 1px solid rgba(216,181,109,.32);
            background: rgba(216,181,109,.10);
            color: #ffe5aa;
            border-radius: 999px;
            padding: .28rem .65rem;
            font-size: .76rem !important;
            font-weight: 850;
        }

        div[role="radiogroup"] {
            display: flex !important;
            flex-wrap: wrap !important;
            gap: .42rem !important;
            align-items: stretch !important;
        }
        div[role="radio"] {
            min-height: 38px !important;
            border-radius: 999px !important;
            border: 1px solid rgba(255,255,255,.08) !important;
            background: rgba(255,255,255,.035) !important;
            padding: .38rem .72rem !important;
            transition: 150ms ease !important;
            box-shadow: none !important;
        }
        div[role="radio"] * { color: var(--text-2) !important; font-weight: 760 !important; font-size: .84rem !important; }
        div[role="radio"]:hover {
            transform: translateY(-1px);
            border-color: rgba(216,181,109,.44) !important;
            background: rgba(216,181,109,.10) !important;
        }
        div[role="radio"][aria-checked="true"] {
            border-color: rgba(216,181,109,.72) !important;
            background: linear-gradient(145deg, rgba(216,181,109,.22), rgba(255,255,255,.035)) !important;
        }
        div[role="radio"][aria-checked="true"] * { color: #fff4d8 !important; }

        .hero {
            position: relative;
            overflow: hidden;
            border: 1px solid var(--line);
            border-radius: var(--r-xl);
            background:
                radial-gradient(circle at 96% 0%, rgba(216,181,109,.17), transparent 30%),
                linear-gradient(135deg, rgba(255,255,255,.055), rgba(255,255,255,.014)),
                var(--bg-3);
            box-shadow: var(--shadow);
            padding: clamp(1rem, 3vw, 2.25rem);
            margin: .35rem 0 1rem 0;
        }
        .hero:before {
            content: "";
            position: absolute;
            inset: 0;
            background-image: linear-gradient(rgba(255,255,255,.025) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.018) 1px, transparent 1px);
            background-size: 42px 42px;
            opacity: .18;
            pointer-events: none;
        }
        .hero > * { position: relative; z-index: 2; }
        .hero-top { display: flex; justify-content: space-between; align-items: center; gap: .7rem; margin-bottom: .8rem; }
        .eyebrow {
            display: inline-flex;
            align-items: center;
            width: fit-content;
            border: 1px solid var(--line-strong);
            color: #ffe4aa;
            background: var(--gold-soft);
            border-radius: 999px;
            padding: .28rem .68rem;
            font-weight: 850;
            font-size: .74rem !important;
            letter-spacing: -.005em;
        }
        .hero-desc {
            max-width: 820px;
            color: var(--text-2);
            font-size: clamp(.94rem, 1vw, 1.04rem) !important;
            margin: 0 !important;
        }
        .hero-actions { display: flex; flex-wrap: wrap; gap: .42rem; margin-top: .95rem; }
        .pill {
            border-radius: 999px;
            border: 1px solid rgba(255,255,255,.08);
            background: rgba(255,255,255,.035);
            color: var(--text-2);
            padding: .3rem .65rem;
            font-size: .76rem !important;
            font-weight: 760;
        }

        .section-title { margin: 1.05rem 0 .55rem 0; }
        .panel {
            border: 1px solid var(--line);
            border-radius: var(--r-lg);
            background: linear-gradient(145deg, rgba(255,255,255,.043), rgba(255,255,255,.012)), var(--bg-3);
            box-shadow: var(--shadow-soft);
            padding: clamp(.9rem, 1.7vw, 1.25rem);
            margin-bottom: .8rem;
        }
        .panel.compact { padding: .85rem; border-radius: 18px; margin-bottom: .65rem; }
        .panel.gold { border-color: rgba(216,181,109,.34); background: linear-gradient(145deg, rgba(216,181,109,.13), rgba(255,255,255,.014)), var(--bg-3); }
        .panel.green { border-color: rgba(155,199,159,.34); background: linear-gradient(145deg, rgba(155,199,159,.12), rgba(255,255,255,.014)), var(--bg-3); }
        .panel.yellow { border-color: rgba(214,189,118,.38); background: linear-gradient(145deg, rgba(214,189,118,.13), rgba(255,255,255,.014)), var(--bg-3); }
        .panel.red { border-color: rgba(225,132,120,.38); background: linear-gradient(145deg, rgba(225,132,120,.14), rgba(255,255,255,.014)), var(--bg-3); }
        .panel.flat { box-shadow: none; background: rgba(255,255,255,.022); }
        .card-title { color: var(--text-0); font-weight: 900; font-size: clamp(1rem, 1.1vw, 1.18rem) !important; line-height: 1.22 !important; letter-spacing: -.028em; margin-bottom: .35rem; }
        .card-value { color: #fff5dc; font-size: clamp(1.35rem, 2vw, 2.05rem) !important; font-weight: 950; line-height: 1.03 !important; letter-spacing: -.05em; margin-bottom: .25rem; word-break: break-word; }
        .muted { color: var(--text-2); }
        .dim { color: var(--text-3); }
        .small { color: var(--text-3); font-size: .8rem !important; line-height: 1.45 !important; }
        .mini-list { margin: .25rem 0 0 0; padding: 0; list-style: none; }
        .mini-list li { border-top: 1px solid rgba(255,255,255,.06); padding: .58rem 0; color: var(--text-2); }
        .mini-list li:first-child { border-top: 0; }
        .callout { border: 1px solid rgba(255,255,255,.08); border-radius: var(--r-md); padding: .85rem; background: rgba(255,255,255,.025); margin: .45rem 0; }
        .callout.safe { border-color: rgba(155,199,159,.38); background: var(--green-soft); }
        .callout.review { border-color: rgba(214,189,118,.42); background: var(--yellow-soft); }
        .callout.danger { border-color: rgba(225,132,120,.42); background: var(--red-soft); }
        .score-line { height: 9px; border-radius: 999px; background: rgba(255,255,255,.08); overflow: hidden; border: 1px solid rgba(255,255,255,.055); margin: .65rem 0 .35rem 0; }
        .score-fill { height: 100%; border-radius: 999px; background: linear-gradient(90deg, var(--green), var(--yellow), var(--red)); }
        .risk-safe { border-color: rgba(155,199,159,.44) !important; background: radial-gradient(circle at 100% 0%, rgba(155,199,159,.18), transparent 28%), linear-gradient(145deg, rgba(155,199,159,.12), rgba(255,255,255,.015)), var(--bg-3) !important; }
        .risk-review { border-color: rgba(214,189,118,.48) !important; background: radial-gradient(circle at 100% 0%, rgba(214,189,118,.18), transparent 28%), linear-gradient(145deg, rgba(214,189,118,.13), rgba(255,255,255,.015)), var(--bg-3) !important; }
        .risk-danger { border-color: rgba(225,132,120,.50) !important; background: radial-gradient(circle at 100% 0%, rgba(225,132,120,.18), transparent 28%), linear-gradient(145deg, rgba(225,132,120,.14), rgba(255,255,255,.015)), var(--bg-3) !important; }
        .step-card { position: relative; padding-left: 3.75rem; min-height: 74px; }
        .step-number { position: absolute; left: .85rem; top: .85rem; width: 38px; height: 38px; border-radius: 14px; display: grid; place-items: center; background: rgba(216,181,109,.14); border: 1px solid rgba(216,181,109,.35); color: #ffe4aa; font-weight: 900; }

        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div, .stNumberInput input {
            background: #12130f !important;
            color: var(--text-0) !important;
            border: 1px solid rgba(255,255,255,.12) !important;
            border-radius: 16px !important;
            min-height: 44px !important;
            font-size: clamp(.9rem, .92vw, .98rem) !important;
            box-shadow: inset 0 1px 0 rgba(255,255,255,.025) !important;
        }
        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: rgba(216,181,109,.72) !important;
            box-shadow: 0 0 0 3px rgba(216,181,109,.12) !important;
        }
        [data-testid="stFileUploader"] section {
            background: linear-gradient(135deg, rgba(255,255,255,.035), rgba(255,255,255,.012)), #12130f !important;
            border: 1px dashed rgba(216,181,109,.50) !important;
            border-radius: var(--r-lg) !important;
            min-height: 112px;
        }
        [data-testid="stFileUploader"] button, .stButton > button, .stDownloadButton > button, button[kind="primary"] {
            width: 100%;
            min-height: 44px;
            border-radius: 16px !important;
            border: 1px solid rgba(216,181,109,.48) !important;
            background: linear-gradient(145deg, #342a1b, #211c15) !important;
            color: #ffe6ae !important;
            font-weight: 900 !important;
            box-shadow: 0 10px 24px rgba(0,0,0,.16) !important;
            transition: 150ms ease !important;
        }
        .stButton > button:hover, .stDownloadButton > button:hover, button[kind="primary"]:hover {
            transform: translateY(-1px);
            border-color: rgba(216,181,109,.78) !important;
            background: linear-gradient(145deg, #3e321f, #2a2216) !important;
        }
        [data-testid="stMetric"] { border: 1px solid var(--line); background: rgba(255,255,255,.024); border-radius: 18px; padding: .65rem .75rem; }
        [data-testid="stMetricValue"] { color: #fff5dc !important; font-size: clamp(1.18rem, 1.65vw, 1.62rem) !important; font-weight: 950 !important; letter-spacing: -.035em !important; white-space: normal !important; overflow: visible !important; text-overflow: unset !important; }
        [data-testid="stDataFrame"] { border-radius: var(--r-lg); overflow: hidden; border: 1px solid rgba(255,255,255,.08); box-shadow: var(--shadow-soft); }
        .stProgress > div > div > div > div { background: linear-gradient(90deg, var(--green), var(--yellow), var(--red)) !important; }
        .stAlert { border-radius: var(--r-lg) !important; border: 1px solid rgba(255,255,255,.08) !important; }
        .stTabs [data-baseweb="tab-list"] { gap: .38rem; flex-wrap: wrap; border-bottom: 0 !important; }
        .stTabs [data-baseweb="tab"] { border-radius: 999px; border: 1px solid rgba(255,255,255,.075); background: rgba(255,255,255,.025); padding: .34rem .7rem; color: var(--text-2) !important; }
        .stTabs [aria-selected="true"] { background: rgba(216,181,109,.15); border-color: rgba(216,181,109,.42); color: var(--text-0) !important; }
        div[data-testid="stExpander"] { border: 1px solid var(--line); background: rgba(255,255,255,.023); border-radius: var(--r-lg); overflow: hidden; }
        div[data-baseweb="popover"] [role="listbox"], div[data-baseweb="popover"] ul, [data-baseweb="menu"] {
            background: #11120f !important;
            color: var(--text-0) !important;
            border: 1px solid rgba(216,181,109,.34) !important;
            border-radius: 18px !important;
            box-shadow: 0 24px 70px rgba(0,0,0,.50) !important;
            padding: .35rem !important;
        }
        div[data-baseweb="popover"] li, div[data-baseweb="popover"] [role="option"], [data-baseweb="menu"] [role="option"] {
            color: var(--text-0) !important;
            background: transparent !important;
            border-radius: 12px !important;
            padding: .6rem .75rem !important;
        }
        div[data-baseweb="popover"] li:hover, div[data-baseweb="popover"] [role="option"]:hover, [data-baseweb="menu"] [role="option"]:hover {
            background: rgba(216,181,109,.14) !important;
            color: #ffe4aa !important;
        }
        .input-lab { border: 1px solid rgba(216,181,109,.24); border-radius: var(--r-xl); background: linear-gradient(145deg, rgba(216,181,109,.09), rgba(255,255,255,.015)), rgba(18,19,16,.74); box-shadow: var(--shadow-soft); padding: clamp(.9rem, 1.7vw, 1.2rem); margin-bottom: .9rem; }
        .idea-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: .75rem; margin-top: .55rem; }
        .idea-card { border: 1px solid rgba(255,255,255,.075); border-radius: 18px; background: rgba(255,255,255,.025); padding: .86rem; min-height: 112px; }
        .idea-card b { color: var(--text-0); font-size: .95rem; }
        .idea-card p { color: var(--text-2); margin: .35rem 0 0 0 !important; font-size: .84rem !important; line-height: 1.48 !important; }
        .soft-divider { height: 1px; background: linear-gradient(90deg, transparent, rgba(216,181,109,.38), transparent); margin: .85rem 0; }

        @media (max-width: 1366px) { .block-container { max-width: 1080px; } }
        @media (max-width: 1024px) {
            .block-container { max-width: 940px; padding-left: .8rem; padding-right: .8rem; }
            .hero { border-radius: 26px; }
            .idea-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        }
        @media (max-width: 768px) {
            .block-container { padding: .58rem .52rem 2.2rem .52rem; }
            [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
            .top-nav-card { top: .25rem; border-radius: 18px; padding: .58rem .58rem .32rem .58rem; margin-bottom: .75rem; }
            .top-nav-head { align-items: flex-start; padding-bottom: .45rem; }
            .brand-mark { width: 34px; height: 34px; border-radius: 12px; }
            .brand-sub { display: none; }
            .nav-badge { font-size: .68rem !important; padding: .22rem .5rem; }
            div[role="radiogroup"] { display: grid !important; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .34rem !important; }
            div[role="radio"] { min-height: 38px !important; justify-content: center !important; padding: .34rem .42rem !important; }
            div[role="radio"] * { font-size: .76rem !important; text-align: center !important; line-height: 1.2 !important; }
            .hero, .panel { border-radius: 18px; padding: .9rem; }
            .hero-top { display: flex; }
            h1 { font-size: clamp(1.9rem, 8vw, 2.7rem) !important; letter-spacing: -.058em !important; }
            .step-card { padding-left: .9rem; padding-top: 3.95rem; }
            .step-number { top: .85rem; left: .85rem; }
            .idea-grid { grid-template-columns: 1fr; }
        }
        @media (max-width: 520px) {
            .block-container { padding-left: .42rem; padding-right: .42rem; }
            p, li, div, label { font-size: .88rem !important; }
            .stButton > button, .stDownloadButton > button { min-height: 42px; }
            .eyebrow, .pill { font-size: .70rem !important; }
            .panel { margin-bottom: .62rem; }
            div[role="radiogroup"] { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            .card-value { font-size: 1.42rem !important; }
        }
        @media (max-width: 380px) {
            div[role="radiogroup"] { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )





def pasang_css_final_override():
    st.markdown(
        """
        <style>
        :root{
            --text-0:#fff9ec;
            --text-1:#eee4d1;
            --text-2:#c8bda9;
            --text-3:#928879;
            --gold-2:#ffe4aa;
            --gold-line:rgba(216,181,109,.42);
            --shadow-soft:0 14px 38px rgba(0,0,0,.26);
        }

        [data-testid="collapsedControl"],
        [data-testid="stSidebar"],
        section[data-testid="stSidebar"]{
            display:none!important;
            visibility:hidden!important;
            width:0!important;
            min-width:0!important;
        }

        .block-container{
            max-width:1180px!important;
            padding:.72rem 1.05rem 2.4rem!important;
        }

        /* NAVBAR */
        .top-nav-card{
            position:sticky!important;
            top:.42rem!important;
            z-index:999!important;
            border:1px solid rgba(255,255,255,.08)!important;
            border-radius:24px!important;
            background:rgba(14,15,13,.92)!important;
            backdrop-filter:blur(18px)!important;
            -webkit-backdrop-filter:blur(18px)!important;
            box-shadow:0 18px 55px rgba(0,0,0,.40)!important;
            padding:.72rem .78rem .78rem!important;
            margin:.12rem 0 1rem!important;
        }
        .top-nav-head{
            display:flex!important;
            align-items:center!important;
            justify-content:space-between!important;
            gap:.75rem!important;
            padding:0 .15rem .55rem!important;
        }
        .brand-block{display:flex!important;align-items:center!important;gap:.65rem!important;min-width:0!important;}
        .brand-mark{
            width:38px!important;height:38px!important;border-radius:14px!important;
            display:grid!important;place-items:center!important;
            border:1px solid rgba(216,181,109,.48)!important;
            background:linear-gradient(145deg,rgba(216,181,109,.21),rgba(255,255,255,.035))!important;
            color:var(--gold-2)!important;font-weight:950!important;letter-spacing:-.08em!important;
        }
        .brand-title{color:var(--text-0)!important;font-weight:950!important;line-height:1.05!important;letter-spacing:-.045em!important;}
        .brand-sub{color:var(--text-3)!important;font-size:.78rem!important;line-height:1.1!important;}
        .nav-badge{
            flex:0 0 auto!important;border:1px solid rgba(216,181,109,.34)!important;
            background:rgba(216,181,109,.11)!important;color:var(--gold-2)!important;
            border-radius:999px!important;padding:.28rem .65rem!important;
            font-size:.76rem!important;font-weight:850!important;
        }
        .nav-help{color:var(--text-3)!important;font-size:.76rem!important;margin-top:.42rem!important;line-height:1.35!important;}

        .stSelectbox div[data-baseweb="select"]>div{
            background:#12130f!important;color:var(--text-0)!important;
            border:1px solid rgba(216,181,109,.38)!important;border-radius:16px!important;
            min-height:48px!important;box-shadow:inset 0 1px 0 rgba(255,255,255,.025)!important;
        }

        /* FILE UPLOADER: rapi, tidak numpuk, tidak mengubah tombol remove file */
        [data-testid="stFileUploader"]{
            border:1px solid rgba(255,255,255,.055)!important;
            border-radius:24px!important;
            background:linear-gradient(145deg,rgba(255,255,255,.026),rgba(255,255,255,.01))!important;
            padding:1rem!important;
        }
        [data-testid="stFileUploaderDropzone"],
        [data-testid="stFileUploader"] section{
            background:linear-gradient(135deg,rgba(255,255,255,.035),rgba(255,255,255,.012)),#12130f!important;
            border:1px dashed rgba(216,181,109,.58)!important;
            border-radius:24px!important;
            min-height:170px!important;
            display:flex!important;
            align-items:center!important;
            justify-content:center!important;
            text-align:center!important;
            padding:1.1rem!important;
        }
        [data-testid="stFileUploaderDropzone"] > div,
        [data-testid="stFileUploader"] section > div{
            width:100%!important;
            display:flex!important;
            flex-direction:column!important;
            align-items:center!important;
            justify-content:center!important;
            gap:.65rem!important;
        }
        [data-testid="stFileUploaderDropzone"] small,
        [data-testid="stFileUploaderDropzone"] span,
        [data-testid="stFileUploaderDropzone"] div,
        [data-testid="stFileUploader"] section small,
        [data-testid="stFileUploader"] section span,
        [data-testid="stFileUploader"] section div{
            color:var(--text-2)!important;
            white-space:normal!important;
            text-align:center!important;
        }

        /* Tombol utama upload saja */
        [data-testid="stFileUploaderDropzone"] button{
            width:auto!important;
            min-width:230px!important;
            max-width:310px!important;
            min-height:58px!important;
            border-radius:999px!important;
            display:inline-flex!important;
            align-items:center!important;
            justify-content:center!important;
            padding:0 1.35rem!important;
            margin:0 auto!important;
            font-size:0!important;
            overflow:hidden!important;
            white-space:nowrap!important;
            border:1px solid rgba(216,181,109,.56)!important;
            background:linear-gradient(145deg,#372b1a,#201a11)!important;
            box-shadow:0 18px 40px rgba(0,0,0,.28)!important;
        }
        [data-testid="stFileUploaderDropzone"] button *{
            font-size:0!important;
            color:transparent!important;
            width:0!important;
            opacity:0!important;
        }
        [data-testid="stFileUploaderDropzone"] button:before{
            content:"Pilih file"!important;
            font-size:1.15rem!important;
            line-height:1!important;
            font-weight:950!important;
            color:var(--gold-2)!important;
            white-space:nowrap!important;
            text-align:center!important;
            opacity:1!important;
        }

        /* Baris file yang sudah dipilih: jangan ikut dipaksa jadi tombol besar */
        [data-testid="stFileUploaderFile"]{
            background:rgba(255,255,255,.06)!important;
            border:1px solid rgba(255,255,255,.08)!important;
            border-radius:16px!important;
            padding:.5rem!important;
        }
        [data-testid="stFileUploaderFile"] button{
            min-width:34px!important;
            width:34px!important;
            height:34px!important;
            min-height:34px!important;
            padding:0!important;
            border-radius:10px!important;
            font-size:.8rem!important;
        }
        [data-testid="stFileUploaderFile"] button:before{content:""!important;display:none!important;}

        [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] button,
        [data-testid="stFileUploaderFile"] button{
            min-width:34px!important;
            width:34px!important;
            max-width:34px!important;
            height:34px!important;
            min-height:34px!important;
            padding:0!important;
            border-radius:10px!important;
            font-size:.8rem!important;
            color:var(--text-0)!important;
            background:rgba(255,255,255,.08)!important;
        }
        [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] button *,
        [data-testid="stFileUploaderFile"] button *{
            font-size:.8rem!important;
            color:var(--text-0)!important;
            width:auto!important;
            opacity:1!important;
        }
        [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] button:before,
        [data-testid="stFileUploaderFile"] button:before{
            content:none!important;
            display:none!important;
        }


        /* Tombol umum */
        .stButton > button,
        .stDownloadButton > button,
        button[kind="primary"]{
            min-height:44px!important;border-radius:16px!important;
            border:1px solid rgba(216,181,109,.48)!important;
            background:linear-gradient(145deg,#342a1b,#211c15)!important;
            color:#ffe6ae!important;font-weight:900!important;
            box-shadow:0 10px 24px rgba(0,0,0,.16)!important;transition:150ms ease!important;
        }
        .stButton > button:hover,
        .stDownloadButton > button:hover,
        button[kind="primary"]:hover{
            transform:translateY(-1px);
            border-color:rgba(216,181,109,.78)!important;
            background:linear-gradient(145deg,#3e321f,#2a2216)!important;
        }

        /* TABEL HTML GELAP, pengganti st.dataframe supaya tidak muncul menu putih yang nabrak */
        .table-shell{
            width:100%;
            overflow-x:auto;
            border:1px solid rgba(255,255,255,.075);
            border-radius:20px;
            background:rgba(255,255,255,.025);
            box-shadow:var(--shadow-soft);
            margin:.55rem 0 1rem 0;
        }
        table.clean-table{
            width:100%;
            border-collapse:separate;
            border-spacing:0;
            min-width:720px;
        }
        .clean-table th{
            position:sticky;
            top:0;
            z-index:1;
            background:#191a16;
            color:#ffe4aa;
            font-weight:850;
            text-align:left;
            padding:.72rem .78rem;
            border-bottom:1px solid rgba(216,181,109,.25);
            font-size:.83rem!important;
            white-space:nowrap;
        }
        .clean-table td{
            color:#eee4d1;
            padding:.68rem .78rem;
            border-bottom:1px solid rgba(255,255,255,.055);
            font-size:.82rem!important;
            line-height:1.42!important;
            vertical-align:top;
            max-width:460px;
            overflow-wrap:anywhere;
        }
        .clean-table tr:nth-child(even) td{background:rgba(255,255,255,.018);}
        .clean-table tr:hover td{background:rgba(216,181,109,.06);}
        .table-note{
            color:var(--text-3);
            font-size:.78rem!important;
            margin:.35rem 0 .1rem 0;
        }

        .site-footer{
            margin:1.35rem 0 .45rem!important;
            border:1px solid rgba(255,255,255,.08)!important;
            border-radius:24px!important;
            background:linear-gradient(145deg,rgba(216,181,109,.10),rgba(255,255,255,.014)),rgba(18,19,16,.82)!important;
            padding:1rem!important;
            box-shadow:var(--shadow-soft)!important;
        }
        .footer-grid{
            display:grid!important;
            grid-template-columns:1.1fr .9fr!important;
            gap:.75rem!important;
            align-items:center!important;
        }
        .footer-name{font-size:1.05rem!important;font-weight:950!important;color:var(--text-0)!important;letter-spacing:-.03em!important;}
        .footer-note{color:var(--text-3)!important;font-size:.82rem!important;line-height:1.45!important;}
        .footer-links{display:flex!important;flex-wrap:wrap!important;gap:.45rem!important;justify-content:flex-end!important;}
        .footer-link{
            border:1px solid rgba(216,181,109,.30)!important;background:rgba(216,181,109,.08)!important;
            border-radius:999px!important;padding:.30rem .62rem!important;color:var(--gold-2)!important;
            font-size:.78rem!important;font-weight:820!important;
        }
        .footer-line{
            margin-top:.65rem;
            padding-top:.65rem;
            border-top:1px solid rgba(255,255,255,.07);
            color:var(--text-3);
            font-size:.76rem!important;
        }

        @media(max-width:1024px){
            .block-container{max-width:940px!important;padding-left:.8rem!important;padding-right:.8rem!important;}
            table.clean-table{min-width:660px;}
        }
        @media(max-width:768px){
            .block-container{padding:.56rem .52rem 2.05rem!important;}
            [data-testid="column"]{width:100%!important;flex:1 1 100%!important;}
            .top-nav-card{top:.22rem!important;border-radius:18px!important;padding:.58rem .58rem .65rem!important;margin-bottom:.72rem!important;}
            .top-nav-head{align-items:flex-start!important;padding-bottom:.45rem!important;}
            .brand-mark{width:34px!important;height:34px!important;border-radius:12px!important;}
            .brand-sub{display:none!important;}
            .nav-badge{font-size:.68rem!important;padding:.22rem .5rem!important;}
            .hero,.panel{border-radius:18px!important;padding:.9rem!important;}
            h1{font-size:clamp(1.85rem,7.8vw,2.65rem)!important;letter-spacing:-.056em!important;}
            [data-testid="stFileUploaderDropzone"],
            [data-testid="stFileUploader"] section{min-height:188px!important;padding:1rem!important;}
            [data-testid="stFileUploaderDropzone"] button{min-width:230px!important;min-height:58px!important;}
            [data-testid="stFileUploaderDropzone"] button:before{font-size:1.16rem!important;}
            .footer-grid{grid-template-columns:1fr!important;}
            .footer-links{justify-content:flex-start!important;}
            table.clean-table{min-width:620px;}
        }
        @media(max-width:520px){
            .block-container{padding-left:.42rem!important;padding-right:.42rem!important;}
            p,li,div,label{font-size:.88rem!important;}
            .top-nav-card{border-radius:16px!important;}
            .brand-title{font-size:.92rem!important;}
            [data-testid="stFileUploaderDropzone"],
            [data-testid="stFileUploader"] section{min-height:196px!important;}
            [data-testid="stFileUploaderDropzone"] button{min-width:226px!important;}
            .clean-table th,.clean-table td{font-size:.78rem!important;padding:.62rem .64rem;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def pasang_css_v8_polish():
    st.markdown(
        """
        <style>
        .system-summary-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.75rem;margin:.65rem 0 1rem}
        .system-pill{border:1px solid rgba(255,255,255,.08);border-radius:20px;background:linear-gradient(145deg,rgba(255,255,255,.045),rgba(255,255,255,.012));padding:.9rem;box-shadow:0 14px 38px rgba(0,0,0,.24)}
        .system-pill b{display:block;color:#fff9ec;font-size:1rem!important;letter-spacing:-.02em;margin-bottom:.2rem}
        .system-pill span{color:#c8bda9;font-size:.82rem!important;line-height:1.45!important}
        .game-board{border:1px solid rgba(216,181,109,.35);border-radius:28px;background:radial-gradient(circle at 100% 0%,rgba(216,181,109,.12),transparent 26%),linear-gradient(145deg,rgba(216,181,109,.10),rgba(255,255,255,.014)),rgba(18,19,16,.86);padding:1rem;box-shadow:0 18px 55px rgba(0,0,0,.30);margin:.8rem 0}
        .game-url{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace!important;color:#ffe7ad!important;background:rgba(0,0,0,.26);border:1px solid rgba(216,181,109,.22);border-radius:18px;padding:.85rem;overflow-wrap:anywhere;font-size:.95rem!important;line-height:1.5!important}
        .game-score{display:flex;gap:.5rem;flex-wrap:wrap;margin:.7rem 0}.game-score span{border:1px solid rgba(255,255,255,.08);border-radius:999px;padding:.32rem .65rem;background:rgba(255,255,255,.035);color:#c8bda9;font-size:.8rem!important;font-weight:800!important}
        .info-strip{border:1px solid rgba(216,181,109,.26);border-radius:22px;background:linear-gradient(145deg,rgba(216,181,109,.08),rgba(255,255,255,.012));padding:.85rem 1rem;margin:.65rem 0;color:#c8bda9!important}
        .site-footer{margin-top:1.2rem!important}.footer-line{margin-top:.65rem!important;padding-top:.65rem!important;border-top:1px solid rgba(255,255,255,.07)!important;color:#928879!important;font-size:.78rem!important;line-height:1.45!important}
        .clean-table td:nth-child(2){overflow-wrap:anywhere}.clean-table td,.clean-table th{vertical-align:top!important}
        @media(max-width:900px){.system-summary-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
        @media(max-width:560px){.system-summary-grid{grid-template-columns:1fr}.game-board{border-radius:20px;padding:.85rem}.game-url{font-size:.82rem!important}.footer-link{font-size:.72rem!important;padding:.28rem .5rem!important}}
        </style>
        """,
        unsafe_allow_html=True,
    )

def aman_teks(nilai):
    return html_escape.escape(str(nilai))


def html(teks):
    st.markdown(teks, unsafe_allow_html=True)





def widget_key(prefix):
    """Key unik untuk widget dinamis."""
    nama_counter = "_counter_" + str(prefix)
    st.session_state[nama_counter] = st.session_state.get(nama_counter, 0) + 1
    return f"{prefix}_{st.session_state[nama_counter]}"


def tabel_rapi(data, max_rows=80, caption=None):
    """Tabel HTML gelap agar tidak muncul menu dataframe putih yang bentrok dengan tema."""
    try:
        df = pd.DataFrame(data).copy()
    except Exception:
        st.write(data)
        return

    if df.empty:
        st.info("Belum ada data untuk ditampilkan.")
        return

    jumlah_asli = len(df)
    if max_rows is not None:
        df = df.head(max_rows)

    # Ringkas nilai yang terlalu panjang agar layout tetap rapi.
    df = df.fillna("-")
    for kolom in df.columns:
        df[kolom] = df[kolom].map(lambda x: str(x))

    head_html = "".join([f"<th>{aman_teks(kolom)}</th>" for kolom in df.columns])
    rows_html = []
    for _, row in df.iterrows():
        cols_html = "".join([f"<td>{aman_teks(row[kolom])}</td>" for kolom in df.columns])
        rows_html.append(f"<tr>{cols_html}</tr>")

    note = caption or f"Menampilkan {len(df)} dari {jumlah_asli} baris."
    html(
        f"""
        <div class="table-shell">
            <table class="clean-table">
                <thead><tr>{head_html}</tr></thead>
                <tbody>{''.join(rows_html)}</tbody>
            </table>
        </div>
        <div class="table-note">{aman_teks(note)}</div>
        """
    )
def hero(label, judul, deskripsi, badges=None):
    badges = badges or []
    badge_html = "".join([f'<span class="pill">{aman_teks(item)}</span>' for item in badges])
    html(
        f"""
        <section class="hero">
            <div class="hero-top">
                <div class="eyebrow">{aman_teks(label)}</div>
                <div class="pill">harpjtn</div>
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
    """Judul antar bagian agar layout tetap rapi."""
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
            tabel_rapi(data, max_rows=80)
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
        tabel_rapi(data_alasan, max_rows=80)

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
        tabel_rapi(pd.DataFrame([hasil]), max_rows=80)


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

    tabel_rapi(data[kolom], max_rows=80)

    st.download_button(
        "Unduh hasil URL",
        data=data.to_csv(index=False).encode("utf-8"),
        file_name="hasil_url_phishrisk_streamlit.csv",
        mime="text/csv",
        key=widget_key("download_hasil_url"),
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
    tabel_rapi(data_file[kolom_file], max_rows=80)

    st.download_button(
        "Unduh hasil file",
        data=data_file.to_csv(index=False).encode("utf-8"),
        file_name="hasil_file_phishrisk_streamlit.csv",
        mime="text/csv",
        key=widget_key("download_hasil_file"),
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
            tabel_rapi(ringkasan, max_rows=80)
    with kolom_2:
        with st.container(border=True):
            st.subheader("Prioritas pengecekan")
            prioritas = data.sort_values("skor_final", ascending=False).head(10)
            kolom_prioritas = [kolom for kolom in ["url", "skor_final", "hasil_akhir", "kategori_risiko", "intelligence_status"] if kolom in prioritas.columns]
            tabel_rapi(prioritas[kolom_prioritas], max_rows=80)

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
            tabel_rapi(ringkasan, max_rows=80)
    with kolom_2:
        with st.container(border=True):
            st.subheader("File prioritas")
            prioritas = data.sort_values("skor_final_file_v3", ascending=False).head(10)
            kolom_prioritas = [kolom for kolom in ["nama_file", "ekstensi", "skor_final_file_v3", "kategori_final_file_v3", "hasil_akhir_file_v3"] if kolom in prioritas.columns]
            tabel_rapi(prioritas[kolom_prioritas], max_rows=80)

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
            <div class="idea-card"><b>Bandingkan hasil</b><p>Gunakan Engine Lab untuk melihat peringkat skor, kategori, alasan, dan rekomendasi secara lebih rapi.</p></div>
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
    section_title("Uji Coba", "Masukkan URL bebas, banyak URL, atau paket uji cepat.")

    html('<div class="input-lab">')
    tab_satu, tab_banyak, tab_set, tab_ide = st.tabs(["Satu URL bebas", "Banyak URL bebas", "Paket uji cepat", "Ide pengujian"])

    with tab_satu:
        st.write("Masukkan alamat bebas untuk menguji sistem secara langsung.")
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
        st.write("Tempel banyak alamat sekaligus. Sistem akan mengambil URL yang ditemukan.")
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
            tabel_rapi(pd.DataFrame({"url": daftar}), max_rows=80)

        if st.button("Periksa daftar bebas", key="beranda_periksa_daftar_bebas"):
            jalankan_uji_banyak_url(engine, daftar)

    with tab_set:
        st.write("Pilih paket uji cepat untuk membandingkan website resmi dan contoh alamat berisiko.")
        nama_paket = st.selectbox("Pilih paket uji", list(DATASET_UJI_CEPAT.keys()), key="beranda_paket_uji")
        daftar_paket = DATASET_UJI_CEPAT[nama_paket]
        tabel_rapi(pd.DataFrame({"url": daftar_paket}), max_rows=80)
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
                key=widget_key("download_paket_uji"),
            )

    with tab_ide:
        tampilkan_ide_uji()
        panel(
            "Ide update berikutnya",
            "Tambahkan laporan PDF, import domain resmi, catatan koreksi user, dan evaluasi salah deteksi.",
            "gold",
        )

    html('</div>')


def halaman_beranda(engine):
    hero(
        "PhishRisk System",
        "Pemeriksa URL dan File",
        "Cek URL, banyak URL, file, dan URL di dalam file. Ringkas, cepat, dan defensif.",
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
        panel("Batasan penting", "Sistem tidak membuka website langsung dan tidak menjalankan file. Hasil dipakai sebagai bantuan awal sebelum klik, login, atau unduh.", "yellow")
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

    section_title("Coba Cepat Template", "Gunakan contoh bawaan hanya sebagai pembanding cepat.")
    with st.container(border=True):
        pilihan = st.selectbox("Pilih contoh URL", CONTOH_URL, key="beranda_selectbox_template")
        kolom_a, kolom_b = st.columns([1, 1])
        with kolom_a:
            tombol = st.button("Periksa contoh URL", key="beranda_cek_cepat")
        with kolom_b:
            st.download_button(
                "Unduh contoh URL",
                data=pd.DataFrame({"url": CONTOH_URL}).to_csv(index=False).encode("utf-8"),
                file_name="contoh_url_phishrisk.csv",
                mime="text/csv",
                key=widget_key("download_contoh_url_beranda"),
            )
        if tombol:
            jalankan_uji_satu_url(engine, pilihan, sumber="template")

    section_title("Kesiapan Sistem", "Sistem terus diperbarui dengan model terbaru dan daftar pembanding resmi. Berikut adalah hasil validasi internal untuk memastikan kualitas tetap terjaga.")
    validasi = muat_validasi_step10()
    if validasi.empty:
        st.info("File validasi STEP 10 belum ditemukan.")
    else:
        tabel_rapi(validasi, max_rows=80)


def halaman_periksa_url(engine):
    hero(
        "Pemeriksaan URL",
        "Input Alamat Link",
        "Masukkan satu URL, banyak URL, atau CSV. Semua memakai Best Engine.",
    )

    panel("Mode uji bebas", "Masukkan URL sendiri, domain resmi, link mencurigakan, atau daftar URL bebas.", "gold")

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
                    key=widget_key("download_contoh_url_periksa"),
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
            tabel_rapi(pd.DataFrame({"url": daftar}), max_rows=80)

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
                key=widget_key("download_template_csv"),
            )

        if file_csv is not None:
            data_csv = pd.read_csv(file_csv)
            tabel_rapi(data_csv.head(20), max_rows=80)

            kolom_url = st.selectbox("Pilih kolom URL", data_csv.columns.tolist())

            if st.button("Periksa URL dari CSV", key="tombol_periksa_url_dari_csv"):
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
        "Input File Bebas",
        "Unggah satu atau banyak file. Sistem membaca risiko secara statis tanpa menjalankan file.",
        ["PDF", "DOCX", "ZIP", "APK", "TXT", "HTML"],
    )

    metrik_kartu([
        {"label": "Mode", "nilai": "Statis", "catatan": "File tidak dijalankan.", "warna": "green"},
        {"label": "Output", "nilai": "CSV", "catatan": "Hasil bisa diunduh.", "warna": "gold"},
        {"label": "Fokus", "nilai": "URL", "catatan": "Mencari link di file.", "warna": "yellow"},
    ], kolom=3)

    panel("Jenis file", "Uploader menerima berbagai ekstensi. Pemeriksaan terbaik untuk TXT, HTML, PDF, DOCX, ZIP, dan APK. File lain tetap dibaca metadata dasarnya.", "gold")
    bullet_panel("Yang dicek", ["URL yang tertanam di dalam file.", "Kata yang sering dipakai pada penipuan.", "Ekstensi, ukuran, hash, dan tanda file berisiko.", "Hasil akhir dapat diunduh sebagai CSV."], "normal")

    with st.container(border=True):
        daftar_file = st.file_uploader(
            "Unggah file",
            accept_multiple_files=True,
            type=None,
            help="Sistem tidak menjalankan file. Aman untuk pemeriksaan awal.",
            key="uploader_file_bebas_final",
        )

        if daftar_file:
            data_info = pd.DataFrame([
                {"nama_file": file.name, "ukuran_kb": round(file.size / 1024, 2), "tipe_browser": file.type or "tidak_diketahui"}
                for file in daftar_file
            ])
            tabel_rapi(data_info, max_rows=80)

        tombol = st.button("Periksa file", key="tombol_periksa_file_final")

    if tombol:
        if not daftar_file:
            st.warning("Unggah minimal satu file terlebih dahulu.")
            return

        daftar_hasil_file = []
        daftar_hasil_url = []

        with st.spinner("Memeriksa file secara statis..."):
            for file in daftar_file:
                lokasi = simpan_file_upload(file)
                data_file, data_url = engine.analisis_file(lokasi)

                if isinstance(data_file, pd.DataFrame):
                    df_file = data_file.copy()
                elif isinstance(data_file, dict):
                    df_file = pd.DataFrame([data_file])
                else:
                    df_file = pd.DataFrame([{"nama_file": file.name}])

                df_file["nama_file"] = file.name
                df_file["sha256_upload"] = hash_file(lokasi)
                daftar_hasil_file.append(df_file)

                for row in df_file.to_dict("records"):
                    tambah_riwayat_file(row)

                if isinstance(data_url, pd.DataFrame) and not data_url.empty:
                    df_url = data_url.copy()
                    df_url["nama_file_sumber"] = file.name
                    daftar_hasil_url.append(df_url)

        data_file_final = pd.concat(daftar_hasil_file, ignore_index=True) if daftar_hasil_file else pd.DataFrame()
        data_url_final = pd.concat(daftar_hasil_url, ignore_index=True) if daftar_hasil_url else pd.DataFrame()

        st.session_state.hasil_file_terakhir = data_file_final
        st.session_state.hasil_url_dalam_file_terakhir = data_url_final

        tampilkan_ringkasan_file(data_file_final)
        tampilkan_tabel_file(data_file_final, data_url_final)

    if not st.session_state.hasil_file_terakhir.empty:
        with st.expander("Lihat hasil file terakhir"):
            tampilkan_tabel_file(st.session_state.hasil_file_terakhir, st.session_state.hasil_url_dalam_file_terakhir)


def halaman_rekomendasi():
    hero(
        "Rekomendasi",
        "Apa yang Harus Dilakukan?",
        "Saran singkat berdasarkan hasil sistem. Fokus pada langkah aman yang mudah dilakukan.",
        ["Aman", "Tinjauan", "Berisiko", "File"],
    )

    metrik_kartu(
        [
            {"label": "Terlihat Aman", "nilai": "Cek", "catatan": "Tetap pastikan domain utama.", "warna": "green"},
            {"label": "Perlu Tinjauan", "nilai": "Tahan", "catatan": "Bandingkan dengan sumber resmi.", "warna": "yellow"},
            {"label": "Berisiko", "nilai": "Hindari", "catatan": "Jangan isi data apa pun.", "warna": "red"},
            {"label": "File", "nilai": "Statis", "catatan": "Jangan jalankan file asing.", "warna": "gold"},
        ],
        kolom=4,
    )

    tab_aman, tab_tinjauan, tab_risiko, tab_file, tab_terlanjur = st.tabs(
        ["Aman", "Tinjauan", "Berisiko", "File", "Terlanjur klik"]
    )

    with tab_aman:
        col_1, col_2 = st.columns(2)
        with col_1:
            bullet_panel(
                "Boleh lanjut, tapi tetap sadar diri",
                [
                    "Ketik domain manual atau buka dari bookmark.",
                    "Pastikan domain utama benar, bukan sekadar tampilan logo.",
                    "Gunakan aplikasi resmi untuk bank dan e-commerce.",
                    "Cek ulang jika halaman meminta login ulang mendadak.",
                ],
                "green",
            )
        with col_2:
            bullet_panel(
                "Tetap jangan asal klik",
                [
                    "Jangan klik link dari pesan yang memaksa.",
                    "Jangan kirim OTP, PIN, atau kode verifikasi.",
                    "Jangan unduh file tambahan dari halaman tidak jelas.",
                    "Jangan percaya hanya karena tampilannya rapi.",
                ],
                "yellow",
            )

    with tab_tinjauan:
        col_1, col_2 = st.columns(2)
        with col_1:
            bullet_panel(
                "Cek manual",
                [
                    "Cari domain resmi lewat sumber resmi.",
                    "Bandingkan huruf, angka, tanda hubung, dan subdomain.",
                    "Cek pengirim link.",
                    "Hubungi admin resmi jika berkaitan dengan kampus, bank, atau perusahaan.",
                ],
                "yellow",
            )
        with col_2:
            bullet_panel(
                "Sikap aman",
                [
                    "Tahan dulu sebelum login.",
                    "Jangan masukkan data pembayaran.",
                    "Gunakan perangkat aman untuk pengecekan lanjutan.",
                    "Simpan hasil pemeriksaan sebagai bukti.",
                ],
                "gold",
            )

    with tab_risiko:
        col_1, col_2 = st.columns(2)
        with col_1:
            bullet_panel(
                "Tindakan cepat",
                [
                    "Jangan buka link.",
                    "Jangan login.",
                    "Jangan isi OTP, PIN, password, atau nomor kartu.",
                    "Laporkan ke admin, bank, kampus, atau pihak terkait.",
                ],
                "red",
            )
        with col_2:
            bullet_panel(
                "Ciri yang perlu dicurigai",
                [
                    "Nama brand digabung login, verify, update, secure, atau account.",
                    "Huruf diganti angka, misalnya micros0ft.",
                    "Domain terlihat mirip brand resmi.",
                    "Path terlalu panjang dan penuh parameter.",
                ],
                "yellow",
            )

    with tab_file:
        col_1, col_2 = st.columns(2)
        with col_1:
            bullet_panel(
                "Jangan jalankan",
                [
                    "EXE, APK, LNK, BAT, CMD, PS1, dan VBS dari sumber tidak jelas.",
                    "ZIP/RAR yang berisi file aneh.",
                    "Dokumen yang meminta macro aktif.",
                    "PDF yang mengarah ke login palsu.",
                ],
                "red",
            )
        with col_2:
            bullet_panel(
                "Cara aman memeriksa file",
                [
                    "Gunakan pemeriksaan statis terlebih dahulu.",
                    "Cek URL yang tertanam di file.",
                    "Periksa sumber pengirim.",
                    "Simpan laporan CSV jika butuh bukti.",
                ],
                "green",
            )

    with tab_terlanjur:
        bullet_panel(
            "Jika sudah terlanjur klik atau login",
            [
                "Segera ganti password dari website atau aplikasi resmi.",
                "Keluar dari semua sesi akun.",
                "Aktifkan verifikasi dua langkah.",
                "Hubungi layanan resmi jika berkaitan dengan bank, kampus, kantor, atau e-commerce.",
                "Simpan bukti pesan dan hasil pemeriksaan.",
            ],
            "red",
        )

def halaman_ciri():
    hero(
        "Ciri-Ciri",
        "Pola yang Perlu Dibaca",
        "Ringkasan ciri URL aman, mencurigakan, dan file berisiko dengan bahasa sederhana.",
    )

    col_1, col_2, col_3 = st.columns(3)
    with col_1:
        bullet_panel("Cenderung aman", ["Domain utama jelas.", "HTTPS aktif.", "Sumber link resmi.", "Tidak memaksa login.", "Tidak meminta OTP."], "green")
    with col_2:
        bullet_panel("URL mencurigakan", ["Mirip brand resmi.", "Ada login/update/verify.", "Huruf diganti angka.", "Subdomain terlalu panjang.", "Path penuh parameter."], "yellow")
    with col_3:
        bullet_panel("File berisiko", ["Script atau executable.", "Meminta macro aktif.", "Arsip berisi file aneh.", "APK dari luar toko resmi.", "PDF berisi link login."], "red")

    section_title("Contoh Pola Tiruan", "Beberapa contoh pola yang sering terlihat sepele, tapi bisa berbahaya.")
    data = pd.DataFrame([
        {"Pola": "rricrosoft.com", "Masalah": "Mirip microsoft.com."},
        {"Pola": "rnicrosoft.com", "Masalah": "r+n bisa terlihat seperti m."},
        {"Pola": "micros0ft-login-update.test", "Masalah": "0 mengganti o dan memakai kata mendesak."},
        {"Pola": "bca-login-update.test", "Masalah": "Nama brand bukan domain resmi."},
        {"Pola": "xn--micrsoft-q4a.test", "Masalah": "Punycode menyamarkan domain."},
    ])
    tabel_rapi(data, max_rows=20)

    section_title("Cara cek cepat", "Gunakan pola sederhana ini sebelum percaya pada link.")
    col_a, col_b = st.columns(2)
    with col_a:
        bullet_panel("Cek domain", ["Lihat domain utama.", "Waspadai huruf mirip.", "Waspadai angka pengganti huruf.", "Cek tanda hubung berlebihan."], "gold")
    with col_b:
        bullet_panel("Cek perilaku halaman", ["Apakah meminta login?", "Apakah meminta OTP?", "Apakah memaksa update akun?", "Apakah mengarahkan unduhan file?"], "yellow")

def halaman_beta():
    hero(
        "Beta",
        "Salah Deteksi Itu Mungkin",
        "Website resmi bisa terbaca perlu tinjauan jika bentuk URL-nya tidak umum.",
    )

    panel("Inti masalah", "Model membaca pola alamat. Ia tidak selalu tahu kepemilikan website kecuali domain resmi sudah masuk data intelligence.", "yellow")
    metrik_kartu([
        {"label": "Penyebab", "nilai": "Subdomain", "catatan": "Contoh: praktikum.gunadarma.ac.id."},
        {"label": "Penyebab", "nilai": "Path", "catatan": "Link resmi kadang panjang."},
        {"label": "Solusi", "nilai": "Update", "catatan": "Tambah domain resmi dan koreksi user."},
    ], kolom=3)

    col_1, col_2 = st.columns(2)
    with col_1:
        bullet_panel("Cara membaca hasil", ["Aman: sinyal rendah.", "Tinjauan: cek manual.", "Berisiko: jangan lanjut.", "Domain resmi perlu pembanding."], "gold")
    with col_2:
        bullet_panel("Update berikutnya", ["Import domain resmi CSV.", "Catatan koreksi user.", "Laporan salah deteksi.", "Daftar kampus, bank, dan e-commerce."], "green")


def halaman_panduan():
    hero(
        "Panduan",
        "Cara Pakai Singkat",
        "Pilih input, baca skor, lihat alasan, lalu ambil tindakan yang aman.",
    )

    col_1, col_2, col_3 = st.columns(3)
    with col_1:
        step_card("1", "Periksa URL", "Masukkan alamat bebas, banyak alamat, atau CSV.")
    with col_2:
        step_card("2", "Periksa file", "Unggah file. Sistem membaca metadata, URL, dan sinyal risiko tanpa menjalankan file.")
    with col_3:
        step_card("3", "Simpan hasil", "Unduh hasil CSV untuk laporan atau dokumentasi.")

    tab_url, tab_file, tab_hasil, tab_batas = st.tabs(["URL", "File", "Hasil", "Batasan"])
    with tab_url:
        bullet_panel("Langkah URL", ["Masukkan satu URL.", "Paste banyak URL.", "Atau unggah CSV.", "Lihat prioritas risiko.", "Unduh hasil."], "gold")
    with tab_file:
        bullet_panel("Langkah file", ["Unggah file.", "Klik periksa.", "Baca URL yang ditemukan.", "Jangan buka file berisiko.", "Simpan laporan."], "yellow")
    with tab_hasil:
        bullet_panel("Arti hasil", ["Terlihat Aman: risiko rendah.", "Perlu Tinjauan: cek manual.", "Berisiko: hindari dan laporkan.", "Skor tinggi berarti prioritas pemeriksaan lebih besar."], "green")
    with tab_batas:
        bullet_panel("Batasan sistem", ["Tidak membuka website secara langsung.", "Tidak menjalankan file.", "Tidak membuktikan pemilik domain.", "Tidak menggantikan pemeriksaan keamanan penuh."], "red")

    section_title("Pola pemakaian terbaik", "Cocok untuk penggunaan harian dan dokumentasi.")
    col_a, col_b = st.columns(2)
    with col_a:
        panel("Untuk user umum", "Cek link dari WhatsApp, email, SMS, browser, atau file sebelum login dan transaksi.", "green")
    with col_b:
        panel("Untuk laporan", "Gunakan fitur unduh CSV agar hasil bisa disimpan, dibagikan, atau dianalisis lagi.", "gold")

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
        tabel_rapi(data, max_rows=80)

        kolom_a, kolom_b = st.columns(2)

        with kolom_a:
            st.download_button(
                "Unduh riwayat",
                data=data.to_csv(index=False).encode("utf-8"),
                file_name="riwayat_streamlit_phishrisk.csv",
                mime="text/csv",
                key=widget_key("download_riwayat"),
            )

        with kolom_b:
            if st.button("Bersihkan riwayat", key="tombol_bersihkan_riwayat"):
                st.session_state.riwayat = []
                if LOKASI_RIWAYAT_STREAMLIT.exists():
                    LOKASI_RIWAYAT_STREAMLIT.unlink()
                st.success("Riwayat berhasil dibersihkan.")
                st.rerun()


def halaman_tentang():
    hero(
        "Tentang",
        "PhishRisk System",
        "Project Data Science untuk memeriksa indikasi phishing dari URL dan file secara defensif.",
    )

    metrik_kartu([
        {"label": "Model", "nilai": "RF", "catatan": "Random Forest Intelligence V2."},
        {"label": "Engine", "nilai": "V1", "catatan": "Model, intelligence, file analyzer."},
        {"label": "Interface", "nilai": "Streamlit", "catatan": "Dashboard untuk user."},
    ], kolom=3)

    col_1, col_2 = st.columns(2)
    with col_1:
        bullet_panel("Komponen", ["URL checker.", "Batch URL.", "File analyzer.", "URL dalam file.", "Riwayat dan export CSV."], "gold")
    with col_2:
        bullet_panel("Tujuan", ["Mudah dipakai.", "Mudah dipahami.", "Aman karena statis.", "Cocok untuk portfolio data science.", "Bisa dikembangkan lagi."], "green")

    with st.container(border=True):
        st.subheader("Author")
        col_a, col_b = st.columns(2)
        with col_a:
            st.write(f"Nama: {AUTHOR_INFO['Nama']}")
            st.write("Fokus: Data Science, Machine Learning, Software Engineering")
        with col_b:
            st.write(f"WhatsApp: {AUTHOR_INFO['WhatsApp']}")
            st.markdown(f"Instagram: [{AUTHOR_INFO['Instagram']}]({AUTHOR_INFO['Instagram']})")
            st.markdown(f"LinkedIn: [{AUTHOR_INFO['LinkedIn']}]({AUTHOR_INFO['LinkedIn']})")
            st.markdown(f"GitHub: [{AUTHOR_INFO['GitHub']}]({AUTHOR_INFO['GitHub']})")


def ringkas_metadata_program(metadata):
    if not metadata:
        return pd.DataFrame()

    pasangan = []
    peta_label = {
        "nama_program": "Nama program",
        "versi_engine": "Versi engine",
        "step": "Tahap program",
        "status": "Status",
        "catatan": "Catatan",
    }

    for kunci, label in peta_label.items():
        if kunci in metadata:
            pasangan.append({"informasi": label, "isi": metadata.get(kunci, "-")})

    fungsi = metadata.get("fungsi_utama")
    if isinstance(fungsi, list):
        pasangan.append({"informasi": "Fungsi utama", "isi": ", ".join([str(item).replace("_", " ") for item in fungsi])})

    return pd.DataFrame(pasangan)


def halaman_sistem():
    hero(
        "Informasi Sistem",
        "Kesiapan Komponen",
        "Ringkasan file penting yang dipakai aplikasi. Halaman ini dibuat untuk memastikan website memakai engine, model, dan data pembanding terbaru.",
        ["Best Engine", "Model V1", "URL", "File"],
    )

    daftar_file = [
        {"komponen": "Engine utama", "fungsi": "Menggabungkan model dan aturan keamanan.", "lokasi": DIREKTORI_SRC / "phishrisk_engine_v3.py", "catatan": "Wajib ada."},
        {"komponen": "CLI utility", "fungsi": "Menjalankan cek URL dan file lewat terminal.", "lokasi": DIREKTORI_SRC / "run_phishrisk.py", "catatan": "Berguna untuk pengujian."},
        {"komponen": "URL Intelligence", "fungsi": "Membaca domain resmi, brand, dan domain tiruan.", "lokasi": DIREKTORI_SRC / "url_intelligence.py", "catatan": "Wajib ada."},
        {"komponen": "File Analyzer", "fungsi": "Membaca file secara statis tanpa menjalankan file.", "lokasi": DIREKTORI_SRC / "file_static_analyzer.py", "catatan": "Wajib ada."},
        {"komponen": "Model terbaik", "fungsi": "Model prediksi phishing berbasis URL dan sinyal tambahan.", "lokasi": DIREKTORI_PROJECT / "models" / "model_terbaik_intelligence_v2.pkl", "catatan": "File besar, jangan dihapus."},
        {"komponen": "Daftar fitur", "fungsi": "Daftar kolom yang harus cocok dengan model.", "lokasi": DIREKTORI_OUTPUT / "daftar_fitur_intelligence_v2.json", "catatan": "Harus sinkron."},
        {"komponen": "Catatan CLI", "fungsi": "Ringkasan hasil pembuatan CLI STEP 10.", "lokasi": LOKASI_METADATA_STEP10, "catatan": "Opsional untuk informasi."},
        {"komponen": "Catatan engine", "fungsi": "Ringkasan Best Engine dan keluaran utamanya.", "lokasi": LOKASI_METADATA_ENGINE, "catatan": "Opsional untuk informasi."},
    ]

    data_ringkas = []
    data_detail = []
    for item in daftar_file:
        lokasi = item["lokasi"]
        tersedia = lokasi.exists()
        ukuran = round(lokasi.stat().st_size / 1024, 2) if tersedia else 0
        status = "Siap" if tersedia else "Belum ada"
        data_ringkas.append({
            "komponen": item["komponen"],
            "fungsi": item["fungsi"],
            "status": status,
            "ukuran_kb": ukuran,
            "catatan": item["catatan"],
        })
        data_detail.append({
            "komponen": item["komponen"],
            "lokasi": str(lokasi),
            "tersedia": tersedia,
            "ukuran_kb": ukuran,
        })

    data_validasi = pd.DataFrame(data_ringkas)
    jumlah_siap = int((data_validasi["status"] == "Siap").sum()) if not data_validasi.empty else 0
    total = len(data_validasi)
    siap_semua = jumlah_siap == total

    metrik_kartu(
        [
            {"label": "Komponen siap", "nilai": f"{jumlah_siap}/{total}", "catatan": "File penting yang ditemukan.", "warna": "green" if siap_semua else "yellow"},
            {"label": "Engine", "nilai": "V3", "catatan": "Versi yang dipakai Streamlit.", "warna": "gold"},
            {"label": "Mode file", "nilai": "Statis", "catatan": "File tidak dijalankan.", "warna": "green"},
            {"label": "Output", "nilai": "CSV", "catatan": "Hasil bisa diunduh.", "warna": "gold"},
        ],
        kolom=4,
    )

    if siap_semua:
        callout("Sistem siap", "Semua komponen utama tersedia. Aplikasi bisa dipakai untuk cek URL, cek file, batch URL, dan membaca link yang tertanam di file.", "safe")
    else:
        callout("Ada file yang belum ditemukan", "Periksa folder src, models, dan reports/outputs. Komponen yang hilang dapat membuat sebagian fitur tidak berjalan.", "review")

    section_title("Ringkasan Komponen", "Tabel ini memakai bahasa singkat agar mudah dibaca user umum.")
    tabel_rapi(data_validasi, max_rows=80)

    metadata_step10 = muat_metadata(LOKASI_METADATA_STEP10)
    metadata_engine = muat_metadata(LOKASI_METADATA_ENGINE)

    section_title("Informasi Program", "Bagian ini merangkum catatan program tanpa menampilkan data mentah yang terlalu teknis.")
    tab_engine, tab_cli, tab_detail = st.tabs(["Engine", "CLI", "Detail lokasi"])

    with tab_engine:
        ringkasan_engine = ringkas_metadata_program(metadata_engine)
        if not ringkasan_engine.empty:
            tabel_rapi(ringkasan_engine, max_rows=20)
        else:
            panel("Belum ada catatan engine", "File metadata engine belum ditemukan.", "yellow")
        bullet_panel(
            "Arti sederhana",
            [
                "Engine membaca URL dan file secara statis.",
                "Domain resmi dibantu oleh daftar pembanding.",
                "Domain tiruan dibaca dari pola nama brand, typo, dan kata mencurigakan.",
                "Hasil sistem adalah bantuan awal, bukan vonis mutlak.",
            ],
            "gold",
        )

    with tab_cli:
        ringkasan_cli = ringkas_metadata_program(metadata_step10)
        if not ringkasan_cli.empty:
            tabel_rapi(ringkasan_cli, max_rows=20)
        else:
            panel("Belum ada catatan CLI", "File metadata CLI belum ditemukan.", "yellow")
        panel("Kegunaan CLI", "CLI dipakai saat ingin memeriksa satu URL, banyak URL, satu file, atau satu folder tanpa membuka dashboard Streamlit.", "green")

    with tab_detail:
        panel("Untuk developer", "Detail lokasi file disediakan untuk pengecekan teknis. User umum cukup membaca ringkasan komponen di atas.", "flat")
        tabel_rapi(pd.DataFrame(data_detail), max_rows=80)


def halaman_game_cyber(engine):
    hero(
        "Cyber Game",
        "Data Science x Cyber Security",
        "Latihan singkat membaca URL, skor risiko, dan tindakan aman. Game ini dibuat ringan agar user belajar sambil mencoba sistem.",
        ["Tebak risiko", "Cari sinyal", "Ambil tindakan"],
    )

    if "game_skor" not in st.session_state:
        st.session_state.game_skor = 0
    if "game_total" not in st.session_state:
        st.session_state.game_total = 0
    if "game_index" not in st.session_state:
        st.session_state.game_index = 0

    daftar_soal = [
        {
            "url": "https://praktikum.gunadarma.ac.id",
            "jawaban": "Terlihat Aman",
            "alasan": "Domain berada di bawah gunadarma.ac.id, yaitu domain resmi yang sudah masuk pembanding.",
            "sinyal": ["Domain resmi", "Subdomain kampus", "HTTPS"],
        },
        {
            "url": "http://rricrosoft.com",
            "jawaban": "Berisiko",
            "alasan": "Domain mirip Microsoft, tetapi bukan microsoft.com.",
            "sinyal": ["Mirip brand", "Bukan domain resmi", "Tidak memakai HTTPS"],
        },
        {
            "url": "http://bca-login-update.test",
            "jawaban": "Berisiko",
            "alasan": "Mengandung nama brand BCA, tetapi memakai domain lain dan kata login/update.",
            "sinyal": ["Brand dipakai di domain palsu", "login", "update"],
        },
        {
            "url": "https://www.bca.co.id",
            "jawaban": "Terlihat Aman",
            "alasan": "Domain cocok dengan pembanding resmi BCA.",
            "sinyal": ["Domain resmi", "HTTPS", "Tidak ada kata mendesak"],
        },
        {
            "url": "https://xn--micrsoft-q4a.test",
            "jawaban": "Berisiko",
            "alasan": "Punycode dapat menyamarkan domain agar terlihat seperti brand resmi.",
            "sinyal": ["Punycode", "Mirip brand", "Bukan domain resmi"],
        },
    ]

    metrik_kartu(
        [
            {"label": "Skor kamu", "nilai": st.session_state.game_skor, "catatan": "Jawaban benar.", "warna": "gold"},
            {"label": "Percobaan", "nilai": st.session_state.game_total, "catatan": "Jumlah jawaban dicek.", "warna": "flat"},
            {"label": "Mode", "nilai": "Latihan", "catatan": "Tidak memengaruhi model.", "warna": "green"},
        ],
        kolom=3,
    )

    tab_tebak, tab_sinyal, tab_aksi, tab_lab = st.tabs(["Tebak Risiko", "Cari Sinyal", "Aksi Aman", "Mini Lab"])

    with tab_tebak:
        soal = daftar_soal[st.session_state.game_index % len(daftar_soal)]
        html(
            f"""
            <div class="game-board">
                <div class="card-title">Tebak hasil untuk URL ini</div>
                <div class="game-url">{aman_teks(soal['url'])}</div>
                <div class="game-score"><span>Soal {st.session_state.game_index + 1}</span><span>Pilih satu jawaban</span></div>
            </div>
            """
        )
        jawaban_user = st.radio(
            "Menurut kamu hasilnya apa?",
            ["Terlihat Aman", "Perlu Tinjauan", "Berisiko"],
            horizontal=True,
            key=f"game_jawaban_{st.session_state.game_index}",
        )
        kolom_a, kolom_b, kolom_c = st.columns(3)
        with kolom_a:
            if st.button("Cek jawaban", key="game_cek_jawaban"):
                st.session_state.game_total += 1
                if jawaban_user == soal["jawaban"]:
                    st.session_state.game_skor += 1
                    callout("Benar", soal["alasan"], "safe")
                else:
                    callout("Belum tepat", f"Jawaban yang lebih sesuai: {soal['jawaban']}. {soal['alasan']}", "review")
        with kolom_b:
            if st.button("Soal berikutnya", key="game_soal_berikutnya"):
                st.session_state.game_index = (st.session_state.game_index + 1) % len(daftar_soal)
                st.rerun()
        with kolom_c:
            if st.button("Reset skor", key="game_reset_skor"):
                st.session_state.game_skor = 0
                st.session_state.game_total = 0
                st.session_state.game_index = 0
                st.rerun()

        with st.expander("Lihat hasil engine untuk soal ini"):
            if st.button("Jalankan engine", key=f"game_run_engine_{st.session_state.game_index}"):
                jalankan_uji_satu_url(engine, soal["url"], sumber="game")

    with tab_sinyal:
        soal_sinyal = daftar_soal[(st.session_state.game_index + 1) % len(daftar_soal)]
        html(f'<div class="game-board"><div class="card-title">Cari sinyal risiko</div><div class="game-url">{aman_teks(soal_sinyal["url"])}</div></div>')
        opsi = ["Domain resmi", "Mirip brand", "login/update", "Punycode", "HTTPS", "Bukan domain resmi", "Tidak ada kata mendesak"]
        pilihan = st.multiselect("Pilih sinyal yang terlihat", opsi, key="game_multiselect_sinyal")
        if st.button("Cek sinyal", key="game_cek_sinyal"):
            target = set([item.lower() for item in soal_sinyal["sinyal"]])
            pilihan_lower = set([item.lower() for item in pilihan])
            cocok = len(target.intersection(pilihan_lower))
            total_target = max(1, len(target))
            if cocok == total_target:
                callout("Mantap", "Semua sinyal utama terbaca. Kamu sudah memahami pola utamanya.", "safe")
            elif cocok > 0:
                callout("Sebagian benar", f"Kamu menemukan {cocok} dari {total_target} sinyal utama. Sinyal penting: {', '.join(soal_sinyal['sinyal'])}.", "review")
            else:
                callout("Perlu latihan", f"Sinyal penting: {', '.join(soal_sinyal['sinyal'])}.", "danger")

    with tab_aksi:
        skenario = st.selectbox(
            "Pilih skenario",
            [
                "Link bank dari chat tidak dikenal meminta login",
                "Website kampus resmi terbaca perlu tinjauan",
                "PDF berisi link login dan kata OTP",
                "Domain mirip brand besar memakai huruf berbeda",
            ],
            key="game_skenario_aksi",
        )
        aksi = st.radio(
            "Tindakan paling aman",
            [
                "Langsung login agar cepat selesai",
                "Cek domain resmi, jangan isi data dulu",
                "Unduh dan jalankan file untuk memastikan",
                "Kirim OTP agar akun tidak diblokir",
            ],
            key="game_aksi_radio",
        )
        if st.button("Cek tindakan", key="game_cek_tindakan"):
            if aksi == "Cek domain resmi, jangan isi data dulu":
                callout("Tindakan benar", "Cek domain resmi dulu. Jangan isi password, OTP, PIN, atau data pembayaran saat sumber link belum jelas.", "safe")
            else:
                callout("Tindakan berbahaya", "Jangan login, jangan jalankan file, dan jangan kirim OTP dari link yang belum jelas.", "danger")

    with tab_lab:
        bullet_panel(
            "Ide latihan cepat",
            [
                "Bandingkan domain resmi dan domain tiruan yang mirip.",
                "Uji URL yang memakai kata login, verify, update, secure, atau account.",
                "Uji file PDF, DOCX, ZIP, TXT, HTML, dan APK dummy untuk melihat sinyal statis.",
                "Catat contoh salah deteksi agar daftar pembanding resmi bisa diperbaiki.",
            ],
            "gold",
        )
        panel("Catatan", "Game ini tidak melatih ulang model. Game hanya membantu user memahami hasil sistem dengan bahasa sederhana.", "flat")


def halaman_batch_lab(engine):
    hero(
        "Engine Lab",
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



MENU_UTAMA = [
    "Beranda",
    "URL",
    "File",
    "Batch",
    "Rekomendasi",
    "Ciri",
    "Panduan",
    "Game",
    "Beta",
    "Riwayat",
    "Tentang",
    "Sistem",
]

MENU_MAP = {
    "Beranda": "Beranda",
    "URL": "Input Alamat Link",
    "File": "Input File",
    "Batch": "Engine Lab",
    "Rekomendasi": "Rekomendasi dan Antisipasi",
    "Ciri": "Ciri-Ciri",
    "Panduan": "Panduan",
    "Game": "Quick PhishRisk Training",
    "Beta": "Beta dan Salah Deteksi",
    "Riwayat": "Riwayat",
    "Tentang": "Tentang Project",
    "Sistem": "Informasi Sistem",
}


def buat_navigasi():
    if "halaman_aktif" not in st.session_state:
        st.session_state.halaman_aktif = "Beranda"

    default = st.session_state.halaman_aktif if st.session_state.halaman_aktif in MENU_UTAMA else "Beranda"

    html(
        """
        <div class="top-nav-card">
            <div class="top-nav-head">
                <div class="brand-block">
                    <div class="brand-mark">PR</div>
                    <div>
                        <div class="brand-title">PhishRisk</div>
                        <div class="brand-sub">URL dan file checker</div>
                    </div>
                </div>
                <div class="nav-badge">Best Engine</div>
            </div>
        """
    )

    pilihan = st.selectbox(
        "Pilih halaman",
        MENU_UTAMA,
        index=MENU_UTAMA.index(default),
        label_visibility="collapsed",
        key="navigasi_utama_dropdown",
    )

    html(
        f"""
            <div class="nav-help">Halaman aktif: <b>{aman_teks(MENU_MAP.get(pilihan, pilihan))}</b></div>
        </div>
        """
    )

    st.session_state.halaman_aktif = pilihan
    return MENU_MAP.get(pilihan, "Beranda")


def buat_sidebar():
    return buat_navigasi()



def footer_site():
    html(
        f"""
        <footer class="site-footer">
            <div class="footer-grid">
                <div>
                    <div class="footer-name">{aman_teks(AUTHOR_INFO.get('Nama', 'Harbangan Panjaitan'))}</div>
                    <div class="footer-note">PhishRisk System. Dashboard defensif untuk memeriksa URL dan file secara statis sebelum user klik, login, unduh, atau membuka lampiran.</div>
                </div>
                <div class="footer-links">
                    <a class="footer-link" href="https://wa.me/628158883565" target="_blank">WhatsApp</a>
                    <a class="footer-link" href="{aman_teks(AUTHOR_INFO.get('Instagram', '#'))}" target="_blank">Instagram</a>
                    <a class="footer-link" href="{aman_teks(AUTHOR_INFO.get('LinkedIn', '#'))}" target="_blank">LinkedIn</a>
                    <a class="footer-link" href="{aman_teks(AUTHOR_INFO.get('GitHub', '#'))}" target="_blank">GitHub</a>
                </div>
            </div>
            <div class="footer-line">Fokus project: Data Science, Machine Learning, dan Cyber Security defensif. Sistem ini membantu menilai risiko, bukan membuat phishing, menjalankan file asing, atau menggantikan pemeriksaan keamanan penuh.</div>
        </footer>
        """
    )

def main():
    pasang_css()
    pasang_css_final_override()
    pasang_css_v8_polish()
    siapkan_state()

    try:
        engine = muat_engine()
    except Exception as error:
        hero(
            "Aplikasi gagal dimuat",
            "Best Engine Belum Siap",
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
    elif halaman == "Engine Lab":
        halaman_batch_lab(engine)
    elif halaman == "Rekomendasi dan Antisipasi":
        halaman_rekomendasi()
    elif halaman == "Ciri-Ciri":
        halaman_ciri()
    elif halaman == "Panduan":
        halaman_panduan()
    elif halaman == "Quick PhishRisk Training":
        halaman_game_cyber(engine)
    elif halaman == "Beta dan Salah Deteksi":
        halaman_beta()
    elif halaman == "Riwayat":
        halaman_riwayat()
    elif halaman == "Tentang Project":
        halaman_tentang()
    else:
        halaman_sistem()


    footer_site()



# ============================================================
# OVERRIDE UPGRADE STREAMLIT - ENGINE V4 + PUBLIC THREAT INTEL
# Bagian ini sengaja diletakkan di akhir file agar mengganti
# fungsi lama tanpa merusak utility yang sudah ada.
# ============================================================

LOKASI_METADATA_ENGINE_V4 = DIREKTORI_OUTPUT / "metadata_step13_public_threat_intelligence.json"
LOKASI_LAPORAN_STEP13 = DIREKTORI_OUTPUT / "laporan_step13_public_threat_intelligence.md"
LOKASI_VALIDASI_STEP13 = DIREKTORI_OUTPUT / "validasi_step13_public_threat_intelligence.csv"
LOKASI_RIWAYAT_STREAMLIT = DIREKTORI_OUTPUT / "riwayat_streamlit_engine_v4.csv"


def pasang_css_engine_v4():
    st.markdown(
        """
        <style>
        .v4-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.75rem;margin:.75rem 0 1rem}
        .v4-card{border:1px solid rgba(255,255,255,.075);border-radius:22px;background:linear-gradient(145deg,rgba(255,255,255,.046),rgba(255,255,255,.012));padding:.95rem;box-shadow:0 14px 38px rgba(0,0,0,.25);min-height:122px}
        .v4-card b{display:block;color:#fff9ec;font-size:1rem!important;letter-spacing:-.025em;margin-bottom:.22rem}
        .v4-card span{color:#c8bda9;font-size:.84rem!important;line-height:1.48!important}
        .v4-tag-row{display:flex;flex-wrap:wrap;gap:.42rem;margin:.55rem 0}
        .v4-tag{border:1px solid rgba(216,181,109,.34);background:rgba(216,181,109,.09);color:#ffe5ad;border-radius:999px;padding:.26rem .58rem;font-size:.75rem!important;font-weight:850!important}
        .v4-feature-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.75rem;margin:.65rem 0 1rem}
        .v4-feature{border:1px solid rgba(255,255,255,.075);border-radius:20px;background:rgba(255,255,255,.025);padding:.9rem;min-height:138px}
        .v4-feature b{color:#fff9ec;font-size:.98rem!important;display:block;margin-bottom:.3rem;letter-spacing:-.02em}
        .v4-feature p{color:#c8bda9!important;font-size:.84rem!important;line-height:1.48!important;margin:0!important}
        .v4-mini-warning{border:1px solid rgba(216,181,109,.32);background:linear-gradient(145deg,rgba(216,181,109,.10),rgba(255,255,255,.012));border-radius:22px;padding:.85rem;margin:.65rem 0;color:#c8bda9!important}
        .v4-intel-box{border:1px solid rgba(155,199,159,.28);background:linear-gradient(145deg,rgba(155,199,159,.09),rgba(255,255,255,.012));border-radius:22px;padding:.9rem;margin:.65rem 0}
        .v4-danger-box{border:1px solid rgba(225,132,120,.36);background:linear-gradient(145deg,rgba(225,132,120,.12),rgba(255,255,255,.012));border-radius:22px;padding:.9rem;margin:.65rem 0}
        .top-nav-card{max-width:1180px!important}
        .top-nav-card .stSelectbox, .top-nav-card div[data-testid="stSelectbox"]{margin-bottom:.1rem!important}
        .top-nav-card [data-baseweb="select"]>div{min-height:46px!important;border-radius:999px!important}
        [data-testid="stFileUploaderDropzone"]{min-height:170px!important}
        [data-testid="stFileUploaderDropzone"] button:before{content:"Pilih file untuk diperiksa"!important}
        .stTextArea textarea{min-height:180px!important}
        @media(max-width:980px){.v4-grid,.v4-feature-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
        @media(max-width:640px){
            .v4-grid,.v4-feature-grid{grid-template-columns:1fr}
            .v4-card,.v4-feature{min-height:auto}
            .top-nav-card [data-baseweb="select"]>div{min-height:44px!important}
            [data-testid="stFileUploaderDropzone"]{min-height:190px!important}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def v4_value(data, kolom_v4, kolom_lama="-"):
    if isinstance(data, dict):
        nilai = data.get(kolom_v4, None)
        if nilai not in [None, ""]:
            return nilai
        return data.get(kolom_lama, "-") if kolom_lama != "-" else "-"
    return "-"


def selaraskan_hasil_url(hasil):
    """Membuat hasil best engine tetap cocok dengan fungsi lama."""
    if hasil is None:
        return {}

    data = dict(hasil)

    if "hasil_akhir_v4" in data:
        data["hasil_akhir_lokal"] = data.get("hasil_akhir", "-")
        data["kategori_risiko_lokal"] = data.get("kategori_risiko", "-")
        data["skor_final_lokal"] = data.get("skor_final", "-")
        data["rekomendasi_lokal"] = data.get("rekomendasi", "-")
        data["hasil_akhir"] = data.get("hasil_akhir_v4", data.get("hasil_akhir", "-"))
        data["kategori_risiko"] = data.get("kategori_risiko_v4", data.get("kategori_risiko", "-"))
        data["skor_final"] = data.get("skor_final_v4", data.get("skor_final", 0))
        data["rekomendasi"] = data.get("rekomendasi_v4", data.get("rekomendasi", "-"))

    data["public_ti_status"] = data.get("public_ti_status", "tidak_dicek")
    data["public_ti_sources"] = data.get("public_ti_sources", "-") or "-"
    data["public_ti_reason"] = data.get("public_ti_reason", "-") or "-"
    data["public_ti_score"] = data.get("public_ti_score", 0)

    return data


def selaraskan_dataframe_url(data):
    if data is None:
        return pd.DataFrame()

    df = pd.DataFrame(data).copy()
    if df.empty:
        return df

    pasangan = [
        ("hasil_akhir_v4", "hasil_akhir"),
        ("kategori_risiko_v4", "kategori_risiko"),
        ("skor_final_v4", "skor_final"),
        ("rekomendasi_v4", "rekomendasi"),
    ]

    for sumber, tujuan in pasangan:
        if sumber in df.columns:
            if tujuan in df.columns:
                df[tujuan + "_lokal"] = df[tujuan]
            df[tujuan] = df[sumber]

    for kolom, default in [
        ("public_ti_status", "tidak_dicek"),
        ("public_ti_sources", "-"),
        ("public_ti_reason", "-"),
        ("public_ti_score", 0),
        ("phishtank_status", "-"),
        ("urlhaus_query_status", "-"),
    ]:
        if kolom not in df.columns:
            df[kolom] = default

    return df


def selaraskan_dataframe_file(data_file):
    df = pd.DataFrame(data_file).copy()
    if df.empty:
        return df

    pasangan = [
        ("hasil_akhir_file_v4", "hasil_akhir_file_v3"),
        ("kategori_final_file_v4", "kategori_final_file_v3"),
        ("skor_final_file_v4", "skor_final_file_v3"),
        ("rekomendasi_final_file_v4", "rekomendasi_final_file_v3"),
    ]

    for sumber, tujuan in pasangan:
        if sumber in df.columns:
            if tujuan in df.columns:
                df[tujuan + "_lokal"] = df[tujuan]
            df[tujuan] = df[sumber]

    for kolom, default in [
        ("jumlah_url_terdeteksi_public_ti", 0),
        ("skor_public_ti_maks_file", 0),
    ]:
        if kolom not in df.columns:
            df[kolom] = default

    return df


@st.cache_resource
def muat_engine():
    """Memakai best engine jika tersedia. Jika belum ada, fallback ke engine lama."""
    try:
        import phishrisk_engine_v4
        return phishrisk_engine_v4.PhishRiskEngineV4(DIREKTORI_PROJECT)
    except Exception:
        import phishrisk_engine_v3
        return phishrisk_engine_v3.buat_engine(DIREKTORI_PROJECT)


def tambah_riwayat_url(hasil):
    hasil = selaraskan_hasil_url(hasil)
    item = {
        "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "jenis": "URL",
        "input": hasil.get("url", "-"),
        "domain": hasil.get("domain", "-"),
        "hasil": hasil.get("hasil_akhir", "-"),
        "skor": hasil.get("skor_final", "-"),
        "kategori": hasil.get("kategori_risiko", "-"),
        "catatan": hasil.get("public_ti_status", hasil.get("intelligence_status", "-")),
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
        "hasil": hasil.get("hasil_akhir_file_v4", hasil.get("hasil_akhir_file_v3", "-")),
        "skor": hasil.get("skor_final_file_v4", hasil.get("skor_final_file_v3", "-")),
        "kategori": hasil.get("kategori_final_file_v4", hasil.get("kategori_final_file_v3", "-")),
        "catatan": hasil.get("ekstensi", "-"),
    }
    st.session_state.riwayat.insert(0, item)
    st.session_state.riwayat = st.session_state.riwayat[:500]
    simpan_riwayat()


def saran_berdasarkan_hasil_url(hasil):
    hasil = selaraskan_hasil_url(hasil)
    status = hasil.get("hasil_akhir", "")
    public_status = str(hasil.get("public_ti_status", "")).lower()
    intelligence_status = str(hasil.get("intelligence_status", "")).lower()
    domain = hasil.get("domain", "-")

    daftar = []

    if status == "Terlihat Aman":
        daftar.extend([
            f"Domain {domain} terlihat rendah risiko berdasarkan best engine.",
            "Tetap buka dari bookmark, aplikasi resmi, atau ketik manual jika berkaitan dengan akun penting.",
            "Jangan memasukkan data sensitif jika link berasal dari pesan acak.",
        ])
    elif status == "Perlu Tinjauan":
        daftar.extend([
            "Tahan dulu sebelum login atau transaksi.",
            "Bandingkan domain dengan website resmi dari sumber terpercaya.",
            "Cek apakah ada kata login, update, verify, secure, account, atau reward.",
        ])
    else:
        daftar.extend([
            "Jangan buka link dari perangkat utama.",
            "Jangan isi username, password, OTP, PIN, nomor kartu, atau data pribadi.",
            "Laporkan link ke admin, bank, kampus, marketplace, atau pihak terkait.",
            "Simpan bukti pesan jika link berasal dari WhatsApp, SMS, email, atau DM.",
        ])

    if "phishing" in public_status or "ancaman" in public_status:
        daftar.append("Public Threat Intelligence memberi sinyal kuat. Perlakukan link ini sebagai prioritas tinggi untuk diblokir.")
    elif "catatan" in public_status:
        daftar.append("Ada catatan ringan dari sumber eksternal. Gunakan sebagai tambahan, bukan satu-satunya keputusan.")

    if "tiruan_brand" in intelligence_status or "domain_mirip" in intelligence_status:
        daftar.append("Waspadai domain yang meniru brand resmi, huruf mirip, angka pengganti huruf, dan tanda hubung.")

    return daftar


def tampilkan_status_url(hasil):
    hasil = selaraskan_hasil_url(hasil)

    hasil_akhir = hasil.get("hasil_akhir", "-")
    risiko_class, label_risiko = status_to_class(hasil_akhir)
    skor = hasil.get("skor_final", 0)
    kelas_panel = f"panel risk-{risiko_class}"

    html(
        f"""
        <section class="{kelas_panel}">
            <div class="eyebrow">Hasil Best Engine</div>
            <h2>{aman_teks(label_risiko)}</h2>
            <p class="muted">{aman_teks(hasil.get("rekomendasi", "-"))}</p>
            <div class="v4-tag-row">
                <span class="v4-tag">Model: {aman_teks(hasil.get("label_model", "-"))}</span>
                <span class="v4-tag">Public TI: {aman_teks(hasil.get("public_ti_status", "-"))}</span>
                <span class="v4-tag">Sumber: {aman_teks(hasil.get("public_ti_sources", "-") or "-")}</span>
            </div>
        </section>
        """
    )

    warna_kategori = "green" if risiko_class == "safe" else "yellow" if risiko_class == "review" else "red"
    metrik_kartu(
        [
            {"label": "Skor V4", "nilai": f"{hasil.get('skor_final', 0)}", "catatan": "Gabungan model, intelligence, dan Public TI.", "warna": "gold"},
            {"label": "Kategori", "nilai": hasil.get("kategori_risiko", "-"), "catatan": "Prioritas tindakan user.", "warna": warna_kategori},
            {"label": "Public TI", "nilai": hasil.get("public_ti_score", 0), "catatan": hasil.get("public_ti_status", "-"), "warna": "normal"},
            {"label": "Sinyal lokal", "nilai": hasil.get("intelligence_status", "-"), "catatan": "Domain, brand, dan pola URL.", "warna": "normal"},
        ],
        kolom=4,
    )

    score_bar(skor)

    tab_ringkas, tab_sinyal, tab_public, tab_saran, tab_teknis = st.tabs(
        ["Ringkasan", "Sinyal Lokal", "Public TI", "Rekomendasi", "Detail"]
    )

    with tab_ringkas:
        data_ringkas = pd.DataFrame([
            {"Bagian": "URL", "Nilai": hasil.get("url", "-")},
            {"Bagian": "Domain", "Nilai": hasil.get("domain", "-")},
            {"Bagian": "Hasil Best Engine", "Nilai": hasil.get("hasil_akhir", "-")},
            {"Bagian": "Kategori Best Engine", "Nilai": hasil.get("kategori_risiko", "-")},
            {"Bagian": "Skor lokal", "Nilai": hasil.get("skor_final_lokal", hasil.get("skor_model", "-"))},
            {"Bagian": "Skor Public TI", "Nilai": hasil.get("public_ti_score", "-")},
            {"Bagian": "Brand resmi", "Nilai": hasil.get("official_brand", "-") or "-"},
            {"Bagian": "Brand terdeteksi", "Nilai": hasil.get("brand_detected", "-") or "-"},
            {"Bagian": "Domain mirip", "Nilai": hasil.get("lookalike_brand", "-") or "-"},
        ])
        tabel_rapi(data_ringkas, max_rows=80)
        callout("Cara baca cepat", "Skor Best Engine adalah hasil final. Jika Public TI tidak menemukan data, keputusan tetap mengikuti Engine lokal.", risiko_class)

    with tab_sinyal:
        panel("Alasan lokal", hasil.get("intelligence_reason", "-"), "gold")
        data_sinyal = pd.DataFrame([
            {"Sinyal": "Domain resmi", "Nilai": hasil.get("is_official_domain", 0), "Makna": "Cocok dengan daftar pembanding resmi."},
            {"Sinyal": "Brand tidak resmi", "Nilai": hasil.get("brand_but_not_official", 0), "Makna": "Ada nama brand tapi bukan domain resmi."},
            {"Sinyal": "Kata mencurigakan", "Nilai": hasil.get("suspicious_keywords", "-") or "-", "Makna": "Kata yang sering dipakai untuk menekan user."},
            {"Sinyal": "Lookalike", "Nilai": hasil.get("lookalike_brand", "-") or "-", "Makna": "Domain terlihat mirip brand resmi."},
            {"Sinyal": "Punycode", "Nilai": hasil.get("uses_punycode", 0), "Makna": "Bisa menyamarkan karakter domain."},
            {"Sinyal": "Angka pengganti huruf", "Nilai": hasil.get("uses_digit_substitution", 0), "Makna": "Contoh: micros0ft."},
        ])
        tabel_rapi(data_sinyal, max_rows=80)

    with tab_public:
        data_public = pd.DataFrame([
            {"Sumber": "PhishTank", "Status": hasil.get("phishtank_status", "-"), "Catatan": "Basis data URL phishing."},
            {"Sumber": "URLhaus", "Status": hasil.get("urlhaus_query_status", "-"), "Catatan": "Basis data URL malware/payload."},
            {"Sumber": "Public TI", "Status": hasil.get("public_ti_status", "-"), "Catatan": hasil.get("public_ti_reason", "-")},
        ])
        tabel_rapi(data_public, max_rows=80)
        panel("Catatan", hasil.get("public_ti_recommendation", "Public TI adalah sinyal tambahan."), "yellow")

    with tab_saran:
        bullet_panel("Rekomendasi tindakan", saran_berdasarkan_hasil_url(hasil), "gold")
        bullet_panel(
            "Antisipasi cepat",
            [
                "Jangan kirim OTP kepada siapa pun.",
                "Gunakan bookmark untuk layanan penting.",
                "Cek domain utama sebelum login.",
                "Pisahkan perangkat utama dan perangkat uji jika harus meninjau link mencurigakan.",
            ],
            "normal",
        )

    with tab_teknis:
        tabel_rapi(pd.DataFrame([hasil]), max_rows=80)


def tampilkan_ringkasan_url(data):
    data = selaraskan_dataframe_url(data)
    if data.empty:
        return

    total = len(data)
    jumlah_aman = int((data["hasil_akhir"] == "Terlihat Aman").sum()) if "hasil_akhir" in data.columns else 0
    jumlah_tinjauan = int((data["hasil_akhir"] == "Perlu Tinjauan").sum()) if "hasil_akhir" in data.columns else 0
    jumlah_risiko = int((data["hasil_akhir"] == "Berisiko").sum()) if "hasil_akhir" in data.columns else 0
    public_temuan = int((pd.to_numeric(data.get("public_ti_score", pd.Series([0] * total)), errors="coerce").fillna(0) > 0).sum())

    metrik_kartu([
        {"label": "Total URL", "nilai": total, "catatan": "Jumlah alamat diperiksa.", "warna": "gold"},
        {"label": "Terlihat Aman", "nilai": jumlah_aman, "catatan": "Risiko rendah.", "warna": "green"},
        {"label": "Perlu Tinjauan", "nilai": jumlah_tinjauan, "catatan": "Butuh cek manual.", "warna": "yellow"},
        {"label": "Berisiko", "nilai": jumlah_risiko, "catatan": "Sebaiknya dihindari.", "warna": "red"},
    ], kolom=4)

    if public_temuan:
        callout("Catatan Public TI", f"Ada {public_temuan} URL yang memiliki catatan dari sumber eksternal.", "review")


def tampilkan_ringkasan_file(data_file):
    data_file = selaraskan_dataframe_file(data_file)
    if data_file.empty:
        return

    total = len(data_file)
    kolom_hasil = "hasil_akhir_file_v3"
    jumlah_risiko = int((data_file.get(kolom_hasil, pd.Series(dtype=str)) == "Berisiko").sum()) if kolom_hasil in data_file.columns else 0
    jumlah_aman = int((data_file.get(kolom_hasil, pd.Series(dtype=str)) == "Terlihat Aman").sum()) if kolom_hasil in data_file.columns else 0
    jumlah_public = int(pd.to_numeric(data_file.get("jumlah_url_terdeteksi_public_ti", pd.Series([0] * total)), errors="coerce").fillna(0).sum())

    metrik_kartu([
        {"label": "Total file", "nilai": total, "catatan": "File yang diperiksa.", "warna": "gold"},
        {"label": "Aman", "nilai": jumlah_aman, "catatan": "Risiko rendah.", "warna": "green"},
        {"label": "Berisiko", "nilai": jumlah_risiko, "catatan": "Perlu dihindari.", "warna": "red"},
        {"label": "Public TI", "nilai": jumlah_public, "catatan": "URL dalam file punya catatan eksternal.", "warna": "yellow"},
    ], kolom=4)


def tampilkan_tabel_url(data):
    data = selaraskan_dataframe_url(data)

    if data.empty:
        st.info("Belum ada hasil pemeriksaan.")
        return

    kolom = [
        "url",
        "domain",
        "hasil_akhir",
        "kategori_risiko",
        "skor_final",
        "label_model",
        "public_ti_score",
        "public_ti_status",
        "public_ti_sources",
        "phishtank_status",
        "urlhaus_query_status",
        "intelligence_status",
        "brand_detected",
        "suspicious_keywords",
        "lookalike_brand",
        "rekomendasi",
    ]
    kolom = [item for item in kolom if item in data.columns]

    tabel_rapi(data[kolom], max_rows=100)

    st.download_button(
        "Unduh hasil URL",
        data=data.to_csv(index=False).encode("utf-8"),
        file_name="hasil_url_phishrisk_streamlit.csv",
        mime="text/csv",
        key=widget_key("download_hasil_url"),
    )


def tampilkan_tabel_file(data_file, data_url):
    data_file = selaraskan_dataframe_file(data_file)
    data_url = selaraskan_dataframe_url(data_url)

    if data_file.empty:
        st.info("Belum ada hasil pemeriksaan file.")
        return

    kolom_file = [
        "nama_file",
        "ekstensi",
        "ukuran_kb",
        "jumlah_url",
        "jumlah_url_berisiko_v3",
        "jumlah_url_perlu_tinjauan_v3",
        "jumlah_url_terdeteksi_public_ti",
        "jumlah_kata_mencurigakan",
        "kata_mencurigakan",
        "skor_final_file_v3",
        "skor_public_ti_maks_file",
        "kategori_final_file_v3",
        "hasil_akhir_file_v3",
        "alasan_file",
        "rekomendasi_final_file_v3",
        "sha256_upload",
    ]
    kolom_file = [item for item in kolom_file if item in data_file.columns]

    st.subheader("Hasil file")
    tabel_rapi(data_file[kolom_file], max_rows=80)

    st.download_button(
        "Unduh hasil file",
        data=data_file.to_csv(index=False).encode("utf-8"),
        file_name="hasil_file_phishrisks_streamlit.csv",
        mime="text/csv",
        key=widget_key("download_hasil_file"),
    )

    if not data_url.empty:
        st.subheader("URL yang ditemukan di dalam file")
        tampilkan_tabel_url(data_url)


def jalankan_uji_satu_url(engine, url, sumber="input"):
    url = normalisasi_url_input(url)
    if not url:
        st.warning("Alamat web tidak boleh kosong.")
        return {}

    with st.spinner("Memeriksa alamat dengan Best Engine..."):
        hasil = selaraskan_hasil_url(engine.analisis_url(url))

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

    with st.spinner("Memeriksa semua alamat dengan Best Engine..."):
        data = selaraskan_dataframe_url(engine.analisis_banyak_url(daftar_url))

    for _, baris in data.iterrows():
        tambah_riwayat_url(baris.to_dict())

    st.session_state.hasil_url_terakhir = data
    tampilkan_ringkasan_url(data)
    tampilkan_tabel_url(data)
    return data


def tampilkan_feature_grid():
    html(
        """
        <div class="v4-feature-grid">
            <div class="v4-feature"><b>URL bebas</b><p>User bisa memasukkan domain resmi, link aneh, atau URL dari chat tanpa mengikuti template.</p></div>
            <div class="v4-feature"><b>Batch URL</b><p>Tempel banyak alamat atau upload CSV, lalu unduh hasil pemeriksaan.</p></div>
            <div class="v4-feature"><b>File statis</b><p>File dibaca tanpa dijalankan. Cocok untuk PDF, DOCX, HTML, ZIP, APK, TXT, dan file lain.</p></div>
            <div class="v4-feature"><b>Public TI</b><p>PhishTank dan URLhaus menjadi sinyal tambahan untuk membaca catatan eksternal.</p></div>
            <div class="v4-feature"><b>Rekomendasi</b><p>Hasil tidak hanya angka. User mendapat alasan dan tindakan aman yang bisa dilakukan.</p></div>
            <div class="v4-feature"><b>Riwayat</b><p>Hasil tersimpan selama aplikasi berjalan dan bisa dipakai untuk membandingkan pemeriksaan.</p></div>
        </div>
        """
    )


def render_lab_uji_bebas_beranda(engine):
    section_title("Uji Coba Bebas", "Masukkan URL sendiri, bukan hanya contoh bawaan. Akhirnya tombol input melakukan tugas mulianya.")
    html('<div class="input-lab">')

    tab_satu, tab_banyak, tab_set, tab_ide = st.tabs(["Satu URL", "Banyak URL", "Paket Uji", "Ide"])

    with tab_satu:
        url_bebas = st.text_input(
            "Alamat bebas",
            value="",
            placeholder="Contoh: shopee.co.id, https://praktikum.gunadarma.ac.id, rricrosoft.com",
            key="beranda_url_bebas_engine_v4",
        )
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Periksa URL bebas", key="beranda_periksa_bebas_v4"):
                jalankan_uji_satu_url(engine, url_bebas)
        with c2:
            if st.button("Coba resmi", key="beranda_coba_resmi_v4"):
                jalankan_uji_satu_url(engine, "https://praktikum.gunadarma.ac.id")
        with c3:
            if st.button("Coba tiruan", key="beranda_coba_tiruan_v4"):
                jalankan_uji_satu_url(engine, "http://bca-login-update.test")

    with tab_banyak:
        teks_bebas = st.text_area(
            "Daftar alamat",
            value="https://www.bca.co.id\nhttp://bca-login-update.test\nhttps://www.google.com\nhttp://rricrosoft.com",
            key="beranda_banyak_url_engine_v4",
            height=190,
        )
        daftar = parse_url_bebas(teks_bebas, tambah_https=True, hapus_duplikat=True)
        panel("Alamat terdeteksi", f"{len(daftar)} URL siap diperiksa.", "gold")
        tabel_rapi(pd.DataFrame({"url": daftar}), max_rows=30)
        if st.button("Periksa semua", key="beranda_periksa_banyak_engine_v4"):
            jalankan_uji_banyak_url(engine, daftar)

    with tab_set:
        nama_paket = st.selectbox("Pilih paket uji", list(DATASET_UJI_CEPAT.keys()), key="beranda_paket_v4")
        daftar_paket = DATASET_UJI_CEPAT[nama_paket]
        tabel_rapi(pd.DataFrame({"url": daftar_paket}), max_rows=40)
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Jalankan paket", key="beranda_run_paket_v4"):
                jalankan_uji_banyak_url(engine, daftar_paket)
        with col_b:
            st.download_button(
                "Unduh paket",
                data=pd.DataFrame({"url": daftar_paket}).to_csv(index=False).encode("utf-8"),
                file_name=f"paket_uji_{nama_paket.lower().replace(' ', '_')}.csv",
                mime="text/csv",
                key=widget_key("download_paket_v4"),
            )

    with tab_ide:
        tampilkan_feature_grid()
        panel("Saran uji", "Bandingkan domain resmi dengan domain tiruan. Misalnya bca.co.id melawan bca-login-update.test, atau microsoft.com melawan rricrosoft.com.", "yellow")

    html("</div>")


def halaman_beranda(engine):
    hero(
        "PhishRisk System",
        "Pemeriksa URL dan File dengan Best Engine",
        "Dashboard ini memakai Best Engine: model lokal, URL intelligence, file analyzer, dan Public Threat Intelligence. Ringkas, defensif, dan tidak sok jadi antivirus sakti.",
        ["Best Engine", "PhishTank", "URLhaus Ready", "File Statis"],
    )

    riwayat = pd.DataFrame(st.session_state.riwayat)
    hasil_url = selaraskan_dataframe_url(st.session_state.hasil_url_terakhir)
    hasil_file = selaraskan_dataframe_file(st.session_state.hasil_file_terakhir)

    metrik_kartu([
        {"label": "Engine", "nilai": "V1", "catatan": "Model + Public TI.", "warna": "gold"},
        {"label": "URL terakhir", "nilai": len(hasil_url), "catatan": "Hasil sesi terakhir.", "warna": "normal"},
        {"label": "File terakhir", "nilai": len(hasil_file), "catatan": "File sesi terakhir.", "warna": "normal"},
        {"label": "Riwayat", "nilai": len(riwayat), "catatan": "Pemeriksaan tersimpan.", "warna": "normal"},
    ], kolom=4)

    section_title("Fitur Utama", "Isi dipadatkan agar user tidak perlu membaca novel cyber security.")
    tampilkan_feature_grid()

    section_title("Alur Kerja", "Masukkan data, baca hasil, ambil tindakan.")
    c1, c2, c3 = st.columns(3)
    with c1:
        step_card("1", "Input", "Masukkan satu URL, banyak URL, CSV, atau file.")
    with c2:
        step_card("2", "Analisis", "Best Engine menggabungkan model, intelligence lokal, dan Public TI.")
    with c3:
        step_card("3", "Tindakan", "Ikuti rekomendasi: lanjut hati-hati, tinjau, atau hindari.")

    render_lab_uji_bebas_beranda(engine)

    if not hasil_url.empty:
        section_title("Hasil URL Terakhir", "Ringkasan pemeriksaan terakhir.")
        tampilkan_ringkasan_url(hasil_url)


def halaman_periksa_url(engine):
    hero(
        "Pemeriksaan URL",
        "Input Link Bebas",
        "Periksa satu URL, banyak URL, atau CSV. Hasil memakai Best Engine dan Public Threat Intelligence.",
        ["Input bebas", "Batch", "CSV", "Public TI"],
    )

    panel("Cara pakai", "Masukkan alamat dari browser, chat, email, atau dokumen. Sistem menilai pola URL, domain resmi, brand tiruan, dan catatan eksternal.", "gold")

    tab_satu, tab_banyak, tab_csv, tab_public = st.tabs(["Satu URL", "Banyak URL", "CSV", "Public TI"])

    with tab_satu:
        with st.container(border=True):
            url = st.text_input(
                "Alamat web",
                value="",
                placeholder="Contoh: shopee.co.id atau https://baak.gunadarma.ac.id",
                key="url_satu_engine_v4",
            )
            col_a, col_b = st.columns(2)
            with col_a:
                tombol = st.button("Periksa alamat", key="periksa_satu_url_engine_v4")
            with col_b:
                st.download_button(
                    "Unduh contoh URL",
                    data=pd.DataFrame({"url": CONTOH_URL}).to_csv(index=False).encode("utf-8"),
                    file_name="contoh_url_phishrisk_engine_v4.csv",
                    mime="text/csv",
                    key=widget_key("download_contoh_url_v4"),
                )
        if tombol:
            jalankan_uji_satu_url(engine, url)

    with tab_banyak:
        teks = st.text_area(
            "Teks berisi alamat",
            value="\n".join(CONTOH_URL),
            height=240,
            key="teks_banyak_url_engine_v4",
        )
        col_a, col_b = st.columns(2)
        with col_a:
            tambah_https = st.checkbox("Tambahkan https:// jika belum ada", value=True, key="batch_tambah_https_v4")
        with col_b:
            hapus_duplikat = st.checkbox("Hapus duplikat", value=True, key="batch_duplikat_v4")
        daftar = parse_url_bebas(teks, tambah_https=tambah_https, hapus_duplikat=hapus_duplikat)
        panel("Alamat terdeteksi", f"{len(daftar)} URL siap dianalisis.", "gold")
        tabel_rapi(pd.DataFrame({"url": daftar}), max_rows=80)
        if st.button("Periksa semua alamat", key="periksa_banyak_url_engine_v4"):
            jalankan_uji_banyak_url(engine, daftar)

    with tab_csv:
        file_csv = st.file_uploader("Unggah CSV URL", type=["csv"], key="csv_url_uploader_engine_v4")
        st.download_button(
            "Unduh template CSV",
            data=pd.DataFrame({"url": CONTOH_URL}).to_csv(index=False).encode("utf-8"),
            file_name="template_url_engine_v4.csv",
            mime="text/csv",
            key=widget_key("download_template_csv_v4"),
        )
        if file_csv is not None:
            data_csv = pd.read_csv(file_csv)
            tabel_rapi(data_csv.head(20), max_rows=20)
            kolom_url = st.selectbox("Pilih kolom URL", data_csv.columns.tolist(), key="kolom_url_csv_v4")
            if st.button("Periksa URL dari CSV", key="periksa_csv_url_engine_v4"):
                daftar = data_csv[kolom_url].dropna().astype(str).str.strip().tolist()
                jalankan_uji_banyak_url(engine, daftar)

    with tab_public:
        bullet_panel(
            "Sinyal Public Threat Intelligence",
            [
                "PhishTank dipakai sebagai catatan URL phishing.",
                "URLhaus siap dipakai untuk URL malware jika Auth-Key sudah diisi.",
                "Jika Public TI tidak menemukan data, hasil tetap mengikuti Engine lokal.",
                "Catatan ringan tidak langsung membuat domain resmi menjadi berbahaya.",
            ],
            "yellow",
        )


def halaman_periksa_file(engine):
    hero(
        "Pemeriksaan File",
        "Upload File Bebas",
        "Unggah satu atau banyak file. Sistem membaca metadata, kata mencurigakan, dan URL tertanam tanpa menjalankan file.",
        ["Statis", "Multi file", "URL dalam file", "CSV output"],
    )

    metrik_kartu([
        {"label": "Mode", "nilai": "Statis", "catatan": "File tidak dijalankan.", "warna": "green"},
        {"label": "Engine", "nilai": "V1", "catatan": "URL dalam file ikut dicek Public TI.", "warna": "gold"},
        {"label": "Output", "nilai": "CSV", "catatan": "Hasil bisa diunduh.", "warna": "yellow"},
    ], kolom=3)

    bullet_panel(
        "Yang diperiksa",
        [
            "URL yang tertanam di file.",
            "Kata mencurigakan seperti login, password, OTP, verify, update, claim.",
            "Ekstensi, ukuran, hash, dan sinyal file berisiko.",
            "Catatan Public TI untuk URL yang ditemukan.",
        ],
        "gold",
    )

    with st.container(border=True):
        daftar_file = st.file_uploader(
            "Unggah file",
            accept_multiple_files=True,
            type=None,
            help="Sistem tidak menjalankan file. Aman untuk pemeriksaan awal.",
            key="uploader_file_engine_v4",
        )

        if daftar_file:
            data_info = pd.DataFrame([
                {"nama_file": file.name, "ukuran_kb": round(file.size / 1024, 2), "tipe_browser": file.type or "tidak_diketahui"}
                for file in daftar_file
            ])
            tabel_rapi(data_info, max_rows=80)

        tombol = st.button("Periksa file", key="tombol_periksa_file_engine_v4")

    if tombol:
        if not daftar_file:
            st.warning("Unggah minimal satu file terlebih dahulu.")
            return

        daftar_hasil_file = []
        daftar_hasil_url = []

        with st.spinner("Memeriksa file secara statis dengan Best Engine..."):
            for file in daftar_file:
                lokasi = simpan_file_upload(file)
                data_file, data_url = engine.analisis_file(lokasi)

                if isinstance(data_file, pd.DataFrame):
                    df_file = data_file.copy()
                elif isinstance(data_file, dict):
                    df_file = pd.DataFrame([data_file])
                else:
                    df_file = pd.DataFrame([{"nama_file": file.name}])

                df_file["nama_file"] = file.name
                df_file["sha256_upload"] = hash_file(lokasi)
                df_file = selaraskan_dataframe_file(df_file)
                daftar_hasil_file.append(df_file)

                for row in df_file.to_dict("records"):
                    tambah_riwayat_file(row)

                if isinstance(data_url, pd.DataFrame) and not data_url.empty:
                    df_url = selaraskan_dataframe_url(data_url.copy())
                    df_url["nama_file_sumber"] = file.name
                    daftar_hasil_url.append(df_url)

        data_file_final = pd.concat(daftar_hasil_file, ignore_index=True) if daftar_hasil_file else pd.DataFrame()
        data_url_final = pd.concat(daftar_hasil_url, ignore_index=True) if daftar_hasil_url else pd.DataFrame()

        st.session_state.hasil_file_terakhir = data_file_final
        st.session_state.hasil_url_dalam_file_terakhir = data_url_final

        tampilkan_ringkasan_file(data_file_final)
        tampilkan_tabel_file(data_file_final, data_url_final)

    if not st.session_state.hasil_file_terakhir.empty:
        with st.expander("Lihat hasil file terakhir"):
            tampilkan_tabel_file(st.session_state.hasil_file_terakhir, st.session_state.hasil_url_dalam_file_terakhir)


def halaman_threat_intel(engine):
    hero(
        "Public Threat Intelligence",
        "PhishTank dan URLhaus",
        "Halaman ini menunjukkan cara Best Engine memakai sumber eksternal sebagai sinyal tambahan, bukan sebagai hakim tunggal yang dramatis.",
        ["PhishTank", "URLhaus", "Sinyal tambahan", "Auth optional"],
    )

    metrik_kartu([
        {"label": "PhishTank", "nilai": "Aktif", "catatan": "Cek catatan phishing.", "warna": "green"},
        {"label": "URLhaus", "nilai": "Ready", "catatan": "Butuh Auth-Key untuk query penuh.", "warna": "yellow"},
        {"label": "Mode", "nilai": "Tambahan", "catatan": "Engine lokal tetap dasar utama.", "warna": "gold"},
    ], kolom=3)

    tab_uji, tab_status, tab_env = st.tabs(["Uji Public TI", "Cara baca", "Env"])

    with tab_uji:
        url = st.text_input("URL untuk diuji", value="https://www.google.com", key="public_ti_url_test")
        if st.button("Cek dengan Best Engine", key="public_ti_test_button"):
            hasil = jalankan_uji_satu_url(engine, url)
            if hasil:
                data_public = pd.DataFrame([
                    {"Sumber": "PhishTank", "Status": hasil.get("phishtank_status", "-"), "Skor": hasil.get("public_ti_score", "-")},
                    {"Sumber": "URLhaus", "Status": hasil.get("urlhaus_query_status", "-"), "Skor": hasil.get("public_ti_score", "-")},
                    {"Sumber": "Final V4", "Status": hasil.get("hasil_akhir", "-"), "Skor": hasil.get("skor_final", "-")},
                ])
                tabel_rapi(data_public, max_rows=20)

    with tab_status:
        bullet_panel(
            "Aturan baca Public TI",
            [
                "Found + valid + verified berarti sinyal kuat.",
                "Found tapi belum valid hanya catatan ringan.",
                "Tidak ditemukan bukan berarti pasti aman.",
                "URLhaus butuh Auth-Key untuk bekerja penuh.",
            ],
            "gold",
        )

    with tab_env:
        data_env = pd.DataFrame([
            {"Nama": "PHISHTANK_APP_KEY", "Status": "Opsional", "Keterangan": "Bisa mengurangi batasan request."},
            {"Nama": "URLHAUS_AUTH_KEY", "Status": "Opsional tapi disarankan", "Keterangan": "Dibutuhkan untuk query URLhaus modern."},
            {"Nama": "PHISHRISK_PUBLIC_TI_TIMEOUT", "Status": "Opsional", "Keterangan": "Batas waktu request."},
        ])
        tabel_rapi(data_env, max_rows=20)


def jelaskan_dengan_ai_fallback(hasil):
    hasil = selaraskan_hasil_url(hasil)
    try:
        import ai_explainer
        explainer = ai_explainer.PhishRiskAIExplainer(aktifkan_ai=False)
        if hasattr(explainer, "jelaskan_hasil_url"):
            penjelasan = explainer.jelaskan_hasil_url(hasil)
            if isinstance(penjelasan, dict):
                return penjelasan
    except Exception:
        pass

    return {
        "ringkasan": f"Hasil Best Engine: {hasil.get('hasil_akhir', '-')} dengan kategori {hasil.get('kategori_risiko', '-')}.",
        "alasan_sederhana": hasil.get("intelligence_reason", hasil.get("public_ti_reason", "-")),
        "rekomendasi": hasil.get("rekomendasi", "-"),
    }


def halaman_ai_laporan(engine):
    hero(
        "AI dan Laporan",
        "Penjelasan Hasil yang Mudah Dibaca",
        "Halaman ini membuat ringkasan sederhana dari hasil Best Engine. Jika AI eksternal belum aktif, fallback lokal tetap dipakai.",
        ["Fallback lokal", "Ringkasan", "Rekomendasi", "Markdown"],
    )

    url = st.text_input("URL untuk dibuatkan penjelasan", value="http://bca-login-update.test", key="ai_laporan_url")
    if st.button("Buat penjelasan", key="ai_laporan_button"):
        hasil = selaraskan_hasil_url(engine.analisis_url(normalisasi_url_input(url)))
        penjelasan = jelaskan_dengan_ai_fallback(hasil)

        col1, col2 = st.columns([1, 1])
        with col1:
            tampilkan_status_url(hasil)
        with col2:
            panel("Ringkasan", penjelasan.get("ringkasan", penjelasan.get("ringkasan_ai", "-")), "gold")
            panel("Alasan sederhana", penjelasan.get("alasan_sederhana", "-"), "yellow")
            panel("Rekomendasi", penjelasan.get("rekomendasi", penjelasan.get("rekomendasi_ai", "-")), "green")

        isi_md = f"""# Laporan Singkat PhishRisk

Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

URL: {hasil.get('url', '-')}

Hasil: {hasil.get('hasil_akhir', '-')}
Kategori: {hasil.get('kategori_risiko', '-')}
Skor: {hasil.get('skor_final', '-')}

Ringkasan:
{penjelasan.get('ringkasan', penjelasan.get('ringkasan_ai', '-'))}

Alasan:
{penjelasan.get('alasan_sederhana', '-')}

Rekomendasi:
{penjelasan.get('rekomendasi', penjelasan.get('rekomendasi_ai', '-'))}
"""
        st.download_button(
            "Unduh laporan Markdown",
            data=isi_md.encode("utf-8"),
            file_name="laporan_singkat_phishrisk.md",
            mime="text/markdown",
            key=widget_key("download_laporan_md"),
        )


def halaman_batch_lab(engine):
    hero(
        "Engine Lab",
        "Analisis Banyak Data",
        "Bandingkan banyak URL atau file terakhir dengan filter sederhana, ringkasan, dan export CSV.",
        ["Filter", "Prioritas", "CSV", "Best Engine"],
    )

    tab_url, tab_file, tab_public = st.tabs(["Batch URL", "Batch File", "Public TI"])

    with tab_url:
        data = selaraskan_dataframe_url(st.session_state.hasil_url_terakhir)
        if data.empty:
            panel("Belum ada data", "Periksa banyak URL dulu dari halaman URL.", "yellow")
        else:
            tampilkan_ringkasan_url(data)
            with st.container(border=True):
                daftar_status = sorted(data["hasil_akhir"].dropna().unique().tolist()) if "hasil_akhir" in data.columns else []
                status = st.multiselect("Pilih hasil", daftar_status, default=daftar_status, key="batch_status_v4")
                skor_min = st.slider("Skor minimum", 0, 100, 0, key="batch_skor_v4")
                public_only = st.checkbox("Tampilkan yang punya catatan Public TI saja", value=False, key="batch_public_only_v4")

                data_filter = data.copy()
                if status:
                    data_filter = data_filter[data_filter["hasil_akhir"].isin(status)]
                if "skor_final" in data_filter.columns:
                    data_filter = data_filter[pd.to_numeric(data_filter["skor_final"], errors="coerce").fillna(0) >= skor_min]
                if public_only and "public_ti_score" in data_filter.columns:
                    data_filter = data_filter[pd.to_numeric(data_filter["public_ti_score"], errors="coerce").fillna(0) > 0]

                tampilkan_tabel_url(data_filter)

    with tab_file:
        data_file = selaraskan_dataframe_file(st.session_state.hasil_file_terakhir)
        data_url = selaraskan_dataframe_url(st.session_state.hasil_url_dalam_file_terakhir)
        if data_file.empty:
            panel("Belum ada data", "Periksa file dulu dari halaman File.", "yellow")
        else:
            tampilkan_ringkasan_file(data_file)
            tampilkan_tabel_file(data_file, data_url)

    with tab_public:
        data = selaraskan_dataframe_url(st.session_state.hasil_url_terakhir)
        if data.empty:
            panel("Belum ada data", "Public TI akan muncul setelah URL diperiksa.", "yellow")
        else:
            kolom = [k for k in ["url", "public_ti_score", "public_ti_status", "public_ti_sources", "phishtank_status", "urlhaus_query_status", "public_ti_reason"] if k in data.columns]
            tabel_rapi(data[kolom], max_rows=80)


def halaman_rekomendasi():
    hero(
        "Rekomendasi",
        "Tindakan Setelah Melihat Hasil",
        "Ringkas saja: aman tetap hati-hati, tinjauan harus dicek ulang, berisiko jangan disentuh.",
        ["Aman", "Tinjauan", "Berisiko", "File"],
    )

    tab_aman, tab_tinjauan, tab_risiko, tab_file, tab_darurat = st.tabs(["Aman", "Tinjauan", "Berisiko", "File", "Darurat"])

    with tab_aman:
        bullet_panel("Lanjut hati-hati", ["Ketik domain manual.", "Gunakan bookmark.", "Cek lagi sebelum login.", "Jangan kirim OTP."], "green")
    with tab_tinjauan:
        bullet_panel("Tahan dulu", ["Cek domain resmi.", "Bandingkan sumber link.", "Hubungi admin resmi.", "Jangan masukkan data sensitif."], "yellow")
    with tab_risiko:
        bullet_panel("Hindari", ["Jangan buka.", "Jangan login.", "Jangan unduh file.", "Laporkan link."], "red")
    with tab_file:
        bullet_panel("File aman diperiksa statis", ["Jangan jalankan APK/EXE/LNK/BAT/CMD/PS1/VBS asing.", "Cek URL dalam file.", "Simpan hasil CSV.", "Hapus file dari sumber tidak jelas."], "gold")
    with tab_darurat:
        bullet_panel("Kalau sudah terlanjur klik/login", ["Ganti password dari website resmi.", "Logout semua sesi.", "Aktifkan 2FA.", "Hubungi bank/kampus/kantor jika ada data penting.", "Simpan bukti."], "red")


def halaman_ciri():
    hero(
        "Ciri-Ciri",
        "Pola URL dan File Berisiko",
        "Panduan cepat untuk membaca pola phishing tanpa istilah yang bikin kepala ingin restart.",
        ["Domain", "Brand", "Kata", "File"],
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        bullet_panel("Cenderung aman", ["Domain utama jelas.", "HTTPS aktif.", "Sumber resmi.", "Tidak memaksa login.", "Tidak meminta OTP."], "green")
    with col2:
        bullet_panel("URL mencurigakan", ["Mirip brand resmi.", "Ada login/update/verify.", "Huruf diganti angka.", "Subdomain panjang.", "Path penuh parameter."], "yellow")
    with col3:
        bullet_panel("File berisiko", ["Script/executable asing.", "Macro diminta aktif.", "ZIP berisi file aneh.", "APK luar toko resmi.", "PDF mengarah login."], "red")

    data = pd.DataFrame([
        {"Contoh": "rricrosoft.com", "Masalah": "Mirip microsoft.com."},
        {"Contoh": "rnicrosoft.com", "Masalah": "r+n bisa terlihat seperti m."},
        {"Contoh": "micros0ft-login-update.test", "Masalah": "0 mengganti o dan memakai kata mendesak."},
        {"Contoh": "bca-login-update.test", "Masalah": "Nama brand bukan domain resmi."},
        {"Contoh": "xn--micrsoft-q4a.test", "Masalah": "Punycode menyamarkan domain."},
    ])
    section_title("Contoh Pola Tiruan", "Contoh ini untuk edukasi defensif.")
    tabel_rapi(data, max_rows=20)


def halaman_panduan():
    hero(
        "Panduan",
        "Cara Pakai Singkat",
        "Tiga langkah saja. Karena user datang untuk cek link, bukan ikut seminar tiga SKS.",
        ["Input", "Analisis", "Tindakan"],
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        step_card("1", "Masukkan data", "URL, daftar URL, CSV, atau file.")
    with col2:
        step_card("2", "Baca hasil", "Lihat skor, kategori, alasan, dan Public TI.")
    with col3:
        step_card("3", "Ambil tindakan", "Aman hati-hati, tinjauan cek manual, berisiko hindari.")

    tab_url, tab_file, tab_public, tab_batas = st.tabs(["URL", "File", "Public TI", "Batasan"])
    with tab_url:
        bullet_panel("URL", ["Satu URL untuk cek cepat.", "Banyak URL untuk daftar link.", "CSV untuk data yang lebih rapi.", "Download hasil jika perlu laporan."], "gold")
    with tab_file:
        bullet_panel("File", ["Upload file.", "Sistem membaca statis.", "URL di dalam file ikut diperiksa.", "File tidak dijalankan."], "yellow")
    with tab_public:
        bullet_panel("Public TI", ["PhishTank membaca catatan phishing.", "URLhaus siap untuk malware URL.", "Tidak ditemukan bukan berarti pasti aman.", "Gunakan sebagai sinyal tambahan."], "green")
    with tab_batas:
        bullet_panel("Batasan", ["Tidak membuka website langsung.", "Tidak membuktikan pemilik domain.", "Tidak menjalankan file.", "Tidak menggantikan pemeriksaan keamanan penuh."], "red")


def halaman_beta():
    hero(
        "Beta dan Salah Deteksi",
        "Kenapa Hasil Bisa Meleset",
        "Sistem membaca pola. Website resmi bisa perlu tinjauan jika bentuk alamatnya tidak umum.",
        ["False positive", "False negative", "Koreksi", "Update"],
    )

    metrik_kartu([
        {"label": "Sumber utama", "nilai": "Pola", "catatan": "Panjang URL, domain, kata, dan TLD."},
        {"label": "Perbaikan", "nilai": "V4", "catatan": "Public TI dan kalibrasi."},
        {"label": "Solusi", "nilai": "Koreksi", "catatan": "Tambahkan domain resmi dan feedback user."},
    ], kolom=3)

    bullet_panel(
        "Kenapa website resmi bisa terlihat berisiko?",
        [
            "Subdomain panjang bisa mirip pola tidak umum.",
            "Path resmi kadang panjang dan penuh parameter.",
            "Model tidak selalu tahu kepemilikan domain jika belum masuk daftar resmi.",
            "Public TI bisa punya catatan ringan yang perlu dibaca hati-hati.",
        ],
        "yellow",
    )

    bullet_panel(
        "Cara menyikapi",
        [
            "Baca kategori dan alasan, bukan hanya angka.",
            "Cek domain utama.",
            "Bandingkan dengan sumber resmi.",
            "Laporkan salah deteksi untuk update berikutnya.",
        ],
        "green",
    )


def halaman_sistem():
    hero(
        "Sistem",
        "Kesiapan Best Engine",
        "Ringkasan komponen yang dipakai aplikasi. Ini supaya website tidak diam-diam memakai engine lama seperti fosil yang masih ngotot bekerja.",
        ["Best Engine", "Model V1", "Public TI", "AI fallback"],
    )

    daftar_file = [
        {"komponen": "Best Engine", "fungsi": "Menggabungkan Best Engine dan Public Threat Intelligence.", "lokasi": DIREKTORI_SRC / "phishrisk_engine_v4.py", "catatan": "Wajib untuk versi terbaru."},
        {"komponen": "Public TI", "fungsi": "PhishTank dan URLhaus.", "lokasi": DIREKTORI_SRC / "public_threat_intelligence.py", "catatan": "Sinyal tambahan."},
        {"komponen": "CLI V4", "fungsi": "Menjalankan Best Engine dari terminal.", "lokasi": DIREKTORI_SRC / "run_phishrisk_v4.py", "catatan": "Untuk testing."},
        {"komponen": "Best Engine", "fungsi": "Dasar prediksi lokal.", "lokasi": DIREKTORI_SRC / "phishrisk_engine_v3.py", "catatan": "Fallback dan core."},
        {"komponen": "URL Intelligence", "fungsi": "Domain resmi, brand, dan lookalike.", "lokasi": DIREKTORI_SRC / "url_intelligence.py", "catatan": "Wajib."},
        {"komponen": "File Analyzer", "fungsi": "Analisis file statis.", "lokasi": DIREKTORI_SRC / "file_static_analyzer.py", "catatan": "Wajib."},
        {"komponen": "Model terbaik", "fungsi": "Model prediksi URL.", "lokasi": DIREKTORI_PROJECT / "models" / "model_terbaik_intelligence_v2.pkl", "catatan": "File besar."},
        {"komponen": "Fitur model", "fungsi": "Daftar fitur model.", "lokasi": DIREKTORI_OUTPUT / "daftar_fitur_intelligence_v2.json", "catatan": "Harus sinkron."},
        {"komponen": "AI Explainer", "fungsi": "Penjelasan fallback/AI.", "lokasi": DIREKTORI_SRC / "ai_explainer.py", "catatan": "Opsional."},
    ]

    data = []
    for item in daftar_file:
        lokasi = item["lokasi"]
        tersedia = lokasi.exists()
        data.append({
            "komponen": item["komponen"],
            "fungsi": item["fungsi"],
            "tersedia": tersedia,
            "ukuran_kb": round(lokasi.stat().st_size / 1024, 2) if tersedia else 0,
            "catatan": item["catatan"],
            "lokasi": str(lokasi),
        })

    df = pd.DataFrame(data)
    jumlah_siap = int(df["tersedia"].sum()) if not df.empty else 0

    metrik_kartu([
        {"label": "Komponen siap", "nilai": f"{jumlah_siap}/{len(df)}", "catatan": "File penting ditemukan.", "warna": "green" if jumlah_siap == len(df) else "yellow"},
        {"label": "Engine", "nilai": "V4", "catatan": "Dipakai Streamlit.", "warna": "gold"},
        {"label": "Public TI", "nilai": "Aktif", "catatan": "PhishTank + URLhaus ready.", "warna": "green"},
        {"label": "Output", "nilai": "CSV", "catatan": "Hasil bisa diunduh.", "warna": "gold"},
    ], kolom=4)

    section_title("Validasi Komponen", "Tabel ini sengaja dibuat sederhana.")
    tabel_rapi(df[["komponen", "fungsi", "tersedia", "ukuran_kb", "catatan"]], max_rows=80)

    metadata_v4 = muat_metadata(LOKASI_METADATA_ENGINE_V4)
    metadata_step10 = muat_metadata(LOKASI_METADATA_STEP10)
    tab_v4, tab_step10 = st.tabs(["Metadata V1", "Metadata Best Engine"])
    with tab_v4:
        if metadata_v4:
            st.json(metadata_v4)
        else:
            panel("Metadata V1 belum ditemukan", "Jalankan Best Engine atau cek reports/outputs.", "yellow")
    with tab_step10:
        if metadata_step10:
            st.json(metadata_step10)
        else:
            panel("Metadata Best Engine belum ditemukan", "File ini opsional untuk ringkasan.", "yellow")


def halaman_tentang():
    hero(
        "Tentang Project",
        "PhishRisk System",
        "Project Data Science x Cyber Security untuk membantu user membaca risiko URL dan file sebelum klik, login, atau membuka lampiran.",
        ["Portfolio", "Defensif", "Machine Learning", "Streamlit"],
    )

    col1, col2 = st.columns([1.1, .9])
    with col1:
        bullet_panel(
            "Tujuan",
            [
                "Mendeteksi URL yang perlu diwaspadai.",
                "Membaca URL dan metadata dari file secara statis.",
                "Memberi alasan dan rekomendasi yang mudah dipahami.",
                "Menggabungkan model lokal, intelligence lokal, dan Public TI.",
            ],
            "gold",
        )
    with col2:
        bullet_panel(
            "Author",
            [
                f"Nama: {AUTHOR_INFO.get('Nama')}",
                f"WhatsApp: {AUTHOR_INFO.get('WhatsApp')}",
                f"Instagram: {AUTHOR_INFO.get('Instagram')}",
                f"LinkedIn: {AUTHOR_INFO.get('LinkedIn')}",
                f"GitHub: {AUTHOR_INFO.get('GitHub')}",
            ],
            "green",
        )


def halaman_game_cyber(engine):
    hero(
        "Game Cyber",
        "Latihan Membaca URL",
        "Mini game ringan untuk melatih user membedakan domain resmi, tiruan brand, dan link berisiko.",
        ["Tebak risiko", "Cari sinyal", "Best Engine", "Latihan seru"],
    )

    if "game_skor_v4" not in st.session_state:
        st.session_state.game_skor_v4 = 0
    if "game_total_v4" not in st.session_state:
        st.session_state.game_total_v4 = 0
    if "game_index_v4" not in st.session_state:
        st.session_state.game_index_v4 = 0

    soal = [
        {"url": "https://praktikum.gunadarma.ac.id", "jawaban": "Terlihat Aman", "alasan": "Domain berada di bawah gunadarma.ac.id."},
        {"url": "http://rricrosoft.com", "jawaban": "Berisiko", "alasan": "Domain mirip Microsoft, tetapi bukan domain resmi."},
        {"url": "http://bca-login-update.test", "jawaban": "Berisiko", "alasan": "Memakai nama BCA dengan kata login/update di domain lain."},
        {"url": "https://www.bca.co.id", "jawaban": "Terlihat Aman", "alasan": "Domain resmi BCA."},
        {"url": "https://xn--micrsoft-q4a.test", "jawaban": "Berisiko", "alasan": "Punycode bisa menyamarkan domain."},
    ]

    item = soal[st.session_state.game_index_v4 % len(soal)]

    metrik_kartu([
        {"label": "Skor", "nilai": st.session_state.game_skor_v4, "catatan": "Jawaban benar.", "warna": "gold"},
        {"label": "Percobaan", "nilai": st.session_state.game_total_v4, "catatan": "Total cek.", "warna": "flat"},
        {"label": "Mode", "nilai": "Latihan", "catatan": "Tidak memengaruhi model.", "warna": "green"},
    ], kolom=3)

    html(f'<div class="game-board"><div class="card-title">Tebak risiko URL ini</div><div class="game-url">{aman_teks(item["url"])}</div></div>')

    jawaban = st.radio("Jawaban", ["Terlihat Aman", "Perlu Tinjauan", "Berisiko"], horizontal=True, key=f"jawaban_game_v4_{st.session_state.game_index_v4}")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Cek jawaban", key="cek_game_v4"):
            st.session_state.game_total_v4 += 1
            if jawaban == item["jawaban"]:
                st.session_state.game_skor_v4 += 1
                callout("Benar", item["alasan"], "safe")
            else:
                callout("Belum tepat", f"Jawaban yang lebih sesuai: {item['jawaban']}. {item['alasan']}", "review")
    with c2:
        if st.button("Soal berikutnya", key="next_game_v4"):
            st.session_state.game_index_v4 = (st.session_state.game_index_v4 + 1) % len(soal)
            st.rerun()
    with c3:
        if st.button("Jalankan Best Engine", key="run_game_engine_v4"):
            jalankan_uji_satu_url(engine, item["url"])


MENU_UTAMA = [
    "Beranda",
    "URL",
    "File",
    "Threat Intel",
    "Batch",
    "AI & Laporan",
    "Rekomendasi",
    "Ciri",
    "Panduan",
    "Game",
    "Beta",
    "Riwayat",
    "Tentang",
    "Sistem",
]

MENU_MAP = {
    "Beranda": "Beranda",
    "URL": "Input Alamat Link",
    "File": "Input File",
    "Threat Intel": "Public Threat Intelligence",
    "Batch": "Engine Lab",
    "AI & Laporan": "AI dan Laporan",
    "Rekomendasi": "Rekomendasi dan Antisipasi",
    "Ciri": "Ciri-Ciri",
    "Panduan": "Panduan",
    "Game": "Quick PhishRisk Training",
    "Beta": "Beta dan Salah Deteksi",
    "Riwayat": "Riwayat",
    "Tentang": "Tentang Project",
    "Sistem": "Informasi Sistem",
}


def buat_navigasi():
    if "halaman_aktif" not in st.session_state:
        st.session_state.halaman_aktif = "Beranda"

    default = st.session_state.halaman_aktif if st.session_state.halaman_aktif in MENU_UTAMA else "Beranda"

    html(
        """
        <div class="top-nav-card">
            <div class="top-nav-head">
                <div class="brand-block">
                    <div class="brand-mark">PR</div>
                    <div>
                        <div class="brand-title">PhishRisk</div>
                        <div class="brand-sub">Best Engine dashboard</div>
                    </div>
                </div>
                <div class="nav-badge">Best Engine</div>
            </div>
        """
    )

    pilihan = st.selectbox(
        "Pilih halaman",
        MENU_UTAMA,
        index=MENU_UTAMA.index(default),
        label_visibility="collapsed",
        key="navigasi_utama_dropdown_v4",
    )

    html(
        f"""
            <div class="nav-help">Halaman aktif: <b>{aman_teks(MENU_MAP.get(pilihan, pilihan))}</b>. Gunakan dropdown ini agar nyaman di mobile.</div>
        </div>
        """
    )

    st.session_state.halaman_aktif = pilihan
    return MENU_MAP.get(pilihan, "Beranda")


def buat_sidebar():
    return buat_navigasi()


def footer_site():
    html(
        f"""
        <footer class="site-footer">
            <div class="footer-grid">
                <div>
                    <div class="footer-name">{aman_teks(AUTHOR_INFO.get('Nama', 'Harbangan Panjaitan'))}</div>
                    <div class="footer-note">PhishRisk System. Best Engine untuk pemeriksaan URL, file, Public Threat Intelligence, dan laporan defensif.</div>
                </div>
                <div class="footer-links">
                    <a class="footer-link" href="https://wa.me/628158883565" target="_blank">WhatsApp</a>
                    <a class="footer-link" href="{aman_teks(AUTHOR_INFO.get('Instagram', '#'))}" target="_blank">Instagram</a>
                    <a class="footer-link" href="{aman_teks(AUTHOR_INFO.get('LinkedIn', '#'))}" target="_blank">LinkedIn</a>
                    <a class="footer-link" href="{aman_teks(AUTHOR_INFO.get('GitHub', '#'))}" target="_blank">GitHub</a>
                </div>
            </div>
            <div class="footer-line">Fokus project: Data Science, Machine Learning, dan Cyber Security defensif. Sistem membantu menilai risiko awal, bukan menjalankan file, membuat phishing, atau menggantikan audit keamanan penuh.</div>
        </footer>
        """
    )


def main():
    pasang_css()
    pasang_css_final_override()
    pasang_css_v8_polish()
    pasang_css_engine_v4()
    siapkan_state()

    try:
        engine = muat_engine()
    except Exception as error:
        hero(
            "Aplikasi gagal dimuat",
            "Best Engine Belum Siap",
            "Pastikan file phishrisk_engine_v4.py, public_threat_intelligence.py, model_terbaik_intelligence_v2.pkl, dan daftar_fitur_intelligence_v2.json tersedia.",
            ["Cek src", "Cek model", "Cek Best Engine"],
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
    elif halaman == "Public Threat Intelligence":
        halaman_threat_intel(engine)
    elif halaman == "Engine Lab":
        halaman_batch_lab(engine)
    elif halaman == "AI dan Laporan":
        halaman_ai_laporan(engine)
    elif halaman == "Rekomendasi dan Antisipasi":
        halaman_rekomendasi()
    elif halaman == "Ciri-Ciri":
        halaman_ciri()
    elif halaman == "Panduan":
        halaman_panduan()
    elif halaman == "Quick PhishRisk Training":
        halaman_game_cyber(engine)
    elif halaman == "Beta dan Salah Deteksi":
        halaman_beta()
    elif halaman == "Riwayat":
        halaman_riwayat()
    elif halaman == "Tentang Project":
        halaman_tentang()
    else:
        halaman_sistem()

    footer_site()

# ============================================================
# UPGRADE V12 - GAME CENTER + STREAMLIT FEATURE EXPANSION
# Ditambahkan setelah versi Engine V4 agar website lebih kaya,
# tetap defensif, dan tetap selaras dengan PhishRisk Engine V4.
# ============================================================

GAME_URL_BANK = [
    {
        "url": "https://www.bca.co.id",
        "jawaban": "Terlihat Aman",
        "level": "Pemula",
        "alasan": "Domain utama cocok dengan website resmi BCA dan tidak memakai pola mendesak.",
        "sinyal": ["Domain resmi", "HTTPS", "Tidak ada kata mendesak"],
        "aksi": "Buka dari bookmark atau ketik manual jika ingin login.",
    },
    {
        "url": "http://bca-login-update.test",
        "jawaban": "Berisiko",
        "level": "Pemula",
        "alasan": "Menggunakan nama BCA, tetapi bukan domain resmi dan memakai kata login/update.",
        "sinyal": ["Brand tidak resmi", "login", "update", "Bukan domain resmi"],
        "aksi": "Jangan login. Cek website resmi dari aplikasi atau bookmark.",
    },
    {
        "url": "https://praktikum.gunadarma.ac.id",
        "jawaban": "Terlihat Aman",
        "level": "Pemula",
        "alasan": "Domain berada di bawah gunadarma.ac.id yang masuk pembanding resmi.",
        "sinyal": ["Domain resmi", "Subdomain kampus", "HTTPS"],
        "aksi": "Tetap pastikan alamat diketik benar.",
    },
    {
        "url": "http://praktikum-gunadarma-login-update.test",
        "jawaban": "Berisiko",
        "level": "Menengah",
        "alasan": "Nama Gunadarma dipakai di domain lain dan digabung kata login/update.",
        "sinyal": ["Brand tidak resmi", "login", "update", "Tanda hubung"],
        "aksi": "Jangan isi akun. Buka portal kampus dari alamat resmi.",
    },
    {
        "url": "http://rricrosoft.com",
        "jawaban": "Berisiko",
        "level": "Menengah",
        "alasan": "Domain terlihat mirip Microsoft, tetapi hurufnya berbeda.",
        "sinyal": ["Domain mirip brand", "Salah eja", "Bukan domain resmi"],
        "aksi": "Jangan dipakai login. Bandingkan dengan microsoft.com.",
    },
    {
        "url": "http://rnicrosoft.com",
        "jawaban": "Berisiko",
        "level": "Menengah",
        "alasan": "Huruf r dan n dapat terlihat seperti m, sehingga domain bisa mengecoh mata.",
        "sinyal": ["Domain mirip brand", "Huruf mengecoh", "Bukan domain resmi"],
        "aksi": "Periksa huruf satu per satu sebelum membuka.",
    },
    {
        "url": "http://micros0ft-login-update.test",
        "jawaban": "Berisiko",
        "level": "Sulit",
        "alasan": "Angka 0 mengganti huruf o, ditambah kata login dan update.",
        "sinyal": ["Pengganti angka", "login", "update", "Brand tidak resmi"],
        "aksi": "Jangan login. Laporkan jika dikirim lewat chat/email.",
    },
    {
        "url": "https://xn--micrsoft-q4a.test",
        "jawaban": "Berisiko",
        "level": "Sulit",
        "alasan": "Punycode dapat menyamarkan bentuk domain.",
        "sinyal": ["Punycode", "Domain mirip brand", "Bukan domain resmi"],
        "aksi": "Jangan buka dari perangkat utama.",
    },
    {
        "url": "https://www.google.com",
        "jawaban": "Terlihat Aman",
        "level": "Pemula",
        "alasan": "Domain utama resmi, tetapi tetap cek konteks link jika berasal dari pesan asing.",
        "sinyal": ["Domain resmi", "HTTPS"],
        "aksi": "Aman dibuka dari sumber resmi. Jangan percaya iklan atau redirect aneh begitu saja.",
    },
    {
        "url": "http://paypal-verify-account.test",
        "jawaban": "Berisiko",
        "level": "Menengah",
        "alasan": "Nama PayPal dipakai di domain lain dengan kata verify/account.",
        "sinyal": ["Brand tidak resmi", "verify", "account", "Bukan domain resmi"],
        "aksi": "Jangan isi password atau data pembayaran.",
    },
]

GAME_FILE_CASES = [
    {
        "nama": "invoice_update.zip",
        "jawaban": "Berisiko",
        "alasan": "ZIP dari sumber tidak jelas bisa menyimpan file script atau shortcut berbahaya.",
        "sinyal": ["Arsip", "Lampiran asing", "Perlu analisis statis"],
    },
    {
        "nama": "catatan_kuliah.txt",
        "jawaban": "Perlu Tinjauan",
        "alasan": "TXT umumnya rendah risiko, tetapi tetap perlu dicek jika berisi link login.",
        "sinyal": ["Teks biasa", "Cek URL di dalam file"],
    },
    {
        "nama": "login_reward.html",
        "jawaban": "Berisiko",
        "alasan": "HTML dapat berisi halaman login palsu atau link pengarah.",
        "sinyal": ["HTML", "login", "reward"],
    },
    {
        "nama": "aplikasi_promo.apk",
        "jawaban": "Berisiko",
        "alasan": "APK dari luar sumber resmi tidak boleh dipasang sembarangan.",
        "sinyal": ["APK", "Instalasi aplikasi", "Izin berisiko"],
    },
    {
        "nama": "surat_resmi.pdf",
        "jawaban": "Perlu Tinjauan",
        "alasan": "PDF perlu dicek jika berisi link, JavaScript, atau aksi otomatis.",
        "sinyal": ["PDF", "Cek link", "Cek open action"],
    },
]

GAME_ACTION_CASES = [
    {
        "skenario": "Ada link bank dari WhatsApp yang meminta login ulang karena akun katanya diblokir.",
        "jawaban": "Cek domain resmi, jangan isi data dulu",
        "penjelasan": "Pesan yang menekan user agar cepat login sering dipakai pada penipuan.",
    },
    {
        "skenario": "Website kampus resmi terbaca Perlu Tinjauan karena bentuk URL panjang.",
        "jawaban": "Bandingkan dengan domain resmi dan simpan sebagai pembanding jika benar",
        "penjelasan": "Website resmi bisa salah terbaca jika bentuknya jarang muncul di dataset.",
    },
    {
        "skenario": "PDF dari email berisi link login dan kata OTP.",
        "jawaban": "Analisis file dulu, jangan klik link langsung",
        "penjelasan": "File dapat menjadi perantara menuju link berisiko.",
    },
    {
        "skenario": "Domain mirip brand memakai angka 0 sebagai pengganti huruf o.",
        "jawaban": "Anggap berisiko dan cek domain resmi",
        "penjelasan": "Pengganti angka adalah pola umum untuk mengecoh pengguna.",
    },
]

def pasang_css_game_v12():
    st.markdown(
        """
        <style>
        .game-hero-line{
            display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:.75rem;margin:.75rem 0 1rem;
        }
        .game-mini-card{
            border:1px solid rgba(255,255,255,.08);
            border-radius:22px;
            background:linear-gradient(145deg,rgba(255,255,255,.045),rgba(255,255,255,.012));
            padding:.9rem;
            box-shadow:0 16px 42px rgba(0,0,0,.24);
        }
        .game-mini-card b{display:block;color:#fff9ec;font-size:.98rem!important;letter-spacing:-.02em;margin-bottom:.18rem}
        .game-mini-card span{color:#c8bda9;font-size:.82rem!important;line-height:1.45!important}
        .game-shell{
            border:1px solid rgba(216,181,109,.34);
            border-radius:28px;
            background:
                radial-gradient(circle at 100% 0%,rgba(216,181,109,.14),transparent 30%),
                linear-gradient(145deg,rgba(216,181,109,.10),rgba(255,255,255,.012)),
                rgba(18,19,16,.86);
            padding:1rem;
            box-shadow:0 22px 70px rgba(0,0,0,.32);
            margin:.7rem 0 1rem;
        }
        .game-question{
            font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace!important;
            color:#ffe7ad!important;
            background:rgba(0,0,0,.30);
            border:1px solid rgba(216,181,109,.25);
            border-radius:18px;
            padding:.9rem;
            overflow-wrap:anywhere;
            font-size:.94rem!important;
            line-height:1.52!important;
        }
        .game-chip-row{display:flex;gap:.45rem;flex-wrap:wrap;margin:.7rem 0 .1rem;}
        .game-chip{
            border:1px solid rgba(255,255,255,.08);
            border-radius:999px;
            padding:.28rem .62rem;
            background:rgba(255,255,255,.035);
            color:#c8bda9;
            font-size:.78rem!important;
            font-weight:820!important;
        }
        .mission-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.75rem;margin:.75rem 0 1rem;}
        .mission-card{
            min-height:142px;
            border:1px solid rgba(255,255,255,.08);
            border-radius:22px;
            background:linear-gradient(145deg,rgba(255,255,255,.040),rgba(255,255,255,.012));
            padding:.95rem;
            box-shadow:0 14px 38px rgba(0,0,0,.22);
        }
        .mission-card strong{display:block;color:#fff9ec;font-size:1rem!important;margin-bottom:.35rem;letter-spacing:-.03em;}
        .mission-card p{color:#c8bda9!important;font-size:.82rem!important;line-height:1.48!important;margin:0!important;}
        .rank-box{
            border:1px solid rgba(155,199,159,.33);
            border-radius:22px;
            background:linear-gradient(145deg,rgba(155,199,159,.10),rgba(255,255,255,.012));
            padding:.9rem;margin:.65rem 0;
        }
        .rank-bar{height:10px;border-radius:999px;background:rgba(255,255,255,.08);overflow:hidden;border:1px solid rgba(255,255,255,.05);margin:.55rem 0;}
        .rank-fill{height:100%;border-radius:999px;background:linear-gradient(90deg,#9bc79f,#d6bd76,#e18478);}
        .copy-card{
            border:1px solid rgba(216,181,109,.26);
            border-radius:22px;
            background:rgba(0,0,0,.18);
            padding:.9rem;
            margin:.65rem 0;
        }
        .copy-card code{
            white-space:pre-wrap!important;
            color:#ffe7ad!important;
            font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace!important;
            font-size:.82rem!important;
        }
        @media(max-width:900px){
            .game-hero-line,.mission-grid{grid-template-columns:repeat(2,minmax(0,1fr));}
        }
        @media(max-width:560px){
            .game-hero-line,.mission-grid{grid-template-columns:1fr;}
            .game-shell{border-radius:20px;padding:.85rem;}
            .game-question{font-size:.81rem!important;border-radius:16px;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def game_init_v12():
    defaults = {
        "game_v12_score": 0,
        "game_v12_total": 0,
        "game_v12_streak": 0,
        "game_v12_index": 0,
        "game_v12_file_index": 0,
        "game_v12_action_index": 0,
        "game_v12_badges": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def game_add_score_v12(benar, badge=None):
    st.session_state.game_v12_total += 1
    if benar:
        st.session_state.game_v12_score += 1
        st.session_state.game_v12_streak += 1
        if badge and badge not in st.session_state.game_v12_badges:
            st.session_state.game_v12_badges.append(badge)
    else:
        st.session_state.game_v12_streak = 0


def game_accuracy_v12():
    total = max(1, int(st.session_state.get("game_v12_total", 0)))
    return round((int(st.session_state.get("game_v12_score", 0)) / total) * 100, 1)


def game_rank_v12():
    akurasi = game_accuracy_v12()
    skor = int(st.session_state.get("game_v12_score", 0))
    if skor >= 12 and akurasi >= 80:
        return "Threat Analyst"
    if skor >= 8:
        return "URL Investigator"
    if skor >= 4:
        return "Security Learner"
    return "New Defender"


def render_game_score_v12():
    akurasi = game_accuracy_v12()
    html(
        f"""
        <div class="game-hero-line">
            <div class="game-mini-card"><b>{aman_teks(st.session_state.game_v12_score)}</b><span>Jawaban benar</span></div>
            <div class="game-mini-card"><b>{aman_teks(st.session_state.game_v12_total)}</b><span>Total percobaan</span></div>
            <div class="game-mini-card"><b>{aman_teks(st.session_state.game_v12_streak)}</b><span>Streak benar</span></div>
            <div class="game-mini-card"><b>{aman_teks(game_rank_v12())}</b><span>Rank latihan</span></div>
        </div>
        <div class="rank-box">
            <div class="card-title">Akurasi latihan: {akurasi}%</div>
            <div class="rank-bar"><div class="rank-fill" style="width:{akurasi}%;"></div></div>
            <div class="small">Game ini tidak mengubah model. Fungsinya untuk melatih cara membaca URL, file, Public TI, dan tindakan aman.</div>
        </div>
        """
    )


def game_soal_sekarang_v12(offset=0):
    indeks = (int(st.session_state.get("game_v12_index", 0)) + offset) % len(GAME_URL_BANK)
    return GAME_URL_BANK[indeks]


def render_tebak_risiko_v12(engine):
    soal = game_soal_sekarang_v12()
    html(
        f"""
        <div class="game-shell">
            <div class="card-title">Tebak risiko URL</div>
            <div class="game-question">{aman_teks(soal["url"])}</div>
            <div class="game-chip-row">
                <span class="game-chip">Level: {aman_teks(soal["level"])}</span>
                <span class="game-chip">Pilih hasil akhir</span>
                <span class="game-chip">Best Engine bisa dicek setelah menjawab</span>
            </div>
        </div>
        """
    )
    pilihan = st.radio(
        "Menurut kamu hasil URL ini apa?",
        ["Terlihat Aman", "Perlu Tinjauan", "Berisiko"],
        horizontal=True,
        key=f"v12_tebak_{st.session_state.game_v12_index}_{st.session_state.game_v12_total}",
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Cek jawaban", key="v12_cek_tebak"):
            benar = pilihan == soal["jawaban"]
            game_add_score_v12(benar, badge="Risk Reader")
            if benar:
                callout("Benar", soal["alasan"], "safe")
            else:
                callout("Belum tepat", f"Jawaban yang lebih sesuai: {soal['jawaban']}. {soal['alasan']}", "review")
    with col2:
        if st.button("Soal berikutnya", key="v12_next_tebak"):
            st.session_state.game_v12_index = (st.session_state.game_v12_index + 1) % len(GAME_URL_BANK)
            st.rerun()
    with col3:
        if st.button("Cek dengan Best Engine", key="v12_engine_tebak"):
            jalankan_uji_satu_url(engine, soal["url"], sumber="game_v12_tebak")

    bullet_panel("Sinyal utama soal ini", soal["sinyal"], "gold")


def render_cari_sinyal_v12(engine):
    soal = game_soal_sekarang_v12(offset=1)
    opsi = [
        "Domain resmi",
        "Subdomain kampus",
        "HTTPS",
        "Brand tidak resmi",
        "Domain mirip brand",
        "Bukan domain resmi",
        "login",
        "update",
        "verify",
        "account",
        "Punycode",
        "Pengganti angka",
        "Tanda hubung",
        "Tidak ada kata mendesak",
        "Huruf mengecoh",
        "Salah eja",
    ]

    html(
        f"""
        <div class="game-shell">
            <div class="card-title">Cari sinyal pada alamat</div>
            <div class="game-question">{aman_teks(soal["url"])}</div>
            <div class="small">Pilih sinyal yang menurut kamu terlihat pada URL.</div>
        </div>
        """
    )

    pilihan = st.multiselect("Sinyal yang terlihat", opsi, key=f"v12_sinyal_{st.session_state.game_v12_index}")
    if st.button("Cek sinyal", key="v12_cek_sinyal"):
        target = set([item.lower() for item in soal["sinyal"]])
        pilih = set([item.lower() for item in pilihan])
        cocok = len(target.intersection(pilih))
        total = len(target)
        benar = cocok == total
        game_add_score_v12(benar, badge="Signal Hunter")
        if benar:
            callout("Sinyal lengkap", "Kamu berhasil membaca sinyal utama.", "safe")
        elif cocok > 0:
            callout("Sebagian benar", f"Kamu menemukan {cocok} dari {total} sinyal. Sinyal utama: {', '.join(soal['sinyal'])}.", "review")
        else:
            callout("Perlu latihan", f"Sinyal utama: {', '.join(soal['sinyal'])}.", "danger")

    with st.expander("Cek sinyal dari Best Engine"):
        if st.button("Jalankan Best Engine untuk URL ini", key="v12_engine_sinyal"):
            jalankan_uji_satu_url(engine, soal["url"], sumber="game_v12_sinyal")


def render_aksi_aman_v12():
    indeks = int(st.session_state.get("game_v12_action_index", 0)) % len(GAME_ACTION_CASES)
    soal = GAME_ACTION_CASES[indeks]
    html(
        f"""
        <div class="game-shell">
            <div class="card-title">Simulasi tindakan aman</div>
            <div class="game-question">{aman_teks(soal["skenario"])}</div>
        </div>
        """
    )
    opsi = [
        "Langsung login agar cepat selesai",
        "Cek domain resmi, jangan isi data dulu",
        "Unduh dan jalankan file untuk memastikan",
        "Kirim OTP agar akun tidak diblokir",
        "Bandingkan dengan domain resmi dan simpan sebagai pembanding jika benar",
        "Analisis file dulu, jangan klik link langsung",
        "Anggap berisiko dan cek domain resmi",
    ]
    pilihan = st.radio("Pilih tindakan", opsi, key=f"v12_aksi_{indeks}_{st.session_state.game_v12_total}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cek tindakan", key="v12_cek_aksi"):
            benar = pilihan == soal["jawaban"]
            game_add_score_v12(benar, badge="Safe Responder")
            if benar:
                callout("Tindakan benar", soal["penjelasan"], "safe")
            else:
                callout("Tindakan berbahaya", f"Tindakan yang lebih aman: {soal['jawaban']}. {soal['penjelasan']}", "danger")
    with col2:
        if st.button("Skenario berikutnya", key="v12_next_aksi"):
            st.session_state.game_v12_action_index = (st.session_state.game_v12_action_index + 1) % len(GAME_ACTION_CASES)
            st.rerun()


def render_file_triage_v12():
    indeks = int(st.session_state.get("game_v12_file_index", 0)) % len(GAME_FILE_CASES)
    soal = GAME_FILE_CASES[indeks]
    html(
        f"""
        <div class="game-shell">
            <div class="card-title">File triage drill</div>
            <div class="game-question">{aman_teks(soal["nama"])}</div>
            <div class="small">Tentukan tindakan awal berdasarkan nama dan jenis file.</div>
        </div>
        """
    )
    pilihan = st.radio(
        "Kategori awal file",
        ["Terlihat Aman", "Perlu Tinjauan", "Berisiko"],
        horizontal=True,
        key=f"v12_file_{indeks}_{st.session_state.game_v12_total}",
    )
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cek file", key="v12_cek_file"):
            benar = pilihan == soal["jawaban"]
            game_add_score_v12(benar, badge="File Triage")
            if benar:
                callout("Tepat", soal["alasan"], "safe")
            else:
                callout("Belum tepat", f"Kategori yang lebih sesuai: {soal['jawaban']}. {soal['alasan']}", "review")
            bullet_panel("Sinyal file", soal["sinyal"], "gold")
    with col2:
        if st.button("File berikutnya", key="v12_next_file"):
            st.session_state.game_v12_file_index = (st.session_state.game_v12_file_index + 1) % len(GAME_FILE_CASES)
            st.rerun()


def render_public_ti_v12(engine):
    url = st.text_input(
        "URL untuk simulasi Public Threat Intelligence",
        value="https://www.google.com",
        key="v12_public_ti_url",
    )
    panel(
        "Aturan cepat",
        "Public TI adalah sinyal tambahan. Jika URL tidak ditemukan di PhishTank atau URLhaus, bukan berarti pasti aman. Engine lokal tetap dipakai sebagai dasar.",
        "gold",
    )
    if st.button("Cek Public TI + Best Engine", key="v12_cek_public_ti"):
        hasil = jalankan_uji_satu_url(engine, url, sumber="game_v12_public_ti")
        ringkas = pd.DataFrame(
            [
                {"Bagian": "Public TI", "Nilai": hasil.get("public_ti_status", "-")},
                {"Bagian": "PhishTank", "Nilai": hasil.get("phishtank_status", "-")},
                {"Bagian": "URLhaus", "Nilai": hasil.get("urlhaus_query_status", "-")},
                {"Bagian": "Hasil V4", "Nilai": hasil.get("hasil_akhir", "-")},
                {"Bagian": "Skor V4", "Nilai": hasil.get("skor_final", "-")},
            ]
        )
        tabel_rapi(ringkas, max_rows=20)


def render_speed_round_v12(engine):
    html(
        """
        <div class="game-shell">
            <div class="card-title">Speed round</div>
            <div class="small">Masukkan beberapa URL. Sistem akan memberi ringkasan latihan cepat dan hasil Best Engine.</div>
        </div>
        """
    )
    teks = st.text_area(
        "Daftar URL latihan",
        value="\n".join([item["url"] for item in GAME_URL_BANK[:6]]),
        height=180,
        key="v12_speed_text",
    )
    daftar = parse_url_bebas(teks, tambah_https=True, hapus_duplikat=True)
    metrik_kartu(
        [
            {"label": "URL terbaca", "nilai": len(daftar), "catatan": "Setelah parsing teks.", "warna": "gold"},
            {"label": "Mode", "nilai": "Batch", "catatan": "Cocok untuk latihan cepat.", "warna": "green"},
            {"label": "Output", "nilai": "CSV", "catatan": "Bisa diunduh.", "warna": "flat"},
        ],
        kolom=3,
    )
    if st.button("Jalankan speed round", key="v12_speed_run"):
        data = jalankan_uji_banyak_url(engine, daftar, pesan_kosong="Tidak ada URL untuk speed round.")
        if not data.empty:
            if "hasil_akhir" in data.columns:
                ringkas = data["hasil_akhir"].value_counts().reset_index()
                ringkas.columns = ["hasil", "jumlah"]
                tabel_rapi(ringkas, max_rows=20, caption="Ringkasan speed round.")


def render_report_builder_v12(engine):
    url = st.text_input("URL untuk laporan mini", value="http://bca-login-update.test", key="v12_report_url")
    if st.button("Buat laporan mini", key="v12_report_button"):
        hasil = selaraskan_hasil_url(engine.analisis_url(normalisasi_url_input(url)))
        teks = f"""LAPORAN MINI PHISHRISK

URL:
{hasil.get('url', '-')}

Hasil:
{hasil.get('hasil_akhir', '-')}

Kategori:
{hasil.get('kategori_risiko', '-')}

Skor:
{hasil.get('skor_final', '-')}

Sinyal:
{hasil.get('intelligence_status', '-')}

Public Threat Intelligence:
{hasil.get('public_ti_status', '-')}

Rekomendasi:
{hasil.get('rekomendasi', '-')}
"""
        html(f'<div class="copy-card"><code>{aman_teks(teks)}</code></div>')
        st.download_button(
            "Unduh laporan mini",
            data=teks.encode("utf-8"),
            file_name="laporan_mini_phishrisk.txt",
            mime="text/plain",
            key="v12_download_report_mini",
        )


def render_badges_v12():
    badge = st.session_state.get("game_v12_badges", [])
    if not badge:
        panel("Belum ada badge", "Jawab beberapa latihan untuk membuka badge.", "yellow")
        return
    bullet_panel("Badge terbuka", badge, "green")


def halaman_game_cyber(engine):
    game_init_v12()
    hero(
        "Game Center",
        "Cyber Security Training Lab",
        "Game ringan untuk melatih user membaca URL, mengenali sinyal phishing, memahami file berisiko, dan memakai Best Engine secara defensif.",
        ["Risk Guess", "Signal Hunt", "File Triage", "Public TI", "Report Builder"],
    )
    render_game_score_v12()

    html(
        """
        <div class="mission-grid">
            <div class="mission-card"><strong>Tebak Risiko</strong><p>Latihan membaca alamat dan menentukan hasil akhir.</p></div>
            <div class="mission-card"><strong>Cari Sinyal</strong><p>Fokus pada brand palsu, punycode, angka pengganti, dan kata mendesak.</p></div>
            <div class="mission-card"><strong>File Triage</strong><p>Latihan mengambil keputusan awal terhadap PDF, ZIP, APK, HTML, dan TXT.</p></div>
            <div class="mission-card"><strong>Public TI</strong><p>Belajar membaca PhishTank dan URLhaus sebagai sinyal tambahan.</p></div>
            <div class="mission-card"><strong>Speed Round</strong><p>Uji banyak URL dalam satu putaran memakai Best Engine.</p></div>
            <div class="mission-card"><strong>Report Builder</strong><p>Buat laporan mini untuk dokumentasi hasil pemeriksaan.</p></div>
        </div>
        """
    )

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(
        [
            "Tebak Risiko",
            "Cari Sinyal",
            "Aksi Aman",
            "File Triage",
            "Public TI",
            "Speed Round",
            "Laporan Mini",
            "Badge",
        ]
    )

    with tab1:
        render_tebak_risiko_v12(engine)
    with tab2:
        render_cari_sinyal_v12(engine)
    with tab3:
        render_aksi_aman_v12()
    with tab4:
        render_file_triage_v12()
    with tab5:
        render_public_ti_v12(engine)
    with tab6:
        render_speed_round_v12(engine)
    with tab7:
        render_report_builder_v12(engine)
    with tab8:
        render_badges_v12()
        if st.button("Reset semua game", key="v12_reset_all_game"):
            for key in ["game_v12_score", "game_v12_total", "game_v12_streak", "game_v12_index", "game_v12_file_index", "game_v12_action_index", "game_v12_badges"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()


def halaman_playbook_v12(engine):
    hero(
        "Playbook",
        "Panduan Keputusan Cepat",
        "Halaman ringkas untuk membantu user mengambil tindakan setelah melihat hasil Best Engine.",
        ["Rendah", "Perlu Tinjauan", "Berisiko", "Laporan"],
    )
    tab_aman, tab_tinjauan, tab_risiko, tab_template = st.tabs(["Terlihat Aman", "Perlu Tinjauan", "Berisiko", "Template Laporan"])

    with tab_aman:
        bullet_panel(
            "Jika hasil Terlihat Aman",
            [
                "Tetap cek domain utama sebelum login.",
                "Buka layanan penting dari bookmark atau aplikasi resmi.",
                "Jangan memasukkan data sensitif jika link datang dari pesan asing.",
                "Gunakan hasil ini sebagai bantuan awal, bukan izin mutlak.",
            ],
            "green",
        )
    with tab_tinjauan:
        bullet_panel(
            "Jika hasil Perlu Tinjauan",
            [
                "Bandingkan domain dengan website resmi.",
                "Cek apakah alamat memakai banyak subdomain, tanda hubung, atau kata login/update.",
                "Jika ini website kampus/perusahaan resmi, simpan sebagai pembanding resmi setelah diverifikasi.",
                "Jangan masukkan OTP, PIN, atau password sebelum yakin.",
            ],
            "yellow",
        )
    with tab_risiko:
        bullet_panel(
            "Jika hasil Berisiko",
            [
                "Jangan buka dari perangkat utama.",
                "Jangan login dan jangan isi data pribadi.",
                "Simpan bukti pesan, email, atau file yang membawa link.",
                "Laporkan ke admin, bank, kampus, atau pihak terkait.",
                "Gunakan halaman File jika link ditemukan di dokumen/lampiran.",
            ],
            "red",
        )
    with tab_template:
        teks = """Template laporan singkat:

Sumber link/file:
[isi sumber]

URL atau nama file:
[isi URL/nama file]

Hasil PhishRisk:
[Terlihat Aman / Perlu Tinjauan / Berisiko]

Skor:
[isi skor]

Sinyal utama:
[domain mirip brand / kata login / punycode / public TI / file berisiko]

Tindakan:
[tidak dibuka / dilaporkan / dicek ke kanal resmi]
"""
        html(f'<div class="copy-card"><code>{aman_teks(teks)}</code></div>')
        st.download_button(
            "Unduh template laporan",
            data=teks.encode("utf-8"),
            file_name="template_laporan_phishrisk.txt",
            mime="text/plain",
            key="v12_download_template_playbook",
        )


def halaman_lab_eksperimen_v12(engine):
    hero(
        "Lab Eksperimen",
        "Uji Banyak Pola Sekaligus",
        "Ruang eksperimen untuk membandingkan website resmi, domain tiruan, kata mendesak, dan hasil Public Threat Intelligence.",
        ["Preset", "Custom", "Ringkasan", "Export"],
    )

    preset = st.selectbox(
        "Pilih preset uji",
        [
            "Campuran resmi dan tiruan",
            "Website resmi",
            "Domain mirip brand",
            "Kata login dan update",
            "Custom kosong",
        ],
        key="v12_lab_preset",
    )

    preset_data = {
        "Campuran resmi dan tiruan": [
            "https://praktikum.gunadarma.ac.id",
            "https://www.bca.co.id",
            "http://bca-login-update.test",
            "http://rricrosoft.com",
            "https://www.google.com",
            "http://paypal-verify-account.test",
        ],
        "Website resmi": [
            "https://www.bca.co.id",
            "https://www.shopee.co.id",
            "https://www.google.com",
            "https://www.microsoft.com",
            "https://praktikum.gunadarma.ac.id",
        ],
        "Domain mirip brand": [
            "http://rricrosoft.com",
            "http://rnicrosoft.com",
            "https://xn--micrsoft-q4a.test",
            "http://c1mb.test",
        ],
        "Kata login dan update": [
            "http://bca-login-update.test",
            "http://micros0ft-login-update.test",
            "http://praktikum-gunadarma-login-update.test",
            "http://paypal-verify-account.test",
        ],
        "Custom kosong": [],
    }

    teks_default = "\n".join(preset_data.get(preset, []))
    teks = st.text_area("Daftar URL eksperimen", value=teks_default, height=210, key="v12_lab_textarea")
    daftar = parse_url_bebas(teks, tambah_https=True, hapus_duplikat=True)

    metrik_kartu(
        [
            {"label": "URL siap uji", "nilai": len(daftar), "catatan": "Hasil parsing dari teks.", "warna": "gold"},
            {"label": "Engine", "nilai": "V1", "catatan": "Memakai Public TI jika tersedia.", "warna": "green"},
            {"label": "Fungsi", "nilai": "Compare", "catatan": "Membandingkan beberapa pola.", "warna": "flat"},
        ],
        kolom=3,
    )

    if daftar:
        tabel_rapi(pd.DataFrame({"url": daftar}), max_rows=80, caption="Daftar URL yang akan diuji.")
    if st.button("Jalankan eksperimen", key="v12_lab_run"):
        data = jalankan_uji_banyak_url(engine, daftar, pesan_kosong="Belum ada URL eksperimen.")
        if not data.empty:
            kolom_ringkas = [kolom for kolom in ["hasil_akhir", "kategori_risiko", "public_ti_status"] if kolom in data.columns]
            for kolom in kolom_ringkas:
                ringkas = data[kolom].value_counts().reset_index()
                ringkas.columns = [kolom, "jumlah"]
                tabel_rapi(ringkas, max_rows=20, caption=f"Ringkasan berdasarkan {kolom}.")


def halaman_insight_v12(engine):
    hero(
        "Insight",
        "Ringkasan Hasil Terakhir",
        "Halaman ini membaca hasil pemeriksaan terakhir dan mengubahnya menjadi prioritas yang mudah dipahami.",
        ["Prioritas", "Ringkasan", "Aksi", "Riwayat"],
    )
    data = st.session_state.get("hasil_url_terakhir", pd.DataFrame())
    data_file = st.session_state.get("hasil_file_terakhir", pd.DataFrame())

    if data.empty and data_file.empty:
        panel("Belum ada hasil", "Periksa URL atau file terlebih dahulu agar halaman Insight bisa membuat ringkasan.", "yellow")
        return

    if not data.empty:
        section_title("Insight URL", "Ringkasan dari pemeriksaan URL terakhir.")
        tampilkan_ringkasan_url(data)
        if "hasil_akhir" in data.columns:
            risiko = data[data["hasil_akhir"].astype(str).str.contains("Berisiko", case=False, na=False)]
            tinjauan = data[data["hasil_akhir"].astype(str).str.contains("Tinjauan", case=False, na=False)]
            metrik_kartu(
                [
                    {"label": "Total URL", "nilai": len(data), "catatan": "Data terakhir.", "warna": "gold"},
                    {"label": "Berisiko", "nilai": len(risiko), "catatan": "Prioritas utama.", "warna": "red"},
                    {"label": "Perlu Tinjauan", "nilai": len(tinjauan), "catatan": "Perlu cek manual.", "warna": "yellow"},
                ],
                kolom=3,
            )
            if not risiko.empty:
                bullet_panel(
                    "Prioritas tindakan",
                    [
                        "Jangan membuka URL berisiko dari perangkat utama.",
                        "Cek domain resmi untuk URL yang membawa nama brand.",
                        "Laporkan URL yang berasal dari chat, email, atau file mencurigakan.",
                    ],
                    "red",
                )
                tampilkan_tabel_url(risiko)

    if not data_file.empty:
        section_title("Insight File", "Ringkasan dari pemeriksaan file terakhir.")
        tampilkan_ringkasan_file(data_file)
        tampilkan_tabel_file(data_file, st.session_state.get("hasil_url_dalam_file_terakhir", pd.DataFrame()))


def halaman_beranda(engine):
    hero(
        "PhishRisk System",
        "Pemeriksa URL dan File Berbasis Best Engine",
        "Website ini membantu user memeriksa link dan file secara defensif, membaca Public Threat Intelligence, membuat ringkasan, dan belajar melalui Quick PhishRisk Training.",
        ["Best Engine", "Public TI", "File Static", "Game Center", "Report"],
    )

    html(
        """
        <div class="game-hero-line">
            <div class="game-mini-card"><b>URL</b><span>Cek satu alamat, banyak alamat, atau CSV.</span></div>
            <div class="game-mini-card"><b>File</b><span>Analisis file tanpa menjalankan isi file.</span></div>
            <div class="game-mini-card"><b>Public TI</b><span>PhishTank dan URLhaus sebagai sinyal tambahan.</span></div>
            <div class="game-mini-card"><b>Game</b><span>Latihan membaca risiko untuk user umum.</span></div>
        </div>
        """
    )

    section_title("Mulai cepat", "Pilih salah satu aksi yang paling sering dipakai.")
    tab_url, tab_batch, tab_game = st.tabs(["Cek URL cepat", "Batch cepat", "Latihan game"])

    with tab_url:
        url = st.text_input("Masukkan URL", value="http://bca-login-update.test", key="v12_home_url")
        if st.button("Periksa sekarang", key="v12_home_check"):
            jalankan_uji_satu_url(engine, url, sumber="beranda_v12")
    with tab_batch:
        teks = st.text_area(
            "Paste beberapa URL",
            value="https://www.bca.co.id\nhttp://bca-login-update.test\nhttps://praktikum.gunadarma.ac.id\nhttp://rricrosoft.com",
            height=160,
            key="v12_home_batch",
        )
        daftar = parse_url_bebas(teks, tambah_https=True, hapus_duplikat=True)
        if st.button("Periksa batch", key="v12_home_batch_button"):
            jalankan_uji_banyak_url(engine, daftar)
    with tab_game:
        panel("Game Center", "Gunakan halaman Game untuk latihan tebak risiko, cari sinyal, file triage, Public TI, speed round, dan laporan mini.", "gold")
        if st.button("Buka lewat menu Game", key="v12_home_game_note"):
            st.session_state.halaman_aktif = "Game"
            st.rerun()


def halaman_rekomendasi():
    hero(
        "Rekomendasi",
        "Antisipasi dan Tindakan",
        "Ringkasan tindakan aman berdasarkan hasil Best Engine. Singkat, padat, dan bisa langsung dipakai user.",
        ["Aman", "Tinjauan", "Risiko", "File", "Akun"],
    )
    tab1, tab2, tab3, tab4 = st.tabs(["URL", "File", "Akun", "Organisasi"])
    with tab1:
        bullet_panel(
            "Saat menerima link",
            [
                "Cek domain utama sebelum login.",
                "Jangan percaya kata mendesak seperti update, verify, unlock, reward, atau suspended.",
                "Untuk bank dan e-commerce, buka dari aplikasi resmi atau bookmark.",
                "Jika domain memakai nama brand tetapi bukan domain resmi, jangan isi data.",
            ],
            "gold",
        )
    with tab2:
        bullet_panel(
            "Saat menerima file",
            [
                "Jangan jalankan APK, EXE, BAT, CMD, PS1, VBS, LNK dari sumber tidak jelas.",
                "Cek PDF, DOCX, HTML, ZIP, dan TXT jika berisi link.",
                "Gunakan halaman File untuk melihat URL yang tertanam di dalam file.",
                "Jika hasil berisiko, simpan bukti dan laporkan.",
            ],
            "yellow",
        )
    with tab3:
        bullet_panel(
            "Lindungi akun",
            [
                "Aktifkan verifikasi dua langkah.",
                "Gunakan password berbeda untuk akun penting.",
                "Jangan kirim OTP kepada siapa pun.",
                "Ganti password jika pernah login dari link mencurigakan.",
            ],
            "green",
        )
    with tab4:
        bullet_panel(
            "Untuk tim atau organisasi",
            [
                "Buat daftar domain resmi internal.",
                "Catat kasus salah deteksi dan perbaiki pembanding resmi.",
                "Gunakan laporan CSV untuk dokumentasi.",
                "Latih user memakai Game Center agar lebih peka terhadap pola phishing.",
            ],
            "flat",
        )


MENU_UTAMA = [
    "Beranda",
    "URL",
    "File",
    "Threat Intel",
    "Batch",
    "Lab",
    "Insight",
    "AI & Laporan",
    "Playbook",
    "Rekomendasi",
    "Ciri",
    "Panduan",
    "Game",
    "Beta",
    "Riwayat",
    "Tentang",
    "Sistem",
]

MENU_MAP = {
    "Beranda": "Beranda",
    "URL": "Input Alamat Link",
    "File": "Input File",
    "Threat Intel": "Public Threat Intelligence",
    "Batch": "Engine Lab",
    "Lab": "Lab Eksperimen",
    "Insight": "Insight",
    "AI & Laporan": "AI dan Laporan",
    "Playbook": "Playbook",
    "Rekomendasi": "Rekomendasi dan Antisipasi",
    "Ciri": "Ciri-Ciri",
    "Panduan": "Panduan",
    "Game": "Quick PhishRisk Training",
    "Beta": "Beta dan Salah Deteksi",
    "Riwayat": "Riwayat",
    "Tentang": "Tentang Project",
    "Sistem": "Informasi Sistem",
}


def buat_navigasi():
    if "halaman_aktif" not in st.session_state:
        st.session_state.halaman_aktif = "Beranda"

    default = st.session_state.halaman_aktif if st.session_state.halaman_aktif in MENU_UTAMA else "Beranda"

    html(
        """
        <div class="top-nav-card">
            <div class="top-nav-head">
                <div class="brand-block">
                    <div class="brand-mark">PR</div>
                    <div>
                        <div class="brand-title">PhishRisk</div>
                        <div class="brand-sub">Best Engine</div>
                    </div>
                </div>
                <div class="nav-badge">Best Engine</div>
            </div>
        """
    )

    pilihan = st.selectbox(
        "Pilih halaman",
        MENU_UTAMA,
        index=MENU_UTAMA.index(default),
        label_visibility="collapsed",
        key="navigasi_utama_dropdown_v12",
    )

    html(
        f"""
            <div class="nav-help">Halaman aktif: <b>{aman_teks(MENU_MAP.get(pilihan, pilihan))}</b> · URL, File, Threat Intel, Insight, Playbook, dan Game Center.</div>
        </div>
        """
    )

    st.session_state.halaman_aktif = pilihan
    return MENU_MAP.get(pilihan, "Beranda")


def buat_sidebar():
    return buat_navigasi()


def main():
    pasang_css()
    pasang_css_final_override()
    pasang_css_v8_polish()
    pasang_css_engine_v4()
    pasang_css_game_v12()
    siapkan_state()
    game_init_v12()

    try:
        engine = muat_engine()
    except Exception as error:
        hero(
            "Aplikasi gagal dimuat",
            "Best Engine Belum Siap",
            "Pastikan file phishrisk_engine_v4.py, public_threat_intelligence.py, model_terbaik_intelligence_v2.pkl, dan daftar_fitur_intelligence_v2.json tersedia.",
            ["Cek src", "Cek model", "Cek Best Engine"],
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
    elif halaman == "Public Threat Intelligence":
        halaman_threat_intel(engine)
    elif halaman == "Engine Lab":
        halaman_batch_lab(engine)
    elif halaman == "Lab Eksperimen":
        halaman_lab_eksperimen_v12(engine)
    elif halaman == "Insight":
        halaman_insight_v12(engine)
    elif halaman == "AI dan Laporan":
        halaman_ai_laporan(engine)
    elif halaman == "Playbook":
        halaman_playbook_v12(engine)
    elif halaman == "Rekomendasi dan Antisipasi":
        halaman_rekomendasi()
    elif halaman == "Ciri-Ciri":
        halaman_ciri()
    elif halaman == "Panduan":
        halaman_panduan()
    elif halaman == "Quick PhishRisk Training":
        halaman_game_cyber(engine)
    elif halaman == "Beta dan Salah Deteksi":
        halaman_beta()
    elif halaman == "Riwayat":
        halaman_riwayat()
    elif halaman == "Tentang Project":
        halaman_tentang()
    else:
        halaman_sistem()

    footer_site()



# ============================================================
# UPGRADE V13 - SYSTEM PAGE FIX + FEATURE EXPANSION
# Fokus:
# 1. Menghapus tampilan metadata mentah putih yang mengganggu.
# 2. Mengubah metadata menjadi ringkasan visual yang mudah dibaca.
# 3. Menambah Checklist, Domain Watch, dan Report Center.
# 4. Memperkaya Game Center agar selaras dengan Engine V4.
# ============================================================

def pasang_css_v13_polish():
    st.markdown(
        """
        <style>
        .meta-grid-v13{
            display:grid;
            grid-template-columns:repeat(4,minmax(0,1fr));
            gap:.75rem;
            margin:.75rem 0 1rem;
        }
        .meta-card-v13{
            border:1px solid rgba(255,255,255,.08);
            border-radius:22px;
            background:linear-gradient(145deg,rgba(216,181,109,.09),rgba(255,255,255,.014)),rgba(18,19,16,.86);
            box-shadow:0 16px 42px rgba(0,0,0,.26);
            padding:.95rem;
            min-height:124px;
        }
        .meta-card-v13 b{
            display:block;
            color:#fff9ec;
            font-size:1.02rem!important;
            line-height:1.2!important;
            letter-spacing:-.03em;
            margin-bottom:.28rem;
        }
        .meta-card-v13 span{
            display:block;
            color:#c8bda9;
            font-size:.82rem!important;
            line-height:1.45!important;
        }
        .meta-card-v13 small{
            display:inline-flex;
            margin-top:.5rem;
            border:1px solid rgba(216,181,109,.28);
            border-radius:999px;
            padding:.22rem .5rem;
            color:#ffe4aa!important;
            background:rgba(216,181,109,.08);
            font-size:.70rem!important;
            font-weight:850;
        }
        .compact-note-v13{
            border:1px solid rgba(255,255,255,.08);
            border-radius:20px;
            background:rgba(255,255,255,.024);
            padding:.86rem;
            color:#c8bda9!important;
            margin:.6rem 0;
        }
        .mini-dashboard-v13{
            display:grid;
            grid-template-columns:1.1fr .9fr;
            gap:.8rem;
            align-items:stretch;
        }
        .mission-grid-v13{
            display:grid;
            grid-template-columns:repeat(3,minmax(0,1fr));
            gap:.75rem;
            margin:.75rem 0 1rem;
        }
        .mission-card-v13{
            border:1px solid rgba(216,181,109,.28);
            border-radius:22px;
            background:linear-gradient(145deg,rgba(255,255,255,.038),rgba(255,255,255,.012)),#12130f;
            padding:.9rem;
            min-height:135px;
            box-shadow:0 14px 34px rgba(0,0,0,.22);
        }
        .mission-card-v13 b{
            color:#fff9ec;
            display:block;
            font-size:.98rem!important;
            line-height:1.2!important;
            margin-bottom:.32rem;
        }
        .mission-card-v13 span{
            color:#c8bda9;
            font-size:.82rem!important;
            line-height:1.45!important;
        }
        .code-free-box-v13{
            border:1px solid rgba(216,181,109,.24);
            border-radius:24px;
            background:radial-gradient(circle at 100% 0%,rgba(216,181,109,.12),transparent 26%),rgba(18,19,16,.86);
            padding:1rem;
            margin:.7rem 0;
            box-shadow:0 16px 44px rgba(0,0,0,.26);
        }
        .signal-token-v13{
            display:inline-flex;
            align-items:center;
            border:1px solid rgba(216,181,109,.34);
            border-radius:999px;
            background:rgba(216,181,109,.09);
            color:#ffe4aa!important;
            padding:.24rem .56rem;
            margin:.16rem;
            font-size:.75rem!important;
            font-weight:850;
        }
        .status-dot-v13{
            display:inline-flex;
            width:.58rem;
            height:.58rem;
            border-radius:999px;
            background:#d8b56d;
            margin-right:.35rem;
            box-shadow:0 0 0 4px rgba(216,181,109,.13);
        }
        .status-dot-v13.ok{background:#9bc79f;box-shadow:0 0 0 4px rgba(155,199,159,.13);}
        .status-dot-v13.warn{background:#d6bd76;box-shadow:0 0 0 4px rgba(214,189,118,.13);}
        .status-dot-v13.danger{background:#e18478;box-shadow:0 0 0 4px rgba(225,132,120,.13);}
        .system-clean-title-v13{
            color:#fff9ec!important;
            font-size:clamp(1.1rem,1.8vw,1.65rem)!important;
            font-weight:950!important;
            line-height:1.08!important;
            letter-spacing:-.045em!important;
            margin:.2rem 0 .55rem!important;
        }
        div[data-testid="stJson"]{
            background:#11120f!important;
            border:1px solid rgba(255,255,255,.08)!important;
            border-radius:18px!important;
            color:#eee4d1!important;
        }
        @media(max-width:1000px){
            .meta-grid-v13{grid-template-columns:repeat(2,minmax(0,1fr));}
            .mini-dashboard-v13{grid-template-columns:1fr;}
            .mission-grid-v13{grid-template-columns:repeat(2,minmax(0,1fr));}
        }
        @media(max-width:620px){
            .meta-grid-v13,.mission-grid-v13{grid-template-columns:1fr;}
            .meta-card-v13,.mission-card-v13{border-radius:18px;padding:.82rem;}
            .compact-note-v13,.code-free-box-v13{border-radius:18px;padding:.82rem;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def baca_json_aman(lokasi):
    try:
        lokasi = Path(lokasi)
        if lokasi.exists():
            return json.loads(lokasi.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def ambil_ukuran_kb_v13(lokasi):
    lokasi = Path(lokasi)
    if not lokasi.exists():
        return 0
    return round(lokasi.stat().st_size / 1024, 2)


def status_file_v13(lokasi, fungsi, prioritas="pendukung"):
    lokasi = Path(lokasi)
    return {
        "komponen": lokasi.name,
        "fungsi": fungsi,
        "status": "Tersedia" if lokasi.exists() else "Belum ada",
        "prioritas": prioritas,
        "ukuran_kb": ambil_ukuran_kb_v13(lokasi),
        "lokasi": str(lokasi),
    }


def metadata_ringkas_v13(metadata):
    if not metadata:
        return pd.DataFrame([{"informasi": "Status", "isi": "Metadata belum ditemukan."}])

    field = [
        ("nama_program", "Nama program"),
        ("versi_engine", "Versi engine"),
        ("step", "Tahap"),
        ("status", "Status"),
        ("waktu", "Waktu"),
        ("catatan_phishtank", "Catatan PhishTank"),
        ("catatan_urlhaus", "Catatan URLhaus"),
        ("catatan", "Catatan"),
    ]

    baris = []
    for key, label in field:
        if key in metadata:
            baris.append({"informasi": label, "isi": metadata.get(key, "-")})

    for key in ["komponen_baru", "api_digunakan", "fungsi_utama"]:
        value = metadata.get(key)
        if isinstance(value, list):
            baris.append({"informasi": key.replace("_", " ").title(), "isi": ", ".join(map(str, value))})

    for key in ["output_public_ti", "output_engine_v4", "laporan", "file_cli", "file_engine", "model_digunakan"]:
        if key in metadata:
            baris.append({"informasi": key.replace("_", " ").title(), "isi": metadata.get(key, "-")})

    if not baris:
        baris.append({"informasi": "Status", "isi": "Metadata ada, tetapi formatnya tidak dikenali."})

    return pd.DataFrame(baris)


def metadata_cards_v13(metadata_v4, metadata_step10):
    nama_v4 = metadata_v4.get("nama_program", "PhishRisk Public Threat Intelligence")
    status_v4 = metadata_v4.get("status", "Siap digunakan")
    step_v4 = metadata_v4.get("step", "Best Engine")
    catatan_phishtank = metadata_v4.get("catatan_phishtank", "PhishTank dipakai sebagai sinyal tambahan.")
    catatan_urlhaus = metadata_v4.get("catatan_urlhaus", "URLhaus aktif penuh jika Auth-Key tersedia.")
    status_cli = metadata_step10.get("status", "CLI utility tersedia jika best engine sudah dijalankan")

    html(
        f"""
        <div class="meta-grid-v13">
            <div class="meta-card-v13">
                <b>{aman_teks(nama_v4)}</b>
                <span>{aman_teks(status_v4)}</span>
                <small>{aman_teks(step_v4)}</small>
            </div>
            <div class="meta-card-v13">
                <b>PhishTank</b>
                <span>{aman_teks(catatan_phishtank)}</span>
                <small>Public TI</small>
            </div>
            <div class="meta-card-v13">
                <b>URLhaus</b>
                <span>{aman_teks(catatan_urlhaus)}</span>
                <small>Auth-Key opsional</small>
            </div>
            <div class="meta-card-v13">
                <b>CLI Utility</b>
                <span>{aman_teks(status_cli)}</span>
                <small>Best Engine</small>
            </div>
        </div>
        """
    )


def tampilkan_validasi_visual_v13(df):
    if df.empty:
        panel("Validasi belum tersedia", "File validasi belum ditemukan. Website tetap bisa berjalan jika file inti tersedia.", "yellow")
        return

    tersedia = int((df["status"] == "Tersedia").sum()) if "status" in df.columns else 0
    total = len(df)
    wajib = df[df.get("prioritas", "") == "wajib"] if "prioritas" in df.columns else pd.DataFrame()
    wajib_ok = int((wajib["status"] == "Tersedia").sum()) if not wajib.empty and "status" in wajib.columns else 0

    metrik_kartu(
        [
            {"label": "Komponen", "nilai": f"{tersedia}/{total}", "catatan": "Jumlah file yang berhasil ditemukan.", "warna": "gold"},
            {"label": "File wajib", "nilai": f"{wajib_ok}/{len(wajib)}", "catatan": "Komponen utama aplikasi.", "warna": "green" if wajib_ok == len(wajib) else "yellow"},
            {"label": "Engine aktif", "nilai": "V4", "catatan": "Engine terbaru untuk URL, file, dan Public TI.", "warna": "gold"},
            {"label": "Output", "nilai": "CSV", "catatan": "Hasil bisa diunduh user.", "warna": "normal"},
        ],
        kolom=4,
    )

    tabel_rapi(df[["komponen", "fungsi", "status", "prioritas", "ukuran_kb"]], max_rows=100)


def halaman_sistem():
    hero(
        "Informasi Sistem",
        "Kesiapan Sistem",
        "Ringkasan visual komponen PhishRisk. Bagian metadata mentah sudah diganti menjadi informasi singkat agar tidak terlihat seperti isi lemari server yang tumpah.",
        ["Best Engine", "Public TI", "CLI", "Deploy Ready"],
    )

    metadata_v4 = baca_json_aman(LOKASI_METADATA_ENGINE_V4) if "LOKASI_METADATA_ENGINE_V4" in globals() else {}
    metadata_step10 = baca_json_aman(LOKASI_METADATA_STEP10)

    lokasi_validasi_step13 = globals().get("LOKASI_VALIDASI_STEP13", DIREKTORI_OUTPUT / "validasi_step13_public_threat_intelligence.csv")

    komponen = [
        status_file_v13(DIREKTORI_SRC / "phishrisk_engine_v4.py", "Engine terbaru untuk menggabungkan model, intelligence lokal, dan Public TI.", "wajib"),
        status_file_v13(DIREKTORI_SRC / "public_threat_intelligence.py", "Koneksi PhishTank dan URLhaus sebagai sinyal tambahan.", "wajib"),
        status_file_v13(DIREKTORI_SRC / "run_phishrisk_v4.py", "CLI untuk menjalankan pemeriksaan Best Engine dari terminal.", "wajib"),
        status_file_v13(DIREKTORI_SRC / "phishrisk_engine_v3.py", "Fallback engine jika V4 belum tersedia.", "wajib"),
        status_file_v13(DIREKTORI_PROJECT / "models" / "model_terbaik_intelligence_v2.pkl", "Model utama hasil retraining intelligence.", "wajib"),
        status_file_v13(DIREKTORI_OUTPUT / "daftar_fitur_intelligence_v2.json", "Daftar fitur yang dipakai model.", "wajib"),
        status_file_v13(lokasi_validasi_step13, "Validasi final Best Engine.", "pendukung"),
        status_file_v13(LOKASI_METADATA_ENGINE_V4 if "LOKASI_METADATA_ENGINE_V4" in globals() else DIREKTORI_OUTPUT / "metadata_step13_public_threat_intelligence.json", "Metadata Public Threat Intelligence.", "pendukung"),
        status_file_v13(DIREKTORI_PROJECT / ".env.example", "Contoh konfigurasi aman untuk deployment.", "pendukung"),
    ]
    df_komponen = pd.DataFrame(komponen)

    metadata_cards_v13(metadata_v4, metadata_step10)
    tampilkan_validasi_visual_v13(df_komponen)

    tab_ringkas, tab_v4, tab_cli, tab_deploy, tab_batasan = st.tabs(
        ["Ringkasan", "Metadata V1", "Metadata CLI", "Deploy", "Batasan"]
    )

    with tab_ringkas:
        html(
            """
            <div class="code-free-box-v13">
                <div class="system-clean-title-v13">Ringkasan tanpa metadata mentah</div>
                <div class="muted">
                    Halaman ini tidak lagi menampilkan JSON mentah besar. User cukup melihat status komponen,
                    fungsi file, API yang dipakai, dan catatan penting. Detail teknis tetap disimpan di file output.
                </div>
            </div>
            """
        )
        bullet_panel(
            "Komponen utama",
            [
                "Best Engine membaca hasil model lokal dan Public Threat Intelligence.",
                "PhishTank menjadi sinyal tambahan, bukan keputusan tunggal.",
                "URLhaus siap aktif jika Auth-Key tersedia.",
                "File .env tidak boleh ikut GitHub atau frontend.",
            ],
            "gold",
        )

    with tab_v4:
        section_title("Metadata V1", "Dibuat ringkas agar manusia normal tidak dipaksa membaca JSON mentah.")
        tabel_rapi(metadata_ringkas_v13(metadata_v4), max_rows=100)
        api = metadata_v4.get("api_digunakan", [])
        if api:
            html("".join([f'<span class="signal-token-v13">{aman_teks(item)}</span>' for item in api]))

    with tab_cli:
        section_title("Metadata Best Engine", "Ringkasan CLI utility untuk menjalankan engine dari terminal.")
        tabel_rapi(metadata_ringkas_v13(metadata_step10), max_rows=100)

    with tab_deploy:
        bullet_panel(
            "Checklist deployment",
            [
                "Pastikan .env tidak ikut GitHub.",
                "Pastikan requirements.txt berisi streamlit, pandas, numpy, scikit-learn, xgboost, joblib, python-docx, PyPDF2, openpyxl, requests, python-dotenv.",
                "Gunakan .env.example sebagai panduan konfigurasi.",
                "Untuk URLhaus, isi URLHAUS_AUTH_KEY jika nanti punya key.",
                "Jangan push data mentah besar, file model besar tanpa pertimbangan, atau API key.",
            ],
            "yellow",
        )
        data_deploy = pd.DataFrame([
            {"item": "Streamlit", "status": "Wajib", "catatan": "Untuk menjalankan dashboard."},
            {"item": "Best Engine", "status": "Wajib", "catatan": "Agar hasil website sesuai program terbaru."},
            {"item": "PhishTank", "status": "Opsional aktif", "catatan": "Bisa berjalan sebagai sinyal tambahan."},
            {"item": "URLhaus Auth-Key", "status": "Opsional", "catatan": "Dibutuhkan agar query URLhaus aktif penuh."},
            {"item": "AI API", "status": "Opsional", "catatan": "Fallback lokal tetap tersedia."},
        ])
        tabel_rapi(data_deploy, max_rows=80)

    with tab_batasan:
        bullet_panel(
            "Batasan sistem",
            [
                "Tidak menggantikan audit keamanan penuh.",
                "Tidak menjalankan file berbahaya.",
                "Tidak membuktikan kepemilikan domain.",
                "Public Threat Intelligence bisa tidak menemukan URL baru atau URL sintetis.",
                "Hasil aman tetap harus dibaca hati-hati jika link datang dari sumber tidak dikenal.",
            ],
            "red",
        )


def halaman_checklist_v13(engine):
    hero(
        "Checklist Aman",
        "Pandu User Mengambil Keputusan",
        "Halaman ini membantu user memilih tindakan setelah mendapat link atau file. Singkat, praktis, dan tidak berubah menjadi ceramah keamanan siber 12 jilid.",
        ["Checklist", "User Action", "Defensif", "Ringkas"],
    )

    skenario = st.selectbox(
        "Pilih skenario",
        [
            "Saya menerima link dari WhatsApp atau email",
            "Saya diminta login ulang",
            "Saya menerima file PDF/DOCX/ZIP/APK",
            "Saya melihat domain mirip brand",
            "Website resmi terbaca perlu tinjauan",
        ],
        key="v13_checklist_skenario",
    )

    data = {
        "Saya menerima link dari WhatsApp atau email": [
            "Jangan klik langsung jika pengirim tidak jelas.",
            "Cek domain utama, bukan hanya judul pesan.",
            "Jangan isi OTP, password, PIN, atau data kartu.",
            "Buka layanan dari aplikasi resmi atau bookmark.",
            "Gunakan halaman URL untuk memeriksa link.",
        ],
        "Saya diminta login ulang": [
            "Pastikan domain benar-benar resmi.",
            "Curigai kata login, verify, update, secure, unlock, atau suspended.",
            "Jangan login dari link pesan mendadak.",
            "Jika ragu, tutup halaman dan ketik alamat resmi manual.",
            "Ganti password jika sudah terlanjur login.",
        ],
        "Saya menerima file PDF/DOCX/ZIP/APK": [
            "Jangan jalankan file dari sumber tidak dikenal.",
            "Upload ke halaman File untuk membaca metadata dan URL tertanam.",
            "Hindari APK, EXE, BAT, CMD, PS1, VBS, dan LNK dari pesan acak.",
            "Jika file berisi link login, cek link itu lagi di halaman URL.",
            "Simpan bukti jika file dikirim dalam konteks penipuan.",
        ],
        "Saya melihat domain mirip brand": [
            "Bandingkan huruf satu per satu.",
            "Cek angka yang mengganti huruf, seperti 0 untuk o atau 1 untuk i.",
            "Waspadai tanda hubung berlebihan.",
            "Cari domain resmi dari aplikasi atau website utama.",
            "Jangan transaksi sebelum yakin.",
        ],
        "Website resmi terbaca perlu tinjauan": [
            "Baca hasil sebagai peringatan, bukan vonis.",
            "Cocokkan domain dengan daftar resmi.",
            "Jika domain resmi tetapi bentuknya panjang, hasil bisa masuk tinjauan.",
            "Gunakan feedback agar daftar pembanding bisa diperbaiki.",
            "Jangan menghapus kewaspadaan hanya karena domain terlihat familiar.",
        ],
    }

    bullet_panel("Langkah yang disarankan", data.get(skenario, []), "gold")

    section_title("Generator ringkasan tindakan", "Bisa dipakai untuk laporan singkat.")
    hasil = "\n".join([f"- {item}" for item in data.get(skenario, [])])
    st.text_area("Ringkasan", value=hasil, height=180, key="v13_checklist_output")
    st.download_button(
        "Unduh checklist",
        data=f"Checklist PhishRisk\nSkenario: {skenario}\n\n{hasil}\n".encode("utf-8"),
        file_name="checklist_phishrisk.txt",
        mime="text/plain",
        key=widget_key("download_checklist_v13"),
    )


def halaman_domain_watch_v13(engine):
    hero(
        "Domain Watch",
        "Pantau Daftar Link",
        "Masukkan beberapa domain atau URL untuk melihat prioritas risiko. Cocok untuk daftar link dari chat, email, catatan, atau laporan user.",
        ["URL Watch", "Batch", "Prioritas", "Best Engine"],
    )

    contoh = "\n".join([
        "https://www.bca.co.id",
        "http://bca-login-update.test",
        "https://praktikum.gunadarma.ac.id",
        "http://rricrosoft.com",
        "https://www.google.com",
    ])

    teks = st.text_area("Daftar URL atau domain", value=contoh, height=210, key="v13_domain_watch_input")
    daftar = parse_url_bebas(teks, tambah_https=True, hapus_duplikat=True)

    metrik_kartu(
        [
            {"label": "Terdeteksi", "nilai": len(daftar), "catatan": "Jumlah alamat yang siap dicek.", "warna": "gold"},
            {"label": "Mode", "nilai": "Batch", "catatan": "Memakai engine aktif website.", "warna": "normal"},
            {"label": "Output", "nilai": "CSV", "catatan": "Hasil bisa diunduh.", "warna": "green"},
        ],
        kolom=3,
    )

    tabel_rapi(pd.DataFrame({"url": daftar}), max_rows=100)

    if st.button("Jalankan Domain Watch", key="v13_domain_watch_run"):
        if not daftar:
            st.warning("Belum ada alamat yang valid.")
        else:
            hasil = engine.analisis_banyak_url(daftar)
            hasil = selaraskan_dataframe_url(pd.DataFrame(hasil))
            st.session_state.hasil_url_terakhir = hasil
            tampilkan_ringkasan_url(hasil)
            tampilkan_tabel_url(hasil)


def halaman_report_center_v13(engine):
    hero(
        "Report Center",
        "Ringkasan Siap Pakai",
        "Buat ringkasan pemeriksaan dari hasil terakhir. Tidak perlu menampilkan JSON mentah yang membuat halaman seperti terminal tersesat.",
        ["Report", "CSV", "Ringkas", "Defensif"],
    )

    data_url = st.session_state.get("hasil_url_terakhir", pd.DataFrame())
    data_file = st.session_state.get("hasil_file_terakhir", pd.DataFrame())

    if data_url.empty and data_file.empty:
        panel("Belum ada hasil", "Periksa URL atau file terlebih dahulu agar laporan bisa dibuat.", "yellow")
        return

    jumlah_url = len(data_url) if isinstance(data_url, pd.DataFrame) else 0
    jumlah_file = len(data_file) if isinstance(data_file, pd.DataFrame) else 0

    ringkasan_url = {}
    if isinstance(data_url, pd.DataFrame) and not data_url.empty and "hasil_akhir" in data_url.columns:
        ringkasan_url = data_url["hasil_akhir"].value_counts().to_dict()

    ringkasan_file = {}
    if isinstance(data_file, pd.DataFrame) and not data_file.empty:
        kolom_hasil = "hasil_akhir_file_v4" if "hasil_akhir_file_v4" in data_file.columns else "hasil_akhir_file_v3"
        if kolom_hasil in data_file.columns:
            ringkasan_file = data_file[kolom_hasil].value_counts().to_dict()

    isi_laporan = f"""# Laporan Singkat PhishRisk

Waktu laporan: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Ringkasan

- Jumlah URL diperiksa: {jumlah_url}
- Jumlah file diperiksa: {jumlah_file}

## Ringkasan URL

{ringkasan_url}

## Ringkasan File

{ringkasan_file}

## Rekomendasi Umum

- Prioritaskan item dengan kategori Tinggi atau Sangat Tinggi.
- Jangan login, transaksi, atau memasukkan OTP pada link berisiko.
- Untuk file berisiko, jangan dijalankan di perangkat utama.
- Gunakan domain resmi dari aplikasi, bookmark, atau kanal resmi.
- Simpan bukti jika link atau file berasal dari pesan mencurigakan.

## Catatan

Hasil ini adalah bantuan awal. Pemeriksaan penuh tetap membutuhkan validasi manual dan kebijakan keamanan organisasi.
"""

    st.text_area("Preview laporan", value=isi_laporan, height=360, key="v13_report_preview")
    st.download_button(
        "Unduh laporan Markdown",
        data=isi_laporan.encode("utf-8"),
        file_name="laporan_singkat_phishrisk.md",
        mime="text/markdown",
        key=widget_key("download_report_v13"),
    )


def halaman_game_cyber(engine):
    hero(
        "Quick PhishRisk Training",
        "Quick PhishRisk Training",
        "Latihan singkat untuk membaca risiko URL, file, Public TI, dan tindakan aman. Game ini selaras dengan Best Engine, bukan kuis pajangan yang cuma menambah scroll.",
        ["Tebak Risiko", "Signal Hunt", "Domain Surgery", "Incident Sprint", "Badge"],
    )

    game_init_v12()
    render_game_score_v12()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Tebak Risiko",
        "Cari Sinyal",
        "Domain Surgery",
        "Incident Sprint",
        "File Triage",
        "Badge",
    ])

    with tab1:
        render_tebak_risiko_v12(engine)

    with tab2:
        render_cari_sinyal_v12()

    with tab3:
        section_title("Domain Surgery", "Bedah domain yang terlihat mirip brand resmi.")
        kasus = st.selectbox(
            "Pilih kasus",
            [
                "rricrosoft.com",
                "rnicrosoft.com",
                "micros0ft-login-update.test",
                "bca-login-update.test",
                "praktikum-gunadarma-login-update.test",
            ],
            key="v13_domain_surgery_case",
        )
        jawaban = st.multiselect(
            "Sinyal yang terlihat",
            ["Salah eja", "Mirip brand", "Ada kata login/update", "Bukan domain resmi", "Tanda hubung", "Angka mengganti huruf"],
            key="v13_domain_surgery_answer",
        )
        aturan = {
            "rricrosoft.com": ["Salah eja", "Mirip brand", "Bukan domain resmi"],
            "rnicrosoft.com": ["Salah eja", "Mirip brand", "Bukan domain resmi"],
            "micros0ft-login-update.test": ["Mirip brand", "Ada kata login/update", "Bukan domain resmi", "Tanda hubung", "Angka mengganti huruf"],
            "bca-login-update.test": ["Mirip brand", "Ada kata login/update", "Bukan domain resmi", "Tanda hubung"],
            "praktikum-gunadarma-login-update.test": ["Mirip brand", "Ada kata login/update", "Bukan domain resmi", "Tanda hubung"],
        }
        benar = set(aturan.get(kasus, []))
        if st.button("Cek jawaban Domain Surgery", key="v13_domain_surgery_check"):
            skor = len(set(jawaban) & benar)
            if set(jawaban) == benar:
                game_add_score_v12(15)
                callout("Tepat", "Kamu membaca semua sinyal utama.", "safe")
            else:
                game_add_score_v12(max(3, skor * 3))
                callout("Masih bisa diperbaiki", f"Sinyal utama: {', '.join(benar)}", "review")
        html("<div class='game-url'>https://" + aman_teks(kasus) + "</div>")

    with tab4:
        section_title("Incident Sprint", "Pilih langkah saat user sudah terlanjur klik link.")
        kondisi = st.radio(
            "Kondisi",
            ["Belum login", "Sudah memasukkan password", "Sudah memasukkan OTP", "Mengunduh file APK"],
            key="v13_incident_condition",
        )
        aksi = st.multiselect(
            "Aksi yang kamu ambil",
            [
                "Tutup halaman",
                "Ganti password",
                "Cabut sesi login aktif",
                "Aktifkan 2FA",
                "Hubungi pihak resmi",
                "Jalankan APK untuk cek isi",
                "Simpan bukti",
            ],
            key="v13_incident_action",
        )
        jawaban_bahaya = "Jalankan APK untuk cek isi"
        if st.button("Nilai Incident Sprint", key="v13_incident_check"):
            if jawaban_bahaya in aksi:
                callout("Aksi berbahaya", "Jangan menjalankan APK atau file mencurigakan di perangkat utama.", "danger")
            elif len(aksi) >= 3:
                game_add_score_v12(12)
                callout("Respon bagus", "Aksi kamu sudah mengarah ke mitigasi yang aman.", "safe")
            else:
                game_add_score_v12(4)
                callout("Kurang lengkap", "Tambahkan ganti password, cabut sesi, 2FA, hubungi pihak resmi, dan simpan bukti bila perlu.", "review")

    with tab5:
        render_file_triage_v12()

    with tab6:
        render_badges_v12()
        html(
            """
            <div class="mission-grid-v13">
                <div class="mission-card-v13"><b>Target pemula</b><span>Capai 40 poin dari Tebak Risiko dan Cari Sinyal.</span></div>
                <div class="mission-card-v13"><b>Target analis</b><span>Capai 90 poin dan selesaikan Incident Sprint tanpa memilih aksi berbahaya.</span></div>
                <div class="mission-card-v13"><b>Target defensif</b><span>Gunakan hasil game untuk menjelaskan phishing ke user non-teknis.</span></div>
            </div>
            """
        )


def halaman_beranda(engine):
    hero(
        "PhishRisk System",
        "Pemeriksa URL dan File Berbasis Best Engine",
        "Website ini membantu user memeriksa link, membaca file secara statis, melihat Public Threat Intelligence, membuat laporan, dan belajar lewat game interaktif.",
        ["Best Engine", "Public TI", "File Static", "Game Center", "Report"],
    )

    html(
        """
        <div class="mission-grid-v13">
            <div class="mission-card-v13"><b>Cek URL</b><span>Input satu link atau banyak link dari chat, email, browser, dan dokumen.</span></div>
            <div class="mission-card-v13"><b>Cek File</b><span>Baca metadata, hash, ekstensi, dan URL tertanam tanpa menjalankan file.</span></div>
            <div class="mission-card-v13"><b>Threat Intel</b><span>Gunakan PhishTank dan URLhaus sebagai sinyal tambahan, bukan vonis tunggal.</span></div>
            <div class="mission-card-v13"><b>Checklist</b><span>Bantu user menentukan tindakan setelah menerima link atau file.</span></div>
            <div class="mission-card-v13"><b>Watch</b><span>Pantau banyak domain sekaligus untuk melihat prioritas risiko.</span></div>
            <div class="mission-card-v13"><b>Game</b><span>Latihan membaca domain tiruan, sinyal phishing, dan tindakan aman.</span></div>
        </div>
        """
    )

    tab_url, tab_batch, tab_watch = st.tabs(["Cek cepat", "Batch cepat", "Domain Watch"])

    with tab_url:
        url = st.text_input("Masukkan URL", value="http://bca-login-update.test", key="v13_home_url")
        if st.button("Periksa sekarang", key="v13_home_check"):
            jalankan_uji_satu_url(engine, url, sumber="beranda_v13")

    with tab_batch:
        teks = st.text_area(
            "Paste beberapa URL",
            value="https://www.bca.co.id\nhttp://bca-login-update.test\nhttps://praktikum.gunadarma.ac.id\nhttp://rricrosoft.com",
            height=160,
            key="v13_home_batch",
        )
        daftar = parse_url_bebas(teks, tambah_https=True, hapus_duplikat=True)
        if st.button("Periksa batch", key="v13_home_batch_button"):
            jalankan_uji_banyak_url(engine, daftar)

    with tab_watch:
        panel("Domain Watch", "Gunakan halaman Watch untuk memantau banyak URL dengan tampilan prioritas risiko.", "gold")
        if st.button("Buka Watch", key="v13_go_watch"):
            st.session_state.halaman_aktif = "Watch"
            st.rerun()


MENU_UTAMA = [
    "Beranda",
    "URL",
    "File",
    "Threat Intel",
    "Batch",
    "Watch",
    "Lab",
    "Insight",
    "Report",
    "Checklist",
    "AI & Laporan",
    "Playbook",
    "Rekomendasi",
    "Ciri",
    "Panduan",
    "Game",
    "Beta",
    "Riwayat",
    "Tentang",
    "Sistem",
]

MENU_MAP = {
    "Beranda": "Beranda",
    "URL": "Input Alamat Link",
    "File": "Input File",
    "Threat Intel": "Public Threat Intelligence",
    "Batch": "Engine Lab",
    "Watch": "Domain Watch",
    "Lab": "Lab Eksperimen",
    "Insight": "Insight",
    "Report": "Report Center",
    "Checklist": "Checklist Aman",
    "AI & Laporan": "AI dan Laporan",
    "Playbook": "Playbook",
    "Rekomendasi": "Rekomendasi dan Antisipasi",
    "Ciri": "Ciri-Ciri",
    "Panduan": "Panduan",
    "Game": "Quick PhishRisk Training",
    "Beta": "Beta dan Salah Deteksi",
    "Riwayat": "Riwayat",
    "Tentang": "Tentang Project",
    "Sistem": "Informasi Sistem",
}


def buat_navigasi():
    if "halaman_aktif" not in st.session_state:
        st.session_state.halaman_aktif = "Beranda"

    default = st.session_state.halaman_aktif if st.session_state.halaman_aktif in MENU_UTAMA else "Beranda"

    html(
        """
        <div class="top-nav-card">
            <div class="top-nav-head">
                <div class="brand-block">
                    <div class="brand-mark">PR</div>
                    <div>
                        <div class="brand-title">PhishRisk</div>
                        <div class="brand-sub">Best Engine</div>
                    </div>
                </div>
                <div class="nav-badge">Best Engine</div>
            </div>
        """
    )

    pilihan = st.selectbox(
        "Pilih halaman",
        MENU_UTAMA,
        index=MENU_UTAMA.index(default),
        label_visibility="collapsed",
        key="navigasi_utama_dropdown_v13",
    )

    html(
        f"""
            <div class="nav-help">Halaman aktif: <b>{aman_teks(MENU_MAP.get(pilihan, pilihan))}</b> · URL, File, Threat Intel, Watch, Report, Checklist, dan Game Center.</div>
        </div>
        """
    )

    st.session_state.halaman_aktif = pilihan
    return MENU_MAP.get(pilihan, "Beranda")


def buat_sidebar():
    return buat_navigasi()


def main():
    pasang_css()
    pasang_css_final_override()
    pasang_css_v8_polish()
    pasang_css_engine_v4()
    pasang_css_game_v12()
    pasang_css_v13_polish()
    siapkan_state()
    game_init_v12()

    try:
        engine = muat_engine()
    except Exception as error:
        hero(
            "Aplikasi gagal dimuat",
            "Engine Belum Siap",
            "Pastikan file Best Engine, Public Threat Intelligence, model, dan daftar fitur tersedia.",
            ["Cek src", "Cek model", "Cek output", "Cek validasi", "Cek metadata"],
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
    elif halaman == "Public Threat Intelligence":
        halaman_threat_intel(engine)
    elif halaman == "Engine Lab":
        halaman_batch_lab(engine)
    elif halaman == "Domain Watch":
        halaman_domain_watch_v13(engine)
    elif halaman == "Lab Eksperimen":
        halaman_lab_eksperimen_v12(engine)
    elif halaman == "Insight":
        halaman_insight_v12(engine)
    elif halaman == "Report Center":
        halaman_report_center_v13(engine)
    elif halaman == "Checklist Aman":
        halaman_checklist_v13(engine)
    elif halaman == "AI dan Laporan":
        halaman_ai_laporan(engine)
    elif halaman == "Playbook":
        halaman_playbook_v12(engine)
    elif halaman == "Rekomendasi dan Antisipasi":
        halaman_rekomendasi()
    elif halaman == "Ciri-Ciri":
        halaman_ciri()
    elif halaman == "Panduan":
        halaman_panduan()
    elif halaman == "Quick PhishRisk Training":
        halaman_game_cyber(engine)
    elif halaman == "Beta dan Salah Deteksi":
        halaman_beta()
    elif halaman == "Riwayat":
        halaman_riwayat()
    elif halaman == "Tentang Project":
        halaman_tentang()
    else:
        halaman_sistem()

    footer_site()


# ============================================================
# HOTFIX V14 - GAME ENGINE ARGUMENT FIX + TRAINING LAB EXPANSION
# Fokus:
# 1. Memperbaiki error render_cari_sinyal_v12() missing engine.
# 2. Memperkaya halaman game tanpa menghapus fitur lama.
# 3. Menambah container latihan yang selaras dengan Engine V4 dan Public Threat Intelligence.
# 4. Menambah CSS responsif agar game lebih aman di mobile/tablet/laptop.
# ============================================================

def pasang_css_v14_game_fix():
    st.markdown(
        """
        <style>
        .v14-grid{
            display:grid;
            grid-template-columns:repeat(4,minmax(0,1fr));
            gap:.72rem;
            margin:.75rem 0 1rem 0;
        }
        .v14-card{
            border:1px solid rgba(255,255,255,.08);
            border-radius:22px;
            background:linear-gradient(145deg,rgba(255,255,255,.045),rgba(255,255,255,.012)),rgba(18,19,16,.82);
            padding:.92rem;
            box-shadow:0 14px 38px rgba(0,0,0,.24);
            min-height:122px;
        }
        .v14-card strong{
            display:block;
            color:#fff9ec;
            font-size:.98rem!important;
            letter-spacing:-.02em;
            line-height:1.25!important;
            margin-bottom:.32rem;
        }
        .v14-card span{
            display:block;
            color:#c8bda9;
            font-size:.82rem!important;
            line-height:1.45!important;
        }
        .v14-game-panel{
            border:1px solid rgba(216,181,109,.34);
            border-radius:28px;
            background:
                radial-gradient(circle at 100% 0%,rgba(216,181,109,.13),transparent 28%),
                linear-gradient(145deg,rgba(216,181,109,.10),rgba(255,255,255,.014)),
                rgba(18,19,16,.88);
            padding:1rem;
            box-shadow:0 18px 55px rgba(0,0,0,.30);
            margin:.75rem 0 .95rem 0;
        }
        .v14-question{
            font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace!important;
            color:#ffe7ad!important;
            background:rgba(0,0,0,.27);
            border:1px solid rgba(216,181,109,.24);
            border-radius:18px;
            padding:.88rem;
            overflow-wrap:anywhere;
            font-size:.95rem!important;
            line-height:1.55!important;
            margin:.55rem 0;
        }
        .v14-chip-row{
            display:flex;
            gap:.42rem;
            flex-wrap:wrap;
            margin:.55rem 0;
        }
        .v14-chip{
            border:1px solid rgba(255,255,255,.08);
            border-radius:999px;
            background:rgba(255,255,255,.035);
            color:#c8bda9;
            padding:.30rem .62rem;
            font-size:.77rem!important;
            line-height:1.2!important;
            font-weight:780!important;
        }
        .v14-answer-box{
            border:1px solid rgba(255,255,255,.08);
            border-radius:20px;
            background:rgba(255,255,255,.026);
            padding:.85rem;
            margin:.55rem 0;
        }
        .v14-mini-board{
            display:grid;
            grid-template-columns:repeat(3,minmax(0,1fr));
            gap:.65rem;
            margin:.7rem 0 .9rem 0;
        }
        .v14-mini{
            border:1px solid rgba(255,255,255,.075);
            border-radius:18px;
            padding:.78rem;
            background:rgba(255,255,255,.025);
        }
        .v14-mini b{
            color:#fff9ec;
            font-size:.90rem!important;
        }
        .v14-mini p{
            color:#c8bda9;
            font-size:.80rem!important;
            line-height:1.42!important;
            margin:.22rem 0 0 0!important;
        }
        .v14-divider{
            height:1px;
            background:linear-gradient(90deg,transparent,rgba(216,181,109,.36),transparent);
            margin:.9rem 0;
        }
        .v14-safe{border-color:rgba(155,199,159,.38)!important;background:linear-gradient(145deg,rgba(155,199,159,.12),rgba(255,255,255,.015)),rgba(18,19,16,.88)!important;}
        .v14-warn{border-color:rgba(214,189,118,.42)!important;background:linear-gradient(145deg,rgba(214,189,118,.13),rgba(255,255,255,.015)),rgba(18,19,16,.88)!important;}
        .v14-danger{border-color:rgba(225,132,120,.42)!important;background:linear-gradient(145deg,rgba(225,132,120,.14),rgba(255,255,255,.015)),rgba(18,19,16,.88)!important;}

        /* Radio dan multiselect pada game dibuat lebih rapi */
        div[role="radiogroup"]{
            gap:.46rem!important;
        }
        div[role="radio"]{
            min-height:42px!important;
            align-items:center!important;
        }
        .stMultiSelect div[data-baseweb="select"] > div{
            background:#12130f!important;
            border:1px solid rgba(216,181,109,.34)!important;
            border-radius:16px!important;
            min-height:46px!important;
            color:#fff9ec!important;
        }

        @media(max-width:1100px){
            .v14-grid{grid-template-columns:repeat(2,minmax(0,1fr));}
            .v14-mini-board{grid-template-columns:repeat(2,minmax(0,1fr));}
        }
        @media(max-width:760px){
            .v14-grid{grid-template-columns:1fr;}
            .v14-mini-board{grid-template-columns:1fr;}
            .v14-game-panel{border-radius:20px;padding:.85rem;}
            .v14-question{font-size:.84rem!important;border-radius:16px;padding:.75rem;}
            .v14-card{min-height:auto;border-radius:18px;}
            div[role="radiogroup"]{
                display:grid!important;
                grid-template-columns:1fr!important;
                gap:.38rem!important;
            }
            div[role="radio"]{
                width:100%!important;
                justify-content:flex-start!important;
                border-radius:14px!important;
            }
            div[role="radio"] *{
                text-align:left!important;
                font-size:.82rem!important;
            }
            .stTabs [data-baseweb="tab-list"]{
                display:flex!important;
                overflow-x:auto!important;
                flex-wrap:nowrap!important;
                gap:.35rem!important;
                padding-bottom:.25rem!important;
            }
            .stTabs [data-baseweb="tab"]{
                flex:0 0 auto!important;
                white-space:nowrap!important;
                min-height:38px!important;
            }
        }
        @media(max-width:430px){
            .v14-chip{font-size:.70rem!important;padding:.25rem .5rem;}
            .v14-card strong{font-size:.92rem!important;}
            .v14-card span{font-size:.78rem!important;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _v14_engine_result(engine, url):
    """Menjalankan Best Engine tanpa membuat game ikut jatuh kalau ada input kosong."""
    url_bersih = normalisasi_url_input(url)
    if not url_bersih:
        return None
    hasil = engine.analisis_url(url_bersih)
    return selaraskan_hasil_url(hasil)


def _v14_add_score(benar, badge=None):
    """Wrapper skor agar game tidak gagal jika state belum lengkap."""
    game_init_v12()
    game_add_score_v12(bool(benar), badge=badge)


def _v14_hasil_ringkas_box(hasil):
    if not hasil:
        panel("Belum ada hasil", "Jalankan Best Engine terlebih dahulu.", "yellow")
        return

    status = hasil.get("hasil_akhir", "-")
    kelas = "v14-safe" if "Aman" in str(status) else "v14-warn" if "Tinjauan" in str(status) else "v14-danger"

    html(
        f"""
        <div class="v14-game-panel {kelas}">
            <div class="card-title">Ringkasan Best Engine</div>
            <div class="v14-mini-board">
                <div class="v14-mini"><b>Hasil</b><p>{aman_teks(hasil.get("hasil_akhir", "-"))}</p></div>
                <div class="v14-mini"><b>Kategori</b><p>{aman_teks(hasil.get("kategori_risiko", "-"))}</p></div>
                <div class="v14-mini"><b>Skor</b><p>{aman_teks(hasil.get("skor_final", "-"))}</p></div>
                <div class="v14-mini"><b>Public TI</b><p>{aman_teks(hasil.get("public_ti_status", "-"))}</p></div>
                <div class="v14-mini"><b>Brand</b><p>{aman_teks(hasil.get("brand_detected", "-") or "-")}</p></div>
                <div class="v14-mini"><b>Sinyal</b><p>{aman_teks(hasil.get("intelligence_status", "-"))}</p></div>
            </div>
            <div class="muted">{aman_teks(hasil.get("rekomendasi", "-"))}</div>
        </div>
        """
    )


def render_dashboard_game_v14(engine):
    section_title("Pusat latihan", "Pilih latihan sesuai kebutuhan: membaca URL, mencari sinyal, memahami file, atau membuat laporan singkat.")
    html(
        """
        <div class="v14-grid">
            <div class="v14-card"><strong>Tebak Risiko</strong><span>Latihan membaca hasil akhir: aman, perlu tinjauan, atau berisiko.</span></div>
            <div class="v14-card"><strong>Signal Hunt</strong><span>Cari tanda seperti brand palsu, punycode, login, update, dan angka pengganti huruf.</span></div>
            <div class="v14-card"><strong>Domain Surgery</strong><span>Bedah domain mirip brand agar user tidak tertipu huruf yang terlihat mirip.</span></div>
            <div class="v14-card"><strong>Incident Sprint</strong><span>Latihan tindakan cepat saat user sudah klik link atau menerima file mencurigakan.</span></div>
            <div class="v14-card"><strong>File Triage</strong><span>Belajar membaca risiko awal PDF, ZIP, HTML, APK, TXT, DOCX, dan file lain.</span></div>
            <div class="v14-card"><strong>Public TI</strong><span>Memahami PhishTank dan URLhaus sebagai sinyal tambahan, bukan vonis tunggal.</span></div>
            <div class="v14-card"><strong>Mini Report</strong><span>Membuat laporan singkat dari hasil Engine V4 agar bisa disalin untuk dokumentasi.</span></div>
            <div class="v14-card"><strong>Badge</strong><span>Melihat capaian latihan dan reset game jika ingin mulai dari awal.</span></div>
        </div>
        """
    )

    with st.container(border=True):
        st.subheader("Uji cepat dari game")
        col1, col2 = st.columns([1.35, .65])
        with col1:
            url = st.text_input(
                "Masukkan URL bebas",
                value="http://bca-login-update.test",
                key="v14_game_quick_url",
                help="Input bebas untuk menguji Best Engine langsung dari halaman game.",
            )
        with col2:
            st.write("")
            st.write("")
            cek = st.button("Cek Best Engine", key="v14_game_quick_button")

        if cek:
            hasil = _v14_engine_result(engine, url)
            _v14_hasil_ringkas_box(hasil)
            if hasil:
                tambah_riwayat_url(hasil)


def render_cari_sinyal_v12(engine=None):
    """Hotfix: engine dibuat opsional agar pemanggilan lama tidak error."""
    soal = game_soal_sekarang_v12(offset=1)
    opsi = [
        "Domain resmi",
        "Subdomain kampus",
        "HTTPS",
        "Brand tidak resmi",
        "Domain mirip brand",
        "Bukan domain resmi",
        "login",
        "update",
        "verify",
        "account",
        "Punycode",
        "Pengganti angka",
        "Tanda hubung",
        "Tidak ada kata mendesak",
        "Huruf mengecoh",
        "Salah eja",
        "IP address",
        "Kata reward",
        "Kata claim",
        "File download",
        "URL pendek",
    ]

    html(
        f"""
        <div class="v14-game-panel">
            <div class="card-title">Cari sinyal pada alamat</div>
            <div class="v14-question">{aman_teks(soal["url"])}</div>
            <div class="v14-chip-row">
                <span class="v14-chip">Pilih lebih dari satu</span>
                <span class="v14-chip">Fokus domain utama</span>
                <span class="v14-chip">Cek kata mendesak</span>
            </div>
        </div>
        """
    )

    pilihan = st.multiselect(
        "Sinyal yang terlihat",
        opsi,
        key=f"v14_sinyal_{st.session_state.game_v12_index}_{st.session_state.game_v12_total}",
        help="Pilih sinyal yang benar-benar terlihat pada URL.",
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Cek sinyal", key="v14_cek_sinyal"):
            target = set([item.lower() for item in soal["sinyal"]])
            pilih = set([item.lower() for item in pilihan])
            cocok = len(target.intersection(pilih))
            total = len(target)
            benar = cocok == total

            _v14_add_score(benar, badge="Signal Hunter")

            if benar:
                callout("Sinyal lengkap", "Kamu berhasil membaca sinyal utama pada URL ini.", "safe")
            elif cocok > 0:
                callout("Sebagian benar", f"Kamu menemukan {cocok} dari {total} sinyal. Sinyal utama: {', '.join(soal['sinyal'])}.", "review")
            else:
                callout("Perlu latihan", f"Sinyal utama: {', '.join(soal['sinyal'])}.", "danger")

    with col2:
        if st.button("Soal sinyal berikutnya", key="v14_next_sinyal"):
            st.session_state.game_v12_index = (st.session_state.game_v12_index + 1) % len(GAME_URL_BANK)
            st.rerun()

    with col3:
        if engine is not None and st.button("Cek dengan Best Engine", key="v14_engine_sinyal"):
            hasil = jalankan_uji_satu_url(engine, soal["url"], sumber="game_v14_sinyal")
            if hasil:
                tambah_riwayat_url(hasil)

    bullet_panel("Sinyal utama soal ini", soal["sinyal"], "gold")


def render_domain_surgery_v14(engine):
    kasus = [
        {
            "url": "http://rricrosoft.com",
            "jawaban": "Huruf awal diganti agar mirip Microsoft",
            "catatan": "rricrosoft terlihat seperti microsoft jika dibaca cepat.",
        },
        {
            "url": "http://rnicrosoft.com",
            "jawaban": "rn bisa terlihat seperti m",
            "catatan": "Kombinasi r dan n sering mengecoh mata user.",
        },
        {
            "url": "http://bca-login-update.test",
            "jawaban": "Brand dipakai di domain tidak resmi",
            "catatan": "Nama BCA muncul, tetapi domain utama bukan bca.co.id.",
        },
        {
            "url": "https://xn--micrsoft-q4a.test",
            "jawaban": "Punycode dapat menyamarkan karakter",
            "catatan": "Punycode perlu dibaca hati-hati karena bisa tampak seperti brand resmi.",
        },
    ]

    if "v14_domain_surgery_index" not in st.session_state:
        st.session_state.v14_domain_surgery_index = 0

    item = kasus[st.session_state.v14_domain_surgery_index % len(kasus)]

    html(
        f"""
        <div class="v14-game-panel">
            <div class="card-title">Domain Surgery</div>
            <div class="v14-question">{aman_teks(item["url"])}</div>
            <div class="small">Bedah masalah utama pada domain ini.</div>
        </div>
        """
    )

    opsi = [
        "Domain resmi dan aman",
        "Huruf awal diganti agar mirip Microsoft",
        "rn bisa terlihat seperti m",
        "Brand dipakai di domain tidak resmi",
        "Punycode dapat menyamarkan karakter",
        "Tidak ada masalah penting",
    ]

    pilihan = st.radio(
        "Masalah utama domain",
        opsi,
        horizontal=False,
        key=f"v14_domain_surgery_{st.session_state.v14_domain_surgery_index}_{st.session_state.game_v12_total}",
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Cek bedah domain", key="v14_domain_surgery_check"):
            benar = pilihan == item["jawaban"]
            _v14_add_score(benar, badge="Domain Surgeon")
            if benar:
                callout("Tepat", item["catatan"], "safe")
            else:
                callout("Belum tepat", f"Jawaban yang lebih cocok: {item['jawaban']}. {item['catatan']}", "review")
    with col2:
        if st.button("Domain berikutnya", key="v14_domain_surgery_next"):
            st.session_state.v14_domain_surgery_index = (st.session_state.v14_domain_surgery_index + 1) % len(kasus)
            st.rerun()
    with col3:
        if st.button("Cek Best Engine", key="v14_domain_surgery_engine"):
            hasil = jalankan_uji_satu_url(engine, item["url"], sumber="game_v14_domain_surgery")
            if hasil:
                tambah_riwayat_url(hasil)


def render_incident_sprint_v14():
    kasus = [
        {
            "skenario": "User sudah klik link login bank dari WhatsApp, tetapi belum mengisi data.",
            "jawaban": "Tutup halaman, buka aplikasi resmi, dan jangan isi data",
            "alasan": "Belum ada data masuk, jadi tindakan utama adalah menghentikan interaksi dan cek kanal resmi.",
        },
        {
            "skenario": "User sudah memasukkan password pada halaman yang ternyata tiruan.",
            "jawaban": "Ganti password dari website resmi dan aktifkan 2FA",
            "alasan": "Akun perlu diamankan dari kanal resmi, bukan dari link yang sama.",
        },
        {
            "skenario": "User menerima PDF berisi link OTP dan tombol login.",
            "jawaban": "Analisis file dan URL, jangan klik tombol di PDF",
            "alasan": "File bisa menjadi pintu menuju link berisiko.",
        },
        {
            "skenario": "Website resmi kampus terdeteksi Perlu Tinjauan.",
            "jawaban": "Bandingkan dengan domain resmi lalu masukkan ke pembanding jika benar",
            "alasan": "Salah deteksi harus dikoreksi secara defensif, bukan dipaksa aman tanpa bukti.",
        },
    ]

    if "v14_incident_index" not in st.session_state:
        st.session_state.v14_incident_index = 0

    item = kasus[st.session_state.v14_incident_index % len(kasus)]

    html(
        f"""
        <div class="v14-game-panel">
            <div class="card-title">Incident Sprint</div>
            <div class="v14-question">{aman_teks(item["skenario"])}</div>
            <div class="small">Pilih tindakan awal yang paling aman.</div>
        </div>
        """
    )

    opsi = [
        "Langsung login lagi agar masalah selesai",
        "Tutup halaman, buka aplikasi resmi, dan jangan isi data",
        "Ganti password dari website resmi dan aktifkan 2FA",
        "Analisis file dan URL, jangan klik tombol di PDF",
        "Bandingkan dengan domain resmi lalu masukkan ke pembanding jika benar",
        "Abaikan semua peringatan sistem",
    ]

    pilihan = st.radio(
        "Tindakan awal",
        opsi,
        horizontal=False,
        key=f"v14_incident_choice_{st.session_state.v14_incident_index}_{st.session_state.game_v12_total}",
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cek tindakan", key="v14_incident_check"):
            benar = pilihan == item["jawaban"]
            _v14_add_score(benar, badge="Incident Responder")
            if benar:
                callout("Tindakan aman", item["alasan"], "safe")
            else:
                callout("Kurang aman", f"Tindakan yang lebih aman: {item['jawaban']}. {item['alasan']}", "danger")
    with col2:
        if st.button("Skenario berikutnya", key="v14_incident_next"):
            st.session_state.v14_incident_index = (st.session_state.v14_incident_index + 1) % len(kasus)
            st.rerun()


def render_public_ti_drill_v14(engine):
    section_title("Public Threat Intelligence Drill", "Latihan membaca PhishTank dan URLhaus sebagai sinyal tambahan, bukan pengganti engine utama.")

    contoh = st.selectbox(
        "Pilih contoh uji",
        [
            "https://www.google.com",
            "https://www.bca.co.id",
            "http://bca-login-update.test",
            "http://rricrosoft.com",
            "http://155.94.163.206/ai/?authenticated=true&account=login",
        ],
        key="v14_public_ti_select",
    )

    custom = st.text_input(
        "Atau masukkan URL sendiri",
        value=contoh,
        key="v14_public_ti_custom",
    )

    panel(
        "Cara membaca",
        "Jika Public TI tidak menemukan URL, bukan berarti pasti aman. Jika ditemukan tetapi belum valid, anggap catatan ringan. Jika valid aktif, jadikan prioritas risiko tinggi.",
        "gold",
    )

    if st.button("Cek Public TI + Best Engine", key="v14_public_ti_check"):
        hasil = _v14_engine_result(engine, custom)
        _v14_hasil_ringkas_box(hasil)
        if hasil:
            data = pd.DataFrame(
                [
                    {"Bagian": "Public TI Status", "Nilai": hasil.get("public_ti_status", "-")},
                    {"Bagian": "Public TI Source", "Nilai": hasil.get("public_ti_sources", "-")},
                    {"Bagian": "PhishTank", "Nilai": hasil.get("phishtank_status", "-")},
                    {"Bagian": "URLhaus", "Nilai": hasil.get("urlhaus_query_status", "-")},
                    {"Bagian": "Reason", "Nilai": hasil.get("public_ti_reason", "-")},
                    {"Bagian": "Recommendation", "Nilai": hasil.get("public_ti_recommendation", "-")},
                ]
            )
            tabel_rapi(data, max_rows=20, caption="Detail Public Threat Intelligence.")
            tambah_riwayat_url(hasil)


def render_report_mini_v14(engine):
    section_title("Laporan mini", "Buat ringkasan singkat dari hasil Best Engine untuk disalin ke catatan, laporan, atau dokumentasi.")

    url = st.text_input("URL laporan", value="http://bca-login-update.test", key="v14_report_url")
    if st.button("Buat laporan mini", key="v14_report_button"):
        hasil = _v14_engine_result(engine, url)
        if not hasil:
            st.warning("URL belum valid.")
            return

        teks = f"""LAPORAN MINI PHISHRISK

Waktu:
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

URL:
{hasil.get('url', '-')}

Domain:
{hasil.get('domain', '-')}

Hasil:
{hasil.get('hasil_akhir', '-')}

Kategori:
{hasil.get('kategori_risiko', '-')}

Skor:
{hasil.get('skor_final', '-')}

Sinyal Engine:
{hasil.get('intelligence_status', '-')}

Public Threat Intelligence:
{hasil.get('public_ti_status', '-')}

Alasan:
{hasil.get('intelligence_reason', '-')}

Rekomendasi:
{hasil.get('rekomendasi', '-')}

Catatan:
Hasil ini adalah bantuan awal. Jangan gunakan sebagai satu-satunya keputusan keamanan.
"""

        html(f'<div class="v14-answer-box"><code>{aman_teks(teks)}</code></div>')
        st.download_button(
            "Unduh laporan mini",
            data=teks.encode("utf-8"),
            file_name="laporan_mini_phishrisk_v14.txt",
            mime="text/plain",
            key="v14_download_report_mini",
        )
        tambah_riwayat_url(hasil)


def halaman_game_cyber(engine):
    """Override final V14: memperbaiki pemanggilan Signal Hunt dan menambah mode latihan."""
    pasang_css_v14_game_fix()
    game_init_v12()

    hero(
        "Quick PhishRisk Training",
        "Cyber Security Training Lab",
        "Latihan interaktif untuk membaca URL, file, Public Threat Intelligence, dan tindakan aman. Semua mode tetap defensif dan selaras dengan Best Engine.",
        ["Best Engine", "Public TI", "Signal Hunt", "Incident Sprint", "Mini Report"],
    )

    render_game_score_v12()

    html(
        """
        <div class="v14-grid">
            <div class="v14-card"><strong>Core Training</strong><span>Tebak hasil URL dan cek dengan Best Engine.</span></div>
            <div class="v14-card"><strong>Signal Training</strong><span>Cari sinyal phishing seperti brand palsu, punycode, login, update, verify, dan account.</span></div>
            <div class="v14-card"><strong>Response Training</strong><span>Latihan tindakan aman saat user menerima link atau file mencurigakan.</span></div>
            <div class="v14-card"><strong>Report Training</strong><span>Buat laporan mini agar hasil bisa terdokumentasi rapi.</span></div>
        </div>
        """
    )

    tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "Pusat",
        "Tebak Risiko",
        "Cari Sinyal",
        "Domain Surgery",
        "Incident Sprint",
        "File Triage",
        "Public TI",
        "Laporan Mini",
        "Badge",
    ])

    with tab0:
        render_dashboard_game_v14(engine)

    with tab1:
        render_tebak_risiko_v12(engine)

    with tab2:
        render_cari_sinyal_v12(engine)

    with tab3:
        render_domain_surgery_v14(engine)

    with tab4:
        render_incident_sprint_v14()

    with tab5:
        render_file_triage_v12()

    with tab6:
        render_public_ti_drill_v14(engine)

    with tab7:
        render_report_mini_v14(engine)

    with tab8:
        render_badges_v12()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Reset skor game", key="v14_reset_game_score"):
                for key in [
                    "game_v12_score",
                    "game_v12_total",
                    "game_v12_streak",
                    "game_v12_index",
                    "game_v12_file_index",
                    "game_v12_action_index",
                    "game_v12_badges",
                    "v14_domain_surgery_index",
                    "v14_incident_index",
                ]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        with col2:
            bullet_panel(
                "Badge yang bisa dibuka",
                [
                    "Risk Reader",
                    "Signal Hunter",
                    "Domain Surgeon",
                    "Incident Responder",
                    "File Guardian",
                ],
                "gold",
            )


def main():
    """Main final V14: sama seperti versi sebelumnya, hanya menambahkan CSS game fix."""
    pasang_css()
    pasang_css_final_override()
    pasang_css_v8_polish()
    pasang_css_engine_v4()
    pasang_css_game_v12()
    pasang_css_v13_polish()
    pasang_css_v14_game_fix()
    siapkan_state()
    game_init_v12()

    try:
        engine = muat_engine()
    except Exception as error:
        hero(
            "Aplikasi gagal dimuat",
            "Engine Belum Siap",
            "Pastikan file Best Engine, Public Threat Intelligence, model, dan daftar fitur tersedia.",
            ["Cek src", "Cek model", "Cek output", "Cek validasi", "Cek metadata"],
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
    elif halaman == "Public Threat Intelligence":
        halaman_threat_intel(engine)
    elif halaman == "Engine Lab":
        halaman_batch_lab(engine)
    elif halaman == "Domain Watch":
        halaman_domain_watch_v13(engine)
    elif halaman == "Lab Eksperimen":
        halaman_lab_eksperimen_v12(engine)
    elif halaman == "Insight":
        halaman_insight_v12(engine)
    elif halaman == "Report Center":
        halaman_report_center_v13(engine)
    elif halaman == "Checklist Aman":
        halaman_checklist_v13(engine)
    elif halaman == "AI dan Laporan":
        halaman_ai_laporan(engine)
    elif halaman == "Playbook":
        halaman_playbook_v12(engine)
    elif halaman == "Rekomendasi dan Antisipasi":
        halaman_rekomendasi()
    elif halaman == "Ciri-Ciri":
        halaman_ciri()
    elif halaman == "Panduan":
        halaman_panduan()
    elif halaman == "Quick PhishRisk Training":
        halaman_game_cyber(engine)
    elif halaman == "Beta dan Salah Deteksi":
        halaman_beta()
    elif halaman == "Riwayat":
        halaman_riwayat()
    elif halaman == "Tentang Project":
        halaman_tentang()
    else:
        halaman_sistem()

    footer_site()

if __name__ == "__main__":
    main()
