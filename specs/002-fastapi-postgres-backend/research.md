# Research: FastAPI Backend with PostgreSQL Database

**Feature**: 002-fastapi-postgres-backend  
**Date**: 2025-11-11  
**Purpose**: Resolve technical unknowns and document technology choices

## Research Tasks

### 1. Python Package Manager Selection

**Decision**: Use `uv` as the Python package manager

**Rationale**:
- 10-100x faster than pip for package installation and resolution
- Drop-in replacement for pip/pip-tools with compatible command syntax
- Built-in virtual environment management
- Lockfile support (uv.lock) for reproducible builds
- Written in Rust for maximum performance
- Compatible with pyproject.toml and requirements.txt
- Active development and growing adoption in Python community
- Minimal configuration required

**Alternatives Considered**:
- `pip`: Standard but slow, no built-in lockfile support
- `poetry`: Slower than uv, more complex configuration
- `pipenv`: Deprecated workflow, performance issues
- `pdm`: Good but less mature than uv

**Implementation Note**: Use `uv pip install` for dependencies, `uv venv` for virtual environments. Maintain pyproject.toml as source of truth for dependencies.

---

### 2. PostgreSQL Async Driver Selection

**Decision**: Use `asyncpg` as the primary async PostgreSQL driver

**Rationale**:
- Native asyncio support, essential for FastAPI's async/await pattern
- Excellent performance (benchmarked as fastest Python PostgreSQL driver)
- Built-in connection pooling
- Type safety with proper Python type hints
- Active maintenance and wide adoption in FastAPI ecosystem
- Direct protocol implementation (not libpq wrapper) = fewer dependencies

**Alternatives Considered**:
- `psycopg3` (async mode): Newer, but asyncpg more mature for async workloads
- `psycopg2`: Synchronous only, would block FastAPI's async event loop
- SQLAlchemy with asyncpg: Adds ORM layer complexity (violates minimal dependencies for initial version)

**Implementation Note**: Can add SQLAlchemy ORM later if needed, but start with raw asyncpg for simplicity and clarity.

---

### 3. Entra ID Token Validation Approach

**Decision**: Use `msal` library with `PyJWT` for token validation

**Rationale**:
- `msal` (Microsoft Authentication Library) is the official Microsoft library for Python
- Handles token caching, refresh, and validation against Entra ID
- `PyJWT` provides lower-level JWT validation if needed for custom scenarios
- Well-documented integration patterns with FastAPI
- Supports both synchronous and asynchronous validation
- Official support from Microsoft ensures compatibility with Entra ID updates

**Alternatives Considered**:
- `python-jose`: Community library, less official support
- Manual JWT validation with `PyJWT` alone: More complex, requires maintaining JWKS endpoint logic
- `authlib`: More generic, adds OAuth complexity we don't need

**Implementation Note**: Use `msal.ConfidentialClientApplication` for backend validation with client credentials flow. Store tenant_id, client_id, and client_secret in environment variables.

---

### 4. Database Connection Pooling Strategy

**Decision**: Use asyncpg's built-in connection pool via `asyncpg.create_pool()`

**Rationale**:
- Built into asyncpg, no additional dependencies
- Configurable pool size (recommend 10-20 connections for initial deployment)
- Automatic connection lifecycle management (acquisition, release, cleanup)
- Lazy initialization (pool created on first request)
- Health checks and connection validation built-in

**Configuration**:
```python
pool = await asyncpg.create_pool(
    dsn=DATABASE_URL,
    min_size=5,
    max_size=20,
    timeout=30,
    command_timeout=60
)
```

**Alternatives Considered**:
- SQLAlchemy async engine pooling: Adds ORM layer (deferred for simplicity)
- Manual connection management: Error-prone, reinvents wheel

---

### 5. CORS Configuration for FastAPI

**Decision**: Use FastAPI's built-in `CORSMiddleware` from `fastapi.middleware.cors`

**Rationale**:
- Native FastAPI integration, no external dependencies
- Simple configuration via allowed origins list
- Supports all standard CORS headers
- Minimal setup required

**Configuration**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Security Note**: In production, restrict `allow_origins` to specific frontend domain(s). Use environment variable for configuration.

