---
name: spring-architecture
description: "This skill should be used when designing or reviewing the LAYERING of a Spring Boot module: Controller/Service/Repository/Entity boundaries, DTO+mapper introduction, Bean Validation placement, global exception handling, naming conventions, or module implementation order. Trigger phrases: \"add a new module\", \"where does this belong\", \"split this controller\", \"DTO mapping\", \"how do I layer this Spring code\". Do not use for Spring Boot configuration concerns (use spring-expert) or JPA/ORM specifics (use spring-data-jpa)."
---

# Spring Architecture

Apply these layering conventions when structuring or reviewing an enterprise Spring application.

**Scope**: layered structure, DTO pattern, validation, error handling, logging, package structure, naming, implementation order. For Spring Boot config → `spring-expert`. For JPA/Hibernate → `spring-data-jpa`. For core Java → `java-expert`.

---

## Package structure

```
com.example.myapp/
  controller/              — REST endpoints, input validation, request→response mapping
  service/
    api/                   — public service layer interfaces
    impl/                  — implementations (annotated with @Service)
  repository/              — Spring Data JPA repositories
  entity/
    domain-a/              — entities for the first domain (e.g. Company, Contact, ...)
    domain-b/              — entities for the second domain (e.g. Order, Product, ...)
  dto/
    request/               — inbound DTOs (validated with @Valid)
    response/              — outbound DTOs (projected from entity)
  mapper/                  — entity ↔ DTO conversion
  config/                  — @Configuration: Security, WebClient, JPA, ...
  security/                — JWT filter, UserDetailsService, ...
  exception/               — custom exception hierarchy
  util/                    — shared stateless utilities
  resources/
    application.yml
    application-dev.yml
    application-prod.yml
    templates/             — FreeMarker templates
```

---

## DTO vs Entity: mandatory separation

```
Entity:  represents the database structure — coupled to Hibernate
DTO:     represents the API contract — stable, independent of the schema
```

```java
// ✅ Request DTO — validated, immutable
public record CompanyCreateRequest(
    @NotBlank @Size(max = 200) String name,
    @NotBlank @Pattern(regexp = "^[0-9]{11}$") String vatNumber,
    @Email @Size(max = 100) String email,
    @NotNull CompanyStatus status
) {}

// ✅ Response DTO — projection of the entity, never references lazy collections
public record CompanyResponse(
    Long id,
    String name,
    String vatNumber,
    String externalCode,
    CompanyStatus status,
    LocalDateTime createdAt
) {}

// ❌ Never return entity directly — exposes JPA structure, lazy serialisation is problematic
@GetMapping("/{id}")
public Company getById(@PathVariable Long id) { ... } // WRONG
```

**Rule**: a field added to the entity should not automatically appear in the response. The DTO is an explicit contract.

---

## Validation

### Bean Validation on DTOs

```java
public record OrderCreateRequest(
    @NotBlank @Size(max = 12) String orderCode,
    @NotNull @Positive BigDecimal amount,
    @NotNull @Future LocalDate dueDate,
    @NotNull Long companyId
) {}
```

### Business validation in the service

```java
// Do not put business logic as custom annotations on DTOs — it becomes hidden and hard to test
// ✅ Explicit validation in the service
@Transactional
public OrderResponse create(OrderCreateRequest request) {
    Company company = companyRepository.findById(request.companyId())
        .orElseThrow(() -> new EntityNotFoundException("Company", request.companyId()));

    if (company.getStatus() != CompanyStatus.ACTIVE) {
        throw new BusinessRuleViolationException(
            "Cannot add Order to inactive company: " + request.companyId());
    }

    if (orderRepository.existsByOrderCode(request.orderCode())) {
        throw new BusinessRuleViolationException("Order code already exists: " + request.orderCode());
    }

    // ...
}
```

---

## Structured logging: conventions

```java
// Pattern: [level] [action] [identifiers] [state/result]

// Controller — do not log sensitive input (personal data, credentials)
log.debug("GET /companies/{} request received", id);

// Service — log operations with identifiers
log.info("Company created id={} vatNumber={}", saved.getId(), saved.getVatNumber());
log.warn("Company not found id={}", id);
log.error("Failed to generate PDF for company id={}: {}", id, ex.getMessage(), ex);

// Service — do not log inside loops over large collections
// ❌
companies.forEach(c -> { log.info("Processing company {}", c.getId()); process(c); });
// ✅
log.info("Processing {} companies", companies.size());
companies.forEach(this::process);
log.info("Completed processing {} companies", companies.size());
```

