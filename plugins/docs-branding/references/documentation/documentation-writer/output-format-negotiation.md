# Output format negotiation: probes, menu and conversion pipeline

> Reference doc for `documentation-writer`. Read at runtime during Step 0,
> before reading any code or drafting any text. The agent body states *that*
> the negotiation is mandatory and what the accepted answers mean; the probe
> commands, the exact menu shape and the pandoc invocations live here.

## Contents

- [Step 0.1: detect the local toolchain](#step-01-detect-the-local-toolchain): the `which` probes and the format-to-tool table that turns them into an availability list.
- [Step 0.2: surface the menu and ask](#step-02-surface-the-menu-and-ask): the exact block to print to the user, and the default-deny rule for unavailable formats.
- [Step 0.3: confirm and lock the format set](#step-03-confirm-and-lock-the-format-set): the echo-back shape that becomes the contract for the session.
- [Step 0.4: single-source authoring pipeline](#step-04-single-source-authoring-pipeline): the pandoc command per target format, and the conventions for hand-authored LaTeX.

## Step 0.1: detect the local toolchain

Run these probes (Bash) and capture which formats are actually producible:

```bash
which pandoc        # required for tex/html/docx/pdf-via-tex output
which pdflatex      # required for pdf via LaTeX (best quality)
which wkhtmltopdf   # alternative for pdf via HTML (fallback if no pdflatex)
which lualatex      # optional alternative engine
which xelatex       # optional alternative engine (Unicode-friendly)
```

From the probe results, build the **available formats list**:

| Format    | Required tools                   |
|-----------|----------------------------------|
| `md`      | (none, always available)         |
| `tex`     | `pandoc`                          |
| `html`    | `pandoc`                          |
| `docx`    | `pandoc`                          |
| `pdf`     | `pandoc` + `pdflatex` (or `lualatex`/`xelatex`); fallback: `wkhtmltopdf` |

Format `md` is always available because it is the source format you author in.

## Step 0.2: surface the menu and ask

Use this exact shape (translate to the user's language if they wrote to you in
non-English):

```
=== Output format selection ===

Available on this machine:
  [md]    Markdown (.md)         always available; the source format
  [tex]   LaTeX (.tex)           pandoc detected
  [html]  HTML (.html)           pandoc detected
  [docx]  Word (.docx)           pandoc detected
  [pdf]   PDF (.pdf)             pandoc + pdflatex detected (LaTeX engine)

Not available (missing toolchain):
  (none)        OR        [<format>]   <missing-tool> not on PATH; install with: <hint>

Default if you say nothing: md + tex + html + pdf
(Markdown source plus LaTeX, HTML and PDF: the most useful combination)

Which format(s) do you want? Reply with one or more (e.g. "pdf, docx" or "all" or "just md").
```

**Default deny on unavailable formats.** If the user requests a format whose
toolchain is missing, do NOT silently degrade. Reply explaining what is missing
and offer the install hint. Let the user decide whether to install or pick a
different format.

## Step 0.3: confirm and lock the format set

Echo back the agreed set:

```
Producing documentation in: md, tex, pdf
- Source:      <output-dir>/<slug>.md
- LaTeX:       <output-dir>/<slug>.tex
- PDF:         <output-dir>/<slug>.pdf
Diagrams:      docs/diagrams/  (referenced from each format)
```

This locked set is the contract for the rest of the session. Do not change
formats mid-session unless the user asks.

## Step 0.4: single-source authoring pipeline

Author once in Markdown (with extended syntax: fenced code blocks, tables,
math via `$...$`, footnotes, cross-refs via `[label](#anchor)`). Convert to all
agreed formats from that single source via pandoc:

```bash
# md to tex
pandoc <slug>.md -o <slug>.tex --standalone --listings

# md to html (with embedded CSS)
pandoc <slug>.md -o <slug>.html --standalone --self-contained --metadata title="<title>"

# md to docx
pandoc <slug>.md -o <slug>.docx --reference-doc=<optional-template>

# md to pdf via LaTeX (preferred, best typesetting)
pandoc <slug>.md -o <slug>.pdf --pdf-engine=pdflatex --listings -V geometry:margin=1in

# md to pdf via wkhtmltopdf (fallback if no pdflatex)
pandoc <slug>.md -o <slug>.pdf --pdf-engine=wkhtmltopdf
```

When emitting LaTeX directly (the user explicitly asked for `.tex` as the
authoring format, not just an export), use these conventions:
`\documentclass{article}`, `\usepackage{listings}` for code,
`\usepackage{hyperref}` for cross-refs, `\usepackage{tikz}` only when the
diagram skill cannot produce the asset. Always cite the toolchain version in a
comment at the top so the file is reproducible.
