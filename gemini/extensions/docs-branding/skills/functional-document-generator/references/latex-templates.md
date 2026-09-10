# LaTeX templates for the functional document

The mandatory preamble, the title page, the revision history and the recurring
table patterns.

## Contents

- [LaTeX file generation](#latex-file-generation)
  - [Mandatory preamble](#mandatory-preamble)
  - [Title page](#title-page)
  - [Revision history](#revision-history)
  - [Patterns for recurring tables](#patterns-for-recurring-tables)

## LaTeX file generation

Produce the complete `.tex` file following these rules:

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

% Hyperlinks and PDF metadata
\usepackage[hidelinks, pdfauthor={\docauthor},
            pdftitle={\doctitle}]{hyperref}

% Images
\usepackage{graphicx}

% Lists
\usepackage{enumitem}
\setlist[itemize]{noitemsep, topsep=4pt}
\setlist[enumerate]{noitemsep, topsep=4pt}

% Paragraph spacing
\setlength{\parindent}{0pt}
\setlength{\parskip}{6pt}

% Document metadata — edit here
\newcommand{\doctitle}{[DOCUMENT TITLE]}
\newcommand{\docsubtitle}{[SUBTITLE / MODULE]}
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

  {\small Document automatically generated from the project's functional content.}
\end{titlepage}
```

### Revision history

```latex
\chapter*{Revision History}
\addcontentsline{toc}{chapter}{Revision History}

\begin{longtable}{|p{1.5cm}|p{2.5cm}|p{3cm}|p{7cm}|}
\hline
\rowcolor{gray!20}
\textbf{Ver.} & \textbf{Date} & \textbf{Author} & \textbf{Description} \\
\hline
\endfirsthead
\hline
\rowcolor{gray!20}
\textbf{Ver.} & \textbf{Date} & \textbf{Author} & \textbf{Description} \\
\hline
\endhead
1.0 & \docdate & \docauthor & First issue. \\
\hline
\end{longtable}
```

### Patterns for recurring tables

**Actors table:**
```latex
\begin{longtable}{|p{3cm}|p{2.5cm}|p{4cm}|p{5cm}|}
\hline
\rowcolor{gray!20}
\textbf{Actor} & \textbf{Type} & \textbf{Description} & \textbf{Responsibilities} \\
\hline
\endfirsthead
% ... rows
\end{longtable}
```

**Functional requirements table:**
```latex
\begin{longtable}{|p{1.8cm}|p{5cm}|p{2.5cm}|p{4cm}|}
\hline
\rowcolor{gray!20}
\textbf{ID} & \textbf{Requirement} & \textbf{Priority} & \textbf{Notes} \\
\hline
\endfirsthead
% ... rows with RF-001, RF-002, ...
\end{longtable}
```

**Business rules table:**
```latex
\begin{longtable}{|p{1.5cm}|p{4cm}|p{3cm}|p{3cm}|p{2.5cm}|}
\hline
\rowcolor{gray!20}
\textbf{ID} & \textbf{Rule} & \textbf{Context} & \textbf{Violation} & \textbf{Source} \\
\hline
\endfirsthead
% ... rows with BR-001, BR-002, ...
\end{longtable}
```

**Note / warning box:**
```latex
\begin{tcolorbox}[colback=yellow!10, colframe=orange!70, title={\textbf{Note}}]
Text of the note or warning.
\end{tcolorbox}
```

**Assumption box:**
```latex
\begin{tcolorbox}[colback=blue!5, colframe=blue!40, title={\textbf{Assumption}}]
Text of the assumption made in the absence of explicit information.
\end{tcolorbox}
```

---

