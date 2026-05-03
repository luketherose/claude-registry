# Phase 3 — Manifest schema

> Reference doc for `baseline-testing-supervisor`. Read at runtime when
> updating `docs/analysis/03-baseline/_meta/manifest.json` after each wave.

The supervisor must update the manifest after every wave. The manifest is
the canonical record of what ran, when, with which policies, and with what
test outcomes. Phase 5 (equivalence verification) reads this file to know
which oracle artifacts are authoritative.

## Path

```
docs/analysis/03-baseline/_meta/manifest.json
```

## Schema

```json
{
  "schema_version": "1.0",
  "supervisor_version": "0.1.0",
  "repo_root": "<abs-path>",
  "kb_source": "<abs-path>/.indexing-kb/",
  "phase1_source": "<abs-path>/docs/analysis/01-functional/",
  "phase2_source": "<abs-path>/docs/analysis/02-technical/",
  "stack_mode": "streamlit | generic",
  "dispatch_mode": "parallel | batched | sequential",
  "execution_policy": "on | off",
  "service_detection": "on | off | ambiguous",
  "challenger_enabled": true,
  "resume_mode": "fresh | resume-incomplete | full-rerun | revise",
  "scope_filter": null,
  "runs": [
    {
      "run_id": "<ISO-8601>",
      "started_at": "<ISO-8601>",
      "completed_at": "<ISO-8601>",
      "duration_seconds": <int>,
      "waves": [
        {
          "wave": 0,
          "agents": [
            {
              "name": "fixture-builder",
              "started_at": "<ISO-8601>",
              "completed_at": "<ISO-8601>",
              "duration_seconds": <int>,
              "status": "complete | partial | failed",
              "outputs": ["<paths>"]
            }
          ],
          "wave_duration_seconds": <int>
        }
      ],
      "test_results": {
        "passed": <int>,
        "xfail": <int>,
        "skipped": <int>,
        "failed_unresolved": <int>,
        "as_is_bugs_critical": <int>,
        "as_is_bugs_high": <int>,
        "as_is_bugs_medium": <int>,
        "as_is_bugs_low": <int>
      }
    }
  ]
}
```

## Field rules

- **`schema_version`** — bump only on breaking schema changes; current `1.0`.
- **`supervisor_version`** — current supervisor SemVer (from `catalog.json`).
- **`repo_root`** — absolute path to the repo being tested.
- **`kb_source` / `phase1_source` / `phase2_source`** — absolute paths to the
  inputs that drove this run. Used by Phase 5 to detect drift.
- **`stack_mode`** — `streamlit` if Streamlit was detected at bootstrap,
  otherwise `generic`.
- **`dispatch_mode` / `execution_policy` / `service_detection`** — the
  resolved values for Q1, Q2, and the service-detection gate (after any
  user override).
- **`resume_mode`** — `fresh` for a clean run; `resume-incomplete`,
  `full-rerun`, or `revise` per the bootstrap dialog.
- **`scope_filter`** — `null` for full coverage; otherwise a list of UC IDs
  if the user requested a subset (e.g. when N > 50).

### Timing fields

`duration_seconds` and `wave_duration_seconds` feed the recap templates.
Compute them from the ISO-8601 timestamps:

```
duration_seconds = (completed_at - started_at) in seconds
```

The supervisor records `started_at` immediately before dispatching the wave
and `completed_at` immediately after reading all worker outputs from disk.
Do not approximate — Phase 5 uses these to estimate test-run cost.

### Test results

Populated only after Wave 2 (`baseline-runner`) completes. Categories:

- **`passed`** — green tests.
- **`xfail`** — expected failures with an `as-is-bugs-found.md` entry.
- **`skipped`** — flaky / env-related skips.
- **`failed_unresolved`** — should be `0` at completion. Non-zero means the
  supervisor stopped on a critical/high failure that the user has not yet
  triaged.
- **`as_is_bugs_*`** — counts per severity from `as-is-bugs-found.md`.

## Update cadence

| When | What changes |
|---|---|
| End of Phase 0 (bootstrap confirmed) | Create file with header fields populated; `runs[].waves` empty |
| End of each wave (W0–W3) | Append the completed wave block under the current `runs[]` entry; update `wave_duration_seconds` |
| End of W2 (`baseline-runner`) | Populate `test_results` |
| End of run (after W3) | Set `runs[].completed_at` and `runs[].duration_seconds` |

If a wave fails or is partial, still write the block with `status` reflecting
the outcome — never omit. The manifest is the only authoritative timeline.
