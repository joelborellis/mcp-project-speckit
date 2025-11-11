import { MCPRegistryDB } from './db.schema';
import type { MCPEndpoint } from '../types/endpoint.types';
import { EndpointStatus } from '../types/endpoint.types';

/**
 * Singleton database instance
 */
export const db = new MCPRegistryDB();

/**
 * Initialize database (call on app startup)
 */
export const initializeDatabase = async (): Promise<void> => {
  try {
    await db.open();
    console.log('Database initialized successfully');
  } catch (error) {
    console.error('Failed to initialize database:', error);
    throw error;
  }
};

/**
 * Clear database (for debugging/testing only)
 */
export const clearDatabase = async (): Promise<void> => {
  await db.endpoints.clear();
};

// ============================================================================
// CRUD Operations
// ============================================================================

/**
 * Get all approved endpoints (Browse)
 */
export const getAllApprovedEndpoints = async (): Promise<MCPEndpoint[]> => {
  return db.endpoints
    .where('status')
    .equals(EndpointStatus.Approved)
    .toArray();
};

/**
 * Search endpoints by query (Real-time filter)
 */
export const searchEndpoints = async (query: string): Promise<MCPEndpoint[]> => {
  const lowerQuery = query.toLowerCase();
  
  return db.endpoints
    .where('status')
    .equals(EndpointStatus.Approved)
    .filter(endpoint => 
      endpoint.name.toLowerCase().includes(lowerQuery) ||
      endpoint.owner.toLowerCase().includes(lowerQuery) ||
      endpoint.tools.some(tool => tool.toLowerCase().includes(lowerQuery))
    )
    .toArray();
};

/**
 * Get user's registrations
 */
export const getUserRegistrations = async (userId: string): Promise<MCPEndpoint[]> => {
  return db.endpoints
    .where('submitterId')
    .equals(userId)
    .reverse() // Newest first
    .toArray();
};

/**
 * Get pending approvals (Admin)
 */
export const getPendingApprovals = async (): Promise<MCPEndpoint[]> => {
  return db.endpoints
    .where('status')
    .equals(EndpointStatus.Pending)
    .reverse() // Newest first
    .toArray();
};

/**
 * Get user's pending registrations
 */
export const getUserPendingRegistrations = async (userId: string): Promise<MCPEndpoint[]> => {
  return db.endpoints
    .where('[status+submitterId]')
    .equals([EndpointStatus.Pending, userId])
    .toArray();
};

/**
 * Check if URL is unique
 */
export const isURLUnique = async (url: string, excludeId?: string): Promise<boolean> => {
  const existing = await db.endpoints
    .where('url')
    .equals(url)
    .first();
  
  if (!existing) return true;
  if (excludeId && existing.id === excludeId) return true; // Same record (edit scenario)
  
  return false;
};

/**
 * Get endpoint by ID
 */
export const getEndpointById = async (id: string): Promise<MCPEndpoint | undefined> => {
  return db.endpoints.get(id);
};

/**
 * Create endpoint
 */
export const createEndpoint = async (endpoint: MCPEndpoint): Promise<string> => {
  try {
    return await db.endpoints.add(endpoint);
  } catch (error) {
    const err = error as Error;
    if (err.name === 'ConstraintError') {
      throw new Error('This URL is already registered');
    }
    if (err.name === 'QuotaExceededError') {
      throw new Error('Storage limit exceeded. Please contact administrator.');
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
  reviewerId: string,
  reviewerName: string
): Promise<void> => {
  await db.endpoints.update(id, {
    status,
    reviewerId,
    reviewerName,
    reviewTimestamp: Date.now()
  });
};

/**
 * Delete endpoint (Remove)
 */
export const deleteEndpoint = async (id: string): Promise<void> => {
  return db.endpoints.delete(id);
};
