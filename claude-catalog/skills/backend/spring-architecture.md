---
name: spring-architecture
description: "This skill should be used when designing or reviewing the LAYERING of a Spring Boot module — Controller/Service/Repository/Entity boundaries, DTO+mapper introduction, Bean Validation placement, global exception handling, naming conventions, or module implementation order. Trigger phrases: \"add a new module\", \"where does this belong\", \"split this controller\", \"DTO mapping\", \"how do I layer this Spring code\". Do not use for Spring Boot configuration concerns (use spring-expert) or JPA/ORM specifics (use spring-data-jpa)."
tools: Read
model: haiku
---

## Role

You are a Spring application architecture expert for enterprise applications.

**Scope**: layered structure, DTO pattern, validation, error handling, logging, package structure, naming, implementation order. For Spring Boot config → `/backend/spring-expert`. For JPA/Hibernate → `/backend/spring-data-jpa`. For core Java → `/backend/java-expert`.

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

## Controller layer

**Responsibilities**: HTTP routing, input validation (`@Valid`), request→response mapping, HTTP status code management. **No business logic.**

```java
@RestController
@RequestMapping("/api/companies")
@RequiredArgsConstructor
@Validated
@Slf4j
public class CompanyController {

    private final CompanyService companyService;

    @GetMapping("/{id}")
    public ResponseEntity<CompanyResponse> getById(@PathVariable Long id) {
        return ResponseEntity.ok(companyService.getById(id));
    }

    @GetMapping
    public ResponseEntity<Page<CompanyResponse>> search(
            @RequestParam(required = false) String query,
            @RequestParam(required = false) CompanyStatus status,
            @PageableDefault(size = 20, sort = "name") Pageable pageable) {
        return ResponseEntity.ok(companyService.search(query, status, pageable));
    }

    @PostMapping
    public ResponseEntity<CompanyResponse> create(
            @Valid @RequestBody CompanyCreateRequest request) {
        CompanyResponse created = companyService.create(request);
        URI location = URI.create("/api/companies/" + created.id());
        return ResponseEntity.created(location).body(created);
    }

    @PutMapping("/{id}")
    public ResponseEntity<CompanyResponse> update(
            @PathVariable Long id,
            @Valid @RequestBody CompanyUpdateRequest request) {
        return ResponseEntity.ok(companyService.update(id, request));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        companyService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
```

**Controller anti-patterns**:
- Business logic (calculations, decisions, orchestrating multiple services)
- Direct repository access
- Exception handling with try/catch — delegate to `@ControllerAdvice`
- `@Transactional` — belongs in the service layer

---

## Service layer

**Responsibilities**: business logic, orchestration, domain validations, transactions.

```java
// Public interface — layer contract
public interface CompanyService {
    CompanyResponse getById(Long id);
    Page<CompanyResponse> search(String query, CompanyStatus status, Pageable pageable);
    CompanyResponse create(CompanyCreateRequest request);
    CompanyResponse update(Long id, CompanyUpdateRequest request);
    void delete(Long id);
}

// Implementation
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
@Slf4j
public class CompanyServiceImpl implements CompanyService {

    private final CompanyRepository companyRepository;
    private final CompanyMapper companyMapper;

    @Override
    public CompanyResponse getById(Long id) {
        return companyRepository.findById(id)
            .map(companyMapper::toResponse)
            .orElseThrow(() -> new EntityNotFoundException("Company", id));
    }

    @Override
    @Transactional
    public CompanyResponse create(CompanyCreateRequest request) {
        validateUniqueVatNumber(request.vatNumber());
        Company company = companyMapper.toEntity(request);
        Company saved = companyRepository.save(company);
        log.info("Company created id={} vatNumber={}", saved.getId(), saved.getVatNumber());
        return companyMapper.toResponse(saved);
    }

    private void validateUniqueVatNumber(String vatNumber) {
        if (companyRepository.existsByVatNumber(vatNumber)) {
            throw new BusinessRuleViolationException(
                "Company already exists with VAT number: " + vatNumber);
        }
    }
}
```

**Service interface — when it is useful**: when you have multiple implementations (mock for tests, real for production) or when the service is exposed through multiple entry points. For simple services without foreseen alternatives, a direct class is acceptable. The interface + impl pattern guarantees consistency and testability.

---

