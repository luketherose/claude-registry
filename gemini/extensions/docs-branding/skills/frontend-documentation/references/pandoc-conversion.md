# Conversion to Word

The pandoc invocation that turns `frontend-doc.tex` into `.docx`, and what each
LaTeX element becomes on the Word side.

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
| `tcolorbox` | Approximated box, refine manually |
| SCSS tokens in table | Values visible, cell background to refine |
| `\fancyhdr` | Word headers if present in the reference template |
