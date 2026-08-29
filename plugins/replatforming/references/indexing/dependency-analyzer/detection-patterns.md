# Detection patterns and output schemas — `dependency-analyzer`

> Reference doc for `dependency-analyzer`. Read at runtime when extracting
> external dependencies, parsing imports, or composing the two output files.

## Goal

Provide the per-language manifest tables, import-grep patterns, top-level
package mapping conventions, dependency-categorization heuristic, and the
exact frontmatter+body schemas for the two output files. The agent body
holds the decision logic; this doc holds the lookup tables.

---

## External dependencies — manifests by language

For each language in `stack.languages[]`, read these manifests and extract
declared dependencies.

| Language | Manifest files | Dependency syntax |
|---|---|---|
| python | `pyproject.toml`, `setup.py`, `setup.cfg`, `requirements.txt`, `requirements-*.txt`, `Pipfile`, `Pipfile.lock`, `poetry.lock` | `[project.dependencies]`, `install_requires`, `requirements*.txt` lines, `[tool.poetry.dependencies]` |
| java | `pom.xml`, `build.gradle`, `build.gradle.kts`, `settings.gradle*` | `<dependencies><dependency>` (Maven); `dependencies { implementation/api/... }` (Gradle); `dependencyManagement` BOMs |
| kotlin | same as Java; `build.gradle.kts` is the typical case | same as Java |
| rust | `Cargo.toml`, `Cargo.lock` | `[dependencies]`, `[dev-dependencies]`, `[build-dependencies]`, `[workspace.dependencies]` |
| go | `go.mod`, `go.sum` | `require ( ... )` block |
| csharp | `*.csproj`, `Directory.Packages.props`, `packages.config` (legacy) | `<PackageReference Include="X" Version="Y" />`, `<PackageVersion>` (CPM) |
| ruby | `Gemfile`, `Gemfile.lock`, `*.gemspec` | `gem "name", "~> X.Y"` |
| php | `composer.json`, `composer.lock` | `require`, `require-dev` objects |
| typescript / javascript | `package.json`, `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock` | `dependencies`, `devDependencies`, `peerDependencies` |
| swift | `Package.swift`, `Package.resolved` | `dependencies: [.package(...)]` |

For each declared dependency, record: **name**, **version constraint**
(as declared), **source file**, **scope** (production / dev / test / build /
optional), **language** (when polyglot).

---

## External dependencies — categorization heuristic

Classify each dependency name into one category (heuristic, name-based,
language-aware):

