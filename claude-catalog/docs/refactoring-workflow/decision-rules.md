# refactoring-supervisor — decision rules

Reference doc. Read on demand when classifying a situation in the
workflow. Each row maps a situation to the supervisor's decision.

## Bootstrap and inputs

| Situation | Decision |
|---|---|
| Bootstrap not confirmed | Do not dispatch any phase |
| Phase N inputs missing | Do not dispatch; ask user how to proceed |
| Phase supervisor not installed | Stop, ask user to install via setup script |

## Pre-advancement audit gates (Phases 0–2)

| Situation | Decision |
|---|---|
| Phase 0 complete — pre-advancement gate | Read `gold/indexing-audit.json` verdict; if FAIL, escalate — do not advance to Phase 1 silently |
| Phase 1 complete — pre-advancement gate | Read `normalized/functional-traceability-audit.json` verdict; if FAIL, escalate — do not advance to Phase 2 silently |
| Phase 2 complete — pre-advancement gate | Read `normalized/technical-evidence-audit.json` verdict; if FAIL, escalate — do not advance to Phase 3 silently |
| Any pre-advancement auditor verdict is FAIL | Show user the blocking gaps; offer `re-run phase` or `override with explicit acknowledgment`; never silently advance |

## Phase reporting (Phases 0–3)

| Situation | Decision |
|---|---|
| Phase reports `complete` (Phases 1–3) | Move to Step E recap → Step E.5 verification → Step F iteration loop; ask `approve / iterate / stop` |
| Phase reports `complete` (Phase 0) | Move to post-phase recap; ask user to confirm next (no iteration loop for Phase 0) |
| Phase reports `partial` (Phases 1–3) | Show partial details + verification report; default to recommending `iterate`; never propose `approve` while partial |
| Phase reports `partial` (Phase 0) | Show partial details; ask user explicitly whether partial is acceptable |
| Phase reports `failed` | Do not propose `approve`; only `iterate`/`stop` (1–3) or `revise`/`stop` (0) |
| Phase has > 5 unresolved blocking questions | Do not propose `approve`; recommend `iterate` (1–3) / `revise` (0) |

## User answer handling

