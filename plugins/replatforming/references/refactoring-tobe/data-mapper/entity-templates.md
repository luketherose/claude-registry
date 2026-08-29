# Data-mapper — entity / value-object / repository / mapper templates

> Reference doc for `data-mapper`. Read at runtime when about to emit JPA
> classes. The decision rules (when to use UUID vs composite keys, when to
> emit @Embeddable, etc.) live in the agent body under `## Method`. The
> code skeletons below are the literal shapes to copy-and-parametrise.

## Entity (one per aggregate / entity)

```java
package com.<org>.<app>.<bc>.domain;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import java.time.Instant;

/**
 * <Entity name> — domain entity in BC-NN.
 *
 * Aggregate root: <yes | no — part of <root> aggregate>
 * Invariants:
 *   - <invariant 1, e.g., "Email is unique system-wide">
 *   - <invariant 2>
 *
 * AS-IS source ref: <repo>/<as-is-pkg>/<file>:<class>
 */
@Entity
@Table(name = "users",
       uniqueConstraints = @UniqueConstraint(name = "uk_users_email", columnNames = "email"))
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "id", updatable = false, nullable = false)
    private UUID id;

    @NotBlank
    @Email
    @Column(name = "email", nullable = false, length = 255)
    private String email;

    @NotBlank
    @Column(name = "password_hash", nullable = false, length = 60)
    private String passwordHash;

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false, length = 20)
    private UserStatus status;

    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt;

    @Column(name = "updated_at", nullable = false)
    private Instant updatedAt;

    @Version
    private Long version;

    // JPA requires no-args constructor — keep package-private
    User() {}

    // Public factory honors invariants
    public static User register(String email, String passwordHash, String fullName) {
        // TODO(BC-01, UC-01): logic-translator will populate; for now
        // basic field setting + initial state machine value
        var u = new User();
        u.id = UUID.randomUUID();
        u.email = email;
        u.passwordHash = passwordHash;
        u.status = UserStatus.PENDING;
        var now = Instant.now();
        u.createdAt = now;
        u.updatedAt = now;
        return u;
    }

    // getters only by default — setters reserved for state-changing
    // methods that enforce invariants
    public UUID getId() { return id; }
    public String getEmail() { return email; }
    public UserStatus getStatus() { return status; }
    // ... additional getters
}
```

Header comments are mandatory: BC, aggregate role, invariants, AS-IS source ref.

## Enum (state machine / type)

```java
package com.<org>.<app>.<bc>.domain;

/**
 * User account status.
 *
 * State machine (per UC-04 from Phase 1):
 *   PENDING → ACTIVE     (after email confirmation)
 *   ACTIVE  → SUSPENDED  (admin action, UC-07)
 *   ACTIVE  → DELETED    (user request, UC-09)
 *   SUSPENDED → ACTIVE   (admin action)
 *
 * AS-IS source ref: <repo>/<as-is-pkg>/<file>:<line>
 */
public enum UserStatus {
    PENDING,
    ACTIVE,
    SUSPENDED,
    DELETED
}
```

If Phase 1 `12-implicit-logic.md` documented the state machine, mirror it.
If not, surface a question.

## Value object (@Embeddable)

```java
package com.<org>.<app>.<bc>.domain;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import java.math.BigDecimal;
import java.util.Currency;

/**
 * Monetary amount value object.
 *
 * Invariants:
 *   - amount has scale = currency.defaultFractionDigits
 *   - currency is non-null
 *
 * AS-IS source ref: <repo>/<as-is-pkg>/<file>:<line>
 */
@Embeddable
public record Money(
        @NotNull BigDecimal amount,
        @NotNull Currency currency) {

    public Money {
        // TODO(BC-02, UC-NN): enforce scale invariant from AS-IS source
    }
}
```

## Repository (Spring Data JPA)

One repository per aggregate root, in the `infrastructure/` package:

```java
package com.<org>.<app>.<bc>.infrastructure;

import com.<org>.<app>.<bc>.domain.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

/**
 * Repository for the User aggregate.
 *
 * Bounded context: BC-01.
 * Cross-aggregate queries: see <Other>Repository.
 */
@Repository
public interface UserRepository extends JpaRepository<User, UUID> {

    Optional<User> findByEmail(String email);

    @Query("select u from User u where u.status = 'ACTIVE'")
    java.util.List<User> findAllActive();

    // TODO(BC-01): add AS-IS query patterns from Phase 2
    // access-pattern-map.md (e.g., findByTenantAndDateRange)
}
```

If the AS-IS access-pattern-map flagged raw SQL for performance, preserve a
`@Query(nativeQuery = true)` form here with a TODO.

## MapStruct mapper (optional)

If ADR-002 specifies MapStruct (recommended for non-trivial mappings):

```java
package com.<org>.<app>.<bc>.api;

import com.<org>.<app>.<bc>.domain.User;
import com.<org>.<app>.<bc>.api.dto.UserDto;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface UserMapper {
    UserDto toDto(User entity);
    User toEntity(CreateUserRequest request);
}
```

Else, hand-write a `<Aggregate>Mapper` static helper class. The scaffolder
placed a placeholder; you replace it.

## Idempotency repository implementation

`backend-scaffolder` left an `IdempotencyKeyRepository` interface in
`shared/idempotency/`. Provide its JPA implementation here:

```java
package com.<org>.<app>.shared.idempotency;

import jakarta.persistence.*;
import java.time.Instant;
import org.springframework.data.jpa.repository.JpaRepository;

@Entity
@Table(name = "idempotency_keys")
public class IdempotencyKeyEntity {
    @Id
    @Column(length = 100)
    private String key;
    @Column(length = 100, nullable = false)
    private String operationId;
    @Column(columnDefinition = "TEXT")
    private String responseSnapshot;
    @Column(nullable = false)
    private Instant createdAt;
    // ...
}

public interface IdempotencyKeyJpaRepository
        extends IdempotencyKeyRepository, JpaRepository<IdempotencyKeyEntity, String> {}
```

Plus a Liquibase changeSet for the `idempotency_keys` table (appended to
`01__baseline_schema.yaml` or as its own `<NN>__idempotency.yaml` changelog).
