# Validation Schema Contract

**Feature**: MCP Registry Web Application  
**Date**: 2025-11-11  
**Purpose**: Define validation rules, type guards, and data sanitization functions

---

## Core Validation Functions

### 1. Endpoint Validation

#### `isValidEndpoint`

Validates a complete `MCPEndpoint` object before database insertion.

```typescript
import { MCPEndpoint, EndpointStatus } from '../types/endpoint.types';

export function isValidEndpoint(endpoint: unknown): endpoint is MCPEndpoint {
  if (typeof endpoint !== 'object' || endpoint === null) {
    return false;
  }
  
  const e = endpoint as MCPEndpoint;
  
  return (
    typeof e.id === 'string' && e.id.length > 0 &&
    typeof e.name === 'string' && e.name.length > 0 && e.name.length <= 100 &&
    typeof e.url === 'string' && isValidURL(e.url) &&
    typeof e.description === 'string' && e.description.length <= 500 &&
    typeof e.owner === 'string' && e.owner.length > 0 && e.owner.length <= 100 &&
    Array.isArray(e.tools) && e.tools.length > 0 && e.tools.every(t => typeof t === 'string' && t.length > 0) &&
    isValidStatus(e.status) &&
    typeof e.submitterId === 'string' && e.submitterId.length > 0 &&
    typeof e.submitterName === 'string' && e.submitterName.length > 0 &&
    typeof e.submissionTimestamp === 'number' && e.submissionTimestamp > 0 &&
    (e.reviewerId === null || typeof e.reviewerId === 'string') &&
    (e.reviewerName === null || typeof e.reviewerName === 'string') &&
    (e.reviewTimestamp === null || typeof e.reviewTimestamp === 'number')
  );
}
```

**Validation Rules**:
- `id`: Non-empty string (UUID v4 recommended)
- `name`: 1-100 characters
- `url`: Valid HTTP/HTTPS URL
- `description`: 0-500 characters
- `owner`: 1-100 characters
- `tools`: Non-empty array of non-empty strings
- `status`: One of: "Pending", "Approved", "Rejected"
- `submitterId`: Non-empty string (Entra ID user ID)
- `submitterName`: Non-empty string (display name)
- `submissionTimestamp`: Positive number (Unix milliseconds)
- `reviewerId`: null (if pending) OR non-empty string (if approved/rejected)
- `reviewerName`: null (if pending) OR non-empty string (if approved/rejected)
- `reviewTimestamp`: null (if pending) OR positive number (if approved/rejected)

---

### 2. URL Validation

#### `isValidURL`

Validates that a string is a properly formatted HTTP/HTTPS URL.

```typescript
export function isValidURL(url: string): boolean {
  try {
    const parsed = new URL(url);
    
    // Must be HTTP or HTTPS
    if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
      return false;
    }
    
    // Must have a hostname
    if (!parsed.hostname || parsed.hostname.length === 0) {
      return false;
    }
    
    // Reject localhost/private IPs (optional - can be removed for dev)
    if (parsed.hostname === 'localhost' || parsed.hostname.startsWith('127.')) {
      return false;
    }
    
    return true;
  } catch {
    return false;
  }
}
```

**Validation Rules**:
- Must parse as valid URL
- Protocol must be `http://` or `https://`
- Must have non-empty hostname
- Rejects localhost (production requirement - remove for local dev)

**Examples**:
- ✅ `https://example.com/mcp`
- ✅ `http://api.example.org:8080/mcp`
- ❌ `ftp://example.com` (wrong protocol)
- ❌ `not-a-url` (invalid format)
- ❌ `http://` (no hostname)
- ❌ `http://localhost:3000` (localhost rejected)

---

### 3. Status Validation

#### `isValidStatus`

Validates that a status value is one of the allowed enum values.

```typescript
export function isValidStatus(status: unknown): status is EndpointStatus {
  return status === 'Pending' || status === 'Approved' || status === 'Rejected';
}
```

**Allowed Values**: `'Pending'` | `'Approved'` | `'Rejected'`

---

### 4. Tools Array Validation

#### `isValidToolsArray`

Validates that tools array contains valid, non-empty strings.

```typescript
export function isValidToolsArray(tools: unknown): tools is string[] {
  if (!Array.isArray(tools)) {
    return false;
  }
  
  if (tools.length === 0) {
    return false;
  }
  
  return tools.every(tool => 
    typeof tool === 'string' && 
    tool.trim().length > 0 &&
    tool.length <= 50 // Max individual tool name length
  );
}
```

