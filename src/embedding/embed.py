import time
from typing import List, Dict
from pinecone import Pinecone
from src.config import (
    PINECONE_API_KEY,
    PINECONE_CLOUD,
    PINECONE_INDEX_NAME,
    PINECONE_REGION,
    PINECONE_EMBEDDING_MODEL,
    BATCH_SIZE
)

# Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)


def get_or_create_index(
    index_name: str = PINECONE_INDEX_NAME,
    cloud: str = PINECONE_CLOUD,
    region: str = PINECONE_REGION,
    embed_model: str = PINECONE_EMBEDDING_MODEL
):

    if not pc.has_index(index_name):

        print(f"Creating index: {index_name}")

        pc.create_index_for_model(
            name=index_name,
            cloud=cloud,
            region=region,
            embed={
                "model": embed_model,
                "field_map": {"text": "chunk_text"}
            }
        )

        # wait until index ready
        while not pc.describe_index(index_name).status.get("ready", False):
            time.sleep(1)

        print(f"Index '{index_name}' created successfully")

    else:
        print(f"Index '{index_name}' already exists")

    return pc.Index(index_name)


# create index once globally
INDEX = get_or_create_index()


def upsert_chunks(
    chunks: List[Dict],
    namespace: str,
    document_id: str,
    batch_size: int = BATCH_SIZE
):
    """
    Upsert chunk records into Pinecone.

    Expected chunk structure:
    {
        "id": "child-1",
        "chunk_text": "...",
        "source": "file.pdf",
        "page_no": 1,
        "parent_id": "Parent-1",
        "source_hash_value": "hash_value"
    }
    """

    records = []

    for chunk in chunks:

        record = {
            "_id": chunk["_id"],
            "chunk_text": chunk["chunk_text"],
            "source": chunk["source"],
            "page": chunk.get("page"),
            "parent_id": chunk["parent_id"],
            "source_hash_value": chunk["source_hash_value"],
            "document_id": document_id
        }

        records.append(record)

    # batch upsert
    for i in range(0, len(records), batch_size):

        batch = records[i:i + batch_size]

        INDEX.upsert_records(
            namespace=namespace,
            records=batch
        )
    print(
        f"{len(records)} chunks successfully inserted into "
        f"namespace '{namespace}' in index '{PINECONE_INDEX_NAME}'"
    )

    return len(records)