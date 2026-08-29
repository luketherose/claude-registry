# Method — `backend-scaffolder`

> Reference doc for `backend-scaffolder`. Extracted from the
> agent body to keep it under the 10 000-char rubric ceiling.
> Read at runtime when the agent is dispatched.

## Method

### 1. Project skeleton (Maven)

Read `pom-template.md`. Honour ADR-002 for groupId/artifactId/version,
Spring Boot version, Java version. Include the core, test, and plugin
dependencies listed there. Flyway is forbidden in TO-BE projects —
Liquibase is the only migration tool.

### 2. Package layout

Read `package-layout.md`. Top-level package (`com.<org>.<app>`) mirrors
ADR-001 (modular monolith vs microservices). For each BC from
`.refactoring-kb/00-decomposition/bounded-contexts.md`, materialise the
per-BC tree (`api/`, `application/`, `domain/` placeholder,
`infrastructure/` placeholder) plus the shared package (`config/`,
`error/`, `idempotency/`, `correlation/`).

### 3. Controller skeletons

Read `code-skeletons.md` (Controllers section). For each tag/operation in
the OpenAPI spec, generate a controller class under the matching BC's
`api/` package. Method signatures derive from OpenAPI operationIds; never
invent endpoints not in the spec.

### 4. DTOs

Read `code-skeletons.md` (DTOs section). For each OpenAPI schema referenced
by a BC's operations, generate a Java record. Choice between hand-written
records and `openapi-generator-maven-plugin` model generation: default to
hand-written for clarity, regenerate via plugin only on user request.
Document the choice in `<bc>/api/README.md`.

### 5. Service skeletons

Read `code-skeletons.md` (Service skeletons section). Method bodies throw
`UnsupportedOperationException` with TODO markers — this is intentional so
that calling them in a test fails loudly. `logic-translator` (W3c) replaces
the bodies; Phase 5 tests are xfailed for unfilled UCs.

### 6. Error handler (RFC 7807)

Read `error-and-security.md` (Error handler section). Emit
`shared/error/ProblemDetailExceptionHandler.java` as a `@RestControllerAdvice`
that extends `ResponseEntityExceptionHandler`. Required handlers:
- `@ExceptionHandler` for `NotFoundException`, `ValidationException`,
  `IdempotencyConflictException`, `ConstraintViolationException`,
  `NoResourceFoundException`, and a generic `Exception` handler with
  status 500 and SAFE message (no stack trace leak);
- **`@Override`** for `handleHttpRequestMethodNotSupported` (→ 405),
  `handleHttpMediaTypeNotSupported` (→ 415),
  `handleHttpMediaTypeNotAcceptable` (→ 406),
  `handleMethodArgumentNotValid` (→ 400 with per-field details). These
  exceptions are produced by `DispatcherServlet` before any
  `@ExceptionHandler` can claim them — only the protected overrides on
  `ResponseEntityExceptionHandler` integrate them into RFC 7807. Skipping
  the 405 override is the canonical bug that turns `GET` on a `POST`-only
  endpoint into HTTP 500.

Match Phase 2 security findings: no internal info leaks in `detail`.

### 7. Security config baseline

Read `error-and-security.md` (Security config section). Emit
`shared/config/SecurityConfig.java` as a baseline (CSRF disabled because
stateless, JWT resource server, CORS for FE origin via a `CorsConfigurationSource`
bean fed by `app.cors.allowed-origin-patterns`). `hardening-architect`
(W4) refines it with the final security headers, CSP, etc.

**Hard rule on CORS**: the `CorsConfigurationSource` bean is the **only**
place CORS is configured. The agent must NOT add `@CrossOrigin` on
individual controllers — duplicating the origin list on every controller
defeats the purpose of the centralised bean and was the cause of GAP-005
(127.0.0.1 vs localhost) in the InfoSync 2026-05 retrospective. Required
self-check at the end of step 7:

```bash
! grep -rln "@CrossOrigin" src/main/java   # must find nothing
```

### 8. application.yml

Read `application-yml-template.md`. Emit
`src/main/resources/application.yml`. `hardening-architect` adds tracing
and logging-format on top of this.

### 9. Application class

Read `code-skeletons.md` (Application class section). Emit
`src/main/java/com/<org>/<app>/Application.java`.

### 10. README + ARCHITECTURE.md

`<backend-dir>/README.md`: build instructions, package layout overview,
links to ADRs.

`<backend-dir>/ARCHITECTURE.md`: cross-references to
`.refactoring-kb/00-decomposition/` and OpenAPI; pointer to
`logic-translator`'s per-UC outputs.

---
