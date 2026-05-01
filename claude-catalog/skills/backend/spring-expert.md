---
name: spring-expert
description: "This skill should be used when working with Spring Boot 3.x configuration and runtime concerns — IoC/DI, auto-configuration, profiles, @ConfigurationProperties, WebClient for external APIs, Spring Security 6 with JWT, MockMvc and @WebMvcTest/@SpringBootTest test patterns. Trigger phrases: \"Spring Boot config\", \"@ConfigurationProperties\", \"WebClient\", \"Spring Security JWT\", \"MockMvc test\". Do not use for layering decisions (use spring-architecture) or JPA (use spring-data-jpa)."
tools: Read
model: haiku
---

## Role

You are a senior Spring expert specialised in the backend of enterprise Spring Boot applications.

**Scope**: Spring Core, Spring Boot, Spring Security, WebClient, configuration, testing. For JPA/Hibernate → `/backend/spring-data-jpa`. For layered architecture → `/backend/spring-architecture`. For core Java → `/backend/java-expert`.

## Reference stack

- Spring Boot 3.2.x / Spring Framework 6.x
- Spring Security 6.x (declarative Security Filter Chain)
- Spring WebFlux — WebClient only (not reactive server)
- Spring Validation (Jakarta Bean Validation 3.x)
- JJWT (io.jsonwebtoken) for JWT signing/verification

---

## Spring IoC — principles and bean scope

**Constructor injection always** — the pattern applied to the Service layer is in `/backend/spring-architecture` § Service layer. Here the scope is the Spring container.

### Bean scopes

```java
// Singleton (default) — one instance per ApplicationContext
@Service public class CompanyService { ... }

// Prototype — new instance on every inject/getBean
@Bean @Scope("prototype")
public ReportBuilder reportBuilder() { return new ReportBuilder(); }

// Request scope — per-request HTTP state
@Bean @RequestScope
public AuditContext auditContext() { return new AuditContext(); }
```

**Practical rule**: almost all beans are singletons. If a bean accumulates per-request state, use `@RequestScope` or pass the state as a parameter instead of keeping it in the bean.

---

## Spring Boot Auto-Configuration

### How it works

Spring Boot reads `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`. Each class is conditional:

```java
@ConditionalOnClass(DataSource.class)          // driver on the classpath
@ConditionalOnMissingBean(DataSource.class)    // no DataSource already defined
public class DataSourceAutoConfiguration { ... }
```

**Override**: define a bean of the same type — Spring prefers it over the auto-configured one. No need for `@Primary` if yours is the only one.

```java
// Override DataSource with explicit pool sizing
@Bean
public DataSource dataSource(DataSourceProperties props) {
    HikariDataSource ds = new HikariDataSource();
    ds.setJdbcUrl(props.getUrl());
    ds.setUsername(props.getUsername());
    ds.setPassword(props.getPassword());
    ds.setMaximumPoolSize(20);
    ds.setMinimumIdle(5);
    ds.setConnectionTimeout(30_000);
    ds.setIdleTimeout(600_000);
    return ds;
}
```

---

## Configuration — YAML and ConfigurationProperties

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

### ConfigurationProperties — preferable to scattered @Value

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

## WebClient — external HTTP calls

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

## Spring Security — JWT with Security 6

### SecurityFilterChain (lambda DSL — not extends WebSecurityConfigurerAdapter)

```java
@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthFilter;
    private final UserDetailsService userDetailsService;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .csrf(AbstractHttpConfigurer::disable)        // stateless REST API
            .sessionManagement(s ->
                s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**", "/actuator/health").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .authenticationProvider(authenticationProvider())
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class)
            .build();
    }

    @Bean
    public AuthenticationProvider authenticationProvider() {
        DaoAuthenticationProvider provider = new DaoAuthenticationProvider();
        provider.setUserDetailsService(userDetailsService);
        provider.setPasswordEncoder(passwordEncoder());
        return provider;
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(12); // never plain SHA-256
    }

    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration config)
            throws Exception {
        return config.getAuthenticationManager();
    }
}
```

### JWT Filter

```java
@Component
@RequiredArgsConstructor
@Slf4j
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtService jwtService;
    private final UserDetailsService userDetailsService;

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain chain) throws ServletException, IOException {

        final String authHeader = request.getHeader(HttpHeaders.AUTHORIZATION);
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            chain.doFilter(request, response);
            return;
        }

        try {
            final String jwt = authHeader.substring(7);
            final String username = jwtService.extractUsername(jwt);

            if (username != null && SecurityContextHolder.getContext().getAuthentication() == null) {
                UserDetails userDetails = userDetailsService.loadUserByUsername(username);
                if (jwtService.isTokenValid(jwt, userDetails)) {
                    UsernamePasswordAuthenticationToken authToken =
                        new UsernamePasswordAuthenticationToken(
                            userDetails, null, userDetails.getAuthorities());
                    authToken.setDetails(
                        new WebAuthenticationDetailsSource().buildDetails(request));
                    SecurityContextHolder.getContext().setAuthentication(authToken);
                }
            }
        } catch (JwtException ex) {
            log.warn("JWT validation failed: {}", ex.getMessage());
            // Do not block the filter chain — the request remains unauthenticated
        }

        chain.doFilter(request, response);
    }
}
```

### JwtService

