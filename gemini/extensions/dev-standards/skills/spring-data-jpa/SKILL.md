---
name: spring-data-jpa
description: "This skill should be used when working with JPA/Hibernate inside a Spring project: entity design, relations, fetch strategies, N+1 fixes, transaction boundaries, JPQL queries, second-level cache, bulk operations, automatic auditing, performance tuning. Trigger phrases: \"JPA entity\", \"@OneToMany\", \"N+1 query\", \"@Transactional placement\", \"Hibernate fetch\". Do not use for raw SQL or migrations (use postgresql-expert) or Spring Boot wiring (use spring-expert)."
---

# Spring Data Jpa

Apply these JPA and Hibernate conventions when working on the persistence layer of an enterprise Spring Boot application: entity design, relations, fetch strategies, N+1 resolution, transaction boundaries, query optimisation, caching.

**Scope**: entity design, JPA relations, fetch strategies, N+1, transactions, query optimisation, caching. For Spring Boot config → `spring-expert`. For layered architecture → `spring-architecture`. For core Java → `java-expert`.

## Reference stack

- Spring Data JPA 3.x, Hibernate 6.x (ORM)
- PostgreSQL 15 (production), H2 (testing)
- `@EntityListeners(AuditingEntityListener.class)` for created/updated timestamps

---

## Quick reference: frequent decisions

| Situation | Correct choice |
|---|---|
| Primary key generation on PostgreSQL | `GenerationType.IDENTITY`, not `SEQUENCE` by default |
| Enum persisted on an entity | `@Enumerated(EnumType.STRING)`, never `ORDINAL` |
| `equals` / `hashCode` on an entity | `@EqualsAndHashCode(of = "id")`, never relations or mutable fields |
| `toString` on an entity with collections | `@ToString(exclude = {...})` on every lazy collection |
| Fetch type on `@OneToMany` | `LAZY`, overridden per query with `JOIN FETCH` or `@EntityGraph` |
| Fetch type on `@ManyToOne` / `@OneToOne` | `LAZY`, except towards small entities always required |
| Same fetch graph needed in several repository methods | `@EntityGraph`, not a repeated `JOIN FETCH` |
| Many lazy collections loaded one by one | `@BatchSize(size = 20)` on the relation |
| Many-to-many relation | Explicit join entity, never a bare `@ManyToMany` |
| Query returning a subset of columns | Projection interface or constructor DTO, not the full entity |
| Query that can return many rows | `findAll(Pageable)`, never bare `findAll()` |
| `@Transactional` placement | Public service methods only. A private method is not intercepted |
| Read-only service method | `@Transactional(readOnly = true)` as the class default |
| UPDATE or DELETE in JPQL | `@Modifying` plus `@Transactional`, and `clearAutomatically = true` to drop the L1 cache |
| Inserting thousands of rows | `saveAll` in chunks with `hibernate.jdbc.batch_size` configured |
| Entity returned from a controller | Never. Map to a DTO in the controller layer |

---

## Entity design: base rules

```java
@Entity
@Table(name = "companies", schema = "public",
    indexes = {
        @Index(name = "idx_company_external_code", columnList = "external_code"),
        @Index(name = "idx_company_vat", columnList = "vat_number")
    }
)
@EntityListeners(AuditingEntityListener.class)
@Getter @Setter
@Builder
@NoArgsConstructor      // required by Hibernate (always!)
@AllArgsConstructor
@EqualsAndHashCode(of = "id")     // never include relations
@ToString(exclude = {"orders"}) // avoids lazy init and loops
public class Company {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY) // PostgreSQL: use IDENTITY, not SEQUENCE by default
    private Long id;

    @Column(name = "name", nullable = false, length = 200)
    private String name;

    @Column(name = "external_code", unique = true, length = 20)
    private String externalCode;

    @Column(name = "vat_number", unique = true, length = 11)
    private String vatNumber;

    @Enumerated(EnumType.STRING) // never EnumType.ORDINAL — fragile to reordering
    @Column(name = "status", nullable = false)
    private CompanyStatus status = CompanyStatus.ACTIVE;

    @OneToMany(mappedBy = "company", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    @Builder.Default
    private List<Order> orders = new ArrayList<>();

    @CreatedDate
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}
```

**Entity rules:**
- `@NoArgsConstructor` is mandatory for Hibernate: do not make it `private` when proxying is in use (Hibernate subclasses the entity)
- `equals`/`hashCode` based on `id` (business key), not on mutable fields or relations
- `@Enumerated(EnumType.STRING)` always: ORDINAL breaks when the enum is reordered
- Indices declared in `@Table`: Hibernate creates them with `ddl-auto=create`/`update`

---

