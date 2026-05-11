from math import hypot
from typing import Any


def _center(box: list[int]) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def extract_fields(words: list, template: dict) -> dict:
    template_width = max(float(template.get("image_width", 1)), 1.0)
    template_height = max(float(template.get("image_height", 1)), 1.0)
    fields = template.get("fields", [])
    value_fields = [field for field in fields if field.get("field_type") == "value"]

    if not words:
        return {field.get("field_name", ""): "" for field in value_fields}

    current_width = max(float(max(word["box"][2] for word in words if word.get("box"))), 1.0)
    current_height = max(float(max(word["box"][3] for word in words if word.get("box"))), 1.0)
    result: dict[str, Any] = {}

    for field in value_fields:
        box = field.get("box", [0, 0, 0, 0])
        cx, cy = _center(box)
        scaled_center = (
            (cx / template_width) * current_width,
            (cy / template_height) * current_height,
        )

        closest_word = min(
            words,
            key=lambda word: hypot(
                _center(word.get("box", [0, 0, 0, 0]))[0] - scaled_center[0],
                _center(word.get("box", [0, 0, 0, 0]))[1] - scaled_center[1],
            ),
        )
        result[field.get("field_name", field.get("for_label", ""))] = closest_word.get("text", "")

    return result
