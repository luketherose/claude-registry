# Indexing Supervisor: Protocol Reference

Operational rules consulted by `indexing-supervisor` during a run.
Read this doc at bootstrap, before any escalation or decision, before
updating the manifest, and on any unclear situation.

---

## Pipeline state

**File**: `.indexing-kb/_meta/pipeline-state.yaml`

### Bootstrap protocol
1. Check if `pipeline-state.yaml` exists.
   - Missing → first run; create it with `status: pending` before dispatching Wave 1.
   - `status: complete` → ask user: skip / re-run / revise. Never auto-skip.
   - `status: in-progress` or `status: partial` → resume from first wave whose status is not `complete`.
2. Read `waves` map to determine which waves completed. Skip completed waves; restart from the first non-complete wave.

### Update protocol
After each wave completes, write the updated `pipeline-state.yaml` immediately before proceeding to the next wave. Never skip this step. It is the resume checkpoint.

### Schema
```yaml
phase: "Phase 0 — Codebase Indexing"
use_case: "application-replatforming"
run_id: "<uuid>"            # generate once at first-run bootstrap
started_at: "<ISO 8601>"
last_updated_at: "<ISO 8601>"
status: "in-progress"       # pending | in-progress | complete | partial | failed
waves:
  W1:
    status: complete        # pending | in-progress | complete | failed | skipped
    completed_at: "<ISO 8601>"
    agents:
      - name: codebase-mapper
        status: complete
        output: .indexing-kb/bronze/
      - name: dependency-analyzer
        status: complete
        output: .indexing-kb/bronze/dependency-graph.md
      - name: streamlit-analyzer
        status: skipped     # skipped when streamlit not in stack.frameworks
        output: null
  W2:
    status: pending
    agents:
      - name: module-documenter   # repeated N times, one per top-level package
        status: pending
        output: .indexing-kb/silver/modules/<package>.md
  W3:
    status: pending
    agents:
      - name: data-flow-analyst
        status: pending
        output: .indexing-kb/silver/data-flows.md
      - name: business-logic-analyst
        status: pending
        output: .indexing-kb/silver/business-rules.md
  W4:
    status: pending
    agents:
      - name: synthesizer
        status: pending
        output: .indexing-kb/gold/
  W4a:
    status: pending
    agents:
      - name: indexing-auditor
        status: pending
        output: .indexing-kb/gold/indexing-audit.md
```

---

## Inputs

- **Source**: the repository path provided by the user (or current working directory).
- There are no prior-phase inputs: Phase 0 is the first phase.
- Output root: `.indexing-kb/` (Bronze/Silver/Gold layout).
- The manifest at `.indexing-kb/_meta/manifest.json` is the authoritative phase state; update it after every wave using the schema in `manifest-spec.md`.

## Manifest update

After every wave, write `.indexing-kb/_meta/manifest.json` per the schema in `manifest-spec.md`. Fields to update per wave: `status` (per-phase entry), `agents` (list with completion timestamp), `unresolved_gaps`, `evidence_count`. On the final HITL gate, set the top-level `status` to `complete`, `partial`, or `failed`.

## Sub-agents

See `sub-agents-catalog.md` for the full roster (wave assignment, output targets, conditional gates). Summary:

| Wave | Agent | Conditional |
|---|---|---|
| W1 | `codebase-mapper`, `dependency-analyzer` | n/a |
| W1 | `streamlit-analyzer` | only when `streamlit` ∈ stack.frameworks |
| W2 | `module-documenter` × N | one per top-level package |
| W3 | `data-flow-analyst`, `business-logic-analyst` | n/a |
| W4 | `synthesizer` | n/a |
| W4a | `indexing-auditor` | always ON |

---

## Escalation triggers: always ask the user

Stop and ask the user before proceeding when:

- **Repo size > 50k LOC of source code (any language) OR > 1000 source files**:
  warn about expected duration and token usage; ask for go/no-go.
- **`.indexing-kb/` already exists with `status: complete` files**: ask
  whether to overwrite, augment (only missing sections), or abort.
- **Sub-agent reports > 5 unresolved ambiguities** in `## Open questions`.
- **Scope expansion mid-run**: a sub-agent discovers significant code outside
  the initially confirmed scope (e.g., a vendored framework, a generated
  module). Confirm whether to extend.
- **Sub-agent fails twice on the same input**: do not retry a third time;
  escalate.
- **Conflict between two sub-agent outputs** you cannot resolve from the
  source code (e.g., dependency-analyzer says module X depends on Y;
  module-documenter says X is standalone).
- **Destructive operation suggested by yourself**: e.g., deleting old KB,
  rewriting manifest from scratch.

---

## Decision rules

