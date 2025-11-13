# Tasks: Browse Functionality, Approval Status Query API, and Audit Logging

**Input**: Design documents from `/specs/003-browse-audit-query/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/api-endpoints.md, contracts/browse-page-ui.md

**Note**: This project does NOT include automated testing per constitutional mandate. All quality assurance is performed through code review and manual verification per quickstart.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and verification of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a **web application** with separate frontend and backend:
- Backend: `backend/src/`
- Frontend: `frontend/src/`
- Database scripts: `backend/scripts/db/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify project structure and dependencies are ready

- [x] T001 Verify backend dependencies installed (FastAPI >=0.115.0, asyncpg >=0.30.0, Pydantic >=2.9.0)
- [x] T002 Verify frontend dependencies installed (React ^19.2.0, React Router ^7.9.5, Tailwind CSS ^3.4.18)
- [x] T003 Verify PostgreSQL database accessible and schema up-to-date per `backend/scripts/db/init_schema.sql`
- [x] T004 Verify audit_log table exists with indexes on registration_id and timestamp

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core services and components that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 [P] Create AuditService class in `backend/src/services/audit_service.py` with log_action() and query_logs() methods
- [x] T006 [P] Create AuditLog Pydantic schemas in `backend/src/schemas/audit_log.py` (AuditLogResponse, AuditLogListResponse)
- [x] T007 [P] Create audit log router in `backend/src/routers/audit_logs.py` with GET /audit-logs endpoint (admin-only, with filters)
- [x] T008 [P] Create StatusBadge component in `frontend/src/components/common/StatusBadge.tsx` (reusable status indicator)
- [x] T009 [P] Create AuditLog TypeScript types in `frontend/src/types/audit-log.types.ts`
- [x] T010 Extend RegistrationService in `backend/src/services/registration_service.py` to wrap operations in transactions and call AuditService.log_action()
- [x] T011 Update existing create_registration method to log 'Created' action with metadata
- [x] T012 Update existing update_registration_status method to log 'Approved'/'Rejected' actions with previous/new status
- [x] T013 Register audit_logs router in `backend/src/main.py` app.include_router()

**Checkpoint**: Audit logging infrastructure ready - all registration modifications now create audit logs automatically

---

## Phase 3: User Story 1 - Browse All Registered MCP Servers (Priority: P1) 🎯 MVP

**Goal**: Enable all users to discover registered MCP servers via comprehensive Browse page with search, pagination, and detailed view

**Manual Verification**: 
1. Login as non-admin user and navigate to `/` (Browse page)
2. Verify only Approved registrations display in card grid
3. Use search box to filter by name/description/owner
4. Click pagination controls to navigate pages
5. Click a card to open detailed view modal
6. Login as admin and verify all statuses (Pending/Approved/Rejected) display
7. Test on mobile viewport (320px) and desktop (1440px)

### Implementation for User Story 1 - Frontend Components

- [x] T014 [P] [US1] Create BrowseSearch component in `frontend/src/components/browse/BrowseSearch.tsx` (search input with clear button)
- [x] T015 [P] [US1] Create BrowseCard component in `frontend/src/components/browse/BrowseCard.tsx` (registration card with truncated description)
- [x] T016 [P] [US1] Create BrowseList component in `frontend/src/components/browse/BrowseList.tsx` (responsive grid container with empty state)
- [x] T017 [P] [US1] Create Pagination component in `frontend/src/components/browse/Pagination.tsx` (page numbers with prev/next buttons)
- [x] T018 [P] [US1] Create RegistrationDetailModal component in `frontend/src/components/browse/RegistrationDetailModal.tsx` (full metadata display)
- [x] T019 [US1] Create BrowsePage in `frontend/src/pages/BrowsePage.tsx` integrating all browse components with search and pagination logic
- [x] T020 [US1] Update `frontend/src/App.tsx` to replace placeholder BrowsePage route at path `/` with real BrowsePage component
- [x] T021 [US1] Add client-side filtering logic in BrowsePage (filter registrations by search query against name/description/owner)
- [x] T022 [US1] Add pagination logic in BrowsePage (20 items per page, calculate totalPages, slice paginatedResults)
- [x] T023 [US1] Add admin vs non-admin filtering in BrowsePage useEffect (fetch all if admin, status=Approved if non-admin)
- [x] T024 [US1] Import and use StatusBadge in BrowseCard and RegistrationDetailModal

