#!/usr/bin/env python3
"""One-off bulk insertion of `## When to invoke` skeletons on the 67 agents
   that still lack the section after iter-2.

   - Pipeline workers (47 files in 6 topics) → topic-template; the
     `output_hint` is extracted from the agent's description (everything after
     the first colon, trimmed to a clean phrase).
   - Standalone agents (20 files) → bespoke per-name content captured in
     `BESPOKE`.

   Idempotent: agents that already have `## When to invoke` are skipped.
   The `refactoring-supervisor.md` body is deliberately left untouched
   (deferred to its v3.0.0 restructure).
"""
from pathlib import Path
import re
import yaml

ROOT = Path("/Users/luca.la.rosa/dev/claude-registry/claude-catalog/agents")
DEFER = {"orchestration/refactoring-supervisor.md"}

PIPELINE = {
    "baseline-testing": {
        "phase": "3",
        "supervisor": "baseline-testing-supervisor",
        "scope": "Strictly AS-IS — never references TO-BE technology.",
        "do_not_use": (
            "TO-BE testing or equivalence verification (use the `tobe-testing/` "
            "agents), or unit-test scaffolding for new code (use `test-writer`)"
        ),
    },
    "functional-analysis": {
        "phase": "1",
        "supervisor": "functional-analysis-supervisor",
        "scope": "Strictly AS-IS.",
        "do_not_use": (
            "technical analysis (use the `technical-analysis/` agents), TO-BE "
            "design (Phases 4+), or producing the final stakeholder LaTeX "
            "deliverable"
        ),
    },
    "indexing": {
        "phase": "0",
        "supervisor": "indexing-supervisor",
        "scope": "Indexing only — no migration planning, no TO-BE.",
        "do_not_use": (
            "functional or technical analysis (use the relevant phase "
            "supervisor) or TO-BE work"
        ),
    },
    "refactoring-tobe": {
        "phase": "4",
        "supervisor": "refactoring-tobe-supervisor",
        "scope": "First phase with target tech (Spring Boot 3 + Angular).",
        "do_not_use": (
            "AS-IS analysis (Phases 0–3) or TO-BE testing (use the "
            "`tobe-testing/` agents)"
        ),
    },
    "technical-analysis": {
        "phase": "2",
        "supervisor": "technical-analysis-supervisor",
        "scope": "Strictly AS-IS — produces findings, not fixes.",
        "do_not_use": (
            "functional analysis (use `functional-analysis/` agents), TO-BE "
            "work, or fixing the issues found (the agent only reports)"
        ),
    },
    "tobe-testing": {
        "phase": "5",
        "supervisor": "tobe-testing-supervisor",
        "scope": "Validates TO-BE against the AS-IS baseline captured in Phase 3.",
        "do_not_use": (
            "writing TO-BE tests for green-field code (use `test-writer`) or "
            "fixing failing TO-BE code (the agent only reports — fixes go to "
            "the relevant developer agent)"
        ),
    },
}

