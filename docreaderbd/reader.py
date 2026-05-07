import os

from dotenv import load_dotenv
from PIL import Image

from .classifier import classify
from .extractors.base import full_text
from .extractors.birth_cert import extract_birth_cert
from .extractors.llm import llm_extract
from .extractors.nid import extract_nid
from .utils.pdf import load_document


class DocReader:
    def __init__(self, groq_api_key=None):
        load_dotenv()
        groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        if groq_api_key:
            os.environ["GROQ_API_KEY"] = groq_api_key

        from shobdoocr import OCR

        self.ocr = OCR()

    def read(self, file_path, page=0, verbose=False) -> dict:
        images = load_document(file_path)
        if page < 0 or page >= len(images):
            raise IndexError(f"Page index {page} out of range for document with {len(images)} page(s)")

        image = images[page]
        ocr_results = self.ocr.read(image, verbose=verbose)
        text = full_text(ocr_results)
        doc_type = classify(text)

        if doc_type == "nid":
            fields = extract_nid(ocr_results)
            mode = "spatial"
        elif doc_type == "birth_cert":
            fields = extract_birth_cert(ocr_results)
            mode = "spatial"
        else:
            fields = llm_extract(ocr_results, doc_type_hint=doc_type)
            mode = "llm"

        return {
            "document_type": doc_type,
            "extraction_mode": mode,
            "fields": fields,
            "ocr_results": ocr_results,
            "page_count": len(images),
        }

    def read_all_pages(self, file_path) -> list:
        images = load_document(file_path)
        return [self.read(file_path, page=page) for page in range(len(images))]

    def visualize(self, file_path_or_image, result, save_path=None) -> Image.Image:
        if isinstance(file_path_or_image, Image.Image):
            image = file_path_or_image.convert("RGB")
        else:
            image = load_document(file_path_or_image)[0]

        annotated = self.ocr.visualize(image, result["ocr_results"])
        if not isinstance(annotated, Image.Image):
            annotated = Image.fromarray(annotated).convert("RGB")

        if save_path:
            annotated.save(save_path)

        return annotated
