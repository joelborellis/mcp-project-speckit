# Feature Specification: FastAPI Backend with PostgreSQL Database

**Feature Branch**: `002-fastapi-postgres-backend`  
**Created**: 2025-11-11  
**Status**: Draft  
**Input**: User description: "We are building the backend for our application that serves routes/endpoints to create, update and fetch data related to the MCP Registry application. This backend will use a PostgresSQL database running in Azure to store data. This will replace the current IndexedDB the frontend is currently using."

## Clarifications

### Session 2025-11-11

- Q: Should the FastAPI backend validate Entra ID tokens on each request, or trust that the frontend has already validated them? → A: Backend validates all Entra ID tokens on every request using Microsoft's token validation libraries
- Q: How should the "available_tools" field be stored in the PostgreSQL database? → A: PostgreSQL JSONB column
- Q: Should the API include versioning from the start, and if so, what strategy? → A: No versioning initially
- Q: What logging approach should the backend implement? → A: Structured JSON logging with standard levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Q: How should the system handle concurrent duplicate endpoint submissions? → A: Database unique constraint on endpoint_url

## User Scenarios & Acceptance *(mandatory)*

### User Story 1 - API Endpoints for MCP Registry Data (Priority: P1)

The frontend application needs RESTful API endpoints to create, retrieve, update, and delete MCP endpoint registrations. These endpoints must replace the current IndexedDB functionality and support the same workflows (registration, approval, browsing).

**Why this priority**: This is the foundational infrastructure that all other features depend on. Without these core CRUD endpoints, the application cannot function. This delivers immediate value by enabling persistent storage across users and sessions.

**Manual Verification**: 
1. Start the FastAPI backend server
2. Use a REST client (Postman, curl, or browser) to test each endpoint
3. Verify POST /registrations creates a new pending registration
4. Verify GET /registrations retrieves all registrations (with filtering options)
5. Verify PATCH /registrations/{id}/status updates approval status
6. Verify GET /registrations/{id} retrieves specific registration details
7. Check that data persists after server restart by querying the database

**Acceptance Scenarios**:

1. **Given** the API is running, **When** a POST request with valid registration data is sent to /registrations, **Then** a new registration is created with "Pending" status and a unique ID is returned
2. **Given** registrations exist in the database, **When** a GET request is sent to /registrations, **Then** all registrations are returned with their metadata
3. **Given** a registration exists, **When** an admin sends a PATCH request to /registrations/{id}/status with status "Approved", **Then** the registration status is updated to "Approved"
4. **Given** a specific registration ID exists, **When** a GET request is sent to /registrations/{id}, **Then** the full registration details are returned
5. **Given** invalid data is sent to an endpoint, **When** the request is processed, **Then** appropriate HTTP error codes (400, 404, 422) and error messages are returned

---

### User Story 2 - User Management and Authentication Support (Priority: P1)

The backend needs endpoints to support user authentication workflows and role management. This includes verifying user identity from Microsoft Entra ID and determining admin privileges based on group membership.

**Why this priority**: Essential for security and role-based access control. Without user management, the system cannot enforce approval workflows or track who submitted registrations. This is required for all authenticated operations.

**Manual Verification**:
1. Send a POST request to create/verify a user record with Entra ID information
2. Verify GET /users/{id} returns user details including admin status
3. Test endpoint that checks if a user is an admin based on Entra ID group membership
4. Verify user information is correctly stored and retrieved from database
5. Check that submitter identity is properly linked to registrations

**Acceptance Scenarios**:

1. **Given** a user authenticates via Entra ID, **When** their token is validated, **Then** their user record is created or updated in the database
2. **Given** a user exists, **When** a GET request is sent to /users/{id}, **Then** their profile including role information is returned
3. **Given** a user's Entra ID token contains admin group membership, **When** their role is checked, **Then** they are identified as an admin
4. **Given** a registration is submitted, **When** it is created, **Then** the submitter's user ID is associated with the registration
5. **Given** an invalid user ID is provided, **When** a request is made, **Then** a 404 error is returned

---

### User Story 3 - Database Schema and Migration Scripts (Priority: P1)

