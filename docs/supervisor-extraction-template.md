# Supervisor extraction template

Concrete recipe for extracting per-phase / per-wave content out of a large
supervisor agent body into reference docs. Use this when an agent's system
prompt grows past the Anthropic `agent-development` rubric body ceiling
(10 000 chars) — typical for the Phase 0–5 supervisors in this registry.

---

## When to extract

Extract a section out of a supervisor body when **all** of the following hold:

1. The agent body is over the 10 000-char ceiling (the validator emits a
   warning).
2. The bulk of the bytes lives in `## Phase <N>`, `## Wave <N>`, `## Step <N>`,
   or per-sub-agent dispatch templates that the supervisor reads once at
   dispatch time, not on every reasoning step.
3. The extracted content is reference material (templates, schemas, schematics,
   sample prompts) — not the supervisor's own decision logic.

Do NOT extract:

- The role definition (`## Role`).
- The orchestration loop (the actual decision flow).
- The `## When to invoke` section.
- The `## Output format` for user-facing messages.
- Any `## What you always do` / `## What you never do` invariants — these are
  consulted on every step.

---

## Target layout

```
claude-catalog/
├── agents/<topic>/<supervisor>.md       ← supervisor body (≤ ~8 000 chars)
└── docs/
    └── <topic>/                         ← extracted reference docs
        ├── phase-<N>-<name>.md
        ├── wave-<N>-<name>.md
        └── dispatch-templates.md
```

`<topic>` matches the agent's catalog topic folder (e.g., `refactoring-tobe`,
`baseline-testing`, `tobe-testing`).

---

## How the supervisor references the extracted docs

The supervisor body should contain a **single anchor section** that lists every
reference doc with one line per doc explaining when to read it. Example:

```markdown
## Reference docs

This supervisor's per-wave templates and dispatch prompts live in
`claude-catalog/docs/refactoring-tobe/` and are read on demand. Read each
doc only when the matching wave is about to start — not preemptively.

| Doc | Read when |
|---|---|
| `phase-4-wave-1-decomposition.md`  | dispatching `decomposition-architect` (W1) |
| `phase-4-wave-2-api-contract.md`   | dispatching `api-contract-designer` (W2) |
| `phase-4-wave-3-backend.md`        | dispatching `backend-scaffolder` + `data-mapper` + `logic-translator` (W3 BE) |
| `phase-4-wave-3-frontend.md`       | dispatching `frontend-scaffolder` (W3 FE) |
| `phase-4-wave-4-hardening.md`      | dispatching `hardening-architect` (W4) |
| `phase-4-wave-5-roadmap.md`        | dispatching `migration-roadmap-builder` (W5) |
| `phase-4-wave-6-challenger.md`     | dispatching `phase4-challenger` (W6) |
```

The supervisor's tool list must include `Read` so the agent can fetch the
doc at runtime. No new tool is needed.

---

## Reference-doc shape

Each extracted doc is a stand-alone Markdown file with this skeleton:

```markdown
# <Phase|Wave|Step> <N> — <name>

> Reference doc for `<supervisor-agent>`. Read at runtime when the matching
> wave is about to start.

## Goal

One paragraph: what this wave produces and why it exists.

## Inputs

| Source | What to read | Required? |
|---|---|---|
| `.indexing-kb/...` | … | yes |
| `docs/analysis/01-functional/...` | … | conditional |

## Sub-agents to dispatch

For each sub-agent, give the dispatch prompt as a fenced block the supervisor
copies and parametrises:

\`\`\`
You are `<sub-agent>`.
Read: <inputs>
Produce: <output path>
Constraints: <hard rules — strict AS-IS, no Flyway, ...>
\`\`\`

## Output

| Path | Schema | Owner |
|---|---|---|
| `docs/analysis/02-technical/<name>.md` | … | this wave |

## Stop conditions

When to stop and ask the user; when to continue automatically.
```

---

## Worked example — one wave

