import numpy as np
from typing import Dict, Optional, Tuple, List
from sentence_transformers import SentenceTransformer
from src.config import SEMANTIC_CACHE_THRESHOLD
from src.utils.logger import get_logger

logger = get_logger(__name__)

embedder = SentenceTransformer('all-MiniLM-L6-v2')

# structure: { namespace: [ { "query": str, "embedding": np.ndarray, "answer": str, "sources": List } ] }
_SEMANTIC_CACHE: Dict[str, List[Dict]] = {}


def get_embedding(text: str) -> np.ndarray:
    return embedder.encode(text)


def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    return dot_product / (norm_v1 * norm_v2)


def get_semantic_cache(
    query: str, 
    namespace: str, 
    threshold: float = SEMANTIC_CACHE_THRESHOLD
) -> Tuple[Optional[str], Optional[List], np.ndarray]:
    query_emb = get_embedding(query)
    
    namespace_cache = _SEMANTIC_CACHE.get(namespace, [])
    if not namespace_cache:
        return None, None, query_emb

    best_match = None
    highest_sim = -1.0
    for cached_item in namespace_cache:
        sim = cosine_similarity(query_emb, cached_item["embedding"])
        if sim > highest_sim:
            highest_sim = sim
            best_match = cached_item
    if best_match and highest_sim >= threshold:
        print(f"Tier 2 (Semantic Cache) hit! Similarity: {highest_sim:.4f}")
        return best_match["answer"], best_match["sources"], query_emb

    return None, None, query_emb


def set_semantic_cache(query: str, namespace: str, answer: str, sources: List, query_emb: np.ndarray = None):
    if namespace not in _SEMANTIC_CACHE:
        _SEMANTIC_CACHE[namespace] = []
        
    if query_emb is None:
        query_emb = get_embedding(query)
        
    _SEMANTIC_CACHE[namespace].append({
        "query": query,
        "embedding": query_emb,
        "answer": answer,
        "sources": sources
    })
    logger.info(f"Tier 2 (Semantic Cache) set for query in namespace '{namespace}'")
