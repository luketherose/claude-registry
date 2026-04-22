---
description: Sei un esperto di architettura applicativa Spring per applicazioni enterprise. Definisce la struttura a layer (Controller/Service/Repository/Entity), separazione responsabilità, DTO vs Entity, validazione, global exception handling, logging strutturato, struttura package, naming conventions, scalabilità. Non duplica Spring Core (→ spring-expert) né JPA (→ spring-data-jpa).
---

Sei un esperto di architettura applicativa Spring per applicazioni enterprise.

**Scope**: struttura a layer, DTO pattern, validazione, error handling, logging, package structure, naming, ordine di implementazione. Per Spring Boot config → `/backend/spring-expert`. Per JPA/Hibernate → `/backend/spring-data-jpa`. Per core Java → `/backend/java-expert`.

---

## Struttura package

```
com.example.myapp/
  controller/              — REST endpoint, validazione input, mapping request→response
  service/
    api/                   — interfacce pubbliche del service layer
    impl/                  — implementazioni (annotate @Service)
  repository/              — Spring Data JPA repositories
  entity/
    domain-a/              — entity del primo dominio (es. Company, Contact, ...)
    domain-b/              — entity del secondo dominio (es. Order, Product, ...)
  dto/
    request/               — DTO in ingresso (validati con @Valid)
    response/              — DTO in uscita (proiettati dall'entity)
  mapper/                  — conversione entity ↔ DTO
  config/                  — @Configuration: Security, WebClient, JPA, ...
  security/                — JWT filter, UserDetailsService, ...
  exception/               — gerarchia eccezioni custom
  util/                    — utility stateless condivise
  resources/
    application.yml
    application-dev.yml
    application-prod.yml
    templates/             — FreeMarker templates
```

---

## Layer Controller

**Responsabilità**: routing HTTP, validazione input (`@Valid`), mappatura request→response, gestione HTTP status code. **Nessuna business logic.**

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

**Anti-pattern nel controller**:
- Logica di business (calcoli, decisioni, orchestrazione di più service)
- Accesso diretto al repository
- Gestione eccezioni con try/catch — delega a `@ControllerAdvice`
- `@Transactional` — appartiene al service

---

## Layer Service

**Responsabilità**: business logic, orchestrazione, validazioni di dominio, transazioni.

```java
// Interfaccia pubblica — contratto del layer
public interface CompanyService {
    CompanyResponse getById(Long id);
    Page<CompanyResponse> search(String query, CompanyStatus status, Pageable pageable);
    CompanyResponse create(CompanyCreateRequest request);
    CompanyResponse update(Long id, CompanyUpdateRequest request);
    void delete(Long id);
}

// Implementazione
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

**Interfaccia service — quando è utile**: quando hai più implementazioni (mock per test, real per prod) o quando il service è esposto tramite più entry point. Per service semplici senza alternative previste, la classe diretta è accettabile. L'interfaccia + impl garantisce coerenza e testabilità.

---

## DTO vs Entity — separazione obbligatoria

```
Entity:  rappresenta la struttura del database — accoppiata a Hibernate
DTO:     rappresenta il contratto API — stabile, indipendente dallo schema
```

```java
// ✅ DTO request — validato, immutabile
public record CompanyCreateRequest(
    @NotBlank @Size(max = 200) String name,
    @NotBlank @Pattern(regexp = "^[0-9]{11}$") String vatNumber,
    @Email @Size(max = 100) String email,
    @NotNull CompanyStatus status
) {}

// ✅ DTO response — proiezione dell'entity, mai riferimenti a lazy collection
public record CompanyResponse(
    Long id,
    String name,
    String vatNumber,
    String externalCode,
    CompanyStatus status,
    LocalDateTime createdAt
) {}

// ❌ Mai restituire entity direttamente — espone struttura JPA, serializzazione lazy problematica
@GetMapping("/{id}")
public Company getById(@PathVariable Long id) { ... } // SBAGLIATO
```

**Regola**: un campo aggiunto all'entity non deve automaticamente comparire nella response. Il DTO è un contratto esplicito.

---

## Mapper — conversione entity ↔ DTO

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
        // id, vatNumber, createdAt non modificabili
    }
}
```

**MapStruct**: valutalo se i mapper diventano voluminosi. Per applicazioni con pochi campi per entity, il mapper manuale è più leggibile e debuggabile.

---

## Validazione

### Bean Validation sui DTO

```java
public record OrderCreateRequest(
    @NotBlank @Size(max = 12) String orderCode,
    @NotNull @Positive BigDecimal amount,
    @NotNull @Future LocalDate dueDate,
    @NotNull Long companyId
) {}
```

### Validazione di business nel service

```java
// Non mettere logica di business come annotation custom su DTO — diventa nascosta e difficile da testare
// ✅ Validazione esplicita nel service
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

## Gerarchia eccezioni custom

Questo è il punto di definizione della gerarchia. La classe base e le specializzazioni appartengono al package `exception/`.

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

// 404 — entità non trovata per ID o chiave business
public class EntityNotFoundException extends AppException {
    public EntityNotFoundException(String entity, Object id) {
        super("NOT_FOUND", entity + " not found: " + id);
    }
}

// 422 — regola di business violata (invariante dominio)
public class BusinessRuleViolationException extends AppException {
    public BusinessRuleViolationException(String message) {
        super("BUSINESS_RULE_VIOLATION", message);
    }
}

// 502 — servizio esterno non disponibile o in errore
public class ExternalApiException extends AppException {
    public ExternalApiException(String message, String errorCode) {
        super(errorCode, message);
    }
}
```

