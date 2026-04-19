# Java/Spring Boot Conventions

This document defines the team's conventions for Java/Spring Boot projects. These
conventions are enforced by the `developer-java-spring` subagent and should be
referenced in project CLAUDE.md files.

---

## Technology baseline

| Component | Standard | Notes |
|-----------|----------|-------|
| Java | 21 LTS | Use Records, Sealed Classes, Text Blocks, Pattern Matching |
| Spring Boot | 3.3.x+ | Spring 6.x; Jakarta EE namespace |
| Build | Maven 3.9+ or Gradle 8+ | Maven preferred for new projects |
| Java version management | SDKMAN or `.java-version` (jenv) | Pin version in project |
| Container base image | `eclipse-temurin:21-jre-alpine` | Minimal JRE, not JDK, for runtime |

---

## Package structure

```
com.{company}.{service}/
  {ServiceName}Application.java    — @SpringBootApplication, no logic
  controller/
    {Resource}Controller.java      — @RestController, @RequestMapping
  service/
    {Domain}Service.java           — @Service interface
    {Domain}ServiceImpl.java       — Implementation
  repository/
    {Entity}Repository.java        — extends JpaRepository<Entity, Long>
  domain/
    {Entity}.java                  — @Entity, JPA annotations
    {Enum}.java                    — domain enums
  dto/
    {Resource}Request.java         — input: Java record with validation
    {Resource}Response.java        — output: Java record or class
  mapper/
    {Domain}Mapper.java            — DTO ↔ entity, no Spring context needed
  config/
    SecurityConfig.java
    {Feature}Config.java
  exception/
    ApplicationException.java      — abstract base
    {Specific}Exception.java       — concrete exceptions
    GlobalExceptionHandler.java    — @RestControllerAdvice
```

---

## Mandatory rules

### Spring Boot
- `@SpringBootApplication` class contains only the `main` method and no beans
- No `@ComponentScan` on non-root packages unless absolutely required
- Use `@ConfigurationProperties` for typed configuration binding (not `@Value` for
  multi-property groups)
- `application.yml` preferred over `application.properties`
- Profiles: `dev`, `test`, `prod`. No `local` profile that differs significantly from `dev`.

### JPA / Persistence
- All entities have a surrogate key (`@Id @GeneratedValue`)
- `@Column(nullable = false)` mirrors the DB constraint
- No `fetch = FetchType.EAGER` unless specifically justified and documented
- Use `@Transactional` at service method level, not class level
- Never use `EntityManager.flush()` in business logic; let Spring manage flush
- Flyway for schema migrations; no `spring.jpa.hibernate.ddl-auto=update` in non-dev

### REST
- API versioning in URI: `/api/v1/`
- All endpoints return `ResponseEntity<T>` for explicit status code control
- Request DTOs are Java records with bean validation annotations
- Response DTOs are Java records or immutable classes — no JPA entities in responses
- Pagination: `Page<T>` from Spring Data; always paginate collection endpoints

### Testing
- Unit tests: no `@SpringBootTest`, use `@ExtendWith(MockitoExtension.class)`
- Integration tests: `@SpringBootTest`, `@ActiveProfiles("test")`, Testcontainers
- Controller tests: `@WebMvcTest` + `@MockBean` for the service layer
- Test class naming: `{ClassName}Test.java`
- Test method naming: `{method}_{condition}_{outcome}`

---

## Dependency guidelines

Prefer Spring Boot starters over manual dependency declarations.

Approved dependencies (non-exhaustive):
- `spring-boot-starter-web` — REST
- `spring-boot-starter-data-jpa` — JPA
- `spring-boot-starter-security` — Security
- `spring-boot-starter-validation` — Bean Validation
- `spring-boot-starter-actuator` — Observability
- `spring-boot-starter-test` — Test scope
- `springdoc-openapi-starter-webmvc-ui` — OpenAPI docs
- `logstash-logback-encoder` — Structured logging
- `micrometer-tracing-bridge-otel` — Distributed tracing
- `testcontainers` + `testcontainers-postgresql` — Integration tests

Do not add dependencies without a PR discussion if they are not on this list.

---

## Code quality gates (CI)

- Checkstyle: Sun or Google style (project choice, enforced consistently)
- SpotBugs: enabled, zero HIGH findings gate
- JaCoCo: 70% minimum line coverage
- OWASP Dependency Check: no CRITICAL CVEs gate
