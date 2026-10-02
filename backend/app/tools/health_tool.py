import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

def get_service_health(service_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Check application health and operational telemetry metrics.
    If service_name is provided, returns granular telemetry for that service.
    If omitted or 'all', returns a system-wide health summary of all services.
    """
    services_file = settings.SERVICES_DATA_FILE
    if not services_file.exists():
        return {
            "error": "Services telemetry file not found",
            "status": "unavailable"
        }

    try:
        with open(services_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            services: List[Dict[str, Any]] = data.get("services", [])

        if service_name and service_name.lower() != "all":
            normalized_name = service_name.strip().lower()
            for service in services:
                if service["name"].lower() == normalized_name:
                    return {
                        "service_name": service["name"],
                        "display_name": service.get("display_name", service["name"]),
                        "status": service.get("status", "unknown"),
                        "error_rate": service.get("error_rate", 0.0),
                        "avg_latency_ms": service.get("avg_latency_ms", 0),
                        "p99_latency_ms": service.get("p99_latency_ms", 0),
                        "cpu_usage": service.get("cpu_usage", 0),
                        "memory_usage": service.get("memory_usage", 0),
                        "active_instances": service.get("active_instances", 1),
                        "version": service.get("version", "v1.0.0"),
                        "dependencies": service.get("dependencies", [])
                    }
            
            # Service name fuzzy match
            for service in services:
                if normalized_name in service["name"].lower() or service["name"].lower() in normalized_name:
                    return {
                        "service_name": service["name"],
                        "display_name": service.get("display_name", service["name"]),
                        "status": service.get("status", "unknown"),
                        "error_rate": service.get("error_rate", 0.0),
                        "avg_latency_ms": service.get("avg_latency_ms", 0),
                        "p99_latency_ms": service.get("p99_latency_ms", 0),
                        "cpu_usage": service.get("cpu_usage", 0),
                        "memory_usage": service.get("memory_usage", 0),
                        "active_instances": service.get("active_instances", 1),
                        "version": service.get("version", "v1.0.0"),
                        "dependencies": service.get("dependencies", [])
                    }

            return {
                "error": f"Service '{service_name}' not found",
                "available_services": [s["name"] for s in services]
            }

        # Return full system overview
        degraded = [s["name"] for s in services if s.get("status") == "degraded"]
        critical = [s["name"] for s in services if s.get("status") == "critical"]
        healthy = [s["name"] for s in services if s.get("status") == "healthy"]

        avg_latency = (
            sum(s.get("avg_latency_ms", 0) for s in services) / len(services)
            if services else 0
        )

        overall = "healthy"
        if critical:
            overall = "critical"
        elif degraded:
            overall = "degraded"

        return {
            "overall_status": overall,
            "total_services": len(services),
            "healthy_count": len(healthy),
            "degraded_count": len(degraded),
            "critical_count": len(critical),
            "avg_system_latency_ms": round(avg_latency, 1),
            "degraded_services": degraded,
            "critical_services": critical,
            "services": services
        }
    except Exception as e:
        logger.error(f"Error reading service health: {e}")
        return {"error": str(e), "status": "error"}
