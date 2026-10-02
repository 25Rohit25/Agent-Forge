import logging
import time
from typing import Any, Callable, Dict, List, Optional
from backend.app.tools.health_tool import get_service_health
from backend.app.tools.log_tool import search_logs
from backend.app.tools.database_tool import query_database
from backend.app.tools.github_tool import create_github_issue
from backend.app.tools.slack_tool import send_slack_message
from backend.app.tools.knowledge_tool import search_knowledge_base

logger = logging.getLogger(__name__)

TOOL_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "name": "get_service_health",
        "description": "Check application health, status (healthy, degraded, critical), error rates, CPU/memory usage, and latency for one or all services.",
        "category": "observability",
        "parameters": {
            "type": "object",
            "properties": {
                "service_name": {
                    "type": "string",
                    "description": "The service name to inspect (e.g. 'payment-service', 'checkout-service', 'auth-service', or 'all')."
                }
            },
            "required": []
        }
    },
    {
        "name": "search_logs",
        "description": "Search application log files for error messages, stack traces, timeouts, or specific keywords.",
        "category": "observability",
        "parameters": {
            "type": "object",
            "properties": {
                "service": {
                    "type": "string",
                    "description": "Name of the service whose logs to inspect (e.g. 'payment-service', 'checkout-service')."
                },
                "level": {
                    "type": "string",
                    "description": "Log level filter: 'ERROR', 'WARN', 'INFO', or 'FATAL'.",
                    "enum": ["INFO", "WARN", "ERROR", "FATAL"]
                },
                "keyword": {
                    "type": "string",
                    "description": "Substring keyword to filter log lines (e.g. 'timeout', 'connection', 'deadlock')."
                },
                "time_range": {
                    "type": "string",
                    "description": "Time window to search (e.g. '1h', '24h'). Default is '1h'."
                },
                "max_lines": {
                    "type": "integer",
                    "description": "Maximum number of log lines to return (default 50)."
                }
            },
            "required": ["service"]
        }
    },
    {
        "name": "search_knowledge_base",
        "description": "Search technical documentation, incident post-mortems, runbooks, and architecture guides using RAG semantic retrieval.",
        "category": "knowledge",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language question or technical keywords to search in internal documentation."
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of relevant documentation fragments to retrieve (default 4)."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "query_database",
        "description": "Execute approved read-only analytical queries against production database metrics (failed_transactions, active_connections, slow_queries, deadlocks, recent_errors).",
        "category": "operations",
        "parameters": {
            "type": "object",
            "properties": {
                "query_type": {
                    "type": "string",
                    "description": "Approved query type.",
                    "enum": ["failed_transactions", "active_connections", "slow_queries", "deadlocks", "recent_errors"]
                },
                "service": {
                    "type": "string",
                    "description": "Optional service filter (e.g. 'payment-service')."
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum records to return (default 10)."
                }
            },
            "required": ["query_type"]
        }
    },
    {
        "name": "create_github_issue",
        "description": "Create a new engineering issue or incident ticket on GitHub.",
        "category": "actions",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Concise, descriptive title for the issue."
                },
                "description": {
                    "type": "string",
                    "description": "Comprehensive markdown description of the incident, observed metrics, root cause hypothesis, and suggested remediation."
                },
                "priority": {
                    "type": "string",
                    "description": "Issue priority level.",
                    "enum": ["low", "medium", "high", "critical"]
                },
                "service": {
                    "type": "string",
                    "description": "Affected service name."
                },
                "labels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Issue labels or tags."
                }
            },
            "required": ["title", "description"]
        }
    },
    {
        "name": "send_slack_message",
        "description": "Send an operational alert message to a designated Slack channel.",
        "category": "actions",
        "parameters": {
            "type": "object",
            "properties": {
                "channel": {
                    "type": "string",
                    "description": "Target Slack channel (e.g. '#backend-alerts', '#incident-response')."
                },
                "message": {
                    "type": "string",
                    "description": "The alert message text."
                },
                "severity": {
                    "type": "string",
                    "description": "Alert severity level: 'info', 'warning', 'critical'.",
                    "enum": ["info", "warning", "critical"]
                }
            },
            "required": ["channel", "message"]
        }
    }
]

# Mapping of tool names to callable functions
# Note: search_knowledge_base will be injected from rag.retrieval
_TOOL_HANDLERS: Dict[str, Callable[..., Any]] = {
    "get_service_health": get_service_health,
    "search_logs": search_logs,
    "search_knowledge_base": search_knowledge_base,
    "query_database": query_database,
    "create_github_issue": create_github_issue,
    "send_slack_message": send_slack_message,
}

def register_tool_handler(name: str, handler: Callable[..., Any]) -> None:
    """Register or override a tool handler at runtime (e.g. RAG knowledge search)."""
    _TOOL_HANDLERS[name] = handler

def get_tool_definitions() -> List[Dict[str, Any]]:
    """Return all available tool definitions formatted for LLM function calling."""
    return TOOL_DEFINITIONS

def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Safely execute a tool by name with arguments.
    Measures duration and returns structured output.
    """
    start_time = time.perf_counter()
    if tool_name not in _TOOL_HANDLERS:
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        return {
            "tool_name": tool_name,
            "status": "FAILED",
            "error": f"Tool '{tool_name}' is not recognized or available.",
            "execution_time_ms": duration_ms,
            "output": None
        }

    handler = _TOOL_HANDLERS[tool_name]
    try:
        # Call handler with unpacking
        result = handler(**arguments)
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        return {
            "tool_name": tool_name,
            "status": "COMPLETED",
            "execution_time_ms": duration_ms,
            "output": result
        }
    except TypeError as te:
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        logger.error(f"Invalid arguments for tool {tool_name}: {te}")
        return {
            "tool_name": tool_name,
            "status": "FAILED",
            "error": f"Invalid arguments: {te}",
            "execution_time_ms": duration_ms,
            "output": None
        }
    except Exception as e:
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        logger.error(f"Error executing tool {tool_name}: {e}")
        return {
            "tool_name": tool_name,
            "status": "FAILED",
            "error": str(e),
            "execution_time_ms": duration_ms,
            "output": None
        }
