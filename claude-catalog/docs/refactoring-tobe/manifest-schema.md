# Manifest schema — Phase 4

> Reference doc for `refactoring-tobe-supervisor`. Read at runtime when
> updating the run manifests after each wave.

After every wave the supervisor updates **both** manifests:

- `.refactoring-kb/_meta/manifest.json` — TO-BE KB run history with
  per-worker timing.
- `docs/refactoring/_meta/manifest.json` — workflow-level summary.

## Common fields (mirrors prior phases)

| Field | Type | Notes |
|---|---|---|
| `started_at` | ISO 8601 | wave start |
| `completed_at` | ISO 8601 | wave end |
| `duration_seconds` | int | derived |
| `status` | `in-progress` \| `complete` \| `partial` \| `failed` | wave-level |
| `outputs` | array of paths | files produced this wave |
| `findings_count` | int | number of findings surfaced |

## Phase-4-specific fields

| Field | Type | Allowed values |
|---|---|---|
| `resume_mode` | string | `fresh` \| `resume-incomplete` \| `full-rerun` \| `revise` |
| `iteration_model` | string | `A` (one-shot) \| `B` (per-BC milestone) |
| `code_scope` | string | `full` \| `scaffold-todo` \| `structural` |
| `verify_policy` | string | `on` \| `off` |
| `verify_results` | object | `{ mvn_compile: pass\|fail\|skipped, ng_build: pass\|fail\|skipped }` |
| `traceability_coverage` | object | `{ ucs_total: N, ucs_covered: M, orphans: K }` |
| `as_is_bugs_deferred` | array of strings | list of `BUG-NN` deferred to Phase 5 |

## Update rules

- Write both files in the same wave-completion step (no half-updates).
- Never delete prior wave entries — append.
- On `failed` status, still write the manifest entry (do not skip).
- On `resume-incomplete`, mark the resumed wave with the new
  `started_at` but preserve the prior partial outputs in `outputs`.
