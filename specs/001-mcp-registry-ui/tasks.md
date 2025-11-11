# Tasks: MCP Registry Web Application

**Feature Branch**: `001-mcp-registry-ui`  
**Input**: Design documents from `/specs/001-mcp-registry-ui/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Note**: This project does NOT include automated testing per constitutional mandate. All quality assurance is performed through code review and manual verification as defined in quickstart.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and verification of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

This is a web application with monorepo structure:
- **Frontend**: `frontend/src/`
- **Backend**: Deferred to future specification

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Verify Vite project structure matches plan.md (frontend/ with src/, public/, package.json)
- [X] T002 Install additional dependencies: @azure/msal-browser, @azure/msal-react, dexie, react-router-dom, react-hot-toast
- [X] T003 [P] Configure Tailwind CSS with red/white theme in frontend/tailwind.config.js
- [X] T004 [P] Create TypeScript type definitions structure in frontend/src/types/
- [X] T005 [P] Setup environment variables template in frontend/.env.example

**Checkpoint**: Project structure ready, dependencies installed

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Configure MSAL for Entra ID in frontend/src/config/msal.config.ts
- [X] T007 Create AuthContext provider in frontend/src/context/AuthContext.tsx
- [X] T008 Create useAuth hook in frontend/src/hooks/useAuth.ts
- [X] T009 Initialize Dexie database schema in frontend/src/services/db.schema.ts
- [X] T010 Create database service layer in frontend/src/services/db.service.ts
- [X] T011 [P] Create User type definition in frontend/src/types/user.types.ts
- [X] T012 [P] Create MCPEndpoint and EndpointStatus types in frontend/src/types/endpoint.types.ts
- [X] T013 [P] Create RegistrationSubmission type in frontend/src/types/registration.types.ts
- [X] T014 Create validation utilities in frontend/src/utils/validation.ts
- [X] T015 [P] Create formatting utilities in frontend/src/utils/formatting.ts (includes timestamp display per FR-020)
- [X] T016 Setup React Router with base structure in frontend/src/App.tsx
- [X] T017 Create ProtectedRoute wrapper component in frontend/src/components/common/ProtectedRoute.tsx
- [X] T018 Create base layout components (Header, Footer, Navigation) in frontend/src/components/layout/
- [X] T019 Setup error boundary in frontend/src/components/common/ErrorBoundary.tsx
- [X] T020 Configure toast notifications in frontend/src/main.tsx

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Authentication and Authorization (Priority: P1) 🎯 MVP

**Goal**: Users can securely authenticate via Microsoft Entra ID and the system correctly identifies admin vs regular users based on Entra ID group membership.

**Manual Verification**: Follow authentication test cases in quickstart.md (Tests 1-4)

### Implementation for User Story 1

- [ ] T021 [P] [US1] Create LoginButton component in frontend/src/components/auth/LoginButton.tsx
- [ ] T022 [P] [US1] Create UserProfile component in frontend/src/components/auth/UserProfile.tsx
- [ ] T023 [US1] Implement authentication service in frontend/src/services/auth.service.ts
- [ ] T024 [US1] Create login page component in frontend/src/pages/LoginPage.tsx
- [ ] T025 [US1] Implement admin role detection logic in AuthContext (check Entra ID groups)
- [ ] T026 [US1] Add logout functionality to UserProfile component
- [ ] T027 [US1] Create AdminBadge component in frontend/src/components/auth/AdminBadge.tsx
- [ ] T028 [US1] Implement token refresh handling in auth.service.ts
- [ ] T029 [US1] Add authentication state persistence across page reloads
- [ ] T030 [US1] Setup redirect logic for unauthenticated users

**Checkpoint**: Authentication flow complete - users can login, logout, and admin role is correctly identified

---

## Phase 4: User Story 2 - Browse and Search MCP Registry (Priority: P1) 🎯 MVP

**Goal**: Authenticated users can browse all approved MCP endpoints and search/filter them in real-time by name, owner, or tools.

**Manual Verification**: Follow browse and search test cases in quickstart.md (Tests 13-15)

**Dependencies**: Requires US1 (authentication) to be complete

### Implementation for User Story 2

- [ ] T031 [P] [US2] Create EndpointCard component in frontend/src/components/endpoints/EndpointCard.tsx
- [ ] T032 [P] [US2] Create EndpointList component in frontend/src/components/endpoints/EndpointList.tsx
- [ ] T033 [P] [US2] Create SearchBar component in frontend/src/components/common/SearchBar.tsx
- [ ] T034 [US2] Implement getAllApprovedEndpoints in frontend/src/services/endpoint.service.ts
- [ ] T035 [US2] Implement searchEndpoints with debouncing in frontend/src/services/endpoint.service.ts
- [ ] T036 [US2] Create Dashboard page in frontend/src/pages/Dashboard.tsx
- [ ] T037 [US2] Create EndpointDetails page in frontend/src/pages/EndpointDetails.tsx
- [ ] T038 [US2] Implement useEndpointSearch custom hook in frontend/src/hooks/useEndpointSearch.ts
- [ ] T039 [US2] Add responsive grid layout for endpoint cards (mobile/tablet/desktop breakpoints)
- [ ] T040 [US2] Add empty state message when no endpoints exist or search returns no results
- [ ] T041 [US2] Add loading states during data fetch
- [ ] T042 [US2] Style components with red/white color scheme per Tailwind config

**Checkpoint**: Users can browse and search approved endpoints with responsive design

---

## Phase 5: User Story 3 - Register New MCP Endpoint (Priority: P2)

**Goal**: Authenticated users can submit new MCP endpoint registrations with validation, and submissions are placed in "Pending" status awaiting admin approval.

**Manual Verification**: Follow registration test cases in quickstart.md (Tests 7-12)

**Dependencies**: Requires US1 (authentication) to be complete

### Implementation for User Story 3

- [ ] T043 [P] [US3] Create RegistrationForm component in frontend/src/components/forms/RegistrationForm.tsx
- [ ] T044 [P] [US3] Create FormInput component in frontend/src/components/common/FormInput.tsx
- [ ] T045 [P] [US3] Create FormTextarea component in frontend/src/components/common/FormTextarea.tsx
- [ ] T046 [US3] Implement createEndpoint in frontend/src/services/endpoint.service.ts
- [ ] T047 [US3] Implement isURLUnique check in frontend/src/services/endpoint.service.ts
- [ ] T048 [US3] Create Register page in frontend/src/pages/RegisterPage.tsx
- [ ] T049 [US3] Implement form validation (URL format, required fields, field lengths)
- [ ] T050 [US3] Implement tools input parsing (comma-separated to array)
- [ ] T051 [US3] Add URL uniqueness validation before submission
- [ ] T052 [US3] Create MyRegistrations page in frontend/src/pages/MyRegistrationsPage.tsx
- [ ] T053 [US3] Implement getUserRegistrations in frontend/src/services/endpoint.service.ts
- [ ] T054 [US3] Add status badges to registration list (Pending/Approved/Rejected)
- [ ] T055 [US3] Add success toast notification after successful registration
- [ ] T056 [US3] Add error handling and display validation errors inline

**Checkpoint**: Users can register new endpoints and view their submissions with status

---

## Phase 6: User Story 4 - Admin Approval Workflow (Priority: P2)

**Goal**: Admin users can review pending endpoint registrations and approve, reject, or remove them. Non-admins cannot access admin features.

**Manual Verification**: Follow admin approval test cases in quickstart.md (Tests 16-21)

**Dependencies**: Requires US1 (authentication + admin role detection) and US3 (endpoints to review) to be complete

### Implementation for User Story 4

- [ ] T057 [P] [US4] Create ApprovalQueue component in frontend/src/components/admin/ApprovalQueue.tsx
- [ ] T058 [P] [US4] Create ApprovalCard component in frontend/src/components/admin/ApprovalCard.tsx
- [ ] T059 [P] [US4] Create ConfirmDialog component in frontend/src/components/common/ConfirmDialog.tsx
- [ ] T060 [US4] Implement getPendingApprovals in frontend/src/services/endpoint.service.ts
- [ ] T061 [US4] Implement updateEndpointStatus (approve/reject) in frontend/src/services/endpoint.service.ts
- [ ] T062 [US4] Implement deleteEndpoint (remove) in frontend/src/services/endpoint.service.ts
- [ ] T063 [US4] Create AdminApprovals page in frontend/src/pages/AdminApprovalsPage.tsx
- [ ] T064 [US4] Add admin-only route protection (requireAdmin flag in ProtectedRoute)
- [ ] T065 [US4] Implement approval action with confirmation dialog
- [ ] T066 [US4] Implement rejection action with confirmation dialog
- [ ] T067 [US4] Implement remove action for approved endpoints
- [ ] T068 [US4] Add self-review prevention (disable approve/reject for own submissions)
- [ ] T069 [US4] Add timestamp tracking for review actions (reviewerId, reviewerName, reviewTimestamp per FR-020)
- [ ] T070 [US4] Update UI after approval/rejection/removal actions
- [ ] T071 [US4] Add success/error toast notifications for admin actions
- [ ] T072 [US4] Add "Pending Approvals" navigation link (visible only to admins)

**Checkpoint**: Admin users can manage endpoint approvals, regular users cannot access admin features

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T073 [P] Add responsive design verification for all pages (320px to 1920px)
- [ ] T074 [P] Ensure all touch targets meet 44x44px minimum size
- [ ] T075 [P] Add ARIA labels for accessibility
- [ ] T076 [P] Optimize performance: check search debounce, minimize re-renders
- [ ] T077 [P] Add loading spinners for async operations
- [ ] T078 Add 404 page for invalid routes in frontend/src/pages/NotFoundPage.tsx
- [ ] T079 Review and refactor duplicate code across components
- [ ] T080 Verify red/white color scheme consistency across all pages
- [ ] T081 Add helpful error messages for common scenarios (no internet, auth failure, etc.)
- [ ] T082 Test error boundary fallback UI
- [ ] T083 Verify all environment variables documented in .env.example
- [ ] T084 Run through all manual verification tests in quickstart.md
- [ ] T085 Document any deviations from original plan in plan.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion
- **User Story 2 (Phase 4)**: Depends on Foundational + US1 (authentication required)
- **User Story 3 (Phase 5)**: Depends on Foundational + US1 (authentication required)
- **User Story 4 (Phase 6)**: Depends on Foundational + US1 (admin role) + US3 (endpoints to approve)
- **Polish (Phase 7)**: Depends on desired user stories being complete

### User Story Dependencies

```
Foundational (Phase 2)
    ↓
