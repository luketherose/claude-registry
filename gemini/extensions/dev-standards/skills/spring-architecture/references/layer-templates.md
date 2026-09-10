# Layer templates

## Contents

- Controller layer
- Service layer
- Mapper: entity ↔ DTO conversion (mandatory layer)

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
- Exception handling with try/catch, which belongs in `@ControllerAdvice`
- `@Transactional`, which belongs in the service layer

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

**When a service interface is useful**: when multiple implementations exist (mock for tests, real for production) or when the service is exposed through multiple entry points. For simple services without foreseen alternatives, a direct class is acceptable. The interface + impl pattern guarantees consistency and testability.

---

## Mapper: entity ↔ DTO conversion (mandatory layer)

A dedicated `*Mapper` class lives between the service layer and the controller. **Entities never reach the controller**, neither as method parameters nor as return types. The mapper is the only place allowed to convert entity ↔ DTO.

**Forbidden patterns** (production-defect-grade, do not generate code that does any of these):

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
- Every controller endpoint that returns a body returns a typed DTO (`record` or final class), never `Map<String,Object>`, never `Map.of(...)`, never an anonymous inline class.
- Service methods may return entities to other services in the same domain, but never to a controller. The mapper is invoked at the service-controller boundary.
- One mapper per aggregate root. Avoid one giant `MapperFacade` for the whole module.
- The mapper has no Spring dependencies beyond `@Component`: no `HttpServletRequest`, no `SecurityContext`, no DB lookups. If a field needs enrichment, do it in the service before mapping.

**MapStruct**: consider it if mappers become bulky. For applications with few fields per entity, a manual mapper is more readable and debuggable.

---
