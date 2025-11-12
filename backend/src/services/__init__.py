"""
Services Package

This package provides business logic layer services for the MCP Registry Backend.
Services handle all business operations and database interactions, keeping route
handlers thin and focused on HTTP request/response handling.

Modules:
    user_service: User management (get_or_create_user, get_user_by_id, check_admin_status)
    registration_service: Registration CRUD operations (create, list, get, update, delete)

Example Usage:
    from services import UserService, RegistrationService
    from database import get_db_connection
    
    async with get_db_connection() as conn:
        user_service = UserService(conn)
        reg_service = RegistrationService(conn)
        
        user = await user_service.get_user_by_id(user_id)
        registrations = await reg_service.get_registrations(status="Pending")

Architecture:
    - Service classes accept database connection in constructor
    - All methods are async (use await)
    - Services encapsulate business logic and SQL operations
    - Route handlers should not contain SQL - delegate to services
"""

from services.user_service import UserService
from services.registration_service import RegistrationService

__all__ = ["UserService", "RegistrationService"]
