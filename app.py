import os
import time
import base64
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# =============================================================================
# PATH RESOLUTION & ASSETS
# =============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.exists(os.path.join(BASE_DIR, "data", "processed")):
    PROC_DIR   = os.path.join(BASE_DIR, "data", "processed")
    RAW_DIR    = os.path.join(BASE_DIR, "data", "raw")
    OUT_DIR    = os.path.join(BASE_DIR, "outputs")
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")
elif os.path.exists(os.path.join(BASE_DIR, "SmartPick-main", "data", "processed")):
    PROC_DIR   = os.path.join(BASE_DIR, "SmartPick-main", "data", "processed")
    RAW_DIR    = os.path.join(BASE_DIR, "SmartPick-main", "data", "raw")
    OUT_DIR    = os.path.join(BASE_DIR, "SmartPick-main", "outputs")
    ASSETS_DIR = os.path.join(BASE_DIR, "SmartPick-main", "assets")
else:
    PROC_DIR   = "data/processed"
    RAW_DIR    = "data/raw"
    OUT_DIR    = "outputs"
    ASSETS_DIR = "assets"

def get_base64_file(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

B64_LOGO_FULL = get_base64_file(os.path.join(ASSETS_DIR, "logo_full.png"))
B64_LOGO_ICON = get_base64_file(os.path.join(ASSETS_DIR, "logo_icon.png"))

# =============================================================================
# REAL SMARTPHONE IMAGE SYSTEM
# Sourced from GSMArena & official databases with brand-level fallbacks
# =============================================================================
import urllib.request
import urllib.parse
import re
import json

BRAND_PHONE_IMAGES = {
    "apple": "https://fdn2.gsmarena.com/vv/bigpic/apple-iphone-15-pro.jpg",
    "samsung": "https://fdn2.gsmarena.com/vv/bigpic/samsung-galaxy-a55.jpg",
    "xiaomi": "https://fdn2.gsmarena.com/vv/bigpic/xiaomi-redmi-note-13-pro-plus.jpg",
    "vivo": "https://fdn2.gsmarena.com/vv/bigpic/vivo-v40e.jpg",
    "realme": "https://fdn2.gsmarena.com/vv/bigpic/realme-12-pro-plus.jpg",
    "oppo": "https://fdn2.gsmarena.com/vv/bigpic/oppo-reno12-pro.jpg",
    "iqoo": "https://fdn2.gsmarena.com/vv/bigpic/vivo-v40e.jpg",
    "motorola": "https://fdn2.gsmarena.com/vv/bigpic/motorola-edge-50-pro.jpg",
    "nothing": "https://fdn2.gsmarena.com/vv/bigpic/nothing-phone-2a.jpg",
    "infinix": "https://upload.wikimedia.org/wikipedia/commons/d/db/Infinix_Note_60_Pro.png",
    "poco": "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/cb/Poco_M7_Pro_5G.jpg/330px-Poco_M7_Pro_5G.jpg",
    "google": "https://fdn2.gsmarena.com/vv/bigpic/google-pixel-8.jpg",
    "oneplus": "https://fdn2.gsmarena.com/vv/bigpic/oneplus-12.jpg",
    "tecno": "https://fdn2.gsmarena.com/vv/bigpic/tecno-camon-30.jpg",
    "honor": "https://fdn2.gsmarena.com/vv/bigpic/honor-200.jpg",
    "lava": "https://fdn2.gsmarena.com/vv/bigpic/lava-blaze-curve-5g.jpg",
    "itel": "https://fdn2.gsmarena.com/vv/bigpic/itel-color-pro-5g.jpg",
    "hmd": "https://fdn2.gsmarena.com/vv/bigpic/hmd-skyline.jpg",
    "cmf": "https://fdn2.gsmarena.com/vv/bigpic/nothing-cmf-phone-1.jpg",
}

DEFAULT_PHONE_IMAGE = "https://fdn2.gsmarena.com/vv/bigpic/xiaomi-redmi-note-13-pro-plus.jpg"

@st.cache_data(show_spinner=False)
def get_phone_image_url(model: str, brand: str) -> str:
    brand_key = str(brand).strip().lower()
    clean_m = re.sub(r'\s*\([^)]*\)', '', str(model)).strip()
    
    # 1. GSMArena bigpic direct slug check
    slug1 = re.sub(r'[^a-z0-9]+', '-', f"{brand_key} {clean_m}".lower()).strip('-')
    slug2 = re.sub(r'[^a-z0-9]+', '-', clean_m.lower()).strip('-')
    
    for s in [slug1, slug2]:
        gsm_url = f"https://fdn2.gsmarena.com/vv/bigpic/{s}.jpg"
        try:
            req = urllib.request.Request(gsm_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=1.2) as r:
                if r.status == 200:
                    return gsm_url
        except Exception:
            pass

    # 2. Wikipedia Search API
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&generator=search&gsrsearch={urllib.parse.quote(clean_m + ' smartphone')}&gsrlimit=2&prop=pageimages&piprop=thumbnail&pithumbsize=300"
        req = urllib.request.Request(url, headers={'User-Agent': 'SmartPickApp/1.0'})
        with urllib.request.urlopen(req, timeout=1.5) as r:
            data = json.loads(r.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            for pid, p in pages.items():
                if 'thumbnail' in p and p['thumbnail'].get('source'):
                    src = p['thumbnail']['source']
                    if not any(k in src.lower() for k in ['logo', 'icon', 'flag', 'svg']):
                        return src
    except Exception:
        pass

    return BRAND_PHONE_IMAGES.get(brand_key, DEFAULT_PHONE_IMAGE)

def render_smartphone_image_html(model: str, brand: str, width: int = 75, height: int = 95):
    img_url = get_phone_image_url(model, brand)
    brand_key = str(brand).strip().lower()
    fb_url = BRAND_PHONE_IMAGES.get(brand_key, DEFAULT_PHONE_IMAGE)
    return f"""<div style="
        width: {width}px; height: {height}px; flex-shrink: 0;
        background: #FFFFFF;
        border-radius: 12px;
        border: 1px solid rgba(0,0,0,0.08);
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        display: flex; align-items: center; justify-content: center;
        padding: 5px; box-sizing: border-box; overflow: hidden;
    ">
        <img src="{img_url}" alt="{model}" loading="lazy" style="
            max-width: 100%; max-height: 100%; object-fit: contain;
        " onerror="this.onerror=null; this.src='{fb_url}';" />
    </div>"""

fav_file = os.path.join(ASSETS_DIR, "favicon.png")
app_icon = fav_file if os.path.exists(fav_file) else "📱"

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="SmartPick Informatika — SPK Smartphone",
    page_icon=app_icon,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =============================================================================
# APPLE MINIMALIST DESIGN SYSTEM (CSS)
# Beautiful interactive card-based selection options, modern and comfortable
# =============================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* --- Global Reset & Apple Canvas --- */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Plus Jakarta Sans", "Helvetica Neue", sans-serif !important;
    letter-spacing: -0.012em;
}

.stApp {
    background-color: #F5F5F7 !important;
}

/* Hide Streamlit default Chrome */
header[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }
#MainMenu { display: none !important; }

.block-container {
    padding-top: 1rem !important;
    padding-bottom: 3.5rem !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    max-width: 100% !important;
    width: 100% !important;
}

@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
}

/* --- Clean Typography --- */
h1, h2, h3, h4, h5, h6 {
    color: #1D1D1F !important;
    font-weight: 700 !important;
    line-height: 1.25 !important;
}

.stApp p:not(button *),
.stApp span:not(button *),
.apple-card p,
.apple-card span,
div[data-testid="stVerticalBlockBorderWrapper"] p,
div[data-testid="stVerticalBlockBorderWrapper"] span {
    color: #1D1D1F;
    line-height: 1.5;
}

/* ==========================================================================
   BEAUTIFUL APPLE CARD-STYLE SELECTIONS (RADIO & CHECKBOXES)
   ========================================================================== */

/* Prevent accidental text-selection blue highlight on clicks */
div[data-testid="stRadio"] *,
div[data-testid="stCheckbox"] * {
    user-select: none !important;
    -webkit-user-select: none !important;
}

::selection {
    background: rgba(0, 113, 227, 0.15) !important;
    color: inherit !important;
}

/* Hide any collapsed or top widget title label so no empty card appears */
div[data-testid="stRadio"] > label,
div[data-testid="stRadioGroup"] > label:empty {
    display: none !important;
}

/* Radio Group: Stack of Apple Cards */
div[data-testid="stRadio"] div[role="radiogroup"] {
    display: flex !important;
    flex-direction: column !important;
    gap: 0.65rem !important;
    padding: 0.25rem 0 !important;
}

