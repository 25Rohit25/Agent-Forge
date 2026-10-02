import pytest
from backend.app.rag.chunking import chunk_markdown_text
from backend.app.rag.embeddings import get_embedding, cosine_similarity
from backend.app.rag.ingestion import ingest_default_knowledge_base_sync
from backend.app.rag.retrieval import search_knowledge

def test_chunking():
    md = """# Title\n\nIntro text.\n\n## Section 1\n\nDetailed section 1 content.\n\n## Section 2\n\nSection 2 content."""
    chunks = chunk_markdown_text(md, max_chunk_chars=300)
    assert len(chunks) >= 2
    assert any("Section 1" in c["content"] for c in chunks)

def test_embedding_cosine_similarity():
    v1 = get_embedding("database connection timeout error")
    v2 = get_embedding("database connection timeout failure")
    v3 = get_embedding("baking chocolate chip cookies in oven")

    sim_related = cosine_similarity(v1, v2)
    sim_unrelated = cosine_similarity(v1, v3)

    assert sim_related > sim_unrelated
    assert sim_related > 0.4

def test_ingestion_and_retrieval():
    ingest_res = ingest_default_knowledge_base_sync()
    assert ingest_res["total_documents"] >= 4
    assert ingest_res["total_chunks"] >= 4

    search_res = search_knowledge("payment connection pool timeout", limit=2)
    assert search_res["results_count"] > 0
    top = search_res["results"][0]
    assert "payment" in top["document_title"].lower() or "database" in top["document_title"].lower()
