# Bulk operations, caching and auditing

Batch insert and update configuration, JPQL bulk statements, the Hibernate
second-level cache, and automatic created/updated auditing.

## Contents

- [Performance: real optimisations](#performance-real-optimisations)
  - [Bulk operations](#bulk-operations)
  - [Bulk update/delete without loading entities](#bulk-updatedelete-without-loading-entities)
  - [Second-level cache (Hibernate L2)](#second-level-cache-hibernate-l2)
- [Automatic auditing](#automatic-auditing)

## Performance: real optimisations

### Bulk operations

```java
// ❌ Loop of individual saves — N separate INSERTs
companies.forEach(companyRepository::save);

// ✅ saveAll — Hibernate can use batch insert if configured
companyRepository.saveAll(companies);

// application.yml — enable batching
spring:
  jpa:
    properties:
      hibernate:
        jdbc:
          batch_size: 50
        order_inserts: true
        order_updates: true
```

### Bulk update/delete without loading entities

```java
// ❌ Loads all entities to update a single field
List<Company> companies = companyRepository.findAll();
companies.forEach(c -> c.setStatus(CompanyStatus.INACTIVE));
// Hibernate generates N separate UPDATEs

// ✅ JPQL bulk update — a single query
@Modifying
@Transactional
@Query("UPDATE Company c SET c.status = :status WHERE c.createdAt < :cutoff")
int bulkDeactivate(@Param("status") CompanyStatus status, @Param("cutoff") LocalDateTime cutoff);
```

**`@Modifying`**: mandatory for UPDATE/DELETE JPQL. Also add `clearAutomatically = true` to clear the first-level cache after the bulk update.

### Second-level cache (Hibernate L2)

```java
// Cacheable entity
@Entity
@Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
public class StatusType { ... } // stable lookup entity — good candidate for L2

// application.yml — Caffeine as provider
spring:
  jpa:
    properties:
      hibernate:
        cache:
          use_second_level_cache: true
          region.factory_class: org.hibernate.cache.jcache.JCacheRegionFactory
```

**L2 candidates**: lookup entities (statuses, types, configurations) that change rarely. **Do not cache** high-write-volume transactional entities.

## Automatic auditing

```java
@SpringBootApplication
@EnableJpaAuditing
public class MyApplication { ... }

// Reusable base entity
@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
public abstract class AuditableEntity {

    @CreatedDate
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @CreatedBy
    @Column(name = "created_by", updatable = false, length = 50)
    private String createdBy;

    @LastModifiedBy
    @Column(name = "updated_by", length = 50)
    private String updatedBy;
}

// AuditorAware implementation — reads user from SecurityContext
@Component
public class SpringSecurityAuditorAware implements AuditorAware<String> {

    @Override
    public Optional<String> getCurrentAuditor() {
        return Optional.ofNullable(SecurityContextHolder.getContext().getAuthentication())
            .filter(Authentication::isAuthenticated)
            .map(Authentication::getName);
    }
}
```
