# Data Model: FastAPI Backend with PostgreSQL Database

**Feature**: 002-fastapi-postgres-backend  
**Date**: 2025-11-11  
**Database**: PostgreSQL (Azure Database for PostgreSQL)

## Overview

This document defines the data entities, relationships, validation rules, and state transitions for the MCP Registry backend. The model supports user management, MCP endpoint registration workflows, and optional audit logging.

---

## Entity Definitions

### 1. User

Represents an authenticated individual from Microsoft Entra ID who can submit registrations or perform admin actions.

**Table Name**: `users`

**Attributes**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| user_id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Internal unique identifier |
| entra_id | TEXT | UNIQUE, NOT NULL | External ID from Microsoft Entra ID (subject claim from JWT) |
| email | TEXT | NOT NULL | User's email address from Entra ID |
| display_name | TEXT | NULL | User's display name from Entra ID |
| is_admin | BOOLEAN | DEFAULT FALSE, NOT NULL | Admin privilege flag (determined by Entra ID group membership) |
| created_at | TIMESTAMPTZ | DEFAULT NOW(), NOT NULL | Record creation timestamp |
| updated_at | TIMESTAMPTZ | DEFAULT NOW(), NOT NULL | Last update timestamp |

**Indexes**:
- `idx_users_entra_id` on `entra_id` (unique, for fast lookups during authentication)
- Primary key index on `user_id` (automatic)

**Validation Rules**:
- `email` must be valid email format (validated by Pydantic schema)
- `entra_id` must be unique (enforced by database constraint)
- `display_name` can be NULL (not all Entra ID accounts have display names)

**Relationships**:
- One user can submit many registrations (1:N with Registration via submitter_id)
- One user can approve many registrations (1:N with Registration via approver_id)

---

### 2. Registration

Represents a registered MCP endpoint with metadata and approval workflow state.

**Table Name**: `registrations`

