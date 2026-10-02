import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.database.connection import init_db
from backend.app.rag.ingestion import ingest_default_knowledge_base_sync

@pytest.fixture(autouse=True)
async def init_test_setup():
    await init_db()
    ingest_default_knowledge_base_sync()

@pytest.mark.asyncio
async def test_root_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/")
        assert resp.status_code == 200
        assert "AgentForge" in resp.json()["message"]

@pytest.mark.asyncio
async def test_health_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

        resp_services = await client.get("/api/health/services")
        assert resp_services.status_code == 200
        assert "overall_status" in resp_services.json()

@pytest.mark.asyncio
async def test_tools_catalog():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/tools")
        assert resp.status_code == 200
        tools = resp.json()
        assert len(tools) >= 5
        tool_names = [t["name"] for t in tools]
        assert "get_service_health" in tool_names
        assert "search_logs" in tool_names
        assert "search_knowledge_base" in tool_names

@pytest.mark.asyncio
async def test_chat_investigation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        req_payload = {
            "message": "Why is payment-service slow? Check logs and open a GitHub issue."
        }
        resp = await client.post("/api/chat", json=req_payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "COMPLETED"
        assert len(data["tools_used"]) >= 3
        assert "payment-service" in data["response"].lower()
        assert data["workflow_id"] is not None

@pytest.mark.asyncio
async def test_documents_search():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/documents/search", json={"query": "connection pool timeout", "limit": 2})
        assert resp.status_code == 200
        data = resp.json()
        assert data["results_count"] > 0
