# W5 critic review: skill trigger evals

Adversarial review of the 46 `plugins/*/evals/*/triggers.json` files written for the 46 Agent Skills.
Everything below was re-derived from the files. The producing agent's report was not used as input.

Snapshot: 46 `SKILL.md` files, combined md5 `5fb1120d9b343e2c476e05d7d64e106c`, read 2026-08-29 23:14 CEST.
`SKILL.md` files were being edited concurrently while this review ran (em dashes were stripped from
descriptions mid-review). Semantics were unchanged; every quote below is from the snapshot above.

## Verdict

**No. These evals cannot gate a routing regression in their current form.**

There is a single defect that voids the entire negative half of the suite: **all 94 of the 94
`should_not_trigger` prompts carry a parenthetical at the end that names the skill that should win, or
states the rule that excludes the current one.** Not most. All 94. And **0 of the 138
`should_trigger` prompts carry one.** The two classes are perfectly separable by a syntactic test that
requires no understanding of routing at all: *does the string contain a parenthesis?* A router that
answers "do not trigger" on every prompt containing `(` scores 94/94 on negatives while knowing nothing.

Verified:

```
positives: 138   with a parenthetical: 0
negatives:  94   with a parenthetical: 94  (100%)
```

Of the 94 annotations, 79 name a sibling skill by its exact name, 6 name an agent, and 9 spell out the
discriminating rule in words (`fuori scope: schema migration design`, `update di routine senza conflitto`).
All 94 are answer-bearing.

**Fraction I would rewrite.** All 94 negatives must be touched. For 38 of them the annotation strip is
sufficient and the underlying prompt is a genuine near-miss. The other 56 negatives and roughly 16 of the
138 positives need to be rewritten, not repaired: **72 of 232 entries (31%) written from scratch, on top
of a mechanical strip applied to 100% of the negatives.**

This is a fixable suite, not a worthless one. The positives are largely sound, the cross-file
bookkeeping is genuinely good (see Strengths), and the framework skills got well-observed Italian
prompts. The negative half needs a pass.

## Findings, ranked by how likely each is to hide a real routing break

### F1. Every negative leaks the answer into the prompt (94/94). Fatal.

`plugins/dev-standards/evals/angular-expert/triggers.json`:

> `"Il selector dello store ricalcola ad ogni tick, memoizzalo e sistema l'effect che non ricarica (ngrx-expert)"`

`plugins/dev-standards/evals/backend-orchestrator/triggers.json`:

> `"Aggiungi un indice su order_date, la query di reportistica ci mette 4 secondi (task single layer, postgresql-expert)"`

The second is worse than the first: it does not merely name the winner, it states the exact criterion
(`task single layer`) that the description uses to exclude the skill. The router is handed the reasoning.

Consequence: if someone deletes the sentence `Do not use for single-layer tasks (use the targeted skill
directly)` from `backend-orchestrator`'s description tomorrow, this eval still passes. That is precisely
the regression the suite exists to catch, and it will not catch it.

This is not a stylistic quibble. It is also not how the repo already writes these. The pre-existing
`plugins/dev-standards/evals/debugger/triggers.json`, written before this batch, has clean negatives:

> `"Rifattorizza questo modulo per togliere la duplicazione, non c'è nessun bug"`

No annotation. The new batch introduced the contamination.

### F2. Schema regression: the field that exists to hold the rationale was removed. Root cause of F1.

The repo's own template, `templates/new-use-case/evals/triggers.json`, uses an array of objects with a
dedicated `description` field, and its placeholder text says exactly where the rationale belongs:

> `"description": "Confusable query [...] should route to SIBLING-AGENT instead"`

Six pre-existing files use that schema. Two of them were converted to the flat object schema in this
batch, and their per-case rationale was destroyed in the process. `git diff` on
`plugins/analysis-architecture/evals/orchestrator/triggers.json` shows four `description` strings
deleted, including one reading `"Single-domain bug fix"` and `"routes to debugger directly"`. Same for
`plugins/analysis-architecture/evals/software-architect/triggers.json`.

So the rationale had a home, the home was removed, and the rationale was then stuffed into the query
string where the router reads it. Restoring the array schema fixes F1 for free and re-aligns 46 files
with the repo template. The repo is now split 55 object / 6 array, which is also a validator hazard.

### F3. Untested collisions. Each is unresolvable from descriptions alone.

