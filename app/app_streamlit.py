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
        "Masukkan satu URL, banyak URL, atau CSV. Semua memakai Engine V3.",
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
        {"label": "Engine", "nilai": "V3", "catatan": "Model, intelligence, file analyzer."},
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
        ["Engine V3", "Model V2", "URL", "File"],
    )

    daftar_file = [
        {"komponen": "Engine utama", "fungsi": "Menggabungkan model dan aturan keamanan.", "lokasi": DIREKTORI_SRC / "phishrisk_engine_v3.py", "catatan": "Wajib ada."},
        {"komponen": "CLI utility", "fungsi": "Menjalankan cek URL dan file lewat terminal.", "lokasi": DIREKTORI_SRC / "run_phishrisk.py", "catatan": "Berguna untuk pengujian."},
        {"komponen": "URL Intelligence", "fungsi": "Membaca domain resmi, brand, dan domain tiruan.", "lokasi": DIREKTORI_SRC / "url_intelligence.py", "catatan": "Wajib ada."},
        {"komponen": "File Analyzer", "fungsi": "Membaca file secara statis tanpa menjalankan file.", "lokasi": DIREKTORI_SRC / "file_static_analyzer.py", "catatan": "Wajib ada."},
        {"komponen": "Model terbaik", "fungsi": "Model prediksi phishing berbasis URL dan sinyal tambahan.", "lokasi": DIREKTORI_PROJECT / "models" / "model_terbaik_intelligence_v2.pkl", "catatan": "File besar, jangan dihapus."},
        {"komponen": "Daftar fitur", "fungsi": "Daftar kolom yang harus cocok dengan model.", "lokasi": DIREKTORI_OUTPUT / "daftar_fitur_intelligence_v2.json", "catatan": "Harus sinkron."},
        {"komponen": "Catatan CLI", "fungsi": "Ringkasan hasil pembuatan CLI STEP 10.", "lokasi": LOKASI_METADATA_STEP10, "catatan": "Opsional untuk informasi."},
        {"komponen": "Catatan engine", "fungsi": "Ringkasan Engine V3 dan keluaran utamanya.", "lokasi": LOKASI_METADATA_ENGINE, "catatan": "Opsional untuk informasi."},
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
    "Batch": "Batch Lab",
    "Rekomendasi": "Rekomendasi dan Antisipasi",
    "Ciri": "Ciri-Ciri",
    "Panduan": "Panduan",
    "Game": "Game Cyber Security",
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
                <div class="nav-badge">Engine V3</div>
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
                    <div class="footer-note">PhishRisk Intelligence System. Dashboard defensif untuk memeriksa URL dan file secara statis sebelum user klik, login, unduh, atau membuka lampiran.</div>
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
    elif halaman == "Game Cyber Security":
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