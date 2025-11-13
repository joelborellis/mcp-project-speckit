# Data Model: Browse Functionality, Approval Status Query API, and Audit Logging

**Feature**: 003-browse-audit-query  
**Date**: 2025-11-12  
**Status**: Complete

## Overview

This feature leverages existing database schema from feature 002. **No new tables or schema changes required**. This document describes how existing entities are used and what service-layer enhancements are needed.

## Database Schema (Existing)

### Table: `registrations`

**Source**: `backend/scripts/db/init_schema.sql` (feature 002)  
**Status**: No changes required

```sql
CREATE TABLE registrations (
    registration_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    endpoint_url TEXT NOT NULL UNIQUE,
    endpoint_name TEXT NOT NULL CHECK (char_length(endpoint_name) >= 3 AND char_length(endpoint_name) <= 200),
    description TEXT,
    owner_contact TEXT NOT NULL,
    available_tools JSONB NOT NULL DEFAULT '[]'::jsonb,
    status TEXT NOT NULL CHECK (status IN ('Pending', 'Approved', 'Rejected')) DEFAULT 'Pending',
    submitter_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    approver_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Existing indexes used by this feature:
CREATE UNIQUE INDEX idx_registrations_endpoint_url ON registrations(endpoint_url);
CREATE INDEX idx_registrations_status ON registrations(status);
CREATE INDEX idx_registrations_submitter_id ON registrations(submitter_id);
CREATE INDEX idx_registrations_created_at ON registrations(created_at DESC);
```

**Usage in this feature**:
- **Browse page**: Query all registrations, filter by status (admin sees all, users see only Approved)
- **Query API**: Fast lookup by endpoint_url using unique index
- No schema changes needed - all fields already support requirements

### Table: `audit_log`

**Source**: `backend/scripts/db/init_schema.sql` (feature 002)  
**Status**: Needs service implementation (table exists, but not currently used)

```sql
CREATE TABLE audit_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    registration_id UUID NOT NULL REFERENCES registrations(registration_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    action TEXT NOT NULL CHECK (action IN ('Created', 'Approved', 'Rejected', 'Updated', 'Deleted')),
    previous_status TEXT,
    new_status TEXT,
    metadata JSONB,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Existing indexes:
CREATE INDEX idx_audit_log_registration_id ON audit_log(registration_id);
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp DESC);
```

**Usage in this feature**:
- **Automatic logging**: Every registration modification creates audit log entry
- **Admin queries**: GET `/audit-logs` endpoint for compliance/troubleshooting
- **Retention**: Audit logs preserved even after registration deletion (ON DELETE CASCADE only for user, not registration)

**Note**: Schema comment says "ON DELETE CASCADE" but this is only for user_id. When a registration is deleted, audit logs are retained (FR-023).

### Table: `users`

**Source**: `backend/scripts/db/init_schema.sql` (feature 002)  
**Status**: No changes required

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entra_id TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL,
    display_name TEXT,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

**Usage in this feature**:
- **Authorization**: Browse page checks is_admin to show all statuses vs. approved only
- **Audit logs**: user_id foreign key links actions to users
- **Detailed view**: Fetch submitter and approver display names for registration details

## Entity Models (Backend)

### AuditLog (Pydantic Models)

**Source**: `backend/src/models/audit_log.py` (already exists from feature 002)

```python
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime

class AuditAction(str, Enum):
    """Types of actions that can be audited."""
    CREATED = "Created"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    UPDATED = "Updated"
    DELETED = "Deleted"

class AuditLog(BaseModel):
    """Full audit log entry (database representation)"""
    log_id: UUID
    registration_id: UUID
    user_id: UUID
    action: AuditAction
    previous_status: Optional[str] = None
    new_status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime

class AuditLogCreate(BaseModel):
    """Schema for creating audit log entries"""
    registration_id: UUID
    user_id: UUID
    action: AuditAction
    previous_status: Optional[str] = None
    new_status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
```

**New schemas needed** (`backend/src/schemas/audit_log.py`):

