import pytest
from backend.app.tools.health_tool import get_service_health
from backend.app.tools.log_tool import search_logs
from backend.app.tools.database_tool import query_database
from backend.app.tools.github_tool import create_github_issue
from backend.app.tools.slack_tool import send_slack_message
from backend.app.tools.registry import execute_tool, get_tool_definitions

def test_get_service_health_all():
    health = get_service_health()
    assert "overall_status" in health
    assert health["total_services"] >= 4
    assert "payment-service" in health["degraded_services"]

def test_get_service_health_single():
    payment = get_service_health("payment-service")
    assert payment["service_name"] == "payment-service"
    assert payment["status"] == "degraded"
    assert payment["error_rate"] > 5.0

def test_search_logs_payment():
    res = search_logs("payment-service", level="ERROR")
    assert res["matches_count"] > 0
    assert any("ConnectionPoolTimeoutException" in line for line in res["logs"])

def test_search_logs_keyword():
    res = search_logs("payment-service", keyword="pool")
    assert res["matches_count"] > 0
    assert any("pool" in line.lower() for line in res["logs"])

def test_query_database_safe_whitelist():
    res = query_database("failed_transactions", service="payment-service")
    assert res["query_type"] == "failed_transactions"
    assert len(res["results"]) > 0

def test_query_database_rejects_sql_injection():
    res = query_database("SELECT * FROM users; DROP TABLE users;")
    assert "error" in res
    assert "Arbitrary SQL is forbidden" in res["error"]

def test_create_github_issue_simulation():
    res = create_github_issue(
        title="Payment Service Connection Pool Exhaustion",
        description="Active pool reached 50/50 capacity.",
        priority="high",
        service="payment-service"
    )
    assert res["status"] == "created"
    assert res["issue_number"] > 0
    assert "github.com" in res["html_url"]

def test_send_slack_message():
    res = send_slack_message("#backend-alerts", "Payment service degraded.", severity="critical")
    assert res["status"] == "delivered"
    assert res["channel"] == "#backend-alerts"

def test_tool_registry_execution():
    res = execute_tool("get_service_health", {"service_name": "auth-service"})
    assert res["status"] == "COMPLETED"
    assert res["output"]["status"] == "healthy"
    assert res["execution_time_ms"] >= 0
