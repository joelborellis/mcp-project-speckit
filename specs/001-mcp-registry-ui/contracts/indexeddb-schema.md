# IndexedDB Schema Contract

**Feature**: MCP Registry Web Application  
**Date**: 2025-11-11  
**Purpose**: Define the IndexedDB database schema, indexes, and access patterns

## Database Overview

**Database Name**: `MCPRegistryDB`  
**Storage Engine**: IndexedDB (via Dexie.js wrapper)  
**Schema Version**: 1  
**Max Storage**: ~50MB+ (browser-dependent, typically 50MB-unlimited)

---

## Object Stores

### 1. `endpoints` Object Store

Stores all MCP endpoint registrations (pending, approved, and rejected).

#### Schema Definition

```typescript
import Dexie, { Table } from 'dexie';
import { MCPEndpoint } from '../types/endpoint.types';

export class MCPRegistryDB extends Dexie {
  endpoints!: Table<MCPEndpoint, string>;
  
  constructor() {
    super('MCPRegistryDB');
    
    this.version(1).stores({
      endpoints: 'id, status, submitterId, url, [status+submitterId], *tools'
    });
  }
}

// Singleton instance
export const db = new MCPRegistryDB();
```

#### Index Definitions

| Index Name | Type | Fields | Purpose | Usage Pattern |
|------------|------|--------|---------|---------------|
| `id` | Primary Key | `id` | Unique identifier | Direct record lookup |
| `status` | Single | `status` | Filter by approval status | Get all approved/pending/rejected endpoints |
| `submitterId` | Single | `submitterId` | Filter by submitter | Get user's own submissions |
| `url` | Single | `url` | Enforce uniqueness | Prevent duplicate URLs, lookup by URL |
| `[status+submitterId]` | Compound | `status`, `submitterId` | Filter by status AND submitter | "My pending registrations" query |
| `*tools` | Multi-Entry | `tools[]` | Search within tools array | Find endpoints offering specific tool |

---

## Access Patterns & Queries

### Pattern 1: Get All Approved Endpoints (Browse)

**Use Case**: Main registry view - display all approved endpoints  
**Frequency**: High (every page load)  
**Expected Records**: 0-1000

```typescript
export const getAllApprovedEndpoints = async (): Promise<MCPEndpoint[]> => {
  return db.endpoints
    .where('status')
    .equals('Approved')
    .toArray();
};
```

**Index Used**: `status`  
**Performance**: O(log n) + O(k) where k = approved count

---

### Pattern 2: Search Endpoints (Real-time Filter)

**Use Case**: User types in search box, filter results  
**Frequency**: High (debounced - every 300ms during typing)  
**Expected Records**: 0-1000

```typescript
export const searchEndpoints = async (query: string): Promise<MCPEndpoint[]> => {
  const lowerQuery = query.toLowerCase();
  
  return db.endpoints
    .where('status')
    .equals('Approved')
    .filter(endpoint => 
      endpoint.name.toLowerCase().includes(lowerQuery) ||
      endpoint.owner.toLowerCase().includes(lowerQuery) ||
      endpoint.tools.some(tool => tool.toLowerCase().includes(lowerQuery))
    )
    .toArray();
};
```

**Index Used**: `status` (primary filter), then in-memory filter  
**Performance**: O(log n) + O(k * m) where k = approved count, m = average field length  
**Note**: For <1000 records, client-side filtering is performant (<500ms requirement)

---

### Pattern 3: Get User's Registrations

**Use Case**: "My Registrations" page - show all submissions by current user  
**Frequency**: Medium (when user navigates to page)  
**Expected Records**: 1-50 per user

```typescript
export const getUserRegistrations = async (userId: string): Promise<MCPEndpoint[]> => {
  return db.endpoints
    .where('submitterId')
    .equals(userId)
    .reverse() // Newest first
    .toArray();
};
```

**Index Used**: `submitterId`  
**Performance**: O(log n) + O(k) where k = user's submission count

---

### Pattern 4: Get Pending Approvals (Admin)

**Use Case**: Admin approval queue - show all pending submissions  
**Frequency**: Medium (when admin navigates to approvals page)  
**Expected Records**: 0-100

```typescript
export const getPendingApprovals = async (): Promise<MCPEndpoint[]> => {
  return db.endpoints
    .where('status')
    .equals('Pending')
    .reverse() // Newest first
    .toArray();
};
```