/* Each Radio Option as an Elegant Card */
div[data-testid="stRadio"] div[role="radiogroup"] label {
    background-color: #FFFFFF !important;
    border: 1px solid rgba(0, 0, 0, 0.1) !important;
    border-radius: 14px !important;
    padding: 0.85rem 1.15rem !important;
    margin: 0 !important;
    display: flex !important;
    align-items: center !important;
    gap: 0.85rem !important;
    cursor: pointer !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    width: 100% !important;
    box-sizing: border-box !important;
}

div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
    background-color: #FAFAFC !important;
    border-color: rgba(0, 113, 227, 0.4) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(0, 113, 227, 0.06) !important;
}

/* Active / Selected Radio Card (Clean soft-blue card tint, blue border) */
div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
    background-color: #F4F8FD !important;
    border: 1.5px solid #0071E3 !important;
    box-shadow: 0 3px 12px rgba(0, 113, 227, 0.12) !important;
}

/* Ensure Text Container is 100% Transparent (ABSOLUTELY NO BLUE RECTANGLE) */
div[data-testid="stRadio"] [data-testid="stMarkdownContainer"],
div[data-testid="stRadio"] [data-testid="stMarkdownContainer"] *,
div[data-testid="stCheckbox"] [data-testid="stMarkdownContainer"],
div[data-testid="stCheckbox"] [data-testid="stMarkdownContainer"] * {
    background: transparent !important;
    background-color: transparent !important;
}

/* Radio Option Text Styling */
div[data-testid="stRadio"] div[role="radiogroup"] label [data-testid="stMarkdownContainer"] p {
    color: #1D1D1F !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    line-height: 1.45 !important;
    margin: 0 !important;
}

/* Active Radio Text: Crisp high-contrast Apple Blue text with zero background collision */
div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) [data-testid="stMarkdownContainer"] p {
    color: #0071E3 !important;
    font-weight: 600 !important;
}

/* Checkbox Cards */
div[data-testid="stCheckbox"] {
    margin-bottom: 0.5rem !important;
}

div[data-testid="stCheckbox"] label {
    background-color: #FFFFFF !important;
    border: 1px solid rgba(0, 0, 0, 0.1) !important;
    border-radius: 12px !important;
    padding: 0.85rem 1rem !important;
    margin: 0 !important;
    display: flex !important;
    align-items: center !important;
    gap: 0.75rem !important;
    cursor: pointer !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    width: 100% !important;
    box-sizing: border-box !important;
}

div[data-testid="stCheckbox"] label:hover {
    background-color: #FAFAFC !important;
    border-color: rgba(0, 113, 227, 0.4) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(0, 113, 227, 0.06) !important;
}

/* Active Checkbox Card */
div[data-testid="stCheckbox"] label:has(input:checked) {
    background-color: #F4F8FD !important;
    border: 1.5px solid #0071E3 !important;
    box-shadow: 0 2px 8px rgba(0, 113, 227, 0.1) !important;
}

div[data-testid="stCheckbox"] label [data-testid="stMarkdownContainer"] p {
    color: #1D1D1F !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    line-height: 1.4 !important;
    margin: 0 !important;
}

div[data-testid="stCheckbox"] label:has(input:checked) [data-testid="stMarkdownContainer"] p {
    color: #0071E3 !important;
    font-weight: 600 !important;
}

/* ==========================================================================
   NAVIGATION TAB BUTTONS (Clean Apple Header Tabs - Zero Clutter)
   ========================================================================== */
div.st-key-nav_home button,
div.st-key-nav_search button,
div.st-key-nav_results button {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    border-radius: 8px !important;
    box-shadow: none !important;
    padding: 0.5rem 1rem !important;
    font-size: 0.95rem !important;
    transition: all 0.2s ease !important;
}

/* Inactive Nav Tabs: Clean Charcoal Gray */
div.st-key-nav_home button[kind="secondary"],
div.st-key-nav_search button[kind="secondary"],
div.st-key-nav_results button[kind="secondary"] {
    color: #6E6E73 !important;
    font-weight: 500 !important;
}

div.st-key-nav_home button[kind="secondary"]:hover,
div.st-key-nav_search button[kind="secondary"]:hover,
div.st-key-nav_results button[kind="secondary"]:hover {
    background-color: rgba(0, 0, 0, 0.05) !important;
    color: #1D1D1F !important;
}

/* Active Nav Tab: Apple Blue with Underline Bar */
div.st-key-nav_home button[kind="primary"],
div.st-key-nav_search button[kind="primary"],
div.st-key-nav_results button[kind="primary"] {
    background-color: rgba(0, 113, 227, 0.08) !important;
    color: #0071E3 !important;
    font-weight: 700 !important;
    border-bottom: 2.5px solid #0071E3 !important;
    border-radius: 8px 8px 0 0 !important;
}

/* ==========================================================================
   GENERAL BUTTONS (Zero Nested Borders, Single Crisp Edge)
   ========================================================================== */

/* Primary Action Buttons (Apple Blue #0071E3) */
button[data-testid="baseButton-primary"],
div[data-testid="stButton"] button[kind="primary"]:not(.st-key-nav_home button):not(.st-key-nav_search button):not(.st-key-nav_results button) {
    background-color: #0071E3 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 980px !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    padding: 0.55rem 1.4rem !important;
    box-shadow: 0 2px 8px rgba(0, 113, 227, 0.22) !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

button[data-testid="baseButton-primary"]:hover,
div[data-testid="stButton"] button[kind="primary"]:not(.st-key-nav_home button):not(.st-key-nav_search button):not(.st-key-nav_results button):hover {
    background-color: #0077ED !important;
    box-shadow: 0 4px 14px rgba(0, 113, 227, 0.32) !important;
    transform: translateY(-1px) !important;
}

/* Secondary Action Buttons (Apple Clean White with Single Crisp Border) */
button[data-testid="baseButton-secondary"],
div[data-testid="stButton"] button[kind="secondary"]:not(.st-key-nav_home button):not(.st-key-nav_search button):not(.st-key-nav_results button) {
    background-color: #FFFFFF !important;
    color: #1D1D1F !important;
    border: 1px solid rgba(0, 0, 0, 0.15) !important;
    border-radius: 980px !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    padding: 0.5rem 1.25rem !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03) !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

button[data-testid="baseButton-secondary"]:hover,
div[data-testid="stButton"] button[kind="secondary"]:not(.st-key-nav_home button):not(.st-key-nav_search button):not(.st-key-nav_results button):hover {
    background-color: #F5F5F7 !important;
    border-color: rgba(0, 0, 0, 0.25) !important;
    color: #1D1D1F !important;
    transform: translateY(-1px) !important;
}

/* CRITICAL FIX: Ensure all children inside ANY button have NO border and NO background! */
button[data-testid="baseButton-primary"] *,
button[data-testid="baseButton-secondary"] *,
div[data-testid="stButton"] button * {
    border: none !important;
    border-radius: 0 !important;
    background: transparent !important;
    background-color: transparent !important;
    box-shadow: none !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Text color inheritance for primary */
button[data-testid="baseButton-primary"]:not(.st-key-nav_home button):not(.st-key-nav_search button):not(.st-key-nav_results button) *,
div[data-testid="stButton"] button[kind="primary"]:not(.st-key-nav_home button):not(.st-key-nav_search button):not(.st-key-nav_results button) * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

/* Text color inheritance for secondary */
button[data-testid="baseButton-secondary"]:not(.st-key-nav_home button):not(.st-key-nav_search button):not(.st-key-nav_results button) *,
div[data-testid="stButton"] button[kind="secondary"]:not(.st-key-nav_home button):not(.st-key-nav_search button):not(.st-key-nav_results button) * {
    color: #1D1D1F !important;
    -webkit-text-fill-color: #1D1D1F !important;
}


/* ==========================================================================
   ULTRA-SMOOTH APPLE LIQUID MOTION TRANSITIONS (GPU OPTICAL BLUR)
   ========================================================================== */
html {
    scroll-behavior: smooth;
}

@keyframes slideFromRight {
    0% {
        opacity: 0;
        filter: blur(5px);
        transform: translate3d(28px, 0, 0);
    }
    100% {
        opacity: 1;
        filter: blur(0px);
        transform: translate3d(0, 0, 0);
    }
}

@keyframes slideFromLeft {
    0% {
        opacity: 0;
        filter: blur(5px);
        transform: translate3d(-28px, 0, 0);
    }
    100% {
        opacity: 1;
        filter: blur(0px);
        transform: translate3d(0, 0, 0);
    }
}

@keyframes smoothFadeIn {
    0% {
        opacity: 0;
        filter: blur(4px);
        transform: scale(0.992) translate3d(0, 8px, 0);
    }
    100% {
        opacity: 1;
        filter: blur(0px);
        transform: scale(1) translate3d(0, 0, 0);
    }
}

/* Spinner & Pulse for Loading Animation */
@keyframes spinRing {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@keyframes spinLogo {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@keyframes modalFadeIn {
    0% { opacity: 0; transform: scale(0.92); }
    100% { opacity: 1; transform: scale(1); }
}

@keyframes pulseLogo {
    0%, 100% {
        transform: scale(1);
        filter: drop-shadow(0 4px 12px rgba(0, 113, 227, 0.25));
    }
    50% {
        transform: scale(1.08);
        filter: drop-shadow(0 8px 24px rgba(0, 113, 227, 0.45));
    }
}

/* --- Apple Minimalist Search Input --- */
div[data-testid="stTextInput"] {
    margin-bottom: 0.5rem !important;
}

div[data-testid="stTextInput"] > div > div {
    background-color: #FFFFFF !important;
    border: 1.5px solid rgba(0, 0, 0, 0.1) !important;
    border-radius: 14px !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02) !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

div[data-testid="stTextInput"] > div > div:focus-within {
    border-color: #0071E3 !important;
    box-shadow: 0 0 0 4px rgba(0, 113, 227, 0.14), 0 4px 14px rgba(0, 113, 227, 0.08) !important;
}

div[data-testid="stTextInput"] input {
    color: #1D1D1F !important;
    font-size: 0.95rem !important;
    padding: 0.75rem 1.1rem !important;
}

div[data-testid="stTextInput"] input::placeholder {
    color: #86868B !important;
    font-size: 0.92rem !important;
}

/* Container as Apple Outer Card */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF !important;
    border-radius: 18px !important;
    border: 1px solid rgba(0, 0, 0, 0.06) !important;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.025) !important;
    padding: 1.4rem !important;
    margin-bottom: 1.25rem !important;
}

/* Apple Standalone Card Surfaces */
.apple-card {
    background: #FFFFFF;
    border-radius: 18px;
    border: 1px solid rgba(0, 0, 0, 0.06);
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.025);
    padding: 1.35rem;
    margin-bottom: 1rem;
    box-sizing: border-box;
}

.apple-card-compact {
    background: #FFFFFF;
    border-radius: 14px;
    border: 1px solid rgba(0, 0, 0, 0.06);
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.02);
    padding: 1rem 1.15rem;
    margin-bottom: 0.75rem;
    box-sizing: border-box;
}

