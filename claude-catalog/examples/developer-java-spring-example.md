# Example: developer-java-spring

## Scenario 1: Add a new REST endpoint with full layered structure

**Setup**: Existing Spring Boot 3 project with `customer` and `invoice` packages. Need to add allocation management.

**User prompt**:
> Add CRUD endpoints to manage allocations. An Allocation has invoice_id, account_id, amount.
> Follow the existing project conventions.

**What the subagent does**:
1. Loads `java-spring-standards`, `testing-standards`, `rest-api-standards` skills
2. Reads existing `customer/` and `invoice/` packages to mirror their structure
3. Produces the full layered output in dependency order:
   - **Migration**: Flyway `V<N>__create_allocations.sql` with FK indexes and constraints
   - **Entity**: `Allocation` with `@NoArgsConstructor`, `@EqualsAndHashCode(of="id")`, `FetchType.LAZY` on relationships
   - **Repository**: `AllocationRepository extends JpaRepository<Allocation, Long>`
   - **DTOs**: `AllocationCreateRequest` (validated), `AllocationResponse` (records)
   - **Mapper**: `AllocationMapper` interface
   - **Service**: `AllocationService` interface + `AllocationServiceImpl` with `@Transactional`
   - **Controller**: `AllocationController` with `@Valid`, semantically-correct status codes
   - **Tests**: unit (Mockito) + `@WebMvcTest` integration test

**Expected output characteristics**:
- No business logic in controller
- No JPA entity exposed past the service boundary
- DB types aligned with JPA enums (`@Enumerated(EnumType.STRING)` ↔ `TEXT` in DDL)
- `GlobalExceptionHandler` updated to map domain exceptions to RFC 7807 ProblemDetail

---

## Scenario 2: Refactor an N+1 query

**Setup**: User reports the `/invoices` list endpoint is slow.

**User prompt**:
> The list invoices endpoint is taking 5+ seconds. Fix it.

**What the subagent does**:
1. Reads the controller → service → repository chain
2. Identifies N+1: lazy-loaded relationships hydrated per row
3. Asks for `EXPLAIN ANALYZE` if available, otherwise inspects JPQL
4. Applies the fix in priority order:
   - Add `@EntityGraph` or `JOIN FETCH` on the repository method
   - Verify DB index exists on the FK
   - Add a projection if the full entity isn't needed for the response
5. Adds a regression test using Testcontainers + Hibernate statistics to assert query count

**What the subagent does NOT do**:
- Add `FetchType.EAGER` as a workaround
- Introduce caching before profiling
- Rewrite the entire repository

---

## Scenario 3: Code review of existing controller

**User prompt**:
> Review `OrderController.java` against our standards.

**What the subagent does**:
1. Loads `java-spring-standards` and `rest-api-standards` skills
2. Identifies violations and severity-rates them:
   - **Blocker**: business logic in controller, entity returned directly
   - **Critical**: missing `@Valid` on `@RequestBody`
   - **Major**: try/catch in controller (should delegate to `GlobalExceptionHandler`)
   - **Minor**: log level mismatches, missing javadoc
3. Produces a structured review with file:line references and proposed diffs
4. Marks issues that the agent will not auto-fix unless explicitly asked
