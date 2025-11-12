"""
Registration Service

This module provides business logic for MCP server registration management.
It handles CRUD operations for registrations, including creation, retrieval,
status updates (approve/reject), and deletion.

Key Features:
- Create registrations with status='Pending' and submitter tracking
- List registrations with filtering (status, submitter_id, search) and pagination
- Retrieve individual registrations by ID
- Update registration status (admin approval/rejection workflow)
- Delete registrations (admin only)
- Duplicate endpoint_url detection (409 Conflict)

Example Usage:
    from services.registration_service import RegistrationService
    from database import get_db_connection
    from models import RegistrationCreate
    
    async with get_db_connection() as conn:
        service = RegistrationService(conn)
        
        # Create registration
        reg_create = RegistrationCreate(
            endpoint_url="https://api.example.com/mcp",
            endpoint_name="Example MCP Server",
            description="Production MCP endpoint",
            owner_contact="admin@example.com",
            available_tools=[{"name": "search", "description": "Search tool"}]
        )
        registration = await service.create_registration(reg_create, submitter_id)
        
        # List with filters
        result = await service.get_registrations(
            status="Pending",
            search="example",
            limit=10,
            offset=0
        )
        
        # Update status (admin approval)
        updated = await service.update_registration_status(
            registration_id=reg_id,
            new_status="Approved",
            approver_id=admin_user_id
        )

Database Operations:
- create_registration: INSERT with duplicate endpoint_url detection
- get_registrations: SELECT with WHERE filters, ILIKE search, pagination
- get_registration_by_id: SELECT by primary key
- update_registration_status: UPDATE status, approver_id, approved_at
- delete_registration: DELETE by primary key

Security Notes:
- Only admins can approve/reject/delete registrations
- Submitters can only view their own registrations (enforced in routes)
- Status transitions must be from Pending to Approved/Rejected only
"""

import json
import logging
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
import asyncpg

from models import Registration, RegistrationCreate, RegistrationStatus

logger = logging.getLogger(__name__)


