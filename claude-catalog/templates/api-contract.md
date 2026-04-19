# API Contract — Template

Use this template to document a REST API contract before or after implementation.
For machine-readable specs, use OpenAPI 3.1 YAML (the `api-designer` subagent can
generate it). This template is for human-readable contract documentation.

---

## API Contract: {Service Name}

**Version**: v{N}
**Base URL**: `https://{host}/api/v{N}`
**Authentication**: {Bearer JWT | API Key | mTLS | None}
**Content-Type**: `application/json`
**Error format**: RFC 7807 ProblemDetail

---

### Endpoints

#### {Resource Name}

##### `GET /resource`

Retrieves a paginated list of resources.

**Query parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | integer | No | Page number, 0-based. Default: 0 |
| `size` | integer | No | Page size. Default: 20, Max: 100 |
| `sort` | string | No | Sort field and direction: `field,asc` or `field,desc` |

**Response 200 OK**
```json
{
  "content": [
    {
      "id": 1,
      "name": "Example"
    }
  ],
  "totalElements": 100,
  "totalPages": 5,
  "hasNext": true
}
```

**Response 400 Bad Request** (invalid query parameters)
```json
{
  "type": "about:blank",
  "title": "Bad Request",
  "status": 400,
  "detail": "Page size cannot exceed 100"
}
```

---

##### `POST /resource`

Creates a new resource.

**Request body**
```json
{
  "name": "string, required, 1-100 chars",
  "description": "string, optional, max 500 chars"
}
```

**Response 201 Created**
- `Location` header: `/api/v1/resource/{id}`
```json
{
  "id": 1,
  "name": "Example",
  "createdAt": "2026-04-19T10:00:00Z"
}
```

**Response 400 Bad Request** (validation failure)
**Response 409 Conflict** (duplicate key)

---

##### `GET /resource/{id}`

Retrieves a single resource by ID.

**Path parameters**: `id` — integer, required

**Response 200 OK**
**Response 404 Not Found**

---

##### `PUT /resource/{id}`

Full replacement of a resource (idempotent).

**Response 200 OK** | **Response 404 Not Found**

---

##### `DELETE /resource/{id}`

Deletes a resource.

**Response 204 No Content** | **Response 404 Not Found**

---

### Common error responses

| Status | Title | When |
|--------|-------|------|
| 400 | Bad Request | Invalid request body or query parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Authenticated but lacks permission |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | Business rule violation (duplicate, state conflict) |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server error |

---

### Breaking change policy

- Adding new optional fields to responses: non-breaking
- Adding new optional request fields: non-breaking
- Removing fields: breaking — requires major version bump
- Changing field types: breaking — requires major version bump
- Changing URL structure: breaking — requires major version bump
