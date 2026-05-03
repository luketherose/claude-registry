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

    // ... handlers for ValidationException, IdempotencyConflictException,
    //     ConstraintViolationException, MethodArgumentNotValidException,
    //     plus a generic Exception handler with status 500 and SAFE
    //     message (no stack trace leak).
}
```

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
    public CorsConfigurationSource corsConfigurationSource() {
        // TODO(ADR-003): configure FE origin from properties
        var config = new CorsConfiguration();
        config.setAllowedOrigins(List.of("http://localhost:4200"));
        config.setAllowedMethods(List.of("GET", "POST", "PUT", "PATCH", "DELETE"));
        config.setAllowedHeaders(List.of("*"));
        var source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        return source;
    }
}
```

This is a baseline — `hardening-architect` (W4) refines it with the final
security headers, CSP, etc.