**Validation Rules**:
- Must be an array
- Cannot be empty (at least 1 tool required)
- Each tool must be a string
- Each tool must be non-empty (after trimming)
- Each tool limited to 50 characters

---

## Form Input Sanitization

### 1. `sanitizeString`

Removes leading/trailing whitespace and limits length.

```typescript
export function sanitizeString(input: string, maxLength: number): string {
  return input.trim().slice(0, maxLength);
}
```

**Usage**:
```typescript
const name = sanitizeString(formData.name, 100);
const description = sanitizeString(formData.description, 500);
```

---

### 2. `sanitizeURL`

Normalizes URL and validates format.

```typescript
export function sanitizeURL(input: string): string {
  const trimmed = input.trim();
  
  // Add https:// if no protocol specified
  if (!/^https?:\/\//i.test(trimmed)) {
    return `https://${trimmed}`;
  }
  
  return trimmed;
}
```

**Examples**:
- `example.com/mcp` → `https://example.com/mcp`
- `http://example.com` → `http://example.com` (unchanged)
- `https://example.com` → `https://example.com` (unchanged)

---

### 3. `sanitizeToolsInput`

Parses comma-separated tools string into validated array.

```typescript
export function sanitizeToolsInput(input: string): string[] {
  return input
    .split(',')
    .map(tool => tool.trim())
    .filter(tool => tool.length > 0)
    .map(tool => tool.slice(0, 50)); // Limit individual tool length
}
```

**Examples**:
- `"tool1, tool2,tool3"` → `["tool1", "tool2", "tool3"]`
- `"  tool1  ,, , tool2  "` → `["tool1", "tool2"]`
- `"tool1,"` → `["tool1"]`
- `", ,"` → `[]`

---

## Field-Level Validation

### Registration Form Validation

#### `validateRegistrationForm`

Validates entire registration form data before submission.

```typescript
export interface RegistrationFormData {
  name: string;
  url: string;
  description: string;
  owner: string;
  tools: string; // Comma-separated
}

export interface ValidationResult {
  isValid: boolean;
  errors: Record<string, string>;
}

export function validateRegistrationForm(data: RegistrationFormData): ValidationResult {
  const errors: Record<string, string> = {};
  
  // Name validation
  if (!data.name || data.name.trim().length === 0) {
    errors.name = 'Endpoint name is required';
  } else if (data.name.length > 100) {
    errors.name = 'Endpoint name must be 100 characters or less';
  }
  
  // URL validation
  if (!data.url || data.url.trim().length === 0) {
    errors.url = 'URL is required';
  } else {
    const sanitizedUrl = sanitizeURL(data.url);
    if (!isValidURL(sanitizedUrl)) {
      errors.url = 'Invalid URL format. Must be a valid HTTP/HTTPS URL';
    }
  }
  
  // Description validation (optional but limited)
  if (data.description && data.description.length > 500) {
    errors.description = 'Description must be 500 characters or less';
  }
  
  // Owner validation
  if (!data.owner || data.owner.trim().length === 0) {
    errors.owner = 'Owner is required';
  } else if (data.owner.length > 100) {
    errors.owner = 'Owner must be 100 characters or less';
  }
  
  // Tools validation
  if (!data.tools || data.tools.trim().length === 0) {
    errors.tools = 'At least one tool is required';
  } else {
    const toolsArray = sanitizeToolsInput(data.tools);
    if (toolsArray.length === 0) {
      errors.tools = 'At least one tool is required';
    }
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
}
```

**Error Messages**:
- `name`: "Endpoint name is required" | "Endpoint name must be 100 characters or less"
- `url`: "URL is required" | "Invalid URL format. Must be a valid HTTP/HTTPS URL"
- `description`: "Description must be 500 characters or less"
- `owner`: "Owner is required" | "Owner must be 100 characters or less"
- `tools`: "At least one tool is required"

---

## Review Validation

### `canUserReviewEndpoint`

Validates if a user can approve/reject an endpoint.

```typescript
import { User } from '../types/user.types';
import { MCPEndpoint } from '../types/endpoint.types';

export function canUserReviewEndpoint(user: User, endpoint: MCPEndpoint): boolean {
  // Only admins can review
  if (!user.isAdmin) {
    return false;
  }
  
  // Cannot review your own submission
  if (user.id === endpoint.submitterId) {
    return false;
  }
  
  // Can only review pending endpoints
  if (endpoint.status !== 'Pending') {
    return false;
  }
  
  return true;
}
```

**Rules**:
- User must be admin (`user.isAdmin === true`)
- User cannot review their own submission
- Endpoint must have `Pending` status

---

