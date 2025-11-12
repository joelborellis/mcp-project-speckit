"""
Database connection module using asyncpg.

Manages PostgreSQL connection pool lifecycle with FastAPI.
"""

import asyncpg
import logging
from typing import Optional
from contextlib import asynccontextmanager

from config import settings

logger = logging.getLogger(__name__)

# Global connection pool
_pool: Optional[asyncpg.Pool] = None


async def get_pool() -> asyncpg.Pool:
    """
    Get the global connection pool.
    
    Returns:
        asyncpg.Pool: Active connection pool
        
    Raises:
        RuntimeError: If pool is not initialized
    """
    global _pool
    if _pool is None:
        raise RuntimeError(
            "Database connection pool not initialized. "
            "Call init_db_pool() during application startup."
        )
    return _pool


async def init_db_pool() -> None:
    """
    Initialize the database connection pool.
    
    Creates an asyncpg connection pool with configuration from settings.
    Should be called during application startup.
    
    Pool Configuration:
        - min_size: 10 connections (minimum pool size)
        - max_size: 20 connections (maximum pool size)
        - command_timeout: 60 seconds
        - max_queries: 50000 per connection before recycling
        - max_inactive_connection_lifetime: 300 seconds (5 minutes)
    
    Raises:
        Exception: If connection pool cannot be created
    """
    global _pool
    
    try:
        logger.info("Initializing database connection pool...")
        logger.info(f"Connecting to database: {settings.database_url.split('@')[-1]}")  # Log without credentials
        
        _pool = await asyncpg.create_pool(
            dsn=settings.database_url,
            min_size=10,
            max_size=20,
            command_timeout=60,
            max_queries=50000,
            max_inactive_connection_lifetime=300.0,
        )
        
        # Test connection
        async with _pool.acquire() as conn:
            version = await conn.fetchval("SELECT version();")
            logger.info(f"Database connection successful: {version.split()[0]} {version.split()[1]}")
            
        logger.info("Database connection pool initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database connection pool: {str(e)}")
        raise


async def close_db_pool() -> None:
    """
    Close the database connection pool.
    
    Gracefully closes all connections in the pool.
    Should be called during application shutdown.
    """
    global _pool
    
    if _pool is not None:
        logger.info("Closing database connection pool...")
        await _pool.close()
        _pool = None
        logger.info("Database connection pool closed")


@asynccontextmanager
async def get_db_connection():
    """
    Context manager for acquiring a database connection.
    
    Usage:
        async with get_db_connection() as conn:
            result = await conn.fetch("SELECT * FROM users")
    
    Yields:
        asyncpg.Connection: Database connection
    """
    pool = await get_pool()
    async with pool.acquire() as connection:
        yield connection


@asynccontextmanager
async def get_db_transaction():
    """
    Context manager for database transactions.
    
    Automatically commits on success and rolls back on error.
    
    Usage:
        async with get_db_transaction() as conn:
            await conn.execute("INSERT INTO users ...")
            await conn.execute("INSERT INTO registrations ...")
            # Automatically committed if no exception
    
    Yields:
        asyncpg.Connection: Database connection with active transaction
    """
    async with get_db_connection() as conn:
        async with conn.transaction():
            yield conn


async def check_db_health() -> dict:
    """
    Check database connectivity and health.
    
    Returns:
        dict: Health status with 'status' and 'details' keys
        
    Example:
        {
            "status": "healthy",
            "details": {
                "database": "connected",
                "version": "PostgreSQL 14.5"
            }
        }
    """
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            version = await conn.fetchval("SELECT version();")
            return {
                "status": "healthy",
                "details": {
                    "database": "connected",
                    "version": version.split()[0] + " " + version.split()[1]
                }
            }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "details": {
                "database": "disconnected",
                "error": str(e)
            }
        }


# Utility functions for common query patterns

async def fetch_one(query: str, *args) -> Optional[dict]:
    """
    Fetch a single row from the database.
    
    Args:
        query: SQL query string
        *args: Query parameters
        
    Returns:
        dict: Row as dictionary, or None if not found
    """
    async with get_db_connection() as conn:
        row = await conn.fetchrow(query, *args)
        return dict(row) if row else None


async def fetch_all(query: str, *args) -> list[dict]:
    """
    Fetch all matching rows from the database.
    
    Args:
        query: SQL query string
        *args: Query parameters
        
    Returns:
        list[dict]: List of rows as dictionaries
    """
    async with get_db_connection() as conn:
        rows = await conn.fetch(query, *args)
        return [dict(row) for row in rows]


async def execute(query: str, *args) -> str:
    """
    Execute a query that doesn't return rows (INSERT, UPDATE, DELETE).
    
    Args:
        query: SQL query string
        *args: Query parameters
        
    Returns:
        str: Query execution status (e.g., "INSERT 0 1")
    """
    async with get_db_connection() as conn:
        return await conn.execute(query, *args)


async def execute_many(query: str, args_list: list) -> None:
    """
    Execute a query multiple times with different parameters.
    
    Args:
        query: SQL query string
        args_list: List of parameter tuples
    """
    async with get_db_connection() as conn:
        await conn.executemany(query, args_list)
