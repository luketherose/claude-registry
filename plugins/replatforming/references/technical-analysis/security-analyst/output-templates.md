# Security-analyst — output templates

> Reference doc for `security-analyst`. Read at runtime when about to write the
> three security deliverables under `docs/analysis/02-technical/08-security/`.

The agent produces three files. Each uses the frontmatter contract shared
across Phase 2 outputs (`agent`, `generated`, `sources`, `confidence`,
`status`).

---

## File 1 — `security-findings.md`

```markdown
---
agent: security-analyst
generated: <ISO-8601>
sources:
  - .indexing-kb/04-modules/*.md
  - .indexing-kb/06-data-flow/configuration.md
  - <repo-path>:<line>
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
---

# Security findings

## Summary
- Critical: <N>
- High:     <N>
- Medium:   <N>
- Low:      <N>
- Info:     <N>

## Findings

### SEC-01 — Hard-coded API key in source
- **Severity**: critical
- **OWASP**: A02 / A05
- **Location**: `<repo-path>:<line>`
- **Description**: <e.g., "Slack webhook URL with embedded token
  hard-coded in alerts.py">
- **AS-IS remediation**: move to env var, rotate the leaked key,
  redact from git history
- **Sources**: [<repo-path>:<line>]

### SEC-02 — SQL injection via f-string
- **Severity**: critical
- **OWASP**: A03
- **Location**: `<repo-path>:<line>`
- **Description**: query built with f-string interpolation of user
  input from Streamlit text_input
- **AS-IS remediation**: parameterize via SQLAlchemy text() with
  bindparams or ORM filter
- **Cross-ref**: RISK-DA-01 (data-access-analyst)
- **Sources**: [...]

### SEC-NN — ...

## Cross-references

| Finding | Related (other agents) |
|---|---|
| SEC-NN | RISK-DA-NN, RISK-RES-NN, INT-NN |

## Open questions
- <e.g., "module X reads a file path from user input; cannot determine
  if path traversal is mitigated">
```

---

## File 2 — `owasp-top10-coverage.md`

```markdown
---
agent: security-analyst
generated: <ISO-8601>
sources: [...]
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
---

# OWASP Top 10 (2021) coverage

| ID | Category | Status | Evidence | Findings |
|---|---|---|---|---|
| A01 | Broken Access Control | partial | <evidence> | SEC-NN |
| A02 | Cryptographic Failures | missing | <evidence> | SEC-NN |
| A03 | Injection | partial | <evidence> | SEC-NN, SEC-NN |
| A04 | Insecure Design | not assessable | KB lacks design docs | — |
| A05 | Security Misconfiguration | partial | <evidence> | SEC-NN |
| A06 | Vulnerable and Outdated Components | see 03-dependencies-security | — | (VULN-* refs) |
| A07 | Authentication Failures | partial | <evidence> | SEC-NN |
| A08 | Software and Data Integrity Failures | high risk | pickle of user input | SEC-NN |
| A09 | Security Logging and Monitoring | see 07-resilience | — | (RISK-RES-* refs) |
| A10 | Server-Side Request Forgery (SSRF) | low risk | no user-controlled outbound URL | — |

## Notes
<one-paragraph per row where status is partial / missing>

## Open questions
- <e.g., "A01 — authorization is enforced upstream by an API gateway
  per ops; cannot verify from this codebase alone">
```

---

## File 3 — `threat-model.md`

```markdown
---
agent: security-analyst
generated: <ISO-8601>
sources: [...]
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
---

# Threat model (STRIDE)

## Assets

| Asset | Description |
|---|---|
| User data (PII) | name, email, address |
| Billing data | card last-4, transaction history |
| Admin actions | user ban, refund, config change |
| session_state contents | per-browser-session cart, filters, current_user |

## STRIDE matrix

| Asset | Spoofing | Tampering | Repudiation | Info disclosure | DoS | Elevation |
|---|---|---|---|---|---|---|
| User data | login required | DB writes parameterized | audit log? | encrypted at rest? | rate limit? | role check? |
| Billing data | login + 2FA? | parameterized | yes, audit_log table | no encryption flagged | — | — |
| Admin actions | role-check enforced via decorator | SEC-NN | yes | — | — | flagged |
| session_state | session-scoped | local | no | shared library on instance — flag | — | — |

## Trust boundaries
- Trusted: server-side code in this repo, env-var config
- Untrusted: any user input, file uploads, webhook payloads, query
  params
- Partially trusted: authenticated user input (still untrusted for
  XSS/SQLi purposes)

## Notable surface

### Entry point: Streamlit dashboard (port 8501)
- Auth: <how>
- Untrusted inputs: widget values, file uploads
- Sinks reached: DB, file system, outbound API

### Entry point: webhook /events
- Auth: HMAC signature verification ✓
- Untrusted inputs: payload body
- Sinks: queue, DB writes

## Open questions
- <e.g., "trust boundary for the embedded admin panel: it is shipped
  in the same Streamlit app; access is gated by a role check, but
  the role is read from session_state which is set elsewhere; need
  to verify upstream enforcement">
```
