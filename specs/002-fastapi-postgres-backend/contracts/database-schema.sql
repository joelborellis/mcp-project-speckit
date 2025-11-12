-- FastAPI Backend Database Schema
-- Feature: 002-fastapi-postgres-backend
-- Database: PostgreSQL (Azure Database for PostgreSQL)
-- Date: 2025-11-11
--
-- This script is IDEMPOTENT and can be safely run multiple times.
-- It creates all tables, indexes, and constraints needed for the MCP Registry backend.

-- Enable UUID generation (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- TABLE: users
-- =============================================================================
-- Stores authenticated users from Microsoft Entra ID

CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entra_id TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    display_name TEXT,
    is_admin BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Indexes for users table
CREATE INDEX IF NOT EXISTS idx_users_entra_id ON users(entra_id);

-- Comments for documentation
COMMENT ON TABLE users IS 'Authenticated users from Microsoft Entra ID';
COMMENT ON COLUMN users.user_id IS 'Internal unique identifier';
COMMENT ON COLUMN users.entra_id IS 'External ID from Microsoft Entra ID (subject claim from JWT)';
COMMENT ON COLUMN users.email IS 'User email address from Entra ID';
COMMENT ON COLUMN users.display_name IS 'User display name from Entra ID';
COMMENT ON COLUMN users.is_admin IS 'Admin privilege flag (determined by Entra ID group membership)';

-- =============================================================================
-- TABLE: registrations
-- =============================================================================
-- Stores MCP endpoint registrations with approval workflow

CREATE TABLE IF NOT EXISTS registrations (
    registration_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    endpoint_url TEXT UNIQUE NOT NULL,
    endpoint_name TEXT NOT NULL,
    description TEXT,
    owner_contact TEXT NOT NULL,
    available_tools JSONB NOT NULL DEFAULT '[]'::jsonb,
    status TEXT NOT NULL CHECK (status IN ('Pending', 'Approved', 'Rejected')),
    submitter_id UUID NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
    approver_id UUID REFERENCES users(user_id) ON DELETE RESTRICT,
    submitted_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    
    -- Ensure approval fields are consistent with status
    CONSTRAINT check_pending_approval CHECK (
        (status = 'Pending' AND approver_id IS NULL AND approved_at IS NULL) OR
        (status IN ('Approved', 'Rejected') AND approver_id IS NOT NULL AND approved_at IS NOT NULL)
    )
);

-- Indexes for registrations table
CREATE INDEX IF NOT EXISTS idx_registrations_endpoint_url ON registrations(endpoint_url);
CREATE INDEX IF NOT EXISTS idx_registrations_status ON registrations(status);
CREATE INDEX IF NOT EXISTS idx_registrations_submitter_id ON registrations(submitter_id);
CREATE INDEX IF NOT EXISTS idx_registrations_created_at ON registrations(created_at DESC);

-- Optional: GIN index for JSONB queries on available_tools (can add later if needed)
-- CREATE INDEX IF NOT EXISTS idx_registrations_available_tools ON registrations USING GIN (available_tools);

-- Comments for documentation
COMMENT ON TABLE registrations IS 'MCP endpoint registrations with approval workflow';
COMMENT ON COLUMN registrations.registration_id IS 'Internal unique identifier';
COMMENT ON COLUMN registrations.endpoint_url IS 'MCP endpoint URL (must be unique)';
COMMENT ON COLUMN registrations.endpoint_name IS 'Human-readable name for the endpoint';
COMMENT ON COLUMN registrations.available_tools IS 'JSONB array of available tools/capabilities';
COMMENT ON COLUMN registrations.status IS 'Current approval status: Pending, Approved, or Rejected';
COMMENT ON COLUMN registrations.submitter_id IS 'User who submitted the registration';
COMMENT ON COLUMN registrations.approver_id IS 'Admin who approved/rejected (NULL if pending)';

-- =============================================================================
-- TABLE: audit_log (OPTIONAL - can be enabled later)
-- =============================================================================
-- Tracks changes to registrations for compliance and troubleshooting

CREATE TABLE IF NOT EXISTS audit_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    registration_id UUID NOT NULL REFERENCES registrations(registration_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
    action TEXT NOT NULL CHECK (action IN ('Created', 'Approved', 'Rejected', 'Updated', 'Deleted')),
    previous_status TEXT,
    new_status TEXT,
    metadata JSONB,
    timestamp TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Indexes for audit_log table
CREATE INDEX IF NOT EXISTS idx_audit_log_registration_id ON audit_log(registration_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp DESC);

-- Comments for documentation
COMMENT ON TABLE audit_log IS 'Audit trail of all changes to registrations';
COMMENT ON COLUMN audit_log.action IS 'Type of action: Created, Approved, Rejected, Updated, Deleted';
COMMENT ON COLUMN audit_log.metadata IS 'Additional context (e.g., reason for rejection, fields changed)';

-- =============================================================================
-- TRIGGERS (Optional - for automatic updated_at management)
-- =============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for users table
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for registrations table
DROP TRIGGER IF EXISTS update_registrations_updated_at ON registrations;
CREATE TRIGGER update_registrations_updated_at
    BEFORE UPDATE ON registrations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- VERIFICATION QUERIES (run after schema creation to verify)
-- =============================================================================

-- List all tables
-- SELECT tablename FROM pg_tables WHERE schemaname = 'public';

-- List all indexes
-- SELECT indexname, tablename FROM pg_indexes WHERE schemaname = 'public';

-- Verify foreign keys
-- SELECT conname, contype FROM pg_constraint WHERE contype = 'f';

-- =============================================================================
-- SAMPLE DATA (Development only - comment out for production)
-- =============================================================================

-- Example: Insert a test admin user
-- INSERT INTO users (entra_id, email, display_name, is_admin)
-- VALUES ('test-admin-entra-id', 'admin@example.com', 'Test Admin', true)
-- ON CONFLICT (entra_id) DO NOTHING;

-- Example: Insert a test regular user
-- INSERT INTO users (entra_id, email, display_name, is_admin)
-- VALUES ('test-user-entra-id', 'user@example.com', 'Test User', false)
-- ON CONFLICT (entra_id) DO NOTHING;

-- =============================================================================
-- END OF SCHEMA
-- =============================================================================
