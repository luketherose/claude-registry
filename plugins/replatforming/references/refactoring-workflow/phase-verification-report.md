# Phase verification report — canonical spec

> Reference doc for `refactoring-supervisor` and every analysis-phase
> supervisor (Phases 1, 2, 3). Read at runtime when the phase's worker
> waves are complete and before the HITL gate.
>
> The verification report is the document the human reads to decide
> whether to `approve`, `iterate`, or `stop` at the end of an analysis
> phase. It is intentionally distinct from the deliverable PDF / PPTX:
> the deliverable targets external stakeholders, the verification
> report targets the human reviewer running the workflow.

## Purpose

Every analysis phase ends with a verification report that:

- is **human-readable** (no JSONL dumps, no traceability matrices as
  primary content);
- is **focused on what the user needs to verify** (gaps, low-confidence
  items, contested findings, AS-IS purity violations);
- supports the **iterate** option by being explicit about what was
  produced AND what was left unresolved;
- supports **convergence** across iterations by including a "what
  changed since the previous iteration" section when iteration > 1.

The verification report is NOT a duplicate of the deliverable PDF. The
PDF / PPTX is the comprehensive reference for stakeholders; the
verification report is the focused checklist for the human running the
workflow.

## File location and naming

The report lives at:

```
docs/analysis/<NN>-<phase>/_meta/phase-verification-report.md
```

Concretely:

- Phase 1 → `docs/analysis/01-functional/_meta/phase-verification-report.md`
- Phase 2 → `docs/analysis/02-technical/_meta/phase-verification-report.md`
- Phase 3 → `docs/analysis/03-baseline/_meta/phase-verification-report.md`

The report is overwritten at every iteration. Prior iterations are
snapshotted under `_meta/snapshots/iter-<N>-verification-report.md`
before overwrite (the snapshot policy lives in
`iteration-loop.md` § "Idempotency").

## Canonical structure

Every verification report has the same top-level structure:

```markdown
---
phase: <1 | 2 | 3>
phase_name: <Functional Analysis | Technical Analysis | Baseline Testing>
iteration: <N>
generated: <ISO-8601>
status: ready-for-review
prior_iteration: <N-1 or null>
---

# Phase <N> verification report — iteration <N>

## 1. Executive summary

<2–3 paragraphs, plain prose, no jargon. Cover:
 - What the phase produced this iteration
 - The headline counts (e.g. "12 features, 27 use cases, 3 open
   questions") — phase-specific, drawn from manifest
 - The overall confidence signal
 - The single most important thing the user should verify before
   approving>

## 2. What was produced (this iteration)

<Phase-specific section. For Phase 1: the feature-narrative chapters
+ the use-case catalogue + the UI map + the I/O catalogue + the
implicit-logic register. For Phase 2: the findings register +
risk register + cross-domain synthesis. For Phase 3: the regression
suite + oracle + benchmark + per-UC test outcomes.>

Each subsection states:
- the artifact path
- the number of items (with breakdown by status when relevant)
- the confidence distribution (high/medium/low)
- a 1–2 sentence narrative interpretation

## 3. What changed since iteration <N-1>

<Only if iteration > 1. Otherwise omit this section entirely.>

- Adjustments applied (from the iteration-log entry for this run)
- Files touched (with a brief delta — "added 4 UCs", "rewrote IL-03
  flow", "removed the 'admin' actor and merged into 'user' per user
  feedback")
- Sub-agents re-dispatched in this iteration
- Deliberation traces consulted (if any)

## 4. Open questions and gaps

Aggregated from `14-unresolved-questions.md` (or the phase's
equivalent). Grouped by severity:

- **Blocking** — the supervisor recommends NOT approving until these
  are resolved
- **Needs review** — the user should read before approving
- **Nice to have** — informational

For each open question: a one-line description, the source sub-agent,
the impact on downstream phases, and a suggested resolution path
(answer / scope-out / iterate / defer).

## 5. Audit verdicts

The verdict of every always-on auditor for this phase:

- Phase 1 → `functional-traceability-auditor`
- Phase 2 → `technical-evidence-auditor`
- Phase 3 → `baseline-challenger` (when ON) + per-test failure register

For each: PASS / PASS_WITH_GAPS / FAIL, plus a 1–2 sentence summary
of the gaps if not PASS. If the verdict is FAIL, the supervisor
MUST NOT propose `approve` — only `iterate` or `stop`.

## 6. AS-IS purity check

A flag (`PASS` / `FAIL`) plus the count of forbidden-token matches
(if any). The drift regex is phase-specific (defined in each
supervisor's `Drift check` section). On FAIL, list the offending
file/line pairs and the suspect tokens.

## 7. What the user should verify before approving

A checklist — 5 to 10 bullets — generated from sections 2–6. Each
bullet is an actionable verification, not a restatement. Examples:

- [ ] Read the 5 feature narrative chapters at
  `01-functional/01-feature-narrative.md` and confirm they describe
  what the app actually does, in your own understanding.
- [ ] Review the 3 use cases marked `requires_human_confirmation` and
  decide whether to confirm, drop, or rephrase them.
- [ ] Review the 2 blocking open questions — provide answers as part
  of the next iteration if `iterate` is selected.

The supervisor is encouraged to be opinionated here. Lower-confidence
items should be surfaced higher in the checklist.

## 8. Recommendation

The supervisor states its recommendation:

- `approve` — when all verdicts PASS, no blocking issues, ≤ 1 needs-
  review item per major output, AS-IS purity OK.
- `iterate` — when any verdict is not PASS, or ≥ 1 blocking issue,
  or the previous iteration left adjustments unresolved.
- `stop` — never recommended automatically; only echo the user's
  choice if they pick it.

Plus a 1-paragraph rationale.

## 9. How to respond

Verbatim block — the supervisor copies this into the HITL prompt:

```
What would you like to do?

  [approve]   Accept the analysis as-is and advance to the next phase
              (or end the workflow if this is the last analysis phase
              the user wants to run).
  [iterate]   Run another iteration with adjustments. You will be
              asked to describe the adjustments. You may include
              debate triggers (e.g. "use multi-agent debate") if you
              want a contested adjustment resolved through
              deliberation before re-dispatch.
  [stop]      End the workflow at this point. The current state is
              preserved as `partial`.