BESPOKE = {
    "analysis/functional-analyst.md": """## When to invoke

- **Requirement extraction from sources.** The user provides specifications, user stories, or existing code and asks for a structured Functional Requirements Catalog, Use Case Specification, or Business Process Map. Common phrasings: "extract the requirements", "list the use cases", "produce the BPMN".
- **Acceptance-criteria authoring (BDD).** A new feature needs Gherkin acceptance criteria before development.
- **Requirement gap analysis or CRUD-matrix generation.** Existing requirements are incomplete or unverified against the codebase.
- **Traceability requirements ↔ code.** A regulator, auditor, or PM asks "which line of code implements requirement X?".

Do NOT use this agent for: AS-IS reverse-engineering of an entire app (use `functional-analysis-supervisor` for the full Phase 1 pipeline), or producing the final stakeholder LaTeX deliverable (use the `functional-document-generator` skill after this agent runs).

---

""",
    "analysis/technical-analyst.md": """## When to invoke

- **Module-level technical structure mapping.** The user asks for a module map, dependency graph, bounded-context hypothesis, or data-flow diagram of a single module or small repo.
- **First step of an analysis pipeline.** Coordinating agents (e.g., `orchestrator`) dispatch this agent before deeper functional or technical work.
- **Repository semantic index for RAG.** A downstream agent or RAG system needs the structured semantic index this agent emits.

Do NOT use this agent for: full Phase 2 AS-IS technical analysis (use `technical-analysis-supervisor`), security/performance/observability findings (use the relevant `technical-analysis/` worker), or TO-BE design.

---

""",
    "api/api-designer.md": """## When to invoke

- **Designing a new REST API.** The user asks to draft a contract for a new endpoint or service. Output: OpenAPI 3.1 spec + design rationale.
- **Reviewing an existing API contract.** The user provides an OpenAPI spec or endpoint set and asks for REST-maturity-level, consistency, or breaking-change-risk feedback.
- **Picking HTTP methods, status codes, URL structure, pagination, or error format** for a specific resource.

Do NOT use this agent for: implementing the API (use the relevant `developer-*` agent), authoring tests against the contract (use `test-writer`), or full-stack architecture decisions (use `software-architect`).

---

""",
    "architecture/software-architect.md": """## When to invoke

- **System-architecture analysis or design.** The user asks for a C4 view, a deployment plan, or an integration-pattern recommendation for a non-trivial system.
- **ADR authoring.** A consequential decision needs to be recorded — technology choice, architecture style, integration approach.
- **Trade-off evaluation across non-functional requirements.** The user asks "scale vs cost", "consistency vs availability", "build vs buy".
- **Architecture review of an existing system** before a refactor, migration, or audit.

Do NOT use this agent for: implementation work (delegate to the `developer-*` agents) or technical-debt inventory (use `technical-analyst` or `technical-analysis-supervisor`).

---

""",
    "developers/developer-csharp.md": """## When to invoke

- **Writing new C# code** — controllers, services, domain logic, background workers — in a .NET 8+ project.
- **Reviewing or refactoring existing C# code** for correctness, idiomatic use of records, pattern matching, async/await, dependency injection.
- **Adding tests with xUnit / NUnit / Testcontainers** for the C# code being authored.

Do NOT use this agent for: Java/Spring projects (use `developer-java`), pure architecture decisions (use `software-architect`), or REST API contract design (use `api-designer`).

---

""",
    "developers/developer-frontend.md": """## When to invoke

- **Writing or refactoring frontend code** in any of the supported stacks: Angular, React (+ Next.js, TanStack Start, TanStack Query, TanStack Router), Vue 3, Qwik, or Vanilla JS/TS. The agent auto-detects the project framework and loads only the relevant skills.
- **Component design + implementation** of a new feature: smart/dumb split, state shape, API integration, accessibility.
- **Migrating UI code** from a legacy framework (or Streamlit) to a target stack.

Do NOT use this agent for: backend work (use the relevant `developer-*` for the language), pure CSS/SCSS theming (use the `css-expert` skill via this agent), or design-only tasks before any code (use `design-expert`).

---

""",
    "developers/developer-go.md": """## When to invoke

- **Writing Go code** — services, CLIs, libraries — using idiomatic Go (interfaces, errors-as-values, context propagation, goroutines).
- **Reviewing or refactoring Go code** for correctness, concurrency safety, dependency management.
- **Adding tests with the `testing` package + `testify` / `gomock`** for the Go code being authored.

Do NOT use this agent for: Java, Python, or other-language projects (use the relevant `developer-*`), or pure architecture decisions (use `software-architect`).

---

""",
    "developers/developer-java.md": """## When to invoke

- **Writing or refactoring Java/Spring Boot code** — Controller, Service, Repository, Entity layers; DTO + mapper introduction; Bean Validation; structured logging; RFC 7807 error handling.
- **Reviewing Java code** for correctness, layering, testing, security, observability.
- **Migrating legacy Java to Spring Boot 3.x** or producing TO-BE Spring Boot scaffolds (e.g., as part of Phase 4).
- **Authoring JUnit 5 + Mockito + Testcontainers tests** alongside the production code.

Do NOT use this agent for: Kotlin, Scala, or non-JVM languages (use the relevant `developer-*`), pure architecture decisions (use `software-architect`), or REST contract design before code (use `api-designer`).

---

""",
    "developers/developer-kotlin.md": """## When to invoke

- **Writing Kotlin code** — Spring Boot, Ktor, or KMP project — using idiomatic Kotlin (data classes, sealed hierarchies, coroutines, scope functions).
- **Reviewing or refactoring Kotlin code** for correctness, null-safety, coroutine lifecycle.
- **Migrating Java code to Kotlin** or producing TO-BE Kotlin scaffolds.

Do NOT use this agent for: pure-Java codebases (use `developer-java`), Android-specific UI (use a Compose-aware skill), or architecture decisions (use `software-architect`).

---

""",
    "developers/developer-php.md": """## When to invoke

- **Writing PHP 8.2+ code** — Laravel 10/11 (layered) or Symfony 6/7 (data-mapper) — using strict_types, readonly classes, enums, PHPStan level 8.
- **Reviewing or refactoring existing PHP code** for type safety, idiomatic framework use, security.
- **Authoring PHPUnit / Pest tests** for the PHP code being written.

Do NOT use this agent for: legacy PHP <8 codebases (capabilities differ), JavaScript/TypeScript backends (use `developer-frontend` or another agent), or architecture decisions (use `software-architect`).

---

""",
    "developers/developer-python.md": """## When to invoke

- **Writing or refactoring Python code** — FastAPI services, CLIs, data pipelines, scripts — with type hints, Pydantic v2, structured logging.
- **Reviewing existing Python code** for correctness, idiomatic use of typing/Pydantic/structlog, dependency hygiene.
- **Migrating legacy Python** or porting between stacks.
- **Authoring pytest tests** alongside the production code.

Do NOT use this agent for: Streamlit apps (use `streamlit-expert` skill or the `developer-frontend` agent for full-stack), Jupyter-only data analysis (out of scope), or architecture decisions (use `software-architect`).

---

""",
    "developers/developer-ruby.md": """## When to invoke

- **Writing Ruby on Rails 7+ code** — controllers, models, service/form/query objects, Sidekiq jobs.
- **Reviewing or refactoring Rails code** for correctness, idiomatic Rails, RuboCop compliance.
- **Authoring RSpec + factory_bot tests** alongside the production code.

Do NOT use this agent for: legacy non-Rails Ruby (capabilities differ), other languages, or pure architecture decisions (use `software-architect`).

---

""",
    "developers/developer-rust.md": """## When to invoke

- **Writing Rust code** — services, CLIs, libraries — using idiomatic Rust (ownership, borrowing, traits, async/await with Tokio).
- **Reviewing or refactoring Rust code** for correctness, memory safety, error handling with `Result`/`thiserror`/`anyhow`.
- **Authoring tests with `cargo test`** + integration tests in `tests/`.

Do NOT use this agent for: WebAssembly-only frontends (use `developer-frontend` if a JS bridge is involved), other languages, or architecture decisions (use `software-architect`).

---

""",
    "documentation/document-creator.md": """## When to invoke

- **Creating an Accenture-branded PDF or DOCX deliverable** — executive summary, problem statement, solution design, architecture, component inventory, dependencies, timeline, risks. Output is read-only on inputs.
- **Converting estimation files or project documents** into a polished branded document.
- **Both business documents** (executive, concise) **and technical documents** (architecture patterns, ADRs, API contracts, detailed specs).

Do NOT use this agent for: PowerPoint output (use `presentation-creator`), enterprise LaTeX deliverables (use the `functional-document-generator` skill), or in-place edits of source files (the agent is read-only on inputs).

---

""",
    "documentation/documentation-writer.md": """## When to invoke

- **Writing or improving technical documentation** — READMEs, API guides, architecture overviews, runbooks, onboarding guides, inline code documentation.
- **Adapting tone and depth to the target audience** — developer, operator, end user, or architect — based on user-stated context.
- **Refreshing stale docs** after a code change, with the codebase as the source of truth.

Do NOT use this agent for: Accenture-branded PDF/DOCX output (use `document-creator`), PowerPoint slides (use `presentation-creator`), or GitHub wiki pages (use `wiki-writer`).

---

""",
    "documentation/presentation-creator.md": """## When to invoke

- **Creating an Accenture-branded PowerPoint deck** from project documents, estimation files, or any source material.
- **Both business decks** (executive summary, problem/solution, timeline) **and technical decks** (architecture, patterns, dependencies, cloud topology).
- **Refreshing an existing pitch deck** when the content has materially changed.

Do NOT use this agent for: PDF/DOCX output (use `document-creator`), inline doc-as-code (use `documentation-writer`), or in-place edits of source files (the agent is read-only on inputs).

---

""",
    "documentation/wiki-writer.md": """## When to invoke

- **Authoring or refreshing GitHub wiki pages** for the registry or any project that uses a wiki.
- **Keeping the wiki in sync with capability changes** — when a new agent or skill lands, the wiki page should reflect the change.
- **Creating cross-linked wiki structure** (Architecture, Capability catalog, How-to guides).

Do NOT use this agent for: in-repo docs (use `documentation-writer`), branded PDF/PPTX (use `document-creator`/`presentation-creator`), or implementing the documented features.

---

""",
    "quality/code-reviewer.md": """## When to invoke

- **Reviewing a PR or set of changed files.** Examines correctness, security (OWASP Top 10), test coverage, performance, maintainability, and convention adherence.
- **Pre-merge gate.** Before merging a feature branch, the user wants a structured review with blocking issues, suggestions, and overall recommendation (Approve / Request Changes / Comment).
- **Spot-review of a single file or function** the user is uncertain about.

Do NOT use this agent for: writing the code itself (use the relevant `developer-*`), debugging a specific failure (use `debugger`), or auditing the whole technical-debt landscape of a project (use `technical-analysis-supervisor`).

---

""",
    "quality/debugger.md": """## When to invoke

- **Diagnosing a bug from an error message + stack trace + relevant source code.** The user pastes an exception, log, or reproduction steps.
- **Identifying the root cause** of unexpected behaviour and proposing a minimal targeted fix.
- **Distinguishing real bugs from environment/configuration issues** when the error is ambiguous.

Do NOT use this agent for: refactoring beyond what the fix requires (use `refactoring-expert` skill), code review on a PR (use `code-reviewer`), or writing comprehensive test suites (use `test-writer`).

---

""",
    "quality/test-writer.md": """## When to invoke

- **Writing tests for existing code** — unit, integration, or end-to-end. Detects existing test framework and conventions.
- **Filling test-coverage gaps** identified by `code-reviewer` or a code-quality analyst.
- **Producing complete, runnable test code** for JUnit 5 + Mockito (Java), pytest (Python), Jest (JavaScript/TypeScript), or others.

Do NOT use this agent for: writing production code (use the relevant `developer-*`), debugging a specific failure (use `debugger`), or designing the test strategy at architecture level (use `software-architect`).

---

""",
}


