import os
import numpy as np
from PIL import Image
import pytesseract
from dotenv import load_dotenv

load_dotenv()

tess_cmd = os.getenv('TESSERACT_CMD')
if tess_cmd:
    pytesseract.pytesseract.tesseract_cmd = tess_cmd

async def run_ocr(image: Image.Image, engine: str) -> dict:
    words = []
    text = ''

    if engine == 'shobdoocr':
        try:
            from shobdoocr import OCR
            ocr = OCR()
            results = ocr.read(image)
            text = ocr.read_text(image)
            for r in results:
                words.append({
                    'text': r['text'],
                    'box': r['box'],
                    'script': r.get('script', 'unknown'),
                    'conf': float(r.get('conf', 0.0))
                })
        except Exception as e:
            print(f'ShobdoOCR error: {e}')
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

    return {
        'text': text,
        'words': words,
        'word_count': len(words),
        'engine': engine
    }