```
```

## What the verification report is NOT

- It is NOT the deliverable. The PDF / PPTX exports are the
  deliverable for stakeholders. The verification report stays inside
  `_meta/` and is not exported.
- It is NOT a re-summary of every artifact. Section 2 points to
  artifacts by path; it does not duplicate their content.
- It is NOT generated by a sub-agent. The supervisor produces it
  directly from the manifest + normalized JSONL + the audit verdict
  files. This guarantees the report is always consistent with what
  is on disk.
- It is NOT optional. Phases 1, 2, 3 cannot exit to the HITL gate
  without this file on disk.

## Per-phase customization

Each phase plan documents its own version of section 2 (what artifacts
to list) and section 4 (where to read open questions from). The
template above is the canonical skeleton; the phase plan fills in the
specifics.

| Phase | Section 2 source | Section 4 source | Section 5 verdicts |
|---|---|---|---|
| 1 | `01-feature-narrative.md`, `02-features.md`, `06-use-cases/`, `03-ui-map.md`, `09-inputs.md`, `10-outputs.md`, `12-implicit-logic.md` | `14-unresolved-questions.md`, `normalized/functional-gaps.jsonl` | `_meta/functional-traceability-report.md`, `_meta/challenger-report.md` (if ran) |
| 2 | `findings/`, `risk-register.md`, `synthesis/cross-domain-risk-matrix.md`, per-domain summaries | `14-unresolved-questions.md`, `normalized/technical-gaps.jsonl` | `_meta/technical-evidence-report.md`, `_meta/challenger-report.md` (if ran) |
| 3 | `tests/baseline/`, `oracle/snapshot/`, benchmark JSON, `as-is-bugs-found.md` | open-questions register, `baseline-report.md` outstanding issues | `_meta/baseline-challenger-report.md` (if ran) + critical/high failure register |

## Iteration on the verification report itself

The verification report is regenerated at the end of every iteration.
The supervisor MUST NOT incrementally edit the previous report — it
generates the next version from scratch from the manifest + audit
files + iteration log. The "what changed" section is the only place
the prior iteration is referenced.

This rule ensures the report cannot drift out of sync with the
underlying analysis state.
