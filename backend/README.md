# DocReader BD Backend

FastAPI API for OCR, template storage, and spatial field extraction.

## Setup
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Copy `.env.example` to `.env` and configure Firebase, Groq, and Tesseract paths before using Firebase-backed routes.

ShobdoOCR runs through its Hugging Face Space API. Configure:

```env
SHOBDOOCR_API_URL=https://sarjinkhan2003-shobdoocr-web.hf.space
SHOBDOOCR_TIMEOUT_SECONDS=120
```

The backend sends images as multipart form data under the `file` field. You can
check the upstream service through `GET /ocr/shobdoocr/health`.
