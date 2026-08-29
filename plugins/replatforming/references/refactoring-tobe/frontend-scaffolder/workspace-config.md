# Workspace config

> Reference doc for `frontend-scaffolder`. Read at runtime when generating
> the Angular workspace skeleton (Method step 1 — workspace skeleton, and
> Method step 2 — OpenAPI typed client).

## Workspace skeleton

Produce a clean Angular 18+ workspace (or version per ADR-002) with
standalone components by default.

```
<frontend-dir>/
├── angular.json
├── package.json
├── tsconfig.json
├── tsconfig.app.json
├── tsconfig.spec.json
├── .eslintrc.json
├── README.md
└── src/
    ├── main.ts                              (bootstrapApplication)
    ├── index.html
    ├── styles.scss
    ├── environments/
    │   ├── environment.ts                   (dev: API base URL, etc.)
    │   └── environment.prod.ts
    └── app/
        ├── app.config.ts                    (providers, router config)
        ├── app.routes.ts                    (top-level routing — lazy)
        ├── app.component.ts
        ├── app.component.html
        ├── app.component.scss
        ├── core/
        ├── shared/
        └── features/
```

`package.json` honors ADR-002:

- `@angular/core` etc. at the version in ADR-002 (default 18)
- `rxjs` (latest matching Angular)
- `@ngx-translate/core` if i18n hinted by Phase 1
- `@auth0/angular-jwt` or similar per ADR-003 if Bearer JWT — or none if
  using `@angular/common/http` interceptors directly
- dev deps: `@angular/cli`, `karma`, `jest` (preferred; configure to
  replace karma if ADR-002 specifies), `playwright` (for E2E in Phase 5),
  `@openapitools/openapi-generator-cli` (if generating client typings
  from openapi.yaml at build time)

## OpenAPI typed client

Two strategies:

### Strategy A — Generate at build time (default)

Configure `@openapitools/openapi-generator-cli` in `package.json` to run
on `prebuild`:

```json
"scripts": {
  "openapi:generate": "openapi-generator-cli generate -i ../docs/refactoring/4.6-api/openapi.yaml -g typescript-angular -o src/app/api/generated --additional-properties=npmName=app-api,modelPropertyNaming=camelCase,fileNaming=kebab-case",
  "prebuild": "npm run openapi:generate",
  "build": "ng build"
}
```

Generated typings live at `src/app/api/generated/` — gitignored if the
team prefers regeneration; or committed for traceability (recommended
for `infosync`-style enterprise migrations: commit, traceable diff).

### Strategy B — Hand-written models

If the team rejects code generation: hand-write models under
`src/app/shared/models/` matching the OpenAPI schemas. Less robust
(drift risk).

The scaffolder defaults to Strategy A. Document the choice in
`<frontend-dir>/README.md`.
