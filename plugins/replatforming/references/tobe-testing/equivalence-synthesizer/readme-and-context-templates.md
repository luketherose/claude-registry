# Phase 5 `README.md` and `00-context.md` — templates

> Reference doc for `equivalence-synthesizer`. Read at runtime when writing the
> Phase 5 entry-point README and supplementing the bootstrap context file.

## Goal

Define the structure of `README.md` (Phase 5 navigation entry point) and the
rules for supplementing `00-context.md` without overwriting the supervisor's
bootstrap content.

## `README.md` structure

```markdown
---
<frontmatter>
---

# Phase 5 — TO-BE testing & equivalence verification

## Reading order

1. **`01-equivalence-report.md`** — start here. PO sign-off required.
2. `00-context.md` — system summary, scope, run mode.
3. `02-coverage-report.md` — backend / frontend / equivalence coverage.
4. `03-contract-tests-report.md` — OpenAPI verification.
5. `04-performance-comparison.md` — p95/p99 deltas vs AS-IS.
6. `05-security-findings.md` — OWASP coverage and Phase 2 regressions.
7. `06-tobe-bug-registry.md` — medium/low non-blocking findings.
8. `14-unresolved-questions.md` — items needing human decision.
9. `_meta/challenger-report.md` — adversarial review.

## Quick links

| What I want | Go to |
|---|---|
| Approve go-live | `01-equivalence-report.md` § Sign-off |
| See per-UC verdict | `01-equivalence-report.md` § Verdict per UC |
| Review accepted differences | `01-equivalence-report.md` § Accepted differences |
| Triage blocking regressions | `01-equivalence-report.md` § Blocking regressions |
| Check coverage thresholds | `02-coverage-report.md` |
| Check OpenAPI compliance | `03-contract-tests-report.md` |
| Check perf gate (+10%) | `04-performance-comparison.md` |
| Check security gate | `05-security-findings.md` |

## Run summary

(populated from `_meta/manifest.json`)
- Started: <ISO>
- Completed: <ISO>
- Duration: <human-readable>
- Execute policy: <on | backend-only | frontend-only | off>
- Resume mode: <fresh | re-run | revise>
```

## `00-context.md` supplementation

If `00-context.md` already exists (written by the supervisor in
bootstrap), add a `## Synthesis run note` section at the bottom with
the synthesis-specific metadata: counts, verdict breakdown, timestamps.
Do NOT overwrite the supervisor's content.

If `00-context.md` doesn't exist (shouldn't happen), create it with
the supervisor's expected fields plus your synthesis note.
