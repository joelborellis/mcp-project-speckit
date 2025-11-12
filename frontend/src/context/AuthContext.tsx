import React, { createContext, useState, useEffect, useMemo } from 'react';
import type { PropsWithChildren } from 'react';
import { MsalProvider, useMsal } from '@azure/msal-react';
import { InteractionStatus } from '@azure/msal-browser';
import { msalInstance } from '../config/msal.config';
import type { User } from '../types/user.types';

/**
 * Authentication context shape
 */
export interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  getAccessToken: () => Promise<string>;
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);

/**
 * Inner provider that uses MSAL hooks
 */
const AuthProviderInner: React.FC<PropsWithChildren> = ({ children }) => {
  const { instance, accounts, inProgress } = useMsal();
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Admin group ID from environment
  const adminGroupId = import.meta.env.VITE_ENTRA_ADMIN_GROUP_ID || '';

  useEffect(() => {
    const loadUser = async () => {
      if (inProgress !== InteractionStatus.None) {
        return; // Wait for MSAL to finish any in-progress interactions
      }

      if (accounts.length === 0) {
        setUser(null);
        setIsLoading(false);
        return;
      }

      const account = accounts[0];
      
      try {
        // Acquire token silently to get groups claim
        const response = await instance.acquireTokenSilent({
          account,
          scopes: ['User.Read', 'GroupMember.Read.All'],
        });

        // Try to get groups from ID token claims first
        let groups: string[] = (response.idTokenClaims as Record<string, unknown>)?.groups as string[] || [];
        
        // If groups claim is not in token, fetch from Microsoft Graph API
        if (groups.length === 0 && adminGroupId) {
          console.log('Groups not in token claims, fetching from Microsoft Graph API...');
          try {
            const graphResponse = await fetch('https://graph.microsoft.com/v1.0/me/memberOf?$select=id', {
              headers: {
                Authorization: `Bearer ${response.accessToken}`,
              },
            });
            
            if (graphResponse.ok) {
              const data = await graphResponse.json();
              groups = data.value.map((group: { id: string }) => group.id);
              console.log(`Fetched ${groups.length} groups from Graph API`);
            } else {
              console.error('Failed to fetch groups from Graph API:', graphResponse.status);
            }
          } catch (graphError) {
            console.error('Error fetching groups from Graph API:', graphError);
          }
        }

        const isAdmin = adminGroupId ? groups.includes(adminGroupId) : false;
        
        console.log('Admin check:', { 
          adminGroupId, 
          userGroups: groups, 
          isAdmin,
          groupsCount: groups.length 
        });

        const userData: User = {
          id: account.homeAccountId,
          displayName: account.name || '',
          email: account.username,
          isAdmin,
          groups,
          lastLoginTimestamp: Date.now(),
        };

        setUser(userData);
      } catch (error) {
        console.error('Failed to load user data:', error);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    loadUser();
  }, [accounts, inProgress, instance, adminGroupId]);

  const login = async () => {
    try {
      await instance.loginPopup({
        scopes: ['User.Read', 'GroupMember.Read.All'],
      });
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      await instance.logoutPopup();
      setUser(null);
    } catch (error) {
      console.error('Logout failed:', error);
      throw error;
    }
  };

  const getAccessToken = async (): Promise<string> => {
    if (accounts.length === 0) {
      throw new Error('No authenticated user');
    }

    try {
      // Request token with API scope (format: api://{client-id}/.default)
      // Token will include basic claims like sub, upn, unique_name
      const apiScope = `api://${import.meta.env.VITE_ENTRA_CLIENT_ID}/.default`;
      
      const response = await instance.acquireTokenSilent({
        account: accounts[0],
        scopes: [apiScope],
      });
      return response.accessToken;
    } catch (error) {
      console.error('Failed to acquire token:', error);
      // Try interactive token acquisition as fallback
      try {
        const apiScope = `api://${import.meta.env.VITE_ENTRA_CLIENT_ID}/.default`;
        
        const response = await instance.acquireTokenPopup({
          scopes: [apiScope],
        });
        return response.accessToken;
      } catch (popupError) {
        console.error('Failed to acquire token via popup:', popupError);
        throw new Error('Failed to get access token');
      }
    }
  };

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: !!user,
      isLoading,
      login,
      logout,
      getAccessToken,
    }),
    [user, isLoading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

/**
 * AuthProvider component
 * Wraps MsalProvider and provides authentication state
 */
export const AuthProvider: React.FC<PropsWithChildren> = ({ children }) => {
  return (
    <MsalProvider instance={msalInstance}>
      <AuthProviderInner>{children}</AuthProviderInner>
    </MsalProvider>
  );
};
