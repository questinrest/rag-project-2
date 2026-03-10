from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from api.ingestion.datamodels import IngestResponse
from fastapi.security import HTTPBearer
import hashlib
import os
import uuid
from datetime import datetime
from api.ingestion.services import get_current_user
from src.embedding.embed import upsert_chunks
from src.chunking.parent_child import ingest as parent_child_ingest
from src.chunking.recursive_character import ingest as recursive_character_ingest
from src.config import document_collection, CHUNKING_STRATEGY
from pathlib import Path
import shutil
from src.utils.logger import get_logger

logger = get_logger(__name__)

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
        logger.warning(f"Upload failed: Unsupported file type '{suffix}' from user '{username}'")
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type"
        )

    # Save file
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    namespace = username
    logger.info(f"User '{username}' started processing file: {file.filename} with strategy: {CHUNKING_STRATEGY}")

    # Run chunking based on strategy
    if CHUNKING_STRATEGY == "recursive_character":
        records = recursive_character_ingest(file_path)
    else:
        records, parents = parent_child_ingest(file_path)
    source_hash = records[0]["source_hash_value"]

    from src.config import parent_store_collection
    
    # Check for existing document in MongoDB
    existing_doc = document_collection.find_one({
        "namespace": namespace,
        "filename": file.filename,
        "is_active": True
    })

    if existing_doc:
        if existing_doc["source_hash"] == source_hash:
            logger.info(f"Skipping upload: Document '{file.filename}' for user '{username}' is already up to date.")
            return {
                "message": "Document already up to date",
                "file": file.filename,
                "chunks_inserted": 0,
                "namespace": namespace
            }
        
        logger.info(f"New version detected for '{file.filename}'. Archiving old version (ID: {existing_doc['document_id']}).")
        # Mark old version as inactive
        document_collection.update_one(
            {"_id": existing_doc["_id"]},
            {"$set": {"is_active": False}}
        )

    # Create new document record
    document_id = str(uuid.uuid4())
    logger.info(f"Generating new document ID: {document_id}")
    doc_record = {
        "document_id": document_id,
        "namespace": namespace,
        "filename": file.filename,
        "source_hash": source_hash,
        "uploaded_at": datetime.utcnow(),
        "is_active": True
    }
    document_collection.insert_one(doc_record)

    # Store parents in MongoDB if parent_child strategy
    if CHUNKING_STRATEGY == "parent_child" and parents:
        logger.info(f"Storing {len(parents)} parent chunks into MongoDB for document '{document_id}'")
        parent_records = []
        for parent_id, parent_text in parents.items():
            parent_records.append({
                "parent_id": parent_id,
                "text": parent_text,
                "namespace": namespace,
                "document_id": document_id
            })
        if parent_records:
            parent_store_collection.insert_many(parent_records)

    # Upsert with document_id
    logger.info(f"Upserting {len(records)} chunks into Pinecone namespace '{namespace}'")
    inserted = upsert_chunks(records, namespace, document_id)
    
    logger.info(f"Successfully processed and embedded '{file.filename}' for user '{username}'.")

    return {
        "message": "Document uploaded and indexed successfully",
        "file": file.filename,
        "chunks_inserted": inserted,
        "namespace": namespace
    }