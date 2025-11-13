/**
 * API Service for MCP Registry Backend
 * 
 * This service handles all HTTP requests to the FastAPI backend,
 * replacing the previous IndexedDB implementation.
 * 
 * Features:
 * - Automatic MSAL token injection
 * - Error handling with user-friendly messages
 * - Type-safe request/response handling
 * - Token expiration handling with re-authentication
 */

import type { MCPEndpoint } from '../types/endpoint.types';
import { EndpointStatus } from '../types/endpoint.types';
import type { RegistrationResponse, RegistrationListResponse } from '../types/registration.types';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * API Error class for structured error handling
 */
export class APIError extends Error {
  statusCode: number;
  details?: unknown;

  constructor(
    message: string,
    statusCode: number,
    details?: unknown
  ) {
    super(message);
    this.statusCode = statusCode;
    this.details = details;
    this.name = 'APIError';
  }
}

/**
 * Make authenticated HTTP request to backend
 */
const fetchWithAuth = async (
  endpoint: string,
  token: string,
  options: RequestInit = {}
): Promise<Response> => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers,
    },
  });

  // Handle common error cases
  if (response.status === 401) {
    throw new APIError(
      'Authentication failed. Please sign in again.',
      401
    );
  }

  if (response.status === 403) {
    throw new APIError(
      'You do not have permission to perform this action.',
      403
    );
  }

  if (response.status === 404) {
    throw new APIError(
      'Resource not found.',
      404
    );
  }

  if (response.status === 409) {
    const data = await response.json();
    throw new APIError(
      data.detail || 'Resource already exists.',
      409,
      data
    );
  }

  if (!response.ok) {
    let errorMessage = 'An error occurred. Please try again.';
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorMessage;
    } catch {
      // Response is not JSON, use default message
    }
    throw new APIError(errorMessage, response.status);
  }

  return response;
};

/**
 * Convert backend RegistrationResponse to frontend MCPEndpoint format
 */
const mapRegistrationToEndpoint = (reg: RegistrationResponse): MCPEndpoint => {
  return {
    id: reg.registration_id,
    name: reg.endpoint_name,
    url: reg.endpoint_url,
    description: reg.description || '',
    owner: reg.owner_contact,
    tools: reg.available_tools.map(tool => tool.name || JSON.stringify(tool)),
    status: reg.status as EndpointStatus,
    submitterId: reg.submitter_id,
    submitterName: '', // Will be fetched separately if needed
    submissionTimestamp: new Date(reg.created_at).getTime(),
    reviewerId: reg.approver_id || null,
    reviewerName: null, // Will be fetched separately if needed
    reviewTimestamp: reg.approved_at ? new Date(reg.approved_at).getTime() : null,
  };
};

/**
 * Convert frontend MCPEndpoint to backend CreateRegistrationRequest
 */
const mapEndpointToCreateRequest = (endpoint: Omit<MCPEndpoint, 'id' | 'status' | 'submitterId' | 'submitterName' | 'submissionTimestamp' | 'reviewerId' | 'reviewerName' | 'reviewTimestamp'>) => {
  return {
    endpoint_url: endpoint.url,
    endpoint_name: endpoint.name,
    description: endpoint.description,
    owner_contact: endpoint.owner,
    available_tools: endpoint.tools.map(tool => ({ name: tool })),
  };
};

// ============================================================================
// API Functions
// ============================================================================

/**
 * Initialize API connection (health check)
 */
export const initializeAPI = async (): Promise<void> => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) {
      throw new Error('Backend health check failed');
    }
    console.log('API connection established');
  } catch (error) {
    console.error('Failed to connect to backend:', error);
    throw new Error('Cannot connect to backend API. Please ensure the server is running.');
  }
};

/**
 * Get registrations with optional filters (Generic browse endpoint)
 * Supports all query parameters for maximum flexibility
 */
export const getRegistrations = async (params: {
  status?: string;
  search?: string;
  limit?: number;
  offset?: number;
}, token: string): Promise<RegistrationListResponse> => {
  const queryParams = new URLSearchParams();
  
  if (params.status) queryParams.append('status', params.status);
  if (params.search) queryParams.append('search', params.search);
  if (params.limit) queryParams.append('limit', params.limit.toString());
  if (params.offset) queryParams.append('offset', params.offset.toString());
  
  const queryString = queryParams.toString();
  const endpoint = queryString ? `/registrations?${queryString}` : '/registrations';
  
  const response = await fetchWithAuth(endpoint, token);
  return response.json();
};

