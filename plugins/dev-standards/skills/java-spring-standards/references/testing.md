# Testing standards

Complete templates for the three test tiers, plus the coverage expectations
enforced in CI.

## Contents

- [Unit tests (no Spring context)](#unit-tests-no-spring-context)
- [Integration tests (Spring context + real DB)](#integration-tests-spring-context--real-db)
- [Controller tests (slice)](#controller-tests-slice)
- [Coverage expectations](#coverage-expectations)

## Unit tests (no Spring context)
Framework: JUnit 5 + Mockito. Must not start a Spring context.

```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {
    @Mock private OrderRepository orderRepository;
    @Mock private PaymentService paymentService;
    @InjectMocks private OrderService orderService;

    @Test
    void createOrder_whenProductAvailable_shouldSaveAndReturnOrder() {
        // Arrange
        // Act
        // Assert
    }
}
```

Test method naming: `{method}_{condition}_{expectedOutcome}`. No `test` prefix.

## Integration tests (Spring context + real DB)
Framework: `@SpringBootTest` + Testcontainers + `@Transactional` (rollback after each).

```java
@SpringBootTest
@ActiveProfiles("test")
@Transactional
class OrderRepositoryIntegrationTest {
    @Autowired private OrderRepository orderRepository;
    // Testcontainers PostgreSQL configured via application-test.yml
}
```

## Controller tests (slice)
`@WebMvcTest` + `@MockBean` for service layer.

```java
@WebMvcTest(OrderController.class)
class OrderControllerTest {
    @Autowired private MockMvc mockMvc;
    @MockBean private OrderService orderService;

    @Test
    void createOrder_withValidRequest_shouldReturn201() throws Exception {
        mockMvc.perform(post("/api/v1/orders")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""{"productId": 1, "quantity": 2}"""))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.orderId").exists());
    }
}
```

## Coverage expectations
- Service business logic: full branch coverage
- Controllers: test all HTTP status codes (200, 201, 400, 404, 409, 500)
- Custom `@Query` methods: integration test for each
- Exception handlers: test each handler method
- JaCoCo minimum: 70% line coverage enforced in CI

---
