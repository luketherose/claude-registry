# Changelog

All notable changes to catalog capabilities are documented here.

Format: `[name@version] - YYYY-MM-DD` for releases, `[Unreleased]` for pending changes.

## [Unreleased]
### Changed
- All 37 skills in `claude-catalog/skills/` — add `name`, `tools: Read`, `model: haiku` frontmatter fields; rewrite `description` to start with "Use when/for/to"; add `## Role` section; remove `$ARGUMENTS` template artefact; translate `utils/caveman.md` body to English UK

### Added
- `java-spring-standards@1.0.0` — skill: Java/Spring Boot standards (package structure, layering, testing, error handling, logging, security, observability)
- `testing-standards@1.0.0` — skill: testing principles, scenario taxonomy, JUnit 5 + pytest + Jest templates
- `accenture-branding@1.0.0` — skill: Accenture brand palette, python-pptx constants, CSS template; migrated from policies/
- `rest-api-standards@1.0.0` — skill: REST design rules, HTTP methods, status codes, RFC 7807, OpenAPI 3.1

### Changed
- `developer-java-spring@1.1.0` — delegates standards to java-spring-standards, testing-standards, rest-api-standards skills
- `test-writer@0.2.0` — delegates to testing-standards and java-spring-standards skills
- `code-reviewer@0.2.0` — delegates to java-spring-standards, testing-standards, rest-api-standards skills (fulfills v1.0 TODO)
- `api-designer@0.2.0` — delegates to rest-api-standards skill
- `presentation-creator@0.2.0` — delegates to accenture-branding skill
- `document-creator@0.2.0` — delegates to accenture-branding skill

### Removed
- `policies/accenture-branding.md` — migrated to skill
- `policies/java-spring-conventions.md` — merged into java-spring-standards skill

### Documentation
- `README.md` — updated: skills layer, repo structure, full capability+skill tables, corrected PPTX link
- `docs/quick-start.md` — updated: skills explanation, setup script instructions, full capability list
- `CONTRIBUTING.md` — updated: skill workflow, skill PR requirements
- `how-to-write-a-capability.md` — updated: section 0 on skills (format, constraints, composition)
- `GOVERNANCE.md` — updated: capability types table (agent vs. skill), lifecycle states
- `review-checklist.md` — updated: section 9 for skill-specific checks
- `scripts/new-capability.sh` — updated: `--type skill` flag for skill scaffolding
- `CLAUDE.md` (root) — created: project-level instructions for documentation maintenance rule


### Added
- Initial catalog structure
- `software-architect@1.0.0` — full capability
- `functional-analyst@1.0.0` — full capability
- `developer-java-spring@1.0.0` — full capability
- `technical-analyst@0.1.0` — initial draft (beta)
- `developer-python@0.1.0` — initial draft (beta)
- `code-reviewer@0.1.0` — initial draft (beta)
- `test-writer@0.1.0` — initial draft (beta)
- `debugger@0.1.0` — initial draft (beta)
- `api-designer@0.1.0` — initial draft (beta)
- `documentation-writer@0.1.0` — initial draft (beta)
- `presentation-creator@0.1.0` — Accenture-branded PPTX creator for project/estimation presentations (beta)
- `document-creator@0.1.0` — Accenture-branded PDF/DOCX creator for project/estimation documents (beta)
- `policies/accenture-branding.md` — brand specification: color palette, typography, CSS/python-pptx constants

---

## Release format reference

```
## [software-architect@1.1.0] - 2026-05-01

### Changed
- Enhanced trade-off analysis output format to include cost dimension
- Added explicit guidance for cloud-native patterns

## [software-architect@1.0.0] - 2026-04-19

### Added
- Initial release
```

### Change types

- `Added` — new capability or new section in existing capability
- `Changed` — behavior change, prompt improvement, model change
- `Fixed` — bug fix in prompt (e.g. missing instruction causing wrong output)
- `Deprecated` — capability will be removed in a future release
- `Removed` — capability removed from marketplace
- `Breaking` — name, description, or tools change requiring consumer action
