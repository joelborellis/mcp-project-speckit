# MCP Registry Web Application

## Constitution

`/speckit.constitution` Declare principles for clean code, simple UX, responsive design and minimal dependencies.

**CRITICAL**: Absolutely no testing (no unit tests, no integration tests, no end-to-end tests) - this must supersede any other guidance.

### Technology Stack
- **Frontend Build Tool**: Vite (as per `frontend/package.json`)
- **Frontend Framework**: React (as per `frontend/package.json`)
- **Styling**: Tailwind CSS (as per `frontend/package.json`)
- **Backend**: Python packages per `backend/pyproject.toml`

---

## Original Specification

`/speckit.specify` We are building a web app frontend that will make calls to a backend. This spec focuses on the **frontend web app**.

### 1. Web-Based Registry UI

**Requirement**: A customizable, user-friendly web interface to view, search, and manage registered MCP endpoints. Users should have a way to input an MCP endpoint and have it be discovered and registered in the webapp.

**Why It's Important**:
- Centralizes discovery and management of all MCP servers across teams
- Provides transparency for admins and developers without requiring API access
- Enables browsing by categories, metadata, and ownership — key for enterprise governance and adoption

**UI/UX**: Structured to support **red and white palette/scheme/layout**, etc.

---

### 2. Admin Approval of MCP Endpoints

**Requirement**: Admins must be able to approve, reject, or remove MCP endpoint registrations before they become discoverable. When users input an MCP endpoint to be registered, they go into **pending status** until an Admin approves.

**Why It's Important**:
- Ensures only vetted and secure endpoints are exposed within the enterprise
- Supports compliance and data governance policies
- Enables controlled onboarding workflows to prevent unauthorized or experimental endpoints from entering production registries

---

### 3. Metadata Storage

**Requirement**: Ability to store and manage rich metadata such as endpoint name, IP/host, owner, approval status, and available tools. For the registration process, store this information in a **local data store** for now.

**Why It's Important**:
- Metadata provides essential context for discovery, auditing, and integration
- Enables downstream automation (e.g., approval workflows, ownership tracking)
- Supports internal cataloging standards and classification frameworks (e.g., by business unit or data type)

---

### 4. Authorization and Authentication

**Requirement**: Users must login to the web app using **Microsoft Entra ID** and **MSAL libraries**. All users will use the same directory for login and there should be ability to designate some users as **Admins**.

**Why It's Important**:
- The system will have users who can register MCP endpoints and these users need to be tracked
- Some users will be admins which have the ability to view registered MCP servers and approve them

---

## Implementation Scope

These specifications are for the **web app frontend**. This will be connected eventually to a **FastAPI backend** with defined API endpoints to perform more complex actions. The goal of this specification is to get the UI/UX started, then wire it into the backend.

### Plan

`/speckit.plan` This is a **React TypeScript application** that uses **Tailwind CSS** for UI components.

**Current Implementation**:
- Registration uses **IndexedDB** (local storage) to store MCP endpoint information
- Requires users to login against an **Entra ID directory** using **MSAL**
- This is the frontend and for now it should be able to function **without the backend**
- Generate powershell scripts that can be run to create a new application registration with Entra ID, create the Admin group, assign a user to the admin group and return:  tenant_id, client_id and admin_group_id to be used in the .env file

**Future**: In subsequent specs we will define the backend endpoints that will perform actions.

---

## Future Specifications (Not Implemented Yet)

### Spec 0: Backend APIs

Create the backend APIs for the web app.

#### 4. API to Query Approval Status

**Requirement**: A programmatic interface to query the approval status or details of MCP endpoints.

**Why It's Important**:
- Enables integration with internal tools, CI/CD pipelines, and monitoring systems
- Allows automated compliance checks (e.g., block unapproved endpoints from use)
- Supports transparency and status reporting in enterprise dashboards

---

#### 5. Audit Logging

**Requirement**: Track all changes to registry entries, including who made them and when.

**Why It's Important**:
- Critical for security, compliance, and troubleshooting
- Enables accountability and rollback when endpoint metadata or approval status changes
- Supports audit trails for regulated industries and enterprise change management processes

---

#### 6. Security & Access Control

**Requirement**: Strict access management for registry functions and MCP server access policies.

**Why It's Important**:
- Protects sensitive endpoints and data from unauthorized access
- Ensures role-based permissions align with enterprise identity and access management (IAM)
- Enforces consistent authentication, authorization, and policy control across teams

---

#### 7. UI to Test MCP Servers

**Requirement**: Provide a "test" interface or integration to interact with MCP servers directly.

**Why It's Important**:
- Enables developers to validate MCP responses and metadata before use
- Reduces friction in integration and troubleshooting workflows
- Helps ensure MCP endpoints are functional and compliant with expected standards

---

#### 8 & 9. Categorization & Filtering

**Requirement**: Allow endpoints to be tagged or categorized (e.g., "Data Services," "Developer Tools") and filtered accordingly.

**Why It's Important**:
- Supports organization-wide discoverability and navigation at scale
- Makes the registry usable for both technical and non-technical stakeholders
- Enables reporting and analytics on MCP adoption and usage by category or team