**Checkpoint**: At this point, User Story 1 should be fully functional - Browse page displays registrations, search works, pagination works, detailed view modal opens, admin/non-admin filtering works

---

## Phase 4: User Story 2 - Programmatic Query of Approval Status (Priority: P2)

**Goal**: Provide API endpoint for CI/CD pipelines and monitoring systems to query registration status by endpoint URL

**Manual Verification**:
1. Get access token from authenticated session
2. Use curl to query: `GET /registrations/by-url?endpoint_url=https://example.com/mcp`
3. Verify 200 response with full registration details
4. Query non-existent URL and verify 404 response
5. Test without token and verify 401 response
6. Measure response time <200ms

### Implementation for User Story 2 - Backend API

- [x] T025 [US2] Add GET /by-url endpoint in `backend/src/routers/registrations.py` (query param: endpoint_url, return RegistrationResponse)
- [x] T026 [US2] Implement get_registration_by_url() method in `backend/src/services/registration_service.py` (query registrations table by endpoint_url)
- [x] T027 [US2] Add URL decoding logic in endpoint handler (handle URL-encoded parameters correctly)
- [x] T028 [US2] Add 404 error response when URL not found with message "No registration found for the given endpoint URL."
- [x] T029 [US2] Verify unique index on registrations.endpoint_url exists (should already exist from feature 002 schema)
- [x] T030 [US2] Add authentication requirement to endpoint (require valid Entra ID token, return 401 if missing)

### Implementation for User Story 2 - Frontend API Service

- [x] T031 [P] [US2] Add getRegistrationByUrl() function in `frontend/src/services/api.service.ts` (call GET /registrations/by-url with encoded URL)
- [x] T032 [P] [US2] Add error handling for 404 (throw APIError with "Registration not found" message)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - Browse page works, and API query by URL works

---

## Phase 5: User Story 3 - Comprehensive Audit Logging (Priority: P1)

**Goal**: Track all registration modifications with who/what/when for compliance and troubleshooting

**Manual Verification**:
1. Create a new registration via UI and query audit_log table - verify 'Created' entry exists
2. Approve the registration as admin and verify 'Approved' entry with previous_status='Pending', new_status='Approved'
3. Login as admin and query: `GET /audit-logs?registration_id={id}`
4. Verify both entries returned in reverse chronological order
5. Query by user_id, action type, and date range - verify filters work
6. Test as non-admin and verify 403 Forbidden response

### Implementation for User Story 3 - Backend Audit Logging (Most work done in Phase 2)

- [x] T033 [US3] Add metadata capture to create_registration audit log (include all initial field values in JSONB metadata) - DONE in Phase 2 (T011)
- [x] T034 [US3] Add metadata capture to approve/reject audit logs (include optional reason text if provided by admin) - DONE in Phase 2 (T012)
- [x] T035 [US3] Implement Update action logging in update_registration method (capture changed fields with before/after values) - NOT APPLICABLE (no update_registration method exists, only update_registration_status which logs in T012)
- [x] T036 [US3] Implement Delete action logging (create audit log entry before deletion in delete_registration method)
- [x] T037 [US3] Update audit_log foreign key constraint to NOT CASCADE on registration deletion (preserve logs after registration deleted)
- [x] T038 [US3] Add query parameter validation in GET /audit-logs endpoint (validate date range: end must be after start, return 400 if invalid) - DONE in Phase 2 (T007)
- [x] T039 [US3] Add pagination to GET /audit-logs (default limit=50, max limit=200, offset parameter) - DONE in Phase 2 (T007)
- [x] T040 [US3] Add admin authorization check in GET /audit-logs endpoint (return 403 Forbidden for non-admin users) - DONE in Phase 2 (T007)
- [ ] T041 [US3] Test audit log query filters: registration_id, user_id, action, from/to dates (verify SQL queries with indexes) - MANUAL VERIFICATION

