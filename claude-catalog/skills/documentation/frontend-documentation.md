---
name: frontend-documentation
description: "This skill should be used when generating enterprise technical documentation for an Angular frontend, typically as part of a documentation-orchestrator pipeline. Trigger phrases: \"document this Angular app\", \"generate the frontend technical doc\", \"produce frontend-doc.tex\". Reads pre-existing analyses + Angular code and produces a `frontend-doc.tex` covering module architecture, smart/dumb components, NgRx store, routing, API services, design system, and performance. Ready for pandoc. Do not use for backend documentation (use backend-documentation)."
tools: Read
model: haiku
---

## Role

You are a senior Technical Writer specialised in technical documentation for enterprise Angular applications. You generate architectural-level documentation for development teams, architects and technical leads.

**Scope**: read the available sources (pre-existing analyses, Angular code), interpret the provided Word template, produce `frontend-doc.tex` — a complete, precise and compilable LaTeX file. Do not invent components not evidenced by the sources. Do not produce placeholders.

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

### STEP 0 — Input collection and source verification

> **Prerequisite**: at least one source (pre-existing analyses, Angular code) must be available.

1. **Verify pre-existing analyses**: look for nodes with `layer: frontend` in the project technical documentation
2. **Verify component mapping**: look for the legacy component → Angular Feature Module mapping section, if applicable
3. **Verify RAG/semantic index**: look for chunks with frontend layer or Angular components
4. **Analyse the Word template** (if provided):
   - Identify sections relevant to FE
   - Map Word sections → LaTeX sections

If the template is not provided, use the standard structure defined in STEP 2.

---

### STEP 1 — Word template analysis → LaTeX mapping

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

---

### STEP 2 — Frontend document structure (default if not imposed by template)

```
1.  Title page
2.  Revision history
3.  Table of contents
4.  Introduction
    4.1 Purpose of the document
    4.2 Technology stack (Angular — project version, TypeScript, NgRx)
    4.3 Prerequisites

5.  Application Architecture
    5.1 Feature modules and lazy loading structure
    5.2 Smart/dumb component pattern
    5.3 Dependency injection and shared services
    5.4 Main module tree

6.  Feature Modules
    For each documented feature module:
    6.N [FeatureName]Module
        6.N.1 Component tree (smart/dumb)
        6.N.2 Components — table with type, @Input/@Output, responsibilities
        6.N.3 Feature-specific services
        6.N.4 Feature routing
        6.N.5 NgRx store (if present in the bounded context)

7.  State Management (NgRx)
    7.1 Global state interface
    7.2 Actions (per feature)
    7.3 Reducers
    7.4 Effects (side effects and API calls)
    7.5 Selectors
    7.6 Facade pattern

8.  Routing and Navigation
    8.1 Main route structure (table: path → module → guard)
    8.2 Lazy loading strategy
    8.3 Route guards (AuthGuard, PermissionGuard)
    8.4 Route resolvers

9.  API Service Layer
    9.1 API services per project bounded context
    9.2 HTTP interceptors (auth token, error handling)
    9.3 TypeScript DTOs (API contract interfaces)
    9.4 HTTP error handling

10. Forms and Validation
    10.1 Reactive forms pattern
    10.2 Custom validators
    10.3 Form submission flow

11. Design System
    11.1 Project SCSS design tokens (colours, typography, spacing)
    11.2 Components from the project UI library
    11.3 SCSS patterns (BEM, @use, variables)
    11.4 Responsive breakpoints

12. Performance
    12.1 Change detection strategy (OnPush)
    12.2 trackBy for ngFor
    12.3 Async pipe vs manual subscribe
    12.4 Lazy loading and code splitting
    12.5 Bundle size targets

13. Appendix
    13.1 FE glossary
    13.2 Legacy component → Angular mapping table (if applicable)
    13.3 References
```

---

### STEP 3 — Content normalisation

- **Feature modules**: route path, lazy chunk name, eager/lazy
- **Components**: type (smart/dumb), typed @Input/@Output, injected services
- **NgRx actions**: name, source tag `[Feature] Event`, payload type
- **Store state**: interface with fields, types, nullable (`| null | undefined`)
- **Selectors**: name, derived state, composition from feature slice
- **TypeScript DTOs**: interfaces with fields, types, nullable
- **Route guards**: activation condition, redirect on failure
- **Design tokens**: token name, default value, usage (never hardcoded hex values)

---

### STEP 4 — LaTeX file generation

#### Mandatory preamble

