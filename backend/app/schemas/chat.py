from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str = Field(..., min_length=1)
    stream: bool = False

class ToolCallInfo(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    output: Optional[Any] = None
    execution_time_ms: int = 0
    status: str = "COMPLETED"

class ChatResponse(BaseModel):
    conversation_id: str
    workflow_id: str
    response: str
    status: str = "COMPLETED"
    steps_count: int = 0
    tools_used: List[str] = []
    tool_executions: List[ToolCallInfo] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StreamEvent(BaseModel):
    event: str  # start, plan, tool_call, tool_result, analysis, final_response, done, error
    workflow_id: Optional[str] = None
    data: Any = None
