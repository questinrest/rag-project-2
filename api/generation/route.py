from fastapi import APIRouter, Depends, HTTPException
from api.generation.datamodels import QueryRequest, QueryResponse
from api.generation.services import retrieve_chunks, build_sources, get_answer
from api.ingestion.services import get_current_user
from src.caching.exact_cache import get_exact_cache, set_exact_cache
from src.caching.semantic_cache import get_semantic_cache, set_semantic_cache
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
def query(request: QueryRequest, username: str = Depends(get_current_user)):
    try:
        namespace = username
        logger.info(f"User '{username}' initiated query: '{request.query}' (Rerank: {request.rerank})")
        
        # tier 1 exact
        
        exact_hit = get_exact_cache(request.query, namespace)
        if exact_hit:
            logger.info("Exact cache hit!")
            answer, sources = exact_hit
            return QueryResponse(answer=answer, reference=sources, rerank=request.rerank, cache_tier="Tier 1 (Exact)")

        # tier 2 semantic
        semantic_hit_ans, semantic_hit_src, query_emb = get_semantic_cache(request.query, namespace)
        if semantic_hit_ans:
            logger.info("Semantic cache hit!")
            return QueryResponse(answer=semantic_hit_ans, reference=semantic_hit_src, rerank=request.rerank, cache_tier="Tier 2 (Semantic)")

        # tier 3 retrieval
        from src.caching.retrieval_cache import get_retrieval_cache, set_retrieval_cache
        retrieval_hit = get_retrieval_cache(request.query, namespace, query_emb=query_emb)
        
        cache_tier_used = "None"
        if retrieval_hit is not None:
            logger.info("Retrieval cache hit!")
            related_docs = retrieval_hit
            cache_tier_used = "Tier 3 (Retrieval)"
        else:
            # full pipeline
            related_docs = retrieve_chunks(
                query=request.query,
                namespace=namespace,
                rerank=request.rerank
            )
            logger.info(f"Retrieved {len(related_docs)} relevant chunks for user '{username}'.")
            set_retrieval_cache(request.query, namespace, related_docs, query_emb=query_emb)
            
        sources = build_sources(related_docs)
        answer = get_answer(query=request.query, chunks=related_docs, namespace=namespace)
        logger.info(f"Successfully generated answer for user '{username}' query.")
        
        # settin Exact and Semantic Caches
        set_exact_cache(request.query, namespace, answer, sources)
        set_semantic_cache(request.query, namespace, answer, sources, query_emb=query_emb)
        
        return QueryResponse(
            answer=answer,
            reference=sources,
            rerank=request.rerank,
            cache_tier=cache_tier_used
        )
    except Exception as e:
        logger.error(f"Error during query execution for user '{username}': {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error generating answer: {str(e)}"
        )