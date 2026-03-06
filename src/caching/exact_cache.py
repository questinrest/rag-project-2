from typing import Dict, Optional, Tuple, List
_EXACT_CACHE: Dict[str, Dict[str, Tuple[str, List]]] = {}  # structure { namespace: { query: (answer, sources) } }


def get_exact_cache(query: str, namespace: str) -> Optional[Tuple[str, List]]:
    namespace_cache = _EXACT_CACHE.get(namespace, {})
    return namespace_cache.get(query.strip().lower())


def set_exact_cache(query: str, namespace: str, answer: str, sources: List):
    if namespace not in _EXACT_CACHE:
        _EXACT_CACHE[namespace] = {}
    _EXACT_CACHE[namespace][query.strip().lower()] = (answer, sources)
    print(f"Tier 1 (Exact Cache) set for query '{query}' in namespace '{namespace}'")
