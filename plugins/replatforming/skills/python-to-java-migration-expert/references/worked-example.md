# Worked example

## Example

### Input (abbreviated)

```
MIGRATION_SCOPE: Order management service — model layer and service layer
PYTHON_FRAMEWORK: Django 3.2, Django REST Framework
TARGET_SPRING_STACK: Java 21, Spring Boot 3.2, Spring Data JPA, Lombok, MapStruct

Source Code:
class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'), ('CONFIRMED', 'Confirmed'),
        ('SHIPPED', 'Shipped'), ('CANCELLED', 'Cancelled'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def cancel(self, reason):
        if self.status in ['SHIPPED', 'DELIVERED']:
            raise ValidationError("Cannot cancel shipped order")
        self.status = 'CANCELLED'
        self.cancellation_reason = reason
        self.save()
```

### Expected Output Excerpt

```java
// Order.java — Entity stub
@Entity
@Table(name = "orders")
@Getter @Setter
public class Order {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "customer_id")
    private Customer customer;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private OrderStatus status = OrderStatus.PENDING;

    @Column(name = "created_at", nullable = false, updatable = false)
    @CreationTimestamp
    private Instant createdAt;

    // BR-CANCEL-001: Status guard for cancellation — implemented in service layer
    // Do NOT put business logic in entity — delegate to OrderService.cancel()
}

// OrderStatus.java — Enum
public enum OrderStatus { PENDING, CONFIRMED, SHIPPED, CANCELLED }
```

```
Migration Pitfall:
| Django choices tuples | Python: `STATUS_CHOICES = [('PENDING', 'Pending')]`, string+label | Java: `@Enumerated(EnumType.STRING)` enum, no label in DB | Use enum for DB, separate display logic in DTO/frontend |
| `auto_now_add=True` | Set at Python ORM level | Java: `@CreationTimestamp` Hibernate annotation | Equivalent, verify timezone handling (use Instant, not LocalDateTime) |
```

---
