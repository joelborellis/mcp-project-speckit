# Implementation Plan: Browse Functionality, Approval Status Query API, and Audit Logging

**Branch**: `003-browse-audit-query` | **Date**: 2025-11-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-browse-audit-query/spec.md`

## Summary

This feature adds three core capabilities to the MCP Registry application:

1. **Browse Page (Frontend)**: A comprehensive UI at root path `/` displaying all registered MCP servers with search, pagination, and detailed view capabilities. Non-admin users see only approved registrations; admins see all statuses.

2. **Approval Status Query API (Backend)**: A new GET `/registrations/by-url` endpoint enabling programmatic queries of registration status by endpoint URL for CI/CD pipelines and monitoring systems.

3. **Audit Logging (Backend)**: Comprehensive tracking of all registration modifications (Create, Approve, Reject, Update, Delete) with a new GET `/audit-logs` endpoint for querying historical changes by registration, user, action type, or date range.

**Technical Approach**: Leverage existing backend infrastructure (FastAPI, PostgreSQL with audit_log table already in schema) and frontend components (React, Tailwind CSS, existing API service layer). Implement new backend service layer for audit logging, new API router endpoints, and a new frontend Browse page component with responsive design patterns.

## Technical Context

**Language/Version**: 
- Frontend: TypeScript ~5.9.3, React ^19.2.0
- Backend: Python >=3.13

**Primary Dependencies**: 
- Frontend: React ^19.2.0, React Router ^7.9.5, Vite ^7.2.2, Tailwind CSS ^3.4.18, MSAL Browser ^4.26.1, react-hot-toast ^2.6.0
- Backend: FastAPI >=0.115.0, asyncpg >=0.30.0, Pydantic >=2.9.0, PyJWT[crypto] >=2.9.0

**Storage**: PostgreSQL (Azure Database for PostgreSQL) with existing schema containing users, registrations, and audit_log tables

**Target Platform**: 
- Frontend: Modern web browsers (Chrome, Firefox, Edge, Safari) on desktop, tablet, and mobile (320px+ viewports)
- Backend: Linux server environment (Azure App Service or similar)

**Project Type**: Web application (full-stack with separate frontend and backend)

**Performance Goals**: 
- Browse page initial load: <2 seconds on standard network
- Search/filter response: <500ms as user types
- API query endpoint: <200ms for 95% of requests
- Audit log queries: <1 second even with 10,000+ entries
- Detailed view modal: <1 second to display

**Constraints**: 
- No automated testing (per constitution V)
- Frontend must work without backend during development (mock/stub data acceptable)
- Must maintain red/white color scheme from feature 001
- Pagination: 20 items per page for Browse, default 50 (max 200) for audit logs
- Description truncation: 150 characters in Browse list view
- Admin-only access for audit log endpoint (403 for non-admins)
- Atomic audit logging within database transactions

**Scale/Scope**: 
- Expected registrations: 100-1000 initially, scalable to 10,000+
- Expected audit log entries: 1KB per entry, 100K entries ≈ 100MB
- Concurrent users: 10-100 initially
- Frontend: ~5-8 new components/pages, ~500-800 lines of code
- Backend: 2 new router endpoints, 1 new service module, ~400-600 lines of code

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ **Clean Code First**: 
  - New Browse page components follow existing React patterns from MyRegistrationsPage and AdminApprovalsPage
  - Backend services use existing clear patterns from RegistrationService
  - Audit logging abstracted into dedicated service module
  - Clear separation: UI components, API services, backend routers, business logic services
  
- ✅ **Simple UX**: 
  - Browse page uses familiar card/list layout pattern (similar to existing admin approvals)
  - Single search box for filtering (no complex filter UI)
  - One-click access to detailed view (modal or dedicated page)
  - Status badges use color coding for immediate recognition
  - Empty states guide users on next actions
  
- ✅ **Responsive Design**: 
  - Browse page uses Tailwind CSS responsive utilities (sm:, md:, lg: breakpoints)
  - Card layout adapts to grid on desktop, stacks on mobile
  - Touch-friendly tap targets (44×44px minimum per spec)
  - Search box and pagination work on all viewport sizes (320px+)
  - Detailed view modal responsive or full-page on mobile
  
- ✅ **Minimal Dependencies**: 
  - No new frontend dependencies required (use existing React Router, Tailwind, react-hot-toast)
  - No new backend dependencies required (use existing FastAPI, asyncpg, Pydantic)
  - Audit logging uses existing database table (audit_log already in schema)
  - Reuse existing authentication/authorization dependencies (MSAL, PyJWT)
  
- ✅ **No Testing**: 
  - No test files, frameworks, or testing infrastructure
  - Quality assured through manual verification steps documented in spec
  - Code review against acceptance scenarios
  - Constitution mandates no automated testing

## Project Structure

### Documentation (this feature)

```text
specs/003-browse-audit-query/
├── spec.md              # Feature specification
├── plan.md              # This file (/speckit.plan output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── api-endpoints.md     # New endpoints: /registrations/by-url, /audit-logs
│   └── browse-page-ui.md    # Frontend Browse page component specs
└── checklists/
    └── requirements.md  # Quality checklist (already exists)
```

### Source Code (repository root)

```text
backend/
└── src/
    ├── models/
    │   └── audit_log.py         # EXISTS - AuditLog Pydantic models
    ├── services/
    │   ├── registration_service.py  # EXISTS - extend for audit logging
    │   └── audit_service.py     # NEW - audit log query/create service
    ├── routers/
    │   ├── registrations.py     # EXISTS - add GET /by-url endpoint
    │   └── audit_logs.py        # NEW - GET /audit-logs endpoint
    └── schemas/
        └── audit_log.py         # NEW - request/response schemas

frontend/
└── src/
    ├── components/
    │   ├── browse/              # NEW directory
    │   │   ├── BrowseCard.tsx       # Registration card component
    │   │   ├── BrowseList.tsx       # List/grid container
    │   │   ├── BrowseSearch.tsx     # Search input component
    │   │   ├── Pagination.tsx       # Pagination controls
    │   │   └── RegistrationDetailModal.tsx  # Detailed view
    │   └── common/
    │       └── StatusBadge.tsx  # NEW - reusable status badge
    ├── pages/
    │   └── BrowsePage.tsx       # NEW - main Browse page
    ├── services/
    │   └── api.service.ts       # EXISTS - add byUrl() and getAuditLogs()
    └── types/
        └── audit-log.types.ts   # NEW - AuditLog TypeScript types
```

**Structure Decision**: Web application structure (Option 2) with separate frontend and backend directories. This matches the existing project layout established in features 001 and 002. Frontend uses component-based architecture with dedicated directories for browse functionality. Backend follows router → service → model pattern with new audit_logs router and audit_service module.

## Complexity Tracking

> **No constitutional violations requiring justification**

All constitutional principles are satisfied without exceptions:
- Clean code achieved through existing patterns and clear service separation
- Simple UX maintained with familiar card/list layout and single search box
- Responsive design via Tailwind utilities (established pattern)
- No new dependencies required
- No testing infrastructure
