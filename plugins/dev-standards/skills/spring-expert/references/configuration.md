# Configuration

## Contents

- Configuration: YAML and ConfigurationProperties
- Recommended profile structure
- ConfigurationProperties: preferable to scattered @Value
- WebClient: external HTTP calls
- Bean configuration
- Call pattern with full error handling

## Configuration: YAML and ConfigurationProperties

### Recommended profile structure

```yaml
# application.yml — base values and structure

spring:
  application:
    name: my-app-backend

app:
  service-a:
    base-url: ${SERVICE_A_BASE_URL}
    api-key: ${SERVICE_A_API_KEY}
    timeout-seconds: 10
  service-b:
    base-url: ${SERVICE_B_BASE_URL}
    api-key: ${SERVICE_B_API_KEY}
  security:
    jwt-secret: ${JWT_SECRET}
    jwt-expiration-ms: 86400000

---
spring:
  config:
    activate:
      on-profile: dev
  datasource:
    url: jdbc:h2:mem:myapp-dev;DB_CLOSE_DELAY=-1
    driver-class-name: org.h2.Driver
  jpa:
    show-sql: true
    hibernate:
      ddl-auto: create-drop
  h2.console.enabled: true

---
spring:
  config:
    activate:
      on-profile: prod
  datasource:
    url: jdbc:postgresql://${DB_HOST:localhost}:5432/myapp
    username: ${DB_USER}
    password: ${DB_PASS}
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
  jpa:
    show-sql: false
    hibernate:
      ddl-auto: validate
```

### ConfigurationProperties: preferable to scattered @Value

```java
@ConfigurationProperties(prefix = "app.service-a")
@Validated
public record ServiceAProperties(
    @NotBlank String baseUrl,
    @NotBlank String apiKey,
    @Positive int timeoutSeconds
) {}

@ConfigurationProperties(prefix = "app.security")
@Validated
public record SecurityProperties(
    @NotBlank String jwtSecret,
    @Positive long jwtExpirationMs
) {}

// Enable in main class
@SpringBootApplication
@ConfigurationPropertiesScan
public class MyApplication { ... }
```

**Advantages vs `@Value`**: validation on startup (fail-fast), type-safe, testable in isolation, IDE autocomplete, auto-generatable documentation with `spring-boot-configuration-processor`.

---

## WebClient: external HTTP calls

### Bean configuration

```java
@Configuration
@RequiredArgsConstructor
public class WebClientConfig {

    private final ServiceAProperties serviceA;
    private final ServiceBProperties serviceB;

    @Bean("serviceAWebClient")
    public WebClient serviceAWebClient(WebClient.Builder builder) {
        return builder
            .baseUrl(serviceA.baseUrl())
            .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
            .defaultHeader("X-API-Key", serviceA.apiKey())
            .clientConnector(new ReactorClientHttpConnector(
                HttpClient.create().responseTimeout(Duration.ofSeconds(serviceA.timeoutSeconds()))
            ))
            .build();
    }

    @Bean("serviceBWebClient")
    public WebClient serviceBWebClient(WebClient.Builder builder) {
        return builder
            .baseUrl(serviceB.baseUrl())
            .defaultHeader(HttpHeaders.AUTHORIZATION, "Bearer " + serviceB.apiKey())
            .build();
    }
}
```

### Call pattern with full error handling

```java
@Service
@Slf4j
@RequiredArgsConstructor
public class ExternalSearchService {

    @Qualifier("serviceAWebClient")
    private final WebClient serviceAWebClient;

    public List<SearchMatch> search(String query) {
        return serviceAWebClient.post()
            .uri("/search")
            .bodyValue(new SearchRequest(query))
            .retrieve()
            .onStatus(HttpStatusCode::is4xxClientError, response ->
                response.bodyToMono(String.class)
                    .flatMap(body -> Mono.error(
                        new ExternalApiException("Service A 4xx: " + body, "SERVICE_A_CLIENT_ERROR")))
            )
            .onStatus(HttpStatusCode::is5xxServerError, response ->
                Mono.error(new ExternalApiException("Service A 5xx", "SERVICE_A_SERVER_ERROR")))
            .bodyToMono(new ParameterizedTypeReference<List<SearchMatch>>() {})
            .retryWhen(Retry.backoff(3, Duration.ofSeconds(1))
                .filter(ex -> ex instanceof ExternalApiException e
                    && e.getErrorCode().endsWith("SERVER_ERROR"))) // retry on 5xx only, not 4xx
            .onErrorResume(ex -> {
                log.error("Service A search failed query='{}': {}", query, ex.getMessage());
                return Mono.just(List.of()); // fallback: empty list instead of propagating
            })
            .block(); // acceptable in Spring MVC (servlet-based) — avoid in WebFlux server
    }
}
```

**`.block()` in Spring MVC**: servlet-stack applications correctly use `.block()` to consume Mono/Flux from WebClient in the request thread. If migrating to Spring WebFlux server, go reactive end-to-end.

---
