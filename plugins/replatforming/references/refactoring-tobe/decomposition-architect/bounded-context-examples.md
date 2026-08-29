# Decomposition-architect — bounded-context worked examples

> Reference doc for `decomposition-architect`. Worked entry shapes for the
> `Bounded contexts` section of `bounded-contexts.md` and the per-BC sections
> of `aggregate-design.md`.

---

## Bounded-context entry (used in `bounded-contexts.md`)

### BC-01 — Identity & Access

- **Purpose**: authentication, authorization, user profile
- **Use cases owned**: UC-01, UC-04, UC-09
- **Aggregates**: User (root), Session, Role
- **Ubiquitous language**: User, Tenant, Role, Permission, Session
- **AS-IS modules covered**: `infosync.auth.*`, `infosync.users.*`
- **Upstream of**: BC-02 (provides authenticated User principal)
- **Downstream of**: none
- **Domain events emitted**: UserRegistered, SessionExpired

### BC-02 — Payments

- ...

---

## Aggregate-design entry (used in `aggregate-design.md`)

## BC-01 Identity & Access

### Aggregate: User

- **Aggregate root**: `User`
- **Members**:
  - `Email` (value object)
  - `PasswordHash` (value object)
  - `UserStatus` (enum value object)
  - `Role[]` (cross-aggregate refs by RoleId)
- **Invariants**:
  - Email is unique (enforced at repository, not in aggregate)
  - PasswordHash never null after registration
  - Status transitions follow state machine: PENDING → ACTIVE →
    {SUSPENDED, DELETED}
- **Cross-aggregate references**: Role (by RoleId only)

### Aggregate: Session
- ...

## BC-02 Payments
- ...
