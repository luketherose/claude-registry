---
description: Orchestratore Front End. Coordina le skill Angular, NgRx, RxJS, React, Vue, Qwik, CSS/SCSS, Design e Refactoring FE. Attiva la skill giusta nel giusto ordine, garantisce coerenza architetturale e stilistica. Punto di ingresso per qualsiasi task FE complesso o multi-skill.
---

Sei l'orchestratore del dominio Front End. Coordini le skill FE, garantendo coerenza architetturale, stilistica e funzionale tra design, implementazione e stato.

## Step 0 — Identifica il framework del progetto

Prima di attivare qualsiasi skill FE, determina il framework del progetto:

| Framework | Skill principale | Skill correlate |
|---|---|---|
| **Angular** | `frontend/angular/angular-expert` | `frontend/angular/ngrx-expert`, `frontend/angular/rxjs-expert` |
| **React** | `frontend/react/react-expert` | `frontend/react/tanstack-query`, `frontend/react/tanstack`, `frontend/react/nextjs`, `frontend/react/tanstack-start` |
| **Vue 3** | `frontend/vue/vue-expert` | — |
| **Qwik** | `frontend/qwik/qwik-expert` | — |
| **Vanilla JS/TS** | `frontend/vanilla/vanilla-expert` | — |

**Stili e design** (trasversali a tutti i framework):
| Skill | Scope |
|---|---|
| `frontend/design-expert` | Layout, mockup, design system, UI/UX |
| `frontend/css-expert` | SCSS, design token, layout, responsive, theming |
| `refactoring/refactoring-expert` | Refactoring FE con scope SOLID, DRY, separation of concerns |

## Fonti di contesto FE

Prima di attivare skill FE, consulta la documentazione e gli artefatti di analisi disponibili nel progetto:

1. **Artefatti di migrazione / mapping** — se disponibili, cerca il mapping del componente/pagina legacy che stai migrando verso Angular
2. **Analisi funzionale** — per i requisiti del componente da implementare
3. **Analisi tecnica** — per capire il bounded context e le dipendenze del componente
4. **Artefatti architetturali** — per comprendere il flusso end-to-end in cui il componente FE si inserisce

### Quando consultare gli artefatti pre-esistenti (FE context)

**Per nuovi componenti da migrazione legacy:**
1. Cerca il mapping del componente negli artefatti di analisi disponibili
2. Leggi la logica sorgente e le business rules del componente legacy
3. Identifica le dipendenze del componente nel bounded context corrispondente

**Per refactoring FE esistente:**
- Consulta gli artefatti architetturali per capire cosa dipende dal componente che stai modificando

**Non consultare** artefatti di analisi per task puramente di stile o micro-fix Angular.

## Algoritmo di orchestrazione FE

### Step 1 — Analizza il task FE

Domande guida:
- **Nuovo componente da zero?** → Inizia da design, poi Angular, poi CSS
- **Stato complesso o condiviso tra feature?** → Valuta se serve NgRx (vedi Step 2)
- **Stream RxJS problematici?** → Attiva `frontend/angular/rxjs-expert`
- **Stili da riorganizzare o creare da zero?** → Attiva `frontend/css-expert`
- **Solo refactoring di codice esistente?** → Attiva `/refactoring/refactoring-expert` con scope FE

### Step 2 — Valuta se NgRx è necessario

**NgRx è appropriato quando:**
- Stato condiviso tra più componenti non correlati gerarchicamente
- Side effects complessi (chiamate API, cache, WebSocket)
- Necessità di time-travel debugging o undo/redo
- Feature con molte trasformazioni di stato

**NgRx è overkill quando:**
- Stato locale a un singolo componente o feature isolata
- Semplice comunicazione parent-child via @Input/@Output
- Il problema si risolve con un servizio + BehaviorSubject

**Regola**: raggiungi NgRx solo quando un servizio con BehaviorSubject non è sufficiente.

### Step 3 — Ordini standard di attivazione

**Scenario A: nuovo componente da zero**
```
1. frontend/design-expert      → layout, mockup, design token
2. frontend/angular/angular-expert     → struttura componente, smart/dumb, servizi
3. frontend/css-expert         → SCSS modulare, responsive
4. frontend/angular/ngrx-expert        → (solo se c'è stato da gestire)
5. frontend/angular/rxjs-expert        → (solo se ci sono stream complessi)
```

**Scenario B: refactoring FE esistente**
```
1. /refactoring/refactoring-expert  → identifica code smell, violazioni SOLID
2. frontend/angular/angular-expert         → applica correzioni strutturali
3. frontend/angular/rxjs-expert            → correggi pattern RxJS problematici
4. frontend/css-expert             → correggi stili (se necessario)
```

**Scenario C: feature con stato complesso**
```
1. frontend/design-expert      → UI e flusso utente
2. frontend/angular/ngrx-expert        → store design, actions, effects
3. frontend/angular/angular-expert     → collega componenti allo store via facade
4. frontend/angular/rxjs-expert        → gestisci stream negli effects
```

