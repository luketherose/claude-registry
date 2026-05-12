# Data-flow analyst — output schemas

> Reference doc for `data-flow-analyst`. Read at runtime when about to
> emit output files under `.indexing-kb/06-data-flow/`, `.indexing-kb/bronze/`,
> or `.indexing-kb/silver/`.

The agent body owns when to write each file and what content qualifies.
This doc is the on-disk shape only — frontmatter, JSONL record schemas, and
section skeletons to copy into the `Write` call.

---

## Bronze JSONL schemas

### `bronze/io-boundaries.jsonl` — one record per I/O call site, append-only

```json
{
  "boundary_id": "IO-001",
  "kind": "http_client | db_read | db_write | file_read | file_write | subprocess | socket",
  "direction": "inbound | outbound | bidirectional",
  "call_site_file": "path/to/file.py",
  "call_site_lines": "42-45",
  "evidence_id": "EV-000050",
  "target": "https://api.example.com or db_name or /path/to/file",
  "confidence": "high | medium | low"
}
```

### `bronze/config-env-index.jsonl` — one record per env var / config key, append-only

```json
{
  "config_id": "CFG-001",
  "kind": "env_var | config_key | secret",
  "name": "DATABASE_URL",
  "default_value": null,
  "read_in_file": "app/settings.py",
  "read_at_line": "15",
  "evidence_id": "EV-000060",
  "purpose": "Database connection string (inferred from name)",
  "confidence": "high | medium | low"
}
```

## Silver JSONL schemas

### `silver/data-flows.jsonl` — agentic: described data flows with evidence

```json
{
  "flow_id": "DF-001",
  "description": "User upload is written to S3 then a DB record is created",
  "source": "api/upload.py",
  "sink": "S3 bucket + PostgreSQL table uploads",
  "evidence_ids": ["EV-000050", "EV-000051"],
  "source_files": ["api/upload.py"],
  "confidence": "high | medium | low",
  "inference_level": "direct | derived | speculative",
  "open_questions": []
}
```

### `silver/integration-points.jsonl` — agentic: third-party / service integrations

```json
{
  "integration_id": "INT-001",
  "system": "Stripe",
  "kind": "http_client",
  "description": "Charges are created via Stripe v1/charges endpoint",
  "evidence_ids": ["EV-000055"],
  "source_files": ["billing/api.py"],
  "confidence": "high | medium | low",
  "inference_level": "direct | derived | speculative",
  "open_questions": []
}
```

---

All four files share the frontmatter convention:

```yaml
---
agent: data-flow-analyst
generated: <ISO-8601>
source_files: ["<files inspected>"]
confidence: <high|medium|low>
status: complete
---
```

---

## File 1 — `.indexing-kb/06-data-flow/database.md`

```markdown
---
agent: data-flow-analyst
generated: <ISO-8601>
source_files: ["<files with DB access>"]
confidence: <high|medium|low>
status: complete
---

# Database access

## Connection setup
- Connection string source: env var `<NAME>` (REDACTED literal value)
- Driver / library: `<JPA / EF Core / sqlx / GORM / Mongoose / …>`
- Async / sync: `<sync|async>`

## ORM in use
- `<library + version if discoverable>`

## Entities / tables
| Entity | Defined in | Operations | Used by | Language |
|---|---|---|---|---|
| User | models/user.py:User | C/R/U | services/auth.py, api/users.py | python |

## Raw SQL
| File:line | Query (truncated) | Operation | Language |
|---|---|---|---|
| services/report.py:45 | `SELECT * FROM ledger WHERE ...` | Read | python |

## Open questions
- <Dynamic SQL via string concatenation: locations>
- <Connection strings hardcoded (not env-based): locations>
```

---

## File 2 — `.indexing-kb/06-data-flow/external-apis.md`

```markdown
---
agent: data-flow-analyst
generated: <ISO-8601>
source_files: ["<files with HTTP calls>"]
confidence: <high|medium|low>
status: complete
---

# External API calls

| URL pattern | Method | File:line | Auth source | Language |
|---|---|---|---|---|
| `<env:STRIPE_BASE>/v1/charges` | POST | billing/api.py:45 | Bearer (env:STRIPE_KEY) | python |

## Open questions
- <URLs assembled dynamically (multiple variables)>
- <No auth detected on endpoints>
```

---

## File 3 — `.indexing-kb/06-data-flow/file-io.md`

```markdown
---
agent: data-flow-analyst
generated: <ISO-8601>
source_files: ["<files with I/O>"]
confidence: <high|medium|low>
status: complete
---

# File I/O

## Read patterns
| Path pattern | Format | Purpose | File:line | Language |

## Write patterns
| Path pattern | Format | Purpose | File:line | Language |

## Open questions
- <Paths assembled with template strings, hard to enumerate>
```

---

## File 4 — `.indexing-kb/06-data-flow/configuration.md`

```markdown
---
agent: data-flow-analyst
generated: <ISO-8601>
source_files: ["<config files + loader code>"]
confidence: <high|medium|low>
status: complete
---

# Configuration

## Env vars used
| Name | Default | Read in | Purpose (inferred from name) | Language |

## Config files
| Path | Format | Loaded by | Used by |

## Settings / configuration classes
| Class | File | Fields (count) | Env prefix / section | Language |

(Examples: Pydantic `BaseSettings` for Python; Spring `@ConfigurationProperties`
for JVM; envconfig structs for Go; `figment` config structs for Rust;
`IOptions<T>` POCOs for C#; etc.)
```