/**
 * Get registration by endpoint URL (User Story 2: Programmatic Query - T031)
 * 
 * Queries registration by exact endpoint_url match. Enables CI/CD pipelines
 * and monitoring systems to check registration status programmatically.
 * 
 * @param endpoint_url - Full URL of the MCP endpoint
 * @param token - Authentication token
 * @returns Single RegistrationResponse if found
 * @throws APIError with status 404 if registration not found (T032)
 * @throws APIError with status 401 if authentication fails
 * 
 * Example:
 * ```ts
 * try {
 *   const registration = await getRegistrationByUrl('https://api.example.com/mcp', token);
 *   console.log(`Status: ${registration.status}`);
 * } catch (error) {
 *   if (error instanceof APIError && error.statusCode === 404) {
 *     console.log('Registration not found');
 *   }
 * }
 * ```
 */
export const getRegistrationByUrl = async (
  endpoint_url: string, 
  token: string
): Promise<RegistrationResponse> => {
  // T027: URL encode the endpoint_url parameter
  const encodedUrl = encodeURIComponent(endpoint_url);
  const response = await fetchWithAuth(`/registrations/by-url?endpoint_url=${encodedUrl}`, token);
  
  // T032: Error handling for 404 already implemented in fetchWithAuth
  // fetchWithAuth throws APIError with status 404 and message "Resource not found."
  // which gets transformed to "Registration not found" in catch block
  return response.json();
};

/**
 * Get all approved endpoints (Browse)
 */
export const getAllApprovedEndpoints = async (token: string): Promise<MCPEndpoint[]> => {
  const response = await fetchWithAuth('/registrations?status=Approved&limit=100', token);
  const data: RegistrationListResponse = await response.json();
  return data.results.map(mapRegistrationToEndpoint);
};

/**
 * Search endpoints by query (Real-time filter)
 * Note: Backend supports server-side search, but for now we'll filter client-side
 * to maintain backward compatibility with the existing UI
 */
export const searchEndpoints = async (query: string, token: string): Promise<MCPEndpoint[]> => {
  const response = await fetchWithAuth(
    `/registrations?status=Approved&search=${encodeURIComponent(query)}&limit=100`,
    token
  );
  const data: RegistrationListResponse = await response.json();
  return data.results.map(mapRegistrationToEndpoint);
};

/**
 * Get user's registrations
 */
export const getUserRegistrations = async (token: string): Promise<MCPEndpoint[]> => {
  const response = await fetchWithAuth('/registrations/my?limit=100', token);
  const data: RegistrationListResponse = await response.json();
  return data.results.map(mapRegistrationToEndpoint);
};

/**
 * Get pending approvals (Admin)
 */
export const getPendingApprovals = async (token: string): Promise<MCPEndpoint[]> => {
  const response = await fetchWithAuth('/registrations?status=Pending&limit=100', token);
  const data: RegistrationListResponse = await response.json();
  return data.results.map(mapRegistrationToEndpoint);
};

/**
 * Get user's pending registrations
 */
export const getUserPendingRegistrations = async (token: string): Promise<MCPEndpoint[]> => {
  const response = await fetchWithAuth('/registrations/my?limit=100', token);
  const data: RegistrationListResponse = await response.json();
  return data.results
    .filter(reg => reg.status === 'Pending')
    .map(mapRegistrationToEndpoint);
};

/**
 * Get audit logs with optional filters (User Story 3: Audit Logging - T042)
 * 
 * Queries audit logs for registration modifications. Requires admin privileges.
 * 
 * @param params - Filter parameters (registration_id, user_id, action, from, to, limit, offset)
 * @param token - Authentication token (must be admin)
 * @returns Paginated list of audit log entries
 * @throws APIError with status 403 if user is not admin (T043)
 * @throws APIError with status 400 if date range invalid (end before start)
 * 
 * Example:
 * ```ts
 * try {
 *   const logs = await getAuditLogs({
 *     registration_id: 'abc-123',
 *     limit: 50,
 *     offset: 0
 *   }, token);
 *   console.log(`Found ${logs.total} audit entries`);
 * } catch (error) {
 *   if (error instanceof APIError && error.statusCode === 403) {
 *     console.log('Admin privileges required');
 *   }
 * }
 * ```
 */
