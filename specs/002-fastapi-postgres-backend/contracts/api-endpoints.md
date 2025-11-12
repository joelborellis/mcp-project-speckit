# API Endpoints Contract

**Feature**: 002-fastapi-postgres-backend  
**Date**: 2025-11-11  
**Base URL**: `http://localhost:8000` (development) | `https://api.example.com` (production)

## Overview

This document defines all REST API endpoints for the MCP Registry backend. All endpoints except `/health` require a valid Microsoft Entra ID token in the `Authorization` header.

### Authentication

All authenticated endpoints require:
```
Authorization: Bearer <entra_id_access_token>
```

The backend validates the token on every request and extracts user identity.

### Response Format

**Success responses** (2xx):
```json
{
  "field1": "value",
  "field2": "value"
}
```

**Error responses** (4xx, 5xx):
```json
{
  "detail": "Human-readable error message"
}
```

---

## Endpoints

### Health Check

#### `GET /health`

Health check endpoint for monitoring and load balancers.

**Authentication**: None required

**Response**: `200 OK`
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-11-11T10:00:00Z"
}
```

**Response**: `503 Service Unavailable` (if database connection failed)
```json
{
  "status": "unhealthy",
  "database": "disconnected",
  "detail": "Database connection pool exhausted"
}
```

---

### User Management

#### `POST /users`

Create or update a user from Entra ID authentication. Called automatically after token validation to ensure user exists in database.

**Authentication**: Required

**Request Body**: None (user info extracted from token)

**Response**: `200 OK` or `201 Created`
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "entra_id": "user-entra-id-from-token",
  "email": "user@example.com",
  "display_name": "John Doe",
  "is_admin": false,
  "created_at": "2025-11-11T10:00:00Z",
  "updated_at": "2025-11-11T10:00:00Z"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or expired token
- `500 Internal Server Error`: Database error

---

#### `GET /users/{user_id}`

Get user details by user_id.

**Authentication**: Required

**Path Parameters**:
- `user_id` (UUID): User's internal ID

**Response**: `200 OK`
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "entra_id": "user-entra-id",
  "email": "user@example.com",
  "display_name": "John Doe",
  "is_admin": false,
  "created_at": "2025-11-11T10:00:00Z",
  "updated_at": "2025-11-11T10:00:00Z"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or expired token
- `404 Not Found`: User not found
- `500 Internal Server Error`: Database error

---

#### `GET /users/me`

Get current authenticated user's details.

**Authentication**: Required

**Response**: `200 OK`
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "entra_id": "user-entra-id",
  "email": "user@example.com",
  "display_name": "John Doe",
  "is_admin": false,
  "created_at": "2025-11-11T10:00:00Z",
  "updated_at": "2025-11-11T10:00:00Z"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or expired token
- `500 Internal Server Error`: Database error

---

### Registration Management

#### `POST /registrations`

Create a new MCP endpoint registration (status: Pending).

**Authentication**: Required

**Request Body**:
```json
{
  "endpoint_url": "https://mcp.example.com",
  "endpoint_name": "Example MCP Server",
  "description": "Optional description of what this endpoint provides",
  "owner_contact": "owner@example.com",
  "available_tools": [
    {"name": "search", "description": "Search capability"},
    {"name": "analyze"}
  ]
}
```

**Validation Rules**:
- `endpoint_url`: Required, valid URL format, must be unique
- `endpoint_name`: Required, 3-200 characters
- `description`: Optional, max 1000 characters
- `owner_contact`: Required, email format preferred
- `available_tools`: Required array (can be empty), each tool must have `name` field

**Response**: `201 Created`
```json
{
  "registration_id": "660e8400-e29b-41d4-a716-446655440000",
  "endpoint_url": "https://mcp.example.com",
  "endpoint_name": "Example MCP Server",
  "description": "Optional description",
  "owner_contact": "owner@example.com",
  "available_tools": [
    {"name": "search", "description": "Search capability"},
    {"name": "analyze"}
  ],
  "status": "Pending",
  "submitter_id": "550e8400-e29b-41d4-a716-446655440000",
  "approver_id": null,
  "submitted_at": "2025-11-11T10:00:00Z",
  "approved_at": null,
  "created_at": "2025-11-11T10:00:00Z",
  "updated_at": "2025-11-11T10:00:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid request body
- `401 Unauthorized`: Invalid or expired token
- `409 Conflict`: Endpoint URL already exists
- `422 Unprocessable Entity`: Validation errors
- `500 Internal Server Error`: Database error

---

#### `GET /registrations`

Get all registrations with optional filtering.

**Authentication**: Required

**Query Parameters** (all optional):
- `status` (string): Filter by status (`Pending`, `Approved`, `Rejected`)
- `submitter_id` (UUID): Filter by submitter
- `search` (string): Search in endpoint_name and owner_contact
- `limit` (integer): Max results (default: 100, max: 500)
- `offset` (integer): Pagination offset (default: 0)

**Example**: `GET /registrations?status=Approved&search=example&limit=50`

**Response**: `200 OK`
```json
{
  "total": 2,
  "limit": 50,
  "offset": 0,
  "results": [
    {
      "registration_id": "660e8400-e29b-41d4-a716-446655440000",
      "endpoint_url": "https://mcp.example.com",
      "endpoint_name": "Example MCP Server",
      "description": "Optional description",
      "owner_contact": "owner@example.com",
      "available_tools": [{"name": "search"}],
      "status": "Approved",
      "submitter_id": "550e8400-e29b-41d4-a716-446655440000",
      "approver_id": "770e8400-e29b-41d4-a716-446655440000",
      "submitted_at": "2025-11-11T09:00:00Z",
      "approved_at": "2025-11-11T09:30:00Z",
      "created_at": "2025-11-11T09:00:00Z",
      "updated_at": "2025-11-11T09:30:00Z"
    }
  ]
}
```

**Error Responses**:
- `400 Bad Request`: Invalid query parameters
- `401 Unauthorized`: Invalid or expired token
- `500 Internal Server Error`: Database error

---

#### `GET /registrations/{registration_id}`

Get a specific registration by ID.

**Authentication**: Required

**Path Parameters**:
- `registration_id` (UUID): Registration's internal ID

**Response**: `200 OK`
```json
{
  "registration_id": "660e8400-e29b-41d4-a716-446655440000",
  "endpoint_url": "https://mcp.example.com",
  "endpoint_name": "Example MCP Server",
  "description": "Optional description",
  "owner_contact": "owner@example.com",
  "available_tools": [{"name": "search"}],
  "status": "Approved",
  "submitter_id": "550e8400-e29b-41d4-a716-446655440000",
  "approver_id": "770e8400-e29b-41d4-a716-446655440000",
  "submitted_at": "2025-11-11T09:00:00Z",
  "approved_at": "2025-11-11T09:30:00Z",
  "created_at": "2025-11-11T09:00:00Z",
  "updated_at": "2025-11-11T09:30:00Z"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or expired token
- `404 Not Found`: Registration not found
- `500 Internal Server Error`: Database error

---

#### `PATCH /registrations/{registration_id}/status`

Update registration status (admin only). Used for approving or rejecting registrations.

**Authentication**: Required (admin only)

**Path Parameters**:
- `registration_id` (UUID): Registration's internal ID

**Request Body**:
```json
{
  "status": "Approved"
}
```

**Validation Rules**:
- `status`: Required, must be `Approved` or `Rejected`
- Only admins (`is_admin = true`) can call this endpoint
- Only registrations with status `Pending` can be updated

**Response**: `200 OK`
```json
{
  "registration_id": "660e8400-e29b-41d4-a716-446655440000",
  "endpoint_url": "https://mcp.example.com",
  "endpoint_name": "Example MCP Server",
  "status": "Approved",
  "approver_id": "770e8400-e29b-41d4-a716-446655440000",
  "approved_at": "2025-11-11T10:00:00Z",
  "updated_at": "2025-11-11T10:00:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid status value or registration not in Pending state
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: User is not an admin
- `404 Not Found`: Registration not found
- `500 Internal Server Error`: Database error

---

#### `DELETE /registrations/{registration_id}`

Delete a registration (admin only). Removes the registration from the database.

**Authentication**: Required (admin only)

**Path Parameters**:
- `registration_id` (UUID): Registration's internal ID

**Response**: `204 No Content` (successful deletion, no body)

**Error Responses**:
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: User is not an admin
- `404 Not Found`: Registration not found
- `500 Internal Server Error`: Database error

---

#### `GET /registrations/my`

Get current user's own registrations.

**Authentication**: Required

**Query Parameters** (optional):
- `status` (string): Filter by status
- `limit` (integer): Max results (default: 100)
- `offset` (integer): Pagination offset (default: 0)

**Response**: `200 OK`
```json
{
  "total": 5,
  "limit": 100,
  "offset": 0,
  "results": [
    {
      "registration_id": "660e8400-e29b-41d4-a716-446655440000",
      "endpoint_url": "https://mcp.example.com",
      "endpoint_name": "My MCP Server",
      "status": "Pending",
      "submitted_at": "2025-11-11T10:00:00Z"
    }
  ]
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid or expired token
- `500 Internal Server Error`: Database error

---

## Error Response Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PATCH request |
| 201 | Created | Successful POST request |
| 204 | No Content | Successful DELETE request |
| 400 | Bad Request | Invalid request format or parameters |
| 401 | Unauthorized | Missing, invalid, or expired token |
| 403 | Forbidden | Valid user but insufficient permissions (not admin) |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate endpoint_url or invalid state transition |
| 422 | Unprocessable Entity | Validation errors on request body |
| 500 | Internal Server Error | Database error or unexpected server error |
| 503 | Service Unavailable | Health check failed (database down) |

---

## CORS Configuration

The API supports CORS with the following configuration:

```python
allow_origins = ["http://localhost:5173"]  # Vite dev server (development)
# Production: ["https://frontend.example.com"]
allow_credentials = True
allow_methods = ["*"]
allow_headers = ["*"]
```

**Security Note**: In production, restrict `allow_origins` to specific frontend domain(s).

---

## Rate Limiting (Future Enhancement)

Not implemented in MVP. Can add later with middleware:
- Per-user rate limits (e.g., 100 requests/minute)
- Per-IP rate limits (e.g., 1000 requests/hour)
- Admin endpoints have separate (higher) limits

---

## Versioning

No API versioning in MVP. Future breaking changes will introduce `/api/v2/` prefix while maintaining `/api/v1/` for backward compatibility.

---

## OpenAPI Documentation

FastAPI automatically generates OpenAPI (Swagger) documentation at:
- `/docs` - Swagger UI (interactive documentation)
- `/redoc` - ReDoc (alternative documentation UI)
- `/openapi.json` - OpenAPI schema (JSON format)

These endpoints are enabled in development, can be disabled in production for security.

---

## Testing the API

### Using curl

**Get health status**:
```bash
curl http://localhost:8000/health
```

**Create registration** (with Entra ID token):
```bash
curl -X POST http://localhost:8000/registrations \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "endpoint_url": "https://mcp.example.com",
    "endpoint_name": "Test Server",
    "owner_contact": "test@example.com",
    "available_tools": [{"name": "search"}]
  }'
```

**Get all approved registrations**:
```bash
curl http://localhost:8000/registrations?status=Approved \
  -H "Authorization: Bearer <your_token>"
```

**Approve registration** (admin only):
```bash
curl -X PATCH http://localhost:8000/registrations/{id}/status \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"status": "Approved"}'
```

---

## Frontend Integration

The frontend `api.service.ts` should wrap these endpoints with:
1. Base URL configuration (environment variable)
2. Authorization header injection (from MSAL token)
3. Error handling and response parsing
4. TypeScript interfaces for request/response types

Example TypeScript interface:
```typescript
interface Registration {
  registration_id: string;
  endpoint_url: string;
  endpoint_name: string;
  description?: string;
  owner_contact: string;
  available_tools: Array<{name: string; description?: string}>;
  status: 'Pending' | 'Approved' | 'Rejected';
  submitter_id: string;
  approver_id?: string;
  submitted_at: string;
  approved_at?: string;
  created_at: string;
  updated_at: string;
}
```
