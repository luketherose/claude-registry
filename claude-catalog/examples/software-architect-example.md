# Example: software-architect

## Scenario 1: Architecture analysis of an existing Spring Boot service

**Setup**: A Spring Boot monolith is to be analyzed before breaking it into microservices.

**User prompt**:
> Review the architecture of this service. I need to understand the main issues before
> we start the decomposition work. Focus on coupling, scalability blockers, and security.

**What the subagent does**:
1. Reads the project structure (`Glob`, `Read`)
2. Identifies the main architectural concerns (coupling between layers, transaction boundaries)
3. Produces an Architecture Analysis Report with findings table and proposed changes
4. Notes security issues (e.g. missing authorization on endpoints)
5. Recommends a decomposition starting point based on cohesion analysis

**Expected output sections**:
- Current State Summary
- Findings table (ID, Area, Severity, Evidence)
- Proposed Changes (each with trade-offs)
- Recommended Roadmap
- Open Questions

---

## Scenario 2: Writing an ADR for a technology choice

**User prompt**:
> We need to decide between Kafka and RabbitMQ for our event streaming. Write an ADR.

**What the subagent does**:
1. Asks for context if not provided: expected throughput, consumer patterns, team experience
2. Produces a full ADR with Alternatives Considered table
3. Includes trade-off analysis for both options
4. States a clear recommendation with rationale

**Expected output**: Full ADR in the defined template format.

---

## Scenario 3: Integration pattern review

**User prompt**:
> We're building a synchronous REST call from the Order service to the Inventory service.
> Is this the right pattern?

**What the subagent does**:
1. Asks for context about the call (frequency, latency requirements, failure tolerance)
2. Evaluates synchronous vs. async patterns for this use case
3. Produces a trade-off analysis
4. Recommends a pattern with rationale

**What the subagent does NOT do**:
- Write the actual implementation code (it will note which developer subagent should do that)
