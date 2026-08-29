# Output specification

## Contents

- Output Format
- 1. Migration Scope Summary
- 2. Library Equivalence Map
- 3. Data Layer Migration
- 4. Service Layer Migration
- 5. API Layer Migration
- 6. Business Rules Implementation Guide
- 7. Cross-Cutting Concerns Migration
- 8. Data Migration Script Guidance
- 9. Testing Strategy
- 10. Migration Pitfall Register

## Output Format

### 1. Migration Scope Summary

Restate what is being migrated:
- Components in scope
- Python patterns present (from framework + code analysis)
- Target Spring components to be created

### 2. Library Equivalence Map

For every Python library used in the scope:

| Python Library | Spring/Java Equivalent | Migration Notes | Risk |
|---|---|---|---|

Flag [NO DIRECT EQUIVALENT:] where applicable with recommended approach.

### 3. Data Layer Migration

For each Django model / SQLAlchemy model / raw table in scope:

---
**[ModelName]** → `[JavaEntityName].java`

Python (source):
```python
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_id = models.IntegerField()
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
```

Java (target stub):
```java
@Entity
@Table(name = "order_items")
@Getter @Setter
public class OrderItem {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "order_id", nullable = false)
    private Order order;
    
    @Column(name = "product_id", nullable = false)
    private Integer productId;
    
    @Column(nullable = false)
    @Positive
    private Integer quantity;
    
    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal unitPrice;
}
```

Migration Notes: [specific considerations]
Business Rules Applied: [BR-N references]

---

### 4. Service Layer Migration

For each Python service/manager/helper in scope:

---
**[PythonServiceName]** → `[JavaServiceName].java`

Responsibilities (from functional spec): [list]

Java stub:
```java
@Service
@RequiredArgsConstructor
public class OrderService {
    private final OrderRepository orderRepository;
    private final PaymentGatewayClient paymentGatewayClient;
    
    public OrderDto createOrder(CreateOrderRequest request) {
        // BR-001: Validate inventory before creating order
        // BR-003: Apply customer discount tier
        // Implementation to be completed
        throw new UnsupportedOperationException("To be implemented");
    }
}
```

Business Rules to Implement: [BR-N references with implementation guidance]
Python Patterns to Translate: [list with Java equivalents]
[ARCHITECTURAL DECISION NEEDED: <description>] (if any)

---

### 5. API Layer Migration

For each Python route/endpoint in scope:

---
**[HTTP Method] [Python Route]** → `[Spring Controller Method]`

Python (source):
```python
@app.route('/orders', methods=['POST'])
@login_required
def create_order():
    data = request.get_json()
    # ...
```

Java (target stub):
```java
@RestController
@RequestMapping("/api/v1/orders")
@RequiredArgsConstructor
public class OrderController {

    @PostMapping
    @PreAuthorize("isAuthenticated()")
    public ResponseEntity<OrderDto> createOrder(
            @Valid @RequestBody CreateOrderRequest request) {
        // ...
    }
}
```

Request DTO:
```java
public record CreateOrderRequest(
    @NotNull Long customerId,
    @NotEmpty List<OrderItemRequest> items
) {}
```

---

### 6. Business Rules Implementation Guide

For each business rule in scope:

| BR-ID | Rule | Python Location | Java Implementation Pattern | Spring Feature |
|---|---|---|---|---|

### 7. Cross-Cutting Concerns Migration

| Concern | Python Implementation | Java/Spring Implementation |
|---|---|---|
| Authentication | | |
| Authorization | | |
| Validation | | |
| Error handling | | |
| Logging | | |
| Transactions | | |
| Caching | | |

### 8. Data Migration Script Guidance

For each model being migrated:
- Is schema migration needed (data type changes, constraint changes)?
- Is data transformation required?
- What is the cutover strategy?

| Entity | Schema Changes | Data Transformation | Cutover Strategy | Risk |
|---|---|---|---|---|

### 9. Testing Strategy

How to validate the migrated components:

| Test Type | Coverage Target | Framework | Key Scenarios |
|---|---|---|---|
| Unit tests | | JUnit 5 + Mockito | |
| Integration tests | | Spring Boot Test | |
| Contract tests | | Spring Cloud Contract | |
| Data migration validation | | | |

### 10. Migration Pitfall Register

Specific Python→Java gotchas for this scope:

| Pitfall | Python Behavior | Java Behavior | How to Handle |
|---|---|---|---|

Always include:
- None vs. null handling differences
- List mutability differences
- Exception hierarchy differences
- Timezone handling (Python datetime vs. Java ZonedDateTime)
- Decimal precision (Python Decimal vs. Java BigDecimal)
- ORM lazy loading differences

---
