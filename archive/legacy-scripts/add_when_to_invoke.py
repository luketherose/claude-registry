#!/usr/bin/env python3
"""One-off: add `## When to invoke` to top-level supervisor agents.

Inserts the section before the heading that follows `## Role` (per registry
convention, that heading is `## Inputs` or its equivalent). Idempotent — skips
files that already have the section.
"""
from pathlib import Path

ROOT = Path("/Users/luca.la.rosa/dev/claude-registry/claude-catalog/agents")

# Map: relative agent path -> (anchor_section_to_insert_before, when_to_invoke_block)
INSERTS = {
    "orchestration/orchestrator.md": (
        "## Step 1 — Discover available agents",
        """## When to invoke

- **Multi-domain request.** The user describes work that spans backend, frontend, database, infrastructure, design, tests, or documentation simultaneously — e.g. "add a feature with API + UI + migration + tests", "review this whole module end-to-end". Decompose, dispatch specialists in parallel where possible, synthesise.
- **Ambiguous scope.** The request is vague about which surface is involved or which agent should own it — e.g. "improve this app", "make this faster", "tighten security across the project". Decompose first, then ask one focused clarifying question if a critical surface is still unclear.
- **Cross-stack refactor.** A change in one place (DTO rename, endpoint shape, database column) cascades into multiple agents' surfaces. Coordinate the cascade so no surface is missed.
- **Heterogeneous deliverable.** The user wants a single coherent output that no individual agent can produce alone — e.g. an architectural proposal that integrates a security review, a performance assessment, and a migration plan.

Do NOT use this agent for: single-surface tasks (use the specialist directly), or full migration/refactoring workflows that have a dedicated supervisor (use `refactoring-supervisor`).

---

""",
    ),
    "indexing/indexing-supervisor.md": (
        "## Knowledge base layout",
        """## When to invoke

- **Phase 0 entry point.** The user asks to "index this codebase", "build the knowledge base", "produce `.indexing-kb/`", or starts a refactoring/migration workflow that has no `.indexing-kb/` yet. Detect the AS-IS stack, dispatch the 7 sub-agents, write the canonical `stack.json`.
- **Refresh of an existing index.** `.indexing-kb/` already exists but the codebase has materially changed since last run. The supervisor detects this on bootstrap and asks the user explicitly to skip / re-run / revise — never auto-overwrites a complete index silently.
- **Stack detection only.** The user wants the canonical `stack.json` without the full module documentation pass — invoke with the partial-run flag.

Do NOT use this agent for: functional analysis (use `functional-analysis-supervisor`), technical analysis (use `technical-analysis-supervisor`), or migration planning (use `refactoring-supervisor`). This is Phase 0 only — indexing and understanding, never TO-BE.

---

""",
    ),
    "functional-analysis/functional-analysis-supervisor.md": (
        "## Inputs",
        """## When to invoke

- **Phase 1 entry point.** `.indexing-kb/` exists (from Phase 0) and the user asks for the AS-IS functional analysis — "what does this app do today", "produce the functional report", "extract the use cases". Dispatch the 8 sub-agents in 3 waves and produce `docs/analysis/01-functional/` plus PDF + PPTX exports.
- **Exports-only resume.** The functional analysis is already complete on disk but one or both exports (PDF/PPTX) are missing. The supervisor detects this and offers to regenerate just the exports without re-running the analysis.
- **Re-run after KB refresh.** Phase 0 was re-run because the codebase changed; the functional analysis should be re-derived.

Do NOT use this agent for: technical-debt or risk analysis (use `technical-analysis-supervisor`), TO-BE design (Phases 4+), or producing the final stakeholder LaTeX deliverable (that uses `functional-document-generator` after this phase completes).

---

""",
    ),
    "technical-analysis/technical-analysis-supervisor.md": (
        "## Inputs",
        """## When to invoke

- **Phase 2 entry point.** Phase 0 (`.indexing-kb/`) and ideally Phase 1 (`docs/analysis/01-functional/`) are complete. The user asks for the AS-IS technical analysis — "audit the technical debt", "produce the security/performance/observability report", "give me the AS-IS risk register". Dispatch 11 sub-agents in 3 waves and produce `docs/analysis/02-technical/` plus PDF + PPTX exports.
- **Exports-only resume.** Technical analysis already exists on disk but exports are missing. Regenerate exports only.
- **Cross-domain risk synthesis.** The user wants a unified view that spans security + performance + resilience + dependencies — exactly what the W2 risk-synthesizer produces.

Do NOT use this agent for: functional analysis (use `functional-analysis-supervisor`), baseline test authoring (use `baseline-testing-supervisor`), or any TO-BE work.

---

""",
    ),
    "baseline-testing/baseline-testing-supervisor.md": (
        "## Inputs",
        """## When to invoke

- **Phase 3 entry point.** Phases 0–2 are complete. The user asks to build the AS-IS baseline regression suite — "produce the baseline tests", "capture the AS-IS oracle", "run the baseline benchmarks", "we need the regression net before refactoring". Dispatch the 7 sub-agents in 4 waves and produce `tests/baseline/` + snapshots + benchmarks (+ optional Postman collection).
- **Bootstrap with existing baseline.** Baseline outputs already exist; the supervisor asks explicitly skip / re-run / revise (default `skip` because the oracle drives Phase 5 equivalence).
- **Adaptive execution policy decision.** The user wants the suite written but not yet executed (or vice versa) — supervisor honours the policy flag.

Do NOT use this agent for: TO-BE testing or equivalence verification (use `tobe-testing-supervisor`), unit-test scaffolding for new code (use `test-writer`), or any AS-IS analysis work.

---

""",
    ),
    "refactoring-tobe/refactoring-tobe-supervisor.md": (
        "## Inputs",
        """## When to invoke

- **Phase 4 entry point — first phase with target tech.** Phases 0–3 are complete and the user asks to start the TO-BE refactoring — "refactor to Spring Boot + Angular", "produce the TO-BE backend/frontend scaffolds", "design the bounded contexts and ADRs". Dispatch 9 sub-agents in 6 waves with strict dependency chain and 3 HITL checkpoints.
- **Adaptive verification.** The user asks the supervisor to validate via `mvn compile` / `ng build` after each wave — the supervisor honours the verify flag.
- **Bootstrap with existing TO-BE outputs.** TO-BE outputs already exist; the supervisor asks explicitly skip / re-run / revise (default `skip` to protect hand-edited generated code).

Do NOT use this agent for: TO-BE testing / equivalence (use `tobe-testing-supervisor`), AS-IS analysis (Phases 0–3), or single-file scaffolding (use `backend-scaffolder` / `frontend-scaffolder` directly when the user only wants one piece).

---

""",
    ),
    "tobe-testing/tobe-testing-supervisor.md": (
        "## Inputs",
        """## When to invoke

- **Phase 5 entry point — final go-live gate.** Phase 4 is complete. The user asks to validate the TO-BE codebase against the AS-IS baseline — "run equivalence tests", "compare TO-BE vs AS-IS Phase 3 oracle", "produce the final equivalence report for PO sign-off". Dispatch 8 Sonnet workers in 5 waves and produce `01-equivalence-report.md`.
- **Iterate on failures.** The user requests `Resume mode: iterate, Iteration scope: failures-only` after a previous run surfaced critical/high failures; the supervisor re-dispatches only on the failing scope.
- **Performance comparison only.** The user wants Phase 5 W2 (perf comparator vs Phase 3 baseline) without re-running the full equivalence suite.

Do NOT use this agent for: writing new TO-BE tests for green-field code (use `test-writer`), fixing failing TO-BE code (the supervisor only reports — fixes go to `developer-java-spring` / `developer-frontend`), or AS-IS work.

---

""",
    ),
}


def main() -> None:
    inserted, skipped = 0, []
    for rel_path, (anchor, block) in INSERTS.items():
        p = ROOT / rel_path
        text = p.read_text(encoding="utf-8")
        if "## When to invoke" in text:
            skipped.append((rel_path, "already present"))
            continue
        if anchor not in text:
            skipped.append((rel_path, f"anchor not found: {anchor!r}"))
            continue
        new_text = text.replace(anchor, block + anchor, 1)
        p.write_text(new_text, encoding="utf-8")
        print(f"  ✓ {rel_path}")
        inserted += 1
    print(f"\nDone: {inserted}/{len(INSERTS)} inserted, {len(skipped)} skipped")
    for rel_path, reason in skipped:
        print(f"  - {rel_path}: {reason}")


if __name__ == "__main__":
    main()