| Situation | Decision |
|---|---|
| User picks `iterate` (Phases 1–3) | Capture adjustments per `iteration-loop.md` § "Iteration delta"; route contested items through deliberation if triggered; snapshot prior outputs; re-dispatch with `Resume mode: iterate`; bump iteration counter |
| User picks `approve` (Phases 1–3) | Regenerate PDF/PPTX exports if they reflect a prior iteration; post next-phase schematic; ask `yes / stop` |
| User picks `stop` (any phase) | Update manifest with `status: partial` + `stopped_at`; write final status note; end workflow |
| User attempts `approve` with blocking items unresolved | Re-ask once: require `approve --override`, else default to `iterate` |
| Iteration count > 5 on the same phase | Suggest (don't force) a deliberation-based reset; user remains in control |
| User asks to skip a phase | Allowed only if the next phase's inputs already exist; otherwise refuse |
| User asks for Phase N+1 with no implementation | Refuse; reiterate which phases are supported |

## Existing-output detection at bootstrap

| Situation | Decision |
|---|---|
| Existing complete output detected | Show in detection table; ask user per phase: `skip / re-run / revise`. Never auto-skip silently. |
| Existing output but manifest partial / failed / missing | Classify `inconsistent`; recommend `re-run`; never auto-resume from broken state |
| Phase 1 or 2 complete but ≥ 1 export file missing | Classify `complete-but-exports-missing`; recommend `regenerate-exports` as a fourth choice |
| User answers `skip` for a phase | Treat as `complete` for downstream dependencies; do not dispatch its supervisor |
| User answers `regenerate-exports` for Phase 1 or 2 | Dispatch with `Resume mode: exports-only` — skip W1/W2/W3, run only the export wave |
| User answers `re-run` for a phase | Dispatch normally; the phase supervisor handles its own overwrite confirmation |
| User selects `regenerate-exports` for Phase 0, 3, or 4 | Refuse: option only available for Phases 1 and 2 (the only phases with PDF/PPTX exports) |
| Conflict between manifest and disk state | Trust disk; flag inconsistency in recap |

## Phase 4 step gating

| Situation | Decision |
|---|---|
| Step 0 build fails | Do NOT advance; trigger Step 3 sub-loop; iterate until build green; never skip |
| Step 0 application fails to start | Do NOT advance; trigger Step 3 sub-loop with debugger on startup logs; iterate until app starts |
| Step 1 fails after Step 0 succeeded | Regression; trigger Step 3 sub-loop and converge before re-attempting |
| Step 2 — feature gate fails (build/tests/startup/behavior) | Do NOT advance; trigger Step 3 sub-loop; resume the failing sub-step (2.4/2.5/2.6/2.7) |
| Step 2 — feature iteration finishes implementation but app no longer starts | Treat exactly like Step 0 startup failure: trigger Step 3 sub-loop; never advance to the next feature until the app starts again |
| Step 3 sub-loop fails to converge after 3 attempts | Stop; surface partial fix + context; ask for guidance; never silently abandon |
| Step 4 — invariant broken (build red / app not running / tests red between features) | Halt forward progress; trigger Step 3 sub-loop |
| Step 5 — hardening change introduces a regression | Trigger Step 3 sub-loop; revert+fix at root cause; do NOT proceed to next hardening concern until green |
| Step 6 — full test suite has failures | Do NOT capture PO sign-off; trigger Step 3 sub-loop; re-run from the failing sub-step until 100% pass (or user accepts residual delta with no critical/high failures) |
| Step 6 — pending TODOs in delivered code | Refuse PO sign-off; either resolve via Step 4/5 or escalate via ADR with explicit user acknowledgment |
| Step 6 — UI smoke gate fails | Run the gate per `ui-smoke-gate.md` BEFORE asking for sign-off. If it fails (CLI placeholder / no nav / blank shell / unreachable route), route back to the offending wave (frontend-scaffolder / hardening-architect / logic-translator) |
| PO sign-off requested while critical or high failures remain | Refuse — sign-off BLOCKED; offer `iterate Step 6` or `stop` |
| User asks to skip a Phase 4 step | Refuse — steps are sequential with hard gates; only `resume from Step N` is valid |

## Per-iteration startup check (Phase 4 Step 2)

Every feature iteration in Step 2 has six sub-gates that MUST pass before
the supervisor advances to the next feature:

| Sub-step | Gate |
|---|---|
| 2.4 build | `mvn -q -DskipTests package` for backend AND `npm run build` for frontend exit 0 |
| 2.5 tests | New feature tests pass AND all prior tests still pass |
| 2.6 startup | `java -jar target/*.jar` (or `mvn spring-boot:run`) reaches `/actuator/health` `UP`; `ng serve` reaches `Application bundle generation complete`; **`mvn -Dtest=BootSmokeTest` passes** |
| 2.6.1 boot wiring | `BootSmokeTest` (no `@ActiveProfiles`) must pass. Without this, default-profile wiring regressions (e.g., missing repo bean for a newly-injected @Service) are silently masked by profile-scoped tests |
| 2.7 behavior | The new feature's happy path is exercised (curl/playwright) |
| 2.8 commit | The supervisor commits with `feat(refactor): step 2 — <feature>` so the working state is snapshotted |

Sub-step 2.6.1 is the canonical guard against the InfoSync 2026-05
regression: `mvn test` reporting 177/177 pass while `java -jar
target/*.jar` crashed with `Parameter 0 of constructor in AdminUserService
required a bean of type 'UserRepository' that could not be found`.

## Deliberation routing

| Situation | Decision |
|---|---|
| User explicitly requests deliberation (IT/EN trigger lexicon match ≥ 0.7) for ANY decision (Phase 1–4) | Build a decision brief and dispatch `deliberative-decision-engine`; do not decide directly. See `deliberative-integration.md`. |
| Dispatch JSON contains `decisionMode: deliberative` (or `useDeliberativeDecision: true`) | Route every decision listed in `claude-catalog/docs/deliberation/integration-replatforming.md` (Phases 1–4) to `deliberative-decision-engine` for the duration of the workflow |
| Phase-4 decision is irreversible / production-impacting / compliance-sensitive | Auto-escalate to `deliberative-decision-engine` with `requireHumanApprovalForHighRisk: true`, even without an explicit trigger |
| Phase 1–3 iteration adjustment contains a debate trigger (lexicon match ≥ 0.7) | Route the contested adjustment through `deliberative-decision-engine` BEFORE re-dispatching workers. See `iteration-loop.md` § "Optional deliberation" |
| Phase 1–3 iteration adjustment conflicts with a prior sub-agent output and resolution is subjective | Route through `deliberative-decision-engine` (self-escalation) even without an explicit trigger |
| Deliberation returns `pending_human_approval` | Treat as a hard HITL gate; halt the affected step; surface question + audit trail; never proceed without the user's decision |
| Deliberation returns `failed_insufficient_drafts` | Halt the affected step; surface the failure artefact; ask user how to proceed. **Never silently substitute a single-agent answer.** |
