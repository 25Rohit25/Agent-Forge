from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class ToolParameterProperty(BaseModel):
    type: str
    description: str
    enum: Optional[List[str]] = None

class ToolParametersSchema(BaseModel):
    type: str = "object"
    properties: Dict[str, Any]
    required: List[str] = []

class ToolDefinition(BaseModel):
    name: str
    description: str
    category: str
    parameters: ToolParametersSchema

class ToolExecutionResponse(BaseModel):
    id: str
    workflow_id: str
    tool_name: str
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Any] = None
    status: str
    execution_time_ms: int
    created_at: datetime

    class Config:
        from_attributes = True

class ToolCallRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]
