import os
from uuid import uuid4

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import credentials, firestore, storage


load_dotenv()


def _initialize_firebase() -> None:
    if firebase_admin._apps:
        return

    credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
    storage_bucket = os.getenv("FIREBASE_STORAGE_BUCKET")

    if not credentials_path:
        raise RuntimeError("FIREBASE_CREDENTIALS_PATH is not configured")

    options = {"storageBucket": storage_bucket} if storage_bucket else None
    cred = credentials.Certificate(credentials_path)
    firebase_admin.initialize_app(cred, options)


def _db():
    _initialize_firebase()
    return firestore.client()


def _bucket():
    _initialize_firebase()
    return storage.bucket()


async def save_template(template: dict, image_bytes: bytes) -> str:
    template_id = str(uuid4())
    payload = {**template, "id": template_id}

    if image_bytes:
        blob = _bucket().blob(f"templates/{template_id}/sample.jpg")
        blob.upload_from_string(image_bytes, content_type="image/jpeg")
        blob.make_public()
        payload["image_url"] = blob.public_url

    _db().collection("templates").document(template_id).set(payload)
    return template_id


async def get_templates(document_type: str | None = None) -> list[dict]:
    query = _db().collection("templates")
    if document_type:
        query = query.where("document_type", "==", document_type)

    return [doc.to_dict() | {"id": doc.id} for doc in query.stream()]


async def get_template_by_id(template_id: str) -> dict:
    doc = _db().collection("templates").document(template_id).get()
    if not doc.exists:
        return {}
    return doc.to_dict() | {"id": doc.id}


async def delete_template(template_id: str) -> None:
    _db().collection("templates").document(template_id).delete()
    bucket = _bucket()
    for blob in bucket.list_blobs(prefix=f"templates/{template_id}/"):
        blob.delete()
