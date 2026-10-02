import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.app.rag.ingestion import ingest_default_knowledge_base_sync
from backend.app.rag.retrieval import search_knowledge

def main():
    print("=" * 60)
    print("AgentForge - Technical Knowledge Ingestion")
    print("=" * 60)
    result = ingest_default_knowledge_base_sync()
    print(f"Total Documents Ingested: {result['total_documents']}")
    print(f"Total Chunks Generated:  {result['total_chunks']}")

    # Run quick test query
    test_q = "payment database connection pool timeout"
    print(f"\nTesting RAG Retrieval for: '{test_q}'")
    search_res = search_knowledge(test_q, limit=2)
    print(f"Matches found: {search_res['results_count']}")
    for idx, match in enumerate(search_res["results"], 1):
        print(f"  [{idx}] {match['document_title']} (score: {match['score']})")
        print(f"      {match['content'][:150]}...")
    print("=" * 60)

if __name__ == "__main__":
    main()
