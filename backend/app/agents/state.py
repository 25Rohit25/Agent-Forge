from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class StepExecution(BaseModel):
    step_number: int
    tool_name: str
    tool_input: Dict[str, Any]
    tool_output: Optional[Any] = None
    status: str = "PENDING"  # PENDING, RUNNING, COMPLETED, FAILED
    reason: Optional[str] = None
    execution_time_ms: int = 0
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class EvidenceBundle(BaseModel):
    service_telemetry: Optional[Dict[str, Any]] = None
    log_errors: List[str] = Field(default_factory=list)
    relevant_docs: List[Dict[str, Any]] = Field(default_factory=list)
    db_metrics: List[Dict[str, Any]] = Field(default_factory=list)
    root_cause_summary: Optional[str] = None
    action_taken: Optional[Dict[str, Any]] = None

class AgentState(BaseModel):
    workflow_id: str
    conversation_id: str
    user_request: str
    status: str = "RUNNING"  # RUNNING, COMPLETED, FAILED
    current_step: int = 0
    plan: List[str] = Field(default_factory=list)
    steps: List[StepExecution] = Field(default_factory=list)
    evidence: EvidenceBundle = Field(default_factory=EvidenceBundle)
    final_response: Optional[str] = None
    error_message: Optional[str] = None
    started_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None

    def add_step(self, tool_name: str, tool_input: Dict[str, Any], reason: Optional[str] = None) -> StepExecution:
        self.current_step += 1
        step = StepExecution(
            step_number=self.current_step,
            tool_name=tool_name,
            tool_input=tool_input,
            reason=reason,
            status="RUNNING"
        )
        self.steps.append(step)
        return step

    def complete_current_step(self, output: Any, execution_time_ms: int, status: str = "COMPLETED") -> None:
        if self.steps:
            last_step = self.steps[-1]
            last_step.tool_output = output
            last_step.execution_time_ms = execution_time_ms
            last_step.status = status