US1: Authentication (P1) ← MVP START
    ↓
    ├─→ US2: Browse/Search (P1) ← MVP COMPLETE (US1 + US2)
    │
    ├─→ US3: Registration (P2) ← Independent feature
    │       ↓
    │       └─→ US4: Admin Approval (P2) ← Depends on US3
    │
    └─→ (US2 and US3 can run in parallel after US1)
```

### Within Each User Story

**US1 (Authentication)**:
- Components can be built in parallel (LoginButton, UserProfile, AdminBadge)
- Auth service must complete before integration
- AuthContext must be updated with admin role logic

**US2 (Browse/Search)**:
- Components can be built in parallel (EndpointCard, EndpointList, SearchBar)
- Services (getAllApprovedEndpoints, searchEndpoints) can be built in parallel
- Pages integrate components after components are ready

**US3 (Registration)**:
- Form components can be built in parallel (FormInput, FormTextarea)
- Validation and service methods before form integration
- MyRegistrations page independent from registration form

**US4 (Admin Approval)**:
- Components can be built in parallel (ApprovalQueue, ApprovalCard, ConfirmDialog)
- Service methods (getPending, approve, reject, remove) can be built in parallel
- Page integrates components after ready

### Parallel Opportunities

**Setup Phase**: T003, T004, T005 can run in parallel (different files)

**Foundational Phase**: T011, T012, T013, T015 can run in parallel (type definitions and utilities)

**US1**: T021, T022 can run in parallel (separate components)

**US2**: T031, T032, T033 can run in parallel (separate components)

**US3**: T043, T044, T045 can run in parallel (separate form components)

**US4**: T057, T058, T059 can run in parallel (separate components)

**Polish**: T073, T074, T075, T076, T077 can run in parallel (different concerns)

---

## Parallel Example: User Story 2 (Browse/Search)

```bash
# Launch all US2 components together:
Task T031: "Create EndpointCard component"
Task T032: "Create EndpointList component"
Task T033: "Create SearchBar component"

