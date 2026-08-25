from __future__ import annotations

import io
import math
import re
import hashlib
import mimetypes
from dataclasses import dataclass
from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st
from supabase import create_client


# ============================================================
# APP CONFIG
# ============================================================

APP_TITLE = "Enterprise Dynamic Analytics"
MAX_FILE_SIZE_MB = 250
MAX_SLICER_VALUES = 100
MAX_BAR_CATEGORIES = 20
MAX_PIE_CATEGORIES = 10
MAX_PREVIEW_ROWS = 200
SUPABASE_BUCKET = "Datasets"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# PROFESSIONAL THEME
# No HTML is used for dashboard content. This prevents the
# raw <div> / <h1> / <p> problem shown in the screenshot.
# ============================================================

st.markdown(
    """
    <style>

    /* ================================================
       FONT IMPORT
       ================================================ */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* ================================================
       ROOT TOKENS
       ================================================ */
    :root {
        --navy:       #101a61;
        --navy-mid:   #1b2a8a;
        --navy-light: #2d42b8;
        --accent:     #4f6aff;
        --accent-2:   #00c6ae;
        --bg:         #f0f2f8;
        --surface:    #ffffff;
        --border:     #e0e4f0;
        --text-head:  #0e1540;
        --text-body:  #4a5378;
        --text-muted: #8891b0;
        --radius:     16px;
        --shadow-sm:  0 2px 8px rgba(16,26,97,.07);
        --shadow-md:  0 6px 24px rgba(16,26,97,.11);
        --shadow-lg:  0 16px 48px rgba(16,26,97,.16);
        --transition: 0.22s cubic-bezier(.4,0,.2,1);
    }

    /* ================================================
       GLOBAL
       ================================================ */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont,
                     'Segoe UI', sans-serif !important;
    }

    .stApp {
        background: var(--bg) !important;
    }

    .block-container {
        padding: 2rem 3rem 4rem !important;
        max-width: 1540px !important;
    }

    /* ================================================
       SIDEBAR — all text forced white
       ================================================ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1650 0%, #101a61 40%, #162280 100%) !important;
        border-right: 1px solid rgba(255,255,255,.10) !important;
    }

    /* accent strip */
    [data-testid="stSidebar"]::before {
        content: '';
        display: block;
        height: 4px;
        background: linear-gradient(90deg, var(--accent), var(--accent-2));
        border-radius: 0 0 4px 4px;
        margin-bottom: 4px;
    }

    /* blanket white + bigger base font on EVERY element */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 1rem !important;
    }

    /* headings */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 1.3rem !important;
    }

    /* widget label / filter name */
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] label p,
    [data-testid="stSidebar"] label span,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"],
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] span {
        color: #ffffff !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: .07em !important;
    }

    /* paragraph text */
    [data-testid="stSidebar"] p {
        color: #ffffff !important;
        font-size: 1rem !important;
    }

    /* caption */
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
        color: rgba(255,255,255,.70) !important;
        font-size: 0.9rem !important;
    }

    /* selectbox / multiselect container */
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: rgba(255,255,255,.10) !important;
        border: 1px solid rgba(255,255,255,.30) !important;
        border-radius: 10px !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] > div:focus-within {
        border-color: var(--accent-2) !important;
        background: rgba(255,255,255,.16) !important;
    }

    /* selected value text */
    [data-testid="stSidebar"] [data-baseweb="select"] span,
    [data-testid="stSidebar"] [data-baseweb="select"] div,
    [data-testid="stSidebar"] [data-baseweb="select"] input {
        color: #ffffff !important;
        background: transparent !important;
    }

    /* placeholder */
    [data-testid="stSidebar"] [data-baseweb="select"] input::placeholder {
        color: rgba(255,255,255,.55) !important;
    }

    /* dropdown arrow */
    [data-testid="stSidebar"] [data-baseweb="select"] svg {
        fill: rgba(255,255,255,.80) !important;
    }

    /* selected tag pills */
    [data-testid="stSidebar"] [data-baseweb="tag"] {
        background: var(--accent) !important;
        border-radius: 6px !important;
    }

    [data-testid="stSidebar"] [data-baseweb="tag"] span {
        color: #ffffff !important;
    }

    /* date / text inputs */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] input[type="text"] {
        background: rgba(255,255,255,.10) !important;
        border: 1px solid rgba(255,255,255,.30) !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        font-size: 1rem !important;
    }

    [data-testid="stSidebar"] input::placeholder {
        color: rgba(255,255,255,.50) !important;
    }

    /* file uploader */
    [data-testid="stSidebar"] [data-testid="stFileUploader"] {
        background: rgba(255,255,255,.07) !important;
        border: 1.5px dashed rgba(255,255,255,.45) !important;
        border-radius: 12px !important;
    }

    [data-testid="stSidebar"] [data-testid="stFileUploader"]:hover {
        border-color: var(--accent-2) !important;
        background: rgba(255,255,255,.13) !important;
    }

    /* ================================================
       HEADINGS — main content
       ================================================ */
    [data-testid="stAppViewContainer"] h1,
    [data-testid="stMarkdownContainer"] h1 {
        font-size: 2.6rem !important;
        font-weight: 900 !important;
        color: var(--text-head) !important;
        letter-spacing: -0.03em !important;
        line-height: 1.15 !important;
    }

    [data-testid="stAppViewContainer"] h2,
    [data-testid="stMarkdownContainer"] h2 {
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        color: var(--text-head) !important;
        letter-spacing: -0.02em !important;
    }

    [data-testid="stAppViewContainer"] h3,
    [data-testid="stMarkdownContainer"] h3 {
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        color: var(--text-head) !important;
        letter-spacing: -0.01em !important;
    }

    [data-testid="stAppViewContainer"] p,
    [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem !important;
        color: var(--text-body) !important;
        line-height: 1.75 !important;
        font-weight: 400 !important;
    }

    [data-testid="stAppViewContainer"] label,
    [data-testid="stMarkdownContainer"] label {
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        color: var(--text-body) !important;
        text-transform: uppercase !important;
        letter-spacing: .07em !important;
    }

    /* caption */
    [data-testid="stCaptionContainer"] {
        font-size: 0.9rem !important;
        color: var(--text-muted) !important;
        font-weight: 500 !important;
    }

    /* ================================================
       KPI CARDS
       ================================================ */
    [data-testid="stMetric"] {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 24px 22px !important;
        box-shadow: var(--shadow-sm) !important;
        transition: transform var(--transition),
                    box-shadow var(--transition) !important;
        position: relative !important;
        overflow: hidden !important;
    }

    /* coloured left-border accent */
    [data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 4px;
        background: linear-gradient(180deg, var(--accent), var(--accent-2));
        border-radius: 4px 0 0 4px;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-4px) !important;
        box-shadow: var(--shadow-md) !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.78rem !important;
        font-weight: 700 !important;
        color: var(--text-muted) !important;
        text-transform: uppercase !important;
        letter-spacing: .08em !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 800 !important;
        color: var(--text-head) !important;
        letter-spacing: -0.02em !important;
        line-height: 1.15 !important;
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        color: var(--text-muted) !important;
    }

    /* ================================================
       SECTION DIVIDER LABEL
       ================================================ */
    .section-hdr {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 2.4rem 0 1rem;
    }

    .section-hdr-icon {
        width: 36px; height: 36px;
        border-radius: 10px;
        background: linear-gradient(135deg, var(--navy), var(--accent));
        display: flex; align-items: center; justify-content: center;
        font-size: 1rem;
        flex-shrink: 0;
    }

    .section-hdr-text {
        font-size: 1.1rem;
        font-weight: 800;
        color: var(--text-head);
        letter-spacing: -0.01em;
    }

    .section-hdr-line {
        flex: 1;
        height: 1px;
        background: var(--border);
    }

    /* ================================================
       HERO BANNER (empty state)
       ================================================ */
    .hero-wrap {
        min-height: 72vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 3rem 1rem;
    }

    .hero-badge {
        display: inline-block;
        background: linear-gradient(135deg, var(--navy), var(--accent));
        color: #fff;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: .1em;
        text-transform: uppercase;
        padding: 5px 14px;
        border-radius: 999px;
        margin-bottom: 22px;
    }

    .hero-title {
        font-size: 3.4rem;
        font-weight: 900;
        color: var(--text-head);
        letter-spacing: -0.04em;
        line-height: 1.1;
        margin-bottom: 16px;
    }

    .hero-title span {
        background: linear-gradient(135deg, var(--accent), var(--accent-2));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-sub {
        font-size: 1.1rem;
        color: var(--text-body);
        max-width: 520px;
        line-height: 1.7;
        margin-bottom: 40px;
    }

    .hero-arrow {
        display: flex;
        align-items: center;
        gap: 8px;
        background: linear-gradient(135deg, var(--navy), var(--navy-mid));
        color: #fff;
        font-size: 0.9rem;
        font-weight: 600;
        padding: 14px 28px;
        border-radius: 999px;
        box-shadow: var(--shadow-md);
        animation: pulse 2.4s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% { box-shadow: 0 6px 24px rgba(16,26,97,.18); }
        50%       { box-shadow: 0 12px 40px rgba(16,26,97,.32); }
    }

    /* ================================================
       PAGE HEADER STRIP (after upload)
       ================================================ */
    .page-header {
        background: linear-gradient(135deg, var(--navy) 0%, var(--navy-mid) 55%, var(--navy-light) 100%);
        border-radius: 20px;
        padding: 28px 36px;
        margin-bottom: 28px;
        box-shadow: var(--shadow-lg);
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
    }

    .page-header-left h1 {
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        margin: 0 !important;
        letter-spacing: -0.02em !important;
    }

    .page-header-left p {
        font-size: 0.85rem !important;
        color: rgba(255,255,255,.7) !important;
        margin: 4px 0 0 !important;
    }

    .page-header-pill {
        background: rgba(255,255,255,.14);
        border: 1px solid rgba(255,255,255,.22);
        border-radius: 999px;
        padding: 8px 20px;
        font-size: 0.82rem;
        font-weight: 600;
        color: rgba(255,255,255,.9);
        white-space: nowrap;
    }

    /* ================================================
       SELECTBOX / INPUTS
       ================================================ */
    [data-baseweb="select"] > div {
        background: var(--surface) !important;
        border-color: var(--border) !important;
        border-radius: 10px !important;
        font-size: 0.9rem !important;
        color: var(--text-head) !important;
        transition: border-color var(--transition), box-shadow var(--transition) !important;
    }

    [data-baseweb="select"] > div:focus-within {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(79,106,255,.15) !important;
    }

    [data-baseweb="select"] span {
        color: var(--text-head) !important;
        font-size: 0.9rem !important;
    }

    /* ================================================
       EXPANDERS
       ================================================ */
    div[data-testid="stExpander"] {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        box-shadow: var(--shadow-sm) !important;
        transition: box-shadow var(--transition) !important;
    }

    div[data-testid="stExpander"]:hover {
        box-shadow: var(--shadow-md) !important;
    }

    div[data-testid="stExpander"] summary {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: var(--text-head) !important;
        padding: 14px 18px !important;
    }

    /* ================================================
       DOWNLOAD BUTTON
       ================================================ */
    [data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, var(--navy), var(--navy-mid)) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 28px !important;
        box-shadow: var(--shadow-sm) !important;
        transition: transform var(--transition), box-shadow var(--transition) !important;
    }

    [data-testid="stDownloadButton"] > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-md) !important;
    }

    /* ================================================
       INFO / WARNING / ERROR BANNERS
       ================================================ */
    [data-testid="stAlert"] {
        border-radius: 12px !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
    }

    /* ================================================
       DATA TABLE
       ================================================ */
    [data-testid="stDataFrame"] {
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid var(--border) !important;
    }

    /* ================================================
       RADIO BUTTONS
       ================================================ */
    [data-testid="stRadio"] label {
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        color: var(--text-body) !important;
    }

    /* ================================================
       PLOTLY CHART WRAPPER
       ================================================ */
    [data-testid="stPlotlyChart"] {
        background: var(--surface);
        border-radius: var(--radius);
        border: 1px solid var(--border);
        padding: 8px;
        box-shadow: var(--shadow-sm);
        transition: box-shadow var(--transition);
    }

    [data-testid="stPlotlyChart"]:hover {
        box-shadow: var(--shadow-md);
    }

    /* ================================================
       MISC
       ================================================ */
    /* hide Streamlit's default "Made with Streamlit" footer */
    footer { visibility: hidden !important; }

    /* ================================================
       SIDEBAR FILE UPLOADER — fix duplicate button
       and suppress keyboard_double_arrow icon text
       ================================================ */

    /* Hide the inner "Browse files" button (duplicate of the drop zone) */
    [data-testid="stSidebar"] [data-testid="stFileUploader"] button {
        display: none !important;
    }

    /* Hide the sidebar collapse arrow icon text that shows as
       "keyboard_double_arrow_left" when Material Icons font fails */
    [data-testid="stSidebarCollapseButton"] span {
        font-size: 0 !important;
    }
    [data-testid="stSidebarCollapseButton"] .material-symbols-rounded {
        font-size: 0 !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATA MODEL
# ============================================================

@dataclass(frozen=True)
class ColumnProfile:
    name: str
    dtype: str
    role: str
    unique_count: int
    non_null_count: int
    missing_pct: float
    numeric: bool
    date: bool
    identifier: bool
    category: bool
    geography: bool


# ============================================================
# HELPERS
# ============================================================

def normalize_name(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).lower())


def pretty_name(value: object) -> str:
    text = re.sub(r"[_\-]+", " ", str(value))
    text = re.sub(r"\s+", " ", text).strip()
    return text.title()


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def format_value(value: object) -> str:
    if value is None or pd.isna(value):
        return "N/A"

    value = float(value)

    if not math.isfinite(value):
        return "N/A"

    absolute = abs(value)

    if absolute >= 1_000_000_000:
        return f"{value / 1_000_000_000:,.2f}B"
    if absolute >= 1_000_000:
        return f"{value / 1_000_000:,.2f}M"
    if absolute >= 1_000:
        return f"{value / 1_000:,.1f}K"
    if value.is_integer():
        return f"{int(value):,}"

    return f"{value:,.2f}"


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    used = {}

    names = []

    for raw in result.columns:
        base = str(raw).strip()

        if not base:
            base = "Unnamed Column"

        count = used.get(base, 0)
        used[base] = count + 1

        names.append(
            base if count == 0 else f"{base} ({count + 1})"
        )

    result.columns = names

    for col in result.select_dtypes(
        include=["object", "string"]
    ).columns:
        result[col] = result[col].map(
            lambda x: x.strip() if isinstance(x, str) else x
        )

    return result


# ============================================================
# SUPABASE STORAGE
# ============================================================

def get_supabase_client():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"],
    )


def dataset_id_for(raw_bytes: bytes, filename: str) -> str:
    digest = hashlib.sha256(raw_bytes + filename.encode("utf-8")).hexdigest()
    return digest[:24]


def upload_dataset_to_supabase(raw_bytes: bytes, filename: str) -> str:
    dataset_id = dataset_id_for(raw_bytes, filename)
    storage_path = f"{dataset_id}/{filename}"
    client = get_supabase_client()
    content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    client.storage.from_(SUPABASE_BUCKET).upload(
        storage_path,
        raw_bytes,
        file_options={
            "upsert": "true",
            "content-type": content_type,
        },
    )
    return dataset_id


def download_dataset_from_supabase(dataset_id: str, filename: str) -> bytes:
    storage_path = f"{dataset_id}/{filename}"
    client = get_supabase_client()
    return client.storage.from_(SUPABASE_BUCKET).download(storage_path)


# ============================================================
# FILE LOADING
# ============================================================

@st.cache_data(show_spinner=False)
def load_dataset(raw_bytes: bytes, filename: str) -> pd.DataFrame:
    lower = filename.lower()

    if lower.endswith(".csv"):
        try:
            df = pd.read_csv(
                io.BytesIO(raw_bytes),
                low_memory=False,
            )
        except UnicodeDecodeError:
            df = pd.read_csv(
                io.BytesIO(raw_bytes),
                encoding="latin-1",
                low_memory=False,
            )

    elif lower.endswith((".xlsx", ".xls")):
        df = pd.read_excel(io.BytesIO(raw_bytes))

    else:
        raise ValueError(
            "Only CSV, XLSX and XLS files are supported."
        )

    df = df.dropna(axis=0, how="all")
    df = df.dropna(axis=1, how="all")
    df = clean_column_names(df)

    return df


# ============================================================
# TYPE DETECTION
# ============================================================

def looks_like_identifier(
    column: str,
    series: pd.Series,
) -> bool:
    name = normalize_name(column)

    exact = {
        "id",
        "identifier",
        "index",
        "asin",
        "sku",
        "zipcode",
        "postalcode",
        "pincode",
    }

    if name in exact:
        return True

    compound = (
        "orderid",
        "employeeid",
        "customerid",
        "userid",
        "studentid",
        "transactionid",
        "productid",
        "accountid",
        "recordid",
        "postalcode",
        "zipcode",
        "pincode",
        "asin",
        "sku",
    )

    if any(name == term or name.startswith(term) for term in compound):
        return True

    if pd.api.types.is_numeric_dtype(series):
        values = series.dropna()

        if len(values) >= 30:
            uniqueness = values.nunique() / len(values)

            if uniqueness >= .995:
                return True

    return False


def looks_like_date_name(column: str) -> bool:
    name = normalize_name(column)

    terms = (
        "date",
        "datetime",
        "timestamp",
        "orderdate",
        "transactiondate",
        "eventdate",
        "createdat",
        "updatedat",
    )

    return any(term in name for term in terms)


def parse_date_candidate(
    series: pd.Series,
) -> Optional[pd.Series]:
    if pd.api.types.is_datetime64_any_dtype(series):
        return series

    if not (
        pd.api.types.is_object_dtype(series)
        or pd.api.types.is_string_dtype(series)
    ):
        return None

    sample = (
        series.dropna()
        .astype(str)
        .head(500)
    )

    if sample.empty:
        return None

    parsed_sample = pd.to_datetime(
        sample,
        errors="coerce",
        format="mixed",
    )

    if parsed_sample.notna().mean() < .85:
        return None

    parsed = pd.to_datetime(
        series,
        errors="coerce",
        format="mixed",
    )

    if parsed.notna().mean() < .85:
        return None

    return parsed


def looks_like_geography(column: str) -> bool:
    name = normalize_name(column)

    terms = (
        "country",
        "state",
        "province",
        "city",
        "region",
        "continent",
        "district",
        "county",
        "location",
    )

    return any(term in name for term in terms)


def profile_dataset(df: pd.DataFrame) -> list[ColumnProfile]:
    profiles = []

    for col in df.columns:
        series = df[col]

        is_numeric = pd.api.types.is_numeric_dtype(series)
        is_date = pd.api.types.is_datetime64_any_dtype(series)
        identifier = looks_like_identifier(col, series)

        unique_count = int(series.nunique(dropna=True))
        non_null_count = int(series.notna().sum())
        missing_pct = float(series.isna().mean() * 100)

        if is_date:
            role = "Date"
        elif identifier:
            role = "Identifier"
        elif is_numeric:
            role = "Measure"
        elif 2 <= unique_count <= 30:
            role = "Category"
        else:
            role = "Text"

        geography = looks_like_geography(col)

        if geography and role in {"Category", "Text"}:
            role = "Geography"

        profiles.append(
            ColumnProfile(
                name=col,
                dtype=str(series.dtype),
                role=role,
                unique_count=unique_count,
                non_null_count=non_null_count,
                missing_pct=missing_pct,
                numeric=is_numeric,
                date=is_date,
                identifier=identifier,
                category=role in {"Category", "Geography"},
                geography=geography,
            )
        )

    return profiles


def infer_dates(
    df: pd.DataFrame,
    profiles: list[ColumnProfile],
) -> tuple[pd.DataFrame, list[ColumnProfile]]:
    result = df.copy()
    updated = []

    for p in profiles:
        current = p

        if not p.date and looks_like_date_name(p.name):
            parsed = parse_date_candidate(result[p.name])

            if parsed is not None:
                result[p.name] = parsed

                current = ColumnProfile(
                    name=p.name,
                    dtype=str(parsed.dtype),
                    role="Date",
                    unique_count=p.unique_count,
                    non_null_count=p.non_null_count,
                    missing_pct=p.missing_pct,
                    numeric=False,
                    date=True,
                    identifier=False,
                    category=False,
                    geography=False,
                )

        updated.append(current)

    return result, updated


# ============================================================
# SEMANTIC COLUMN SELECTION
# ============================================================

def primary_measure(
    profiles: list[ColumnProfile],
) -> Optional[str]:
    measures = [
        p.name
        for p in profiles
        if p.role == "Measure"
    ]

    if not measures:
        return None

    preferred = (
        "revenue",
        "sales",
        "amount",
        "profit",
        "income",
        "salary",
        "value",
        "price",
        "cost",
        "quantity",
        "qty",
        "score",
        "hours",
    )

    for term in preferred:
        for col in measures:
            if term in normalize_name(col):
                return col

    return measures[0]


def primary_identifier(
    profiles: list[ColumnProfile],
) -> Optional[str]:
    identifiers = [
        p.name
        for p in profiles
        if p.role == "Identifier"
    ]

    if not identifiers:
        return None

    preferred = (
        "orderid",
        "transactionid",
        "employeeid",
        "customerid",
        "productid",
        "userid",
    )

    for term in preferred:
        for col in identifiers:
            if term in normalize_name(col):
                return col

    return identifiers[0]


# ============================================================
# ACCURATE AGGREGATION
# ============================================================

def aggregate(
    series: pd.Series,
    operation: str,
) -> float:
    if operation == "Count Rows":
        return float(len(series))

    if operation == "Count Non-Null":
        return float(series.notna().sum())

    if operation == "Distinct Count":
        return float(series.nunique(dropna=True))

    values = numeric(series).dropna()

    if values.empty:
        return float("nan")

    if operation == "Sum":
        return float(values.sum())
    if operation == "Average":
        return float(values.mean())
    if operation == "Minimum":
        return float(values.min())
    if operation == "Maximum":
        return float(values.max())
    if operation == "Median":
        return float(values.median())

    raise ValueError(f"Unsupported aggregation: {operation}")


# ============================================================
# SLICERS
# ============================================================

def apply_slicers(
    df: pd.DataFrame,
    profiles: list[ColumnProfile],
) -> pd.DataFrame:
    result = df.copy()

    st.sidebar.header("Slicers")

    category_profiles = [
        p for p in profiles
        if p.role in {"Category", "Geography"}
        and 1 < p.unique_count <= MAX_SLICER_VALUES
    ]

    for p in category_profiles:
        values = (
            result[p.name]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        if not values:
            continue

        selected = st.sidebar.multiselect(
            pretty_name(p.name),
            sorted(values),
            key=f"slicer_{p.name}",
            placeholder=f"All {pretty_name(p.name)}",
        )

        if selected:
            result = result[
                result[p.name]
                .astype(str)
                .isin(selected)
            ]

    date_profiles = [
        p for p in profiles if p.date
    ]

    for p in date_profiles:
        dates = pd.to_datetime(
            result[p.name],
            errors="coerce",
        ).dropna()

        if dates.empty:
            continue

        minimum = dates.min().date()
        maximum = dates.max().date()

        selected = st.sidebar.date_input(
            pretty_name(p.name),
            value=(minimum, maximum),
            min_value=minimum,
            max_value=maximum,
            key=f"date_{p.name}",
        )

        if isinstance(selected, (tuple, list)) and len(selected) == 2:
            start, end = selected

            result = result[
                pd.to_datetime(
                    result[p.name],
                    errors="coerce",
                ).dt.date.between(start, end)
            ]

    return result


# ============================================================
# KPI ENGINE
# ============================================================

def build_kpis(
    df: pd.DataFrame,
    profiles: list[ColumnProfile],
) -> list[tuple[str, str]]:
    measure = primary_measure(profiles)
    identifier = primary_identifier(profiles)

    result = []

    if measure:
        result.append(
            (
                f"Total {pretty_name(measure)}",
                format_value(
                    aggregate(
                        df[measure],
                        "Sum",
                    )
                ),
            )
        )

        result.append(
            (
                f"Average {pretty_name(measure)}",
                format_value(
                    aggregate(
                        df[measure],
                        "Average",
                    )
                ),
            )
        )
    else:
        result.append(
            (
                "Total Records",
                format_value(len(df)),
            )
        )

    if identifier:
        result.append(
            (
                f"Unique {pretty_name(identifier)}",
                format_value(
                    aggregate(
                        df[identifier],
                        "Distinct Count",
                    )
                ),
            )
        )
    else:
        result.append(
            (
                "Total Records",
                format_value(len(df)),
            )
        )

    result.append(
        (
            "Filtered Records",
            format_value(len(df)),
        )
    )

    return result[:4]


# ============================================================
# CHART ENGINE
# ============================================================

def grouped_data(
    df: pd.DataFrame,
    dimension: str,
    measure: str,
    operation: str,
) -> pd.DataFrame:
    work = df[[dimension, measure]].copy()

    work[measure] = numeric(work[measure])
    work = work.dropna(subset=[dimension])

    if operation == "Count Rows":
        result = (
            work.groupby(dimension, dropna=False)
            .size()
            .reset_index(name="Value")
        )

    elif operation == "Count Non-Null":
        result = (
            work.groupby(dimension, dropna=False)[measure]
            .count()
            .reset_index(name="Value")
        )

    elif operation == "Distinct Count":
        result = (
            work.groupby(dimension, dropna=False)[measure]
            .nunique()
            .reset_index(name="Value")
        )

    elif operation == "Sum":
        result = (
            work.groupby(dimension, dropna=False)[measure]
            .sum()
            .reset_index(name="Value")
        )

    elif operation == "Average":
        result = (
            work.groupby(dimension, dropna=False)[measure]
            .mean()
            .reset_index(name="Value")
        )

    elif operation == "Minimum":
        result = (
            work.groupby(dimension, dropna=False)[measure]
            .min()
            .reset_index(name="Value")
        )

    elif operation == "Maximum":
        result = (
            work.groupby(dimension, dropna=False)[measure]
            .max()
            .reset_index(name="Value")
        )

    elif operation == "Median":
        result = (
            work.groupby(dimension, dropna=False)[measure]
            .median()
            .reset_index(name="Value")
        )

    else:
        raise ValueError(f"Unsupported aggregation: {operation}")

    result["Dimension"] = result[dimension].astype(str)

    return result[["Dimension", "Value"]]


def style_chart(fig):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=24, r=24, t=56, b=36),
        height=400,
        font=dict(
            family="Inter, Arial, sans-serif",
            size=12,
            color="#4a5378",
        ),
        title=dict(
            font=dict(
                family="Inter, Arial, sans-serif",
                size=15,
                color="#0e1540",
            ),
            pad=dict(t=4, l=4),
        ),
        legend=dict(
            bgcolor="rgba(255,255,255,0)",
            borderwidth=0,
            font=dict(size=11, color="#4a5378"),
        ),
        colorway=[
            "#4f6aff", "#00c6ae", "#ff6b6b", "#ffc94d",
            "#a78bfa", "#34d399", "#f472b6", "#60a5fa",
        ],
    )

    fig.update_xaxes(
        showgrid=False,
        linecolor="#dde1ee",
        linewidth=1.5,
        tickfont=dict(size=11, color="#8891b0"),
        title_font=dict(size=12, color="#4a5378"),
    )

    fig.update_yaxes(
        gridcolor="#edf0f8",
        gridwidth=1,
        zeroline=False,
        tickfont=dict(size=11, color="#8891b0"),
        title_font=dict(size=12, color="#4a5378"),
    )

    return fig


# ============================================================
# AUTOMATIC OVERVIEW
# ============================================================

def automatic_overview(
    df: pd.DataFrame,
    profiles: list[ColumnProfile],
):
    measure = primary_measure(profiles)

    if not measure or df.empty:
        st.info(
            "No numeric measure is available for automatic charts."
        )
        return

    dimensions = [
        p.name
        for p in profiles
        if p.role in {"Category", "Geography"}
        and 1 < p.unique_count <= MAX_BAR_CATEGORIES * 5
    ]

    dates = [
        p.name for p in profiles if p.date
    ]

    left, right = st.columns(2)

    with left:
        if dates:
            date_col = dates[0]

            work = df[[date_col, measure]].copy()
            work[measure] = numeric(work[measure])
            work = work.dropna()

            if not work.empty:
                trend = (
                    work.groupby(date_col, as_index=False)[measure]
                    .sum()
                    .sort_values(date_col)
                )

                fig = px.line(
                    trend,
                    x=date_col,
                    y=measure,
                    markers=True,
                    title=f"{pretty_name(measure)} Trend",
                )

                st.plotly_chart(
                    style_chart(fig),
                    use_container_width=True,
                )

        elif dimensions:
            data = grouped_data(
                df,
                dimensions[0],
                measure,
                "Sum",
            ).nlargest(MAX_BAR_CATEGORIES, "Value")

            fig = px.bar(
                data,
                x="Dimension",
                y="Value",
                title=(
                    f"{pretty_name(measure)} by "
                    f"{pretty_name(dimensions[0])}"
                ),
            )

            st.plotly_chart(
                style_chart(fig),
                use_container_width=True,
            )

    with right:
        if dimensions:
            data = grouped_data(
                df,
                dimensions[0],
                measure,
                "Sum",
            ).nlargest(MAX_PIE_CATEGORIES, "Value")

            if len(data) >= 2:
                fig = px.pie(
                    data,
                    names="Dimension",
                    values="Value",
                    hole=.48,
                    title=(
                        f"{pretty_name(measure)} Distribution"
                    ),
                )

                st.plotly_chart(
                    style_chart(fig),
                    use_container_width=True,
                )


# ============================================================
# VISUAL BUILDER
# ============================================================

def visual_builder(
    df: pd.DataFrame,
    profiles: list[ColumnProfile],
):
    st.subheader("Visual Analysis")

    dimensions = [
        p.name
        for p in profiles
        if p.role in {"Category", "Geography"}
    ]

    dates = [
        p.name for p in profiles if p.date
    ]

    measures = [
        p.name for p in profiles if p.role == "Measure"
    ]

    all_dimensions = dates + dimensions

    if not all_dimensions or not measures:
        st.info(
            "This dataset does not contain enough "
            "dimension and numeric columns for chart building."
        )
        return

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        chart_type = st.selectbox(
            "Chart Type",
            ["None", "Bar", "Pie", "Line", "Area", "Scatter"],
        )

    with c2:
        dimension = st.selectbox(
            "Dimension",
            all_dimensions,
            format_func=pretty_name,
        )

    with c3:
        default_measure = primary_measure(profiles)

        measure = st.selectbox(
            "Measure",
            measures,
            index=(
                measures.index(default_measure)
                if default_measure in measures
                else 0
            ),
            format_func=pretty_name,
        )

    with c4:
        operation = st.selectbox(
            "Calculation",
            [
                "Sum",
                "Average",
                "Minimum",
                "Maximum",
                "Median",
                "Count Rows",
                "Count Non-Null",
                "Distinct Count",
            ],
        )

    if chart_type == "None":
        st.info("Select a chart type to render a visualisation.")
        return

    if chart_type == "Scatter":
        other = [
            m for m in measures if m != measure
        ]

        if not other:
            st.warning(
                "Scatter plots require at least two numeric columns."
            )
            return

        y_measure = st.selectbox(
            "Second Measure",
            other,
            format_func=pretty_name,
        )

        data = df[[measure, y_measure]].copy()
        data[measure] = numeric(data[measure])
        data[y_measure] = numeric(data[y_measure])
        data = data.dropna()

        if data.empty:
            st.warning("No numeric observations are available.")
            return

        fig = px.scatter(
            data,
            x=measure,
            y=y_measure,
            title=(
                f"{pretty_name(y_measure)} vs "
                f"{pretty_name(measure)}"
            ),
        )

        st.plotly_chart(
            style_chart(fig),
            use_container_width=True,
        )
        return

    if chart_type in {"Line", "Area"} and dimension not in dates:
        st.warning(
            f"{chart_type} charts require a date/time dimension."
        )
        return

    if chart_type in {"Bar", "Pie"}:
        data = grouped_data(
            df,
            dimension,
            measure,
            operation,
        )

        if data.empty:
            st.warning("No data is available for this chart.")
            return

        if chart_type == "Bar":
            data = data.nlargest(
                MAX_BAR_CATEGORIES,
                "Value",
            )

            fig = px.bar(
                data,
                x="Dimension",
                y="Value",
                title=(
                    f"{operation} of {pretty_name(measure)} "
                    f"by {pretty_name(dimension)}"
                ),
            )

        else:
            data = data.nlargest(
                MAX_PIE_CATEGORIES,
                "Value",
            )

            if len(data) < 2:
                st.warning(
                    "A pie chart requires at least two categories."
                )
                return

            fig = px.pie(
                data,
                names="Dimension",
                values="Value",
                hole=.45,
                title=(
                    f"{operation} of {pretty_name(measure)} "
                    f"by {pretty_name(dimension)}"
                ),
            )

    else:
        work = df[[dimension, measure]].copy()
        work[measure] = numeric(work[measure])
        work = work.dropna()

        if work.empty:
            st.warning("No data is available for this chart.")
            return

        grouped = (
            work.groupby(dimension, as_index=False)[measure]
            .agg(
                {
                    "Sum": "sum",
                    "Average": "mean",
                    "Minimum": "min",
                    "Maximum": "max",
                    "Median": "median",
                }.get(operation, "sum")
            )
            .sort_values(dimension)
        )

        if chart_type == "Line":
            fig = px.line(
                grouped,
                x=dimension,
                y=measure,
                markers=True,
                title=(
                    f"{operation} of {pretty_name(measure)} "
                    "Over Time"
                ),
            )
        else:
            fig = px.area(
                grouped,
                x=dimension,
                y=measure,
                title=(
                    f"{operation} of {pretty_name(measure)} "
                    "Over Time"
                ),
            )

    st.plotly_chart(
        style_chart(fig),
        use_container_width=True,
    )


# ============================================================
# DATA QUALITY
# ============================================================

def data_quality(
    df: pd.DataFrame,
    profiles: list[ColumnProfile],
):
    with st.expander("Dataset Information"):
        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Rows", f"{len(df):,}")
        c2.metric("Columns", f"{len(df.columns):,}")
        c3.metric(
            "Missing Cells",
            f"{int(df.isna().sum().sum()):,}",
        )
        c4.metric(
            "Numeric Columns",
            f"{sum(p.numeric for p in profiles):,}",
        )

        structure = pd.DataFrame(
            [
                {
                    "Column": p.name,
                    "Data Type": p.dtype,
                    "Detected Role": p.role,
                    "Unique": p.unique_count,
                    "Missing %": round(p.missing_pct, 2),
                }
                for p in profiles
            ]
        )

        st.dataframe(
            structure,
            use_container_width=True,
            hide_index=True,
        )

    with st.expander("Data Preview"):
        st.dataframe(
            df.head(MAX_PREVIEW_ROWS),
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Enterprise Analytics")
st.sidebar.caption(
    "Generic data intelligence platform"
)

uploaded = st.sidebar.file_uploader(
    "Upload Dataset",
    type=["csv", "xlsx", "xls"],
    help="Upload one structured CSV or Excel dataset.",
)


# ============================================================
# LOAD OR RESTORE DATASET
# ============================================================

shared_dataset_id = st.query_params.get("dataset")
shared_filename = st.query_params.get("filename")

raw_bytes = None
active_filename = None

if uploaded is not None:
    active_filename = uploaded.name
    raw_bytes = uploaded.getvalue()

    if len(raw_bytes) > MAX_FILE_SIZE_MB * 1024 * 1024:
        st.error(
            f"The uploaded file exceeds the "
            f"{MAX_FILE_SIZE_MB} MB limit."
        )
        st.stop()

    current_id = dataset_id_for(raw_bytes, active_filename)
    if st.session_state.get("uploaded_dataset_id") != current_id:
        try:
            upload_dataset_to_supabase(raw_bytes, active_filename)
            st.session_state["uploaded_dataset_id"] = current_id
            st.query_params["dataset"] = current_id
            st.query_params["filename"] = active_filename
            st.success("Dataset saved. You can now share this URL.")
        except Exception as exc:
            st.error(f"Dataset could not be saved to Supabase: {exc}")
            st.stop()

elif shared_dataset_id and shared_filename:
    active_filename = shared_filename
    try:
        raw_bytes = download_dataset_from_supabase(
            shared_dataset_id,
            shared_filename,
        )
        st.sidebar.success("Shared dataset loaded.")
    except Exception as exc:
        st.error(
            "The shared dataset could not be loaded from Supabase. "
            f"Details: {exc}"
        )
        st.stop()

else:
    st.markdown(
        """
        <div class="hero-wrap">
            <div class="hero-badge">✦ Enterprise Data Intelligence</div>
            <div class="hero-title">
                Analyse Any Dataset<br><span>Instantly</span>
            </div>
            <div class="hero-sub">
                Upload a CSV or Excel file and get automatic KPIs,
                interactive filters, trend charts and data-quality
                insights — no configuration required.
            </div>
            <div class="hero-arrow">← Upload your dataset in the sidebar</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


# ============================================================
# LOAD DATA
# ============================================================

try:
    df = load_dataset(
        raw_bytes,
        active_filename,
    )
except Exception as exc:
    st.error(f"Dataset could not be loaded: {exc}")
    st.stop()


# ============================================================
# PROFILE DATA
# ============================================================

try:
    profiles = profile_dataset(df)
    df, profiles = infer_dates(df, profiles)
except Exception as exc:
    st.error(f"Dataset profiling failed: {exc}")
    st.stop()


# ============================================================
# SIDEBAR SLICERS
# ============================================================

filtered = apply_slicers(
    df,
    profiles,
)


# ============================================================
# HEADER
# Native Streamlit title/caption prevents the raw HTML problem.
# ============================================================

st.markdown(
    f"""
    <div class="page-header">
        <div class="page-header-left">
            <h1>📊 Enterprise Dynamic Analytics</h1>
            <p>{active_filename} &nbsp;·&nbsp;
               {len(filtered):,} filtered rows &nbsp;/&nbsp;
               {len(df):,} total &nbsp;·&nbsp;
               {len(df.columns):,} columns</p>
        </div>
        <div class="page-header-pill">Live Dashboard</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# KPIs
# Native st.metric prevents raw HTML such as:
# <div class="kpi-label">...</div>
# ============================================================

st.markdown(
    '<div class="section-hdr">'
    '<div class="section-hdr-icon">📈</div>'
    '<div class="section-hdr-text">Key Performance Indicators</div>'
    '<div class="section-hdr-line"></div>'
    '</div>',
    unsafe_allow_html=True,
)

kpis = build_kpis(
    filtered,
    profiles,
)

kpi_columns = st.columns(4)

for column, (label, value) in zip(
    kpi_columns,
    kpis,
):
    with column:
        st.metric(
            label=label,
            value=value,
        )


# ============================================================
# AUTOMATIC OVERVIEW
# ============================================================

st.markdown(
    '<div class="section-hdr">'
    '<div class="section-hdr-icon">🔭</div>'
    '<div class="section-hdr-text">Executive Overview</div>'
    '<div class="section-hdr-line"></div>'
    '</div>',
    unsafe_allow_html=True,
)

if filtered.empty:
    st.warning(
        "The active slicers returned no records."
    )
else:
    automatic_overview(
        filtered,
        profiles,
    )


# ============================================================
# VISUAL BUILDER
# ============================================================

visual_builder(
    filtered,
    profiles,
)


# ============================================================
# DATA QUALITY
# ============================================================

data_quality(
    filtered,
    profiles,
)


# ============================================================
# DOWNLOAD
# ============================================================

st.markdown(
    '<div class="section-hdr">'
    '<div class="section-hdr-icon">⬇️</div>'
    '<div class="section-hdr-text">Export</div>'
    '<div class="section-hdr-line"></div>'
    '</div>',
    unsafe_allow_html=True,
)

st.download_button(
    "⬇️  Download Filtered Dataset as CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_dataset.csv",
    mime="text/csv",
)


st.caption(
    "All displayed calculations are generated from the uploaded "
    "dataset after the active slicers are applied."
)