These are the cases where two descriptions both claim the same prompt and no eval probes the boundary.
A routing change that moves the prompt from one to the other passes the suite silently.

**C1. `backend-orchestrator` vs `spring-architecture`.** Not flagged by the producer. The strongest one.
`spring-architecture`'s own positive is:

> `"Aggiungo un nuovo modulo: in che ordine implemento controller, service e repository, e dove metto DTO e mapper?"`

`backend-orchestrator`'s description opens with `ALWAYS use this skill when a backend task spans more
than one Java/Spring layer: the user asks to ... design a module from Controller to DB`. That prompt is
a module spanning controller, service, repository and DTO. `ALWAYS` beats `spring-architecture`'s milder
`This skill should be used when`. Both descriptions list a near-identical trigger phrase: `"add a new
module"` (spring-architecture) against `"design this module Controller to DB"` (backend-orchestrator).
Neither eval contains a negative for the other. A term-weighted match scores `backend-orchestrator` at
1.50 against `spring-architecture`'s own 1.00 on its own positive.

**C2. `tech-analyst` vs `graphify-code-graph`.** Flagged by the producer, and worse than reported. It is
not only the phrase `map this codebase`. Both descriptions claim dependency analysis and data flow:
`tech-analyst` says `Produces module maps, dependency graphs, bounded contexts, data flows`, and
`graphify-code-graph` says `dependency and impact analysis ... data-flow tracing`. `tech-analyst`'s own
positive

> `"Mappa i data flow e il dependency graph di questo monolite, e' il primo step della pipeline di analisi"`

scores `graphify-code-graph` at 1.65 against `tech-analyst`'s own 0.81. The eval's negatives dodge this:
`tech-analyst`'s graphify negative is `"Costruisci il graph.json con graphify..."`, which names the other
skill's CLI and artefact filename and is therefore trivially separable.

**C3. `doc-expert` vs `documentation-orchestrator`.** Neither description mentions the other.
`doc-expert` covers `a Python/Streamlit, Java/Spring Boot, or Angular project`, which includes every
full-stack project `documentation-orchestrator` claims with `ALWAYS use this skill when generating
enterprise technical documentation for a full-stack project`. `doc-expert`'s exclusion clause names
`functional-document-generator or backend/frontend-documentation` and stops there. No eval on either side
probes it.

**C4. `documentation-orchestrator` vs `functional-document-generator`.** Both descriptions claim Word
template interpretation (`it interprets a Word template` against `interprets a provided Word template`)
and both produce `.tex` for pandoc. `documentation-orchestrator`'s positive

> `"Serve il documento tecnico enterprise di tutto il progetto, pronto per pandoc"`

scores 0.20 for its owner against 0.70 for both `functional-document-generator` and
`backend-documentation`. The only discriminator is `tecnico` against `funzionale`, one word.

**C5. `route loader`, three ways.** `qwik-expert` lists trigger phrase `"route loader"`. `tanstack` lists
the identical phrase `"route loader"`. `tanstack-start`, `nextjs` and `qwik-expert` all claim
`file-based routing`. `tanstack`'s positive

> `"Definisci il loader e i search param tipizzati per la route /orders/$id"`

names no framework. It is matchable from `tanstack`'s description, but equally reachable from
`qwik-expert`'s `"route loader"` plus `file-based routing`. The `$id` file-route syntax that a human
would use to disambiguate appears in neither description. No eval probes it.

**C6. `refactoring-expert` vs `angular-expert`.** `angular-expert` lists trigger phrase
`"Angular FE refactoring"`; `refactoring-expert` claims `refactoring code in any language` with trigger
phrase `"refactor this"`. `frontend-orchestrator` additionally claims to coordinate `FE Refactoring
skills`. Three-way overlap. No eval on any of the three tests it, and `angular-expert`'s own positives
never exercise the `"Angular FE refactoring"` phrase.

### F4. One negative contradicts its own description outright.

`plugins/dev-standards/evals/postgresql-expert/triggers.json`:

> `"Il progetto usa Flyway, dove metto il @Transactional sulle entity? (concern JPA: spring-data-jpa)"`