```python
class AuditLogResponse(BaseModel):
    """API response for audit log queries"""
    log_id: UUID
    registration_id: UUID
    user_id: UUID
    user_email: Optional[str] = None  # Joined from users table
    user_display_name: Optional[str] = None  # Joined from users table
    action: AuditAction
    previous_status: Optional[str] = None
    new_status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime

class AuditLogListResponse(BaseModel):
    """Paginated audit log results"""
    total: int
    limit: int
    offset: int
    results: List[AuditLogResponse]
```

### Registration (Pydantic Models)

**Source**: `backend/src/models/registration.py` (already exists)

No changes needed. Existing models support all Browse and Query API requirements.

## Service Layer

### AuditService (NEW)

**File**: `backend/src/services/audit_service.py`

```python
class AuditService:
    """Service for creating and querying audit logs"""
    
    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn
    
    async def log_action(
        self,
        registration_id: UUID,
        user_id: UUID,
        action: AuditAction,
        previous_status: Optional[str] = None,
        new_status: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """Create audit log entry (called within transaction)"""
        # INSERT INTO audit_log ... RETURNING *
        pass
    
    async def get_audit_logs(
        self,
        registration_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        action: Optional[AuditAction] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Query audit logs with filters and pagination"""
        # SELECT with JOINs to users table
        # Return {total, limit, offset, results}
        pass
```

### RegistrationService (EXTEND)

**File**: `backend/src/services/registration_service.py` (already exists)

**Changes needed**:
1. Add `AuditService` instance
2. Wrap operations in transactions
3. Call `audit_service.log_action()` after each CRUD operation

```python
class RegistrationService:
    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn
        self.audit_service = AuditService(conn)  # NEW
    
    async def create_registration(self, data: RegistrationCreate, submitter_id: UUID):
        async with self.conn.transaction():  # WRAP in transaction
            registration = await self._insert_registration(...)
            
            # NEW: Log creation
            await self.audit_service.log_action(
                registration_id=registration.registration_id,
                user_id=submitter_id,
                action=AuditAction.CREATED,
                new_status="Pending",
                metadata={"initial_values": data.dict()}
            )
            
            return registration
    
    async def update_registration_status(
        self, registration_id, new_status, approver_id, reason=None
    ):
        async with self.conn.transaction():  # WRAP in transaction
            old_registration = await self.get_registration_by_id(registration_id)
            updated = await self._update_status_in_db(...)
            
            # NEW: Log status change
            action = AuditAction.APPROVED if new_status == "Approved" else AuditAction.REJECTED
            await self.audit_service.log_action(
                registration_id=registration_id,
                user_id=approver_id,
                action=action,
                previous_status=old_registration.status,
                new_status=new_status,
                metadata={"reason": reason} if reason else None
            )
            
            return updated
    
    async def delete_registration(self, registration_id: UUID, deleter_id: UUID):
        async with self.conn.transaction():
            registration = await self.get_registration_by_id(registration_id)
            
            # NEW: Log deletion BEFORE deleting registration
            await self.audit_service.log_action(
                registration_id=registration_id,
                user_id=deleter_id,
                action=AuditAction.DELETED,
                previous_status=registration.status,
                metadata={"final_state": registration.dict()}
            )
            
            # Now delete (audit log survives due to separate FK)
            await self._delete_from_db(registration_id)
            return True
    
    async def get_by_url(self, endpoint_url: str) -> Optional[Registration]:
        """NEW: Query by endpoint URL for /registrations/by-url API"""
        # SELECT * FROM registrations WHERE endpoint_url = $1
        pass
```

## Frontend Types

### AuditLog Types (NEW)

**File**: `frontend/src/types/audit-log.types.ts`

```typescript
export enum AuditAction {
  Created = 'Created',
  Approved = 'Approved',
  Rejected = 'Rejected',
  Updated = 'Updated',
  Deleted = 'Deleted'
}

export interface AuditLog {
  log_id: string;
  registration_id: string;
  user_id: string;
  user_email?: string;
  user_display_name?: string;
  action: AuditAction;
  previous_status?: string;
  new_status?: string;
  metadata?: Record<string, any>;
  timestamp: string; // ISO 8601 format
}

export interface AuditLogListResponse {
  total: number;
  limit: number;
  offset: number;
  results: AuditLog[];
}
```

### Registration Types (EXISTING)

**File**: `frontend/src/types/registration.types.ts`

No changes needed. Existing types support Browse page requirements.

