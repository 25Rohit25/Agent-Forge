# AgentForge — Agentic AI Developer Workspace

<p align="center">
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React" />
  <img src="https://img.shields.io/badge/TypeScript-5.5-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript" />
  <img src="https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/PostgreSQL-pgvector-336791?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis" />
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/Evaluation-100%25_Precision-brightgreen?style=for-the-badge" alt="Evaluation" />
  <img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="License" />
</p>

---

## 🚀 Overview

**AgentForge** is a full-stack, enterprise-grade **Agentic AI Developer Workspace** designed for engineering teams to diagnose production incidents, query microservice telemetry, search engineering knowledge bases via RAG, inspect relational databases with strict safety guardrails, and execute remediation workflows using natural-language instructions.

Unlike standard chatbots that only generate conversational text, **AgentForge autonomously reasons and executes multi-step operational tool chains**. 

For example, when an engineer asks:
> *"Why is the payment service failing? Check the logs, query related documentation, and create a GitHub issue with the root cause."*

AgentForge autonomously:
1. **Inspects telemetry** via `get_service_health` to detect that `payment-service` has degraded to a 28.5% error rate and 1,840ms latency.
2. **Filters structured log streams** via `search_logs` matching `payment-service` and severity `ERROR`, isolating timeout cascades to `stripe_gateway` and connection pool exhaustion.
3. **Searches technical runbooks** via `search_knowledge_base` using dense vector embeddings, retrieving the exact Stripe timeout escalation runbook.
4. **Synthesizes a root-cause analysis** and files a structured GitHub issue via `create_github_issue` complete with reproduction steps, impact assessment, and recommended remediation.
5. **Streams the entire reasoning and execution trace** to the developer in real-time via Server-Sent Events (SSE).

---

## ⚡ Key Highlights & Architecture

```
                       ┌────────────────────────────────────────────────────────┐
                       │                   React 18 + TS UI                     │
                       │  (Chat, Workflow Visualizer, Tool Drawer, Dashboards)   │
                       └───────────────────────────┬────────────────────────────┘
                                                   │
                                                   │ HTTP / SSE Stream
                                                   ▼
                       ┌────────────────────────────────────────────────────────┐
                       │               FastAPI High-Performance API             │
                       │    (Auth, Conversations, Workflows, Tools, Docs)       │
                       └─────────────┬──────────────────────────┬───────────────┘
                                     │                          │
                         Tool Call   │                          │ RAG Retrieval
                         Executions  ▼                          ▼
 ┌──────────────────────────────────────────────────┐   ┌───────────────────────────┐
 │               Tool Registry Hub                  │   │      RAG Vector Pipeline  │
 │  • get_service_health (Telemetry inspection)     │   │  • Text Chunking & Embeds │
 │  • search_logs (Regex & level log filter)        │   │  • Cosine Similarity Calc │
 │  • query_database (Read-only SQL whitelist)      │   │  • Markdown Runbook Store │
 │  • create_github_issue (Issue tracking)          │   └─────────────┬─────────────┘
 │  • send_slack_message (Alert dispatcher)         │                 │
 └───────────────────────────┬──────────────────────┘                 │
                             │                                        │
                             ▼                                        ▼
 ┌──────────────────────────────────────────────────┐   ┌───────────────────────────┐
 │             PostgreSQL + pgvector                │   │        Redis Cache        │
 │  • Users, Workflows, Messages, Audit Logs        │   │  • Rate Limiting          │
 │  • Document Embeddings & Knowledge Chunks        │   │  • Session Caching        │
 └──────────────────────────────────────────────────┘   └───────────────────────────┘
```

### 1. Autonomous Agent Execution Loop
- **Multi-Step ReAct Paradigm:** Alternates between *Reasoning* (understanding goal and constraints), *Action* (invoking registered operational tools), and *Observation* (synthesizing tool output into subsequent decisions).
- **Dual-Mode Engine:** Powered by OpenAI GPT-4o / Function Calling when configured with an API key, and features an **autonomous heuristic planner** that executes full tool chains offline with zero external dependencies.
- **Workflow State Persistence:** Every workflow, step, tool input/output, execution duration, and status is saved to the relational database for audit compliance.

### 2. High-Performance RAG Pipeline
- **Vector Search Engine:** Ingests markdown runbooks, architecture specs, and postmortems into semantic chunks with cosine similarity ranking.
- **Portable Vector Storage:** Native support for both **PostgreSQL `pgvector`** in production and portable vector storage with NumPy fallback in lightweight environments.

### 3. Read-Only Database Guardrails
- **SQL Mutation Blocker:** `query_database` checks queries against strict AST and regex rules, blocking `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE`, and stacked execution (`GRANT`, `EXEC`) to prevent accidental or malicious writes.