### `canUserEditEndpoint`

Validates if a user can edit an endpoint.

```typescript
export function canUserEditEndpoint(user: User, endpoint: MCPEndpoint): boolean {
  // Only the submitter can edit
  if (user.id !== endpoint.submitterId) {
    return false;
  }
  
  // Can only edit pending endpoints
  if (endpoint.status !== 'Pending') {
    return false;
  }
  
  return true;
}
```

**Rules**:
- User must be the original submitter
- Endpoint must have `Pending` status

---

## State Transition Validation

### `isValidStatusTransition`

Validates that a status change is allowed.

```typescript
export function isValidStatusTransition(
  currentStatus: EndpointStatus,
  newStatus: EndpointStatus
): boolean {
  // Allowed transitions
  const allowedTransitions: Record<EndpointStatus, EndpointStatus[]> = {
    'Pending': ['Approved', 'Rejected'],
    'Approved': [], // Cannot change once approved
    'Rejected': []  // Cannot change once rejected
  };
  
  return allowedTransitions[currentStatus].includes(newStatus);
}
```

**Allowed Transitions**:
- `Pending` → `Approved` ✅
- `Pending` → `Rejected` ✅
- `Approved` → `Rejected` ❌
- `Approved` → `Pending` ❌
- `Rejected` → `Approved` ❌
- `Rejected` → `Pending` ❌

**Rationale**: Once an endpoint is approved or rejected, the decision is final (audit trail).

---

## Type Guards

### `isEndpoint`

Type guard for `MCPEndpoint` objects.

```typescript
export function isEndpoint(value: unknown): value is MCPEndpoint {
  return isValidEndpoint(value);
}
```

---

### `isUser`

Type guard for `User` objects.

```typescript
export function isUser(value: unknown): value is User {
  if (typeof value !== 'object' || value === null) {
    return false;
  }
  
  const u = value as User;
  
  return (
    typeof u.id === 'string' && u.id.length > 0 &&
    typeof u.displayName === 'string' && u.displayName.length > 0 &&
    typeof u.email === 'string' && isValidEmail(u.email) &&
    typeof u.isAdmin === 'boolean' &&
    Array.isArray(u.groups) &&
    (u.lastLoginTimestamp === null || typeof u.lastLoginTimestamp === 'number')
  );
}
```

---

### `isValidEmail`

Helper function for email validation.

```typescript
export function isValidEmail(email: string): boolean {
  // Basic email regex (RFC 5322 simplified)
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}
```

---

## Error Handling Utilities

### `ValidationError`

Custom error class for validation failures.

```typescript
export class ValidationError extends Error {
  constructor(
    message: string,
    public field?: string,
    public value?: unknown
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}
```

**Usage**:
```typescript
if (!isValidURL(url)) {
  throw new ValidationError('Invalid URL format', 'url', url);
}
```

---

### `validateOrThrow`

Validates an endpoint and throws if invalid.

```typescript
export function validateOrThrow(endpoint: unknown): asserts endpoint is MCPEndpoint {
  if (!isValidEndpoint(endpoint)) {
    throw new ValidationError('Invalid endpoint data', undefined, endpoint);
  }
}
```

**Usage**:
```typescript
const endpoint = createEndpointFromForm(formData);
validateOrThrow(endpoint); // Throws if invalid
await db.endpoints.add(endpoint); // TypeScript knows endpoint is valid
```

---

## Constants

### Validation Limits

```typescript
export const VALIDATION_LIMITS = {
  NAME_MAX_LENGTH: 100,
  DESCRIPTION_MAX_LENGTH: 500,
  OWNER_MAX_LENGTH: 100,
  TOOL_MAX_LENGTH: 50,
  URL_MAX_LENGTH: 2048,
  MIN_TOOLS: 1,
  MAX_TOOLS: 20 // Prevent abuse
} as const;
```

### Error Messages

```typescript
export const VALIDATION_MESSAGES = {
  NAME_REQUIRED: 'Endpoint name is required',
  NAME_TOO_LONG: `Endpoint name must be ${VALIDATION_LIMITS.NAME_MAX_LENGTH} characters or less`,
  URL_REQUIRED: 'URL is required',
  URL_INVALID: 'Invalid URL format. Must be a valid HTTP/HTTPS URL',
  URL_DUPLICATE: 'This URL is already registered',
  DESCRIPTION_TOO_LONG: `Description must be ${VALIDATION_LIMITS.DESCRIPTION_MAX_LENGTH} characters or less`,
  OWNER_REQUIRED: 'Owner is required',
  OWNER_TOO_LONG: `Owner must be ${VALIDATION_LIMITS.OWNER_MAX_LENGTH} characters or less`,
  TOOLS_REQUIRED: 'At least one tool is required',
  TOOLS_TOO_MANY: `Cannot exceed ${VALIDATION_LIMITS.MAX_TOOLS} tools`,
  NOT_ADMIN: 'You must be an admin to perform this action',
  CANNOT_REVIEW_OWN: 'You cannot review your own submission',
  ALREADY_REVIEWED: 'This endpoint has already been reviewed',
  INVALID_TRANSITION: 'Invalid status transition'
} as const;
```

