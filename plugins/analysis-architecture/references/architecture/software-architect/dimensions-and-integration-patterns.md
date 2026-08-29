# Architecture dimensions and integration patterns

> Reference doc for `software-architect`. Read at runtime when analysing a
> system (sweep the dimensions before writing findings) and when evaluating or
> proposing an integration. The decision logic and the output templates stay in
> the agent body; the two exhaustive checklists live here.

## Contents

- [Architecture dimensions](#architecture-dimensions): the six dimensions to sweep systematically on any system analysis, with the questions each one asks.
- [Integration patterns: quick reference](#integration-patterns-quick-reference): the pattern table, when each applies and what to watch for.

## Architecture dimensions

When analyzing any system, consider these dimensions systematically:

**Security**
- Authentication and authorization model (who can do what, how verified)
- Data classification and protection in transit and at rest
- Attack surface: exposed endpoints, dependencies with known CVEs, secrets management
- Compliance requirements (GDPR, PCI, SOC2, etc.) and whether the architecture supports them

**Performance**
- Expected load profile (throughput, concurrency, latency targets)
- Bottlenecks: synchronous blocking calls, N+1 queries, missing indexes, missing caching
- Scalability model: vertical vs. horizontal, stateful vs. stateless components

**Reliability**
- Failure modes: what fails, how it fails, what cascades
- Single points of failure
- Recovery: circuit breakers, retries, fallbacks, graceful degradation
- SLA/SLO targets and whether the architecture can meet them

**Maintainability**
- Coupling and cohesion: bounded contexts, dependency direction, circular dependencies
- Testability: can individual components be tested in isolation?
- Operational observability: is the system inspectable in production?
- Team topology fit: does the architecture match team boundaries?

**Deployment**
- Build and deploy pipeline complexity
- Environment parity: how close are dev/staging/prod?
- Rollout strategy: can the system support zero-downtime deployments?
- Configuration management: are secrets managed correctly?

**Cost**
- Infrastructure cost model: fixed vs. variable
- Operational overhead: who owns what in production?
- Hidden costs: egress, licensing, support contracts

## Integration patterns: quick reference

When evaluating or proposing integration, identify the appropriate pattern explicitly:

| Pattern | Use when | Watch for |
|---------|----------|-----------|
| Synchronous REST/gRPC | Low latency needed, caller needs immediate result | Tight coupling, cascading failures |
| Async messaging (Kafka, RabbitMQ) | Decoupling needed, eventual consistency acceptable | At-least-once delivery semantics, ordering guarantees |
| Event sourcing | Audit trail required, temporal queries needed | Storage growth, event schema evolution |
| Saga pattern | Distributed transactions across services | Compensation logic complexity |
| BFF (Backend for Frontend) | Multiple clients with different data needs | Additional layer to maintain |
| API Gateway | Cross-cutting concerns: auth, rate limiting, routing | Single point of failure, vendor lock-in |
