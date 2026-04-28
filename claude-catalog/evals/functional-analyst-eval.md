# Evals: functional-analyst

---

## Eval-001: Full BRD analysis — happy path (all formats)

**Input context**: BRD text provided inline in the prompt (no existing files).

**User prompt**:
```
Fai l'analisi funzionale del seguente BRD e produce tutti i formati disponibili
nella cartella test/:

[BRD — App di finanziamento integrata nel carrello partner]
1. Obiettivo: app che si integri con carrello e-commerce per consentire richiesta
   finanziamento, confronto offerte multi-istituto, completamento processo senza
   uscire dal flusso di acquisto.
2. User Journey: utente aggiunge prodotti → seleziona "Paga a rate" → app riceve
   dati carrello → mostra offerte comparate → utente seleziona offerta → inserisce
   dati personali + documenti → approvazione real-time o differita → acquisto.
3. Requisiti: integrazione carrello via API (importo, prodotti, ordine ID),
   motore comparazione N istituti, simulazione real-time (<2s), KYC + firma digitale,
   decisioning instant + async, GDPR, disponibilità >99.5%.
```

**Expected output characteristics**:
- `test/docs/functional/features.md` exists with ≥15 FR-NNN entries, each with acceptance criteria
- `test/docs/functional/usecases.md` exists with ≥5 UC-NNN entries, each with main flow + ≥1 alternative + ≥1 exception + BDD Gherkin
- `test/docs/functional/business-rules.md` exists with ≥8 BR-NNN entries
- `test/docs/functional/userflows.md` exists with ≥3 UF-NNN flows with pre/post-conditions
- `test/docs/functional/assumptions.md` exists with ≥3 A-NNN entries and ≥2 OQ-NNN open questions
- `test/docs/diagrams/use-cases.svg` exists and is a valid SVG (starts with `<?plantuml` or `<svg`)
- `test/docs/diagrams/` contains ≥3 additional SVG files (activity or state or sequence diagrams)
- All `.puml` source files are present alongside each `.svg`
- `test/docs/functional-spec.tex` exists, ≥400 lines, starts with `\documentclass`
- `test/docs/functional-spec.tex` contains `\includegraphics` references to diagram files
- `test/docs/functional-spec.docx` exists (if pandoc is installed)
- `test/docs/functional-spec.html` exists (if pandoc is installed)
- `test/docs/CONVERT.md` exists with pandoc commands

**Must NOT contain**:
- Raw PlantUML text blocks inline in any `.md` file as a substitute for rendered diagrams
- Requirements without unique FR-NNN / UC-NNN / BR-NNN identifiers
- Use cases with only a happy path (no alternative or exception flows)
- LaTeX file with `\includegraphics` pointing to non-existent files
- Any TODO or placeholder text in produced documents

**How to run**:
1. Ensure `.mcp.json` at project root contains the `uml` MCP server entry
2. Restart Claude Code to load the MCP server
3. Verify `pandoc` is available: `which pandoc`
4. Run the prompt with `functional-analyst` active
5. Check all files listed above exist: `find test/docs -type f | sort`
6. Verify SVG files: `head -c 50 test/docs/diagrams/use-cases.svg`
7. Verify LaTeX: `grep -c includegraphics test/docs/functional-spec.tex` (must be ≥3)
8. Open `test/docs/functional-spec.docx` in Word and verify diagrams are embedded

---

## Eval-002: Format selection — docx only

**User prompt**:
```
Fai l'analisi funzionale del BRD [same as Eval-001]. Voglio solo il file .docx.
```

**Expected output characteristics**:
- `test/docs/functional/*.md` source files are still produced (always required)
- `test/docs/diagrams/*.svg` are still produced (always required)
- `test/docs/functional-spec.tex` is produced (intermediate step for docx)
- `test/docs/functional-spec.docx` exists
- `test/docs/functional-spec.html` does NOT exist (not requested)
- `test/docs/functional-spec.pdf` does NOT exist (not requested)
- Agent reports in Step 0 which formats were requested and which were produced

**Must NOT contain**:
- HTML or PDF files when the user explicitly requested only docx

---

## Eval-003: Format negotiation — missing pandoc

**Context**: pandoc is NOT installed on the machine.

**User prompt**:
```
Analisi funzionale del BRD [same as Eval-001]. Tutti i formati.
```

**Expected behavior**:
- Step 0 runs `which pandoc` → not found
- Agent reports clearly: "pandoc not found — docx and html will be skipped"
- Agent provides the install command: `brew install pandoc`
- `test/docs/functional-spec.tex` is produced correctly
- `test/docs/functional-spec.docx` is NOT produced (no silent failure)
- `test/docs/CONVERT.md` is produced with the pandoc command for later use
- Delivery summary lists docx and html as "skipped" with reason

**Must NOT contain**:
- A crash or silent failure
- A `.docx` file with zero bytes or corrupt content
- Missing `CONVERT.md`

---

## Eval-004: UML diagram completeness

**Input context**: BRD describing a system with: actors (3+), user flows (3+),
entity states (application lifecycle), external integrations (KYC, lender APIs).

**Expected diagram output**:
- `use-cases.svg` — groups use cases by module (cart, comparison, application, decision)
- `activity-*.svg` — one per main flow from `userflows.md`
- `state-*.svg` — application lifecycle states (DRAFT → SUBMITTED → IN_REVIEW → APPROVED/REJECTED)
- `sequence-*.svg` — at least one for external integration (e.g. lender API calls)

**Must NOT contain**:
- Fewer than 4 SVG diagram files for a system with flows + states + integrations
- Diagrams described only as PlantUML text without actual rendering via MCP server

**How to verify**:
```bash
ls test/docs/diagrams/*.svg | wc -l   # must be ≥ 4
for f in test/docs/diagrams/*.svg; do head -c 10 "$f"; echo " ← $f"; done
# each must start with <?plantuml or <svg, not @startuml (raw PlantUML)
```

---

## Eval-005: Existing analysis detected — no re-analysis

**Context**: `test/docs/functional/*.md` files already exist from a previous run.

**User prompt**:
```
Rigenera solo i formati mancanti dall'ultima analisi funzionale.
```

**Expected behavior**:
- Agent reads existing `test/docs/functional/*.md` files (does not re-run analysis)
- Agent checks which format files are missing in `test/docs/`
- Produces only the missing formats
- Does NOT overwrite existing `.md` source files
- Reports: "Analysis artefacts found — skipping re-analysis, producing missing formats only"

---

## Regression checklist (run after any update to functional-analyst)

```
[ ] Eval-001: all files produced, SVGs are rendered images not raw text
[ ] Eval-002: only requested format produced
[ ] Eval-003: graceful degradation when pandoc missing
[ ] Eval-004: ≥4 diagram types for complex BRD
[ ] Eval-005: existing artefacts respected, no unnecessary re-analysis
[ ] LaTeX compiles: cd test/docs && pdflatex functional-spec.tex (exit 0)
[ ] Word opens: functional-spec.docx opens in Word without errors
[ ] Diagrams in Word: images visible in .docx (not broken links)
```
