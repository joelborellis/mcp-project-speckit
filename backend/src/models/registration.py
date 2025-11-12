"""
Registration data models.

Pydantic models for Registration entity representing MCP endpoint registrations.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, HttpUrl, Field, field_validator


class RegistrationStatus(str, Enum):
    """Registration approval status."""
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class ToolInfo(BaseModel):
    """Information about an available tool."""
    name: str = Field(..., description="Tool name", min_length=1)
    description: Optional[str] = Field(None, description="Tool description")
    version: Optional[str] = Field(None, description="Tool version")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "search",
                "description": "Search capability",
                "version": "1.0"
            }
        }
    }


class Registration(BaseModel):
    """
    Registration model representing an MCP endpoint registration.
    
    Attributes:
        registration_id: Internal unique identifier
        endpoint_url: MCP endpoint URL (must be unique)
        endpoint_name: Human-readable name for the endpoint
        description: Optional description
        owner_contact: Contact information for endpoint owner
        available_tools: List of available tools/capabilities
        status: Current approval status (Pending, Approved, Rejected)
        submitter_id: User who submitted the registration
        approver_id: Admin who approved/rejected (None if pending)
        submitted_at: When registration was submitted
        approved_at: When registration was approved/rejected (None if pending)
        created_at: Record creation timestamp
        updated_at: Last update timestamp
    """
    
    registration_id: UUID = Field(
        ...,
        description="Internal unique identifier"
    )
    
    endpoint_url: HttpUrl = Field(
        ...,
        description="MCP endpoint URL (must be unique)"
    )
    
    endpoint_name: str = Field(
        ...,
        description="Human-readable name for the endpoint",
        min_length=3,
        max_length=200
    )
    
    description: Optional[str] = Field(
        default=None,
        description="Optional description of what the endpoint provides"
    )
    
    owner_contact: str = Field(
        ...,
        description="Contact information for endpoint owner",
        min_length=1
    )
    
    available_tools: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of available tools/capabilities"
    )
    
    status: RegistrationStatus = Field(
        default=RegistrationStatus.PENDING,
        description="Current approval status"
    )
    
    submitter_id: UUID = Field(
        ...,
        description="User who submitted the registration"
    )
    
    approver_id: Optional[UUID] = Field(
        default=None,
        description="Admin who approved/rejected (None if pending)"
    )
    
    created_at: datetime = Field(
        ...,
        description="When registration was submitted (record creation timestamp)"
    )
    
    updated_at: datetime = Field(
        ...,
        description="Last update timestamp"
    )
    
    approved_at: Optional[datetime] = Field(
        default=None,
        description="When registration was approved/rejected (None if pending)"
    )
    
    @field_validator("available_tools", mode="before")
    @classmethod
    def validate_available_tools(cls, v):
        """Ensure available_tools is a list and parse JSON string if needed."""
        if v is None:
            return []
        # If it's a JSON string (from database), parse it
        if isinstance(v, str):
            import json
            try:
                v = json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("available_tools must be valid JSON")
        if not isinstance(v, list):
            raise ValueError("available_tools must be a list")
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "registration_id": "123e4567-e89b-12d3-a456-426614174000",
                "endpoint_url": "https://mcp.example.com",
                "endpoint_name": "Example MCP Server",
                "description": "Provides search and analysis capabilities",
                "owner_contact": "owner@example.com",
                "available_tools": [
                    {"name": "search", "description": "Search capability"},
                    {"name": "analyze", "version": "1.0"}
                ],
                "status": "Pending",
                "submitter_id": "223e4567-e89b-12d3-a456-426614174000",
                "approver_id": None,
                "created_at": "2025-11-11T10:00:00Z",
                "updated_at": "2025-11-11T10:00:00Z",
                "approved_at": None
            }
        }
    }


class RegistrationCreate(BaseModel):
    """
    Schema for creating a new registration.
    
    Used when users submit new MCP endpoint registrations.
    Status defaults to Pending, submitter_id comes from authenticated user.
    """
    
    endpoint_url: HttpUrl = Field(
        ...,
        description="MCP endpoint URL"
    )
    
    endpoint_name: str = Field(
        ...,
        description="Human-readable name for the endpoint",
        min_length=3,
        max_length=200
    )
    
    description: Optional[str] = Field(
        default=None,
        description="Optional description"
    )
    
    owner_contact: str = Field(
        ...,
        description="Contact information for endpoint owner",
        min_length=1
    )
    
    available_tools: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of available tools"
    )
    
    @field_validator("available_tools", mode="before")
    @classmethod
    def validate_available_tools(cls, v):
        """Ensure available_tools is a list and parse JSON string if needed."""
        if v is None:
            return []
        # If it's a JSON string, parse it
        if isinstance(v, str):
            import json
            try:
                v = json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("available_tools must be valid JSON")
        if not isinstance(v, list):
            raise ValueError("available_tools must be a list")
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "endpoint_url": "https://mcp.example.com",
                "endpoint_name": "Example MCP Server",
                "description": "Provides search capabilities",
                "owner_contact": "owner@example.com",
                "available_tools": [
                    {"name": "search"}
                ]
            }
        }
    }
