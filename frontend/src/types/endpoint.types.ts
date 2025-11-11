/**
 * Endpoint status enum
 */
export const EndpointStatus = {
  Pending: 'Pending',
  Approved: 'Approved',
  Rejected: 'Rejected',
} as const;

export type EndpointStatus = typeof EndpointStatus[keyof typeof EndpointStatus];

/**
 * MCP Endpoint interface
 * Represents a registered Model Context Protocol server endpoint
 */
export interface MCPEndpoint {
  /** Unique identifier (UUID v4) */
  id: string;
  
  /** Human-readable name for the endpoint */
  name: string;
  
  /** Endpoint URL (host/IP with protocol) */
  url: string;
  
  /** Detailed description of endpoint purpose/functionality */
  description: string;
  
  /** Contact information for endpoint owner */
  owner: string;
  
  /** Array of available tools/capabilities */
  tools: string[];
  
  /** Current approval status */
  status: EndpointStatus;
  
  /** Entra ID user ID of submitter */
  submitterId: string;
  
  /** Display name of submitter (denormalized for display) */
  submitterName: string;
  
  /** Unix timestamp when endpoint was submitted */
  submissionTimestamp: number;
  
  /** Entra ID user ID of approving/rejecting admin (null if pending) */
  reviewerId: string | null;
  
  /** Display name of reviewer (denormalized for display) */
  reviewerName: string | null;
  
  /** Unix timestamp when endpoint was approved/rejected (null if pending) */
  reviewTimestamp: number | null;
}