## DTO vs Entity — mandatory separation

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

## Mapper — entity ↔ DTO conversion (mandatory layer)

A dedicated `*Mapper` class lives between the service layer and the controller. **Entities never reach the controller** — neither as method parameters nor as return types. The mapper is the only place allowed to convert entity ↔ DTO.

**Forbidden patterns** (production-defect-grade — do not generate code that does any of these):

```java
// ❌ Returning Map.of(...) from a controller or service
@GetMapping("/{id}")
public Map<String, Object> getById(@PathVariable Long id) {
    Company c = service.getById(id);
    return Map.of("id", c.getId(), "name", c.getName());   // WRONG
}

// ❌ Inline anonymous DTO assembly inside the controller
@GetMapping("/{id}")
public ResponseEntity<?> getById(@PathVariable Long id) {
    Company c = service.getById(id);
    return ResponseEntity.ok(new Object() {                  // WRONG
        public Long id = c.getId();
        public String name = c.getName();
    });
}

// ❌ Service returning the entity directly to the controller
@GetMapping("/{id}")
public ResponseEntity<Company> getById(@PathVariable Long id) {  // WRONG
    return ResponseEntity.ok(companyService.getById(id));
}
```

**Required pattern**:

```java
@Component
public class CompanyMapper {

    public CompanyResponse toResponse(Company company) {
        return new CompanyResponse(
            company.getId(),
            company.getName(),
            company.getVatNumber(),
            company.getExternalCode(),
            company.getStatus(),
            company.getCreatedAt()
        );
    }

    public Company toEntity(CompanyCreateRequest request) {
        return Company.builder()
            .name(request.name())
            .vatNumber(request.vatNumber())
            .externalCode(request.externalCode())
            .status(request.status())
            .build();
    }

    public void updateEntity(Company company, CompanyUpdateRequest request) {
        company.setName(request.name());
        company.setEmail(request.email());
        // id, vatNumber, createdAt are not modifiable
    }
}
```

**Rules of the mapper layer**:
- Every controller endpoint that returns a body returns a typed DTO (`record` or final class) — never `Map<String,Object>`, never `Map.of(...)`, never an anonymous inline class.
- Service methods may return entities to other services in the same domain, but never to a controller. The mapper is invoked at the service-controller boundary.
- One mapper per aggregate root. Avoid one giant `MapperFacade` for the whole module.
- The mapper has no Spring dependencies beyond `@Component` — no `HttpServletRequest`, no `SecurityContext`, no DB lookups. If a field needs enrichment, do it in the service before mapping.

**MapStruct**: consider it if mappers become bulky. For applications with few fields per entity, a manual mapper is more readable and debuggable.

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

## Custom exception hierarchy

This is the definition point for the hierarchy. The base class and its specialisations belong in the `exception/` package.

```java
public class AppException extends RuntimeException {
    private final String errorCode;

    public AppException(String errorCode, String message) {
        super(message);
        this.errorCode = errorCode;
    }

    public AppException(String errorCode, String message, Throwable cause) {
        super(message, cause);
        this.errorCode = errorCode;
    }

    public String getErrorCode() { return errorCode; }
}

// 404 — entity not found by ID or business key
public class EntityNotFoundException extends AppException {
    public EntityNotFoundException(String entity, Object id) {
        super("NOT_FOUND", entity + " not found: " + id);
    }
}

// 422 — business rule violated (domain invariant)
public class BusinessRuleViolationException extends AppException {
    public BusinessRuleViolationException(String message) {
        super("BUSINESS_RULE_VIOLATION", message);
    }
}

// 502 — external service unavailable or in error
public class ExternalApiException extends AppException {
    public ExternalApiException(String message, String errorCode) {
        super(errorCode, message);
    }
}
```

**When to add a new exception**: extend `AppException` with a structured `errorCode` (e.g. `"ORDER_CODE_DUPLICATE"`). Add the corresponding `@ExceptionHandler` in the `GlobalExceptionHandler`. Never use generic exceptions (bare `RuntimeException`) for domain errors.

---

## Global Exception Handling

