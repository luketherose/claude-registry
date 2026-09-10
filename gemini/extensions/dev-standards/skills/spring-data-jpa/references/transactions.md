# Transaction management

Where `@Transactional` belongs, what each propagation mode changes, and the
failure modes that silently disable a transaction.

## Contents

- [Service and repository placement](#service-and-repository-placement)
- [Propagation: when it changes](#propagation-when-it-changes)
- [Common mistakes with @Transactional](#common-mistakes-with-transactional)

## Service and repository placement

```java
// Service: transaction on the public method
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true) // read-only default for the service — override on writes
public class CompanyServiceImpl implements CompanyService {

    private final CompanyRepository companyRepository;

    // Inherits readOnly = true from the class
    public CompanyResponse getById(Long id) {
        return companyRepository.findById(id)
            .map(companyMapper::toResponse)
            .orElseThrow(() -> new EntityNotFoundException("Company", id));
    }

    @Transactional // read-write — overrides the default
    public CompanyResponse create(CompanyCreateRequest request) {
        if (companyRepository.findByVatNumber(request.vatNumber()).isPresent()) {
            throw new BusinessRuleViolationException(
                "Company already exists with VAT: " + request.vatNumber());
        }
        Company company = companyMapper.toEntity(request);
        return companyMapper.toResponse(companyRepository.save(company));
    }

    @Transactional
    public void delete(Long id) {
        Company company = companyRepository.findById(id)
            .orElseThrow(() -> new EntityNotFoundException("Company", id));
        companyRepository.delete(company);
    }
}
```

**`readOnly = true`**: Hibernate skips dirty checking and flush (~20% less overhead on read-only queries). Set it as the default on the service, with explicit override on write methods.

## Propagation: when it changes

```java
// REQUIRED (default): join the existing transaction or create a new one
@Transactional(propagation = Propagation.REQUIRED)

// REQUIRES_NEW: always a new transaction — useful for a separate audit log
@Transactional(propagation = Propagation.REQUIRES_NEW)
public void saveAuditEvent(AuditEvent event) { ... } // does not roll back with the parent transaction

// NOT_SUPPORTED: suspends the current transaction — for operations that must not run in a transaction
@Transactional(propagation = Propagation.NOT_SUPPORTED)
```

## Common mistakes with @Transactional

```java
// ❌ @Transactional on a private method — Spring proxy does not intercept it
@Transactional
private void internalSave(Company c) { ... } // transaction NOT active

// ❌ Self-invocation — bypasses the proxy
@Service
public class CompanyService {
    @Transactional
    public void processAll() {
        this.save(company); // calls directly, not via proxy → @Transactional ignored
    }

    @Transactional
    public void save(Company c) { ... }
}

// ✅ Inject the proxy (via self-injection or refactoring into separate methods)
```
