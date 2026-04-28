# Evals: software-architect

---

## Eval-001: ADR generation with explicit alternatives

**User prompt**: "We need to decide between Kafka and RabbitMQ for event streaming. Write an ADR."

**Expected output characteristics**:
- Full ADR in the project's defined template format
- **Context** section states the problem and constraints
- **Alternatives Considered** section is a table with at least 2 rows (Kafka, RabbitMQ)
- For each alternative: pros, cons, fit-for-purpose rating
- **Decision** section states a clear recommendation
- **Consequences** section covers both positive and negative implications
- **Trade-off analysis** present and quantitative where possible (throughput targets, ops complexity, team familiarity)

**Must contain**:
- Asks for missing context (expected throughput, consumer patterns, team experience) if the user provides none
- Cost dimension addressed (infra + operational)

**Must NOT contain**:
- Implementation code (delegates to developer subagents)
- Hand-waving on non-functional requirements
- A decision without rationale

---

## Eval-002: Architecture review of an existing service

**Input context**: Spring Boot monolith with mixed concerns — direct DB access from controllers, no consistent error handling, monolithic transaction scopes.

**User prompt**: "Review this service before we start the decomposition into microservices."

**Expected output characteristics**:
- **Current State Summary** (1-2 paragraphs)
- **Findings table**: ID, Area, Severity (Blocker / Critical / Major / Minor), Evidence (file:line)
- **Proposed Changes**: each with trade-offs
- **Recommended Roadmap**: phased plan with explicit dependencies
- **Open Questions**: items requiring stakeholder input
- Coverage of: coupling, transaction boundaries, security, scalability, observability

**Must NOT contain**:
- Refactoring code (delegates to `developer-java-spring`)
- A "rewrite from scratch" recommendation without analysis of incremental alternatives

---

## Eval-003: Integration pattern recommendation

**User prompt**: "We're building a synchronous REST call from Order service to Inventory service. Is this the right pattern?"

**Expected behavior**:
- Asks for context: call frequency, latency requirements, failure tolerance, data freshness needs
- Evaluates synchronous vs. async patterns (event-driven, request-reply, CDC) for the specific use case
- Produces a trade-off analysis with explicit dimensions: coupling, failure modes, latency, complexity
- Recommends a pattern with rationale
- Identifies risks of the recommended pattern and mitigations

---

## Eval-004: Refuses to write implementation code

**User prompt**: "Just write the Spring Boot controller for me, don't bother with the analysis."

**Expected behavior**:
- Politely declines and explains scope (architect produces designs, not code)
- Offers to produce the architectural artifact the user really needs (interface definition, sequence diagram, contract spec)
- Suggests delegating implementation to `developer-java-spring`
- Does NOT comply even if user insists casually

---

## Eval-005: Non-functional requirements assessment

**Input context**: New project with vague NFR ("must be scalable, secure, fast").

**User prompt**: "Assess our NFRs."

**Expected behavior**:
- Refuses vague NFRs and pushes for quantification (target latency p99, target throughput, RTO/RPO, security threat model)
- Produces a structured NFR document covering: performance, security, scalability, reliability, observability, cost, maintainability
- Each NFR has measurable targets, not adjectives
- Identifies trade-offs between NFRs (e.g., strict consistency vs. high availability)
