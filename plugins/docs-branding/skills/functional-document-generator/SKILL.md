---
name: functional-document-generator
description: "This skill should be used when converting existing functional documentation into an enterprise LaTeX deliverable for stakeholders. Trigger phrases: \"generate the functional document\", \"produce the .docx for the client\", \"convert docs/functional to LaTeX\", \"Word-template-driven functional doc\". Reads from `docs/functional/`, interprets a provided Word template, and generates a complete `.tex` file ready for pandoc → `.docx`. Does not invent functionality not supported by the source content. Do not use to write the functional analysis itself (use functional-analyst)."
---

# Functional Document Generator

Convert existing functional documentation into an enterprise LaTeX deliverable, ready for conversion to `.docx`.

**Scope**: read the existing functional documentation in the project, interpret the provided Word template, produce a structured, professional and consistent `.tex` file, ready for conversion to `.docx`. Do not invent functionality not supported by the content. Do not produce placeholders or generic text.

---

## Mandatory process (in order)

### STEP 0: Input collection

> **Prerequisite**: `functional-analyst` must have completed the analysis and saved the files in the project's functional documentation folder (e.g. `docs/functional/` or equivalent). If the folder is absent or empty, first run `functional-analyst` with the scope set to the module to be documented. This generator cannot produce quality content from absent inputs.

Before producing any content:

1. **Read all available functional documentation files in the project**
   - `*-features.md` → feature list and actors
   - `*-userflows.md` → step-by-step user flows
   - `*-business-rules.md` → business rules (BR-N)
   - `*-usecases.md` → formal use cases (UC-N)
   - `*-dependencies.md` → functional dependencies between modules
   - `*-assumptions.md` → assumptions and open questions

2. **Analyse the Word template provided as input**
   - Identify: chapters, sections, subsections, order
   - Identify: recurring elements (tables, lists, notes, headers)
   - Identify: implicit style (formal, numbering, footer)

If the template is not provided, use the standard structure in [references/document-structure.md](references/document-structure.md).

---

### STEP 1: Word template mapping and document structure

Map Word elements onto LaTeX before writing a line of the document:

| Word element | LaTeX equivalent |
|---|---|
| Heading 1 (chapter) | `\section{}` |
| Heading 2 (section) | `\subsection{}` |
| Heading 3 (subsection) | `\subsubsection{}` |
| Word table | `\begin{longtable}` (for multi-page tables) or `tabular` |
| Bulleted list | `\begin{itemize}` |
| Numbered list | `\begin{enumerate}` |
| Bold text | `\textbf{}` |
| Italic text | `\textit{}` |
| Note / box | `\begin{tcolorbox}` (with tcolorbox package) |
| Document header | `\fancyhead` (fancyhdr package) |
| Footer | `\fancyfoot` |
| Title page | `\begin{titlepage}` |
| Index | `\tableofcontents` |

Then fix the document structure. Where the Word template does not impose one, use this default top-level layout:

```
1. Title page (title, version, date, author, classification)
2. Revision history (version, date, author, change description)
3. Table of contents
4. Introduction (purpose, scope of application, intended audience)
5. Glossary and Definitions
6. Context and General Description (business context, objectives, functional architecture)
7. System Actors (actor, type, description, responsibilities)
8. Functional Requirements, one subsection per module, IDs `RF-XXX`
9. Main Flows (pre-conditions, steps, post-conditions, alternatives)
10. Use Cases, IDs `UC-XXX`
11. Business Rules, IDs `BR-XXX`
12. Constraints and Limitations (functional, technical, regulatory)
13. Functional Dependencies Between Modules
14. Assumptions and Open Questions
15. Appendix (references to related documents, additional notes)
```

- **Standard chapter and section schema**: see [references/document-structure.md](references/document-structure.md)
- **Element mapping table, mandatory preamble, title page, revision history and recurring table patterns**: see [references/latex-templates.md](references/latex-templates.md)

---

### STEP 2: Content normalisation

Before writing LaTeX, process the content from the project's functional documentation:

- **Functional requirements**: assign progressive IDs (RF-001, RF-002, …)
- **Business rules**: preserve existing BR-N IDs, assign new ones only if missing
- **Use cases**: preserve existing UC-N IDs
- **Flows**: structure step-by-step with numbering
- **Actors**: deduplicate and classify (End user / System / Administrator / External)
- **Terminology**: normalise by choosing one term per concept and using it consistently
- **Incomplete content**: complete with reasonable assumptions, documented in STEP 3

---

### STEP 3: Notes and assumptions

After the LaTeX file, report:

```
## Assumptions made

- [Assumption 1]: [Rationale]
- [Assumption 2]: [Rationale]

## Inferred or completed parts

- [Section X]: completed with [source/logic used]

## Open questions to validate with stakeholders

- [Question 1]
- [Question 2]
```

---

## Conversion to Word

Convert with pandoc, passing `--reference-doc` to keep the client's Word style. Custom `tcolorbox` styling, `\rowcolor` backgrounds and fine column widths do not survive the conversion intact and are refined in Word afterwards.

Commands, reference-template handling, known limitations and the recommended workflow: see [references/pandoc-conversion.md](references/pandoc-conversion.md).

---

## Mandatory writing rules

| Rule | Detail |
|---|---|
| Language | Formal, documentary, third person |
| Sentences | Short, direct, unambiguous |
| Terminology | Consistent throughout the document: one term = one concept |
| Placeholders | Never: no "TODO", "to be completed", "insert here" |
| Inventions | Never functionality not supported by the content read |
| Gaps | If information is missing: reasonable assumption + assumption box |
| Duplications | No repetition between different sections |
| Completeness | Every section must be balanced and concluded |

---

## Final output checklist

- [ ] LaTeX file compilable (no syntax errors)
- [ ] Structure consistent with the provided Word template (or standard structure if absent)
- [ ] All content from the project's functional documentation used and organised
- [ ] Tables with headers, alternating colours, defined borders
- [ ] Functional requirements with progressive IDs (RF-XXX)
- [ ] Business rules with IDs (BR-XXX)
- [ ] Use cases with IDs (UC-XXX)
- [ ] Flows structured with pre/post-conditions and alternatives
- [ ] No placeholders or TODOs
- [ ] Notes and assumptions documented at the end
- [ ] Pandoc instructions included for conversion to .docx

---

## Detailed references

- **Standard functional document structure, chapter by chapter**: see [references/document-structure.md](references/document-structure.md)
- **Word-to-LaTeX mapping, preamble, title page, revision history and table patterns**: see [references/latex-templates.md](references/latex-templates.md)
- **Pandoc commands, reference template, limitations and workflow**: see [references/pandoc-conversion.md](references/pandoc-conversion.md)