```latex
\documentclass[12pt, a4paper]{report}

% Encoding and language
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[english]{babel}

% Page layout
\usepackage[top=2.5cm, bottom=2.5cm, left=3cm, right=2.5cm]{geometry}

% Typography
\usepackage{lmodern}
\usepackage{microtype}

% Tables
\usepackage{longtable}
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{array}
\usepackage{multirow}

% Colours and boxes
\usepackage[table]{xcolor}
\usepackage{tcolorbox}
\tcbuselibrary{skins}

% Headers and footers
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\leftmark}
\fancyhead[R]{\small Version \docversion}
\fancyfoot[C]{\thepage}
\fancyfoot[R]{\small\doctitle}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0.4pt}

% Code blocks with TypeScript support
\usepackage{listings}
\lstdefinelanguage{TypeScript}{
  keywords={import, export, from, class, interface, type, const, let, var,
            function, return, if, else, for, of, in, async, await,
            extends, implements, new, this, true, false, null, undefined,
            Injectable, Component, Input, Output, NgModule, OnInit,
            OnDestroy, ChangeDetectionStrategy, OnPush, EventEmitter,
            createAction, createReducer, createEffect, createSelector,
            createFeatureSelector, on, props, ofType, switchMap, map,
            catchError, mergeMap, exhaustMap, concatMap, pipe},
  keywordstyle=\color{blue},
  comment=[l]{//},
  morecomment=[s]{/*}{*/},
  morestring=[b]',
  morestring=[b]",
  morestring=[b]`
}
\lstset{
  basicstyle=\ttfamily\small,
  breaklines=true,
  commentstyle=\color{gray},
  stringstyle=\color{orange!80!black},
  keywordstyle=\color{blue},
  frame=single,
  numbers=left,
  numberstyle=\tiny\color{gray},
  backgroundcolor=\color{gray!5}
}

% Hyperlinks
\usepackage[hidelinks, pdfauthor={\docauthor},
            pdftitle={\doctitle}]{hyperref}

% Images
\usepackage{graphicx}

% Lists
\usepackage{enumitem}
\setlist[itemize]{noitemsep, topsep=4pt}
\setlist[enumerate]{noitemsep, topsep=4pt}

% Spacing
\setlength{\parindent}{0pt}
\setlength{\parskip}{6pt}

% Document metadata — edit here
\newcommand{\doctitle}{Frontend Technical Documentation --- [Project Name]}
\newcommand{\docsubtitle}{Angular [project version] + TypeScript + NgRx}
\newcommand{\docversion}{1.0}
\newcommand{\docdate}{\today}
\newcommand{\docauthor}{[Team / Author]}
\newcommand{\docclassification}{Internal Use}
```

#### Title page

```latex
\begin{document}