**MDC for request correlation**: in environments with multiple threads/parallel requests, add a correlation ID.

```java
// Filter that adds requestId to the MDC
@Component
public class MdcLoggingFilter extends OncePerRequestFilter {
    @Override
    protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res,
                                    FilterChain chain) throws ServletException, IOException {
        String requestId = Optional.ofNullable(req.getHeader("X-Request-ID"))
            .orElse(UUID.randomUUID().toString().substring(0, 8));
        MDC.put("requestId", requestId);
        res.setHeader("X-Request-ID", requestId);
        try {
            chain.doFilter(req, res);
        } finally {
            MDC.clear();
        }
    }
}
```

---

## Naming conventions

| Element | Convention | Example |
|---|---|---|
| Entity | Singular, PascalCase | `Company`, `Order` |
| Repository | `{Entity}Repository` | `CompanyRepository` |
| Service interface | `{Entity}Service` | `CompanyService` |
| Service impl | `{Entity}ServiceImpl` | `CompanyServiceImpl` |
| Controller | `{Entity}Controller` | `CompanyController` |
| Request DTO | `{Entity}{Action}Request` | `CompanyCreateRequest`, `CompanyUpdateRequest` |
| Response DTO | `{Entity}Response` | `CompanyResponse` |
| Mapper | `{Entity}Mapper` | `CompanyMapper` |
| Exception | Descriptive, `Exception` suffix | `EntityNotFoundException`, `BusinessRuleViolationException` |
| REST endpoint | Plural, kebab-case | `/api/companies`, `/api/orders` |
| Variables | camelCase, explicit names | `companyRepository`, `vatNumber` |

---

## Implementation order for a new module

```
1. Entity:        data structure, relations, indices
2. Repository:    derived queries + custom JPQL + projections
3. DTO:           request (validated) + response (projection)
4. Mapper:        entity ↔ DTO
5. Service:       interface + implementation with business logic
6. Controller:    REST endpoints, @Valid, response code mapping
7. Exception:     custom exceptions if not already present
8. SecurityConfig: authorisation for the new endpoints
9. Test:          service unit tests (Mockito) + controller integration tests (@WebMvcTest)
```

---

## Scalability and maintainability

### Stateless by design

Every service bean is stateless (singleton). Session state lives in the JWT, not on the server. This makes the application horizontally scalable without session affinity.

### Domain separation

When the application manages distinct domains (e.g. CRM and Orders), keep them with separate DB schemas or at minimum with separate packages. Avoid direct dependencies between services from different domains: use an `orchestration service` if coordination is needed.

```java
// ❌ Service of one domain that directly depends on the service of another
@Service
public class CompanyServiceImpl {
    private final OrderService orderService; // inter-domain coupling
}

// ✅ Orchestration in a dedicated service
@Service
public class CompanyDossierService {
    private final CompanyService companyService;  // domain A
    private final OrderService orderService;      // domain B
    // assembles the dossier by combining the two domains
}
```

### Feature scaling: adding a module without touching existing code

Each new domain follows the same structure. Do not modify existing classes to add unrelated features: open new files, respect OCP.

---

## Checklist: layer architecture

- [ ] Controller: routing, validation, HTTP status mapping only, zero business logic
- [ ] Service: interface + impl, `@Transactional(readOnly=true)` default, override for writes
- [ ] Repository: derived queries for simple cases, JPQL for complex logic, native only for DB-specific features
- [ ] DTO: immutable records, requests validated with `@Valid`, responses never JPA entities
- [ ] Mapper: dedicated class, no mapping in the service or controller
- [ ] Exception handler: centralised `@ControllerAdvice`, no try/catch in controllers
- [ ] Logging: DEBUG for parameters, INFO for completed operations, WARN for handled anomalies, ERROR for failures
- [ ] Naming: conventions respected for entity/service/controller/DTO/endpoint
- [ ] Package: structure by layer, not by feature
- [ ] Security: every new endpoint explicitly authorised in `SecurityConfig`

## Detailed references

- **Full code templates for the controller, service and mapper layers**: see [references/layer-templates.md](references/layer-templates.md)
- **Custom exception hierarchy and RFC 7807 global exception handling**: see [references/error-handling.md](references/error-handling.md)
