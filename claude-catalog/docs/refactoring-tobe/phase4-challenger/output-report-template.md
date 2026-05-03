# Phase 4 challenger — output report templates

> Reference doc for `phase4-challenger`. Read at runtime when emitting
> the three deliverables: the challenger report, the traceability matrix,
> and the appended section in `unresolved-tobe.md`.

## Goal

Verbatim shapes for the challenger's three output files plus example
findings (one per check) the agent uses as templates when populating the
report.

---

## File 1 — `docs/refactoring/_meta/challenger-report.md`

```markdown
---
agent: phase4-challenger
generated: <ISO-8601>
sources: [...]
related_ucs: [<all UCs analyzed>]
related_bcs: [<all BCs analyzed>]
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
duration_seconds: <int>
---

# Challenger report — Phase 4 TO-BE Refactoring

## Summary
- Blocking issues:    <N>
- Needs-review:       <N>
- Nice-to-have:       <N>

## Traceability matrix summary
- Total UCs:          <N>
- Fully covered:      <N>
- Partial:            <N>
- Uncovered:          <N>  (must be 0 for status: complete)

## Findings by check

### 1. Traceability gaps

#### CHL-01 — UC-04 has no TO-BE counterpart
- **Type**: orphan / uncovered
- **Description**: UC-04 (List users) is in Phase 1 with severity
  `medium`, but no operation in openapi.yaml has `x-uc-ref: UC-04`
  and no Java controller method exists.
- **Suggested fix**: add the endpoint to openapi.yaml; re-dispatch
  api-contract-designer; backend-scaffolder will produce the
  controller.
- **Severity**: blocking

### 2. OpenAPI↔code drift

#### CHL-NN — DTO field `tenantId` in openapi.yaml not in Java
- **Type**: drift
- ...

### 3. ADR completeness

(For each missing or incomplete ADR.)

### 4. AS-IS bug carry-over

#### CHL-NN — BUG-04 (critical) deferred but not in roadmap
- **Type**: bug-carry-over
- **Description**: Phase 3 _meta/as-is-bugs-found.md lists BUG-04
  (silent payment failure) as "deferred to Phase 5". The roadmap
  does not include it in the M-02 (Payments) carry-over table.
- **Suggested fix**: re-dispatch migration-roadmap-builder with the
  bug list; it should appear in M-02 with disposition.
- **Severity**: blocking

### 5. Performance hypothesis

(Per Phase 2 hotspots not addressed in TO-BE.)

### 6. Security regression

(Per Phase 2 OWASP gaps not addressed.)

### 7. Equivalence claims

(Per roadmap claims without baseline backing.)

### 8. AS-IS-only leak

#### CHL-NN — `st.session_state` referenced in Angular component without ADR ref
- **Type**: as-is-leak
- **Where**: `<frontend-dir>/src/app/features/identity/pages/login/login.component.ts:34`
- **Description**: Comment says "AS-IS uses st.session_state for
  remember-me" but no ADR resolution; should reference ADR-003 (auth)
  or ADR-005 (session strategy).
- **Suggested fix**: add ADR ref to the comment; or move the note to
  the design rationale.
- **Severity**: needs-review

### 9. AS-IS source modification

(git status verification.)

## Verdict

\`\`\`
Blocking issues:   <N>
Phase 4 ready:     <yes | no — see blocking issues above>
Phase 5 enabled:   <yes | no>
\`\`\`

If `Phase 4 ready: no`: the supervisor must NOT declare Phase 4
complete and must escalate.
```

---

## File 2 — `.refactoring-kb/02-traceability/as-is-to-be-matrix.json`

Per the schema in `checklist-templates.md` (Check 1).

---

## File 3 — appended section in `.refactoring-kb/_meta/unresolved-tobe.md`

```markdown
## Challenger findings

(Bulleted summary; cross-link by CHL-NN.)

- **CHL-01** [blocking] uncovered UC-04
- **CHL-02** [blocking] BUG-04 not in roadmap
- ...
```

If `unresolved-tobe.md` doesn't yet have `## Challenger findings`,
add it. If it does (from prior run), replace its content.
