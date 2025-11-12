"""
AuditLog data models.

Pydantic models for AuditLog entity tracking changes to registrations.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class AuditAction(str, Enum):
    """Types of actions that can be audited."""
    CREATED = "Created"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    UPDATED = "Updated"
    DELETED = "Deleted"


class AuditLog(BaseModel):
    """
    AuditLog model tracking changes to registrations.
    
    Attributes:
        log_id: Internal unique identifier
        registration_id: Registration that was modified
        user_id: User who performed the action
        action: Type of action performed
        previous_status: Status before change (None for Create action)
        new_status: Status after change
        metadata: Additional context (reason for rejection, fields changed, etc.)
        timestamp: When the action occurred
    """
    
    log_id: UUID = Field(
        ...,
        description="Internal unique identifier"
    )
    
    registration_id: UUID = Field(
        ...,
        description="Registration that was modified"
    )
    
    user_id: UUID = Field(
        ...,
        description="User who performed the action"
    )
    
    action: AuditAction = Field(
        ...,
        description="Type of action performed"
    )
    
    previous_status: Optional[str] = Field(
        default=None,
        description="Status before change (None for Create action)"
    )
    
    new_status: Optional[str] = Field(
        default=None,
        description="Status after change"
    )
    
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context (reason, changed fields, etc.)"
    )
    
    timestamp: datetime = Field(
        ...,
        description="When the action occurred"
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
                    "reason": "Meets all requirements",
                    "reviewer_notes": "Verified endpoint security"
                },
                "timestamp": "2025-11-11T10:00:00Z"
            }
        }
    }


class AuditLogCreate(BaseModel):
    """
    Schema for creating an audit log entry.
    
    Used internally by services to track changes.
    """
    
    registration_id: UUID = Field(
        ...,
        description="Registration that was modified"
    )
    
    user_id: UUID = Field(
        ...,
        description="User who performed the action"
    )
    
    action: AuditAction = Field(
        ...,
        description="Type of action performed"
    )
    
    previous_status: Optional[str] = Field(
        default=None,
        description="Status before change"
    )
    
    new_status: Optional[str] = Field(
        default=None,
        description="Status after change"
    )
    
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "registration_id": "223e4567-e89b-12d3-a456-426614174000",
                "user_id": "323e4567-e89b-12d3-a456-426614174000",
                "action": "Approved",
                "previous_status": "Pending",
                "new_status": "Approved",
                "metadata": {"reason": "Approved by admin"}
            }
        }
    }
