# Integrity and security

## 6. Data Integrity and Security

### DB constraints as the last line of defence

```sql
-- Even if the Java Service validates, the DB must have the constraints
-- Scenario: data migration scripts, ETL batch jobs, code bugs — the DB blocks

-- Deferrable constraint — useful for bulk imports where the insert order is random
ALTER TABLE items
    ADD CONSTRAINT fk_items_owner
    FOREIGN KEY (owner_id) REFERENCES owners(id)
    DEFERRABLE INITIALLY DEFERRED; -- checks FK only at COMMIT, not on each INSERT
```

### Handling PostgreSQL errors in Java

```java
// Intercept DB constraint violations in the GlobalExceptionHandler
@ExceptionHandler(DataIntegrityViolationException.class)
public ResponseEntity<ErrorResponse> handleDataIntegrity(DataIntegrityViolationException ex) {
    String message = ex.getMostSpecificCause().getMessage();

    if (message.contains("uq_companies_vat_number")) {
        return buildError(HttpStatus.CONFLICT, "DUPLICATE_VAT_NUMBER",
            "A company with this VAT number already exists");
    }
    if (message.contains("fk_items_owner")) {
        return buildError(HttpStatus.UNPROCESSABLE_ENTITY, "OWNER_NOT_FOUND",
            "Referenced owner does not exist");
    }

    log.error("Data integrity violation: {}", message);
    return buildError(HttpStatus.CONFLICT, "DATA_INTEGRITY_ERROR", "Data constraint violation");
}
```

### SQL Injection — prevention

```java
// ❌ String concatenation — vulnerable to SQL injection
String sql = "SELECT * FROM companies WHERE name = '" + userInput + "'";
jdbcTemplate.query(sql, ...);

// ✅ Parameters with PreparedStatement (JPQL, Spring Data, named params)
@Query("SELECT c FROM Company c WHERE c.name = :name")
List<Company> findByName(@Param("name") String name);

// ✅ JdbcTemplate with parameters
jdbcTemplate.query(
    "SELECT * FROM companies WHERE LOWER(name) LIKE LOWER(?)",
    new Object[]{"%" + searchTerm + "%"},
    rowMapper
);
```

### PostgreSQL roles and permissions

```sql
-- Principle of least privilege — the app must not be a superuser
CREATE ROLE app_user LOGIN PASSWORD 'strong_password';

-- Only the necessary permissions
GRANT CONNECT ON DATABASE myapp TO app_user;
GRANT USAGE ON SCHEMA schema_main TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE
    ON ALL TABLES IN SCHEMA schema_main TO app_user;
GRANT USAGE, SELECT
    ON ALL SEQUENCES IN SCHEMA schema_main TO app_user;

-- Explicitly revoke dangerous permissions
REVOKE CREATE ON SCHEMA schema_main FROM app_user;
REVOKE ALL ON SCHEMA public FROM PUBLIC; -- public schema is open by default

-- Separate role for read-only operations (reporting, analytics)
CREATE ROLE app_readonly LOGIN PASSWORD 'readonly_password';
GRANT CONNECT ON DATABASE myapp TO app_readonly;
GRANT USAGE ON SCHEMA schema_main TO app_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA schema_main TO app_readonly;
```

---
