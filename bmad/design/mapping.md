# BMAD Pattern Mapping for claude-registry

This document defines exactly how BMAD methodology patterns map to the
Anthropic-compliant capability format used in this registry. Every implementation
decision here has two constraints: (a) comply with BMAD's quality model, (b)
pass the Anthropic catalog/marketplace validator unchanged.

---

## 1. Core principle: adopt BMAD patterns, not BMAD file format

BMAD uses directory-based skills (`SKILL.md` + `prompts/`, `references/`,
`scripts/`). The Anthropic validator requires flat single-file `.md` capabilities.

**Resolution**: keep single `.md` files for each capability. Adopt BMAD's
*content patterns* (progressive disclosure, stage loading, document-as-cache,
DAG metadata, eval suites) using conventions already partially present in this
registry and extending them systematically.

---

## 2. Progressive disclosure (BMAD stage files)

### Problem
Supervisor bodies exceed 10k chars because Decision rules, Escalation triggers,
Sub-agent tables, and Constraints are inlined. This forces the model to process
everything at activation time, regardless of which step it is executing.

### BMAD equivalent
BMAD loads prompt files one at a time (`prompts/stage-NN-*.md`) and injects
`references/` only when needed. The skill body is minimal: identity + dispatch
table.

### Implementation for this registry
Each supervisor keeps in its `.md` body only:
- `## Role`: one paragraph max
- `## When to invoke`: 2–4 bullets + `Do NOT use` line
- `## Reference docs` table, the index of stage docs with `Read when` conditions

All operational content moves to reference docs in `plugins/<plugin>/references/<phase>/`:

| Reference doc | Contains |
|---|---|
| `supervisor-protocol.md` | Decision rules table, escalation triggers, constraints, manifest update instructions |
| `phase-plan.md` | Bootstrap dialog, per-wave dispatch instructions, HITL checkpoint prompts, closing report schema |
| `sub-agents.md` | Sub-agent roster, wave assignments, output targets, conditional gates |
| `dispatch-prompt-template.md` | Boilerplate prompt text for Agent tool calls (already exists in most phases) |

This is the primary body-length reduction path. After extraction, all supervisors
must be ≤ 10k chars and removed from `legacy-body-baseline.json`.

### Directory convention
```
plugins/<plugin>/references/<phase>/
├── supervisor-protocol.md    # decision rules + escalation + constraints
├── phase-plan.md             # bootstrap + per-wave + HITL + closing
├── sub-agents.md             # roster + wave map + output targets
└── dispatch-prompt-template.md  # Agent dispatch boilerplate
```

`<phase>` values: `indexing`, `functional-analysis`, `technical-analysis`,
`baseline-testing`, `refactoring-workflow`, `deliberation`.

---

## 3. Document-as-cache (BMAD workflow state persistence)

### Problem
Supervisors use ad-hoc "detect existing outputs" logic. After a context
compression event the supervisor cannot reliably resume, it re-reads disk but
has no authoritative state record.

### BMAD equivalent
BMAD tracks workflow state in the output document itself (YAML frontmatter with
stage status, draft sections accumulating content). On resumption the agent reads
the document to restore state.

### Implementation for this registry
Each phase outputs a `_meta/pipeline-state.yaml` in its output directory. Format:

```yaml
phase: "Phase 1, Functional Analysis"
use_case: "application-replatforming"
run_id: "<uuid>"
started_at: "2026-05-30T10:00:00Z"
last_updated_at: "2026-05-30T10:45:00Z"
status: "in-progress"   # pending | in-progress | complete | partial | failed
iteration: 1
waves:
  W1:
    status: complete    # pending | in-progress | complete | failed | skipped
    completed_at: "2026-05-30T10:20:00Z"
    agents:
      - name: actor-feature-mapper
        status: complete
        output: docs/analysis/01-functional/raw/01-actors-features.md
      - name: ui-surface-analyst
        status: complete
        output: docs/analysis/01-functional/raw/02-ui-surface.md
      - name: io-catalog-analyst
        status: complete
        output: docs/analysis/01-functional/raw/03-io-catalog.md
  W2:
    status: in-progress
    agents: []
exports:
  pdf: null            # path when generated
  pptx: null
```

