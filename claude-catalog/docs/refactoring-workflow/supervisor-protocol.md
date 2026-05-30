# Refactoring Supervisor — Protocol Reference

Read this document at bootstrap start, before any escalation or HITL prompt,
and whenever consulting the workflow phase map or output format rules.

---

## Workflow phases

| Phase | Name | Supervisor | Output root | Status |
|---|---|---|---|---|
| 0 | Codebase Indexing | `indexing-supervisor` | `.indexing-kb/` | implemented |
| 1 | AS-IS Functional Analysis | `functional-analysis-supervisor` | `docs/analysis/01-functional/` | implemented |
| 2 | AS-IS Technical Analysis | `technical-analysis-supervisor` | `docs/analysis/02-technical/` | implemented |
| 3 | AS-IS Baseline Testing | `baseline-testing-supervisor` | `tests/baseline/` + `docs/analysis/03-baseline/` | implemented |
| 4 | Application Replatforming | this agent (drives 7-step loop directly) | `docs/refactoring/` + `backend/` + `frontend/` + `e2e/` | implemented |

**Phase outputs (highlights).** Phase 0 produces a Bronze/Silver/Gold KB plus `evidence-ledger.jsonl` and a `graph/` context graph (canonical stack path: `.indexing-kb/bronze/stack.json`). Phase 1 and Phase 2 produce `normalized/` JSONL alongside the markdown (`use-case-candidates.jsonl`, `feature-candidates.jsonl`, `technical-findings.jsonl`, `risk-register.jsonl`, plus audit verdicts). **Phase 4 must consume normalized JSONL**, not narrative markdown alone, and must NOT treat `candidate_not_confirmed` UCs as certain requirements.

**No Phase 5.** The previous Phase 5 (TO-BE Testing & Equivalence Verification) has been absorbed into Phase 4 Step 6 in v3.0.0. If the user references "Phase 5", clarify that the workflow now ends at Phase 4 and final validation is Step 6.

**Unimplemented phases** (go-live automation, post-launch monitoring, performance tuning loops, deprecation of AS-IS). Respond: "Phase N is not yet implemented. Currently supported: Phase 0–4." Do not invent content for unsupported phases. Do not silently extend scope.

---

## Escalation triggers — always ask the user

- **Bootstrap, pre-phase, post-phase**: always.
- **Mid-phase**: never — phase supervisors own their mid-phase HITL.
- **Phase failure**: always; offer `iterate`/`revise` or `stop`, never auto-retry.
- **Unimplemented phase requested**: refuse and clarify.
- **Output-paths conflict** with existing files: confirm before allowing overwrite.

---

## Output format for user-facing messages

Keep updates terse between protocol steps. The verbose blocks are the pre-phase brief and the post-phase recap (templates in `per-phase-protocol.md`) — those are shown verbatim. Anything outside of those should be one to three lines.
