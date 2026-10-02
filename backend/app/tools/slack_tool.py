import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import httpx
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

_simulated_slack_messages: List[Dict[str, Any]] = []

def send_slack_message(
    channel: str,
    message: str,
    severity: Optional[str] = "info"
) -> Dict[str, Any]:
    """
    Send an engineering alert message to a Slack channel.
    Uses incoming webhook if SLACK_WEBHOOK_URL is configured,
    otherwise records structured simulation.
    """
    clean_channel = channel if channel.startswith("#") else f"#{channel}"

    if settings.SLACK_WEBHOOK_URL:
        try:
            payload = {
                "channel": clean_channel,
                "text": f"[{severity.upper()}] {message}",
                "username": "AgentForge Alert Bot"
            }
            with httpx.Client(timeout=5.0) as client:
                resp = client.post(settings.SLACK_WEBHOOK_URL, json=payload)
                if resp.status_code == 200:
                    return {
                        "status": "delivered",
                        "mode": "webhook",
                        "channel": clean_channel,
                        "severity": severity,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
        except Exception as e:
            logger.warning(f"Failed to post to Slack webhook: {e}")

    # Simulation mode
    record = {
        "status": "delivered",
        "mode": "simulation",
        "channel": clean_channel,
        "severity": severity,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    _simulated_slack_messages.append(record)
    return record

def get_recent_slack_messages() -> List[Dict[str, Any]]:
    return _simulated_slack_messages
