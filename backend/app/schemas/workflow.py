from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel
from backend.app.schemas.chat import ToolCallInfo

class WorkflowResponse(BaseModel):
    id: str
    conversation_id: str
    request: str
    status: str
    steps_count: int
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class WorkflowDetailResponse(WorkflowResponse):
    tool_executions: List[ToolCallInfo] = []
