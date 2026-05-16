# Per-phase protocol (Steps A–F)

> Reference doc for `refactoring-supervisor`. Read at runtime when running
> any phase (0..4). For Phases 0–3, follow steps A → B → C → D → E → F. For
> Phase 4, replace Step C with the Phase 4 driving model and replace Step E
> with the Phase 4 per-step recap shapes.
>
> **Iteration loop (Phases 1–3 only).** For analysis phases the protocol
> includes an iteration loop: after Step E (recap) the supervisor produces
> the **phase verification report** in Step E.5, then enters the
> **iterate / approve / stop** loop in Step F. The user may request one or
> more re-iterations with adjustments before approving. Phase 0 is one-shot
> (re-run by adjusting scope and dispatching again). Phase 4 has its own
> per-step HITL and never enters the analysis iteration loop.
>
> See `iteration-loop.md` and `phase-verification-report.md` for the
> canonical specs of the new HITL pattern.

For each phase N you are about to run, follow this protocol exactly.

## Step A — Pre-phase brief (you to user)

Post a brief in this exact shape:

```
=== Phase <N>: <Name> — about to start ===

Goal:        <one-line>
Supervisor:  <agent-name> (opus)
Inputs:      <expected paths; verify they exist before dispatch>
Output root: <where the supervisor will write>
Entry point: <which file the user reads first when this phase ends>

Internal parallelization:
<paste the schematic for this phase, verbatim — see schematics.md>

Estimated user touchpoints during this phase:
- The phase supervisor will itself ask for its own confirmations (e.g.,
  scope confirmation in indexing Phase 0, or Wave 1 checkpoint in
  functional analysis). Those are separate from this workflow-level
  confirmation.

Confirm: proceed with Phase <N>? [yes / revise / stop]
```

Wait for the user response. Do not dispatch without explicit "yes" (or
equivalent: "go", "procedi", "ok", "start").

## Step B — Pre-flight checks (you only)

Before dispatching the phase supervisor:

- Verify all inputs listed in the brief actually exist on disk.
- Verify the supervisor agent is available (Agent tool will return an
  error if not — surface it clearly).
- Update `workflow-manifest.json`: mark phase N as `in-progress`,
  set `current_phase: N`, write `started: <ISO-8601>`.
- Record the dispatch start timestamp in memory (you'll need it for the
  duration calculation in Step E).

If any check fails: do NOT dispatch. Surface to the user and stop.

## Step C — Dispatch (single Agent call) — Phases 0–3 only

Invoke the phase supervisor via the Agent tool. The prompt to the
phase supervisor must include:

```
You are <supervisor-name>, invoked by refactoring-supervisor.

Repo root:        <abs-path>
Output root:      <as defined in your standard contract>
Mode:             <fresh | resume>
Resume mode:      <fresh | resume-incomplete | exports-only | full-rerun | iterate>
User options:     <e.g., "challenger ON" for functional-analysis>

Run your standard pipeline. If `Resume mode: exports-only` is set
(only valid for functional-analysis-supervisor and technical-analysis-
supervisor), skip your W1/W2/W3 waves and run ONLY the export wave
for the missing file(s). The workflow supervisor has already verified
the existing analysis is `complete`. You retain full authority for
your own human-in-the-loop checkpoints; the workflow supervisor will
not override them. Report back when you have completed your final
report and the manifest is updated.
```

Pass paths and options, not contents. The phase supervisor reads from
disk.

## Step C (Phase 4) — Driving model (NO single-supervisor dispatch)

Phase 4 (Application Replatforming) is **NOT dispatched as a single
Agent call**. Unlike Phases 0–3, Phase 4 is driven directly by the
Workflow Supervisor through the 7-step loop. The reason: each step
(and each feature within Step 2) has a **hard build+start+test gate**
that must be observed and confirmed by the workflow supervisor before
forward progress; a black-box sub-supervisor cannot enforce these
gates while still surfacing every failure to the user.

The driving model:

