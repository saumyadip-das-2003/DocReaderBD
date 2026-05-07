# DocReader BD
Intelligent Document Processing for Bangladeshi Enterprises

Extracts structured data from NID cards, birth certificates,
land deeds, and invoices using ShobdoOCR + Groq LLM + PostgreSQL.

---

## Requirements
- Python 3.10+
- PostgreSQL (running locally or remote)
- Tesseract OCR installed
- Groq API key (free at https://console.groq.com)

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env and fill in your credentials
```

### 3. Setup PostgreSQL
```sql
CREATE DATABASE docreaderbd;
```
Tables are created automatically on first run.

### 4. Install Tesseract
- Windows: https://github.com/UB-Mannheim/tesseract/wiki
- Linux: `sudo apt install tesseract-ocr tesseract-ocr-ben`
- Mac: `brew install tesseract tesseract-lang`

### 5. Run the app

**Windows:**
```powershell
venv\Scripts\Activate.ps1
streamlit run app.py
```

**Linux/Mac:**
```bash
source venv/bin/activate
streamlit run app.py
```

---

## Models
All ShobdoOCR models download automatically from HuggingFace
on first run (~80MB). No manual download needed.

HuggingFace: https://huggingface.co/ShobdoOCR/shobdo-ocr

---

## Features
- OCR Mode: extract raw text using ShobdoOCR / Tesseract / EasyOCR
- DocReader Mode: extract structured JSON fields via Groq LLM
- Database Mode: browse archive, search NID records, ZIP export

---
