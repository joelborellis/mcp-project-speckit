"""
Quick test script to diagnose PostgreSQL connection issues.
"""

import asyncio
import asyncpg
import socket
from urllib.parse import urlparse

DATABASE_URL = "postgresql://postgresadmin:407Brooks@mcp-registry-postgres.postgres.database.azure.com:5432/postgres"

async def test_connection():
    """Test database connection with detailed diagnostics."""
    
    # Parse the connection string
    parsed = urlparse(DATABASE_URL.replace("postgresql://", "postgres://"))
    host = parsed.hostname
    port = parsed.port or 5432
    
    print(f"Testing connection to: {host}:{port}")
    print("-" * 60)
    
    # Test 1: DNS Resolution
    print("\n1. DNS Resolution...")
    try:
        ip = socket.gethostbyname(host)
        print(f"   ✓ Resolved {host} to {ip}")
    except socket.gaierror as e:
        print(f"   ✗ DNS resolution failed: {e}")
        return
    
    # Test 2: TCP Connection
    print("\n2. TCP Connection...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"   ✓ Port {port} is reachable")
        else:
            print(f"   ✗ Port {port} is not reachable (firewall blocked?)")
            print(f"     Error code: {result}")
            return
    except Exception as e:
        print(f"   ✗ TCP connection failed: {e}")
        return
    
    # Test 3: PostgreSQL Connection
    print("\n3. PostgreSQL Connection...")
    try:
        conn = await asyncpg.connect(
            dsn=DATABASE_URL,
            timeout=10,
            ssl='require'  # Azure requires SSL
        )
        
        version = await conn.fetchval("SELECT version();")
        print(f"   ✓ Connected successfully!")
        print(f"   Database version: {version.split()[0]} {version.split()[1]}")
        
        await conn.close()
        print("\n✓ All tests passed!")
        
    except asyncpg.exceptions.InvalidPasswordError:
        print("   ✗ Invalid username or password")
    except asyncpg.exceptions.InvalidCatalogNameError:
        print("   ✗ Database does not exist")
    except Exception as e:
        print(f"   ✗ Connection failed: {e}")
        print(f"     Type: {type(e).__name__}")
    
    print("\n" + "-" * 60)

if __name__ == "__main__":
    print("PostgreSQL Connection Diagnostic Tool")
    print("=" * 60)
    asyncio.run(test_connection())