Supervisors:
1. Read `_meta/pipeline-state.yaml` on bootstrap (create if absent).
2. Write it after each wave with updated statuses.
3. Use it to decide what to skip on resume (status: complete → skip) vs rerun.
4. Replace the current ad-hoc "detect existing outputs by listing files" pattern.

---

## 4. Workflow DAG (BMAD preceded_by / followed_by)

### Problem
`catalog.json` has no dependency graph. There is no machine-readable way to know
which agents must precede a given agent or what agents it can trigger.

### BMAD equivalent
`module-help.csv` has explicit `preceded-by` and `followed-by` columns for every
skill, enabling completion detection and dependency graphing.

### Implementation for this registry
Extend `catalog.json` entries with two optional arrays:

```json
{
  "name": "user-flow-analyst",
  "preceded_by": ["actor-feature-mapper", "ui-surface-analyst", "io-catalog-analyst"],
  "followed_by": ["functional-analysis-challenger", "functional-traceability-auditor"],
  "workflow": "application-replatforming",
  "phase": "Phase 1",
  "wave": "W2"
}
```

Fields:
- `preceded_by`: agents whose outputs this agent consumes (must be complete first).
- `followed_by`: agents that consume this agent's output.
- `workflow`: which workflow this agent belongs to (empty for standalone agents).
- `phase`: phase identifier within the workflow (empty for standalone).
- `wave`: wave identifier within the phase (empty for standalone).

The validator does NOT need to validate these fields (they are additive metadata).
The `bmad/workflows.json` registry reads them to build the execution graph.

---

## 5. Workflow registry (BMAD module registry)

### Problem
No machine-readable index of available workflows, their entry points, their input
requirements, or their output locations. Adding a new use case requires modifying
the `refactoring-supervisor` body.

### BMAD equivalent
`module-help.csv` at the module level + `assets/module.yaml` for discovery.
The `bmad-help` skill reads these to present available capabilities contextually.

### Implementation for this registry
`bmad/workflows.json`, top-level use-case registry:

```json
{
  "workflows": [
    {
      "id": "application-replatforming",
      "name": "Application Replatforming",
      "description": "End-to-end AS-IS→TO-BE migration of a codebase",
      "entry_agent": "refactoring-supervisor",
      "trigger_phrases": [
        "Start the application replatforming workflow",
        "Lancia il refactoring",
        "Run Phase"
      ],
      "phases": [
        {"id": "phase-0", "name": "Codebase Indexing",     "supervisor": "indexing-supervisor",              "output": ".indexing-kb/"},
        {"id": "phase-1", "name": "Functional Analysis",   "supervisor": "functional-analysis-supervisor",   "output": "docs/analysis/01-functional/"},
        {"id": "phase-2", "name": "Technical Analysis",    "supervisor": "technical-analysis-supervisor",    "output": "docs/analysis/02-technical/"},
        {"id": "phase-3", "name": "Baseline Testing",      "supervisor": "baseline-testing-supervisor",      "output": "tests/baseline/"},
        {"id": "phase-4", "name": "Application Replatforming", "supervisor": "refactoring-supervisor",       "output": "backend/, frontend/"}
      ],
      "prerequisites": [],
      "shared_agents": ["developer-java", "developer-frontend", "test-writer", "debugger", "software-architect", "api-designer"]
    }
  ]
}
```

`entry_agent` for independent phase supervisors is the supervisor itself.
`shared_agents` lists agents used across multiple workflows (not owned by one).

---

## 6. Eval suites (BMAD trigger evals + artifact evals)

### Problem
No formal quality gate on whether agents activate correctly or produce correct
outputs. Quality is enforced only via the body-length ratchet and description
rubric, not via behavioral testing.

