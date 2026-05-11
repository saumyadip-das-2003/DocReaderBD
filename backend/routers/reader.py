from io import BytesIO

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from PIL import Image

from models.schemas import ExtractionResult
from services import firebase_service, spatial_service
from services.ocr_service import run_ocr


router = APIRouter(prefix="/reader", tags=["reader"])


@router.post("/extract", response_model=ExtractionResult)
async def extract_document(
    file: UploadFile = File(...),
    template_id: str = Form(...),
) -> ExtractionResult:
    try:
        template = await firebase_service.get_template_by_id(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        image_bytes = await file.read()
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        ocr_result = await run_ocr(image, "shobdoocr")
        fields = spatial_service.extract_fields(ocr_result["words"], template)

        return ExtractionResult(
            document_type=template.get("document_type", "custom"),
            template_name=template.get("template_name", ""),
            fields=fields,
            raw_words=ocr_result["words"],
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