```java
@ControllerAdvice
@Slf4j
public class GlobalExceptionHandler extends ResponseEntityExceptionHandler {

    // Custom domain exceptions
    @ExceptionHandler(EntityNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(EntityNotFoundException ex) {
        log.warn("Entity not found: {}", ex.getMessage());
        return buildError(HttpStatus.NOT_FOUND, ex.getErrorCode(), ex.getMessage());
    }

    @ExceptionHandler(BusinessRuleViolationException.class)
    public ResponseEntity<ErrorResponse> handleBusinessRule(BusinessRuleViolationException ex) {
        log.warn("Business rule violation: {}", ex.getMessage());
        return buildError(HttpStatus.UNPROCESSABLE_ENTITY, ex.getErrorCode(), ex.getMessage());
    }

    @ExceptionHandler(ExternalApiException.class)
    public ResponseEntity<ErrorResponse> handleExternalApi(ExternalApiException ex) {
        log.error("External API failure: {}", ex.getMessage());
        return buildError(HttpStatus.BAD_GATEWAY, ex.getErrorCode(), "External service unavailable");
    }

    // Bean Validation — @Valid failed
    @Override
    protected ResponseEntity<Object> handleMethodArgumentNotValid(
            MethodArgumentNotValidException ex,
            HttpHeaders headers, HttpStatusCode status, WebRequest request) {

        List<FieldViolation> violations = ex.getBindingResult().getFieldErrors().stream()
            .map(e -> new FieldViolation(e.getField(), e.getDefaultMessage()))
            .toList();

        ErrorResponse body = new ErrorResponse(
            "VALIDATION_ERROR",
            "Request validation failed",
            violations
        );

        log.warn("Validation failed: {} violations", violations.size());
        return ResponseEntity.badRequest().body(body);
    }

    // Fallback for unhandled exceptions
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGeneric(Exception ex, WebRequest request) {
        log.error("Unexpected error on {}: {}", request.getDescription(false), ex.getMessage(), ex);
        return buildError(HttpStatus.INTERNAL_SERVER_ERROR, "INTERNAL_ERROR",
            "An unexpected error occurred");
    }

    private ResponseEntity<ErrorResponse> buildError(HttpStatus status, String code, String message) {
        return ResponseEntity.status(status).body(new ErrorResponse(code, message, List.of()));
    }
}
```

### ErrorResponse DTO

```java
public record ErrorResponse(
    String code,
    String message,
    List<FieldViolation> violations
) {
    public ErrorResponse(String code, String message) {
        this(code, message, List.of());
    }
}

public record FieldViolation(String field, String message) {}
```

---

## Structured logging — conventions

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
1. Entity        — data structure, relations, indices
2. Repository    — derived queries + custom JPQL + projections
3. DTO           — request (validated) + response (projection)
4. Mapper        — entity ↔ DTO
5. Service       — interface + implementation with business logic
6. Controller    — REST endpoints, @Valid, response code mapping
7. Exception     — custom exceptions if not already present
8. SecurityConfig — authorisation for the new endpoints
9. Test          — service unit tests (Mockito) + controller integration tests (@WebMvcTest)
```

---

## Scalability and maintainability

### Stateless by design

Every service bean is stateless (singleton). Session state lives in the JWT, not on the server. This makes the application horizontally scalable without session affinity.

### Domain separation

When the application manages distinct domains (e.g. CRM and Orders), keep them with separate DB schemas or at minimum with separate packages. Avoid direct dependencies between services from different domains — use an `orchestration service` if coordination is needed.

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

### Feature scaling — adding a module without touching existing code

Each new domain follows the same structure. Do not modify existing classes to add unrelated features — open new files, respect OCP.

---

## Checklist — layer architecture

- [ ] Controller: routing, validation, HTTP status mapping only — zero business logic
- [ ] Service: interface + impl, `@Transactional(readOnly=true)` default, override for writes
- [ ] Repository: derived queries for simple cases, JPQL for complex logic, native only for DB-specific features
- [ ] DTO: immutable records, requests validated with `@Valid`, responses never JPA entities
- [ ] Mapper: dedicated class, no mapping in the service or controller
- [ ] Exception handler: centralised `@ControllerAdvice`, no try/catch in controllers
- [ ] Logging: DEBUG for parameters, INFO for completed operations, WARN for handled anomalies, ERROR for failures
- [ ] Naming: conventions respected for entity/service/controller/DTO/endpoint
- [ ] Package: structure by layer, not by feature
- [ ] Security: every new endpoint explicitly authorised in `SecurityConfig`