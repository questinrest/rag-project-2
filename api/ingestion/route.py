from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from api.ingestion.datamodels import IngestResponse
from fastapi.security import HTTPBearer
import hashlib
import os
import uuid
from datetime import datetime
from api.ingestion.services import get_current_user
from src.embedding.embed import upsert_chunks
from src.chunking.parent_child import ingest
from src.config import document_collection
from pathlib import Path
import shutil

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload", response_model=IngestResponse)
async def upload_document(
    file: UploadFile = File(...),
    username: str = Depends(get_current_user)
):
    allowed_types = {".pdf", ".txt"}
    suffix = Path(file.filename).suffix.lower()

    if suffix not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type"
        )

    # Save file
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    namespace = username

    # Run chunking
    records, parents = ingest(file_path)
    source_hash = records[0]["source_hash_value"]

    # Check for existing document in MongoDB
    existing_doc = document_collection.find_one({
        "namespace": namespace,
        "filename": file.filename,
        "is_active": True
    })

    if existing_doc:
        if existing_doc["source_hash"] == source_hash:
            return {
                "message": "Document already up to date",
                "file": file.filename,
                "chunks_inserted": 0,
                "namespace": namespace
            }
        
        # Mark old version as inactive
        document_collection.update_one(
            {"_id": existing_doc["_id"]},
            {"$set": {"is_active": False}}
        )

    # Create new document record
    document_id = str(uuid.uuid4())
    doc_record = {
        "document_id": document_id,
        "namespace": namespace,
        "filename": file.filename,
        "source_hash": source_hash,
        "uploaded_at": datetime.utcnow(),
        "is_active": True
    }
    document_collection.insert_one(doc_record)

    # Upsert with document_id
    inserted = upsert_chunks(records, namespace, document_id)

    return {
        "message": "Document uploaded and indexed successfully",
        "file": file.filename,
        "chunks_inserted": inserted,
        "namespace": namespace
    }