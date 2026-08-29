# Output templates — README and bug-found policy

> Reference doc for `service-collection-builder`. Read at runtime when
> writing `tests/baseline/postman/README.md` and when handling AS-IS
> defects discovered during collection construction.

## README skeleton

```markdown
---
agent: service-collection-builder
generated: <ISO-8601>
sources: [...]
confidence: <high|medium|low>
status: <complete|partial|needs-review|blocked>
duration_seconds: <int>
---

# AS-IS service collection (Postman 2.1)

## Services covered
| Service | Endpoints | Collection |
|---|---|---|
| `payments` | 6 | `payments.postman_collection.json` |

## Run

In Postman:
1. Import `<service>.postman_collection.json`
2. Import `<service>.postman_environment.json`
3. Set `access_token` and other secrets in the environment
4. Run the collection: Runner → select all → Run

In CLI (newman):
```
newman run tests/baseline/postman/payments.postman_collection.json \
       -e tests/baseline/postman/payments.postman_environment.json
```

## AS-IS contract
This collection captures the endpoints AS THEY BEHAVE TODAY. Phase 5
will compare TO-BE responses against these requests. Discrepancies must
be reviewed for either:
- intentional behavioral change (document in equivalence-report.md)
- regression (block migration)

## Determinism caveats
- Idempotency-Key uses Postman's `{{$guid}}` (random per run); for AS-IS
  regression assertions to be deterministic, use a fixed fixture key
  when running against AS-IS for the second time.
- Time-sensitive responses (`createdAt` fields) are asserted only on
  presence + format, not exact value.

## Open questions
- ...
```

## Bug-found policy

If during collection building you find that:

- an endpoint is documented in code but not reachable
- auth is missing or weaker than Phase 2 declared
- a response shape doesn't match the schema

document in `## Open questions` per the global Phase 3 policy. Never
modify AS-IS source. Add a request to the collection that **documents**
the current (potentially broken) behavior.

## Reporting (text response back to supervisor)

```markdown
## Files written
- tests/baseline/postman/<service>.postman_collection.json (×N services)
- tests/baseline/postman/<service>.postman_environment.json (×N)
- tests/baseline/postman/README.md

## Coverage
- Services:  <N>
- Endpoints: <N> total
- Happy + edge per endpoint: <N happy>, <N edge>

## Auth coverage
- Bearer JWT: <N endpoints>
- API key:    <N endpoints>
- HMAC:       <N endpoints>
- None:       <N endpoints>

## Confidence
high | medium | low

## Duration (wall-clock)
<seconds>

## Open questions
- ...
```