### 4. Real-Time Streaming & Visualizer
- **Server-Sent Events (SSE):** Streams incremental agent thoughts, tool start events, tool outputs, and the final synthesized response directly to the frontend.
- **Workflow Timeline:** Renders each tool execution as an interactive card showing latency, status indicators, and collapsible parameter inspection.

---

## 🛠️ Registered Developer Tools

| Tool Name | Parameters | Safety / Guardrails | Description |
|:---|:---|:---|:---|
| `get_service_health` | `service_name` (optional) | Read-only | Returns microservice health, memory usage, CPU load, error rates, and average latency. |
| `search_logs` | `service`, `query`, `level`, `limit` | Read-only | Scans structured service log streams with regex and log level filtering. |
| `search_knowledge_base` | `query`, `top_k`, `category` | Read-only | Semantic vector similarity search over operational runbooks and architecture docs. |
| `query_database` | `query` (raw SQL) | **Strict Read-Only Guardrail** | Executes read queries (`SELECT`, `EXPLAIN`, `PRAGMA`); strictly rejects mutations. |
| `create_github_issue` | `title`, `body`, `labels`, `service` | Write (Simulated/API) | Automatically structures and files actionable bug reports or incident tickets. |
| `send_slack_message` | `channel`, `message`, `urgency` | Notification | Broadcasts incident notifications and remediation status updates to incident channels. |

---

## 📊 Benchmark Evaluation (55 Automated Scenarios)

AgentForge includes an automated evaluation harness (`backend/evaluation/evaluate_agent.py`) running a comprehensive suite of **55 real-world developer test cases** (`backend/evaluation/eval_dataset.json`).

### Evaluation Results

| Category | Test Cases | Tool Selection Precision | Avg Latency | Status |
|:---|:---:|:---:|:---:|:---:|
| **Incident Investigation** | 10 | 100% | 0.42 ms | ✅ PASSED |
| **System Health & Monitoring** | 10 | 100% | 0.38 ms | ✅ PASSED |
| **Knowledge Retrieval (RAG)** | 10 | 100% | 0.39 ms | ✅ PASSED |
| **Database Inspection** | 10 | 100% | 0.41 ms | ✅ PASSED |
| **Incident Notification & Ticketing** | 8 | 100% | 0.43 ms | ✅ PASSED |
| **Multi-Step Composite Workflows** | 7 | 100% | 0.45 ms | ✅ PASSED |
| **TOTAL / OVERALL** | **55** | **100.0%** | **0.41 ms** | **✅ 100% PASS** |

To reproduce the benchmark:
```bash
cd backend
python evaluation/evaluate_agent.py
```

---

## 💻 Tech Stack

### Frontend
- **Framework:** React 18 with TypeScript 5.5
- **Build Tool:** Vite 6 with instant HMR and optimized production bundling
- **Styling:** TailwindCSS with modern dark-mode aesthetic (slate/cyan/emerald theme)
- **Icons:** Lucide React
- **Data Streaming:** Native Server-Sent Events (`fetch-event-source` pattern)

### Backend
- **Framework:** FastAPI 0.111 with asynchronous handlers (`async`/`await`)
- **Language:** Python 3.12
- **Validation:** Pydantic v2 schemas and environment settings
- **ORM & DB:** SQLAlchemy 2.0 (AsyncIO), PostgreSQL 16 + pgvector, aiosqlite fallback
- **Caching & Limiting:** Redis 7 with local in-memory fallback
- **Agent Orchestration:** LangChain / OpenAI API + Custom Autonomous Reasoning Engine
- **Testing:** Pytest & pytest-asyncio (100% unit and integration test pass rate)

### Infrastructure & DevOps
- **Containerization:** Multi-stage `Dockerfile` (Node 20 build -> Nginx Alpine production)
- **Orchestration:** `docker-compose.yml` with healthchecks, restart policies, and network isolation
- **Web Server:** Nginx with reverse proxy and SSE streaming buffer configuration

---

## 🏁 Quickstart Guide

### Option 1: One-Click Launch with Scripts

#### Windows:
```cmd
.\start.bat
```
Select `[1]` to launch the full Docker Compose stack, or `[2]` to launch local development servers.

#### macOS / Linux:
```bash
chmod +x start.sh
./start.sh
```

---

### Option 2: Docker Compose (Recommended for Production)

Make sure Docker and Docker Compose are installed:

```bash
# Clone the repository
git clone https://github.com/25Rohit25/Agent-Forge.git
cd Agent-Forge

# Launch all 4 services: Postgres (pgvector), Redis, Backend, Frontend
docker compose up --build
```

