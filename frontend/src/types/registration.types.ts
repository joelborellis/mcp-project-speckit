import type { MCPEndpoint } from './endpoint.types';

/**
 * Backend API Response Types
 * 
 * Type definitions for FastAPI backend responses.
 * These match the Pydantic schemas in backend/src/schemas/
 */

/**
 * Registration status enum (matches backend)
 */
export type RegistrationStatus = 'Pending' | 'Approved' | 'Rejected';

/**
 * Tool information structure
 */
export interface ToolInfo {
  name: string;
  description?: string;
  [key: string]: unknown; // Allow additional properties
}

/**
 * Single registration response
 */
export interface RegistrationResponse {
  registration_id: string;
  endpoint_url: string;
  endpoint_name: string;
  description: string | null;
  owner_contact: string;
  available_tools: ToolInfo[];
  status: RegistrationStatus;
  submitter_id: string;
  approver_id: string | null;
  created_at: string; // ISO 8601 datetime
  updated_at: string; // ISO 8601 datetime
  approved_at: string | null; // ISO 8601 datetime
}

/**
 * Paginated registration list response
 */
export interface RegistrationListResponse {
  total: number;
  limit: number;
  offset: number;
  results: RegistrationResponse[];
}

/**
 * Create registration request body
 */
export interface CreateRegistrationRequest {
  endpoint_url: string;
  endpoint_name: string;
  description?: string;
  owner_contact: string;
  available_tools: ToolInfo[];
}

/**
 * Update status request body
 */
export interface UpdateStatusRequest {
  status: 'Approved' | 'Rejected';
  reason?: string;
}

/**
 * User response
 */
export interface UserResponse {
  user_id: string;
  entra_id: string;
  email: string;
  display_name: string | null;
  is_admin: boolean;
  created_at: string; // ISO 8601 datetime
  updated_at: string; // ISO 8601 datetime
}

/**
 * Registration Submission view model
 * Extends MCPEndpoint with computed UI-specific metadata
 */
export interface RegistrationSubmission extends MCPEndpoint {
  /** Computed field: Can current user edit this submission? */
  canEdit: boolean;
  
  /** Computed field: Can current user approve/reject this submission? */
  canReview: boolean;
  
  /** Computed field: Formatted submission date for display */
  submittedDateDisplay: string;
  
  /** Computed field: Formatted review date for display (null if pending) */
  reviewedDateDisplay: string | null;
  
  /** Computed field: CSS class for status badge */
  statusBadgeClass: string;
}
