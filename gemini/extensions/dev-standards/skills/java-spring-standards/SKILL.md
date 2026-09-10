---
name: java-spring-standards
description: "This skill should be used when an agent (developer-java, pr-review-toolkit:code-reviewer, test-writer) needs the canonical Java/Spring Boot standards: package structure, layering rules, DI, JUnit 5 + Mockito + Testcontainers, RFC 7807 ProblemDetail, SLF4J + MDC logging, Spring Security 6 baseline, Micrometer observability, and Maven conventions. Trigger phrases: \"Spring standards\", \"review this Spring code\", \"how should I structure this Spring module\". Returns reference material, not code. Do not trigger directly from a coding prompt. Use spring-expert (config), spring-architecture (layering), or spring-data-jpa (ORM)."
---

# Java Spring Standards

This skill is the authoritative source for Java/Spring Boot development
standards used by this team. Apply the section of
the standard with enough precision that the calling agent can apply it without
ambiguity.

For every standard returned:
1. The rule (stated precisely)
2. The rationale (one sentence)
3. A minimal concrete example where the rule is non-obvious

Does not write production code, make architectural decisions, or answer
questions outside this domain. If asked about Python, REST design, or
architecture trade-offs, redirect to the relevant skill.

---

## Technology Baseline

| Component | Standard | Notes |
|---|---|---|
| Java | 21 LTS | Use Records, Sealed Classes, Text Blocks, Pattern Matching |
| Spring Boot | 3.3.x+ | Spring 6.x; Jakarta EE namespace |
| Build | Maven 3.9+ | Maven preferred; Gradle 8+ acceptable |
| Container base | `eclipse-temurin:21-jre-alpine` | Minimal JRE, not JDK, for runtime |
| Java version | SDKMAN or `.java-version` (jenv) | Pin version in project |

---

## Package Structure

```
com.{company}.{service}/
  {ServiceName}Application.java:     @SpringBootApplication, main only, no beans
  controller/:      HTTP layer: request/response mapping, validation trigger
  service/:         Business logic: @Service, @Transactional where needed
  repository/:      Data access: Spring Data JPA interfaces, @Query methods
  domain/:          JPA entities, domain objects, enums
  dto/:             Request/Response DTOs: validation annotations, no JPA mappings
  config/:          @Configuration classes, Bean definitions, security config
  exception/:       Typed exception hierarchy, @RestControllerAdvice
  mapper/:          DTO ↔ domain mapping (manual or MapStruct)
```

---

## Layering Rules (non-negotiable)

- **Controllers**: HTTP only. Deserialize request, call one service method, return response.
  No business logic. No repository access. No JPA entities in responses.
- **Services**: All business logic. No HTTP concepts (HttpServletRequest, etc.).
  Single responsibility: one service per bounded subdomain.
- **Repositories**: Spring Data JPA interfaces. Custom queries use `@Query`.
  No business logic in repositories.
- **Entities**: Pure JPA domain objects. No business logic. No Jackson annotations.
  Prefer `@Column(nullable = false)` where DB schema enforces it.
- **DTOs**: Immutable records (Java 16+) or final classes. Validation annotations go on
  DTOs, never on entities.
- Dependency direction: Controller → Service → Repository → Domain. Never reverse.
- No circular dependencies between packages.

---

## Dependency Injection

**Constructor injection only.** Never `@Autowired` on fields or setters.

```java
// Correct
@Service
public class OrderService {
    private final OrderRepository orderRepository;
    private final PaymentService paymentService;

    public OrderService(OrderRepository orderRepository, PaymentService paymentService) {
        this.orderRepository = orderRepository;
        this.paymentService = paymentService;
    }
}
```

Use `@RequiredArgsConstructor` (Lombok) only if Lombok is already a declared
dependency in the project's build file.

---

## Testing standards