| Situation | Decision |
|---|---|
| `.indexing-kb/` exists with manifest `complete` | Detect as `complete-eligible`; ask user explicitly: skip / re-run / revise. Never auto-skip silently. |
| `.indexing-kb/` exists but manifest `partial` / `failed` / missing | Detect as `resume-incomplete`; recommend `re-run`; user may override with `revise` |
| Phase already complete (manifest entry exists) | Skip; ask user if refresh wanted |
| < 4 packages | Parallelize Phase 2 fully |
| > 20 packages | Ask user for prioritization |
| Circular import detected by dependency-analyzer | Run `module-documenter` sequentially (warn user) |
| Framework `X` not detected (Streamlit, etc.) | Skip the corresponding framework-specific analyzer (e.g., `streamlit-analyzer`) entirely; do not create its target directory (e.g., `05-streamlit/`) |
| Phase 1 fails (any sub-agent) | Stop pipeline, do not proceed to Phase 2 |
| Phase 2/3 single sub-agent fails | Continue with others; flag failure in manifest |
| Sub-agent retried once already | Do not retry again; escalate |
| Bronze KB missing or empty | Cannot proceed to Phase 2 (module docs) or beyond; run codebase-mapper first |
| Large files exist without classification | Run large file index before dispatching semantic sub-agents |
| evidence-ledger.jsonl has 0 entries after Phase 1 | Escalate: codebase-mapper may have failed silently |
| indexing-auditor verdict is FAIL | Stop; surface unresolved gaps to user before proceeding |

---

## Output format for user-facing messages

After each phase, post a single concise update:

```
Phase <N>/<total>: <name> — <status>
Outputs: <list of files written or updated>
Issues: <number> open questions, <number> low-confidence sections
Next: <next phase or "awaiting confirmation">
```

Final report after Phase 4a (HITL gate):

```
Phase 0 completed.

Summary:
- X source files classified, Y large files chunked, Z evidence IDs registered
- Bronze outputs: manifest.json, file-inventory.jsonl, stack.json, symbol-index.jsonl, large-files.jsonl, large-file-chunks.jsonl, [others]
- Silver outputs: module-summaries.jsonl, business-rules.jsonl, data-flows.jsonl, [others]
- Gold outputs: system-overview.md, bounded-context-hypothesis.md, complexity-hotspots.md, coverage-report.md
- Graph outputs: nodes.jsonl, edges.jsonl
- Evidence ledger: Z entries
- Indexing auditor verdict: PASS / PASS_WITH_GAPS / FAIL
- Graph quality verdict: PASS / PASS_WITH_GAPS / N/A

Unresolved gaps:
1. [GAP-001] ...

Available decisions:
1. Proceed to Phase 1 with gaps documented
2. Re-run targeted analysis on specific gaps
3. Answer open questions now
4. Mark specific gaps as intentionally out of scope
```

---

## Constraints

- **Grounding policy enforced**: every sub-agent dispatch prompt MUST include the grounding policy block (from `grounding-policy.md`). Claims without evidence_ids must become gaps, not hallucinations.
- **Evidence ledger**: sub-agents emit evidence records to `evidence-ledger.jsonl`. The ledger is append-only and monotonically growing per run.
- **Large file policy**: before dispatching `codebase-mapper` or `module-documenter`, read `large-file-policy.md` thresholds. For files >800 lines or >150 KB, the outline→chunk→evidence strategy applies.
- **Run `indexing-auditor` before HITL.** After the synthesizer completes, dispatch `indexing-auditor` to validate coverage. Only surface the auditor's verdict and unresolved blocking gaps to the user.
- **Coverage gate**: Phase 0 cannot be declared PASS if: source files unclassified, large files without chunk coverage or exclusion reason, evidence_id duplicates in ledger, Silver claims without evidence_ids, `bronze/stack.json` missing, `_meta/manifest.json` missing, `gold/coverage-report.md` missing, `gold/graph-quality-report.md` missing, unresolved blocking gaps not shown to user.
- **Never write code or refactor source files.**
- **Never produce migration recommendations.** That is a separate later phase.
- **Never invoke yourself recursively.**
- **Never let a sub-agent write outside `.indexing-kb/`.** Verify after each
  dispatch by listing modified files in the repo.
- **Always read sub-agent outputs from disk** after dispatch: the Agent
  tool result text is a summary, not the source of truth. The KB markdown is.
- **Always update `.indexing-kb/_meta/manifest.json`** after each phase
  (schema in `${CLAUDE_PLUGIN_ROOT}/references/indexing/manifest-spec.md`).
- **Never skip Phase 0 confirmation**, even if the user says "go ahead, do
  everything". Confirmation in Phase 0 is non-negotiable: it sets scope.
- **Aggregate open questions** from all sub-agent outputs into
  `_meta/unresolved.md` after Phase 3 and again after Phase 4.
- **Redact credentials** in any output you produce or any error you echo
  to the user. Never quote a connection string with real password back.
- **All file content output via `Write`**, never via `Bash` heredoc /
  echo redirect / `tee` / `printf > file`. Mermaid, code blocks, and
  any text containing `[`, `{`, `}`, `>`, `<`, `*` are unsafe to pass
  through the shell. Reference: Phase 2 incident of 2026-04-28
  (48 accidental files, executed `store` command via redirect).
  This rule MUST be propagated to every sub-agent dispatch prompt
  (template in `${CLAUDE_PLUGIN_ROOT}/references/indexing/dispatch-prompt-template.md`
  already includes it, verify on every dispatch).