def extract_output_hint(description: str) -> str:
    """Pull a clean output_hint phrase from a sub-agent description.

    Most pipeline workers describe themselves as
        '<Topic>-<phase> sub-agent (Wn): <colon-separated outputs>'
    or
        'Use when <conditions>: <colon-separated outputs>'
    """
    # remove the multi-line YAML folding artefact (a description that was
    # `description: >` followed by indented lines becomes one wrapped string)
    desc = " ".join(description.split())
    # strip the rubric prefix we just standardised on
    for prefix in ("Use this agent when ", "Use when ", "Use to ", "Use for "):
        if desc.startswith(prefix):
            desc = desc[len(prefix):]
            break
    # Prefer everything after the first colon (most pipeline workers use it)
    if ":" in desc:
        return desc.split(":", 1)[1].strip().rstrip(".")
    return desc.split(".", 1)[0].strip()


def make_pipeline_block(topic_cfg: dict, output_hint: str) -> str:
    return (
        "## When to invoke\n\n"
        f"- **Phase {topic_cfg['phase']} dispatch.** Invoked by "
        f"`{topic_cfg['supervisor']}` during the appropriate wave to produce "
        f"{output_hint}. {topic_cfg['scope']}\n"
        f"- **Standalone use.** When the user explicitly asks for "
        f"{output_hint} outside the `{topic_cfg['supervisor']}` pipeline, with "
        f"the same inputs already in place.\n\n"
        f"Do NOT use this agent for: {topic_cfg['do_not_use']}.\n\n"
        "---\n\n"
    )


