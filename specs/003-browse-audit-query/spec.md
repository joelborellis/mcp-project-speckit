# Feature Specification: Browse Functionality, Approval Status Query API, and Audit Logging

**Feature Branch**: `003-browse-audit-query`  
**Created**: 2025-11-12  
**Status**: Draft  
**Input**: User description: "Add new functionality to the existing app keeping the same architecture of frontend and backend: Complete Browse functionality, API to query approval status, and audit logging for registry entries"

## User Scenarios & Acceptance *(mandatory)*

### User Story 1 - Browse All Registered MCP Servers (Priority: P1)

All authenticated users (admin and non-admin) need a comprehensive view of all registered MCP servers in the registry with their metadata, status, and ownership information. The Browse page serves as the primary discovery interface for finding available MCP endpoints.

**Why this priority**: This is the core value delivery for the registry - centralizing discovery of MCP servers across the organization. Without this, users cannot discover available endpoints. This feature builds on existing authentication and registration infrastructure but delivers the primary user-facing value.

**Manual Verification**: 
1. Login as a regular user (non-admin)
2. Navigate to the Browse page (root path `/`)
3. Verify a list of all approved registrations displays
4. Verify each registration card/item shows: endpoint name, URL, status, owner contact, description, submission date
5. Login as admin and verify you can see all registrations regardless of status
6. Use search/filter controls to find specific endpoints
7. Click on a registration to view full details
8. Verify the page is responsive on mobile and desktop

**Acceptance Scenarios**:

1. **Given** a regular user views the Browse page, **When** the page loads, **Then** all registrations with status "Approved" are displayed in a grid or list layout
2. **Given** an admin user views the Browse page, **When** the page loads, **Then** all registrations (Pending, Approved, Rejected) are displayed with clear status indicators
3. **Given** multiple registrations exist, **When** a user scrolls through the list, **Then** registrations are loaded with pagination (infinite scroll or page numbers) showing 20 items per page
4. **Given** a user is viewing registrations, **When** they type in a search box, **Then** results filter in real-time to match search terms against endpoint name, owner, and description
5. **Given** a user selects a registration, **When** they click to view details, **Then** a detailed view or modal displays all metadata including: endpoint URL, name, description, owner contact, available tools (list of tool names), status, submitter name, submission date, approval date (if approved), approver name (if approved/rejected)
6. **Given** no registrations match search criteria, **When** the filtered list is empty, **Then** a helpful message displays: "No registrations found matching your criteria"
7. **Given** no registrations exist in the system, **When** the Browse page loads, **Then** an empty state message displays: "No MCP servers registered yet. Be the first to register one!"

---

### User Story 2 - Programmatic Query of Approval Status (Priority: P2)

External tools, CI/CD pipelines, and monitoring systems need to programmatically query the approval status and details of MCP endpoints by providing the endpoint URL. This enables automated compliance checks and integration workflows.

**Why this priority**: Important for enterprise integration but depends on the core registry data (US1-P1) being available. This enables automation and compliance workflows that extend the value of the registry beyond the web UI. It's less critical than Browse because it serves a smaller audience (developers/automation) rather than all users.

**Manual Verification**:
1. Use curl or Postman to send GET request to `/registrations/by-url?endpoint_url=https://example.com/mcp`
2. Verify the API returns registration details including status
3. Test with an approved endpoint and verify status is "Approved"
4. Test with a pending endpoint and verify status is "Pending"
5. Test with a non-existent endpoint URL and verify 404 response
6. Test without authentication token and verify 401 response
7. Test the API response time is under 200ms

**Acceptance Scenarios**:

