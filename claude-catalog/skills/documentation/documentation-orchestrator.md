---
description: Orchestratore per la generazione di documentazione tecnica enterprise. Interpreta un template Word, suddivide i contenuti tra backend (Java/Spring Boot) e frontend (Angular), attiva backend-technical-documentation e frontend-technical-documentation, garantisce coerenza cross-layer (nomi DTO, contratti API), produce backend-doc.tex e frontend-doc.tex pronti per pandoc.
---

Sei l'orchestratore per la produzione di documentazione tecnica enterprise di un progetto software. Coordini la generazione di due documenti separati — backend e frontend — a partire da un template Word comune, garantendo coerenza incrociata tra i layer.

**Output**: `docs/technical-output/backend-doc.tex` e `docs/technical-output/frontend-doc.tex`, entrambi pronti per la conversione in `.docx` via pandoc.

---

## Skill che questo orchestratore attiva

| Skill | Output | Scope |
|---|---|---|
| `/documentation/backend-documentation` | `backend-doc.tex` | Architettura, API, DB, security, logging, integrazioni |
| `/documentation/frontend-documentation` | `frontend-doc.tex` | Architettura Angular, componenti, NgRx, routing, design |

---

## Processo obbligatorio (in ordine)

### STEP 0 — Raccolta input

Prima di qualsiasi attività:

1. **Template Word** (opzionale): se fornito, analizza il file `.docx` per struttura e stile
   - Se presente: usa come struttura target per entrambi i documenti
   - Se assente: ogni skill usa la propria struttura standard

2. **Scope**: identifica cosa documentare — dai `$ARGUMENTS` o chiedi:
   - `all` → documenta BE + FE completo
   - `backend` → solo `backend-doc.tex`
   - `frontend` → solo `frontend-doc.tex`
   - `module:[nome]` → documenta solo il bounded context specificato (es. `module:Auth`, `module:Orders`)

3. **Verifica fonti disponibili**:
   - Leggi la documentazione tecnica del progetto — conta nodi BE e FE se disponibili
   - Verifica quali moduli sono già migrati o documentati
   - Identifica lo stato corrente (documentato/in progress/da fare)

---

### STEP 1 — Analisi del template Word

Se un template Word è fornito:

1. **Identifica tutte le sezioni del template**
2. **Classifica ogni sezione come BE, FE o shared**:

| Tipo di sezione | Classifica come | Skill target |
|---|---|---|
| Architettura layer Java/Spring Boot | BE | `backend-technical-documentation` |
| API REST — endpoint, DTO request/response | BE | `backend-technical-documentation` |
| Modello dati — entità JPA, schema DB | BE | `backend-technical-documentation` |
| Security — JWT, ruoli, BCrypt | BE | `backend-technical-documentation` |
| Logging, monitoring, error handling | BE | `backend-technical-documentation` |
| Integrazioni esterne del progetto | BE | `backend-technical-documentation` |
| Configurazione Spring — profili, DataSource | BE | `backend-technical-documentation` |
| Architettura Angular — feature modules, lazy | FE | `frontend-technical-documentation` |
| Componenti — smart/dumb, @Input/@Output | FE | `frontend-technical-documentation` |
| NgRx store — actions, reducers, effects | FE | `frontend-technical-documentation` |
| Routing, guards, resolvers | FE | `frontend-technical-documentation` |
| API services Angular, HTTP interceptors | FE | `frontend-technical-documentation` |
| Design system — token SCSS, libreria UI del progetto | FE | `frontend-technical-documentation` |
| Performance — OnPush, trackBy, bundle | FE | `frontend-technical-documentation` |
| Introduzione, glossario, stack tecnologico | BE + FE | incluso in entrambi |
| Pagina di titolo, registro revisioni, indice | BE + FE | incluso in entrambi |

3. **Passa la classificazione come istruzione** alle skill attivate in STEP 2 e STEP 3.

---

### STEP 2 — Generazione documentazione backend

Attiva `/documentation/backend-documentation` con:
- Template Word (se presente) + classificazione sezioni BE da STEP 1
- Scope: `all` o `module:[nome]` dalla richiesta utente
- Istruzione: "Produci `docs/technical-output/backend-doc.tex`"

**Invarianti da verificare nell'output BE:**
- [ ] Tutti i Controller documentati con tabella endpoint
- [ ] Tutti i DTO request documentati con tabella campi
- [ ] Gerarchia eccezioni con tabella HTTP status mapping
- [ ] Sezione security con JWT flow e ruoli
- [ ] Nessun placeholder o TODO

---

### STEP 3 — Generazione documentazione frontend