The system needs SQL scripts to create and maintain PostgreSQL database tables and objects. These scripts must be runnable to set up new environments or update existing ones as the schema evolves.

**Why this priority**: Without a properly structured database, no data can be stored or retrieved. This is foundational infrastructure that must be in place before any API functionality works. Migration scripts enable consistent deployment across environments.

**Manual Verification**:
1. Run the initial schema creation script against a fresh PostgreSQL database
2. Verify all tables are created with correct columns and data types
3. Verify indexes are created on appropriate columns
4. Run the script again and verify it handles existing tables gracefully (idempotent)
5. Check that foreign key relationships are properly established
6. Test a sample migration script that adds a new column

**Acceptance Scenarios**:

1. **Given** a fresh PostgreSQL database, **When** the schema creation script is executed, **Then** all required tables (users, registrations, audit_log) are created
2. **Given** tables are created, **When** they are inspected, **Then** all columns have correct data types, constraints, and default values
3. **Given** performance requirements, **When** the schema is reviewed, **Then** appropriate indexes exist on frequently queried columns (user_id, status, created_at)
4. **Given** the schema script is run on an existing database, **When** it executes, **Then** it completes without errors (using CREATE TABLE IF NOT EXISTS or equivalent)
5. **Given** relationships between entities, **When** foreign keys are examined, **Then** proper constraints exist between users and registrations tables

---

### User Story 4 - Frontend Integration Updates (Priority: P2)

The existing frontend application needs to be updated to use the new backend API endpoints instead of IndexedDB. This includes modifying the data service layer to make HTTP requests and handle API responses.

**Why this priority**: Important for delivering the full value of the backend, but depends on the API endpoints being implemented (US1 - P1). The frontend can continue using IndexedDB until this migration is complete.

**Manual Verification**:
1. Start both frontend and backend servers
2. Login to the frontend application
3. Register a new MCP endpoint and verify it's saved to the database (not IndexedDB)
4. Refresh the page and verify data persists from the database
5. As admin, approve/reject an endpoint and verify the action calls the backend API
6. Check browser developer tools to confirm HTTP requests are being made to backend endpoints
7. Verify IndexedDB is no longer being used for registration storage

**Acceptance Scenarios**:

1. **Given** the frontend data service, **When** a user submits a registration, **Then** an HTTP POST request is sent to the backend API instead of writing to IndexedDB
2. **Given** the user views the registry, **When** the page loads, **Then** data is fetched from the backend API via HTTP GET
3. **Given** an admin performs an approval action, **When** they click approve/reject, **Then** an HTTP PATCH request updates the backend
4. **Given** API errors occur, **When** requests fail, **Then** the frontend displays user-friendly error messages
5. **Given** the migration is complete, **When** the application is inspected, **Then** no IndexedDB operations are performed for registration data

---

### User Story 5 - Azure PostgreSQL Database Configuration (Priority: P2)

The backend needs to connect securely to an Azure-hosted PostgreSQL database. This includes configuration for connection strings, authentication, and environment-specific settings.

**Why this priority**: Critical for production deployment but can use local PostgreSQL during development. Requires the schema scripts (US3 - P1) to be available to initialize the Azure database.

**Manual Verification**:
1. Create an Azure PostgreSQL database instance
2. Run the schema scripts against the Azure database
3. Configure the backend with Azure database connection string
4. Start the backend and verify it connects to Azure PostgreSQL
5. Test API endpoints and confirm data is being stored in Azure
6. Verify connection pooling and SSL/TLS configuration
7. Check that connection credentials are stored securely (environment variables, not hardcoded)

**Acceptance Scenarios**:

1. **Given** an Azure PostgreSQL instance exists, **When** the backend starts, **Then** it successfully connects using credentials from environment variables
2. **Given** the backend is configured for Azure, **When** API requests are made, **Then** data is persisted to the Azure database
3. **Given** security requirements, **When** the connection is established, **Then** SSL/TLS encryption is enforced
4. **Given** multiple environments (dev, staging, prod), **When** the backend is deployed, **Then** it uses the correct connection string for each environment
5. **Given** connection failures, **When** the database is unreachable, **Then** the backend logs errors and returns appropriate HTTP 503 responses

