# Sub-agents roster — Phase 4

> Reference doc for `refactoring-tobe-supervisor`. Read at runtime when
> deciding which sub-agent to dispatch in a given wave, or when wiring
> a worker prompt to its declared output target.

The Phase 4 supervisor coordinates 9 in-house Sonnet workers across 6
waves plus an opt-in export wave. External agents (`code-reviewer`,
`debugger`, `documentation-writer`, `document-creator`,
`presentation-creator`) are called on demand outside the wave grid.

## In-house workers

| Sub-agent | Wave | Output target |
|---|---|---|
| `decomposition-architect` | W1 | `.refactoring-kb/00-decomposition/`, `docs/refactoring/4.1-decomposition/`, `docs/adr/ADR-001`, `ADR-002` |
| `api-contract-designer` | W2 | `docs/refactoring/4.6-api/`, `docs/adr/ADR-003` |
| `backend-scaffolder` | W3 (BE track) | `backend/` (Maven scaffold + structure) |
| `data-mapper` | W3 (BE track) | `backend/src/main/java/.../<bc>/domain/`, `backend/src/main/resources/db/migration/` |
| `logic-translator` | W3 (BE track, fan-out per UC) | `backend/src/main/java/.../<bc>/application/`, `backend/src/main/java/.../<bc>/api/` |
| `frontend-scaffolder` | W3 (FE track) | `frontend/` (Angular workspace) |
| `hardening-architect` | W4 | `docs/refactoring/4.7-hardening/`, `docs/adr/ADR-004`, `ADR-005`, `backend/src/main/resources/application.yml` updates |
| `migration-roadmap-builder` | W5 | `docs/refactoring/roadmap.md` |
| `phase4-challenger` | W6 (always ON) | `docs/refactoring/_meta/challenger-report.md`, `.refactoring-kb/02-traceability/as-is-to-be-matrix.json` |

## External agents

| Agent | Used for | Mode |
|---|---|---|
| `code-reviewer` | Background review after each scaffold/translation (W4 review-mode) | per Q4 flag |
| `debugger` | Equivalence discrepancies vs. Phase 3 baseline | on demand |
| `documentation-writer` | Polish of ADRs | background |
| `document-creator` | PDF export of roadmap | opt-in (Export Wave) |
| `presentation-creator` | PPTX export of roadmap | opt-in (Export Wave) |

## Dispatch rules

- Workers are invoked only by the supervisor — never by each other and
  never directly by the user.
- W3 backend track is sequential: `backend-scaffolder` → `data-mapper` →
  `logic-translator` (fan-out per UC).
- W3 frontend track (`frontend-scaffolder`) runs in parallel with the BE
  track.
- Every worker writes only under `backend/`, `frontend/`,
  `docs/refactoring/`, `.refactoring-kb/`, or `docs/adr/`. Never under
  AS-IS paths or Phase 0–3 outputs.
