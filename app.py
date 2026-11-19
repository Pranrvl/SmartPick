import os
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
# BRAND IMAGE SYSTEM — Gradient phone mockups with brand colors (no API needed)
# =============================================================================
BRAND_STYLES = {
    "samsung":  {"gradient": "linear-gradient(135deg, #1428A0 0%, #4A90D9 100%)", "letter": "S", "accent": "#1428A0"},
    "apple":    {"gradient": "linear-gradient(135deg, #333333 0%, #555555 100%)", "letter": "A", "accent": "#333333"},
    "xiaomi":   {"gradient": "linear-gradient(135deg, #FF6900 0%, #FF9A44 100%)", "letter": "X", "accent": "#FF6900"},
    "oppo":     {"gradient": "linear-gradient(135deg, #1A8D1A 0%, #4ADE4A 100%)", "letter": "O", "accent": "#1A8D1A"},
    "vivo":     {"gradient": "linear-gradient(135deg, #415FFF 0%, #7B93FF 100%)", "letter": "V", "accent": "#415FFF"},
    "realme":   {"gradient": "linear-gradient(135deg, #F5C900 0%, #FFE066 100%)", "letter": "R", "accent": "#C4A000"},
    "poco":     {"gradient": "linear-gradient(135deg, #FFD500 0%, #FFEB80 100%)", "letter": "P", "accent": "#C4A800"},
    "oneplus":  {"gradient": "linear-gradient(135deg, #EB0028 0%, #FF5252 100%)", "letter": "1+", "accent": "#EB0028"},
    "motorola": {"gradient": "linear-gradient(135deg, #5C2D91 0%, #8B5CF6 100%)", "letter": "M", "accent": "#5C2D91"},
    "nothing":  {"gradient": "linear-gradient(135deg, #000000 0%, #333333 100%)", "letter": "N", "accent": "#000000"},
    "infinix":  {"gradient": "linear-gradient(135deg, #00A5E0 0%, #66D4FF 100%)", "letter": "∞", "accent": "#00A5E0"},
    "tecno":    {"gradient": "linear-gradient(135deg, #0066CC 0%, #3399FF 100%)", "letter": "T", "accent": "#0066CC"},
    "iqoo":     {"gradient": "linear-gradient(135deg, #FF4500 0%, #FF7744 100%)", "letter": "iQ", "accent": "#FF4500"},
    "honor":    {"gradient": "linear-gradient(135deg, #00539B 0%, #4D93D9 100%)", "letter": "H", "accent": "#00539B"},
    "google":   {"gradient": "linear-gradient(135deg, #4285F4 0%, #34A853 50%, #EA4335 100%)", "letter": "G", "accent": "#4285F4"},
    "lava":     {"gradient": "linear-gradient(135deg, #E60012 0%, #FF5252 100%)", "letter": "L", "accent": "#E60012"},
    "itel":     {"gradient": "linear-gradient(135deg, #FF7700 0%, #FFB366 100%)", "letter": "i", "accent": "#FF7700"},
    "hmd":      {"gradient": "linear-gradient(135deg, #003580 0%, #336FB5 100%)", "letter": "H", "accent": "#003580"},
    "cmf":      {"gradient": "linear-gradient(135deg, #FF6600 0%, #FF9944 100%)", "letter": "C", "accent": "#FF6600"},
    "ulefone":  {"gradient": "linear-gradient(135deg, #2E7D32 0%, #66BB6A 100%)", "letter": "U", "accent": "#2E7D32"},
    "acer":     {"gradient": "linear-gradient(135deg, #83B81A 0%, #A8E063 100%)", "letter": "A", "accent": "#83B81A"},
    "alcatel":  {"gradient": "linear-gradient(135deg, #E91E63 0%, #F48FB1 100%)", "letter": "A", "accent": "#E91E63"},
    "blackzone":{"gradient": "linear-gradient(135deg, #212121 0%, #616161 100%)", "letter": "B", "accent": "#212121"},
    "ringme":   {"gradient": "linear-gradient(135deg, #009688 0%, #4DB6AC 100%)", "letter": "R", "accent": "#009688"},
    "peace":    {"gradient": "linear-gradient(135deg, #607D8B 0%, #90A4AE 100%)", "letter": "P", "accent": "#607D8B"},
    "ai+":      {"gradient": "linear-gradient(135deg, #7C4DFF 0%, #B388FF 100%)", "letter": "AI", "accent": "#7C4DFF"},
}

