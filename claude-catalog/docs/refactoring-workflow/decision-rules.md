# Decision rules — `refactoring-supervisor`

> Reference doc for `refactoring-supervisor`. Read at runtime on every
> supervision step that involves a state transition or a HITL prompt.
> This is the authoritative table — the agent body keeps only a pointer
> to this file to stay under the rubric body-length ceiling.

The table is grouped by phase and by situation. The supervisor MUST
consult it whenever a decision is needed; never decide silently
outside the table.

## Bootstrap and pre-phase gates

| Situation | Decision |
|---|---|
| Bootstrap not confirmed | Do not dispatch any phase |
| Phase N inputs missing | Do not dispatch; ask user how to proceed |
| Phase 0 complete — pre-advancement gate | Read `gold/indexing-audit.json` verdict; if FAIL, escalate to user — do not advance to Phase 1 silently |
| Phase 1 complete — pre-advancement gate | Read `normalized/functional-traceability-audit.json` verdict; if FAIL, escalate to user — do not advance to Phase 2 silently |
| Phase 2 complete — pre-advancement gate | Read `normalized/technical-evidence-audit.json` verdict; if FAIL, escalate to user — do not advance to Phase 3 silently |
| Any pre-advancement auditor verdict is FAIL | Show user the blocking gaps from the verdict file; offer `re-run phase` or `override with explicit acknowledgment`; never silently advance |
| Phase supervisor not installed | Stop, ask user to install via setup script |

## Phase status and the iteration loop (Phases 1–3)