```
Phase 4 driving — per-step protocol (driven by you, the Workflow Supervisor)

  Step 0 (Bootstrap, HARD GATE):
    - dispatch developer-java + developer-frontend in parallel
      to scaffold backend + frontend project structure
    - run `mvn clean verify` (Bash) — must succeed
    - run `mvn spring-boot:run` (Bash, background) — must start;
      capture startup log; kill process after readiness probe
    - run `ng serve` (Bash, background) — must start; capture
      ready-line; kill process after readiness probe
    - on ANY failure → enter Step 3 sub-loop (delegate to debugger),
      then re-run Step 0 from the failing sub-step
    - record gate evidence in manifest; HITL CHECKPOINT 0

  Step 1 (Minimal Runnable Skeleton):
    - dispatch developer-java (skeleton controllers, no logic)
    - dispatch developer-frontend (router shell + blank pages)
    - dispatch developer-java with directive
      "security: temporarily permitAll, no auth"
    - re-run build + startup gates; on failure → Step 3 sub-loop
    - HITL CHECKPOINT 1

  Step 2 (Incremental Feature Loop):
    For each feature in the Phase 1 UC list (priority order from
    decomposition; if absent, ask the user for ordering):
      2.1  announce: "starting feature: <UC-id>: <name>"
      2.2  dispatch developer-java with directive:
           "implement minimal vertical slice for <UC-id>:
            controller + DTOs + service + repository + integration
            with whatever is already there. NO over-engineering,
            NO premature abstraction. Reference Phase 1 UC
            description and Phase 3 oracle snapshot."
      2.3  dispatch developer-frontend with directive:
           "implement minimal page + service + form + binding for
            <UC-id>, calling the backend endpoint just authored."
      2.4  dispatch test-writer with directive:
           "write unit + integration tests for <UC-id>; per-UC E2E
            only when the UC requires cross-page flow."
      2.5  run `mvn clean verify` (Bash) — gate
      2.6  run `mvn test` and `ng test` — gate
      2.7  start app + smoke probe + compare output to Phase 3
           oracle snapshot for <UC-id>
      Any failure at 2.5 / 2.6 / 2.7 → Step 3 sub-loop, then resume
      at the failing sub-step. ONLY after 2.5 / 2.6 / 2.7 ALL green:
      surface per-feature recap (Step E.4 below) and advance.

  Step 3 (Validation sub-loop):
    Triggered automatically by any other step on failure.
    - dispatch debugger with the failure context (build log,
      stack trace, test output, baseline diff) and ask for root
      cause + minimal fix
    - delegate the fix to developer-java or
      developer-frontend (whichever owns the failing module)
    - re-run the gate that triggered Step 3
    - if still failing: repeat with broader context
    - on convergence: update manifest
      `validation_loop_total_triggers++` and resume the calling
      step

  Step 4 (Progressive System Construction):
    - continue Step 2 across remaining features
    - run code-reviewer in background after each Step 2.7 success
      (delegate per-feature review; non-blocking unless severity
      ≥ high)
    - HITL CHECKPOINT 2 after every N features (default N=3, ask
      user)

  Step 5 (Hardening):
    For each hardening concern (security, env config, error
    handler, logging, security headers):
      - dispatch developer-java or developer-frontend with
        the specific concern
      - re-run build + tests + startup gates
      - on regression → Step 3 sub-loop
    - HITL CHECKPOINT 3

  Step 6 (Final Validation, DELIVERABLE):
    - run full backend test suite (mvn verify)
    - run full frontend test suite (ng test)
    - run full E2E suite (Playwright)
    - compare every Phase 1 UC output to Phase 3 oracle
    - TODO sweep across delivered code (grep TODO, fail if any)
    - dispatch document-creator (or write directly) to produce
      `docs/refactoring/01-replatforming-report.md`
    - capture PO sign-off in the report
    - on any failure → Step 3 sub-loop, then re-run Step 6 from
      the failing sub-step
    - BLOCKED while critical/high failures remain
```

Each sub-agent dispatch in Phase 4 is a **single-purpose, narrowly
scoped Agent call** with full context (UC reference, oracle path,
output path, prior-step manifest excerpt). Never dispatch a
"do everything" Phase 4 call.

## Step D — Read outputs (verify, do not synthesize)

After dispatch returns:

1. Record the dispatch end timestamp.
2. Read the phase manifest (e.g., `.indexing-kb/_meta/manifest.json`
   for Phase 0) to get authoritative status.
3. List files actually produced under the output root.
4. Verify the entry-point file exists and has valid frontmatter.
5. Aggregate quality signals:
   - status of each section (complete / partial / needs-review / blocked)
   - count of open questions
   - count of low-confidence sections
6. Compute timings:
   - phase total duration = end - start (your dispatch envelope)
   - per-wave / per-step durations: parse the phase manifest's
     `started_at` / `completed_at` / `duration_seconds` fields
   - if the phase manifest exposes per-agent timings (Phase 3 does),
     surface them in the recap; for older phases that don't expose
     them, fall back to wave-level timings or just the phase total

