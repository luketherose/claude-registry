# KB manifest update — schema and rules

> Reference doc for `indexing-supervisor`. Read at runtime after every phase,
> before writing the manifest update.

---

## Update rule

After every phase, update `.indexing-kb/_meta/manifest.json`. If the file
does not exist, create it. Append to `runs` for resumed sessions; do not
overwrite previous run entries.

## Schema

```json
{
  "schema_version": "1.0",
  "repo_root": "<abs-path>",
  "runs": [
    {
      "run_id": "<ISO-8601>",
      "supervisor_version": "1.0.0",
      "resume_mode": "fresh | resume-incomplete | full-rerun | revise",
      "scope": {
        "packages_included": ["<list>"],
        "packages_skipped": ["<list>"]
      },
      "phases": [
        {
          "phase": 1,
          "agent": "<name>",
          "started": "<ISO-8601>",
          "completed": "<ISO-8601>",
          "outputs": ["<paths>"],
          "status": "complete | partial | failed",
          "open_questions_count": 0
        }
      ]
    }
  ]
}
```

## Cross-references

- The `stack` block from `02-structure/stack.json` (written by
  `codebase-mapper` in Phase 1) must be copied into the current run entry
  so downstream phases have a single canonical reference location.
- `resume_mode` values match the Phase-0 detection table: `fresh`,
  `resume-incomplete`, `full-rerun` (after a `re-run` user choice on
  `complete-eligible`), `revise`.
- Phase entries are append-only within a run — a failed phase keeps its
  entry with `status: failed` and the next attempt creates a new entry
  in the next run.