JUnit 5 plus Mockito for unit tests, which must not start a Spring context.
`@SpringBootTest` plus Testcontainers plus `@Transactional` (rollback after each)
for integration tests. `@WebMvcTest` with MockMvc and a mocked service for
controller slices. Name every test method `{method}_{condition}_{expectedOutcome}`
with no `test` prefix, and structure the body Arrange-Act-Assert. JaCoCo enforces
a 70% line-coverage floor in CI.

Full templates for all three tiers and the per-layer coverage expectations: see [references/testing.md](references/testing.md).

---

## Error handling (RFC 7807)

Every service throws from a typed exception hierarchy rooted in a single
application exception. A `@RestControllerAdvice` maps each type to an RFC 7807
`ProblemDetail` carrying `type`, `title`, `status`, `detail` and `instance`.
Never swallow an exception, never log and rethrow at the same layer, never expose
a stack trace or an internal class name in an API response, and never use an
exception for flow control. Return `Optional<T>` for the absent case instead.

Hierarchy, global handler and the full rule list: see [references/error-handling.md](references/error-handling.md).

---

## Security, logging and observability

Spring Security 6 with stateless sessions for REST APIs, method-level
authorisation and JSR-380 validation triggered on DTOs at the controller
boundary. SLF4J with MDC correlation context (`traceId`, `userId`, `requestId`)
and structured JSON in production. Never log a password, token, PII, credit card
or secret. Actuator plus Micrometer for metrics and OpenTelemetry for traces, and
SpringDoc annotations on every public endpoint.

Security config, log level rules, metric and trace setup and the OpenAPI
annotations: see [references/security-logging-observability.md](references/security-logging-observability.md).

---

## Code formatting (non-negotiable)

One annotation per line, vertically stacked, on classes, methods, fields and
parameters alike. One POM element per line, never a collapsed `<dependency>`.
Controllers and services never return `Map.of(...)`, a `HashMap<>` or an
anonymous inline class as a response body. Always return a typed DTO produced by
a `*Mapper` class.

Correct and incorrect form of each rule: see [references/formatting.md](references/formatting.md).

---

## Maven Conventions

- Always inherit from `spring-boot-starter-parent` or `spring-boot-dependencies` BOM
- Use `<dependencyManagement>`: no inline version tags for Spring-managed dependencies
- Profiles: `local` (H2 in-memory + Liquibase + seed data), `test` (Testcontainers), `prod` (external DB, structured logging)
- `application.yml` preferred over `application.properties`
- JaCoCo minimum 70% line coverage enforced in CI
- SpotBugs: zero HIGH findings gate; OWASP Dependency Check: no CRITICAL CVEs
- **Schema migration tool: Liquibase**, the only supported migration tool. Flyway is forbidden. Default changelog at `db/changelog/db.changelog-master.yaml`.
- **Local-dev database: H2 in-memory**, configured via `application-local.yml` with Liquibase applying both schema and a seed-data changeset so a fresh checkout is runnable with zero external dependencies.

Approved dependencies:
`spring-boot-starter-web`, `spring-boot-starter-data-jpa`, `spring-boot-starter-security`,
`spring-boot-starter-validation`, `spring-boot-starter-actuator`, `spring-boot-starter-test`,
`springdoc-openapi-starter-webmvc-ui`, `logstash-logback-encoder`,
`micrometer-tracing-bridge-otel`, `liquibase-core`, `h2` (runtime, scope `runtime`),
`testcontainers`, `testcontainers-postgresql`

## Detailed references

- **Unit, integration and controller test templates with coverage expectations**: see [references/testing.md](references/testing.md)
- **Typed exception hierarchy and the RFC 7807 global handler**: see [references/error-handling.md](references/error-handling.md)
- **Spring Security 6 baseline, validation, logging, Micrometer and SpringDoc**: see [references/security-logging-observability.md](references/security-logging-observability.md)
- **Annotation stacking, POM layout and the inline-response ban**: see [references/formatting.md](references/formatting.md)