**Attributes**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| registration_id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Internal unique identifier |
| endpoint_url | TEXT | UNIQUE, NOT NULL | MCP endpoint URL (e.g., https://mcp.example.com) |
| endpoint_name | TEXT | NOT NULL | Human-readable name for the endpoint |
| description | TEXT | NULL | Optional description of what the endpoint provides |
| owner_contact | TEXT | NOT NULL | Contact information for endpoint owner (email or team) |
| available_tools | JSONB | NOT NULL, DEFAULT '[]'::jsonb | Array of available tools/capabilities (JSON format) |
| status | TEXT | NOT NULL, CHECK (status IN ('Pending', 'Approved', 'Rejected')) | Current approval status |
| submitter_id | UUID | FOREIGN KEY → users(user_id), NOT NULL | User who submitted the registration |
| approver_id | UUID | FOREIGN KEY → users(user_id), NULL | Admin who approved/rejected (NULL if pending) |
| submitted_at | TIMESTAMPTZ | DEFAULT NOW(), NOT NULL | When registration was submitted |
| approved_at | TIMESTAMPTZ | NULL | When registration was approved/rejected (NULL if pending) |
| created_at | TIMESTAMPTZ | DEFAULT NOW(), NOT NULL | Record creation timestamp |
| updated_at | TIMESTAMPTZ | DEFAULT NOW(), NOT NULL | Last update timestamp |

**Indexes**:
- `idx_registrations_endpoint_url` on `endpoint_url` (unique, prevents duplicates)
- `idx_registrations_status` on `status` (for filtering by status)
- `idx_registrations_submitter_id` on `submitter_id` (for user's registrations view)
- `idx_registrations_created_at` on `created_at` (for sorting by submission date)
- Primary key index on `registration_id` (automatic)

**Validation Rules**:
- `endpoint_url` must be valid URL format (validated by Pydantic schema)
- `endpoint_url` must be unique (enforced by database constraint)
- `endpoint_name` must be non-empty string (min length 3, max 200)
- `owner_contact` must be non-empty string (email format preferred)
- `available_tools` must be valid JSONB array (can be empty array)
- `status` must be one of: 'Pending', 'Approved', 'Rejected' (CHECK constraint)
- `approver_id` must be NULL when status is 'Pending'
- `approved_at` must be NULL when status is 'Pending'
- `approver_id` and `approved_at` must both be NOT NULL when status is 'Approved' or 'Rejected'

**Relationships**:
- Each registration belongs to one submitter (N:1 with User via submitter_id)
- Each registration optionally belongs to one approver (N:1 with User via approver_id)
- Each registration can have many audit log entries (1:N with AuditLog)

**State Transitions**:
```
Pending → Approved (by admin)
Pending → Rejected (by admin)
(No transitions from Approved or Rejected in MVP - immutable once decided)
```

**available_tools JSONB Structure**:
```json
[
  {
    "name": "search",
    "description": "Search capability",
    "version": "1.0" 
  },
  {
    "name": "analyze"
  }
]
```
- Each tool is an object with at minimum a `name` field
- Optional `description` and `version` fields for future extensibility
- Frontend sends array of tool names, backend stores as JSONB for queryability

---

### 3. AuditLog (Optional - Phase 2)

Represents changes to registrations for compliance and troubleshooting. Optional for MVP but included in schema for future use.

**Table Name**: `audit_log`

**Attributes**:

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| log_id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Internal unique identifier |
| registration_id | UUID | FOREIGN KEY → registrations(registration_id), NOT NULL | Registration that was modified |
| user_id | UUID | FOREIGN KEY → users(user_id), NOT NULL | User who performed the action |
| action | TEXT | NOT NULL, CHECK (action IN ('Created', 'Approved', 'Rejected', 'Updated', 'Deleted')) | Type of action performed |
| previous_status | TEXT | NULL | Status before change (NULL for Create action) |
| new_status | TEXT | NULL | Status after change |
| metadata | JSONB | NULL | Additional context (e.g., reason for rejection, fields changed) |
| timestamp | TIMESTAMPTZ | DEFAULT NOW(), NOT NULL | When the action occurred |

**Indexes**:
- `idx_audit_log_registration_id` on `registration_id` (for audit trail queries)
- `idx_audit_log_timestamp` on `timestamp` (for time-based queries)
- Primary key index on `log_id` (automatic)

**Validation Rules**:
- `action` must be one of the defined action types (CHECK constraint)
- `metadata` must be valid JSONB if present

**Relationships**:
- Each audit log entry belongs to one registration (N:1 with Registration)
- Each audit log entry belongs to one user (N:1 with User)

---

## Entity Relationship Diagram

```
┌─────────────────┐
│     User        │
│─────────────────│
│ user_id (PK)    │
│ entra_id (UQ)   │
│ email           │
│ display_name    │
│ is_admin        │
│ created_at      │
│ updated_at      │
└─────────────────┘
         │
         │ 1:N (submitter)
         ├───────────────────────────┐
         │                           │
         │ 1:N (approver)            │
         │                           │
         ▼                           ▼
┌─────────────────────────┐  ┌───────────────┐
│    Registration         │  │   AuditLog    │
│─────────────────────────│  │───────────────│
│ registration_id (PK)    │  │ log_id (PK)   │
│ endpoint_url (UQ)       │  │ registration_ │
│ endpoint_name           │  │   id (FK)     │
│ description             │  │ user_id (FK)  │
│ owner_contact           │  │ action        │
│ available_tools (JSONB) │  │ previous_     │
│ status                  │  │   status      │
│ submitter_id (FK)       │  │ new_status    │
│ approver_id (FK)        │──▶│ metadata      │
│ submitted_at            │  │ timestamp     │
│ approved_at             │  └───────────────┘
│ created_at              │
│ updated_at              │
└─────────────────────────┘
```

---

## Validation Rules Summary

### User Entity
- ✅ `entra_id` uniqueness enforced by database
- ✅ `email` format validated by Pydantic schema
- ✅ `is_admin` defaults to `false`

### Registration Entity
- ✅ `endpoint_url` uniqueness enforced by database (prevents duplicates including race conditions)
- ✅ `endpoint_url` format validated by Pydantic schema
- ✅ `status` restricted to enum values by CHECK constraint
- ✅ `available_tools` stored as JSONB for flexibility and queryability
- ✅ State consistency: `approver_id` and `approved_at` NULL when Pending
- ✅ Foreign key constraints maintain referential integrity

### AuditLog Entity
- ✅ `action` restricted to enum values by CHECK constraint
- ✅ Foreign keys cascade appropriately (consider ON DELETE CASCADE for audit_log)

---

## Data Integrity Constraints

### Database-Level Constraints
1. **UNIQUE constraints**: Prevent duplicate `entra_id` and `endpoint_url`
2. **FOREIGN KEY constraints**: Maintain referential integrity between tables
3. **CHECK constraints**: Enforce enum values for `status` and `action`
4. **NOT NULL constraints**: Ensure required fields always have values
5. **DEFAULT values**: Provide sensible defaults (timestamps, UUIDs, booleans)

### Application-Level Validation (Pydantic)
1. **URL format**: `endpoint_url` must match URL regex
2. **Email format**: `email` and `owner_contact` must match email regex
3. **String lengths**: Min/max length validation for names and descriptions
4. **JSONB structure**: `available_tools` must be valid JSON array
5. **Business logic**: Status transitions enforced in service layer

---

## State Transitions

### Registration Status Lifecycle

```
┌──────────┐
│ Pending  │ ◀── Initial state (on creation)
└────┬─────┘
     │
     ├──────────┐
     │          │
     ▼          ▼
┌──────────┐ ┌──────────┐
│ Approved │ │ Rejected │ ◀── Terminal states (immutable in MVP)
└──────────┘ └──────────┘
```

**Transition Rules**:
1. New registrations created with `status = 'Pending'`
2. Only admins (`is_admin = true`) can approve/reject
3. Approval sets: `status = 'Approved'`, `approver_id = <admin_user_id>`, `approved_at = NOW()`
4. Rejection sets: `status = 'Rejected'`, `approver_id = <admin_user_id>`, `approved_at = NOW()`
5. No transitions out of 'Approved' or 'Rejected' in MVP (future: may add "Resubmit" workflow)

**Audit Trail**:
- Each status transition creates an audit log entry (if audit_log table exists)
- `action` = 'Approved' or 'Rejected'
- `previous_status` = 'Pending'
- `new_status` = 'Approved' or 'Rejected'

---

## Query Patterns

### Common Queries

1. **Get all approved registrations** (for main registry view):
   ```sql
   SELECT * FROM registrations WHERE status = 'Approved' ORDER BY created_at DESC;
   ```

2. **Get pending registrations** (for admin approval queue):
   ```sql
   SELECT r.*, u.email as submitter_email, u.display_name as submitter_name
   FROM registrations r
   JOIN users u ON r.submitter_id = u.user_id
   WHERE r.status = 'Pending'
   ORDER BY r.submitted_at ASC;
   ```

3. **Get user's own registrations** (for "My Registrations" view):
   ```sql
   SELECT * FROM registrations 
   WHERE submitter_id = $1 
   ORDER BY created_at DESC;
   ```

4. **Search registrations** (by name or owner):
   ```sql
   SELECT * FROM registrations 
   WHERE status = 'Approved' 
   AND (endpoint_name ILIKE $1 OR owner_contact ILIKE $1)
   ORDER BY created_at DESC;
   ```

5. **Get or create user from Entra ID**:
   ```sql
   INSERT INTO users (entra_id, email, display_name, is_admin)
   VALUES ($1, $2, $3, $4)
   ON CONFLICT (entra_id) DO UPDATE
   SET email = EXCLUDED.email,
       display_name = EXCLUDED.display_name,
       updated_at = NOW()
   RETURNING *;
   ```

---

## Performance Considerations

### Indexes Strategy
- **Primary keys**: Automatic B-tree indexes (user_id, registration_id, log_id)
- **Unique constraints**: Create indexes for fast lookups (entra_id, endpoint_url)
- **Foreign keys**: Index for efficient joins (submitter_id, approver_id)
- **Filter columns**: Index status for WHERE clauses in common queries
- **Sort columns**: Index created_at for ORDER BY in list views

### JSONB Performance
- `available_tools` stored as JSONB allows GIN indexing (future optimization)
- Can query JSONB with operators: `available_tools @> '["search"]'::jsonb`
- For MVP, no JSONB indexes needed (small dataset)

### Connection Pooling
- Pool size: 10-20 connections for initial deployment
- Prevents connection exhaustion under concurrent load
- asyncpg pool handles connection lifecycle automatically

---

## Migration Strategy

### Initial Schema (Phase 1)
1. Create `users` table with indexes
2. Create `registrations` table with foreign keys and indexes
3. Optionally create `audit_log` table (can defer to Phase 2)

### Future Migrations
- Add columns: `ALTER TABLE ... ADD COLUMN ... `
- Add indexes: `CREATE INDEX CONCURRENTLY ... `
- Add constraints: `ALTER TABLE ... ADD CONSTRAINT ... `
- All DDL wrapped in idempotent checks (IF NOT EXISTS, IF EXISTS)

---

## Data Seeding (Development Only)

For development/testing, seed with:
1. Admin user with known `entra_id` for testing admin flows
2. Regular user for testing submission flows
3. Sample approved registrations for browsing
4. Sample pending registrations for approval testing

**Note**: Production database starts empty; users created on first login via Entra ID.

---

## Next Steps

1. ✅ Data model defined
2. → Generate database schema SQL in `/contracts/database-schema.sql`
3. → Define API contracts in `/contracts/api-endpoints.md`
4. → Create quickstart guide in `quickstart.md`