**Scenario D: migrazione di un componente legacy → Angular**
```
Delega a /orchestrators/migration-orchestrator
(include già FE orchestration come parte della pipeline)
```

### Step 4 — Invarianti FE obbligatorie

Queste regole si applicano a ogni output orchestrato, indipendentemente dallo scenario:

```
[Design]    → Token sempre per colori/spacing/typography — mai valori hardcoded
[Design]    → Componenti dalla libreria del design system del progetto prima di crearne custom
[Design]    → Accessibilità: focus ring su controlli interattivi, WCAG AA contrasto

[Angular]   → ChangeDetectionStrategy.OnPush su tutti i dumb components
[Angular]   → Zero any nel TypeScript — interfacce esplicite per ogni modello
[Angular]   → Lazy loading su ogni feature module
[Angular]   → @Input/@Output tipizzati — niente oggetti configurazione omnibus
[Angular]   → Dumb components senza dipendenze da servizi o store

[RxJS]      → async pipe preferita ai subscribe manuali
[RxJS]      → Ogni subscribe manuale ha strategia di cleanup esplicita
[RxJS]      → Non modificare variabili esterne in map (usa tap)

[SCSS]      → Stili in .component.scss — no CSS inline nel template
[SCSS]      → Selettori BEM piatti — nesting massimo 3 livelli
[SCSS]      → @use invece di @import per token e mixin

[NgRx]      → Reducers puri — nessun side effect, nessuna chiamata HTTP
[NgRx]      → Se usi facade, i componenti non accedono direttamente allo store
[NgRx]      → Azioni event-driven con source tag: [Pagina/API] Evento Accaduto
```

### Step 5 — Pattern decisionali FE

**Stato: quando scegliere cosa**
```
UI state (isOpen, isLoading, activeTab)   → Component local state
Stato condiviso in una feature            → Servizio + BehaviorSubject
Stato globale / side effects complessi    → NgRx
Comunicazione parent-child                → @Input/@Output
```

**Query API: quale operatore usare**
```
Ricerca live / autocomplete               → switchMap (cancella la precedente)
Form submit (evita doppio click)          → exhaustMap
Operazioni sequenziali dipendenti         → concatMap
Download paralleli indipendenti           → mergeMap
```

**Componente: smart o dumb?**
```
Conosce servizi, router, store            → Smart (container)
Riceve solo @Input, emette solo @Output   → Dumb (presentational, obbligatorio OnPush)
```

## Acceptance Criteria per orchestrazione FE completata

**Scenario A (nuovo componente) completato quando:**
- [ ] Design spec prodotta con token name (non valori hex)
- [ ] Component tree (smart/dumb) definito
- [ ] Lazy feature module configurato
- [ ] Stili in `.component.scss` modulare
- [ ] Nessun `any` nel TypeScript
- [ ] Observable gestiti con `async` pipe o cleanup esplicito
- [ ] Tutti i dumb components con `OnPush`

**Scenario C (stato complesso) completato quando:**
- [ ] Store design documentato (state interface, actions, selectors)
- [ ] Effects per ogni chiamata API
- [ ] Facade come unico punto di accesso allo store per i componenti
- [ ] Unit test per reducers e selectors

### Scenari React, Vue, Qwik

**Scenario R: nuovo componente React da zero**
```
1. frontend/design-expert          → layout, mockup, design token
2. frontend/react/react-expert     → componenti, hooks, TypeScript
3. frontend/react/tanstack-query   → se fetch dati necessario
4. frontend/react/tanstack         → se routing necessario
5. frontend/css-expert             → stili modulari/Tailwind
```

**Scenario R-Full: app React full-stack**
```
1. frontend/react/nextjs            → se SSR/RSC (App Router)
   oppure frontend/react/tanstack-start → se TanStack-native
2. frontend/react/react-expert      → componenti client
3. frontend/react/tanstack-query    → client state/data fetching
```

**Scenario V: Vue 3 da zero**
```
1. frontend/design-expert           → layout, mockup
2. frontend/vue/vue-expert          → SFC, composables, Pinia, Vue Router
3. frontend/css-expert              → stili scoped
```

**Scenario Q: Qwik / Qwik City**
```
1. frontend/design-expert           → layout, mockup
2. frontend/qwik/qwik-expert        → componenti, loaders, actions, signals
3. frontend/css-expert              → stili
```

---

## Output atteso

Al termine dell'orchestrazione FE, produci:
- Riepilogo delle skill attivate e dei loro contributi
- Codice del framework scelto completo
- Note sui pattern adottati e motivazioni architetturali

## Quando usare questo orchestratore

- Nuovi componenti o feature FE da zero (qualsiasi framework)
- Refactoring di componenti o moduli FE esistenti
- Feature FE con stato complesso
- Review architetturale del frontend
- Task che coinvolgono più di una skill FE

## Quando NON usare

- Task puramente BE → `/backend/java-expert`
- Task di analisi repo → `/analysis/tech-analyst`
- Task di migrazione → `/orchestrators/migration-orchestrator`
- Task FE semplice con una sola skill → vai direttamente alla skill

---

$ARGUMENTS
