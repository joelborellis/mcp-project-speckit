import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import type { AuthContextValue } from '../context/AuthContext';

/**
 * Custom hook to access authentication context
 * @throws Error if used outside AuthProvider
 */
export const useAuth = (): AuthContextValue => {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
};