| Situation | Decision |
|---|---|
| Phase reports `complete` (Phases 1–3) | Move to Step E recap → Step E.5 verification report → Step F iteration loop; ask user `approve / iterate / stop` |
| Phase reports `complete` (Phase 0) | Move to post-phase recap; ask user to confirm next (no iteration loop for Phase 0) |
| Phase reports `partial` (Phases 1–3) | Show partial details in recap + verification report; default to recommending `iterate`; never propose `approve` while partial |
| Phase reports `partial` (Phase 0) | Show partial details; ask user explicitly whether partial is acceptable |
| Phase reports `failed` | Do not propose `approve`; only `iterate` or `stop` (Phases 1–3) / `revise` or `stop` (Phase 0) |
| Phase has > 5 unresolved blocking questions | Do not propose `approve`; recommend `iterate` (Phases 1–3) / `revise` (Phase 0) |
| User picks `iterate` (Phases 1–3) | Capture adjustments per `iteration-loop.md` § "Iteration delta"; route contested items through deliberation if a debate trigger is detected or the adjustment is subjective; snapshot prior outputs; re-dispatch the phase supervisor with `Resume mode: iterate`; bump iteration counter |
| User picks `approve` (Phases 1–3) | Regenerate PDF/PPTX exports if they reflect a prior iteration's state; then post next-phase schematic and ask `yes / stop` |
| User picks `stop` (any phase) | Update manifest with `status: partial` and `stopped_at`; write final status note; end workflow |
| Pre-advancement auditor verdict FAIL (Phases 1–3) | Surface gaps; do NOT propose `approve` — offer only `iterate` or `stop` |
| User attempts `approve` with blocking items unresolved | Re-ask once: require `approve --override` to confirm, else default to `iterate` |
| Iteration count > 5 on the same phase | Suggest (don't force) a deliberation-based reset on the contested scope; the user remains in control |

## Skip / resume / re-run at bootstrap

| Situation | Decision |
|---|---|
| User asks to skip a phase | Allowed only if the next phase's inputs already exist; otherwise refuse |
| User asks for Phase N+1 with no implementation | Refuse; reiterate which phases are supported |
| Existing complete output detected at bootstrap | Show in detection table; **ask user explicitly per phase**: skip / re-run / revise. Do not auto-skip silently. |
| Existing output detected but manifest is partial / failed / missing | Classify as `inconsistent`; recommend `re-run`; never auto-resume from broken state |
| Phase 1 or 2 complete but ≥ 1 export file missing | Classify as `complete-but-exports-missing`; recommend `regenerate-exports`; offer it as a fourth choice in the per-phase prompt |
| User answers `skip` for a phase at bootstrap | Treat the phase as `complete` for downstream dependencies; do not dispatch its supervisor |
| User answers `regenerate-exports` for Phase 1 or 2 | Dispatch the phase supervisor with `Resume mode: exports-only` — it will skip W1/W2/W3 and run only the export wave for the missing file(s) |
| User answers `re-run` for a phase at bootstrap | Dispatch normally; the phase supervisor handles its own overwrite confirmation |
| User selects `regenerate-exports` for Phase 0, 3, or 4 | Refuse: this option is only available for Phase 1 (functional analysis) and Phase 2 (technical analysis), the only phases that produce PDF/PPTX exports |
| Conflict between manifest and disk state | Trust disk; flag inconsistency in recap |

## Phase 4 gating

| Situation | Decision |
|---|---|
| Phase 4 Step 0 build fails | Do NOT advance to Step 1; trigger Step 3 sub-loop on the build failure; iterate until build green; never skip a failing build |
| Phase 4 Step 0 application fails to start | Do NOT advance to Step 1; trigger Step 3 sub-loop with debugger on startup logs; iterate until app starts; never skip a failing startup |
| Phase 4 Step 1 fails after Step 0 succeeded | Treat as a regression; trigger Step 3 sub-loop and converge before re-attempting Step 1 |
| Phase 4 Step 2 — feature gate fails (build / tests / startup / behavior) | Do NOT advance to next feature; trigger Step 3 sub-loop; resume the failing sub-step (2.4 / 2.5 / 2.6 / 2.7) until green |
| Phase 4 Step 3 sub-loop fails to converge after 3 attempts | Stop; surface partial fix + trigger context to user; ask for guidance; do NOT silently abandon |
| Phase 4 Step 4 — invariant broken (build red / app not running / tests red between features) | Halt forward progress; trigger Step 3 sub-loop on whatever broke the invariant |
| Phase 4 Step 5 — hardening change introduces a regression | Trigger Step 3 sub-loop; revert+fix the hardening change at root cause; do NOT proceed to next hardening concern until green |
| Phase 4 Step 6 — full test suite has failures | Do NOT capture PO sign-off; trigger Step 3 sub-loop; re-run Step 6 from the failing sub-step until 100% pass-rate (or user explicitly accepts residual delta with no critical/high failures) |
| Phase 4 Step 6 — pending TODOs in delivered code | Refuse to capture PO sign-off; either (a) resolve the TODOs by routing back to Step 4 / Step 5, or (b) escalate via ADR with explicit user acknowledgment |
| Phase 4 Step 6 — UI smoke gate fails | Run the UI smoke gate (see `phase-4-step-6-ui-smoke-gate.md`) BEFORE asking for PO sign-off. If it fails (FE shows Angular CLI placeholder / no nav / blank shell / unreachable route), do NOT capture sign-off; route back to the offending wave (frontend-scaffolder for shell/nav, hardening-architect for CORS/auth, logic-translator for missing endpoints) and iterate until it passes. |
| Phase 4 PO sign-off requested while critical or high failures remain | Refuse — sign-off is BLOCKED; offer `iterate Step 6` or `stop` |
| User asks to skip a Phase 4 step | Refuse — Phase 4 steps are sequential with hard gates; the only valid option is `resume from Step N` after a partial run, not skip-ahead |

## Deliberation routing

| Situation | Decision |
|---|---|
| User explicitly requests deliberation (IT/EN trigger lexicon match ≥ 0.7) for ANY decision (Phase 1–4) | Build a decision brief and dispatch `deliberative-decision-engine`; do not decide directly. See `claude-catalog/docs/deliberation/integration-replatforming.md`. |
| Dispatch JSON contains `decisionMode: deliberative` (or `useDeliberativeDecision: true`) | Route every decision listed in `integration-replatforming.md` (Phases 1–4) to `deliberative-decision-engine` for the duration of the workflow. |
| Phase-4 decision is irreversible / production-impacting / compliance-sensitive | Auto-escalate to `deliberative-decision-engine` with `requireHumanApprovalForHighRisk: true`, even without an explicit trigger. |
| Phase 1–3 iteration adjustment contains a debate trigger (lexicon match ≥ 0.7) | Route the contested adjustment through `deliberative-decision-engine` BEFORE re-dispatching the worker sub-agents. See `iteration-loop.md` § "Optional deliberation". |
| Phase 1–3 iteration adjustment conflicts with a prior sub-agent output and resolution is subjective | Route the contested adjustment through `deliberative-decision-engine` (self-escalation by the supervisor) even without an explicit trigger. |
| Deliberation returns `pending_human_approval` | Treat as a hard HITL gate; halt the affected step; surface the question + audit trail; never proceed without the user's decision. |
| Deliberation returns `failed_insufficient_drafts` | Halt the affected step; surface the failure artefact; ask user how to proceed. **Never silently substitute a single-agent answer.** |
