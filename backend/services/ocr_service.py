import asyncio
import io
import os
import traceback
import numpy as np
from PIL import Image
import pytesseract
import requests
from dotenv import load_dotenv

load_dotenv()

tess_cmd = os.getenv('TESSERACT_CMD')
if tess_cmd:
    pytesseract.pytesseract.tesseract_cmd = tess_cmd

SHOBDOOCR_API_URL = os.getenv('SHOBDOOCR_API_URL', '').rstrip('/')
SHOBDOOCR_TIMEOUT_SECONDS = max(
    float(os.getenv('SHOBDOOCR_TIMEOUT_SECONDS', '120')),
    120.0
)


def _shobdoocr_url(path: str) -> str:
    if not SHOBDOOCR_API_URL:
        raise RuntimeError('SHOBDOOCR_API_URL is not configured')
    return f'{SHOBDOOCR_API_URL}/{path.lstrip("/")}'


def _request_shobdoocr(image: Image.Image) -> dict:
    image_buffer = io.BytesIO()
    image.convert('RGB').save(image_buffer, format='PNG')
    image_buffer.seek(0)

    # Let requests create the multipart Content-Type header and boundary.
    response = requests.post(
        _shobdoocr_url('/ocr'),
        files={'file': ('document.png', image_buffer, 'image/png')},
        timeout=SHOBDOOCR_TIMEOUT_SECONDS
    )
    response.raise_for_status()

    payload = response.json()
    if not isinstance(payload.get('full_text'), str):
        raise ValueError('ShobdoOCR response is missing the full_text field')
    return payload


async def check_shobdoocr_health() -> bool:
    try:
        response = await asyncio.to_thread(
            requests.get,
            _shobdoocr_url('/health'),
            timeout=SHOBDOOCR_TIMEOUT_SECONDS
        )
        response.raise_for_status()
        return response.json() == {'status': 'healthy'}
    except (requests.RequestException, ValueError, RuntimeError):
        return False


async def run_ocr(image: Image.Image, engine: str) -> dict:
    print(f"OCR called with engine: {engine}")
    words = []
    text = ''

    if engine == 'shobdoocr':
        try:
            payload = await asyncio.to_thread(_request_shobdoocr, image)
            text = payload['full_text']
            for r in payload.get('words', []):
                if not isinstance(r, dict) or not r.get('text') or not r.get('box'):
                    continue
                words.append({
                    'text': r['text'],
                    'box': r['box'],
                    'script': r.get('script', 'unknown'),
                    'conf': float(r.get('confidence', r.get('conf', 0.0)))
                })
        except requests.Timeout as e:
            print(f'ShobdoOCR timed out after {SHOBDOOCR_TIMEOUT_SECONDS}s: {e}')
            return await run_ocr(image, 'tesseract')
        except requests.HTTPError as e:
            status = e.response.status_code if e.response is not None else 'unknown'
            print(f'ShobdoOCR returned HTTP {status}: {e}')
            return await run_ocr(image, 'tesseract')
        except requests.RequestException as e:
            print(f'ShobdoOCR request failed: {e}')
            return await run_ocr(image, 'tesseract')
        except Exception as e:
            print(f'ShobdoOCR error: {e}')
            traceback.print_exc()
            return await run_ocr(image, 'tesseract')

    elif engine == 'tesseract':
        try:
            lang = 'ben+eng'
            config = '--oem 3 --psm 6'
            data = pytesseract.image_to_data(
                image, lang=lang, config=config,
                output_type=pytesseract.Output.DICT)
            lines = []
            for i in range(len(data['text'])):
                w = data['text'][i].strip()
                conf = int(data['conf'][i])
                if not w or conf < 0:
                    continue
                x1 = data['left'][i]
                y1 = data['top'][i]
                x2 = x1 + data['width'][i]
                y2 = y1 + data['height'][i]
                words.append({
                    'text': w,
                    'box': [x1, y1, x2, y2],
                    'script': 'unknown',
                    'conf': conf / 100.0
                })
                lines.append(w)
            text = ' '.join(lines)
        except Exception as e:
            print(f'Tesseract error: {e}')
            traceback.print_exc()

    elif engine == 'easyocr':
        try:
            import easyocr
            reader = easyocr.Reader(['bn', 'en'], gpu=False)
            results = reader.readtext(np.array(image), detail=1)
            lines = []
            for (bbox, word, conf) in results:
                if not word.strip():
                    continue
                xs = [p[0] for p in bbox]
                ys = [p[1] for p in bbox]
                words.append({
                    'text': word,
                    'box': [int(min(xs)), int(min(ys)),
                            int(max(xs)), int(max(ys))],
                    'script': 'unknown',
                    'conf': float(conf)
                })
                lines.append(word)
            text = ' '.join(lines)
        except Exception as e:
            print(f'EasyOCR error: {e}')
            traceback.print_exc()

    return {
        'text': text,
        'words': words,
        'word_count': len(words),
        'engine': engine
    }
