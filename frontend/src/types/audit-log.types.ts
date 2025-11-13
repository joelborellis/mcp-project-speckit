/**
 * AuditLog TypeScript Types
 * 
 * Type definitions for audit log entries returned by the backend API.
 * Used for admin audit log queries and compliance reporting.
 */

export type AuditAction = 'Created' | 'Approved' | 'Rejected' | 'Updated' | 'Deleted';

export interface AuditLog {
  log_id: string;
  registration_id: string;
  user_id: string;
  action: AuditAction;
  previous_status: string | null;
  new_status: string | null;
  metadata: Record<string, any> | null;
  timestamp: string; // ISO 8601 format
}

export interface AuditLogListResponse {
  results: AuditLog[];
  total: number;
  limit: number;
  offset: number;
}

export interface AuditLogQueryParams {
  registration_id?: string;
  user_id?: string;
  action?: AuditAction;
  from?: string; // ISO 8601 format
  to?: string; // ISO 8601 format
  limit?: number;
  offset?: number;
}
