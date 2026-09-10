# Repository queries and projections

Custom query authoring in Spring Data JPA repositories, and the two ways to
return a narrowed result set.

## Contents

- [Repository with custom queries](#repository-with-custom-queries)
- [Projections: interface-based (alternative to constructor DTO)](#projections-interface-based-alternative-to-constructor-dto)

## Repository with custom queries

```java
public interface CompanyRepository extends JpaRepository<Company, Long> {

    // Derived query — for simple conditions
    Optional<Company> findByExternalCode(String externalCode);
    List<Company> findByStatusOrderByNameAsc(CompanyStatus status);

    // JPQL — for more complex logic, type-safe
    @Query("""
        SELECT c FROM Company c
        WHERE LOWER(c.name) LIKE LOWER(CONCAT('%', :query, '%'))
          AND c.status = 'ACTIVE'
        ORDER BY c.name
        """)
    List<Company> searchByName(@Param("query") String query);

    // JPQL with JOIN FETCH
    @Query("""
        SELECT DISTINCT c FROM Company c
        LEFT JOIN FETCH c.orders o
        WHERE c.id = :id
        """)
    Optional<Company> findByIdWithOrders(@Param("id") Long id);

    // Native query — for PostgreSQL-specific features (ANY, JSONB, full-text)
    @Query(value = "SELECT * FROM companies WHERE external_code = ANY(:codes)",
           nativeQuery = true)
    List<Company> findAllByExternalCodes(@Param("codes") String[] codes);

    // Projection — only the required fields (avoids hydrating the entire entity)
    @Query("SELECT new com.example.myapp.dto.CompanySummary(c.id, c.name, c.externalCode) FROM Company c WHERE c.status = 'ACTIVE'")
    List<CompanySummary> findActiveSummaries();

    // Pagination
    @Query("SELECT c FROM Company c WHERE c.status = :status")
    Page<Company> findByStatus(@Param("status") CompanyStatus status, Pageable pageable);
}
```

### Projections: interface-based (alternative to constructor DTO)

```java
public interface CompanyProjection {
    Long getId();
    String getName();
    String getExternalCode();
}

// In the repository — Spring Data automatically generates the proxy
List<CompanyProjection> findProjectedByStatus(CompanyStatus status);
```

**When to use a projection**: when entities are large but the query only needs to return 3–4 fields. Avoids hydrating the entire entity just to serialise it partially.