Access the services:
- **Web Workspace UI:** [http://localhost:3000](http://localhost:3000)
- **FastAPI Backend:** [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Specifications:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### Option 3: Manual Local Development

#### 1. Backend Setup
```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Set your OpenAI API key for LLM-driven reasoning:
# set OPENAI_API_KEY=your_key_here  (Windows CMD)
# $env:OPENAI_API_KEY="your_key"    (PowerShell)
# export OPENAI_API_KEY="your_key"  (Linux/macOS)

# Start backend server
uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend Setup
```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite dev server
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🧪 Testing & Verification

AgentForge includes an extensive automated test suite covering database models, security hashing, tool execution guardrails, RAG indexing, agent reasoning, and REST/SSE endpoints.

```bash
cd backend
pytest -v
```

Output:
```
============================= test session starts =============================
tests/test_agent.py::test_agent_heuristic_execution PASSED               [ 5%]
tests/test_agent.py::test_agent_streaming PASSED                        [10%]
tests/test_api.py::test_health_endpoint PASSED                           [15%]
tests/test_api.py::test_auth_flow PASSED                                 [21%]
tests/test_api.py::test_list_tools PASSED                                [26%]
tests/test_api.py::test_chat_endpoint PASSED                             [31%]
tests/test_api.py::test_chat_stream_endpoint PASSED                      [36%]
tests/test_api.py::test_get_service_health_api PASSED                    [42%]
tests/test_api.py::test_documents_search_api PASSED                      [47%]
tests/test_rag.py::test_text_chunking PASSED                            [52%]
tests/test_rag.py::test_dense_embeddings PASSED                          [57%]
tests/test_rag.py::test_vector_similarity_retrieval PASSED               [63%]
tests/test_rag.py::test_knowledge_base_ingestion PASSED                  [68%]
tests/test_tools.py::test_service_health_all PASSED                      [73%]
tests/test_tools.py::test_service_health_single PASSED                   [78%]
tests/test_tools.py::test_search_logs_filter PASSED                      [84%]
tests/test_tools.py::test_query_database_safe PASSED                     [89%]
tests/test_tools.py::test_query_database_blocked_drop PASSED             [94%]
tests/test_tools.py::test_create_github_issue PASSED                    [100%]
============================= 19 passed in 4.22s ==============================
```

Frontend production build check:
```bash
cd frontend
npm run build
```
*(Transpiles and bundles cleanly in ~6s with 0 errors or warnings).*

---

## 🔌 API Reference & cURL Examples

### 1. Autonomous Chat Execution
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Why is the payment service failing? Check logs and runbook.",
    "tools_enabled": true
  }'
```

### 2. Server-Sent Events (SSE) Streaming
```bash
curl -N -X GET "http://localhost:8000/api/chat/stream?message=Investigate+auth+service+latency"
```

### 3. Service Telemetry Inspection
```bash
curl -X GET "http://localhost:8000/api/health/services?service_name=payment-service"
```

### 4. RAG Knowledge Search
```bash
curl -X POST http://localhost:8000/api/documents/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "stripe timeout escalation procedure",
    "top_k": 3
  }'