def find_anchor(text: str) -> str | None:
    """Return the heading right after `## Role` so we can insert the new
    section before it. Falls back to `---` separator if no next heading."""
    role_idx = text.find("## Role")
    if role_idx < 0:
        return None
    rest = text[role_idx + len("## Role"):]
    # Find the next top-level heading after Role
    m = re.search(r"^## (?!When to invoke).+?$", rest, re.MULTILINE)
    if m:
        return rest[m.start(): m.end()]
    return None


def insert_block(text: str, block: str) -> str | None:
    anchor = find_anchor(text)
    if not anchor:
        return None
    return text.replace(anchor, block + anchor, 1)


def main() -> None:
    pipeline_done, bespoke_done, skipped = 0, 0, []
    for p in sorted(ROOT.rglob("*.md")):
        rel = str(p.relative_to(ROOT))
        if rel in DEFER:
            skipped.append((rel, "deferred"))
            continue
        text = p.read_text(encoding="utf-8")
        if "## When to invoke" in text:
            continue
        # Resolve the block to insert
        topic = p.parent.name
        if rel in BESPOKE:
            block = BESPOKE[rel]
            kind = "bespoke"
        elif topic in PIPELINE:
            fm_match = re.search(r"^---\n(.*?)\n---", text, re.DOTALL)
            if not fm_match:
                skipped.append((rel, "no frontmatter"))
                continue
            try:
                fm = yaml.safe_load(fm_match.group(1)) or {}
            except yaml.YAMLError:
                skipped.append((rel, "yaml parse"))
                continue
            desc = str(fm.get("description", "")).strip()
            output_hint = extract_output_hint(desc) or "the artefacts described in the frontmatter"
            block = make_pipeline_block(PIPELINE[topic], output_hint)
            kind = "pipeline"
        else:
            skipped.append((rel, f"no template for topic {topic}"))
            continue

        new_text = insert_block(text, block)
        if not new_text or new_text == text:
            skipped.append((rel, "no insertion anchor"))
            continue
        p.write_text(new_text, encoding="utf-8")
        if kind == "pipeline":
            pipeline_done += 1
        else:
            bespoke_done += 1
        print(f"  ✓ {kind:8s} {rel}")

    print(
        f"\nDone: pipeline {pipeline_done}, bespoke {bespoke_done}, "
        f"skipped {len(skipped)}"
    )
    for rel, why in skipped:
        print(f"  - {rel}: {why}")


if __name__ == "__main__":
    main()
