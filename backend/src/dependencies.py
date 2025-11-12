"""
FastAPI Dependencies

This module provides FastAPI dependency functions for authentication and authorization.
Dependencies are used as function parameters in route handlers to automatically
validate tokens, fetch/create user records, and check admin permissions.

Key Dependencies:
- get_current_user: Validates token, creates/updates user in DB, returns User model
- require_admin: Extends get_current_user, checks is_admin flag, raises 403 if not admin

Example Usage in Routes:
    from fastapi import APIRouter, Depends
    from dependencies import get_current_user, require_admin
    from models import User
    
    router = APIRouter()
    
    @router.get("/users/me")
    async def get_my_profile(current_user: User = Depends(get_current_user)):
        return current_user
    
    @router.delete("/registrations/{id}")
    async def delete_registration(
        id: str,
        admin_user: User = Depends(require_admin)
    ):
        # Only admins can reach this code
        return {"deleted": id}

Token Format:
    Authorization header must be in format: "Bearer <jwt_token>"
    Example: "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."

Error Responses:
    - 401 Unauthorized: Missing or invalid token
    - 403 Forbidden: User is not an admin (for require_admin dependency)
    - 500 Internal Server Error: Database or validation errors

Security Notes:
- All protected routes must use get_current_user or require_admin dependency
- Never bypass token validation in production
- Admin checks are performed on every request (no caching)
"""

import logging
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from auth import validate_token, extract_user_claims
from config import get_settings
from database import get_db_connection
from models import User, UserCreate
from services.user_service import UserService

logger = logging.getLogger(__name__)

# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    FastAPI dependency to get the current authenticated user.
    
    Workflow:
    1. Extract Bearer token from Authorization header
    2. Validate token using Entra ID JWKS
    3. Extract user claims (entra_id, email, display_name)
    4. Get or create user record in database (upsert pattern)
    5. Return User model
    
    This dependency automatically creates user records on first login,
    and updates existing records if email or display_name changed.
    
    Args:
        credentials: Automatically injected by FastAPI from Authorization header
        
    Returns:
        User: Current authenticated user model
        
    Raises:
        HTTPException 401: If token is missing, invalid, or expired
        HTTPException 500: If database operation fails
        
    Example Usage:
        @router.get("/users/me")
        async def get_profile(current_user: User = Depends(get_current_user)):
            return {
                "user_id": current_user.user_id,
                "email": current_user.email,
                "is_admin": current_user.is_admin
            }
            
    Security Notes:
        - Token validation is performed on every request (no caching)
        - User record is upserted to keep database in sync with Entra ID
        - Admin status (is_admin) comes from database, not token
    """
    token = credentials.credentials
    
    try:
        # Validate token and extract claims
        logger.debug("Validating Entra ID token")
        claims = validate_token(token)
        user_claims = extract_user_claims(claims)
        
        # Extract user information
        entra_id = user_claims["entra_id"]
        email = user_claims["email"]
        display_name = user_claims.get("display_name")
        
        logger.debug(f"Token validated for user: {entra_id} ({email})")
        
        # Check if user is in admin group (from token claims)
        groups = claims.get("groups", [])
        admin_group_id = get_settings().entra_admin_group_id
        is_admin = admin_group_id in groups if admin_group_id else False
        
        if is_admin:
            logger.info(f"User {email} is in admin group {admin_group_id}")
        
        # Get or create user in database
        async with get_db_connection() as conn:
            user_service = UserService(conn)
            
            # Create UserCreate model for upsert
            user_create = UserCreate(
                entra_id=entra_id,
                email=email,
                display_name=display_name
            )
            
            # Upsert user (INSERT ON CONFLICT DO UPDATE)
            user = await user_service.get_or_create_user(user_create)
            
            # Sync admin status from token to database if it has changed
            if user.is_admin != is_admin:
                logger.info(f"Syncing admin status for {email}: {user.is_admin} -> {is_admin}")
                await user_service.update_admin_status(user.user_id, is_admin)
                user.is_admin = is_admin  # Update the model
            
            logger.info(f"User authenticated: {user.user_id} ({user.email}), is_admin={user.is_admin}")
            return user
            
    except ValueError as e:
        # Token validation failed
        logger.warning(f"Token validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        # Database or unexpected error
        logger.error(f"Error in get_current_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication"
        )


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    FastAPI dependency to require admin privileges.
    
    This dependency extends get_current_user by additionally checking
    the is_admin flag in the user record. If the user is not an admin,
    a 403 Forbidden error is raised.
    
    Use this dependency for admin-only routes such as:
    - Approving/rejecting registrations (PATCH /registrations/{id}/status)
    - Deleting registrations (DELETE /registrations/{id})
    - Viewing all users (GET /users)
    
    Args:
        current_user: Automatically injected by get_current_user dependency
        
    Returns:
        User: Current authenticated admin user model
        
    Raises:
        HTTPException 403: If user is not an admin
        HTTPException 401: If token validation fails (from get_current_user)
        
    Example Usage:
        @router.patch("/registrations/{registration_id}/status")
        async def update_status(
            registration_id: str,
            admin_user: User = Depends(require_admin)
        ):
            # Only admins can reach this code
            # admin_user.is_admin is guaranteed to be True
            return {"updated_by": admin_user.user_id}
            
    Admin Management:
        - Admin status is stored in the users.is_admin database column
        - Admins can be assigned manually via SQL or Entra ID group membership
        - Use Setup-EntraIDAdminGroup.ps1 script to configure admin group
        - Admin checks are performed on every request (no caching)
        
    Security Notes:
        - Admin flag is checked from database, not token claims
        - No caching - admin status is verified on every request
        - Revoked admin access takes effect immediately
    """
    if not current_user.is_admin:
        logger.warning(
            f"Access denied: User {current_user.user_id} ({current_user.email}) "
            f"attempted admin action without admin privileges"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required for this operation"
        )
    
    logger.debug(f"Admin access granted for user: {current_user.user_id} ({current_user.email})")
    return current_user
