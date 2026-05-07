KEYWORDS = {
    "nid": [
        "জাতীয় পরিচয়",
        "National ID",
        "ID NO",
        "Blood Group",
        "রক্তের গ্রুপ",
        "গণপ্রজাতন্ত্রী",
        "National Identity",
    ],
    "birth_cert": [
        "জন্ম নিবন্ধন",
        "BIRTH REGISTRATION",
        "REGISTRAR GENERAL",
        "Birth Registration Number",
        "মাতার নাম",
        "পিতার নাম",
        "DATE OF BIRTH",
    ],
    "invoice": [
        "Invoice",
        "চালান",
        "মোট",
        "VAT",
        "Total",
        "Receipt",
        "Amount",
    ],
    "land_deed": [
        "দলিল",
        "মৌজা",
        "খতিয়ান",
        "ভূমি",
        "Deed",
        "Property",
    ],
}


def classify(ocr_text: str) -> str:
    text = ocr_text or ""
    text_lower = text.lower()
    scores = {}

    for doc_type, keywords in KEYWORDS.items():
        score = 0
        for keyword in keywords:
            score += text_lower.count(keyword.lower())
        scores[doc_type] = score

    best_type = max(scores, key=scores.get)
    return best_type if scores[best_type] > 0 else "unknown"
