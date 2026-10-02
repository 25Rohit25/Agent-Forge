import logging
from typing import Any, Dict
from backend.app.rag.retrieval import search_knowledge

logger = logging.getLogger(__name__)

def search_knowledge_base(query: str, limit: int = 4) -> Dict[str, Any]:
    """
    Search company technical documentation, runbooks, and past incident post-mortems using RAG.
    """
    return search_knowledge(query=query, limit=limit)
