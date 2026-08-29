# API contract designer — OpenAPI 3.1 template

> Reference doc for `api-contract-designer`. Read at runtime when authoring
> `docs/refactoring/4.6-api/openapi.yaml`. The agent body keeps the decision
> logic (resource modelling, error format, pagination, idempotency, auth);
> this doc holds the canonical YAML skeleton and validation rules.

## Top-level skeleton

Single file at `docs/refactoring/4.6-api/openapi.yaml`:

```yaml
openapi: 3.1.0
info:
  title: <App> API
  version: 1.0.0
  description: |
    TO-BE API for <App>. Single contract consumed by both backend
    (Spring Boot) and frontend (Angular). Generated from Phase 1
    use cases and Phase 4 bounded contexts.
servers:
  - url: https://{environment}.example.com/v1
    variables:
      environment:
        default: api
        enum: [api, api-staging]
security:
  - bearerAuth: []
tags:
  - name: identity
    description: BC-01 — Identity & Access
  - name: payments
    description: BC-02 — Payments
paths:
  /users:
    get:
      tags: [identity]
      summary: List users
      operationId: listUsers
      x-uc-ref: UC-04   # custom extension: the UC-NN this endpoint serves
      parameters:
        - $ref: '#/components/parameters/Cursor'
        - $ref: '#/components/parameters/Limit'
      responses:
        '200':
          description: list of users
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserListResponse'
        '4XX':
          $ref: '#/components/responses/Error'
    post:
      tags: [identity]
      summary: Create a user
      operationId: createUser
      x-uc-ref: UC-01
      parameters:
        - $ref: '#/components/parameters/IdempotencyKey'
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
      responses:
        '201':
          description: created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '4XX':
          $ref: '#/components/responses/Error'
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  parameters:
    Cursor:
      name: cursor
      in: query
      schema: { type: string }
    Limit:
      name: limit
      in: query
      schema: { type: integer, minimum: 1, maximum: 200, default: 50 }
    IdempotencyKey:
      name: Idempotency-Key
      in: header
      required: true
      schema: { type: string }
  responses:
    Error:
      description: error
      content:
        application/problem+json:
          schema:
            $ref: '#/components/schemas/ProblemDetail'
  schemas:
    ProblemDetail: { ... }
    User: { ... }
    CreateUserRequest: { ... }
    UserListResponse: { ... }
```

## Error envelope (RFC 7807)

All error responses use the RFC 7807 ProblemDetail shape:

```yaml
ProblemDetail:
  type: object
  required: [type, title, status]
  properties:
    type: { type: string, format: uri }
    title: { type: string }
    status: { type: integer }
    detail: { type: string }
    instance: { type: string, format: uri }
    correlationId: { type: string }
```

Per Phase 2 security findings, ensure no internal information leaks in
`detail` (no stack traces, no SQL, no file paths).

## Key authoring rules

- every endpoint has an `operationId` (drives generated client method names)
- every endpoint has `x-uc-ref` (custom extension referencing the Phase 1 UC)
  — supports challenger traceability
- every endpoint has at least one error response using ProblemDetail
- schemas reused via `$ref: '#/components/schemas/...'` (no duplicates)
- examples for at least one happy and one error path per endpoint

## Validation step

After writing, validate:

- Bash: `which spectral` — if available, run
  `spectral lint docs/refactoring/4.6-api/openapi.yaml`
- if spectral unavailable: do a manual structural check (parse YAML;
  every `$ref` resolves; every `operationId` is unique; every schema is
  defined)
