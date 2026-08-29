# Orders service

Single Spring Boot 3 deployment, one PostgreSQL instance, two replicas behind an
ALB. No cache tier. Deployed by hand from a laptop.

## Runtime dependencies

| Dependency | Protocol | Timeout | Retry | Circuit breaker |
|---|---|---|---|---|
| payments.internal | HTTP/1.1 | none set | 5 | none |
| warehouse.internal | HTTP/1.1 | 2s | 0 | none |
| PostgreSQL | JDBC | 30s | n/a | n/a |

## Traffic

| Metric | Value |
|---|---|
| Peak requests/second | 340 |
| p99 latency | 2.4s |
| Tomcat max threads | 200 |
| Hikari max pool size | 5 |

## Operations

- `OrderService.place` is annotated `@Transactional`; the call to
  `payments.internal` is made inside it, before the order row is flushed.
- Order state changes are written with `log.info` and are not persisted anywhere.
- RDS automated backup retention is 7 days. No restore drill appears in the
  runbook, and the runbook states no RPO and no RTO.
- Monthly cloud spend is 4,100 EUR, of which 2,600 EUR is the RDS instance
  (db.r6g.2xlarge, 6% average CPU over the last 90 days).
