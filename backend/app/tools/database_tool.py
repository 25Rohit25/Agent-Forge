from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

APPROVED_QUERIES = {
    "failed_transactions": {
        "description": "Retrieve recent failed transaction records with failure reasons and latency",
        "sample_data": [
            {
                "transaction_id": "tx_99812401",
                "service": "payment-service",
                "amount": 149.99,
                "currency": "USD",
                "failure_reason": "ConnectionPoolTimeoutException: HikariCP connection checkout timed out",
                "latency_ms": 30012,
                "timestamp": "2026-10-02T19:28:19Z"
            },
            {
                "transaction_id": "tx_99812402",
                "service": "payment-service",
                "amount": 29.50,
                "currency": "USD",
                "failure_reason": "ConnectionPoolTimeoutException: No idle connection available",
                "latency_ms": 30005,
                "timestamp": "2026-10-02T19:28:45Z"
            },
            {
                "transaction_id": "tx_99812403",
                "service": "payment-service",
                "amount": 890.00,
                "currency": "USD",
                "failure_reason": "GatewayTimeoutException: Upstream payment provider response timeout",
                "latency_ms": 15400,
                "timestamp": "2026-10-02T19:31:12Z"
            }
        ]
    },
    "active_connections": {
        "description": "Inspect database connection pool metrics and active sessions",
        "sample_data": [
            {
                "pool_name": "HikariCP-PaymentPool",
                "max_connections": 50,
                "active_connections": 50,
                "idle_connections": 0,
                "pending_threads": 34,
                "utilization_pct": 100.0,
                "status": "EXHAUSTED"
            },
            {
                "pool_name": "HikariCP-AuthPool",
                "max_connections": 30,
                "active_connections": 4,
                "idle_connections": 26,
                "pending_threads": 0,
                "utilization_pct": 13.3,
                "status": "HEALTHY"
            }
        ]
    },
    "slow_queries": {
        "description": "Inspect PostgreSQL queries exceeding execution latency threshold",
        "sample_data": [
            {
                "pid": 4821,
                "duration_seconds": 45.2,
                "state": "idle in transaction",
                "query": "SELECT * FROM charges WHERE settlement_batch_id = $1 FOR UPDATE",
                "service": "payment-service",
                "leak_suspected": True
            },
            {
                "pid": 4902,
                "duration_seconds": 12.8,
                "state": "active",
                "query": "SELECT count(*) FROM transaction_ledger WHERE created_at > now() - interval '24 hours'",
                "service": "payment-service",
                "leak_suspected": False
            }
        ]
    },
    "deadlocks": {
        "description": "Inspect row-level database deadlock conflict reports",
        "sample_data": [
            {
                "incident_id": "dl_4021",
                "table": "inventory_item_reservations",
                "service": "checkout-service",
                "blocked_pid": 5104,
                "blocking_pid": 5099,
                "conflict": "ExclusiveLock on tuple (48, 12)",
                "timestamp": "2026-10-02T19:31:15Z"
            }
        ]
    },
    "recent_errors": {
        "description": "Query operational error event table across application services",
        "sample_data": [
            {
                "event_id": "err_10928",
                "service": "payment-service",
                "error_class": "ConnectionPoolTimeoutException",
                "occurrences_last_hour": 87,
                "first_seen": "2026-10-02T19:24:00Z"
            },
            {
                "event_id": "err_10929",
                "service": "checkout-service",
                "error_class": "CascadingTimeoutException",
                "occurrences_last_hour": 34,
                "first_seen": "2026-10-02T19:28:25Z"
            }
        ]
    }
}

def query_database(
    query_type: str = "failed_transactions",
    service: Optional[str] = None,
    limit: int = 10,
    query: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute an approved, read-only operational database query.
    Arbitrary SQL execution is strictly forbidden for security.
    """
    if query:
        # Arbitrary SQL guardrail check
        return {
            "error": f"Direct arbitrary SQL execution is strictly forbidden by AgentForge guardrails. Query '{query}' was safely blocked.",
            "approved_query_types": list(APPROVED_QUERIES.keys()),
            "status": "BLOCKED"
        }

    clean_type = query_type.strip().lower()

    if clean_type not in APPROVED_QUERIES:
        return {
            "error": f"Invalid query_type '{query_type}'. Arbitrary SQL is forbidden.",
            "approved_query_types": list(APPROVED_QUERIES.keys())
        }

    query_meta = APPROVED_QUERIES[clean_type]
    records = query_meta["sample_data"]

    # Filter by service if specified
    if service:
        clean_service = service.strip().lower()
        filtered = [
            r for r in records
            if "service" in r and (clean_service in r["service"].lower() or r["service"].lower() in clean_service)
        ]
        if filtered:
            records = filtered

    results = records[:limit]

    return {
        "query_type": clean_type,
        "description": query_meta["description"],
        "records_count": len(results),
        "results": results,
        "executed_at": datetime.now(timezone.utc).isoformat()
    }
