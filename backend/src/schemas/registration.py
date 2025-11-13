"""
Registration API schemas.

Pydantic schemas for registration-related API requests and responses.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, HttpUrl, EmailStr, Field, field_validator

from models.registration import RegistrationStatus


class CreateRegistrationRequest(BaseModel):
    """
    Request schema for creating a new MCP endpoint registration.
    
    Validation rules:
    - endpoint_url: Must be valid URL format
    - endpoint_name: 3-200 characters
    - owner_contact: Valid email format preferred
    - available_tools: Array of tool objects
    """
    
    endpoint_url: HttpUrl = Field(
        ...,
        description="MCP endpoint URL",
        json_schema_extra={"example": "https://mcp.example.com"}
    )
    
    endpoint_name: str = Field(
        ...,
        description="Human-readable name for the endpoint",
        min_length=3,
        max_length=200,
        json_schema_extra={"example": "Example MCP Server"}
    )
    
    description: Optional[str] = Field(
        default=None,
        description="Optional description of the endpoint",
        json_schema_extra={"example": "Provides search and analysis capabilities"}
    )
    
    owner_contact: EmailStr = Field(
        ...,
        description="Contact email for endpoint owner",
        json_schema_extra={"example": "owner@example.com"}
    )
    
    available_tools: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Array of available tools with names and optional metadata",
        json_schema_extra={
            "example": [
                {"name": "search", "description": "Search capability"},
                {"name": "analyze", "version": "1.0"}
            ]
        }
    )
    
    @field_validator("available_tools", mode="before")
    @classmethod
    def validate_available_tools(cls, v):
        """Ensure available_tools is a list and each tool has a name."""
        if v is None:
            return []
        if not isinstance(v, list):
            raise ValueError("available_tools must be an array")
        
        for tool in v:
            if not isinstance(tool, dict):
                raise ValueError("Each tool must be an object")
            if "name" not in tool:
                raise ValueError("Each tool must have a 'name' field")
            if not isinstance(tool["name"], str) or not tool["name"].strip():
                raise ValueError("Tool name must be a non-empty string")
        
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "endpoint_url": "https://mcp.example.com",
                "endpoint_name": "Example MCP Server",
                "description": "Provides search and analysis capabilities",
                "owner_contact": "owner@example.com",
                "available_tools": [
                    {"name": "search", "description": "Search capability"},
                    {"name": "analyze", "version": "1.0"}
                ]
            }
        }
    }


class UpdateStatusRequest(BaseModel):
    """
    Request schema for updating registration approval status.
    
    Admin-only operation to approve or reject pending registrations.
    """
    
    status: RegistrationStatus = Field(
        ...,
        description="New status (Approved or Rejected)",
        json_schema_extra={"example": "Approved"}
    )
    
    reason: Optional[str] = Field(
        default=None,
        description="Optional reason for approval/rejection",
        max_length=500,
        json_schema_extra={"example": "Meets all security requirements"}
    )
    
    @field_validator("status")
    @classmethod
    def validate_status_transition(cls, v):
        """Ensure status is Approved or Rejected (not Pending)."""
        if v == RegistrationStatus.PENDING:
            raise ValueError("Cannot set status to Pending - use Approved or Rejected")
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "Approved",
                "reason": "Verified endpoint security and functionality"
            }
        }
    }


class RegistrationResponse(BaseModel):
    """
    Response schema for a single registration.
    
    Returned when creating, retrieving, or updating a registration.
    """
    
    registration_id: UUID = Field(..., description="Internal unique identifier")
    endpoint_url: str = Field(..., description="MCP endpoint URL")
    endpoint_name: str = Field(..., description="Endpoint name")
    description: Optional[str] = Field(None, description="Endpoint description")
    owner_contact: str = Field(..., description="Owner contact information")
    available_tools: List[Dict[str, Any]] = Field(..., description="Available tools")
    status: RegistrationStatus = Field(..., description="Approval status")
    submitter_id: UUID = Field(..., description="User who submitted")
    approver_id: Optional[UUID] = Field(None, description="User who approved/rejected")
    created_at: datetime = Field(..., description="Creation timestamp (when submitted)")
    updated_at: datetime = Field(..., description="Last update timestamp")
    approved_at: Optional[datetime] = Field(None, description="Approval timestamp")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "registration_id": "123e4567-e89b-12d3-a456-426614174000",
                "endpoint_url": "https://mcp.example.com",
                "endpoint_name": "Example MCP Server",
                "description": "Provides search capabilities",
                "owner_contact": "owner@example.com",
                "available_tools": [{"name": "search"}],
                "status": "Pending",
                "submitter_id": "223e4567-e89b-12d3-a456-426614174000",
                "approver_id": None,
                "created_at": "2025-11-11T10:00:00Z",
                "updated_at": "2025-11-11T10:00:00Z",
                "approved_at": None
            }
        }
    }


class RegistrationListResponse(BaseModel):
    """
    Response schema for paginated list of registrations.
    
    Includes pagination metadata and array of registrations.
    """
    
    total: int = Field(
        ...,
        description="Total number of registrations matching filters",
        ge=0
    )
    
    limit: int = Field(
        ...,
        description="Maximum number of results per page",
        ge=1,
        le=1000
    )
    
    offset: int = Field(
        ...,
        description="Number of results skipped",
        ge=0
    )
    
    results: List[RegistrationResponse] = Field(
        ...,
        description="Array of registration objects"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "total": 42,
                "limit": 20,
                "offset": 0,
                "results": [
                    {
                        "registration_id": "123e4567-e89b-12d3-a456-426614174000",
                        "endpoint_url": "https://mcp.example.com",
                        "endpoint_name": "Example MCP Server",
                        "description": None,
                        "owner_contact": "owner@example.com",
                        "available_tools": [{"name": "search"}],
                        "status": "Approved",
                        "submitter_id": "223e4567-e89b-12d3-a456-426614174000",
                        "approver_id": "323e4567-e89b-12d3-a456-426614174000",
                        "created_at": "2025-11-10T10:00:00Z",
                        "updated_at": "2025-11-11T09:00:00Z",
                        "approved_at": "2025-11-11T09:00:00Z"
                    }
                ]
            }
        }
    }


