# Quickstart Guide: Browse, Audit, and Query Feature

**Feature**: 003-browse-audit-query  
**Last Updated**: 2025-11-12

This guide provides step-by-step instructions for developers implementing and manually verifying this feature.

---

## Prerequisites

Before starting, ensure you have:

1. **Development Environment**:
   - Python 3.13+ installed
   - Node.js 18+ and npm installed
   - PowerShell (for Windows scripts)
   - Git configured

2. **Azure Resources** (from feature 002):
   - Azure Database for PostgreSQL instance running
   - Database initialized with schema from `backend/scripts/db/init_schema.sql`
   - Connection string stored in `.env` file

3. **Authentication** (from feature 001):
   - Microsoft Entra ID app registration created
   - Tenant ID, Client ID configured in frontend `.env`
   - User accounts with admin role for testing

4. **Feature Branch**:
   ```powershell
   git checkout 003-browse-audit-query
   ```

5. **Dependencies Installed**:
   ```powershell
   # Backend
   cd backend
   pip install -e .
   
   # Frontend
   cd ../frontend
   npm install
   ```

---

## Environment Configuration

### Backend `.env` (in `backend/` directory)

```env
# Database
DATABASE_URL=postgresql://user:pass@host.postgres.database.azure.com:5432/mcp_registry?sslmode=require

# Azure Entra ID
ENTRA_TENANT_ID=your-tenant-id
ENTRA_CLIENT_ID=your-client-id

# Admin Configuration
ADMIN_GROUP_ID=your-admin-group-id

# Optional: Logging
LOG_LEVEL=INFO
```

### Frontend `.env` (in `frontend/` directory)

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_ENTRA_CLIENT_ID=your-client-id
VITE_ENTRA_TENANT_ID=your-tenant-id
VITE_ENTRA_REDIRECT_URI=http://localhost:5173
```

**Note**: API base URL should point to backend server (default: `http://localhost:8000`)

---

## Running the Application

### Terminal 1: Backend API

```powershell
cd backend
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Health Check**:
```powershell
curl http://localhost:8000/health
# Expected: {"status":"healthy","database":"connected"}
```

### Terminal 2: Frontend Dev Server

```powershell
cd frontend
npm run dev
```

**Expected Output**:
```
VITE v7.2.2  ready in 431 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
➜  press h + enter to show help
```

**Access Application**: Open browser to `http://localhost:5173`

---

## Manual Verification Steps

### Setup: Create Test Data

Before testing, create sample registrations in the database:

```powershell
cd backend
python make_admin.py seed-test-data  # (Create this helper if needed)
```

Or manually insert via psql:
```sql
INSERT INTO registrations (
  registration_id, endpoint_name, endpoint_url, description, 
  owner_contact, available_tools, status, submitter_user_id
) VALUES
  (gen_random_uuid(), 'Weather MCP', 'http://weather.example.com', 
   'Weather forecast data', 'weather@example.com', '[]', 'Approved', 'user1'),
  (gen_random_uuid(), 'Finance MCP', 'http://finance.example.com', 
   'Stock market analysis', 'finance@example.com', '[]', 'Pending', 'user2'),
  (gen_random_uuid(), 'News MCP', 'http://news.example.com', 
   'Latest news aggregation', 'news@example.com', '[]', 'Rejected', 'user3');
```

---

### Test 1: Browse Page - Non-Admin User

**Objective**: Verify non-admin users see only approved registrations

**Steps**:
1. Login as non-admin user via Microsoft auth
2. Navigate to Browse page (root path `/`)
3. Observe card grid display

**Success Criteria (SC-001)**:
- ✅ Only "Approved" registrations visible
- ✅ No "Pending" or "Rejected" registrations shown
- ✅ Cards display: name, URL, description (truncated), owner, date
- ✅ Status badge shows "Approved" in green

**Browser Console Check**:
```javascript
// Verify API call
// Network tab should show: GET /registrations?status=Approved
```

---

### Test 2: Browse Page - Admin User

**Objective**: Verify admin users see all registrations

**Steps**:
1. Login as admin user (member of admin group)
2. Navigate to Browse page (root path `/`)
3. Observe all statuses visible

**Success Criteria (SC-001)**:
- ✅ "Approved", "Pending", and "Rejected" registrations all visible
- ✅ Status badges color-coded: green/yellow/red
- ✅ All metadata displayed in cards