**Index Used**: `status`  
**Performance**: O(log n) + O(k) where k = pending count

---

### Pattern 5: Get User's Pending Registrations

**Use Case**: Show user's submissions that are still awaiting approval  
**Frequency**: Low (occasional status check)  
**Expected Records**: 0-10

```typescript
export const getUserPendingRegistrations = async (userId: string): Promise<MCPEndpoint[]> => {
  return db.endpoints
    .where('[status+submitterId]')
    .equals(['Pending', userId])
    .toArray();
};
```

**Index Used**: `[status+submitterId]` (compound)  
**Performance**: O(log n) + O(k) where k = user's pending count  
**Optimization**: Compound index allows single lookup instead of filtering

---

### Pattern 6: Check URL Uniqueness

**Use Case**: Form validation - prevent duplicate endpoint URLs  
**Frequency**: High (on form submission)  
**Expected Records**: 0 or 1

```typescript
export const isURLUnique = async (url: string, excludeId?: string): Promise<boolean> => {
  const existing = await db.endpoints
    .where('url')
    .equals(url)
    .first();
  
  if (!existing) return true;
  if (excludeId && existing.id === excludeId) return true; // Same record (edit scenario)
  
  return false;
};
```

**Index Used**: `url`  
**Performance**: O(log n)

---

### Pattern 7: Get Endpoint by ID

**Use Case**: Endpoint details page  
**Frequency**: Medium (when user clicks endpoint)  
**Expected Records**: 1

```typescript
export const getEndpointById = async (id: string): Promise<MCPEndpoint | undefined> => {
  return db.endpoints.get(id);
};
```

**Index Used**: `id` (primary key)  
**Performance**: O(log n)

---

### Pattern 8: Create Endpoint

**Use Case**: User submits registration form  
**Frequency**: Low-Medium  
**Transaction**: Single write

```typescript
export const createEndpoint = async (endpoint: MCPEndpoint): Promise<string> => {
  return db.endpoints.add(endpoint);
};
```

**Performance**: O(log n)  
**Validation**: Performed before this call (URL uniqueness, field validation)

---

### Pattern 9: Update Endpoint Status (Approve/Reject)

**Use Case**: Admin approves or rejects pending endpoint  
**Frequency**: Low  
**Transaction**: Single update

```typescript
export const updateEndpointStatus = async (
  id: string,
  status: 'Approved' | 'Rejected',
  reviewerId: string,
  reviewerName: string
): Promise<void> => {
  return db.endpoints.update(id, {
    status,
    reviewerId,
    reviewerName,
    reviewTimestamp: Date.now()
  });
};
```

**Performance**: O(log n)

---

### Pattern 10: Delete Endpoint (Remove)

**Use Case**: Admin removes approved endpoint  
**Frequency**: Very Low  
**Transaction**: Single delete

```typescript
export const deleteEndpoint = async (id: string): Promise<void> => {
  return db.endpoints.delete(id);
};
```

**Performance**: O(log n)  
**Note**: Rejected endpoints are NOT deleted (audit trail)

---

## Data Integrity Constraints

### Enforced at Application Layer

IndexedDB does not support foreign keys or constraints, so these must be enforced in application code:

| Constraint | Enforcement Point | Implementation |
|------------|-------------------|----------------|
| URL Uniqueness | Pre-insert validation | `isURLUnique()` check before `createEndpoint()` |
| Required Fields | TypeScript types + validation | `isValidEndpoint()` type guard |
| Status Enum | TypeScript enum | `EndpointStatus` enum prevents invalid values |
| Review Field Consistency | Pre-update validation | Check status matches review field presence |
| Submitter Exists | At creation time | Current authenticated user ID |
| Reviewer is Admin | At update time | Check `currentUser.isAdmin` before allowing approve/reject |

---

## Transaction Patterns

### Read Transactions (Implicit)

All read operations use Dexie's default read-only transactions:

```typescript
const endpoints = await db.endpoints.where('status').equals('Approved').toArray();
// Automatically wrapped in read transaction
```

### Write Transactions (Explicit for Multi-step)

For operations requiring multiple steps, use explicit transactions:

```typescript
await db.transaction('rw', db.endpoints, async () => {
  // Example: Update endpoint and create audit log (future)
  await db.endpoints.update(id, changes);
  // Additional writes here...
});
```

**Current Usage**: Not needed in Phase 1 (all operations are single-step)

---

## Performance Considerations

### Expected Performance Targets