---

### Edge Cases

- **What happens when the database connection is lost during a request?** The API should return HTTP 503 errors and attempt to reconnect. Pending requests should fail gracefully with error messages.
- **What happens when concurrent requests try to update the same registration status?** Database transactions and optimistic locking should prevent conflicting updates. Last write wins or version-based conflict detection.
- **What happens when the frontend sends a registration for an endpoint URL that already exists?** The database unique constraint on endpoint_url prevents the duplicate insertion, and the API catches the constraint violation and returns a 409 Conflict error with details about the existing registration.
- **What happens when two users simultaneously submit the exact same endpoint URL?** The database unique constraint handles the race condition automatically - the first transaction to commit succeeds, the second receives a constraint violation error and returns HTTP 409 Conflict to the user.
- **What happens when database migration scripts are run on an already-migrated database?** Scripts should be idempotent (using CREATE TABLE IF NOT EXISTS, ALTER TABLE IF NOT EXISTS patterns) to safely run multiple times.
- **What happens when a user's Entra ID token is invalid or expired during an API call?** The API should return HTTP 401 Unauthorized and the frontend should prompt for re-authentication.
- **What happens when the Azure PostgreSQL database reaches storage limits?** The system should log warnings and fail gracefully with HTTP 507 errors when inserts fail due to storage constraints.
- **What happens when a registration is deleted from the database while a user is viewing it in the frontend?** The frontend should handle 404 responses gracefully and refresh the view.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a RESTful API built with FastAPI framework
- **FR-002**: System MUST implement POST /registrations endpoint to create new MCP endpoint registrations with "Pending" status
- **FR-003**: System MUST implement GET /registrations endpoint to retrieve all registrations with optional filtering by status, owner, and search terms
- **FR-004**: System MUST implement GET /registrations/{id} endpoint to retrieve a specific registration by ID
- **FR-005**: System MUST implement PATCH /registrations/{id}/status endpoint to update approval status (admin only)
- **FR-006**: System MUST implement DELETE /registrations/{id} endpoint to remove a registration (admin only)
- **FR-007**: System MUST implement POST /users endpoint to create or update user records from Entra ID authentication
- **FR-008**: System MUST implement GET /users/{id} endpoint to retrieve user profile including admin status
- **FR-009**: System MUST store data in a PostgreSQL database hosted in Azure
- **FR-010**: System MUST provide SQL scripts to create database schema including tables for users, registrations, and audit logs
- **FR-011**: System MUST provide SQL migration scripts that are idempotent and can be safely run multiple times
- **FR-012**: System MUST validate all API request payloads and return appropriate HTTP error codes (400 Bad Request, 422 Unprocessable Entity)
- **FR-013**: System MUST return proper HTTP status codes for all responses (200, 201, 400, 401, 404, 409, 503)
- **FR-014**: System MUST use environment variables for database connection credentials and Azure configuration
- **FR-015**: System MUST implement database connection pooling for efficient resource usage
- **FR-016**: System MUST enforce SSL/TLS encryption for database connections to Azure PostgreSQL
- **FR-017**: System MUST implement structured JSON logging with standard levels (DEBUG, INFO, WARNING, ERROR, CRITICAL) for all database connection errors, API errors, and operational events
- **FR-018**: System MUST validate Entra ID authentication tokens on every API request using Microsoft's token validation libraries
- **FR-019**: Frontend MUST replace IndexedDB calls with HTTP requests to backend API endpoints
- **FR-020**: Frontend MUST handle API errors gracefully with user-friendly error messages
- **FR-021**: Frontend MUST include authentication tokens in API requests for user identification
- **FR-022**: System MUST store registration metadata including name, endpoint URL, description, owner, available tools, status, submitter ID, submission timestamp, approver ID, and approval timestamp
- **FR-023**: System MUST validate endpoint URLs for proper format before storing in database
- **FR-024**: System MUST enforce unique constraint on endpoint_url column in the database to prevent duplicate registrations
- **FR-025**: System MUST detect database unique constraint violations and return HTTP 409 Conflict errors with details about the existing registration
- **FR-026**: System MUST create database indexes on frequently queried columns (user_id, status, created_at, endpoint_url)
- **FR-027**: System MUST maintain referential integrity with foreign key constraints between users and registrations tables
- **FR-028**: System MUST support CORS configuration to allow frontend requests from approved origins
- **FR-029**: System MUST implement health check endpoint (GET /health) for monitoring and load balancer checks
- **FR-030**: System MUST return HTTP 401 Unauthorized for requests with invalid, expired, or missing Entra ID tokens
- **FR-031**: System MUST implement GET /users/me endpoint to retrieve current authenticated user's profile

