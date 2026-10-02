from typing import List, Optional
from pydantic import BaseModel

class ServiceHealthResponse(BaseModel):
    name: str
    display_name: str
    status: str  # healthy, degraded, critical
    error_rate: float
    avg_latency_ms: float
    p99_latency_ms: float
    cpu_usage: float
    memory_usage: float
    active_instances: int
    version: str
    dependencies: List[str] = []

class SystemOverviewResponse(BaseModel):
    total_services: int
    healthy_services: int
    degraded_services: int
    critical_services: int
    avg_system_latency_ms: float
    overall_health: str
    services: List[ServiceHealthResponse]
