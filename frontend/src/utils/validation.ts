import type { User } from '../types/user.types';
import type { MCPEndpoint } from '../types/endpoint.types';
import { EndpointStatus } from '../types/endpoint.types';

// ============================================================================
// Validation Constants
// ============================================================================

export const VALIDATION_LIMITS = {
  NAME_MAX_LENGTH: 100,
  DESCRIPTION_MAX_LENGTH: 500,
  OWNER_MAX_LENGTH: 100,
  TOOL_MAX_LENGTH: 50,
  URL_MAX_LENGTH: 2048,
  MIN_TOOLS: 1,
  MAX_TOOLS: 20
} as const;

export const VALIDATION_MESSAGES = {
  NAME_REQUIRED: 'Endpoint name is required',
  NAME_TOO_LONG: `Endpoint name must be ${VALIDATION_LIMITS.NAME_MAX_LENGTH} characters or less`,
  URL_REQUIRED: 'URL is required',
  URL_INVALID: 'Invalid URL format. Must be a valid HTTP/HTTPS URL',
  URL_DUPLICATE: 'This URL is already registered',
  DESCRIPTION_TOO_LONG: `Description must be ${VALIDATION_LIMITS.DESCRIPTION_MAX_LENGTH} characters or less`,
  OWNER_REQUIRED: 'Owner is required',
  OWNER_TOO_LONG: `Owner must be ${VALIDATION_LIMITS.OWNER_MAX_LENGTH} characters or less`,
  TOOLS_REQUIRED: 'At least one tool is required',
  TOOLS_TOO_MANY: `Cannot exceed ${VALIDATION_LIMITS.MAX_TOOLS} tools`,
  NOT_ADMIN: 'You must be an admin to perform this action',
  CANNOT_REVIEW_OWN: 'You cannot review your own submission',
  ALREADY_REVIEWED: 'This endpoint has already been reviewed',
  INVALID_TRANSITION: 'Invalid status transition'
} as const;

// ============================================================================
// Core Validation Functions
// ============================================================================

export function isValidURL(url: string): boolean {
  try {
    const parsed = new URL(url);
    
    if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
      return false;
    }
    
    if (!parsed.hostname || parsed.hostname.length === 0) {
      return false;
    }
    
    // Reject localhost/private IPs (remove for local dev if needed)
    if (parsed.hostname === 'localhost' || parsed.hostname.startsWith('127.')) {
      return false;
    }
    
    return true;
  } catch {
    return false;
  }
}

export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export function isValidStatus(status: unknown): status is typeof EndpointStatus[keyof typeof EndpointStatus] {
  return status === EndpointStatus.Pending || 
         status === EndpointStatus.Approved || 
         status === EndpointStatus.Rejected;
}

export function isValidToolsArray(tools: unknown): tools is string[] {
  if (!Array.isArray(tools)) {
    return false;
  }
  
  if (tools.length === 0) {
    return false;
  }
  
  return tools.every(tool => 
    typeof tool === 'string' && 
    tool.trim().length > 0 &&
    tool.length <= VALIDATION_LIMITS.TOOL_MAX_LENGTH
  );
}

export function isValidEndpoint(endpoint: unknown): endpoint is MCPEndpoint {
  if (typeof endpoint !== 'object' || endpoint === null) {
    return false;
  }
  
  const e = endpoint as MCPEndpoint;
  
  return (
    typeof e.id === 'string' && e.id.length > 0 &&
    typeof e.name === 'string' && e.name.length > 0 && e.name.length <= VALIDATION_LIMITS.NAME_MAX_LENGTH &&
    typeof e.url === 'string' && isValidURL(e.url) &&
    typeof e.description === 'string' && e.description.length <= VALIDATION_LIMITS.DESCRIPTION_MAX_LENGTH &&
    typeof e.owner === 'string' && e.owner.length > 0 && e.owner.length <= VALIDATION_LIMITS.OWNER_MAX_LENGTH &&
    Array.isArray(e.tools) && e.tools.length > 0 && e.tools.every(t => typeof t === 'string' && t.length > 0) &&
    isValidStatus(e.status) &&
    typeof e.submitterId === 'string' && e.submitterId.length > 0 &&
    typeof e.submitterName === 'string' && e.submitterName.length > 0 &&
    typeof e.submissionTimestamp === 'number' && e.submissionTimestamp > 0 &&
    (e.reviewerId === null || typeof e.reviewerId === 'string') &&
    (e.reviewerName === null || typeof e.reviewerName === 'string') &&
    (e.reviewTimestamp === null || typeof e.reviewTimestamp === 'number')
  );
}

export function isUser(value: unknown): value is User {
  if (typeof value !== 'object' || value === null) {
    return false;
  }
  
  const u = value as User;
  
  return (
    typeof u.id === 'string' && u.id.length > 0 &&
    typeof u.displayName === 'string' && u.displayName.length > 0 &&
    typeof u.email === 'string' && isValidEmail(u.email) &&
    typeof u.isAdmin === 'boolean' &&
    Array.isArray(u.groups) &&
    (u.lastLoginTimestamp === null || typeof u.lastLoginTimestamp === 'number')
  );
}

