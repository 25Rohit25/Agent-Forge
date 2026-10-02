# AgentForge Agent Workflow & Decision Engine

## 1. Multi-Step Execution Lifecycle

The AgentForge Agentic Engine operates through a multi-step loop:

```
[ Engineer Request ]
        │
        ▼
┌───────────────────────────────┐
│     Step 1: Goal Analysis     │  Deconstruct prompt into target services,
│                               │  intentions, and required actions.
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│   Step 2: Service Telemetry   │  Query get_service_health() to assess
│                               │  error rates, latency, and degradation.
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│   Step 3: Log Pattern Search  │  Query search_logs() for ERROR / FATAL lines,
│                               │  database timeouts, or unhandled exceptions.
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│   Step 4: RAG Knowledge Query │  Search internal documentation & postmortems
│                               │  for known failure modes and mitigation runbooks.
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│   Step 5: Evidence Synthesis  │  Correlate telemetry + logs + knowledge base
│                               │  into a structured root cause hypothesis.
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│   Step 6: Automated Action    │  If requested or warranted, file a GitHub issue
│                               │  or send a Slack engineering alert.
└───────────────┬───────────────┘
                │
                ▼
[ Structured Root Cause Report ]
```

## 2. Tool Execution Rules & Guardrails
- **Read-Only Database Access**: Database queries are strictly limited to predefined, safe query types. Arbitrary SQL execution is prohibited.
- **Idempotency**: External action tools (e.g. GitHub issue creation) verify existing tickets to prevent duplicate issue spam.
- **Deterministic Transparency**: Every tool invocation records timestamp, input JSON, output JSON, duration in milliseconds, and status (SUCCESS / FAILED).