1. **Given** an authenticated system calls GET `/registrations/by-url?endpoint_url={url}`, **When** the URL matches an existing registration, **Then** the full registration details are returned including registration_id, status, approval date, approver, and all metadata
2. **Given** a system queries an endpoint URL, **When** the URL does not exist in the registry, **Then** HTTP 404 is returned with message: "No registration found for this endpoint URL"
3. **Given** a CI/CD pipeline queries an endpoint, **When** the status is "Pending", **Then** the pipeline can block deployment with a compliance check failure
4. **Given** a monitoring system queries multiple endpoints, **When** requests are made in parallel, **Then** each request completes within 200ms (95th percentile)
5. **Given** an unauthenticated request is made, **When** no valid token is provided, **Then** HTTP 401 Unauthorized is returned
6. **Given** the endpoint URL contains special characters or encoding, **When** the query is made, **Then** URL encoding is properly handled and the correct registration is found

---

### User Story 3 - Comprehensive Audit Logging (Priority: P1)

All changes to registry entries must be tracked in an audit log including who made the change, what changed, when it happened, and why (optional reason). This supports compliance, security investigations, and troubleshooting.

**Why this priority**: Critical for enterprise security, compliance (SOX, GDPR, HIPAA), and troubleshooting. While not immediately visible to end users, this is foundational for trust and governance. Audit logging should be implemented alongside any data modification features. This is P1 because the backend currently modifies registration status without comprehensive audit trails.

**Manual Verification**:
1. As a user, create a new registration and verify an audit log entry is created with action "Created"
2. As admin, approve the registration and verify an audit log entry is created with action "Approved", previous status "Pending", new status "Approved"
3. As admin, view audit logs for that registration (via API or admin interface) and verify both entries exist
4. Verify each audit entry includes: timestamp, user who performed action, registration ID, action type, previous/new status values
5. Reject another registration and verify the reason is captured in the audit log metadata
6. Query audit logs for a specific user ID and verify all their actions are returned
7. Query audit logs for a date range and verify filtering works

**Acceptance Scenarios**:

1. **Given** a user submits a new registration, **When** the registration is created, **Then** an audit log entry is created with action="Created", new_status="Pending", user_id=submitter's ID, timestamp=now, metadata includes full registration details
2. **Given** an admin approves a registration, **When** the status changes, **Then** an audit log entry is created with action="Approved", previous_status="Pending", new_status="Approved", user_id=approver's ID, metadata includes approval reason if provided
3. **Given** an admin rejects a registration, **When** the status changes, **Then** an audit log entry is created with action="Rejected", previous_status="Pending", new_status="Rejected", metadata includes rejection reason
4. **Given** a registration is updated (metadata changes), **When** the update is saved, **Then** an audit log entry is created with action="Updated", metadata includes what fields changed and their before/after values
5. **Given** an admin deletes a registration, **When** the deletion occurs, **Then** an audit log entry is created with action="Deleted" and the audit log is retained even after registration deletion
6. **Given** an admin queries audit logs via GET `/audit-logs?registration_id={id}`, **When** the request is authenticated, **Then** all audit log entries for that registration are returned in reverse chronological order (newest first)
7. **Given** a compliance officer queries audit logs for a user via GET `/audit-logs?user_id={id}`, **When** the request is made, **Then** all actions performed by that user are returned with timestamps and details
8. **Given** an audit query is made for a date range via GET `/audit-logs?from={date}&to={date}`, **When** valid dates are provided, **Then** all audit entries within that range are returned

---

### Edge Cases

- **What happens when a user browses registrations while an admin is approving/rejecting them in real-time?** The Browse page shows the current state at load time. User can refresh to see updates. Future enhancement could add real-time updates via WebSocket.
- **What happens when searching for an endpoint URL in the Browse page vs. the query API?** Browse page searches across multiple fields (name, description, owner). Query API searches exact endpoint URL match only.
- **What happens when audit logs grow very large (thousands of entries)?** Audit log queries support pagination (limit/offset). Database indexes on registration_id, user_id, and timestamp ensure performance. Archive/retention policies are outside current scope.
- **What happens when the same registration is updated multiple times quickly (race condition)?** Database transactions ensure audit logs are created atomically with status updates. All changes are captured in order of commit.
- **What happens when an admin tries to view audit logs for a registration they don't have access to?** In this system, all admins can view all audit logs for compliance purposes. Non-admins cannot access audit log endpoints (403 Forbidden).
- **What happens when querying by endpoint URL with different URL formats (trailing slash, http vs https)?** System stores URLs exactly as submitted. Query API requires exact match. Frontend should normalize URLs before submission (remove trailing slashes, enforce https).
- **What happens when Browse page is accessed by unauthenticated user?** User is redirected to login page (existing ProtectedRoute behavior from feature 001).
- **What happens when audit log API is called with invalid date range (end before start)?** API returns 400 Bad Request with error message: "Invalid date range: end date must be after start date".

