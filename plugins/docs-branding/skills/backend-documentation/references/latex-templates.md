# LaTeX templates for backend-doc.tex

The mandatory preamble, the title page and the recurring table and box
patterns used throughout the backend document.

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

% Code blocks
\usepackage{listings}
\lstset{
  basicstyle=\ttfamily\small,
  breaklines=true,
  keywordstyle=\color{blue},
  commentstyle=\color{gray},
  stringstyle=\color{orange!80!black},
  frame=single,
  numbers=left,
  numberstyle=\tiny\color{gray},
  backgroundcolor=\color{gray!5}
}

% Hyperlinks and PDF metadata
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
\newcommand{\doctitle}{Backend Technical Documentation --- [Project Name]}
\newcommand{\docsubtitle}{[Technology stack, e.g. Java 17 + Spring Boot 3.x + PostgreSQL]}
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

**Endpoint table:**
```latex
\begin{longtable}{|p{2cm}|p{5cm}|p{2.5cm}|p{4cm}|}
\hline
\rowcolor{gray!20}
\textbf{Method} & \textbf{Path} & \textbf{Auth} & \textbf{Description} \\
\hline
\endfirsthead
\hline
\rowcolor{gray!20}
\textbf{Method} & \textbf{Path} & \textbf{Auth} & \textbf{Description} \\
\hline
\endhead
\texttt{GET} & \texttt{/api/entities/\{id\}} & Bearer JWT & Retrieves entity detail by ID \\
\hline
\end{longtable}
```

**DTO table:**
```latex
\begin{longtable}{|p{3.5cm}|p{2.5cm}|p{1.5cm}|p{6cm}|}
\hline
\rowcolor{gray!20}
\textbf{Field} & \textbf{Type} & \textbf{Req.} & \textbf{Description / Validation} \\
\hline
\endfirsthead
\hline
\rowcolor{gray!20}
\textbf{Field} & \textbf{Type} & \textbf{Req.} & \textbf{Description / Validation} \\
\hline
\endhead
\texttt{entityId} & \texttt{String} & \checkmark & Unique identifier, \texttt{@NotBlank} \\
\hline
\end{longtable}
```

**JPA entity table:**
```latex
\begin{longtable}{|p{3cm}|p{2.5cm}|p{2cm}|p{6cm}|}
\hline
\rowcolor{gray!20}
\textbf{Field} & \textbf{Java Type} & \textbf{SQL Type} & \textbf{Constraints / Notes} \\
\hline
\endfirsthead
\hline
\rowcolor{gray!20}
\textbf{Field} & \textbf{Java Type} & \textbf{SQL Type} & \textbf{Constraints / Notes} \\
\hline
\endhead
\texttt{id} & \texttt{Long} & \texttt{BIGSERIAL} & PK, auto-generated \\
\hline
\end{longtable}
```

**HTTP error table:**
```latex
\begin{longtable}{|p{3.5cm}|p{1.8cm}|p{3cm}|p{5.5cm}|}
\hline
\rowcolor{gray!20}
\textbf{Exception} & \textbf{HTTP} & \textbf{App code} & \textbf{Cause} \\
\hline
\endfirsthead
\hline
\rowcolor{gray!20}
\textbf{Exception} & \textbf{HTTP} & \textbf{App code} & \textbf{Cause} \\
\hline
\endhead
\texttt{EntityNotFoundException} & 404 & \texttt{ENTITY\_NOT\_FOUND} & Entity not found for the provided ID \\
\hline
\texttt{BusinessRuleViolationException} & 422 & \texttt{BR\_VIOLATION} & Business rule violation \\
\hline
\end{longtable}
```

**Java code block:**
```latex
\begin{lstlisting}[language=Java, caption={EntityController --- entity search}]
@GetMapping("/search")
public ResponseEntity<Page<EntityDto>> search(
    @RequestParam String query,
    @RequestParam(defaultValue = "0") int page,
    @RequestParam(defaultValue = "20") int size) {
    return ResponseEntity.ok(
        entityService.search(query, PageRequest.of(page, size))
    );
}
\end{lstlisting}
```

**Known architectural issue box:**
```latex
\begin{tcolorbox}[colback=red!5, colframe=red!50,
                  title={\textbf{Known architectural issue}}]
\textbf{Issue description}: brief explanation of the identified issue.
Status: [under analysis / being migrated / resolved].
Reference: [project technical documentation].
\end{tcolorbox}
```

**Note box:**
```latex
\begin{tcolorbox}[colback=yellow!10, colframe=orange!70, title={\textbf{Note}}]
Text of the note or warning.
\end{tcolorbox}
```

---

