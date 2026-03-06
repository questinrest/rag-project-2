import numpy as np
from typing import Dict, Optional, List
from src.caching.semantic_cache import get_embedding, cosine_similarity
from src.config import RETRIEVAL_CACHE_THRESHOLD

_RETRIEVAL_CACHE: Dict[str, List[Dict]] = {} # structure: { namespace: [ { "query": str, "embedding": np.ndarray, "chunks": List[Dict] } ] }


def get_retrieval_cache(
    query: str, 
    namespace: str, 
    threshold: float = RETRIEVAL_CACHE_THRESHOLD
) -> Optional[List[Dict]]:
    namespace_cache = _RETRIEVAL_CACHE.get(namespace, [])
    if not namespace_cache:
        return None
    query_emb = get_embedding(query)

    best_match = None
    highest_sim = -1.0

    for cached_item in namespace_cache:
        sim = cosine_similarity(query_emb, cached_item["embedding"])
        if sim > highest_sim:
            highest_sim = sim
            best_match = cached_item

    if best_match and highest_sim >= threshold:
        print(f"Tier 3 (Retrieval Cache) hit! Similarity: {highest_sim:.4f}")
        return best_match["chunks"]

    return None


def set_retrieval_cache(query: str, namespace: str, chunks: List[Dict]):
    if namespace not in _RETRIEVAL_CACHE:
        _RETRIEVAL_CACHE[namespace] = []
        
    query_emb = get_embedding(query)
    
    _RETRIEVAL_CACHE[namespace].append({
        "query": query,
        "embedding": query_emb,
        "chunks": chunks
    })
    print(f"Tier 3 (Retrieval Cache) set for retrieved chunks in namespace '{namespace}'")
