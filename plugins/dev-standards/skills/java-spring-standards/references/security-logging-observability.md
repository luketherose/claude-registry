# Security, logging, observability and OpenAPI

The Spring Security 6 baseline and input validation rules, the SLF4J plus MDC
logging contract, the Micrometer and OpenTelemetry setup, and SpringDoc
annotation requirements.

## Contents

- [Spring Security 6 baseline](#spring-security-6-baseline)
- [Input validation (JSR-380)](#input-validation-jsr-380)
- [Logging (SLF4J + MDC)](#logging-slf4j--mdc)
  - [Log level rules](#log-level-rules)
  - [Rules](#rules)
- [Observability (Micrometer + OpenTelemetry)](#observability-micrometer--opentelemetry)
- [OpenAPI documentation (SpringDoc)](#openapi-documentation-springdoc)

## Spring Security 6 baseline

- Stateless sessions for REST APIs (`SessionCreationPolicy.STATELESS`)
- CORS configured explicitly, never `allowedOrigins("*")` in production
- CSRF disabled for stateless REST
- Method-level security with `@PreAuthorize`
- Passwords: `BCryptPasswordEncoder` strength ≥ 12
- Never store secrets in `application.properties`: use env vars or secrets manager

```java
@Configuration @EnableWebSecurity @EnableMethodSecurity
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            .csrf(AbstractHttpConfigurer::disable)
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/actuator/health", "/actuator/info").permitAll()
                .requestMatchers("/api/v1/auth/**").permitAll()
                .anyRequest().authenticated())
            .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()))
            .build();
    }
}
```

### Input validation (JSR-380)
Validation annotations on DTO fields, `@Valid` on controller params.

```java
public record CreateOrderRequest(
    @NotNull @Positive Long productId,
    @NotNull @Min(1) @Max(100) Integer quantity
) {}
```

---

## Logging (SLF4J + MDC)

```java
private static final Logger log = LoggerFactory.getLogger(OrderService.class);
// Or @Slf4j (Lombok) only if already in project
```

### Log level rules
- `INFO`: business-significant events (order created, payment processed)
- `DEBUG`: diagnostic info (intermediate state in multi-step processes)
- `WARN`: recoverable issues (retry, fallback, degraded mode)
- `ERROR`: unrecoverable issues, always with exception attached

### Rules
- Never log sensitive data: passwords, tokens, PII, credit cards, secrets.
- Always include correlation context via MDC: `traceId`, `userId`, `requestId`.
- Log messages must be useful to an on-call engineer with no prior code knowledge.
- Use structured JSON in production: `logstash-logback-encoder`.

```java
// Good
log.info("Order created. orderId={}, customerId={}, totalAmount={}",
    order.getId(), order.getCustomerId(), order.getTotalAmount());

// Wrong — useless
log.info("Done");

// Wrong — leaks PII
log.info("User {} logged in with password {}", username, password);
```

---

## Observability (Micrometer + OpenTelemetry)

- Include `spring-boot-starter-actuator`; expose health, info, metrics
- Protect actuator endpoints except `/health` and `/info`

```java
// Custom metrics
Counter ordersCreated = Counter.builder("orders.created")
    .description("Total orders created")
    .register(meterRegistry);

Timer orderProcessingTime = Timer.builder("orders.processing.time")
    .register(meterRegistry);
```

- Micrometer Tracing (OTel bridge) for distributed tracing
- Include `traceId` and `spanId` in log output via MDC
- Propagate `X-B3-TraceId` in RestTemplate/WebClient/Feign calls

---

## OpenAPI documentation (SpringDoc)

```java
@Operation(summary = "Create a new order")
@ApiResponses({
    @ApiResponse(responseCode = "201", description = "Order created"),
    @ApiResponse(responseCode = "400", description = "Invalid request"),
    @ApiResponse(responseCode = "409", description = "Product unavailable")
})
@PostMapping("/orders")
public ResponseEntity<OrderResponse> createOrder(@Valid @RequestBody CreateOrderRequest req) {}
```

Public service interface methods require Javadoc describing the contract (not the implementation).

---
