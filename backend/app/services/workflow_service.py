import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.models.workflow import Workflow
from backend.app.models.tool_execution import ToolExecution
from backend.app.models.message import Message
from backend.app.models.conversation import Conversation
from backend.app.agents.state import AgentState
from backend.app.services.redis_service import redis_service

logger = logging.getLogger(__name__)

async def persist_workflow_run(session: AsyncSession, state: AgentState) -> Workflow:
    """
    Persist completed or running agent workflow and all its tool executions to the database.
    """
    try:
        # Check or create conversation
        conv_res = await session.execute(
            select(Conversation).where(Conversation.id == state.conversation_id)
        )
        conv = conv_res.scalar_one_or_none()
        if not conv:
            conv = Conversation(
                id=state.conversation_id,
                title=state.user_request[:50] + "..." if len(state.user_request) > 50 else state.user_request
            )
            session.add(conv)
            await session.flush()

        # Add user message
        user_msg = Message(
            conversation_id=state.conversation_id,
            role="USER",
            content=state.user_request
        )
        session.add(user_msg)

        # Add assistant response message
        if state.final_response:
            asst_msg = Message(
                conversation_id=state.conversation_id,
                role="ASSISTANT",
                content=state.final_response,
                tool_calls=[step.model_dump() for step in state.steps]
            )
            session.add(asst_msg)

        # Save workflow record
        workflow = Workflow(
            id=state.workflow_id,
            conversation_id=state.conversation_id,
            request=state.user_request,
            status=state.status,
            steps_count=len(state.steps),
            completed_at=datetime.now(timezone.utc) if state.status == "COMPLETED" else None
        )
        session.add(workflow)
        await session.flush()

        # Save tool execution records
        for step in state.steps:
            te = ToolExecution(
                workflow_id=workflow.id,
                tool_name=step.tool_name,
                input_data=step.tool_input,
                output_data=step.tool_output,
                status=step.status,
                execution_time_ms=step.execution_time_ms
            )
            session.add(te)

        await session.commit()

        # Cache in Redis
        redis_service.set_workflow_state(workflow.id, state.model_dump())
        return workflow

    except Exception as e:
        logger.error(f"Error persisting workflow {state.workflow_id}: {e}")
        await session.rollback()
        raise
