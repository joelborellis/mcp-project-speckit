# Task Breakdown: FastAPI Backend with PostgreSQL Database

**Feature**: 002-fastapi-postgres-backend  
**Date**: 2025-11-11  
**Status**: Ready for Implementation

## Task Overview

This document breaks down the implementation into actionable tasks organized by user story priority. Each task follows the strict checklist format: `- [ ] T### [P] [US#] Description with file path`.

**Total Tasks**: 51  
**MVP Scope**: US1 (API Endpoints) - Phases 1-7  
**P1 User Stories**: US1 (API Endpoints), US2 (User Management), US3 (Database Schema)  
**P2 User Stories**: US4 (Frontend Integration), US5 (Azure Config)

**Parallel Opportunities**: 
- Database schema (Phase 2) + Data models (Phase 3) can work in parallel after Phase 1
- Auth setup (Phase 4) + Service layer (Phase 5) can work in parallel
- US2 (User Management) and US3 (Database Schema) can be developed in parallel

---

## Phase 1: Setup (5 tasks)

Project initialization and foundational configuration.

- [x] T001 Initialize Python project with pyproject.toml for uv package manager (fastapi, uvicorn, asyncpg, pydantic, python-jose/PyJWT, python-dotenv, python-json-logger) in backend/pyproject.toml
- [x] T002 Create project directory structure (src/, routers/, services/, models/, schemas/, auth/) in backend/src/
- [x] T003 Create .env.example with DATABASE_URL, AZURE_CLIENT_ID, AZURE_TENANT_ID, ENTRA_ADMIN_GROUP_ID, CORS_ORIGINS in backend/.env.example
- [x] T004 Create backend README.md with setup instructions, running instructions, environment variables documentation in backend/README.md
- [x] T005 Create config.py to load environment variables and validate required settings in backend/src/config.py

---

## Phase 2: Foundational (8 tasks)

**User Story 3**: Database Schema and Migration Scripts (Priority: P1)

Blocking prerequisites that all other user stories depend on.

- [x] T006 [US3] Create database schema SQL script with users table (user_id, entra_id, email, display_name, is_admin, timestamps) in backend/scripts/db/init_schema.sql
- [x] T007 [US3] Add registrations table to schema SQL (registration_id, endpoint_url, endpoint_name, description, owner_contact, available_tools JSONB, status, submitter_id FK, approver_id FK, timestamps) in backend/scripts/db/init_schema.sql
- [x] T008 [US3] Add audit_log table to schema SQL (log_id, registration_id FK, user_id FK, action, previous_status, new_status, metadata JSONB, timestamp) in backend/scripts/db/init_schema.sql
- [x] T009 [US3] Add database indexes to schema (idx_users_entra_id unique, idx_registrations_endpoint_url unique, idx_registrations_status, idx_registrations_submitter_id, idx_registrations_created_at) in backend/scripts/db/init_schema.sql
- [x] T010 [US3] Add database constraints (CHECK status IN enum, CHECK action IN enum, UNIQUE constraints, NOT NULL constraints) in backend/scripts/db/init_schema.sql
- [x] T011 [US3] Add triggers for auto-updating updated_at timestamps on users and registrations tables in backend/scripts/db/init_schema.sql
- [x] T012 [US3] Create database connection module with asyncpg connection pool (10-20 connections), connection lifecycle management, error handling in backend/src/database.py
- [x] T013 [US3] Create database README with instructions for running init_schema.sql against PostgreSQL locally and in Azure in backend/scripts/db/README.md

---

## Phase 3: User Story 1 - API Endpoints (Data Models & Schemas, 6 tasks)

**Goal**: Create Pydantic models for request/response validation and internal data structures.

- [x] T014 [P] [US1] Create User Pydantic model with user_id, entra_id, email, display_name, is_admin, timestamps fields in backend/src/models/user.py
- [x] T015 [P] [US1] Create Registration Pydantic model with all fields (registration_id, endpoint_url, endpoint_name, description, owner_contact, available_tools, status, submitter_id, approver_id, timestamps) in backend/src/models/registration.py
- [x] T016 [P] [US1] Create AuditLog Pydantic model with log_id, registration_id, user_id, action, status fields, metadata in backend/src/models/audit_log.py
- [x] T017 [P] [US1] Create registration request schemas (CreateRegistrationRequest with validation: endpoint_url URL format, endpoint_name 3-200 chars, owner_contact email format, available_tools array) in backend/src/schemas/registration.py
- [x] T018 [P] [US1] Create registration response schemas (RegistrationResponse, RegistrationListResponse with pagination: total, limit, offset, results) in backend/src/schemas/registration.py
- [x] T019 [P] [US1] Create user response schemas (UserResponse, UpdateStatusRequest with status enum validation) in backend/src/schemas/user.py