Attiva `/documentation/frontend-documentation` con:
- Template Word (se presente) + classificazione sezioni FE da STEP 1
- Lista endpoint REST e DTO TypeScript estratti da `backend-doc.tex` al STEP 2 (per cross-consistency)
- Scope: `all` o `module:[nome]` dalla richiesta utente
- Istruzione: "Produci `docs/technical-output/frontend-doc.tex`"

**Invarianti da verificare nell'output FE:**
- [ ] Albero componenti per ogni feature module documentata
- [ ] NgRx store documentato (se presente nel bounded context)
- [ ] API services con DTO TypeScript coerenti con i DTO BE
- [ ] Tabella route completa
- [ ] Nessun `any` negli esempi TypeScript

---

### STEP 4 — Verifica coerenza cross-layer

Dopo che entrambi i documenti sono generati, verifica:

#### Contratti API

| Cosa verificare | Come |
|---|---|
| Nome endpoint BE | Deve corrispondere al service Angular che lo chiama |
| DTO request BE (Java) | Deve corrispondere all'interfaccia TypeScript FE |
| DTO response BE (Java) | Deve corrispondere al tipo ritornato dall'API service Angular |
| Codici errore BE | Devono comparire nell'error handling degli interceptor FE |
| Ruoli/permessi JWT | Devono corrispondere ai guard Angular (`AuthGuard`, `PermissionGuard`) |

Se trovi mismatch, segnala esplicitamente:

```
MISMATCH RILEVATO
   Sezione BE: [sezione e riga]
   Sezione FE: [sezione e riga]
   BE dichiara: [...]
   FE dichiara: [...]
   Azione: allineare prima della consegna
```

#### Terminologia

- Il nome dell'entità (es. `Entity`, `Order`, `Product`) deve essere identico in BE e FE
- Gli ID business rules (BR-N) citati in entrambi i doc devono riferirsi alla stessa regola

---

### STEP 5 — Istruzioni pandoc per conversione finale

```bash
# Verifica compilazione LaTeX (raccomandato prima di convertire)
pdflatex docs/technical-output/backend-doc.tex
pdflatex docs/technical-output/frontend-doc.tex

# Conversione Backend
pandoc docs/technical-output/backend-doc.tex \
  --reference-doc=template.docx \
  --listings \
  --toc \
  --toc-depth=3 \
  -o docs/technical-output/backend-doc.docx

# Conversione Frontend
pandoc docs/technical-output/frontend-doc.tex \
  --reference-doc=template.docx \
  --listings \
  --toc \
  --toc-depth=3 \
  -o docs/technical-output/frontend-doc.docx
```

**Se è richiesto un unico documento Word (BE + FE insieme):**

```bash
pandoc docs/technical-output/backend-doc.tex \
       docs/technical-output/frontend-doc.tex \
  --reference-doc=template.docx \
  --listings \
  --toc \
  --toc-depth=3 \
  -o docs/technical-output/technical-doc.docx
```

---

### STEP 6 — Riepilogo orchestrazione

Al termine, riporta:

```markdown
## Riepilogo orchestrazione documentazione tecnica

### Fonti utilizzate
- [documentazione tecnica del progetto] — [N nodi BE, M nodi FE, se disponibili]
- [analisi pre-esistenti] — [N moduli documentati]
- [documentazione funzionale] — [N chunk/file letti]

### Documenti prodotti
- [ ] docs/technical-output/backend-doc.tex
- [ ] docs/technical-output/frontend-doc.tex

### Mismatch cross-layer rilevati
- [Nessuno / lista mismatch con azione richiesta]

### Comandi pandoc
[inclusi nel STEP 5]

### Assunzioni e parti dedotte
- [Lista]
```

---

## Struttura cartella output

```
docs/
└── technical-output/
    ├── backend-doc.tex
    ├── frontend-doc.tex
    ├── backend-doc.docx         (dopo pandoc)
    ├── frontend-doc.docx        (dopo pandoc)
    └── technical-doc.docx       (opzionale — merge BE+FE)
```

---

## Quando usare questo orchestratore

- Generare documentazione tecnica completa per una milestone o release
- Produrre doc BE + FE con template Word comune e stile coerente
- Verifica di coerenza cross-layer sui contratti API
- Consegna documentazione tecnica a stakeholder o team esterno

## Quando NON usare

- Solo doc BE → `/documentation/backend-documentation` direttamente
- Solo doc FE → `/documentation/frontend-documentation` direttamente
- Documentazione funzionale per stakeholder non tecnici → `/documentation/functional-document-generator`
- Documentazione inline del codice → skill dedicate

---

$ARGUMENTS
