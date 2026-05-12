from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from PIL import Image
import io
from services.ocr_service import run_ocr
from services.firebase_service import get_template_by_id
from services.spatial_service import extract_fields

router = APIRouter(prefix='/reader', tags=['reader'])

@router.post('/extract')
async def extract(
    file: UploadFile = File(...),
    template_id: str = Form(...),
    engine: str = Form(default='tesseract')
):
    template = await get_template_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail='Template not found')

    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert('RGB')
    
    # Pass actual image dimensions to spatial service
    image_w, image_h = image.size

    ocr_result = await run_ocr(image, engine)

    extracted = extract_fields(
        ocr_result['words'], 
        template,
        image_w,
        image_h
    )

    return {
        'document_type': template['document_type'],
        'template_name': template['template_name'],
        'fields': extracted,
        'raw_words': ocr_result['words'],
        'word_count': ocr_result['word_count']
    }