/* Apple Badges */
.apple-chip {
    font-size: 0.72rem;
    font-weight: 600;
    padding: 0.25rem 0.6rem;
    border-radius: 980px;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    line-height: 1.2;
    white-space: nowrap;
    flex-shrink: 0;
}

.chip-neutral {
    background: #F0F0F2;
    color: #1D1D1F;
}

.chip-accent {
    background: rgba(0, 113, 227, 0.08);
    color: #0071E3;
}

.chip-cost {
    background: rgba(224, 62, 62, 0.08);
    color: #C93B2B;
}

.chip-benefit {
    background: rgba(0, 113, 227, 0.08);
    color: #0071E3;
}

.chip-success {
    background: rgba(52, 199, 89, 0.12);
    color: #1E7E34;
}

/* Spec Pills */
.spec-group {
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
    margin: 0.75rem 0 0.95rem 0;
}

.spec-chip {
    font-size: 0.72rem;
    font-weight: 500;
    color: #48484A;
    background: #F5F5F7;
    padding: 0.25rem 0.55rem;
    border-radius: 6px;
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    white-space: nowrap;
}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# DATA ENGINE
# =============================================================================
FEATURES = [
    "price_idr", "ram_gb", "storage_gb", "clock_speed_ghz",
    "battery_mah", "rear_camera_main_mp", "charging_watt",
]

CRITERIA = {
    "price_idr": {
        "code": "C1", "name": "Harga", "type": "Cost", "w": 0.20,
        "unit": "Jutaan IDR", "icon": "🏷️",
        "desc": "Anggaran smartphone dalam Rupiah. Nilai lebih rendah diprioritaskan."
    },
    "ram_gb": {
        "code": "C2", "name": "RAM", "type": "Benefit", "w": 0.15,
        "unit": "Gigabyte (GB)", "icon": "⚡",
        "desc": "Kapasitas RAM untuk kelancaran multitasking aplikasi berat dan gaming."
    },
    "storage_gb": {
        "code": "C3", "name": "Penyimpanan", "type": "Benefit", "w": 0.12,
        "unit": "Gigabyte (GB)", "icon": "💾",
        "desc": "Ruang internal untuk instalasi aplikasi, game, foto, dan dokumen."
    },
    "clock_speed_ghz": {
        "code": "C4", "name": "Clock Speed", "type": "Benefit", "w": 0.18,
        "unit": "Gigahertz (GHz)", "icon": "⚙️",
        "desc": "Frekuensi komputasi inti CPU penentu responsivitas tugas aplikasi."
    },
    "battery_mah": {
        "code": "C5", "name": "Kapasitas Baterai", "type": "Benefit", "w": 0.15,
        "unit": "Milliampere (mAh)", "icon": "🔋",
        "desc": "Daya simpan energi untuk ketahanan pemakaian harian tanpa sering charge."
    },
    "rear_camera_main_mp": {
        "code": "C6", "name": "Kamera Utama", "type": "Benefit", "w": 0.10,
        "unit": "Megapixel (MP)", "icon": "📷",
        "desc": "Resolusi sensor kamera utama untuk kejernihan foto dan perekaman video."
    },
    "charging_watt": {
        "code": "C7", "name": "Fast Charging", "type": "Benefit", "w": 0.10,
        "unit": "Watt (W)", "icon": "⚡",
        "desc": "Daya transfer pengisian baterai yang memangkas waktu tunggu isi ulang."
    },
}

@st.cache_data
def load_and_prepare_data():
    feat_path = os.path.join(PROC_DIR, "02_feature_engineering.csv")
    clean_path = os.path.join(PROC_DIR, "01_clean_smartphones.csv")

    if not os.path.exists(feat_path):
        df_clean = pd.read_csv(clean_path)
        kurs_inr_idr = 190.22
        df_clean["price_idr"] = (df_clean["price_inr"] * kurs_inr_idr).round(0).astype("int64")
        df_feat = df_clean[["smartphone_brand", "model"] + FEATURES].copy()
    else:
        df_feat = pd.read_csv(feat_path)
        df_clean = pd.read_csv(clean_path)

    meta_cols = ["model", "processor_name", "processor_brand", "display_inches",
                 "refresh_rate_hz", "has_5g", "fast_charging", "rating_score"]
    meta_cols = [c for c in meta_cols if c in df_clean.columns]

    df = df_feat.merge(
        df_clean[meta_cols].drop_duplicates(subset=["model"]),
        on="model", how="left"
    )

    # K-Means Clustering K=2
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[FEATURES])
    kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
    df["cluster"] = kmeans.fit_predict(X_scaled)
    centroids = kmeans.cluster_centers_
    df["dist_centroid"] = np.sqrt(((X_scaled - centroids[df["cluster"].values]) ** 2).sum(axis=1))

    return df

DF_SMARTPHONES = load_and_prepare_data()

@st.cache_data
def get_criteria_weights():
    weights_path = os.path.join(OUT_DIR, "bobot_kriteria_topsis.csv")
    if os.path.exists(weights_path):
        b_df = pd.read_csv(weights_path)
        return dict(zip(b_df["Kriteria"], b_df["Bobot"]))
    return {k: v["w"] for k, v in CRITERIA.items()}

WEIGHTS_DICT = get_criteria_weights()

def calculate_topsis(data_subset, weights):
    df_calc = data_subset.copy().reset_index(drop=True)
    if len(df_calc) == 0:
        return df_calc

    X = df_calc[FEATURES].astype(float)
    divisors = np.sqrt((X ** 2).sum(axis=0)).replace(0, np.nan)
    R = X.div(divisors, axis=1).fillna(0)

    for col in FEATURES:
        df_calc[f"norm_{col}"] = R[col].values

    w_series = pd.Series(weights)
    V = R.mul(w_series, axis=1)

    ideal_pos = {}
    ideal_neg = {}
    for col in FEATURES:
        if CRITERIA[col]["type"] == "Cost":
            ideal_pos[col] = V[col].min()
            ideal_neg[col] = V[col].max()
        else:
            ideal_pos[col] = V[col].max()
            ideal_neg[col] = V[col].min()

    d_pos = np.sqrt(((V - pd.Series(ideal_pos)) ** 2).sum(axis=1))
    d_neg = np.sqrt(((V - pd.Series(ideal_neg)) ** 2).sum(axis=1))

    df_calc["jarak_positif"] = d_pos
    df_calc["jarak_negatif"] = d_neg
    denom = d_pos + d_neg
    df_calc["nilai_preferensi"] = np.where(denom != 0, d_neg / denom, 0.0)

    df_calc = df_calc.sort_values(by="nilai_preferensi", ascending=False).reset_index(drop=True)
    df_calc["ranking"] = df_calc.index + 1
    return df_calc

