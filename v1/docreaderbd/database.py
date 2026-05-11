import io
import json
import os
from typing import Any

import psycopg2
from dotenv import load_dotenv
from PIL import Image
from psycopg2.extras import RealDictCursor


def get_connection():
    load_dotenv()
    try:
        return psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "docreaderbd"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
        )
    except Exception as exc:
        raise ConnectionError(f"Database connection failed: {exc}") from exc


def init_db():
    documents_query = """
    CREATE TABLE IF NOT EXISTS documents (
        id              SERIAL PRIMARY KEY,
        created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        document_type   VARCHAR(50),
        extraction_mode VARCHAR(20),
        filename        VARCHAR(255),
        file_size_kb    FLOAT,
        original_image  BYTEA,
        annotated_image BYTEA,
        fields_json     JSONB,
        ocr_word_count  INTEGER
    );
    """
    nid_query = """
    CREATE TABLE IF NOT EXISTS nid_cards (
        id              SERIAL PRIMARY KEY,
        document_id     INTEGER REFERENCES documents(id) ON DELETE CASCADE,
        created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        bangla_name     TEXT,
        english_name    TEXT,
        husband_or_father_name_bn TEXT,
        mother_name_bn  TEXT,
        date_of_birth   TEXT,
        nid_number      TEXT,
        blood_group     TEXT,
        address         TEXT,
        fields_json     JSONB
    );
    """
    nid_migration_query = """
    ALTER TABLE nid_cards
    ADD COLUMN IF NOT EXISTS husband_or_father_name_bn TEXT;

    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'nid_cards'
              AND column_name = 'father_name_bn'
        ) THEN
            EXECUTE 'UPDATE nid_cards
                     SET husband_or_father_name_bn = father_name_bn
                     WHERE husband_or_father_name_bn IS NULL';
        END IF;
    END $$;
    """
    birth_query = """
    CREATE TABLE IF NOT EXISTS birth_certificates (
        id                  SERIAL PRIMARY KEY,
        document_id         INTEGER REFERENCES documents(id) ON DELETE CASCADE,
        created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        birth_reg_number    TEXT,
        bangla_name         TEXT,
        english_name        TEXT,
        gender              TEXT,
        mother_name_bn      TEXT,
        mother_name_en      TEXT,
        father_name_bn      TEXT,
        father_name_en      TEXT,
        date_of_birth       TEXT,
        birthplace          TEXT,
        present_address     TEXT,
        permanent_address   TEXT,
        fields_json         JSONB
    );
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(documents_query)
            cur.execute(nid_query)
            cur.execute(nid_migration_query)
            cur.execute(birth_query)
        conn.commit()


def _to_bytes(value: Any) -> bytes | None:
    if value is None:
        return None
    if isinstance(value, bytes):
        return value
    if isinstance(value, Image.Image):
        buffer = io.BytesIO()
        value.save(buffer, format="PNG")
        return buffer.getvalue()
    raise TypeError(f"Unsupported image type: {type(value)!r}")


def save_document(
    document_type,
    extraction_mode,
    filename,
    file_size_kb,
    original_image_bytes,
    annotated_image_bytes,
    fields_dict,
    ocr_word_count,
):
    query = """
    INSERT INTO documents (
        document_type, extraction_mode, filename, file_size_kb,
        original_image, annotated_image, fields_json, ocr_word_count
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s)
    RETURNING id;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                query,
                (
                    document_type,
                    extraction_mode,
                    filename,
                    file_size_kb,
                    psycopg2.Binary(_to_bytes(original_image_bytes)),
                    psycopg2.Binary(_to_bytes(annotated_image_bytes)),
                    json.dumps(fields_dict or {}, ensure_ascii=False),
                    ocr_word_count,
                ),
            )
            record_id = cur.fetchone()[0]
        conn.commit()
    return record_id


