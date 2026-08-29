# Phase 2 — Phase plan (Phase 0 bootstrap + Wave 1–3 + Wave 3c verification + Export Wave + iteration handling)

> Reference doc for `technical-analysis-supervisor`. Read at runtime to drive the bootstrap dialog, dispatch each wave, write the phase verification report, and (on `approve`) regenerate the exports.
>
> **Iteration loop.** Phase 2 ends with the HITL iteration loop documented in [`../refactoring-workflow/iteration-loop.md`](../refactoring-workflow/iteration-loop.md). After Wave 3c the supervisor returns control to `refactoring-supervisor`, which presents `approve / iterate / stop`. On `iterate`, this supervisor is re-dispatched with `Resume mode: iterate` and a structured delta — see § "Wave 4 — Iteration handling" below.

## Phase 0 — Bootstrap (supervisor only, no sub-agents)

1. Verify `.indexing-kb/` exists and contains at minimum:
   - `00-index.md` or `01-overview.md`
   - `02-structure/`
   - `03-dependencies/`
   - `04-modules/`
   - `06-data-flow/`
   - `07-business-logic/`
   If any of these is missing, stop and ask the user.
2. Read `.indexing-kb/00-index.md`, `01-overview.md`, `02-structure/language-stats.md`, `_meta/manifest.json`.
3. **Detect stack mode**:
   - `.indexing-kb/05-streamlit/` non-empty → **Streamlit mode ON**.
   - Otherwise → generic mode.
4. Check Phase 1 availability:
   - If `docs/analysis/01-functional/_meta/manifest.json` exists with `status: complete` → mark `phase1_available: true`.
   - Else → flag in recap; risk traceability to features will be partial.
5. Read `docs/analysis/02-technical/_meta/manifest.json` if it exists (resume support).
6. **Detect resume mode**. Inspect what is on disk and pick one of:

   | Condition | Resume mode |
   |---|---|
   | No `docs/analysis/02-technical/` | `fresh` |
   | Manifest reports `partial` / `failed` / missing while output dir exists | `resume-incomplete` |
   | Manifest reports `complete` AND **both** `_exports/02-technical-report.pdf` AND `_exports/02-technical-deck.pptx` exist | `complete` (default = nothing to do; ask user whether to refresh) |
   | Manifest reports `complete` AND **at least one of** the export files is missing | `exports-only-eligible` — offer the user the option to dispatch ONLY the export wave |
   | Manifest reports `complete` AND user explicitly asked for a refresh | `full-rerun` |

   When `exports-only-eligible` triggers, ask the user verbatim:

   ```
   The technical analysis at docs/analysis/02-technical/ is complete,
   but the following Accenture-branded export(s) are missing:
     - <list missing files>

   What should I do?
     [exports-only]  regenerate only the missing export(s), reusing the
                     existing analysis and risk register. Fast — does
                     not re-run any of the W1/W2/W3 workers.
     [full-rerun]    re-run the full pipeline from W1 (overwrites the
                     existing analysis; you'll get an explicit
                     overwrite confirmation).
     [skip]          do nothing, leave the analysis as-is without the
                     missing export(s).
   ```

   Default recommendation: `exports-only`. Do not proceed without an explicit answer.
7. Check exports (only if resume mode is NOT `exports-only`):
   - If `_exports/02-technical-report.pdf` or `_exports/02-technical-deck.pptx` already exist → **ask the user explicitly** whether to overwrite. Do not silently overwrite. Choices: `overwrite`, `keep` (skip export), `rename` (append timestamp suffix).
   In `exports-only` mode this step is skipped — the export wave will regenerate only the missing file(s); existing files are kept untouched.
8. Compute **dispatch mode** per the decision tree (skipped in `exports-only` mode — no W1 workers will run).
9. Write `00-context.md` with:
   - 1-paragraph system summary derived from `01-overview.md`
   - Scope: what is in / out of analysis
   - Stack mode (Streamlit / generic)
   - Phase 1 availability
   - Resume mode
   - Dispatch mode + rationale (or "n/a — exports-only")
   - Export overwrite decision
   In `exports-only` mode, do NOT overwrite an existing `00-context.md` from the prior run — append a `## Re-run note` block at the bottom that records the date and which files were regenerated.
10. **Present the plan to the user** (use the Wave 1 dispatch plan template, or — in `exports-only` mode — a short brief listing only the export(s) to regenerate). Wait for confirmation.

Skip Phase 0 confirmation only if the user has explicitly said "go ahead, do the whole pipeline" in the same conversation — and even then, post the plan and wait at least one turn before dispatch unless the user repeats "proceed".

> **Resume-mode shortcut**: if bootstrap chose `exports-only`, skip Waves 1, 1.5, 2, and 3 entirely. Jump directly to the Export Wave below — that is the whole point of `exports-only`. The existing analysis in `docs/analysis/02-technical/` is treated as the source of truth and is not modified.

