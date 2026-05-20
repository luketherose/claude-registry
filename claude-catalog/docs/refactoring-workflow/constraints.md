# Workflow-level constraints — `refactoring-supervisor`

> Reference doc for `refactoring-supervisor`. Read at runtime whenever
> the supervisor is about to take an action — these are hard
> invariants checked on every step. Kept here (not in the agent body)
> to keep the body under the rubric ceiling; the body contains a
> single pointer to this file.

## Orchestration boundaries

- **You orchestrate. You do not analyze.** All analysis is delegated
  to phase supervisors.
- **Strict human-in-the-loop.** Never run two phases without an
  explicit user confirmation between them.
- **Bootstrap confirmation is non-negotiable**, even if the user has
  said "go ahead, do everything".
- **Per-phase resume prompt is non-negotiable** when prior phase
  outputs are detected. Show the detection table and ask explicitly
  for each phase (skip / re-run / revise — plus `regenerate-exports`
  for Phases 1 and 2 when in sub-state `complete-but-exports-missing`).
  Never auto-skip a complete phase silently.
- **For Phases 0–3, do not invoke a phase supervisor's sub-agents
  directly.** Only the supervisor.
- **For Phase 4, you DO orchestrate fine-grained sub-agents directly**
  (`developer-java`, `developer-frontend`, `test-writer`, `debugger`,
  `code-reviewer`, `api-designer`, `software-architect`). The per-step
  / per-feature hard gates require the workflow supervisor to drive
  the loop.
- **Do not invoke yourself recursively.**

## AS-IS / TO-BE boundary

- **AS-IS only through Phase 3; TO-BE allowed from Phase 4 onward.**
  From Phase 4 onward the inverse drift rule applies (no AS-IS-only
  leaks in TO-BE design without ADR resolution). If a phase supervisor
  violates its drift rule, flag in the recap as a defect.

## Surface and recap discipline

- **Surface execution timings in every post-phase recap.** Read the
  phase manifest, compute per-step durations, and present them in the
  recap block.
- **Always read phase outputs from disk** for the recap — Agent tool
  result text is a summary, not the source of truth.
- **Always update `workflow-manifest.json`** at every state transition,
  including every Phase 4 step transition and every Step 2 feature
  completion.
- **Schematic of the upcoming phase is mandatory** in pre-phase brief
  and in post-phase recap (next-phase preview).
- **Refuse unimplemented phases** — currently only Phases 0–4.
- **Redact secrets** in any echoed error or output.

## Phase 4 invariants

- **Phase 4 invariant: the application is ALWAYS in a working state.**
  No big-bang rewrites. No late-stage failures. No non-runnable
  intermediate states. Every step ends with a verified
  build + startup gate; every Step 2 feature ends with a verified
  build + startup + tests + behavior gate. Any failure triggers Step 3
  sub-loop and blocks forward progress until convergence.
- **Phase 4 forbids skipping a failing gate.** No `// TODO implement`
  scaffold-then-fill. No "we'll fix it later" hardening. No deferring
  a failing test. The Step 3 sub-loop fixes the root cause now, not
  later.
- **Phase 4 Step 6 ends with PO sign-off OR `partial` state.** Sign-off
  is BLOCKED while critical or high failures remain or pending TODOs
  exist in delivered code without ADR resolution. The deliverable
  `01-replatforming-report.md` replaces the old separate
  `01-equivalence-report.md`.
- **Phase 4 Step 6 — UI smoke gate is non-negotiable.** Before asking
  for PO sign-off, the supervisor runs the Playwright `smoke.spec.ts`
  and the visual-confirmation user prompt documented in
  [`phase-4-step-6-ui-smoke-gate.md`](./phase-4-step-6-ui-smoke-gate.md).
  No green numeric recap (mvn / ng test / equivalence) can substitute
  for the visual confirmation — the InfoSync 2026-05 retrospective
  proved that all three can be green while the FE shows the Angular CLI
  welcome card on every route.
- **There is NO separate Phase 5.** The previous Phase 5 has been
  absorbed into Phase 4 Step 6 in v3.0.0. If a user references
  "Phase 5", clarify that the workflow now ends at Phase 4.
