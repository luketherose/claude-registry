# Report — Lacune del registro e dell'agente di refactoring

**Sessione di riferimento:** validazione end-to-end del refactoring `InfoSync`
(`/Users/luca.la.rosa/dev/InfoSync`, branch `refactor/python-to-java-angular`),
prodotto dalle pipeline `refactoring-supervisor` → `refactoring-tobe-supervisor`
→ `tobe-testing-supervisor` (fasi 0–4 dichiarate completate).

**Stato dei fix:** il presente report **identifica** le lacune e propone le
modifiche al registro. **Non sono state ancora applicate** né al codice
`InfoSync` né ai prompt degli agenti — sono pronte per essere fatte in una
sessione separata su esplicita richiesta.

---

## 1. Quadro di sintesi

### 1.1 Cosa il pipeline dichiara verde

| Suite | Esito reale (ri-eseguito in questa sessione) |
|---|---|
| `mvn -q -DskipTests package` | exit 0 |
| `mvn test -Dspring.profiles.active=test` | **177 / 177 pass** |
| `npm run build` (Angular 17) | exit 0, 31 lazy chunk |
| `ng test --watch=false --browsers=ChromeHeadless` | **200 / 200 pass** |
| `pytest tests/tobe/` vs backend live (profilo test) | **204 / 204 pass** |

Il report `docs/refactoring/06-final-validation.md` **non mente** sui numeri:
tutto compila, tutto passa.

### 1.2 Cosa il pipeline ha sistematicamente mancato

| # | Problema | Severità | Visibile a |
|---|---|---|---|
| G1 | `app.component.html` lasciato come template default di Angular CLI (336 righe di "Hello, infosync-frontend / Congratulations 🎉"). Ogni pagina autenticata mostra quel placeholder **sopra** il componente reale. | Critica | Qualsiasi utente che esegue `ng serve` |
| G2 | Nessun shell / nav / sidebar / header in tutta l'app. Dopo il login si atterra su `/home` (un `<h1>` + bottone logout) e si può raggiungere ognuna delle 22 feature solo digitando l'URL a mano. | Critica | Qualsiasi utente |
| G3 | `frontend/src/app/core/interceptors/` esiste ma è **vuoto**. Ogni service ri-implementa a mano `Authorization: Bearer ${token}` (≥ 15 occorrenze). | Alta — code smell ma funziona | Solo chi legge il codice |
| G4 | `GlobalExceptionHandler` non gestisce `HttpRequestMethodNotSupportedException`. Un `GET` su un endpoint POST-only restituisce **500** invece di **405**. Esempio reale: `GET /api/minibond/workflows` → 500. | Media — contratto API rotto | Frontend e client esterni |
| G5 | `@CrossOrigin(origins = "http://localhost:4200")` su **23 controller**. La stessa macchina `http://127.0.0.1:4200` viene rifiutata dal preflight CORS (preflight 403). | Bassa — config | Sviluppatori che usano 127.0.0.1 invece di localhost |
| G6 | Nessun test E2E Playwright in tutto il repo (`tests/e2e/` non esiste, nessuno `.spec.ts` Playwright). Il piano `tobe-testing-supervisor` Wave 1 prevedeva un E2E per ogni user-flow — è stato saltato dalla pipeline "absorbed testing" della Fase 4. | Alta — copertura mancante | Pipeline CI futura |
| G7 | Build emette warning NG8107 in `admin.component.ts:68` e `conversation-logger.component.ts:42` (optional-chain su tipi non-nullable). Avvertimenti reali del compilatore Angular, ignorati. | Bassa | Build log |
| G8 | Warning NG8107 in build (`?.` su non-null types) — `admin.component.ts:68`, `conversation-logger.component.ts:42`. | Bassa | Build log |