**Browser Console Check**:
```javascript
// Network tab should show: GET /registrations (no status filter)
```

---

### Test 3: Search/Filter

**Objective**: Verify client-side search works

**Steps**:
1. On Browse page, type in search box: "Weather"
2. Observe results update instantly
3. Clear search (click X button)
4. Search again: "example.com"

**Success Criteria (SC-009)**:
- ✅ Results filter in <500ms (instant)
- ✅ Matches endpoint_name, description, owner_contact
- ✅ Page resets to 1 on new search
- ✅ Clear button removes search query

**Browser Console**:
```javascript
// No API calls during search (client-side filtering)
```

---

### Test 4: Pagination

**Objective**: Verify 20 items per page with page controls

**Steps**:
1. Insert 50+ registrations into database
2. Refresh Browse page
3. Observe only 20 cards displayed
4. Click "Next" button
5. Click page number "3"
6. Click "Previous" button

**Success Criteria (SC-002, SC-004)**:
- ✅ Exactly 20 registrations per page
- ✅ Pagination controls visible if >20 results
- ✅ Current page highlighted in red
- ✅ Previous/Next buttons disabled at boundaries
- ✅ Ellipsis shown for large page counts
- ✅ Page load <2 seconds

---

### Test 5: Card Click - Modal Detail View

**Objective**: Verify modal opens with full registration details

**Steps**:
1. On Browse page, click any registration card
2. Observe modal overlay appears
3. Scroll modal content
4. Click backdrop to close
5. Click card again, then click "X" button to close

**Success Criteria (SC-006)**:
- ✅ Modal opens in <1 second
- ✅ All fields visible: name, URL, description (full), owner, tools, dates
- ✅ Status badge displayed
- ✅ Close on backdrop click
- ✅ Close on X button click
- ✅ Close on ESC key (if implemented)
- ✅ Modal scrollable on small screens

---

### Test 6: Mobile Responsiveness

**Objective**: Verify UI adapts to mobile screens

**Steps**:
1. Open Chrome DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Select "iPhone SE" (375px width)
4. Refresh Browse page
5. Test search, pagination, modal

**Success Criteria (SC-010)**:
- ✅ Cards stack vertically (1 column)
- ✅ Search input full width
- ✅ Modal fullscreen on mobile
- ✅ All buttons >44px touch targets
- ✅ Text readable without zoom
- ✅ No horizontal scroll

**Test Tablets**:
- iPad (768px): 2-column grid
- Desktop (1024px+): 3-column grid

---

### Test 7: Query by URL API

**Objective**: Verify GET /registrations/by-url endpoint

**Steps**:
1. Get access token from browser (DevTools → Application → Session Storage → msal.token)
2. Test exact URL match:
   ```powershell
   $token = "your-token-here"
   curl -H "Authorization: Bearer $token" `
     "http://localhost:8000/registrations/by-url?endpoint_url=http://weather.example.com"
   ```
3. Test non-existent URL:
   ```powershell
   curl -H "Authorization: Bearer $token" `
     "http://localhost:8000/registrations/by-url?endpoint_url=http://fake.example.com"
   ```

**Success Criteria (SC-005)**:
- ✅ Returns 200 with RegistrationResponse for existing URL
- ✅ Returns 404 for non-existent URL
- ✅ Response time <200ms
- ✅ URL encoding handled correctly (spaces, special chars)
- ✅ Works for both admin and non-admin users

**Expected Response** (200):
```json
{
  "registration_id": "uuid-here",
  "endpoint_name": "Weather MCP",
  "endpoint_url": "http://weather.example.com",
  "description": "Weather forecast data",
  "owner_contact": "weather@example.com",
  "available_tools": [],
  "status": "Approved",
  "created_at": "2025-01-12T10:00:00Z",
  "submitter_email": "user@example.com"
}
```

**Expected Response** (404):
```json
{
  "detail": "No registration found for the given endpoint URL."
}
```

---

### Test 8: Audit Logging - Create Action

**Objective**: Verify new registrations are audit logged

**Steps**:
1. Navigate to Register page
2. Submit a new registration (POST /registrations)
3. Check database for audit log entry:
   ```sql
   SELECT * FROM audit_log 
   WHERE action = 'create' 
   ORDER BY created_at DESC LIMIT 1;
   ```

