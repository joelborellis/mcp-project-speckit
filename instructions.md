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

## Original Specification (Frontend)

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

These specifications are for the **web app frontend**. This will be connected eventually to a **FastAPI backend** with defined API endpoints to perform more complex actions. The goal of this specification is to get the UI/UX started, then wire it into the backend.

## Clarify

`/speckit.clarify` No Arguments

This command asks come clarifying questions about the Spec.  Run without arguments and answer the questions as posed to update the Specification.

## Plan

`/speckit.plan` This is a **React TypeScript application** that uses **Tailwind CSS** for UI components.

**Current Implementation**:
- Registration uses **IndexedDB** (local storage) to store MCP endpoint information
- Requires users to login against an **Entra ID directory** using **MSAL**
- This is the frontend and for now it should be able to function **without the backend**
- Generate powershell scripts that can be run to create a new application registration with Entra ID, create the Admin group, assign a user to the admin group and return:  tenant_id, client_id and admin_group_id to be used in the .env file

**Future**: In subsequent specs we will define the backend endpoints that will perform actions.

---

## Tasks

`/speckit.tasks` No Arguments

This command breaks down the specification into tasks

---

## Analyze

`/speckit.analyze` No Arguments

This command analyzes the specification aand the constitution to confirm consistencies

---

## Implement

`/speckit.implement` No Arguments

This command implements and creates the code for the frontend

---

## First Specification Update

`/speckit.specify`  We are building the backend for our application that serves routes/endpoints to create, update and fetch data related to the MCP Registry application.  This backend will use a PostgresSQL database running in Azure to store data.  This will replace the current IndexedDB the frontend is currently using.

#### 4.  Create Backend FastAPI 

**Requirement**:  Create backend FastAPI app that will support the current feaures of the frontend application.  Update the frontend application to use this new backend.

**Why It's Important**:
- The backend needs to replace the IndexedDB that currently runs the application
- The backend should implement as many routes/endpoints that are required to support the functionality of the frontend

#### 5.  Generate scripts to create database tables in PostgresSQL in Azure

**Requirement**:  Create scripts to be run to setup the tables and whatever database objects are needed to support the application.

**Why It's Important**:
- The systme might change databases and will need to rebuild the tables and objects in the database

## Clarify

`/speckit.clarify` No Arguments

This command asks come clarifying questions about the Spec.  Run without arguments and answer the questions as posed to update the Specification.

## Plan

`/speckit.plan` This is a **FastAPI Application**.

**Current Implementation**:
- Use CORS so that browser can access the routes/endpoints
- Use uv for package management
- Create .env file for the required environment variables to connect to the PostgresSQL database
- Generate scripts to create any database objects required by the application
- Make the Python code easy to read and any functions easy to understand what they do
- Ensure that the frontend is connecting to this backend

---

## Tasks

`/speckit.tasks` No Arguments

This command breaks down the specification into tasks

---

## Analyze

`/speckit.analyze` No Arguments

This command analyzes the specification aand the constitution to confirm consistencies

---

## Implement

`/speckit.implement` No Arguments

This command implements and creates the code for the backend

---

## Second Specification Update

`/speckit.specify` Add new functionality to the existing app keeping the same architecture of frontend and backend.

#### 6. Create the Browse Functioanlity

**Requirement**: Complete the Browse functionality.  

**Why It's Important**:
- Allows users regardless of whether they are Admin or not to see all the registeretd Servers and their status via the Browse page

---

#### 7. API to Query Approval Status

**Requirement**: A programmatic interface to query the approval status or details of MCP endpoints given the endpoint URL.

**Why It's Important**:
- Enables integration with internal tools, CI/CD pipelines, and monitoring systems
- Allows automated compliance checks (e.g., block unapproved endpoints from use)
- Supports transparency and status reporting in enterprise dashboards

---

#### 8. Audit Logging

**Requirement**: Track all changes to registry entries in the database, including who made them and when.

**Why It's Important**:
- Critical for security, compliance, and troubleshooting
- Enables accountability and rollback when endpoint metadata or approval status changes
- Supports audit trails for regulated industries and enterprise change management processes

---

## Clarify

`/speckit.clarify` No Arguments

This command asks come clarifying questions about the Spec.  Run without arguments and answer the questions as posed to update the Specification.

---

## Plan

`/speckit.plan` These are enhancements and some new functionality.

**Current Implementation**:
- Add to the frontend Browse section a full page that shows all the registrations and details about their status and who owns and created them
- Create backend routes/endpoints where necessary
- Create scripts to update the database schema if required to support functionality

---

## Tasks

`/speckit.tasks` No Arguments

This command breaks down the specification into tasks

---

## Analyze

`/speckit.analyze` No Arguments

This command analyzes the specification aand the constitution to confirm consistencies

---

## Implement

`/speckit.implement` No Arguments

This command implements and creates the code for the backend

---

## Third Specification Update (Not Implemented Yet)

`/speckit.specify` Add API's or routes/endpoints to the backend that can be accessed eventually by the frontend or other systems.

#### 9. UI to Test MCP Servers

**Requirement**: Provide a "test" interface or integration to interact with MCP servers directly list the tools available.

**Why It's Important**:
- Enables developers to validate MCP responses and metadata before use
- Reduces friction in integration and troubleshooting workflows
- Helps ensure MCP endpoints are functional and compliant with expected standards

---

#### 10. Security & Access Control

**Requirement**: Strict access management for registry functions and MCP server access policies.

**Why It's Important**:
- Protects sensitive endpoints and data from unauthorized access
- Ensures role-based permissions align with enterprise identity and access management (IAM)
- Enforces consistent authentication, authorization, and policy control across teams

---

#### 11. Categorization & Filtering

**Requirement**: Allow endpoints to be tagged or categorized (e.g., "Data Services," "Developer Tools") and filtered accordingly.

**Why It's Important**:
- Supports organization-wide discoverability and navigation at scale
- Makes the registry usable for both technical and non-technical stakeholders
- Enables reporting and analytics on MCP adoption and usage by category or team
