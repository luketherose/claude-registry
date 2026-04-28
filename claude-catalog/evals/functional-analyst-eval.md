# Evals: functional-analyst

---

## Eval-001: Reconstruct requirements from a codebase

**Input context**: Small Python repo (~20 modules, no docs) implementing an order management system.

**User prompt**: "Reconstruct functional requirements from this codebase. Write to `docs/functional/`."

**Expected output characteristics**:
- `docs/functional/features.md` — every distinct feature, with entry point and user-facing outcome
- `docs/functional/user-flows.md` — step-by-step traces for each feature, source-file references included
- `docs/functional/business-rules.md` — extracted rules with conditions, effects, and source location
- `docs/functional/actors.md` — actors and system boundaries
- All artifacts are traceable: every claim links back to a file:line in source

**Must contain**:
- A `## Open questions` section flagging ambiguities (purpose unclear, magic numbers without comment)
- Domain terms preserved verbatim from code (no normalization: "Invoice" stays "Invoice")

**Must NOT contain**:
- Implementation suggestions (delegate to developer subagents)
- Architecture decisions (delegate to software-architect)
- Invented requirements not supported by source

---

## Eval-002: Acceptance criteria from a user story

**User prompt**: "Write acceptance criteria for: 'As a customer, I want to download my invoice as PDF.'"

**Expected behavior**:
- Asks one focused clarifying question if a precondition is genuinely unclear
- Produces criteria in Given-When-Then format
- Covers happy path, authorization edge cases, and failure modes
- Each criterion tagged with priority (must / should / could)
- Includes non-functional acceptance (latency budget, audit trail, file size limits) where relevant

**Must NOT contain**:
- Vague phrasing ("the system should work")
- Implementation details (specific HTTP libraries, framework choices)
- Missing the negative paths

---

## Eval-003: Gap analysis on existing requirements

**Input context**: Markdown requirements doc with 12 user stories. Existing codebase implements 9 of them.

**User prompt**: "Compare the requirements doc against the codebase. What's missing?"

**Expected behavior**:
- Identifies the 3 missing stories with file:line evidence (or absence thereof)
- Identifies code that exists but isn't covered by any story (orphan features)
- Identifies stories that are partially implemented
- Produces a traceability matrix: story → code locations OR "not implemented"
- Does NOT propose to write the missing code (out of scope for the analyst)

---

## Eval-004: CRUD matrix generation

**Input context**: Codebase with role-based access and 5 entities.

**User prompt**: "Generate a CRUD matrix for our entities and roles."

**Expected output**:
- Table: entity × role × operation
- Each cell: enforcement source (annotation, guard, controller check) OR "no rule found — gap"
- Inconsistencies flagged (e.g., role can read but not delete — intentional or oversight?)
- File:line references for every enforcement

---

## Eval-005: Refuses to make architecture decisions

**User prompt**: "Should we split this into microservices? Write the analysis."

**Expected behavior**:
- Recognizes this is an architecture question, not a functional analysis question
- Produces functional input for the decision (bounded contexts, data ownership, user flow boundaries)
- Explicitly delegates the decision to `software-architect`
- Does NOT produce an ADR or recommend a target architecture
