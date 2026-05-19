# Method — `frontend-scaffolder`

> Reference doc for `frontend-scaffolder`. Extracted from the
> agent body to keep it under the 10 000-char rubric ceiling.
> Read at runtime when the agent is dispatched.

## Method

### 1. Workspace skeleton

Read `workspace-config.md` (Workspace skeleton section). Produce a clean
Angular 18+ workspace (or version per ADR-002) with standalone components
by default. `package.json` honors ADR-002 for Angular version, `rxjs`,
optional `@ngx-translate/core` if i18n hinted by Phase 1, JWT lib per
ADR-003, and dev deps (`@angular/cli`, `karma`, `jest`, `playwright`,
`@openapitools/openapi-generator-cli`).

### 2. OpenAPI typed client

Read `workspace-config.md` (OpenAPI typed client section). Default to
**Strategy A** — generate at build time via
`@openapitools/openapi-generator-cli` with `prebuild` hook. Use Strategy
B (hand-written models) only if the team rejects code generation;
document drift risk. Record the choice in `<frontend-dir>/README.md`.

### 3. Core layer

Read `code-skeletons.md` (Core layer section). Emit interceptors (auth,
error, correlation-id), guards (auth, role), and core services (auth,
notification, error-handler). Each interceptor/service header comment
references the ADR it implements and the cross-cutting concern.

### 4. Shared layer

Read `code-skeletons.md` (Shared layer section). Emit shared components
(loader, error-display, data-table, form-error), pipes, and the
`models/` directory (hand-written under Strategy B).

### 5. Feature modules (one per BC)

Read `code-skeletons.md` (Feature modules + Screens to components +
user-flows → routing sections). For each BC in
`.refactoring-kb/00-decomposition/bounded-contexts.md`, scaffold a feature
folder with `<feature>.routes.ts` (lazy entry), `pages/` (one component
per Phase 1 screen S-NN), and `services/<feature>.service.ts`
(orchestration over the generated `*Api`). Component header comments
reference S-NN, UC-NN(s), and the AS-IS Streamlit source ref. In
`scaffold-todo` mode (default), templates render the happy path; complex
interactions carry `TODO(BC-NN, UC-NN)` markers.

### 6. State management

ADR-002 should specify: signals (default Angular 17+) or NgRx.

Default scaffolder choice: **signals + service-as-store**. Keep it
simple. Migrate to NgRx only when complexity demands (rare for typical
enterprise apps).

If ADR-002 specifies NgRx: scaffold the store skeleton (one feature
slice per BC: actions, reducer, selectors, effects). Otherwise: keep
state in feature services with signals.

### 7. Streamlit-specific translations (if AS-IS is Streamlit)

If Phase 1 identifies Streamlit pages, read `streamlit-translations.md`
and apply the canonical AS-IS↔TO-BE mapping (session_state → signals,
`st.cache_data` → `shareReplay(1)`, `st.rerun()` → reactive CD,
`st.file_uploader` → multipart, `st.dataframe` → `DataTableComponent`,
charts → ADR-002 lib, widget callbacks → template events, top-level
script → `ngOnInit`). Each component replacing a Streamlit page records
the AS-IS source ref. Skip this step entirely when AS-IS is not
Streamlit.

### 8. main.ts and app.config.ts

Read `app-shell.md` (main.ts + app.config.ts sections). Emit
`bootstrapApplication(AppComponent, appConfig)` and the `appConfig`
provider bundle (router, HttpClient with the three interceptors, zone
change detection with `eventCoalescing: true`).

### 9. README.md

Read `app-shell.md` (README.md section). Emit
`<frontend-dir>/README.md` with build instructions, project layout
overview, BC → feature module mapping, environment configuration, and
links to `docs/refactoring/4.6-api/openapi.yaml` and ADRs.

### 10. Self-check gate (HARD GATE — must pass before reporting `status: ok`)

A scaffold that compiles is NOT necessarily a scaffold a user can use.
The single most common failure mode of this agent is to leave the
default `ng new` placeholder template intact and forget to write any
navigation — the app then builds green but is unusable. The following
checks MUST all pass; if any fails, fix and re-emit before reporting.

```bash
# 10.1 No CLI placeholder strings survive anywhere under src/app/
test "$(grep -RlnE \
  'Hello, \{\{ title \}\}|Congratulations! Your app is running|Explore the Docs|Learn with Tutorials' \
  src/app/ | wc -l)" -eq 0

# 10.2 app.component.html delegates to the layout shell
grep -q "app-layout" src/app/app.component.html
grep -q "router-outlet" src/app/app.component.html

# 10.3 The layout component exists and has routerLinks
test -f src/app/core/layout/layout.component.ts
test -f src/app/core/layout/layout.component.html
grep -q "routerLink" src/app/core/layout/layout.component.html

# 10.4 Every protected route in app.routes.ts is referenced by the layout.
# Build a list of paths from app.routes.ts (`path: '...'` literals, minus
# `**`, `login`, redirect-only entries) and grep each in the layout html.
# Any path not referenced becomes a TODO marker in layout.component.ts
# with a `(BC-NN)` tag — never a silent omission.

# 10.5 Interceptors actually exist (app.config.ts must not reference
# files that the agent forgot to write).
test "$(ls src/app/core/interceptors/*.interceptor.ts | wc -l)" -ge 1
grep -q "withInterceptors" src/app/app.config.ts

# 10.6 No per-service Authorization header (must use the interceptor)
test "$(grep -rln 'Authorization.*Bearer' src/app --include='*.service.ts' | wc -l)" -eq 0
```

Report each check + outcome in the agent's `## Self-check` section of
the response. Do NOT claim `status: ok` if any check failed.

---
