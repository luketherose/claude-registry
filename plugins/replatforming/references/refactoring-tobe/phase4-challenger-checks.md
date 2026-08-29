# Method: ten checks (`phase4-challenger`)

> Reference doc for `phase4-challenger`. Extracted from the
> agent body to keep it under the 10 000-char rubric ceiling.
> Read at runtime when the agent is dispatched.

## Contents

- [Method: ten checks](#method-ten-checks): the ten checks, all reporting findings in the common `Type` / `Where` / `Description` / `Suggested fix` / `Severity` shape.
  - [Check 1: AS-IS↔TO-BE traceability](#check-1-as-isto-be-traceability): the matrix connecting every Phase 1 use case to its TO-BE manifestation across four layers.
  - [Check 2: OpenAPI↔code drift](#check-2-openapicode-drift): operations without a controller method, and controller methods without a use-case reference.
  - [Check 3: ADR completeness](#check-3-adr-completeness): every major decision has its ADR.
  - [Check 4: AS-IS bug carry-over consistency](#check-4-as-is-bug-carry-over-consistency): deferred and escalated Phase 3 bugs appear in the roadmap.
  - [Check 5: Performance hypothesis sanity](#check-5-performance-hypothesis-sanity): high and critical Phase 2 bottlenecks are addressed in the TO-BE design.
  - [Check 6: Security regression](#check-6-security-regression): OWASP categories that were missing or partial in the AS-IS are covered.
  - [Check 7: Equivalence claims integrity](#check-7-equivalence-claims-integrity): equivalence targets in the roadmap are backed by real Phase 3 baseline metrics.
  - [Check 8: AS-IS-only leak in TO-BE (inverse drift)](#check-8-as-is-only-leak-in-to-be-inverse-drift): AS-IS-only tokens leaking into TO-BE outputs.
  - [Check 9: AS-IS source modification (forbidden)](#check-9-as-is-source-modification-forbidden): `git status` proves no AS-IS source file was modified.
  - [Check 10: Frontend navigation reachability](#check-10-frontend-navigation-reachability): every protected route is reachable through the UI, not only by typing the URL.

## Method: ten checks

For each check, list every finding using the common shape (`Type`,
`Where`, `Description`, `Suggested fix`, `Severity`). See
`checklist-templates.md` → "Finding shape" for the enumerations.

### Check 1: AS-IS↔TO-BE traceability

This is the BIG one. Build the matrix that connects every Phase 1 UC to
its TO-BE manifestation across the four layers (openapi operation →
controller → service → frontend component for each S-NN).

Tag each UC as `fully covered`, `partial` (with documented exception in
`4.6-api/design-rationale.md`), or `uncovered`.

→ See `checklist-templates.md` → Check 1 for the layer hierarchy and the
JSON schema written to `.refactoring-kb/02-traceability/as-is-to-be-matrix.json`.

### Check 2: OpenAPI↔code drift

Cross-check:
- every operation in openapi.yaml has a matching method in a Java
  controller (operationId match)
- every Java controller method has an `x-uc-ref` operation in openapi.yaml
- every DTO field in openapi.yaml schema is present in the Java DTO
  (and vice versa)
- response status codes documented in openapi.yaml match
  `ResponseEntity.status(...)` in controllers

Drift here is a `blocking` issue (the contract is the contract).

### Check 3: ADR completeness

Check that:
- every major decision documented:
  - architecture style → ADR-001 (decomposition-architect)
  - target stack → ADR-002 (decomposition-architect)
  - auth flow → ADR-003 (api-contract-designer)
  - observability → ADR-004 (hardening-architect)
  - security baseline → ADR-005 (hardening-architect)
- every ADR has all Nygard sections (Status, Context, Decision,
  Consequences, Alternatives)
- every ADR is referenced from at least one worker output (no orphan
  ADRs)
- no MAJOR design decision present in non-ADR docs (e.g., a database
  choice declared in roadmap but no ADR to back it)

Severity:
- missing required ADR: `blocking`
- ADR missing a Nygard section: `needs-review`
- orphan ADR: `nice-to-have`

### Check 4: AS-IS bug carry-over consistency

For each entry in Phase 3 `_meta/as-is-bugs-found.md` with status
`deferred` or `escalated`:
- the roadmap (`docs/refactoring/roadmap.md`) must include it in the
  carry-over table
- the affected milestone has it in scope (with disposition: fix-in-flight,
  document-as-limitation, descope-with-rationale)
- if disposition is `fix-in-flight`: the corresponding logic-translator
  output for the relevant UC has implemented the fix (verify by reading
  the service method body, should not have an
  `UnsupportedOperationException` for that branch)

Severity:
- deferred bug not in roadmap: `blocking`
- bug disposition unclear: `needs-review`

### Check 5: Performance hypothesis sanity

Phase 2 `06-performance/performance-bottleneck-report.md` lists
hypothesized perf hotspots. For each:
- if severity high/critical: the TO-BE design (decomposition,
  data-mapper, logic-translator, hardening) addresses it explicitly
  (e.g., N+1 query → repository query method with JOIN; missing cache
  → Spring caching annotation; blocking I/O → async / virtual thread)
- the ADR-002 + ADR-004 combination doesn't introduce NEW
  hypothesized regressions (e.g., adding heavy serialization to log
  every request)
- baseline metrics from Phase 3 (if write+execute mode ran) should be
  within reach for the TO-BE per ADR-002 / ADR-004 choices

Severity:
- high/critical perf hotspot ignored in TO-BE: `needs-review`
- TO-BE design introduces new perf risk: `needs-review` to
  `blocking` depending on impact

### Check 6: Security regression

Phase 2 `08-security/owasp-top10-coverage.md` lists per-category
status. For each category that was `missing` or `partial` in AS-IS:
- the TO-BE has a mitigation (verify by checking ADR-005 + actual
  Java/TS code)
- the TO-BE doesn't introduce a NEW gap (e.g., hardening-architect
  disabled CSRF without proper stateless reasoning → already in
  ADR-005, but verify)

For Phase 2 `08-security/security-findings.md` SEC-NN entries:
- each one has a TO-BE fix or an explicit deferral

Severity:
- AS-IS security gap not addressed in TO-BE: `blocking`
- new security gap introduced: `blocking`

### Check 7: Equivalence claims integrity

The roadmap and milestones state equivalence targets ("100% UCs vs
Phase 3 oracle", "p95 ≤ 110% of baseline"). Verify:
- Phase 3 baseline metrics actually exist (read
  `docs/analysis/03-baseline/_meta/benchmark-baseline.json`)
- the % thresholds in the roadmap match the supervisor's bootstrap
  policy (no surprise tightening or loosening)
- equivalence claims aren't made for UCs that have no Phase 3 test
  (uncovered UCs cannot have an equivalence target)

Severity:
- equivalence promise without baseline: `blocking`
- threshold mismatch: `needs-review`

### Check 8: AS-IS-only leak in TO-BE (inverse drift)

Scan TO-BE outputs for AS-IS-only token leaks using the regex in
`checklist-templates.md` → Check 8. That doc also enumerates the
legitimate vs forbidden contexts (comments / ADR resolution OK; runtime
code / undocumented design-doc bodies NOT OK).

Severity:
- leak in code: `blocking`
- leak in design doc without ADR ref: `needs-review`

### Check 9: AS-IS source modification (forbidden)

Run `git status` (Bash) and verify no AS-IS source files (anything
outside `<backend-dir>/`, `<frontend-dir>/`, `docs/refactoring/`,
`.refactoring-kb/`, `docs/adr/ADR-00{1,2,3,4,5}-*.md`) are modified.

Phase 3 had the same rule. It's reiterated here because Phase 4
workers have Edit access for some scaffolds; mistakes can leak.

Severity:
- AS-IS source modified: `blocking` (revert immediately)

### Check 10: Frontend navigation reachability

Verify the user can actually reach every protected route from the UI,
not just by typing the URL. Source of truth: `<frontend-dir>/src/app/app.routes.ts`.

For each `path: '...'` entry (excluding the literal `**`, `login`,
public routes, and pure redirects like `{ path: '', redirectTo: ... }`):

1. The path must appear in at least one `[routerLink]` / `routerLink="..."`
   / `router.navigate(['/...'])` reachable from `app.component.html`
   transitively (the app shell, usually a `LayoutComponent` under
   `core/layout/`).
2. `app.component.html` must NOT contain the Angular CLI default
   placeholder strings (`Hello, {{ title }}`, `Congratulations! Your app
   is running`, `Explore the Docs`, `Learn with Tutorials`). If it does,
   record FINDING-NAV-PLACEHOLDER as `blocking`: the app is unusable
   regardless of test counts.
3. The shell must reference the user's permissions to gate admin-only
   routes (grep `AuthService` or `hasPermission` in `layout.component.ts`).

Concrete checks the challenger runs:

```bash
# 10.1 placeholder must not survive
! grep -RnE "Hello, \{\{ title \}\}|Congratulations! Your app is running|Explore the Docs|Learn with Tutorials" \
  <frontend-dir>/src/app/

# 10.2 layout shell exists
test -f <frontend-dir>/src/app/core/layout/layout.component.ts
test -f <frontend-dir>/src/app/core/layout/layout.component.html

# 10.3 every protected route is linked
# parse paths from app.routes.ts -> grep each in layout.component.html
```

Severity:
- placeholder strings present → `blocking` (FINDING-NAV-PLACEHOLDER)
- shell file absent → `blocking` (FINDING-NAV-NO-SHELL)
- route present in `app.routes.ts` but unreferenced anywhere in
  the UI tree → `high` (FINDING-NAV-ORPHAN-ROUTE-<slug>): one finding
  per orphan route.

> Rationale: the InfoSync 2026-05 retrospective found that Phase 4
> declared green (177/177 + 200/200 + 204/204) while the FE was
> unusable because the Angular CLI placeholder survived and there was
> no nav. Component unit tests and HTTP equivalence tests both run
> *below* the level at which this gap lives. Check 10 enforces it.

---
