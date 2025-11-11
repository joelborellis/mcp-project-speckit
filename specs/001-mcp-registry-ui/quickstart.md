# MCP Registry - Quickstart Guide

**Feature**: MCP Registry Web Application  
**Branch**: `001-mcp-registry-ui`  
**Last Updated**: 2025-11-11

---

## Prerequisites

Before starting development, ensure you have:

1. **Node.js** >= 20.x (recommended: 22.x)
2. **npm** >= 10.x (comes with Node.js)
3. **Git** (for version control)
4. **Microsoft Entra ID Tenant Access**
   - Permissions to create App Registrations
   - Access to create/manage Entra ID groups
   - Admin consent permissions for API scopes

---

## Initial Setup

### 1. Clone Repository

```bash
cd C:\Projects\2025\mcp-project-speckit
git checkout 001-mcp-registry-ui
```

### 2. Install Dependencies

```bash
cd frontend
npm install
```

**Installed Packages**:
- `react` ^19.2.0
- `react-dom` ^19.2.0
- `vite` ^7.2.2
- `typescript` ~5.9.3
- `tailwindcss` ^4.x
- `@azure/msal-browser` ^3.x
- `@azure/msal-react` ^2.x
- `dexie` ^4.x
- `react-router-dom` ^6.x
- `react-hot-toast` ^2.x

### 3. Configure Microsoft Entra ID

#### A. Create App Registration

