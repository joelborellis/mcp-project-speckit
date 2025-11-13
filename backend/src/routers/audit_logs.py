"""
Audit Logs API Router.

Endpoints for querying audit log entries (admin-only).
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from dependencies import get_current_user, require_admin
from database import get_db_connection
from models.audit_log import AuditAction
from models.user import User
from schemas.audit_log import AuditLogListResponse, AuditLogResponse
from services.audit_service import AuditService
import asyncpg


router = APIRouter(
    prefix="/audit-logs",
    tags=["audit"],
    dependencies=[Depends(require_admin)]  # All endpoints require admin privileges
)


@router.get(
    "",
    response_model=AuditLogListResponse,
    summary="Query audit logs",
    description="""
    Query audit log entries with filters and pagination.
    
    **Admin-only endpoint** - requires admin privileges (403 Forbidden for non-admins).
    
    Returns audit logs in reverse chronological order (newest first).
    All filter parameters are optional - omit to query all logs.
    
    **Filters:**
    - `registration_id`: Filter by specific registration
    - `user_id`: Filter by user who performed action
    - `action`: Filter by action type (Created, Approved, Rejected, Updated, Deleted)
    - `from`: Filter by timestamp >= from (ISO 8601 format)
    - `to`: Filter by timestamp <= to (ISO 8601 format)
    
    **Pagination:**
    - `limit`: Maximum results per page (default 50, max 200)
    - `offset`: Number of results to skip (default 0)
    
    **Performance:**
    - Target response time: <1 second even with 10,000+ entries
    - Uses database indexes on registration_id, user_id, and timestamp
    
    **Example:**
    ```
    GET /audit-logs?registration_id=123e4567-e89b-12d3-a456-426614174000&limit=10
    ```
    """
)
async def query_audit_logs(
    registration_id: Optional[UUID] = Query(
        default=None,
        description="Filter by specific registration UUID"
    ),
    user_id: Optional[UUID] = Query(
        default=None,
        description="Filter by user UUID who performed action"
    ),
    action: Optional[AuditAction] = Query(
        default=None,
        description="Filter by action type: Created, Approved, Rejected, Updated, Deleted"
    ),
    from_date: Optional[datetime] = Query(
        default=None,
        alias="from",
        description="Filter by timestamp >= from (ISO 8601 format, e.g., 2025-01-01T00:00:00Z)"
    ),
    to_date: Optional[datetime] = Query(
        default=None,
        alias="to",
        description="Filter by timestamp <= to (ISO 8601 format)"
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
        description="Maximum number of results (default 50, max 200)"
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of results to skip for pagination (default 0)"
    ),
    current_user: User = Depends(get_current_user)
):
    """
    Query audit logs with filters and pagination.
    
    Admin-only endpoint for compliance and troubleshooting.
    Returns audit log entries in reverse chronological order (newest first).
    """
    # Create audit service
    audit_service = AuditService()
    
    try:
        # Get database connection and query audit logs
        async with get_db_connection() as conn:
            results, total = await audit_service.query_logs(
                connection=conn,
                registration_id=registration_id,
                user_id=user_id,
                action=action,
                from_date=from_date,
                to_date=to_date,
                limit=limit,
                offset=offset
            )
        
        # Convert dict results to AuditLogResponse models
        audit_logs = [AuditLogResponse(**result) for result in results]
        
        return AuditLogListResponse(
            results=audit_logs,
            total=total,
            limit=limit,
            offset=offset
        )
    
    except ValueError as e:
        # Handle invalid date range
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query audit logs: {str(e)}"
        )

