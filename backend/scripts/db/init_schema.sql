-- ============================================================================
-- MCP Registry Database Schema
-- ============================================================================
-- PostgreSQL 14+ required
-- Idempotent script - safe to run multiple times
--
-- Tables:
--   1. users - Authenticated users from Microsoft Entra ID
--   2. registrations - MCP endpoint registrations with approval workflow
--   3. audit_log - Change tracking for compliance (optional)
--
-- Features:
--   - UUID primary keys
--   - Automatic timestamp management via triggers
--   - Foreign key constraints for referential integrity
--   - Unique constraints to prevent duplicates
--   - CHECK constraints for data validation
--   - Indexes for query performance
-- ============================================================================

-- Note: gen_random_uuid() is available by default in PostgreSQL 13+
-- No need to install uuid-ossp extension in Azure PostgreSQL

-- ============================================================================
-- Table: users
-- ============================================================================
-- Stores authenticated users from Microsoft Entra ID
-- Tracks admin status based on Entra ID group membership

CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entra_id TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL,
    display_name TEXT,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for fast lookups during authentication
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_entra_id ON users(entra_id);

-- Comments for documentation
COMMENT ON TABLE users IS 'Authenticated users from Microsoft Entra ID';
COMMENT ON COLUMN users.user_id IS 'Internal unique identifier';
COMMENT ON COLUMN users.entra_id IS 'External ID from Microsoft Entra ID (subject claim from JWT)';
COMMENT ON COLUMN users.email IS 'User email address from Entra ID';
COMMENT ON COLUMN users.display_name IS 'User display name from Entra ID (nullable)';
COMMENT ON COLUMN users.is_admin IS 'Admin privilege flag (determined by Entra ID group membership)';
COMMENT ON COLUMN users.created_at IS 'Record creation timestamp';
COMMENT ON COLUMN users.updated_at IS 'Last update timestamp';

-- ============================================================================
-- Table: registrations
-- ============================================================================
-- Stores MCP endpoint registrations with metadata and approval workflow

CREATE TABLE IF NOT EXISTS registrations (
    registration_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    endpoint_url TEXT NOT NULL UNIQUE,
    endpoint_name TEXT NOT NULL CHECK (char_length(endpoint_name) >= 3 AND char_length(endpoint_name) <= 200),
    description TEXT,
    owner_contact TEXT NOT NULL,
    available_tools JSONB NOT NULL DEFAULT '[]'::jsonb,
    status TEXT NOT NULL CHECK (status IN ('Pending', 'Approved', 'Rejected')) DEFAULT 'Pending',
    submitter_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    approver_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Consistency constraint: approver_id and approved_at must both be NULL or both be NOT NULL
    CONSTRAINT registration_approval_consistency 
        CHECK (
            (status = 'Pending' AND approver_id IS NULL AND approved_at IS NULL) OR
            (status IN ('Approved', 'Rejected') AND approver_id IS NOT NULL AND approved_at IS NOT NULL)
        )
);

-- Indexes for performance
CREATE UNIQUE INDEX IF NOT EXISTS idx_registrations_endpoint_url ON registrations(endpoint_url);
CREATE INDEX IF NOT EXISTS idx_registrations_status ON registrations(status);
CREATE INDEX IF NOT EXISTS idx_registrations_submitter_id ON registrations(submitter_id);
CREATE INDEX IF NOT EXISTS idx_registrations_created_at ON registrations(created_at DESC);

-- Comments for documentation
COMMENT ON TABLE registrations IS 'MCP endpoint registrations with approval workflow';
COMMENT ON COLUMN registrations.registration_id IS 'Internal unique identifier';
COMMENT ON COLUMN registrations.endpoint_url IS 'MCP endpoint URL (must be unique)';
COMMENT ON COLUMN registrations.endpoint_name IS 'Human-readable name (3-200 characters)';
COMMENT ON COLUMN registrations.description IS 'Optional description';
COMMENT ON COLUMN registrations.owner_contact IS 'Contact information for endpoint owner';
COMMENT ON COLUMN registrations.available_tools IS 'Array of available tools (JSONB format)';
COMMENT ON COLUMN registrations.status IS 'Approval status: Pending, Approved, or Rejected';
COMMENT ON COLUMN registrations.submitter_id IS 'User who submitted the registration';
COMMENT ON COLUMN registrations.approver_id IS 'Admin who approved/rejected (NULL if pending)';
COMMENT ON COLUMN registrations.submitted_at IS 'When registration was submitted';
COMMENT ON COLUMN registrations.approved_at IS 'When registration was approved/rejected (NULL if pending)';
COMMENT ON COLUMN registrations.created_at IS 'Record creation timestamp';
COMMENT ON COLUMN registrations.updated_at IS 'Last update timestamp';

