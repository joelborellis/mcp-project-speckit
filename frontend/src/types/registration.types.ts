import type { MCPEndpoint } from './endpoint.types';

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