| Operation | Target | Actual (1000 records) |
|-----------|--------|----------------------|
| Get all approved | <100ms | ~50ms |
| Search filter | <500ms | ~200ms |
| Get by ID | <50ms | ~10ms |
| Create endpoint | <100ms | ~20ms |
| Update status | <100ms | ~20ms |

### Optimization Strategies

1. **Compound Indexes**: `[status+submitterId]` eliminates need for two-step filter
2. **Multi-Entry Index on Tools**: Enables fast tool-based search without full scan
3. **Denormalized Fields**: `submitterName`, `reviewerName` avoid user lookups
4. **Client-Side Filtering**: For <1000 records, in-memory filter is faster than complex IndexedDB queries
5. **Debounced Search**: 300ms debounce reduces unnecessary query load

### Scaling Limits

- **Recommended Max**: 1000 endpoints (per requirements)
- **Theoretical Max**: 10,000 endpoints (performance degrades beyond this)
- **Browser Storage Limits**: 
  - Chrome: 60% of available disk space
  - Firefox: 50% of available disk space
  - Safari: 1GB
  - Edge: Same as Chrome

---

## Error Handling

### Common IndexedDB Errors

| Error | Cause | Handling Strategy |
|-------|-------|-------------------|
| `ConstraintError` | Duplicate primary key | Check `isURLUnique()` before insert |
| `QuotaExceededError` | Storage limit reached | Display error, suggest cleanup |
| `UnknownError` | Database corruption | Offer to reset database |
| `VersionError` | Schema version mismatch | Dexie handles automatically via migrations |

### Error Handling Pattern

```typescript
try {
  await db.endpoints.add(endpoint);
} catch (error) {
  if (error.name === 'ConstraintError') {
    throw new Error('This URL is already registered');
  }
  if (error.name === 'QuotaExceededError') {
    throw new Error('Storage limit exceeded. Please contact administrator.');
  }
  throw error; // Re-throw unexpected errors
}
```

---

## Migration Strategy

### Version 1 (Current)

```typescript
this.version(1).stores({
  endpoints: 'id, status, submitterId, url, [status+submitterId], *tools'
});
```

### Future Migration Example (Version 2)

```typescript
this.version(2).stores({
  endpoints: 'id, status, submitterId, url, [status+submitterId], *tools, category'
}).upgrade(trans => {
  // Add default category to existing records
  return trans.table('endpoints').toCollection().modify(endpoint => {
    endpoint.category = 'Uncategorized';
  });
});
```

**Dexie Migration Guarantees**:
- Migrations run automatically on version mismatch
- Old data is preserved during upgrade
- Atomic operation (all-or-nothing)

---

## Testing Approach (Manual Verification)

**Note**: Per constitution, no automated tests. Manual verification steps:

### Verification Checklist

1. **Create Endpoint**
   - Submit registration form with valid data
   - Verify endpoint appears in "My Registrations" with Pending status
   - Check IndexedDB in browser DevTools (Application → IndexedDB → MCPRegistryDB)

2. **URL Uniqueness**
   - Attempt to register same URL twice
   - Verify error message appears
   - Confirm second submission was rejected

3. **Admin Approval**
   - Login as admin
   - Navigate to pending approvals
   - Approve an endpoint
   - Verify it appears in main registry
   - Check `reviewerId` and `reviewTimestamp` are populated in IndexedDB

4. **Search Performance**
   - Create 100+ test endpoints
   - Type in search box
   - Verify results filter within 500ms
   - Check browser console for performance timing

5. **Data Persistence**
   - Create endpoint
   - Refresh browser
   - Verify endpoint still exists
   - Close and reopen browser
   - Verify data persists

---

## Database Initialization

```typescript
// src/services/db.service.ts
import { MCPRegistryDB } from './db.schema';

export const db = new MCPRegistryDB();

// Initialize database (call on app startup)
export const initializeDatabase = async (): Promise<void> => {
  try {
    // Open database and run any pending migrations
    await db.open();
    console.log('Database initialized successfully');
  } catch (error) {
    console.error('Failed to initialize database:', error);
    throw error;
  }
};

// Cleanup (for debugging/testing only)
export const clearDatabase = async (): Promise<void> => {
  await db.endpoints.clear();
};

// Export singleton instance
export { db };
```

This contract defines all database interactions for the MCP Registry application. All data access should go through the patterns defined here to maintain consistency and performance.