### Implementation for User Story 3 - Frontend API Service

- [x] T042 [P] [US3] Add getAuditLogs() function in `frontend/src/services/api.service.ts` (call GET /audit-logs with filter params)
- [x] T043 [P] [US3] Add error handling for 403 (throw APIError with "Admin privileges required" message)

**Checkpoint**: All user stories should now be independently functional - Browse page works, query API works, and all registration changes create audit logs queryable by admins

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T044 [P] Add ESC key listener to RegistrationDetailModal in `frontend/src/components/browse/RegistrationDetailModal.tsx` (close modal on ESC)
- [x] T045 [P] Add loading spinner to Browse page in `frontend/src/pages/BrowsePage.tsx` (show during initial data fetch) - DONE in Phase 3
- [x] T046 [P] Add error toast notifications throughout Browse page using react-hot-toast
- [x] T047 [P] Verify responsive breakpoints work: mobile 320px (1 column), tablet 768px (2 columns), desktop 1024px (3 columns) - DONE in Phase 3 (BrowseList)
- [x] T048 [P] Add aria-labels to all icon buttons (search clear button, modal close button) for accessibility - DONE in Phase 3
- [ ] T049 [P] Test keyboard navigation through Browse page (tab through cards, pagination, search) - MANUAL TESTING
- [ ] T050 Verify all success criteria from spec.md (SC-001 through SC-010) using quickstart.md manual verification steps - MANUAL VERIFICATION
- [ ] T051 Code review: Check Browse components follow existing patterns from MyRegistrationsPage and AdminApprovalsPage - CODE REVIEW
- [ ] T052 Code review: Check backend services follow clean code patterns from existing RegistrationService - CODE REVIEW
- [ ] T053 Performance check: Verify Browse page loads in <2s, search responds <500ms, query API <200ms, audit logs <1s - MANUAL PERFORMANCE TESTING
- [ ] T054 Update documentation: Ensure quickstart.md manual verification steps match implemented functionality - DOCUMENTATION

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) - Browse page needs StatusBadge and audit logging foundation
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2) - Query API needs audit logging for queried registrations
- **User Story 3 (Phase 5)**: Depends on Foundational (Phase 2) - Audit logging core already built in Phase 2, this phase completes it
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent from US1, but often tested via Browse page
- **User Story 3 (P1)**: Starts in Foundational (Phase 2), completed in Phase 5 - Independent verification via database queries

### Within Each User Story

**User Story 1 (Browse)**:
1. All frontend components marked [P] can be built in parallel (BrowseSearch, BrowseCard, BrowseList, Pagination, RegistrationDetailModal)
2. Then BrowsePage integrates them (T019)
3. Then add logic and routing (T020-T024)

**User Story 2 (Query API)**:
1. Backend endpoint and service can proceed together (T025, T026 in parallel)
2. Then add validation and error handling (T027-T030)
3. Frontend API service can be built in parallel with backend (T031-T032 marked [P])

**User Story 3 (Audit Logging)**:
1. Core audit service built in Foundational phase (T005-T013)
2. Phase 5 completes metadata capture and query features (T033-T041)
3. Frontend API service can be built in parallel (T042-T043 marked [P])

### Parallel Opportunities