---

### 5. Structured Logging Implementation

---

### 6. Structured Logging Implementation

**Decision**: Use `python-json-logger` for structured JSON logging

**Rationale**:
- Built-in logging module is standard Python (minimal dependencies)
- `python-json-logger` adds JSON formatting with minimal overhead
- Azure Application Insights and Log Analytics natively parse JSON logs
- Supports standard log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Easy to add contextual fields (request_id, user_id, etc.)

**Configuration**:
```python
from pythonjsonlogger import jsonlogger

handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

**Alternatives Considered**:
- `structlog`: More features but adds dependency complexity
- Plain text logging: Not machine-parsable for Azure monitoring
- Custom JSON formatter: Reinvents wheel, error-prone

---

### 7. Environment Variable Management

**Decision**: Use `python-dotenv` with `pydantic` Settings management

**Rationale**:
- `python-dotenv` loads `.env` files in development (standard practice)
- `pydantic.BaseSettings` provides type-safe environment variable parsing
- Validation and type coercion built-in
- Single source of truth for configuration
- Clear error messages for missing/invalid environment variables

**Configuration**:
```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str
    entra_tenant_id: str
    entra_client_id: str
    entra_client_secret: str
    cors_origins: list[str] = ["http://localhost:5173"]
    
    class Config:
        env_file = ".env"
```

**Alternatives Considered**:
- Manual `os.environ` access: No validation, error-prone
- `python-decouple`: Less integrated with FastAPI ecosystem
- Azure Key Vault direct access: Over-engineering for initial version (can add later)

---

### 8. Database Schema Management Approach

**Decision**: Use plain SQL migration scripts (idempotent DDL)

**Rationale**:
- Simplest approach for initial version (no migration framework dependency)
- SQL scripts are explicit and reviewable
- Idempotent design (CREATE TABLE IF NOT EXISTS) allows safe re-runs
- Easy to version control and audit
- Can migrate to Alembic later if complex migrations needed

**Script Structure**:
```sql
-- init_schema.sql
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entra_id TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    display_name TEXT,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_entra_id ON users(entra_id);
```

**Alternatives Considered**:
- Alembic: Full migration framework, adds complexity for MVP
- Django migrations: Wrong framework (we're using FastAPI)
- Flyway: Java-based, unnecessary dependency

---

### 9. HTTP Client Library for Frontend API Calls

**Decision**: Use native `fetch` API (no library needed)

**Rationale**:
- Built into modern browsers (no dependencies)
- TypeScript has excellent `fetch` type definitions
- Sufficient for RESTful API calls with JSON payloads
- Frontend already uses TypeScript, which provides type safety

**Implementation Note**: Create a thin `api.service.ts` wrapper around fetch to:
- Centralize base URL configuration
- Add authorization headers (Entra ID token)
- Handle common error responses
- Provide typed request/response interfaces

**Alternatives Considered**:
- `axios`: Popular but adds 13KB+ dependency (violates minimal dependencies)
- `ky`: Modern fetch wrapper, but unnecessary for simple REST calls
- `@tanstack/react-query`: Powerful but over-engineering for MVP

---

### 10. API Response Format Standardization

**Decision**: Use consistent JSON response structure with Pydantic models

**Rationale**:
- Pydantic provides automatic serialization/validation
- FastAPI automatically generates OpenAPI schema from Pydantic models
- Type safety enforced at compile time (TypeScript) and runtime (Python)
- Consistent error response format across all endpoints

**Standard Response Format**:
```python
# Success response (200, 201)
{
    "id": "uuid",
    "field1": "value",
    ...
}

# Error response (400, 404, 409, etc.)
{
    "detail": "Human-readable error message",
    "error_code": "DUPLICATE_ENDPOINT",  # Optional machine-readable code
    "field_errors": {...}  # Optional validation errors
}
```

---

### 11. Database Transaction Management

**Decision**: Use asyncpg's connection-level transactions with context managers

**Rationale**:
- Explicit transaction boundaries improve code clarity
- Context manager ensures automatic rollback on errors
- Works naturally with FastAPI's dependency injection
- Prevents partial updates on concurrent race conditions

**Pattern**:
```python
async with pool.acquire() as conn:
    async with conn.transaction():
        # Execute multiple queries atomically
        await conn.execute("INSERT INTO ...")
        await conn.execute("UPDATE ...")
