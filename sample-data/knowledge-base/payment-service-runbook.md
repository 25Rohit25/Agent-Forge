# Payment Service Runbook & Incident Troubleshooting

## Service Overview
The Payment Service manages authorization, capture, and settlement of credit card and digital wallet transactions. It maintains a dedicated PostgreSQL connection pool via HikariCP and publishes transaction receipts to Kafka.

## Known Failure Modes

### 1. ConnectionPoolTimeoutException (Database Pool Exhaustion)
- **Symptoms**:
  - API latency spikes above 800ms (normal is < 150ms).
  - Error rate increases beyond 5% with HTTP 500 / 504 responses.
  - Logs show: `ConnectionPoolTimeoutException: Timeout waiting for idle connection in pool [HikariCP-PaymentPool]`.
  - HikariCP active connections stick at maximum (e.g. 50/50).
- **Root Cause**:
  - Unclosed JDBC connections during third-party gateway timeouts.
  - Long-running unindexed queries holding connections open.
  - Missing `@Transactional(timeout = 5)` on charge verification routines, resulting in connection leaks.
- **Immediate Mitigation**:
  1. Increase HikariCP maximum pool size from 50 to 80 via runtime configuration.
  2. Verify that connection leak detection is set to `leakDetectionThreshold: 20000ms`.
  3. Restart degraded worker pods sequentially to flush leaked sockets:
     `kubectl rollout restart deployment/payment-service -n production`
  4. Ensure PostgreSQL max_connections is configured above total pod capacity.

### 2. Upstream Gateway Outage (Stripe / Adyen)
- **Symptoms**: HTTP 502 / 503 errors with `GatewayUnavailableException`.
- **Mitigation**: Enable local circuit breaker to queue charges for asynchronous reconciliation.