// ============================================================================
// Sanitization Functions
// ============================================================================

export function sanitizeString(input: string, maxLength: number): string {
  return input.trim().slice(0, maxLength);
}

export function sanitizeURL(input: string): string {
  const trimmed = input.trim();
  
  if (!/^https?:\/\//i.test(trimmed)) {
    return `https://${trimmed}`;
  }
  
  return trimmed;
}

export function sanitizeToolsInput(input: string): string[] {
  return input
    .split(',')
    .map(tool => tool.trim())
    .filter(tool => tool.length > 0)
    .map(tool => tool.slice(0, VALIDATION_LIMITS.TOOL_MAX_LENGTH));
}

// ============================================================================
// Form Validation
// ============================================================================

export interface RegistrationFormData {
  name: string;
  url: string;
  description: string;
  owner: string;
  tools: string; // Comma-separated
}

export interface ValidationResult {
  isValid: boolean;
  errors: Record<string, string>;
}

export function validateRegistrationForm(data: RegistrationFormData): ValidationResult {
  const errors: Record<string, string> = {};
  
  // Name validation
  if (!data.name || data.name.trim().length === 0) {
    errors.name = VALIDATION_MESSAGES.NAME_REQUIRED;
  } else if (data.name.length > VALIDATION_LIMITS.NAME_MAX_LENGTH) {
    errors.name = VALIDATION_MESSAGES.NAME_TOO_LONG;
  }
  
  // URL validation
  if (!data.url || data.url.trim().length === 0) {
    errors.url = VALIDATION_MESSAGES.URL_REQUIRED;
  } else {
    const sanitizedUrl = sanitizeURL(data.url);
    if (!isValidURL(sanitizedUrl)) {
      errors.url = VALIDATION_MESSAGES.URL_INVALID;
    }
  }
  
  // Description validation
  if (data.description && data.description.length > VALIDATION_LIMITS.DESCRIPTION_MAX_LENGTH) {
    errors.description = VALIDATION_MESSAGES.DESCRIPTION_TOO_LONG;
  }
  
  // Owner validation
  if (!data.owner || data.owner.trim().length === 0) {
    errors.owner = VALIDATION_MESSAGES.OWNER_REQUIRED;
  } else if (data.owner.length > VALIDATION_LIMITS.OWNER_MAX_LENGTH) {
    errors.owner = VALIDATION_MESSAGES.OWNER_TOO_LONG;
  }
  
  // Tools validation
  if (!data.tools || data.tools.trim().length === 0) {
    errors.tools = VALIDATION_MESSAGES.TOOLS_REQUIRED;
  } else {
    const toolsArray = sanitizeToolsInput(data.tools);
    if (toolsArray.length === 0) {
      errors.tools = VALIDATION_MESSAGES.TOOLS_REQUIRED;
    }
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
}

// ============================================================================
// Permission Validation
// ============================================================================

export function canUserReviewEndpoint(user: User, endpoint: MCPEndpoint): boolean {
  if (!user.isAdmin) {
    return false;
  }
  
  if (user.id === endpoint.submitterId) {
    return false;
  }
  
  if (endpoint.status !== EndpointStatus.Pending) {
    return false;
  }
  
  return true;
}

export function canUserEditEndpoint(user: User, endpoint: MCPEndpoint): boolean {
  if (user.id !== endpoint.submitterId) {
    return false;
  }
  
  if (endpoint.status !== EndpointStatus.Pending) {
    return false;
  }
  
  return true;
}

// ============================================================================
// State Transition Validation
// ============================================================================

export function isValidStatusTransition(
  currentStatus: typeof EndpointStatus[keyof typeof EndpointStatus],
  newStatus: typeof EndpointStatus[keyof typeof EndpointStatus]
): boolean {
  const allowedTransitions: Record<string, string[]> = {
    [EndpointStatus.Pending]: [EndpointStatus.Approved, EndpointStatus.Rejected],
    [EndpointStatus.Approved]: [],
    [EndpointStatus.Rejected]: []
  };
  
  return allowedTransitions[currentStatus]?.includes(newStatus) ?? false;
}

// ============================================================================
// Error Classes
// ============================================================================

export class ValidationError extends Error {
  field?: string;
  value?: unknown;
  
  constructor(
    message: string,
    field?: string,
    value?: unknown
  ) {
    super(message);
    this.name = 'ValidationError';
    this.field = field;
    this.value = value;
  }
}

export function validateOrThrow(endpoint: unknown): asserts endpoint is MCPEndpoint {
  if (!isValidEndpoint(endpoint)) {
    throw new ValidationError('Invalid endpoint data', undefined, endpoint);
  }
}