---

## Usage Examples

### Example 1: Form Submission

```typescript
// In registration form component
const handleSubmit = async (formData: RegistrationFormData) => {
  // 1. Validate form
  const validation = validateRegistrationForm(formData);
  if (!validation.isValid) {
    setFormErrors(validation.errors);
    return;
  }
  
  // 2. Check URL uniqueness
  const isUnique = await isURLUnique(sanitizeURL(formData.url));
  if (!isUnique) {
    setFormErrors({ url: VALIDATION_MESSAGES.URL_DUPLICATE });
    return;
  }
  
  // 3. Create endpoint object
  const endpoint: MCPEndpoint = {
    id: crypto.randomUUID(),
    name: sanitizeString(formData.name, VALIDATION_LIMITS.NAME_MAX_LENGTH),
    url: sanitizeURL(formData.url),
    description: sanitizeString(formData.description, VALIDATION_LIMITS.DESCRIPTION_MAX_LENGTH),
    owner: sanitizeString(formData.owner, VALIDATION_LIMITS.OWNER_MAX_LENGTH),
    tools: sanitizeToolsInput(formData.tools),
    status: 'Pending',
    submitterId: currentUser.id,
    submitterName: currentUser.displayName,
    submissionTimestamp: Date.now(),
    reviewerId: null,
    reviewerName: null,
    reviewTimestamp: null
  };
  
  // 4. Final validation
  validateOrThrow(endpoint);
  
  // 5. Save to database
  await createEndpoint(endpoint);
};
```

---

### Example 2: Admin Review

```typescript
// In admin approval component
const handleApprove = async (endpoint: MCPEndpoint) => {
  // 1. Validate user can review
  if (!canUserReviewEndpoint(currentUser, endpoint)) {
    toast.error(VALIDATION_MESSAGES.NOT_ADMIN);
    return;
  }
  
  // 2. Validate state transition
  if (!isValidStatusTransition(endpoint.status, 'Approved')) {
    toast.error(VALIDATION_MESSAGES.INVALID_TRANSITION);
    return;
  }
  
  // 3. Update endpoint
  await updateEndpointStatus(
    endpoint.id,
    'Approved',
    currentUser.id,
    currentUser.displayName
  );
  
  toast.success('Endpoint approved successfully');
};
```

---

## Manual Verification Checklist

**Note**: Per constitution, no automated tests. Manual verification steps:

1. **Valid Form Submission**
   - Fill all required fields with valid data
   - Submit form
   - Verify no error messages appear
   - Check endpoint created in IndexedDB

2. **Name Validation**
   - Leave name empty → Verify error: "Endpoint name is required"
   - Enter 101 characters → Verify error: "Endpoint name must be 100 characters or less"
   - Enter valid name → No error

3. **URL Validation**
   - Leave URL empty → Verify error: "URL is required"
   - Enter "not-a-url" → Verify error: "Invalid URL format"
   - Enter "ftp://example.com" → Verify error: "Invalid URL format"
   - Enter "https://example.com" → No error

4. **URL Uniqueness**
   - Register endpoint with URL "https://test.com"
   - Attempt to register another with same URL
   - Verify error: "This URL is already registered"

5. **Tools Validation**
   - Leave tools empty → Verify error: "At least one tool is required"
   - Enter "tool1, tool2" → No error
   - Verify IndexedDB stores `["tool1", "tool2"]`

6. **Admin Review Permission**
   - Login as non-admin
   - Navigate to pending endpoint
   - Verify approve/reject buttons hidden
   - Login as admin
   - Verify buttons appear

7. **Self-Review Prevention**
   - Login as admin
   - Submit endpoint
   - Navigate to own pending endpoint
   - Verify approve/reject buttons hidden

8. **Status Transition**
   - Approve a pending endpoint
   - Attempt to reject it
   - Verify action is prevented (no UI control)
   - Check IndexedDB status remains "Approved"

This contract defines all validation logic for the MCP Registry application. All data should pass through these validators before database operations.
