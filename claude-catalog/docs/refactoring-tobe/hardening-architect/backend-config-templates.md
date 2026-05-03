# Backend hardening — config templates

> Reference doc for `hardening-architect`. Read at runtime when applying
> Method steps 1–5 (backend logging, metrics, tracing, security, secrets).

## Goal

Verbatim configuration blocks the agent emits when hardening the backend
scaffold. The agent's Method describes the decisions; this doc holds the
output templates.

---

## 1. Logging — structured JSON with correlation-id

Update `<backend-dir>/src/main/resources/application.yml`:

```yaml
spring:
  # ... existing config ...

logging:
  level:
    root: INFO
    com.<org>.<app>: INFO
    org.springframework.security: INFO
    org.hibernate.SQL: WARN
  config: classpath:logback-spring.xml
```

Add `<backend-dir>/src/main/resources/logback-spring.xml`:

```xml
<configuration>
  <springProperty name="appName" source="spring.application.name"/>
  <appender name="JSON" class="ch.qos.logback.core.ConsoleAppender">
    <encoder class="net.logstash.logback.encoder.LogstashEncoder">
      <includeMdc>true</includeMdc>
      <customFields>{"app":"${appName}"}</customFields>
    </encoder>
  </appender>
  <root level="INFO">
    <appender-ref ref="JSON"/>
  </root>
</configuration>
```

Add `net.logstash.logback:logstash-logback-encoder` to pom.xml.

Verify the existing `CorrelationIdFilter` (from `backend-scaffolder`) sets
MDC `correlationId` from `X-Request-Id` header (or generates UUID). Update
if needed.

Result: every log line is JSON with `correlationId`, `app`, level,
timestamp, message, MDC fields. Aggregators (ELK, Loki, Datadog) parse
trivially.

---

## 2. Metrics — Micrometer + Prometheus

`backend-scaffolder` already added Spring Boot Actuator + Prometheus
registry. Verify and extend:

`<backend-dir>/src/main/resources/application.yml`:

```yaml
management:
  endpoints:
    web:
      exposure:
        include: [health, info, prometheus, metrics, loggers]
      base-path: /actuator
  endpoint:
    health:
      show-details: when-authorized
      probes:
        enabled: true                  # liveness + readiness
  metrics:
    tags:
      application: ${spring.application.name}
      env: ${ENV:local}
    distribution:
      percentiles-histogram:
        http.server.requests: true
      sla:
        http.server.requests: 50ms,100ms,200ms,500ms,1s,2s,5s
```

Add custom metrics for domain KPIs (a tiny example — workers can extend):

```java
package com.<org>.<app>.shared.metrics;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import org.springframework.stereotype.Component;

/**
 * Custom domain metrics. Extend per BC as needed.
 *
 * ADR-004: Micrometer + Prometheus.
 */
@Component
public class DomainMetrics {
    private final Counter usersRegistered;

    public DomainMetrics(MeterRegistry registry) {
        this.usersRegistered = Counter.builder("app.users.registered")
            .description("Number of users registered")
            .register(registry);
    }

    public void incrementUsersRegistered() {
        usersRegistered.increment();
    }
}
```

Reference in `application.service.UserService.registerUser()` via a TODO
note (logic-translator or a follow-up may wire it).

---

## 3. Tracing — OpenTelemetry

Add to pom.xml:

```xml
<dependency>
    <groupId>io.opentelemetry.instrumentation</groupId>
    <artifactId>opentelemetry-spring-boot-starter</artifactId>
    <version>2.x</version>
</dependency>
```

Add to application.yml:

```yaml
otel:
  service:
    name: ${spring.application.name}
  exporter:
    otlp:
      endpoint: ${OTEL_EXPORTER_OTLP_ENDPOINT:http://localhost:4317}
  resource:
    attributes:
      deployment.environment: ${ENV:local}
  instrumentation:
    spring-webmvc:
      enabled: true
    spring-data:
      enabled: true
    jdbc:
      enabled: true
```

Document that custom spans (for domain events) can be added with
`@WithSpan` on service methods or programmatic Span building. Provide one
example as TODO in a service.

---

## 4. Security — production baseline

Refine `<backend-dir>/src/main/java/com/<org>/<app>/shared/config/SecurityConfig.java`
(scaffolder created the baseline; you tighten it):

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        return http
            .csrf(csrf -> csrf.disable())
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .headers(headers -> headers
                .contentTypeOptions(Customizer.withDefaults())
                .frameOptions(f -> f.deny())
                .httpStrictTransportSecurity(hsts -> hsts.includeSubDomains(true).maxAgeInSeconds(31_536_000))
                .referrerPolicy(rp -> rp.policy(ReferrerPolicy.STRICT_ORIGIN_WHEN_CROSS_ORIGIN))
                .crossOriginOpenerPolicy(cop -> cop.policy(CrossOriginOpenerPolicyHeaderWriter.CrossOriginOpenerPolicy.SAME_ORIGIN))
                .crossOriginEmbedderPolicy(cep -> cep.policy(CrossOriginEmbedderPolicyHeaderWriter.CrossOriginEmbedderPolicy.REQUIRE_CORP))
                .crossOriginResourcePolicy(crp -> crp.policy(CrossOriginResourcePolicyHeaderWriter.CrossOriginResourcePolicy.SAME_ORIGIN)))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/v1/auth/**", "/actuator/health/**", "/actuator/info", "/v3/api-docs/**", "/swagger-ui/**").permitAll()
                .requestMatchers("/actuator/**").hasRole("ADMIN")    // metrics + loggers gated
                .anyRequest().authenticated())
            .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()))
            .cors(c -> c.configurationSource(corsConfigurationSource()))
            .build();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        var config = new CorsConfiguration();
        config.setAllowedOrigins(List.of(
            // TODO(ADR-005): pull from env / config server
            System.getenv().getOrDefault("FRONTEND_ORIGIN", "http://localhost:4200")));
        config.setAllowedMethods(List.of("GET", "POST", "PUT", "PATCH", "DELETE"));
        config.setAllowedHeaders(List.of("Authorization", "Content-Type", "Idempotency-Key", "X-Request-Id"));
        config.setExposedHeaders(List.of("X-Request-Id", "Location"));
        config.setMaxAge(3600L);
        var source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        return source;
    }
}
```

Headers per OWASP Secure Headers Project. CSP is set on the FE (HTML
meta) — see frontend-config-templates.md.

---

## 5. Secrets management

- application.yml: secrets via env vars (`${DB_PASSWORD}`,
  `${OAUTH2_CLIENT_SECRET}`)
- never commit `application-prod.yml` with values; rely on
  `application-prod.yml` empty + env override at deploy time
- document Vault / AWS Secrets Manager integration as ADR-005 follow-up
  (out of scope for this scaffolder; user picks)

Provide a `<backend-dir>/.env.example`:

```
# .env.example — copy to .env and fill (gitignored)
DB_URL=jdbc:postgresql://localhost:5432/<app>
DB_USER=<app>
DB_PASSWORD=
OAUTH2_ISSUER_URI=
OAUTH2_CLIENT_ID=
OAUTH2_CLIENT_SECRET=
OTEL_EXPORTER_OTLP_ENDPOINT=
FRONTEND_ORIGIN=http://localhost:4200
ENV=local
```

Plus `<backend-dir>/.gitignore`:

```
.env
target/
*.iml
.idea/
*.log
```
