import re

from .base import find_value_near_label, full_text, regex_find


DATE_PATTERN = r"\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b"
NID_PATTERN = r"\b\d{10}\b|\b\d{17}\b"
BLOOD_GROUP_PATTERN = r"(?<!\w)(?:AB|A|B|O)[+-](?!\w)"


def _add_if_found(output: dict, key: str, value: str | None) -> None:
    if value:
        output[key] = value


def _has_bengali(text: str | None) -> bool:
    return bool(text and re.search(r"[\u0980-\u09FF]", text))


def _clean_date_value(spatial_value: str | None, text: str) -> str | None:
    regex_value = regex_find(text, DATE_PATTERN)
    if not spatial_value:
        return regex_value
    if _has_bengali(spatial_value):
        return regex_value
    if regex_find(spatial_value, DATE_PATTERN):
        return regex_find(spatial_value, DATE_PATTERN)
    return regex_value


def _clean_nid_value(spatial_value: str | None, text: str) -> str | None:
    if spatial_value:
        candidate = spatial_value.strip()
        if candidate.upper() != "NO" and len(candidate) >= 5 and regex_find(candidate, NID_PATTERN):
            return regex_find(candidate, NID_PATTERN)
    return regex_find(text, NID_PATTERN)


def extract_nid(ocr_results) -> dict:
    text = full_text(ocr_results)
    fields = {}

    _add_if_found(
        fields,
        "name_bn",
        find_value_near_label(
            ocr_results,
            ["নাম", "নামঃ", "নাম:"],
            search_right=True,
            search_below=False,
            collect_tokens=4,
        ),
    )
    _add_if_found(fields, "name_en", find_value_near_label(ocr_results, ["Name", "NAME", "Name:"], collect_tokens=4))
    _add_if_found(fields, "father_bn", find_value_near_label(ocr_results, ["পিতা", "পিতাঃ", "পিতা:"], collect_tokens=4))
    _add_if_found(fields, "mother_bn", find_value_near_label(ocr_results, ["মাতা", "মাতাঃ", "মাতা:"], collect_tokens=4))

    dob = find_value_near_label(ocr_results, ["Date of Birth", "জন্ম তারিখ"], collect_tokens=3)
    _add_if_found(fields, "dob", _clean_date_value(dob, text))

    nid_no = find_value_near_label(ocr_results, ["ID NO", "ID No", "NID NO"], collect_tokens=1)
    _add_if_found(fields, "nid_no", _clean_nid_value(nid_no, text))

    _add_if_found(fields, "blood_group", regex_find(text, BLOOD_GROUP_PATTERN))
    _add_if_found(fields, "birth_place", find_value_near_label(ocr_results, ["জন্মস্থান", "জন্মস্থানঃ"], collect_tokens=2))
    _add_if_found(
        fields,
        "address",
        find_value_near_label(ocr_results, ["ঠিকানা", "ঠিকানাঃ", "Address"], collect_tokens=12, max_below_px=120),
    )

    issue_date = regex_find(text, r"[\u09E6-\u09EF]{1,2}/[\u09E6-\u09EF]{1,2}/[\u09E6-\u09EF]{4}")
    issue_date = issue_date or regex_find(text, r"\d{2}/\d{2}/\d{4}")
    _add_if_found(fields, "issue_date", issue_date)

    return fields
