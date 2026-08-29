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

## Known operational facts

- Credentials for the database live in `application.yml`, committed to the repo.
- `management.endpoints.web.exposure.include` is `*` and the actuator port is the
  same as the public HTTP port.
- CORS allows every origin.
- The payment call is synchronous and inside the request transaction.
- No structured audit log exists for order state changes.
- Restores from backup have never been exercised. RPO and RTO are undefined.
- Monthly cloud spend is 4,100 EUR, of which 2,600 EUR is the always-on
  over-provisioned RDS instance (db.r6g.2xlarge at 6% average CPU).
