from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from services.firebase_service import (
    save_template, get_templates,
    get_template_by_id, delete_template
)

router = APIRouter(prefix='/template', tags=['template'])

class TemplateField(BaseModel):
    field_name: str
    field_type: str
    for_label: str = ''
    box: List[int]
    word: str

class TemplateCreate(BaseModel):
    template_name: str
    document_type: str
    image_width: int
    image_height: int
    fields: List[TemplateField]

@router.post('/save')
async def save(template: TemplateCreate):
    template_dict = template.dict()
    template_id = await save_template(template_dict)
    return {'success': True, 'template_id': template_id}

@router.get('/list')
async def list_templates(document_type: Optional[str] = None):
    templates = await get_templates(document_type)
    return {'templates': templates}

@router.get('/{template_id}')
async def get_template(template_id: str):
    template = await get_template_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail='Template not found')
    return template

@router.delete('/{template_id}')
async def remove_template(template_id: str):
    await delete_template(template_id)
    return {'success': True}
