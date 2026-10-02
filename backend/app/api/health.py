import logging
from typing import Any, Dict
from fastapi import APIRouter
from backend.app.tools.health_tool import get_service_health

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/health", tags=["Health & Telemetry"])

@router.get("")
async def backend_health() -> Dict[str, Any]:
    """FastAPI system health check endpoint."""
    return {
        "status": "healthy",
        "service": "AgentForge Backend",
        "version": "1.0.0"
    }

@router.get("/services")
async def all_services_health() -> Dict[str, Any]:
    """Retrieve operational telemetry and health metrics across all microservices."""
    return get_service_health()

@router.get("/services/{service_name}")
async def single_service_health(service_name: str) -> Dict[str, Any]:
    """Retrieve operational telemetry for a specific microservice."""
    return get_service_health(service_name)