**Success Criteria (SC-007)**:
- ✅ Audit log entry created with:
  - registration_id: UUID of new registration
  - user_id: Submitter's user ID
  - action: 'create'
  - previous_status: NULL
  - new_status: 'Pending'
  - metadata: `{"endpoint_name": "...", "endpoint_url": "..."}`
  - created_at: Timestamp of submission

**Database Verification**:
```sql
-- Expected row
{
  "audit_log_id": "uuid",
  "registration_id": "uuid",
  "user_id": "user-uuid",
  "action": "create",
  "previous_status": null,
  "new_status": "Pending",
  "metadata": {"endpoint_name": "My MCP", "endpoint_url": "http://..."},
  "created_at": "2025-01-12T10:15:00Z"
}
```

---

### Test 9: Audit Logging - Approve Action

**Objective**: Verify approvals are audit logged

**Steps**:
1. Login as admin
2. Navigate to Admin Approvals page
3. Approve a pending registration (PATCH /registrations/{id})
4. Check database for audit log entry:
   ```sql
   SELECT * FROM audit_log 
   WHERE action = 'approve' 
   ORDER BY created_at DESC LIMIT 1;
   ```

**Success Criteria (SC-007)**:
- ✅ Audit log entry created with:
  - registration_id: UUID of approved registration
  - user_id: Admin's user ID
  - action: 'approve'
  - previous_status: 'Pending'
  - new_status: 'Approved'
  - metadata: NULL (or minimal)
  - created_at: Timestamp of approval

---

### Test 10: Audit Logging - Reject Action

**Objective**: Verify rejections are audit logged

**Steps**:
1. Login as admin
2. Reject a pending registration
3. Check database for audit log entry (action = 'reject')

**Success Criteria (SC-007)**:
- ✅ Audit log entry with new_status: 'Rejected'

---

### Test 11: Audit Logs API - Admin Query

**Objective**: Verify GET /audit-logs endpoint (admin only)

**Steps**:
1. Login as admin user, get access token
2. Query all audit logs:
   ```powershell
   $token = "admin-token"
   curl -H "Authorization: Bearer $token" `
     "http://localhost:8000/audit-logs?limit=10&offset=0"
   ```
3. Filter by registration_id:
   ```powershell
   curl -H "Authorization: Bearer $token" `
     "http://localhost:8000/audit-logs?registration_id=uuid-here&limit=50"
   ```
4. Filter by action:
   ```powershell
   curl -H "Authorization: Bearer $token" `
     "http://localhost:8000/audit-logs?action=approve&limit=100"
   ```
5. Date range filter:
   ```powershell
   curl -H "Authorization: Bearer $token" `
     "http://localhost:8000/audit-logs?from=2025-01-01&to=2025-01-31&limit=100"
   ```

**Success Criteria (SC-008)**:
- ✅ Returns 200 with AuditLogListResponse
- ✅ Response includes: results (array), total, limit, offset
- ✅ Filters work correctly (registration_id, user_id, action, date range)
- ✅ Pagination works (limit/offset)
- ✅ Response time <1 second
- ✅ Results ordered by created_at DESC

**Expected Response**:
```json
{
  "results": [
    {
      "audit_log_id": "uuid",
      "registration_id": "uuid",
      "user_id": "uuid",
      "action": "approve",
      "previous_status": "Pending",
      "new_status": "Approved",
      "metadata": null,
      "created_at": "2025-01-12T14:30:00Z"
    }
  ],
  "total": 42,
  "limit": 10,
  "offset": 0
}
```

---

### Test 12: Audit Logs API - Non-Admin Forbidden

**Objective**: Verify non-admin users cannot access audit logs

