"""
MCP Registry Backend - Main Application

This is the main FastAPI application for the MCP (Model Context Protocol) Registry Backend.
It provides REST API endpoints for managing MCP server registrations with:
- Microsoft Entra ID authentication
- PostgreSQL database storage
- Admin approval workflow
- CORS support for frontend integration
- Structured JSON logging
- Health checks for monitoring

Quick Start:
    # Install dependencies
    uv pip install -e .
    
    # Set up environment variables
    cp .env.example .env
    # Edit .env with your configuration
    
    # Run development server
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    
    # Test health endpoint
    curl http://localhost:8000/health

API Endpoints:
    GET /health - Health check (no auth required)
    POST /users - Create/update user (auto on login)
    GET /users/me - Get current user profile
    GET /users/{user_id} - Get user by ID
    POST /registrations - Create registration
    GET /registrations - List registrations with filters
    GET /registrations/{id} - Get registration by ID
    GET /registrations/my - Get current user's registrations
    PATCH /registrations/{id}/status - Approve/reject (admin)
    DELETE /registrations/{id} - Delete registration (admin)

Environment Variables:
    DATABASE_URL - PostgreSQL connection string
    AZURE_CLIENT_ID - Entra ID application client ID
    AZURE_TENANT_ID - Entra ID tenant ID
    ENTRA_ADMIN_GROUP_ID - Entra ID admin group ID (optional)
    CORS_ORIGINS - Comma-separated allowed origins
    LOG_LEVEL - Logging level (DEBUG/INFO/WARNING/ERROR/CRITICAL)
    ENVIRONMENT - Environment name (development/staging/production)

Production Deployment:
    # Using Gunicorn with Uvicorn workers
    gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
    
    # Using Docker
    docker build -t mcp-registry-backend .
    docker run -p 8000:8000 --env-file .env mcp-registry-backend

Monitoring:
    - Health check: GET /health
    - Azure Application Insights: Automatic via structured JSON logs
    - Prometheus: Export metrics via /metrics (requires prometheus-client)

Security:
    - All endpoints (except /health) require Entra ID Bearer token
    - Admin endpoints require is_admin=true in user record
    - CORS restricted to configured origins
    - Database connection pooling with SSL/TLS
    - No sensitive data in logs (tokens, passwords)
"""

import logging
import sys
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pythonjsonlogger import jsonlogger

from config import settings
from database import init_db_pool, close_db_pool
from routers import health, users, registrations

# Configure structured JSON logging
logger = logging.getLogger()


def setup_logging():
    """
    Configure structured JSON logging for the application.
    
    Sets up logging with:
    - JSON formatter for structured logs (Azure-compatible)
    - Configurable log level from environment
    - Stdout output for container environments
    - Timestamp, level, message, and context fields
    
    Log Format (JSON):
        {
            "timestamp": "2025-11-11T10:30:00.123456Z",
            "level": "INFO",
            "name": "main",
            "message": "Application startup",
            "pathname": "/app/main.py",
            "lineno": 123
        }
        
    Azure Application Insights:
        JSON logs are automatically parsed by Azure App Insights
        for structured querying and alerting.
    """
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create stdout handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Create JSON formatter
    formatter = jsonlogger.JsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s %(pathname)s %(lineno)d',
        rename_fields={
            "levelname": "level",
            "asctime": "timestamp"
        },
        datefmt='%Y-%m-%dT%H:%M:%S'
    )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(settings.log_level)
    
    logger.info(f"Logging configured: level={settings.log_level}, environment={settings.environment}")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Application lifespan context manager.
    
    Handles startup and shutdown events:
    - Startup: Initialize database connection pool, log startup message
    - Shutdown: Close database connection pool gracefully, log shutdown message
    
    This replaces the deprecated @app.on_event("startup") and @app.on_event("shutdown")
    decorators with the new lifespan parameter in FastAPI 0.109+.
    
    Args:
        app: FastAPI application instance
        
    Yields:
        None during application runtime
        
    Raises:
        Exception: If database initialization fails (exits application)
        
    Example:
        app = FastAPI(lifespan=lifespan)
        # Startup events run here
        # ... application handles requests ...
        # Shutdown events run on exit
    """
    # Startup
    logger.info("=" * 60)
    logger.info("MCP Registry Backend starting...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Database: {settings.database_url.split('@')[-1]}")  # Hide credentials
    logger.info(f"CORS Origins: {settings.cors_origins_list}")
    logger.info(f"Log Level: {settings.log_level}")
    logger.info("=" * 60)
    
    try:
        # Initialize database connection pool
        logger.info("Initializing database connection pool...")
        await init_db_pool()
        logger.info("Database connection pool initialized successfully")
        logger.info("Application startup complete - ready to accept requests")
        
    except Exception as e:
        logger.critical(f"Failed to initialize database connection pool: {str(e)}")
        logger.critical("Application startup failed - exiting")
        sys.exit(1)
    
    # Yield control to application (handle requests)
    yield
    
    # Shutdown
    logger.info("=" * 60)
    logger.info("MCP Registry Backend shutting down...")
    
    try:
        # Close database connection pool
        logger.info("Closing database connection pool...")
        await close_db_pool()
        logger.info("Database connection pool closed successfully")
        
    except Exception as e:
        logger.error(f"Error during database connection pool shutdown: {str(e)}")
    
    logger.info("Application shutdown complete")
    logger.info("=" * 60)


# Initialize structured logging
setup_logging()

# Create FastAPI application
app = FastAPI(
    title="MCP Registry Backend",
    description=(
        "REST API for managing Model Context Protocol (MCP) server registrations. "
        "Features Microsoft Entra ID authentication, PostgreSQL storage, and admin approval workflow."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PATCH, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers (Authorization, Content-Type, etc.)
)

logger.info(f"CORS configured with origins: {settings.cors_origins_list}")

# Include routers
app.include_router(health.router)
app.include_router(users.router)
app.include_router(registrations.router)

logger.info("API routers registered: /health, /users, /registrations")


@app.get("/")
async def root():
    """
    Root endpoint - API information.
    
    Returns basic information about the API including:
    - Service name and version
    - Available endpoints
    - Documentation links
    
    Returns:
        dict: API information
        
    Example:
        GET /
        
        Response:
        {
            "name": "MCP Registry Backend",
            "version": "1.0.0",
            "status": "running",
            "docs": "/docs",
            "health": "/health"
        }
    """
    return {
        "name": "MCP Registry Backend",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.environment,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "endpoints": {
            "health": "/health",
            "users": "/users",
            "registrations": "/registrations"
        }
    }


# Log application configuration on module load
logger.info("FastAPI application created")
logger.info(f"API documentation available at: /docs and /redoc")
logger.info(f"Health check available at: /health")