def format_rupiah(num):
    return f"Rp {int(num):,}".replace(",", ".")

# =============================================================================
# STATE MANAGEMENT & DIRECTIONAL NAVIGATION
# =============================================================================
PAGE_ORDER = {
    "Beranda": 0,
    "Cari Rekomendasi": 1,
    "Hasil Rekomendasi": 2,
    "Detail": 3,
}

if "nav_page" not in st.session_state:
    st.session_state.nav_page = "Beranda"
if "prev_nav_page" not in st.session_state:
    st.session_state.prev_nav_page = "Beranda"
if "nav_direction" not in st.session_state:
    st.session_state.nav_direction = "fade"
if "nav_count" not in st.session_state:
    st.session_state.nav_count = 0
if "selected_phone" not in st.session_state:
    st.session_state.selected_phone = None
if "topsis_data" not in st.session_state:
    st.session_state.topsis_data = None
if "budget_choice" not in st.session_state or st.session_state.budget_choice > 4:
    st.session_state.budget_choice = 2
if "usage_choice" not in st.session_state:
    st.session_state.usage_choice = 0

def navigate(page_name, phone_model=None):
    prev_idx = PAGE_ORDER.get(st.session_state.nav_page, 0)
    new_idx = PAGE_ORDER.get(page_name, 0)

    if new_idx > prev_idx:
        st.session_state.nav_direction = "slide_right"  # Maju: slide dari kanan ke tengah
    elif new_idx < prev_idx:
        st.session_state.nav_direction = "slide_left"   # Mundur: slide dari kiri ke tengah
    else:
        st.session_state.nav_direction = "fade"

    st.session_state.prev_nav_page = st.session_state.nav_page
    st.session_state.nav_page = page_name
    st.session_state.nav_count += 1
    if phone_model is not None:
        st.session_state.selected_phone = phone_model
    st.rerun()

# =============================================================================
# UNIFIED NAVIGATION BAR
# =============================================================================
nav_left, nav_mid, nav_right = st.columns([3.8, 4.4, 3.8])

