import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.database.connection import init_db, AsyncSessionLocal
from backend.app.rag.ingestion import ingest_default_knowledge_base_sync, sync_knowledge_to_db
from backend.app.core.security import get_password_hash
from backend.app.models.user import User
from sqlalchemy import select

# Import API routers
from backend.app.api import (
    auth_router,
    chat_router,
    conversations_router,
    workflows_router,
    tools_router,
    documents_router,
    health_router,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("agentforge")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database and Knowledge Base
    logger.info("Initializing AgentForge Database Schema...")
    await init_db()

    logger.info("Ingesting Knowledge Base documents into RAG index...")
    kb_res = ingest_default_knowledge_base_sync()
    logger.info(f"Ingested {kb_res.get('total_documents')} documents ({kb_res.get('total_chunks')} chunks).")

    # Seed demo user
    async with AsyncSessionLocal() as session:
        try:
            res = await session.execute(select(User).where(User.email == "demo@agentforge.dev"))
            if not res.scalar_one_or_none():
                demo_user = User(
                    email="demo@agentforge.dev",
                    full_name="Staff Reliability Engineer",
                    hashed_password=get_password_hash("AgentForgeDemo2026!"),
                    is_active=True
                )
                session.add(demo_user)
                await session.commit()
                logger.info("Seeded demo user: demo@agentforge.dev")
            
            # Sync knowledge to database
            await sync_knowledge_to_db(session)
        except Exception as e:
            logger.warning(f"Note during startup seeding: {e}")

    yield
    logger.info("AgentForge shutting down.")

app = FastAPI(
    title="AgentForge API",
    description="Agentic AI Developer Workspace for Engineering Investigations & Automated Tool Workflows",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers under /api
app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(conversations_router, prefix="/api")
app.include_router(workflows_router, prefix="/api")
app.include_router(tools_router, prefix="/api")
app.include_router(documents_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "Welcome to AgentForge — Agentic AI Developer Workspace API",
        "docs_url": "/docs",
        "api_prefix": "/api"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=settings.PORT, reload=settings.DEBUG)
