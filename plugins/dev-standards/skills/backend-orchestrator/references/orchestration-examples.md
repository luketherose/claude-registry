# Orchestration examples

## Contents

- 9. Orchestration examples
- Case 1 — Complete CRUD endpoint for a new module
- Case 2 — Slow query optimisation
- Case 3 — Bug between Service and Repository

## 9. Orchestration examples

### Case 1 — Complete CRUD endpoint for a new module

**Request**: "Create the CRUD endpoints to manage investors (Investor) with name, email, type (RETAIL/INSTITUTIONAL) and a list of allocations"

**Classification**: TYPE A — New feature

**Skills activated in order**:

1. **`spring-architecture`** — defines the contracts:
   - `InvestorCreateRequest`, `InvestorResponse` (records)
   - `InvestorService` (public interface)
   - Package structure: `com.example.projectname.entity`, `dto/request`, `dto/response`
   - Endpoints: `POST /api/investors`, `GET /api/investors/{id}`, `PUT`, `DELETE`

2. **`postgresql-expert`** — schema:
   ```sql
   CREATE TABLE investors (
       id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
       name TEXT NOT NULL,
       email TEXT NOT NULL,
       investor_type TEXT NOT NULL CHECK (investor_type IN ('RETAIL', 'INSTITUTIONAL')),
       CONSTRAINT uq_investors_email UNIQUE (email)
   );
   CREATE INDEX idx_investors_type ON investors (investor_type);
   ```

3. **`spring-data-jpa`** — entity + repository:
   - `@Entity`, `@Enumerated(EnumType.STRING)`, `@EqualsAndHashCode(of="id")`
   - `InvestorRepository extends JpaRepository<Investor, Long>`
   - Custom query: `findByInvestorType(InvestorType type, Pageable pageable)`

4. **`spring-architecture`** (return) — mapper + service impl + complete controller

**Key decisions**:
- `investor_type` is TEXT in the DB (not SMALLINT) → aligned to `EnumType.STRING`
- Pagination on GET collection from the start — the list can grow
- `email` has `UNIQUE` in the DB as well as `@Email` in the DTO — double defence

---

### Case 2 — Slow query optimisation

**Request**: "The main list page takes many seconds"

**Classification**: TYPE C — Optimisation

**Skills activated in order**:

1. **`postgresql-expert`** — DB diagnosis:
   ```sql
   EXPLAIN (ANALYZE, BUFFERS)
   SELECT p.*, r.*
   FROM parent_table p LEFT JOIN related_table r ON r.parent_id = p.id
   WHERE p.status = 'ACTIVE';
   ```
   - Identifies: Seq Scan on `related_table` (FK without index)
   - Fix: `CREATE INDEX idx_related_parent_id ON related_table (parent_id)`

2. **`spring-data-jpa`** — N+1 check:
   - Does Hibernate generate 1 query for the parent + N queries for the related? → N+1
   - Fix: `@Query("SELECT DISTINCT p FROM Parent p LEFT JOIN FETCH p.related WHERE p.status = 'ACTIVE'")`
   - Or `@EntityGraph` if the graph is reusable

3. **`java-expert`** — stream/mapping check (only if DB+ORM already optimised)

**Key decisions**:
- Do not add caching as the first response — the problem was the missing index
- Do not change the architecture — it is not a structural problem
- Verify in staging with EXPLAIN before making JPA optimisations

---

### Case 3 — Bug between Service and Repository

**Request**: "Saving an entity with relationships fails with LazyInitializationException"

**Classification**: TYPE B — Bug

**Skills activated in order**:

1. **`spring-data-jpa`** — diagnosis:
   - `LazyInitializationException` = access to lazy collection outside the Hibernate session
   - Common causes: JSON serialisation of the entity outside `@Transactional`, or `toString()` with lazy relationships
   - Check: is the controller serialising an entity instead of a DTO?

2. **`spring-architecture`** — structural check:
   - Is the entity returned by the controller? → violates the DTO principle
   - Is `@Transactional` on the correct method (public, in the service)?

3. **`spring-expert`** — Spring check:
   - Is the bean a singleton? Is the transaction active in the correct context?
   - `@Transactional` on a private method? → Spring does not intercept it

**Typical root cause**: the service returns the entity (not the DTO) to the controller, which then serialises it with Jackson. Jackson accesses a lazy relationship outside the JPA session.

**Fix**:
- Map the entity to DTO before leaving the service (inside the transaction)
- Or add `@Transactional(readOnly=true)` to the controller (weak solution — avoid)

**Key decisions**:
- The correct fix is architectural (DTO) — do not add `FetchType.EAGER` as a workaround
- `EAGER` resolves the symptom but creates explosive queries — it worsens performance

---
