# JPA relations and fetch strategies

Correct mapping for each relation cardinality, and the full N+1 diagnosis and
resolution toolkit. The SKILL.md body states the rules; this file carries the
mappings, the generated SQL and the trade-offs.

## Contents

- [Relations: correct mapping](#relations-correct-mapping)
  - [One-to-Many / Many-to-One (bidirectional)](#one-to-many--many-to-one-bidirectional)
  - [Many-to-Many: use an explicit join entity](#many-to-many-use-an-explicit-join-entity)
- [Fetch strategies: N+1 is problem #1](#fetch-strategies-n1-is-problem-1)
  - [N+1 diagnosis](#n1-diagnosis)
  - [Solutions for N+1](#solutions-for-n1)

## Relations: correct mapping

### One-to-Many / Many-to-One (bidirectional)

```java
// "Many" side — FK owner
@Entity
public class Order {
    @ManyToOne(fetch = FetchType.LAZY) // LAZY always on ManyToOne
    @JoinColumn(name = "company_id", nullable = false)
    private Company company;
}

// "One" side — helper methods to maintain consistency
@Entity
public class Company {
    @OneToMany(mappedBy = "company", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Order> orders = new ArrayList<>();

    public void addOrder(Order order) {
        orders.add(order);
        order.setCompany(this);
    }

    public void removeOrder(Order order) {
        orders.remove(order);
        order.setCompany(null);
    }
}
```

**`orphanRemoval = true`**: removing an Order from the list makes Hibernate execute the DELETE automatically. Use only when the "many" cannot exist without the "one".

### Many-to-Many: use an explicit join entity

```java
// ❌ @ManyToMany with @JoinTable — does not allow attributes on the relation
@ManyToMany
@JoinTable(name = "company_tags", ...)
private Set<Tag> tags;

// ✅ Explicit join entity — allows extra attributes (assignment date, assigned by, etc.)
@Entity
@Table(name = "company_tags")
public class CompanyTag {
    @EmbeddedId
    private CompanyTagId id;

    @ManyToOne(fetch = FetchType.LAZY) @MapsId("companyId")
    private Company company;

    @ManyToOne(fetch = FetchType.LAZY) @MapsId("tagId")
    private Tag tag;

    @Column(name = "assigned_at")
    private LocalDateTime assignedAt;
}
```

---

## Fetch strategies: N+1 is problem #1

### N+1 diagnosis

```
// JPA logging (dev): spring.jpa.show-sql=true
// Symptom: 1 query for Company + N queries for orders
SELECT * FROM companies WHERE status = 'ACTIVE';      -- 1 query
SELECT * FROM orders WHERE company_id = 1;             -- N queries
SELECT * FROM orders WHERE company_id = 2;
...
```

### Solutions for N+1

```java
// 1. JOIN FETCH in JPQL — for a single query with a collection
@Query("SELECT DISTINCT c FROM Company c LEFT JOIN FETCH c.orders WHERE c.status = :status")
List<Company> findActiveWithOrders(@Param("status") CompanyStatus status);

// 2. @EntityGraph — declarative, reusable
@NamedEntityGraph(name = "Company.withOrders",
    attributeNodes = @NamedAttributeNode("orders"))
@Entity
public class Company { ... }

// In the repository
@EntityGraph("Company.withOrders")
Optional<Company> findWithOrdersById(Long id);

// 3. @BatchSize — Hibernate loads N lazy in batches instead of one-by-one
@OneToMany(mappedBy = "company", fetch = FetchType.LAZY)
@BatchSize(size = 20)
private List<Order> orders;
```

**Trade-off JOIN FETCH vs EntityGraph**: same generated SQL. JOIN FETCH is explicit in the query, EntityGraph is reusable across multiple repository methods. Use EntityGraph when the same graph is needed in multiple places.

**When NOT to use EAGER fetch**: `FetchType.EAGER` always loads the collection even when it is not needed, so avoid it on relations with many elements. Exception: `@ManyToOne` and `@OneToOne` towards small entities that are always required.