# Then launch service methods in parallel:
Task T034: "Implement getAllApprovedEndpoints"
Task T035: "Implement searchEndpoints"

# Then integrate in pages:
Task T036: "Create Dashboard page"
Task T037: "Create EndpointDetails page"
```

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Authentication) ✅
4. Complete Phase 4: User Story 2 (Browse/Search) ✅
5. **STOP and VALIDATE**: Run manual verification tests for US1 and US2
6. **Deploy MVP**: Users can login and browse approved endpoints

### Incremental Delivery

1. **MVP**: Setup + Foundational + US1 + US2 → Deploy (Browse registry)
2. **Increment 1**: Add US3 (Registration) → Deploy (Users can submit endpoints)
3. **Increment 2**: Add US4 (Admin Approval) → Deploy (Full workflow with governance)
4. **Increment 3**: Polish phase → Final improvements

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together**
2. **After Foundational completion:**
   - Developer A: US1 (Authentication) - MUST complete first
3. **After US1 completion:**
   - Developer A: US2 (Browse/Search)
   - Developer B: US3 (Registration)
4. **After US3 completion:**
   - Developer C: US4 (Admin Approval)
5. **All developers**: Polish phase together

---

## Task Summary

- **Total Tasks**: 85
- **Setup**: 5 tasks
- **Foundational**: 15 tasks (CRITICAL PATH)
- **US1 (Authentication - P1)**: 10 tasks
- **US2 (Browse/Search - P1)**: 12 tasks
- **US3 (Registration - P2)**: 14 tasks
- **US4 (Admin Approval - P2)**: 16 tasks
- **Polish**: 13 tasks

**Parallel Opportunities**: 23 tasks marked [P] can run in parallel

**MVP Scope (US1 + US2)**: 42 tasks (Setup + Foundational + US1 + US2)

---

## Manual Verification Checkpoints

After completing each phase, refer to quickstart.md for manual verification:

- **Phase 3 Complete**: Run Authentication tests (Tests 1-4)
- **Phase 4 Complete**: Run Browse/Search tests (Tests 13-15)
- **Phase 5 Complete**: Run Registration tests (Tests 7-12)
- **Phase 6 Complete**: Run Admin Approval tests (Tests 16-21)
- **Phase 7 Complete**: Run all tests including Responsive Design (Tests 22-24) and Error Handling (Tests 25-26)

**Final Sign-Off**: Complete manual verification sign-off checklist in quickstart.md before considering feature complete.

---

## Notes

- All tasks follow constitution: NO automated tests, manual verification only
- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and verifiable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Database operations in db.service.ts wrap Dexie calls per contracts/indexeddb-schema.md
- Validation functions in validation.ts implement rules per contracts/validation-schema.md