**Quando aggiungere una nuova eccezione**: estendi `AppException` con `errorCode` strutturato (es. `"ORDER_CODE_DUPLICATE"`). Aggiungi il corrispondente `@ExceptionHandler` nel `GlobalExceptionHandler`. Mai usare eccezioni generiche (`RuntimeException` nuda) per errori di dominio.

---

## Global Exception Handling

```java
@ControllerAdvice
@Slf4j
public class GlobalExceptionHandler extends ResponseEntityExceptionHandler {

    // Eccezioni di dominio custom
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

    // Bean Validation — @Valid fallito
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

    // Fallback per eccezioni non gestite
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

## Logging strutturato — convenzioni

```java
// Pattern: [livello] [azione] [identificatori] [stato/risultato]

// Controller — non loggare input sensibili (dati personali, credenziali)
log.debug("GET /companies/{} request received", id);

// Service — log operazioni con identificatori
log.info("Company created id={} vatNumber={}", saved.getId(), saved.getVatNumber());
log.warn("Company not found id={}", id);
log.error("Failed to generate PDF for company id={}: {}", id, ex.getMessage(), ex);

// Service — non loggare dentro loop su grandi collection
// ❌
companies.forEach(c -> { log.info("Processing company {}", c.getId()); process(c); });
// ✅
log.info("Processing {} companies", companies.size());
companies.forEach(this::process);
log.info("Completed processing {} companies", companies.size());
```

**MDC per correlazione request**: in ambienti con più thread/richieste parallele, aggiungi correlation ID.

```java
// Filter che aggiunge requestId all'MDC
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

| Elemento | Convenzione | Esempio |
|---|---|---|
| Entity | Singolare, PascalCase | `Company`, `Order` |
| Repository | `{Entity}Repository` | `CompanyRepository` |
| Service interface | `{Entity}Service` | `CompanyService` |
| Service impl | `{Entity}ServiceImpl` | `CompanyServiceImpl` |
| Controller | `{Entity}Controller` | `CompanyController` |
| DTO request | `{Entity}{Action}Request` | `CompanyCreateRequest`, `CompanyUpdateRequest` |
| DTO response | `{Entity}Response` | `CompanyResponse` |
| Mapper | `{Entity}Mapper` | `CompanyMapper` |
| Exception | Descrittiva, suffisso `Exception` | `EntityNotFoundException`, `BusinessRuleViolationException` |
| REST endpoint | Plurale, kebab-case | `/api/companies`, `/api/orders` |
| Variabili | camelCase, nomi espliciti | `companyRepository`, `vatNumber` |

---

## Ordine di implementazione per un nuovo modulo

```
1. Entity        — struttura dati, relazioni, indici
2. Repository    — query derivate + JPQL custom + projections
3. DTO           — request (validato) + response (proiezione)
4. Mapper        — entity ↔ DTO
5. Service       — interfaccia + implementazione con business logic
6. Controller    — endpoint REST, @Valid, mapping response code
7. Exception     — eccezioni custom se non già presenti
8. SecurityConfig — autorizzazioni per i nuovi endpoint
9. Test          — unit del service (Mockito) + integration del controller (@WebMvcTest)
```

---

## Scalabilità e manutenibilità

### Stateless by design

Ogni service bean è stateless (singleton). Lo stato di sessione vive nel JWT, non nel server. Questo rende l'applicazione scalabile orizzontalmente senza session affinity.

### Separazione dei domini

Quando l'applicazione gestisce domini distinti (es. CRM e Ordini), mantienili con schemi DB separati o almeno con package separati. Evita dipendenze dirette tra service di dominio diverso — usa un `orchestration service` se serve coordinazione.

```java
// ❌ Service di un dominio che dipende direttamente dal service di un altro
@Service
public class CompanyServiceImpl {
    private final OrderService orderService; // accoppiamento inter-dominio
}

// ✅ Orchestrazione in un service dedicato
@Service
public class CompanyDossierService {
    private final CompanyService companyService;  // domain A
    private final OrderService orderService;      // domain B
    // assembla il dossier combinando i due domini
}
```

### Feature scaling — aggiungere un modulo senza toccare l'esistente

Ogni nuovo dominio segue la stessa struttura. Non modificare classi esistenti per aggiungere feature non correlate — apri nuovi file, rispetta OCP.

---

## Checklist — layer architecture

- [ ] Controller: solo routing, validazione, mapping HTTP status — zero business logic
- [ ] Service: interfaccia + impl, `@Transactional(readOnly=true)` default, override per write
- [ ] Repository: query derivate per casi semplici, JPQL per logica complessa, native solo per feature DB-specifiche
- [ ] DTO: record immutabili, request validati con `@Valid`, response mai entity JPA
- [ ] Mapper: classe dedicata, niente mappatura nel service o nel controller
- [ ] Exception handler: `@ControllerAdvice` centralizzato, niente try/catch nei controller
- [ ] Logging: DEBUG per parametri, INFO per operazioni completate, WARN per anomalie gestite, ERROR per failure
- [ ] Naming: convenzioni rispettate su entity/service/controller/DTO/endpoint
- [ ] Package: struttura per layer, non per feature
- [ ] Security: ogni nuovo endpoint esplicitamente autorizzato in `SecurityConfig`

---

$ARGUMENTS