### Key Entities

- **User**: Represents an authenticated individual from Microsoft Entra ID. Attributes include user_id (primary key), entra_id (external ID from Entra ID), email, display_name, is_admin (boolean), created_at, updated_at. Relationships: one user can submit many registrations.

- **Registration**: Represents a registered MCP endpoint. Attributes include registration_id (primary key), endpoint_url, endpoint_name, description, owner_contact, available_tools (JSONB column storing tool names and optional metadata), status (enum: Pending/Approved/Rejected), submitter_id (foreign key to User), approver_id (foreign key to User, nullable), submitted_at, approved_at (nullable), created_at, updated_at. Relationships: belongs to one submitter (User), optionally belongs to one approver (User).

- **AuditLog** (optional): Represents changes to registrations for compliance tracking. Attributes include log_id (primary key), registration_id (foreign key), user_id (foreign key), action (enum: Created/Approved/Rejected/Updated/Deleted), previous_status, new_status, timestamp, metadata (JSON).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: API endpoints respond to requests within 200ms for 95% of requests under normal load (excluding network latency)
- **SC-002**: Database schema scripts successfully create all tables and indexes on fresh PostgreSQL database in under 10 seconds
- **SC-003**: Backend successfully connects to Azure PostgreSQL database within 5 seconds of startup
- **SC-004**: All frontend data operations (create, read, update, delete) complete successfully via API calls with 99% success rate
- **SC-005**: API supports at least 100 concurrent requests without performance degradation
- **SC-006**: Frontend completes migration from IndexedDB to backend API with no loss of existing functionality
- **SC-007**: Database connection pool maintains stable connections with less than 1% connection failure rate
- **SC-008**: API returns appropriate HTTP status codes for all error conditions (100% accuracy)
- **SC-009**: All sensitive configuration (database credentials, connection strings) is stored in environment variables, not hardcoded (100% compliance)
- **SC-010**: Health check endpoint returns status within 100ms for monitoring systems

### Assumptions

- Azure PostgreSQL database instance is provisioned and accessible from the backend application
- Network connectivity exists between the backend server and Azure database with acceptable latency
- FastAPI framework and Python 3.13+ are used for backend development
- Environment variables or Azure Key Vault are available for secure credential storage
- The existing frontend is already using TypeScript with a service layer that abstracts data access
- Microsoft Entra ID authentication tokens can be passed from frontend to backend for user identification
- Database schema changes will be infrequent enough that manual migration scripts are acceptable (no need for automated migration tools initially)
- PostgreSQL database has sufficient storage capacity (at least 10GB initially)
- Backend will initially be deployed as a single instance (horizontal scaling is future enhancement)
- CORS configuration will allow requests from the frontend domain
- Standard HTTP RESTful conventions will be followed for endpoint design
- JSON will be used as the data interchange format for all API requests and responses
- API versioning is not required initially; versioning strategy can be introduced when breaking changes become necessary

### Out of Scope

- Advanced caching mechanisms (Redis, CDN)
- Real-time WebSocket connections for live updates
- Automated database migration tools (Alembic, Flyway)
- Horizontal scaling and load balancing (single instance deployment initially)
- Comprehensive API documentation (Swagger/OpenAPI can be added later)
- Rate limiting and throttling
- Advanced analytics or reporting endpoints
- Bulk import/export endpoints
- Endpoint health monitoring or validation
- Email notification system for approval status changes
- GraphQL API (REST only)
- Multi-region database replication
- Automated backup and restore procedures (handled by Azure)
- Performance monitoring and APM integration
- CI/CD pipeline configuration
