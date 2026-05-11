import os
from typing import Any

import numpy as np
from PIL import Image


def _normalize_engine(engine: str) -> str:
    return (engine or "shobdoocr").strip().lower()


async def run_ocr(image: Image.Image, engine: str) -> dict[str, Any]:
    selected_engine = _normalize_engine(engine)

    if selected_engine == "shobdoocr":
        words, text = _run_shobdoocr(image)
    elif selected_engine == "tesseract":
        words, text = _run_tesseract(image)
    elif selected_engine == "easyocr":
        words, text = _run_easyocr(image)
    else:
        raise ValueError(f"Unsupported OCR engine: {engine}")

    return {
        "text": text,
        "words": words,
        "word_count": len(words),
        "engine": selected_engine,
    }


def _run_shobdoocr(image: Image.Image) -> tuple[list[dict[str, Any]], str]:
    from shobdoocr import OCR

    ocr = OCR()
    raw_words = ocr.read(image)
    text = ocr.read_text(image)

    words = [
        {
            "text": item.get("text", ""),
            "box": [int(value) for value in item.get("box", [0, 0, 0, 0])],
            "script": item.get("script", "unknown"),
            "conf": float(item.get("conf", 0.0)),
        }
        for item in raw_words
        if item.get("text")
    ]
    return words, text


def _run_tesseract(image: Image.Image) -> tuple[list[dict[str, Any]], str]:
    import pytesseract
    from pytesseract import Output

    tesseract_cmd = os.getenv("TESSERACT_CMD")
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    data = pytesseract.image_to_data(
        image,
        lang="ben+eng",
        config="--psm 6",
        output_type=Output.DICT,
    )

    words: list[dict[str, Any]] = []
    for index, text in enumerate(data.get("text", [])):
        clean_text = text.strip()
        try:
            conf = float(data["conf"][index])
        except (ValueError, TypeError):
            conf = -1.0

        if not clean_text or conf < 0:
            continue

        x = int(data["left"][index])
        y = int(data["top"][index])
        width = int(data["width"][index])
        height = int(data["height"][index])
        words.append(
            {
                "text": clean_text,
                "box": [x, y, x + width, y + height],
                "script": "unknown",
                "conf": conf,
            }
        )

    return words, " ".join(word["text"] for word in words)


def _run_easyocr(image: Image.Image) -> tuple[list[dict[str, Any]], str]:
    import easyocr

    reader = easyocr.Reader(["bn", "en"])
    results = reader.readtext(np.array(image), detail=1)

    words: list[dict[str, Any]] = []
    for polygon, text, conf in results:
        xs = [point[0] for point in polygon]
        ys = [point[1] for point in polygon]
        words.append(
            {
                "text": text,
                "box": [int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))],
                "script": "unknown",
                "conf": float(conf),
            }
        )

    return words, " ".join(word["text"] for word in words)