`postgresql-expert`'s description says: `Liquibase is the only supported migration tool. Flyway is
forbidden; if Flyway appears, this skill should redirect to Liquibase.` The description instructs the
skill to engage when Flyway appears. The eval asserts it must not. One of the two is wrong. As written,
a correct router following the description fails this case, and a router that fails this case for the
wrong reason (ignoring Flyway entirely) passes it.

### F5. Only 38 of 94 negatives are real near-misses, even after stripping the annotation.

Grading rule applied: strip the parenthetical, then ask whether a reader given only the skill's
`description` field could plausibly have activated the skill on that prompt.

| Tier | Meaning | Count |
|---|---|---|
| A. Real near-miss | Prompt sits inside or adjacent to the description's stated positive territory; only a fine distinction excludes it | 38 (40%) |
| B. Exclusion echo | Prompt is family-adjacent but outside the positive territory; the description's closing `Do not use for X` sentence names it verbatim | 49 (52%) |
| C. Fake | Nothing in the description pulls toward the skill | 6 (6%) |
| Contradictory | See F4 | 1 |

The Tier B cases are not worthless, but they only defend the last sentence of the description. They tell
you nothing about whether the positive territory is drawn correctly, which is where routing actually
breaks.

The six Tier C fakes, with the offending strings:

| File | Fake negative | Why it discriminates nothing |
|---|---|---|
| `plugins/dev-standards/evals/browser-automation/triggers.json` | `"Fammi uno script che scarica il CSV dall'API e lo processa in batch (automazione non browser)"` | Description is entirely about `controlling a real browser`. A CSV batch script has no pull. |
| `plugins/analysis-architecture/evals/graphify-code-graph/triggers.json` | `"Genera un class diagram UML dei package di dominio e salvalo come SVG (uml-diagram-generator)"` | The description never mentions producing diagrams or images. Shared word `graph` is the only link. |
| `plugins/analysis-architecture/evals/tech-analyst/triggers.json` | `"Costruisci il graph.json con graphify e interrogalo per sapere chi chiama questo metodo (graphify-code-graph)"` | Names the rival skill's CLI and its artefact filename. Separable without reading either description. |
| `plugins/dev-standards/evals/rest-api-standards/triggers.json` | `"Come strutturo i layer di questo modulo, controller e service? (spring-architecture)"` | The description covers `resource modeling, HTTP method semantics, status codes, URL structure, versioning, pagination`. Nothing about layering. |
| `plugins/docs-branding/evals/accenture-branding/triggers.json` | `"Genera il documento funzionale in LaTeX partendo da docs/functional (functional-document-generator)"` | The description supplies brand reference data. Generating a functional document is not adjacent to it. |
| `plugins/docs-branding/evals/uml-diagram-generator/triggers.json` | `"Fammi un'infografica con i numeri del progetto per la slide (non è UML)"` | Lifted verbatim from the description's own exclusion example list `(e.g. infographics, BPMN ...)`. Tests only whether the last clause survived. |

### F6. Seven files spend both negatives on the same boundary.

Two shots at one edge, zero at the others. Each of these skills has at least two other plausible rivals
named in its own description or plugin, and all are untested.

| File | Both negatives probe |
|---|---|
| `ngrx-expert` | `angular-expert` twice (`"Metti questo component in OnPush..."`, `"Rifai questa form in Reactive Forms..."`) |
| `python-expert` | `streamlit-expert` twice |
| `streamlit-expert` | `python-expert` twice |
| `postgresql-expert` | `spring-data-jpa` twice (and one of the two is F4) |
| `rest-api-standards` | `spring-architecture` twice (and one of the two is a Tier C fake) |
| `uml-diagram-generator` | `non è UML` twice |
| `test-data-seeding-standards` | `fuori scope: schema migration design` twice, both quoting the description's own final sentence |

### F7. Positives that recite the description rather than probe it.

Every positive was written by paraphrasing the description, which is why check 2 turned up almost no
unmatchable positives. That is the inverse failure: **positives that cannot fail.** 32 of 138 (23%)
contain three or more rare terms lifted verbatim from their own description. Worst offenders:

`plugins/dev-standards/evals/java-spring-standards/triggers.json`:

> `"Dammi il riferimento canonico su ProblemDetail RFC 7807, logging SLF4J con MDC e baseline Spring Security 6"`

recites `the canonical Java/Spring Boot standards`, `RFC 7807 ProblemDetail`, `SLF4J + MDC logging` and
`Spring Security 6 baseline` in order. No user constructs that sentence.

A sharper subclass: **positives that recite an internal guardrail the user has no way to know.**

| File | Positive | Recited from |
|---|---|---|
| `functional-document-generator` | `"Produci il .tex del documento funzionale pronto per pandoc, senza inventare funzionalita"` | `Does not invent functionality not supported by the source content` |
| `backend-documentation` | `"Produci backend-doc.tex partendo dalle analisi gia fatte e dal codice Java"` | `Reads pre-existing analyses + source code` |
| `documentation-orchestrator` | `"Produci i deliverable doc: backend-doc.tex e frontend-doc.tex, coerenti sui nomi dei DTO e sui contratti API"` | `ensures cross-layer consistency (DTO names, API contracts)` |
| `tech-analyst` | `"Mappa i data flow e il dependency graph di questo monolite, e' il primo step della pipeline di analisi"` | `when an analysis, migration, or architecture-understanding pipeline starts` |
| `accenture-branding` | `"Che font e che hex uso per il documento Accenture? Mi servono anche le costanti python-pptx"` | `(hex values, python-pptx + CSS constants)` |

The same pattern shows up as disambiguating tokens bolted onto otherwise natural prompts. `doc-expert`'s
`"Scrivi la guida dei moduli di questo progetto Spring, taglio business, salvala in docs/"` needs both
`taglio business` and `salvala in docs/` to beat `backend-documentation`. `testing-standards`'s
`"Come dovrei strutturare questi test secondo lo standard aziendale?"` needs `secondo lo standard
aziendale` to beat `test-writer`. Strip those bolt-ons and the routing is ambiguous, which is the
honest state of affairs and what the eval should be recording.

### F8. One positive carries no discriminating signal at all.

`plugins/replatforming/evals/python-to-java-migration-expert/triggers.json`:

> `"L'architettura target e' gia definita, produci la specifica di migrazione modulo per modulo"`

No source language, no target language. The three `python-to-*` siblings differ only in source and
target. It scores identically (0.33) against all three descriptions. It is technically matchable, but
only because it echoes one oddly specific sentence, `Use it after the target architecture is defined, to
produce module-by-module migration specifications`. If that sentence were deleted from the description
tomorrow the prompt would route nowhere, and the suite would show a failure whose cause is unreadable.

### F9. The English trigger phrases in the descriptions are never exercised.

All 46 descriptions are in English. 84 of 138 positives are predominantly Italian, 48 lightly mixed, 6
carry no Italian marker. Every one of the 94 negatives is Italian. That matches how the repo owner
actually writes and is the right call, but it means the suite tests only cross-lingual semantic matching
and never the literal English `Trigger phrases:` strings the descriptions advertise. If someone corrupts
`"generateMetadata"` to `"generateMetaData"` in the `nextjs` description, nothing here notices. At least
one English positive per skill would close that gap cheaply.

### F10. Language quality: mostly good, with one bad cluster.

The framework skills read exactly as intended. These are good and I would not touch them:

- `css-expert`: `"Questo SCSS ha una specificity war con !important ovunque, rifallo con BEM e design token"`
- `streamlit-expert`: `"L'app Streamlit ricalcola tutto ad ogni click, metti a posto st.cache_data e session_state"`
- `rxjs-expert`: `"switchMap o exhaustMap per il submit di questa form? Adesso parte il doppio invio"`
- `refactoring-expert`: `"Questo metodo e' lungo 300 righe e fa cinque cose, spaccalo senza cambiare il comportamento"`
- `dependency-resolver`: `"Conflitto transitivo: il modulo A tira guava 2.x, il modulo B la 1.x, il build e' rotto"`

Symptom first, request second, concrete numbers. That is a real person typing.

The standards and documentation cluster is where the prose collapses into description headings. Flagged
as synthetic:

- `backend-documentation`: `"Genera la documentazione tecnica del backend: architettura, API reference, data model, sicurezza, error handling"` (the description's own section list)
- `frontend-documentation`: `"Genera il documento tecnico del frontend: moduli, smart/dumb component, store NgRx, routing, design system, performance"` (same)
- `test-data-seeding-standards`: `"Principi per il seed dataset: consistenza delle FK, utenti di login con permessi diversi, casi limite"`
- `testing-standards`: `"Quali sono i nostri testing standard? Naming, tassonomia degli scenari, struttura AAA"`
- `rest-api-standards`: `"Regole di authoring OpenAPI 3.1 che seguiamo in azienda"` (a noun phrase, not a request)
- `tanstack-start`: `"Streaming SSR e type safety end to end con TanStack Start"` (noun phrase)
- `uml-diagram-generator`: `"ER diagram del data model e component diagram dell'architettura"` (noun phrase, and asks for two unrelated diagrams in one breath)
- `vanilla-expert`: `"Libreria riutilizzabile in TypeScript strict con Custom Events e IntersectionObserver"` (noun phrase listing three description terms)

### F11. Six negatives route to agents, not sibling skills.

`functional-reconstruction`, `tech-analyst`, `dependency-resolver`, `refactoring-expert`,
`testing-standards` and `functional-document-generator` each have a negative whose annotation names
`functional-analyst`, `technical-analyst`, `debugger` or `test-writer`. Those are agents under
`plugins/*/agents/`, not skills. Skill activation and agent dispatch are different mechanisms, so these
cases assert something the skill-trigger suite is not measuring. Worth keeping, but they belong in a
separate routing suite rather than mixed in with skill-versus-skill discrimination.

## Strengths, stated plainly

The cross-file bookkeeping is the best part of this work and should survive any rewrite. At least ten
prompt clusters are used consistently as a positive for the owner and a negative for every skill whose
description defers to it. Examples:

- `useEffect` to `useQuery`: positive for `tanstack-query`, negative for `react-expert` and `tanstack`.
- `app/` plus Server Action: positive for `nextjs`, negative for `react-expert` and `tanstack-start`.
- Angular standalone plus OnPush: positive for `angular-expert`, negative for `qwik-expert`, `vanilla-expert`, `ngrx-expert` and `frontend-orchestrator`.
- `@OneToMany` N+1 fetch strategy: positive for `spring-data-jpa`, negative for `spring-architecture`, `spring-expert`, `postgresql-expert` and `java-spring-standards`.
- Fat controller, where does the logic go: positive for `spring-architecture`, negative for `spring-expert`.

No prompt appears as a positive for two skills. That is a real property and it was not free.

The three `python-to-*` migration files form a clean triangle: each names the other two as negatives with
the correct source or target swap, and `python-to-angular` against `python-to-react` is a genuinely hard
pair, differing only in the target framework. The four documentation files form the same shape.
`plugins/dev-standards/evals/react-expert/triggers.json` is the single best file in the batch: three
positives that are all real React work, and three distinct negatives (`nextjs`, `tanstack-query`,
`vanilla-expert`) covering every rival its description names.

## What to change in the evals, before the description edits

1. Restore the array schema from `templates/new-use-case/evals/triggers.json` across all 46 files and
   move every parenthetical into the `description` field. This alone fixes F1 and F2 and repairs 38 of
   the 94 negatives outright.
2. Rewrite the 6 Tier C fakes and redistribute the 7 duplicated boundaries onto rivals that are actually
   named in the relevant description.
3. Resolve F4 by deciding whether `postgresql-expert` owns Flyway prompts, then fix whichever of the
   description or the eval is wrong.
4. Add one negative each for C1 through C6 once the descriptions below are amended.
5. Replace the 5 guardrail-reciting positives in F7 and the 8 noun-phrase entries in F10 with utterances.
6. Add one English positive per skill so the advertised `Trigger phrases:` strings are actually covered.

## Independent judgement on the producer's six doubts

**1. `java-spring-standards`, `rest-api-standards`, `testing-standards` are self-contradictory. AGREE.**
The contradiction is exact and I can point at it. `testing-standards` lists trigger phrase `"how should
I structure these tests"` and then says `Do not trigger directly from a coding prompt.` A user asking how
to structure their tests is asking a coding question. Same for `rest-api-standards`, which lists `"how
should this endpoint look"` and `"review this API contract"`, and `java-spring-standards`, which lists
`"review this Spring code"`. Worse, the evals dodge the contradiction instead of pinning it: none of the
nine positives across the three files uses any of the contradicting phrases, and the disambiguation is
achieved by bolting `secondo lo standard aziendale` or `che seguiamo in azienda` onto the prompt. The
suite is silent on exactly the prompt shape the descriptions get wrong. Fix proposed below.

**2. `tech-analyst` vs `graphify-code-graph` phrase collision. AGREE, and it is bigger than reported.**
See C2. The collision is not confined to `map this codebase`; both descriptions claim dependency analysis
and data flow, and the term-weighted evidence puts `graphify` ahead of `tech-analyst` on `tech-analyst`'s
own positive. The producer under-called this.

**3. `dependency-resolver` exclusion depends on an outcome unknown at prompt time. DISAGREE.**
The description's positive side is entirely symptom-based: `the user reports NoSuchMethodError`, `works
locally fails in CI`, `incompatible peer deps`. Absence of a reported symptom is observable at prompt
time, so the exclusion is decidable: no failure reported, no trigger. What the producer missed is that
the defect is in the eval, not the description. The negative reads `"Aggiorna Spring Boot da 3.2.4 a
3.2.5 nel pom, e' solo una patch e non ha rotto niente"`, and the clause `non ha rotto niente` pre-answers
the question. The honest negative is `"Aggiorna Spring Boot da 3.2.4 a 3.2.5 nel pom"` and nothing more.
One clause of the description is still worth sharpening, since `Do not use for routine version updates`
leaves a major-version bump request in a grey zone; see the table.

**4. `doc-expert` remit is the union of `backend-documentation` and `frontend-documentation`. AGREE on the
overlap, DISAGREE on the reason.** The overlap is real: `doc-expert` covers `Python/Streamlit, Java/Spring
Boot, or Angular`, which is a strict superset of the other two. But the descriptions *do* disambiguate,
on output artefact: `doc-expert` says `saves to docs/` and is `business-oriented`, the others produce
`backend-doc.tex` and `frontend-doc.tex` for pandoc. That is a clean discriminator when the user states
the format. The genuine hole is different and the producer did not name it: `doc-expert`'s exclusion
clause omits `documentation-orchestrator` entirely, and `documentation-orchestrator` claims every
full-stack project with an `ALWAYS`. That is C3, and neither eval touches it.

**5. `design-expert` vs `unicredit-design-system` unnamed company. AGREE.** `design-expert` says `Applies
the company design system`, which is a dangling referent, while `unicredit-design-system` says `ALWAYS use
this skill when the project end client is UniCredit`. In a UniCredit engagement, `"segui il design system
aziendale"` matches both, and `ALWAYS` wins by phrasing rather than by evidence. The eval sidesteps this
by writing `"Cliente retail generico, dammi la style spec..."`, which names a client precisely so the
ambiguity cannot arise. One caveat the producer should note: the honest fix for the client-identity half
is a project-level `CLAUDE.md` pin, not a description edit, because the end client is a property of the
engagement and not of the prompt. The description edit below fixes only the dangling referent.

**6. The two orchestrators trigger on a property of the resulting work, not of the prompt. AGREE for
`frontend-orchestrator`, PARTIALLY DISAGREE for `backend-orchestrator`.**

`frontend-orchestrator`: `ALWAYS use this skill when a frontend task spans multiple concerns` is
unbounded. Nearly every real frontend task touches routing, state, styling and an API call. Read
literally, this skill swallows `angular-expert`. The eval's two negatives are both single-concern, so the
broad zone is never probed. Full agreement.

`backend-orchestrator`: partially decidable. The description supplies prompt-observable phrases
(`add a new endpoint end-to-end`, `from controller to database`, `full backend feature`), and the eval's
second negative, `"Sposta questo @Transactional dal repository al service"`, is an unusually sharp
near-miss because moving a concern between two layers literally satisfies `spans more than one Java/Spring
layer`. So the description is not wholly a property of the outcome. What the producer missed is the more
serious problem: the untested collision with `spring-architecture` (C1), and the fact that the real
undecidable shape is a prompt like `"Aggiungi il campo partita IVA al cliente"`, which implicitly spans
entity, repository, service, controller and migration while naming no layer. Neither eval contains that
shape.

## Proposed description edits

| Skill | Current problematic clause | Proposed replacement |
|---|---|---|
| `java-spring-standards` | `Trigger phrases: "Spring standards", "review this Spring code", "how should I structure this Spring module". ... Do not trigger directly from a coding prompt.` | `Trigger phrases: "what are our Spring standards", "the canonical Spring reference", "which layering rules do we follow". Returns reference material, not code. Do not use when the prompt asks for code to be written, reviewed, or fixed: use spring-expert (config), spring-architecture (layering), or spring-data-jpa (ORM).` |
| `rest-api-standards` | `Trigger phrases: "REST API design", "how should this endpoint look", "review this API contract", "OpenAPI authoring rules". ... Do not trigger directly from a coding prompt. It is invoked by the agents above.` | `Trigger phrases: "what are our REST standards", "the canonical API reference", "our OpenAPI authoring rules". Returns reference material, not a generated spec. Do not use when the prompt asks for an endpoint, a controller, or a spec to be written or reviewed: that is api-designer.` |
| `testing-standards` | `Trigger phrases: "testing standards", "how should I structure these tests", "AAA pattern", "JUnit template", "pytest fixture conventions". ... Do not trigger directly from a coding prompt.` | `Trigger phrases: "what are our testing standards", "the AAA convention we use", "our JUnit template", "our pytest fixture conventions". Returns reference material and complete test templates, not generated test code. Do not use when the prompt names code to be tested: that is test-writer.` |
| `postgresql-expert` | `Flyway is forbidden; if Flyway appears, this skill should redirect to Liquibase.` | `Flyway is forbidden. Once this skill is active and the project uses Flyway, redirect the work to Liquibase. The mere presence of the word Flyway in a prompt is not on its own a reason to activate this skill.` |
| `backend-orchestrator` | `ALWAYS use this skill when a backend task spans more than one Java/Spring layer:` | `ALWAYS use this skill when the prompt asks for working code across more than one Java/Spring layer:` and append `Do not use when the prompt asks where something belongs or how to layer it without asking for the code: that is spring-architecture.` |
| `frontend-orchestrator` | `ALWAYS use this skill when a frontend task spans multiple concerns:` | `ALWAYS use this skill when the prompt itself names more than one frontend concern (routing, state, styling, API) in the same request, asks to plan or review a whole FE module, or states that the framework is not yet chosen. A task that happens to touch several concerns but names only one is not enough: use the targeted skill.` |
| `tech-analyst` | `Trigger phrases: "analyse this repo", "map the modules", "what is the structure of this codebase", "index this project".` | `Trigger phrases: "give me the architecture report", "what are the bounded contexts", "produce the structural analysis of this project". Produces prose documents, not a queryable artefact. Do not use when the user wants to query the code rather than read a report: that is graphify-code-graph.` |
| `graphify-code-graph` | `Trigger phrases: "map this codebase", "what depends on X", "impact of changing Y", ...` | `Trigger phrases: "build a knowledge graph of the repo", "query the codebase", "what depends on X", "impact of changing Y", "how does Z flow through the code". Produces a queryable graph.json, not a written report.` (drop `"map this codebase"`) |
| `doc-expert` | `Do not use to generate enterprise LaTeX deliverables (use functional-document-generator or backend/frontend-documentation).` | `Produces markdown under docs/, never .tex. Do not use for any enterprise LaTeX deliverable: single-sided goes to backend-documentation or frontend-documentation, full-stack goes to documentation-orchestrator, functional goes to functional-document-generator.` |
| `documentation-orchestrator` | `ALWAYS use this skill when generating enterprise technical documentation for a full-stack project:` | Append `Technical documentation only. For a functional deliverable use functional-document-generator, and for business-oriented markdown under docs/ use doc-expert.` |
| `design-expert` | `Applies the company design system and coordinates with the framework skill` | `Applies the default in-house design system. When the end client has a named design system of its own, for example UniCredit Bricks, use that client skill instead. Coordinates with the framework skill` |
| `qwik-expert` | `Trigger phrases: "Qwik component", "resumability", "Qwik signals", "route loader", "minimum TTI".` | `Trigger phrases: "Qwik component", "resumability", "Qwik signals", "routeLoader$", "minimum TTI".` (removes the exact collision with `tanstack`) |
| `dependency-resolver` | `Do not use for routine version updates with no conflict.` | `Do not use when the prompt reports no failure: a plain request to bump, add, or remove a dependency is not a conflict, even for a major version.` |
| `refactoring-expert` | `Do not use to add new features or fix bugs (use the language developer skill or debugger).` | `Do not use to add new features or fix bugs (use the language developer skill or debugger). When the code is Angular, React, Vue, or Qwik and the request is framework-idiomatic, use that framework skill instead.` |
| `angular-expert` | Trigger phrase `"Angular FE refactoring"` | `"refactor this Angular component or module"` (keeps the intent, removes the bare overlap with refactoring-expert's `"refactor this"`) |
| `python-to-java-migration-expert` | `Use it after the target architecture is defined, to produce module-by-module migration specifications.` | `Use it after the target architecture is defined, to produce module-by-module Python to Java migration specifications.` (restores the language signal the eval positive currently relies on it not needing) |