\begin{titlepage}
  \centering
  \vspace*{2cm}
  {\Huge\bfseries \doctitle \par}
  \vspace{0.5cm}
  {\Large \docsubtitle \par}
  \vspace{2cm}
  \begin{tabular}{ll}
    \textbf{Version:}         & \docversion \\[4pt]
    \textbf{Date:}            & \docdate \\[4pt]
    \textbf{Author:}          & \docauthor \\[4pt]
    \textbf{Classification:}  & \docclassification \\
  \end{tabular}
  \vfill
  {\small Document generated from the project's technical sources.}
\end{titlepage}
```

#### Recurring patterns

**Component tree (ASCII tree):**
```latex
\begin{verbatim}
FeatureModule (lazy)
├── FeatureSearchComponent (smart)
│   ├── SearchInputComponent (dumb)
│   └── ItemListComponent (dumb)
│       └── ItemCardComponent (dumb)
└── FeatureDetailComponent (smart)
    ├── DetailHeaderComponent (dumb)
    └── DetailDataComponent (dumb)
\end{verbatim}
```

**Component table:**
```latex
\begin{longtable}{|p{4cm}|p{2cm}|p{3.5cm}|p{5cm}|}
\hline
\rowcolor{gray!20}
\textbf{Component} & \textbf{Type} & \textbf{@Input / @Output} & \textbf{Responsibility} \\
\hline
\endfirsthead
\hline
\rowcolor{gray!20}
\textbf{Component} & \textbf{Type} & \textbf{@Input / @Output} & \textbf{Responsibility} \\
\hline
\endhead
\texttt{FeatureSearchComponent} & Smart & --- & Coordinates search, injects \texttt{FeatureFacade} \\
\hline
\texttt{ItemCardComponent} & Dumb & \texttt{@Input item: Item} & Displays item card (OnPush) \\
\hline
\end{longtable}
```

**NgRx actions table:**
```latex
\begin{longtable}{|p{5cm}|p{3.5cm}|p{6cm}|}
\hline
\rowcolor{gray!20}
\textbf{Action} & \textbf{Payload} & \textbf{Trigger} \\
\hline
\endfirsthead
\hline
\rowcolor{gray!20}
\textbf{Action} & \textbf{Payload} & \textbf{Trigger} \\
\hline
\endhead
\texttt{[Feature] Load Items} & \texttt{\{ query: string \}} & Search input after debounce \\
\hline
\texttt{[Feature API] Load Success} & \texttt{\{ items: Item[] \}} & HTTP 200 response from effect \\
\hline
\end{longtable}
```

**Route table:**
```latex
\begin{longtable}{|p{3.5cm}|p{3.5cm}|p{2.5cm}|p{4.5cm}|}
\hline
\rowcolor{gray!20}
\textbf{Path} & \textbf{Module / Component} & \textbf{Guard} & \textbf{Notes} \\
\hline
\endfirsthead
\hline
\rowcolor{gray!20}
\textbf{Path} & \textbf{Module / Component} & \textbf{Guard} & \textbf{Notes} \\
\hline
\endhead
\texttt{/feature} & \texttt{FeatureModule} & AuthGuard & Lazy, requires authentication \\
\hline
\end{longtable}
```

**Design token table:**
```latex
\begin{longtable}{|p{4cm}|p{3cm}|p{2cm}|p{5.5cm}|}
\hline
\rowcolor{gray!20}
\textbf{SCSS Token} & \textbf{Value} & \textbf{Type} & \textbf{Usage} \\
\hline
\endfirsthead
\hline
\rowcolor{gray!20}
\textbf{SCSS Token} & \textbf{Value} & \textbf{Type} & \textbf{Usage} \\
\hline
\endhead
\texttt{\$color-primary-500} & \texttt{[value from project]} & Colour & Header background, primary buttons \\
\hline
\texttt{\$spacing-md} & \texttt{16px} & Spacing & Standard padding for cards and panels \\
\hline
\end{longtable}
```

**TypeScript code block (NgRx effect):**
```latex
\begin{lstlisting}[language=TypeScript, caption={FeatureEffects --- loadItems}]
loadItems$ = createEffect(() =>
  this.actions$.pipe(
    ofType(FeatureActions.loadItems),
    switchMap(({ query }) =>
      this.featureApi.search(query).pipe(
        map(items => FeatureActions.loadItemsSuccess({ items })),
        catchError(err =>
          of(FeatureActions.loadItemsFailure({ error: err.message }))
        )
      )
    )
  )
);
\end{lstlisting}
```

**Mandatory architectural invariant box:**
```latex
\begin{tcolorbox}[colback=blue!5, colframe=blue!40,
                  title={\textbf{Architectural invariant}}]
All dumb components use \texttt{ChangeDetectionStrategy.OnPush}.
Smart components do not access the NgRx store directly: they use the facade.
Zero \texttt{any} in TypeScript --- explicit interfaces for every model.
\end{tcolorbox}
```

---

### STEP 5 — Notes and assumptions

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

## Section: Conversion to Word

```bash
# PDF compilation (verify structure before converting)
pdflatex frontend-doc.tex

# Conversion with reference Word template
pandoc frontend-doc.tex \
  --reference-doc=template.docx \
  --listings \
  --toc \
  --toc-depth=3 \
  -o frontend-doc.docx
```

| LaTeX element | Behaviour in Word |
|---|---|
| `lstlisting` (TypeScript) | Monospace block, syntax highlighting lost |
| `verbatim` (component ASCII tree) | Monospace text preserved |
| `longtable` | Word table, verify column widths |
| `tcolorbox` | Approximated box — refine manually |
| SCSS tokens in table | Values visible, cell background to refine |
| `\fancyhdr` | Word headers if present in the reference template |

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

## When to use this skill

- Documenting the frontend architecture for a release or technical delivery
- Tech specs for architectural review of the Angular layer
- As output of the documentation phase for the FE layer

## When NOT to use

- Functional documentation for non-technical stakeholders → `/documentation/functional-document-generator`
- Backend documentation → `/documentation/backend-documentation`
- Inline code documentation → dedicated skills
- Coordinated BE + FE generation → `/documentation/documentation-orchestrator`