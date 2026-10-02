import logging
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from backend.app.database.connection import get_db
from backend.app.models.workflow import Workflow
from backend.app.models.tool_execution import ToolExecution
from backend.app.services.redis_service import redis_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/workflows", tags=["Workflows & Observability"])

@router.get("", response_model=List[Dict[str, Any]])
async def list_workflows(
    limit: int = 50,
    status: str = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Workflow).order_by(desc(Workflow.started_at)).limit(limit)
    if status:
        query = query.where(Workflow.status == status.upper())

    res = await db.execute(query)
    wfs = res.scalars().all()

    return [
        {
            "id": w.id,
            "conversation_id": w.conversation_id,
            "request": w.request,
            "status": w.status,
            "steps_count": w.steps_count,
            "started_at": w.started_at.isoformat() if w.started_at else None,
            "completed_at": w.completed_at.isoformat() if w.completed_at else None,
        }
        for w in wfs
    ]

@router.get("/{workflow_id}")
async def get_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db)
):
    # Check cache first
    cached = redis_service.get_workflow_state(workflow_id)
    if cached:
        return cached

    query = (
        select(Workflow)
        .where(Workflow.id == workflow_id)
        .options(selectinload(Workflow.tool_executions))
    )
    res = await db.execute(query)
    wf = res.scalar_one_or_none()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    executions = [
        {
            "id": te.id,
            "tool_name": te.tool_name,
            "input_data": te.input_data,
            "output_data": te.output_data,
            "status": te.status,
            "execution_time_ms": te.execution_time_ms,
            "created_at": te.created_at.isoformat() if te.created_at else None
        }
        for te in wf.tool_executions
    ]

    return {
        "id": wf.id,
        "conversation_id": wf.conversation_id,
        "request": wf.request,
        "status": wf.status,
        "steps_count": wf.steps_count,
        "started_at": wf.started_at.isoformat() if wf.started_at else None,
        "completed_at": wf.completed_at.isoformat() if wf.completed_at else None,
        "tool_executions": executions
    }