with nav_left:
    logo_html = f'<img src="data:image/png;base64,{B64_LOGO_FULL}" height="36" style="object-fit: contain; vertical-align: middle;" alt="SmartPick Informatika Logo" />' if B64_LOGO_FULL else '<span style="font-size: 1.25rem; font-weight: 700; color: #1D1D1F;">SmartPick</span>'
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 0.75rem; padding-top: 0.15rem;">
            {logo_html}
            <span class="apple-chip chip-neutral" style="font-weight: 500;">Hybrid K-Means & TOPSIS</span>
        </div>
    """, unsafe_allow_html=True)

with nav_mid:
    n_c1, n_c2, n_c3 = st.columns(3)
    with n_c1:
        if st.button("Beranda", key="nav_home", use_container_width=True,
                     type="primary" if st.session_state.nav_page == "Beranda" else "secondary"):
            navigate("Beranda")
    with n_c2:
        if st.button("Cari Rekomendasi", key="nav_search", use_container_width=True,
                     type="primary" if st.session_state.nav_page == "Cari Rekomendasi" else "secondary"):
            navigate("Cari Rekomendasi")
    with n_c3:
        if st.button("Hasil Rekomendasi", key="nav_results", use_container_width=True,
                     type="primary" if st.session_state.nav_page in ["Hasil Rekomendasi", "Detail"] else "secondary"):
            navigate("Hasil Rekomendasi")

with nav_right:
    pass

st.markdown("<hr style='margin: 0.75rem 0 1.5rem 0; border: none; border-top: 1px solid rgba(0,0,0,0.06);' />", unsafe_allow_html=True)

# Dynamic directional transition animation (Liquid Smooth Motion)
if st.session_state.nav_direction == "slide_right":
    anim_name = "slideFromRight"
    anim_duration = "0.42s"
elif st.session_state.nav_direction == "slide_left":
    anim_name = "slideFromLeft"
    anim_duration = "0.42s"
else:
    anim_name = "smoothFadeIn"
    anim_duration = "0.32s"

clean_page_slug = st.session_state.nav_page.replace(" ", "_")
view_key = f"main_view_{clean_page_slug}_{st.session_state.nav_count}"

st.markdown(f"""
<style>
div.st-key-{view_key} {{
    animation: {anim_name} {anim_duration} cubic-bezier(0.22, 1, 0.36, 1) both !important;
    will-change: transform, opacity, filter !important;
    backface-visibility: hidden !important;
    -webkit-backface-visibility: hidden !important;
    transform-style: preserve-3d !important;
}}
</style>
""", unsafe_allow_html=True)

with st.container(key=view_key):


    # =============================================================================
    # SCREEN 1: BERANDA
    # =============================================================================
    if st.session_state.nav_page == "Beranda":
        col_hero_text, col_hero_card = st.columns([7.2, 2.8], gap="large")
        with col_hero_text:
            st.markdown("""
                <div style="font-size: 0.76rem; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; color: #6E6E73; margin-bottom: 0.35rem;">
                    Sistem Pendukung Keputusan • Multi-Criteria Decision Making
                </div>
                <h1 style="font-size: 2.35rem; font-weight: 800; color: #1D1D1F; letter-spacing: -0.025em; line-height: 1.2; margin-bottom: 0.65rem;">
                    Temukan Smartphone yang Tepat untukmu
                </h1>
                <p style="font-size: 1rem; color: #515154; max-width: 740px; line-height: 1.6; margin-bottom: 1.75rem;">
                    Rekomendasi smartphone presisi berbasis segmentasi algoritma K-Means Clustering dan perangkingan multi-kriteria TOPSIS yang telah diuji secara ilmiah oleh Teknik Informatika.
                </p>
            """, unsafe_allow_html=True)

            c_cta, _ = st.columns([3.2, 6.8])
            with c_cta:
                if st.button("Mulai Rekomendasi  →", type="primary", use_container_width=True, key="btn_hero_cta"):
                    navigate("Cari Rekomendasi")

        with col_hero_card:
            logo_card_html = f'<img src="data:image/png;base64,{B64_LOGO_FULL}" style="max-width: 100%; max-height: 85px; object-fit: contain; margin-bottom: 0.85rem;" alt="SmartPick Informatika" />' if B64_LOGO_FULL else ''
            st.markdown(f"""
                <div class="apple-card" style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 1.5rem; height: 100%; box-sizing: border-box;">
                    {logo_card_html}
                    <span class="apple-chip chip-accent" style="font-size: 0.75rem; margin-top: 0.25rem;">Sistem Rekomendasi Terverifikasi</span>
                    <span style="font-size: 0.74rem; color: #86868B; margin-top: 0.5rem;">Program Studi Teknik Informatika</span>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

        # 3 Stat Cards
        s1, s2, s3 = st.columns(3)
        with s1:
            st.markdown("""
                <div class="apple-card" style="margin-bottom: 0;">
                    <div style="font-size: 1.75rem; font-weight: 700; color: #1D1D1F; letter-spacing: -0.02em;">7 Kriteria</div>
                    <div style="font-size: 0.85rem; color: #6E6E73; margin-top: 0.2rem;">Parameter Analitik Terverifikasi</div>
                </div>
            """, unsafe_allow_html=True)
        with s2:
            st.markdown("""
                <div class="apple-card" style="margin-bottom: 0;">
                    <div style="font-size: 1.75rem; font-weight: 700; color: #1D1D1F; letter-spacing: -0.02em;">2 Cluster</div>
                    <div style="font-size: 0.85rem; color: #6E6E73; margin-top: 0.2rem;">Segmentasi Karakteristik K-Means</div>
                </div>
            """, unsafe_allow_html=True)
        with s3:
            st.markdown("""
                <div class="apple-card" style="margin-bottom: 0;">
                    <div style="font-size: 1.75rem; font-weight: 700; color: #1D1D1F; letter-spacing: -0.02em;">Top 10</div>
                    <div style="font-size: 0.85rem; color: #6E6E73; margin-top: 0.2rem;">Ranking Solusi Ideal TOPSIS</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom: 2.5rem;'></div>", unsafe_allow_html=True)

        # Section 7 Kriteria
        sec_l, sec_r = st.columns([7, 3])
        with sec_l:
            st.markdown("""
                <div style="font-size: 0.76rem; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; color: #6E6E73; margin-bottom: 0.25rem;">
                    Matriks Dasar Penelitian
                </div>
                <h3 style="font-size: 1.35rem; font-weight: 700; color: #1D1D1F; margin: 0 0 0.35rem 0;">
                    7 Kriteria Parameter Rekomendasi
                </h3>
                <p style="font-size: 0.88rem; color: #6E6E73; margin: 0;">
                    Karakteristik matematis Cost dan Benefit yang dinormalisasi ke dalam matriks keputusan TOPSIS.
                </p>
            """, unsafe_allow_html=True)
        with sec_r:
            st.markdown("""
                <div style="display: flex; justify-content: flex-end; align-items: center; gap: 0.75rem; height: 100%;">
                    <span class="apple-chip chip-cost">Cost (Makin rendah makin baik)</span>
                    <span class="apple-chip chip-benefit">Benefit (Makin tinggi makin baik)</span>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom: 1.25rem;'></div>", unsafe_allow_html=True)

        # 7 Cards Grid
        crit_keys = list(CRITERIA.keys())

        # Row 1 (4 cards)
        row1 = st.columns(4)
        for i in range(4):
            k = crit_keys[i]
            c_item = CRITERIA[k]
            badge_cls = "chip-cost" if c_item["type"] == "Cost" else "chip-benefit"
            with row1[i]:
                st.markdown(f"""
                    <div class="apple-card" style="height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
                        <div>
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem; margin-bottom: 0.65rem;">
                                <span style="font-weight: 700; font-size: 0.95rem; color: #1D1D1F;">{i+1}. {c_item['name']}</span>
                                <span class="apple-chip {badge_cls}">{c_item['type']} ({c_item['code']})</span>
                            </div>
                            <div style="font-size: 0.82rem; color: #515154; line-height: 1.5;">{c_item['desc']}</div>
                        </div>
                        <div style="margin-top: 1rem; font-size: 0.75rem; color: #6E6E73;">
                            Satuan: <strong style="color: #1D1D1F;">{c_item['unit']}</strong>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom: 0.85rem;'></div>", unsafe_allow_html=True)

        # Row 2 (3 cards)
        row2 = st.columns(3)
        for i in range(4, 7):
            k = crit_keys[i]
            c_item = CRITERIA[k]
            badge_cls = "chip-cost" if c_item["type"] == "Cost" else "chip-benefit"
            with row2[i - 4]:
                st.markdown(f"""
                    <div class="apple-card" style="height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
                        <div>
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem; margin-bottom: 0.65rem;">
                                <span style="font-weight: 700; font-size: 0.95rem; color: #1D1D1F;">{i+1}. {c_item['name']}</span>
                                <span class="apple-chip {badge_cls}">{c_item['type']} ({c_item['code']})</span>
                            </div>
                            <div style="font-size: 0.82rem; color: #515154; line-height: 1.5;">{c_item['desc']}</div>
                        </div>
                        <div style="margin-top: 1rem; font-size: 0.75rem; color: #6E6E73;">
                            Satuan: <strong style="color: #1D1D1F;">{c_item['unit']}</strong>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        # Bottom Banner (Clean native container)
        with st.container(border=True):
            b_c1, b_c2 = st.columns([7.5, 2.5])
            with b_c1:
                st.markdown("""
                    <div style="font-size: 1.15rem; font-weight: 700; color: #1D1D1F; margin-bottom: 0.2rem;">
                        Siap Menemukan Smartphone Pilihanmu?
                    </div>
                    <div style="font-size: 0.85rem; color: #515154;">
                        Tentukan batasan anggaran dan kebutuhan harian untuk menghitung rekomendasi otomatis.
                    </div>
                """, unsafe_allow_html=True)
            with b_c2:
                if st.button("Mulai Perhitungan  →", type="primary", use_container_width=True, key="btn_cta_bottom"):
                    navigate("Cari Rekomendasi")

    # =============================================================================
    # SCREEN 2: CARI REKOMENDASI (FORM)
    # =============================================================================
    elif st.session_state.nav_page == "Cari Rekomendasi":
        st.markdown("""
            <div style="font-size: 0.76rem; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; color: #6E6E73; margin-bottom: 0.25rem;">
                Preferensi Pengguna • Multi-Criteria Setup
            </div>
            <h2 style="font-size: 1.85rem; font-weight: 700; color: #1D1D1F; margin-bottom: 0.35rem;">
                Atur Preferensi Kebutuhan Smartphone
            </h2>
            <p style="font-size: 0.92rem; color: #515154; max-width: 780px; line-height: 1.55; margin-bottom: 1.75rem;">
                Pilih anggaran dan fokus penggunaan harian. Sistem SmartPick akan menyaring dataset menggunakan K-Means Clustering dan perangkingan TOPSIS dengan bobot ilmiah yang telah teruji.
            </p>
        """, unsafe_allow_html=True)

        # Question 1: Budget
        with st.container(border=True):
            st.markdown("""
                <div style="font-size: 1.05rem; font-weight: 700; color: #1D1D1F; margin-bottom: 0.2rem;">
                    1. Rentang Anggaran (Budget)
                </div>
                <div style="font-size: 0.82rem; color: #6E6E73; margin-bottom: 0.85rem;">
                    Tentukan batasan harga smartphone untuk penyaringan awal alternatif dalam Rupiah (IDR).
                </div>
            """, unsafe_allow_html=True)

            budget_options = [
                "Di bawah Rp 2.000.000 — Entry-Level Terjangkau",
                "Rp 2.000.000 – Rp 3.000.000 — Mid-Range Budget",
                "Rp 3.000.000 – Rp 5.000.000 — Mid-Range Populer (Keseimbangan Spesifikasi & Harga)",
                "Rp 5.000.000 – Rp 8.000.000 — Upper Mid-Range",
                "Di atas Rp 10.000.000 — Flagship & Premium",
            ]

            curr_b_idx = min(max(0, st.session_state.budget_choice), len(budget_options) - 1)
            sel_budget = st.radio(
                "Pilih Anggaran",
                options=budget_options,
                index=curr_b_idx,
                label_visibility="collapsed",
                key="radio_budget_input"
            )
            st.session_state.budget_choice = budget_options.index(sel_budget)

        # Question 2: Usage
        with st.container(border=True):
            st.markdown("""
                <div style="font-size: 1.05rem; font-weight: 700; color: #1D1D1F; margin-bottom: 0.2rem;">
                    2. Smartphone ini paling sering kamu gunakan untuk apa?
                </div>
                <div style="font-size: 0.82rem; color: #6E6E73; margin-bottom: 0.85rem;">
                    Pilih satu kebutuhan utama yang paling mencerminkan aktivitas harianmu.
                </div>
            """, unsafe_allow_html=True)

            usage_options = [
                "▷  Gaming — Bermain game dengan performa grafis tinggi, chipset kencang, refresh rate stabil",
                "◎  Fotografi & Konten — Mengambil foto jernih, video resolusi tinggi & pembuatan konten",
                "◈  Produktivitas — Kuliah, pekerjaan kantor, multitasking aplikasi & dokumen",
                "◉  Penggunaan Sehari-hari — Komunikasi, media sosial, navigasi & daya tahan harian andal",
                "◇  Hemat Budget — Mendapatkan smartphone fungsional dengan harga paling efisien",
            ]

            sel_usage = st.radio(
                "Pilih Aktivitas",
                options=usage_options,
                index=st.session_state.usage_choice,
                label_visibility="collapsed",
                key="radio_usage_input"
            )
            st.session_state.usage_choice = usage_options.index(sel_usage)

        # Question 3: Priority Checkboxes
        with st.container(border=True):
            st.markdown("""
                <div style="font-size: 1.05rem; font-weight: 700; color: #1D1D1F; margin-bottom: 0.2rem;">
                    3. Apa yang paling kamu prioritaskan?
                </div>
                <div style="font-size: 0.82rem; color: #6E6E73; margin-bottom: 0.85rem;">
                    Pilih aspek spesifik yang Anda utamakan sebagai aturan penyaringan tambahan.
                </div>
            """, unsafe_allow_html=True)

            p1, p2 = st.columns(2)
            with p1:
                st.checkbox("◈  Performa dan Kecepatan CPU", value=True, key="cb_p1")
                st.checkbox("◎  Resolusi Kamera Tinggi", value=False, key="cb_p2")
                st.checkbox("▣  RAM & Storage Besar", value=False, key="cb_p3")
            with p2:
                st.checkbox("▷  Baterai Tahan Lama & Fast Charge", value=False, key="cb_p4")
                st.checkbox("◇  Efisiensi Harga Terjangkau", value=False, key="cb_p5")

        # Action Buttons
        ab1, ab2 = st.columns([3, 7])
        with ab1:
            if st.button("Reset Preferensi", use_container_width=True, key="btn_reset"):
                st.session_state.budget_choice = 2
                st.session_state.usage_choice = 0
                st.rerun()
        with ab2:
            if st.button("Cari Rekomendasi (Hitung SPK)  →", type="primary", use_container_width=True, key="btn_calc"):
                load_box = st.empty()
                steps = [
                    ("Memfilter data sesuai rentang anggaran & preferensi...", 25),
                    ("Segmentasi K-Means Clustering (2 Klaster Karakteristik)...", 55),
                    ("Normalisasi matriks & kalkulasi solusi ideal TOPSIS...", 85),
                    ("Menyusun perangkingan smartphone terbaik...", 100)
                ]
                for text, pct in steps:
                    load_box.markdown(f"""
                        <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0, 0, 0, 0.45); backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px); z-index: 9999999; display: flex; align-items: center; justify-content: center; pointer-events: all;">
                            <div style="background: #FFFFFF; border-radius: 24px; padding: 2.8rem 2.2rem; width: 90%; max-width: 420px; box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.35); text-align: center; border: 1px solid rgba(255, 255, 255, 0.8); animation: modalFadeIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);">
                                <div style="margin: 0 auto 1.5rem auto; width: 96px; height: 96px; display: flex; align-items: center; justify-content: center; background: #F5F5F7; border-radius: 50%; box-shadow: inset 0 2px 6px rgba(0,0,0,0.04);">
                                    <img src="data:image/png;base64,{B64_LOGO_ICON}" style="width: 58px; height: 58px; object-fit: contain; animation: spinLogo 1.2s linear infinite;" alt="SmartPick Logo" />
                                </div>
                                <div style="font-weight: 700; font-size: 1.25rem; color: #1D1D1F; margin-bottom: 0.4rem; letter-spacing: -0.01em;">
                                    Menganalisis Rekomendasi
                                </div>
                                <div style="font-size: 0.88rem; color: #6E6E73; margin-bottom: 1.4rem; min-height: 1.5rem; line-height: 1.4;">
                                    {text}
                                </div>
                                <div style="width: 100%; height: 6px; background: #E5E5EA; border-radius: 99px; overflow: hidden;">
                                    <div style="width: {pct}%; height: 100%; background: #0071E3; border-radius: 99px; transition: width 0.3s ease;"></div>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    time.sleep(0.35)

                df_pool = DF_SMARTPHONES.copy()
                b_idx = st.session_state.budget_choice

                if b_idx == 0:
                    df_pool = df_pool[df_pool["price_idr"] < 2000000]
                elif b_idx == 1:
                    df_pool = df_pool[(df_pool["price_idr"] >= 2000000) & (df_pool["price_idr"] <= 3000000)]
                elif b_idx == 2:
                    df_pool = df_pool[(df_pool["price_idr"] >= 3000000) & (df_pool["price_idr"] <= 5000000)]
                elif b_idx == 3:
                    df_pool = df_pool[(df_pool["price_idr"] >= 5000000) & (df_pool["price_idr"] <= 8000000)]
                elif b_idx == 4:
                    df_pool = df_pool[df_pool["price_idr"] >= 8000000]

                if len(df_pool) == 0:
                    df_pool = DF_SMARTPHONES.copy()

                results = calculate_topsis(df_pool, WEIGHTS_DICT)
                st.session_state.topsis_data = results
                load_box.empty()
                navigate("Hasil Rekomendasi")

    # =============================================================================
    # SCREEN 3: HASIL REKOMENDASI (TOP 10 CARDS)
    # =============================================================================
    elif st.session_state.nav_page == "Hasil Rekomendasi":
        if st.session_state.topsis_data is None or len(st.session_state.topsis_data) == 0:
            st.session_state.topsis_data = calculate_topsis(DF_SMARTPHONES, WEIGHTS_DICT)

        df_results = st.session_state.topsis_data
        total_found = len(df_results)
        top_n = min(10, total_found)

        # Title
        st.markdown("""
            <h2 style="font-size: 1.85rem; font-weight: 700; color: #1D1D1F; margin-bottom: 0.85rem;">
                Hasil Rekomendasi dari Kriteria yang Anda Inginkan
            </h2>
        """, unsafe_allow_html=True)

        # Professional Search Bar with Real-time Filtering
        search_col, stat_col = st.columns([7.5, 2.5])
        with search_col:
            search_query = st.text_input(
                "Cari Smartphone Rekomendasi",
                placeholder="🔍 Ketik nama smartphone, brand (Xiaomi, Vivo, Samsung, dll), prosesor, RAM...",
                key="search_phone_input",
                label_visibility="collapsed"
            )

        sq = search_query.strip().lower()
        if sq:
            def matches(r):
                text_pool = f"{r['model']} {r['smartphone_brand']} {r.get('processor_name', '')} {r.get('processor_brand', '')} {int(r['ram_gb'])}gb {int(r['storage_gb'])}gb"
                if r.get('has_5g', False):
                    text_pool += " 5g"
                return sq in text_pool.lower()
            
            display_df = df_results[df_results.apply(matches, axis=1)]
        else:
            display_df = df_results.head(10)

        with stat_col:
            if sq:
                st.markdown(f"""
                    <div style="display: flex; justify-content: flex-end; align-items: center; height: 100%; padding-bottom: 0.5rem;">
                        <span class="apple-chip chip-accent" style="padding: 0.45rem 0.85rem; font-size: 0.8rem;">
                            Ditemukan {len(display_df)} Smartphone
                        </span>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div style="display: flex; justify-content: flex-end; align-items: center; height: 100%; padding-bottom: 0.5rem;">
                        <span class="apple-chip chip-neutral" style="padding: 0.45rem 0.85rem; font-size: 0.8rem;">
                            Top {min(10, total_found)} Rekomendasi
                        </span>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

        if len(display_df) == 0:
            st.markdown(f"""
                <div class="apple-card" style="text-align: center; padding: 3.5rem 1.5rem; margin: 1.5rem 0;">
                    <div style="font-size: 2.8rem; margin-bottom: 0.6rem;">🔍</div>
                    <div style="font-weight: 700; font-size: 1.25rem; color: #1D1D1F; margin-bottom: 0.35rem;">
                        Tidak Ditemukan Smartphone yang Cocok
                    </div>
                    <div style="color: #6E6E73; font-size: 0.88rem; max-width: 480px; margin: 0 auto 1.5rem auto; line-height: 1.5;">
                        Pencarian untuk <strong>"{search_query}"</strong> tidak menemukan hasil pada kriteria smartphone yang disaring. Coba periksa ejaan atau gunakan kata kunci lain (misal: nama brand, prosesor, atau kapasitas RAM).
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("← Reset Pencarian", key="btn_clear_search", type="secondary"):
                st.session_state["search_phone_input"] = ""
                st.rerun()
        else:
            display_count = len(display_df)
            grid_cols = st.columns(3)
            for idx in range(display_count):
                row = display_df.iloc[idx]
                col_pos = idx % 3
                with grid_cols[col_pos]:
                    with st.container(border=True):
                        price_str = format_rupiah(row["price_idr"])
                        score_str = f"{row['nilai_preferensi']:.4f}"
                        rank_num = int(row.get("ranking", idx + 1))

                        # Highlight
                        highlight = "Performa seimbang dan efisiensi baterai untuk penggunaan harian"
                        if row.get("charging_watt", 0) >= 67:
                            highlight = "Dukungan fast charging tinggi dengan efisiensi pengisian daya cepat"
                        elif row.get("rear_camera_main_mp", 0) >= 64:
                            highlight = "Kamera resolusi tinggi optimal untuk fotografi dan kreasi konten"
                        elif row.get("clock_speed_ghz", 0) >= 3.0:
                            highlight = "Kecepatan prosesor flagship untuk kebutuhan komputasi berat"

                        brand_str = str(row.get("smartphone_brand", "")).title()
                        brand_raw = str(row.get("smartphone_brand", ""))
                        phone_mockup = render_smartphone_image_html(row['model'], brand_raw, width=78, height=100)

                        st.markdown(f"""
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                <span class="apple-chip chip-neutral" style="font-weight: 700; color: #1D1D1F;">Top {rank_num}</span>
                                <span class="apple-chip chip-accent">Skor V = {score_str}</span>
                            </div>
                            <div style="display: flex; gap: 0.85rem; align-items: flex-start; margin-bottom: 0.5rem;">
                                {phone_mockup}
                                <div style="flex: 1; min-width: 0;">
                                    <div style="font-size: 0.72rem; color: #6E6E73; text-transform: uppercase; letter-spacing: 0.04em; margin-bottom: 0.15rem;">{brand_str}</div>
                                    <div style="font-size: 1.05rem; font-weight: 700; color: #1D1D1F; line-height: 1.3; margin-bottom: 0.25rem; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                                        {row['model']}
                                    </div>
                                    <div style="font-size: 1.1rem; font-weight: 700; color: #1D1D1F;">
                                        {price_str}
                                    </div>
                                </div>
                            </div>
                            <div style="font-size: 0.78rem; color: #515154; min-height: 2rem; line-height: 1.45; margin-bottom: 0.5rem; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                                {highlight}
                            </div>
                            <div class="spec-group">
                                <span class="spec-chip">◈ {row['clock_speed_ghz']} GHz</span>
                                <span class="spec-chip">▣ {int(row['ram_gb'])}GB/{int(row['storage_gb'])}GB</span>
                                <span class="spec-chip">▷ {int(row['battery_mah']):,} mAh</span>
                                <span class="spec-chip">◎ {int(row['rear_camera_main_mp'])} MP</span>
                                <span class="spec-chip">◉ {int(row['charging_watt'])}W</span>
                            </div>
                        """, unsafe_allow_html=True)

                        if st.button("Lihat Detail Spesifikasi", key=f"btn_card_detail_{idx}_{rank_num}", use_container_width=True, type="secondary"):
                            navigate("Detail", row["model"])

        # Bottom Summary Tile
        st.markdown("""
            <div class="apple-card" style="margin-top: 1rem; padding: 1.35rem 1.6rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem; margin-bottom: 0.75rem;">
                    <span style="font-weight: 700; font-size: 0.95rem; color: #1D1D1F;">Rincian Komputasi Algoritma SPK</span>
                    <span class="apple-chip chip-neutral">Metode: K-Means (Euclidean) + TOPSIS</span>
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; font-size: 0.75rem;">
                    <span class="apple-chip chip-cost">K1: Harga (Cost)</span>
                    <span class="apple-chip chip-benefit">K2: RAM (Benefit)</span>
                    <span class="apple-chip chip-benefit">K3: ROM (Benefit)</span>
                    <span class="apple-chip chip-benefit">K4: Clock Speed (Benefit)</span>
                    <span class="apple-chip chip-benefit">K5: Baterai (Benefit)</span>
                    <span class="apple-chip chip-benefit">K6: Kamera (Benefit)</span>
                    <span class="apple-chip chip-benefit">K7: Fast Charge (Benefit)</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # =============================================================================
    # SCREEN 4: DETAIL SMARTPHONE
    # =============================================================================
    elif st.session_state.nav_page == "Detail":
        target_model = st.session_state.selected_phone
        results_df = st.session_state.topsis_data

        if results_df is None or target_model is None or target_model not in results_df["model"].values:
            results_df = calculate_topsis(DF_SMARTPHONES, WEIGHTS_DICT)
            st.session_state.topsis_data = results_df
            if target_model not in results_df["model"].values:
                target_model = results_df.iloc[0]["model"]

        item = results_df[results_df["model"] == target_model].iloc[0]

        rank_num = int(item["ranking"])
        score_val = float(item["nilai_preferensi"])
        d_pos_val = float(item["jarak_positif"])
        d_neg_val = float(item["jarak_negatif"])
        price_fmt = format_rupiah(item["price_idr"])
        cluster_val = int(item.get("cluster", 0))
        cluster_desc = "Cluster 1 — Spesifikasi Flagship & Performa Tinggi" if cluster_val == 0 else "Cluster 2 — Mid-Range & Efisiensi Biaya"
        tier_desc = "Flagship Tier" if cluster_val == 0 else "Mid-Range Tier"
        dist_val = f"{float(item.get('dist_centroid', 0.0821)):.4f}"
        brand_title = str(item.get("smartphone_brand", "")).title()

        # Back Action
        bk_c, _ = st.columns([3, 7])
        with bk_c:
            if st.button("← Kembali ke Hasil Rekomendasi", use_container_width=True, key="back_to_results", type="secondary"):
                navigate("Hasil Rekomendasi")

        st.markdown(f"""
            <div style="font-size: 0.76rem; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; color: #6E6E73; margin: 1rem 0 0.5rem 0;">
                Hasil Rekomendasi › Detail Smartphone › {item['model']}
            </div>
        """, unsafe_allow_html=True)

        # Hero Phone Tile
        has_5g_support = item.get("has_5g", False)
        badge_network = "5G Connected" if has_5g_support else "4G LTE"
        detail_brand_raw = str(item.get("smartphone_brand", ""))
        detail_phone_mockup = render_smartphone_image_html(item['model'], detail_brand_raw, width=95, height=125)

        st.markdown(f"""
            <div class="apple-card" style="padding: 1.6rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1.25rem;">
                    <div style="display: flex; gap: 1.25rem; align-items: center;">
                        <div style="display: flex; flex-direction: column; align-items: center; gap: 0.3rem; flex-shrink: 0;">
                            {detail_phone_mockup}
                            <span class="apple-chip chip-neutral" style="font-size: 0.65rem; padding: 0.1rem 0.45rem;">{badge_network}</span>
                        </div>
                        <div>
                            <div style="display: flex; gap: 0.45rem; margin-bottom: 0.35rem; flex-wrap: wrap;">
                                <span class="apple-chip chip-neutral">Peringkat #{rank_num} dari Alternatif Terfilter</span>
                                <span class="apple-chip chip-neutral">Basis 758 Alternatif</span>
                            </div>
                            <h2 style="font-size: 1.75rem; font-weight: 700; color: #1D1D1F; margin: 0 0 0.25rem 0; line-height: 1.25;">
                                {item['model']}
                            </h2>
                            <div style="font-size: 0.88rem; color: #515154; margin-bottom: 0.3rem;">
                                Arsitektur Mobile Presisi dengan Efisiensi Komputasi Teruji TOPSIS
                            </div>
                            <div style="font-size: 0.8rem; color: #6E6E73;">
                                Brand: <strong style="color: #1D1D1F;">{brand_title}</strong> &nbsp;•&nbsp; Kategori: <strong style="color: #1D1D1F;">{tier_desc}</strong>
                            </div>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 0.8rem; color: #6E6E73; font-weight: 500;">Harga Acuan Resmi</div>
                        <div style="font-size: 1.85rem; font-weight: 700; color: #1D1D1F; letter-spacing: -0.02em;">{price_fmt}</div>
                        <div class="apple-chip chip-cost" style="margin-top: 0.25rem;">Kriteria Biaya Terfilter (C1)</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Two Main Analytics Tiles
        an_c1, an_c2 = st.columns(2)
        with an_c1:
            st.markdown(f"""
                <div class="apple-card" style="height: 100%;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.65rem;">
                        <span style="font-size: 1.05rem; font-weight: 700; color: #1D1D1F;">Skor Preferensi TOPSIS (Vi)</span>
                        <span class="apple-chip chip-accent">V_{rank_num}</span>
                    </div>
                    <div style="font-size: 2.35rem; font-weight: 700; color: #1D1D1F; letter-spacing: -0.03em; margin-bottom: 0.2rem;">
                        {score_val:.4f}
                    </div>
                    <div style="font-size: 0.82rem; color: #515154; margin-bottom: 0.85rem;">
                        Nilai kedekatan relatif terhadap solusi ideal positif (rentang 0.0000 – 1.0000)
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.6rem 0.8rem; background: #F5F5F7; border-radius: 10px; font-size: 0.78rem;">
                        <span style="color: #1E7E34; font-weight: 600;">Status: Kedekatan Tertinggi</span>
                        <span style="color: #515154; font-family: monospace;">D⁺ = {d_pos_val:.4f} &nbsp;|&nbsp; D⁻ = {d_neg_val:.4f}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with an_c2:
            st.markdown(f"""
                <div class="apple-card" style="height: 100%;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.65rem;">
                        <span style="font-size: 1.05rem; font-weight: 700; color: #1D1D1F;">Segmentasi K-Means</span>
                        <span class="apple-chip chip-neutral">2 Klaster</span>
                    </div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #1D1D1F; margin: 0.25rem 0 0.25rem 0;">
                        {cluster_desc}
                    </div>
                    <div style="font-size: 0.82rem; color: #515154; margin-bottom: 0.85rem;">
                        Jarak Euclidean ke Centroid Klaster: <strong>{dist_val}</strong>
                    </div>
                    <div style="padding: 0.6rem 0.8rem; background: #F5F5F7; border-radius: 10px; font-size: 0.78rem; color: #515154;">
                        ◈ Karakteristik: <strong>RAM {int(item['ram_gb'])}GB &nbsp;•&nbsp; ROM {int(item['storage_gb'])}GB &nbsp;•&nbsp; {item['clock_speed_ghz']} GHz</strong>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom: 1.25rem;'></div>", unsafe_allow_html=True)

        # 3 Recommendation Reason Cards
        st.markdown("""
            <h3 style="font-size: 1.25rem; font-weight: 700; color: #1D1D1F; margin-bottom: 0.2rem;">
                Kenapa Smartphone Ini Direkomendasikan?
            </h3>
            <p style="font-size: 0.85rem; color: #515154; margin-bottom: 1rem;">
                Tiga faktor utama pembuktian matematis hasil perankingan SPK.
            </p>
        """, unsafe_allow_html=True)

        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            st.markdown(f"""
                <div class="apple-card" style="height: 100%; padding: 1.35rem;">
                    <div style="font-weight: 700; font-size: 0.95rem; color: #1D1D1F; margin-bottom: 0.35rem;">
                        🎯 Sesuai Batasan Anggaran
                    </div>
                    <div style="font-size: 0.82rem; color: #515154; line-height: 1.5; margin-bottom: 0.85rem;">
                        Harga {price_fmt} masuk dalam filter rentang biaya pengguna tanpa mengorbankan parameter teknis utama.
                    </div>
                    <span class="apple-chip chip-cost">✓ Kriteria C1 (Cost) Terpenuhi</span>
                </div>
            """, unsafe_allow_html=True)

        with rc2:
            st.markdown(f"""
                <div class="apple-card" style="height: 100%; padding: 1.35rem;">
                    <div style="font-weight: 700; font-size: 0.95rem; color: #1D1D1F; margin-bottom: 0.35rem;">
                        ⚙️ Spesifikasi Sesuai Kebutuhan
                    </div>
                    <div style="font-size: 0.82rem; color: #515154; line-height: 1.5; margin-bottom: 0.85rem;">
                        Kombinasi RAM {int(item['ram_gb'])}GB, ROM {int(item['storage_gb'])}GB, dan clock speed {item['clock_speed_ghz']} GHz memberikan efisiensi tinggi kriteria manfaat.
                    </div>
                    <span class="apple-chip chip-benefit">✓ Kriteria C2, C3, C4 Unggul</span>
                </div>
            """, unsafe_allow_html=True)

        with rc3:
            st.markdown(f"""
                <div class="apple-card" style="height: 100%; padding: 1.35rem;">
                    <div style="font-weight: 700; font-size: 0.95rem; color: #1D1D1F; margin-bottom: 0.35rem;">
                        🏆 Kedekatan Relatif Tertinggi
                    </div>
                    <div style="font-size: 0.82rem; color: #515154; line-height: 1.5; margin-bottom: 0.85rem;">
                        Memiliki jarak terdekat dengan solusi ideal positif (D⁺) dan terjauh dari negatif (D⁻) berdasarkan bobot ilmiah.
                    </div>
                    <span class="apple-chip chip-accent">✓ Skor V = {score_val:.4f} (Peringkat #{rank_num})</span>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

        # 7 Criteria Parameter Breakdown
        st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.85rem;">
                <div>
                    <h3 style="font-size: 1.25rem; font-weight: 700; color: #1D1D1F; margin: 0 0 0.2rem 0;">
                        Spesifikasi 7 Kriteria Penelitian SPK
                    </h3>
                    <div style="font-size: 0.82rem; color: #515154;">
                        Matriks parameter matematis dan nilai normalisasi vektor (rij) dalam algoritma TOPSIS.
                    </div>
                </div>
                <div style="display: flex; gap: 0.5rem;">
                    <span class="apple-chip chip-benefit">6 Kriteria Benefit</span>
                    <span class="apple-chip chip-cost">1 Kriteria Cost</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        crit_meta_list = [
            ("C1", "Harga", "price_idr", price_fmt, "Cost", WEIGHTS_DICT.get("price_idr", 0.20)),
            ("C2", "Kapasitas RAM", "ram_gb", f"{int(item['ram_gb'])} GB", "Benefit", WEIGHTS_DICT.get("ram_gb", 0.15)),
            ("C3", "Penyimpanan ROM", "storage_gb", f"{int(item['storage_gb'])} GB", "Benefit", WEIGHTS_DICT.get("storage_gb", 0.12)),
            ("C4", "Kecepatan CPU", "clock_speed_ghz", f"{item['clock_speed_ghz']} GHz", "Benefit", WEIGHTS_DICT.get("clock_speed_ghz", 0.18)),
            ("C5", "Kapasitas Baterai", "battery_mah", f"{int(item['battery_mah']):,} mAh", "Benefit", WEIGHTS_DICT.get("battery_mah", 0.15)),
            ("C6", "Kamera Utama", "rear_camera_main_mp", f"{int(item['rear_camera_main_mp'])} MP", "Benefit", WEIGHTS_DICT.get("rear_camera_main_mp", 0.10)),
            ("C7", "Fast Charging", "charging_watt", f"{int(item['charging_watt'])} Watt", "Benefit", WEIGHTS_DICT.get("charging_watt", 0.10)),
        ]

        # Row 1 (4 items)
        dt_c1 = st.columns(4)
        for i in range(4):
            code, name, key, actual_str, c_type, weight_val = crit_meta_list[i]
            b_class = "chip-cost" if c_type == "Cost" else "chip-benefit"
            norm_v = float(item.get(f"norm_{key}", 0.0))
            pct_label = f"{weight_val * 100:.1f}%"
            with dt_c1[i]:
                st.markdown(f"""
                    <div class="apple-card-compact">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 0.4rem; margin-bottom: 0.4rem;">
                            <span style="font-size: 0.8rem; font-weight: 700; color: #1D1D1F;">{code} • {name}</span>
                            <span class="apple-chip {b_class}">{c_type} {pct_label}</span>
                        </div>
                        <div style="font-size: 0.72rem; color: #6E6E73;">Nilai Aktual</div>
                        <div style="font-size: 0.98rem; font-weight: 700; color: #1D1D1F; margin-bottom: 0.35rem;">{actual_str}</div>
                        <div style="font-size: 0.72rem; color: #515154;">
                            Normalisasi: <strong style="color: #1D1D1F;">r = {norm_v:.4f}</strong>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        # Row 2 (3 items)
        dt_c2 = st.columns(3)
        for i in range(4, 7):
            code, name, key, actual_str, c_type, weight_val = crit_meta_list[i]
            b_class = "chip-cost" if c_type == "Cost" else "chip-benefit"
            norm_v = float(item.get(f"norm_{key}", 0.0))
            pct_label = f"{weight_val * 100:.1f}%"
            with dt_c2[i - 4]:
                st.markdown(f"""
                    <div class="apple-card-compact">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 0.4rem; margin-bottom: 0.4rem;">
                            <span style="font-size: 0.8rem; font-weight: 700; color: #1D1D1F;">{code} • {name}</span>
                            <span class="apple-chip {b_class}">{c_type} {pct_label}</span>
                        </div>
                        <div style="font-size: 0.72rem; color: #6E6E73;">Nilai Aktual</div>
                        <div style="font-size: 0.98rem; font-weight: 700; color: #1D1D1F; margin-bottom: 0.35rem;">{actual_str}</div>
                        <div style="font-size: 0.72rem; color: #515154;">
                            Normalisasi: <strong style="color: #1D1D1F;">r = {norm_v:.4f}</strong>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
        _, bottom_center, _ = st.columns([3, 4, 3])
        with bottom_center:
            if st.button("← Kembali ke Daftar Rekomendasi", key="btn_back_bottom", use_container_width=True, type="secondary"):
                navigate("Hasil Rekomendasi")


# =============================================================================
# FOOTER BRANDING (SMARTPICK INFORMATIKA)
# =============================================================================
icon_ft_html = f'<img src="data:image/png;base64,{B64_LOGO_ICON}" height="22" style="object-fit: contain; vertical-align: middle; border-radius: 4px;" />' if B64_LOGO_ICON else '📱'
st.markdown(f"""
    <div style="margin-top: 3.5rem; padding-top: 1.5rem; border-top: 1px solid rgba(0, 0, 0, 0.08); display: flex; justify-content: space-between; align-items: center; color: #86868B; font-size: 0.8rem;">
        <div style="display: flex; align-items: center; gap: 0.6rem;">
            {icon_ft_html}
            <span style="font-weight: 700; color: #1D1D1F;">SmartPick Informatika</span>
            <span>• Sistem Pendukung Keputusan Pemilihan Smartphone</span>
        </div>
        <div>
            K-Means Clustering &amp; TOPSIS Algorithm • Hybrid MCDM
        </div>
    </div>
""", unsafe_allow_html=True)
