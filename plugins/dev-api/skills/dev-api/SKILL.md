---
name: dev-api
description: Design and implement REST APIs using OpenAPI-first approach with proper versioning, error handling, and documentation. Use when designing or implementing API endpoints.
argument-hint: "[api-description]"
---

# API Design & Implementation (OpenAPI-First)

Design and implement the API for: **$ARGUMENTS**

## Workflow

1. **Define OpenAPI spec first** — design the contract before code
2. **Review with stakeholders** — agree on shapes, errors, versioning
3. **Generate types/validators** — from the spec
4. **Implement handlers** — test-driven
5. **Validate against spec** — contract tests

## OpenAPI Spec Design

Write the spec in `api/openapi.yaml`:

```yaml
openapi: 3.1.0
info:
  title: Service API
  version: 1.0.0
  description: API documentation

servers:
  - url: /api/v1

paths:
  /resources:
    get:
      operationId: listResources
      summary: List resources with pagination
      tags: [resources]
      parameters:
        - $ref: '#/components/parameters/PageParam'
        - $ref: '#/components/parameters/PageSizeParam'
        - name: status
          in: query
          schema:
            $ref: '#/components/schemas/ResourceStatus'
      responses:
        '200':
          description: Paginated list
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaginatedResources'
        '401':
          $ref: '#/components/responses/Unauthorized'

    post:
      operationId: createResource
      summary: Create a resource
      tags: [resources]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateResourceRequest'
      responses:
        '201':
          description: Created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Resource'
        '400':
          $ref: '#/components/responses/BadRequest'
        '409':
          $ref: '#/components/responses/Conflict'

  /resources/{id}:
    get:
      operationId: getResource
      parameters:
        - $ref: '#/components/parameters/ResourceId'
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Resource'
        '404':
          $ref: '#/components/responses/NotFound'
```

## Error Response Standard (RFC 7807)

```yaml
components:
  schemas:
    ProblemDetail:
      type: object
      required: [type, title, status]
      properties:
        type:
          type: string
          format: uri
          description: Error type URI
        title:
          type: string
          description: Human-readable summary
        status:
          type: integer
          description: HTTP status code
        detail:
          type: string
          description: Human-readable explanation
        instance:
          type: string
          format: uri
          description: URI of the specific occurrence
        errors:
          type: array
          items:
            type: object
            properties:
              field:
                type: string
              message:
                type: string
```

## API Design Rules

### Naming
- Use plural nouns for collections: `/orders`, `/users`
- Use kebab-case for multi-word paths: `/order-items`
- Use camelCase for JSON fields: `createdAt`, `orderId`
- Nest sub-resources: `/orders/{id}/items`

### HTTP Methods
| Method | Usage | Idempotent | Response |
|--------|-------|------------|----------|
| GET | Read | Yes | 200 |
| POST | Create | No | 201 + Location |
| PUT | Full replace | Yes | 200 |
| PATCH | Partial update | No | 200 |
| DELETE | Remove | Yes | 204 |

### Pagination
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "totalItems": 150,
    "totalPages": 8
  }
}
```

### Filtering & Sorting
- Filter: `?status=active&created_after=2024-01-01`
- Sort: `?sort=created_at:desc,name:asc`
- Search: `?q=search+term`

### Versioning
- URL path versioning: `/api/v1/resources`
- Increment on breaking changes only
- Maintain previous version during migration period

### Status Codes
| Code | When |
|------|------|
| 200 | Success (GET, PUT, PATCH) |
| 201 | Created (POST) |
| 204 | No Content (DELETE) |
| 400 | Validation error |
| 401 | Not authenticated |
| 403 | Not authorized |
| 404 | Resource not found |
| 409 | Conflict (duplicate, state conflict) |
| 422 | Unprocessable (business rule violation) |
| 429 | Rate limited |
| 500 | Server error (never expose details) |

## Rules
- Design spec BEFORE implementation
- All endpoints documented with examples
- Consistent error format (RFC 7807)
- Input validation on every endpoint
- Never expose internal IDs, stack traces, or DB errors
- Always paginate list endpoints
- Use ETag/If-None-Match for caching where appropriate
- Rate limit all public endpoints
- Version all breaking changes