---

## Phase 4: User Story 2 - User Management (Authentication & Authorization, 4 tasks)

**Goal**: Implement Entra ID token validation and admin permission checks.

- [x] T020 [US2] Create Entra ID token validator using python-jose/PyJWT to validate signature, issuer, audience, expiration in backend/src/auth/entra_validator.py
- [x] T021 [US2] Extract user claims from validated token (entra_id from 'sub', email, display_name) and return user info dict in backend/src/auth/entra_validator.py
- [x] T022 [US2] Create get_current_user FastAPI dependency that validates token, extracts user info, creates/updates user record in database, returns User model in backend/src/dependencies.py
- [x] T023 [US2] Create require_admin FastAPI dependency that calls get_current_user and checks is_admin flag, raises HTTPException 403 if not admin in backend/src/dependencies.py

---

## Phase 5: User Story 1 & 2 - Business Logic (Services, 8 tasks)

**Goal**: Implement service layer with business logic for users and registrations.

- [x] T024 [P] [US2] Create UserService.get_or_create_user method (INSERT ON CONFLICT DO UPDATE pattern to upsert user from Entra ID info) in backend/src/services/user_service.py
- [x] T025 [P] [US2] Create UserService.get_user_by_id method (SELECT user by user_id with error handling for not found) in backend/src/services/user_service.py
- [x] T026 [P] [US2] Create UserService.check_admin_status method (query Entra ID groups API or check cached is_admin flag) in backend/src/services/user_service.py
- [x] T027 [P] [US1] Create RegistrationService.create_registration method (INSERT new registration with status='Pending', submitter_id from current user, handle 409 conflict for duplicate endpoint_url) in backend/src/services/registration_service.py
- [x] T028 [P] [US1] Create RegistrationService.get_registrations method (SELECT with optional filters: status, submitter_id, search on endpoint_name/owner_contact, pagination: limit/offset, ORDER BY created_at DESC) in backend/src/services/registration_service.py
- [x] T029 [P] [US1] Create RegistrationService.get_registration_by_id method (SELECT registration by registration_id with error handling for not found) in backend/src/services/registration_service.py
- [x] T030 [US1] Create RegistrationService.update_registration_status method (UPDATE status, approver_id, approved_at for admin approval/rejection, validate status transition from Pending only) in backend/src/services/registration_service.py
- [x] T031 [US1] Create RegistrationService.delete_registration method (DELETE registration by registration_id for admin only) in backend/src/services/registration_service.py

---

## Phase 6: User Story 1 & 2 - API Routes (10 tasks)

**Goal**: Create FastAPI router endpoints mapping HTTP requests to service methods.

