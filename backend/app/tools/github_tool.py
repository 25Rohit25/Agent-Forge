import logging
import random
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import httpx
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# Maintain simulated issue storage in memory
_simulated_issues: List[Dict[str, Any]] = []

def create_github_issue(
    title: str,
    description: str,
    priority: Optional[str] = "medium",
    service: Optional[str] = None,
    labels: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create an engineering ticket / GitHub issue.
    Supports real GitHub API integration if GITHUB_TOKEN is set,
    otherwise provides high-fidelity simulation.
    """
    issue_labels = labels or ["bug", "incident-investigation"]
    if priority:
        issue_labels.append(f"priority:{priority.lower()}")
    if service:
        issue_labels.append(f"service:{service.lower()}")

    # Attempt real GitHub API if token is provided
    if settings.GITHUB_TOKEN and settings.GITHUB_REPO:
        try:
            repo = settings.GITHUB_REPO
            url = f"https://api.github.com/repos/{repo}/issues"
            headers = {
                "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "AgentForge-Agentic-Workspace"
            }
            payload = {
                "title": title,
                "body": description,
                "labels": issue_labels
            }
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(url, json=payload, headers=headers)
                if resp.status_code in [200, 201]:
                    data = resp.json()
                    return {
                        "status": "created",
                        "mode": "github_api",
                        "issue_number": data.get("number"),
                        "issue_id": str(data.get("id")),
                        "title": data.get("title"),
                        "html_url": data.get("html_url"),
                        "state": data.get("state", "open"),
                        "labels": [lbl.get("name") if isinstance(lbl, dict) else lbl for lbl in data.get("labels", [])],
                        "created_at": data.get("created_at")
                    }
                else:
                    logger.warning(f"GitHub API returned {resp.status_code}: {resp.text}. Falling back to simulation.")
        except Exception as e:
            logger.warning(f"Error calling GitHub API: {e}. Falling back to simulation.")

    # High-fidelity Simulation Mode
    simulated_number = 140 + len(_simulated_issues) + 1
    issue_data = {
        "status": "created",
        "mode": "simulation",
        "issue_number": simulated_number,
        "issue_id": f"sim_iss_{simulated_number}",
        "title": title,
        "html_url": f"https://github.com/{settings.GITHUB_REPO}/issues/{simulated_number}",
        "state": "open",
        "priority": priority,
        "service": service,
        "labels": issue_labels,
        "body_preview": description[:200] + "..." if len(description) > 200 else description,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    _simulated_issues.append(issue_data)
    return issue_data

def get_recent_github_issues() -> List[Dict[str, Any]]:
    """Retrieve all simulated GitHub issues created during session."""
    return _simulated_issues
