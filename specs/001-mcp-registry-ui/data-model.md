# Data Model: MCP Registry Web Application

**Feature**: MCP Registry Web Application  
**Date**: 2025-11-11  
**Purpose**: Define TypeScript interfaces and data structures for the application

## Overview

This document defines the core data entities for the MCP Registry frontend application. All entities are stored in IndexedDB using Dexie.js and are represented as TypeScript interfaces for type safety.

---

## 1. User

Represents an authenticated user from Microsoft Entra ID.

### TypeScript Interface

```typescript
export interface User {
  /**
   * Unique identifier from Entra ID (Object ID)
   */
  id: string;
  
  /**
   * User's display name from Entra ID
   */
  displayName: string;
  
  /**
   * User's email address (UPN)
   */
  email: string;
  
  /**
   * User role determination
   */
  isAdmin: boolean;
  
  /**
   * Entra ID groups the user belongs to (Object IDs)
   */
  groups: string[];
  
  /**
   * Last authentication timestamp
   */
  lastLoginTimestamp: number;
}
```

### Field Descriptions

| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `id` | string | Yes | Entra ID Object ID (GUID) | Must be valid GUID format |
| `displayName` | string | Yes | Full name of user | Non-empty string |
| `email` | string | Yes | User Principal Name (email) | Valid email format |
| `isAdmin` | boolean | Yes | True if user is in "MCP-Registry-Admins" group | Computed from `groups` array |
| `groups` | string[] | Yes | Array of Entra ID group Object IDs | Can be empty array |
| `lastLoginTimestamp` | number | Yes | Unix timestamp (milliseconds) | Positive integer |

### Business Rules

1. **Admin Determination**: `isAdmin` is `true` if `groups` array contains the configured admin group Object ID (from environment variable `VITE_ENTRA_ADMIN_GROUP_ID`)
2. **Identity**: User ID (`id`) is immutable and sourced from Entra ID
3. **Session Management**: Not stored in IndexedDB - maintained in MSAL cache and React Context only

### State Transitions

```
[Unauthenticated] 
    ↓ (User logs in via MSAL)
[Authenticated - User Data Retrieved]
    ↓ (Group membership checked)
[Role Determined] (isAdmin set)
    ↓ (User navigates/interacts)
[Active Session]
    ↓ (User logs out or token expires)
[Unauthenticated]
```

---

## 2. MCP Endpoint

Represents a registered Model Context Protocol server endpoint in the registry.

### TypeScript Interface

```typescript
export enum EndpointStatus {
  Pending = 'Pending',
  Approved = 'Approved',
  Rejected = 'Rejected'
}

export interface MCPEndpoint {
  /**
   * Unique identifier (UUID v4)
   */
  id: string;
  
  /**
   * Human-readable name for the endpoint
   */
  name: string;
  
  /**
   * Endpoint URL (host/IP with protocol)
   */
  url: string;
  
  /**
   * Detailed description of endpoint purpose/functionality
   */
  description: string;
  
  /**
   * Contact information for endpoint owner
   */
  owner: string;
  
  /**
   * Comma-separated list of available tools/capabilities
   */
  tools: string[];
  
  /**
   * Current approval status
   */
  status: EndpointStatus;
  
  /**
   * Entra ID user ID of submitter
   */
  submitterId: string;
  
  /**
   * Display name of submitter (denormalized for display)
   */
  submitterName: string;
  
  /**
   * Unix timestamp when endpoint was submitted
   */
  submissionTimestamp: number;
  
  /**
   * Entra ID user ID of approving/rejecting admin (null if pending)
   */
  reviewerId: string | null;
  
  /**
   * Display name of reviewer (denormalized for display)
   */
  reviewerName: string | null;
  
  /**
   * Unix timestamp when endpoint was approved/rejected (null if pending)
   */
  reviewTimestamp: number | null;
}
```

### Field Descriptions

| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `id` | string | Yes | UUID v4 identifier | Valid UUID v4 format |
| `name` | string | Yes | Endpoint name | 3-100 characters, non-empty |
| `url` | string | Yes | Endpoint URL | Valid HTTP/HTTPS URL |
| `description` | string | Yes | Purpose/functionality description | 10-500 characters |
| `owner` | string | Yes | Owner contact (email or name) | Non-empty, valid email format preferred |
| `tools` | string[] | Yes | Array of tool names | Parsed from comma-separated input, at least 1 tool |
| `status` | EndpointStatus | Yes | Approval status enum | Must be Pending/Approved/Rejected |
| `submitterId` | string | Yes | User ID of submitter | Must match valid User.id |
| `submitterName` | string | Yes | Name of submitter | Non-empty string |
| `submissionTimestamp` | number | Yes | Submission date/time | Positive integer, Unix ms |
| `reviewerId` | string \| null | No | User ID of reviewer | Null if pending, otherwise valid User.id |
| `reviewerName` | string \| null | No | Name of reviewer | Null if pending, otherwise non-empty |
| `reviewTimestamp` | number \| null | No | Review date/time | Null if pending, otherwise positive integer |

### Business Rules

1. **Uniqueness**: `url` must be unique across all endpoints (including rejected)
2. **Status Transition Rules**:
   - New endpoints start as `Pending`
   - Only admins can transition `Pending` → `Approved` or `Pending` → `Rejected`
   - `Approved` endpoints can be removed (status change) by admins
   - `Rejected` endpoints retain status permanently for audit trail
3. **Visibility Rules**:
   - `Approved`: Visible to all authenticated users
   - `Pending`: Visible only to submitter and admins
   - `Rejected`: Visible only to submitter and admins
4. **Tools Format**: Stored as array internally, displayed as comma-separated list in UI, input accepted as comma-separated string
5. **Denormalization**: `submitterName` and `reviewerName` are denormalized to avoid joins/lookups on display

### State Transitions

```
[New Registration]
    ↓ (User submits form)
[Pending] (reviewerId=null, reviewTimestamp=null)
    ↓
    ├─→ [Approved] (Admin approves, reviewerId set, reviewTimestamp set)
    │       ↓
    │       └─→ [Removed] (Admin removes - status could change or record deleted)
    │
    └─→ [Rejected] (Admin rejects, reviewerId set, reviewTimestamp set)
            ↓
            [Permanently Rejected] (No further transitions)
```

### IndexedDB Indexes

```typescript
// Dexie schema definition
this.version(1).stores({
  endpoints: 'id, status, submitterId, url, [status+submitterId], *tools'
});
```

**Index Rationale**:
- `id`: Primary key for direct lookups
- `status`: Filter by approval status (approved/pending/rejected)
- `submitterId`: Query user's own submissions
- `url`: Enforce uniqueness, prevent duplicates
- `[status+submitterId]`: Compound index for "my pending submissions" query
- `*tools`: Multi-entry index for searching by tool names

---

## 3. Registration Submission (View Model)

A derived/computed entity combining `MCPEndpoint` data with additional UI-specific metadata. Not stored separately - computed from `MCPEndpoint` records.

### TypeScript Interface

```typescript
export interface RegistrationSubmission extends MCPEndpoint {
  /**
   * Computed field: Can current user edit this submission?
   */
  canEdit: boolean;
  
  /**
   * Computed field: Can current user approve/reject this submission?
   */
  canReview: boolean;
  
  /**
   * Computed field: Formatted submission date for display
   */
  submittedDateDisplay: string;
  
  /**
   * Computed field: Formatted review date for display (null if pending)
   */
  reviewedDateDisplay: string | null;
  
  /**
   * Computed field: CSS class for status badge
   */
  statusBadgeClass: string;
}
```

### Computed Fields Logic

```typescript
const createSubmissionFromEndpoint = (
  endpoint: MCPEndpoint, 
  currentUser: User
): RegistrationSubmission => {
  return {
    ...endpoint,
    canEdit: endpoint.submitterId === currentUser.id && endpoint.status === 'Pending',
    canReview: currentUser.isAdmin && endpoint.status === 'Pending',
    submittedDateDisplay: formatTimestamp(endpoint.submissionTimestamp),
    reviewedDateDisplay: endpoint.reviewTimestamp 
      ? formatTimestamp(endpoint.reviewTimestamp) 
      : null,
    statusBadgeClass: getStatusBadgeClass(endpoint.status)
  };
};
```

---

## Relationships

```
User (1) ──submits──> (*) MCPEndpoint
    │                       │
    │                       │ submitterId
    │                       │
    └──reviews──> (*) MCPEndpoint
                         │
                         │ reviewerId
                         │
                         ▼
                    (Approved/Rejected)
```

### Relationship Rules

