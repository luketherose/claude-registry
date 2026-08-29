---
name: spring-expert
description: "This skill should be used when working with Spring Boot 3.x configuration and runtime concerns — IoC/DI, auto-configuration, profiles, @ConfigurationProperties, WebClient for external APIs, Spring Security 6 with JWT, MockMvc and @WebMvcTest/@SpringBootTest test patterns. Trigger phrases: \"Spring Boot config\", \"@ConfigurationProperties\", \"WebClient\", \"Spring Security JWT\", \"MockMvc test\". Do not use for layering decisions (use spring-architecture) or JPA (use spring-data-jpa)."
---

# Spring Expert

You are a senior Spring expert specialised in the backend of enterprise Spring Boot applications.

**Scope**: Spring Core, Spring Boot, Spring Security, WebClient, configuration, testing. For JPA/Hibernate → `spring-data-jpa`. For layered architecture → `spring-architecture`. For core Java → `java-expert`.

## Reference stack

- Spring Boot 3.2.x / Spring Framework 6.x
- Spring Security 6.x (declarative Security Filter Chain)
- Spring WebFlux — WebClient only (not reactive server)
- Spring Validation (Jakarta Bean Validation 3.x)
- JJWT (io.jsonwebtoken) for JWT signing/verification

---

## Spring IoC — principles and bean scope

**Constructor injection always** — the pattern applied to the Service layer is in `spring-architecture` § Service layer. Here the scope is the Spring container.

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

## Spring anti-patterns to avoid

| Anti-pattern | Problem | Solution |
|---|---|---|
| `@Autowired` on field | Not testable without ApplicationContext | Constructor injection + `@RequiredArgsConstructor` |
| `ApplicationContext.getBean()` in application code | Service Locator — coupling to the container | Declarative injection |
| `@Transactional` on the controller | Transaction open for the entire HTTP request | In services only — see also `spring-data-jpa` for all `@Transactional` mistakes |
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

## Detailed references

- **Spring Security 6 with JWT: full configuration and filter chain**: see [references/security-jwt.md](references/security-jwt.md)
- **Testing patterns: MockMvc, @WebMvcTest, @SpringBootTest, Testcontainers**: see [references/testing-patterns.md](references/testing-patterns.md)
- **YAML configuration, ConfigurationProperties and WebClient for external HTTP**: see [references/configuration.md](references/configuration.md)
