# Error handler & security baseline

> Reference doc for `backend-scaffolder`. Read at runtime when generating
> the shared error handler and security baseline (Method steps 6–7).

## RFC 7807 error handler

`shared/error/ProblemDetailExceptionHandler.java`:

```java
@RestControllerAdvice
public class ProblemDetailExceptionHandler extends ResponseEntityExceptionHandler {

    @ExceptionHandler(NotFoundException.class)
    public ProblemDetail handleNotFound(NotFoundException ex, HttpServletRequest req) {
        ProblemDetail pd = ProblemDetail.forStatus(HttpStatus.NOT_FOUND);
        pd.setTitle("Resource not found");
        pd.setDetail(ex.getMessage());
        pd.setInstance(URI.create(req.getRequestURI()));
        pd.setProperty("correlationId", MDC.get("correlationId"));
        return pd;
    }

    // 405 — wrong HTTP verb on an existing path.
    // MUST be overridden explicitly: without this method, Spring routes
    // HttpRequestMethodNotSupportedException through the generic
    // Exception handler and the FE sees 500 instead of 405.
    @Override
    protected ResponseEntity<Object> handleHttpRequestMethodNotSupported(
            HttpRequestMethodNotSupportedException ex,
            HttpHeaders headers, HttpStatusCode status, WebRequest req) {
        ProblemDetail pd = ProblemDetail.forStatus(HttpStatus.METHOD_NOT_ALLOWED);
        pd.setTitle("Method not allowed");
        pd.setDetail("Method " + ex.getMethod() + " is not supported on this resource");
        pd.setProperty("supportedMethods", ex.getSupportedHttpMethods());
        pd.setProperty("correlationId", MDC.get("correlationId"));
        return ResponseEntity.status(HttpStatus.METHOD_NOT_ALLOWED).body(pd);
    }

    // 415 — request body in unsupported Content-Type.
    @Override
    protected ResponseEntity<Object> handleHttpMediaTypeNotSupported(
            HttpMediaTypeNotSupportedException ex,
            HttpHeaders headers, HttpStatusCode status, WebRequest req) {
        ProblemDetail pd = ProblemDetail.forStatus(HttpStatus.UNSUPPORTED_MEDIA_TYPE);
        pd.setTitle("Unsupported media type");
        pd.setDetail("Content-Type " + ex.getContentType() + " is not supported");
        pd.setProperty("supportedMediaTypes", ex.getSupportedMediaTypes());
        return ResponseEntity.status(HttpStatus.UNSUPPORTED_MEDIA_TYPE).body(pd);
    }

    // 406 — Accept header cannot be satisfied.
    @Override
    protected ResponseEntity<Object> handleHttpMediaTypeNotAcceptable(
            HttpMediaTypeNotAcceptableException ex,
            HttpHeaders headers, HttpStatusCode status, WebRequest req) {
        ProblemDetail pd = ProblemDetail.forStatus(HttpStatus.NOT_ACCEPTABLE);
        pd.setTitle("Not acceptable");
        pd.setDetail("None of the requested media types can be produced");
        pd.setProperty("supportedMediaTypes", ex.getSupportedMediaTypes());
        return ResponseEntity.status(HttpStatus.NOT_ACCEPTABLE).body(pd);
    }

    // 404 — unmatched static resource / handler (Boot 3.2+).
    @ExceptionHandler(NoResourceFoundException.class)
    public ProblemDetail handleNoResource(NoResourceFoundException ex) {
        ProblemDetail pd = ProblemDetail.forStatus(HttpStatus.NOT_FOUND);
        pd.setTitle("Not found");
        pd.setDetail("No handler for: " + ex.getResourcePath());
        return pd;
    }

    // ... handlers for ValidationException, IdempotencyConflictException,
    //     ConstraintViolationException, MethodArgumentNotValidException,
    //     plus a generic Exception handler with status 500 and SAFE
    //     message (no stack trace leak).
}
```

