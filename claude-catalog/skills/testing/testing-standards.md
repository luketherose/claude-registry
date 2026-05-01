---
name: testing-standards
description: "This skill should be used when an agent (test-writer, developer, code-reviewer) needs the canonical testing standards: principles, scenario taxonomy, naming conventions, Arrange-Act-Assert structure, framework templates for JUnit 5 + Mockito (Java), pytest (Python), Jest (TypeScript). Trigger phrases: \"testing standards\", \"how should I structure these tests\", \"AAA pattern\", \"JUnit template\", \"pytest fixture conventions\". Returns reference material and complete test templates, not generated test code. Do not trigger directly from a coding prompt — invoked by the agents above."
tools: Read
model: haiku
color: cyan
---

## Role

You are the authoritative knowledge source for testing standards and patterns
used by this team. When invoked, you return the relevant testing doctrine,
conventions, and framework templates with enough precision that the calling
agent can produce consistent, high-quality tests.

You do not write tests for a specific class — you provide the standards and
templates that the calling agent uses to write them.

---

## Core Principles

- **Test behavior, not implementation.** A test that breaks when you rename a
  private method is testing the wrong thing.
- **Arrange-Act-Assert.** Every test has: setup, a single action, explicit assertions.
  Separate each section with a blank line. No multi-action tests.
- **One concept per test.** Multiple `assert` calls are fine if they verify the same
  concept. Multiple unrelated assertions in one test are not.
- **Names describe scenarios.** `createOrder_whenProductUnavailable_shouldThrowException`
  is good. `testCreateOrder2` is useless.
- **No test logic in production code.** No `if (isTestEnvironment())`.
- **No flaky tests.** Tests that depend on external services, system time, or random
  values must use mocks, fixed clocks, or seeded randomness.
- **Tests are documentation.** A reader should understand what the production code does
  by reading the test names alone.

---

## Test Scenario Taxonomy

For any unit under test, always identify scenarios in this order:

1. **Happy path** — expected successful execution with valid, representative input
2. **Boundary conditions** — min/max values, empty collections, zero, single-element
3. **Invalid input** — null, empty string, negative numbers, wrong types
4. **Business rule violations** — combinations of valid inputs that violate a rule
5. **Error propagation** — what happens when a dependency throws or returns empty/null

Do not ship tests that only cover the happy path.

---

## Method Naming Convention

Format: `{methodUnderTest}_{condition}_{expectedOutcome}`

```
createOrder_whenProductAvailable_shouldSaveAndReturnOrder
createOrder_whenProductUnavailable_shouldThrowBusinessException
createOrder_withNullProductId_shouldThrowValidationException
findById_whenIdDoesNotExist_shouldReturnEmpty
processPayment_whenGatewayTimesOut_shouldRetryAndFail
```

Rules:
- No `test` prefix
- Use `should` in the outcome — describes expected behavior
- Use `when` or `with` in the condition — describes the scenario
- Test class name: `{ClassName}Test` (Java) or `test_{module}.py` (Python)

---

## JUnit 5 + Mockito Templates

### Unit test template
```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @Mock
    private OrderRepository orderRepository;

    @Mock
    private PaymentService paymentService;

    @InjectMocks
    private OrderService orderService;

    @Test
    void createOrder_whenProductAvailable_shouldSaveAndReturnOrder() {
        // Arrange
        var request = new CreateOrderRequest(1L, 2);
        var savedOrder = new Order(UUID.randomUUID(), 1L, 2, OrderStatus.PENDING);
        when(orderRepository.findProductById(1L)).thenReturn(Optional.of(new Product(1L, 10)));
        when(orderRepository.save(any())).thenReturn(savedOrder);

        // Act
        var result = orderService.createOrder(42L, request);

        // Assert
        assertThat(result.orderId()).isNotNull();
        assertThat(result.status()).isEqualTo(OrderStatus.PENDING);
        verify(orderRepository).save(any(Order.class));
    }

    @Test
    void createOrder_whenProductUnavailable_shouldThrowBusinessException() {
        // Arrange
        when(orderRepository.findProductById(any())).thenReturn(Optional.empty());

        // Act & Assert
        assertThatThrownBy(() -> orderService.createOrder(42L, new CreateOrderRequest(999L, 1)))
            .isInstanceOf(ResourceNotFoundException.class)
            .hasMessageContaining("Product not found");
    }
}
```

### Integration test template (Testcontainers)
```java
@SpringBootTest
@ActiveProfiles("test")
@Transactional
class OrderRepositoryIntegrationTest {

    @Autowired
    private OrderRepository orderRepository;

    @Test
    void findByCustomerIdAndStatus_shouldReturnMatchingOrders() {
        // Arrange — DB is pre-populated by test profile or @Sql annotation
        // Act
        var orders = orderRepository.findByCustomerIdAndStatus(42L, OrderStatus.PENDING);

        // Assert
        assertThat(orders).hasSize(1);
        assertThat(orders.get(0).getCustomerId()).isEqualTo(42L);
    }
}
```

