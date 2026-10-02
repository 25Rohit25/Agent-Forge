# Incident Postmortem: Checkout Service Cascading Timeout & Deadlock (INC-042)

## Executive Summary
On August 14, 2026, an upstream latency spike in the payment-service triggered cascading request queueing in checkout-service. As checkout requests hung for 30 seconds waiting on payment confirmation, client retries overwhelmed inventory reservation locks, resulting in database deadlocks.

## Timeline
- **14:02 UTC**: Payment service database connection pool was exhausted due to a leaked connection in batch settlement.
- **14:04 UTC**: Checkout service HTTP calls to `/v1/charges` began exceeding the default 30-second timeout.
- **14:08 UTC**: Customers clicked "Checkout" repeatedly, spawning duplicate reservation requests.
- **14:15 UTC**: PostgreSQL detected multiple deadlocks on `inventory_item_reservations` rows.
- **14:28 UTC**: Payment service pool resized and checkout circuit breaker tripped, restoring stability.

## Action Items & Preventative Rules
1. Implement a 5-second strict timeout on all HTTP calls from checkout-service to payment-service.
2. Implement idempotent idempotency keys on checkout button submissions.
3. Decouple inventory reservation commit from payment gateway authorization.