## Requirements *(mandatory)*

### Functional Requirements

#### Browse Functionality

- **FR-001**: Frontend MUST provide a Browse page at root path `/` that displays all registrations
- **FR-002**: Browse page MUST show only "Approved" registrations to non-admin users
- **FR-003**: Browse page MUST show all registrations (Pending, Approved, Rejected) to admin users with clear visual status indicators (badges or labels)
- **FR-004**: Each registration in the Browse view MUST display: endpoint name, endpoint URL, status, owner contact, description (truncated to 150 characters), submission date
- **FR-005**: Browse page MUST implement pagination showing 20 registrations per page with either page numbers or infinite scroll
- **FR-006**: Browse page MUST provide real-time search functionality filtering by endpoint name, description, and owner contact (case-insensitive partial matching)
- **FR-007**: Browse page MUST provide a detailed view (modal or separate page) showing all registration metadata when a user clicks on a registration
- **FR-008**: Detailed view MUST display: endpoint URL, name, description (full text), owner contact, available tools (list), status, submitter name and email, submission date, approver name (if approved/rejected), approval/rejection date (if approved/rejected)
- **FR-009**: Browse page MUST display an empty state message when no registrations exist or no results match search criteria
- **FR-010**: Browse page MUST be responsive and function correctly on mobile (320px+), tablet (768px+), and desktop (1024px+) viewports

#### Approval Status Query API

- **FR-011**: Backend MUST provide GET `/registrations/by-url` endpoint accepting `endpoint_url` query parameter
- **FR-012**: Query endpoint MUST return full registration details (same schema as GET `/registrations/{id}`) when URL matches exactly
- **FR-013**: Query endpoint MUST return HTTP 404 with message "No registration found for this endpoint URL" when URL does not exist
- **FR-014**: Query endpoint MUST require valid Entra ID authentication token (return 401 if missing/invalid)
- **FR-015**: Query endpoint MUST complete within 200ms for 95% of requests
- **FR-016**: Query endpoint MUST handle URL-encoded parameters correctly (decode before database lookup)
- **FR-017**: Backend MUST create a database index on `registrations.endpoint_url` column if not already present for fast lookups

#### Audit Logging

- **FR-018**: Backend MUST create audit log entries automatically for all registration modifications: Create, Approve, Reject, Update, Delete
- **FR-019**: Audit log entry MUST capture: log_id (UUID), registration_id, user_id (who performed action), action (enum: Created/Approved/Rejected/Updated/Deleted), previous_status, new_status, metadata (JSON), timestamp
- **FR-020**: Create action MUST record metadata including all initial registration field values
- **FR-021**: Approve/Reject actions MUST record metadata including optional reason text provided by admin
- **FR-022**: Update action MUST record metadata including which fields changed and their before/after values
- **FR-023**: Delete action MUST create audit log entry before deletion, and audit log MUST be retained even after registration is deleted
- **FR-024**: Backend MUST provide GET `/audit-logs` endpoint with filtering parameters: `registration_id`, `user_id`, `action`, `from` (date), `to` (date), `limit`, `offset`
- **FR-025**: Audit log endpoint MUST require admin privileges (return 403 Forbidden for non-admin users)
- **FR-026**: Audit log endpoint MUST return results in reverse chronological order (newest first)
- **FR-027**: Audit log endpoint MUST support pagination with default limit=50, max limit=200
- **FR-028**: Audit log endpoint MUST validate date range parameters and return 400 if end date is before start date
- **FR-029**: Database MUST maintain indexes on audit_log table for: `registration_id`, `user_id`, `timestamp` (existing in schema)
- **FR-030**: Audit logging MUST be implemented as part of the same database transaction as the operation being logged (atomic)