### Controller test template (@WebMvcTest)
```java
@WebMvcTest(OrderController.class)
class OrderControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private OrderService orderService;

    @Test
    void createOrder_withValidRequest_shouldReturn201WithLocation() throws Exception {
        // Arrange
        var response = new OrderResponse(UUID.randomUUID(), OrderStatus.PENDING);
        when(orderService.createOrder(any(), any())).thenReturn(response);

        // Act & Assert
        mockMvc.perform(post("/api/v1/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""{"productId": 1, "quantity": 2}"""))
            .andExpect(status().isCreated())
            .andExpect(header().exists("Location"))
            .andExpect(jsonPath("$.orderId").exists())
            .andExpect(jsonPath("$.status").value("PENDING"));
    }

    @Test
    void createOrder_withMissingProductId_shouldReturn400WithViolations() throws Exception {
        mockMvc.perform(post("/api/v1/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""{"quantity": 2}"""))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.violations[0].field").value("productId"));
    }
}
```

---

## pytest Templates

### Unit test template
```python
import pytest
from unittest.mock import MagicMock, patch
from app.services.order_service import OrderService
from app.exceptions import ResourceNotFoundError

class TestOrderService:

    def setup_method(self):
        self.order_repo = MagicMock()
        self.payment_service = MagicMock()
        self.service = OrderService(self.order_repo, self.payment_service)

    def test_create_order_when_product_available_should_return_order(self):
        # Arrange
        self.order_repo.find_product.return_value = {"id": 1, "stock": 10}
        self.order_repo.save.return_value = {"id": "abc", "status": "pending"}

        # Act
        result = self.service.create_order(customer_id=42, product_id=1, quantity=2)

        # Assert
        assert result["status"] == "pending"
        self.order_repo.save.assert_called_once()

    def test_create_order_when_product_missing_should_raise_not_found(self):
        # Arrange
        self.order_repo.find_product.return_value = None

        # Act & Assert
        with pytest.raises(ResourceNotFoundError, match="Product not found"):
            self.service.create_order(customer_id=42, product_id=999, quantity=1)
```

### Fixture pattern
```python
@pytest.fixture
def mock_order_repo():
    repo = MagicMock()
    repo.find_product.return_value = {"id": 1, "stock": 10}
    return repo

@pytest.fixture
def order_service(mock_order_repo):
    return OrderService(mock_order_repo)

def test_create_order_happy_path(order_service, mock_order_repo):
    result = order_service.create_order(customer_id=1, product_id=1, quantity=1)
    assert result is not None
```

### FastAPI integration test template
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_order_returns_201():
    response = client.post("/api/v1/orders", json={"product_id": 1, "quantity": 2})
    assert response.status_code == 201
    assert "order_id" in response.json()

def test_create_order_missing_field_returns_422():
    response = client.post("/api/v1/orders", json={"quantity": 2})
    assert response.status_code == 422
```

---

## Jest Templates (TypeScript)

### Unit test template
```typescript
import { OrderService } from './order.service';
import { OrderRepository } from './order.repository';

jest.mock('./order.repository');

describe('OrderService', () => {
    let service: OrderService;
    let mockRepo: jest.Mocked<OrderRepository>;

    beforeEach(() => {
        mockRepo = new OrderRepository() as jest.Mocked<OrderRepository>;
        service = new OrderService(mockRepo);
    });

    describe('createOrder', () => {
        it('should return order when product is available', async () => {
            // Arrange
            mockRepo.findProduct.mockResolvedValue({ id: 1, stock: 10 });
            mockRepo.save.mockResolvedValue({ id: 'abc', status: 'pending' });

            // Act
            const result = await service.createOrder({ productId: 1, quantity: 2 });

            // Assert
            expect(result.status).toBe('pending');
            expect(mockRepo.save).toHaveBeenCalledTimes(1);
        });

        it('should throw NotFoundException when product does not exist', async () => {
            mockRepo.findProduct.mockResolvedValue(null);
            await expect(service.createOrder({ productId: 999, quantity: 1 }))
                .rejects.toThrow('Product not found');
        });
    });
});
```

---

## Coverage Expectations

| Layer | Expected coverage | Method |
|---|---|---|
| Service business logic | Full branch coverage | Unit tests |
| Controllers | All HTTP status codes | @WebMvcTest / TestClient |
| Repositories with custom queries | Each query exercised | Integration test |
| Exception handlers | Each handler method | Unit or WebMvcTest |
| Utility / pure functions | Full branch coverage | Unit tests |

Minimum enforced in CI: **70% line coverage** (Java: JaCoCo; Python: pytest-cov).

---

## What good tests do NOT do

- Test implementation details (private method names, internal state)
- Depend on execution order
- Share mutable state between test methods
- Hit real external services (databases, APIs, message queues) in unit tests
- Use `Thread.sleep()` to wait for async operations — use `CompletableFuture`, `awaitility`, or test doubles
- Assert on log output (fragile) — assert on observable side effects instead
