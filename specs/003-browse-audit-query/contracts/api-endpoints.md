# API Endpoints: Browse Functionality, Approval Status Query API, and Audit Logging

**Feature**: 003-browse-audit-query  
**Date**: 2025-11-12  
**Backend**: FastAPI with Python 3.13+

## Overview

This document defines the API contracts for:
1. **GET /registrations/by-url** - Query registration by endpoint URL
2. **GET /audit-logs** - Query audit log entries with filters

Both endpoints build on existing `/registrations` API from feature 002.

---

## Endpoint 1: Query Registration by URL

### GET `/registrations/by-url`

Query a single registration by its exact endpoint URL. Used by CI/CD pipelines and monitoring systems for automated compliance checks.

**Path**: `/registrations/by-url`  
**Method**: GET  
**Authentication**: Required (Bearer token)  
**Authorization**: Any authenticated user

#### Query Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `endpoint_url` | string | Yes | Exact endpoint URL to query (URL-encoded) | `https%3A%2F%2Fapi.example.com%2Fmcp` |

**Note**: URL encoding handled automatically by HTTP clients. Example curl:
```bash
curl -G "http://localhost:8000/registrations/by-url" \
  --data-urlencode "endpoint_url=https://api.example.com/mcp" \
  -H "Authorization: Bearer $TOKEN"
```

#### Response Codes

| Code | Description |
|------|-------------|
| 200 | Registration found and returned |
| 401 | Unauthorized (missing or invalid token) |
| 404 | No registration found for this endpoint URL |
| 500 | Internal server error |

#### Success Response (200)

**Content-Type**: `application/json`

```json
{
  "registration_id": "abc-123-def-456",
  "endpoint_url": "https://api.example.com/mcp",
  "endpoint_name": "Example MCP Server",
  "description": "Production MCP endpoint for example.com",
  "owner_contact": "admin@example.com",
  "available_tools": [
    {
      "name": "search",
      "description": "Search tool"
    },
    {
      "name": "analyze",
      "description": "Analysis tool"
    }
  ],
  "status": "Approved",
  "submitter_id": "user-uuid-123",
  "approver_id": "admin-uuid-456",
  "created_at": "2025-11-11T10:00:00Z",
  "updated_at": "2025-11-11T10:30:00Z",
  "approved_at": "2025-11-11T10:30:00Z"
}
```

**Schema**: Same as `RegistrationResponse` from existing GET `/registrations/{id}` endpoint.

#### Error Response (404)

```json
{
  "detail": "No registration found for this endpoint URL"
}
```

#### Error Response (401)

```json
{
  "detail": "Not authenticated"
}
```

#### Implementation Notes

- Uses existing `RegistrationResponse` schema (no new schema needed)
- Fast lookup via unique index on `registrations.endpoint_url` column
- URL must match exactly (no normalization, no partial matching)
- Special characters in URL are supported (properly encoded/decoded)
- Performance target: <200ms for 95% of requests (FR-015)

#### Example Usage

**Python (requests)**:
```python
import requests

response = requests.get(
    "http://localhost:8000/registrations/by-url",
    params={"endpoint_url": "https://api.example.com/mcp"},
    headers={"Authorization": f"Bearer {token}"}
)

if response.status_code == 200:
    registration = response.json()
    if registration["status"] != "Approved":
        print(f"ERROR: Endpoint not approved (status: {registration['status']})")
        exit(1)
elif response.status_code == 404:
    print("ERROR: Endpoint not registered")
    exit(1)
```

**curl**:
```bash
# Query approved status
STATUS=$(curl -s -G "http://localhost:8000/registrations/by-url" \
  --data-urlencode "endpoint_url=https://api.example.com/mcp" \
  -H "Authorization: Bearer $TOKEN" \
  | jq -r '.status')

if [ "$STATUS" != "Approved" ]; then
  echo "ERROR: Endpoint not approved (status: $STATUS)"
  exit 1
fi
```

---

## Endpoint 2: Query Audit Logs

### GET `/audit-logs`

Query audit log entries with filtering by registration, user, action type, and date range. Admin-only endpoint for compliance and troubleshooting.

**Path**: `/audit-logs`  
**Method**: GET  
**Authentication**: Required (Bearer token)  
**Authorization**: Admin only (returns 403 if user is not admin)

#### Query Parameters

