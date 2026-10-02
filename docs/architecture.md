# AgentForge Architecture & System Design

## 1. High-Level Architecture

AgentForge is organized into a modular layered architecture that separates presentation, agent orchestration, tool execution, retrieval-augmented generation (RAG), and persistent storage.

```
┌─────────────────────────────────────────────────────────────┐
│                 React + TypeScript Frontend                 │
│  - AI Workspace & Chat           - Step Execution Drawer    │
│  - Live Service Health Monitor   - Knowledge Base Explorer  │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / SSE Stream
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                       FastAPI Backend                       │
│  - REST API Routing              - JWT Authentication       │
│  - SSE Streaming Protocol        - Rate Limiting Middleware │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               ▼                              ▼
┌──────────────────────────────┐ ┌────────────────────────────┐
│      Agent Orchestrator      │ │        RAG Pipeline        │
│  - LangChain Agent Executor  │ │  - Markdown Chunking       │
│  - Multi-step Planning Loop  │ │  - Embedding Generation    │
│  - Tool Selection & Invocation│ │  - Vector Cosine Matcher   │
│  - Incident Evidence Synthesis│ │  - pgvector / Memory Index │
└──────────────┬───────────────┘ └────────────┬───────────────┘
               │                              │
               ▼                              ▼
┌──────────────────────────────┐ ┌────────────────────────────┐
│        Tool Sandbox          │ │    Data & Storage Layer    │
│  - get_service_health()      │ │  - PostgreSQL + pgvector   │
│  - search_logs()             │ │  - Redis (State & Cache)   │
│  - search_knowledge_base()   │ │  - SQLite / Memory Backup  │
│  - query_database()          │ └────────────────────────────┘
│  - create_github_issue()     │
│  - send_slack_message()      │
└──────────────────────────────┘
```

## 2. Core Subsystems

### 2.1 Agentic Workflow Engine
The core agent engine uses LangChain tool calling powered by OpenAI models (with an offline rule-based reasoning engine fallback for deterministic local runs and testing). The agent does not simply output text; it iterates through:
1. **Goal Formulation**: Deconstructing the engineer's prompt into actionable intents (e.g. Investigation, Verification, Action).
2. **Dynamic Tool Execution**: Invoking telemetry checks, log greps, and RAG lookups.
3. **Evidence Accumulation**: Aggregating intermediate observations into structured state.
4. **Synthesis & Mitigation**: Formulating root cause hypotheses, matching with runbooks, and initiating actions (such as filing GitHub issues).

### 2.2 RAG Knowledge Pipeline
- **Document Chunking**: Header-aware and token-bounded chunking of operational runbooks, post-mortems, and system documentation.
- **Embedding Generation**: Uses OpenAI's `text-embedding-3-small` (1536 dims) with fallback to deterministic dense hash embeddings.
- **Vector Search**: Performs cosine similarity matching against pgvector (or vectorized memory cache) to retrieve the top-K relevant chunks with similarity scoring.

### 2.3 Resilient Database & Cache Architecture
- **Primary**: PostgreSQL with the `vector` extension for storing users, conversations, messages, workflows, tool executions, and document embeddings.
- **Graceful Fallback**: Automatically detects if PostgreSQL or Redis is offline and initializes a fast SQLite database and in-memory cache/vector index, ensuring zero-configuration local development.
- **Redis Cache**: Caches recent conversation history, workflow states, and implements token-bucket rate limiting.