The Agent tool's text result is a summary, not the source of truth.
Trust the manifest and the files on disk.

## Step E — Post-phase recap (you to user) — Phases 0–3

Post a recap in this exact shape:

```
=== Phase <N>: <Name> — iteration <K> completed ===

Status:           <complete | partial | failed>
Iteration:        <K>      (1 for the first run; bumps on every iterate)
Output root:      <path>
Entry point:      <path>
Files produced:   <count>

Execution timing:
- Started:        <ISO-8601>
- Completed:      <ISO-8601>
- Duration:       <human-readable, e.g., "4m 32s">
- Per-step breakdown (from phase manifest):
  - <step-1>:    <duration>
  - <step-2>:    <duration>
  - ...
  (Phases 0–2 expose wave-level timings; Phase 3 exposes per-agent
   timings — surface whatever granularity the phase manifest provides.
   If a phase manifest exposes no timing fields, surface only the
   phase total.)

Quality signals:
- Open questions:           <N>  (see <path-to-unresolved>)
- Low-confidence sections:  <N>
- Blocking issues:          <N>  (if > 0, list them)

Verification report:
- <path-to-_meta/phase-verification-report.md>     (generated in Step E.5)

Recommended review order:
1. Verification report (above) — start here
2. <entry-point file>
3. <unresolved-questions file>
4. <other notable files>

Cumulative workflow time so far:
- Phase 0:   <duration>     [if completed in this workflow run]
- Phase 1:   <duration>     [if completed]
- Phase 2:   <duration>     [if completed]
- Phase N:   <duration>     [the one just completed]
- Total:     <sum>
```

The timing block is mandatory — added in v0.3.0 per user request to
expose per-step execution times after every phase. Surface the finest
granularity the phase manifest exposes.

For Phases 1–3, the next decision is taken via the iteration loop
(Step F). The schematic of the next phase is shown in Step F's
`approve` branch — not in the recap — because the user may still
choose to iterate before moving on.

For Phase 0, the iteration loop does NOT apply. Re-running Phase 0 is
handled by re-dispatching the indexing supervisor with adjusted
scope. After Phase 0 the supervisor proceeds directly to Step F
without Step E.5.

If the phase reported `failed` or `≥ 1 blocking issue`: do NOT propose
`approve`. Offer only `iterate` or `stop` in Step F.

## Step E.5 — Phase verification report (mandatory for Phases 1–3)

After Step E and before Step F, write the **phase verification report**
to:

```
<output-root>/_meta/phase-verification-report.md
```

The canonical structure and section-by-section guidance are in
[`phase-verification-report.md`](./phase-verification-report.md). The
supervisor produces this file directly (no sub-agent dispatch). It is
generated from the phase manifest + the normalized JSONL artifacts +
the audit verdict files + the iteration log. It is overwritten at
every iteration, with the prior version snapshotted under
`_meta/snapshots/iter-<K-1>-verification-report.md`.

The verification report is the document the user reads to decide
between `approve`, `iterate`, `stop`. The deliverable PDF / PPTX is
NOT a substitute — it targets external stakeholders, not the human
running the workflow.

This step is skipped for Phase 0 (no iteration loop) and for Phase 4
(per-step recaps replace the verification report).

## Step F — Iteration loop (HITL) — Phases 1–3

Default deny. Do not auto-proceed. After Step E.5, present the
verification report path and ask the user to pick one of three
options:

```
Phase <N>: <Name> — iteration <K> ready for review.

Verification report:  <path>

What would you like to do?

  [approve]   Accept the analysis as-is. Workflow advances to Phase <N+1>
              (or ends, if Phase <N> is the last analysis phase the user
              wants to run). PDF/PPTX exports are regenerated to reflect
              the approved state.
  [iterate]   Run another iteration with adjustments. You will be asked
              to describe the adjustments. You may include debate triggers
              (e.g. "use multi-agent debate") to have a contested
              adjustment resolved through deliberation before re-dispatch.
  [stop]      End the workflow at this point. Current state is preserved
              as `partial`.
```

The canonical spec of the loop (states, delta capture, re-dispatch
policy, optional deliberation, convergence) is in
[`iteration-loop.md`](./iteration-loop.md). The supervisor follows
that spec.

### Step F branches

**If `approve`**

1. Update the phase manifest: set the run's `status: approved`,
   `approved_at: <ISO-8601>`.
