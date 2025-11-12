"""
User Service

This module provides business logic for user management operations.
It handles user creation/updates from Entra ID authentication and
user retrieval operations.

Key Features:
- Upsert pattern (INSERT ON CONFLICT) for syncing Entra ID users to database
- Admin status management from Entra ID group membership
- User lookup by user_id
- Error handling for not found and database errors

Example Usage:
    from services.user_service import UserService
    from database import get_db_connection
    from models import UserCreate
    
    async with get_db_connection() as conn:
        user_service = UserService(conn)
        
        # Create/update user from Entra ID
        user_create = UserCreate(
            entra_id="abc-123-def-456",
            email="user@example.com",
            display_name="John Doe"
        )
        user = await user_service.get_or_create_user(user_create)
        
        # Get user by ID
        user = await user_service.get_user_by_id(user_id)
        
        # Check admin status
        is_admin = await user_service.check_admin_status(user_id)

Database Operations:
- get_or_create_user: INSERT ON CONFLICT DO UPDATE (upsert pattern)
- get_user_by_id: SELECT by primary key
- check_admin_status: SELECT is_admin flag

Security Notes:
- Admin status stored in database, not derived from token
- User records automatically updated on each login
- Entra ID is source of truth for email and display_name
"""

import logging
from typing import Optional
from uuid import UUID
import asyncpg

from models import User, UserCreate

logger = logging.getLogger(__name__)


