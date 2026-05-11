import json
import os
import re

from dotenv import load_dotenv
from groq import Groq

from .base import _words, full_text


def _spatial_pairs(ocr_results) -> list[dict[str, str]]:
    words = _words(ocr_results)
    pairs = []

    for word in words:
        text = word["text"].strip()
        if not (text.endswith(":") or text.endswith("।")):
            continue

        neighbors = [
            candidate
            for candidate in words
            if candidate is not word
            and candidate["x1"] >= word["x2"] - 2
            and abs(candidate["cy"] - word["cy"]) <= 18
        ]
        if not neighbors:
            continue

        value = " ".join(candidate["text"] for candidate in sorted(neighbors, key=lambda item: item["x1"])[:6])
        pairs.append({"label": text.rstrip(":।"), "value": value})

    return pairs


def _parse_json(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def llm_extract(ocr_results, doc_type_hint="unknown", model="llama-3.3-70b-versatile") -> dict:
    load_dotenv()
    raw = ""

    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        reading_text = full_text(ocr_results)
        spatial_pairs = _spatial_pairs(ocr_results)

        prompt = f"""
You are extracting structured data from a Bangladeshi document OCR result.

Document type hint: {doc_type_hint}

Reconstructed reading-order text:
{reading_text}

Spatial label:value pairs:
{json.dumps(spatial_pairs, ensure_ascii=False, indent=2)}

Instructions:
- Identify document type.
- Extract all key-value fields.
- Return ONLY valid JSON, no explanation, no markdown.
- Use English snake_case field names.
- Keep values in the original language, Bengali or English as found.
- Include document_type and confidence fields.
- confidence must be a number from 0.0 to 1.0.
- Skip noise, watermarks, page numbers.
"""

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Return only valid JSON for document OCR extraction."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=1500,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content or ""
        return _parse_json(raw)
    except Exception as exc:
        return {"error": str(exc), "raw": raw}
