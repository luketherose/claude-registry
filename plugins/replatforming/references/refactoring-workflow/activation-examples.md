# Activation examples

> Reference doc for `refactoring-supervisor`. Read at runtime when the user's
> opening message is unclear about which phase to run, or when describing the
> capability's surface to the user.

The user can trigger the workflow with phrases such as:

- "Start the application replatforming workflow"
- "Start the refactoring workflow" (legacy phrasing — still accepted;
  the capability has been renamed but old triggers still route here)
- "Lancia il workflow di replatforming" / "Lancia il refactoring"
- "Run application replatforming on this repo"
- "Resume replatforming" (you detect prior state — including the
  Phase 4 step / feature progress — and propose where to pick up)
- "Run only Phase 0" / "Run only the indexing phase"
- "Run Phase 1" (assumes Phase 0 is already complete; verify before
  dispatch)
- "Run Phase 2" (assumes Phase 0 is complete and ideally Phase 1 too;
  Phase 2 can run with Phase 1 missing but with reduced traceability —
  flag this in the pre-phase brief)
- "Run Phase 3" / "Run source application testing" (requires Phase 0,
  1, and 2 complete; Phase 3 cannot run without them as it consumes
  UC list, integrations, and risk register from those outputs)
- "Run Phase 4" / "Start the rewrite" / "Start replatforming"
  (requires Phase 0, 1, 2, and 3 complete; the rewriting phase with
  target tech — Spring Boot 3 + Angular; drives the 7-step
  incremental loop with hard build+start+test gates; produces the
  fully built/runnable/tested TO-BE application + the deliverable
  `01-replatforming-report.md` with PO sign-off in Step 6)
- "Resume Phase 4 from Step <N>" (resumes a partial replatforming
  run — verify the manifest's `current_step` and feature-loop
  progress; do not re-run completed steps)
- "Run Phase 5" (legacy phrasing — clarify: there is no separate
  Phase 5 anymore; final validation is Phase 4 Step 6)

Whatever the phrasing, you always start from the bootstrap step (see
`bootstrap-protocol.md`) and present the plan before delegating.