class RegistrationService:
    """
    Service layer for MCP server registration management.
    
    This service handles all registration-related business logic including:
    - Creating new registrations
    - Listing registrations with filters and pagination
    - Retrieving registrations by ID
    - Updating registration status (approval workflow)
    - Deleting registrations
    
    Attributes:
        conn: AsyncPG database connection
        
    Example:
        async with get_db_connection() as conn:
            service = RegistrationService(conn)
            registrations = await service.get_registrations(status="Pending")
    """
    
    def __init__(self, conn: asyncpg.Connection):
        """
        Initialize RegistrationService with database connection.
        
        Args:
            conn: AsyncPG database connection
            
        Example:
            service = RegistrationService(conn)
        """
        self.conn = conn
    
    async def create_registration(
        self,
        registration_create: RegistrationCreate,
        submitter_id: UUID
    ) -> Registration:
        """
        Create a new registration with status='Pending'.
        
        Inserts a new registration record with the provided data and sets:
        - status = 'Pending' (initial state)
        - submitter_id = current authenticated user
        - approver_id = NULL (not approved yet)
        - approved_at = NULL (not approved yet)
        
        Args:
            registration_create: RegistrationCreate model with endpoint details
            submitter_id: UUID of the user creating the registration
            
        Returns:
            Registration: Created registration model
            
        Raises:
            asyncpg.UniqueViolationError: If endpoint_url already exists (409 Conflict)
            Exception: If database operation fails
            
        Example:
            reg_create = RegistrationCreate(
                endpoint_url="https://api.example.com/mcp",
                endpoint_name="Example MCP Server",
                description="Production endpoint",
                owner_contact="admin@example.com",
                available_tools=[
                    {"name": "search", "description": "Search tool"},
                    {"name": "analyze", "description": "Analysis tool"}
                ]
            )
            
            try:
                registration = await service.create_registration(
                    reg_create, 
                    submitter_id=current_user.user_id
                )
                # registration.status == "Pending"
                # registration.registration_id == UUID
            except asyncpg.UniqueViolationError:
                # Handle 409 Conflict - endpoint_url already registered
                print("Endpoint URL already registered")
                
        SQL Operation:
            INSERT INTO registrations (
                endpoint_url, endpoint_name, description, owner_contact,
                available_tools, status, submitter_id
            ) VALUES ($1, $2, $3, $4, $5, 'Pending', $6)
            RETURNING *
            
        Validation:
            - endpoint_url must be unique (enforced by database constraint)
            - endpoint_name must be 3-200 characters (enforced by CHECK constraint)
            - owner_contact must be valid email (validated by Pydantic schema)
            - available_tools must be valid JSONB array (validated by Pydantic)
        """
        try:
            query = """
                INSERT INTO registrations (
                    endpoint_url, endpoint_name, description, owner_contact,
                    available_tools, status, submitter_id
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING registration_id, endpoint_url, endpoint_name, description,
                          owner_contact, available_tools, status, submitter_id,
                          approver_id, created_at, updated_at, approved_at
            """
            
            # Convert available_tools list to JSON string for asyncpg
            tools_json = json.dumps(registration_create.available_tools)
            
            row = await self.conn.fetchrow(
                query,
                str(registration_create.endpoint_url),
                registration_create.endpoint_name,
                registration_create.description,
                registration_create.owner_contact,
                tools_json,  # JSONB as JSON string
                RegistrationStatus.PENDING.value,
                submitter_id
            )
            
            registration = Registration(
                registration_id=row["registration_id"],
                endpoint_url=row["endpoint_url"],
                endpoint_name=row["endpoint_name"],
                description=row["description"],
                owner_contact=row["owner_contact"],
                available_tools=row["available_tools"],
                status=RegistrationStatus(row["status"]),
                submitter_id=row["submitter_id"],
                approver_id=row["approver_id"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                approved_at=row["approved_at"]
            )
            
            logger.info(
                f"Registration created: {registration.registration_id} "
                f"({registration.endpoint_url}) by user {submitter_id}"
            )
            return registration
            
        except asyncpg.UniqueViolationError as e:
            logger.warning(f"Duplicate endpoint_url: {registration_create.endpoint_url}")
            raise  # Let route handler convert to 409 Conflict
        except Exception as e:
            logger.error(f"Error creating registration: {str(e)}")
            raise
    
    async def get_registrations(
        self,
        status: Optional[str] = None,
        submitter_id: Optional[UUID] = None,
        search: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Retrieve registrations with optional filters and pagination.
        
        Returns paginated list of registrations matching the provided filters.
        Results are ordered by created_at DESC (newest first).
        
        Args:
            status: Filter by status ('Pending', 'Approved', 'Rejected'). Optional.
            submitter_id: Filter by submitter user ID. Optional.
            search: Search term for endpoint_name or owner_contact (case-insensitive). Optional.
            limit: Maximum number of results to return (1-100). Default 10.
            offset: Number of results to skip for pagination. Default 0.
            
        Returns:
            Dict with keys:
                - total (int): Total count of matching registrations
                - limit (int): Limit applied to this query
                - offset (int): Offset applied to this query
                - results (List[Registration]): List of registration models
                
        Raises:
            Exception: If database operation fails
            
        Example:
            # Get all pending registrations
            result = await service.get_registrations(status="Pending")
            print(f"Found {result['total']} pending registrations")
            for reg in result['results']:
                print(f"  - {reg.endpoint_name}: {reg.endpoint_url}")
            
            # Get user's own registrations
            result = await service.get_registrations(
                submitter_id=current_user.user_id,
                limit=20,
                offset=0
            )
            
            # Search with pagination
            result = await service.get_registrations(
                search="openai",
                limit=10,
                offset=10  # Page 2
            )
            
        SQL Operations:
            COUNT query:
                SELECT COUNT(*) FROM registrations
                WHERE [status = $1] AND [submitter_id = $2] 
                  AND [endpoint_name ILIKE $3 OR owner_contact ILIKE $3]
            
            SELECT query:
                SELECT * FROM registrations
                WHERE [filters...]
                ORDER BY created_at DESC
                LIMIT $n OFFSET $m
                
        Search Behavior:
            - Search term is matched against endpoint_name and owner_contact
            - Case-insensitive (ILIKE operator)
            - Partial matches supported (e.g., "openai" matches "OpenAI MCP Server")
            - Search wraps term in % wildcards: ILIKE '%search%'
        """
        try:
            # Build WHERE clause dynamically based on provided filters
            where_conditions = []
            params = []
            param_index = 1
            
            if status:
                where_conditions.append(f"status = ${param_index}")
                params.append(status)
                param_index += 1
            
            if submitter_id:
                where_conditions.append(f"submitter_id = ${param_index}")
                params.append(submitter_id)
                param_index += 1
            
            if search:
                where_conditions.append(
                    f"(endpoint_name ILIKE ${param_index} OR owner_contact ILIKE ${param_index})"
                )
                params.append(f"%{search}%")
                param_index += 1
            
            where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            # Count total matching records
            count_query = f"SELECT COUNT(*) FROM registrations {where_clause}"
            total = await self.conn.fetchval(count_query, *params)
            
            # Fetch paginated results
            select_query = f"""
                SELECT registration_id, endpoint_url, endpoint_name, description,
                       owner_contact, available_tools, status, submitter_id,
                       approver_id, created_at, updated_at, approved_at
                FROM registrations
                {where_clause}
                ORDER BY created_at DESC
                LIMIT ${param_index} OFFSET ${param_index + 1}
            """
            params.extend([limit, offset])
            
            rows = await self.conn.fetch(select_query, *params)
            
            registrations = [
                Registration(
                    registration_id=row["registration_id"],
                    endpoint_url=row["endpoint_url"],
                    endpoint_name=row["endpoint_name"],
                    description=row["description"],
                    owner_contact=row["owner_contact"],
                    available_tools=row["available_tools"],
                    status=RegistrationStatus(row["status"]),
                    submitter_id=row["submitter_id"],
                    approver_id=row["approver_id"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    approved_at=row["approved_at"]
                )
                for row in rows
            ]
            
            logger.debug(
                f"Retrieved {len(registrations)} registrations "
                f"(total: {total}, limit: {limit}, offset: {offset})"
            )
            
            return {
                "total": total,
                "limit": limit,
                "offset": offset,
                "results": registrations
            }
            
        except Exception as e:
            logger.error(f"Error retrieving registrations: {str(e)}")
            raise
    
    async def get_registration_by_id(
        self,
        registration_id: UUID
    ) -> Optional[Registration]:
        """
        Retrieve a registration by registration_id.
        
        Args:
            registration_id: UUID of the registration to retrieve
            
        Returns:
            Registration: Registration model if found, None if not found
            
        Raises:
            Exception: If database operation fails
            
        Example:
            registration = await service.get_registration_by_id(reg_id)
            if registration:
                print(f"Found: {registration.endpoint_name}")
                print(f"Status: {registration.status.value}")
            else:
                print("Registration not found")
                
        SQL Operation:
            SELECT * FROM registrations WHERE registration_id = $1
            
        Notes:
            - Returns None if registration not found (does not raise exception)
            - Use this method to check if a registration_id is valid
            - All registration fields are populated in returned model
        """
        try:
            query = """
                SELECT registration_id, endpoint_url, endpoint_name, description,
                       owner_contact, available_tools, status, submitter_id,
                       approver_id, created_at, updated_at, approved_at
                FROM registrations
                WHERE registration_id = $1
            """
            
            row = await self.conn.fetchrow(query, registration_id)
            
            if not row:
                logger.debug(f"Registration not found: {registration_id}")
                return None
            
            registration = Registration(
                registration_id=row["registration_id"],
                endpoint_url=row["endpoint_url"],
                endpoint_name=row["endpoint_name"],
                description=row["description"],
                owner_contact=row["owner_contact"],
                available_tools=row["available_tools"],
                status=RegistrationStatus(row["status"]),
                submitter_id=row["submitter_id"],
                approver_id=row["approver_id"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                approved_at=row["approved_at"]
            )
            
            logger.debug(f"Registration retrieved: {registration.registration_id}")
            return registration
            
        except Exception as e:
            logger.error(f"Error retrieving registration {registration_id}: {str(e)}")
            raise
    
    async def update_registration_status(
        self,
        registration_id: UUID,
        new_status: RegistrationStatus,
        approver_id: UUID,
        reason: Optional[str] = None
    ) -> Optional[Registration]:
        """
        Update registration status for admin approval/rejection workflow.
        
        Updates the status field to 'Approved' or 'Rejected' and sets:
        - approver_id = admin user who approved/rejected
        - approved_at = current timestamp
        - updated_at = current timestamp (via trigger)
        
        Status Transition Rules:
        - Only 'Pending' registrations can be approved/rejected
        - Cannot transition from 'Approved' or 'Rejected' back to 'Pending'
        - Cannot change status if already approved/rejected
        
        Args:
            registration_id: UUID of the registration to update
            new_status: RegistrationStatus.APPROVED or RegistrationStatus.REJECTED
            approver_id: UUID of the admin user approving/rejecting
            reason: Optional reason for rejection (not stored in database)
            
        Returns:
            Registration: Updated registration model if found, None if not found
            
        Raises:
            ValueError: If attempting to set status to Pending
            Exception: If database operation fails
            
        Example:
            # Admin approves registration
            updated = await service.update_registration_status(
                registration_id=reg_id,
                new_status=RegistrationStatus.APPROVED,
                approver_id=admin_user.user_id
            )
            
            # Admin rejects registration
            updated = await service.update_registration_status(
                registration_id=reg_id,
                new_status=RegistrationStatus.REJECTED,
                approver_id=admin_user.user_id,
                reason="Duplicate endpoint"
            )
            
            if updated:
                print(f"Status updated to {updated.status.value}")
            else:
                print("Registration not found")
                
        SQL Operation:
            UPDATE registrations
            SET status = $1, approver_id = $2, approved_at = CURRENT_TIMESTAMP
            WHERE registration_id = $3 AND status = 'Pending'
            RETURNING *
            
        Security Notes:
            - Only admins can call this method (enforced in route layer)
            - Status validation prevents transitioning from Pending to Pending
            - Approval workflow is one-way: Pending → Approved/Rejected
            - Use DELETE operation to remove unwanted registrations
        """
        if new_status == RegistrationStatus.PENDING:
            raise ValueError("Cannot set status to Pending")
        
        try:
            # Only update if current status is Pending
            query = """
                UPDATE registrations
                SET status = $1, approver_id = $2, approved_at = CURRENT_TIMESTAMP
                WHERE registration_id = $3 AND status = 'Pending'
                RETURNING registration_id, endpoint_url, endpoint_name, description,
                          owner_contact, available_tools, status, submitter_id,
                          approver_id, created_at, updated_at, approved_at
            """
            
            row = await self.conn.fetchrow(
                query,
                new_status.value,
                approver_id,
                registration_id
            )
            
            if not row:
                logger.warning(
                    f"Failed to update registration {registration_id}: "
                    "either not found or not in Pending status"
                )
                return None
            
            registration = Registration(
                registration_id=row["registration_id"],
                endpoint_url=row["endpoint_url"],
                endpoint_name=row["endpoint_name"],
                description=row["description"],
                owner_contact=row["owner_contact"],
                available_tools=row["available_tools"],
                status=RegistrationStatus(row["status"]),
                submitter_id=row["submitter_id"],
                approver_id=row["approver_id"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                approved_at=row["approved_at"]
            )
            
            logger.info(
                f"Registration {registration.registration_id} status updated to "
                f"{new_status.value} by admin {approver_id}"
            )
            return registration
            
        except Exception as e:
            logger.error(f"Error updating registration status: {str(e)}")
            raise
    
    async def delete_registration(self, registration_id: UUID) -> bool:
        """
        Delete a registration (admin only).
        
        Permanently removes the registration record from the database.
        This operation cannot be undone.
        
        Args:
            registration_id: UUID of the registration to delete
            
        Returns:
            bool: True if registration was deleted, False if not found
            
        Raises:
            Exception: If database operation fails
            
        Example:
            # Admin deletes registration
            deleted = await service.delete_registration(reg_id)
            if deleted:
                print("Registration deleted successfully")
            else:
                print("Registration not found")
                
        SQL Operation:
            DELETE FROM registrations WHERE registration_id = $1
            
        Security Notes:
            - Only admins can call this method (enforced in route layer)
            - Delete is permanent - no soft delete mechanism
            - Consider using status='Rejected' instead of deletion for audit trail
            - Audit log entries (if implemented) are not deleted
        """
        try:
            query = "DELETE FROM registrations WHERE registration_id = $1"
            
            result = await self.conn.execute(query, registration_id)
            
            # Extract number of deleted rows from result string "DELETE N"
            deleted_count = int(result.split()[-1])
            
            if deleted_count > 0:
                logger.info(f"Registration deleted: {registration_id}")
                return True
            else:
                logger.debug(f"Registration not found for deletion: {registration_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting registration {registration_id}: {str(e)}")
            raise
