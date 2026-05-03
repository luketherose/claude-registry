# Codebase mapper — classification tables

> Reference doc for `codebase-mapper`. Read at runtime during the
> classification, package-mapping, and entrypoint-identification steps
> of the structural map.

---

## File classification by extension or content

For each file, classify its language/role:

| Language / role | Markers (extension or content) |
|---|---|
| python | `.py`, `.pyi`, `.ipynb` |
| java | `.java` |
| kotlin | `.kt`, `.kts` |
| scala | `.scala` |
| csharp | `.cs` |
| go | `.go` |
| rust | `.rs` |
| ruby | `.rb`, `.erb`, `.rake` |
| php | `.php`, `.blade.php` |
| typescript | `.ts`, `.tsx` |
| javascript | `.js`, `.jsx`, `.mjs`, `.cjs` |
| swift | `.swift` |
| objective-c | `.m`, `.mm` |
| html / template | `.html`, `.j2`, `.jinja`, `.erb`, `.twig`, `.blade.php`, `.razor`, `.cshtml` |
| css / styling | `.css`, `.scss`, `.sass`, `.less` |
| sql | `.sql` |
| shell | `.sh`, `.bash`, `.zsh` |
| config | `.toml`, `.yaml`, `.yml`, `.cfg`, `.ini`, `.json` (when config-like — e.g. tsconfig, package, jest, eslint) |
| data | `.csv`, `.parquet`, `.sqlite`, `.db` |
| build manifest | `pom.xml`, `build.gradle*`, `Cargo.toml`, `go.mod`, `package.json`, `pyproject.toml`, `setup.py`, `requirements.txt`, `Pipfile`, `composer.json`, `Gemfile`, `*.csproj`, `*.sln`, `mix.exs`, `Package.swift` |
| docs | `.md`, `.rst`, `.adoc` |
| other | everything else |

---

## Top-level package / module markers

Identify the top-level package or module units according to language
conventions:

| Language | Marker for "top-level package/module" |
|---|---|
| python | directories containing `__init__.py` directly under repo root or `src/` |
| java | directories under `src/main/java/` reflecting the package hierarchy (top-level = first directory after `src/main/java/`) |
| kotlin | same as Java but `src/main/kotlin/` |
| go | directories listed in `go.mod` `module` declaration; subdirectories under `cmd/` and `internal/` |
| rust | crates declared in `Cargo.toml` (workspace members) or the single crate at root |
| csharp | each `.csproj` file is a project |
| ruby | top-level directories under `app/` (Rails) or `lib/` |
| php | namespaces declared in `composer.json` `autoload.psr-4` |
| typescript / javascript | top-level directories under `src/` (or `app/` for Next.js) and `packages/` for monorepos |

---

## Entrypoint markers

| Language | Entrypoint markers |
|---|---|
| python | files with `if __name__ == "__main__":`; scripts in `bin/`, `scripts/`; `console_scripts` in `pyproject.toml`/`setup.py` |
| java | classes with `public static void main(String[] args)`; `@SpringBootApplication`-annotated classes |
| kotlin | `fun main()` at top level; `@SpringBootApplication`-annotated classes |
| go | `package main` directories under `cmd/` or repo root |
| rust | `[[bin]]` declarations in `Cargo.toml`; `src/main.rs` and `src/bin/*.rs` |
| csharp | `Program.cs` or top-level statement files; `*.csproj` with `<OutputType>Exe</OutputType>` |
| ruby | `bin/*` files; `config/application.rb` (Rails) |
| php | `public/index.php` (Laravel/Symfony); `bin/console` (Symfony) |
| typescript / javascript | `bin` field in `package.json`; `main` field; framework entrypoints (`server.ts`, `app.ts`) |