Below is a fully worked extracted doc for an imaginary `Phase 4 — Wave 1`.
Copy and adapt for each wave that gets extracted.

````markdown
# Phase 4 — Wave 1: Bounded-context decomposition

> Reference doc for `refactoring-tobe-supervisor`. Read at runtime when W1
> is about to start.

## Goal

Produce the bounded-context map, the AS-IS↔TO-BE module map, and ADR-001 +
ADR-002. Without these, every downstream wave is blocked.

## Inputs

| Source | What to read | Required? |
|---|---|---|
| `.indexing-kb/00-overview.md` | system overview | yes |
| `.indexing-kb/05-business-logic/` | domain concepts, glossary | yes |
| `docs/analysis/01-functional/use-cases.md` | use-case catalogue | yes |
| `docs/analysis/02-technical/code-quality.md` | hotspots & monolith smells | conditional |

## Sub-agents to dispatch

```
You are `decomposition-architect`.
Read:
  - .indexing-kb/00-overview.md
  - .indexing-kb/05-business-logic/
  - docs/analysis/01-functional/use-cases.md
Produce:
  - docs/refactoring/4.1-decomposition/bounded-contexts.md
  - docs/refactoring/4.1-decomposition/as-is-to-be-map.md
  - docs/refactoring/4.1-decomposition/ADR-001-architecture-style.md
  - docs/refactoring/4.1-decomposition/ADR-002-target-stack.md
Constraints:
  - First phase that may reference TO-BE technology.
  - Aggregates and value objects respect bounded-context boundaries.
  - One ADR per architectural choice; alternatives must be documented.
```

## Output

| Path | Schema | Owner |
|---|---|---|
| `docs/refactoring/4.1-decomposition/bounded-contexts.md` | DDD context map | W1 |
| `docs/refactoring/4.1-decomposition/as-is-to-be-map.md` | Module mapping table | W1 |
| `docs/refactoring/4.1-decomposition/ADR-001-architecture-style.md` | ADR template | W1 |
| `docs/refactoring/4.1-decomposition/ADR-002-target-stack.md` | ADR template | W1 |

## Stop conditions

- **Stop and ask the user** if the bounded-context boundaries materially
  diverge from the AS-IS module structure (>50 % overlap loss).
- **Stop and ask the user** if any ADR proposes a stack choice not pre-approved
  in the project's stack policy.
- Otherwise continue to W2.
````

---

## Extraction procedure (for the contributor doing the work)

1. Read the supervisor body. Identify section blocks ≥ 1 500 chars that match
   the per-phase / per-wave / per-template pattern.
2. For each block, create `claude-catalog/docs/<topic>/<phase|wave>-<name>.md`
   with the skeleton above. Copy the block content into "Goal", "Sub-agents to
   dispatch", and "Output".
3. In the supervisor body, replace the extracted block with one line:
   `→ Read \`claude-catalog/docs/<topic>/<phase|wave>-<name>.md\` when this
   wave starts.`
4. Add the doc to the supervisor's `## Reference docs` table (create the section
   if missing — it goes near the top of the body, right after `## When to
   invoke`).
5. Run `python3 .github/scripts/validate_catalog.py` — the body-length warning
   for that supervisor should drop. The doc files themselves are not under
   `claude-catalog/agents/` so they are not validated as agents.
6. Run the affected supervisor in a real workflow once to confirm the agent
   reads the doc on demand and produces the expected outputs.

---

## How to verify the extraction is correct

After extraction the supervisor body should:

- Stay under 10 000 chars (the rubric ceiling — validator warning gone).
- Contain a `## Reference docs` table that points at every extracted file.
- Still describe the **decision logic** (which wave runs when, escalation
  rules, stop conditions) — only the *templates* moved out.

The extracted docs should be:

- Independently readable (no dangling pronouns, no implicit references back to
  the supervisor body).
- Versioned in the same PR as the supervisor change.
- Referenced from `CHANGELOG.md` `[Unreleased]` so the trail is visible.
