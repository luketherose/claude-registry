# Backend document structure

The default chapter and section layout for `backend-doc.tex`, used whenever
the provided Word template does not impose one.

```
1.  Title page
2.  Revision history
3.  Table of contents
4.  Introduction
    4.1 Purpose of the document
    4.2 Scope of application
    4.3 Technology stack (the project's backend stack, e.g. Java 17 + Spring Boot 3.x + PostgreSQL)
    4.4 Prerequisites and references

5.  System Architecture
    5.1 Architectural overview (layer: controller → service → repository → DB)
    5.2 Bounded context and project package structure
    5.3 Datasource configuration (if multi-datasource)
    5.4 Java package schema

6.  API Reference
    6.1 Base configuration (base URL, versioning, authentication)
    6.N [ControllerName] — [feature]
        - Endpoint: METHOD /api/path
        - Authorisation: required roles
        - Request DTO: fields, validations
        - Response DTO: fields, HTTP codes
        - Errors: codes and causes

7.  Data Model
    7.1 Relational schema (main tables)
    7.2 JPA Entities (per project bounded context)
        - [EntityName]: fields, relations, constraints
    7.3 Request/response DTOs for API

8.  Business Logic
    8.1 [ServiceName] — [responsibility]
        - Main methods
        - Applied business rules (BR-N reference)
    8.N [ServiceName N]

9.  Security Architecture
    9.1 Authentication (JWT flow)
    9.2 Authorisation (roles, @PreAuthorize)
    9.3 Password hashing (BCrypt)
    9.4 CORS and CSRF

10. Error Handling and Logging
    10.1 Exception hierarchy (base exception and project subclasses)
    10.2 GlobalExceptionHandler — HTTP status mapping
    10.3 Structured logging (MDC, correlation ID, log levels)
    10.4 Monitoring and metrics

11. External Integrations
    For each external integration in the project:
    11.N [Integration name] — WebClient pattern

12. Configuration
    12.1 Spring profiles (dev, prod)
    12.2 DataSource configuration
    12.3 Mandatory environment variables

13. Appendix
    13.1 Technical glossary
    13.2 Known architectural issues (if documented in the project)
    13.3 References
```
