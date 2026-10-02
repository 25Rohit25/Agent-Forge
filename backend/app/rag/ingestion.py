import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.core.config import settings
from backend.app.rag.chunking import chunk_markdown_text
from backend.app.rag.embeddings import get_embedding
from backend.app.rag.retrieval import clear_index, index_chunk
from backend.app.models.document import Document, DocumentChunk

logger = logging.getLogger(__name__)

def ingest_file_sync(file_path: Path) -> Dict[str, Any]:
    """Ingest a single markdown document into the in-memory retrieval index."""
    if not file_path.exists():
        return {"error": f"File {file_path} does not exist"}

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Extract title from first markdown header
    title = file_path.stem.replace("-", " ").title()
    for line in content.split("\n"):
        if line.startswith("# "):
            title = line[2:].strip()
            break

    chunks = chunk_markdown_text(content)
    ingested_chunks = []

    for c in chunks:
        vec = get_embedding(c["content"])
        chunk_record = {
            "document_title": title,
            "source": file_path.name,
            "heading": c.get("heading", ""),
            "chunk_index": c["chunk_index"],
            "content": c["content"],
            "embedding": vec
        }
        index_chunk(chunk_record)
        ingested_chunks.append(chunk_record)

    logger.info(f"Ingested '{title}' ({len(ingested_chunks)} chunks).")
    return {
        "title": title,
        "source": file_path.name,
        "chunks_count": len(ingested_chunks)
    }

def ingest_default_knowledge_base_sync() -> Dict[str, Any]:
    """Scans and ingests all markdown files from the sample-data knowledge-base directory."""
    kb_dir = settings.KNOWLEDGE_BASE_DIR
    if not kb_dir.exists():
        logger.warning(f"Knowledge base directory {kb_dir} does not exist.")
        return {"total_documents": 0, "total_chunks": 0}

    clear_index()
    docs_ingested = []
    total_chunks = 0

    for file_path in kb_dir.glob("*.md"):
        res = ingest_file_sync(file_path)
        if "chunks_count" in res:
            docs_ingested.append(res)
            total_chunks += res["chunks_count"]

    logger.info(f"Knowledge Base Ingestion Complete: {len(docs_ingested)} docs, {total_chunks} chunks.")
    return {
        "total_documents": len(docs_ingested),
        "total_chunks": total_chunks,
        "documents": docs_ingested
    }

async def sync_knowledge_to_db(session: AsyncSession) -> None:
    """Optional database persistence for knowledge documents and chunks."""
    try:
        kb_dir = settings.KNOWLEDGE_BASE_DIR
        if not kb_dir.exists():
            return

        for file_path in kb_dir.glob("*.md"):
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            title = file_path.stem.replace("-", " ").title()
            for line in content.split("\n"):
                if line.startswith("# "):
                    title = line[2:].strip()
                    break

            # Check if exists
            result = await session.execute(select(Document).where(Document.title == title))
            existing = result.scalar_one_or_none()
            if not existing:
                doc = Document(
                    title=title,
                    source=file_path.name,
                    content=content,
                    metadata_info={"filename": file_path.name}
                )
                session.add(doc)
                await session.flush()

                chunks = chunk_markdown_text(content)
                for c in chunks:
                    vec = get_embedding(c["content"])
                    chunk_obj = DocumentChunk(
                        document_id=doc.id,
                        chunk_index=c["chunk_index"],
                        content=c["content"],
                        embedding_json=vec,
                        metadata_info={"heading": c.get("heading", "")}
                    )
                    session.add(chunk_obj)
        await session.commit()
    except Exception as e:
        logger.error(f"Error syncing knowledge to DB: {e}")
        await session.rollback()
