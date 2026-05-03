# Output templates — severity matrix and remediation priority

> Reference doc for `risk-synthesizer`. Read at runtime when writing the
> severity matrix and the ordered remediation backlog. Defines the markdown
> shape of the two narrative artifacts that sit alongside the risk register.

## Goal

Provide the canonical markdown templates for:

- `09-synthesis/severity-matrix.md` — likelihood × impact heatmap
- `09-synthesis/remediation-priority.md` — tiered AS-IS backlog

The risk-register itself (MD/JSON/CSV) lives in `risk-register-schemas.md`.

---

## Severity matrix — `09-synthesis/severity-matrix.md`

```markdown
---
agent: risk-synthesizer
generated: <ISO-8601>
sources: [...]
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
---

# Severity matrix

## Method
Each finding is placed on a likelihood × impact grid using the
inference rules described below. The rules are heuristic — they are
not a substitute for stakeholder review.

## Inference rules
1. <list the rules you applied>
2. ...

## Heatmap

|             | Negligible | Minor | Moderate | Major | Catastrophic |
|-------------|------------|-------|----------|-------|--------------|
| Certain     |            |       |          | SEC-01 |              |
| Likely      |            |       | PERF-02  | RISK-RES-01 | SEC-02       |
| Possible    |            | DEP-01 | RISK-CQ-01 | VULN-03 |              |
| Unlikely    |            |       |          |       |              |
| Rare        |            |       |          |       |              |

## Top quadrant (Likely+Major or worse)

<list of IDs requiring immediate review>

## Open questions
- <items where the matrix placement is debatable>
```

### Likelihood × impact — inference rules to apply (in order)

Likelihood:

- security finding with secret in code → `certain`
- N+1 in code path tied to user-facing feature → `likely`
- vulnerability in pinned old library → `possible` (depends on exposure)
- isolated duplication in dead code → `rare`

Impact:

- code execution / SQL injection → `catastrophic`
- data leak → `major`
- silent failure in user path → `major`
- performance degradation → `moderate`
- maintainability → `minor` / `negligible`

Document the rules actually applied at the top of the matrix file.

---

## Remediation priority — `09-synthesis/remediation-priority.md`

```markdown
---
agent: risk-synthesizer
generated: <ISO-8601>
sources: [...]
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
---

# Remediation priority (AS-IS)

## Method
Ordered by: severity, likelihood, effort, cross-feature impact.
Remediation hints are AS-IS only — they propose changes within the
current stack, not migration to a different one. Migration planning
lives in Phase 4 of the workflow.

## Tier 1 — Fix immediately (critical)

1. **SEC-01** [security] Hard-coded API key
   - Effort: small
   - Hint: rotate key, move to env var, redact from git history
2. **SEC-02** [security] SQL injection in reports
   - Effort: medium
   - Hint: parameterize via SQLAlchemy `text()` with bindparams
3. ...

## Tier 2 — Address in next iteration (high)

<numbered list>

## Tier 3 — Plan in roadmap (medium)

<numbered list>

## Tier 4 — Track (low / info)

<numbered list>

## Notes
- Dependencies between fixes (if any): "fixing SEC-02 requires the
  query-builder helper to be in place — track as prerequisite"
- Items where AS-IS remediation may be limited (e.g., upstream
  library has no fix): explicitly noted

## Open questions
- <items requiring stakeholder input on priority>
```

### Ordering keys (apply in this order)

1. severity (critical > high > medium > low)
2. likelihood (certain > likely > possible > unlikely > rare)
3. estimated effort (small / medium / large — your inference)
4. cross-feature impact (more features touched → higher priority)

Group output as the four tiers above (`Fix immediately`, `Address in next
iteration`, `Plan in roadmap`, `Track`).
