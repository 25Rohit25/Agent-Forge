from backend.app.api.auth import router as auth_router
from backend.app.api.chat import router as chat_router
from backend.app.api.conversations import router as conversations_router
from backend.app.api.workflows import router as workflows_router
from backend.app.api.tools import router as tools_router
from backend.app.api.documents import router as documents_router
from backend.app.api.health import router as health_router

__all__ = [
    "auth_router",
    "chat_router",
    "conversations_router",
    "workflows_router",
    "tools_router",
    "documents_router",
    "health_router",
]
