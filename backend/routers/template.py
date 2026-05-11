import json

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile

from models.schemas import Template
from services import firebase_service


router = APIRouter(prefix="/template", tags=["template"])


@router.post("/save")
async def save_template(
    template: str = Form(...),
    image: UploadFile | None = File(None),
) -> dict[str, object]:
    try:
        parsed = Template(**json.loads(template))
        image_bytes = await image.read() if image else b""
        template_id = await firebase_service.save_template(parsed.dict(), image_bytes)
        return {"success": True, "template_id": template_id}
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid template JSON") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/list")
async def list_templates(
    document_type: str | None = Query(default=None),
) -> list[dict]:
    return await firebase_service.get_templates(document_type)


@router.get("/{template_id}")
async def get_template(template_id: str) -> dict:
    template = await firebase_service.get_template_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.delete("/{template_id}")
async def delete_template(template_id: str) -> dict[str, bool]:
    await firebase_service.delete_template(template_id)
    return {"success": True}
