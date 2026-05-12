from fastapi import APIRouter, UploadFile, File, Form
from PIL import Image
import io
from services.ocr_service import run_ocr

router = APIRouter(prefix='/ocr', tags=['ocr'])

@router.post('/process')
async def process_ocr(
    file: UploadFile = File(...),
    engine: str = Form(default='shobdoocr')
):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert('RGB')
    result = await run_ocr(image, engine)
    return result
