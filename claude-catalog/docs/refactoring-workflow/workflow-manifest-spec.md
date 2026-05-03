# Workflow manifest specification

> Reference doc for `refactoring-supervisor`. Read at runtime when creating or
> updating `<repo>/docs/refactoring/workflow-manifest.json`. The supervisor
> maintains this manifest at every state transition (phase started, phase
> completed, user revised, user stopped, every Phase 4 step transition, every
> Step 2 feature completion).

You maintain a workflow-level manifest at
`<repo>/docs/refactoring/workflow-manifest.json`. It records what has been
done, what is in progress, and what is next.

## Schema

```json
{
  "schema_version": "1.0",
  "supervisor_version": "0.1.0",
  "repo_root": "<abs-path>",
  "started": "<ISO-8601>",
  "last_updated": "<ISO-8601>",
  "phases": [
    {
      "phase": 0,
      "name": "indexing",
      "supervisor": "indexing-supervisor",
      "status": "complete | in-progress | pending | failed",
      "started": "<ISO-8601>",
      "completed": "<ISO-8601>",
      "output_root": ".indexing-kb/",
      "entry_point": ".indexing-kb/00-index.md",
      "open_questions": 0,
      "low_confidence_sections": 0
    },
    {
      "phase": 1,
      "name": "functional-analysis",
      "supervisor": "functional-analysis-supervisor",
      "status": "pending",
      "output_root": "docs/analysis/01-functional/",
      "entry_point": "docs/analysis/01-functional/README.md"
    },
    {
      "phase": 2,
      "name": "technical-analysis",
      "supervisor": "technical-analysis-supervisor",
      "status": "pending",
      "output_root": "docs/analysis/02-technical/",
      "entry_point": "docs/analysis/02-technical/README.md"
    },
    {
      "phase": 3,
      "name": "baseline-testing",
      "supervisor": "baseline-testing-supervisor",
      "status": "pending",
      "started": null,
      "completed": null,
      "duration_seconds": null,
      "output_root": "tests/baseline/",
      "entry_point": "docs/analysis/03-baseline/README.md"
    },
    {
      "phase": 4,
      "name": "application-replatforming",
      "driver": "refactoring-supervisor (this agent, drives directly)",
      "status": "pending",
      "started": null,
      "completed": null,
      "duration_seconds": null,
      "output_root": "docs/refactoring/",
      "entry_point": "docs/refactoring/README.md",
      "deliverable": "docs/refactoring/01-replatforming-report.md",
      "code_outputs": ["backend/", "frontend/", "e2e/"],
      "current_step": 0,
      "steps": [
        {
          "index": 0,
          "name": "bootstrap",
          "status": "pending | in-progress | complete | failed",
          "started": null,
          "completed": null,
          "duration_seconds": null,
          "gate": {
            "build_green": false,
            "app_starts": false
          }
        },
        {
          "index": 1,
          "name": "minimal-runnable-skeleton",
          "status": "pending",
          "gate": {
            "build_green": false,
            "app_starts": false
          }
        },
        {
          "index": 2,
          "name": "incremental-feature-loop",
          "status": "pending",
          "feature_loop_progress": {
            "total_features": 0,
            "features_done": 0,
            "features_in_flight": null,
            "features_pending": []
          },
          "gate_per_feature": {
            "build_green": false,
            "tests_pass": false,
            "app_starts": false,
            "behavior_validated_vs_baseline": false
          }
        },
        {
          "index": 3,
          "name": "validation-loop",
          "is_subloop": true,
          "trigger_count": 0,
          "last_trigger_step": null,
          "last_root_cause": null
        },
        {
          "index": 4,
          "name": "progressive-system-construction",
          "status": "pending",
          "feature_coverage_percent": 0
        },
        {
          "index": 5,
          "name": "hardening",
          "status": "pending",
          "hardening_concerns_done": [],
          "gate": {
            "build_green": false,
            "app_starts": false,
            "full_tests_pass": false
          }
        },
        {
          "index": 6,
          "name": "final-validation",
          "status": "pending",
          "gate": {
            "backend_tests_pass": false,
            "frontend_tests_pass": false,
            "e2e_tests_pass": false,
            "business_flows_validated": false,
            "todos_resolved": false
          },
          "po_signoff": "pending | approved | rejected"
        }
      ],
      "validation_loop_total_triggers": 0
    }
  ],
  "current_phase": null,
  "next_phase": 1
}
```

## Update rules

- Each phase entry tracks `started`, `completed`, and `duration_seconds`
  to support the timing recap (added in v0.3.0). Compute duration from
  the ISO timestamps when reading the phase's manifest in Step D of the
  per-phase protocol.
- If the directory `<repo>/docs/refactoring/` does not exist, create it
  before writing.
- Update this manifest after every state transition: phase started, phase
  completed, user revised, user stopped, every Phase 4 step transition, every
  Step 2 feature completion.
- For Phase 4, additionally update `validation_loop_total_triggers` every
  time the Step 3 sub-loop is invoked, and `feature_loop_progress` after
  each Step 2 feature passes its 7 sub-step gates.
