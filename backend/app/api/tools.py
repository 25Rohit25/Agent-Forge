import logging
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from backend.app.database.connection import get_db
from backend.app.models.tool_execution import ToolExecution
from backend.app.tools.registry import get_tool_definitions, execute_tool
from backend.app.schemas.tool import ToolCallRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tools", tags=["Tools Sandbox"])

@router.get("", response_model=List[Dict[str, Any]])
async def list_tools():
    """Get the full catalog of available engineering tools with JSON schemas."""
    return get_tool_definitions()

@router.get("/executions/{workflow_id}")
async def list_tool_executions_by_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(ToolExecution)
        .where(ToolExecution.workflow_id == workflow_id)
        .order_by(ToolExecution.created_at)
    )
    res = await db.execute(query)
    executions = res.scalars().all()
    return [
        {
            "id": te.id,
            "workflow_id": te.workflow_id,
            "tool_name": te.tool_name,
            "input_data": te.input_data,
            "output_data": te.output_data,
            "status": te.status,
            "execution_time_ms": te.execution_time_ms,
            "created_at": te.created_at.isoformat() if te.created_at else None
        }
        for te in executions
    ]

@router.post("/execute")
async def execute_tool_endpoint(req: ToolCallRequest):
    """Direct sandbox execution of an engineering tool."""
    res = execute_tool(req.tool_name, req.parameters)
    return res
