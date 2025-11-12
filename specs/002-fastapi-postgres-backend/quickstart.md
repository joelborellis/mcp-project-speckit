# Quickstart Guide: FastAPI Backend

**Feature**: 002-fastapi-postgres-backend  
**Date**: 2025-11-11

## Overview

This guide walks you through setting up and running the FastAPI backend for the MCP Registry application.

---

## Prerequisites

- **Python**: 3.13 or higher
- **PostgreSQL**: 13+ (local installation or Azure Database for PostgreSQL)
- **Git**: For cloning the repository
- **uv**: Fast Python package manager (install from https://github.com/astral-sh/uv)
- **Microsoft Entra ID**: Tenant and app registration (for authentication)

---

## Setup Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd mcp-project-speckit
git checkout 002-fastapi-postgres-backend
```

### 2. Install uv Package Manager

If you haven't installed uv yet:

```bash
# On Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify installation:

```bash
uv --version
```

### 3. Set Up Python Environment

Create a virtual environment using uv:

```bash
# Navigate to backend directory
cd backend

# Create virtual environment with Python 3.13
uv venv --python 3.13

# Activate the virtual environment
# On Windows (PowerShell)
.venv\Scripts\Activate.ps1

# On macOS/Linux
source .venv/bin/activate
```

### 4. Install Dependencies

Install all dependencies using uv (much faster than pip):

```bash
# Install from pyproject.toml
uv pip install -e .

# Or if you have a requirements.txt:
uv pip install -r requirements.txt
```

**Core Dependencies** (installed automatically):
- `fastapi` - Web framework
- `uvicorn[standard]` - ASGI server
- `asyncpg` - Async PostgreSQL driver
- `pydantic` - Data validation
- `python-jose[cryptography]` or `PyJWT` - JWT validation
- `python-multipart` - File upload support
- `python-dotenv` - Environment variable loading
- `python-json-logger` - JSON logging

### 5. Set Up PostgreSQL Database

#### Option A: Local PostgreSQL

1. Install PostgreSQL (if not already installed)
2. Create a database:

```bash
psql -U postgres
CREATE DATABASE mcp_registry;
\q
```

3. Note your connection details:
   - Host: `localhost`
   - Port: `5432`
   - Database: `mcp_registry`
   - Username: `postgres`
   - Password: (your password)

#### Option B: Azure Database for PostgreSQL

1. Create an Azure Database for PostgreSQL instance via Azure Portal
2. Configure firewall rules to allow your IP address
3. Note your connection details from the Azure Portal:
   - Host: `<your-server>.postgres.database.azure.com`
   - Port: `5432`
   - Database: `mcp_registry`
   - Username: `<your-username>@<your-server>`
   - Password: (your password)
   - SSL Mode: `require`

### 5. Run Database Schema Script

Execute the schema creation script:

```bash
# From the backend directory
psql -h <host> -U <username> -d mcp_registry -f scripts/db/init_schema.sql

# Example for local:
psql -h localhost -U postgres -d mcp_registry -f scripts/db/init_schema.sql

# Example for Azure (may need to specify SSL):
psql "host=<server>.postgres.database.azure.com port=5432 dbname=mcp_registry user=<user>@<server> password=<pwd> sslmode=require" -f scripts/db/init_schema.sql
```

**Verify tables were created**:

```bash
psql -h <host> -U <username> -d mcp_registry -c "\dt"
```

You should see: `users`, `registrations`, `audit_log`

### 6. Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# backend/.env
DATABASE_URL=postgresql://<username>:<password>@<host>:<port>/mcp_registry

# For Azure with SSL:
# DATABASE_URL=postgresql://<user>@<server>:<password>@<server>.postgres.database.azure.com:5432/mcp_registry?sslmode=require

# Microsoft Entra ID Configuration
ENTRA_TENANT_ID=<your-tenant-id>
ENTRA_CLIENT_ID=<your-client-id>
ENTRA_CLIENT_SECRET=<your-client-secret>

# CORS Origins (comma-separated for production)
CORS_ORIGINS=http://localhost:5173

# Optional: Logging level
LOG_LEVEL=INFO
```

**Getting Entra ID Credentials**:
1. Go to Azure Portal → Entra ID → App registrations
2. Find or create your app registration
3. Note the Application (client) ID and Directory (tenant) ID
4. Create a client secret under "Certificates & secrets"

**Security Note**: Never commit `.env` to version control. Add `.env` to `.gitignore`.

### 7. Start the Backend Server

From the `backend/` directory:

```bash
# Development mode (with auto-reload)
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The server will start at: `http://localhost:8000`

**Expected output**:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Database connection pool created
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 8. Verify the Backend is Running

Open a browser or use curl:

```bash
curl http://localhost:8000/health
```

**Expected response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-11-11T10:00:00Z"
}
```

### 9. View API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

---

## Testing the API

### Get Health Status

```bash
curl http://localhost:8000/health
```

### Create a Registration (requires Entra ID token)

First, get a token from your frontend or using MSAL:

```bash
export TOKEN="<your-entra-id-token>"