### BMAD equivalent
- `triggers.json`: verifies skill activation rate (3 runs, threshold 0.5).
- `evals.json`: tests skill execution against graded expectations.

### Implementation for this registry
Directory: `plugins/<plugin>/evals/<agent-name>/`

#### triggers.json schema
```json
[
  {
    "query": "Index this codebase and build the knowledge base",
    "should_trigger": true,
    "description": "Direct Phase 0 invocation"
  },
  {
    "query": "What does this function do?",
    "should_trigger": false,
    "description": "Generic question, should NOT trigger indexing-supervisor"
  }
]
```

#### evals.json schema
```json
[
  {
    "id": "eval-001",
    "prompt": "Index the codebase at /path/to/repo",
    "expectations": [
      "Dispatches codebase-mapper in Wave 1",
      "Produces .indexing-kb/bronze/stack.json",
      "Runs indexing-auditor before HITL",
      "Asks user before overwriting existing index"
    ],
    "timeout": 300
  }
]
```

Priority order for eval authoring:
1. All 6 supervisors (trigger + artifact evals)
2. Top-10 standalone agents by usage frequency
3. All challenger/auditor agents (artifact evals only, activation is via supervisor)

---

## 7. New use-case template (BMAD Build Process equivalent)

### Problem
Adding a use case beyond "application replatforming" requires knowing the exact
structure, writing agents from scratch, and manually wiring catalog.json.

### BMAD equivalent
Build Process (BP), 6-step guided skill creation. `Convert (CW)`, migrates
existing capabilities to BMAD standard.

### Implementation for this registry
`templates/new-use-case/` scaffold:

```
new-use-case/
├── README.md                         # Step-by-step instructions
├── supervisor-template.md            # Frontmatter + skeleton body
├── worker-template.md                # Worker agent skeleton
├── docs/
│   ├── supervisor-protocol.md        # Empty decision rules + constraints template
│   └── dispatch-prompt-template.md  # Boilerplate dispatch prompt
├── evals/
│   └── triggers.json                 # Empty eval template
└── catalog-entry-template.json       # catalog.json entry template with all fields
```

`README.md` walks through the 7 steps to add a new use case:
1. Define the use case ID, name, trigger phrases
2. Copy supervisor-template.md → `plugins/<plugin>/agents/<use-case>-supervisor.md`
3. Identify workers, list which are shared (from shared_agents) vs new
4. For each new worker: copy worker-template.md + fill body
5. Create `plugins/<plugin>/references/<use-case>/` with reference docs
6. Add workflow entry to `bmad/workflows.json`
7. Add catalog.json entries for supervisor + all new workers

---

## 8. Summary table: BMAD → registry mapping

| BMAD concept | Registry implementation |
|---|---|
| `SKILL.md` body | Single `.md` file frontmatter + `## Role` + `## When to invoke` + `## Reference docs` |
| `prompts/stage-NN.md` | `plugins/<plugin>/references/<phase>/supervisor-protocol.md`, `phase-plan.md`, etc. |
| `references/` directory | `plugins/<plugin>/references/<phase>/` companion docs (already exists) |
| Progressive disclosure | `## Reference docs` table with `Read when` conditions, load on demand |
| Document-as-cache | `_meta/pipeline-state.yaml` in each phase output directory |
| `module-help.csv` `preceded_by`/`followed_by` | `preceded_by[]`/`followed_by[]` arrays in `catalog.json` entries |
| Module registry / `assets/module.yaml` | `bmad/workflows.json` |
| `triggers.json` + `evals.json` | `plugins/<plugin>/evals/<name>/triggers.json` + `evals.json` |
| Build Process (BP) scaffold | `templates/new-use-case/` |
| Three-layer `customize.toml` | Deferred, not needed for current use case count |
| Sanctum memory | Out of scope, Claude Code is stateless by design |
| `npm install` / headless mode | Out of scope, distribution via git + bash scripts |
