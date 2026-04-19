# Architecture Decision Record — Template

Copy this template when documenting a new architecture decision. Place the file in
your project's `docs/adr/` directory as `ADR-NNN-short-title.md`.

---

## ADR-{NNN}: {Title}

**Date**: YYYY-MM-DD
**Status**: Proposed | Accepted | Deprecated | Superseded by ADR-NNN
**Deciders**: {Names or roles of people involved in this decision}
**Tags**: {e.g. security, persistence, integration, deployment}

---

### Context

What situation, problem, or force is driving this decision?
Include:
- Relevant constraints (technical, organizational, regulatory)
- The quality attributes that matter most for this decision (performance, security, etc.)
- What will happen if no decision is made

Keep this factual and concise. This is not the place for recommendations — just context.

### Decision

One clear statement of what we have decided to do.

> Example: "We will use PostgreSQL as the primary datastore for the Order service,
> accessed via Spring Data JPA with Flyway for schema migrations."

### Rationale

Why did we choose this option over the alternatives? What evidence or analysis led to
this conclusion? Reference any trade-off analysis, benchmarks, or experiments conducted.

### Alternatives Considered

| Option | Pros | Cons | Why Rejected |
|--------|------|------|-------------|
| {Option A — chosen} | ... | ... | N/A (selected) |
| {Option B} | ... | ... | {Specific reason} |
| {Option C} | ... | ... | {Specific reason} |

### Consequences

**Positive**:
- {What becomes easier or better as a result}

**Negative**:
- {What becomes harder, more expensive, or constrained}
- {Technical debt introduced, if any}

**Neutral**:
- {Side effects that are neither positive nor negative}

### Related decisions

- Supersedes: ADR-NNN (if applicable)
- Related to: ADR-NNN (if applicable)
- Blocked by: ADR-NNN (if applicable)

### Review date

{Date when this decision should be revisited, if relevant — e.g. when the technology
reaches end of life, or after a specific milestone}

---

## Usage notes

- Number sequentially within your project: ADR-001, ADR-002, etc.
- Never delete an ADR — if a decision is reversed, mark it "Superseded by ADR-NNN"
- Keep ADRs short: 1–2 pages max
- Link to this file from relevant CLAUDE.md or architecture overview docs
- The `software-architect` subagent can produce a draft ADR when asked