> Why the 405 / 415 / 406 overrides are mandatory: in `Spring 6 /
> Boot 3` these exceptions are produced by `DispatcherServlet` *before*
> any `@ExceptionHandler`-annotated method on a `@RestControllerAdvice`
> can claim them. The only correct integration is to override the
> protected `handleXxx` methods from `ResponseEntityExceptionHandler`.
> Forgetting them turns "wrong verb on existing path" into a generic
> 500, leaking implementation detail and breaking RFC 7807 semantics.

Match Phase 2 security findings: no internal info leaks in `detail`.

## Security config baseline

`shared/config/SecurityConfig.java`:

```java
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        return http
            .csrf(csrf -> csrf.disable())  // stateless; cookies not used
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/v1/auth/**", "/actuator/health", "/swagger-ui/**", "/v3/api-docs/**").permitAll()
                .anyRequest().authenticated())
            .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()))
            .cors(Customizer.withDefaults())
            .build();
    }

    @Bean
    public CorsConfigurationSource corsConfigurationSource(
            @Value("${app.cors.allowed-origin-patterns:http://localhost:*,http://127.0.0.1:*}") List<String> originPatterns) {
        var config = new CorsConfiguration();
        // setAllowedOriginPatterns (not setAllowedOrigins) so localhost AND
        // 127.0.0.1 on any port are accepted in dev. In prod, set
        // app.cors.allowed-origin-patterns explicitly via application.yml /
        // env vars to the real FE origin(s).
        config.setAllowedOriginPatterns(originPatterns);
        config.setAllowedMethods(List.of("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"));
        config.setAllowedHeaders(List.of("*"));
        config.setExposedHeaders(List.of("X-Correlation-Id"));
        config.setAllowCredentials(true);
        var source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        return source;
    }
}
```

> CORS rule: **the `CorsConfigurationSource` bean is the single source
> of truth**. Controllers MUST NOT carry `@CrossOrigin` annotations
> (those bypass the centralised bean, duplicate origin lists on every
> controller, and were the cause of GAP-005 in the InfoSync 2026-05
> retrospective). The agent must grep its own output:
> ```bash
> ! grep -rln "@CrossOrigin" src/main/java
> ```
> If the grep finds matches, remove them — the centralised bean already
> covers every endpoint via `/**`.

This is a baseline — `hardening-architect` (W4) refines it with the final
security headers, CSP, etc.

## Boot smoke test (mandatory)

Emit at `src/test/java/com/<org>/<app>/BootSmokeTest.java`:

```java
package com.<org>.<app>;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

/**
 * Boot smoke — verifies that the Spring application can start with the
 * DEFAULT profile (no @ActiveProfiles), the same way `java -jar` runs it.
 *
 * Every other test in this module typically uses @ActiveProfiles("test"),
 * so they only exercise the test profile and would not catch a regression
 * in the default-profile boot path (e.g. a missing JPA autoconfig
 * exclude that makes Spring fail to resolve `XxxRepository` beans).
 *
 * If this test fails with NoSuchBeanDefinitionException /
 * UnsatisfiedDependencyException, the bug is in the default profile
 * wiring — most likely application.yml `spring.profiles.default` or
 * the autoconfigure-exclude list. Do NOT add @ActiveProfiles here.
 */
@SpringBootTest
class BootSmokeTest {

    @Test
    void contextLoadsOnDefaultProfile() {
        // empty — framework asserts context startup
    }
}
```

The default profile in `application.yml` should either (a) define a
working datasource (H2 for dev, real DB for prod profiles), or (b) set
`spring.profiles.default: test` so `java -jar` boots on an in-memory
profile. Excluding `DataSourceAutoConfiguration` alone does NOT make
repositories optional — `@Service` constructors still require them and
the context fails. This was GAP-009 in the InfoSync 2026-05 retro.
