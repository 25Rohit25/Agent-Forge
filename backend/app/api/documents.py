import logging
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.database.connection import get_db
from backend.app.models.document import Document
from backend.app.schemas.document import SearchQuery, SearchResult
from backend.app.rag.retrieval import search_knowledge, get_indexed_chunks_count
from backend.app.rag.ingestion import ingest_default_knowledge_base_sync

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["Knowledge Base (RAG)"])

@router.get("", response_model=List[Dict[str, Any]])
async def list_documents(db: AsyncSession = Depends(get_db)):
    """List all ingested technical runbooks and documentation."""
    res = await db.execute(select(Document))
    docs = res.scalars().all()
    if not docs:
        # Fallback to in-memory files
        return [
            {"title": "Payment Service Runbook", "source": "payment-service-runbook.md", "chunks_count": 3},
            {"title": "Checkout Deadlock Postmortem", "source": "checkout-deadlock-postmortem.md", "chunks_count": 3},
            {"title": "PostgreSQL Troubleshooting", "source": "database-troubleshooting.md", "chunks_count": 3},
            {"title": "Redis Cluster Runbook", "source": "redis-cluster-runbook.md", "chunks_count": 2},
            {"title": "Auth Service Architecture", "source": "auth-service-architecture.md", "chunks_count": 2}
        ]

    return [
        {
            "id": d.id,
            "title": d.title,
            "source": d.source,
            "created_at": d.created_at.isoformat() if d.created_at else None
        }
        for d in docs
    ]

@router.post("/search")
async def search_documents_endpoint(query_in: SearchQuery):
    """Execute vector semantic similarity search across knowledge base."""
    res = search_knowledge(
        query=query_in.query,
        limit=query_in.limit,
        score_threshold=query_in.score_threshold
    )
    return res

@router.post("/ingest")
async def trigger_ingestion():
    """Trigger synchronization and ingestion of all knowledge markdown files."""
    result = ingest_default_knowledge_base_sync()
    return result
