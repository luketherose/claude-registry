# Decomposition-architect — output templates

> Reference doc for `decomposition-architect`. Read at runtime when writing the
> Phase 4 Wave 1 outputs (bounded contexts, aggregate design, AS-IS↔TO-BE
> mapping). Schemas only — decision logic stays in the agent body.

---

## File 1: `.refactoring-kb/00-decomposition/bounded-contexts.md`

```markdown
---
agent: decomposition-architect
generated: <ISO-8601>
sources:
  - .indexing-kb/08-synthesis/bounded-contexts.md
  - .indexing-kb/07-business-logic/
  - docs/analysis/01-functional/02-features.md
  - docs/analysis/01-functional/06-use-cases/
  - docs/analysis/02-technical/01-code-quality/codebase-map.md
related_ucs: [UC-01, UC-02, ...]   (every UC handled by ANY BC)
related_bcs: [BC-01, BC-02, ...]
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
duration_seconds: <int>
---

# Bounded contexts (TO-BE)

## Context map

```mermaid
flowchart LR
  BC1[BC-01 Identity & Access]
  BC2[BC-02 Payments]
  BC3[BC-03 Reporting]
  Shared[shared kernel<br/>(common types)]

  BC1 --U--> BC2
  BC2 -.-> Shared
  BC3 --D--> BC2
```

(U = upstream-downstream; D = downstream; CF = customer-supplier;
SK = shared kernel; ACL = anti-corruption layer.)

## Bounded contexts

(See `bounded-context-examples.md` for the BC-01 / BC-02 entry shape.)

## AS-IS module → TO-BE BC mapping

| AS-IS module | LOC | Role | TO-BE BC | Notes |
|---|---|---|---|---|
| `infosync.payments.charge` | 423 | business | BC-02 | direct port |
| `infosync.shared.utils` | 89 | utility | (shared kernel) | promoted |
| `infosync.streamlit.dashboard` | 612 | UI | (FE only) | Angular replacement |
| `infosync.legacy.batch_v1` | 156 | batch | (deprecated — not migrating) | superseded by BC-03 reporting |

## Coverage check

- AS-IS modules: <total>
- Mapped to a BC: <N>
- Mapped to shared kernel: <N>
- Frontend-only (no Java port): <N>
- Deprecated (not migrating): <N> — see roadmap for cutover

## Open questions
- ...
```

---

## File 2: `.refactoring-kb/00-decomposition/aggregate-design.md`

```markdown
---
agent: decomposition-architect
generated: <ISO-8601>
sources: [...]
related_ucs: [...]
related_bcs: [...]
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
duration_seconds: <int>
---

# Aggregate design

For each BC, the aggregates that anchor data + behavior consistency.
(See `bounded-context-examples.md` for worked entries.)

## Open questions
- ...
```

---

## File 3: `.refactoring-kb/00-decomposition/module-decomposition.md`

Authoritative AS-IS → TO-BE table — see Method §2 in the agent body. Same
column shape as the mapping table in File 1, scoped to the full module
inventory (every module appears exactly once).

---

## File 6: `docs/refactoring/4.1-decomposition/README.md`

Index linking to all 4.1 outputs in `.refactoring-kb/00-decomposition/`
and the two ADRs.

---

## File 7: `docs/refactoring/4.1-decomposition/decomposition-summary.md`

One-page summary for stakeholder review: BC count, key decisions, AS-IS
coverage percent, escalation items.

---

## Reporting (text response to supervisor)

```markdown
## Files written
- .refactoring-kb/00-decomposition/bounded-contexts.md
- .refactoring-kb/00-decomposition/aggregate-design.md
- .refactoring-kb/00-decomposition/module-decomposition.md
- docs/adr/ADR-001-architecture-style.md
- docs/adr/ADR-002-target-stack.md
- docs/refactoring/4.1-decomposition/README.md
- docs/refactoring/4.1-decomposition/decomposition-summary.md

## Decomposition stats
- Bounded contexts:        <N>
- AS-IS modules covered:   <covered>/<total>
- Aggregates designed:     <N>
- UCs distributed:         <N>/<M>

## ADRs proposed
- ADR-001: <decision in one line>
- ADR-002: <stack summary in one line>

## Confidence
high | medium | low

## Duration (wall-clock)
<seconds>

## Open questions
- <e.g., "BC-04 'Reporting' has overlapping use cases with BC-02
  'Payments' — recommend boundary review with stakeholder">
```
