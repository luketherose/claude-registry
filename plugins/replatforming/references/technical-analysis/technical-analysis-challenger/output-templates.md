# Technical-analysis-challenger — output templates

> Reference doc for `technical-analysis-challenger`. Read at runtime when about
> to write the challenger report and append findings to the unresolved-questions
> register.

The agent produces two artifacts:

1. `docs/analysis/02-technical/_meta/challenger-report.md` (overwrite)
2. A `## Challenger findings` section appended to
   `docs/analysis/02-technical/14-unresolved-questions.md`

Both share the same finding shape:

- **Type**: gap | contradiction | unverified | as-is-violation |
  streamlit-risk | duplicate | severity-mismatch
- **Where**: which file(s) the issue lives in
- **Description**: one paragraph
- **Suggested fix**: short, actionable
- **Severity of the meta-finding**: blocking | needs-review | nice-to-have

Stable IDs: `CHL-NN`. Severity is the meta-finding's severity, not the
underlying finding's severity.

---

## File 1 — `_meta/challenger-report.md`

```markdown
---
agent: technical-analysis-challenger
generated: <ISO-8601>
sources:
  - docs/analysis/02-technical/01-code-quality/...
  - ... (every file actually read)
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
---

# Challenger report — Phase 2 Technical Analysis

## Summary
- Blocking issues:    <N>
- Needs-review:       <N>
- Nice-to-have:       <N>

## Findings by check

### 1. Orphan IDs and broken cross-references

#### CHL-01 — <title>
- **Type**: orphan-id
- **Where**: `09-synthesis/risk-register.md`
- **Description**: References RISK-DA-04 but `04-data-access/` only
  has up to RISK-DA-03.
- **Suggested fix**: clarify ID or add the missing finding
- **Severity**: needs-review

### 2. Contradictions

#### CHL-NN — <title>
- **Type**: contradiction
- **Where**: `04-data-access/access-pattern-map.md` vs
  `08-security/security-findings.md`
- **Description**: data-access reports "all queries parameterized";
  security reports SEC-02 SQL injection at <repo-path>:<line>.
- **Suggested fix**: resolve which is accurate; update both.
- **Severity**: blocking (cannot leave Phase 2 with this unresolved)

### 3. Unverified claims

#### CHL-NN — <title>
- **Type**: unverified
- **Where**: `08-security/security-findings.md`
- **Description**: SEC-04 (critical) cites only KB sources, no
  source-line. Critical findings require code-level evidence.
- **Suggested fix**: add `<repo-path>:<line>` to sources, or
  downgrade to "suspected" with explicit caveat.
- **Severity**: needs-review

### 4. Coverage gaps

#### CHL-NN — <title>
- **Type**: gap
- **Where**: workflow-level
- **Description**: package `<name>` from Phase 0 KB has no entry in
  any Wave 1 output.
- **Suggested fix**: add a "no findings — clean" note in code-quality
  or trigger re-analysis on the missing module.
- **Severity**: nice-to-have / needs-review (depends on package size)

### 5. AS-IS violations

#### CHL-NN — <title>
- **Type**: as-is-violation
- **Where**: `06-performance/performance-bottleneck-report.md`
- **Description**: Remediation hint says "consider migrating to
  FastAPI for async I/O".
- **Suggested fix**: rewrite hint within AS-IS scope (e.g., "use
  asyncio + httpx within the existing app").
- **Severity**: blocking (AS-IS rule is non-negotiable)

### 6. Streamlit-specific risks (if applicable)

#### CHL-NN — <title>
- **Type**: streamlit-risk
- **Where**: `02-state-runtime/session-state-inventory.md`
- **Description**: cross-page key `current_user` documented as
  consumer on page B but no producer found on page A; could be
  legacy or a real bug.
- **Suggested fix**: confirm and either add to RISK-RES or remove
  inventory entry.
- **Severity**: needs-review

## Verdict

\`\`\`
Blocking issues:  <N>
Phase 2 ready:    <yes | no — see blocking issues above>
\`\`\`

If `Phase 2 ready: no`: the supervisor should not declare Phase 2
complete and must escalate.
```

---

## File 2 — appended section in `14-unresolved-questions.md`

You **append** (not overwrite) a section:

```markdown
## Challenger findings

(Same content as challenger-report.md, but in a flat bulleted list
for easier reviewer scanning. Cross-link by CHL-NN.)

- **CHL-01** [needs-review] orphan-id reference in risk register
- **CHL-02** [blocking] contradiction between data-access and security
  on SQL injection
- ...
```

If `14-unresolved-questions.md` does not yet have a `## Challenger
findings` heading, add it. If it does (from a previous run), replace
its content with the latest run's findings.

---

## Streamlit-specific risk checklist (Check 6 detail)

Even seasoned analysts miss Streamlit-specific traps. Verify each is
addressed somewhere in the analysis:

- **Reactive cost**: every page that performs DB / HTTP work without
  `st.cache_*` decorator at the top? Should be flagged in
  `performance-analyst`.
- **session_state isolation**: is per-user isolation explicitly
  documented? Streamlit DOES isolate session_state per browser
  session, but this is often misunderstood and worth confirming.
- **Multipage state leaks**: keys read on page B but written on
  page A — do they have proper init? Should be in `state-runtime`.
- **`st.cache_resource` mutation**: cached resources (DB connections,
  models) returned and mutated by callers? Subtle bug.
- **No native auth**: Streamlit has no built-in login. Is there a
  documented enforcement layer (proxy, gate component) and is it
  explicit? `security-analyst` should have noted this.
- **File upload sanitization**: `st.file_uploader` returns a
  `BytesIO`. Is filename sanitized before reuse? Is content type
  validated?
- **`st.query_params` / `experimental_get_query_params`**: are these
  user-controlled and sanitized?

If stack mode is generic (non-Streamlit), this check is skipped.