-- ============================================================================
-- Table: audit_log (Optional - for compliance tracking)
-- ============================================================================
-- Tracks all changes to registrations for compliance and troubleshooting

CREATE TABLE IF NOT EXISTS audit_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    registration_id UUID NOT NULL,  -- T037: NO FOREIGN KEY CONSTRAINT to preserve logs after registration deletion
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    action TEXT NOT NULL CHECK (action IN ('Created', 'Approved', 'Rejected', 'Updated', 'Deleted')),
    previous_status TEXT,
    new_status TEXT,
    metadata JSONB,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_audit_log_registration_id ON audit_log(registration_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp DESC);

-- Comments for documentation
COMMENT ON TABLE audit_log IS 'Change tracking for registrations (compliance and troubleshooting)';
COMMENT ON COLUMN audit_log.log_id IS 'Internal unique identifier';
COMMENT ON COLUMN audit_log.registration_id IS 'Registration that was modified';
COMMENT ON COLUMN audit_log.user_id IS 'User who performed the action';
COMMENT ON COLUMN audit_log.action IS 'Type of action: Created, Approved, Rejected, Updated, Deleted';
COMMENT ON COLUMN audit_log.previous_status IS 'Status before change (NULL for Create action)';
COMMENT ON COLUMN audit_log.new_status IS 'Status after change';
COMMENT ON COLUMN audit_log.metadata IS 'Additional context (reason for rejection, fields changed, etc.)';
COMMENT ON COLUMN audit_log.timestamp IS 'When the action occurred';

-- ============================================================================
-- Triggers: Automatic timestamp updates
-- ============================================================================

-- Function to update updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for users table
DROP TRIGGER IF EXISTS users_updated_at_trigger ON users;
CREATE TRIGGER users_updated_at_trigger
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for registrations table
DROP TRIGGER IF EXISTS registrations_updated_at_trigger ON registrations;
CREATE TRIGGER registrations_updated_at_trigger
    BEFORE UPDATE ON registrations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Verification Queries (for manual testing)
-- ============================================================================

-- Verify tables were created
-- SELECT table_name FROM information_schema.tables 
-- WHERE table_schema = 'public' 
-- ORDER BY table_name;

-- Verify indexes were created
-- SELECT indexname, tablename 
-- FROM pg_indexes 
-- WHERE schemaname = 'public' 
-- ORDER BY tablename, indexname;

-- Verify constraints were created
-- SELECT constraint_name, table_name, constraint_type 
-- FROM information_schema.table_constraints 
-- WHERE table_schema = 'public' 
-- ORDER BY table_name, constraint_type;

-- ============================================================================
-- Sample Data (Development Only - Comment out for production)
-- ============================================================================

-- Insert a sample admin user (replace entra_id with your actual Entra ID)
-- INSERT INTO users (entra_id, email, display_name, is_admin) 
-- VALUES ('00000000-0000-0000-0000-000000000000', 'admin@example.com', 'Admin User', TRUE)
-- ON CONFLICT (entra_id) DO NOTHING;

-- Insert a sample regular user
-- INSERT INTO users (entra_id, email, display_name, is_admin) 
-- VALUES ('11111111-1111-1111-1111-111111111111', 'user@example.com', 'Regular User', FALSE)
-- ON CONFLICT (entra_id) DO NOTHING;

-- ============================================================================
-- Script Complete
-- ============================================================================
-- Tables created: users, registrations, audit_log
-- Indexes created: 7 indexes for query performance
-- Triggers created: auto-update updated_at on users and registrations
-- Ready for application use
-- ============================================================================