| Parameter | Type | Required | Description | Default | Example |
|-----------|------|----------|-------------|---------|---------|
| `registration_id` | UUID | No | Filter by specific registration | None | `abc-123-def-456` |
| `user_id` | UUID | No | Filter by user who performed action | None | `user-uuid-123` |
| `action` | string | No | Filter by action type: `Created`, `Approved`, `Rejected`, `Updated`, `Deleted` | None | `Approved` |
| `from` | ISO 8601 datetime | No | Start of date range (inclusive) | None | `2025-11-01T00:00:00Z` |
| `to` | ISO 8601 datetime | No | End of date range (inclusive) | None | `2025-11-30T23:59:59Z` |
| `limit` | integer | No | Maximum results to return (1-200) | 50 | `100` |
| `offset` | integer | No | Number of results to skip (pagination) | 0 | `50` |

**Filter Combinations**: All filters can be combined. Results match ALL specified filters (AND logic).

#### Response Codes

| Code | Description |
|------|-------------|
| 200 | Results returned (may be empty list) |
| 400 | Bad request (invalid parameters, e.g., end date before start date) |
| 401 | Unauthorized (missing or invalid token) |
| 403 | Forbidden (user is not admin) |
| 500 | Internal server error |

#### Success Response (200)

**Content-Type**: `application/json`

```json
{
  "total": 125,
  "limit": 50,
  "offset": 0,
  "results": [
    {
      "log_id": "log-uuid-001",
      "registration_id": "abc-123-def-456",
      "user_id": "admin-uuid-456",
      "user_email": "admin@example.com",
      "user_display_name": "Admin User",
      "action": "Approved",
      "previous_status": "Pending",
      "new_status": "Approved",
      "metadata": {
        "reason": "Meets all security requirements"
      },
      "timestamp": "2025-11-11T10:30:00Z"
    },
    {
      "log_id": "log-uuid-002",
      "registration_id": "abc-123-def-456",
      "user_id": "user-uuid-123",
      "user_email": "user@example.com",
      "user_display_name": "Regular User",
      "action": "Created",
      "previous_status": null,
      "new_status": "Pending",
      "metadata": {
        "initial_values": {
          "endpoint_url": "https://api.example.com/mcp",
          "endpoint_name": "Example MCP Server",
          "status": "Pending"
        }
      },
      "timestamp": "2025-11-11T10:00:00Z"
    }
  ]
}
```

**Schema**: `AuditLogListResponse` with array of `AuditLogResponse` objects.

#### Error Response (403)

```json
{
  "detail": "Admin privileges required for this operation"
}
```

#### Error Response (400)

```json
{
  "detail": "Invalid date range: end date must be after start date"
}
```

**Other 400 scenarios**:
- `limit` < 1 or > 200: "Limit must be between 1 and 200"
- `offset` < 0: "Offset must be non-negative"
- Invalid UUID format: "Invalid UUID format for registration_id"
- Invalid action value: "Action must be one of: Created, Approved, Rejected, Updated, Deleted"

#### Pagination

Calculate pagination info:
```python
total_pages = ceil(total / limit)
has_next_page = (offset + limit) < total
has_prev_page = offset > 0

next_offset = offset + limit if has_next_page else None
prev_offset = max(0, offset - limit) if has_prev_page else None
```

#### Example Usage

**Get all audit logs for a specific registration**:
```bash
curl "http://localhost:8000/audit-logs?registration_id=abc-123-def-456&limit=50&offset=0" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Get all actions by a specific user**:
```bash
curl "http://localhost:8000/audit-logs?user_id=user-uuid-123&limit=100&offset=0" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Get all approvals in November 2025**:
```bash
curl -G "http://localhost:8000/audit-logs" \
  --data-urlencode "action=Approved" \
  --data-urlencode "from=2025-11-01T00:00:00Z" \
  --data-urlencode "to=2025-11-30T23:59:59Z" \
  --data-urlencode "limit=200" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Python (requests) - paginated query**:
```python
import requests

