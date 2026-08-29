# Code skeletons

> Reference doc for `backend-scaffolder`. Read at runtime when generating
> Java sources (Method steps 3–5 — controllers, DTOs, services).

## Controllers

For each tag/operation in the OpenAPI spec, generate a controller class
under the matching BC's `api/` package:

```java
package com.<org>.<app>.<bc>.api;

import com.<org>.<app>.<bc>.application.<Aggregate>Service;
import com.<org>.<app>.<bc>.api.dto.*;
import com.<org>.<app>.shared.error.NotFoundException;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * <BC name> controller.
 *
 * Implements OpenAPI operations defined in
 * docs/refactoring/4.6-api/openapi.yaml under tag `<bc-tag>`.
 *
 * Bounded context: BC-NN
 * UCs handled: UC-NN, UC-NN, UC-NN  (per x-uc-ref in OpenAPI)
 */
@RestController
@RequestMapping("/v1/<resource>")
@Tag(name = "<bc-tag>")
public class <BC>Controller {

    private final <Aggregate>Service service;

    public <BC>Controller(<Aggregate>Service service) {
        this.service = service;
    }

    /**
     * UC-NN — <human title>.
     *
     * AS-IS source ref: <repo>/<as-is-pkg>/<file>:<line>
     * (See logic-translator output for translation.)
     */
    @GetMapping("/{id}")
    public ResponseEntity<<DTO>> get<Resource>ById(@PathVariable String id) {
        // TODO(BC-NN, UC-NN): translate from <as-is-source-ref>
        // The service method below is a stub; logic-translator (W3c)
        // will replace its body. For now this returns a placeholder
        // that compiles.
        return ResponseEntity.ok(service.findById(id));
    }

    @PostMapping
    public ResponseEntity<<DTO>> create<Resource>(
            @RequestHeader("Idempotency-Key") String idempotencyKey,
            @Valid @RequestBody Create<Resource>Request request) {
        // TODO(BC-NN, UC-NN): translate from <as-is-source-ref>
        return ResponseEntity.status(201).body(service.create(idempotencyKey, request));
    }
}
```

### Controller rules

- Controller method signatures derived from OpenAPI operationIds.
- `@Valid` on every request body.
- Path parameters typed as `String` (opaque IDs per ADR-003 contract); the
  service handles parsing.
- Response wrapped in `ResponseEntity<>` for explicit status codes.
- Header parameters mapped via `@RequestHeader`.
- `@Tag` references match OpenAPI tag.

## DTOs

For each OpenAPI schema referenced by a BC's operations, generate a Java
record:

```java
package com.<org>.<app>.<bc>.api.dto;

import jakarta.validation.constraints.*;

/**
 * Request DTO for createUser (UC-01).
 *
 * Generated from openapi.yaml#/components/schemas/CreateUserRequest.
 * Field validation mirrors OpenAPI constraints.
 */
public record CreateUserRequest(
        @NotBlank @Email String email,
        @NotBlank @Size(min = 8, max = 72) String password,
        @NotBlank @Size(max = 100) String fullName) {}
```

If the openapi-generator-maven-plugin is configured to generate models,
prefer that over hand-written records. The scaffolder configures the plugin
to generate API interfaces only; DTOs can be either generated or
hand-written depending on the project's preference (default: hand-write
records here for clarity, regenerate via plugin only if user requests).

Document the choice in
`src/main/java/com/<org>/<app>/<bc>/api/README.md`.

## Service skeletons

```java
package com.<org>.<app>.<bc>.application;

import com.<org>.<app>.<bc>.api.dto.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * <Aggregate> application service.
 *
 * Orchestrates use cases for BC-NN. Domain logic in:
 * com.<org>.<app>.<bc>.domain.<Aggregate>  (populated by data-mapper)
 *
 * Translation status: scaffold (logic-translator W3c will fill).
 */
@Service
@Transactional
public class <Aggregate>Service {

    /**
     * UC-NN — <human title>.
     *
     * AS-IS source ref: <repo>/<as-is-pkg>/<file>:<line>
     */
    public <DTO> findById(String id) {
        // TODO(BC-NN, UC-NN): translate from <as-is-source-ref>
        throw new UnsupportedOperationException(
            "TODO: implement findById — see TODO marker above");
    }

    public <DTO> create(String idempotencyKey, Create<Resource>Request request) {
        // TODO(BC-NN, UC-NN): translate from <as-is-source-ref>
        throw new UnsupportedOperationException(
            "TODO: implement create — see TODO marker above");
    }
}
```

`UnsupportedOperationException` is intentional — calling these methods in a
test would fail loudly, signaling unfilled translation. Phase 5 tests will
be xfailed for unfilled UCs (mirroring Phase 3 policy).

## Application class

`src/main/java/com/<org>/<app>/Application.java`:

```java
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```
