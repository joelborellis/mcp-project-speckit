# Research: Browse Functionality, Approval Status Query API, and Audit Logging

**Feature**: 003-browse-audit-query  
**Date**: 2025-11-12  
**Status**: Complete

## Overview

This document consolidates research findings for implementing Browse functionality, approval status query API, and comprehensive audit logging in the MCP Registry application.

## 1. Browse Page UI Patterns

### Decision: Card Grid with Modal Detail View

**Rationale**:
- **Scannable**: Card grid allows users to quickly scan multiple registrations at once
- **Responsive**: Cards naturally reflow from grid (desktop) to stacked list (mobile)
- **Familiar**: Pattern used successfully in existing AdminApprovalsPage
- **Performance**: Pagination limits initial render to 20 items for fast load times
- **Modal for details**: Keeps user context, no navigation away from browse list

**Alternatives Considered**:
- **Table layout**: Rejected - not responsive, too dense on mobile, horizontal scroll issues
- **Accordion list**: Rejected - requires clicking each item to see any details, slower discovery
- **Separate detail page**: Rejected - breaks browsing flow, requires back navigation
- **Infinite scroll only**: Rejected - harder to jump to specific page, accessibility concerns with no page numbers

**Implementation Pattern**:
```tsx
// Card-based browse with responsive grid
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {registrations.map(reg => <BrowseCard key={reg.id} registration={reg} />)}
</div>

// Modal for detailed view (using existing pattern)
<RegistrationDetailModal 
  isOpen={selectedId !== null} 
  registration={selectedRegistration}
  onClose={() => setSelectedId(null)}
/>
```

### Search/Filter Strategy

**Decision**: Client-side filtering with backend search API fallback

**Rationale**:
- **Instant feedback**: Client-side filter as user types (<500ms requirement)
- **Simple**: Single search box, no complex filter UI (aligns with Simple UX principle)
- **Scalable**: If dataset grows beyond client capacity, backend `/registrations?search=` already exists (FR-003 from feature 002)
- **No dependencies**: Uses native JavaScript filter, no search libraries needed

**Implementation**:
```tsx
// Local filter for instant results
const filtered = registrations.filter(reg => 
  reg.endpoint_name.toLowerCase().includes(search.toLowerCase()) ||
  reg.description?.toLowerCase().includes(search.toLowerCase()) ||
  reg.owner_contact.toLowerCase().includes(search.toLowerCase())
);
```

### Pagination Approach

**Decision**: Client-side pagination with page numbers (not infinite scroll)

**Rationale**:
- **Predictable**: Users can see total pages and jump to specific page
- **Accessible**: Keyboard navigation and screen reader friendly
- **Performance**: Only render current page (20 items), virtualization unnecessary
- **Simple**: No scroll position tracking, no "load more" button complexity

**Implementation**:
```tsx
const pageCount = Math.ceil(filtered.length / PAGE_SIZE);
const paginated = filtered.slice(offset, offset + PAGE_SIZE);

<Pagination 
  currentPage={currentPage}
  totalPages={pageCount}
  onPageChange={setCurrentPage}
/>
```

## 2. Audit Logging Best Practices

### Decision: Trigger-style Service Layer Pattern

**Rationale**:
- **Automatic**: Audit logs created automatically on every modification (no manual calls)
- **Atomic**: Logged within same database transaction as the operation (rollback safety)
- **Centralized**: Single `AuditService` handles all audit log creation
- **Consistent**: Every CRUD operation in `RegistrationService` calls `AuditService`

**Alternatives Considered**:
- **Database triggers**: Rejected - harder to capture rich metadata (reason, field changes), less portable
- **Decorator pattern**: Rejected - over-engineering for Python asyncio, harder to read
- **Manual calls in routes**: Rejected - error-prone, easy to forget, inconsistent
- **Event bus/queue**: Rejected - adds complexity, new dependency, overkill for this scale

**Implementation Pattern**:
```python
# In RegistrationService
async def update_registration_status(
    self, registration_id, new_status, approver_id, reason=None
):
    async with self.conn.transaction():
        # Update registration
        updated = await self._update_status_in_db(...)
        
        # Audit log (within same transaction)
        await self.audit_service.log_action(
            registration_id=registration_id,
            user_id=approver_id,
            action=AuditAction.APPROVED,
            previous_status=old_status,
            new_status=new_status,
            metadata={"reason": reason}
        )
        
        return updated
```

### Audit Log Metadata Structure

**Decision**: JSONB column with flexible schema per action type

**Rationale**:
- **Flexible**: Different actions need different metadata (approval reason vs. field changes)
- **Queryable**: PostgreSQL JSONB supports indexed queries if needed later
- **No schema migration**: Adding new metadata fields doesn't require DDL changes

**Metadata Schemas by Action**:
```python
# Created action
{"initial_values": {"endpoint_name": "...", "status": "Pending", ...}}

# Approved/Rejected action
{"reason": "Meets security requirements", "reviewer_notes": "..."}

# Updated action
{"changes": [
  {"field": "description", "old": "...", "new": "..."},
  {"field": "owner_contact", "old": "...", "new": "..."}
]}

# Deleted action
{"final_state": {"endpoint_name": "...", "status": "Rejected", ...}}
```

### Audit Log Query Performance

**Decision**: Composite indexes on common query patterns

