import logging
from typing import Any, Dict
from backend.app.rag.retrieval import search_knowledge
from backend.app.tools.registry import register_tool_handler

logger = logging.getLogger(__name__)

def search_knowledge_base(query: str, limit: int = 4) -> Dict[str, Any]:
    """
    Search company technical documentation, runbooks, and past incident post-mortems using RAG.
    """
    return search_knowledge(query=query, limit=limit)

# Register handler into central registry
register_tool_handler("search_knowledge_base", search_knowledge_base)
