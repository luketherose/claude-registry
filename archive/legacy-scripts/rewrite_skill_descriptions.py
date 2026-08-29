#!/usr/bin/env python3
"""Bulk-rewrite skill descriptions to Anthropic rubric format.
   Single-shot script for the U1+U2+U5 sweep. Idempotent."""
import re
from pathlib import Path

ROOT = Path("/Users/luca.la.rosa/dev/claude-registry/claude-catalog/skills")

# New descriptions, keyed by skill name (= filename without .md)
NEW_DESC = {
    "functional-reconstruction": 'This skill should be used when the user asks to reconstruct, document, or describe the existing functional behaviour of a codebase before a migration, refactoring, or onboarding. Trigger phrases: "document existing functionality", "reconstruct the features", "map the user flows of this codebase", "we need to migrate, document the AS-IS first". Produces feature lists, user flows, business rules, use cases, and functional dependencies in `docs/functional/`. Do not use to write new requirements — that is functional-analyst.',

    "tech-analyst": 'This skill should be used when an analysis, migration, or architecture-understanding pipeline starts and the codebase needs a structural map first. Trigger phrases: "analyse this repo", "map the modules", "what is the structure of this codebase", "index this project". Produces module maps, dependency graphs, bounded contexts, data flows, integration points, and a semantic index. Do not use for technical-debt findings — that is technical-analyst.',

    "rest-api-standards": 'This skill should be used when an agent (api-designer, developer, code-reviewer) needs the canonical REST API design standards: resource modeling, HTTP method semantics, status codes, URL structure, versioning, pagination, RFC 7807 error format, and OpenAPI 3.1 authoring. Trigger phrases: "REST API design", "how should this endpoint look", "review this API contract", "OpenAPI authoring rules". Returns reference material, not a generated spec. Do not trigger directly from a coding prompt — invoked by the agents above.',

    "java-expert": 'This skill should be used when working with Java 17+ language features outside the Spring layer — records, sealed classes, Optional, Stream API, Lombok, concurrency (CompletableFuture, virtual threads), custom exception hierarchies, SLF4J logging conventions, and document generation (Apache POI, iText). Trigger phrases: "Java records", "sealed class", "Optional best practice", "Stream API", "POI", "iText". Do not use for Spring Boot configuration (use spring-expert), JPA (use spring-data-jpa), or layered architecture (use spring-architecture).',

    "java-spring-standards": 'This skill should be used when an agent (developer-java, code-reviewer, test-writer) needs the canonical Java/Spring Boot standards: package structure, layering rules, DI, JUnit 5 + Mockito + Testcontainers, RFC 7807 ProblemDetail, SLF4J + MDC logging, Spring Security 6 baseline, Micrometer observability, and Maven conventions. Trigger phrases: "Spring standards", "review this Spring code", "how should I structure this Spring module". Returns reference material, not code. Do not trigger directly from a coding prompt — use spring-expert (config), spring-architecture (layering), or spring-data-jpa (ORM).',

    "spring-architecture": 'This skill should be used when designing or reviewing the LAYERING of a Spring Boot module — Controller/Service/Repository/Entity boundaries, DTO+mapper introduction, Bean Validation placement, global exception handling, naming conventions, or module implementation order. Trigger phrases: "add a new module", "where does this belong", "split this controller", "DTO mapping", "how do I layer this Spring code". Do not use for Spring Boot configuration concerns (use spring-expert) or JPA/ORM specifics (use spring-data-jpa).',

    "spring-data-jpa": 'This skill should be used when working with JPA/Hibernate inside a Spring project — entity design, relations, fetch strategies, N+1 fixes, transaction boundaries, JPQL queries, second-level cache, bulk operations, automatic auditing, performance tuning. Trigger phrases: "JPA entity", "@OneToMany", "N+1 query", "@Transactional placement", "Hibernate fetch". Do not use for raw SQL or migrations (use postgresql-expert) or Spring Boot wiring (use spring-expert).',

    "spring-expert": 'This skill should be used when working with Spring Boot 3.x configuration and runtime concerns — IoC/DI, auto-configuration, profiles, @ConfigurationProperties, WebClient for external APIs, Spring Security 6 with JWT, MockMvc and @WebMvcTest/@SpringBootTest test patterns. Trigger phrases: "Spring Boot config", "@ConfigurationProperties", "WebClient", "Spring Security JWT", "MockMvc test". Do not use for layering decisions (use spring-architecture) or JPA (use spring-data-jpa).',

    "accenture-branding": 'This skill should be used when an agent (presentation-creator, document-creator) generates an Accenture-branded deliverable and needs the brand reference data — color palette (hex values, python-pptx + CSS constants), typography (fonts and sizes), slide layout specs, HTML/CSS template for PDF, and usage guidelines. Trigger phrases: "Accenture branding", "Accenture deck", "Accenture PDF template", "brand colors". Do not use for client-specific design systems (e.g., UniCredit Bricks — use unicredit-design-system).',

    "postgresql-expert": 'This skill should be used when the user works with PostgreSQL — designing tables, writing or reviewing SQL, picking indices, tuning queries, authoring Liquibase migrations, configuring transactions, or setting up the H2 local-dev profile. Trigger phrases: "PostgreSQL", "Postgres", "Liquibase changelog", "SQL performance", "index tuning", "H2 local profile". Liquibase is the only supported migration tool — Flyway is forbidden; if Flyway appears, this skill should redirect to Liquibase. Do not use for ORM/JPA mapping concerns (use spring-data-jpa).',

    "backend-documentation": 'This skill should be used when generating enterprise technical documentation for a Java/Spring Boot backend, typically as part of a documentation-orchestrator pipeline. Trigger phrases: "document this backend", "generate the backend technical doc", "produce backend-doc.tex". Reads pre-existing analyses + source code and produces a `backend-doc.tex` covering architecture, API reference, data model, business logic, security, and error handling. Output is ready for pandoc conversion. Do not use for frontend documentation (use frontend-documentation).',

    "doc-expert": 'This skill should be used when producing technical or functional documentation for a Python/Streamlit, Java/Spring Boot, or Angular project. Trigger phrases: "document this code", "write the technical docs", "generate the module guide", "add docstrings + flow descriptions". Covers docstrings, flow descriptions, domain glossary, and module guides. Output is business-oriented, not implementation-oriented; saves to `docs/`. Do not use to generate enterprise LaTeX deliverables (use functional-document-generator or backend/frontend-documentation).',

    "documentation-orchestrator": 'ALWAYS use this skill when generating enterprise technical documentation for a full-stack project — it interprets a Word template, coordinates `backend-documentation` and `frontend-documentation`, ensures cross-layer consistency (DTO names, API contracts), and produces both `backend-doc.tex` and `frontend-doc.tex` ready for pandoc. Trigger phrases: "generate the technical documentation", "produce the deliverable docs", "fullstack technical doc". Do not use for single-side documentation (call backend-documentation or frontend-documentation directly).',

    "frontend-documentation": 'This skill should be used when generating enterprise technical documentation for an Angular frontend, typically as part of a documentation-orchestrator pipeline. Trigger phrases: "document this Angular app", "generate the frontend technical doc", "produce frontend-doc.tex". Reads pre-existing analyses + Angular code and produces a `frontend-doc.tex` covering module architecture, smart/dumb components, NgRx store, routing, API services, design system, and performance. Ready for pandoc. Do not use for backend documentation (use backend-documentation).',

    "functional-document-generator": 'This skill should be used when converting existing functional documentation into an enterprise LaTeX deliverable for stakeholders. Trigger phrases: "generate the functional document", "produce the .docx for the client", "convert docs/functional to LaTeX", "Word-template-driven functional doc". Reads from `docs/functional/`, interprets a provided Word template, and generates a complete `.tex` file ready for pandoc → `.docx`. Does not invent functionality not supported by the source content. Do not use to write the functional analysis itself (use functional-analyst).',

    "uml-diagram-generator": 'This skill should be used when producing UML diagrams for documentation, architecture design, system modeling, or code-structure explanation. Trigger phrases: "draw a class diagram", "sequence diagram for this flow", "component diagram", "ER diagram", "activity diagram", "state machine diagram". Routes requests to the `uml` MCP server (antoinebou12/uml-mcp) and selects the diagram type automatically: class for structure, sequence for interactions, component for architecture, activity for behaviour, ER for data models. Saves rendered SVG/PNG and PlantUML source side-by-side under `docs/diagrams/`. Forbids inline PlantUML/Mermaid in surrounding `.md` — the artefact must be rendered.',

    "angular-expert": 'This skill should be used when the user works on Angular 17+ code — writing or reviewing components, applying the smart/dumb split, configuring OnPush, integrating RxJS observables in templates, building Reactive Forms, setting up lazy-loaded routes, or refactoring an Angular module. Trigger phrases: "Angular component", "OnPush", "standalone component", "reactive form", "lazy module", "Angular FE refactoring". Do not use for state-management tasks specifically (use ngrx-expert) or pure RxJS pipelines (use rxjs-expert).',

    "ngrx-expert": 'This skill should be used when the user designs, reviews, or refactors NgRx state management — store design, event-driven actions, pure reducers, memoised selectors, effects, facade pattern, state normalisation. Also use when deciding whether NgRx is the right choice or a simpler alternative (signals, services) is enough. Trigger phrases: "NgRx store", "add an action", "reducer", "memoised selector", "effect", "should I use NgRx". Do not use for general Angular component patterns (use angular-expert).',

    "rxjs-expert": 'This skill should be used when working with RxJS in an Angular project — naming conventions, flattening strategies (switchMap/mergeMap/concatMap/exhaustMap), subscription management, memory safety, stream combination, error handling, pipeline clarity, elimination of anti-patterns (nested subscribes, manual unsubscribe leaks). Trigger phrases: "switchMap vs mergeMap", "unsubscribe properly", "combine these observables", "RxJS pipeline", "Subject vs BehaviorSubject". Do not use for component design (use angular-expert) or NgRx effects (use ngrx-expert).',

    "css-expert": 'This skill should be used when writing, refactoring, or reviewing CSS/SCSS — design tokens, BEM naming, specificity rules, modularity, mobile-first responsive design, theming, layout patterns. Trigger phrases: "refactor this SCSS", "BEM naming", "design tokens", "specificity issue", "eliminate inline styles", "responsive layout". Do not use for component design (use design-expert) or framework-specific styling (Angular, React, Vue have their own skills).',

    "design-expert": 'This skill should be used when designing layouts, mockups, or style specifications BEFORE implementing a new frontend component. Trigger phrases: "design this component", "mockup for this view", "style spec", "layout for this page", "before I implement, what should it look like". Applies the company design system and coordinates with the framework skill (angular-expert / react-expert / vue-expert / qwik-expert / vanilla-expert) and css-expert. Do not use during implementation — invoke before.',

    "qwik-expert": 'This skill should be used when working on a Qwik or Qwik City app — resumability, lazy components, signals, server-side loaders/actions, file-based routing, Qwik-specific performance patterns. Trigger phrases: "Qwik component", "resumability", "Qwik signals", "route loader", "minimum TTI". Use when extreme performance and minimum Time To Interactive are required. Do not use for general React or Angular FE work (use react-expert or angular-expert).',

    "nextjs": 'This skill should be used when working with Next.js 14+ App Router — React Server Components, Server Actions, file-based routing, metadata API, multi-level caching, deployment patterns. Trigger phrases: "Next.js app router", "Server Component", "Server Action", "generateMetadata", "app/ directory", "Next.js caching". Does NOT cover the legacy Pages Router. Do not use for plain React (use react-expert) or for full-stack outside the Next ecosystem (use tanstack-start).',

    "react-expert": 'This skill should be used when working with React 18+ — component architecture, hooks, TypeScript prop typing, performance optimisation (memo/useCallback/useMemo), Suspense, concurrent features, React Testing Library. Trigger phrases: "React component", "custom hook", "memo this", "TypeScript props", "Suspense boundary", "RTL test". For data fetching use tanstack-query, for routing use tanstack, for SSR/Next ecosystem use nextjs. Do not use for plain Vanilla JS (use vanilla-expert).',

    "tanstack-query": 'This skill should be used when working with TanStack Query v5 in a React app — useQuery, useMutation, useInfiniteQuery, QueryClient configuration, cache invalidation, optimistic updates, prefetching. Trigger phrases: "useQuery", "useMutation", "invalidateQueries", "optimistic update", "prefetch a query", "replace useEffect with TanStack Query". Replaces useEffect for server state management. Do not use for client-only state or for routing (use tanstack).',

    "tanstack-start": 'This skill should be used when building a full-stack React application with TanStack Start — SSR, Server Functions, streaming, file-based routing, end-to-end type safety. Trigger phrases: "TanStack Start", "Server Functions", "full-stack React without Next", "streaming SSR". Use for new full-stack React apps that do not require the Next.js ecosystem. Do not use for Next.js projects (use nextjs) or pure client-side React (use react-expert).',

    "tanstack": 'This skill should be used when adding type-safe routing to a React app with TanStack Router — file-based routes, route definitions, loaders, search params, lazy routes, per-route error boundaries. Trigger phrases: "TanStack Router", "type-safe routing", "route loader", "search params", "replace React Router". Type-safe alternative to React Router. Do not use for Next.js (which has its own router) or Remix-style data loading.',

    "unicredit-design-system": 'ALWAYS use this skill when the project end client is UniCredit (UC banking group, including UniCredit Bank Italy/Germany/Austria/CEE). Trigger phrases: "UniCredit", "UCB", "Bricks design system", any UC product or app. Provides UniCredit brand identity rules (logo, colors, typography), the Bricks design-system component catalogue, accessibility targets (EN 301 549 / WCAG 2.1 AA), tone of voice, and ready-to-use design tokens for HTML/CSS/SCSS. Loaded automatically by the frontend-developer agent (Angular, React, Vue, Qwik, Vanilla). Do not use for non-UniCredit projects (use design-expert + accenture-branding for Accenture deliverables).',

    "vanilla-expert": 'This skill should be used when building independent widgets, reusable libraries, or projects where a framework would be overkill — Web Components, ES Modules, modern DOM APIs, Custom Events, Intersection/MutationObserver, strict TypeScript, Vite bundling. Trigger phrases: "Web Component", "no framework", "lightweight widget", "pure TypeScript DOM". Do not use for full Angular/React/Vue/Qwik apps.',

    "vue-expert": 'This skill should be used when working with Vue 3 Composition API — components, composables, Pinia state management, Vue Router 4, TypeScript patterns, performance optimisation, testing with Vitest and Vue Test Utils. Trigger phrases: "Vue 3 component", "composable", "Pinia store", "Vue Router", "Vitest test". Does NOT cover Vue 2 or the Options API. Do not use for React (use react-expert) or Nuxt-specific concerns.',

    "backend-orchestrator": 'ALWAYS use this skill when a backend task spans more than one Java/Spring layer — the user asks to add a new endpoint end-to-end, design a module from Controller to DB, refactor an existing feature across Service/Repository/Entity, or resolve cross-layer inconsistencies. Trigger phrases: "add a new endpoint end-to-end", "wire a service", "from controller to database", "full backend feature", "design this module Controller to DB". Coordinates java-expert, spring-expert, spring-data-jpa, spring-architecture, postgresql-expert, and guarantees cross-layer consistency. Do not use for single-layer tasks (use the targeted skill directly).',

    "frontend-orchestrator": 'ALWAYS use this skill when a frontend task spans multiple concerns — the user asks to design a feature mixing routing, state management, styling, and API calls; the framework is undecided; or the request explicitly asks for cross-skill coordination. Trigger phrases: "design a feature end-to-end", "review the architecture of this FE module", "plan the FE for X", "NgRx + RxJS + design system together". Coordinates Angular, NgRx, RxJS, React, Vue, Qwik, CSS/SCSS, Design, FE Refactoring skills. Do not use for single-framework, single-concern tasks (use the targeted skill directly).',

    "python-expert": 'This skill should be used when writing, reviewing, or refactoring Python code outside Streamlit — mandatory type hints, project structure, Pydantic v2, pytest, structlog, dependency management with uv or pip-tools. Trigger phrases: "Python type hints", "Pydantic model", "pytest test", "FastAPI endpoint", "structlog setup", "uv install". Covers FastAPI services, CLIs, data pipelines, scripts. Do not use for Streamlit apps (use streamlit-expert).',

    "streamlit-expert": 'This skill should be used when developing or maintaining a Streamlit web app — page structure, session_state management, caching (`@st.cache_data`, `@st.cache_resource`), reusable components, PostgreSQL/API integration, Streamlit-specific anti-patterns. Trigger phrases: "Streamlit page", "session_state", "st.cache", "multipage Streamlit", "Streamlit form", "st.experimental_rerun". Do not use for pure Python logic outside the UI (use python-expert) or for non-Streamlit web frameworks.',

    "dependency-resolver": 'This skill should be used when a dependency conflict blocks progress — the user reports `NoSuchMethodError`, "works locally fails in CI", incompatible peer deps, "2.x conflicts with 1.x", or a major-version bump that broke the build. Trigger phrases: "NoSuchMethodError", "incompatible peer deps", "X conflicts with Y", "after upgrading Z it broke", "transitive dependency conflict", "deprecated API". Investigates incompatible library versions, breaking changes, missing/outdated docs, transitive conflicts, and deprecated APIs. Support skill — do not use for routine version updates with no conflict.',

    "refactoring-expert": 'This skill should be used when refactoring code in any language to improve internal structure without changing behaviour. Trigger phrases: "refactor this", "clean this up", "improve the design", "extract method/class", "reduce coupling", "apply SOLID", "too long, too complex". Applies SOLID, DRY, KISS, YAGNI, Separation of Concerns, high cohesion / low coupling, testability, readability. Do not use to add new features or fix bugs (use the language developer skill or debugger).',

    "browser-automation": 'This skill should be used when controlling a real browser — navigating pages, taking screenshots, clicking elements, filling forms, switching tabs, emitting keyboard/mouse events, evaluating JavaScript, or running E2E tests via Playwright. Trigger phrases: "open this page", "screenshot of", "click this button", "fill the form", "evaluate JS in the page", "run an E2E test". Delegates all browser interactions to the `browser` MCP server (`@playwright/mcp`). Stops and asks the user to register the server if `.mcp.json` is missing the `browser` entry. Do not use for unit tests or non-browser automation.',

    "testing-standards": 'This skill should be used when an agent (test-writer, developer, code-reviewer) needs the canonical testing standards: principles, scenario taxonomy, naming conventions, Arrange-Act-Assert structure, framework templates for JUnit 5 + Mockito (Java), pytest (Python), Jest (TypeScript). Trigger phrases: "testing standards", "how should I structure these tests", "AAA pattern", "JUnit template", "pytest fixture conventions". Returns reference material and complete test templates, not generated test code. Do not trigger directly from a coding prompt — invoked by the agents above.',

    "caveman-commit": 'This skill should be used when the user asks for a commit message — triggers include "write a commit", "commit message for this", "conventional commit", "cc:". Produces a terse, intent-focused Conventional Commits subject line (max 72 chars) with a body only when reasoning is non-obvious. No emojis, no AI credits. Outputs message text in a code block only — does not run git. Do not use for PR review comments (use caveman-review) or general terse output (use caveman).',

    "caveman-review": 'This skill should be used when the user asks for code-review comments or PR review — triggers include "review this PR", "review the diff", "comments for this change", "PR feedback". Each comment follows the format `L<line>: <severity> <problem>. <fix>.`. No hedging, no code repetition, no motivational asides. Produces comments ready to paste into a PR. Do not use for commit messages (use caveman-commit) or general terse output (use caveman).',

    "caveman": 'This skill should be used when the user asks for terser, more direct output — explicit triggers include "caveman mode", "caveman lite|full|ultra", "be terse", "cut the fluff", "token-efficient". Activates token-efficient communication mode (~75% token reduction). Switches responses to compressed prose with articles, fillers, hedging, and pleasantries removed; preserves exact technical terminology and code unchanged. Do not use for commit messages (use caveman-commit) or PR comments (use caveman-review).',
}