def _field(fields: dict, *names: str):
    normalized = {str(key).lower(): value for key, value in (fields or {}).items()}
    for name in names:
        value = normalized.get(name.lower())
        if value not in (None, ""):
            return value
    return None


def save_nid_record(document_id, fields_dict):
    query = """
    INSERT INTO nid_cards (
        document_id, bangla_name, english_name, husband_or_father_name_bn, mother_name_bn,
        date_of_birth, nid_number, blood_group, address, fields_json
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
    RETURNING id;
    """
    fields = fields_dict or {}
    values = (
        document_id,
        _field(fields, "bangla_name", "name_bn", "bn_name"),
        _field(fields, "english_name", "name_en", "eng_name"),
        _field(
            fields,
            "husband_or_father_name_bn",
            "husband_name_bn",
            "husbands_name_bangla",
            "father_name_bn",
            "fathers_name_bangla",
            "father_bn",
        ),
        _field(fields, "mother_name_bn", "mother_name_bangla", "mother_bn"),
        _field(fields, "date_of_birth", "dob"),
        _field(fields, "nid_number", "nid_no", "id_number"),
        _field(fields, "blood_group"),
        _field(fields, "address"),
        json.dumps(fields, ensure_ascii=False),
    )
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, values)
            record_id = cur.fetchone()[0]
        conn.commit()
    return record_id


def save_birth_certificate_record(document_id, fields_dict):
    query = """
    INSERT INTO birth_certificates (
        document_id, birth_reg_number, bangla_name, english_name, gender,
        mother_name_bn, mother_name_en, father_name_bn, father_name_en,
        date_of_birth, birthplace, present_address, permanent_address, fields_json
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
    RETURNING id;
    """
    fields = fields_dict or {}
    values = (
        document_id,
        _field(fields, "birth_reg_number", "birth_registration_number", "registration_number"),
        _field(fields, "bangla_name", "name_bn"),
        _field(fields, "english_name", "name_en"),
        _field(fields, "gender", "sex"),
        _field(fields, "mother_name_bn", "mother_name_bangla"),
        _field(fields, "mother_name_en", "mother_name_english"),
        _field(fields, "father_name_bn", "father_name_bangla"),
        _field(fields, "father_name_en", "father_name_english"),
        _field(fields, "date_of_birth", "dob"),
        _field(fields, "birthplace", "birth_place", "place_of_birth"),
        _field(fields, "present_address"),
        _field(fields, "permanent_address"),
        json.dumps(fields, ensure_ascii=False),
    )
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, values)
            record_id = cur.fetchone()[0]
        conn.commit()
    return record_id


def get_all_documents():
    query = """
    SELECT id, created_at, document_type, extraction_mode,
           filename, file_size_kb, ocr_word_count
    FROM documents
    ORDER BY created_at DESC;
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            return [dict(row) for row in cur.fetchall()]


def get_document_by_id(doc_id):
    query = "SELECT * FROM documents WHERE id = %s;"
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (doc_id,))
            row = cur.fetchone()
            return dict(row) if row else None


def delete_document(doc_id):
    query = "DELETE FROM documents WHERE id = %s;"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (doc_id,))
            deleted = cur.rowcount
        conn.commit()
    return deleted


def get_all_nid_cards():
    query = """
    SELECT id, document_id, created_at, bangla_name, english_name, husband_or_father_name_bn,
           mother_name_bn, date_of_birth, nid_number, blood_group, address
    FROM nid_cards
    ORDER BY created_at DESC;
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            return [dict(row) for row in cur.fetchall()]


def get_all_birth_certificates():
    query = """
    SELECT id, document_id, created_at, birth_reg_number, bangla_name, english_name,
           gender, mother_name_bn, mother_name_en, father_name_bn, father_name_en,
           date_of_birth, birthplace, present_address, permanent_address
    FROM birth_certificates
    ORDER BY created_at DESC;
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            return [dict(row) for row in cur.fetchall()]
