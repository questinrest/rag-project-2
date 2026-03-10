from typing import List, Dict
from src.retrieval.retriever import search_vector_db
from src.retrieval.reranker import search_vector_db_reranker
from src.generation.generator import generate_answer
from api.generation.datamodels import Source


def retrieve_chunks(query: str, namespace: str, rerank: bool) -> List[Dict]:
    if rerank:
        return search_vector_db_reranker(query=query, namespace=namespace)
    return search_vector_db(query=query, namespace=namespace)


def build_sources(chunks: List[Dict]) -> List[Source]:
    sources = []
    for chunk in chunks:
        page = chunk.get("page")
        sources.append(Source(
            source=chunk.get("source", "unknown"),
            page=str(int(page)) if page else None
        ))
    return sources


def get_answer(query: str, chunks: List[Dict], namespace: str) -> str:
    return generate_answer(query=query, chunks=chunks, namespace=namespace)