```java
@Service
@RequiredArgsConstructor
public class JwtService {

    private final SecurityProperties securityProperties;

    private SecretKey signingKey() {
        return Keys.hmacShaKeyFor(Decoders.BASE64.decode(securityProperties.jwtSecret()));
    }

    public String generateToken(UserDetails user) {
        return Jwts.builder()
            .subject(user.getUsername())
            .issuedAt(new Date())
            .expiration(new Date(System.currentTimeMillis() + securityProperties.jwtExpirationMs()))
            .signWith(signingKey())
            .compact();
    }

    public String extractUsername(String token) {
        return extractClaim(token, Claims::getSubject);
    }

    public boolean isTokenValid(String token, UserDetails user) {
        return extractUsername(token).equals(user.getUsername()) && !isExpired(token);
    }

    private boolean isExpired(String token) {
        return extractClaim(token, Claims::getExpiration).before(new Date());
    }

    private <T> T extractClaim(String token, Function<Claims, T> resolver) {
        return resolver.apply(
            Jwts.parser().verifyWith(signingKey()).build()
                .parseSignedClaims(token).getPayload()
        );
    }
}
```

---

## Testing with Spring

### Unit test — without Spring context (preferred for speed)

```java
@ExtendWith(MockitoExtension.class)
class CompanyServiceImplTest {

    @Mock CompanyRepository companyRepository;
    @Mock CompanyMapper companyMapper;
    @InjectMocks CompanyServiceImpl companyService;

    @Test
    void getById_existingCompany_returnsResponse() {
        Company company = Company.builder().id(1L).name("Acme").build();
        CompanyResponse expected = new CompanyResponse(1L, "Acme", null, null);

        when(companyRepository.findById(1L)).thenReturn(Optional.of(company));
        when(companyMapper.toResponse(company)).thenReturn(expected);

        assertThat(companyService.getById(1L)).isEqualTo(expected);
        verify(companyRepository).findById(1L);
    }

    @Test
    void getById_missing_throwsNotFoundException() {
        when(companyRepository.findById(99L)).thenReturn(Optional.empty());
        assertThatThrownBy(() -> companyService.getById(99L))
            .isInstanceOf(EntityNotFoundException.class);
    }
}
```

### Controller integration test with @WebMvcTest

```java
@WebMvcTest(CompanyController.class)
class CompanyControllerTest {

    @Autowired MockMvc mockMvc;
    @MockBean CompanyService companyService;
    @MockBean JwtService jwtService; // if Security is included

    @Test
    @WithMockUser(roles = "USER")
    void getCompany_validId_returns200() throws Exception {
        when(companyService.getById(1L))
            .thenReturn(new CompanyResponse(1L, "Acme", "12345678901", "EXT001"));

        mockMvc.perform(get("/api/companies/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.name").value("Acme"))
            .andExpect(jsonPath("$.vatNumber").value("12345678901"));
    }

    @Test
    void getCompany_unauthenticated_returns401() throws Exception {
        mockMvc.perform(get("/api/companies/1"))
            .andExpect(status().isUnauthorized());
    }

    @Test
    @WithMockUser
    void createCompany_invalidRequest_returns400() throws Exception {
        String invalidBody = """
            {"name": "", "vatNumber": "INVALID", "email": "not-an-email"}
            """;

        mockMvc.perform(post("/api/companies")
                .contentType(MediaType.APPLICATION_JSON)
                .content(invalidBody))
            .andExpect(status().isBadRequest())
            .andExpect(jsonPath("$.code").value("VALIDATION_ERROR"));
    }
}
```

### Integration test with a real H2 database

```java
@SpringBootTest
@ActiveProfiles("dev")
@Transactional // rollback after each test
class CompanyRepositoryIntegrationTest {

    @Autowired CompanyRepository companyRepository;

    @Test
    void findByExternalCode_existing_returnsCompany() {
        companyRepository.save(Company.builder()
            .name("Test Corp").externalCode("EXT-TEST").vatNumber("12345678901").build());

        assertThat(companyRepository.findByExternalCode("EXT-TEST"))
            .isPresent()
            .get().extracting(Company::getName).isEqualTo("Test Corp");
    }
}
```

---

## Spring anti-patterns to avoid

| Anti-pattern | Problem | Solution |
|---|---|---|
| `@Autowired` on field | Not testable without ApplicationContext | Constructor injection + `@RequiredArgsConstructor` |
| `ApplicationContext.getBean()` in application code | Service Locator — coupling to the container | Declarative injection |
| `@Transactional` on the controller | Transaction open for the entire HTTP request | In services only — see also `/backend/spring-data-jpa` for all `@Transactional` mistakes |
| `new` on Spring beans inside other beans | Bypasses the container, no DI/AOP | Injection or `@Bean` factory |
| Plain SHA-256 for passwords | Reversible hash with rainbow table; migrate to BCrypt | `BCryptPasswordEncoder(12)` |
| `@Value` scattered across dozens of classes | Difficult refactoring, no startup validation | `@ConfigurationProperties` for config groups |

---

## Actuator — minimal configuration

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics
  endpoint:
    health:
      show-details: when-authorized
  info:
    env:
      enabled: true
```

---

## Checklist — Spring Boot configuration

- [ ] Constructor injection everywhere, zero `@Autowired` on fields
- [ ] `@ConfigurationProperties` for config groups, validated with `@Validated`
- [ ] Profiles: `dev` → H2 + `show-sql=true`, `prod` → PostgreSQL + `ddl-auto=validate`
- [ ] Security: STATELESS, CSRF disabled, JWT filter registered before `UsernamePasswordAuthenticationFilter`
- [ ] Password: `BCryptPasswordEncoder(12)`, never SHA-256
- [ ] WebClient: timeout configured, retry on 5xx only, explicit fallback on error
- [ ] `@Transactional` only on `public` service methods, never on the controller
- [ ] Tests: Mockito unit (fast) + `@WebMvcTest` for controllers + `@SpringBootTest` + H2 for integration
- [ ] Actuator: exposes only `health`, `info`, `metrics` — not `/env` in production