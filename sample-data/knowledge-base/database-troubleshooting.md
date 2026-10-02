# PostgreSQL Database Troubleshooting & Connection Pool Tuning

## Diagnosing Connection Starvation
When applications report connection timeouts, follow this diagnostic checklist:

1. **Check Active PostgreSQL Connections**:
   ```sql
   SELECT count(*), state FROM pg_stat_activity GROUP BY state;
   ```
   If `state = 'idle in transaction'`, an application thread opened a transaction and stalled without issuing COMMIT or ROLLBACK.

2. **Identify Long Running Queries**:
   ```sql
   SELECT pid, now() - pg_stat_activity.query_start AS duration, query, state
   FROM pg_stat_activity
   WHERE (now() - pg_stat_activity.query_start) > interval '5 seconds'
   ORDER BY duration DESC;
   ```

3. **HikariCP Recommended Parameters**:
   - `maximumPoolSize`: Compute as `((core_count * 2) + effective_spindle_count)`. Typically 20-50 per service instance.
   - `connectionTimeout`: Set to `10000ms` (avoid hanging indefinitely).
   - `idleTimeout`: `600000ms` (10 minutes).
   - `leakDetectionThreshold`: `15000ms` (logs a stack trace for any thread holding a connection longer than 15s).
