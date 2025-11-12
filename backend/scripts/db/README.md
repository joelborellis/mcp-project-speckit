# Database Setup Guide

This directory contains SQL scripts for initializing and managing the PostgreSQL database for the MCP Registry backend.

## Prerequisites

- PostgreSQL 14 or higher
- Database administrator credentials
- `psql` command-line tool or database client (e.g., Azure Data Studio, pgAdmin, DBeaver)

## Files

- `init_schema.sql` - Complete database schema with tables, indexes, constraints, and triggers

## Quick Start

### 1. Create Database

```bash
# Connect to PostgreSQL as admin
psql -U postgres

# Create database
CREATE DATABASE mcp_registry;

# Exit psql
\q
```

### 2. Run Schema Script

```bash
# Run init_schema.sql against the database
psql -U postgres -d mcp_registry -f init_schema.sql
```

### 3. Verify Installation

```bash
# Connect to database
psql -U postgres -d mcp_registry

# List tables
\dt

# Expected output:
#            List of relations
#  Schema |      Name       | Type  |  Owner   
# --------+-----------------+-------+----------
#  public | audit_log       | table | postgres
#  public | registrations   | table | postgres
#  public | users           | table | postgres

# List indexes
\di

# Exit
\q
```

## Detailed Setup Instructions

### Local Development (PostgreSQL)

#### Option 1: Using psql command line

```bash
# 1. Create database
psql -U postgres -c "CREATE DATABASE mcp_registry;"

# 2. Run schema script
psql -U postgres -d mcp_registry -f init_schema.sql

# 3. Verify
psql -U postgres -d mcp_registry -c "\dt"
```

#### Option 2: Using database client (Azure Data Studio, pgAdmin, etc.)

1. Connect to PostgreSQL server
2. Create new database named `mcp_registry`
3. Open `init_schema.sql` in the query editor
4. Execute the script
5. Verify tables were created

### Azure Database for PostgreSQL

#### Prerequisites

- Azure subscription
- Azure CLI installed (optional but recommended)

#### Option 1: Using Azure Portal

1. **Create Azure Database for PostgreSQL**:
   - Navigate to Azure Portal
   - Create new "Azure Database for PostgreSQL flexible server"
   - Configure server settings:
     - Server name: `mcp-registry-db-<unique-id>`
     - Location: Choose your region
     - PostgreSQL version: 14 or higher
     - Compute + storage: Choose appropriate tier (Start with Basic)
   - Set admin username and password
   - Configure networking (allow your IP address)
   - Create the server

2. **Configure Firewall**:
   - Go to server's "Networking" blade
   - Add firewall rule for your IP address
   - Or enable "Allow public access from any Azure service"

3. **Connect and Initialize**:
   ```bash
   # Get connection string from Azure Portal (Connection strings blade)
   psql "host=mcp-registry-db.postgres.database.azure.com port=5432 dbname=postgres user=adminuser password=yourpassword sslmode=require"
   
   # Create database
   CREATE DATABASE mcp_registry;
   \c mcp_registry
   
   # Run schema script
   \i init_schema.sql
   ```

#### Option 2: Using Azure CLI

```bash
# 1. Create resource group (if needed)
az group create --name mcp-registry-rg --location eastus

# 2. Create PostgreSQL server
az postgres flexible-server create \
  --resource-group mcp-registry-rg \
  --name mcp-registry-db \
  --location eastus \
  --admin-user mcpadmin \
  --admin-password <YourStrongPassword> \
  --sku-name Standard_B1ms \
  --storage-size 32 \
  --version 14

# 3. Configure firewall
az postgres flexible-server firewall-rule create \
  --resource-group mcp-registry-rg \
  --name mcp-registry-db \
  --rule-name AllowMyIP \
  --start-ip-address <YourIPAddress> \
  --end-ip-address <YourIPAddress>

# 4. Get connection string
az postgres flexible-server show-connection-string \
  --server-name mcp-registry-db \
  --admin-user mcpadmin \
  --admin-password <YourStrongPassword> \
  --database-name postgres

# 5. Connect and create database
psql "<connection-string>"
CREATE DATABASE mcp_registry;
\c mcp_registry
\i init_schema.sql
```

#### Option 3: Using Azure Data Studio