curl -X POST http://localhost:8000/registrations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "endpoint_url": "https://mcp.example.com",
    "endpoint_name": "Test MCP Server",
    "owner_contact": "test@example.com",
    "available_tools": [{"name": "search"}]
  }'
```

### List All Registrations

```bash
curl http://localhost:8000/registrations \
  -H "Authorization: Bearer $TOKEN"
```

### Approve a Registration (admin only)

```bash
curl -X PATCH http://localhost:8000/registrations/<registration-id>/status \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "Approved"}'
```

---

## Connecting the Frontend

### 1. Update Frontend Environment Variables

Create or update `frontend/.env`:

```
VITE_API_BASE_URL=http://localhost:8000
```

### 2. Update Frontend API Service

The `frontend/src/services/api.service.ts` should:

1. Use `VITE_API_BASE_URL` as the base URL
2. Include Entra ID token in Authorization header
3. Replace IndexedDB calls with HTTP requests

Example:

```typescript
// frontend/src/services/api.service.ts
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function createRegistration(data: RegistrationCreate, token: string) {
  const response = await fetch(`${API_BASE_URL}/registrations`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(data)
  });
  
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  
  return response.json();
}
```

### 3. Start Both Frontend and Backend

**Terminal 1 (Backend)**:
```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

**Terminal 2 (Frontend)**:
```bash
cd frontend
npm run dev
```

Frontend will be at `http://localhost:5173` (Vite default)

---

## Common Issues

### 1. Database Connection Fails

**Error**: `connection refused` or `could not connect to server`

**Solutions**:
- Verify PostgreSQL is running: `pg_isready` or check services
- Check DATABASE_URL in `.env` has correct host/port/credentials
- For Azure: Verify firewall rules allow your IP address
- Check SSL mode: Azure requires `sslmode=require`

### 2. Token Validation Fails

**Error**: `401 Unauthorized` or `Invalid token`

**Solutions**:
- Verify ENTRA_TENANT_ID and ENTRA_CLIENT_ID in `.env`
- Ensure token is from the correct Entra ID tenant
- Check token expiration (tokens expire after 1 hour typically)
- Verify app registration has correct permissions in Entra ID

### 3. CORS Errors in Browser

**Error**: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solutions**:
- Verify CORS_ORIGINS in `.env` includes frontend URL
- Ensure frontend is running on the allowed origin
- Check that CORSMiddleware is properly configured in `main.py`

### 4. Module Not Found Errors

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solutions**:
- Activate virtual environment: `source venv/bin/activate` or `.\venv\Scripts\Activate.ps1`
- Install dependencies: `pip install -r requirements.txt`
- Verify correct Python interpreter is being used

### 5. Database Schema Not Created

**Error**: `relation "users" does not exist`

**Solutions**:
- Run the schema script: `psql ... -f scripts/db/init_schema.sql`
- Check script output for errors (permissions, syntax)
- Verify you're connecting to the correct database

---

## Development Workflow

1. **Make code changes** in `backend/src/`
2. **Server auto-reloads** (if running with `--reload` flag)
3. **Test changes** using `/docs` or curl
4. **Check logs** in terminal for errors/warnings
5. **Commit changes** to git when tests pass

---

## Production Deployment

### Checklist

- [ ] Set `LOG_LEVEL=WARNING` or `ERROR` in production `.env`
- [ ] Restrict `CORS_ORIGINS` to specific frontend domain(s)
- [ ] Use strong database credentials (not default postgres/postgres)
- [ ] Enable SSL/TLS for database connections
- [ ] Use Azure Key Vault or similar for secret management (not `.env` files)
- [ ] Run with multiple workers: `--workers 4`
- [ ] Set up reverse proxy (nginx, Azure Application Gateway)
- [ ] Configure health checks and monitoring
- [ ] Disable `/docs` and `/redoc` endpoints (optional security measure)
- [ ] Set up logging to Azure Application Insights or similar

### Azure Deployment Example

Using Azure App Service:

1. Create App Service with Python 3.13 runtime
2. Configure app settings (environment variables) in Azure Portal
3. Deploy code via GitHub Actions, Azure DevOps, or git push
4. Configure custom startup command:
   ```
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app
   ```

---

## Next Steps

1. ✅ Backend is running
2. → Update frontend to call backend APIs (see "Connecting the Frontend")
3. → Test full workflow: login → register endpoint → admin approve
4. → Set up monitoring and logging
5. → Deploy to production environment

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)
- [Microsoft Entra ID Documentation](https://learn.microsoft.com/entra/)
- [Azure Database for PostgreSQL](https://learn.microsoft.com/azure/postgresql/)
- [Uvicorn Documentation](https://www.uvicorn.org/)

---

## Getting Help

If you encounter issues:

1. Check the logs in the terminal where the server is running
2. Review error messages in `/docs` interactive API documentation
3. Verify all environment variables are set correctly
4. Test database connectivity separately with psql
5. Check that Entra ID tokens are valid and not expired