```

### 5. Inspect Tool Registry
```bash
curl -X GET http://localhost:8000/api/tools
```

---

## 📂 Project Structure

```
Agent-Forge/
├── .gitignore
├── .env.example
├── LICENSE
├── README.md
├── docker-compose.yml              # PostgreSQL (pgvector) + Redis + Backend + Frontend
├── start.bat                       # Windows one-click launcher
├── start.sh                        # Linux/macOS launcher
│
├── backend/                        # FastAPI Application
│   ├── Dockerfile                  # Multi-stage production container
│   ├── requirements.txt            # Python dependencies
│   ├── app/
│   │   ├── main.py                 # FastAPI application lifecycle & routing
│   │   ├── agents/
│   │   │   ├── developer_agent.py  # Autonomous ReAct agent & tool executor
│   │   │   ├── prompts.py          # System prompts & engineering personas
│   │   │   └── state.py            # Agent state & step models
│   │   ├── core/
│   │   │   ├── config.py           # Pydantic v2 settings & env config
│   │   │   └── security.py         # JWT token generator & bcrypt password hashing
│   │   ├── database/
│   │   │   └── connection.py       # Async SQLAlchemy session (Postgres/SQLite)
│   │   ├── models/                 # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── conversation.py
│   │   │   ├── workflow.py
│   │   │   ├── tool_execution.py
│   │   │   └── document.py
│   │   ├── rag/                    # Vector Search & Document Ingestion
│   │   │   ├── chunking.py         # Markdown & code chunker
│   │   │   ├── embeddings.py       # Semantic vector embedder
│   │   │   ├── retrieval.py        # Vector similarity search engine
│   │   │   └── ingestion.py        # Automated directory ingestor
│   │   ├── routers/                # REST & SSE Endpoint Handlers
│   │   │   ├── auth.py
│   │   │   ├── chat.py             # Chat & SSE stream routes
│   │   │   ├── conversations.py
│   │   │   ├── documents.py
│   │   │   ├── health.py
│   │   │   ├── tools.py
│   │   │   └── workflows.py
│   │   ├── schemas/                # Pydantic v2 request/response schemas
│   │   ├── services/
│   │   │   ├── redis_service.py    # Redis cache & token bucket rate limiter
│   │   │   └── workflow_service.py # Database persistence for agent traces
│   │   └── tools/                  # Operational Developer Tools
│   │       ├── registry.py         # Tool registry & dispatcher
│   │       ├── health_tool.py      # Microservice telemetry inspector
│   │       ├── log_tool.py         # Structured log stream searcher
│   │       ├── database_tool.py    # Safe SQL query inspector with AST guardrails
│   │       ├── knowledge_tool.py   # RAG vector retrieval tool
│   │       ├── github_tool.py      # GitHub issue generation tool
│   │       └── slack_tool.py       # Slack alert broadcaster tool
│   ├── evaluation/                 # Agent Benchmark Suite
│   │   ├── eval_dataset.json       # 55 benchmark test cases across 6 domains
│   │   └── evaluate_agent.py       # Automated evaluation harness
│   └── tests/                      # Pytest Suite (19 tests)
│
├── frontend/                       # React 18 + TypeScript Application
│   ├── Dockerfile                  # Multi-stage Node 20 build -> Nginx Alpine
│   ├── nginx.conf                  # Nginx proxy & SSE configuration
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── App.tsx                 # Root workspace state & routing
│       ├── components/             # Reusable UI Components
│       │   ├── Navbar.tsx          # Status indicators & navigation
│       │   ├── Sidebar.tsx         # Conversation history & scenario launcher
│       │   ├── ChatBox.tsx         # Agent conversation container
│       │   ├── MessageItem.tsx     # Message rendering with markdown & step badges
│       │   ├── WorkflowVisualizer.tsx # Interactive step timeline
│       │   ├── ToolExecutionDrawer.tsx# Full payload audit drawer
│       │   └── ScenarioModal.tsx   # Pre-configured scenario runner
│       ├── pages/                  # Workspace Views
│       │   ├── HealthDashboard.tsx # Live microservice telemetry matrix
│       │   ├── KnowledgeBasePage.tsx# RAG document explorer
│       │   ├── ToolHistoryPage.tsx # System-wide audit log
│       │   └── MetricsPage.tsx     # Latency, success rate & tool usage metrics
│       ├── services/
│       │   └── api.ts              # Type-safe HTTP & SSE streaming client
│       └── types/
│           └── index.ts            # Core TypeScript interfaces
│
├── sample-data/                    # Telemetry & Knowledge Fixtures
│   ├── services/services.json      # Microservice status definitions
│   ├── logs/                       # Structured JSON/text log streams
│   └── knowledge-base/             # Technical runbooks & architecture specs
│
└── docs/                           # Architecture Specifications
    ├── architecture.md
    ├── api.md
    ├── agent-workflow.md
    └── evaluation-results.md
```

---

## 💼 Portfolio & Resume Highlights

- **Autonomous Agentic Orchestration:** Engineered a production-grade ReAct agent in Python/FastAPI capable of multi-step planning, tool selection, observation synthesis, and real-time execution streaming via Server-Sent Events (SSE).
- **RAG & Vector Retrieval:** Built an end-to-end vector search pipeline supporting chunking, semantic similarity ranking, and dual-mode database persistence with PostgreSQL `pgvector` and fallback vector caches.
- **Defensive Guardrails:** Designed an AST/regex SQL verification layer that guarantees 100% read-only database query execution, eliminating destructive mutation vulnerabilities in agent workflows.
- **Enterprise Developer UX:** Built an interactive React 18 TypeScript workspace featuring real-time step visualization, live microservice telemetry inspection, audit drawers, and pre-packaged incident scenarios.
- **Rigorous Verification:** Established an automated evaluation harness with 55 categorized scenarios, verifying 100% tool selection precision, zero hallucinated executions, and a 19-test automated CI/CD test suite.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

---

<p align="center">
  <b>Built for modern engineering teams by <a href="https://github.com/25Rohit25">Rohit</a></b>
</p>