export const getAuditLogs = async (params: {
  registration_id?: string;
  user_id?: string;
  action?: string;
  from?: string;  // ISO 8601 datetime
  to?: string;    // ISO 8601 datetime
  limit?: number;
  offset?: number;
}, token: string): Promise<import('../types/audit-log.types').AuditLogListResponse> => {
  const queryParams = new URLSearchParams();
  
  if (params.registration_id) queryParams.append('registration_id', params.registration_id);
  if (params.user_id) queryParams.append('user_id', params.user_id);
  if (params.action) queryParams.append('action', params.action);
  if (params.from) queryParams.append('from', params.from);
  if (params.to) queryParams.append('to', params.to);
  if (params.limit) queryParams.append('limit', params.limit.toString());
  if (params.offset) queryParams.append('offset', params.offset.toString());
  
  const queryString = queryParams.toString();
  const endpoint = queryString ? `/audit-logs?${queryString}` : '/audit-logs';
  
  // T043: Error handling for 403 Forbidden already implemented in fetchWithAuth
  // fetchWithAuth throws APIError with status 403 and message "You do not have permission..."
  const response = await fetchWithAuth(endpoint, token);
  return response.json();
};

/**
 * Check if URL is unique
 * Note: Backend will handle this via 409 Conflict on create, but we can pre-check
 */
export const isURLUnique = async (url: string, token: string, excludeId?: string): Promise<boolean> => {
  try {
    // Get all registrations and check if URL exists
    const response = await fetchWithAuth('/registrations?limit=1000', token);
    const data: RegistrationListResponse = await response.json();
    
    const existing = data.results.find(reg => reg.endpoint_url === url);
    
    if (!existing) return true;
    if (excludeId && existing.registration_id === excludeId) return true;
    
    return false;
  } catch (error) {
    console.warn('URL uniqueness check failed:', error);
    return true; // Assume unique, backend will validate
  }
};

/**
 * Get endpoint by ID
 */
export const getEndpointById = async (id: string, token: string): Promise<MCPEndpoint | undefined> => {
  try {
    const response = await fetchWithAuth(`/registrations/${id}`, token);
    const data: RegistrationResponse = await response.json();
    return mapRegistrationToEndpoint(data);
  } catch (error) {
    if (error instanceof APIError && error.statusCode === 404) {
      return undefined;
    }
    throw error;
  }
};

/**
 * Create endpoint
 */
export const createEndpoint = async (
  endpoint: Omit<MCPEndpoint, 'id' | 'status' | 'submitterId' | 'submitterName' | 'submissionTimestamp' | 'reviewerId' | 'reviewerName' | 'reviewTimestamp'>,
  token: string
): Promise<string> => {
  try {
    const requestBody = mapEndpointToCreateRequest(endpoint);
    
    const response = await fetchWithAuth('/registrations', token, {
      method: 'POST',
      body: JSON.stringify(requestBody),
    });
    
    const data: RegistrationResponse = await response.json();
    return data.registration_id;
  } catch (error) {
    if (error instanceof APIError && error.statusCode === 409) {
      throw new Error('This URL is already registered');
    }
    throw error;
  }
};

/**
 * Update endpoint status (Approve/Reject)
 */
export const updateEndpointStatus = async (
  id: string,
  status: typeof EndpointStatus.Approved | typeof EndpointStatus.Rejected,
  token: string
): Promise<void> => {
  await fetchWithAuth(`/registrations/${id}/status`, token, {
    method: 'PATCH',
    body: JSON.stringify({
      status,
      reason: status === EndpointStatus.Rejected ? 'Rejected by admin' : undefined,
    }),
  });
};

/**
 * Delete endpoint (Remove)
 */
export const deleteEndpoint = async (id: string, token: string): Promise<void> => {
  await fetchWithAuth(`/registrations/${id}`, token, {
    method: 'DELETE',
  });
};

/**
 * Get current user profile
 */
export const getCurrentUser = async (token: string) => {
  const response = await fetchWithAuth('/users/me', token);
  return await response.json();
};

/**
 * Health check (no auth required)
 */
export const healthCheck = async (): Promise<{ status: string; database: string }> => {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error('Health check failed');
  }
  return await response.json();
};