- **Web framework** — flask, fastapi, django, streamlit, dash (Python);
  spring-boot-starter-web, micronaut-http (JVM); axum, actix-web (Rust);
  gin, chi (Go); aspnetcore (C#); rails, sinatra (Ruby); laravel,
  symfony (PHP); express, fastify, nestjs, next, nuxt (JS/TS).
- **ORM / database driver** — sqlalchemy, peewee, psycopg2, pymongo
  (Python); spring-data-jpa, hibernate, jdbc, jdbi (JVM); diesel, sqlx,
  sea-orm (Rust); database/sql, gorm (Go); ef-core, dapper (C#);
  activerecord, sequel (Ruby); doctrine, eloquent (PHP); prisma,
  typeorm, drizzle, mongoose (JS/TS).
- **HTTP client** — requests, httpx, aiohttp (Python); WebClient,
  RestTemplate, OkHttp (JVM); reqwest (Rust); net/http (Go); HttpClient
  (C#); httparty, faraday (Ruby); guzzle (PHP); axios, fetch, ky (JS/TS).
- **Data / numerics / ML** — pandas, numpy, polars, scikit-learn, torch,
  tensorflow, transformers (Python); breeze, smile (JVM); polars-rs
  (Rust); gonum (Go); ml.net (C#); etc.
- **Testing** — pytest, unittest, hypothesis (Python); junit, testng,
  mockito, testcontainers (JVM); rstest, proptest (Rust); testify (Go);
  xunit, nunit, mstest, fluentassertions (C#); rspec, minitest (Ruby);
  phpunit, pest (PHP); jest, vitest, playwright, cypress (JS/TS).
- **Dev tooling / linters** — black, ruff, mypy (Python); checkstyle,
  spotbugs, errorprone (JVM); rustfmt, clippy (Rust — toolchain
  components, not deps); golangci-lint (Go); roslyn analyzers (C#);
  rubocop (Ruby); php-cs-fixer, phpstan, psalm (PHP); eslint, prettier,
  biome (JS/TS).
- **Observability** — loguru, structlog, sentry-sdk (Python); micrometer,
  opentelemetry (JVM); tracing (Rust); slog (Go); serilog (C#); etc.
- **Other** — anything not matching above; preserve the name and let the
  synthesizer interpret.

---

## Internal dependencies — import grep patterns

Parse imports line-based (no full-AST parse needed for graph purposes).

| Language | Import pattern (regex-friendly) |
|---|---|
| python | `^(from \S+|import \S+)` |
| java | `^import [a-zA-Z0-9_.]+;` |
| kotlin | `^import [a-zA-Z0-9_.]+` |
| rust | `^(use |extern crate )` (`mod` for in-crate modules) |
| go | inside `import (...)` blocks: lines `"<path>"` |
| csharp | `^using [a-zA-Z0-9_.]+;` |
| ruby | `^(require\|require_relative) ['"][^'"]+['"]` |
| php | `^use [a-zA-Z0-9_\\]+;` (after `namespace`) |
| typescript / javascript | `^import .* from ['"]([^'"]+)['"]`, `^const .* = require\(['"]([^'"]+)['"]\)` |
| swift | `^import \w+` |

### Top-level package mapping

- **Python**: drop `.<sub-module>` suffix; map to top-level package
  matching `02-structure/codebase-map.md`.
- **Java/Kotlin**: drop the class name suffix; group by leading 2-3
  package segments (typically `com.acme.<domain>`).
- **Rust**: top-level crate name from `use crate::X::...` or
  `use other_crate::...`.
- **Go**: full import path; `internal/<x>` modules grouped by their
  immediate parent.
- **C#**: top-level namespace.
- **Ruby**: relative path normalized to logical package.
- **PHP**: leading 2 segments of the use statement.
- **TypeScript/JavaScript**: relative paths resolved to `src/<dir>`;
  `@scope/pkg` for monorepo internal packages.

Build a directed graph: package A → package B if any file in A imports
from B. Detect cycles using DFS. Identify standalone packages (no
incoming or outgoing internal edges) and coupling hotspots (packages
depended on by ≥ 5 others).

---

## Output schemas

### File 1: `.indexing-kb/03-dependencies/external-deps.md`

```markdown
---
agent: dependency-analyzer
generated: <ISO-8601>
source_files: ["pyproject.toml", "package.json", "..."]
confidence: high
status: complete
---

# External dependencies

## By language and category

### python — Web frameworks
| Name | Version | Source | Notes |
|---|---|---|---|

### python — ORM / database drivers
…

### typescript — Web framework
…

### typescript — Testing
…

(One section per language present in `stack.languages[]`.)

## Migration relevance flags
- `streamlit` — UI framework; replacement target depends on TO-BE
  decision in Phase 4 (typically Angular/React/Vue/Qwik via
  `developer-frontend`)
- `<package>` — language-specific utility; check if equivalent exists
  in target language
```

### File 2: `.indexing-kb/03-dependencies/internal-deps.md`

```markdown
---
agent: dependency-analyzer
generated: <ISO-8601>
source_files: ["<all source files in scope>"]
confidence: high
status: complete
---

# Internal dependency graph

## Package / module dependency table
| Package | Depends on | Depended on by | Language |
|---|---|---|---|

## Circular dependencies
- `A → B → C → A` — involves files: `<list>` (language: <X>)

## Standalone packages
- `<pkg>` — no internal couplings (good migration unit)

## Coupling hotspots
| Package | In-degree | Out-degree | Language | Risk |
|---|---|---|---|---|
| `<pkg>` | 8 | 2 | python | High in-degree: blast radius if interface changes |
```

### Open questions section (in `internal-deps.md`)

In a `## Open questions` section, list:
- Imports that could not be resolved to any internal or known external
  package (typos, missing packages)
- Dynamic imports / reflection (`importlib.import_module(<string>)`,
  `Class.forName(...)`, `require(<expr>)` with non-literal arg)
- Wildcard imports (`from x import *`, `import .*` Java patterns)
