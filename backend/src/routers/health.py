"""
Health Check Router

This module provides health check endpoints for monitoring service availability
and database connectivity. Health checks are commonly used by:
- Load balancers for routing decisions
- Orchestration platforms (Kubernetes, Docker Swarm) for readiness/liveness probes
- Monitoring systems (Azure Monitor, Prometheus) for uptime tracking
- CI/CD pipelines for deployment validation

Endpoints:
    GET /health: Check service and database health

Example Response (Healthy):
    {
        "status": "healthy",
        "database": "connected",
        "timestamp": "2025-11-11T10:30:00Z"
    }

Example Response (Unhealthy):
    HTTP 503 Service Unavailable
    {
        "status": "unhealthy",
        "database": "disconnected",
        "error": "Connection timeout",
        "timestamp": "2025-11-11T10:30:00Z"
    }

Usage in Kubernetes:
    livenessProbe:
      httpGet:
        path: /health
        port: 8000
      initialDelaySeconds: 30
      periodSeconds: 10
      
    readinessProbe:
      httpGet:
        path: /health
        port: 8000
      initialDelaySeconds: 5
      periodSeconds: 5

Security Notes:
- Health endpoint does not require authentication (public)
- Does not expose sensitive information (credentials, connection strings)
- Database check performs lightweight SELECT 1 query
"""

import logging
from datetime import datetime
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from database import check_db_health

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Check service and database health.
    
    Performs a lightweight health check by:
    1. Verifying database connection pool is initialized
    2. Executing a simple SELECT 1 query to test database connectivity
    3. Returning health status with timestamp
    
    Returns:
        JSONResponse: Health status with 200 OK if healthy, 503 Service Unavailable if unhealthy
        
    Response Schema:
        {
            "status": "healthy" | "unhealthy",
            "database": "connected" | "disconnected",
            "timestamp": "2025-11-11T10:30:00Z",
            "error": "Error message (only if unhealthy)"
        }
        
    Status Codes:
        - 200 OK: Service is healthy and database is connected
        - 503 Service Unavailable: Service is unhealthy or database is disconnected
        
    Example:
        # Curl request
        curl http://localhost:8000/health
        
        # Response (healthy)
        {
            "status": "healthy",
            "database": "connected",
            "timestamp": "2025-11-11T10:30:00.123456"
        }
        
        # Response (unhealthy)
        HTTP 503 Service Unavailable
        {
            "status": "unhealthy",
            "database": "disconnected",
            "error": "Connection pool not initialized",
            "timestamp": "2025-11-11T10:30:00.123456"
        }
        
    Monitoring Integration:
        - Azure Monitor: Configure Application Insights availability test
        - Prometheus: Use blackbox_exporter to scrape this endpoint
        - Kubernetes: Use as livenessProbe and readinessProbe
        - Load Balancers: Configure health check with path /health
        
    Performance:
        - Query execution time: < 10ms (SELECT 1)
        - No external API calls
        - Lightweight operation safe for frequent polling (every 5-10 seconds)
        
    Security:
        - No authentication required (public endpoint)
        - No sensitive data in response
        - Connection string not exposed
        - Errors are generic (no internal details leaked)
    """
    try:
        # Check database health
        db_health = await check_db_health()
        
        timestamp = datetime.utcnow().isoformat()
        
        if db_health["status"] == "healthy":
            logger.debug("Health check passed")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": "healthy",
                    "database": "connected",
                    "timestamp": timestamp
                }
            )
        else:
            logger.warning(f"Health check failed: {db_health.get('error', 'Unknown error')}")
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "unhealthy",
                    "database": "disconnected",
                    "error": db_health.get("error", "Database connection failed"),
                    "timestamp": timestamp
                }
            )
            
    except Exception as e:
        logger.error(f"Health check exception: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": "Internal health check error",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