- [x] T032 [P] [US1] Create health check router GET /health (check database connection, return {"status": "healthy", "database": "connected"} or 503 if down) in backend/src/routers/health.py
- [x] T033 [US2] Create user router POST /users (call get_current_user dependency auto-creates/updates user, return user info, 201/200 status) in backend/src/routers/users.py
- [x] T034 [US2] Create user router GET /users/me (use get_current_user dependency, return current user's info) in backend/src/routers/users.py
- [x] T035 [US2] Create user router GET /users/{user_id} (call UserService.get_user_by_id, return user or 404) in backend/src/routers/users.py
- [x] T036 [US1] Create registration router POST /registrations (validate CreateRegistrationRequest, call RegistrationService.create_registration, return 201 or 409 conflict) in backend/src/routers/registrations.py
- [x] T037 [US1] Create registration router GET /registrations (parse query params: status, submitter_id, search, limit, offset, call RegistrationService.get_registrations, return paginated response) in backend/src/routers/registrations.py
- [x] T038 [US1] Create registration router GET /registrations/{registration_id} (call RegistrationService.get_registration_by_id, return registration or 404) in backend/src/routers/registrations.py
- [x] T039 [US1] Create registration router GET /registrations/my (use get_current_user dependency, call get_registrations filtered by current user's submitter_id) in backend/src/routers/registrations.py
- [x] T040 [US1] Create registration router PATCH /registrations/{registration_id}/status (use require_admin dependency, validate UpdateStatusRequest, call update_registration_status, return 200 or 400/403/404) in backend/src/routers/registrations.py
- [x] T041 [US1] Create registration router DELETE /registrations/{registration_id} (use require_admin dependency, call delete_registration, return 204 or 403/404) in backend/src/routers/registrations.py

---

## Phase 7: Application Setup (4 tasks)

**User Story 1**: Complete API application configuration.

- [x] T042 [US1] Create main.py FastAPI application (initialize FastAPI app, configure CORS with frontend origins from config, include all routers: health, users, registrations) in backend/src/main.py
- [x] T043 [US1] Configure structured JSON logging in main.py (use python-json-logger, set log level from environment, log startup/shutdown events) in backend/src/main.py
- [x] T044 [US1] Add startup event handler to main.py (initialize database connection pool, log successful connection or exit on failure) in backend/src/main.py
- [x] T045 [US1] Add shutdown event handler to main.py (close database connection pool gracefully) in backend/src/main.py

---

## Phase 8: User Story 4 - Frontend Integration (3 tasks)

**Goal**: Update frontend to replace IndexedDB with backend API calls.

**Priority**: P2 (depends on US1 completion)

- [x] T046 [US4] Update frontend api.service.ts (replace IndexedDB calls with fetch/axios HTTP requests to backend endpoints, add Authorization header with MSAL token) in frontend/src/services/api.service.ts
- [x] T047 [US4] Add error handling to api.service.ts (catch HTTP errors 401/403/404/409/500, display user-friendly error messages, handle token expiration with re-authentication prompt) in frontend/src/services/api.service.ts
- [x] T048 [US4] Remove IndexedDB code from frontend (delete db.service.ts and db.schema.ts, update imports in components to use api.service.ts only) in frontend/src/services/

**✅ Phase 8 Complete**: Frontend successfully integrated with backend API, all endpoints working.

**Additional Fixes Applied**:
- Fixed FastAPI route order (specific routes like `/my` must come before parameterized routes like `/{id}`)
- Implemented automatic admin status sync from Entra ID group membership to database
- Enhanced token claim extraction to support multiple claim sources (email, upn, unique_name, preferred_username)
- Fixed JSONB handling for PostgreSQL (Python list ↔ JSON string conversion)
- Fixed Pydantic model serialization (HttpUrl → string conversion, from_attributes config)
- Added comprehensive error handling and debug logging throughout authentication flow

---

## Phase 9: User Story 5 - Azure Configuration (3 tasks)

**Goal**: Configure backend to connect to Azure-hosted PostgreSQL database.

**Priority**: P2 (depends on US3 completion)

- [ ] T049 [US5] Create Azure PostgreSQL instance via Azure Portal or CLI (enable SSL/TLS enforcement, configure firewall rules) using Azure Portal/CLI
- [ ] T050 [US5] Run init_schema.sql against Azure PostgreSQL (connect using psql or Azure Data Studio, execute schema creation script) in Azure PostgreSQL
- [ ] T051 [US5] Configure backend for Azure (update DATABASE_URL environment variable with Azure connection string, test backend connection to Azure database, verify SSL/TLS encryption) in backend/.env (production)

---

- [ ] [T014] [P1] [US1,US2] Create User Pydantic model with user_id, entra_id, email, display_name, is_admin, timestamps fields → `backend/src/models/user.py`
- [ ] [T015] [P1] [US1] Create Registration Pydantic model with all fields from data model (registration_id, endpoint_url, endpoint_name, etc.) → `backend/src/models/registration.py`
- [ ] [T016] [P1] [US1] Create AuditLog Pydantic model with log_id, registration_id, user_id, action, status fields, metadata → `backend/src/models/audit_log.py`
- [ ] [T017] [P1] [US1] Create registration request schemas: CreateRegistrationRequest with validation (endpoint_url URL format, endpoint_name 3-200 chars, owner_contact email format, available_tools array) → `backend/src/schemas/registration.py`
- [ ] [T018] [P1] [US1] Create registration response schemas: RegistrationResponse, RegistrationListResponse with pagination (total, limit, offset, results) → `backend/src/schemas/registration.py`
- [ ] [T019] [P1] [US2] Create user response schemas: UserResponse, UpdateStatusRequest (status enum validation) → `backend/src/schemas/user.py`

---

## Phase 4: Authentication & Authorization (4 tasks)

Entra ID token validation and admin permission checks.

- [ ] [T020] [P1] [US2] Create Entra ID token validator using python-jose/PyJWT to validate signature, issuer, audience, expiration → `backend/src/auth/entra_validator.py`
- [ ] [T021] [P1] [US2] Extract user claims from validated token (entra_id from 'sub', email, display_name) and return user info dict → `backend/src/auth/entra_validator.py`
- [ ] [T022] [P1] [US2] Create get_current_user FastAPI dependency that validates token, extracts user info, creates/updates user record in database, returns User model → `backend/src/dependencies.py`
- [ ] [T023] [P1] [US2] Create require_admin FastAPI dependency that calls get_current_user and checks is_admin flag, raises HTTPException 403 if not admin → `backend/src/dependencies.py`

---

## Phase 5: Business Logic Services (6 tasks)

Service layer implementing business logic for users and registrations.

- [ ] [T024] [P1] [US2] Create UserService.get_or_create_user method: INSERT ON CONFLICT DO UPDATE pattern to upsert user from Entra ID info → `backend/src/services/user_service.py`
- [ ] [T025] [P1] [US2] Create UserService.get_user_by_id method: SELECT user by user_id with error handling for not found → `backend/src/services/user_service.py`
- [ ] [T026] [P1] [US2] Create UserService.check_admin_status method: query Entra ID groups API or check cached is_admin flag → `backend/src/services/user_service.py`
- [ ] [T027] [P1] [US1] Create RegistrationService.create_registration method: INSERT new registration with status='Pending', submitter_id from current user, handle 409 conflict for duplicate endpoint_url → `backend/src/services/registration_service.py`
- [ ] [T028] [P1] [US1] Create RegistrationService.get_registrations method: SELECT with optional filters (status, submitter_id, search on endpoint_name/owner_contact), pagination (limit/offset), ORDER BY created_at DESC → `backend/src/services/registration_service.py`
- [ ] [T029] [P1] [US1] Create RegistrationService.get_registration_by_id method: SELECT registration by registration_id with error handling for not found → `backend/src/services/registration_service.py`
- [ ] [T030] [P1] [US1] Create RegistrationService.update_registration_status method: UPDATE status, approver_id, approved_at for admin approval/rejection, validate status transition from Pending only → `backend/src/services/registration_service.py`
- [ ] [T031] [P1] [US1] Create RegistrationService.delete_registration method: DELETE registration by registration_id (admin only) → `backend/src/services/registration_service.py`

---

## Phase 6: API Routes (9 tasks)

FastAPI router endpoints mapping HTTP requests to service methods.

- [ ] [T032] [P1] [US1] Create health check router GET /health: check database connection, return {"status": "healthy", "database": "connected"} or 503 if database down → `backend/src/routers/health.py`
- [ ] [T033] [P1] [US2] Create user router POST /users: call get_current_user dependency (auto-creates/updates user), return user info, 201/200 status → `backend/src/routers/users.py`
- [ ] [T034] [P1] [US2] Create user router GET /users/me: use get_current_user dependency, return current user's info → `backend/src/routers/users.py`
- [ ] [T035] [P1] [US2] Create user router GET /users/{user_id}: call UserService.get_user_by_id, return user or 404 → `backend/src/routers/users.py`
- [ ] [T036] [P1] [US1] Create registration router POST /registrations: validate CreateRegistrationRequest, call RegistrationService.create_registration, return 201 or 409 conflict → `backend/src/routers/registrations.py`
- [ ] [T037] [P1] [US1] Create registration router GET /registrations: parse query params (status, submitter_id, search, limit, offset), call RegistrationService.get_registrations, return paginated response → `backend/src/routers/registrations.py`
- [ ] [T038] [P1] [US1] Create registration router GET /registrations/{registration_id}: call RegistrationService.get_registration_by_id, return registration or 404 → `backend/src/routers/registrations.py`
- [ ] [T039] [P1] [US1] Create registration router GET /registrations/my: use get_current_user dependency, call get_registrations filtered by current user's submitter_id → `backend/src/routers/registrations.py`
- [ ] [T040] [P1] [US1] Create registration router PATCH /registrations/{registration_id}/status: use require_admin dependency, validate UpdateStatusRequest, call update_registration_status, return 200 or 400/403/404 → `backend/src/routers/registrations.py`
- [ ] [T041] [P1] [US1] Create registration router DELETE /registrations/{registration_id}: use require_admin dependency, call delete_registration, return 204 or 403/404 → `backend/src/routers/registrations.py`

---

## Phase 7: FastAPI Application Setup (3 tasks)

Main application configuration, CORS, logging, and startup/shutdown hooks.

- [ ] [T042] [P1] [US1] Create main.py FastAPI application: initialize FastAPI app, configure CORS with frontend origins from config, include all routers (health, users, registrations) → `backend/src/main.py`
- [ ] [T043] [P1] [US1] Configure structured JSON logging in main.py: use python-json-logger, set log level from environment, log startup/shutdown events → `backend/src/main.py`
- [ ] [T044] [P1] [US1] Add startup event handler to main.py: initialize database connection pool, log successful connection or exit on failure → `backend/src/main.py`
- [ ] [T045] [P1] [US1] Add shutdown event handler to main.py: close database connection pool gracefully → `backend/src/main.py`

---

## Phase 8: Frontend Integration (3 tasks) - Priority P2

Update frontend to replace IndexedDB with backend API calls.

- [x] [T046] [P2] [US4] Update frontend api.service.ts: replace IndexedDB calls with fetch/axios HTTP requests to backend endpoints, add Authorization header with MSAL token → `frontend/src/services/api.service.ts`
- [x] [T047] [P2] [US4] Add error handling to api.service.ts: catch HTTP errors (401/403/404/409/500), display user-friendly error messages, handle token expiration with re-authentication prompt → `frontend/src/services/api.service.ts`
- [x] [T048] [P2] [US4] Remove IndexedDB code from frontend: delete db.service.ts and db.schema.ts, update imports in components to use api.service.ts only → `frontend/src/services/`

**✅ Phase 8 Complete**: All frontend integration tasks completed successfully.

---

## Phase 9: Azure PostgreSQL Configuration (3 tasks) - Priority P2

Configure backend to connect to Azure-hosted PostgreSQL database.

- [ ] [T049] [P2] [US5] Create Azure PostgreSQL instance via Azure Portal or CLI, enable SSL/TLS enforcement, configure firewall rules → Azure Portal/CLI
- [ ] [T050] [P2] [US5] Run init_schema.sql against Azure PostgreSQL: connect using psql or Azure Data Studio, execute schema creation script → Azure PostgreSQL
- [ ] [T051] [P2] [US5] Configure backend for Azure: update DATABASE_URL environment variable with Azure connection string, test backend connection to Azure database, verify SSL/TLS encryption → `backend/.env` (production)

---

## Task Dependencies

### Critical Path (MVP - US1 only):
1. Phase 1 (Foundation) → Phase 2 (Database) → Phase 3 (Models) → Phase 4 (Auth) → Phase 5 (Services) → Phase 6 (Routes) → Phase 7 (App Setup)

### Parallel Opportunities:
- **Phase 2 & Phase 3**: Database schema (T006-T013) and data models/schemas (T014-T019) can be worked in parallel after Phase 1
- **Phase 4 & Phase 5**: Auth setup (T020-T023) and service layer (T024-T031) can be worked in parallel after Phase 3
- **US2 & US3**: User Management tasks and Database Schema tasks can be worked in parallel (both P1)
- **Phase 8 & Phase 9**: Frontend integration (T046-T048) and Azure config (T049-T051) can be worked in parallel (both P2)

### Blocking Dependencies:
- Phase 6 (Routes) depends on Phase 5 (Services) completion
- Phase 7 (App Setup) depends on Phase 6 (Routes) completion
- Phase 8 (Frontend) depends on Phase 7 (App Setup) - backend must be running
- Phase 9 (Azure) can start after Phase 2 (Database schema ready)

---

## Task Status Legend

- `[ ]` Not started
- `[~]` In progress
- `[x]` Completed
- `[!]` Blocked

---

## MVP Recommendation

**Start with US1 (API Endpoints) only**: Tasks T001-T045 (Phases 1-7)

This delivers:
✅ Working FastAPI backend with all CRUD endpoints  
✅ Database schema and connection to PostgreSQL  
✅ Entra ID authentication and authorization  
✅ Health check endpoint for monitoring  
✅ Structured logging for observability  
✅ CORS configuration for frontend access  

**Defer to Phase 2**:
- US4 (Frontend Integration) - Tasks T046-T048
- US5 (Azure Configuration) - Tasks T049-T051

Frontend can continue using IndexedDB until backend is stable, then migrate in US4.

---

## Next Steps

1. ✅ Tasks breakdown completed
2. → Begin implementation with Phase 1 (Foundation) tasks T001-T005
3. → Review task dependencies before starting work to identify parallel opportunities
4. → Mark tasks as completed using checkboxes as you progress
5. → Update this document if new tasks are discovered during implementation

---

## Notes

- **Package Manager**: Use `uv` for all dependency installation (10-100x faster than pip)
- **No Testing**: Per project constitution, no unit tests, integration tests, or testing frameworks will be created
- **Manual Verification**: Use manual testing approaches from spec.md acceptance scenarios (curl, Postman, browser)
- **Idempotent SQL**: init_schema.sql uses CREATE TABLE IF NOT EXISTS for safe re-runs
- **Environment Variables**: Never commit .env with real credentials; use .env.example as template
- **Connection Pooling**: asyncpg pool configured in database.py for efficient connection management
- **Error Handling**: All services and routes include proper exception handling and HTTP status codes
- **Structured Logging**: JSON logging format compatible with Azure Application Insights
