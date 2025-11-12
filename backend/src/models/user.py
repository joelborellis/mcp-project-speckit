"""
User data models.

Pydantic models for User entity representing authenticated users from Microsoft Entra ID.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    """
    User model representing an authenticated user from Microsoft Entra ID.
    
    Attributes:
        user_id: Internal unique identifier
        entra_id: External ID from Microsoft Entra ID (subject claim from JWT)
        email: User's email address
        display_name: User's display name (optional)
        is_admin: Admin privilege flag based on Entra ID group membership
        created_at: Record creation timestamp
        updated_at: Last update timestamp
    """
    
    user_id: UUID = Field(
        ...,
        description="Internal unique identifier"
    )
    
    entra_id: str = Field(
        ...,
        description="External ID from Microsoft Entra ID (subject claim)",
        min_length=1,
        max_length=255
    )
    
    email: EmailStr = Field(
        ...,
        description="User's email address from Entra ID"
    )
    
    display_name: Optional[str] = Field(
        default=None,
        description="User's display name from Entra ID",
        max_length=255
    )
    
    is_admin: bool = Field(
        default=False,
        description="Admin privilege flag (determined by Entra ID group membership)"
    )
    
    created_at: datetime = Field(
        ...,
        description="Record creation timestamp"
    )
    
    updated_at: datetime = Field(
        ...,
        description="Last update timestamp"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "entra_id": "00000000-0000-0000-0000-000000000000",
                "email": "user@example.com",
                "display_name": "John Doe",
                "is_admin": False,
                "created_at": "2025-11-11T10:00:00Z",
                "updated_at": "2025-11-11T10:00:00Z"
            }
        }
    }


class UserCreate(BaseModel):
    """
    Schema for creating or updating a user from Entra ID information.
    
    Used when processing Entra ID tokens to create/update user records.
    """
    
    entra_id: str = Field(
        ...,
        description="External ID from Microsoft Entra ID",
        min_length=1,
        max_length=255
    )
    
    email: EmailStr = Field(
        ...,
        description="User's email address from Entra ID"
    )
    
    display_name: Optional[str] = Field(
        default=None,
        description="User's display name from Entra ID",
        max_length=255
    )
    
    is_admin: bool = Field(
        default=False,
        description="Admin privilege flag"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "entra_id": "00000000-0000-0000-0000-000000000000",
                "email": "user@example.com",
                "display_name": "John Doe",
                "is_admin": False
            }
        }
    }
