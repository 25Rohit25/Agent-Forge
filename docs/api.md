# AgentForge API Specification

Base URL: `http://localhost:8000/api`

## Authentication

### `POST /auth/register`
Register a new developer account.
- **Request Body**:
  ```json
  {
    "email": "engineer@agentforge.dev",
    "password": "SecurePassword123!",
    "full_name": "DevOps Engineer"
  }
  ```
- **Response**:
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user": {
      "id": "usr_1",
      "email": "engineer@agentforge.dev",
      "full_name": "DevOps Engineer"
    }
  }
  ```

### `POST /auth/login`
Authenticate existing user and obtain JWT token.

---

## Agent Chat & Streaming

### `POST /chat`
Execute a synchronous chat message with the developer agent.
- **Request Body**:
  ```json
  {
    "conversation_id": "conv_123",
    "message": "Investigate why payment-service is slow and file an issue if error rate exceeds 5%."
  }
  ```
- **Response**:
  ```json
  {
    "conversation_id": "conv_123",
    "workflow_id": "wf_456",
    "response": "Investigation completed. Likely root cause: Database connection pool exhaustion...",
    "status": "COMPLETED",
    "steps_count": 4,
    "tools_used": ["get_service_health", "search_logs", "search_knowledge_base", "create_github_issue"]
  }
  ```

### `GET /chat/stream?conversation_id=...&message=...`
Server-Sent Events (SSE) endpoint providing real-time streaming updates of agent reasoning and tool executions.
- **Stream Events**:
  - `start`: Workflow initialized
  - `step_start`: Agent decided to invoke a tool with specific arguments
  - `step_complete`: Tool returned output with execution duration in ms
  - `analysis`: Agent intermediate synthesis
  - `final_response`: Complete markdown report
  - `done`: Stream finished

---

## Workflows & Observability

### `GET /workflows`
List all workflow runs with pagination and status filters.

### `GET /workflows/{id}`
Retrieve complete execution details for a workflow, including every tool invocation, input payloads, outputs, and timestamps.

### `GET /tool-executions/{workflow_id}`
Retrieve raw trace of tool executions for visual inspection.

---

## Services & Telemetry

### `GET /health/services`
Get current operational status, CPU, memory, error rates, and latency for all microservices.

### `GET /health/services/{service_name}`
Get granular telemetry for a specific service.

---

## Knowledge Base (RAG)

### `GET /documents`
List all ingested documentation and runbooks.

### `POST /documents/search`
Execute vector similarity search across technical documentation.
