# Implementation Plan: MCP Registry Web Application

**Branch**: `001-mcp-registry-ui` | **Date**: 2025-11-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-mcp-registry-ui/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a React TypeScript web application for managing MCP (Model Context Protocol) endpoint registrations with Microsoft Entra ID authentication and admin approval workflows. The frontend uses IndexedDB for local data persistence and implements a responsive red/white UI design. Users can browse/search approved endpoints, register new endpoints (pending admin approval), and admins can approve/reject/remove registrations. This phase focuses solely on the frontend; backend API integration is deferred to future specifications.

## Technical Context

**Language/Version**: TypeScript ~5.9.3, React ^19.2.0, Node.js (compatible with Vite 7.2.2)  
**Primary Dependencies**: 
- **React** ^19.2.0 & **React DOM** ^19.2.0 (UI framework)
- **Vite** ^7.2.2 (build tool and dev server)
- **Tailwind CSS** (responsive styling - version per frontend/package.json)
- **@azure/msal-browser** (Microsoft Entra ID authentication)
- **@azure/msal-react** (React integration for MSAL)

**Storage**: IndexedDB (browser-based structured database for endpoint metadata, ~50MB+ capacity)  
**Target Platform**: Modern web browsers (Chrome, Firefox, Edge, Safari with JavaScript enabled)  
**Project Type**: Web application (frontend only - monorepo structure with separate backend)  
**Performance Goals**: 
- Authentication within 10 seconds
- Search results filter in <500ms
- Initial page load fast on 3G connections
- Admin approval actions complete in <2 seconds

**Constraints**: 
- Viewport support: 320px (mobile) to 1920px (desktop)
- No automated testing (manual verification only per constitution)
- Frontend must function independently without backend API
- Red and white color palette (specific hex codes TBD during implementation)

**Scale/Scope**: 
- Initial support for <1000 MCP endpoints
- Single Entra ID tenant (no multi-tenancy)
- 4 user stories (2 P1, 2 P2)
- 3 core entities (User, MCP Endpoint, Registration Submission)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ **Clean Code First**: Design promotes readable code with clear component boundaries, descriptive naming, and logical file organization (pages, components, services, utils)
- ✅ **Simple UX**: User workflows are intuitive - authentication flow is transparent, browsing requires single search, registration form is straightforward, admin actions are clear
- ✅ **Responsive Design**: Tailwind CSS mobile-first approach ensures 320px-1920px viewport support with touch-friendly targets (44×44px minimum)
- ✅ **Minimal Dependencies**: Only essential dependencies added - MSAL for auth (required by Entra ID), IndexedDB wrapper (native API), Tailwind CSS (already in stack)
- ⚠️ **No Testing**: **VIOLATION NOTED** - User request includes "integration testing for login capabilities". Per Constitution Principle V (NON-NEGOTIABLE), NO automated tests are permitted. **ALTERNATIVE**: Manual verification checklist will be provided in quickstart.md for validating Entra ID configuration

### Constitution Violation Resolution

**User Request**: "In the plan include integration testing for the login capabilities to ensure we have things setup correctly in Entra ID."

**Constitutional Conflict**: Principle V explicitly prohibits ALL forms of automated testing including integration tests.

**Approved Alternative**: 
- Manual verification checklist in quickstart.md
- Step-by-step Entra ID configuration validation steps
- Browser-based manual testing procedures
- Documentation of expected authentication flow behaviors
- Troubleshooting guide for common Entra ID setup issues

The plan proceeds WITHOUT any test code, test frameworks, or CI/CD testing pipelines per constitutional mandate.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
frontend/
└── src/
    ├── components/           # Reusable UI components
    │   ├── auth/            # Auth-related components (LoginButton, UserProfile, etc.)
    │   ├── endpoints/       # Endpoint-related components (EndpointCard, EndpointList, etc.)
    │   ├── admin/           # Admin-specific components (ApprovalQueue, AdminActions, etc.)
    │   ├── layout/          # Layout components (Header, Footer, Navigation, etc.)
    │   └── common/          # Common UI elements (Button, Input, Modal, etc.)
    ├── pages/               # Page-level components/routes
    │   ├── Dashboard.tsx    # Main landing page (browse/search)
    │   ├── Register.tsx     # Endpoint registration form
    │   ├── MyRegistrations.tsx  # User's submitted endpoints
    │   ├── AdminApprovals.tsx   # Admin approval queue
    │   └── EndpointDetails.tsx  # Detailed endpoint view
    ├── services/            # Business logic and data access
    │   ├── auth.service.ts  # MSAL authentication logic
    │   ├── db.service.ts    # IndexedDB operations
    │   └── endpoint.service.ts  # Endpoint CRUD operations
    ├── types/               # TypeScript interfaces and types
    │   ├── user.types.ts
    │   ├── endpoint.types.ts
    │   └── registration.types.ts
    ├── utils/               # Utility functions
    │   ├── validation.ts    # Form validation helpers
    │   └── formatting.ts    # Date/text formatting helpers
    ├── config/              # Configuration
    │   └── msal.config.ts   # MSAL configuration
    ├── App.tsx              # Root application component
    ├── App.css              # Global styles (Tailwind base)
    ├── main.tsx             # Application entry point
    └── index.css            # Tailwind CSS imports

backend/                     # (Future phase - not part of this spec)
└── src/                     # Backend API endpoints (deferred)
```

**Structure Decision**: Web application structure (Option 2) selected. This is a frontend-focused feature with explicit backend deferral. The `frontend/src/` directory uses a feature-based organization (auth, endpoints, admin) combined with technical layers (components, pages, services). This structure supports the 4 user stories while maintaining clear separation of concerns and adhering to Clean Code First principle.

## Complexity Tracking

> **No complexity violations** - All constitution checks pass with one user request clarification (testing → manual verification)
