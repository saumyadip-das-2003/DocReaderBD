import io
import json
import os
import traceback
import zipfile
from datetime import datetime
from pathlib import Path

import fitz
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from PIL import Image

from docreaderbd.database import (
    delete_document,
    get_all_birth_certificates,
    get_all_documents,
    get_all_nid_cards,
    get_document_by_id,
    init_db,
    save_birth_certificate_record,
    save_document,
    save_nid_record,
)
from docreaderbd.extractors.base import full_text


st.set_page_config(
    page_title="DocReader BD",
    page_icon="🇧🇩",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv()


st.markdown(
    """
    <style>
    :root {
        --app-bg: #F4F7FB;
        --surface: #FFFFFF;
        --surface-soft: #F8FAFC;
        --sidebar: #0F2742;
        --sidebar-2: #143A5A;
        --primary: #1D4E89;
        --primary-dark: #12385F;
        --green: #208A5D;
        --red: #C0392B;
        --orange: #D97706;
        --purple: #6D3FB3;
        --teal: #0F766E;
        --border: #D8E0EA;
        --text: #17202A;
        --muted: #5B6776;
    }

    html, body, .stApp, [data-testid="stAppViewContainer"] {
        background: var(--app-bg) !important;
        color: var(--text) !important;
        font-family: "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    .main .block-container,
    [data-testid="stAppViewContainer"] .block-container {
        padding-top: 2.3rem;
        padding-bottom: 3rem;
        max-width: 1280px;
    }

    header[data-testid="stHeader"] {
        background: transparent !important;
        box-shadow: none !important;
        height: 0 !important;
        min-height: 0 !important;
        pointer-events: none !important;
    }

    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    #MainMenu,
    footer {
        visibility: hidden !important;
    }

    [data-testid="stAppViewContainer"] {
        padding-top: 0 !important;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--sidebar), var(--sidebar-2)) !important;
        min-width: 375px !important;
        width: 375px !important;
        max-width: 375px !important;
        transform: translateX(0) !important;
        visibility: visible !important;
        display: block !important;
        opacity: 1 !important;
    }

    [data-testid="collapsedControl"],
    button[kind="header"],
    button[data-testid="stBaseButton-header"] {
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1.1rem !important;
        overflow-y: auto !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
        padding-top: 0.4rem !important;
        padding-bottom: 0.8rem !important;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div {
        color: #FFFFFF;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.22) !important;
        border-radius: 12px;
        padding: 0.65rem 0.8rem;
        margin-bottom: 0.45rem;
        transition: all 160ms ease;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: rgba(255, 255, 255, 0.18) !important;
        transform: translateX(2px);
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: #FFFFFF !important;
        border-color: #FFFFFF !important;
        box-shadow: 0 8px 18px rgba(0, 0, 0, 0.18);
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) * {
        color: var(--primary-dark) !important;
        font-weight: 800 !important;
    }

    section[data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.4) !important;
    }

    section[data-testid="stSidebar"] [data-baseweb="select"] * {
        color: var(--text) !important;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin: 0.15rem 0 1rem;
    }

    .brand-logo {
        background: #FFFFFF;
        color: var(--primary-dark);
        border-radius: 12px;
        padding: 0.55rem 0.7rem;
        font-weight: 900;
        font-size: 1.35rem;
        letter-spacing: 0.02em;
    }

    .brand-title {
        font-size: 1.45rem;
        font-weight: 900;
        line-height: 1.1;
    }

    .brand-subtitle {
        font-size: 0.82rem;
        color: rgba(255,255,255,0.78) !important;
    }

    .sidebar-rule {
        height: 1px;
        background: rgba(255,255,255,0.22);
        margin: 0.75rem 0;
    }

    .page-title {
        color: var(--text);
        font-size: 2.15rem;
        font-weight: 900;
        margin-bottom: 0.15rem;
    }

    .page-subtitle {
        color: var(--muted);
        font-size: 1.05rem;
        margin-bottom: 1.35rem;
    }

    .panel, .placeholder, .file-meta, .metric-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 14px;
        box-shadow: 0 10px 26px rgba(20, 42, 68, 0.07);
    }

    .placeholder {
        border: 2px dashed var(--primary);
        padding: 3rem 2rem;
        text-align: center;
        background: var(--surface);
        color: var(--text);
    }

    .file-meta {
        padding: 0.9rem 1rem;
        margin-top: 0.75rem;
        color: var(--text);
    }

    div[data-testid="stFileUploader"] section {
        border: 2px dashed var(--primary);
        border-radius: 14px;
        background: var(--surface) !important;
        transition: border-color 160ms ease, box-shadow 160ms ease;
    }

    div[data-testid="stFileUploader"] section *,
    div[data-testid="stFileUploader"] label,
    div[data-testid="stFileUploader"] small {
        color: var(--text) !important;
    }

    div[data-testid="stFileUploader"] section:hover {
        border-color: var(--green);
        box-shadow: 0 8px 22px rgba(27, 79, 114, 0.12);
    }

    .badge {
        display: inline-flex;
        align-items: center;
        border-radius: 999px;
        color: #FFFFFF;
        font-weight: 800;
        padding: 0.4rem 0.75rem;
        margin: 0 0.45rem 0.75rem 0;
        font-size: 0.88rem;
    }

    .badge.navy { background: var(--primary); }
    .badge.green { background: var(--green); }
    .badge.orange { background: var(--orange); }
    .badge.gray { background: #6C757D; }
    .badge.teal { background: var(--teal); }
    .badge.purple { background: var(--purple); }

    .metric-row {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.85rem;
        margin: 1rem 0;
    }

    .metric-card {
        padding: 1rem;
        text-align: center;
    }

    .metric-value {
        color: var(--primary);
        font-size: 1.55rem;
        font-weight: 900;
    }

    .metric-label {
        color: var(--muted);
        font-size: 0.82rem;
        font-weight: 700;
    }

    .legend {
        color: var(--muted);
        font-size: 0.9rem;
        margin-top: 0.4rem;
    }

    .legend .bn { color: #00C896; font-weight: 800; }
    .legend .en { color: #4A90D9; font-weight: 800; }

    .stButton > button, .stDownloadButton > button {
        background: #FFFFFF !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px;
        font-weight: 800;
        transition: all 160ms ease;
    }

    .stButton > button *, .stDownloadButton > button * {
        color: inherit !important;
    }

    .stButton > button:hover, .stDownloadButton > button:hover {
        border-color: var(--primary);
        box-shadow: 0 8px 20px rgba(27, 79, 114, 0.12);
        transform: translateY(-1px);
    }

    div[data-testid="stDownloadButton"] button {
        background: var(--green) !important;
        color: #FFFFFF !important;
        border-color: var(--green) !important;
    }

    button[kind="primary"] {
        background: var(--primary) !important;
        color: #FFFFFF !important;
        border-color: var(--primary) !important;
    }

    textarea,
    input,
    [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea {
        background: #FFFFFF !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        color: var(--text) !important;
        -webkit-text-fill-color: var(--text) !important;
    }

    div[data-testid="stTextArea"] textarea,
    div[data-testid="stTextArea"] textarea:disabled {
        background: #FFFFFF !important;
        color: var(--text) !important;
        -webkit-text-fill-color: var(--text) !important;
        opacity: 1 !important;
    }

    [data-testid="stMarkdownContainer"],
    [data-testid="stMarkdownContainer"] *,
    [data-testid="stCaptionContainer"],
    [data-testid="stMetric"],
    .stJson,
    pre,
    code {
        color: var(--text) !important;
    }

    [data-testid="stDataFrame"] *,
    [data-testid="stTable"] * {
        color: var(--text) !important;
    }

    [data-testid="stAlert"] * {
        color: var(--text) !important;
    }

    hr {
        border-color: var(--border) !important;
    }

    /* Final contrast pass: keep sidebar readable while forcing main content light/professional. */
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] *,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .brand-title,
    section[data-testid="stSidebar"] .brand-subtitle {
        color: #F8FAFC !important;
        -webkit-text-fill-color: #F8FAFC !important;
    }

    section[data-testid="stSidebar"] .brand-logo {
        color: var(--primary-dark) !important;
        -webkit-text-fill-color: var(--primary-dark) !important;
        background: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.9);
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked),
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) * {
        color: var(--primary-dark) !important;
        -webkit-text-fill-color: var(--primary-dark) !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:not(:has(input:checked)),
    section[data-testid="stSidebar"] div[role="radiogroup"] label:not(:has(input:checked)) * {
        color: #F8FAFC !important;
        -webkit-text-fill-color: #F8FAFC !important;
    }

    section[data-testid="stSidebar"] [data-baseweb="select"] > div,
    section[data-testid="stSidebar"] [data-baseweb="select"] input,
    section[data-testid="stSidebar"] [data-baseweb="select"] span {
        background: #FFFFFF !important;
        color: #17202A !important;
        -webkit-text-fill-color: #17202A !important;
    }

    div[data-testid="stFileUploader"] button,
    div[data-testid="stFileUploader"] button * {
        background: #FFFFFF !important;
        color: var(--primary-dark) !important;
        -webkit-text-fill-color: var(--primary-dark) !important;
        border-color: var(--border) !important;
    }

    div[data-testid="stFileUploader"] [data-testid="stMarkdownContainer"],
    div[data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] *,
    div[data-testid="stFileUploader"] small {
        color: #17202A !important;
        -webkit-text-fill-color: #17202A !important;
    }

    div[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"],
    div[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] *,
    div[data-testid="stFileUploader"] [data-testid="stFileUploaderFileName"],
    div[data-testid="stFileUploader"] [data-testid="stFileUploaderFileSize"] {
        background: #FFFFFF !important;
        color: #17202A !important;
        -webkit-text-fill-color: #17202A !important;
    }

    div[data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] {
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
    }

    .json-panel {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 12px;
        box-shadow: 0 8px 20px rgba(20, 42, 68, 0.06);
        padding: 1rem 1.1rem;
        overflow-x: auto;
        color: #17202A !important;
    }

    .json-panel pre,
    .json-panel code {
        background: transparent !important;
        color: #17202A !important;
        -webkit-text-fill-color: #17202A !important;
        font-size: 0.96rem;
        line-height: 1.55;
        margin: 0;
        white-space: pre-wrap;
    }

    [data-testid="stAppViewContainer"] label,
    [data-testid="stAppViewContainer"] p,
    [data-testid="stAppViewContainer"] span,
    [data-testid="stAppViewContainer"] div {
        color: #17202A;
    }

    [data-testid="stAppViewContainer"] .badge,
    [data-testid="stAppViewContainer"] .badge *,
    [data-testid="stDownloadButton"] button,
    [data-testid="stDownloadButton"] button *,
    button[kind="primary"],
    button[kind="primary"] * {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    table {
        background: #FFFFFF !important;
        border-collapse: collapse !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        color: #17202A !important;
    }

    thead tr, thead th {
        background: #EAF1F8 !important;
        color: #17202A !important;
        font-weight: 800 !important;
    }

    tbody tr, tbody td {
        background: #FFFFFF !important;
        color: #17202A !important;
        border-color: var(--border) !important;
    }

    tbody tr:nth-child(even), tbody tr:nth-child(even) td {
        background: #F8FAFC !important;
    }

    .doc-table {
        width: 100%;
        border-collapse: collapse;
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 8px 20px rgba(20, 42, 68, 0.06);
        font-size: 0.92rem;
    }

    .doc-table th {
        background: #EAF1F8;
        color: #17202A !important;
        text-align: left;
        padding: 0.72rem 0.8rem;
        font-weight: 800;
        border-bottom: 1px solid var(--border);
    }

    .doc-table td {
        color: #17202A !important;
        padding: 0.68rem 0.8rem;
        border-bottom: 1px solid var(--border);
    }

    .doc-table tr:nth-child(even) td {
        background: #F8FAFC;
    }

    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div:not(.brand-logo) {
        color: #F8FAFC !important;
        -webkit-text-fill-color: #F8FAFC !important;
    }

    section[data-testid="stSidebar"] .brand-logo,
    section[data-testid="stSidebar"] .brand-logo * {
        color: var(--primary-dark) !important;
        -webkit-text-fill-color: var(--primary-dark) !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked),
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) div,
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) span,
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
        color: var(--primary-dark) !important;
        -webkit-text-fill-color: var(--primary-dark) !important;
    }

    section[data-testid="stSidebar"] [data-baseweb="select"],
    section[data-testid="stSidebar"] [data-baseweb="select"] div,
    section[data-testid="stSidebar"] [data-baseweb="select"] span,
    section[data-testid="stSidebar"] [data-baseweb="select"] input {
        color: #17202A !important;
        -webkit-text-fill-color: #17202A !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


MODE_MAP = {
    "DocReader BD": "docreader",
    "OCR Mode": "ocr",
    "Database": "database",
}


def init_state():
    defaults = {
        "current_mode": "docreader",
        "last_ocr_results": None,
        "last_docreader_result": None,
        "last_original_image": None,
        "last_annotated_image": None,
        "last_filename": "",
        "last_file_bytes": b"",
        "last_file_size_kb": 0.0,
        "last_text": "",
        "last_raw_text": "",
        "last_ocr_engine": "shobdoocr",
        "last_page_index": 0,
        "last_mode_processed": "",
        "uploader_version": 0,
        "db_refresh": 0,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


@st.cache_resource
def load_ocr():
    from shobdoocr import OCR

    return OCR()


@st.cache_resource
def load_reader():
    from docreaderbd import DocReader

    return DocReader()


@st.cache_resource
def load_groq_client():
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing in .env")
    return Groq(api_key=api_key)


@st.cache_resource
def init_database_once():
    try:
        init_db()
        return True, ""
    except Exception as exc:
        return False, str(exc)


def load_models_once():
    try:
        with st.spinner("Loading OCR models..."):
            ocr = load_ocr()
            load_reader()
        st.success("✅ Models loaded")
        return ocr
    except Exception:
        raise


def run_tesseract_ocr(image: Image.Image) -> tuple[str, list[dict]]:
    import pytesseract

    tesseract_cmd = os.getenv("TESSERACT_CMD")
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    text = pytesseract.image_to_string(image, lang="ben+eng", config="--psm 6").strip()
    ocr_results = [{"text": word, "box": [0, 0, 0, 0], "script": "tesseract"} for word in text.split()]
    return text, ocr_results


@st.cache_resource
def load_easyocr_reader():
    import easyocr

    return easyocr.Reader(["bn", "en"], gpu=False)


def run_easyocr(image: Image.Image) -> tuple[str, list[dict]]:
    import numpy as np

    reader = load_easyocr_reader()
    results = reader.readtext(np.array(image.convert("RGB")), detail=1, paragraph=False)
    ocr_results = []
    lines = []
    for box, text, confidence in results:
        xs = [point[0] for point in box]
        ys = [point[1] for point in box]
        ocr_results.append(
            {
                "text": text,
                "box": [float(min(xs)), float(min(ys)), float(max(xs)), float(max(ys))],
                "script": "easyocr",
                "conf": float(confidence),
            }
        )
        if text:
            lines.append(text)
    return "\n".join(lines).strip(), ocr_results


def image_to_png_bytes(image: Image.Image | bytes | None) -> bytes | None:
    if image is None:
        return None
    if isinstance(image, bytes):
        return image
    buffer = io.BytesIO()
    image.convert("RGB").save(buffer, format="PNG")
    return buffer.getvalue()


def bytes_to_image(data) -> Image.Image | None:
    if data is None:
        return None
    return Image.open(io.BytesIO(bytes(data))).convert("RGB")


def images_to_zip(original_bytes, annotated_bytes, fields_dict) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        if original_bytes:
            archive.writestr("original.png", bytes(original_bytes))
        if annotated_bytes:
            archive.writestr("annotated.png", bytes(annotated_bytes))
        archive.writestr("fields.json", json.dumps(fields_dict or {}, ensure_ascii=False, indent=2))
    return buffer.getvalue()


def uploaded_file_to_images(uploaded_file) -> tuple[list[Image.Image], int]:
    suffix = Path(uploaded_file.name).suffix.lower()
    payload = uploaded_file.getvalue()

    if suffix == ".pdf":
        images = []
        zoom = 200 / 72
        matrix = fitz.Matrix(zoom, zoom)
        with fitz.open(stream=payload, filetype="pdf") as document:
            for page in document:
                pixmap = page.get_pixmap(matrix=matrix, alpha=False)
                image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
                images.append(image)
            return images, len(document)

    if suffix not in {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}:
        raise ValueError("Unsupported file format. Please upload JPG, PNG, PDF, BMP, or TIFF.")

    with Image.open(io.BytesIO(payload)) as image:
        return [image.convert("RGB")], 1


def annotate_image(ocr, image: Image.Image, results, show_boxes: bool) -> Image.Image:
    if not show_boxes:
        return image.copy()
    return ocr.visualize(image, results)


def count_language_mix(ocr_results) -> tuple[int, int]:
    bengali = 0
    english = 0
    for item in ocr_results or []:
        text = str(item.get("text", "")) if isinstance(item, dict) else str(item)
        if any("\u0980" <= char <= "\u09ff" for char in text):
            bengali += 1
        elif any(char.isalpha() for char in text):
            english += 1
    return bengali, english


def clean_ocr_text(text: str) -> str:
    prompt = f"""The following text was extracted from a Bangladeshi document using OCR. 
It contains Bengali and English text mixed together. Some words may be 
garbled or incorrectly recognized (e.g. single random characters, 
nonsense syllables). 

Clean the text by:
1. Removing clearly garbled/nonsense words (single random chars, 
   meaningless syllables like ঘু, বিও, লপট্ট, ম)
2. Fixing obvious OCR errors where the correct word is clear from context
3. Preserving all correctly recognized Bengali and English words
4. Maintaining the original line structure
5. Return ONLY the cleaned text, nothing else

Raw OCR text:
{text}"""
    client = load_groq_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Clean OCR text and return only the cleaned text."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
    )
    return (response.choices[0].message.content or "").strip()


def extract_json_from_text(ocr_text: str, ocr_engine: str) -> dict:
    prompt = f"""You are an expert information extraction system for Bangladeshi documents.

The following text was extracted using OCR engine: {ocr_engine}.

STRICT RULES:
1. Use ONLY text that appears in the OCR text below.
2. Do NOT invent, guess, infer, or add random values.
3. If a requested field is not found, keep its value as an empty string.
4. For English words, if a word is broken or has an obvious OCR typo, fix it only when the correct word is clear from nearby OCR context.
5. Preserve Bengali values exactly as found unless spacing is obviously broken.
6. Skip watermarks, random noise, page numbers, and meaningless garbled fragments.
7. Return ONLY valid JSON. No markdown. No explanation.

DOCUMENT TYPE RULES:
- If this is a Bangladesh NID card, set document_type to "nid" and extract these fields inside fields:
  bangla_name, english_name, husband_or_father_name_bn, mother_name_bn, date_of_birth, nid_number, blood_group, address
  For husband_or_father_name_bn: if the NID text has Husband Name / স্বামী / স্বামীর নাম, use that value.
  Otherwise use Father Name / পিতা / পিতার নাম. Do not create separate father and husband fields for NID.

- If this is a birth certificate, set document_type to "birth_cert" and extract these fields inside fields:
  birth_reg_number, bangla_name, english_name, gender, mother_name_bn, mother_name_en, father_name_bn, father_name_en,
  date_of_birth, birthplace, present_address, permanent_address

- If this is an invoice, set document_type to "invoice" and choose suitable key-value fields from the OCR text, such as invoice_number, date, vendor, customer, items, subtotal, vat, total, amount_due, payment_method.

- For any other document, set document_type to "unknown" and extract only clear key-value fields found in the OCR text.

OUTPUT SCHEMA:
1. Include these top-level keys:
   - document_type
   - confidence
   - fields
2. fields must be a JSON object.
3. confidence must be a number from 0.0 to 1.0.
4. Use English snake_case keys.

OCR text:
{ocr_text}"""
    client = load_groq_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Return only valid JSON extracted from OCR text."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_tokens=1800,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content or "{}"
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        parsed = json.loads(raw[start : end + 1]) if start >= 0 and end > start else {}
    if not isinstance(parsed, dict):
        return {"document_type": "unknown", "confidence": 0.0, "fields": {}}
    parsed.setdefault("document_type", "unknown")
    parsed.setdefault("confidence", 0.0)
    if not isinstance(parsed.get("fields"), dict):
        parsed["fields"] = {}
    return parsed


def doc_type_label(doc_type: str) -> str:
    return {
        "nid": "NID Card",
        "birth_cert": "Birth Certificate",
        "birth_certificate": "Birth Certificate",
        "invoice": "Invoice",
        "unknown": "Unknown",
    }.get(doc_type or "unknown", str(doc_type or "Unknown"))


def doc_type_class(doc_type: str) -> str:
    return {
        "nid": "navy",
        "birth_cert": "green",
        "birth_certificate": "green",
        "invoice": "orange",
        "unknown": "gray",
    }.get(doc_type or "unknown", "gray")


def extraction_badge_class(mode: str) -> str:
    return "purple" if mode == "llm" else "gray"


def extraction_label(mode: str) -> str:
    if mode == "llm":
        return "AI Extraction"
    return str(mode or "Unknown")


def render_badges(document_type: str, extraction_mode: str):
    st.markdown(
        f"""
        <span class="badge {doc_type_class(document_type)}">{doc_type_label(document_type)}</span>
        <span class="badge {extraction_badge_class(extraction_mode)}">{extraction_label(extraction_mode)}</span>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    st.sidebar.markdown(
        """
        <div class="brand">
            <div class="brand-logo">DR</div>
            <div>
                <div class="brand-title">DocReader BD</div>
                <div class="brand-subtitle">Bangladesh Document AI</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown('<div class="sidebar-rule"></div>', unsafe_allow_html=True)

    current_label = next(label for label, value in MODE_MAP.items() if value == st.session_state.current_mode)
    selected = st.sidebar.radio(
        "Navigation",
        list(MODE_MAP.keys()),
        index=list(MODE_MAP.keys()).index(current_label),
        label_visibility="collapsed",
    )
    st.session_state.current_mode = MODE_MAP[selected]

    with st.sidebar.expander("Settings", expanded=True):
        ocr_engine = st.selectbox(
            "OCR engine",
            ["ShobdoOCR", "Tesseract Bangla", "EasyOCR Bangla"],
            index=0,
            help="Tesseract and EasyOCR return raw OCR text only. They do not use Groq/LLM cleaning.",
        )

    st.sidebar.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    st.sidebar.markdown(
        """
        <div class="sidebar-rule"></div>
        <strong>About</strong><br>
        DocReader BD v1.0<br>
        Powered by ShobdoOCR<br>
        Models: YOLOv8 · BiLSTM · CTC<br>
        Supports: বাংলা + English
        """,
        unsafe_allow_html=True,
    )
    return ocr_engine


def clear_document_state():
    for key in (
        "last_ocr_results",
        "last_docreader_result",
        "last_original_image",
        "last_annotated_image",
        "last_filename",
        "last_file_bytes",
        "last_file_size_kb",
        "last_text",
        "last_raw_text",
        "last_ocr_engine",
        "last_page_index",
        "last_mode_processed",
    ):
        st.session_state[key] = b"" if key == "last_file_bytes" else "" if key in {"last_filename", "last_text", "last_raw_text", "last_mode_processed"} else "shobdoocr" if key == "last_ocr_engine" else 0 if key == "last_page_index" else 0.0 if key == "last_file_size_kb" else None
    st.session_state.uploader_version += 1


def render_placeholder(mode_name: str):
    st.markdown(
        f"""
        <div class="placeholder">
            <div style="font-size: 3rem;">🇧🇩📄</div>
            <h3>{mode_name}</h3>
            <p>Upload a Bangladeshi document to begin.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_file_info(uploaded_file):
    size_kb = len(uploaded_file.getvalue()) / 1024
    st.markdown(
        f"""
        <div class="file-meta">
            <strong>File name:</strong> {uploaded_file.name}<br>
            <strong>Size:</strong> {size_kb:.1f} KB<br>
            <strong>Type:</strong> {uploaded_file.type or Path(uploaded_file.name).suffix.upper()}
        </div>
        """,
        unsafe_allow_html=True,
    )


def should_process(uploaded_file, page_index: int, mode: str, ocr_engine: str) -> bool:
    file_bytes = uploaded_file.getvalue()
    return (
        st.session_state.last_file_bytes != file_bytes
        or st.session_state.last_page_index != page_index
        or st.session_state.last_mode_processed != mode
        or st.session_state.last_ocr_engine != ocr_engine
        or st.session_state.last_ocr_results is None
    )


def process_uploaded(uploaded_file, page_index: int, mode: str, ocr_engine: str):
    progress = st.progress(0)
    status = st.empty()
    try:
        file_bytes = uploaded_file.getvalue()
        images, _ = uploaded_file_to_images(uploaded_file)
        image = images[page_index]

        status.info("Running OCR...")
        with st.spinner("Running OCR..."):
            if ocr_engine == "Tesseract Bangla":
                raw_text, ocr_results = run_tesseract_ocr(image)
                text = raw_text
                annotated = image.copy()
            elif ocr_engine == "EasyOCR Bangla":
                raw_text, ocr_results = run_easyocr(image)
                text = raw_text
                annotated = image.copy()
            else:
                ocr = load_models_once()
                ocr_results = ocr.read(image, verbose=False)
                raw_text = full_text(ocr_results)
                text = raw_text
                annotated = annotate_image(ocr, image, ocr_results, True)
        progress.progress(40)

        result = None
        if mode == "docreader":
            status.info("Extracting fields...")
            with st.spinner("Extracting fields..."):
                structured = extract_json_from_text(text, ocr_engine)
                doc_type = structured.get("document_type", "unknown")
                fields = structured.get("fields", {}) or {}
                extraction_mode = "llm"
                result = {
                    "document_type": doc_type,
                    "extraction_mode": extraction_mode,
                    "fields": fields,
                    "confidence": structured.get("confidence", 0.0),
                    "ocr_results": ocr_results,
                    "page_count": len(images),
                }
                st.session_state.last_docreader_result = result
        elif mode == "ocr" and raw_text.strip() and ocr_engine == "ShobdoOCR":
            status.info("Cleaning OCR text...")
            try:
                with st.spinner("Cleaning OCR text with Groq..."):
                    text = clean_ocr_text(raw_text)
            except Exception as exc:
                st.warning(f"AI cleaner failed. Showing raw OCR text instead. {exc}")
        progress.progress(80)

        st.session_state.last_ocr_results = ocr_results
        st.session_state.last_original_image = image
        st.session_state.last_annotated_image = annotated
        st.session_state.last_filename = uploaded_file.name
        st.session_state.last_file_bytes = file_bytes
        st.session_state.last_file_size_kb = len(file_bytes) / 1024
        st.session_state.last_raw_text = raw_text
        st.session_state.last_text = text
        st.session_state.last_ocr_engine = ocr_engine
        st.session_state.last_page_index = page_index
        st.session_state.last_mode_processed = mode

        progress.progress(100)
        status.success("Done!")
        return result
    except Exception as exc:
        st.error(f"OCR failed: {exc}")
        with st.expander("Traceback"):
            st.code(traceback.format_exc())
        return None
    finally:
        progress.empty()


def render_document_columns(uploaded_file, images, page_index):
    original = st.session_state.last_original_image or images[page_index]
    annotated = st.session_state.last_annotated_image or original
    left, right = st.columns([0.55, 0.45])
    with left:
        st.subheader("Original Document")
        st.image(original, use_container_width=True)
        render_file_info(uploaded_file)
    with right:
        st.subheader("Processed Result")
        st.image(annotated, use_container_width=True)
        st.markdown('<div class="legend"><span class="bn">Green</span>=Bengali · <span class="en">Blue</span>=English</div>', unsafe_allow_html=True)


def render_docreader_actions(db_connected: bool, db_error: str):
    result = st.session_state.last_docreader_result or {}

    if db_connected:
        if st.button("Save to Database", type="primary", use_container_width=True):
            st.session_state.show_save_dialog = True
    else:
        st.warning("Database not connected. Save feature disabled.")
        if db_error:
            with st.expander("Database error"):
                st.code(db_error)

    if st.session_state.get("show_save_dialog"):
        show_save_dialog()


@st.dialog("Save document")
def show_save_dialog():
    st.warning("Save this document and extracted data to database?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Confirm Save", type="primary", use_container_width=True):
            try:
                result = st.session_state.last_docreader_result or {}
                record_id = save_document(
                    result.get("document_type", "unknown"),
                    result.get("extraction_mode", "unknown"),
                    st.session_state.last_filename,
                    st.session_state.last_file_size_kb,
                    st.session_state.last_original_image,
                    st.session_state.last_annotated_image,
                    result.get("fields", {}),
                    len(st.session_state.last_text.split()),
                )
                doc_type = str(result.get("document_type", "unknown")).lower()
                fields = result.get("fields", {}) or {}
                if doc_type == "nid":
                    save_nid_record(record_id, fields)
                elif doc_type in {"birth_cert", "birth_certificate"}:
                    save_birth_certificate_record(record_id, fields)
                st.session_state.show_save_dialog = False
                st.success(f"Saved to database successfully. Record ID: {record_id}")
            except Exception as exc:
                st.error(f"Save failed: {exc}")
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.session_state.show_save_dialog = False
            st.rerun()


def render_docreader_mode(ocr_engine, db_connected, db_error):
    st.markdown('<div class="page-title">DocReader BD</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Intelligent Document Understanding for Bangladesh</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload a Bangladeshi document",
        type=["jpg", "jpeg", "png", "pdf", "bmp", "tiff"],
        key=f"docreader_upload_{st.session_state.uploader_version}",
    )
    if uploaded_file is None:
        render_placeholder("DocReader BD")
        return

    try:
        images, page_count = uploaded_file_to_images(uploaded_file)
        page_index = 0
        if Path(uploaded_file.name).suffix.lower() == ".pdf" and page_count > 1:
            page_index = st.selectbox("Select PDF page", range(page_count), format_func=lambda i: f"Page {i + 1}")
        if should_process(uploaded_file, page_index, "docreader", ocr_engine):
            process_uploaded(uploaded_file, page_index, "docreader", ocr_engine)
        render_document_columns(uploaded_file, images, page_index)

        result = st.session_state.last_docreader_result or {}
        st.divider()
        st.caption(f"OCR engine: {ocr_engine}")
        render_badges(result.get("document_type", "unknown"), result.get("extraction_mode", "unknown"))
        st.markdown("### Extracted Fields")
        render_json_panel(result.get("fields", {}) or {})
        render_docreader_actions(db_connected, db_error)
    except Exception as exc:
        st.warning(str(exc))


def render_ocr_mode(ocr_engine):
    st.markdown('<div class="page-title">OCR Mode</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Extract raw text from documents</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload a Bangladeshi document",
        type=["jpg", "jpeg", "png", "pdf", "bmp", "tiff"],
        key=f"ocr_upload_{st.session_state.uploader_version}",
    )
    if uploaded_file is None:
        render_placeholder("OCR Mode")
        return

    try:
        images, page_count = uploaded_file_to_images(uploaded_file)
        page_index = 0
        if Path(uploaded_file.name).suffix.lower() == ".pdf" and page_count > 1:
            page_index = st.selectbox("Select PDF page", range(page_count), format_func=lambda i: f"Page {i + 1}")
        if should_process(uploaded_file, page_index, "ocr", ocr_engine):
            process_uploaded(uploaded_file, page_index, "ocr", ocr_engine)
        render_document_columns(uploaded_file, images, page_index)

        st.divider()
        st.caption(
            f"OCR engine: {ocr_engine}"
            + (" · Raw OCR output, no Groq/LLM cleaning" if ocr_engine != "ShobdoOCR" else " · Cleaned with Groq")
        )
        words = st.session_state.last_text.split()
        bengali_words, english_words = count_language_mix(st.session_state.last_ocr_results)
        st.markdown(
            f"""
            <div class="metric-row">
                <div class="metric-card"><div class="metric-value">{len(words)}</div><div class="metric-label">Total Words</div></div>
                <div class="metric-card"><div class="metric-value">{bengali_words}</div><div class="metric-label">Bengali Words</div></div>
                <div class="metric-card"><div class="metric-value">{english_words}</div><div class="metric-label">English Words</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.text_area("Extracted text", value=st.session_state.last_text, height=300, disabled=True)
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "Download Text",
                data=st.session_state.last_text.encode("utf-8"),
                file_name="extracted_text.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with col2:
            if st.button("Clear", use_container_width=True):
                clear_document_state()
                st.rerun()
    except Exception as exc:
        st.warning(str(exc))


def format_document_rows(rows):
    formatted = []
    for row in rows:
        created_at = row.get("created_at")
        formatted.append(
            {
                "ID": row.get("id"),
                "Date/Time": created_at.strftime("%d %b %Y %H:%M") if hasattr(created_at, "strftime") else str(created_at),
                "Document Type": doc_type_label(row.get("document_type")),
                "Filename": row.get("filename"),
                "Size": f"{float(row.get('file_size_kb') or 0):.1f} KB",
                "Words": row.get("ocr_word_count") or 0,
                "Actions": "View below",
            }
        )
    return formatted


def filter_rows(rows, query: str):
    if not query:
        return rows
    query = query.lower()
    return [
        row
        for row in rows
        if query in " ".join("" if value is None else str(value) for value in row.values()).lower()
    ]


def format_structured_rows(rows):
    formatted = []
    for row in rows:
        item = {}
        for key, value in row.items():
            label = key.replace("_", " ").title()
            if key == "created_at" and hasattr(value, "strftime"):
                item[label] = value.strftime("%d %b %Y %H:%M")
            else:
                item[label] = value
        formatted.append(item)
    return formatted


def render_light_table(rows):
    df = pd.DataFrame(rows)
    if df.empty:
        st.info("No records to display.")
        return
    st.markdown(df.to_html(index=False, escape=False, classes="doc-table"), unsafe_allow_html=True)


def render_json_panel(data):
    text = json.dumps(data or {}, ensure_ascii=False, indent=2)
    st.markdown(
        f'<div class="json-panel"><pre><code>{text}</code></pre></div>',
        unsafe_allow_html=True,
    )


def render_database_mode(db_connected: bool, db_error: str):
    st.markdown('<div class="page-title">🗄️ Document Database</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Stored documents and extracted data</div>', unsafe_allow_html=True)

    if not db_connected:
        st.warning("Database not connected. Save feature disabled.")
        if db_error:
            with st.expander("Database error"):
                st.code(db_error)
        return

    if st.button("Refresh", use_container_width=False):
        st.session_state.db_refresh += 1

    try:
        rows = get_all_documents()
    except Exception as exc:
        st.warning("Database not connected. Save feature disabled.")
        with st.expander("Database error"):
            st.code(str(exc))
        return

    total = len(rows)
    nid_count = sum(1 for row in rows if row.get("document_type") == "nid")
    birth_count = sum(1 for row in rows if row.get("document_type") == "birth_cert")
    other_count = total - nid_count - birth_count
    st.markdown(
        f"""
        <div class="metric-row">
            <div class="metric-card"><div class="metric-value">{total}</div><div class="metric-label">Total Documents</div></div>
            <div class="metric-card"><div class="metric-value">{nid_count}</div><div class="metric-label">NID Cards</div></div>
            <div class="metric-card"><div class="metric-value">{birth_count}</div><div class="metric-label">Birth Certificates</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(f"Others: {other_count}")

    if not rows:
        st.info("No documents saved yet.")
        return

    render_light_table(format_document_rows(rows))
    ids = [row["id"] for row in rows]
    selected_id = st.selectbox("View document ID:", ids)

    try:
        detail = get_document_by_id(selected_id)
    except Exception as exc:
        st.error(f"Could not load document: {exc}")
        return

    if not detail:
        st.warning("Document not found.")
        return

    fields = detail.get("fields_json") or {}
    original_bytes = detail.get("original_image")
    annotated_bytes = detail.get("annotated_image")
    original_image = bytes_to_image(original_bytes)
    annotated_image = bytes_to_image(annotated_bytes)

    with st.expander("Images", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original Image")
            if original_image:
                st.image(original_image, use_container_width=True)
                st.download_button("Download Original", bytes(original_bytes), "original.png", "image/png", use_container_width=True)
        with col2:
            st.subheader("Annotated Image")
            if annotated_image:
                st.image(annotated_image, use_container_width=True)
                st.download_button("Download Annotated", bytes(annotated_bytes), "annotated.png", "image/png", use_container_width=True)

    with st.expander("Extracted Fields", expanded=True):
        render_json_panel(fields)
        st.download_button(
            "Download JSON",
            json.dumps(fields, ensure_ascii=False, indent=2).encode("utf-8"),
            f"{detail.get('document_type', 'document')}_{selected_id}.json",
            "application/json",
            use_container_width=True,
        )

    with st.expander("Actions", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "⬇️ Download All",
                images_to_zip(original_bytes, annotated_bytes, fields),
                f"document_{selected_id}.zip",
                "application/zip",
                use_container_width=True,
            )
        with col2:
            if st.button("🗑️ Delete Record", use_container_width=True):
                st.session_state.delete_id = selected_id
                st.session_state.show_delete_dialog = True

    if st.session_state.get("show_delete_dialog"):
        show_delete_dialog()


@st.dialog("Delete record")
def show_delete_dialog():
    doc_id = st.session_state.get("delete_id")
    st.warning(f"Delete record {doc_id}? This cannot be undone.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Confirm Delete", type="primary", use_container_width=True):
            try:
                delete_document(doc_id)
                st.session_state.show_delete_dialog = False
                st.success("Record deleted.")
                st.rerun()
            except Exception as exc:
                st.error(f"Delete failed: {exc}")
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.session_state.show_delete_dialog = False
            st.rerun()


def render_database_mode(db_connected: bool, db_error: str):
    st.markdown('<div class="page-title">Document Database</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Stored documents and extracted data</div>', unsafe_allow_html=True)

    if not db_connected:
        st.warning("Database not connected. Save feature disabled.")
        if db_error:
            with st.expander("Database error"):
                st.code(db_error)
        return

    if st.button("Refresh", use_container_width=False):
        st.session_state.db_refresh += 1

    table_choice = st.radio(
        "Select table",
        ["Document Archive", "NID Cards", "Birth Certificates"],
        horizontal=True,
    )

    try:
        if table_choice == "Document Archive":
            rows = get_all_documents()
            if not rows:
                st.info("No documents saved yet.")
                return
            render_light_table(format_document_rows(rows))
            ids = [row["id"] for row in rows]
            selected_id = st.selectbox("Select archive entry for ZIP download:", ids)
            detail = get_document_by_id(selected_id)
            if detail:
                st.download_button(
                    "Download selected entry as ZIP",
                    images_to_zip(detail.get("original_image"), detail.get("annotated_image"), detail.get("fields_json") or {}),
                    f"document_{selected_id}.zip",
                    "application/zip",
                    use_container_width=True,
                )
                if st.button("Delete selected archive record", use_container_width=True):
                    st.session_state.delete_id = selected_id
                    st.session_state.show_delete_dialog = True

        elif table_choice == "NID Cards":
            rows = filter_rows(get_all_nid_cards(), st.text_input("Search NID table"))
            if rows:
                render_light_table(format_structured_rows(rows))
            else:
                st.info("No matching NID records.")

        else:
            rows = filter_rows(get_all_birth_certificates(), st.text_input("Search Birth Certificate table"))
            if rows:
                render_light_table(format_structured_rows(rows))
            else:
                st.info("No matching birth certificate records.")
    except Exception as exc:
        st.error(f"Could not load database table: {exc}")

    if st.session_state.get("show_delete_dialog"):
        show_delete_dialog()


def main():
    init_state()
    db_connected, db_error = init_database_once()
    ocr_engine = render_sidebar()

    if st.session_state.current_mode == "docreader":
        render_docreader_mode(ocr_engine, db_connected, db_error)
    elif st.session_state.current_mode == "ocr":
        render_ocr_mode(ocr_engine)
    else:
        render_database_mode(db_connected, db_error)


if __name__ == "__main__":
    main()
