# Codebase mapper — stack detection markers

> Reference doc for `codebase-mapper`. Read at runtime during the
> stack-detection step (populating `stack.json`).

Apply the markers below in order. Multiple markers can match — emit them
all in `languages[]` and `frameworks[]`. Pick `primary_language` as the one
with most LOC (ties broken by alphabetic order).

---

## Build / package manager markers (language)

| Marker file | Implies language |
|---|---|
| `pyproject.toml`, `setup.py`, `requirements.txt`, `Pipfile` | python |
| `package.json` | typescript (if `tsconfig.json` exists) or javascript |
| `pom.xml`, `build.gradle*` (without `*.kt` files) | java |
| `build.gradle.kts` or `*.kt` files | kotlin |
| `Cargo.toml` | rust |
| `go.mod` | go |
| `*.csproj`, `*.sln`, `global.json` | csharp |
| `Gemfile`, `*.gemspec` | ruby |
| `composer.json`, `composer.lock` | php |
| `Package.swift` | swift |
| `mix.exs` | elixir |

---

## Content markers (framework)

Grep across `.py` / `.java` / `.ts` etc. files (sample the first 50 files
per language to keep cost bounded):

| Pattern | Implies framework |
|---|---|
| `import streamlit` (in any `.py`) | streamlit |
| `from fastapi`, `import fastapi` | fastapi |
| `from django`, `import django` (in any `.py`) | django |
| `from flask`, `import flask` | flask |
| `@SpringBootApplication` (in any `.java`/`.kt`) | spring-boot |
| `org.springframework` (import) | spring (any module) |
| `io.micronaut` | micronaut |
| `io.quarkus` | quarkus |
| `angular.json` file present, or `@angular/core` in `package.json` | angular |
| `next.config.{js,ts,mjs}` file present | nextjs |
| `nuxt.config.{js,ts}` file present | nuxt |
| `vite.config.{js,ts}` file present | vite (build tool) |
| `qwik.config.ts`, `@builder.io/qwik` in `package.json` | qwik |
| `vue.config.js` or `*.vue` files | vue |
| `Cargo.toml` with `axum` dependency | axum |
| `Cargo.toml` with `actix-web` dependency | actix-web |
| `go.mod` with `gin-gonic/gin` | gin |
| `go.mod` with `go-chi/chi` | chi |
| `app/Http/Controllers/` directory | laravel |
| `bin/console` + `symfony/framework-bundle` in `composer.json` | symfony |
| `config/routes.rb` | rails |
| `Sinatra::Base` reference in `.rb` files | sinatra |
| `Microsoft.AspNetCore` in `.csproj` | aspnet-core |

---

## Test framework markers

| Marker | Implies test framework |
|---|---|
| `pytest` in dependency files; `pytest.ini`, `conftest.py` files | pytest |
| `unittest` imports (and no pytest) | unittest |
| `org.junit.jupiter` in dependencies | junit-5 |
| `org.testng` in dependencies | testng |
| `cargo test` is the universal default for Rust → assume `rust-test` if `Cargo.toml` exists |
| `go test` is the universal default for Go → assume `go-test` if `go.mod` exists |
| `xunit` in `.csproj` PackageReferences | xunit |
| `nunit` in `.csproj` | nunit |
| `mstest` in `.csproj` | mstest |
| `rspec` in `Gemfile` | rspec |
| `minitest` (Ruby) | minitest |
| `phpunit` in `composer.json` | phpunit |
| `pest` in `composer.json` | pest |
| `jest`, `vitest` in `package.json` devDependencies | jest, vitest |
| `playwright` in `package.json` | playwright |
| `cypress` in `package.json` | cypress |
