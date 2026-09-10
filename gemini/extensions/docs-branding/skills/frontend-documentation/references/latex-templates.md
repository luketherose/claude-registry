# LaTeX templates for frontend-doc.tex

The mandatory preamble, the title page and the recurring table and box
patterns used throughout the frontend document.

## Contents

- [LaTeX file generation](#latex-file-generation)
  - [Mandatory preamble](#mandatory-preamble)
  - [Title page](#title-page)
  - [Recurring patterns](#recurring-patterns)

## LaTeX file generation

### Mandatory preamble

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

### Title page

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

### Recurring patterns

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