**Rationale**:
- **Fast lookups**: Index on (registration_id, timestamp DESC) for single registration history
- **User audits**: Index on (user_id, timestamp DESC) for user action history
- **Already exists**: Schema already has these indexes (feature 002)

```sql
-- Existing indexes (from init_schema.sql)
CREATE INDEX idx_audit_log_registration_id ON audit_log(registration_id);
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp DESC);

-- Query patterns enabled:
-- 1. Get all changes for registration X (newest first)
SELECT * FROM audit_log WHERE registration_id = $1 ORDER BY timestamp DESC;

-- 2. Get all actions by user Y
SELECT * FROM audit_log WHERE user_id = $2 ORDER BY timestamp DESC;

-- 3. Get actions in date range
SELECT * FROM audit_log WHERE timestamp BETWEEN $3 AND $4 ORDER BY timestamp DESC;
```

## 3. Approval Status Query API

### Decision: Dedicated `/registrations/by-url` endpoint

**Rationale**:
- **Clear intent**: Endpoint name explicitly conveys purpose (query by URL)
- **RESTful**: Still under /registrations resource, uses query parameter
- **Performance**: Direct database query with indexed endpoint_url column (unique index)
- **Consistent**: Returns same RegistrationResponse schema as GET `/registrations/{id}`

**Alternatives Considered**:
- **Reuse GET `/registrations?endpoint_url=X`**: Rejected - semantically wrong (list endpoint, not single item lookup)
- **POST with URL in body**: Rejected - query operation should be GET (idempotent, cacheable)
- **New top-level `/query` endpoint**: Rejected - breaks REST resource hierarchy

**Implementation Pattern**:
```python
# New endpoint in registrations.py router
@router.get("/by-url", response_model=RegistrationResponse)
async def get_registration_by_url(
    endpoint_url: str = Query(..., description="Exact endpoint URL to query"),
    current_user: User = Depends(get_current_user)
):
    # Fast lookup via unique index on endpoint_url
    registration = await service.get_by_url(endpoint_url)
    if not registration:
        raise HTTPException(404, "No registration found for this endpoint URL")
    return registration
```

### URL Matching Strategy

**Decision**: Exact match only (no normalization)

**Rationale**:
- **Simple**: No complex URL parsing or normalization logic
- **Predictable**: What you register is what you query (no surprises)
- **Frontend responsibility**: Frontend should normalize URLs before submission (remove trailing slashes, enforce https)
- **Fast**: Direct string equality on indexed column

**Edge Case Handling**:
```python
# URL encoding handled by FastAPI/Pydantic automatically
# Example: endpoint_url=https%3A%2F%2Fapi.example.com%2Fmcp
# Decoded to: https://api.example.com/mcp

# Special characters in URL supported
# Example: https://api.example.com/mcp?key=value&other=123
```

## 4. Component Reusability

### Decision: Shared StatusBadge component

**Rationale**:
- **DRY**: Status badges used in Browse, My Registrations, Admin Approvals
- **Consistent**: Same color scheme across all pages (red/white theme)
- **Simple**: Single component handles all status types

```tsx
// StatusBadge.tsx - reusable across pages
export const StatusBadge: React.FC<{ status: EndpointStatus }> = ({ status }) => {
  const styles = {
    Pending: 'bg-yellow-100 text-yellow-800',
    Approved: 'bg-green-100 text-green-800',
    Rejected: 'bg-red-100 text-red-800'
  };
  
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${styles[status]}`}>
      {status}
    </span>
  );
};
```

## 5. Error Handling

### Decision: React Hot Toast for user notifications

**Rationale**:
- **Already exists**: react-hot-toast already in dependencies (feature 001)
- **No new dependency**: Aligns with Minimal Dependencies principle
- **User-friendly**: Toast messages are non-intrusive, auto-dismiss

**Pattern**:
```tsx
// In BrowsePage.tsx
try {
  const data = await getRegistrations(token, { status: 'Approved' });
  setRegistrations(data.results);
} catch (error) {
  toast.error('Failed to load registrations. Please refresh the page.');
}
```

## 6. Mobile Responsiveness

### Decision: Tailwind responsive utilities with mobile-first approach

**Rationale**:
- **Existing pattern**: All current pages use Tailwind responsive classes
- **No new code**: Standard grid/flex utilities handle responsive layouts
- **Performance**: CSS-only, no JavaScript media queries needed

**Responsive Breakpoints**:
```tsx
// Mobile (default): Stack cards vertically
<div className="grid grid-cols-1 gap-4">

// Tablet (md: 768px+): 2 columns
<div className="grid grid-cols-1 md:grid-cols-2 gap-4">

// Desktop (lg: 1024px+): 3 columns
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">

// Modal adaptation
<div className="fixed inset-0 md:inset-auto md:w-2/3 lg:w-1/2">
  {/* Full screen on mobile, sized modal on desktop */}
</div>
```

## Research Conclusions

All technical decisions documented above have been made based on:
- Existing codebase patterns (features 001 and 002)
- Constitutional principles (clean code, simple UX, responsive design, minimal dependencies, no testing)
- Performance requirements from spec (SC-001 through SC-010)
- Industry best practices for React, FastAPI, and PostgreSQL

**No additional research or clarification needed** - ready to proceed to Phase 1 (data model and contracts).