## Relations and fetch strategies

Map `@OneToMany` / `@ManyToOne` bidirectionally with the owning side on the `@ManyToOne`, and keep both ends in sync through helper methods on the parent. Model a many-to-many as an explicit join entity, never as a bare `@ManyToMany`, so the association can carry its own columns and lifecycle.

N+1 is the single most common JPA defect: one query for the parents followed by one query per parent for the collection. Detect it with `spring.jpa.show-sql=true` in dev, and resolve it with `JOIN FETCH` in JPQL, a reusable `@EntityGraph`, or `@BatchSize` on the relation. Do not reach for `FetchType.EAGER`, which loads the collection even when nothing needs it.

Full mappings, generated SQL, the JOIN FETCH versus EntityGraph trade-off and the EAGER exception: see [references/relations-and-fetching.md](references/relations-and-fetching.md).

---

## Repository queries and projections

Derived query methods cover the simple cases. Beyond that, write explicit JPQL with `@Query` and named parameters, page every query that can grow, and return a projection (interface-based or constructor DTO) whenever only a subset of the entity's fields is needed.

Query catalogue and both projection styles: see [references/queries-and-projections.md](references/queries-and-projections.md).

---

## Transaction management

`@Transactional` goes on public service methods. Spring's proxy does not intercept a private method or a self-invocation, so the annotation is silently inert there. Default the service class to `@Transactional(readOnly = true)` and override on the writing methods. Keep transactions short and free of external I/O.

Propagation modes, rollback rules and the full list of silent failures: see [references/transactions.md](references/transactions.md).

---

## Performance and auditing

Configure `hibernate.jdbc.batch_size` and insert with `saveAll` in chunks rather than a loop of single saves. Express bulk updates and deletes as `@Modifying` JPQL so the rows never load into the persistence context. Enable the Hibernate second-level cache only for genuinely read-mostly reference data. Wire `@EnableJpaAuditing` plus `@EntityListeners(AuditingEntityListener.class)` so `createdAt` and `updatedAt` are never set by hand.

Batch configuration, bulk statement templates, L2 cache setup and the full auditing wiring: see [references/performance-and-auditing.md](references/performance-and-auditing.md).

---

## JPA/Hibernate anti-patterns to avoid

| Anti-pattern | Problem | Solution |
|---|---|---|
| `FetchType.EAGER` on collections | Always loads, even when not needed | `LAZY` + `JOIN FETCH`/`@EntityGraph` where necessary |
| `@Data` on entities with relations | `toString()`/`equals()` traverse lazy → `LazyInitializationException` / loop | `@EqualsAndHashCode(of="id")` + `@ToString(exclude=...)` |
| `@Transactional` on private methods | Proxy does not intercept → no transaction | Only on `public` methods |
| `EnumType.ORDINAL` | Breaks when the enum is reordered | `EnumType.STRING` always |
| `findAll()` without pagination | OOM on large tables | `findAll(Pageable)` |
| Undetected N+1 | Query explosion in production | `show-sql=true` in dev, profiler in staging |
| Bulk update with loop of saves | N queries instead of 1 | `@Modifying` JPQL bulk + `saveAll` for inserts |
| Entity exposed directly from controller | Schema-API coupling, lazy init during serialisation | DTO always in the controller layer |

---

## Checklist: JPA entity design

- [ ] `@NoArgsConstructor` on all entities
- [ ] `@EqualsAndHashCode(of = "id")`: no relations in equals/hashCode
- [ ] `@ToString(exclude = {...})`: exclude lazy collections
- [ ] `FetchType.LAZY` on `@OneToMany` and `@ManyToOne`, overridden with `JOIN FETCH` where needed
- [ ] `@Enumerated(EnumType.STRING)` on all enum fields
- [ ] `@Transactional(readOnly = true)` as class default in services, override on writes
- [ ] `@Modifying` + `@Transactional` on UPDATE/DELETE JPQL
- [ ] Pagination on all queries that can return many rows
- [ ] Projections for queries that use only a subset of entity fields
- [ ] `batch_size` configured in `application.yml` for bulk insert/update
- [ ] Indices declared in `@Table` for columns used in `WHERE`/`JOIN`

## Detailed references

- **Relation mappings and the full N+1 diagnosis and resolution toolkit**: see [references/relations-and-fetching.md](references/relations-and-fetching.md)
- **Custom repository queries and both projection styles**: see [references/queries-and-projections.md](references/queries-and-projections.md)
- **Transaction placement, propagation modes and silent failures**: see [references/transactions.md](references/transactions.md)
- **Bulk operations, second-level cache and automatic auditing**: see [references/performance-and-auditing.md](references/performance-and-auditing.md)