2. Regenerate the PDF / PPTX exports if they reflect a prior
   iteration's state (compare timestamps with the iteration log).
   For Phases 1 and 2 this means dispatching `document-creator` and
   `presentation-creator` in `Resume mode: exports-only`. For
   Phase 3 there is no PDF export — skip.
3. Post the next-phase schematic (from `schematics.md`) and ask:
   `Confirm: proceed to Phase <N+1>? [yes / stop]`. This is the
   workflow-level confirmation between phases (existing behaviour).
4. On `yes`: move to Step A for Phase N+1. On `stop`: end workflow.

**If `iterate`**

1. Ask the user for adjustments verbatim:
   ```
   Please describe the adjustments. Be as specific as you can:
   the artifact(s) to revise, the IDs (UC-NN, F-NN, A-NN, ...),
   what is wrong, and what should be true after the iteration.
   You may include a debate trigger (e.g. "use multi-agent
   debate") if you want a contested item resolved through
   deliberation.
   ```
2. Capture the user's response. Normalize into the structured
   delta schema documented in
   [`iteration-loop.md`](./iteration-loop.md) § "Iteration delta".
3. If a debate trigger is detected (lexicon match ≥ 0.7), or if
   the delta contains an adjustment that conflicts with a prior
   sub-agent output and resolution is subjective, route the
   contested adjustment through `deliberative-decision-engine`
   per `iteration-loop.md` § "Optional deliberation" BEFORE
   re-dispatching the worker sub-agents.
4. Snapshot the current outputs to
   `_meta/snapshots/iter-<K>/...` (the phase plan documents the
   per-phase snapshot policy; the supervisor enforces it).
5. Append the delta to `_meta/iteration-log.jsonl` (one record per
   iteration). Bump the iteration counter in the phase manifest.
6. Re-dispatch the phase supervisor with `Resume mode: iterate`,
   passing the delta path. The phase supervisor decides which
   sub-agents to re-run based on the targeted artifacts (per its
   own phase plan).
7. After re-dispatch returns, re-enter the protocol at Step D
   (Read outputs) → Step E (Recap) → Step E.5 (regenerate
   verification report — section 3 "What changed" is populated
   this time) → Step F (loop again).

**If `stop`**

1. Update the phase manifest: set `status: partial`,
   `stopped_at: <ISO-8601>`.
2. Write a final status note to `_meta/workflow-status.md`
   summarising state at stop.
3. End gracefully. No further phases run in this workflow.

### Hard rules

- `approve` is NEVER auto-selected. The supervisor must wait for
  the user's explicit answer.
- If any pre-advancement auditor verdict is FAIL (see
  `refactoring-supervisor.md` § "Decision rules"), the supervisor
  MUST NOT propose `approve` — offer only `iterate` or `stop`.
- If the user picks `approve` while critical/high open questions
  exist in the verification report's blocking list, the supervisor
  re-asks once: "There are blocking items unresolved. Approve
  anyway? Type `approve --override` to confirm, or `iterate` to
  resolve them first."
- There is NO fixed cap on iterations. The user decides when to
  stop iterating.
- The verification report is regenerated from scratch at every
  iteration. Never edit it incrementally.
- Exports are regenerated only on `approve` (so the deliverable
  always reflects the approved state — never an intermediate
  iteration).

## Step F (Phase 0) — Simple confirm

Phase 0 (indexing) does not use the iteration loop. After Step E
post the next-phase schematic and ask:
`Confirm: proceed to Phase 1? [yes / revise / stop]`. `revise` for
Phase 0 means re-running with adjusted scope (not a structured
delta) — the user describes a new scope and the supervisor
re-dispatches `indexing-supervisor`.

## Step E.4 — Phase 4 per-step recap (Application Replatforming)

Phase 4 does not have a single end-of-phase recap because it runs
through 7 steps with hard gates. Instead, you produce a recap **after
every step transition** (Step 0 → 1, 1 → 2, end of each Step 2 feature,
4 → 5, 5 → 6, end of 6) AND after every Step 3 sub-loop convergence.

### Step 0 / 1 / 5 / 6 recap shape (gate steps)

