# Migration roadmap — example milestones

> Reference doc for `migration-roadmap-builder`. Read at runtime when
> filling in concrete milestone entries in `docs/refactoring/roadmap.md`.

## Goal

Worked example milestones (foundation, BC cutover, AS-IS retirement) the
agent copies and parametrises. Use alongside `roadmap-template.md`.

---

## M-00 — Foundation (always present)

Cross-cutting milestone — not BC-specific. Place at the start of the
roadmap.

- **BCs**: none (cross-cutting)
- **Activities**: deploy backend + frontend in staging, wire
  observability, run smoke tests; no production traffic yet.
- **Go-live criteria**: staging green; smoke tests pass; on-call rotation
  briefed.
- **Duration**: 2 weeks (typical).
- **Dependencies**: none.
- **Sign-off**: ops.

---

## M-01 — Identity & Access (worked example BC milestone)

- **BCs**: BC-01
- **UCs**: UC-01, UC-04, UC-09
- **AS-IS modules retired**: infosync.auth.*, infosync.users.*
- **API endpoints**: /v1/users/*, /v1/auth/*
- **FE feature module**: identity
- **Pre-conditions**: M-00 done
- **Activities**: ...
- **Cutover**: 1% → 10% → 50% → 100% over 2 weeks
- **Go-live**: 100% UC equivalence, p95 ≤ 110%
- **Rollback trigger**: error rate >0.5% sustained 5 min OR p95 >120%
  sustained 10 min OR critical security finding
- **Rollback procedure**: flag→0%; data is forward-compatible (no schema
  rollback needed because TO-BE schema is additive vs AS-IS)
- **Duration**: 3 weeks
- **Dependencies**: M-00
- **Risks**: token migration; sessions on AS-IS will continue until
  expiry; no auto-relog after cutover (acceptable per ADR-003)
- **Sign-off**: PO + Security

---

## M-Final — AS-IS retirement (always present)

Cross-cutting milestone — not BC-specific. Place at the end of the
roadmap.

- **BCs**: none (cross-cutting)
- **Activities**: after all BC milestones complete, retire AS-IS
  application (preserve DB if needed; archive logs; decommission
  infrastructure).
- **Go-live criteria**: AS-IS receiving 0 traffic for ≥ <X> days; final
  data reconciliation passes; sign-off from PO + ops.
- **Duration**: 2 weeks (typical).
- **Dependencies**: all BC milestones complete.
- **Sign-off**: PO + ops + security.

---

## Strangler-fig topology choices

The cutover requires a routing layer that decides per-request whether to
send traffic to AS-IS or TO-BE. Document the choice in §"Cutover
topology" of the roadmap with a one-paragraph rationale.

### Topology A — Reverse proxy (NGINX / Envoy)

A proxy in front of both apps; routes by path:
- `/v1/<resource-group-A>/*` → TO-BE
- `/<old-streamlit-route>` → AS-IS (preserved)

Advantages: simple, explicit, atomic per-route cutover.

### Topology B — API gateway with feature flags

A gateway (Kong / AWS API Gateway / Spring Cloud Gateway) with feature
flags per route:
- flag ON → TO-BE
- flag OFF → AS-IS
- flag percent → canary

Advantages: progressive rollout, instant rollback via flag toggle.

### Topology C — DNS / load balancer

Two FQDNs; switch DNS or LB at cutover. Coarsest grain; lowest control.

### Default recommendation

- **Topology A** for medium projects.
- **Topology B** for high-stakes domains (banking / fintech).
- **Topology C** only when neither A nor B is operationally feasible.
