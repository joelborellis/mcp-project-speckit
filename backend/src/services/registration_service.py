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
from models.audit_log import AuditAction
from services.audit_service import AuditService

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
        self.audit_service = AuditService()
    
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
            # Debug: Check what we received
            logger.info(f"create_registration called with type: {type(registration_create)}")
            
            # If it's a dict or has model_dump, convert to ensure we have clean data
            if isinstance(registration_create, dict):
                reg_data = registration_create
            elif hasattr(registration_create, 'model_dump'):
                reg_data = registration_create.model_dump()
            else:
                reg_data = registration_create
            
            logger.info(f"reg_data type: {type(reg_data)}, keys: {reg_data.keys() if isinstance(reg_data, dict) else 'not a dict'}")
            
            # Start transaction for atomic operation + audit logging
            async with self.conn.transaction():
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
                
                # Extract values from dict
                endpoint_url_str = str(reg_data.get("endpoint_url") if isinstance(reg_data, dict) else reg_data["endpoint_url"])
                endpoint_name_str = reg_data.get("endpoint_name") if isinstance(reg_data, dict) else reg_data["endpoint_name"]
                description_str = reg_data.get("description") if isinstance(reg_data, dict) else reg_data["description"]
                owner_contact_str = reg_data.get("owner_contact") if isinstance(reg_data, dict) else reg_data["owner_contact"]
                available_tools_list = reg_data.get("available_tools", []) if isinstance(reg_data, dict) else reg_data["available_tools"]
                status_str = RegistrationStatus.PENDING.value
                submitter_id_uuid = submitter_id if isinstance(submitter_id, UUID) else UUID(str(submitter_id))
                
                # Convert available_tools list to JSON string for asyncpg
                tools_json = json.dumps(available_tools_list)
                
                # Log parameters for debugging
                logger.info(f"About to call fetchrow with 7 params:")
                logger.info(f"  $1 endpoint_url: {endpoint_url_str} (type: {type(endpoint_url_str)})")
                logger.info(f"  $2 endpoint_name: {endpoint_name_str} (type: {type(endpoint_name_str)})")
                logger.info(f"  $3 description: {description_str} (type: {type(description_str)})")
                logger.info(f"  $4 owner_contact: {owner_contact_str} (type: {type(owner_contact_str)})")
                logger.info(f"  $5 tools_json: {tools_json[:100]}... (type: {type(tools_json)})")
                logger.info(f"  $6 status: {status_str} (type: {type(status_str)})")
                logger.info(f"  $7 submitter_id: {submitter_id_uuid} (type: {type(submitter_id_uuid)})")
                
                # Try calling with explicit inline values to rule out variable issues
                try:
                    row = await self.conn.fetchrow(
                        query,
                        endpoint_url_str,  # $1
                        endpoint_name_str,  # $2
                        description_str,  # $3
                        owner_contact_str,  # $4
                        tools_json,  # $5
                        status_str,  # $6
                        submitter_id_uuid  # $7
                    )
                except Exception as fetch_error:
                    logger.error(f"fetchrow exception: {type(fetch_error).__name__}: {fetch_error}")
                    logger.error(f"Query was: {query}")
                    raise
                
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
                
                # Log audit entry within transaction (T011: log 'Created' action)
                metadata = {
                    "endpoint_url": str(registration.endpoint_url),
                    "endpoint_name": registration.endpoint_name,
                    "owner_contact": registration.owner_contact,
                    "available_tools_count": len(registration.available_tools)
                }
                await self.audit_service.log_action(
                    connection=self.conn,
                    registration_id=registration.registration_id,
                    user_id=submitter_id,
                    action=AuditAction.CREATED,
                    previous_status=None,
                    new_status=RegistrationStatus.PENDING.value,
                    metadata=metadata
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
    
    async def get_registration_by_url(
        self,
        endpoint_url: str
    ) -> Optional[Registration]:
        """
        Retrieve a registration by endpoint_url (User Story 2: Programmatic Query).
        
        Queries registrations by exact endpoint_url match. This method enables
        CI/CD pipelines and monitoring systems to check registration status
        programmatically.
        
        Args:
            endpoint_url: Full URL of the MCP endpoint (e.g., "https://api.example.com/mcp")
            
        Returns:
            Registration: Registration model if found, None if not found
            
        Raises:
            Exception: If database operation fails
            
        Example:
            registration = await service.get_registration_by_url("https://api.example.com/mcp")
            if registration:
                print(f"Found: {registration.endpoint_name}")
                print(f"Status: {registration.status.value}")
            else:
                print("Registration not found for this URL")
                
        SQL Operation:
            SELECT * FROM registrations WHERE endpoint_url = $1
            
        Notes:
            - Returns None if URL not found (does not raise exception)
            - Uses unique index on endpoint_url for fast query (<200ms)
            - URL comparison is case-sensitive and exact match
            - T026: Implementation for User Story 2 - Query API
        """
        try:
            query = """
                SELECT registration_id, endpoint_url, endpoint_name, description,
                       owner_contact, available_tools, status, submitter_id,
                       approver_id, created_at, updated_at, approved_at
                FROM registrations
                WHERE endpoint_url = $1
            """
            
            row = await self.conn.fetchrow(query, endpoint_url)
            
            if not row:
                logger.debug(f"Registration not found for URL: {endpoint_url}")
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
            
            logger.debug(f"Registration retrieved by URL: {registration.registration_id}")
            return registration
            
        except Exception as e:
            logger.error(f"Error retrieving registration by URL {endpoint_url}: {str(e)}")
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
            # Start transaction for atomic operation + audit logging
            async with self.conn.transaction():
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
                
                # Log audit entry within transaction (T012: log 'Approved'/'Rejected' action)
                audit_action = (
                    AuditAction.APPROVED if new_status == RegistrationStatus.APPROVED
                    else AuditAction.REJECTED
                )
                metadata = {
                    "approver_id": str(approver_id),
                    "reason": reason if reason else None
                }
                await self.audit_service.log_action(
                    connection=self.conn,
                    registration_id=registration.registration_id,
                    user_id=approver_id,
                    action=audit_action,
                    previous_status=RegistrationStatus.PENDING.value,
                    new_status=new_status.value,
                    metadata=metadata
                )
                
                logger.info(
                    f"Registration {registration.registration_id} status updated to "
                    f"{new_status.value} by admin {approver_id}"
                )
                return registration
            
        except Exception as e:
            logger.error(f"Error updating registration status: {str(e)}")
            raise
    
    async def delete_registration(
        self,
        registration_id: UUID,
        deleter_id: UUID
    ) -> bool:
        """
        Delete a registration (admin only) with audit logging (T036).
        
        Permanently removes the registration record from the database after
        creating an audit log entry. This ensures compliance tracking even
        after deletion (FR-023: audit logs retained after registration deleted).
        
        Args:
            registration_id: UUID of the registration to delete
            deleter_id: UUID of the admin user performing deletion
            
        Returns:
            bool: True if registration was deleted, False if not found
            
        Raises:
            Exception: If database operation fails
            
        Example:
            # Admin deletes registration
            deleted = await service.delete_registration(reg_id, admin_user.user_id)
            if deleted:
                print("Registration deleted successfully")
            else:
                print("Registration not found")
                
        SQL Operations:
            1. SELECT registration details (for audit metadata)
            2. INSERT INTO audit_log (action='Deleted')
            3. DELETE FROM registrations
            
        Security Notes:
            - Only admins can call this method (enforced in route layer)
            - Delete is permanent - no soft delete mechanism
            - Consider using status='Rejected' instead of deletion for audit trail
            - Audit log entries are preserved (FK constraint is NO ACTION - T037)
        """
        try:
            # Start transaction for atomic operation + audit logging
            async with self.conn.transaction():
                # T036: Get registration details before deletion for audit metadata
                get_query = """
                    SELECT registration_id, endpoint_url, endpoint_name, status,
                           submitter_id, approver_id
                    FROM registrations
                    WHERE registration_id = $1
                """
                
                row = await self.conn.fetchrow(get_query, registration_id)
                
                if not row:
                    logger.debug(f"Registration not found for deletion: {registration_id}")
                    return False
                
                # T036: Create audit log entry BEFORE deletion
                metadata = {
                    "endpoint_url": row["endpoint_url"],
                    "endpoint_name": row["endpoint_name"],
                    "previous_status": row["status"],
                    "submitter_id": str(row["submitter_id"]),
                    "approver_id": str(row["approver_id"]) if row["approver_id"] else None,
                    "deleted_by": str(deleter_id)
                }
                
                await self.audit_service.log_action(
                    connection=self.conn,
                    registration_id=registration_id,
                    user_id=deleter_id,
                    action=AuditAction.DELETED,
                    previous_status=row["status"],
                    new_status=None,  # No new status after deletion
                    metadata=metadata
                )
                
                # Now delete the registration
                delete_query = "DELETE FROM registrations WHERE registration_id = $1"
                result = await self.conn.execute(delete_query, registration_id)
                
                # Extract number of deleted rows from result string "DELETE N"
                deleted_count = int(result.split()[-1])
                
                if deleted_count > 0:
                    logger.info(f"Registration deleted: {registration_id} by admin {deleter_id}")
                    return True
                else:
                    logger.warning(f"Registration delete failed: {registration_id}")
                    return False
                
        except Exception as e:
            logger.error(f"Error deleting registration {registration_id}: {str(e)}")
            raise
