import json
import logging
from typing import Any, AsyncGenerator, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse
from backend.app.database.connection import get_db
from backend.app.schemas.chat import ChatRequest, ChatResponse, ToolCallInfo
from backend.app.agents.developer_agent import DeveloperAgent
from backend.app.services.workflow_service import persist_workflow_run
from backend.app.services.redis_service import redis_service
from backend.app.api.auth import get_current_user
from backend.app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Agent Chat & Streaming"])

@router.post("", response_model=ChatResponse)
async def chat_endpoint(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Apply rate limiting
    user_id = current_user.id if current_user else "anonymous"
    if not redis_service.check_rate_limit(user_id, max_requests=60, window_seconds=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Maximum 60 requests per minute."
        )

    agent = DeveloperAgent(conversation_id=req.conversation_id)
    state = await agent.run(req.message)

    # Persist workflow run to DB and cache
    await persist_workflow_run(db, state)

    # Map tool execution info
    tool_infos = [
        ToolCallInfo(
            tool_name=s.tool_name,
            arguments=s.tool_input,
            output=s.tool_output,
            execution_time_ms=s.execution_time_ms,
            status=s.status
        )
        for s in state.steps
    ]

    return ChatResponse(
        conversation_id=state.conversation_id,
        workflow_id=state.workflow_id,
        response=state.final_response or "Investigation completed.",
        status=state.status,
        steps_count=len(state.steps),
        tools_used=[s.tool_name for s in state.steps],
        tool_executions=tool_infos
    )

@router.get("/stream")
async def chat_stream_endpoint(
    message: str = Query(..., min_length=1),
    conversation_id: str = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Server-Sent Events (SSE) streaming endpoint for live agent workflow tracking.
    """
    agent = DeveloperAgent(conversation_id=conversation_id)

    async def event_generator() -> AsyncGenerator[Dict[str, Any], None]:
        final_state = None
        async for event in agent.stream(message):
            yield {
                "event": event["event"],
                "data": json.dumps(event)
            }
        # Final persistence on done
        # We can run full run persistence in background if needed

    return EventSourceResponse(event_generator())