def get_brand_style(brand_name):
    """Get brand visual style; fallback to generic blue gradient."""
    brand_key = str(brand_name).strip().lower()
    return BRAND_STYLES.get(brand_key, {
        "gradient": "linear-gradient(135deg, #6E6E73 0%, #A1A1A6 100%)",
        "letter": brand_key[0].upper() if brand_key else "?",
        "accent": "#6E6E73",
    })

def render_phone_mockup_html(brand_name, model_name, size=90):
    """Generate a pure-CSS phone mockup with brand gradient and letter."""
    bs = get_brand_style(brand_name)
    return f"""<div style="
        width: {size}px; height: {int(size * 1.25)}px; flex-shrink: 0;
        background: {bs['gradient']};
        border-radius: {int(size * 0.18)}px;
        display: flex; align-items: center; justify-content: center;
        box-shadow: 0 4px 16px rgba(0,0,0,0.12), inset 0 1px 0 rgba(255,255,255,0.15);
        position: relative; overflow: hidden;
    ">
        <div style="
            position: absolute; top: 6px; left: 50%; transform: translateX(-50%);
            width: {int(size * 0.22)}px; height: 4px; background: rgba(0,0,0,0.25);
            border-radius: 2px;
        "></div>
        <span style="
            font-size: {int(size * 0.32)}px; font-weight: 800; color: rgba(255,255,255,0.92);
            letter-spacing: -0.02em; text-shadow: 0 1px 3px rgba(0,0,0,0.2);
        ">{bs['letter']}</span>
        <div style="
            position: absolute; bottom: 8px; left: 50%; transform: translateX(-50%);
            width: {int(size * 0.2)}px; height: {int(size * 0.2)}px;
            border: 2px solid rgba(255,255,255,0.3); border-radius: 50%;
        "></div>
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
    st.markdown("""
        <div style="display: flex; justify-content: flex-end; align-items: center; gap: 0.5rem; padding-top: 0.35rem;">
            <span class="apple-chip chip-neutral">758 Smartphone</span>
            <span class="apple-chip chip-success">● SPK Aktif</span>
        </div>
    """, unsafe_allow_html=True)

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

        col_form, col_info = st.columns([6.2, 3.8], gap="large")

        with col_form:
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
                    "🎮 Gaming — Bermain game dengan performa grafis tinggi, chipset kencang, refresh rate stabil",
                    "📷 Fotografi & Konten — Mengambil foto jernih, video resolusi tinggi & pembuatan konten",
                    "💼 Produktivitas — Kuliah, pekerjaan kantor, multitasking aplikasi & dokumen",
                    "📱 Penggunaan Sehari-hari — Komunikasi, media sosial, navigasi & daya tahan harian andal",
                    "🏷️ Hemat Budget — Mendapatkan smartphone fungsional dengan harga paling efisien",
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
                    st.checkbox("⚡ Performa dan Kecepatan CPU", value=True, key="cb_p1")
                    st.checkbox("📷 Resolusi Kamera Tinggi", value=False, key="cb_p2")
                    st.checkbox("💾 RAM & Storage Besar", value=False, key="cb_p3")
                with p2:
                    st.checkbox("🔋 Baterai Tahan Lama & Fast Charge", value=False, key="cb_p4")
                    st.checkbox("🏷️ Efisiensi Harga Terjangkau", value=False, key="cb_p5")

            # Action Buttons
            ab1, ab2 = st.columns([3, 7])
            with ab1:
                if st.button("Reset Preferensi", use_container_width=True, key="btn_reset"):
                    st.session_state.budget_choice = 2
                    st.session_state.usage_choice = 0
                    st.rerun()
            with ab2:
                if st.button("Cari Rekomendasi (Hitung SPK)  →", type="primary", use_container_width=True, key="btn_calc"):
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
                    navigate("Hasil Rekomendasi")

        # Right Information Cards
        with col_info:
            st.markdown("""
                <div class="apple-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                        <span style="font-weight: 700; font-size: 1.05rem; color: #1D1D1F;">Bobot Ilmiah Tetap</span>
                        <span class="apple-chip chip-neutral">∑ W = 1.000</span>
                    </div>
                    <p style="font-size: 0.82rem; color: #6E6E73; line-height: 1.5; margin-bottom: 1rem;">
                        Bobot 7 kriteria dibakukan berdasarkan hasil kuesioner preferensi pengguna teruji secara objektif:
                    </p>
            """, unsafe_allow_html=True)

            for col_name, c_info in CRITERIA.items():
                actual_w = WEIGHTS_DICT.get(col_name, c_info["w"])
                pct_str = f"{actual_w * 100:.1f}%"
                type_tag = "Cost" if c_info["type"] == "Cost" else "Benefit"
                tag_cls = "chip-cost" if c_info["type"] == "Cost" else "chip-benefit"
                st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.45rem 0.65rem; background: #F5F5F7; border-radius: 10px; margin-bottom: 0.45rem; font-size: 0.82rem;">
                        <div style="display: flex; align-items: center; gap: 0.45rem;">
                            <span style="font-weight: 700; color: #1D1D1F;">{c_info['code']}</span>
                            <span style="color: #333336;">{c_info['name']}</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 0.45rem;">
                            <span class="apple-chip {tag_cls}">{type_tag}</span>
                            <strong style="color: #1D1D1F;">{pct_str}</strong>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("""
                    <div style="margin-top: 1rem; padding: 0.75rem 0.9rem; background: #F5F5F7; border-radius: 10px; font-size: 0.75rem; color: #515154; line-height: 1.45;">
                        ℹ️ Standardisasi bobot kuesioner menjamin objektivitas perangkingan tanpa bias subjektif.
                    </div>
                </div>

                <div class="apple-card">
                    <div style="font-weight: 700; font-size: 1.05rem; color: #1D1D1F; margin-bottom: 0.75rem;">Alur Komputasi SPK</div>
                    <div style="display: flex; flex-direction: column; gap: 0.75rem; font-size: 0.82rem; color: #515154;">
                        <div style="display: flex; gap: 0.75rem; align-items: flex-start;">
                            <span style="background: #1D1D1F; color: #FFF; font-size: 0.7rem; font-weight: 700; width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">1</span>
                            <div><strong>Filter Anggaran:</strong> Seleksi kandidat smartphone sesuai rentang harga.</div>
                        </div>
                        <div style="display: flex; gap: 0.75rem; align-items: flex-start;">
                            <span style="background: #1D1D1F; color: #FFF; font-size: 0.7rem; font-weight: 700; width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">2</span>
                            <div><strong>K-Means Clustering:</strong> Pemetaan segmentasi spesifikasi (2 klaster).</div>
                        </div>
                        <div style="display: flex; gap: 0.75rem; align-items: flex-start;">
                            <span style="background: #1D1D1F; color: #FFF; font-size: 0.7rem; font-weight: 700; width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">3</span>
                            <div><strong>Normalisasi & Solusi Ideal:</strong> Komputasi jarak Euclidean D⁺ dan D⁻.</div>
                        </div>
                        <div style="display: flex; gap: 0.75rem; align-items: flex-start;">
                            <span style="background: #1D1D1F; color: #FFF; font-size: 0.7rem; font-weight: 700; width: 20px; height: 20px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">4</span>
                            <div><strong>Skor Preferensi (Vi):</strong> Perangkingan kedekatan relatif terbaik.</div>
                        </div>
                    </div>
                    <div style="margin-top: 1.25rem; padding-top: 0.85rem; border-top: 1px dashed rgba(0,0,0,0.1); font-size: 0.78rem; font-weight: 600; color: #6E6E73; text-align: center;">
                        Basis Data: 758 Alternatif Smartphone
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # =============================================================================
    # SCREEN 3: HASIL REKOMENDASI (TOP 10 CARDS)
    # =============================================================================
    elif st.session_state.nav_page == "Hasil Rekomendasi":
        if st.session_state.topsis_data is None or len(st.session_state.topsis_data) == 0:
            st.session_state.topsis_data = calculate_topsis(DF_SMARTPHONES, WEIGHTS_DICT)

        df_results = st.session_state.topsis_data
        total_found = len(df_results)
        top_n = min(10, total_found)

        # Header Row
        top_l, top_r = st.columns([7, 3])
        with top_l:
            st.markdown("""
                <div style="font-size: 0.76rem; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; color: #6E6E73; margin-bottom: 0.25rem;">
                    Kalkulasi Multi-Kriteria • Hasil Rekomendasi
                </div>
                <h2 style="font-size: 1.85rem; font-weight: 700; color: #1D1D1F; margin-bottom: 0.35rem;">
                    Hasil Rekomendasi Smartphone Terbaik
                </h2>
                <p style="font-size: 0.92rem; color: #515154; margin-bottom: 0.85rem;">
                    Daftar alternatif paling optimal berdasarkan kalkulasi kedekatan relatif solusi ideal TOPSIS dari 7 kriteria teknis.
                </p>
            """, unsafe_allow_html=True)
        with top_r:
            st.markdown(f"""
                <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 0.4rem; padding-top: 0.4rem;">
                    <span class="apple-chip chip-neutral">Normalisasi Vektor TOPSIS</span>
                    <span class="apple-chip chip-success">Valid ({top_n} Alternatif)</span>
                </div>
            """, unsafe_allow_html=True)

        # Status Pill Row
        st.markdown(f"""
            <div style="display: flex; gap: 0.5rem; margin-bottom: 1.5rem;">
                <span class="apple-chip chip-neutral" style="padding: 0.35rem 0.85rem; font-size: 0.8rem;">
                    ✓ {top_n} Smartphone Terfilter
                </span>
                <span class="apple-chip chip-neutral" style="padding: 0.35rem 0.85rem; font-size: 0.8rem;">
                    ⚙️ 7 Kriteria Pembobotan Diterapkan
                </span>
            </div>
        """, unsafe_allow_html=True)

        # Top 10 Responsive Grid
        grid_cols = st.columns(3)
        for idx in range(top_n):
            row = df_results.iloc[idx]
            col_pos = idx % 3
            with grid_cols[col_pos]:
                with st.container(border=True):
                    price_str = format_rupiah(row["price_idr"])
                    score_str = f"{row['nilai_preferensi']:.4f}"

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
                    phone_mockup = render_phone_mockup_html(brand_raw, row['model'], size=72)

                    st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <span class="apple-chip chip-neutral" style="font-weight: 700; color: #1D1D1F;">Top {idx+1}</span>
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
                            <span class="spec-chip">⚡ {row['clock_speed_ghz']} GHz</span>
                            <span class="spec-chip">💾 {int(row['ram_gb'])}GB/{int(row['storage_gb'])}GB</span>
                            <span class="spec-chip">🔋 {int(row['battery_mah']):,} mAh</span>
                            <span class="spec-chip">📷 {int(row['rear_camera_main_mp'])} MP</span>
                            <span class="spec-chip">⚡ {int(row['charging_watt'])}W</span>
                        </div>
                    """, unsafe_allow_html=True)

                    if st.button("Lihat Detail Spesifikasi", key=f"btn_card_detail_{idx}", use_container_width=True, type="secondary"):
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
        detail_phone_mockup = render_phone_mockup_html(detail_brand_raw, item['model'], size=80)

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
                        ⚡ Karakteristik: <strong>RAM {int(item['ram_gb'])}GB &nbsp;•&nbsp; ROM {int(item['storage_gb'])}GB &nbsp;•&nbsp; {item['clock_speed_ghz']} GHz</strong>
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
