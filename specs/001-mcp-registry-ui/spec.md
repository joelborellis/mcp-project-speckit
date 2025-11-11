# Feature Specification: MCP Registry Web Application

**Feature Branch**: `001-mcp-registry-ui`  
**Created**: 2025-11-11  
**Status**: Draft  
**Input**: User description: "Web-based MCP registry UI with admin approval and Microsoft Entra ID authentication"

## Clarifications

### Session 2025-11-11

- Q: How should the system determine if a user has admin privileges? → A: Entra ID security group membership (e.g., user belongs to "MCP-Registry-Admins" group)
- Q: Which browser storage mechanism should be used for endpoint metadata? → A: IndexedDB (structured database, ~50MB+ limit, asynchronous API, supports indexes and queries)
- Q: How should users specify the available tools/capabilities when registering an MCP endpoint? → A: Comma-separated list of tool names (e.g., "search, analyze, summarize")
- Q: What happens to rejected endpoint registrations? → A: Store with "Rejected" status
- Q: Should we define the primary red color now, or defer all color decisions to the planning/design phase? → A: Defer to design phase

## User Scenarios & Acceptance *(mandatory)*

### User Story 1 - User Authentication and Authorization (Priority: P1)

Users need to securely access the MCP Registry web application using their organizational credentials. The system must distinguish between regular users and administrators to control access to administrative functions.

**Why this priority**: Authentication is foundational—no other features can be used without secure user access. This establishes the security boundary and role-based access control that all subsequent features depend on.

**Manual Verification**: 
1. Navigate to the application root URL
2. Verify Microsoft Entra ID login page appears
3. Login with test user credentials
4. Verify successful redirect to main dashboard
5. Login with admin credentials and verify admin-only features are visible
6. Login with regular user credentials and verify admin features are hidden

**Acceptance Scenarios**:

1. **Given** a user navigates to the application, **When** they are not authenticated, **Then** they are redirected to Microsoft Entra ID login
2. **Given** a user successfully authenticates, **When** they access the dashboard, **Then** their role (Admin or User) is correctly identified and appropriate UI elements are displayed
3. **Given** an unauthenticated user attempts to access protected routes, **When** the request is made, **Then** they are redirected to login
4. **Given** a regular user is authenticated, **When** they attempt to access admin-only features, **Then** those features are not visible or accessible
5. **Given** an admin user is authenticated, **When** they access the application, **Then** all admin approval and management features are available

---

### User Story 2 - Browse and Search MCP Registry (Priority: P1)

Users need to discover and explore registered MCP endpoints through an intuitive, searchable interface. The registry must provide clear visibility into available endpoints, their metadata, and organizational information.

**Why this priority**: This is the core value proposition—centralizing discovery of MCP servers. Without browsing and search, the registry has no utility. This delivers immediate value even before registration workflows.

**Manual Verification**:
1. Login as any authenticated user
2. Navigate to main registry view
3. Verify list of approved MCP endpoints displays
4. Use search box to filter by endpoint name
5. Click on an endpoint to view detailed metadata
6. Verify red and white color scheme is applied throughout
7. Test responsive behavior on mobile device or narrow browser window

**Acceptance Scenarios**:

1. **Given** a user is on the main registry page, **When** they view the endpoint list, **Then** all approved endpoints are displayed with name, status, and owner information
2. **Given** multiple endpoints exist, **When** a user types in the search box, **Then** results filter in real-time to match the search term against endpoint name, owner, or metadata
3. **Given** a user selects an endpoint from the list, **When** they click to view details, **Then** a detailed view shows all metadata including name, host/IP, owner, available tools, and approval status
4. **Given** the interface is displayed, **When** viewed on any device, **Then** the layout adapts responsively with red and white color scheme maintained
5. **Given** no endpoints exist or search returns no results, **When** the list is empty, **Then** a helpful message guides the user on next steps

---

### User Story 3 - Register New MCP Endpoint (Priority: P2)

Regular users need the ability to submit new MCP endpoints for registration. The system must capture all necessary metadata and place submissions into a pending state awaiting admin approval.

