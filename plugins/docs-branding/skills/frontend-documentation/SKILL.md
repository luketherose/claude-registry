---
name: frontend-documentation
description: "This skill should be used when generating enterprise technical documentation for an Angular frontend, typically as part of a documentation-orchestrator pipeline: documenting the frontend architecture for a release or technical delivery, or producing tech specs for architectural review of the Angular layer. Trigger phrases: \"document this Angular app\", \"generate the frontend technical doc\", \"produce frontend-doc.tex\". Reads pre-existing analyses + Angular code and produces a `frontend-doc.tex` covering module architecture, smart/dumb components, NgRx store, routing, API services, design system, and performance. Ready for pandoc. Do not use for backend documentation (use backend-documentation), for coordinated backend plus frontend generation (use documentation-orchestrator), for functional documentation aimed at non-technical stakeholders (use functional-document-generator), or for inline code documentation."
---

# Frontend Documentation

Generate architectural-level technical documentation for an enterprise Angular application, addressed to development teams, architects and technical leads.

**Scope**: read the available sources (pre-existing analyses, Angular code), interpret the provided Word template, produce `frontend-doc.tex`, a complete, precise and compilable LaTeX file. Do not invent components not evidenced by the sources. Do not produce placeholders.

---

## Sources to consult (in order of priority)

| Source | Where to look | Content |
|---|---|---|
| Migration/component map | project technical documentation (e.g. `docs/graph/migration-map.md`) | Mapping legacy components → Angular Feature Module, if applicable |
| Architectural nodes | project technical documentation | Nodes with `layer: frontend`, `Migration_Target` field |
| Execution paths | project technical documentation | End-to-end user flows with Angular components |
| Dependencies | project technical documentation | DEPENDS_ON, NAVIGATES_TO between components |
| RAG chunks / semantic index | project technical documentation | Business rules for relevant bounded contexts |
| User flows | `docs/functional/*-userflows.md` or equivalent | Step-by-step user flows |
| Business rules | `docs/functional/*-business-rules.md` or equivalent | Rules that determine UI logic |

If the Angular source code is accessible, read primarily:
- Feature modules (`*.module.ts`) → lazy loading structure
- Smart components (`*-container.component.ts`) → injected services, store selectors
- NgRx store (`*.actions.ts`, `*.reducer.ts`, `*.effects.ts`, `*.selectors.ts`, `*.facade.ts`)
- Routing (`*.routing.ts`, `app-routing.module.ts`)
- API services (`*-api.service.ts`) → HTTP calls, DTO mapping
- `_tokens.scss` / `_variables.scss` → project SCSS design tokens

---

## Mandatory process (in order)

### STEP 0: Input collection and source verification

> **Prerequisite**: at least one source (pre-existing analyses, Angular code) must be available.

1. **Verify pre-existing analyses**: look for nodes with `layer: frontend` in the project technical documentation
2. **Verify component mapping**: look for the legacy component → Angular Feature Module mapping section, if applicable
3. **Verify RAG/semantic index**: look for chunks with frontend layer or Angular components
4. **Analyse the Word template** (if provided):
   - Identify sections relevant to FE
   - Map Word sections → LaTeX sections

If the template is not provided, use the default structure in [references/document-structure.md](references/document-structure.md).

---

### STEP 1: Word template mapping and document structure

Map Word elements onto LaTeX before writing a line of the document:

| Word element | LaTeX equivalent |
|---|---|
| Heading 1 (chapter) | `\section{}` |
| Heading 2 (section) | `\subsection{}` |
| Heading 3 (subsection) | `\subsubsection{}` |
| Word table | `\begin{longtable}` |
| Bulleted list | `\begin{itemize}` |
| Numbered list | `\begin{enumerate}` |
| Bold | `\textbf{}` |
| Italic | `\textit{}` |
| Note / box | `\begin{tcolorbox}` |
| Code block | `\begin{lstlisting}[language=TypeScript]` |
| Component tree diagram | `\begin{verbatim}` (ASCII tree) |

Then fix the document structure. Where the Word template does not impose one, use this default top-level layout:

```
1. Title page
2. Revision history
3. Table of contents
4. Introduction (purpose, technology stack, prerequisites)
5. Application Architecture (feature modules, smart/dumb split, DI, module tree)
6. Feature Modules (one subsection per module: component tree, components, services, routing, store)
7. State Management (NgRx state, actions, reducers, effects, selectors, facades)
8. Routing and Navigation (route table, lazy loading, guards, resolvers)
9. API Service Layer (services per bounded context, interceptors, DTOs, error handling)
10. Forms and Validation (reactive forms, custom validators, submission flow)
11. Design System (SCSS tokens, UI library components, BEM patterns, breakpoints)
12. Performance (OnPush, trackBy, async pipe, code splitting, bundle targets)
13. Appendix (glossary, legacy-to-Angular mapping, references)
```

- **Default chapter and section layout**: see [references/document-structure.md](references/document-structure.md)
- **Element mapping table, mandatory preamble, title page and recurring patterns**: see [references/latex-templates.md](references/latex-templates.md)

---

### STEP 2: Content normalisation

- **Feature modules**: route path, lazy chunk name, eager/lazy
- **Components**: type (smart/dumb), typed @Input/@Output, injected services
- **NgRx actions**: name, source tag `[Feature] Event`, payload type
- **Store state**: interface with fields, types, nullable (`| null | undefined`)
- **Selectors**: name, derived state, composition from feature slice
- **TypeScript DTOs**: interfaces with fields, types, nullable
- **Route guards**: activation condition, redirect on failure
- **Design tokens**: token name, default value, usage (never hardcoded hex values)

---

### STEP 3: Notes and assumptions

After the LaTeX file, report:

```
## Sources used

- [List of files read with path]

## Assumptions made

- [Assumption]: [Rationale]

## Undocumented feature modules (absence of sources)

- [Module]: [Reason for exclusion]

## Open questions

- [Question]
```

---

## Conversion to Word

Compile with `pdflatex` to verify the structure before converting, then run pandoc with the reference Word template. Syntax highlighting inside `lstlisting` is lost, `tcolorbox` borders are approximated, and SCSS token table backgrounds need refining by hand.

Full command and the per-element behaviour table: see [references/pandoc-conversion.md](references/pandoc-conversion.md).

---

## Final output checklist

- [ ] LaTeX file compilable without errors
- [ ] Structure consistent with Word template (or standard schema)
- [ ] Component tree (verbatim) for every feature module
- [ ] Component table with type, @Input/@Output, responsibility
- [ ] NgRx: actions tables, reducers (state interface), effects, selectors, facade
- [ ] Routing: complete table path → module → guard
- [ ] API services: TypeScript DTOs documented with interfaces
- [ ] Design tokens: table with values and usage
- [ ] Performance section: OnPush, trackBy, async pipe
- [ ] Zero `any` in TypeScript examples shown
- [ ] No placeholders or TODOs
- [ ] Assumptions documented at the end
- [ ] Pandoc instructions included

---

## Detailed references

- **Default frontend document structure, chapter by chapter**: see [references/document-structure.md](references/document-structure.md)
- **Word-to-LaTeX mapping, preamble, title page and recurring patterns**: see [references/latex-templates.md](references/latex-templates.md)
- **Pandoc command and LaTeX-to-Word element behaviour**: see [references/pandoc-conversion.md](references/pandoc-conversion.md)