1. Install [Azure Data Studio](https://docs.microsoft.com/sql/azure-data-studio/)
2. Install PostgreSQL extension
3. Connect to your Azure PostgreSQL server
4. Create database `mcp_registry`
5. Open `init_schema.sql` and execute

## Database Schema Overview

### Tables

#### users
- Stores authenticated users from Microsoft Entra ID
- Tracks admin status based on group membership
- Primary key: `user_id` (UUID)
- Unique constraint: `entra_id`

#### registrations
- Stores MCP endpoint registrations
- Approval workflow: Pending → Approved/Rejected
- Primary key: `registration_id` (UUID)
- Unique constraint: `endpoint_url`
- Foreign keys: `submitter_id`, `approver_id` → `users.user_id`

#### audit_log
- Tracks changes to registrations (optional)
- Primary key: `log_id` (UUID)
- Foreign keys: `registration_id`, `user_id`

### Indexes

- `idx_users_entra_id` - Unique index on `users.entra_id`
- `idx_registrations_endpoint_url` - Unique index on `registrations.endpoint_url`
- `idx_registrations_status` - Index on `registrations.status` (for filtering)
- `idx_registrations_submitter_id` - Index on foreign key
- `idx_registrations_created_at` - Index for sorting by date
- `idx_audit_log_registration_id` - Index on foreign key
- `idx_audit_log_timestamp` - Index for time-based queries

### Triggers

- `users_updated_at_trigger` - Auto-update `updated_at` on users table
- `registrations_updated_at_trigger` - Auto-update `updated_at` on registrations table

## Verification Queries

Run these queries to verify the schema was created correctly:

```sql
-- Check tables
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Check indexes
SELECT indexname, tablename 
FROM pg_indexes 
WHERE schemaname = 'public' 
ORDER BY tablename, indexname;

-- Check constraints
SELECT constraint_name, table_name, constraint_type 
FROM information_schema.table_constraints 
WHERE table_schema = 'public' 
ORDER BY table_name, constraint_type;

-- Check foreign keys
SELECT
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE constraint_type = 'FOREIGN KEY';
```

## Sample Data (Development Only)

For development/testing, you can insert sample users:

```sql
-- Sample admin user
INSERT INTO users (entra_id, email, display_name, is_admin) 
VALUES ('00000000-0000-0000-0000-000000000000', 'admin@example.com', 'Admin User', TRUE)
ON CONFLICT (entra_id) DO NOTHING;

-- Sample regular user
INSERT INTO users (entra_id, email, display_name, is_admin) 
VALUES ('11111111-1111-1111-1111-111111111111', 'user@example.com', 'Regular User', FALSE)
ON CONFLICT (entra_id) DO NOTHING;
```

**Warning**: Never use sample data in production. Production users are created automatically on first login via Entra ID.

## Connection String Format

### Local PostgreSQL
```
postgresql://username:password@localhost:5432/mcp_registry
```

### Azure Database for PostgreSQL
```
postgresql://adminuser%40servername:password@servername.postgres.database.azure.com:5432/mcp_registry?sslmode=require
```

Note: For Azure, URL-encode the username (replace `@` with `%40`).

## Troubleshooting

### Connection Refused

```
psql: error: connection to server at "localhost" (127.0.0.1), port 5432 failed: Connection refused
```

**Solution**: Ensure PostgreSQL is running
```bash
# Check status (Linux)
sudo systemctl status postgresql

# Start service (Linux)
sudo systemctl start postgresql

# Windows: Check if service is running in Services app
```

### Authentication Failed

```
psql: error: connection to server failed: FATAL: password authentication failed
```

**Solution**: 
- Verify username and password
- Check `pg_hba.conf` configuration
- For Azure, ensure firewall rules allow your IP

### SSL Required (Azure)

```
psql: error: server does not support SSL, but SSL was required
```

**Solution**: Add `sslmode=require` to connection string
```bash
psql "host=server.postgres.database.azure.com sslmode=require ..."
```

### Permission Denied

```
ERROR: permission denied for table users
```

**Solution**: Ensure user has appropriate privileges
```sql
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_user;
```

## Migration Strategy

### Adding New Columns

```sql
-- Example: Add new column to registrations
ALTER TABLE registrations 
ADD COLUMN IF NOT EXISTS new_column_name TEXT;
```

### Adding New Indexes

```sql
-- Use CONCURRENTLY to avoid locking (PostgreSQL 11+)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_name 
ON table_name(column_name);
```

### Data Migrations

For data transformations, create separate migration scripts:
- Name format: `YYYYMMDD_description.sql`
- Example: `20251111_add_categories.sql`
- Keep migrations in version control
- Document each migration

## Backup and Restore

### Backup

```bash
# Full database backup
pg_dump -U postgres mcp_registry > mcp_registry_backup.sql

# Schema only
pg_dump -U postgres --schema-only mcp_registry > mcp_registry_schema.sql

# Data only
pg_dump -U postgres --data-only mcp_registry > mcp_registry_data.sql
```

### Restore

```bash
# Restore from backup
psql -U postgres -d mcp_registry < mcp_registry_backup.sql
```

### Azure Backup

Azure Database for PostgreSQL provides automated backups:
- Retention: 7-35 days (configurable)
- Point-in-time restore available
- Managed through Azure Portal

## Performance Tuning

### Monitor Slow Queries

```sql
-- Enable slow query logging
ALTER DATABASE mcp_registry SET log_min_duration_statement = 1000; -- Log queries > 1 second

-- Check slow queries
SELECT * FROM pg_stat_statements 
ORDER BY total_exec_time DESC 
LIMIT 10;
```

### Analyze Query Plans

```sql
EXPLAIN ANALYZE 
SELECT * FROM registrations WHERE status = 'Pending';
```

### Update Statistics

```sql
ANALYZE users;
ANALYZE registrations;
ANALYZE audit_log;
```

## Security Best Practices

1. **Use Strong Passwords**: Admin accounts should have complex passwords
2. **Restrict Network Access**: Configure firewall to allow only necessary IPs
3. **Enable SSL/TLS**: Always use encrypted connections (especially Azure)
4. **Principle of Least Privilege**: Grant minimum necessary permissions
5. **Regular Backups**: Automate backup schedule
6. **Monitor Logs**: Enable and review audit logs
7. **Keep Updated**: Apply security patches promptly

## Support

For database-related issues:
1. Check PostgreSQL logs
2. Verify connection string in `.env` file
3. Ensure database is accessible from application server
4. Review this README's troubleshooting section
5. Consult PostgreSQL documentation: https://www.postgresql.org/docs/

For Azure-specific issues:
- Azure PostgreSQL docs: https://docs.microsoft.com/azure/postgresql/
- Azure support portal: https://portal.azure.com