**Why this priority**: This enables users to contribute to the registry, but depends on authentication (US1 - P1). It's less critical than browsing because initial value comes from viewing existing endpoints.

**Manual Verification**:
1. Login as a regular user
2. Navigate to "Register Endpoint" or similar action
3. Fill in the registration form with endpoint URL and metadata
4. Submit the registration
5. Verify success message and pending status
6. As admin, verify the endpoint appears in pending approvals list

**Acceptance Scenarios**:

1. **Given** an authenticated user is on the registration page, **When** they enter a valid MCP endpoint URL, **Then** the system validates the URL format
2. **Given** a user fills out all required metadata fields (name, description, owner contact), **When** they submit the form, **Then** the endpoint is saved with "Pending" status
3. **Given** a user submits an endpoint, **When** the submission is successful, **Then** they receive confirmation and can see their submission in a "My Registrations" view
4. **Given** a user enters invalid or incomplete information, **When** they attempt to submit, **Then** clear validation messages indicate which fields need correction
5. **Given** an endpoint is submitted, **When** the system stores it, **Then** all metadata is captured including submitter identity, timestamp, and pending approval status

---

### User Story 4 - Admin Approval Workflow (Priority: P2)

Administrators need to review pending MCP endpoint registrations and approve, reject, or remove them. This ensures only vetted endpoints become discoverable in the registry.

**Why this priority**: Critical for governance and security, but requires authentication (US1 - P1) and registration submissions (US3 - P2) to have content to approve. Enables controlled onboarding.

**Manual Verification**:
1. Login as an admin user
2. Navigate to "Pending Approvals" section
3. View list of pending endpoint registrations
4. Select a pending endpoint and review its metadata
5. Click "Approve" and verify it moves to approved list
6. Submit another endpoint as regular user
7. Reject it as admin and verify it's removed or marked rejected
8. Approve an endpoint then remove it from approved list

**Acceptance Scenarios**:

1. **Given** an admin is viewing pending approvals, **When** they see the list, **Then** all pending endpoints are displayed with key metadata and submission timestamp
2. **Given** an admin selects a pending endpoint, **When** they review details, **Then** full metadata including submitter, endpoint URL, and description are visible
3. **Given** an admin approves an endpoint, **When** approval is confirmed, **Then** the endpoint status changes to "Approved" and it becomes visible in the main registry
4. **Given** an admin rejects an endpoint, **When** rejection is confirmed, **Then** the endpoint status changes to "Rejected", it does not appear in the main registry, but is retained in the system for audit purposes
5. **Given** an admin views approved endpoints, **When** they select one, **Then** they have the option to remove it, which changes its status and removes it from public view
6. **Given** an approval action is taken, **When** the status changes, **Then** the submitting user can see the updated status of their registration

---

### Edge Cases

