# MCP Registry Backend

FastAPI backend for MCP Registry application with PostgreSQL database and Microsoft Entra ID authentication.

## Features

- RESTful API for MCP endpoint registration and management
- PostgreSQL database with asyncpg async driver
- Microsoft Entra ID token validation
- Role-based access control (admin approval workflow)
- Structured JSON logging
- CORS support for frontend integration

## Prerequisites

- Python 3.13 or higher
- PostgreSQL 14+ (local or Azure Database for PostgreSQL)
- uv package manager (recommended) or pip
- Microsoft Entra ID application registration

## Installation

### 1. Install uv (recommended)

**Windows (PowerShell)**:
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

**macOS/Linux**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Create virtual environment

```bash
cd backend
uv venv --python 3.13
```

### 3. Activate virtual environment

**Windows (PowerShell)**:
```powershell
.venv\Scripts\Activate.ps1
```

**macOS/Linux**:
```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
uv pip install -e .
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/mcp_registry` |
| `AZURE_CLIENT_ID` | Entra ID application client ID | `12345678-1234-1234-1234-123456789012` |
| `AZURE_TENANT_ID` | Entra ID tenant ID | `87654321-4321-4321-4321-210987654321` |
| `ENTRA_ADMIN_GROUP_ID` | Entra ID admin group ID | `abcdef12-3456-7890-abcd-ef1234567890` |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `http://localhost:5173,http://localhost:3000` |
| `LOG_LEVEL` | Logging level | `INFO` (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `ENVIRONMENT` | Environment name | `development` |

### Database Setup

1. Create PostgreSQL database:
```sql
CREATE DATABASE mcp_registry;
```

2. Run schema initialization script:
```bash
psql -U postgres -d mcp_registry -f scripts/db/init_schema.sql
```

See `scripts/db/README.md` for detailed database setup instructions.

## Running the Application

### Development Server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Production Server

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the server is running, access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## API Endpoints

### Health Check

- `GET /health` - Check API and database health

### User Management

- `POST /users` - Create or update user from Entra ID token
- `GET /users/me` - Get current authenticated user
- `GET /users/{user_id}` - Get user by ID

### Registration Management

- `POST /registrations` - Submit new MCP endpoint registration
- `GET /registrations` - List all registrations (with filters)
- `GET /registrations/{id}` - Get specific registration
- `GET /registrations/my` - Get current user's registrations
- `PATCH /registrations/{id}/status` - Approve/reject registration (admin only)
- `DELETE /registrations/{id}` - Delete registration (admin only)

## Project Structure

```
backend/
├── src/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration and environment variables
│   ├── database.py          # Database connection and pool management
│   ├── dependencies.py      # FastAPI dependencies (auth, etc.)
│   ├── auth/
│   │   └── entra_validator.py  # Entra ID token validation
│   ├── models/              # Pydantic models (internal data structures)
│   │   ├── user.py
│   │   ├── registration.py
│   │   └── audit_log.py
│   ├── schemas/             # Pydantic schemas (API request/response)
│   │   ├── registration.py
│   │   └── user.py
│   ├── services/            # Business logic layer
│   │   ├── user_service.py
│   │   └── registration_service.py
│   └── routers/             # API route handlers
│       ├── health.py
│       ├── users.py
│       └── registrations.py
├── scripts/
│   └── db/
│       ├── init_schema.sql  # Database schema initialization
│       └── README.md        # Database setup instructions
├── pyproject.toml           # Project dependencies and metadata
├── .env.example             # Example environment variables
└── README.md                # This file
```

## Development

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all function parameters and return values
- Keep functions small and focused (single responsibility)
- Use descriptive variable and function names

### Manual Verification

Since this project follows a no-testing constitution, use these manual verification methods:

1. **API Testing**: Use Postman, curl, or FastAPI Swagger UI
2. **Database Testing**: Direct SQL queries via psql or database client
3. **Integration Testing**: Full workflow testing with frontend application

Example curl commands:

```bash
# Health check
curl http://localhost:8000/health

# Create registration (requires Entra ID token)
curl -X POST http://localhost:8000/registrations \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "endpoint_url": "https://mcp.example.com",
    "endpoint_name": "Example MCP Server",
    "description": "Example description",
    "owner_contact": "owner@example.com",
    "available_tools": [{"name": "search"}]
  }'

# List registrations
curl http://localhost:8000/registrations
```

## Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running: `pg_isready`
- Check connection string in `.env`
- Ensure database exists and schema is initialized
- Check firewall settings for PostgreSQL port (default 5432)

### Authentication Issues

- Verify `AZURE_CLIENT_ID` and `AZURE_TENANT_ID` are correct
- Check Entra ID token validity and claims
- Ensure token includes required scopes

### CORS Issues

- Add frontend origin to `CORS_ORIGINS` in `.env`
- Restart backend after changing CORS configuration

## License

[Your License Here]

## Support

For questions or issues, contact [Your Contact Information]
