"""
Users Router

This module provides user management endpoints for the MCP Registry Backend.
User records are automatically created/updated from Entra ID authentication tokens.

Endpoints:
    POST /users: Create/update user from current auth token (auto-creates on first login)
    GET /users/me: Get current authenticated user's profile
    GET /users/{user_id}: Get user by ID

Authentication:
    All endpoints require valid Entra ID Bearer token in Authorization header.
    Format: Authorization: Bearer <jwt_token>

Example Usage:
    # Get current user profile
    curl -H "Authorization: Bearer <token>" http://localhost:8000/users/me
    
    # Get user by ID
    curl -H "Authorization: Bearer <token>" http://localhost:8000/users/{user_id}

Response Schema:
    {
        "user_id": "uuid",
        "entra_id": "string",
        "email": "string",
        "display_name": "string | null",
        "is_admin": boolean,
        "created_at": "datetime",
        "updated_at": "datetime"
    }

Security Notes:
- All endpoints require authentication (get_current_user dependency)
- Users can only view their own profile or other users by ID (no list endpoint)
- Admin status is stored in database, not derived from token
- User records sync automatically on each authenticated request
"""

import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from models import User
from dependencies import get_current_user
from services import UserService
from database import get_db_connection
from schemas.user import UserResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_user(current_user: User = Depends(get_current_user)):
    """
    Create or update user from current authentication token.
    
    This endpoint is automatically called by the get_current_user dependency,
    so explicit POST requests are optional. The dependency handles user
    upsert (INSERT ON CONFLICT DO UPDATE) on every authenticated request.
    
    Use this endpoint to:
    - Explicitly create user record on first login
    - Verify user creation/update succeeded
    - Get user profile after authentication
    
    Args:
        current_user: Automatically injected by get_current_user dependency
        
    Returns:
        UserResponse: Created or updated user profile
        
    Status Codes:
        - 201 Created: User was created (first login)
        - 200 OK: User already existed and was updated (subsequent logins)
        - 401 Unauthorized: Invalid or missing token
        
    Example:
        POST /users
        Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
        
        Response (201 Created):
        {
            "user_id": "abc-123-def-456",
            "entra_id": "user-entra-id",
            "email": "user@example.com",
            "display_name": "John Doe",
            "is_admin": false,
            "created_at": "2025-11-11T10:30:00Z",
            "updated_at": "2025-11-11T10:30:00Z"
        }
        
    Notes:
        - User creation is automatic - no need to explicitly call this endpoint
        - User email and display_name are synced from Entra ID on each request
        - is_admin flag is NOT updated automatically (must be set via SQL or admin script)
        - Status code differentiates creation (201) vs update (200)
    """
    logger.info(f"User upserted via POST: {current_user.user_id} ({current_user.email})")
    
    # Determine status code: 201 if created recently, 200 if updated
    # Check if created_at and updated_at are very close (within 1 second)
    time_diff = (current_user.updated_at - current_user.created_at).total_seconds()
    status_code = status.HTTP_201_CREATED if time_diff < 1 else status.HTTP_200_OK
    
    return UserResponse(
        user_id=current_user.user_id,
        entra_id=current_user.entra_id,
        email=current_user.email,
        display_name=current_user.display_name,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's profile.
    
    Returns the profile of the user making the request based on the
    Bearer token in the Authorization header. This is the most common
    endpoint for frontend applications to fetch user information.
    
    Args:
        current_user: Automatically injected by get_current_user dependency
        
    Returns:
        UserResponse: Current user's profile
        
    Status Codes:
        - 200 OK: Profile retrieved successfully
        - 401 Unauthorized: Invalid or missing token
        
    Example:
        GET /users/me
        Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
        
        Response (200 OK):
        {
            "user_id": "abc-123-def-456",
            "entra_id": "user-entra-id",
            "email": "user@example.com",
            "display_name": "John Doe",
            "is_admin": false,
            "created_at": "2025-11-11T10:00:00Z",
            "updated_at": "2025-11-11T10:30:00Z"
        }
        
    Frontend Usage:
        // React example
        const response = await fetch('/users/me', {
            headers: {
                'Authorization': `Bearer ${msalToken}`
            }
        });
        const user = await response.json();
        
        // Check admin status
        if (user.is_admin) {
            // Show admin UI
        }
        
    Notes:
        - Most commonly used user endpoint
        - User data is always fresh (synced from Entra ID on request)
        - Use this endpoint to check is_admin flag for UI rendering
        - No user_id parameter needed (derived from token)
    """
    logger.debug(f"Get profile for user: {current_user.user_id} ({current_user.email})")
    
    return UserResponse(
        user_id=current_user.user_id,
        entra_id=current_user.entra_id,
        email=current_user.email,
        display_name=current_user.display_name,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    Get user profile by user_id.
    
    Allows authenticated users to view other users' profiles by UUID.
    Useful for displaying submitter/approver information on registrations.
    
    Args:
        user_id: UUID of the user to retrieve
        current_user: Automatically injected by get_current_user dependency (for auth)
        
    Returns:
        UserResponse: User profile for the specified user_id
        
    Status Codes:
        - 200 OK: User found and returned
        - 401 Unauthorized: Invalid or missing token
        - 404 Not Found: User with specified user_id does not exist
        
    Example:
        GET /users/abc-123-def-456
        Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
        
        Response (200 OK):
        {
            "user_id": "abc-123-def-456",
            "entra_id": "other-user-entra-id",
            "email": "other@example.com",
            "display_name": "Jane Smith",
            "is_admin": true,
            "created_at": "2025-11-01T10:00:00Z",
            "updated_at": "2025-11-10T15:30:00Z"
        }
        
        Response (404 Not Found):
        {
            "detail": "User not found"
        }
        
    Frontend Usage:
        // Display submitter info on registration detail page
        const registration = await getRegistration(regId);
        const submitter = await fetch(`/users/${registration.submitter_id}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
    Security Notes:
        - Requires authentication (cannot view users without being logged in)
        - Any authenticated user can view any other user's profile
        - No sensitive data exposed (only public profile fields)
        - Useful for displaying registration submitter/approver names
    """
    logger.debug(f"Get user {user_id} requested by {current_user.user_id}")
    
    async with get_db_connection() as conn:
        user_service = UserService(conn)
        user = await user_service.get_user_by_id(user_id)
        
        if not user:
            logger.warning(f"User not found: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            user_id=user.user_id,
            entra_id=user.entra_id,
            email=user.email,
            display_name=user.display_name,
            is_admin=user.is_admin,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