- **What happens when a user submits a duplicate endpoint URL?** System should detect and warn that this endpoint is already registered or pending
- **What happens when Microsoft Entra ID authentication fails or times out?** User receives clear error message and option to retry
- **What happens when an admin attempts to approve an endpoint that was deleted by another admin?** System prevents the action and displays current state
- **What happens when a user's session expires during registration?** Form data is preserved where possible, user is prompted to re-authenticate
- **What happens when an endpoint URL becomes invalid after approval?** Admin can update metadata or remove the endpoint
- **What happens when a submitter views their rejected registration?** The "My Registrations" view displays the rejected status and the endpoint remains in IndexedDB for audit trail

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST authenticate users via Microsoft Entra ID using MSAL libraries
- **FR-002**: System MUST distinguish between "Admin" and "User" roles by checking Entra ID security group membership (users in "MCP-Registry-Admins" group have admin privileges)
- **FR-003**: System MUST store endpoint metadata including name, host/IP, owner, approval status, available tools, submitter identity, and submission timestamp
- **FR-004**: System MUST use IndexedDB for metadata persistence in the frontend browser storage
- **FR-005**: System MUST display all approved MCP endpoints in a browsable list view
- **FR-006**: System MUST provide real-time search/filter capability across endpoint name, owner, and metadata
- **FR-007**: System MUST provide a registration form for users to submit new MCP endpoints with required metadata (name, description, owner contact, endpoint URL, comma-separated list of available tools)
- **FR-008**: System MUST place newly registered endpoints in "Pending" status until admin approval
- **FR-009**: System MUST provide an admin-only view of pending endpoint registrations
- **FR-010**: System MUST allow admins to approve, reject, or remove endpoint registrations
- **FR-011**: System MUST transition approved endpoints from "Pending" to "Approved" status and make them visible in the main registry
- **FR-012**: System MUST retain rejected endpoints with "Rejected" status for audit purposes (not visible in main registry)
- **FR-013**: System MUST apply red and white color palette consistently throughout the UI
- **FR-021**: System MUST implement responsive design that works on mobile, tablet, and desktop viewports
- **FR-014**: System MUST validate endpoint URLs for proper format before submission
- **FR-015**: System MUST display clear validation messages for form errors
- **FR-016**: System MUST show submitter's own registrations in a dedicated view
- **FR-017**: System MUST prevent unauthenticated access to protected routes
- **FR-018**: System MUST hide admin-only features from regular users
- **FR-019**: System MUST provide detailed metadata view when an endpoint is selected
- **FR-020**: System MUST track and display timestamp of when each endpoint was registered

### Key Entities

- **User**: Represents an authenticated individual from Microsoft Entra ID directory. Has role (Admin or User), identity information, and can submit endpoint registrations. Admins can approve/reject/remove endpoints.

- **MCP Endpoint**: Represents a registered Model Context Protocol server. Attributes include unique identifier, endpoint URL (host/IP), name, description, owner/contact information, comma-separated list of available tools, approval status (Pending/Approved/Rejected), submitter identity, submission timestamp, approval/rejection timestamp, and approval/rejection admin identity.

- **Registration Submission**: Represents a user's request to add an MCP endpoint. Contains all MCP Endpoint metadata plus submission context (who submitted, when, current status in approval workflow).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can authenticate and access the application within 10 seconds of clicking login
- **SC-002**: Users can discover an existing approved endpoint within 3 clicks or a single search query
- **SC-003**: Users can complete the endpoint registration form in under 2 minutes
- **SC-004**: Admins can review and approve/reject a pending endpoint in under 1 minute
- **SC-005**: Search results filter in real-time with less than 500ms delay as users type
- **SC-006**: The application displays correctly and is fully functional on viewports ranging from 320px (mobile) to 1920px (desktop) width
- **SC-007**: 95% of registration form submissions succeed on first attempt without validation errors (when valid data is provided)
- **SC-008**: The red and white color scheme is consistently applied across all pages and components
- **SC-009**: Unauthorized users attempting to access protected routes are redirected to login within 1 second
- **SC-010**: Admin approval actions (approve/reject/remove) complete and update the UI within 2 seconds

### Assumptions

- Microsoft Entra ID tenant is already configured and accessible
- Admin designation is managed through Entra ID security group membership (e.g., "MCP-Registry-Admins" group)
- Initial dataset will contain fewer than 1000 endpoints (IndexedDB can accommodate this comfortably)
- Backend API endpoints are defined and will be integrated in future phases—this specification focuses on UI/UX with local data storage
- Users have modern browsers (Chrome, Firefox, Edge, Safari) with JavaScript enabled
- MCP endpoint URLs follow standard URL format (http/https protocols)
- Available tools are specified as a comma-separated list (e.g., "search, analyze, summarize, code-generation")
- Red and white palette specifics (exact hex codes, usage guidelines) will be defined during design phase

### Out of Scope

- Backend API integration (future phase)
- MCP endpoint health monitoring or validation
- Bulk import/export of endpoints
- Email notifications for approval status changes
- Advanced analytics or usage tracking
- Multi-tenant support (single Entra ID directory only)
- Endpoint versioning or history tracking
- Custom role definitions beyond Admin/User
