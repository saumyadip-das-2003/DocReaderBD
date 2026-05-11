import re
from typing import Any


KNOWN_LABELS = {
    "নাম",
    "পিতা",
    "মাতা",
    "name",
    "date",
    "birth",
    "blood",
    "group",
    "card",
    "national",
    "id",
    "no",
    "নামঃ",
    "পিতাঃ",
    "মাতাঃ",
    "জাতীয়",
    "পরিচয়",
    "পত্র",
    "ঠিকানা",
}


def _box_to_rect(box: Any) -> tuple[float, float, float, float] | None:
    if box is None:
        return None

    if isinstance(box, dict):
        for key in ("bbox", "box", "bounds", "bounding_box", "coordinates"):
            if key in box:
                return _box_to_rect(box[key])

        keys = ("x", "y", "w", "h")
        if all(key in box for key in keys):
            x, y, w, h = (float(box[key]) for key in keys)
            return x, y, x + w, y + h

        keys = ("left", "top", "right", "bottom")
        if all(key in box for key in keys):
            return tuple(float(box[key]) for key in keys)

    if isinstance(box, (list, tuple)):
        if len(box) >= 4 and all(isinstance(value, (int, float)) for value in box[:4]):
            x1, y1, x2, y2 = (float(value) for value in box[:4])
            if x2 < x1 or y2 < y1:
                return x1, y1, x1 + x2, y1 + y2
            return x1, y1, x2, y2

        points = []
        for point in box:
            if isinstance(point, (list, tuple)) and len(point) >= 2:
                points.append((float(point[0]), float(point[1])))
            elif isinstance(point, dict) and "x" in point and "y" in point:
                points.append((float(point["x"]), float(point["y"])))

        if points:
            xs = [point[0] for point in points]
            ys = [point[1] for point in points]
            return min(xs), min(ys), max(xs), max(ys)

    return None


def _word_from_result(result: Any) -> dict[str, Any] | None:
    text = None
    box = None

    if isinstance(result, dict):
        for key in ("text", "word", "label", "value"):
            if key in result and result[key] is not None:
                text = str(result[key])
                break
        box = result
    elif isinstance(result, (list, tuple)):
        for item in result:
            if isinstance(item, str):
                text = item
                break
        for item in result:
            rect = _box_to_rect(item)
            if rect is not None:
                box = item
                break

    rect = _box_to_rect(box)
    if not text or rect is None:
        return None

    x1, y1, x2, y2 = rect
    return {
        "text": text.strip(),
        "x1": x1,
        "y1": y1,
        "x2": x2,
        "y2": y2,
        "cx": (x1 + x2) / 2,
        "cy": (y1 + y2) / 2,
    }


def _words(ocr_results: Any) -> list[dict[str, Any]]:
    if isinstance(ocr_results, dict):
        for key in ("results", "words", "detections", "ocr_results", "data"):
            if key in ocr_results:
                return _words(ocr_results[key])

    if not isinstance(ocr_results, (list, tuple)):
        return []

    words = []
    for result in ocr_results:
        word = _word_from_result(result)
        if word and word["text"]:
            words.append(word)
    return words


def _normalize_label(text: str) -> str:
    return text.strip().rstrip(":：।").lower()


def _is_known_label(text: str) -> bool:
    normalized = _normalize_label(text)
    return normalized in {_normalize_label(label) for label in KNOWN_LABELS}


def reconstruct_lines(ocr_results, line_tolerance=14) -> list[str]:
    words = sorted(_words(ocr_results), key=lambda item: (item["cy"], item["x1"]))
    lines: list[dict[str, Any]] = []

    for word in words:
        matching_line = None
        for line in lines:
            if abs(word["cy"] - line["cy"]) <= line_tolerance:
                matching_line = line
                break

        if matching_line is None:
            lines.append({"cy": word["cy"], "words": [word]})
        else:
            matching_line["words"].append(word)
            count = len(matching_line["words"])
            matching_line["cy"] = ((matching_line["cy"] * (count - 1)) + word["cy"]) / count

    output = []
    for line in sorted(lines, key=lambda item: item["cy"]):
        line_words = sorted(line["words"], key=lambda item: item["x1"])
        output.append(" ".join(word["text"] for word in line_words))

    return output


def full_text(ocr_results) -> str:
    return "\n".join(reconstruct_lines(ocr_results))


def find_value_near_label(
    ocr_results,
    label_texts,
    search_right=True,
    search_below=True,
    max_below_px=50,
    collect_tokens=6,
) -> str | None:
    words = _words(ocr_results)
    normalized_labels = [_normalize_label(label) for label in label_texts]

    for label in sorted(words, key=lambda item: (item["cy"], item["x1"])):
        label_text = _normalize_label(label["text"])
        if not any(label_candidate in label_text or label_text in label_candidate for label_candidate in normalized_labels):
            continue

        candidates = []
        if search_right:
            same_row = []
            for word in words:
                if word is label or _is_known_label(word["text"]):
                    continue
                if word["x1"] > label["x2"] and abs(word["cy"] - label["cy"]) <= 18:
                    same_row.append(word)
            candidates.extend(sorted(same_row, key=lambda item: item["x1"]))

        if not candidates and search_below:
            below = []
            for word in words:
                if word is label or _is_known_label(word["text"]):
                    continue
                starts_in_label_band = label["x1"] - 20 <= word["x1"] <= label["x2"] + 100
                is_below_label = 0 < word["cy"] - label["cy"] <= max_below_px
                if starts_in_label_band and is_below_label:
                    below.append(word)
            candidates.extend(sorted(below, key=lambda item: (item["y1"], item["x1"])))

        unique_candidates = list({id(word): word for word in candidates}.values())
        ordered = unique_candidates[:collect_tokens]

        if ordered:
            ordered = sorted(ordered, key=lambda item: item["x1"])
            return " ".join(word["text"].strip().strip(":：।") for word in ordered).strip()

    return None


def regex_find(text, pattern) -> str | None:
    match = re.search(pattern, text or "", flags=re.IGNORECASE)
    if not match:
        return None
    return match.group(1) if match.groups() else match.group(0)
