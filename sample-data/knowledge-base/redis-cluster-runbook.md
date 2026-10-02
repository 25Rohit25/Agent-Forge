# Redis Cluster & Cache Operations Runbook

## Overview
AgentForge and microservices utilize Redis for:
1. High-throughput distributed rate limiting.
2. Temporary agent workflow execution state (`agent:workflow:<id>`).
3. Caching hot RAG query embeddings and conversational memory.

## Common Alerts & Remediation
- **OOM (Out of Memory) Command Not Allowed**:
  - Eviction policy should be set to `volatile-lru` or `allkeys-lru`.
  - Check memory fragmentation ratio via `INFO memory`.
- **Failover / Connection Refused**:
  - If a Redis master node fails, Sentinel or Cluster orchestrator promotes a replica within 3-5 seconds.
  - Client connection pools automatically retry using exponential backoff.
