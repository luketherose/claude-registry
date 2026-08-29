# Conversion to Word

The pandoc invocation that turns `backend-doc.tex` into `.docx`, and what each
LaTeX element becomes on the Word side.

```bash
# PDF compilation (verify structure before converting)

pdflatex backend-doc.tex

# Conversion with reference Word template

pandoc backend-doc.tex \
  --reference-doc=template.docx \
  --listings \
  --toc \
  --toc-depth=3 \
  -o backend-doc.docx
```

| LaTeX element | Behaviour in Word |
|---|---|
| `lstlisting` (Java code) | Monospace block, syntax highlighting lost |
| `longtable` | Word table, verify column widths |
| `tcolorbox` | Text box, border approximated, refine manually |
| `\rowcolor` | Cell background not always preserved |
| `\fancyhdr` | Word headers if present in the reference template |
| `\texttt` | Monospace correctly preserved |
| Footnotes `\footnote` | Preserved as Word footnotes |

---