1. Navigate to [Azure Portal](https://portal.azure.com)
2. Go to **Microsoft Entra ID** → **App registrations**
3. Click **New registration**
4. Configure:
   - **Name**: `MCP Registry Local Dev` (or your preferred name)
   - **Supported account types**: `Accounts in this organizational directory only (Single tenant)`
   - **Redirect URI**: 
     - Platform: `Single-page application (SPA)`
     - URI: `http://localhost:5173`
   - Click **Register**

5. **Copy Application Details** (you'll need these for `.env.local`):
   - **Application (client) ID**: e.g., `a1b2c3d4-e5f6-7890-abcd-ef1234567890`
   - **Directory (tenant) ID**: e.g., `12345678-1234-1234-1234-123456789012`

#### B. Configure Authentication

1. In your app registration, go to **Authentication**
2. Under **Single-page application**, ensure redirect URI is `http://localhost:5173`
3. Under **Implicit grant and hybrid flows**, check:
   - ✅ **Access tokens** (used for implicit flows)
   - ✅ **ID tokens** (used for implicit and hybrid flows)
4. Under **Advanced settings**:
   - Allow public client flows: **No**
5. Click **Save**

#### C. Configure API Permissions

1. Go to **API permissions**
2. Click **Add a permission**
3. Select **Microsoft Graph**
4. Select **Delegated permissions**
5. Add:
   - ✅ `User.Read` (Read user profile)
   - ✅ `GroupMember.Read.All` (Read group memberships - for admin role)
6. Click **Add permissions**
7. Click **Grant admin consent for [Your Tenant]** (requires admin)
8. Verify status shows green checkmarks

#### D. Create Admin Group

1. Go to **Microsoft Entra ID** → **Groups**
2. Click **New group**
3. Configure:
   - **Group type**: `Security`
   - **Group name**: `MCP Registry Admins`
   - **Group description**: `Users with admin privileges for MCP Registry`
   - **Members**: Add yourself and other admins
4. Click **Create**
5. **Copy Group Object ID**: e.g., `87654321-4321-4321-4321-210987654321`

### 4. Configure Environment Variables

Create `frontend/.env.local` file:

```bash
# Microsoft Entra ID Configuration
VITE_ENTRA_CLIENT_ID=a1b2c3d4-e5f6-7890-abcd-ef1234567890
VITE_ENTRA_TENANT_ID=12345678-1234-1234-1234-123456789012
VITE_ENTRA_REDIRECT_URI=http://localhost:5173
VITE_ENTRA_ADMIN_GROUP_ID=87654321-4321-4321-4321-210987654321

# Application Configuration
VITE_APP_NAME=MCP Registry
```

**Replace** the placeholder values with your actual IDs from steps above.

**Environment Variables Explained**:
- `VITE_ENTRA_CLIENT_ID`: Application (client) ID from App Registration
- `VITE_ENTRA_TENANT_ID`: Directory (tenant) ID from App Registration
- `VITE_ENTRA_REDIRECT_URI`: Must match redirect URI in Entra ID (use `http://localhost:5173` for local dev)
- `VITE_ENTRA_ADMIN_GROUP_ID`: Object ID of the admin security group
- `VITE_APP_NAME`: Application display name

### 5. Start Development Server

```bash
npm run dev
```

**Expected Output**:
```
VITE v7.2.2  ready in 1200 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
➜  press h + enter to show help
```

Open browser to: [http://localhost:5173](http://localhost:5173)

---

## Manual Verification Checklist

**Note**: Per project constitution, we do NOT use automated tests. All functionality must be verified manually.

### ✅ Authentication Flow Verification

#### Test 1: Initial Login

1. **Action**: Open `http://localhost:5173`
2. **Expected**:
   - See login page with "Sign in with Microsoft" button
   - No console errors in browser DevTools (F12)
3. **Action**: Click "Sign in with Microsoft"
4. **Expected**:
   - Redirect to Microsoft login page (`login.microsoftonline.com`)
   - URL contains your tenant ID
5. **Action**: Enter credentials and click "Sign in"
6. **Expected**:
   - Redirect back to `http://localhost:5173`
   - See main application (registry browse view)
   - User name appears in header (top-right)
7. **Verification**:
   - ✅ Login redirect works
   - ✅ Token acquired successfully
   - ✅ User profile displayed

---

#### Test 2: Admin Role Detection

1. **Prerequisites**: Ensure you are a member of "MCP Registry Admins" group
2. **Action**: Login as admin user
3. **Expected**:
   - See "Admin" badge next to username in header
   - Navigation includes "Pending Approvals" link
4. **Action**: Open browser DevTools → Application → IndexedDB
5. **Verification**:
   - Check user object in memory
   - Verify `isAdmin: true`
   - Verify `groups` array contains admin group ID

**Non-Admin Test**:
1. **Action**: Login as user NOT in admin group
2. **Expected**:
   - No "Admin" badge in header
   - No "Pending Approvals" link
   - `isAdmin: false` in user object

---

#### Test 3: Token Refresh

1. **Action**: Login and use app normally
2. **Action**: Wait for access token to near expiration (~50 minutes)
3. **Expected**:
   - MSAL automatically refreshes token in background
   - No visible interruption to user
   - No forced re-login
4. **Verification** (DevTools Console):
   - Look for MSAL token acquisition logs
   - Verify `acquireTokenSilent` is called, not `acquireTokenPopup`

---

#### Test 4: Logout Flow

1. **Action**: Click "Sign out" button in header
2. **Expected**:
   - User redirected to login page
   - No user name in header
   - Browser storage cleared (check DevTools → Application → Local Storage)
3. **Action**: Click browser back button
4. **Expected**:
   - Redirected back to login page (not authenticated state)
   - No access to protected routes

---

### ✅ Data Persistence Verification

#### Test 5: IndexedDB Initialization

1. **Action**: Open app for first time (clear browser data first)
2. **Action**: Open DevTools → Application → IndexedDB
3. **Expected**:
   - Database named `MCPRegistryDB` is created
   - Object store `endpoints` exists
   - Indexes exist:
     - `id` (primary key)
     - `status`
     - `submitterId`
     - `url`
     - `[status+submitterId]`
     - `*tools`
4. **Verification**:
   - ✅ Database auto-created on first use
   - ✅ Schema matches contract (see `contracts/indexeddb-schema.md`)

---

#### Test 6: Data Persistence Across Sessions

1. **Action**: Register a new endpoint
2. **Expected**: Endpoint saved to IndexedDB
3. **Action**: Close browser completely
4. **Action**: Reopen browser and navigate to `http://localhost:5173`
5. **Expected**:
   - Previously registered endpoint still appears
   - Data persisted across browser sessions
6. **Verification**:
   - ✅ IndexedDB data survives browser restart
   - ✅ No data loss on page refresh

---

### ✅ Registration Flow Verification

#### Test 7: Submit Valid Registration

1. **Prerequisites**: Logged in as any user
2. **Action**: Click "Register New Endpoint" button
3. **Expected**: Registration form appears
4. **Action**: Fill form with valid data:
   - **Name**: `Test Endpoint`
   - **URL**: `https://example.com/mcp`
   - **Description**: `This is a test endpoint for manual verification`
   - **Owner**: `Test Organization`
   - **Tools**: `search, analyze, summarize`
5. **Action**: Click "Submit"
6. **Expected**:
   - Success toast notification appears
   - Redirect to "My Registrations" page
   - New endpoint appears in list with "Pending" status
7. **Verification** (IndexedDB):
   - Open DevTools → IndexedDB → MCPRegistryDB → endpoints
   - Find new record
   - Verify:
     - ✅ `status: "Pending"`
     - ✅ `submitterId` matches current user ID
     - ✅ `tools: ["search", "analyze", "summarize"]` (array, not string)
     - ✅ `submissionTimestamp` is recent Unix timestamp
     - ✅ `reviewerId: null`, `reviewerName: null`, `reviewTimestamp: null`

---

#### Test 8: Form Validation - Required Fields

1. **Action**: Click "Register New Endpoint"
2. **Action**: Leave all fields empty
3. **Action**: Click "Submit"
4. **Expected**: Error messages appear:
   - "Endpoint name is required"
   - "URL is required"
   - "Owner is required"
   - "At least one tool is required"
5. **Verification**:
   - ✅ Form prevents submission with empty fields
   - ✅ Error messages display correctly

---

#### Test 9: Form Validation - URL Format

1. **Action**: Enter invalid URL: `not-a-url`
2. **Expected**: Error message: "Invalid URL format. Must be a valid HTTP/HTTPS URL"
3. **Action**: Enter URL with wrong protocol: `ftp://example.com`
4. **Expected**: Same error message
5. **Action**: Enter valid URL: `https://example.com`
6. **Expected**: No error message
7. **Verification**:
   - ✅ URL validation works correctly
   - ✅ Only HTTP/HTTPS accepted

---

#### Test 10: Form Validation - URL Uniqueness

1. **Action**: Register endpoint with URL `https://unique-test.com`
2. **Expected**: Registration succeeds
3. **Action**: Attempt to register another endpoint with SAME URL
4. **Expected**: Error message: "This URL is already registered"
5. **Verification**:
   - ✅ Duplicate URL prevention works
   - ✅ Uniqueness check performed before submission

---

#### Test 11: Form Validation - Field Lengths

1. **Action**: Enter name with 101 characters
2. **Expected**: Error: "Endpoint name must be 100 characters or less"
3. **Action**: Enter description with 501 characters
4. **Expected**: Error: "Description must be 500 characters or less"
5. **Action**: Reduce to valid lengths
6. **Expected**: No error messages
7. **Verification**:
   - ✅ Length validation enforced
   - ✅ Limits match specification (see `contracts/validation-schema.md`)

---

#### Test 12: Tools Input Parsing

1. **Action**: Enter tools as: `tool1, tool2,tool3 , , tool4`
2. **Expected** (after submission, check IndexedDB):
   - `tools: ["tool1", "tool2", "tool3", "tool4"]`
   - Empty entries removed
   - Whitespace trimmed
3. **Verification**:
   - ✅ Comma-separated input parsed correctly
   - ✅ Empty/whitespace-only entries filtered out

---

### ✅ Browse Flow Verification

#### Test 13: View Approved Endpoints

1. **Prerequisites**: At least one endpoint has been approved
2. **Action**: Navigate to main registry page (browse view)
3. **Expected**:
   - List displays only approved endpoints
   - No pending or rejected endpoints visible
   - Each card shows:
     - Endpoint name
     - URL (clickable link)
     - Description
     - Owner
     - Tools (as badges)
4. **Verification**:
   - ✅ Approved endpoints visible to all users
   - ✅ Status filter working (only "Approved" shown)

---

#### Test 14: Search Functionality

1. **Prerequisites**: Multiple approved endpoints exist
2. **Action**: Type in search box: `test`
3. **Expected**:
   - Results filter in real-time (debounced 300ms)
   - Matches found in:
     - Endpoint name
     - Owner
     - Tools
4. **Action**: Type: `search` (a tool name)
5. **Expected**: Only endpoints with "search" tool appear
6. **Action**: Clear search
7. **Expected**: All approved endpoints reappear
8. **Verification**:
   - ✅ Search filters by name, owner, and tools
   - ✅ Case-insensitive matching
   - ✅ Debounced input (not laggy)

---

#### Test 15: Performance with Many Endpoints

1. **Prerequisites**: Create 100+ test endpoints (use admin approve to get them in registry)
2. **Action**: Load main registry page
3. **Expected**:
   - Page loads within 500ms
   - Search responds within 500ms
   - No noticeable lag
4. **Verification** (DevTools Performance tab):
   - ✅ Initial load < 500ms
   - ✅ Search filter < 500ms
   - ✅ No memory leaks (check with repeated searches)

---

### ✅ Admin Approval Verification

#### Test 16: Admin Can See Pending Approvals

1. **Prerequisites**: Logged in as admin
2. **Action**: Click "Pending Approvals" in navigation
3. **Expected**:
   - List shows all endpoints with "Pending" status
   - Each entry shows:
     - Submitter name
     - Submission timestamp
     - Approve button (green)
     - Reject button (red)
4. **Verification**:
   - ✅ Admin-only page accessible
   - ✅ All pending submissions visible

---

#### Test 17: Admin Cannot Review Own Submission

1. **Prerequisites**: Admin user submits an endpoint
2. **Action**: Navigate to "Pending Approvals"
3. **Expected**:
   - Own submission appears in list
   - Approve/Reject buttons are DISABLED or HIDDEN
   - Tooltip or message: "Cannot review your own submission"
4. **Verification**:
   - ✅ Self-review prevention works
   - ✅ Clear UI indication

---

#### Test 18: Approve Endpoint

1. **Prerequisites**: Admin logged in, pending submission exists (not by admin)
2. **Action**: Click "Approve" button
3. **Expected**:
   - Confirmation dialog appears: "Approve this endpoint?"
   - Click "Confirm"
   - Success toast: "Endpoint approved successfully"
   - Endpoint removed from pending list
4. **Verification** (IndexedDB):
   - Check endpoint record
   - Verify:
     - ✅ `status: "Approved"`
     - ✅ `reviewerId: <admin-user-id>`
     - ✅ `reviewerName: <admin-display-name>`
     - ✅ `reviewTimestamp: <recent-unix-timestamp>`
5. **Verification** (Browse Page):
   - Navigate to main registry
   - Verify approved endpoint now appears in list

---

#### Test 19: Reject Endpoint

1. **Prerequisites**: Admin logged in, pending submission exists
2. **Action**: Click "Reject" button
3. **Expected**:
   - Confirmation dialog: "Reject this endpoint?"
   - Click "Confirm"
   - Success toast: "Endpoint rejected"
   - Endpoint removed from pending list
4. **Verification** (IndexedDB):
   - Check endpoint record
   - Verify:
     - ✅ `status: "Rejected"`
     - ✅ `reviewerId: <admin-user-id>`
     - ✅ `reviewerName: <admin-display-name>`
     - ✅ `reviewTimestamp: <recent-unix-timestamp>`
5. **Verification** (Browse Page):
   - Navigate to main registry
   - Verify rejected endpoint does NOT appear

---

#### Test 20: Rejected Endpoints Stored (Audit Trail)

1. **Prerequisites**: At least one rejected endpoint exists
2. **Action**: Open DevTools → IndexedDB → endpoints
3. **Expected**:
   - Rejected endpoint record still exists
   - Not deleted from database
4. **Action**: Navigate to "My Registrations" as original submitter
5. **Expected**:
   - Rejected endpoint appears with "Rejected" badge
   - No edit/delete options
6. **Verification**:
   - ✅ Rejected endpoints preserved for audit
   - ✅ Status visible to submitter

---

#### Test 21: Non-Admin Cannot Access Approval Page

1. **Prerequisites**: Logged in as non-admin user
2. **Action**: Manually navigate to `/admin/approvals` (or wherever approval route is)
3. **Expected**:
   - Redirect to home page OR "Access Denied" message
   - No pending approvals visible
4. **Verification**:
   - ✅ Protected route works
   - ✅ Non-admins cannot bypass via URL

---

### ✅ Responsive Design Verification

#### Test 22: Mobile View (375px)

1. **Action**: Open DevTools → Responsive Design Mode
2. **Action**: Set viewport to 375x667 (iPhone SE)
3. **Expected**:
   - Layout adjusts to single column
   - Navigation collapses to hamburger menu
   - Cards stack vertically
   - Text remains readable (no horizontal scroll)
4. **Verification**:
   - ✅ Mobile-first Tailwind classes work
   - ✅ No layout breakage

---

#### Test 23: Tablet View (768px)

1. **Action**: Set viewport to 768x1024 (iPad)
2. **Expected**:
   - Layout shows 2 columns
   - Navigation remains horizontal
   - Cards have more spacing
3. **Verification**:
   - ✅ Tablet breakpoint responsive

---

#### Test 24: Desktop View (1920px)

1. **Action**: Set viewport to 1920x1080 (Desktop)
2. **Expected**:
   - Layout shows 3+ columns
   - Maximum content width maintained (no ultra-wide stretching)
   - Proper whitespace/margins
3. **Verification**:
   - ✅ Desktop layout optimal
   - ✅ Content doesn't stretch too wide

---

### ✅ Error Handling Verification

#### Test 25: Network Error Simulation

1. **Action**: Open DevTools → Network tab
2. **Action**: Enable "Offline" mode
3. **Action**: Attempt to login
4. **Expected**:
   - Error toast: "Network error. Please check your connection."
   - Login button re-enabled
5. **Action**: Disable offline mode and retry
6. **Expected**: Login succeeds
7. **Verification**:
   - ✅ Network errors handled gracefully
   - ✅ User-friendly error messages

---

#### Test 26: Entra ID Misconfiguration

**Scenario A: Invalid Client ID**
1. **Action**: Set `VITE_ENTRA_CLIENT_ID` to invalid GUID in `.env.local`
2. **Action**: Restart dev server
3. **Action**: Attempt login
4. **Expected**: 
   - Error message: "Authentication configuration error"
   - Link to troubleshooting guide

**Scenario B: Invalid Redirect URI**
1. **Action**: Change redirect URI in `.env.local` to `http://localhost:9999`
2. **Action**: Restart dev server
3. **Action**: Attempt login
4. **Expected**:
   - Microsoft error page: "Redirect URI mismatch"
   - Clear error message

5. **Verification**:
   - ✅ Configuration errors detected
   - ✅ Helpful error messages displayed

---

## Troubleshooting Guide

### Issue: "Failed to acquire token"

**Possible Causes**:
1. Invalid client ID or tenant ID
2. Redirect URI mismatch
3. Admin consent not granted

**Solutions**:
1. Verify `.env.local` values match Azure Portal
2. Check redirect URI in App Registration matches `http://localhost:5173`
3. Grant admin consent in API permissions tab

---

### Issue: "User is not admin" (but should be)

**Possible Causes**:
1. User not added to admin group
2. Wrong group ID in `.env.local`
3. Token not refreshed after group membership change

**Solutions**:
1. Verify user is member of "MCP Registry Admins" in Entra ID
2. Copy correct group Object ID to `VITE_ENTRA_ADMIN_GROUP_ID`
3. Logout and login again to refresh token

---

### Issue: IndexedDB not accessible

**Possible Causes**:
1. Private/Incognito mode (some browsers block IndexedDB)
2. Browser storage quota exceeded
3. IndexedDB disabled in browser settings

**Solutions**:
1. Use normal browsing mode (not incognito)
2. Clear browser data to free storage
3. Check browser settings → Privacy → Site data

---

### Issue: "Invalid URL format" on valid URL

**Possible Causes**:
1. URL missing protocol (http:// or https://)
2. Localhost URLs (rejected in production mode)

**Solutions**:
1. Include `https://` prefix explicitly
2. Use publicly accessible URLs (not localhost)
3. For local dev testing, temporarily modify `isValidURL()` in validation-schema.md

---

### Issue: Performance lag with many endpoints

**Possible Causes**:
1. Too many endpoints (>1000)
2. Inefficient search filter
3. Re-rendering issues

**Solutions**:
1. Verify endpoint count in IndexedDB
2. Check search debounce is working (300ms)
3. Use React DevTools Profiler to identify slow components

---

## Development Workflow

### 1. Making Changes

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes to code

# 3. Verify changes with manual tests (see checklist above)

# 4. Commit changes
git add .
git commit -m "feat: add new feature"

# 5. Push to remote
git push origin feature/my-feature
```

### 2. Code Organization

```
frontend/
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── auth/          # Login, logout, auth-related
│   │   ├── registry/      # Endpoint cards, lists
│   │   └── forms/         # Registration form
│   ├── pages/             # Page-level components
│   │   ├── BrowsePage.tsx
│   │   ├── RegisterPage.tsx
│   │   ├── MyRegistrationsPage.tsx
│   │   └── AdminApprovalsPage.tsx
│   ├── services/          # Business logic, API calls
│   │   ├── auth.service.ts      # MSAL configuration
│   │   ├── db.service.ts        # IndexedDB operations
│   │   └── validation.service.ts # Validation functions
│   ├── types/             # TypeScript interfaces
│   │   ├── user.types.ts
│   │   ├── endpoint.types.ts
│   │   └── validation.types.ts
│   ├── context/           # React Context providers
│   │   └── AuthContext.tsx
│   ├── hooks/             # Custom React hooks
│   │   └── useAuth.ts
│   ├── App.tsx            # Main app component
│   └── main.tsx           # Entry point
```

### 3. Running Build

```bash
# Production build
npm run build

# Preview production build
npm run preview
```

---

## Next Steps

After completing manual verification:

1. ✅ All authentication tests passing → Proceed to implement main features
2. ✅ All registration tests passing → Add admin approval workflow
3. ✅ All admin tests passing → Add advanced search features
4. ✅ All responsive tests passing → Optimize performance

**Note**: See `tasks.md` (generated by `/speckit.tasks`) for detailed implementation steps.

---

## Manual Verification Sign-Off

**Tester Name**: _______________________  
**Date**: _______________________  
**Environment**: Local Dev / Staging / Production

### Sign-Off Checklist

- [ ] All authentication tests (1-4) passed
- [ ] All data persistence tests (5-6) passed
- [ ] All registration tests (7-12) passed
- [ ] All browse tests (13-15) passed
- [ ] All admin tests (16-21) passed
- [ ] All responsive tests (22-24) passed
- [ ] All error handling tests (25-26) passed

**Signature**: _______________________

---

**This document satisfies the manual verification requirement per project constitution (Principle V: No Testing). All functionality must be validated by hand using these procedures before considering a feature complete.**