## Wave 1 — Discovery (mode-dependent dispatch of 8 workers)

Per chosen mode:

- **parallel**: single message with 8 Agent calls in parallel
- **batched**: three messages, batch 1 → batch 2 → batch 3, each batch is a single message with parallel calls inside
- **sequential**: 8 messages, one per worker, in domain order (code-quality → state-runtime → dependency-security → data-access → integration → performance → resilience → security)

After each batch (or each worker in sequential mode), read outputs from disk. Verify:
- expected files exist and have valid frontmatter
- no sub-agent wrote outside `docs/analysis/02-technical/`
- no sub-agent referenced target technologies (see drift check in supervisor body)

If any worker reports `status: blocked` or `confidence: low` on a foundational area (code-quality, dependency-security): surface to the user **before Wave 2**. Wave 2 depends on these.

## Wave 1.5 — Human-in-the-loop checkpoint

Present to the user after all Wave 1 workers complete:
- counts: total findings, by severity (critical/high/medium/low)
- top-3 risks per worker (one-line summaries)
- any blocking unresolved items

Ask: "Proceed to Wave 2 (synthesis), revise specific Wave 1 outputs, or stop?"

This checkpoint is non-negotiable when Wave 1 produced ≥ 1 critical finding without remediation context, or ≥ 5 `low` confidence sections. Otherwise it is recommended but skippable if the user has set `--no-checkpoint`.

## Wave 2 — Synthesis (sequential, single Agent call)

Dispatch `risk-synthesizer`. It reads all W1 outputs (and Phase 1 if available) and produces:
- `09-synthesis/risk-register.md` — markdown table sorted by severity
- `09-synthesis/severity-matrix.md` — likelihood × impact heatmap
- `09-synthesis/remediation-priority.md` — ordered backlog (AS-IS scope only)
- `_meta/risk-register.json` — machine-readable
- `_meta/risk-register.csv` — Excel/Jira import-friendly

After dispatch, read outputs. Aggregate `## Open questions` sections from all W1 + W2 sub-agents into `14-unresolved-questions.md`.

## Wave 3 — Challenger (always ON)

Dispatch `technical-analysis-challenger`. It performs adversarial review of all W1 + W2 outputs and produces:
- `_meta/challenger-report.md`
- appends entries to `14-unresolved-questions.md` under `## Challenger findings`

If the challenger reports ≥ 1 blocking contradiction or AS-IS violation: **stop, do not declare Phase 2 complete; escalate**.

## Wave 3b — technical-evidence-auditor (always ON)

Dispatch after Wave 3 (challenger) completes. If the challenger is disabled, dispatch after Wave 2.

The auditor validates:
- every finding has `evidence_ids`
- high/critical findings have `validation.status` of `verified` or `requires_validation`
- no AS-IS purity violations
- no unrequested TO-BE architectural recommendations

Read outputs from disk: `normalized/technical-evidence-audit.json` and `_meta/technical-evidence-report.md`.

If verdict is FAIL, do NOT declare Phase 2 complete — escalate to user with the audit details.

## Gap closure loop (before HITL)

Run before the HITL checkpoint and before the Export Wave:

1. Check if `validate_technical_analysis.py` exists in `.github/scripts/`; if so, run it.
2. Read `normalized/technical-evidence-audit.json` for verdict.
3. If FAIL: identify auto-resolvable gaps (e.g., findings without severity can be set to `requires_validation`); attempt targeted re-dispatch.
4. Surface all residual gaps in the HITL summary.

## Export Wave — Always ON (parallel, single message)

Dispatch in parallel:
- `document-creator` → `_exports/02-technical-report.pdf`
- `presentation-creator` → `_exports/02-technical-deck.pptx`

Both agents are passed paths to the entire `docs/analysis/02-technical/` tree as source. Audience: `document-creator` produces a technical PDF for senior architects; `presentation-creator` produces an executive deck for steering committee (top-10 risks, dependency health, performance hotspots, security findings).

In `exports-only` resume mode, dispatch ONLY the generators whose output file is missing on disk. Existing export files are kept untouched. If both files exist, the supervisor should not have reached this wave in `exports-only` mode (bootstrap step 6 would have classified the run as `complete`, not `exports-only-eligible`).

If the export overwrite decision in bootstrap was `keep` → skip this wave and note in the final recap.

If either generator fails: do not block Phase 2 completion; mark the export as failed in the manifest and surface in the recap. The markdown KB is the primary deliverable.

## Wave 3c — Phase verification report (supervisor only)

After the Gap closure loop and BEFORE the Export Wave, the supervisor
writes the verification report at `_meta/phase-verification-report.md`
per the canonical structure in
[`../refactoring-workflow/phase-verification-report.md`](../refactoring-workflow/phase-verification-report.md).

Phase-2 customization of the canonical structure:

| Section | Phase 2 source |
|---|---|
| 1. Executive summary | Manifest counts + risk-register top items + auditor verdicts. 2–3 paragraphs. |
| 2. What was produced | Per-domain findings (`05-security/`, `06-performance/`, `07-observability/`, `08-data-access/`, `09-state-runtime/`, `10-integrations/`, `11-dependencies/`, `12-code-quality/`), `09-synthesis/risk-register.md`, cross-domain matrix. |
| 3. What changed since iteration N-1 | Read `_meta/iteration-log.jsonl` latest entry. Omit on iteration 1. |
| 4. Open questions and gaps | `14-unresolved-questions.md` + `normalized/technical-gaps.jsonl`. Group by severity. |
| 5. Audit verdicts | `_meta/technical-evidence-report.md` (always) + `_meta/challenger-report.md` (if ran). |
| 6. AS-IS purity check | Drift scan per § "Drift check" in the supervisor body. |
| 7. What to verify | At minimum: review the top 10 risks in `09-synthesis/risk-register.md`; review findings marked `requires_validation`; review blocking open questions. |
| 8. Recommendation | `approve` only if all verdicts PASS and no blocking issues; `iterate` otherwise. |

The verification report is mandatory. The Export Wave runs only after
this file is on disk.

## Export Wave — gated on `approve`

The Export Wave (PDF + PPTX via `document-creator` +
`presentation-creator`) no longer runs unconditionally at the end of
every iteration. It runs:

- on `approve` from the iteration loop (per-phase protocol Step F
  branch `approve`), to produce the deliverable for stakeholders
  reflecting the approved state, OR
- on `Resume mode: exports-only` when an existing approved analysis
  has missing exports (no change to existing behaviour).

During iterations 1..N-1 (before approval) the exports are not
regenerated.

Dispatch in parallel:
- `document-creator` → `_exports/02-technical-report.pdf`
- `presentation-creator` → `_exports/02-technical-deck.pptx`

Both agents are passed paths to the entire `docs/analysis/02-technical/`
tree as source. Audience: `document-creator` produces a technical PDF
for senior architects; `presentation-creator` produces an executive
deck for steering committee (top-10 risks, dependency health,
performance hotspots, security findings).

In `exports-only` resume mode, dispatch ONLY the generators whose
output file is missing on disk. Existing export files are kept
untouched.

If either generator fails: do not block Phase 2 completion; mark the
export as failed in the manifest and surface in the verification
report. The markdown KB is the primary deliverable.

## Wave 4 — Iteration handling (supervisor only)

After Wave 3c (verification report) the supervisor returns control to
`refactoring-supervisor` for the HITL prompt. On user choice:

- **`approve`** → run the Export Wave; manifest entry's
  `approved_at: <ISO-8601>`; workflow advances.
- **`iterate`** → re-dispatched with `Resume mode: iterate` and a
  delta path. The supervisor:
  1. Reads the delta from `_meta/iteration-log.jsonl` (latest).
  2. Snapshots prior outputs to `_meta/snapshots/iter-<K>/`.
  3. Re-dispatches sub-agents per this mapping:

     | Adjustment target | Sub-agents to re-dispatch |
     |---|---|
     | security findings (T-NN sec) | security-analyst → risk-synthesizer |
     | performance hotspots | performance-analyst → risk-synthesizer |
     | resilience / state-runtime | resilience-analyst / state-runtime-analyst → risk-synthesizer |
     | data-access / persistence | data-access-analyst → risk-synthesizer |
     | integrations | integration-analyst → risk-synthesizer |
     | dependencies / CVEs | dependency-security-analyst → risk-synthesizer |
     | code quality | code-quality-analyst → risk-synthesizer |
     | risk severity dispute | route to deliberative-decision-engine first; re-decide; then re-run risk-synthesizer with the resolved severity |
     | cross-domain synthesis only | risk-synthesizer (re-run) |

  4. Always re-runs Wave 2 (risk-synthesizer), Wave 3b (auditor), and
     Wave 3c (verification report). Wave 3 (challenger) re-runs if
     requested or if > 30% of artifacts changed.
- **`stop`** → manifest `status: partial`; end.

### Manifest update for iterations

Every iteration appends to `manifest.json` `runs[]`:

```json
{
  "run_id": "<ISO-8601>",
  "iteration": <K>,
  "trigger": "fresh | iterate | exports-only | full-rerun",
  "delta_ref": "_meta/iteration-log.jsonl#<line>",
  "waves": [ ... ],
  "deliberation_traces": ["<trace-id>", ...],
  "status": "complete | partial | failed",
  "approved_at": null | "<ISO-8601>"
}
```

`approved_at` is set only on `approve` — it is the lock signal that
the phase is no longer iteratable.

## Closing summary (compatibility shim)

The "Phase 2 Technical Analysis — complete" free-text block is now
produced as part of the verification report's section 1 ("Executive
summary"). The old free-text closing block is no longer emitted —
the verification report supersedes it.