```

**Alternatives Considered**:
- Auto-commit mode: Risky for multi-step operations
- SQLAlchemy session management: Adds ORM complexity

---

## Technology Stack Summary

| Category | Technology | Version | Justification |
|----------|-----------|---------|---------------|
| Package Manager | uv | Latest stable | 10-100x faster than pip, built-in lockfile support |
| Framework | FastAPI | Latest stable | Async-native, excellent docs, type safety |
| ASGI Server | Uvicorn | Latest stable | Standard ASGI server for FastAPI |
| Database Driver | asyncpg | Latest stable | Fastest async PostgreSQL driver |
| Auth | msal + PyJWT | Latest stable | Official Microsoft library for Entra ID |
| Validation | pydantic | Latest stable | Built into FastAPI, type-safe validation |
| Environment Config | python-dotenv | Latest stable | Standard for .env file loading |
| Logging | python-json-logger | Latest stable | JSON structured logging for Azure |
| CORS | fastapi.middleware.cors | Built-in | Native FastAPI middleware |

**Total External Dependencies**: 7 packages (all essential, well-maintained, minimal transitive dependencies)

---

## Best Practices

### FastAPI Code Organization

1. **Router Pattern**: Group related endpoints in separate router files
2. **Dependency Injection**: Use FastAPI dependencies for DB connections, auth validation
3. **Type Hints**: Use throughout for IDE support and runtime validation
4. **Async/Await**: Use consistently (never mix sync/async incorrectly)
5. **Error Handling**: Use HTTPException for consistent error responses

### Database Patterns

1. **Connection Pooling**: Always use pool, never create connections per request
2. **Parameterized Queries**: Use `$1, $2` placeholders (prevents SQL injection)
3. **Transactions**: Wrap multi-step operations in transactions
4. **Indexes**: Create indexes on foreign keys and frequently queried columns
5. **Unique Constraints**: Enforce uniqueness at database level, not just application

### Security Patterns

1. **Token Validation**: Validate on every request (zero-trust)
2. **Environment Secrets**: Never commit secrets, use .env (gitignored)
3. **CORS**: Restrict origins in production
4. **SQL Injection**: Use parameterized queries exclusively
5. **Error Messages**: Don't leak sensitive info in error responses

---

## Integration Patterns

### Frontend → Backend Authentication Flow

1. User logs in via MSAL in React frontend
2. Frontend receives Entra ID access token
3. Frontend includes token in `Authorization: Bearer <token>` header
4. Backend validates token against Entra ID on every request
5. Backend extracts user identity (entra_id, email) from validated token
6. Backend creates/updates user record in database
7. Backend associates user_id with registration operations

### Database Connection Lifecycle

1. Application startup: Create connection pool
2. Per request: Acquire connection from pool (via dependency)
3. Execute queries within connection/transaction
4. Release connection back to pool
5. Application shutdown: Close pool gracefully

---

## Open Questions Resolved

1. ✅ **Which Python package manager?** → uv (10-100x faster than pip)
2. ✅ **Which async PostgreSQL driver?** → asyncpg (performance + maturity)
3. ✅ **How to validate Entra ID tokens?** → msal library + PyJWT
4. ✅ **Schema management approach?** → Idempotent SQL scripts initially
5. ✅ **CORS configuration?** → FastAPI built-in middleware
6. ✅ **Logging format?** → JSON with python-json-logger
7. ✅ **Environment variables?** → python-dotenv + pydantic Settings
8. ✅ **Frontend HTTP client?** → Native fetch API (no library needed)
9. ✅ **Transaction management?** → asyncpg context managers

---

## Next Steps (Phase 1)

1. Create `data-model.md` with entity definitions and relationships
2. Generate API contracts in `/contracts/api-endpoints.md`
3. Generate database schema in `/contracts/database-schema.sql`
4. Create `quickstart.md` with setup instructions
5. Update agent context files with new backend technologies
