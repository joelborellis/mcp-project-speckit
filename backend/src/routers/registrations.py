"""
Registrations Router

This module provides MCP server registration management endpoints.
Handles full CRUD operations for registration lifecycle:
- Create: Submit new registration (any authenticated user)
- Read: List registrations with filters, get by ID, get user's own registrations
- Update: Approve/reject registrations (admin only)
- Delete: Remove registrations (admin only)

Endpoints:
    POST /registrations: Create new registration
    GET /registrations: List all registrations with filters (status, search, pagination)
    GET /registrations/{registration_id}: Get registration by ID
    GET /registrations/my: Get current user's registrations
    PATCH /registrations/{registration_id}/status: Update registration status (admin)
    DELETE /registrations/{registration_id}: Delete registration (admin)

Authentication:
    All endpoints require valid Entra ID Bearer token.
    Admin-only endpoints (PATCH, DELETE) require is_admin=true.

Example Usage:
    # Create registration
    curl -X POST -H "Authorization: Bearer <token>" \\
         -H "Content-Type: application/json" \\
         -d '{"endpoint_url": "https://api.example.com", ...}' \\
         http://localhost:8000/registrations
    
    # List pending registrations
    curl -H "Authorization: Bearer <token>" \\
         "http://localhost:8000/registrations?status=Pending&limit=10"
    
    # Approve registration (admin)
    curl -X PATCH -H "Authorization: Bearer <token>" \\
         -H "Content-Type: application/json" \\
         -d '{"status": "Approved"}' \\
         http://localhost:8000/registrations/{id}/status

Security Notes:
- Create: Any authenticated user
- Read: Any authenticated user (list/get operations)
- Update status: Admin only (require_admin dependency)
- Delete: Admin only (require_admin dependency)
"""

import logging
from typing import Optional
from uuid import UUID
import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status, Query

