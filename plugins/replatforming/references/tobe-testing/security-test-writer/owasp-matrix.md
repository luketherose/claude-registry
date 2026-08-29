# OWASP Top 10 — coverage policy

> Reference doc for `security-test-writer`. Read at runtime when planning
> the OWASP coverage and authoring the per-category tests.

Every category gets a dedicated test class. Categories that don't
apply to the project (rare) get an explicit non-applicability
documentation in `05-security-findings.md` with rationale.

| Category | Approach |
|---|---|
| A01 Broken Access Control | Authorisation matrix (see `test-templates.md`) |
| A02 Cryptographic Failures | Verify HTTPS-only redirect, strong TLS ciphers (config check), password hashing (BCrypt + min cost factor) |
| A03 Injection | Payload battery on each string-input endpoint |
| A04 Insecure Design | Rate-limit verification, account lockout, idempotency on writes |
| A05 Security Misconfiguration | Actuator access, default credentials check, error verbosity (no stack traces in responses) |
| A06 Vulnerable & Outdated Components | OWASP Dependency-Check Maven plugin verification (CVSS gate) |
| A07 Identification & Authentication Failures | Session fixation, password reset flow, MFA (if applicable) |
| A08 Software & Data Integrity Failures | Verify deserialisation safety, SBOM presence, signed artifacts |
| A09 Security Logging & Monitoring | Audit log emission tests (see `test-templates.md`) |
| A10 SSRF | Outbound HTTP to user-supplied URLs is rejected unless allowlist |

## Phase 2 cross-reference (regression prevention)

Read every SEC-NN entry from
`docs/analysis/02-technical/08-security/security-findings.md`. For
each:
1. Identify whether it applied to a layer that exists in TO-BE.
2. Write a regression test that proves the issue is NOT present in
   TO-BE.
3. Reference the SEC-NN explicitly in the test's javadoc / comment.

If a Phase 2 finding cannot be tested in TO-BE because the affected
component doesn't exist anymore (e.g., Streamlit-specific cache leak):
document the rationale in `05-security-findings.md` under
`## Phase 2 findings — TO-BE applicability`.