class UserService:
    """
    Service layer for user management operations.
    
    This service handles all user-related business logic including:
    - Creating/updating users from Entra ID authentication
    - Retrieving users by ID
    - Checking admin status
    
    Attributes:
        conn: AsyncPG database connection
        
    Example:
        async with get_db_connection() as conn:
            service = UserService(conn)
            user = await service.get_user_by_id(user_id)
    """
    
    def __init__(self, conn: asyncpg.Connection):
        """
        Initialize UserService with database connection.
        
        Args:
            conn: AsyncPG database connection
            
        Example:
            service = UserService(conn)
        """
        self.conn = conn
    
    async def get_or_create_user(self, user_create: UserCreate) -> User:
        """
        Create a new user or update existing user (upsert pattern).
        
        Uses INSERT ON CONFLICT DO UPDATE to sync user data from Entra ID.
        If user with entra_id already exists, updates email and display_name.
        If user doesn't exist, creates new record with is_admin=False by default.
        
        The is_admin flag is NOT updated by this method - it must be managed
        separately through admin group sync or manual SQL updates.
        
        Args:
            user_create: UserCreate model with entra_id, email, display_name
            
        Returns:
            User: Created or updated user model with all fields
            
        Raises:
            Exception: If database operation fails
            
        Example:
            user_create = UserCreate(
                entra_id="abc-123-def-456",
                email="user@example.com",
                display_name="John Doe"
            )
            user = await service.get_or_create_user(user_create)
            
            # user.user_id will be UUID (new or existing)
            # user.is_admin preserves existing value or defaults to False
            
        SQL Operation:
            INSERT INTO users (entra_id, email, display_name)
            VALUES ($1, $2, $3)
            ON CONFLICT (entra_id) DO UPDATE
            SET email = EXCLUDED.email,
                display_name = EXCLUDED.display_name,
                updated_at = CURRENT_TIMESTAMP
            RETURNING *
            
        Security Notes:
            - is_admin flag is NOT updated by this method
            - Entra ID is source of truth for email and display_name
            - User records are automatically synced on each login
        """
        try:
            query = """
                INSERT INTO users (entra_id, email, display_name)
                VALUES ($1, $2, $3)
                ON CONFLICT (entra_id) DO UPDATE
                SET email = EXCLUDED.email,
                    display_name = EXCLUDED.display_name,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING user_id, entra_id, email, display_name, is_admin, 
                          created_at, updated_at
            """
            
            row = await self.conn.fetchrow(
                query,
                user_create.entra_id,
                user_create.email,
                user_create.display_name
            )
            
            user = User(
                user_id=row["user_id"],
                entra_id=row["entra_id"],
                email=row["email"],
                display_name=row["display_name"],
                is_admin=row["is_admin"],
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
            
            logger.info(f"User upserted: {user.user_id} ({user.email})")
            return user
            
        except Exception as e:
            logger.error(f"Error upserting user: {str(e)}")
            raise
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Retrieve a user by user_id.
        
        Args:
            user_id: UUID of the user to retrieve
            
        Returns:
            User: User model if found, None if not found
            
        Raises:
            Exception: If database operation fails
            
        Example:
            user = await service.get_user_by_id(user_id)
            if user:
                print(f"Found user: {user.email}")
            else:
                print("User not found")
                
        SQL Operation:
            SELECT * FROM users WHERE user_id = $1
            
        Notes:
            - Returns None if user not found (does not raise exception)
            - Use this method to check if a user_id is valid
            - All user fields are populated in returned User model
        """
        try:
            query = """
                SELECT user_id, entra_id, email, display_name, is_admin,
                       created_at, updated_at
                FROM users
                WHERE user_id = $1
            """
            
            row = await self.conn.fetchrow(query, user_id)
            
            if not row:
                logger.debug(f"User not found: {user_id}")
                return None
            
            user = User(
                user_id=row["user_id"],
                entra_id=row["entra_id"],
                email=row["email"],
                display_name=row["display_name"],
                is_admin=row["is_admin"],
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
            
            logger.debug(f"User retrieved: {user.user_id} ({user.email})")
            return user
            
        except Exception as e:
            logger.error(f"Error retrieving user {user_id}: {str(e)}")
            raise
    
    async def check_admin_status(self, user_id: UUID) -> bool:
        """
        Check if a user has admin privileges.
        
        Queries the is_admin flag from the database. This flag can be set:
        - Manually via SQL: UPDATE users SET is_admin = TRUE WHERE user_id = '...'
        - Via Entra ID group sync (future enhancement)
        - Via admin management script: Setup-EntraIDAdminGroup.ps1
        
        Args:
            user_id: UUID of the user to check
            
        Returns:
            bool: True if user is admin, False otherwise (including if user not found)
            
        Raises:
            Exception: If database operation fails
            
        Example:
            is_admin = await service.check_admin_status(user_id)
            if is_admin:
                print("User has admin privileges")
            else:
                print("User does not have admin privileges")
                
        SQL Operation:
            SELECT is_admin FROM users WHERE user_id = $1
            
        Admin Management:
            To grant admin access:
                UPDATE users SET is_admin = TRUE 
                WHERE entra_id = 'user-entra-id';
            
            To revoke admin access:
                UPDATE users SET is_admin = FALSE 
                WHERE entra_id = 'user-entra-id';
                
        Security Notes:
            - Admin status is not cached - checked on every request
            - Returns False if user not found (safe default)
            - Admin revocation takes effect immediately
        """
        try:
            query = "SELECT is_admin FROM users WHERE user_id = $1"
            
            row = await self.conn.fetchrow(query, user_id)
            
            if not row:
                logger.debug(f"User not found when checking admin status: {user_id}")
                return False
            
            is_admin = row["is_admin"]
            logger.debug(f"Admin status for user {user_id}: {is_admin}")
            
            return is_admin
            
        except Exception as e:
            logger.error(f"Error checking admin status for user {user_id}: {str(e)}")
            raise
    
    async def update_admin_status(self, user_id: UUID, is_admin: bool) -> None:
        """
        Update a user's admin status.
        
        This method is called automatically during authentication to sync
        admin status from Entra ID group membership to the database.
        
        Args:
            user_id: UUID of the user to update
            is_admin: New admin status (True for admin, False for regular user)
            
        Raises:
            Exception: If database operation fails
            
        Example:
            # Grant admin privileges
            await service.update_admin_status(user_id, True)
            
            # Revoke admin privileges
            await service.update_admin_status(user_id, False)
            
        SQL Operation:
            UPDATE users 
            SET is_admin = $1, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = $2
            
        Notes:
            - Called automatically when user logs in and group membership has changed
            - Admin status changes take effect immediately
            - Does not raise exception if user not found (idempotent)
        """
        try:
            query = """
                UPDATE users 
                SET is_admin = $1, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = $2
            """
            
            await self.conn.execute(query, is_admin, user_id)
            
            logger.info(f"Updated admin status for user {user_id}: is_admin={is_admin}")
            
        except Exception as e:
            logger.error(f"Error updating admin status for user {user_id}: {str(e)}")
            raise
