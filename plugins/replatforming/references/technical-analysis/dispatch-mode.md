# Phase 2 — Dispatch-mode decision (parallel / batched / sequential)

> Reference doc for `technical-analysis-supervisor`. Read at runtime when deciding the W1 dispatch mode.

The supervisor decides the dispatch mode for **Wave 1 only** (8 workers). Wave 2 and Wave 3 are always sequential by design (synthesis depends on W1; challenger depends on synthesis).

## Decision tree

```
1. Did the user pass --mode <X>?
   -> Yes: use it. Skip the rest.
   -> No:  continue.

2. Read .indexing-kb/_meta/manifest.json:
     - module count (M)
     - LOC (L) from 02-structure/language-stats
     - status of each section

3. Apply rules in order:
   a. If any KB section has status: needs-review or partial > 30% of total
      -> sequential (quality over speed; lets you triage between workers)
   b. If M <= 30 AND L <= 30k AND --cheap not set
      -> parallel (single tool call with 8 Agent invocations)
   c. If M <= 80 OR L <= 80k
      -> batched (3 batches of [3, 3, 2] workers)
   d. Else
      -> sequential (8 sequential dispatches)
```

## Batching plan (used in `batched` mode only)

Group workers by domain affinity so each batch shares roughly the same KB sections (improves cache locality, reduces re-reads):

```
Batch 1 (structure/code):    code-quality, state-runtime, dependency-security
Batch 2 (data/integration):  data-access, integration, performance
Batch 3 (resilience/sec):    resilience, security
```

Within a batch, workers run in parallel (single tool call). Batches run sequentially.

## Mode confirmation

Before dispatching Wave 1, post the chosen mode to the user with the rationale (KB size, status flags). The user may override:

```
=== Wave 1 dispatch plan ===

Repo size:      <M> modules, <L> LOC
KB status:      <complete | partial-N-sections>
Chosen mode:    parallel | batched | sequential
Rationale:      <one line>

Workers (8):
  code-quality, state-runtime, dependency-security, data-access,
  integration, performance, resilience, security

Confirm: proceed with this mode? [yes / change to <X> / stop]
```

Do not dispatch without explicit confirmation.
