# Indexing pipeline — phase plan (default)

> Reference doc for `indexing-supervisor`. Read at runtime when starting a
> fresh indexing run, resuming an incomplete one, or revising a single phase.
> Decision logic (escalation, stop conditions, retry rules) stays in the
> supervisor body — only the per-phase mechanics live here.

---

## Phase 0 — Bootstrap (supervisor only, no sub-agents)

1. **Detect resume mode**. Inspect what is on disk and pick one of:

   | Condition | Resume mode |
   |---|---|
   | No `.indexing-kb/` directory | `fresh` |
   | `.indexing-kb/` exists but `_meta/manifest.json` reports `partial` / `failed` / missing / unreadable | `resume-incomplete` |
   | `.indexing-kb/` exists AND `_meta/manifest.json` last run reports `complete` | `complete-eligible` — ask the user before doing anything |

   When `complete-eligible` triggers, ask the user verbatim:

   ```
   The codebase index at .indexing-kb/ is already COMPLETE in this repo.
     Last run:    <ISO-8601 from manifest>
     Modules:     <count from 02-structure/language-stats>
     Stack:       <python | python+streamlit | …>

   What should I do?
     [skip]    keep the existing index as-is, do nothing.
     [re-run]  re-run the full pipeline from Phase 1 (you'll see a
               per-section overwrite confirmation; old artifacts are
               replaced).
     [revise]  inspect a specific section together first (e.g.,
               regenerate only `04-modules/<package>/` for a package
               that changed).
   ```

   Default deny: do not proceed without an explicit answer. Default
   recommendation: `skip`. If the user answers `skip`, post a short
   recap pointing to `.indexing-kb/00-index.md` and exit cleanly. If
   `revise`, ask which section(s) to refresh and dispatch only those
   sub-agents. If `re-run`, continue with the remaining bootstrap
   steps.

   In `resume-incomplete` mode, surface the manifest status to the
   user and recommend `re-run` (do not auto-resume from broken state);
   the user may override with `revise` to fix specific sections.

   In `fresh` mode, continue with the remaining bootstrap steps as
   normal.

2. Read `.indexing-kb/_meta/manifest.json` if it exists (resume support).
3. **Lightweight stack pre-detection** (full detection happens in Phase 1
   via `codebase-mapper`; this step is just enough to decide which
   framework-specific sub-agents to include in Phase 1). Apply the same
   markers documented in `codebase-mapper`'s `stack.json` schema, but
   only at the level needed for dispatch decisions:

   - **Build manifest scan**: check repo root for `pyproject.toml`,
     `setup.py`, `requirements.txt`, `Pipfile`, `package.json`,
     `pom.xml`, `build.gradle*`, `Cargo.toml`, `go.mod`, `*.csproj`,
     `*.sln`, `Gemfile`, `composer.json`, `Package.swift`, `mix.exs`.
   - **File-extension count** (rough): `find . -type f -name '*.<ext>' | wc -l`
     for each major language extension, to identify the primary
     language. Skip the default skip list below.
   - **Framework signals** (gates dispatch of framework-specific
     analyzers — currently only `streamlit-analyzer`):
     - Streamlit: `import streamlit` in any `.py`, OR `.streamlit/`
       directory, OR `streamlit` in dependency files. 2 of 3 → confirmed.
     - (Future framework-specific analyzers will gate similarly. The
       canonical detection rules live in `codebase-mapper`'s
       `stack.json` output and the design doc dispatch table.)
4. Identify top-level packages / modules per language conventions
   (`__init__.py` for Python, `src/main/{java,kotlin}/...` for JVM,
   `cmd/`/`internal/` for Go, `Cargo.toml` workspace members for
   Rust, `*.csproj` for .NET, `app/`/`lib/` for Ruby, etc.). The full
   inventory is `codebase-mapper`'s job at Phase 1; in Phase 0 a
   rough count is sufficient.
5. Build the proposed scope. Default skip list (language-aware):
   - common: `node_modules/`, `dist/`, `build/`, `out/`, `target/`,
     `.cache/`, `.idea/`, `.vscode/`, `.git/`
   - python: `__pycache__/`, `.venv/`, `venv/`, `env/`,
     `*.egg-info/`, `migrations/`, `alembic/versions/` (keep
     `alembic/env.py`)
   - java/kotlin: `.gradle/`, `gradle-wrapper/`, `bin/` if Maven
     output, generated `target/`
   - rust: `target/`
   - go: `vendor/` (unless explicitly committed)
   - csharp: `bin/`, `obj/`
   - ruby: `vendor/bundle/`, `tmp/`, `log/`
   - php: `vendor/`
   - typescript / javascript: `coverage/`, `.next/`, `.nuxt/`, `.svelte-kit/`
   - tests: skip `tests/`, `test/`, `spec/`, `__tests__/` from module
     documentation but keep them visible in the structural map (test
     code carries valuable signal about behaviour).
6. **Present scope, detected primary language + frameworks, and
   phase plan to the user. Ask for confirmation before dispatching
   any sub-agent.** The full, evidence-backed `stack.json` will be
   written by `codebase-mapper` in Phase 1; this Phase-0 detection
   is rough and only used to decide which framework-specific
   analyzers to include in the Phase 1 batch.

---

## Phase 1 — Structural (parallel, single message with multiple Agent calls)

Dispatch in parallel:
- `codebase-mapper` — produces `stack.json` (the authoritative AS-IS
  stack manifest) plus `codebase-map.md` and `language-stats.md`
- `dependency-analyzer`
- **framework-specific analyzers** — gated on `stack.frameworks` from
  the Phase-0 lightweight pre-detection. Currently:
  - `streamlit-analyzer` if `streamlit` is among the detected
    frameworks
  - (future framework-specific analyzers slot in here following the
    same gate-by-detection pattern)

After dispatch, **read `02-structure/stack.json` first** — it is the
canonical AS-IS stack and supersedes the Phase-0 pre-detection. Cross-
check that the analyzers dispatched (e.g., streamlit-analyzer) match
`stack.frameworks` from the authoritative output. If there is a
disagreement between Phase-0 pre-detection and Phase-1 authoritative
detection (e.g., streamlit appeared in pre-detection but not in
`stack.json`, or vice versa), surface it to the user before
proceeding to Phase 2.

If any sub-agent reports `status: needs-review` or `confidence: low`,
surface to the user before proceeding. Copy the `stack` block from
`stack.json` into `_meta/manifest.json` so downstream phases (1-5 in
the broader refactoring pipeline) have a single canonical reference
location.

---

## Phase 2 — Module documentation (parallel fan-out)

For each top-level package identified in Phase 0:
- Dispatch one `module-documenter` invocation, scoped to that package.
- Batch in groups of 4 parallel invocations to avoid overload on large repos.
- For repos with > 20 packages: ask the user whether to index all or
  prioritize a subset.

If `dependency-analyzer` reported circular imports between packages, run
`module-documenter` sequentially (one package at a time) and warn the user.

---

## Phase 3 — Cross-cutting (parallel)

Dispatch in a single message:
- `data-flow-analyst`
- `business-logic-analyst`

---

## Phase 4 — Synthesis (sequential, single agent)

Dispatch `synthesizer`. It reads everything in `.indexing-kb/` produced by
prior phases and writes the final consolidated views.

After synthesis, post a final report to the user with:
- Path to `.indexing-kb/00-index.md` (entrypoint)
- Open questions list (from `_meta/unresolved.md`)
- Any low-confidence sections flagged for human review