- **Setup (Phase 1)**: All verification tasks (T001-T004) can run in parallel
- **Foundational (Phase 2)**: T005-T009 marked [P] can run in parallel, then T010-T013 in sequence
- **User Story 1**: All component creation tasks (T014-T018) marked [P] can run in parallel
- **User Story 2**: Backend (T025-T030) and Frontend (T031-T032) can run in parallel
- **User Story 3**: Frontend tasks (T042-T043) marked [P] can run in parallel with backend work
- **Polish (Phase 6)**: T044-T049, T051-T052 marked [P] can run in parallel

---

## Parallel Example: User Story 1 (Browse Page)

```bash
# Launch all Browse components together:
Task T014: "Create BrowseSearch component"
Task T015: "Create BrowseCard component"
Task T016: "Create BrowseList component"
Task T017: "Create Pagination component"
Task T018: "Create RegistrationDetailModal component"

# Then integrate them:
Task T019: "Create BrowsePage integrating all components"
Task T020: "Update App.tsx to use BrowsePage"
Task T021-T024: "Add filtering, pagination, and admin logic"
```

---

## Implementation Strategy

### MVP First (User Stories 1 and 3 Only)

Since both User Story 1 (Browse) and User Story 3 (Audit Logging) are marked P1 priority, the MVP includes:

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - includes audit service foundation)
3. Complete Phase 3: User Story 1 (Browse Page)
4. Complete Phase 5: User Story 3 (Complete Audit Logging)
5. **STOP and VALIDATE**: Manually verify both stories independently per quickstart.md
6. Deploy/demo if ready

User Story 2 (Query API) is P2 and can be added as an enhancement.

### Incremental Delivery

1. **Foundation**: Complete Setup + Foundational → Audit logging infrastructure ready
2. **MVP (P1 stories)**: 
   - Add User Story 1 (Browse) → Verify independently → Deploy/Demo
   - Complete User Story 3 (Audit) → Verify independently → Deploy/Demo
3. **Enhancement (P2 story)**:
   - Add User Story 2 (Query API) → Verify independently → Deploy/Demo
4. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (especially T005-T013 audit service)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (Browse Page - Frontend heavy)
   - **Developer B**: User Story 3 (Audit Logging - Backend heavy)
   - **Developer C**: User Story 2 (Query API - Backend + minimal Frontend)
3. Stories complete and integrate independently

---

## Task Count Summary

- **Total Tasks**: 54
- **Setup (Phase 1)**: 4 tasks
- **Foundational (Phase 2)**: 9 tasks (BLOCKING)
- **User Story 1 - Browse (P1)**: 11 tasks (Frontend heavy)
- **User Story 2 - Query API (P2)**: 8 tasks (Backend + Frontend API)
- **User Story 3 - Audit Logging (P1)**: 11 tasks (Backend heavy, extends Phase 2)
- **Polish (Phase 6)**: 11 tasks (Cross-cutting)

**Parallelizable Tasks**: 24 tasks marked [P] can run in parallel within their phases

**Independent Test Criteria**:
- **US1**: Browse page displays registrations, search/pagination work, modal opens, responsive design verified (per quickstart.md tests 1-6)
- **US2**: API returns registration by URL, 404 for missing, 401 for unauthorized, <200ms response time (per quickstart.md test 7)
- **US3**: All CRUD operations create audit logs, audit query API works with filters, admin-only access enforced (per quickstart.md tests 8-12)

**Suggested MVP Scope**: 
- User Story 1 (Browse Page) + User Story 3 (Audit Logging) = 31 tasks total
- Provides complete discovery interface and compliance foundation
- User Story 2 (Query API) can be added as post-MVP enhancement (8 additional tasks)

---

## Notes

- [P] tasks = different files, no dependencies within their phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and verifiable through manual testing per quickstart.md
- Constitutional mandate: No automated tests - all verification via manual steps in quickstart.md
- Commit after each task or logical group for granular version control
- Stop at any checkpoint to validate story independently before proceeding
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All file paths are absolute and match existing project structure (backend/src/, frontend/src/)