def yaml_escape(s: str) -> str:
    """Escape a string for use as a YAML double-quoted scalar."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def rewrite_skill(path: Path) -> tuple[bool, str]:
    text = path.read_text(encoding="utf-8")
    # Extract name from frontmatter
    m = re.search(r"^name:\s*(\S+)\s*$", text, re.MULTILINE)
    if not m:
        return False, f"no name field"
    name = m.group(1)
    if name not in NEW_DESC:
        return False, f"no new description for {name}"

    new_desc = NEW_DESC[name]
    new_line = f'description: "{yaml_escape(new_desc)}"'

    # Match the description field: either single-line (`description: "..."` or `description: ...`)
    # or multi-line block scalar (`description: >` followed by indented lines until next top-level key).
    # Replace it with the new single-line form.
    pattern = re.compile(
        r"^description:\s*(?:>\s*\n(?:[ \t]+[^\n]*\n)+|[^\n]*\n)",
        re.MULTILINE,
    )
    new_text, n = pattern.subn(new_line + "\n", text, count=1)
    if n != 1:
        return False, "description block not matched"

    if new_text == text:
        return False, "no change"

    path.write_text(new_text, encoding="utf-8")
    return True, "ok"


def main() -> None:
    paths = sorted(ROOT.rglob("*.md"))
    print(f"Found {len(paths)} skill files")
    ok, skipped = 0, []
    for p in paths:
        success, reason = rewrite_skill(p)
        if success:
            ok += 1
            print(f"  ✓ {p.relative_to(ROOT)}")
        else:
            skipped.append((p, reason))
            print(f"  ✗ {p.relative_to(ROOT)} — {reason}")
    print(f"\nDone: {ok}/{len(paths)} rewritten, {len(skipped)} skipped")
    if skipped:
        print("Skipped:")
        for p, r in skipped:
            print(f"  - {p}: {r}")


if __name__ == "__main__":
    main()
