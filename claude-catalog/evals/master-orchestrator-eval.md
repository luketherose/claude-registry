# Evals: master-orchestrator

---

## Eval-001: Functional analysis routing — BRD input

**User prompt**:
```
Analizza questo BRD e producimi l'analisi funzionale completa con tutti i formati:
[BRD text with actors, flows, requirements]
```

**Expected routing**:
- Agent classifies intent → "functional analysis from BRD"
- Agent runs pre-routing checklist: checks `test/docs/functional/` (empty or absent)
- Agent resolves output_formats → `["md","tex","docx","html"]` (default, no user preference)
- Agent invokes `functional-analyst` with: BRD text + output_path=`test/` + output_formats list
- `functional-analyst` runs its full pipeline (Steps 0–4)

**Expected output**:
- All files in `test/docs/` as specified in `functional-analyst` Eval-001
- Master orchestrator reports: which agent was invoked, what was produced, where saved

**Must NOT contain**:
- Master orchestrator writing analysis content directly (must delegate)
- Missing UML diagrams
- Only `.md` files without `.tex` / `.docx`

---

## Eval-002: Frontend routing — stack detection + functional context injection

**Context**: `test/docs/functional/features.md` and `test/docs/functional/userflows.md`
exist from a previous functional analysis.

**User prompt**:
```
Implementa il frontend React per il modulo di simulazione finanziamento.
```

**Expected routing**:
- Pre-routing checklist: finds `test/docs/functional/*.md` → loads content
- Detects stack: no `package.json` found → infers React from prompt
- Invokes `developer-frontend` with:
  - Functional context from `test/docs/functional/features.md` (simulation module FR-NNN)
  - Functional context from `test/docs/functional/userflows.md` (UF-simulation flow)
  - Stack = React

**Expected behavior**:
- `developer-frontend` receives functional requirements without the user having to re-state them
- Agent reports: "Loaded functional analysis from test/docs/functional/ — passing simulation module context"

**Must NOT contain**:
- `developer-frontend` being invoked without functional context when it exists
- Re-running functional analysis (artefacts already exist)

---

## Eval-003: Multi-step pipeline — BRD then frontend

**User prompt**:
```
Partendo dal BRD allegato, prima fai l'analisi funzionale poi implementa
il frontend React per il modulo di comparazione offerte.
```

**Expected routing**:
- Agent identifies multi-step task
- Communicates plan BEFORE executing: "Step 1: functional-analyst → Step 2: developer-frontend"
- Executes Step 1: `functional-analyst` → produces `test/docs/`
- Executes Step 2: `developer-frontend` ← receives output of Step 1 as context
- Steps are sequential, NOT parallel

**Must NOT contain**:
- Both agents invoked simultaneously
- Step 2 starting before Step 1 has completed
- Step 2 receiving no functional context

---

## Eval-004: Ambiguous routing — chooses correct specialist

**Prompt A**: `"Rivedi il codice nel file PaymentService.java"`
→ Must route to `code-reviewer`, NOT `debugger` or `developer-java-spring`

**Prompt B**: `"C'è un NullPointerException in CartController riga 42"`
→ Must route to `debugger`, NOT `code-reviewer`

**Prompt C**: `"Scrivi i test per UserService.java"`
→ Must route to `test-writer`, NOT `developer-java-spring`

**Prompt D**: `"Crea un'architettura per un sistema di pagamenti distribuito"`
→ Must route to `software-architect`, NOT `developer-java-spring`

**How to verify**: for each prompt, check the agent reports which specialist was invoked
and confirm it matches the expected routing above.

---

## Eval-005: Format preference propagation

**User prompt**:
```
Analisi funzionale del BRD [text]. Voglio solo .tex e .pdf.
```

**Expected routing**:
- Master orchestrator resolves output_formats → `["tex", "pdf"]`
- Invokes `functional-analyst` with `output_formats=["tex","pdf"]`
- `functional-analyst` Step 0 uses the passed formats (does not ask again)
- Only `.tex` and `.pdf` produced (no `.docx`, no `.html`)
- If pdflatex missing: reports clearly, produces only `.tex`

**Must NOT contain**:
- `functional-analyst` asking the user again which formats they want
- `.docx` or `.html` being produced when not requested

---

## Eval-006: No recursive invocation

**User prompt**: any prompt that would normally route to `master-orchestrator`

**Expected behavior**:
- Agent never invokes `master-orchestrator` as a sub-agent
- If somehow triggered recursively, stops and reports the loop

---

## Regression checklist (run after any update to master-orchestrator)

```
[ ] Eval-001: functional-analyst invoked, all formats produced
[ ] Eval-002: developer-frontend receives functional context automatically
[ ] Eval-003: multi-step is sequential, Step 2 uses Step 1 output
[ ] Eval-004: correct specialist selected for each ambiguous prompt
[ ] Eval-005: format preference passed through without re-asking
[ ] Eval-006: no recursive invocation of master-orchestrator
[ ] Master orchestrator never writes content directly (always delegates)
[ ] Delivery summary present after every invocation
```
