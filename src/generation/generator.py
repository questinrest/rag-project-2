from typing import List, Dict
from langchain_groq import ChatGroq
from langsmith import traceable
from src.config import (
    OPENAI_MODEL_GROQ,
    TEMPERATURE,
    MAX_TOKENS,
    GROQ_API_KEY
)


llm = ChatGroq(
    model=OPENAI_MODEL_GROQ,
    api_key=GROQ_API_KEY,
    temperature=TEMPERATURE,
    max_tokens=MAX_TOKENS
)


SYSTEM_PROMPT = """You are a helpful assistant that excels in answering questions based on the given context.
You always use the context below to answer. If the answer is not in the context, say "I don't have enough information to answer that."

CITATION RULES:
- Each context chunk is labeled [0], [1], [2], etc. with its source document and page number(s).
- When you use information from a chunk, cite it inline like [0], [1], etc.
- At the end of your answer, add a "References" section listing each cited source with page numbers.
- Format: [n] source_filename, p.X

Example: The offer letter must be accepted within ten days of issuance [0], and it remains valid for three months [1].

References:
[0] HR Handbook 2025.pdf, p.10
[1] HR Handbook 2025.pdf, p.11
"""


from src.config import parent_store_collection

def context_build(retrieved_chunks: List[Dict], namespace: str) -> str:
    sections = []
    
    # Extract unique parent IDs
    parent_ids = set()
    for chunk in retrieved_chunks:
        parent_id = chunk.get("parent_id")
        if parent_id:
            parent_ids.add(parent_id)
            
    # Retrieve unique parent chunks from MongoDB
    if parent_ids:
        parent_docs = parent_store_collection.find({
            "parent_id": {"$in": list(parent_ids)},
            "namespace": namespace
        })
        
        # Create a lookup for quick access
        parent_lookup = {doc["parent_id"]: doc["text"] for doc in parent_docs}
        
        # Build context using unique parent chunks
        for idx, parent_id in enumerate(parent_lookup):
            parent_text = parent_lookup[parent_id]
            # Try to find a source/page from the child chunks that match this parent
            source = "unknown"
            page = ""
            for chunk in retrieved_chunks:
                if chunk.get("parent_id") == parent_id:
                    source = chunk.get("source", "unknown")
                    page = chunk.get("page", "")
                    break
                    
            page_label = f", p.{page}" if page else ""
            sections.append(f"[{idx}] (source: {source}{page_label})\n{parent_text}")
            
    # Fallback to child chunks if no parent IDs were found (e.g. recursive_character chunking)
    if not sections:
        for idx, chunk in enumerate(retrieved_chunks):
            chunk_text = chunk.get("chunk_text", "")
            page = chunk.get("page", "")
            source = chunk.get("source", "unknown")

            page_label = f", p.{page}" if page else ""
            sections.append(f"[{idx}] (source: {source}{page_label})\n{chunk_text}")

    return "\n\n".join(sections)


@traceable(run_type="chain", name="Generate Final Answer")
def generate_answer(query: str, chunks: List[Dict], namespace: str) -> str:
    context = context_build(chunks, namespace)
    messages = [
        ("system", SYSTEM_PROMPT),
        ("human", f"Context:\n{context}\n\n---\nQuestion: {query}"),
    ]

    model_response = llm.invoke(messages)
    return model_response.content