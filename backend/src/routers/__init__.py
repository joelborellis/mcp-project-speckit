"""
Routers Package

This package provides FastAPI router modules for all API endpoints.
Each router handles a specific domain of functionality:
- health: Health check and readiness endpoints
- users: User profile and management endpoints
- registrations: MCP server registration CRUD endpoints

Example Usage:
    from routers import health, users, registrations
    from fastapi import FastAPI
    
    app = FastAPI()
    app.include_router(health.router)
    app.include_router(users.router)
    app.include_router(registrations.router)

Router Organization:
    - Each router is a separate module with APIRouter instance
    - Routers use dependency injection for auth (get_current_user, require_admin)
    - All routes include comprehensive docstrings with examples
    - Error handling with appropriate HTTP status codes

Authentication:
    - health.router: No authentication required
    - users.router: All endpoints require authentication
    - registrations.router: Read operations require auth, write operations require admin
"""

from routers import health, users, registrations

__all__ = ["health", "users", "registrations"]