def get_all_audit_logs(registration_id: str, token: str):
    all_logs = []
    offset = 0
    limit = 100
    
    while True:
        response = requests.get(
            "http://localhost:8000/audit-logs",
            params={
                "registration_id": registration_id,
                "limit": limit,
                "offset": offset
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        data = response.json()
        all_logs.extend(data["results"])
        
        if offset + limit >= data["total"]:
            break
        
        offset += limit
    
    return all_logs
```

#### Implementation Notes

- Results ordered by timestamp DESC (newest first) - FR-026
- User information (email, display_name) joined from users table for convenience
- Metadata column is JSONB - flexible schema per action type
- Performance target: <1 second even with 10,000+ entries (SC-005)
- Uses composite indexes on (registration_id, timestamp) and (user_id, timestamp)
- Admin check via `require_admin` dependency (same pattern as existing endpoints)

---

## Existing Endpoints Used by Browse Page

The Browse page frontend uses existing `/registrations` endpoints from feature 002:

### GET `/registrations`

**Used by**: Browse page to fetch all registrations

**Query parameters used**:
- `status=Approved` - for non-admin users to see only approved registrations
- `limit=20` - for pagination (20 items per page)
- `offset=0, 20, 40, ...` - for pagination
- `search=term` - for search/filter functionality

**Example**:
```bash
# Non-admin user: Get first page of approved registrations
curl "http://localhost:8000/registrations?status=Approved&limit=20&offset=0" \
  -H "Authorization: Bearer $TOKEN"

# Admin user: Get all registrations (no status filter)
curl "http://localhost:8000/registrations?limit=20&offset=0" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Search for "openai"
curl "http://localhost:8000/registrations?search=openai&limit=20" \
  -H "Authorization: Bearer $TOKEN"
```

### GET `/registrations/{registration_id}`

**Used by**: Detailed view modal to fetch full registration details (including submitter/approver info)

**Example**:
```bash
curl "http://localhost:8000/registrations/abc-123-def-456" \
  -H "Authorization: Bearer $TOKEN"
```

---

## OpenAPI Schema Snippets

### For `/registrations/by-url` endpoint

```yaml
/registrations/by-url:
  get:
    tags:
      - registrations
    summary: Query registration by endpoint URL
    description: Retrieve registration details by exact endpoint URL match. Used for CI/CD compliance checks.
    operationId: get_registration_by_url
    security:
      - BearerAuth: []
    parameters:
      - name: endpoint_url
        in: query
        required: true
        schema:
          type: string
          format: uri
          example: "https://api.example.com/mcp"
        description: Exact endpoint URL to query (URL-encoded)
    responses:
      '200':
        description: Registration found
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RegistrationResponse'
      '401':
        $ref: '#/components/responses/UnauthorizedError'
      '404':
        description: No registration found for this endpoint URL
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ErrorResponse'
```

### For `/audit-logs` endpoint

```yaml
/audit-logs:
  get:
    tags:
      - audit
    summary: Query audit logs
    description: Retrieve audit log entries with filtering. Admin only.
    operationId: get_audit_logs
    security:
      - BearerAuth: []
    parameters:
      - name: registration_id
        in: query
        schema:
          type: string
          format: uuid
      - name: user_id
        in: query
        schema:
          type: string
          format: uuid
      - name: action
        in: query
        schema:
          type: string
          enum: [Created, Approved, Rejected, Updated, Deleted]
      - name: from
        in: query
        schema:
          type: string
          format: date-time
          example: "2025-11-01T00:00:00Z"
      - name: to
        in: query
        schema:
          type: string
          format: date-time
          example: "2025-11-30T23:59:59Z"
      - name: limit
        in: query
        schema:
          type: integer
          minimum: 1
          maximum: 200
          default: 50
      - name: offset
        in: query
        schema:
          type: integer
          minimum: 0
          default: 0
    responses:
      '200':
        description: Audit log results
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/AuditLogListResponse'
      '400':
        $ref: '#/components/responses/BadRequestError'
      '401':
        $ref: '#/components/responses/UnauthorizedError'
      '403':
        $ref: '#/components/responses/ForbiddenError'
```

### Schemas

```yaml
components:
  schemas:
    AuditLogResponse:
      type: object
      required:
        - log_id
        - registration_id
        - user_id
        - action
        - timestamp
      properties:
        log_id:
          type: string
          format: uuid
        registration_id:
          type: string
          format: uuid
        user_id:
          type: string
          format: uuid
        user_email:
          type: string
          format: email
          nullable: true
        user_display_name:
          type: string
          nullable: true
        action:
          type: string
          enum: [Created, Approved, Rejected, Updated, Deleted]
        previous_status:
          type: string
          nullable: true
        new_status:
          type: string
          nullable: true
        metadata:
          type: object
          additionalProperties: true
          nullable: true
        timestamp:
          type: string
          format: date-time
    
    AuditLogListResponse:
      type: object
      required:
        - total
        - limit
        - offset
        - results
      properties:
        total:
          type: integer
          description: Total number of audit logs matching filters
        limit:
          type: integer
          description: Maximum results per page
        offset:
          type: integer
          description: Number of results skipped
        results:
          type: array
          items:
            $ref: '#/components/schemas/AuditLogResponse'
```

---

## Summary

**New endpoints**: 2
- `GET /registrations/by-url` - Query by endpoint URL
- `GET /audit-logs` - Query audit logs (admin only)

**Existing endpoints used**: 2
- `GET /registrations` - Browse page list
- `GET /registrations/{id}` - Detailed view

**Performance targets**:
- Query by URL: <200ms (95th percentile)
- Audit logs: <1 second (even with 10,000+ entries)

**Security**:
- All endpoints require authentication
- `/audit-logs` requires admin privileges
- Authorization enforced via existing dependencies (`get_current_user`, `require_admin`)
