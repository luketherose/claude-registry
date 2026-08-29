# Package layout

> Reference doc for `backend-scaffolder`. Read at runtime when laying out
> the source tree (Method step 2 — Package layout).

## Top-level package

`com.<org>.<app>` mirrors ADR-001:

- **modular monolith**: one sub-package per BC.
- **microservices**: one project per service. This scaffolder produces ONE
  service at a time; supervisor invokes once per service if Mode B.

## Per-BC layout

For each BC from `.refactoring-kb/00-decomposition/bounded-contexts.md`:

```
src/main/java/com/<org>/<app>/<bc-pkg>/
├── api/                          (controllers + DTOs)
│   ├── <BC>Controller.java       (implements the OpenAPI-generated interface)
│   └── dto/                      (request / response DTOs derived from OpenAPI schemas)
├── application/                  (services — orchestration, not domain logic)
│   └── <Aggregate>Service.java
├── domain/                       (placeholder — populated by data-mapper)
│   └── README.md                 ("populated by data-mapper")
└── infrastructure/               (placeholder — populated by data-mapper)
    └── README.md                 ("populated by data-mapper")
```

## Shared package

```
src/main/java/com/<org>/<app>/shared/
├── config/
│   ├── SecurityConfig.java       (Spring Security 6 baseline)
│   ├── OpenApiConfig.java        (springdoc config)
│   └── ObservabilityConfig.java  (placeholder for hardening-architect)
├── error/
│   ├── ProblemDetailExceptionHandler.java   (@ControllerAdvice, RFC 7807)
│   ├── DomainException.java                 (base for domain errors)
│   ├── NotFoundException.java
│   ├── ValidationException.java
│   └── IdempotencyConflictException.java
├── idempotency/
│   ├── IdempotencyKey.java                  (annotation)
│   ├── IdempotencyKeyAspect.java            (AOP — placeholder logic)
│   └── IdempotencyKeyRepository.java        (interface; data-mapper fills impl)
└── correlation/
    ├── CorrelationIdFilter.java             (puts X-Request-Id in MDC)
    └── CorrelationIdInterceptor.java        (extracts header / generates UUID)
```