```
=== Phase 4 — Step <N> (<name>) — completed ===

Hard gate evidence:
- Build (mvn clean verify):     <PASS | FAIL>     <duration>
- Application starts:           <PASS | FAIL>     <startup-time>
- Tests (mvn test / ng test):   <PASS | FAIL>     <duration>     (Step 5/6 only)
- E2E (Playwright):             <PASS | FAIL>     <duration>     (Step 6 only)
- Business-flow validation:     <PASS | FAIL>     <count>/<total> UCs    (Step 6 only)

Step 3 sub-loop:
- Triggered:    <N> times during this step
- Last cause:   <root-cause summary>
- Resolved:     yes / no (block forward progress)

What was done:
- <bullet list of substantial changes>

What is next:
- Step <N+1>: <name>
- <one-line description>

Confirm: proceed to Step <N+1>? [yes / revise / stop]
```

### Step 2 per-feature recap shape (incremental loop)

After every feature completes Step 2.7 successfully, surface:

```
=== Phase 4 — Step 2 — feature <UC-id>: <name> — done ===

Per-feature gate evidence:
- 2.4 Build:                     PASS    <duration>
- 2.5 Tests (unit + integration): PASS    <pass>/<total>    (<pct>%)
- 2.6 App starts + smoke:        PASS    <startup-time>
- 2.7 Behavior vs Phase 3 oracle: PASS    snapshot diff = none

Step 3 sub-loop:
- Triggered:    <N> times during this feature
- Resolutions:  <list of root causes>

Feature-loop progress:
- Done:         <K> / <total>    (<pct>%)
- In flight:    (none — ready for next)
- Next:         <UC-id-next>: <name>     [or "all features done — advance to Step 4"]

Top remaining features (up to 5):
  1. <UC-id>  <name>     priority: <high|med|low>
  2. ...

What would you like to do?
  [next]     advance to the next feature (recommended)
  [pause]    pause the loop here, review what's been built
  [revise]   re-do the just-finished feature (broader context)
  [stop]     end Phase 4 in `partial` state — application is in a
             working state at this checkpoint
```

Decision rules:

- Per-feature gate green → recommend `next`
- Per-feature gate failed AND Step 3 sub-loop did not converge → do
  NOT advance; offer only `revise` or `stop`
- Loop progress ≥ user-defined milestone (default every 3 features
  or end of priority block) → also surface HITL CHECKPOINT 2

### Step 3 sub-loop convergence recap (any time the sub-loop closes)

```
=== Phase 4 — Step 3 sub-loop converged ===

Triggered from:    Step <calling-step>
Trigger reason:    <build failure | test failure | runtime failure | functional issue>
Root cause:        <one-line summary from debugger>
Fix applied:       <minimal-fix summary>
Re-validation:
- Build:    PASS    <duration>
- Tests:    PASS    <pass>/<total>
- App start: PASS    <startup-time>

Resuming Step <calling-step> at sub-step <X>.
```

Failed sub-loop convergence (after N attempts, default N=3) escalates
to the user with the current partial fix and asks for guidance —
NEVER silently abandon the failure.

### End-of-Phase-4 recap (Step 6 done + PO sign-off)

```
=== Phase 4 — Application Replatforming — COMPLETED ===

Status:                complete
Output root:           docs/refactoring/
Deliverable:           docs/refactoring/01-replatforming-report.md
PO sign-off:           approved (note: <one-line>)

Step durations:
- Step 0 (Bootstrap):                 <duration>
- Step 1 (Skeleton):                  <duration>
- Step 2 (Feature loop):              <duration>     (<K>/<total> features)
- Step 4 (Progressive construction):  <duration>     (counts in Step 2's total feature work)
- Step 5 (Hardening):                 <duration>
- Step 6 (Final validation):          <duration>
- Step 3 sub-loop total triggers:     <N>            (cumulative across all steps)

Final test outcome:
- Backend tests:    <pass>/<total>    (<pct>%)
- Frontend tests:   <pass>/<total>    (<pct>%)
- E2E tests:        <pass>/<total>    (<pct>%)
- Business flows:   <K>/<total>       (<pct>%)
- TODOs in delivered code: <count>     (must be 0 unless ADR-resolved)

The application is fully built, fully runnable, fully tested.
No further phases are implemented in this workflow.
```

## Step F (Phase 4) — End-of-phase handling

After the End-of-Phase-4 recap is posted (Step 6 done + PO sign-off
captured), the workflow ends. There is no `iterate` option at the
Phase 4 boundary — Phase 4 has its own per-step iteration via the
Step 3 sub-loop. If the user wants more work after Phase 4 ends, that
is a NEW workflow invocation.

If PO sign-off was declined (state `partial`): update manifest with
`current_phase: 4, status: partial`, write a final status note, end
gracefully. The user may re-enter Phase 4 in a future workflow run
with `Resume Phase 4 from Step <N>`.
