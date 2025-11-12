"""
User API schemas.

Pydantic schemas for user-related API responses.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserResponse(BaseModel):
    """
    Response schema for user information.
    
    Returned when retrieving user profiles.
    """
    
    user_id: UUID = Field(..., description="Internal unique identifier")
    entra_id: str = Field(..., description="Entra ID external identifier")
    email: EmailStr = Field(..., description="User's email address")
    display_name: Optional[str] = Field(None, description="User's display name")
    is_admin: bool = Field(..., description="Admin privilege flag")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
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