## Data Flow

### Browse Page Flow

```
User → BrowsePage.tsx
  ↓ useEffect on mount
  ↓ calls api.service.getRegistrations(token, { status: user.isAdmin ? undefined : 'Approved' })
  ↓
Backend → GET /registrations?status=Approved (or no filter for admin)
  ↓ RegistrationService.get_registrations()
  ↓ SQL: SELECT * FROM registrations WHERE status = $1 ORDER BY created_at DESC LIMIT 20 OFFSET 0
  ↓
  ↓ returns RegistrationListResponse { total, results }
  ↓
Frontend → setState(registrations)
  ↓ render BrowseCard for each registration
  ↓ user clicks card
  ↓ show RegistrationDetailModal
```

### Query API Flow

```
CI/CD Tool → GET /registrations/by-url?endpoint_url=https://api.example.com/mcp
  ↓ auth check (requires valid token)
  ↓ RegistrationService.get_by_url(endpoint_url)
  ↓ SQL: SELECT * FROM registrations WHERE endpoint_url = $1 (uses unique index)
  ↓
  ↓ if found: return RegistrationResponse
  ↓ if not found: raise HTTPException(404)
```

### Audit Logging Flow

```
Admin → PATCH /registrations/{id}/status { status: "Approved", reason: "..." }
  ↓ require_admin dependency checks user
  ↓ RegistrationService.update_registration_status()
  ↓
  ↓ BEGIN TRANSACTION
  ↓   UPDATE registrations SET status = $1, approver_id = $2, approved_at = NOW() WHERE registration_id = $3
  ↓   AuditService.log_action(registration_id, user_id, APPROVED, "Pending", "Approved", {"reason": "..."})
  ↓     INSERT INTO audit_log (...) VALUES (...)
  ↓ COMMIT TRANSACTION
  ↓
  ↓ return updated RegistrationResponse
```

### Audit Log Query Flow

```
Admin → GET /audit-logs?registration_id=abc-123&limit=50&offset=0
  ↓ require_admin dependency checks user
  ↓ AuditService.get_audit_logs(registration_id=abc-123, limit=50, offset=0)
  ↓
  ↓ SQL: 
  ↓   SELECT al.*, u.email, u.display_name
  ↓   FROM audit_log al
  ↓   JOIN users u ON al.user_id = u.user_id
  ↓   WHERE al.registration_id = $1
  ↓   ORDER BY al.timestamp DESC
  ↓   LIMIT 50 OFFSET 0
  ↓
  ↓ Also: SELECT COUNT(*) FROM audit_log WHERE registration_id = $1
  ↓
  ↓ return AuditLogListResponse { total, limit, offset, results }
```

## Validation Rules

### Backend Validation

**Existing** (from Registration model):
- endpoint_url: Must be valid HTTP/HTTPS URL
- endpoint_name: 3-200 characters
- owner_contact: Valid email format
- status: Must be 'Pending', 'Approved', or 'Rejected'

**New** (for audit log queries):
- Date range: If both from_date and to_date provided, to_date must be after from_date
- Limit: Must be between 1 and 200 (default 50)
- Offset: Must be non-negative

### Frontend Validation

**Existing** (used by Browse page):
- Search input: No special validation, case-insensitive string match
- Pagination: Current page must be between 1 and total pages

**New** (for detailed view):
- None - detailed view is read-only, displays data from API

## State Transitions

### Registration Status (Existing)

```
[Created] → Pending
    ↓
    ├→ Approved (admin action)
    └→ Rejected (admin action)

# Status cannot transition back to Pending
# Approved/Rejected are terminal states
```

### Audit Log Lifecycle

```
[Action occurs] → Audit log created
    ↓
    Never deleted (retained indefinitely)
    Never modified (immutable)

# Even if registration is deleted, audit logs remain
```

## Summary

- **No schema changes required**: All tables already exist from feature 002
- **Service layer enhancements**: New AuditService, extend RegistrationService with audit calls
- **New API endpoints**: 2 new endpoints (GET /registrations/by-url, GET /audit-logs)
- **Frontend additions**: New Browse page components, audit log types, extend API service
- **Data integrity**: Audit logging within transactions ensures atomicity
- **Performance**: Existing indexes support all query patterns efficiently
