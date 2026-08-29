# Actor-Feature Mapper: Output Specification

This document defines the exact file formats, JSONL schemas, and output templates for `actor-feature-mapper`. Read it immediately before writing any output file.

---

## Output files

### File 1: `docs/analysis/01-functional/01-actors.md`

```markdown
---
agent: actor-feature-mapper
generated: <ISO-8601>
sources:
  - .indexing-kb/01-overview.md
  - .indexing-kb/06-data-flow/database.md
  - .indexing-kb/04-modules/<relevant>.md
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
---

# Actors

This document inventories the actors AS-IS: humans, systems, and inferred
roles that interact with the application as it exists today.

## Summary
- Total actors: <N>
- Human actors: <N>
- System actors: <N>
- Inferred (not explicitly named): <N>

## Actor catalog

### A-01 — <Actor name>
- **Type**: human | system | inferred
- **Description**: <1-2 sentences in plain language>
- **Permissions / scope**: <what this actor can do, at high level>
- **Evidence**: <KB references that support this identification>
- **Sources**:
  - .indexing-kb/06-data-flow/database.md (users table)
  - .indexing-kb/04-modules/auth.md
- **Confidence**: high | medium | low
- **Notes**: <anything ambiguous>

### A-02 — ...

## Open questions
- <e.g., "Is there a distinction between 'analyst' and 'data scientist'
  actors? Both are mentioned in module docstrings but no permission
  difference is encoded.">
```

---

### File 2: `docs/analysis/01-functional/02-features.md`

```markdown
---
agent: actor-feature-mapper
generated: <ISO-8601>
sources:
  - .indexing-kb/04-modules/
  - .indexing-kb/05-streamlit/pages.md
  - .indexing-kb/07-business-logic/business-rules.md
  - .indexing-kb/08-synthesis/bounded-contexts.md
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
---

# Feature map

This document inventories the features (business capabilities) of the
application AS-IS, grouped by bounded context where available.

## Summary
- Total features: <N>
- Interactive: <N>
- Automated: <N>
- Bounded contexts covered: <list>

## Feature catalog

### F-01 — <Feature name (verb-led, business language)>
- **Description**: <1-2 sentences, business language>
- **Bounded context**: <name or "n/a">
- **Type**: interactive | automated | hybrid
- **Implemented in**: <module paths from KB>
- **Actors**: A-01, A-02
- **Sources**:
  - .indexing-kb/04-modules/<pkg>.md
  - .indexing-kb/07-business-logic/business-rules.md#<anchor>
- **Confidence**: high | medium | low
- **Notes**: <e.g., "feature is gated behind a feature flag in config.yaml">

### F-02 — ...

## Actor × Feature matrix

| Actor \ Feature | F-01 | F-02 | F-03 | ... |
|---|---|---|---|---|
| A-01 | full | — | read | ... |
| A-02 | — | full | full | ... |

Legend: full | read | restricted | — (no access)

## Orphans (flag for review)
- Features without any actor: <list — likely dead code or missing actor>
- Actors without any feature: <list — likely identification error>

## Open questions
- <e.g., "Feature F-07 (export to CSV) is reachable from two screens but
  the second invocation appears unreachable from the navigation; is it
  legacy or a hidden flow?">
```

---

## JSONL outputs (write before markdown)

### `docs/analysis/01-functional/raw/actor-candidates-raw.jsonl`

Raw actor findings before normalization: one record per candidate actor.

### `docs/analysis/01-functional/normalized/actor-candidates.jsonl`

One record per actor. Required fields:

```json
{
  "actor_id": "A-01",
  "name": "Actor name",
  "type": "human | system | inferred",
  "confidence": "high | medium | low",
  "inference_level": "direct | derived | speculative",
  "evidence_ids": ["EV-000001"],
  "description": "1-2 sentence description",
  "permissions_scope": "what this actor can do"
}
```

If no direct evidence exists for an actor, set `confidence: low` and add the actor to `docs/analysis/01-functional/normalized/functional-gaps.jsonl` as well.

### `docs/analysis/01-functional/normalized/feature-candidates.jsonl`

One record per feature. Required fields:

```json
{
  "feature_id": "F-01",
  "name": "Feature name",
  "bounded_context": "context name or null",
  "type": "interactive | automated | hybrid",
  "confidence": "high | medium | low",
  "inference_level": "direct | derived | speculative",
  "evidence_ids": ["EV-000001"],
  "description": "1-2 sentence business description",
  "actors": ["A-01"],
  "implementing_modules": ["module path"]
}
```

Each actor record must have `evidence_ids` citing at least one `EV-NNNNNN`. If no direct evidence, set `confidence: low` and add to `normalized/functional-gaps.jsonl`.
