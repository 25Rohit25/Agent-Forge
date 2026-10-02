import logging
from typing import Any, Dict, List, Optional
from backend.app.rag.embeddings import cosine_similarity, get_embedding

logger = logging.getLogger(__name__)

# Global in-memory index for fast semantic retrieval across processes
_IN_MEMORY_CHUNKS: List[Dict[str, Any]] = []

def index_chunk(chunk_record: Dict[str, Any]) -> None:
    """Add a chunk with its embedding to the in-memory retrieval index."""
    _IN_MEMORY_CHUNKS.append(chunk_record)

def clear_index() -> None:
    """Clear in-memory retrieval index."""
    global _IN_MEMORY_CHUNKS
    _IN_MEMORY_CHUNKS = []

def get_indexed_chunks_count() -> int:
    return len(_IN_MEMORY_CHUNKS)

def search_knowledge(
    query: str,
    limit: int = 4,
    score_threshold: float = 0.05
) -> Dict[str, Any]:
    """
    Execute semantic similarity search across knowledge base chunks.
    Matches natural language queries against technical runbooks and post-mortems.
    """
    if not _IN_MEMORY_CHUNKS:
        return {
            "query": query,
            "results_count": 0,
            "results": [],
            "message": "Knowledge base index is empty. Please run ingestion."
        }

    query_vec = get_embedding(query)
    scored_results: List[Dict[str, Any]] = []

    for item in _IN_MEMORY_CHUNKS:
        chunk_vec = item.get("embedding")
        if not chunk_vec:
            continue
        sim = cosine_similarity(query_vec, chunk_vec)
        scored_results.append({
            "document_title": item.get("document_title", "Technical Runbook"),
            "source": item.get("source", "knowledge-base"),
            "heading": item.get("heading", ""),
            "chunk_index": item.get("chunk_index", 0),
            "score": round(sim, 4),
            "content": item.get("content", "")
        })

    # Sort by similarity score descending
    scored_results.sort(key=lambda x: x["score"], reverse=True)
    filtered = [r for r in scored_results if r["score"] >= score_threshold]
    top_matches = filtered[:limit] if filtered else scored_results[:limit]

    return {
        "query": query,
        "results_count": len(top_matches),
        "results": top_matches
    }
