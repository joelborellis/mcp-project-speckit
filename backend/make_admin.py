"""
Quick script to make a user an admin by email address.
Usage: python make_admin.py your-email@domain.com
"""
import asyncio
import asyncpg
import sys
from src.config import get_settings

async def make_admin(email: str):
    settings = get_settings()
    
    # Parse DATABASE_URL
    db_url = settings.database_url
    
    conn = await asyncpg.connect(db_url)
    
    try:
        # First, show current users
        print("\nCurrent users:")
        rows = await conn.fetch(
            "SELECT user_id, email, is_admin FROM users ORDER BY created_at DESC LIMIT 10"
        )
        for row in rows:
            admin_badge = "✓ ADMIN" if row['is_admin'] else ""
            print(f"  {row['email']} - {admin_badge}")
        
        # Update the specified user
        result = await conn.execute(
            "UPDATE users SET is_admin = true WHERE email = $1",
            email
        )
        
        if result == "UPDATE 1":
            print(f"\n✓ Successfully made {email} an admin!")
        else:
            print(f"\n✗ User with email {email} not found.")
            print("   Make sure the user has logged in at least once.")
        
        # Show updated users
        print("\nUpdated users:")
        rows = await conn.fetch(
            "SELECT user_id, email, is_admin FROM users ORDER BY created_at DESC LIMIT 10"
        )
        for row in rows:
            admin_badge = "✓ ADMIN" if row['is_admin'] else ""
            print(f"  {row['email']} - {admin_badge}")
            
    finally:
        await conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python make_admin.py your-email@domain.com")
        sys.exit(1)
    
    email = sys.argv[1]
    asyncio.run(make_admin(email))
