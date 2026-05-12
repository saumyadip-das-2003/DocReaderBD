import os
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

db = None

def init_firebase():
    global db
    if firebase_admin._apps:
        db = firestore.client()
        return

    # Option 1: JSON string in env var (Railway)
    cred_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
    if cred_json:
        try:
            cred_dict = json.loads(cred_json)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            print('Firebase initialized from env variable')
            return
        except Exception as e:
            print(f'Firebase env init failed: {e}')

    # Option 2: JSON file (local development)
    cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'serviceAccountKey.json')
    if os.path.exists(cred_path):
        try:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            print(f'Firebase initialized from file: {cred_path}')
            return
        except Exception as e:
            print(f'Firebase file init failed: {e}')

    print('WARNING: Firebase not initialized')

init_firebase()

TEMPLATES_COLLECTION = 'templates'

async def save_template(template: dict) -> str:
    if not db:
        raise Exception('Firebase not initialized')
    doc_ref = db.collection(TEMPLATES_COLLECTION).document()
    template['id'] = doc_ref.id
    template['created_at'] = datetime.utcnow().isoformat()
    doc_ref.set(template)
    return doc_ref.id

async def get_templates(document_type: str = None) -> list:
    if not db:
        return []
    col = db.collection(TEMPLATES_COLLECTION)
    if document_type:
        query = col.where('document_type', '==', document_type)
    else:
        query = col
    docs = query.stream()
    return [doc.to_dict() for doc in docs]

async def get_template_by_id(template_id: str) -> dict:
    if not db:
        return None
    doc = db.collection(TEMPLATES_COLLECTION).document(template_id).get()
    if doc.exists:
        return doc.to_dict()
    return None

async def delete_template(template_id: str):
    if not db:
        return
    db.collection(TEMPLATES_COLLECTION).document(template_id).delete()
