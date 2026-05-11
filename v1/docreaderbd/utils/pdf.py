from pathlib import Path

import fitz
from PIL import Image


SUPPORTED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}


def load_document(path: str) -> list[Image.Image]:
    file_path = Path(path)
    extension = file_path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(f"Unsupported file type '{extension}'. Supported types: {supported}")

    if extension == ".pdf":
        images = []
        zoom = 200 / 72
        matrix = fitz.Matrix(zoom, zoom)

        with fitz.open(file_path) as document:
            for page in document:
                pixmap = page.get_pixmap(matrix=matrix, alpha=False)
                image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
                images.append(image)

        return images

    with Image.open(file_path) as image:
        return [image.convert("RGB")]
