/**
 * User type definition
 * Represents an authenticated user from Microsoft Entra ID
 */
export interface User {
  /** Unique identifier from Entra ID (Object ID) */
  id: string;
  
  /** User's display name from Entra ID */
  displayName: string;
  
  /** User's email address (UPN) */
  email: string;
  
  /** User role determination */
  isAdmin: boolean;
  
  /** Entra ID groups the user belongs to (Object IDs) */
  groups: string[];
  
  /** Last authentication timestamp */
  lastLoginTimestamp: number | null;
}
