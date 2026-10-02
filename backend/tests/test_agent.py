import pytest
from backend.app.agents.developer_agent import DeveloperAgent
from backend.app.rag.ingestion import ingest_default_knowledge_base_sync

@pytest.fixture(autouse=True)
def setup_rag():
    ingest_default_knowledge_base_sync()

@pytest.mark.asyncio
async def test_agent_investigation_workflow():
    agent = DeveloperAgent()
    prompt = "Why is payment-service failing, check the logs, find related documentation, and create a GitHub issue."
    state = await agent.run(prompt)

    assert state.status == "COMPLETED"
    assert len(state.steps) >= 3
    tool_names = [s.tool_name for s in state.steps]
    assert "get_service_health" in tool_names
    assert "search_logs" in tool_names
    assert "search_knowledge_base" in tool_names
    assert "create_github_issue" in tool_names
    assert state.final_response is not None
    assert "payment-service" in state.final_response.lower()

@pytest.mark.asyncio
async def test_agent_streaming():
    agent = DeveloperAgent()
    prompt = "Check checkout-service health and search logs."
    events = []
    async for event in agent.stream(prompt):
        events.append(event)

    event_types = [e["event"] for e in events]
    assert "start" in event_types
    assert "plan" in event_types
    assert "tool_start" in event_types
    assert "tool_complete" in event_types
    assert "final_response" in event_types
    assert "done" in event_types
