# refactoring-supervisor — Phase 4 Step 6 UI smoke gate

Component tests, contract tests, and HTTP equivalence harnesses **all
run below the level at which the user perceives "the app is broken"**.
The InfoSync 2026-05 retrospective (`INFOSYNC-REFACTORING-AGENT-GAP-REPORT.md`
in the registry root) showed that the entire pipeline can declare green
(mvn 177/177 + ng test 200/200 + equivalence 204/204) while the FE shows
the Angular CLI welcome card on every route and has no navigation.

The UI smoke gate forces the supervisor to validate the app **the way a
human would** before sign-off.

## Procedure

1. Bring the backend up (`mvn spring-boot:run` or `java -jar
   target/*.jar` with the test/integration profile) and wait for
   `/actuator/health` to return `{"status":"UP"}`.
2. Run `mvn -q test -Dtest=BootSmokeTest` to confirm the default
   profile boots (`@SpringBootTest` without `@ActiveProfiles`). If this
   fails, the application cannot run with plain `java -jar` even if
   profile-scoped tests pass.
3. Bring the frontend dev server up (`ng serve` or `npm start`) and
   wait for the bundle-ready message.
4. Run the Playwright `smoke.spec.ts` produced by `frontend-test-writer`
   (see `agents/tobe-testing/frontend-test-writer.md` → "Mandatory:
   smoke.spec.ts"). The spec MUST cover every protected route from
   `app.routes.ts` and assert:
   - no Angular CLI placeholder strings on any page;
   - a feature `<h1>`/`<h2>` is visible on each route;
   - a nav link to each route exists in the layout shell;
   - no console errors and no failed network responses (status ≥ 400)
     on routes that should not produce them.
5. If `smoke.spec.ts` is absent, dispatch `frontend-test-writer` to
   create it first; do NOT declare Step 6 complete without it.
6. Capture screenshots of `/home` and three sample routes (one per
   bounded context). Embed them in
   `docs/refactoring/06-final-validation.md` and surface them in the
   pre-sign-off user message.

## Pre-sign-off user message (mandatory wording)

Do NOT replace the smoke-gate result with a numeric recap. Ask the user
an **explicit visual question** before requesting PO sign-off:

```
Phase 4 Step 6 — UI smoke gate result

✓ BootSmokeTest (default profile): pass
✓ smoke.spec.ts: <N>/<N> routes pass
✓ no CLI placeholder detected
✓ <N> nav links wired

Screenshots attached:
  - /home
  - /<bc-1-sample>
  - /<bc-2-sample>
  - /<bc-3-sample>

Visually inspect the screenshots. Do you see a coherent layout with a
working navigation menu, or do you see the Angular CLI welcome page or
a blank shell?

  [confirm-layout-ok] [reject — layout broken]

Sign-off cannot proceed until you confirm.
```

If the user answers `reject`, route back to `frontend-scaffolder`
(shell / nav / placeholder) or `hardening-architect` (CORS / auth) as
appropriate; do NOT capture sign-off.
