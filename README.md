# MCP Registry Project: A SpecKit Process Demonstration

## Overview

This project demonstrates the **Spec driven development approach** using the tool **SpecKit** (https://github.com/github/spec-kit) I was anxious to try a specification-driven development approach designed for pre-sales technical engineers to rapidly prototype enterprise solutions during short customer engagements (typically 2-3 days). Rather than a traditional README explaining how to run the code, this document chronicles the **process** used to create a fully functional enterprise MCP (Model Context Protocol) Registry using SpecKit.

**Want to see what it looks like?** Check out the [`screenshots/`](screenshots/) directory for visual examples of the application in action.

## The Challenge

Pre-sales technical engineers face a unique challenge: they need to engage with customers, gather requirements, and deliver working prototypes that demonstrate technical capabilities—all within extremely compressed timeframes. Traditional development approaches are too slow; pure mockups lack credibility; Demos are cool but sometimes not specific enough to customer specifications. SpecKit bridges this gap by combining specification rigor with AI-assisted rapid development.

## Learnings: GitHub Copilot as a Coding Partner

Throughout this project, **GitHub Copilot** proved to be an exceptional coding agent and development partner. What impressed me most was its ability to maintain context and coherence throughout the entire SpecKit process—never getting lost despite the complexity and multi-phase nature of the engagement.

**Key Observations**:

- **Context Retention**: Copilot understood the full scope across both feature branches (frontend and backend), remembering architectural decisions, naming conventions, and design patterns established early in the process.

- **Beyond Code Generation**: This wasn't just about writing TypeScript and Python. Copilot seamlessly generated:
  - **PowerShell Scripts**: Complete automation for Entra ID app registration and admin group setup
  - **SQL Scripts**: PostgreSQL schema with proper indexes, constraints, and triggers
  - **Configuration Files**: `.env` templates, CORS settings, MSAL configurations
  - **Documentation**: Setup guides, API documentation, and troubleshooting instructions

- **Complex Integration Handling**: The project required orchestrating multiple enterprise systems:
  - Microsoft Entra ID (authentication, group-based authorization)
  - Azure PostgreSQL (connection pooling, SSL/TLS, environment-specific configs)
  - FastAPI backend with JWT validation
  - React frontend with MSAL browser libraries
  
  Copilot navigated these dependencies confidently, suggesting correct patterns for each integration point.

- **True "Buddy Coding" Experience**: Rather than feeling like a tool I was directing, Copilot felt like a knowledgeable pair programmer who:
  - Anticipated next steps in the implementation
  - Caught potential issues (route ordering in FastAPI, JSONB serialization)
  - Suggested best practices aligned with the constitutional principles
  - Adapted to feedback and course corrections without losing momentum

- **SpecKit Process Alignment**: Copilot excelled at each phase:
  - **Specify**: Helped transform vague requirements into structured user stories
  - **Plan**: Generated technical architecture matching constitutional constraints
  - **Tasks**: Broke down plans into granular, actionable tasks with dependencies
  - **Implement**: Produced production-quality code across multiple languages and frameworks

**The Bottom Line**: For solution engineers using SpecKit, GitHub Copilot isn't just a productivity tool—it's a force multiplier that makes rapid prototyping with customers genuinely feasible. The combination of structured specifications (SpecKit) and contextual code generation (Copilot) delivers working enterprise applications in days instead of weeks.

## What is SpecKit?

SpecKit is a **Specification-Driven Development (SDD)** methodology that inverts traditional development: instead of writing code that you hope matches requirements, you write executable specifications that *generate* code. The specification becomes the source of truth—code is simply its expression.

**The Power Inversion**: For decades, specifications served code. SpecKit inverts this: code serves specifications. When specifications change, code regenerates. There's no gap between intent and implementation—only transformation.

**Why This is Perfect for Solution Engineers**:

1. **Speed**: Transform vague customer ideas into working prototypes in days, not weeks. Specifications that traditionally take 12+ hours of documentation work now take 15 minutes with SpecKit commands (`/speckit.specify`, `/speckit.plan`, `/speckit.tasks`).

2. **Customer Confidence**: Live with the customer in their language (business requirements), not technical jargon. The specification remains readable by stakeholders while AI handles the translation to code.

3. **Rapid Pivots**: Customer changed their mind? Update the specification and regenerate—pivots become systematic regenerations rather than manual rewrites. Perfect for the "let me show you" moment in sales cycles.

4. **Quality by Design**: Constitutional principles (established upfront) prevent over-engineering and scope creep. Every technical decision traces back to specific requirements, creating instant credibility.

5. **Reusable Assets**: Specifications become portfolio pieces. Similar customer needs? Start with a proven specification and adapt it. Each engagement builds your library of proven patterns.

**The Process**: Constitution → Specify → Clarify → Plan → Tasks → Implement. Each step is structured, AI-assisted, and produces artifacts that customers can review and approve. You're never "heads down coding"—you're continuously validating with stakeholders while AI handles implementation details.

This isn't about replacing engineering—it's about amplifying solution engineers' effectiveness by automating the mechanical translation from customer needs to working demonstrations, letting you focus on understanding requirements and building relationships.

---

## Starting Point: Raw Customer Requirements

Before applying the SpecKit process, this is **all** I had from the customer—raw, unstructured requirements captured during initial discussions:

### Original Customer Requirements (Frontend)

> **Requirement 1**: A customizable, user-friendly web interface to view, search, and manage registered MCP endpoints. Users should have a way to input an MCP endpoint and have it be discovered and registered in the webapp.
>
> **Why It's Important**: Centralizes discovery and management of all MCP servers across teams. Provides transparency for admins and developers without requiring API access. Enables browsing by categories, metadata, and ownership — key for enterprise governance and adoption.

> **Requirement 2**: Admins must be able to approve, reject, or remove MCP endpoint registrations before they become discoverable. When users input an MCP endpoint to be registered, they go into **pending status** until an Admin approves.
>
> **Why It's Important**: Ensures only vetted and secure endpoints are exposed within the enterprise. Supports compliance and data governance policies. Enables controlled onboarding workflows to prevent unauthorized or experimental endpoints from entering production registries.

> **Requirement 3**: Ability to store and manage rich metadata such as endpoint name, IP/host, owner, approval status, and available tools. For the registration process, store this information in a **local data store** for now.
>
> **Why It's Important**: Metadata provides essential context for discovery, auditing, and integration. Enables downstream automation (e.g., approval workflows, ownership tracking). Supports internal cataloging standards and classification frameworks (e.g., by business unit or data type).

> **Requirement 4**: Users must login to the web app. All users will use the same directory for login and there should be ability to designate some users as **Admins**.
>
> **Why It's Important**: The system will have users who can register MCP endpoints and these users need to be tracked. Some users will be admins which have the ability to view registered MCP servers and approve them.

These specifications are for the **web app frontend**. This will be connected eventually to a **FastAPI backend** with defined API endpoints to perform more complex actions. The goal of this specification is to get the UI/UX started, then wire it into the backend.

### Updated Customer Requirements (Backend)

After validating the frontend, the customer came back with:

> **Requirement 5**: Create backend FastAPI app that will support the current features of the frontend application. Update the frontend application to use this new backend.
>
> **Why It's Important**: The backend needs to replace the IndexedDB that currently runs the application. The backend should implement as many routes/endpoints that are required to support the functionality of the frontend.

> **Requirement 6**: Generate scripts to create database tables in PostgreSQL in Azure.
>
> **Why It's Important**: The system might change databases and will need to rebuild the tables and objects in the database.

**That was it.** No user stories, no acceptance criteria, no technical architecture—just high-level business requirements. Everything else you'll see in the following sections was **generated through the SpecKit process**.

---

## The SpecKit Process: Step-by-Step

This project followed the exact SpecKit workflow defined in `instructions.md`. Here's how it unfolded:

### Phase 0: Constitution

**Command**: `/speckit.constitution`

Before any code was written, the project established its **constitution**—a set of non-negotiable principles that would guide all decisions:

#### Core Principles Established:

1. **Clean Code First**: Prioritize readability and maintainability
   - Clear, descriptive naming conventions
   - Small, focused functions and components
   - Self-documenting code over excessive comments
   - Logical file organization reflecting feature boundaries

2. **Simple UX**: Intuitive interfaces requiring minimal learning
   - Clear visual hierarchy
   - Minimal clicks to accomplish goals
   - Consistent interaction patterns
   - Immediate feedback for all user actions

3. **Responsive Design**: Seamless experience across all devices
   - Mobile-first approach with progressive enhancement
   - Touch-friendly interactive elements (44×44px minimum)
   - Fluid layouts adapting to viewport changes

4. **Minimal Dependencies**: Carefully justified external libraries
   - Prefer standard library solutions
   - Choose focused libraries over monolithic frameworks
   - Regular dependency audits
   - Lock versions to prevent breaking changes

5. **No Testing** *(NON-NEGOTIABLE)*: Zero automated testing
   - No unit, integration, or end-to-end tests
   - No test frameworks or testing infrastructure
   - Quality assurance through clean code and manual verification
   - All energy directed toward production code quality

**Technology Stack Locked**:
- **Frontend**: React 19.2.0, TypeScript 5.9.3, Vite 7.2.2, Tailwind CSS
- **Backend**: Python 3.13+, FastAPI, PostgreSQL, Azure deployment

**Why This Matters**: The constitution prevented scope creep, established clear technical boundaries, and ensured consistency across two separate feature branches. The "no testing" principle is particularly important for rapid prototyping—all effort goes into demonstrable functionality.

---

### Phase 1: Specification - Frontend (Branch 001)

**Command**: `/speckit.specify`

**Requirements Gathered**:
The customer needed an enterprise-wide registry for MCP (Model Context Protocol) servers where:
- Multiple departments could register their MCP endpoints
- A simple approval workflow would control what gets published
- Microsoft Entra ID would handle authentication and authorization
- Designated admins could approve or reject registrations

**Branch**: `001-mcp-registry-ui`

**Specifications Created**: [`specs/001-mcp-registry-ui/spec.md`](specs/001-mcp-registry-ui/spec.md)

#### User Stories Defined:

**US1 - User Authentication (Priority P1)**:
- Users authenticate via Microsoft Entra ID using MSAL libraries
- System distinguishes between "Admin" and "User" roles via Entra ID security group membership
- Protected routes enforce authentication boundaries

**US2 - Browse and Search MCP Registry (Priority P1)**:
- Users can view all approved MCP endpoints
- Real-time search/filter across endpoint name, owner, metadata
- Detailed metadata view for each endpoint
- Red and white color scheme applied consistently

**US3 - Register New MCP Endpoint (Priority P2)**:
- Users submit new endpoints with metadata (name, URL, owner, tools)
- Submissions enter "Pending" status awaiting approval
- "My Registrations" view shows user's submissions
- Form validation ensures data quality

**US4 - Admin Approval Workflow (Priority P2)**:
- Admins view pending registrations
- Approve, reject, or remove endpoints
- Status updates tracked with timestamps
- Regular users cannot access admin features

#### Key Decisions:

- **Data Storage**: IndexedDB for initial frontend-only implementation (to be replaced by backend in phase 2)
- **Authentication**: MSAL browser libraries with Entra ID group-based role detection
- **UI Framework**: React with Tailwind CSS for responsive design
- **Color Palette**: Red and white theme (specific hex codes deferred to implementation)

**Clarifications Made** (via `/speckit.clarify`):
- Admin detection: Entra ID security group membership ("MCP-Registry-Admins")
- Storage mechanism: IndexedDB with 50MB+ capacity
- Tool specification: Comma-separated list input
- Rejected endpoints: Retained with "Rejected" status for audit trail
- Color decisions: Deferred to design phase

---

### Phase 2: Planning - Frontend (Branch 001)

**Command**: `/speckit.plan`

**Deliverable**: [`specs/001-mcp-registry-ui/plan.md`](specs/001-mcp-registry-ui/plan.md)

The planning phase converted specifications into technical architecture:

#### Technical Decisions:

**Project Structure**:
```
frontend/src/
├── components/
│   ├── auth/           # Authentication components (LoginButton, UserProfile)
│   ├── endpoints/      # Endpoint display (EndpointCard, EndpointList)
│   ├── admin/          # Admin features (ApprovalQueue, ApprovalCard)
│   ├── layout/         # Layout components (Header, Footer, Navigation)
│   └── common/         # Reusable UI (Button, Input, Modal)
├── pages/              # Route-level components
│   ├── Dashboard.tsx
│   ├── Register.tsx
│   ├── MyRegistrations.tsx
│   └── AdminApprovals.tsx
├── services/           # Business logic and data access
│   ├── auth.service.ts
│   ├── db.service.ts
│   └── endpoint.service.ts
├── types/              # TypeScript interfaces
├── utils/              # Utility functions
└── config/             # Configuration (MSAL setup)
```

**Dependencies Justified**:
- **@azure/msal-browser** & **@azure/msal-react**: Required for Entra ID authentication
- **dexie**: IndexedDB wrapper for structured data storage
- **react-router-dom**: Client-side routing
- **react-hot-toast**: User notifications

**Performance Goals**:
- Authentication within 10 seconds
- Search results filter in <500ms
- Viewport support: 320px to 1920px
- Admin actions complete in <2 seconds

**Constitution Compliance Check**:
✅ Clean Code First: Component-based architecture with clear boundaries  
✅ Simple UX: Intuitive workflows (single search, straightforward forms)  
✅ Responsive Design: Tailwind mobile-first approach  
✅ Minimal Dependencies: Only essential libraries added  
✅ No Testing: Manual verification checklist provided instead  

---

### Phase 3: Task Breakdown - Frontend (Branch 001)

**Command**: `/speckit.tasks`

**Deliverable**: [`specs/001-mcp-registry-ui/tasks.md`](specs/001-mcp-registry-ui/tasks.md)

The specification was broken into **85 actionable tasks** organized by user story:

**Task Distribution**:
- **Setup** (Phase 1): 5 tasks - Project initialization
- **Foundational** (Phase 2): 15 tasks - Core infrastructure (BLOCKS all user stories)
- **US1 - Authentication** (Phase 3): 10 tasks - Login/role detection
- **US2 - Browse/Search** (Phase 4): 12 tasks - Registry browsing
- **US3 - Registration** (Phase 5): 14 tasks - Endpoint submission
- **US4 - Admin Approval** (Phase 6): 16 tasks - Approval workflow
- **Polish** (Phase 7): 13 tasks - Cross-cutting improvements

**Parallel Opportunities**: 23 tasks marked `[P]` could run in parallel (different files, no dependencies)

**MVP Scope**: 42 tasks (Setup + Foundational + US1 + US2) delivered core browsing functionality

**Execution Strategy**:
1. Complete foundational phase (blocks everything else)
2. Implement US1 (authentication) - enables all other stories
3. Parallel development: US2 (browse) + US3 (registration)
4. Sequential: US4 (admin approval) requires US3 to exist
5. Polish phase after core features stable

**Manual Verification**: Each phase included specific manual test cases (no automated tests per constitution)

---

### Phase 4: Implementation - Frontend (Branch 001)

**Command**: `/speckit.implement`

**Deliverables**: Complete frontend application in [`frontend/`](frontend/)

#### What Was Built:

**Authentication System**:
- MSAL configuration for Entra ID integration ([`src/config/msal.config.ts`](frontend/src/config/msal.config.ts))
- Auth context providing user state across app ([`src/context/AuthContext.tsx`](frontend/src/context/AuthContext.tsx))
- Protected routes enforcing authentication ([`src/components/common/ProtectedRoute.tsx`](frontend/src/components/common/ProtectedRoute.tsx))
- Admin role detection via Entra ID group membership

**Data Layer**:
- IndexedDB schema with Dexie (users, endpoints, registrations)
- Service layer abstracting data operations ([`src/services/api.service.ts`](frontend/src/services/api.service.ts))
- TypeScript types for compile-time safety ([`src/types/`](frontend/src/types/))

**User Interface**:
- **Dashboard**: Browse approved endpoints with real-time search
- **Registration Page**: Submit new MCP endpoints with validation
- **My Registrations**: Track submission status (Pending/Approved/Rejected)
- **Admin Approvals** *(Admin Only)*: Review and approve/reject submissions
- **Responsive Design**: Mobile-first with Tailwind CSS, red/white theme

**Key Features Implemented**:
- Microsoft Entra ID single sign-on
- Role-based access control (Admin vs User)
- Real-time search/filtering (<500ms response)
- Form validation (URL format, required fields)
- Status tracking with timestamps
- Toast notifications for user feedback
- Error boundaries for graceful failure handling

**Supporting Scripts** (PowerShell):
- [`Setup-EntraIDAdminGroup.ps1`](Setup-EntraIDAdminGroup.ps1): Creates Entra ID app registration and admin group
- [`Add-UserToAdminGroup.ps1`](Add-UserToAdminGroup.ps1): Assigns admin privileges
- [`List-AdminGroupMembers.ps1`](List-AdminGroupMembers.ps1): Audits admin users

#### Frontend Delivered:
✅ Fully functional React TypeScript application  
✅ Working authentication with Entra ID  
✅ Complete CRUD operations via IndexedDB  
✅ Responsive design (320px - 1920px viewports)  
✅ Admin approval workflow  
✅ No automated tests (per constitution)  

---

### Phase 5: Specification - Backend (Branch 002)

**Command**: `/speckit.specify` *(Second iteration)*

**Requirements Update**:
With the frontend validated, the customer needed to move from browser-based storage to a centralized database that would:
- Support multiple users across the organization
- Persist data beyond individual browser sessions
- Enable reporting and audit trails
- Deploy to Azure for enterprise scalability

**Branch**: `002-fastapi-postgres-backend`

**Specifications Created**: [`specs/002-fastapi-postgres-backend/spec.md`](specs/002-fastapi-postgres-backend/spec.md)

#### User Stories Defined:

**US1 - API Endpoints for MCP Registry Data (Priority P1)**:
- RESTful endpoints replacing IndexedDB functionality
- CRUD operations: Create, retrieve, update, delete registrations
- Filtering, pagination, search capabilities
- Proper HTTP status codes and error handling

**US2 - User Management and Authentication Support (Priority P1)**:
- Validate Entra ID tokens on every request
- Create/update user records from token claims
- Admin role detection based on Entra ID group membership
- User profile endpoints

**US3 - Database Schema and Migration Scripts (Priority P1)**:
- PostgreSQL database with tables for users, registrations, audit logs
- SQL scripts to create schema
- Idempotent migrations (safe to run multiple times)
- Indexes on frequently queried columns
- Foreign key relationships

**US4 - Frontend Integration Updates (Priority P2)**:
- Replace IndexedDB calls with HTTP requests to backend
- Add authentication headers to API calls
- Handle API errors gracefully
- Remove IndexedDB code completely

**US5 - Azure PostgreSQL Database Configuration (Priority P2)**:
- Connect to Azure-hosted PostgreSQL
- SSL/TLS encryption enforcement
- Environment-specific configuration
- Connection pooling for performance

#### Key Decisions:

- **Backend Framework**: FastAPI (modern, async, automatic OpenAPI docs)
- **Database**: PostgreSQL with JSONB for flexible metadata storage
- **Authentication**: Validate Entra ID JWT tokens on every request
- **Package Management**: `uv` for fast Python dependency resolution (10-100x faster than pip)
- **Logging**: Structured JSON logging compatible with Azure Application Insights

**Edge Cases Addressed**:
- Concurrent duplicate submissions: Database unique constraint
- Connection loss during requests: HTTP 503 with reconnection attempts
- Token expiration: HTTP 401 with frontend re-authentication prompt
- Conflicting status updates: Database transactions + optimistic locking

---

### Phase 6: Planning - Backend (Branch 002)

**Command**: `/speckit.plan`

**Deliverable**: [`specs/002-fastapi-postgres-backend/plan.md`](specs/002-fastapi-postgres-backend/plan.md)

#### Technical Architecture:

**Project Structure**:
```
backend/
├── src/
│   ├── main.py                  # FastAPI application entry point
│   ├── config.py                # Environment configuration
│   ├── database.py              # PostgreSQL connection pool
│   ├── dependencies.py          # FastAPI dependencies (auth)
│   ├── auth/
│   │   └── entra_validator.py  # JWT token validation
│   ├── models/                  # Pydantic models (internal)
│   │   ├── user.py
│   │   ├── registration.py
│   │   └── audit_log.py
│   ├── schemas/                 # Pydantic schemas (API contracts)
│   │   ├── user.py
│   │   └── registration.py
│   ├── services/                # Business logic
│   │   ├── user_service.py
│   │   └── registration_service.py
│   └── routers/                 # API endpoints
│       ├── health.py
│       ├── users.py
│       └── registrations.py
├── scripts/
│   └── db/
│       ├── init_schema.sql      # Database schema
│       └── README.md            # Database setup instructions
├── pyproject.toml               # Python dependencies (uv)
└── README.md                    # Backend setup guide
```

**API Endpoints Designed**:
- `GET /health` - Health check for monitoring
- `POST /users` - Create/update user from Entra ID token
- `GET /users/me` - Current user profile
- `GET /users/{user_id}` - Specific user details
- `POST /registrations` - Submit new endpoint registration
- `GET /registrations` - List registrations (with filters)
- `GET /registrations/{id}` - Specific registration details
- `GET /registrations/my` - Current user's submissions
- `PATCH /registrations/{id}/status` - Approve/reject (admin only)
- `DELETE /registrations/{id}` - Remove registration (admin only)

**Database Schema**:
```sql
-- Users table
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    entra_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Registrations table
CREATE TABLE registrations (
    registration_id UUID PRIMARY KEY,
    endpoint_url VARCHAR(500) UNIQUE NOT NULL,
    endpoint_name VARCHAR(200) NOT NULL,
    description TEXT,
    owner_contact VARCHAR(255),
    available_tools JSONB,
    status VARCHAR(20) CHECK (status IN ('Pending', 'Approved', 'Rejected')),
    submitter_id UUID REFERENCES users(user_id),
    approver_id UUID REFERENCES users(user_id),
    submitted_at TIMESTAMP DEFAULT NOW(),
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Audit log for compliance
CREATE TABLE audit_log (
    log_id UUID PRIMARY KEY,
    registration_id UUID REFERENCES registrations(registration_id),
    user_id UUID REFERENCES users(user_id),
    action VARCHAR(50),
    previous_status VARCHAR(20),
    new_status VARCHAR(20),
    metadata JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_registrations_status ON registrations(status);
CREATE INDEX idx_registrations_submitter_id ON registrations(submitter_id);
CREATE INDEX idx_registrations_created_at ON registrations(created_at DESC);
```

**Dependencies**:
- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **asyncpg**: PostgreSQL async driver
- **pydantic**: Data validation
- **python-jose**: JWT token validation
- **python-dotenv**: Environment variables
- **python-json-logger**: Structured logging

**Performance Targets**:
- API response time: <200ms for 95% of requests
- Database connection pool: 10-20 connections
- Support: 100 concurrent requests without degradation
- Health check: <100ms response time

---

### Phase 7: Task Breakdown - Backend (Branch 002)

**Command**: `/speckit.tasks`

**Deliverable**: [`specs/002-fastapi-postgres-backend/tasks.md`](specs/002-fastapi-postgres-backend/tasks.md)

The backend was broken into **51 actionable tasks** across 9 phases:

**Task Distribution**:
- **Phase 1 - Setup**: 5 tasks - Project initialization, dependencies
- **Phase 2 - Foundational**: 8 tasks - Database schema, connection pool
- **Phase 3 - Data Models**: 6 tasks - Pydantic models and schemas
- **Phase 4 - Authentication**: 4 tasks - JWT validation, admin checks
- **Phase 5 - Services**: 8 tasks - Business logic layer
- **Phase 6 - API Routes**: 10 tasks - RESTful endpoints
- **Phase 7 - App Setup**: 4 tasks - FastAPI config, CORS, logging
- **Phase 8 - Frontend Integration**: 3 tasks - Replace IndexedDB
- **Phase 9 - Azure Config**: 3 tasks - Azure PostgreSQL setup

**Critical Path** (MVP - US1 only):
```
Phase 1 (Foundation) 
  → Phase 2 (Database) 
    → Phase 3 (Models) 
      → Phase 4 (Auth) 
        → Phase 5 (Services) 
          → Phase 6 (Routes) 
            → Phase 7 (App Setup)
```

**Parallel Opportunities**:
- Phase 2 (Database) + Phase 3 (Models) - different concerns
- Phase 4 (Auth) + Phase 5 (Services) - independent systems
- US2 (User Management) + US3 (Database) - separate domains
- Phase 8 (Frontend) + Phase 9 (Azure) - different tiers

**MVP Recommendation**: Tasks T001-T045 (Phases 1-7)
- Delivers working FastAPI backend with all CRUD endpoints
- Database schema and PostgreSQL connection
- Entra ID authentication and authorization
- Health check endpoint for monitoring
- CORS configuration for frontend access

**Deferred to Phase 2**:
- Phase 8: Frontend integration (let backend stabilize first)
- Phase 9: Azure deployment (test locally first)

---

### Phase 8: Implementation - Backend (Branch 002)

**Command**: `/speckit.implement`

**Deliverables**: Complete backend application in [`backend/`](backend/)

#### What Was Built:

**Database Layer** ([`scripts/db/init_schema.sql`](backend/scripts/db/init_schema.sql)):
- Three tables: `users`, `registrations`, `audit_log`
- Foreign key relationships maintaining referential integrity
- Unique constraints preventing duplicate registrations
- Indexes on frequently queried columns (status, submitter_id, created_at)
- Timestamps with automatic update triggers
- Check constraints for enum validation (status, action)

**Connection Management** ([`src/database.py`](backend/src/database.py)):
- asyncpg connection pool (10-20 connections)
- Startup/shutdown lifecycle management
- Connection health checks
- SSL/TLS support for Azure
- Error handling with automatic reconnection

**Authentication** ([`src/auth/entra_validator.py`](backend/src/auth/entra_validator.py)):
- JWT token validation (signature, issuer, audience, expiration)
- Claim extraction (entra_id, email, display_name)
- Group membership parsing for admin detection
- FastAPI dependencies: `get_current_user`, `require_admin`
- HTTP 401 for invalid tokens, 403 for insufficient permissions

**Data Models**:
- **Pydantic Models** ([`src/models/`](backend/src/models/)): Internal representations with validation
- **API Schemas** ([`src/schemas/`](backend/src/schemas/)): Request/response contracts
- Type safety with Python 3.13+ type hints
- JSONB handling for flexible metadata (available_tools)

**Business Logic** ([`src/services/`](backend/src/services/)):
- **UserService**: Create/update users from Entra ID, admin status checks
- **RegistrationService**: CRUD operations with business rules
  - Create: Default "Pending" status, track submitter
  - Get: Filtering (status, submitter, search), pagination
  - Update: Status transitions (Pending → Approved/Rejected), track approver
  - Delete: Admin-only removal
- Duplicate detection: HTTP 409 conflict on unique constraint violation
- Transaction management for data consistency

**API Endpoints** ([`src/routers/`](backend/src/routers/)):

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/health` | GET | Health check with database status | None |
| `/users` | POST | Create/update user from token | User |
| `/users/me` | GET | Current user profile | User |
| `/users/{user_id}` | GET | Specific user details | User |
| `/registrations` | POST | Submit new endpoint | User |
| `/registrations` | GET | List registrations (filterable) | User |
| `/registrations/my` | GET | Current user's submissions | User |
| `/registrations/{id}` | GET | Registration details | User |
| `/registrations/{id}/status` | PATCH | Approve/reject registration | Admin |
| `/registrations/{id}` | DELETE | Remove registration | Admin |

**Application Setup** ([`src/main.py`](backend/src/main.py)):
- FastAPI application with automatic OpenAPI docs
- CORS configuration allowing frontend origin
- Structured JSON logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Startup event: Initialize database connection pool
- Shutdown event: Close connections gracefully
- Exception handlers for common errors (404, 409, 422, 500, 503)

**Configuration** ([`src/config.py`](backend/src/config.py)):
- Environment variable loading with python-dotenv
- Required settings validation on startup
- Support for multiple environments (dev, staging, prod)

**Environment Variables** ([`.env.example`](backend/.env.example)):
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/mcp_registry
AZURE_CLIENT_ID=your-entra-app-client-id
AZURE_TENANT_ID=your-entra-tenant-id
ENTRA_ADMIN_GROUP_ID=your-admin-group-object-id
CORS_ORIGINS=http://localhost:5173
LOG_LEVEL=INFO
```

#### Integration Phase:

**Frontend Updates** (Phase 8 - Tasks T046-T048):
1. **Replaced IndexedDB** with HTTP API calls ([`frontend/src/services/api.service.ts`](frontend/src/services/api.service.ts))
   - Fetch/Axios requests to backend endpoints
   - Authorization header with MSAL access token
   - Base URL configuration for environment flexibility

2. **Error Handling**:
   - HTTP status code mapping (401, 403, 404, 409, 500)
   - User-friendly error messages
   - Token expiration detection → re-authentication prompt
   - Network error recovery

3. **Cleanup**:
   - Removed `db.service.ts` and `db.schema.ts`
   - Updated component imports to use `api.service.ts`
   - Verified no IndexedDB references remain

**Fixes Applied During Integration**:
- **Route Ordering**: FastAPI matches routes sequentially; moved specific routes (`/my`) before parameterized routes (`/{id}`)
- **Admin Sync**: Implemented automatic admin status sync from Entra ID group membership to database on every request
- **Token Claims**: Enhanced extraction to support multiple claim sources (email, upn, unique_name, preferred_username)
- **JSONB Handling**: Proper conversion between Python lists and PostgreSQL JSONB (JSON string serialization)
- **Pydantic Serialization**: Fixed HttpUrl → string conversion for API responses, added `from_attributes` config
- **Debug Logging**: Added comprehensive logging throughout authentication flow for troubleshooting

#### Backend Delivered:
✅ Fully functional FastAPI backend with RESTful API  
✅ PostgreSQL database with normalized schema  
✅ Entra ID JWT token validation on every request  
✅ Admin role detection via group membership  
✅ CRUD operations with filtering and pagination  
✅ Structured JSON logging  
✅ CORS configuration for frontend  
✅ Health check endpoint  
✅ No automated tests (per constitution)  
✅ Frontend successfully integrated and IndexedDB removed  

---

## Project Deliverables

### Frontend (`001-mcp-registry-ui`)

**Technology**: React 19.2.0 + TypeScript 5.9.3 + Vite 7.2.2 + Tailwind CSS

**Features**:
- ✅ Microsoft Entra ID authentication with MSAL
- ✅ Role-based access control (Admin vs User via Entra ID groups)
- ✅ Browse approved MCP endpoints with real-time search
- ✅ Register new MCP endpoints with validation
- ✅ Track registration status (Pending/Approved/Rejected)
- ✅ Admin approval workflow (approve/reject/remove)
- ✅ Responsive design (320px - 1920px viewports)
- ✅ Red and white color theme
- ✅ Toast notifications for user feedback
- ✅ Error boundaries for graceful failures

**Lines of Code**: ~3,500 lines (estimated)

**Development Time**: 2 days (with SpecKit process)

**Files Created**: 45+ components, services, types, and configuration files

### Backend (`002-fastapi-postgres-backend`)

**Technology**: Python 3.13+ + FastAPI + PostgreSQL + Azure

**Features**:
- ✅ RESTful API with 10 endpoints
- ✅ PostgreSQL database with 3 tables
- ✅ Entra ID JWT token validation
- ✅ Admin role detection via Entra ID groups
- ✅ CRUD operations with filtering and pagination
- ✅ Duplicate detection (unique constraints)
- ✅ Structured JSON logging
- ✅ CORS configuration
- ✅ Health check endpoint
- ✅ SSL/TLS support for Azure
- ✅ Connection pooling (10-20 connections)
- ✅ Automatic OpenAPI documentation

**Lines of Code**: ~1,800 lines (estimated)

**Development Time**: 1.5 days (with SpecKit process)

**Files Created**: 20+ modules, schemas, services, and SQL scripts

### Supporting Scripts

**PowerShell Automation**:
- [`Setup-EntraIDAdminGroup.ps1`](Setup-EntraIDAdminGroup.ps1): One-command Entra ID setup
- [`Add-UserToAdminGroup.ps1`](Add-UserToAdminGroup.ps1): Admin user management
- [`List-AdminGroupMembers.ps1`](List-AdminGroupMembers.ps1): Admin audit

**Documentation**:
- [`ENTRA-ID-SETUP.md`](ENTRA-ID-SETUP.md): Manual Entra ID configuration guide
- [`ENTRA-API-SETUP.md`](ENTRA-API-SETUP.md): API permissions configuration
- [`backend/README.md`](backend/README.md): Backend setup and running instructions
- [`frontend/README.md`](frontend/README.md): Frontend setup and development guide

---

## Key SpecKit Outcomes

### Specification Quality

**Precision**: Every requirement traced to user story → acceptance criteria → tasks → code

**Completeness**: 
- Frontend: 4 user stories, 21 functional requirements, 85 tasks
- Backend: 5 user stories, 31 functional requirements, 51 tasks

**Clarity**: Non-technical stakeholders could understand specifications; developers could implement without ambiguity

### Development Speed

**Traditional Approach** (estimated):
- Requirements gathering: 1 week
- Design and architecture: 1 week  
- Frontend development: 2-3 weeks
- Backend development: 2 weeks
- Integration and testing: 1-2 weeks
- **Total**: 7-9 weeks

**SpecKit Approach** (actual):
- Constitution: 0.5 days
- Frontend spec + plan + tasks: 0.5 days
- Frontend implementation: 2 days
- Backend spec + plan + tasks: 0.5 days
- Backend implementation + integration: 1.5 days
- **Total**: 5 days

**Speedup**: ~10x faster than traditional development

### Code Quality

**Metrics** (estimated):
- **Complexity**: Low (max 3 levels of nesting, functions <30 lines average)
- **Maintainability Index**: High (descriptive naming, clear structure)
- **Duplication**: Minimal (<5% estimated)
- **Type Safety**: 100% (TypeScript + Python type hints)

**Constitution Compliance**: 
- ✅ Clean code principles followed throughout
- ✅ Simple UX with minimal cognitive load
- ✅ Responsive design verified across viewports
- ✅ Dependencies justified and documented
- ✅ Zero automated tests (manual verification only)

### Documentation as Artifact

**Living Documentation**: Specifications remain accurate because they drove implementation—not written after the fact

**Traceability**: 
- User story → Functional requirement → Task → Code file
- Every feature decision documented with rationale

**Onboarding**: New developers can understand system by reading specs (not reverse-engineering code)

---

## Lessons Learned

### What Worked Well

1. **Constitution First**: Establishing ground rules prevented mid-project debates about testing, dependencies, and code style

2. **User Story Organization**: Breaking specs into stories with clear priorities enabled incremental delivery (MVP in 2.5 days)

3. **Task Granularity**: 85+ frontend tasks meant no task took >2 hours; progress was visible and trackable

4. **Parallel Opportunities**: Tasks marked `[P]` enabled concurrent work without merge conflicts

5. **Manual Verification**: Without automated tests, manual verification checklists ensured quality (faster than writing tests for prototypes)

6. **Branch Isolation**: Separate branches for frontend and backend allowed independent progress and clear specification boundaries

7. **AI-Assisted Implementation**: AI tools accelerated coding by 5-10x while human oversight maintained architecture consistency

### Challenges Encountered

1. **Specification Completeness**: Initial specs missed edge cases (duplicate submissions, concurrent updates); required mid-implementation clarifications

2. **Integration Assumptions**: Frontend assumed backend API shapes that differed slightly from final implementation; required minor refactoring

3. **Entra ID Complexity**: Microsoft Entra ID configuration was more involved than expected (group claims, token validation); PowerShell scripts mitigated this

4. **JSONB Handling**: PostgreSQL JSONB serialization required explicit handling (Python list → JSON string); caught during integration testing

5. **Route Ordering**: FastAPI route matching sequenced (/my before /{id}); not obvious until runtime errors

### Improvements for Next Iteration

1. **Tighter Contracts**: Define API contracts (OpenAPI spec) during planning phase to prevent frontend/backend drift

2. **Environment Parity**: Use Docker Compose to ensure dev environment matches production (Azure PostgreSQL, Entra ID)

3. **Incremental Integration**: Integrate one endpoint at a time rather than big-bang migration from IndexedDB

4. **Edge Case Workshop**: Dedicated session to brainstorm failure modes and edge cases before implementation

5. **Schema Versioning**: Include migration strategy in constitution for projects expecting schema evolution

---

## For Pre-Sales Engineers: Using SpecKit

### When to Use SpecKit

**Ideal Scenarios**:
- **Customer Engagements**: 2-5 day prototyping sprints with live requirements gathering
- **Proof of Concepts**: Demonstrating technical feasibility of proposed solutions
- **Pilot Projects**: First-phase implementations before full product commitment
- **Sales Demos**: Customized demonstrations showing customer-specific workflows

**Not Ideal For**:
- Long-term production applications (where testing and scalability matter more than speed)
- Projects with undefined requirements (SpecKit requires concrete specifications)
- Maintenance of existing codebases (SpecKit is for greenfield development)

### How to Run a SpecKit Engagement

**Day 0 - Preparation**:
1. Review SpecKit methodology (`instructions.md`)
2. Prepare AI tools (GitHub Copilot, ChatGPT, Claude, etc.)
3. Set up development environment (IDE, Git, Docker if needed)

**Day 1 - Requirements & Constitution**:
- **Morning**: Customer meeting to gather requirements (user stories, pain points)
- **Afternoon**: 
  - Run `/speckit.constitution` to establish project principles
  - Run `/speckit.specify` to document requirements
  - Run `/speckit.clarify` to resolve ambiguities with customer

**Day 2 - Planning & Setup**:
- **Morning**:
  - Run `/speckit.plan` to create technical architecture
  - Run `/speckit.tasks` to break down implementation
- **Afternoon**: 
  - Setup project (dependencies, configuration)
  - Begin foundational tasks (database schema, authentication setup)

**Day 3-4 - Implementation**:
- Run `/speckit.implement` command for AI-assisted development
- Work through tasks systematically (foundational → MVP → enhancements)
- Frequent commits with task references (e.g., "T023: Implement admin role check")
- Manual verification of each feature as completed

**Day 5 - Integration & Demo**:
- **Morning**: Final integration and polish
- **Afternoon**: Customer demo with live walkthrough
- **Wrap-up**: Deliver codebase, documentation, and deployment guide

### Success Metrics

**For Customers**:
- Working prototype in 3-5 days (vs. weeks for traditional approach)
- Visible progress daily (not "we're still designing")
- Accurate specifications documenting what was built
- Confidence in technical feasibility

**For Engineers**:
- Clear scope boundaries (constitution prevents feature creep)
- Structured workflow reduces decision fatigue
- Reusable specifications for future phases
- Portfolio-worthy code quality (even for prototypes)

**For Sales Teams**:
- Technical credibility during sales cycle
- Concrete demonstrations of capabilities
- Shortens sales cycle (proof of feasibility)
- Differentiation from competitors (show working code, not slides)

---

## Technical Stack Summary

### Frontend
- **Framework**: React 19.2.0
- **Language**: TypeScript 5.9.3
- **Build Tool**: Vite 7.2.2
- **Styling**: Tailwind CSS
- **Authentication**: @azure/msal-browser, @azure/msal-react
- **Routing**: react-router-dom
- **Notifications**: react-hot-toast
- **Data Storage**: Initially IndexedDB (Dexie), migrated to API calls

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.13+
- **Database**: PostgreSQL (Azure Database for PostgreSQL)
- **Database Driver**: asyncpg (async connection pool)
- **Authentication**: python-jose (JWT validation)
- **Validation**: Pydantic
- **Logging**: python-json-logger (structured JSON)
- **Server**: Uvicorn (ASGI)
- **Package Manager**: uv (10-100x faster than pip)

### Infrastructure
- **Authentication**: Microsoft Entra ID (formerly Azure AD)
- **Database**: Azure Database for PostgreSQL (SSL/TLS enforced)
- **Deployment Target**: Azure (container services or App Service)
- **CORS**: Configured for local development and production domains

### Development Tools
- **Version Control**: Git with feature branches
- **AI Assistance**: GitHub Copilot, Claude, ChatGPT
- **Manual Testing**: REST clients (Postman, curl), browser DevTools
- **Documentation**: Markdown specifications in `specs/` directory

---

## Repository Structure

```
mcp-project-speckit/
├── README.md                          # This file
├── instructions.md                    # SpecKit step-by-step process
├── .specify/
│   └── memory/
│       └── constitution.md            # Project constitution (principles)
├── specs/
│   ├── 001-mcp-registry-ui/           # Frontend specifications
│   │   ├── spec.md                    # User stories and requirements
│   │   ├── plan.md                    # Technical architecture
│   │   ├── tasks.md                   # Implementation tasks (85 tasks)
│   │   ├── data-model.md              # Data structures and types
│   │   ├── quickstart.md              # Manual verification guide
│   │   └── contracts/
│   │       ├── indexeddb-schema.md    # Database schema contract
│   │       └── validation-schema.md   # Validation rules
│   └── 002-fastapi-postgres-backend/  # Backend specifications
│       ├── spec.md                    # User stories and requirements
│       ├── plan.md                    # Technical architecture
│       ├── tasks.md                   # Implementation tasks (51 tasks)
│       ├── data-model.md              # Database schema and models
│       ├── quickstart.md              # Backend setup and testing
│       └── contracts/
│           ├── api-endpoints.md       # API contract documentation
│           └── database-schema.sql    # SQL schema reference
├── frontend/                          # React TypeScript application
│   ├── src/
│   │   ├── components/                # UI components (auth, admin, layout, etc.)
│   │   ├── pages/                     # Route-level components
│   │   ├── services/                  # API and business logic
│   │   ├── types/                     # TypeScript type definitions
│   │   ├── utils/                     # Utility functions
│   │   ├── config/                    # MSAL and app configuration
│   │   └── context/                   # React context (auth state)
│   ├── package.json                   # Dependencies and scripts
│   ├── vite.config.ts                 # Vite build configuration
│   ├── tailwind.config.js             # Tailwind CSS theme
│   └── README.md                      # Frontend setup guide
├── backend/                           # FastAPI Python application
│   ├── src/
│   │   ├── main.py                    # FastAPI app entry point
│   │   ├── config.py                  # Environment configuration
│   │   ├── database.py                # PostgreSQL connection pool
│   │   ├── dependencies.py            # FastAPI dependencies
│   │   ├── auth/                      # JWT token validation
│   │   ├── models/                    # Pydantic internal models
│   │   ├── schemas/                   # API request/response schemas
│   │   ├── services/                  # Business logic layer
│   │   └── routers/                   # API endpoint routes
│   ├── scripts/
│   │   └── db/
│   │       ├── init_schema.sql        # Database creation script
│   │       └── README.md              # Database setup guide
│   ├── pyproject.toml                 # Python dependencies (uv)
│   ├── .env.example                   # Environment variables template
│   └── README.md                      # Backend setup and running guide
├── Setup-EntraIDAdminGroup.ps1        # Automated Entra ID setup
├── Add-UserToAdminGroup.ps1           # Admin user management
├── List-AdminGroupMembers.ps1         # Admin audit script
├── ENTRA-ID-SETUP.md                  # Manual Entra ID guide
└── ENTRA-API-SETUP.md                 # API permissions guide
```

---

## Getting Started

### Prerequisites

- **Node.js** 18+ (for frontend)
- **Python** 3.13+ (for backend)
- **PostgreSQL** 14+ (local or Azure)
- **Azure Subscription** (for Entra ID and Azure PostgreSQL)
- **Git** for version control

### Quick Start

**1. Clone Repository**:
```bash
git clone https://github.com/yourusername/mcp-project-speckit.git
cd mcp-project-speckit
```

**2. Setup Entra ID** (automated):
```powershell
cd mcp-project-speckit
.\Setup-EntraIDAdminGroup.ps1
```
This creates:
- Entra ID app registration
- Admin security group
- Outputs tenant_id, client_id, admin_group_id for configuration

**3. Setup Backend**:
```bash
cd backend

# Install dependencies with uv
uv pip install -e .

# Create .env from template
cp .env.example .env
# Edit .env with your Entra ID values and database URL

# Initialize database
psql -U your_user -d your_database -f scripts/db/init_schema.sql

# Run backend
uvicorn src.main:app --reload --port 8000
```

**4. Setup Frontend**:
```bash
cd frontend

# Install dependencies
npm install

# Create .env from template
cp .env.example .env
# Edit .env with your Entra ID client_id and tenant_id

# Run frontend
npm run dev
```

**5. Access Application**:
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs` (automatic OpenAPI documentation)

**6. Make Yourself Admin**:
```powershell
.\Add-UserToAdminGroup.ps1 -UserEmail your.email@yourdomain.com
```

### Manual Verification

Since this project follows the "no testing" principle, use the manual verification checklists:

**Frontend**: See [`specs/001-mcp-registry-ui/quickstart.md`](specs/001-mcp-registry-ui/quickstart.md)

**Backend**: See [`specs/002-fastapi-postgres-backend/quickstart.md`](specs/002-fastapi-postgres-backend/quickstart.md)

---

## Next Steps (Future Enhancements)

The SpecKit process is designed for iterative development. Here are logical next phases:

### Phase 3: Audit Logging (Branch 003)

**User Story**: Complete audit trail for compliance
- Track all registration state changes
- Record who made changes and when
- Queryable audit history endpoint
- Export audit logs to CSV/JSON

**Estimated Effort**: 1-2 days with SpecKit

### Phase 4: Endpoint Health Monitoring (Branch 004)

**User Story**: Validate MCP endpoints are reachable
- Periodic health checks for approved endpoints
- Status dashboard (healthy/degraded/down)
- Automated alerts for endpoint failures
- Historical uptime tracking

**Estimated Effort**: 2-3 days with SpecKit

### Phase 5: Advanced Search & Categorization (Branch 005)

**User Story**: Enhanced discoverability
- Tag/category system for endpoints
- Faceted search (filter by category, owner, tools)
- Saved search queries
- Endpoint recommendations

**Estimated Effort**: 2 days with SpecKit

### Phase 6: Testing Interface (Branch 006)

**User Story**: Test MCP servers directly from registry
- Interactive test panel for each endpoint
- Send sample requests, view responses
- Tool capability validation
- Performance metrics (latency, throughput)

**Estimated Effort**: 3-4 days with SpecKit

### Phase 7: Deployment & Scalability (Branch 007)

**User Story**: Production-ready deployment
- Docker containerization
- Azure Container Apps or App Service deployment
- Horizontal scaling configuration
- CDN for frontend assets
- Monitoring and alerting (Application Insights)

**Estimated Effort**: 2-3 days with SpecKit

---

## Conclusion

This project demonstrates the power of **SpecKit** for rapid, specification-driven development in customer engagement scenarios. By following a structured process—constitution, specification, planning, task breakdown, implementation—we delivered a fully functional, enterprise-grade MCP Registry in **5 days** that would traditionally take 7-9 weeks.

### Key Takeaways:

1. **Specifications Drive Everything**: Clear requirements eliminate ambiguity and reduce rework
2. **Constitution Prevents Chaos**: Ground rules established upfront prevent mid-project debates
3. **Task Granularity Enables Progress**: 85+ small tasks provide visible, trackable progress
4. **AI Acceleration**: AI tools (GitHub Copilot, Claude) accelerate implementation by 5-10x when guided by good specifications
5. **Branch Isolation**: Separate specifications for frontend and backend enabled parallel progress
6. **Manual Verification Works**: For prototypes, manual testing is faster and more pragmatic than automated test suites
7. **Documentation as Artifact**: Specifications remain accurate because they drove implementation

### For Pre-Sales Engineers:

SpecKit is not just a development methodology—it's a **customer engagement framework**. Use it to:
- Demonstrate technical competence during sales cycles
- Deliver working prototypes in days, not weeks
- Build credibility with engineering teams
- Shorten sales cycles with proof of feasibility
- Create reusable templates for common scenarios

### For Development Teams:

Even outside sales contexts, SpecKit principles apply:
- **Greenfield Projects**: Get from idea to working code faster
- **Prototyping**: Validate technical approaches before committing
- **Documentation-First**: Specifications as living documentation
- **AI Pair Programming**: Structured prompts for AI coding assistants

---

## Resources

### Documentation
- **Process Guide**: [`instructions.md`](instructions.md) - Step-by-step SpecKit workflow
- **Constitution**: [`.specify/memory/constitution.md`](.specify/memory/constitution.md) - Project principles
- **Frontend Specs**: [`specs/001-mcp-registry-ui/`](specs/001-mcp-registry-ui/)
- **Backend Specs**: [`specs/002-fastapi-postgres-backend/`](specs/002-fastapi-postgres-backend/)

### Setup Guides
- **Entra ID Setup**: [`ENTRA-ID-SETUP.md`](ENTRA-ID-SETUP.md)
- **Entra API Setup**: [`ENTRA-API-SETUP.md`](ENTRA-API-SETUP.md)
- **Backend Setup**: [`backend/README.md`](backend/README.md)
- **Frontend Setup**: [`frontend/README.md`](frontend/README.md)

### Scripts
- **Automated Entra ID Setup**: [`Setup-EntraIDAdminGroup.ps1`](Setup-EntraIDAdminGroup.ps1)
- **Admin Management**: [`Add-UserToAdminGroup.ps1`](Add-UserToAdminGroup.ps1)
- **Admin Audit**: [`List-AdminGroupMembers.ps1`](List-AdminGroupMembers.ps1)

### External References
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) - What MCP servers are
- [Microsoft Entra ID](https://learn.microsoft.com/en-us/entra/identity/) - Authentication platform
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Backend framework
- [React Documentation](https://react.dev/) - Frontend framework
- [Azure PostgreSQL](https://azure.microsoft.com/en-us/products/postgresql/) - Database hosting

---

## Contact & Feedback

This project was created as an experiment in specification-driven development for customer engagement scenarios. Feedback, questions, and suggestions are welcome.

**Project Maintainer**: [Your Name]  
**Organization**: [Your Company]  
**Purpose**: Pre-sales engineering methodology demonstration

---

*Generated with SpecKit - A specification-driven development methodology for rapid prototyping.*

**Last Updated**: November 12, 2025
