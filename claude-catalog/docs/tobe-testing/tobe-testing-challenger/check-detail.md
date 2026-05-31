# tobe-testing-challenger — check details

Detailed definitions for the cross-cutting checks that the agent body
keeps as one-line summaries. Reference doc — read on demand per check.

## Check 9 — Shell coverage in E2E

Verify that the FE test suite includes an end-to-end smoke spec that
actually drives the application as a user — not just isolated component
tests. Read `<frontend-dir>/tests/e2e/smoke.spec.ts` (or equivalent).

Required properties of the smoke spec:

1. It iterates over **every protected route in `app.routes.ts`** (or has
   a hard-coded list that the challenger can diff against the routes
   file — any orphan route generates one CHL per orphan).
2. It asserts the page does NOT contain Angular CLI placeholder strings
   (`Hello, infosync-frontend`, `Congratulations! Your app is running`,
   `Explore the Docs`, `Learn with Tutorials`).
3. It asserts a feature `<h1>`/`<h2>` is visible on each route
   (proves the lazy chunk rendered, not just the shell).
4. It asserts a nav link to each route exists.
5. The spec is part of the CI default pipeline (referenced from
   `tobe-testing-supervisor`'s Final Validation gate).

Severity:
- smoke spec absent → `blocking` (CHL-SHELL-NOEXIST)
- smoke spec exists but covers < 80% of protected routes → `high`
  (CHL-SHELL-PARTIAL)
- spec does not check for placeholder strings → `high`
  (CHL-SHELL-NOPLACEHOLDER-GUARD)
- spec runs only on the static build (no real backend) → `medium`
  (CHL-SHELL-NOREALAPI)

> Rationale: the InfoSync 2026-05 retrospective had 200/200 component
> tests + 204/204 equivalence tests all passing while the FE was unusable
> because every route showed the Angular CLI welcome card. Component
> tests and HTTP equivalence tests both run *below* the level at which
> this gap lives.

## Check 10 — Backend boots on default profile

Verify the backend can start with plain `java -jar` (no
`-Dspring.profiles.active=...`). Test-profile @SpringBootTest tests
explicitly use `@ActiveProfiles("test")` and therefore mask
default-profile wiring regressions.

Required: `<backend-dir>/src/test/java/.../BootSmokeTest.java` with
`@SpringBootTest` and NO `@ActiveProfiles` annotation. The class body
can be empty — Spring Boot fails the test when context wiring breaks.

```bash
# File must exist
test -f <backend-dir>/src/test/java/com/<org>/<app>/BootSmokeTest.java
# Must NOT carry @ActiveProfiles
! grep -q "@ActiveProfiles" <backend-dir>/src/test/java/com/<org>/<app>/BootSmokeTest.java
# Must pass
mvn -q test -Dtest=BootSmokeTest
```

Severity:
- BootSmokeTest missing → `blocking` (CHL-BOOT-MISSING)
- BootSmokeTest fails → `blocking` (CHL-BOOT-FAILS) — the app cannot run

> Rationale: the InfoSync 2026-05 retrospective had
> `mvn test` reporting 177/177 pass while `java -jar target/*.jar` crashed
> immediately with `Parameter 0 of constructor in AdminUserService
> required a bean of type 'UserRepository' that could not be found` —
> the default profile excluded JPA autoconfig but the @Service constructors
> still required the repos. Test-profile tests masked the bug. Check 10
> enforces a profile-agnostic boot.