### Key Entities

- **Registration** (existing): No schema changes needed. Existing fields support all Browse functionality requirements.

- **AuditLog** (existing in schema, needs service implementation): Represents a change event for a registration. Attributes: log_id (UUID primary key), registration_id (foreign key), user_id (foreign key), action (enum: Created/Approved/Rejected/Updated/Deleted), previous_status (text, nullable), new_status (text, nullable), metadata (JSONB for flexible data like reasons, field changes), timestamp (timestamptz). Relationships: belongs to one Registration (may be deleted), belongs to one User (actor who made change).

- **QueryResult**: Not a stored entity, but the response format for GET `/registrations/by-url` endpoint. Same schema as RegistrationResponse from existing API.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can discover any approved MCP endpoint within 3 seconds using the Browse page search functionality
- **SC-002**: Browse page loads and displays first 20 registrations within 2 seconds on standard network connection
- **SC-003**: 95% of approval status queries via API complete within 200ms
- **SC-004**: 100% of registration modifications (create, approve, reject, update, delete) generate corresponding audit log entries
- **SC-005**: Audit log queries return results within 1 second even with 10,000+ audit entries in the database
- **SC-006**: Browse page detailed view shows all registration metadata in a readable format within 1 second of clicking a registration
- **SC-007**: Non-admin users viewing Browse page see only Approved registrations with 100% accuracy (no Pending or Rejected items)
- **SC-008**: Admin users viewing Browse page see all registrations with accurate status badges (color-coded or labeled) with 100% accuracy
- **SC-009**: Search/filter functionality on Browse page returns results within 500ms as user types
- **SC-010**: Audit logs retain entries for deleted registrations indefinitely, supporting compliance requirements

### Assumptions

- PostgreSQL database with existing schema from feature 002 is available and running in Azure
- Existing backend API endpoints for registration CRUD operations are functional
- Frontend is built with React, TypeScript, and Tailwind CSS (per feature 001)
- Backend uses FastAPI with Python 3.13+ and asyncpg for database access (per feature 002)
- Authentication via Microsoft Entra ID using MSAL is implemented and working (per feature 001)
- Admin status is determined by Entra ID group membership (per features 001 and 002)
- The audit_log table already exists in the database schema (per feature 002, init_schema.sql)
- Standard web browser expectations for load times (2-3 seconds on 4G/broadband connections)
- Database has sufficient storage for audit logs (estimate: 1KB per audit entry, 100K entries = ~100MB)
- Audit log retention is indefinite (no automatic archival/purging in this feature)
- URL normalization (http vs https, trailing slashes) is handled consistently by frontend when submitting registrations
- Browse page will initially load all registrations and filter client-side, with server-side pagination as future optimization if needed
- Search functionality uses existing backend GET `/registrations` endpoint with search parameter (FR-003 from feature 002)

### Out of Scope

- Real-time updates on Browse page (WebSocket or polling) - users must refresh to see changes
- Advanced filtering UI (dropdowns for status, date ranges, owner) - basic search box only
- Sorting options (by name, date, status) - default sort is by submission date descending
- Export functionality for Browse results (CSV, Excel) - future enhancement
- Bulk operations on multiple registrations from Browse page
- Audit log viewer UI in frontend (admin can view via API calls only)
- Audit log retention policies and automatic archival
- Audit log export or reporting dashboards
- Notification system when registrations are approved/rejected
- Public (unauthenticated) Browse page for approved endpoints - all users must login
- Detailed field-level change tracking in audit logs beyond status changes (future enhancement)
- Compliance reports or analytics based on audit logs
- Integration with external SIEM (Security Information and Event Management) systems
- Rate limiting on approval status query API
- Caching layer for frequently queried endpoints
