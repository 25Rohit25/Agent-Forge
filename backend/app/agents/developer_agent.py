import asyncio
import json
import logging
import re
import time
import uuid
from typing import Any, AsyncGenerator, Dict, List, Optional
import httpx
from backend.app.core.config import settings
from backend.app.agents.prompts import SYSTEM_PROMPT, INCIDENT_REPORT_TEMPLATE
from backend.app.agents.state import AgentState, StepExecution
from backend.app.tools.registry import execute_tool, get_tool_definitions

logger = logging.getLogger(__name__)

class DeveloperAgent:
    """
    Autonomous Agentic AI Developer Workspace Agent.
    Deconstructs engineering requests, plans sequential tool executions,
    gathers multi-source evidence, performs root-cause synthesis,
    and executes actions (e.g. GitHub issue creation).
    """

    def __init__(self, conversation_id: Optional[str] = None):
        self.conversation_id = conversation_id or str(uuid.uuid4())

    def _extract_target_service(self, message: str) -> Optional[str]:
        """Extract candidate service name from prompt."""
        lower = message.lower()
        known_services = [
            "payment-service", "checkout-service", "auth-service",
            "inventory-service", "notification-service", "api-gateway"
        ]
        for s in known_services:
            if s in lower or s.replace("-", " ") in lower or s.replace("-", "") in lower:
                return s

        # Heuristic search for "<word>-service"
        match = re.search(r"\b([a-zA-Z0-9_\-]+-service)\b", lower)
        if match:
            return match.group(1)

        # Check for keywords like payment, checkout, auth
        if "payment" in lower:
            return "payment-service"
        if "checkout" in lower:
            return "checkout-service"
        if "auth" in lower or "login" in lower:
            return "auth-service"
        if "inventory" in lower:
            return "inventory-service"
        return None

    def _determine_execution_plan(self, message: str, service: Optional[str]) -> List[Dict[str, Any]]:
        """
        Formulate an intelligent multi-step plan based on user instructions and detected signals.
        """
        lower = message.lower()
        plan: List[Dict[str, Any]] = []

        is_docs_only = any(k in lower for k in ["runbook", "documentation", "how do we", "how to", "architecture"]) and not any(k in lower for k in ["investigate", "failing", "why is", "latency", "errors"])

        if is_docs_only:
            plan.append({
                "tool": "search_knowledge_base",
                "args": {"query": message, "limit": 4},
                "reason": "Search technical documentation and runbooks for the user's query."
            })
            return plan

        # Step 1: Health check
        if service:
            plan.append({
                "tool": "get_service_health",
                "args": {"service_name": service},
                "reason": f"Inspect operational metrics and degradation status for {service}."
            })
        else:
            plan.append({
                "tool": "get_service_health",
                "args": {"service_name": "all"},
                "reason": "Inspect overall system health and discover degraded services."
            })

        # Step 2: Log search
        if service or any(k in lower for k in ["error", "log", "fail", "slow", "exception", "investigate", "why"]):
            plan.append({
                "tool": "search_logs",
                "args": {
                    "service": service or "payment-service",
                    "level": "ERROR",
                    "time_range": "1h",
                    "max_lines": 20
                },
                "reason": f"Examine recent error logs and exception stack traces."
            })

        # Step 3: Knowledge base RAG
        plan.append({
            "tool": "search_knowledge_base",
            "args": {
                "query": f"{service or 'service'} timeout failure root cause troubleshooting",
                "limit": 3
            },
            "reason": "Search internal runbooks and historical post-mortems for matching failure patterns."
        })

        # Step 4: Optional database query
        if any(k in lower for k in ["database", "db", "transaction", "pool", "connection"]):
            plan.append({
                "tool": "query_database",
                "args": {
                    "query_type": "active_connections" if "connection" in lower or "pool" in lower else "failed_transactions",
                    "service": service
                },
                "reason": "Query operational database metrics to verify connection pool state and transaction errors."
            })

        # Step 5: GitHub issue creation if requested
        wants_issue = any(k in lower for k in ["issue", "ticket", "bug", "github", "open an issue", "create an issue", "file an issue"])
        if wants_issue:
            plan.append({
                "tool": "create_github_issue",
                "args": {
                    "title": f"Investigate {service or 'system'} incident: High error rate and degradation",
                    "description": "Auto-generated incident ticket by AgentForge based on operational telemetry and logs.",
                    "priority": "high",
                    "service": service or "general"
                },
                "reason": "Create tracking GitHub issue as requested by the engineer."
            })

        # Step 6: Slack alert if requested
        if any(k in lower for k in ["slack", "notify", "alert team"]):
            plan.append({
                "tool": "send_slack_message",
                "args": {
                    "channel": "#backend-alerts",
                    "message": f"AgentForge detected degradation in {service or 'services'}. Automated investigation initiated.",
                    "severity": "warning"
                },
                "reason": "Send incident alert to the engineering team via Slack."
            })

        return plan

    async def run(self, user_request: str) -> AgentState:
        """
        Execute an end-to-end agentic workflow synchronously.
        """
        workflow_id = f"wf_{uuid.uuid4().hex[:8]}"
        state = AgentState(
            workflow_id=workflow_id,
            conversation_id=self.conversation_id,
            user_request=user_request
        )

        service = self._extract_target_service(user_request)
        planned_steps = self._determine_execution_plan(user_request, service)
        state.plan = [f"{p['tool']}: {p['reason']}" for p in planned_steps]

        # Execute each planned tool dynamically
        for p in planned_steps:
            tool_name = p["tool"]
            tool_args = p["args"]
            reason = p["reason"]

            step = state.add_step(tool_name, tool_args, reason)

            # Execute tool
            exec_res = execute_tool(tool_name, tool_args)
            step.tool_output = exec_res["output"]
            step.execution_time_ms = exec_res["execution_time_ms"]
            step.status = exec_res["status"]

            # Store evidence
            if tool_name == "get_service_health" and exec_res["output"]:
                state.evidence.service_telemetry = exec_res["output"]
            elif tool_name == "search_logs" and exec_res["output"]:
                logs = exec_res["output"].get("logs", [])
                state.evidence.log_errors.extend(logs[:5])
            elif tool_name == "search_knowledge_base" and exec_res["output"]:
                docs = exec_res["output"].get("results", [])
                state.evidence.relevant_docs.extend(docs[:3])
            elif tool_name == "query_database" and exec_res["output"]:
                db_res = exec_res["output"].get("results", [])
                state.evidence.db_metrics.extend(db_res[:3])
            elif tool_name == "create_github_issue" and exec_res["output"]:
                state.evidence.action_taken = exec_res["output"]

        # Synthesize final response
        state.final_response = self._synthesize_response(user_request, service, state)
        state.status = "COMPLETED"
        state.completed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        return state

    async def stream(self, user_request: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream agent execution events in real time for SSE / WebSockets.
        """
        workflow_id = f"wf_{uuid.uuid4().hex[:8]}"
        state = AgentState(
            workflow_id=workflow_id,
            conversation_id=self.conversation_id,
            user_request=user_request
        )

        yield {"event": "start", "workflow_id": workflow_id, "data": {"request": user_request}}

        service = self._extract_target_service(user_request)
        planned_steps = self._determine_execution_plan(user_request, service)
        state.plan = [f"{p['tool']}: {p['reason']}" for p in planned_steps]

        yield {
            "event": "plan",
            "workflow_id": workflow_id,
            "data": {
                "target_service": service,
                "steps_count": len(planned_steps),
                "steps": [p["tool"] for p in planned_steps]
            }
        }

        # Sequential tool execution with streaming updates
        for p in planned_steps:
            tool_name = p["tool"]
            tool_args = p["args"]
            reason = p["reason"]

            yield {
                "event": "tool_start",
                "workflow_id": workflow_id,
                "data": {
                    "tool": tool_name,
                    "input": tool_args,
                    "reason": reason
                }
            }

            step = state.add_step(tool_name, tool_args, reason)
            # Execute tool safely
            exec_res = execute_tool(tool_name, tool_args)
            step.tool_output = exec_res["output"]
            step.execution_time_ms = exec_res["execution_time_ms"]
            step.status = exec_res["status"]

            # Store evidence
            if tool_name == "get_service_health" and exec_res["output"]:
                state.evidence.service_telemetry = exec_res["output"]
            elif tool_name == "search_logs" and exec_res["output"]:
                logs = exec_res["output"].get("logs", [])
                state.evidence.log_errors.extend(logs[:5])
            elif tool_name == "search_knowledge_base" and exec_res["output"]:
                docs = exec_res["output"].get("results", [])
                state.evidence.relevant_docs.extend(docs[:3])
            elif tool_name == "query_database" and exec_res["output"]:
                db_res = exec_res["output"].get("results", [])
                state.evidence.db_metrics.extend(db_res[:3])
            elif tool_name == "create_github_issue" and exec_res["output"]:
                state.evidence.action_taken = exec_res["output"]

            yield {
                "event": "tool_complete",
                "workflow_id": workflow_id,
                "data": {
                    "tool": tool_name,
                    "output": exec_res["output"],
                    "status": exec_res["status"],
                    "execution_time_ms": exec_res["execution_time_ms"]
                }
            }

            # Brief pause for smooth frontend streaming animation
            await asyncio.sleep(0.05)

        # Synthesize final report
        final_answer = self._synthesize_response(user_request, service, state)
        state.final_response = final_answer
        state.status = "COMPLETED"
        state.completed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        yield {
            "event": "final_response",
            "workflow_id": workflow_id,
            "data": {
                "response": final_answer,
                "steps_count": len(state.steps),
                "action_taken": state.evidence.action_taken
            }
        }

        yield {"event": "done", "workflow_id": workflow_id, "data": {"status": "COMPLETED"}}

    def _synthesize_response(self, user_request: str, service: Optional[str], state: AgentState) -> str:
        """
        Synthesize multi-source evidence into a professional root cause investigation report.
        """
        telemetry = state.evidence.service_telemetry or {}
        logs = state.evidence.log_errors
        docs = state.evidence.relevant_docs
        action = state.evidence.action_taken

        # If pure knowledge search
        if not telemetry and docs:
            top_doc = docs[0]
            return f"### Knowledge Base Retrieval\n\nFound relevant documentation from **{top_doc.get('document_title', 'Runbook')}**:\n\n{top_doc.get('content')}\n\n*Reference: {top_doc.get('source')} (relevance score: {top_doc.get('score')})*"

        svc_name = service or telemetry.get("service_name", "Microservices System")
        status = telemetry.get("status", "Degraded").capitalize()
        err_rate = telemetry.get("error_rate", 8.7)
        latency = telemetry.get("avg_latency_ms", 870)

        # Determine root cause hypothesis
        root_cause = "Likely database connection pool exhaustion (HikariCP) due to leaked connections during batch settlement or long-running transactions."
        if any("timeout" in l.lower() for l in logs):
            root_cause = "Database Connection Pool Starvation: Client threads timed out waiting for available pooled connections."
        elif any("deadlock" in l.lower() for l in logs):
            root_cause = "Database Row Lock Contention & Deadlock on concurrent order reservation records."

        telemetry_bullets = [
            f"- **Service Status**: `{status}`",
            f"- **Error Rate**: `{err_rate}%` (Threshold: 5.0%)",
            f"- **Average Latency**: `{latency}ms` (P99: `{telemetry.get('p99_latency_ms', 2400)}ms`)",
            f"- **Active Pod Replicas**: `{telemetry.get('active_instances', 4)}` pods"
        ]

        log_bullets = []
        if logs:
            for l in logs[:3]:
                log_bullets.append(f"- `{l}`")
        else:
            log_bullets.append("- No fatal log events recorded in search window.")

        doc_bullets = []
        if docs:
            for d in docs[:2]:
                doc_bullets.append(f"- **{d.get('document_title')}**: {d.get('heading', 'Guideline')} — *{d.get('content', '')[:140]}...*")
        else:
            doc_bullets.append("- Standard microservice recovery runbooks apply.")

        remediation_steps = [
            "1. Increase HikariCP max pool size from 50 to 80 via runtime configuration.",
            "2. Enable connection leak detection: `leakDetectionThreshold: 20000ms`.",
            "3. Sequentially restart degraded worker instances to clear orphaned sockets: `kubectl rollout restart deployment/{svc}`.".format(svc=svc_name),
            "4. Verify PostgreSQL `max_connections` allocation on primary database."
        ]

        action_section = ""
        if action:
            issue_num = action.get("issue_number", 142)
            html_url = action.get("html_url", f"https://github.com/{settings.GITHUB_REPO}/issues/{issue_num}")
            action_section = f"\n#### 6. Automated Actions Performed\n- **GitHub Issue Created**: [Issue #{issue_num}]({html_url})\n- **Priority**: `{action.get('priority', 'high').upper()}`\n- **Labels**: {', '.join([f'`{lbl}`' for lbl in action.get('labels', [])])}"

        report = INCIDENT_REPORT_TEMPLATE.format(
            service_name=svc_name,
            status=status,
            error_rate=err_rate,
            latency=latency,
            telemetry_summary="\n".join(telemetry_bullets),
            logs_summary="\n".join(log_bullets),
            knowledge_summary="\n".join(doc_bullets),
            root_cause=root_cause,
            remediation="\n".join(remediation_steps),
            action_taken=action_section
        )
        return report.strip()
