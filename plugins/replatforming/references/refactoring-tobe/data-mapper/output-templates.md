# Data-mapper — output / reporting templates

> Reference doc for `data-mapper`. Read at runtime when assembling the
> deliverable file list and the supervisor-facing report. The agent body
> keeps the canonical list of paths under `## Outputs`; this doc holds
> the full markdown reporting skeleton.

## Files written

- `<backend-dir>/src/main/java/com/<org>/<app>/<bc>/domain/*.java`
  (entities, value objects, enums)
- `<backend-dir>/src/main/java/com/<org>/<app>/<bc>/infrastructure/*Repository.java`
- `<backend-dir>/src/main/java/com/<org>/<app>/<bc>/api/*Mapper.java`
  (overwriting scaffolder's placeholder)
- `<backend-dir>/src/main/java/com/<org>/<app>/shared/idempotency/IdempotencyKeyEntity.java`
- `<backend-dir>/src/main/java/com/<org>/<app>/shared/idempotency/IdempotencyKeyJpaRepository.java`
- `<backend-dir>/src/main/resources/db/changelog/db.changelog-master.yaml`
- `<backend-dir>/src/main/resources/db/changelog/<NN>__*.yaml`
- `<backend-dir>/src/main/java/com/<org>/<app>/<bc>/domain/README.md`
  (overwrite scaffolder's placeholder with: aggregates list, invariants,
   cross-references)
- `<backend-dir>/src/main/java/com/<org>/<app>/<bc>/infrastructure/README.md`
  (overwrite: repository list, query patterns from Phase 2)

## Reporting skeleton

```markdown
## Files written
<list>

## Stats
- Aggregates implemented: <N>
- Entities:               <N>
- Value objects:          <N>
- Enums:                  <N>
- Repositories:           <N>
- Liquibase changesets:  <N>

## Schema strategy
- Case A (greenfield) | Case B (existing-schema migration)
- Changelogs starting at: 01

## Compile readiness
- After this worker, mvn compile expected to pass for the BE track
  (controller / service references resolve to entities now).

## Confidence
high | medium | low

## Duration (wall-clock)
<seconds>

## Open questions
- <e.g., "BC-02 aggregate uses Money but currency precision rules
  unclear — flagged for logic-translator">
```
