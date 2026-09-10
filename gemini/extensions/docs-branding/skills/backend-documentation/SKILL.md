---
name: backend-documentation
description: "This skill should be used when generating enterprise technical documentation for a Java/Spring Boot backend, typically as part of a documentation-orchestrator pipeline: documenting the backend architecture for a release or technical delivery, or producing tech specs for architectural review. Trigger phrases: \"document this backend\", \"generate the backend technical doc\", \"produce backend-doc.tex\". Reads pre-existing analyses + source code and produces a `backend-doc.tex` covering architecture, API reference, data model, business logic, security, and error handling. Output is ready for pandoc conversion. Do not use for frontend documentation (use frontend-documentation), for coordinated backend plus frontend generation (use documentation-orchestrator), for functional documentation aimed at non-technical stakeholders (use functional-document-generator), or for inline code documentation."
---

# Backend Documentation

Generate enterprise-level technical documentation for a Java/Spring Boot backend, addressed to development teams, architects and technical leads.

**Scope**: read the available sources (pre-existing analyses, source code), interpret the provided Word template, produce `backend-doc.tex`, a complete, precise, compilable LaTeX file convertible to `.docx`. Do not invent components not evidenced by the sources. Do not produce placeholders.

---

## Sources to consult (in order of priority)

| Source | Where to look | Content |
|---|---|---|
| Architectural nodes | project technical documentation (e.g. `docs/graph/nodes.md`) | Controllers, Services, Repositories, Entities with responsibilities |
| Migration/refactoring map | pre-existing analyses | Target Java classes, component mapping |
| Architectural issues | pre-existing analyses | Constraints and decisions already made |
| Dependencies | pre-existing analyses | CALLS, READS_FROM, WRITES_TO between layers |
| RAG chunks / semantic index | project technical documentation | Business rules, inputs, outputs per bounded context |
| Functional documentation | `docs/functional/` or equivalent | Business rules (BR-N), use cases (UC-N) |
| Execution paths | pre-existing analyses | End-to-end flows, call sequences |
| Bounded context | pre-existing analyses | The project's bounded contexts |

If the Spring Boot source code is accessible, read primarily:
- Controllers (`@RestController`) → endpoints, DTOs
- Services (`@Service`) → business methods
- Entities (`@Entity`) → fields, constraints, JPA relations
- `application.properties` / `application.yml` → configuration

---

## Mandatory process (in order)

### STEP 0: Input collection and source verification

> **Prerequisite**: at least one source (pre-existing analyses, source code) must be available. If no source is accessible, stop and request input.

1. **Verify pre-existing analyses**: look for nodes with `layer: backend` in the project technical documentation
2. **Verify RAG/semantic documentation**: look for chunks for the relevant bounded contexts
3. **Verify code**: look for `@RestController`, `@Service`, `@Entity` classes in the project
4. **Analyse the Word template** (if provided as input):
   - Identify chapters, sections, order
   - Map each section to available BE content
   - Determine which Word sections → LaTeX sections

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
| Code block | `\begin{lstlisting}[language=Java]` |
| Header/footer | `\fancyhead` / `\fancyfoot` |

Then fix the document structure. Where the Word template does not impose one, use this default top-level layout:

```
1. Title page
2. Revision history
3. Table of contents
4. Introduction (purpose, scope, technology stack, prerequisites)
5. System Architecture (layers, bounded context, datasource, package schema)
6. API Reference (base configuration, then one subsection per controller)
7. Data Model (relational schema, JPA entities, request/response DTOs)
8. Business Logic (one subsection per service, with the BR-N rules it applies)
9. Security Architecture (JWT authentication, authorisation, hashing, CORS/CSRF)
10. Error Handling and Logging (exception hierarchy, handler, MDC, monitoring)
11. External Integrations (one subsection per integration)
12. Configuration (Spring profiles, datasource, environment variables)
13. Appendix (glossary, known architectural issues, references)
```

- **Default chapter and section layout**: see [references/document-structure.md](references/document-structure.md)
- **Element mapping table, mandatory preamble, title page and recurring patterns**: see [references/latex-templates.md](references/latex-templates.md)

---

### STEP 2: Content normalisation

Before writing LaTeX:

- **Endpoints**: full URLs, HTTP method, standard response codes
- **DTOs**: field table with Java type, validations, nullable
- **Entities**: fields with SQL type + Java type, constraints (NOT NULL, UNIQUE, FK)
- **Business rules**: reference to existing BR-N from functional documentation; assign new IDs if missing
- **Errors**: HTTP status + application code + cause + remediation
- **Configuration**: `${ENV_VAR}` variables with type and default value

---

### STEP 3: Notes and assumptions

After the LaTeX file, report:

```
## Sources used

- [List of files read with path]

## Assumptions made

- [Assumption]: [Rationale]

## Undocumented components (absence of sources)

- [Component]: [Reason for exclusion]

## Open questions

- [Question]
```

---

## Conversion to Word

Compile with `pdflatex` to verify the structure before converting, then run pandoc with `--reference-doc=template.docx --listings --toc --toc-depth=3`. Syntax highlighting inside `lstlisting` is lost, `tcolorbox` borders are approximated, and `\rowcolor` backgrounds are not always preserved. Refine those manually.

Full command and the per-element behaviour table: see [references/pandoc-conversion.md](references/pandoc-conversion.md).

---

## Final output checklist

- [ ] LaTeX file compilable without errors
- [ ] Structure consistent with Word template (or standard schema)
- [ ] All Controllers documented with endpoint table
- [ ] All request/response DTOs documented with field table
- [ ] All Entities documented with fields, SQL type, JPA constraints
- [ ] Exception hierarchy with HTTP status mapping table
- [ ] Security section with JWT flow and roles
- [ ] `lstlisting` blocks for critical code examples
- [ ] Boxes for known architectural issues (if present in the project)
- [ ] No placeholders or TODOs
- [ ] Assumptions documented at the end
- [ ] Pandoc instructions included

---

## Detailed references

- **Default backend document structure, chapter by chapter**: see [references/document-structure.md](references/document-structure.md)
- **Word-to-LaTeX mapping, preamble, title page and recurring patterns**: see [references/latex-templates.md](references/latex-templates.md)
- **Pandoc command and LaTeX-to-Word element behaviour**: see [references/pandoc-conversion.md](references/pandoc-conversion.md)
