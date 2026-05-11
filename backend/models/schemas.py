from pydantic import BaseModel


class OCRRequest(BaseModel):
    engine: str = "shobdoocr"  # shobdoocr | tesseract | easyocr


class WordBox(BaseModel):
    text: str
    box: list[int]  # [x1, y1, x2, y2]
    script: str = "unknown"
    conf: float = 0.0


class OCRResponse(BaseModel):
    text: str
    words: list[WordBox]
    word_count: int
    engine: str


class TemplateField(BaseModel):
    field_name: str  # e.g. "name", "father", "nid_no"
    field_type: str  # "label" or "value"
    for_label: str = ""  # if value, which label it belongs to
    box: list[int]  # [x1, y1, x2, y2] position on template image
    word: str  # the actual word text


class Template(BaseModel):
    template_name: str
    document_type: str  # nid | birth_cert | invoice | custom
    fields: list[TemplateField]
    image_width: int
    image_height: int


class ExtractionResult(BaseModel):
    document_type: str
    template_name: str
    fields: dict
    raw_words: list[WordBox]