**Steps**:
1. Login as non-admin user
2. Attempt to call GET /audit-logs with non-admin token
   ```powershell
   curl -H "Authorization: Bearer $non_admin_token" `
     "http://localhost:8000/audit-logs"
   ```

**Success Criteria (SC-008)**:
- ✅ Returns 403 Forbidden
- ✅ Error message: "Admin privileges required"

---

### Test 13: Performance - Initial Load

**Objective**: Verify Browse page loads in <2 seconds

**Steps**:
1. Open Chrome DevTools → Network tab
2. Clear cache (Ctrl+Shift+Delete)
3. Navigate to Browse page
4. Observe timing in Network tab

**Success Criteria (SC-002)**:
- ✅ DOMContentLoaded <2 seconds
- ✅ All API calls complete <2 seconds
- ✅ Cards render immediately after data load

**Performance Budget**:
- HTML: <100ms
- JS bundles: <500ms
- API call: <200ms
- Total: <2000ms

---

### Test 14: Error Handling

**Objective**: Verify graceful error handling

**Steps**:
1. Stop backend API server
2. Refresh Browse page
3. Observe error message
4. Restart backend
5. Click retry (if implemented) or refresh

**Success Criteria (SC-003)**:
- ✅ Error message displayed: "Failed to load registrations"
- ✅ Toast notification shown (react-hot-toast)
- ✅ No app crash
- ✅ Recovers on backend restart

---

## Troubleshooting

### Issue: Browse Page Shows Empty State

**Possible Causes**:
1. No approved registrations in database (non-admin user)
2. Backend not running
3. API base URL misconfigured

**Solution**:
```sql
-- Check registrations in database
SELECT status, COUNT(*) FROM registrations GROUP BY status;

-- If all pending, approve one:
UPDATE registrations SET status = 'Approved' WHERE registration_id = 'uuid-here';
```

### Issue: 401 Unauthorized on API Calls

**Possible Causes**:
1. Token expired
2. Entra ID configuration mismatch

**Solution**:
1. Clear browser storage (DevTools → Application → Clear storage)
2. Re-login
3. Verify VITE_ENTRA_CLIENT_ID matches backend ENTRA_CLIENT_ID

### Issue: Modal Doesn't Open

**Possible Cause**: JavaScript error

**Solution**:
1. Check browser console for errors
2. Verify RegistrationDetailModal component imported correctly
3. Check selectedId state updates on card click

### Issue: Pagination Missing

**Possible Cause**: <20 registrations in database

**Solution**:
```sql
-- Insert 25 test registrations
INSERT INTO registrations (registration_id, endpoint_name, endpoint_url, description, owner_contact, available_tools, status, submitter_user_id)
SELECT 
  gen_random_uuid(),
  'Test MCP ' || i,
  'http://test' || i || '.example.com',
  'Test description ' || i,
  'test' || i || '@example.com',
  '[]',
  'Approved',
  'user1'
FROM generate_series(1, 25) AS i;
```

### Issue: Audit Logs Empty

**Possible Cause**: No transactions logged yet

**Solution**:
1. Create a registration
2. Approve/reject a registration
3. Query audit_log table directly:
   ```sql
   SELECT * FROM audit_log ORDER BY created_at DESC LIMIT 10;
   ```

---

## Success Metrics

After completing all tests, verify these metrics:

**Feature Completion**:
- ✅ Browse page displays registrations (FR-001, FR-002, FR-003)
- ✅ Search/filter works (FR-006)
- ✅ Pagination works (FR-005)
- ✅ Modal detail view works (FR-004, FR-007, FR-008)
- ✅ Query by URL API works (FR-012, FR-013, FR-014)
- ✅ Audit logging works (FR-015, FR-016, FR-017)
- ✅ Audit logs API works (FR-020, FR-021, FR-022)
- ✅ Mobile responsive (FR-009, FR-010)

**Performance**:
- ✅ Initial load <2s (SC-002)
- ✅ Search <500ms (SC-009)
- ✅ Query by URL <200ms (SC-005)
- ✅ Audit logs query <1s (SC-008)

**Security**:
- ✅ Non-admin users see only approved (SC-001)
- ✅ Audit logs restricted to admin (SC-008)
- ✅ All actions logged (SC-007)

---

## Next Steps

After manual verification passes:

1. **Code Review**: Submit PR for 003-browse-audit-query branch
2. **QA Testing**: Hand off to QA team for comprehensive testing
3. **Deploy to Staging**: Merge to staging branch
4. **Production Deployment**: After staging validation

**Note**: Automated testing is out of scope per Project Constitution V.

---

## Additional Resources

- **API Documentation**: `/specs/003-browse-audit-query/contracts/api-endpoints.md`
- **UI Components**: `/specs/003-browse-audit-query/contracts/browse-page-ui.md`
- **Data Model**: `/specs/003-browse-audit-query/data-model.md`
- **Database Schema**: `/backend/scripts/db/init_schema.sql`
- **Feature Spec**: `/specs/003-browse-audit-query/spec.md`
