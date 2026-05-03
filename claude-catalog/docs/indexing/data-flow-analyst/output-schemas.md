# Data-flow analyst — output schemas

> Reference doc for `data-flow-analyst`. Read at runtime when about to
> emit one of the four output files under `.indexing-kb/06-data-flow/`.

The agent body owns when to write each file and what content qualifies.
This doc is the on-disk shape only — frontmatter and section skeletons
to copy into the `Write` call.

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