from models import User, RegistrationStatus
from dependencies import get_current_user, require_admin
from services import RegistrationService
from database import get_db_connection
from schemas.registration import (
    CreateRegistrationRequest,
    UpdateStatusRequest,
    RegistrationResponse,
    RegistrationListResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/registrations", tags=["registrations"])


@router.post("", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
async def create_registration(
    request: CreateRegistrationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new MCP server registration.
    
    Submits a new registration with status='Pending'. Any authenticated user
    can create registrations. The submitter_id is automatically set to the
    current user's user_id.
    
    Args:
        request: CreateRegistrationRequest with endpoint details
        current_user: Automatically injected by get_current_user dependency
        
    Returns:
        RegistrationResponse: Created registration with status='Pending'
        
    Status Codes:
        - 201 Created: Registration created successfully
        - 400 Bad Request: Invalid request data (validation error)
        - 401 Unauthorized: Invalid or missing token
        - 409 Conflict: endpoint_url already registered
        
    Example:
        POST /registrations
        Authorization: Bearer <token>
        Content-Type: application/json
        
        {
            "endpoint_url": "https://api.example.com/mcp",
            "endpoint_name": "Example MCP Server",
            "description": "Production MCP endpoint for example.com",
            "owner_contact": "admin@example.com",
            "available_tools": [
                {"name": "search", "description": "Search tool"},
                {"name": "analyze", "description": "Analysis tool"}
            ]
        }
        
        Response (201 Created):
        {
            "registration_id": "uuid",
            "endpoint_url": "https://api.example.com/mcp",
            "endpoint_name": "Example MCP Server",
            "description": "Production MCP endpoint for example.com",
            "owner_contact": "admin@example.com",
            "available_tools": [...],
            "status": "Pending",
            "submitter_id": "user-uuid",
            "approver_id": null,
            "created_at": "2025-11-11T10:30:00Z",
            "updated_at": "2025-11-11T10:30:00Z",
            "approved_at": null
        }
        
        Response (409 Conflict):
        {
            "detail": "Registration with this endpoint URL already exists"
        }
        
    Validation:
        - endpoint_url: Must be valid HTTP/HTTPS URL
        - endpoint_name: 3-200 characters
        - owner_contact: Valid email address
        - available_tools: Array of objects, each must have "name" field
        
    Workflow:
        1. User submits registration → status='Pending'
        2. Admin reviews → PATCH /registrations/{id}/status
        3. Admin approves → status='Approved'
        4. OR Admin rejects → status='Rejected'
    """
    logger.info(
        f"Creating registration for {request.endpoint_url} "
        f"by user {current_user.user_id} ({current_user.email})"
    )
    
    try:
        async with get_db_connection() as conn:
            service = RegistrationService(conn)
            
            # Convert schema to model
            from models import RegistrationCreate
            
            # Pass request directly - RegistrationService will handle conversion
            registration = await service.create_registration(
                request,
                submitter_id=current_user.user_id
            )
            
            logger.info(f"Registration created: {registration.registration_id}")
            
            return RegistrationResponse(
                registration_id=registration.registration_id,
                endpoint_url=str(registration.endpoint_url),  # Convert HttpUrl to string
                endpoint_name=registration.endpoint_name,
                description=registration.description,
                owner_contact=registration.owner_contact,
                available_tools=registration.available_tools,
                status=registration.status,
                submitter_id=registration.submitter_id,
                approver_id=registration.approver_id,
                created_at=registration.created_at,
                updated_at=registration.updated_at,
                approved_at=registration.approved_at
            )
            
    except asyncpg.UniqueViolationError:
        logger.warning(f"Duplicate endpoint_url: {request.endpoint_url}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Registration with this endpoint URL already exists"
        )
    except Exception as e:
        logger.error(f"Error creating registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("", response_model=RegistrationListResponse)
async def list_registrations(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: Pending, Approved, Rejected"),
    submitter_id: Optional[UUID] = Query(None, description="Filter by submitter user ID"),
    search: Optional[str] = Query(None, description="Search in endpoint_name and owner_contact"),
    limit: int = Query(10, ge=1, le=1000, description="Maximum results to return (1-1000)"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: User = Depends(get_current_user)
):
    """
    List all registrations with optional filters and pagination.
    
    Returns paginated list of registrations ordered by created_at DESC (newest first).
    Any authenticated user can list registrations.
    
    Args:
        status_filter: Filter by status ('Pending', 'Approved', 'Rejected'). Optional.
        submitter_id: Filter by submitter user ID. Optional.
        search: Search term for endpoint_name or owner_contact (case-insensitive). Optional.
        limit: Maximum results to return (1-100). Default 10.
        offset: Number of results to skip for pagination. Default 0.
        current_user: Automatically injected by get_current_user dependency
        
    Returns:
        RegistrationListResponse: Paginated list with total count and results
        
    Status Codes:
        - 200 OK: Results returned (may be empty list)
        - 401 Unauthorized: Invalid or missing token
        
    Example:
        GET /registrations?status=Pending&limit=10&offset=0
        Authorization: Bearer <token>
        
        Response (200 OK):
        {
            "total": 25,
            "limit": 10,
            "offset": 0,
            "results": [
                {
                    "registration_id": "uuid",
                    "endpoint_url": "https://api.example.com",
                    "endpoint_name": "Example MCP Server",
                    "status": "Pending",
                    ...
                },
                ...
            ]
        }
        
    Query Examples:
        # Page 1: First 10 pending registrations
        GET /registrations?status=Pending&limit=10&offset=0
        
        # Page 2: Next 10 pending registrations
        GET /registrations?status=Pending&limit=10&offset=10
        
        # Search for "openai"
        GET /registrations?search=openai&limit=20
        
        # Get all registrations by specific user
        GET /registrations?submitter_id=user-uuid
        
    Pagination:
        - Use offset and limit for pagination
        - total field indicates total matching records
        - Calculate pages: total_pages = ceil(total / limit)
        - Next page: offset += limit
        - Previous page: offset -= limit (if offset > 0)
        
    Search Behavior:
        - Case-insensitive partial matching (ILIKE %search%)
        - Searches in endpoint_name and owner_contact fields
        - Example: search="openai" matches "OpenAI MCP Server"
    """
    logger.debug(
        f"Listing registrations: status={status_filter}, submitter_id={submitter_id}, "
        f"search={search}, limit={limit}, offset={offset}"
    )
    
    try:
        async with get_db_connection() as conn:
            service = RegistrationService(conn)
            
            result = await service.get_registrations(
                status=status_filter,
                submitter_id=submitter_id,
                search=search,
                limit=limit,
                offset=offset
            )
            
            logger.debug(f"Found {len(result['results'])} registrations (total: {result['total']})")
            
            return RegistrationListResponse(
                total=result["total"],
                limit=result["limit"],
                offset=result["offset"],
                results=[
                    RegistrationResponse(
                        registration_id=reg.registration_id,
                        endpoint_url=str(reg.endpoint_url),  # Convert HttpUrl to string
                        endpoint_name=reg.endpoint_name,
                        description=reg.description,
                        owner_contact=reg.owner_contact,
                        available_tools=reg.available_tools,
                        status=reg.status,
                        submitter_id=reg.submitter_id,
                        approver_id=reg.approver_id,
                        created_at=reg.created_at,
                        updated_at=reg.updated_at,
                        approved_at=reg.approved_at
                    )
                    for reg in result["results"]
                ]
            )
            
    except Exception as e:
        logger.error(f"Error listing registrations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/my", response_model=RegistrationListResponse)
async def get_my_registrations(
    limit: int = Query(10, ge=1, le=100, description="Maximum results to return (1-100)"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's registrations.
    
    Returns paginated list of registrations created by the authenticated user.
    Automatically filters by current user's submitter_id.
    
    Args:
        limit: Maximum results to return (1-100). Default 10.
        offset: Number of results to skip for pagination. Default 0.
        current_user: Automatically injected by get_current_user dependency
        
    Returns:
        RegistrationListResponse: Paginated list of user's registrations
        
    Status Codes:
        - 200 OK: Results returned (may be empty list)
        - 401 Unauthorized: Invalid or missing token
        
    Example:
        GET /registrations/my?limit=20&offset=0
        Authorization: Bearer <token>
        
        Response (200 OK):
        {
            "total": 5,
            "limit": 20,
            "offset": 0,
            "results": [
                {
                    "registration_id": "uuid",
                    "endpoint_url": "https://my-api.com",
                    "endpoint_name": "My MCP Server",
                    "status": "Approved",
                    "submitter_id": "current-user-uuid",
                    ...
                },
                ...
            ]
        }
        
    Frontend Usage:
        // React component to show user's registrations
        const MyRegistrations = () => {
            const [data, setData] = useState(null);
            
            useEffect(() => {
                fetch('/registrations/my', {
                    headers: { 'Authorization': `Bearer ${token}` }
                })
                .then(res => res.json())
                .then(setData);
            }, []);
            
            return (
                <div>
                    <h2>My Registrations ({data?.total})</h2>
                    {data?.results.map(reg => (
                        <div key={reg.registration_id}>
                            {reg.endpoint_name} - {reg.status}
                        </div>
                    ))}
                </div>
            );
        };
    """
    logger.debug(f"Get registrations for user {current_user.user_id}")
    
    try:
        async with get_db_connection() as conn:
            service = RegistrationService(conn)
            
            result = await service.get_registrations(
                submitter_id=current_user.user_id,
                limit=limit,
                offset=offset
            )
            
            logger.debug(
                f"Found {len(result['results'])} registrations for user "
                f"{current_user.user_id} (total: {result['total']})"
            )
            
            # Debug: Log first result if any
            if result['results']:
                first_reg = result['results'][0]
                logger.debug(f"First registration endpoint_url type: {type(first_reg.endpoint_url)}, value: {first_reg.endpoint_url}")
            
            return RegistrationListResponse(
                total=result["total"],
                limit=result["limit"],
                offset=result["offset"],
                results=[
                    RegistrationResponse(
                        registration_id=reg.registration_id,
                        endpoint_url=str(reg.endpoint_url),  # Convert HttpUrl to string
                        endpoint_name=reg.endpoint_name,
                        description=reg.description,
                        owner_contact=reg.owner_contact,
                        available_tools=reg.available_tools,
                        status=reg.status,
                        submitter_id=reg.submitter_id,
                        approver_id=reg.approver_id,
                        created_at=reg.created_at,
                        updated_at=reg.updated_at,
                        approved_at=reg.approved_at
                    )
                    for reg in result["results"]
                ]
            )
            
    except Exception as e:
        logger.error(f"Error retrieving user registrations: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{registration_id}", response_model=RegistrationResponse)
async def get_registration(
    registration_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Get registration by ID.
    
    Retrieves a single registration by its UUID. Any authenticated user
    can view any registration.
    
    Args:
        registration_id: UUID of the registration to retrieve
        current_user: Automatically injected by get_current_user dependency
        
    Returns:
        RegistrationResponse: Registration details
        
    Status Codes:
        - 200 OK: Registration found and returned
        - 401 Unauthorized: Invalid or missing token
        - 404 Not Found: Registration with specified ID does not exist
        
    Example:
        GET /registrations/abc-123-def-456
        Authorization: Bearer <token>
        
        Response (200 OK):
        {
            "registration_id": "abc-123-def-456",
            "endpoint_url": "https://api.example.com/mcp",
            "endpoint_name": "Example MCP Server",
            "description": "Production endpoint",
            "owner_contact": "admin@example.com",
            "available_tools": [...],
            "status": "Approved",
            "submitter_id": "user-uuid",
            "approver_id": "admin-uuid",
            "created_at": "2025-11-11T10:00:00Z",
            "updated_at": "2025-11-11T10:30:00Z",
            "approved_at": "2025-11-11T10:30:00Z"
        }
        
        Response (404 Not Found):
        {
            "detail": "Registration not found"
        }
    """
    logger.debug(f"Get registration {registration_id} requested by {current_user.user_id}")
    
    try:
        async with get_db_connection() as conn:
            service = RegistrationService(conn)
            registration = await service.get_registration_by_id(registration_id)
            
            if not registration:
                logger.warning(f"Registration not found: {registration_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Registration not found"
                )
            
            return RegistrationResponse(
                registration_id=registration.registration_id,
                endpoint_url=str(registration.endpoint_url),  # Convert HttpUrl to string
                endpoint_name=registration.endpoint_name,
                description=registration.description,
                owner_contact=registration.owner_contact,
                available_tools=registration.available_tools,
                status=registration.status,
                submitter_id=registration.submitter_id,
                approver_id=registration.approver_id,
                created_at=registration.created_at,
                updated_at=registration.updated_at,
                approved_at=registration.approved_at
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving registration {registration_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/by-url", response_model=RegistrationResponse)
async def get_registration_by_url(
    endpoint_url: str = Query(..., description="URL of the MCP endpoint to query"),
    current_user: User = Depends(get_current_user)
):
    """
    Get registration by endpoint URL (User Story 2: Programmatic Query).
    
    Queries registrations by exact endpoint_url match. This endpoint enables
    CI/CD pipelines and monitoring systems to check registration status
    programmatically without needing the registration_id.
    
    Args:
        endpoint_url: Full URL of the MCP endpoint (URL-encoded in query string)
        current_user: Automatically injected by get_current_user dependency
        
    Returns:
        RegistrationResponse: Registration details if found
        
    Status Codes:
        - 200 OK: Registration found and returned
        - 401 Unauthorized: Invalid or missing token
        - 404 Not Found: No registration found for the given URL
        
    Performance:
        - Query response time: <200ms (leverages unique index on endpoint_url)
        
    Example:
        GET /registrations/by-url?endpoint_url=https://api.example.com/mcp
        Authorization: Bearer <token>
        
        Response (200 OK):
        {
            "registration_id": "abc-123-def-456",
            "endpoint_url": "https://api.example.com/mcp",
            "endpoint_name": "Example MCP Server",
            "status": "Approved",
            "created_at": "2025-11-11T10:00:00Z",
            ...
        }
        
        Response (404 Not Found):
        {
            "detail": "No registration found for the given endpoint URL."
        }
        
    Use Cases (User Story 2 - US2):
        - CI/CD: Check if MCP endpoint registered/approved before deployment
        - Monitoring: Track registration status of production endpoints
        - Automation: Query approval status from scripts/tools
    """
    logger.debug(f"Get registration by URL requested: {endpoint_url} by {current_user.user_id}")
    
    try:
        async with get_db_connection() as conn:
            service = RegistrationService(conn)
            # T026: Call new get_registration_by_url method
            registration = await service.get_registration_by_url(endpoint_url)
            
            # T028: Return 404 if URL not found
            if not registration:
                logger.warning(f"Registration not found for URL: {endpoint_url}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No registration found for the given endpoint URL."
                )
            
            return RegistrationResponse(
                registration_id=registration.registration_id,
                endpoint_url=str(registration.endpoint_url),  # Convert HttpUrl to string
                endpoint_name=registration.endpoint_name,
                description=registration.description,
                owner_contact=registration.owner_contact,
                available_tools=registration.available_tools,
                status=registration.status,
                submitter_id=registration.submitter_id,
                approver_id=registration.approver_id,
                created_at=registration.created_at,
                updated_at=registration.updated_at,
                approved_at=registration.approved_at
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving registration by URL {endpoint_url}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.patch("/{registration_id}/status", response_model=RegistrationResponse)
async def update_registration_status(
    registration_id: UUID,
    request: UpdateStatusRequest,
    admin_user: User = Depends(require_admin)
):
    """
    Update registration status (admin only).
    
    Allows admins to approve or reject pending registrations. Sets:
    - status = 'Approved' or 'Rejected'
    - approver_id = admin user ID
    - approved_at = current timestamp
    
    Only registrations with status='Pending' can be updated.
    Once approved/rejected, status cannot be changed back to Pending.
    
    Args:
        registration_id: UUID of the registration to update
        request: UpdateStatusRequest with new status ('Approved' or 'Rejected')
        admin_user: Automatically injected by require_admin dependency
        
    Returns:
        RegistrationResponse: Updated registration
        
    Status Codes:
        - 200 OK: Status updated successfully
        - 400 Bad Request: Invalid status or registration not in Pending state
        - 401 Unauthorized: Invalid or missing token
        - 403 Forbidden: User is not an admin
        - 404 Not Found: Registration does not exist
        
    Example:
        PATCH /registrations/abc-123-def-456/status
        Authorization: Bearer <admin-token>
        Content-Type: application/json
        
        {
            "status": "Approved"
        }
        
        Response (200 OK):
        {
            "registration_id": "abc-123-def-456",
            "endpoint_url": "https://api.example.com/mcp",
            "endpoint_name": "Example MCP Server",
            "status": "Approved",
            "submitter_id": "user-uuid",
            "approver_id": "admin-uuid",
            "approved_at": "2025-11-11T10:30:00Z",
            ...
        }
        
        Response (403 Forbidden):
        {
            "detail": "Admin privileges required for this operation"
        }
        
        Response (400 Bad Request):
        {
            "detail": "Registration is not in Pending status or does not exist"
        }
        
    Admin Workflow:
        1. Admin lists pending registrations: GET /registrations?status=Pending
        2. Admin reviews registration details: GET /registrations/{id}
        3. Admin approves: PATCH /registrations/{id}/status {"status": "Approved"}
        4. OR Admin rejects: PATCH /registrations/{id}/status {"status": "Rejected", "reason": "..."}
        
    Status Transition Rules:
        - Pending → Approved ✓
        - Pending → Rejected ✓
        - Approved → Pending ✗
        - Rejected → Pending ✗
        - Approved → Rejected ✗
        - Rejected → Approved ✗
    """
    logger.info(
        f"Admin {admin_user.user_id} updating registration {registration_id} "
        f"status to {request.status.value}"
    )
    
    try:
        async with get_db_connection() as conn:
            service = RegistrationService(conn)
            
            registration = await service.update_registration_status(
                registration_id=registration_id,
                new_status=request.status,
                approver_id=admin_user.user_id,
                reason=request.reason
            )
            
            if not registration:
                logger.warning(
                    f"Failed to update registration {registration_id}: "
                    "not found or not in Pending status"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Registration is not in Pending status or does not exist"
                )
            
            logger.info(f"Registration {registration_id} status updated to {request.status.value}")
            
            return RegistrationResponse(
                registration_id=registration.registration_id,
                endpoint_url=str(registration.endpoint_url),  # Convert HttpUrl to string
                endpoint_name=registration.endpoint_name,
                description=registration.description,
                owner_contact=registration.owner_contact,
                available_tools=registration.available_tools,
                status=registration.status,
                submitter_id=registration.submitter_id,
                approver_id=registration.approver_id,
                created_at=registration.created_at,
                updated_at=registration.updated_at,
                approved_at=registration.approved_at
            )
            
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Invalid status update request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating registration status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{registration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_registration(
    registration_id: UUID,
    admin_user: User = Depends(require_admin)
):
    """
    Delete registration (admin only).
    
    Permanently removes a registration from the database. This operation
    cannot be undone. Consider using status='Rejected' instead for audit trail.
    
    Args:
        registration_id: UUID of the registration to delete
        admin_user: Automatically injected by require_admin dependency
        
    Returns:
        No content (204 status code)
        
    Status Codes:
        - 204 No Content: Registration deleted successfully
        - 401 Unauthorized: Invalid or missing token
        - 403 Forbidden: User is not an admin
        - 404 Not Found: Registration does not exist
        
    Example:
        DELETE /registrations/abc-123-def-456
        Authorization: Bearer <admin-token>
        
        Response: 204 No Content (empty body)
        
        Response (403 Forbidden):
        {
            "detail": "Admin privileges required for this operation"
        }
        
        Response (404 Not Found):
        {
            "detail": "Registration not found"
        }
        
    Security Notes:
        - Only admins can delete registrations
        - Delete is permanent - no soft delete mechanism
        - Consider using PATCH /status to Rejected for audit trail
        - Audit log entries (if implemented) are preserved
        
    Use Cases:
        - Remove duplicate/test registrations
        - Clean up spam entries
        - Remove registrations created in error
        
    Alternative:
        For preserving history, use status update instead:
        PATCH /registrations/{id}/status {"status": "Rejected"}
    """
    logger.info(f"Admin {admin_user.user_id} deleting registration {registration_id}")
    
    try:
        async with get_db_connection() as conn:
            service = RegistrationService(conn)
            
            # T036: Pass deleter_id for audit logging
            deleted = await service.delete_registration(registration_id, admin_user.user_id)
            
            if not deleted:
                logger.warning(f"Registration not found for deletion: {registration_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Registration not found"
                )
            
            logger.info(f"Registration {registration_id} deleted successfully")
            return None  # 204 No Content
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting registration {registration_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
