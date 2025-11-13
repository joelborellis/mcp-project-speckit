"""
Audit Service: Tracks all changes to registrations for compliance and troubleshooting.

This service provides two main operations:
1. log_action() - Create audit log entries for registration modifications
2. query_logs() - Query audit logs with filters for compliance reporting

All audit logging is atomic - it occurs within the same database transaction
as the operation being logged.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

import asyncpg

from models.audit_log import AuditAction


class AuditService:
    """Service for creating and querying audit log entries."""
    
    def __init__(self):
        """
        Initialize the audit service.
        
        Note: This service operates on database connections passed to its methods,
        not on a connection pool.
        """
        pass
    
    async def log_action(
        self,
        connection: asyncpg.Connection,
        registration_id: UUID,
        user_id: UUID,
        action: AuditAction,
        previous_status: Optional[str] = None,
        new_status: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> UUID:
        """
        Create an audit log entry for a registration modification.
        
        This method MUST be called within an existing database transaction.
        The connection parameter should be from an active transaction context.
        
        Args:
            connection: Active database connection within a transaction
            registration_id: UUID of the registration being modified
            user_id: UUID of the user performing the action
            action: Type of action (Created, Approved, Rejected, Updated, Deleted)
            previous_status: Status before the change (None for Created action)
            new_status: Status after the change
            metadata: Additional context (JSONB) - field changes, reasons, etc.
        
        Returns:
            UUID of the created audit log entry
        
        Example:
            async with db_pool.acquire() as conn:
                async with conn.transaction():
                    # Perform registration modification
                    await conn.execute(...)
                    
                    # Log the action in the same transaction
                    log_id = await audit_service.log_action(
                        connection=conn,
                        registration_id=reg_id,
                        user_id=user_id,
                        action=AuditAction.APPROVED,
                        previous_status="Pending",
                        new_status="Approved",
                        metadata={"reason": "Meets security requirements"}
                    )
        """
        query = """
            INSERT INTO audit_log (
                registration_id,
                user_id,
                action,
                previous_status,
                new_status,
                metadata,
                timestamp
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING log_id
        """
        
        log_id = await connection.fetchval(
            query,
            registration_id,
            user_id,
            action.value,
            previous_status,
            new_status,
            metadata,
            datetime.utcnow()
        )
        
        return log_id
    
    async def query_logs(
        self,
        connection: asyncpg.Connection,
        registration_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        action: Optional[AuditAction] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[dict], int]:
        """
        Query audit logs with filters and pagination.
        
        Returns audit log entries in reverse chronological order (newest first).
        All filter parameters are optional - omit to query all logs.
        
        Args:
            connection: Active database connection
            registration_id: Filter by specific registration (optional)
            user_id: Filter by user who performed action (optional)
            action: Filter by action type (optional)
            from_date: Filter by timestamp >= from_date (optional)
            to_date: Filter by timestamp <= to_date (optional)
            limit: Maximum number of results (default 50, max 200)
            offset: Number of results to skip for pagination (default 0)
        
        Returns:
            Tuple of (list of audit log dicts, total count matching filters)
        
        Raises:
            ValueError: If date range is invalid (end before start)
        """
        # Validate date range
        if from_date and to_date and to_date < from_date:
            raise ValueError("Invalid date range: end date must be after start date")
        
        # Enforce max limit
        limit = min(limit, 200)
        
        # Build dynamic query with filters
        where_clauses = []
        params = []
        param_index = 1
        
        if registration_id:
            where_clauses.append(f"registration_id = ${param_index}")
            params.append(registration_id)
            param_index += 1
        
        if user_id:
            where_clauses.append(f"user_id = ${param_index}")
            params.append(user_id)
            param_index += 1
        
        if action:
            where_clauses.append(f"action = ${param_index}")
            params.append(action.value)
            param_index += 1
        
        if from_date:
            where_clauses.append(f"timestamp >= ${param_index}")
            params.append(from_date)
            param_index += 1
        
        if to_date:
            where_clauses.append(f"timestamp <= ${param_index}")
            params.append(to_date)
            param_index += 1
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "TRUE"
        
        # Count total matching records
        count_query = f"SELECT COUNT(*) FROM audit_log WHERE {where_sql}"
        
        # Query audit logs with pagination
        query = f"""
            SELECT 
                log_id,
                registration_id,
                user_id,
                action,
                previous_status,
                new_status,
                metadata,
                timestamp
            FROM audit_log
            WHERE {where_sql}
            ORDER BY timestamp DESC
            LIMIT ${param_index} OFFSET ${param_index + 1}
        """
        
        # Get total count
        total = await connection.fetchval(count_query, *params)
        
        # Get paginated results
        rows = await connection.fetch(query, *params, limit, offset)
        
        # Convert rows to dicts
        results = [dict(row) for row in rows]
        
        return results, total

