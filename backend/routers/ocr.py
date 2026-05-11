from io import BytesIO

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from PIL import Image

from models.schemas import OCRResponse
from services.ocr_service import run_ocr


router = APIRouter(prefix="/ocr", tags=["ocr"])


@router.post("/process", response_model=OCRResponse)
async def process_ocr(
    file: UploadFile = File(...),
    engine: str = Form("shobdoocr"),
) -> OCRResponse:
    try:
        image_bytes = await file.read()
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        result = await run_ocr(image, engine)
        return OCRResponse(**result)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
