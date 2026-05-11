# DocReader BD Backend

FastAPI API for OCR, template storage, and spatial field extraction.

## Setup
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Copy `.env.example` to `.env` and configure Firebase, Groq, and Tesseract paths before using Firebase-backed routes.
