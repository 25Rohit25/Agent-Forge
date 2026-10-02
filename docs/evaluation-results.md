# AgentForge Evaluation & Benchmark Report

## Overview
Automated benchmark run evaluated on **2026-10-02 14:57:32 UTC**.
Total evaluation test cases: **55** across 8 core engineering categories.

## Summary Metrics
| Metric | Value |
|---|---|
| **Total Evaluation Prompts** | 55 |
| **Pass Rate** | **78.2%** (43/55) |
| **Tool Selection Precision** | **100.0%** |
| **Average Workflow Duration** | **0.4 ms** |
| **P95 Latency** | **0.9 ms** |

## Category Performance Breakdown
| Category | Evaluated Cases | Passed | Accuracy |
|---|---|---|---|
| Incident investigation | 12 | 10 | 83.3% |
| Service health | 10 | 9 | 90.0% |
| Log analysis | 10 | 10 | 100.0% |
| Documentation search | 11 | 4 | 36.4% |
| GitHub creation | 4 | 4 | 100.0% |
| Multi-tool workflow | 6 | 5 | 83.3% |
| Invalid request | 1 | 1 | 100.0% |
| Missing information | 1 | 0 | 0.0% |

## Key Findings & Reliability Analysis
1. **Tool Calling Accuracy**: The Agentic engine achieves high accuracy in selecting required observability (`get_service_health`, `search_logs`) and knowledge retrieval (`search_knowledge_base`) tools.
2. **Deterministic Guardrails**: Malicious or unauthorized attempts to execute arbitrary SQL are safely blocked and redirected to predefined read-only queries.
3. **Action Execution**: When requested by the developer, GitHub issues are created with proper markdown formatting, priority, and service tags.
