# Error handling

## Contents

- Custom exception hierarchy
- Global Exception Handling
- ErrorResponse DTO

## Custom exception hierarchy

This is the definition point for the hierarchy. The base class and its specialisations belong in the `exception/` package.

```java
public class AppException extends RuntimeException {
    private final String errorCode;

    public AppException(String errorCode, String message) {
        super(message);
        this.errorCode = errorCode;
    }

    public AppException(String errorCode, String message, Throwable cause) {
        super(message, cause);
        this.errorCode = errorCode;
    }

    public String getErrorCode() { return errorCode; }
}

// 404 — entity not found by ID or business key
public class EntityNotFoundException extends AppException {
    public EntityNotFoundException(String entity, Object id) {
        super("NOT_FOUND", entity + " not found: " + id);
    }
}

// 422 — business rule violated (domain invariant)
public class BusinessRuleViolationException extends AppException {
    public BusinessRuleViolationException(String message) {
        super("BUSINESS_RULE_VIOLATION", message);
    }
}

// 502 — external service unavailable or in error
public class ExternalApiException extends AppException {
    public ExternalApiException(String message, String errorCode) {
        super(errorCode, message);
    }
}
```

**When to add a new exception**: extend `AppException` with a structured `errorCode` (e.g. `"ORDER_CODE_DUPLICATE"`). Add the corresponding `@ExceptionHandler` in the `GlobalExceptionHandler`. Never use generic exceptions (bare `RuntimeException`) for domain errors.

---

## Global Exception Handling

```java
@ControllerAdvice
@Slf4j
public class GlobalExceptionHandler extends ResponseEntityExceptionHandler {

    // Custom domain exceptions
    @ExceptionHandler(EntityNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(EntityNotFoundException ex) {
        log.warn("Entity not found: {}", ex.getMessage());
        return buildError(HttpStatus.NOT_FOUND, ex.getErrorCode(), ex.getMessage());
    }

    @ExceptionHandler(BusinessRuleViolationException.class)
    public ResponseEntity<ErrorResponse> handleBusinessRule(BusinessRuleViolationException ex) {
        log.warn("Business rule violation: {}", ex.getMessage());
        return buildError(HttpStatus.UNPROCESSABLE_ENTITY, ex.getErrorCode(), ex.getMessage());
    }

    @ExceptionHandler(ExternalApiException.class)
    public ResponseEntity<ErrorResponse> handleExternalApi(ExternalApiException ex) {
        log.error("External API failure: {}", ex.getMessage());
        return buildError(HttpStatus.BAD_GATEWAY, ex.getErrorCode(), "External service unavailable");
    }

    // Bean Validation — @Valid failed
    @Override
    protected ResponseEntity<Object> handleMethodArgumentNotValid(
            MethodArgumentNotValidException ex,
            HttpHeaders headers, HttpStatusCode status, WebRequest request) {

        List<FieldViolation> violations = ex.getBindingResult().getFieldErrors().stream()
            .map(e -> new FieldViolation(e.getField(), e.getDefaultMessage()))
            .toList();

        ErrorResponse body = new ErrorResponse(
            "VALIDATION_ERROR",
            "Request validation failed",
            violations
        );

        log.warn("Validation failed: {} violations", violations.size());
        return ResponseEntity.badRequest().body(body);
    }

    // Fallback for unhandled exceptions
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleGeneric(Exception ex, WebRequest request) {
        log.error("Unexpected error on {}: {}", request.getDescription(false), ex.getMessage(), ex);
        return buildError(HttpStatus.INTERNAL_SERVER_ERROR, "INTERNAL_ERROR",
            "An unexpected error occurred");
    }

    private ResponseEntity<ErrorResponse> buildError(HttpStatus status, String code, String message) {
        return ResponseEntity.status(status).body(new ErrorResponse(code, message, List.of()));
    }
}
```

### ErrorResponse DTO

```java
public record ErrorResponse(
    String code,
    String message,
    List<FieldViolation> violations
) {
    public ErrorResponse(String code, String message) {
        this(code, message, List.of());
    }
}

public record FieldViolation(String field, String message) {}
```

---
