# Evals: developer-java-spring

---

## Eval-001: New CRUD endpoint — happy path

**Input context**: Empty Spring Boot 3 project with PostgreSQL configured via Testcontainers. Existing `customer` package as reference.

**User prompt**: "Add CRUD for `Order` (id, customer_id, total, status). Status enum: DRAFT, PENDING, FULFILLED."

**Expected output characteristics**:
- Flyway migration with `orders` table, FK + index on `customer_id`, CHECK constraint on `status`
- `Order` JPA entity: `@NoArgsConstructor`, `@EqualsAndHashCode(of="id")`, `FetchType.LAZY`, `@Enumerated(EnumType.STRING)` aligned to TEXT DDL
- DTOs as records: `OrderCreateRequest` with `@Valid` constraints, `OrderResponse`
- `OrderService` interface + `OrderServiceImpl` with `@Transactional(readOnly = true)` default and `@Transactional` on writes
- `OrderController` with no business logic; status codes: 201 Created, 204 No Content for delete
- `GlobalExceptionHandler` returns RFC 7807 ProblemDetail
- Unit test on service with Mockito, integration test with `@WebMvcTest` or `@SpringBootTest` + Testcontainers

**Must NOT contain**:
- Entity returned past the service→controller boundary
- Business logic in the controller
- `try/catch` blocks around the service call
- `FetchType.EAGER` on relationships

---

## Eval-002: N+1 detection and fix

**Input context**: Existing repository method `findAll()` returning entities with lazy `OneToMany` collections; controller serializes them.

**User prompt**: "The `/orders` endpoint is slow. Fix."

**Expected behavior**:
- Identifies the N+1 source via stack trace, query log, or static reading
- Applies a `@Query("... JOIN FETCH ...")` or `@EntityGraph` solution
- Does NOT introduce caching, does NOT switch to `FetchType.EAGER`
- Adds a regression test that asserts query count using Hibernate `Statistics`
- Verifies/adds DB index on the FK if missing

---

## Eval-003: Code review against standards

**Input context**: Existing controller with violations: business logic inline, entity returned, missing `@Valid`.

**User prompt**: "Review `OrderController.java`."

**Expected behavior**:
- Severity-rated findings table (Blocker / Critical / Major / Minor) with file:line references
- Identifies all violations, including subtle ones (log levels, missing constructor injection)
- Does NOT auto-apply fixes unless explicitly asked
- References the specific standard violated (e.g., `java-spring-standards § Controller layer`)

---

## Eval-004: Spring Security baseline

**Input context**: New microservice without security configuration.

**User prompt**: "Add JWT-based authentication."

**Expected behavior**:
- Adds `SecurityFilterChain` bean (Spring Security 6 functional config), no `WebSecurityConfigurerAdapter`
- JWT validation via `JwtDecoder` bean (uses `spring-boot-starter-oauth2-resource-server`)
- Configures CSRF appropriately (disabled for stateless API)
- Endpoint authorization rules in `SecurityFilterChain`, not on individual controllers
- Tests cover: valid token, expired token, missing token, role mismatch
- Does NOT use `@EnableGlobalMethodSecurity` (deprecated)

---

## Eval-005: Refusal of insecure shortcut

**User prompt**: "Quick fix — just put the SQL query directly in the controller for now."

**Expected behavior**:
- Refuses politely
- Explains the architectural issue (controller has no business with persistence)
- Offers the correct minimal version (delegate to a service method)
- Does NOT comply with the shortcut even if user insists weakly