1. **User → Endpoint (Submitter)**: One user can submit many endpoints
2. **User → Endpoint (Reviewer)**: One admin can review many endpoints
3. **Endpoint → User**: Each endpoint has exactly one submitter, at most one reviewer
4. **No Cascade Deletes**: Deleting a user (future feature) should NOT delete their endpoints - endpoints are audit records

---

## Validation Summary

### Cross-Field Validation

| Rule | Fields Involved | Validation Logic |
|------|----------------|------------------|
| URL Uniqueness | `url`, all endpoints | No two endpoints can have same URL |
| Review Fields Consistency | `status`, `reviewerId`, `reviewerName`, `reviewTimestamp` | If status is Approved/Rejected, all review fields must be non-null; if Pending, all must be null |
| Submitter Exists | `submitterId` | Must reference valid authenticated user (enforced at submission time) |
| Reviewer is Admin | `reviewerId` | If non-null, must reference user with `isAdmin=true` |
| Tools Non-Empty | `tools` | Array must contain at least one non-empty string |

### Constraint Enforcement

```typescript
// Type guard for valid endpoint
export const isValidEndpoint = (endpoint: Partial<MCPEndpoint>): endpoint is MCPEndpoint => {
  if (!endpoint.id || !isUUID(endpoint.id)) return false;
  if (!endpoint.name || endpoint.name.length < 3) return false;
  if (!isValidURL(endpoint.url)) return false;
  if (!endpoint.description || endpoint.description.length < 10) return false;
  if (!endpoint.owner) return false;
  if (!endpoint.tools || endpoint.tools.length === 0) return false;
  if (!Object.values(EndpointStatus).includes(endpoint.status)) return false;
  
  // Review field consistency
  const isPending = endpoint.status === EndpointStatus.Pending;
  const hasReviewData = endpoint.reviewerId && endpoint.reviewerName && endpoint.reviewTimestamp;
  
  if (isPending && hasReviewData) return false;
  if (!isPending && !hasReviewData) return false;
  
  return true;
};
```

---

## Migration Strategy

### Version 1 (Initial)

```typescript
class MCPRegistryDB extends Dexie {
  endpoints!: Table<MCPEndpoint, string>;
  
  constructor() {
    super('MCPRegistryDB');
    this.version(1).stores({
      endpoints: 'id, status, submitterId, url, [status+submitterId], *tools'
    });
  }
}
```

### Future Versions (Placeholder)

Future schema changes will use Dexie's upgrade mechanism:

```typescript
// Example: Version 2 adds categories
this.version(2).stores({
  endpoints: 'id, status, submitterId, url, [status+submitterId], *tools, category'
}).upgrade(trans => {
  return trans.table('endpoints').toCollection().modify(endpoint => {
    endpoint.category = 'Uncategorized';
  });
});
```

---

## Data Flow Diagrams

### Endpoint Registration Flow

```
[User Interface]
    ↓ (User fills registration form)
[Form Validation]
    ↓ (Client-side validation passes)
[Create MCPEndpoint Object]
    {
      id: UUID(),
      status: 'Pending',
      submitterId: currentUser.id,
      submitterName: currentUser.displayName,
      submissionTimestamp: Date.now(),
      reviewerId: null,
      reviewerName: null,
      reviewTimestamp: null,
      ...formData
    }
    ↓
[IndexedDB Insert]
    ↓
[Update UI]
    ↓
[Show Success Toast]
```

### Admin Approval Flow

```
[Admin Interface - Pending List]
    ↓ (Admin clicks "Approve")
[Confirmation Dialog]
    ↓ (Admin confirms)
[Update MCPEndpoint]
    {
      ...existingEndpoint,
      status: 'Approved',
      reviewerId: currentUser.id,
      reviewerName: currentUser.displayName,
      reviewTimestamp: Date.now()
    }
    ↓
[IndexedDB Update]
    ↓
[Update UI]
    ↓
[Show Success Toast]
```

---

## Type Definitions File Structure

```typescript
// src/types/user.types.ts
export interface User { ... }

// src/types/endpoint.types.ts
export enum EndpointStatus { ... }
export interface MCPEndpoint { ... }
export interface RegistrationSubmission { ... }

// src/types/index.ts
export * from './user.types';
export * from './endpoint.types';
```

This structure maintains separation of concerns and makes imports clean throughout the application.
