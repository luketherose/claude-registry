# Error handling (RFC 7807)

The typed exception hierarchy, the global `@RestControllerAdvice` that renders
every failure as an RFC 7807 `ProblemDetail`, and the rules that govern both.

## Contents

- [Exception hierarchy](#exception-hierarchy)
- [Global handler (RFC 7807 ProblemDetail)](#global-handler-rfc-7807-problemdetail)
- [Error handling rules](#error-handling-rules)

## Exception hierarchy

```java
public abstract class ApplicationException extends RuntimeException {
    private final String errorCode;
    protected ApplicationException(String errorCode, String message) {
        super(message);
        this.errorCode = errorCode;
    }
}

public class ResourceNotFoundException extends ApplicationException {
    public ResourceNotFoundException(String resource, Object id) {
        super("RESOURCE_NOT_FOUND", resource + " not found with id: " + id);
    }
}

public class BusinessRuleViolationException extends ApplicationException {
    public BusinessRuleViolationException(String errorCode, String message) {
        super(errorCode, message);
    }
}
```

## Global handler (RFC 7807 ProblemDetail)

```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(ResourceNotFoundException.class)
    public ProblemDetail handleNotFound(ResourceNotFoundException ex) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
            HttpStatus.NOT_FOUND, ex.getMessage());
        problem.setTitle("Resource Not Found");
        problem.setProperty("errorCode", ex.getErrorCode());
        return problem;
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ProblemDetail handleValidation(MethodArgumentNotValidException ex) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(
            HttpStatus.BAD_REQUEST, "Validation failed");
        problem.setProperty("violations", ex.getBindingResult().getFieldErrors().stream()
            .map(e -> Map.of("field", e.getField(), "message", e.getDefaultMessage()))
            .toList());
        return problem;
    }

    @ExceptionHandler(Exception.class)
    public ProblemDetail handleGeneral(Exception ex) {
        log.error("Unhandled exception", ex);
        return ProblemDetail.forStatusAndDetail(
            HttpStatus.INTERNAL_SERVER_ERROR, "An unexpected error occurred");
    }
}
```

## Error handling rules
- Never swallow exceptions silently.
- Never log and rethrow at the same layer (duplicate entries).
- Never expose stack traces or internal class names in API responses.
- Never use exceptions for flow control. Use `Optional<T>` instead.
