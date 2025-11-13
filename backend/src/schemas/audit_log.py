"""
Audit Log API Schemas.

Pydantic schemas for audit log API requests and responses.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from pydantic import BaseModel, Field

from models.audit_log import AuditAction


class AuditLogResponse(BaseModel):
    """
    Response schema for a single audit log entry.
    
    Returned by GET /audit-logs endpoint for individual entries.
    """
    
    log_id: UUID = Field(
        ...,
        description="Unique identifier for this audit log entry"
    )
    
    registration_id: UUID = Field(
        ...,
        description="UUID of the registration that was modified"
    )
    
    user_id: UUID = Field(
        ...,
        description="UUID of the user who performed the action"
    )
    
    action: AuditAction = Field(
        ...,
        description="Type of action: Created, Approved, Rejected, Updated, or Deleted"
    )
    
    previous_status: Optional[str] = Field(
        default=None,
        description="Status before the change (None for Created action)"
    )
    
    new_status: Optional[str] = Field(
        default=None,
        description="Status after the change"
    )
    
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context (JSONB): reason, changed fields, etc."
    )
    
    timestamp: datetime = Field(
        ...,
        description="When the action occurred (UTC)"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "log_id": "123e4567-e89b-12d3-a456-426614174000",
                "registration_id": "223e4567-e89b-12d3-a456-426614174000",
                "user_id": "323e4567-e89b-12d3-a456-426614174000",
                "action": "Approved",
                "previous_status": "Pending",
                "new_status": "Approved",
                "metadata": {
                    "reason": "Meets all security requirements"
                },
                "timestamp": "2025-11-12T10:30:00Z"
            }
        }
    }


class AuditLogListResponse(BaseModel):
    """
    Response schema for paginated audit log queries.
    
    Returned by GET /audit-logs endpoint with filters and pagination.
    """
    
    results: List[AuditLogResponse] = Field(
        ...,
        description="Array of audit log entries matching the query"
    )
    
    total: int = Field(
        ...,
        description="Total number of audit log entries matching filters (before pagination)"
    )
    
    limit: int = Field(
        ...,
        description="Maximum number of results per page (applied to this response)"
    )
    
    offset: int = Field(
        ...,
        description="Number of results skipped (pagination offset)"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "results": [
                    {
                        "log_id": "123e4567-e89b-12d3-a456-426614174000",
                        "registration_id": "223e4567-e89b-12d3-a456-426614174000",
                        "user_id": "323e4567-e89b-12d3-a456-426614174000",
                        "action": "Approved",
                        "previous_status": "Pending",
                        "new_status": "Approved",
                        "metadata": {"reason": "Approved by admin"},
                        "timestamp": "2025-11-12T10:30:00Z"
                    },
                    {
                        "log_id": "124e4567-e89b-12d3-a456-426614174001",
                        "registration_id": "223e4567-e89b-12d3-a456-426614174000",
                        "user_id": "424e4567-e89b-12d3-a456-426614174002",
                        "action": "Created",
                        "previous_status": None,
                        "new_status": "Pending",
                        "metadata": {
                            "endpoint_name": "Example MCP Server",
                            "endpoint_url": "https://example.com/mcp"
                        },
                        "timestamp": "2025-11-12T09:00:00Z"
                    }
                ],
                "total": 42,
                "limit": 50,
                "offset": 0
            }
        }
    }

