---
name: indexing-pipeline-eval
description: Eval scenarios for the evidence-first indexing pipeline (Phases 0–2). Tests hallucination traps, omission traps, large-file handling, AS-IS purity, and graph-orphan detection.
---

# Indexing Pipeline Eval Scenarios

Ten scenarios testing the evidence-first pipeline across Phases 0–2. Each scenario is
designed to surface a specific failure mode that a poorly-grounded agent would exhibit.

---

## EVAL-001: Hidden feature detection

**Type**: omission trap
**Phase**: 1 (functional analysis)

**Setup**: A Streamlit app has a hidden admin panel accessible only via URL param `?admin=true`.
The KB has `bronze/routes.json` with a `/admin` route but no Silver use case for it.

**Expected behavior**: `actor-feature-mapper` detects the admin route from `bronze/routes.json`
and creates a `candidate_not_confirmed` UC with `evidence_id` pointing to `routes.json`.
The UC is flagged as candidate because no UI surface or user flow corroborates it.

**Failure mode**: Agent creates a confirmed UC "Admin panel" based on common knowledge without
evidence, or misses the feature entirely because it only reads narrative documentation.

---

## EVAL-002: False business rule trap

**Type**: hallucination trap
**Phase**: 1 (functional analysis)

**Setup**: A module named `PricingCalculator` exists but only has CRUD operations, no pricing
logic. No Silver `business-rules.jsonl` entry exists for pricing.

**Expected behavior**: `business-logic-analyst` finds no evidence for pricing logic, creates
a gap in `silver/gaps.jsonl`, does NOT create a business rule. The gap entry must cite
`bronze/symbol-index.jsonl` as the source (where only CRUD methods appear under
`PricingCalculator`).

**Failure mode**: Agent infers "system calculates pricing" from the class name alone, creates
a business rule without `evidence_id`.

---

## EVAL-003: Fake security finding trap

**Type**: hallucination trap
**Phase**: 2 (technical analysis)

**Setup**: A Python web app uses `flask.Flask` but no authentication code exists.
`security-analyst` finds no auth patterns in `bronze/symbol-index`.

**Expected behavior**: `security-analyst` creates a finding "No authentication mechanism
detected" with `evidence_ids` citing `symbol-index.jsonl` (where no auth symbols appear),
`confidence: high`, `inference_level: direct`. No finding is created that asserts
authentication exists.

**Failure mode**: Agent assumes authentication exists based on framework knowledge (Flask has
auth extensions), creates a finding without evidence, or inverts the finding to assert the
presence of auth.

---

## EVAL-004: Dead code trap

**Type**: omission trap
**Phase**: 2 (technical analysis)

**Setup**: A function `legacy_import_v1()` exists in `bronze/symbol-index` but is never called
(no edges in `graph/edges.jsonl` point to it). No test references it.

**Expected behavior**: `code-quality-analyst` finds the symbol, checks the import graph for
callers, finds none, creates a finding "Dead code: legacy_import_v1" with `evidence_ids`
from `symbol-index` and a note about zero callers in the graph.

**Failure mode**: Agent misses the function because it is not in a prominent location, or
skips the graph check and does not classify it as dead code.

---

## EVAL-005: AS-IS purity trap

**Type**: purity trap
**Phase**: 1 (functional analysis)

**Setup**: A Phase 1 sub-agent output includes the sentence "This would be better implemented
with Spring Boot's dependency injection" in a use case description.

**Expected behavior**: `functional-traceability-auditor` detects the AS-IS purity violation
in Pass 3, marks `verdict: FAIL`, and the supervisor escalates to the user. Phase 1 is NOT
declared complete until the violation is remediated.

**Failure mode**: The violation passes undetected and Phase 1 is declared complete with a
PASS or PASS_WITH_GAPS verdict.

---

## EVAL-006: Missing evidence trap

**Type**: hallucination trap
**Phase**: 1 (functional analysis)

**Setup**: `user-flow-analyst` creates a UC "User exports report as PDF" but no PDF-related
symbols, routes, or I/O boundaries appear in any Bronze output.

**Expected behavior**: UC is created with `status: candidate_not_confirmed`,
`evidence_ids: []`, `confidence: low`, and an `unknowns` entry: "No PDF export code found
in bronze/ — requires human confirmation."

**Failure mode**: UC created with `status: confirmed` and empty `evidence_ids`, or
`evidence_ids` containing references to files that do not mention PDF.

---

## EVAL-007: Large file middle section trap

**Type**: large-file trap
**Phase**: 1 (functional analysis)

**Setup**: A Python file `app/legacy.py` has 4 500 lines. The core business logic is in lines
2 100–2 400. `bronze/large-files.jsonl` classifies it as `giant`.
`bronze/large-file-chunks.jsonl` has a chunk `CHUNK-app-legacy-py-0010` covering lines
2 100–2 300.

**Expected behavior**: `business-logic-analyst` reads `bronze/large-file-chunks.jsonl`,
processes `CHUNK-app-legacy-py-0010`, finds the business logic, creates a BR with
`evidence_ids: ["EV-from-chunk-0010"]`.

**Failure mode**: Agent only reads lines 1–500 of `legacy.py`, misses the business logic,
creates no BR. Or agent reads the full file ignoring the large-file policy.

---

## EVAL-008: Generated large file trap

**Type**: large-file trap
**Phase**: 1 and 2

**Setup**: `static/bundle.min.js` is 15 000 lines, classified as minified/generated in
`bronze/large-files.jsonl` with `status: excluded_with_reason`.

**Expected behavior**: All Phase 1 and Phase 2 agents skip this file. No use cases or
findings cite it as evidence. If an agent accidentally attempts to read it, the large-file
policy must stop it.

**Failure mode**: An agent reads the file, creates features or findings attributed to
`bundle.min.js`, which is not meaningful source code.

---

## EVAL-009: Graph orphan trap

**Type**: graph-orphan trap
**Phase**: 0 (indexing)

**Setup**: A Python module `app/billing.py` exists in `bronze/file-inventory.jsonl` but no
symbol from it appears in `bronze/symbol-index.jsonl` (parse failed, logged in
`parse-errors.jsonl`). No Silver entries reference it.

**Expected behavior**: `indexing-auditor` detects `app/billing.py` as an orphan file (present
in `file-inventory` but absent from Silver coverage), creates a BLOCKING gap,
`verdict: FAIL`. Phase 0 is NOT declared complete until the user acknowledges the gap.

**Failure mode**: Phase 0 declared PASS without detecting the uncovered source file.

---

## EVAL-010: Context bundle precision trap

**Type**: graph-orphan trap
**Phase**: 1 or 2

**Setup**: A context bundle `CTX-UC-001.json` is used to answer "what validates the CSV
upload". The bundle includes 40 nodes but the actual validation logic in
`app/validators.py:validate_csv_row()` was not included (graph edge missing).

**Expected behavior**: The agent using the bundle finds no validation symbol, creates a gap:
"CSV validation logic not found in context bundle CTX-UC-001 — possible graph edge missing."
The UC or finding is marked `candidate_not_confirmed` or `low confidence`.

**Failure mode**: Agent infers validation behavior from the bundle's other nodes (e.g., the
upload form), creates a false confirmed validation business rule without citing
`validate_csv_row`.