> G1 + G2 sono la causa di quello che l'utente ha percepito come "syntax
> errors / missing components / missing imports". Tecnicamente non c'è nessun
> errore di sintassi né import mancante (il `tsc` e l'`ng build` passano):
> l'app è "rotta" perché **manca interamente il guscio applicativo**, non
> perché qualcosa è scritto male.

---

## 2. Perché il sistema dei controlli automatici non li ha intercettati

La pipeline ha eseguito molti controlli — ma tutti **dentro** il livello a cui
l'errore non era visibile:

1. **`mvn test` (JUnit)** verifica controller + service in isolamento con
   MockMvc → non ha mai mosso un GET su `/api/minibond/workflows`, quindi
   G4 era invisibile.
2. **`ng test` (Karma + Jasmine)** monta ogni componente in isolamento → non
   monta mai `AppComponent` con il routing reale → G1 e G2 sono invisibili.
3. **`pytest tests/tobe/`** è una equivalence-harness che parla HTTP al
   backend. **Non apre mai un browser**, non visita mai un URL del frontend
   → G1, G2, G3 sono invisibili.
4. **`docs/refactoring/06-final-validation.md`** ha eseguito 12 "business-flow
   smoke" — tutti `curl` o equivalenti, **mai un browser**. Anche qui G1+G2
   invisibili.
5. **`phase4-challenger`** (l'adversarial review del registro che dovrebbe
   trovare drift) ha 7 check ma nessuno mira allo shell o alla navigazione
   utente — grep per `shell|nav|router-outlet|placeholder` nel suo prompt
   restituisce 0 match.
6. **`tobe-testing-challenger`** non ha mai girato perché la Fase 5 separata
   non è stata eseguita (il `refactoring-supervisor` ha "assorbito" il
   testing nella Fase 4 incrementale, perdendo il challenger).

In una parola: **il pipeline misura la correttezza dei pezzi, mai
l'esperienza di un utente che logga e prova ad usare l'app**.

---

## 3. Lacune nei prompt del registro

Mappa lacuna-osservata → file del registro responsabile → modifica
proposta. Path relativi a `claude-catalog/`.

### G1 — App shell placeholder lasciato

**Responsabile:** `agents/refactoring-tobe/frontend-scaffolder.md`
+ il template `docs/refactoring-tobe/frontend-scaffolder/app-shell.md`.

**Bug del registro:** `app-shell.md` prescrive `main.ts` e `app.config.ts`
ma **non** prescrive il contenuto di `app.component.html`. Il file di
default emesso da `ng new` (336 righe di template "Hello/Congratulations")
sopravvive intatto al passaggio dell'agente.

**Fix proposto:** aggiungere a `app-shell.md` una sezione
`## app.component.html` con:
- un template minimale `<app-layout><router-outlet /></app-layout>`
- istruzione esplicita: *"sovrascrivere completamente il template default
  emesso da `ng new`; nessuna riga 'Hello, {{ title }}' o 'Congratulations'
  deve sopravvivere"*.

### G2 — Nessuna navigation / shell

**Responsabile:** `agents/refactoring-tobe/frontend-scaffolder.md`
+ `docs/refactoring-tobe/frontend-scaffolder/code-skeletons.md`.

**Bug del registro:** `code-skeletons.md` documenta interceptor, base
service, error handler — ma non un componente `core/layout/` con sidenav
indicizzata sui bounded context. L'agente non sa che è suo dovere produrre
un menu di navigazione.

**Fix proposto:** aggiungere a `code-skeletons.md` la sezione
`## core/layout` con il pattern standard:
```
core/layout/layout.component.{ts,html,scss}
  - sidenav con un'entry per ogni bounded context
  - badge admin-only visibile solo se AuthService.isAdmin()
  - hide-when-anonymous: si nasconde su `/login`
  - emette CSS variables UniCredit (vedi unicredit-design-system skill)
```
+ aggiungere in `frontend-scaffolder.md` la checklist:
*"l'output deve passare il check `grep -q 'router-outlet' app.component.html
&& grep -rq 'routerLink' src/app/core/layout/`"*.

### G3 — Interceptor auth non scritto

**Responsabile:** `agents/refactoring-tobe/frontend-scaffolder.md`.

**Bug del registro:** `app-shell.md` dichiara
`withInterceptors([authInterceptor, correlationIdInterceptor,
errorInterceptor])` ma `code-skeletons.md` mostra il codice **solo** di
`authInterceptor` come esempio, e non vincola l'agente a crearlo davvero.
Risultato: l'agente cita gli interceptor nell'`app.config.ts` ma poi
**non emette i file** (la cartella `core/interceptors/` rimane vuota e il
build fallirebbe — sicché l'agente toglie anche il `withInterceptors([...])`
dal config per non rompere il build).

**Fix proposto:** in `frontend-scaffolder.md` rendere obbligatorio il
self-check finale:
```
- ls src/app/core/interceptors/*.ts deve restituire ≥ 3 file
- app.config.ts deve contenere withInterceptors([...]) non vuoto
- grep -rq 'Authorization.*Bearer' src/app/**/*.service.ts deve essere 0
  (ogni service usa l'interceptor, NON imposta l'header da sé)
```

### G4 — `HttpRequestMethodNotSupportedException` → 500

**Responsabile:** `docs/refactoring-tobe/backend-scaffolder/error-and-security.md`.

**Bug del registro:** il template del `ProblemDetailExceptionHandler`
elenca handler per `NotFoundException`, `ValidationException`,
`IdempotencyConflictException`, `ConstraintViolationException`,
`MethodArgumentNotValidException` + generico — **manca** l'override di
`handleHttpRequestMethodNotSupported` di `ResponseEntityExceptionHandler`.
Risultato: HTTP 405 cade nel `@ExceptionHandler(Exception.class)` generico
e diventa 500.

**Fix proposto:** aggiungere all'esempio nel template:
```java
@Override
protected ResponseEntity<Object> handleHttpRequestMethodNotSupported(
        HttpRequestMethodNotSupportedException ex,
        HttpHeaders headers, HttpStatusCode status, WebRequest req) {
    ProblemDetail pd = ProblemDetail.forStatus(HttpStatus.METHOD_NOT_ALLOWED);
    pd.setTitle("Method not allowed");
    pd.setDetail("Method " + ex.getMethod() + " not supported on this resource");
    pd.setProperty("supportedMethods", ex.getSupportedHttpMethods());
    pd.setProperty("correlationId", MDC.get("correlationId"));
    return ResponseEntity.status(HttpStatus.METHOD_NOT_ALLOWED).body(pd);
}
```
e analogamente per `HttpMediaTypeNotSupportedException`,
`HttpMediaTypeNotAcceptableException`, `NoHandlerFoundException`,
`AsyncRequestTimeoutException`.

### G5 — CORS `127.0.0.1` rifiutato

**Responsabile:** `docs/refactoring-tobe/backend-scaffolder/error-and-security.md`
+ `agents/refactoring-tobe/backend-scaffolder.md`.

**Bug del registro:** il template `setAllowedOrigins(List.of("http://localhost:4200"))`
hardcoda **un solo origin**. Inoltre nel codice `InfoSync` reale i singoli
controller usano `@CrossOrigin(origins = "http://localhost:4200")` invece
del `CorsConfigurationSource` globale — l'agente ha duplicato 23 volte la
stessa annotation invece di centralizzare.

**Fix proposto:**
- nel template: `setAllowedOriginPatterns(List.of("http://localhost:*",
  "http://127.0.0.1:*"))` + nota *"in produzione popolare da
  `app.cors.allowed-origins` in application.yml"*.
- vietare `@CrossOrigin` sui controller (lint rule documentata nel prompt):
  *"CORS è configurato una sola volta in SecurityConfig.corsConfigurationSource();
  NESSUN controller deve dichiarare @CrossOrigin"*.

### G6 — Test E2E Playwright assenti

**Responsabile:** `agents/refactoring-supervisor.md` (top-level) +
`agents/tobe-testing/frontend-test-writer.md`.

**Bug del registro:** la nuova fase "absorbed testing" del
`refactoring-supervisor` (Fase 4 progressiva test-driven) ha **rimosso**
il passaggio per `tobe-testing-supervisor` che a sua volta avrebbe
delegato a `frontend-test-writer` per scrivere Playwright E2E. Risultato:
non esiste E2E, non esiste un test che faccia "login → navigate to
/ma/pipeline → assert page renders". Quel test avrebbe trovato G1+G2
in 30 secondi.

**Fix proposto:**
- in `refactoring-supervisor.md`, al passo Step 6 (Final Validation) della
  Fase 4 rendere obbligatorio un check Playwright minimale:
  ```
  - npx playwright test tests/e2e/smoke.spec.ts deve passare
  - smoke.spec.ts deve: aprire /, fare login, visitare ogni route da
    app.routes.ts, asserire console.errors === 0 e che il body contenga
    almeno un <h1>/<h2> SPECIFICO di quella feature (non placeholder)
  ```
- in `frontend-test-writer.md` aggiungere il caso "shell-smoke" come
  scenario E2E obbligatorio, indipendente dagli user flow funzionali.

### G7 / G8 — Warning di build ignorati

**Responsabile:** `agents/refactoring-tobe/refactoring-tobe-supervisor.md`
e/o `agents/refactoring-supervisor.md`.

**Bug del registro:** nessun gate sui warning di `ng build`. L'agente
considera "verde" anche un build con warning Angular ufficiali.

**Fix proposto:** aggiungere un soft gate documentato:
```
- Se ng build emette ≥ 1 warning NG8xxx, registrare ciascuno
  in docs/refactoring/_meta/build-warnings.md con
  decisione esplicita: fix | accepted-with-rationale.
```

---

## 4. Lacune cross-cutting nei "challenger"

Sia `phase4-challenger` sia `tobe-testing-challenger` sono **agenti
adversariali** che dovrebbero cercare buchi. Entrambi hanno fallito su
G1 e G2 perché:

- **`phase4-challenger`** ha 7 check (coverage gaps, OpenAPI↔code drift,
  ADR completeness, AS-IS bug carry-over, perf hypothesis sanity, security
  regression, equivalence claims integrity, inverse drift). Nessuno è
  *"navigation map: per ogni route in `app.routes.ts` esiste un link
  navigabile dall'UI?"*.

  **Fix proposto:** aggiungere a `agents/refactoring-tobe/phase4-challenger.md`
  un check #8: *"Navigation reachability — ogni `path:` in `app.routes.ts`
  (escluse rotte tecniche come `**`, `login`) deve essere referenziato
  almeno una volta in un template `[routerLink]` o `router.navigate`
  raggiungibile dal layout principale; emettere FINDING-NAV-X per ogni
  route orfana"*.

- **`tobe-testing-challenger`** ha 8 check. Nessuno verifica che esista
  almeno un test E2E shell-level.

  **Fix proposto:** aggiungere check #9: *"Shell-coverage — esiste almeno
  un test Playwright che (a) faccia login, (b) visiti ≥ 80% delle route
  protette, (c) asserisca assenza di placeholder string come
  'Hello, {{ title }}' o 'Congratulations'"*.

---

## 5. Lacuna di "human-in-the-loop"

Il `refactoring-supervisor` ha checkpoint HITL ben definiti tra le fasi.
Ma il messaggio mostrato all'utente al checkpoint post-Fase 4 si limita a
elencare i **conteggi** (`177/177 pass`, `200/200 pass`, `31 chunks`).
**Non viene mai mostrato all'utente uno screenshot, una sequenza di URL
visitati, o un'istruzione di tipo "apri `http://localhost:4200` e dimmi se
vedi il menu"**.

L'utente di questa sessione ha individuato il problema **solo perché lo ha
aperto manualmente** — il pipeline non lo prevede.

**Fix proposto:** in `agents/refactoring-supervisor.md`, al gate finale
della Fase 4, sostituire il riepilogo numerico con:
```
1. avvia backend + frontend
2. apri http://localhost:4200 in Chromium headed
3. esegui login admin/admin
4. fai screenshot di /home + di 3 route a campione (una per bounded context)
5. mostra gli screenshot all'utente con la domanda esplicita:
   "Vedi un layout coerente con menu di navigazione, oppure vedi
    placeholder/welcome page di Angular CLI? Conferma per chiudere la
    fase."
```

---

## 6. Riepilogo modifiche al registro (formato actionable)

| File del registro | Cosa modificare |
|---|---|
| `claude-catalog/docs/refactoring-tobe/frontend-scaffolder/app-shell.md` | Aggiungere sezione `## app.component.html` con template di shell minimale e divieto esplicito di lasciare il default `ng new`. |
| `claude-catalog/docs/refactoring-tobe/frontend-scaffolder/code-skeletons.md` | Aggiungere sezione `## core/layout` con pattern sidenav per-BC. |
| `claude-catalog/agents/refactoring-tobe/frontend-scaffolder.md` | Aggiungere self-check finale su interceptor scritti, `app.component.html` sovrascritto, almeno un `routerLink` nel layout. |
| `claude-catalog/docs/refactoring-tobe/backend-scaffolder/error-and-security.md` | Aggiungere handler espliciti per `HttpRequestMethodNotSupportedException`, `HttpMediaTypeNotSupportedException`, `HttpMediaTypeNotAcceptableException`, `NoHandlerFoundException`. Cambiare CORS a `setAllowedOriginPatterns` con localhost + 127.0.0.1. |
| `claude-catalog/agents/refactoring-tobe/backend-scaffolder.md` | Vietare `@CrossOrigin` sui singoli controller. |
| `claude-catalog/agents/refactoring-tobe/phase4-challenger.md` | Aggiungere check #8 "Navigation reachability". |
| `claude-catalog/agents/tobe-testing/frontend-test-writer.md` | Aggiungere "shell-smoke" come scenario E2E obbligatorio. |
| `claude-catalog/agents/tobe-testing/tobe-testing-challenger.md` | Aggiungere check #9 "Shell-coverage". |
| `claude-catalog/agents/refactoring-supervisor.md` | Gate finale Fase 4: avvio reale dell'app + screenshot route + domanda esplicita all'utente. |

---

## 7. Fix lato InfoSync (separati dai fix al registro)

Indipendentemente dalle modifiche al registro, il progetto InfoSync ha
bisogno di:

1. Riscrivere `frontend/src/app/app.component.html` (336 righe → ~10 righe
   con `<app-layout><router-outlet /></app-layout>`).
2. Creare `frontend/src/app/core/layout/layout.component.{ts,html,scss}`
   con sidenav su 22 route, gated da `permissions` di `AuthService`.
3. Creare `frontend/src/app/core/interceptors/auth.interceptor.ts` e
   registrarlo in `app.config.ts`; rimuovere le 15+ `headers()` duplicate
   nei service.
4. In `backend/.../shared/error/GlobalExceptionHandler.java` aggiungere
   l'override di `handleHttpRequestMethodNotSupported`.
5. Aggiornare i 23 `@CrossOrigin` a una `CorsConfigurationSource` unica
   con `setAllowedOriginPatterns(List.of("http://localhost:*",
   "http://127.0.0.1:*"))`.
6. Risolvere i due NG8107 in `admin.component.ts:68` e
   `conversation-logger.component.ts:42`.
7. Aggiungere `tests/e2e/smoke.spec.ts` Playwright che faccia login +
   smoke su tutte le route.

Le 7 azioni sopra hanno una stima di ~1–2 giornate di lavoro per uno
sviluppatore Angular+Spring; possono essere eseguite in branch
separato dall'agente `developer-frontend` + `developer-java-spring` su
richiesta esplicita.

---

## 8. Lezione architetturale per il registro

Il pattern ricorrente: **tutti gli agenti di test e tutti i challenger
operano sopra astrazioni** (controller test, service test, equivalence
harness HTTP). Nessuno opera al livello "utente che apre il browser".

Per un refactoring Streamlit → Angular questa è una lacuna grave perché
il valore percepito dell'app è esattamente quello che l'utente vede
nel browser. La pipeline può legittimamente dichiarare "tutto verde"
mentre l'app è inutilizzabile.

Raccomandazione strategica: introdurre un nuovo sub-agente
`ui-smoke-validator` (Wave 5 post-hardening) il cui unico compito è:
*"avvia tutto, apri Chrome headed, prova a usare l'app come un utente
finale, salva screenshot, fai un report sulla qualità percepita"*.
Tools: `Bash` + `WebFetch` + browser-MCP. Output: PDF con screenshot
e dispositivo confermato dall'utente prima di chiudere la fase.
