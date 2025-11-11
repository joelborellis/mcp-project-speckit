import { PublicClientApplication } from '@azure/msal-browser';
import type { Configuration } from '@azure/msal-browser';

// MSAL configuration
export const msalConfig: Configuration = {
  auth: {
    clientId: import.meta.env.VITE_ENTRA_CLIENT_ID || 'not-configured',
    authority: `https://login.microsoftonline.com/${import.meta.env.VITE_ENTRA_TENANT_ID || 'common'}`,
    redirectUri: import.meta.env.VITE_ENTRA_REDIRECT_URI || window.location.origin,
  },
  cache: {
    cacheLocation: 'sessionStorage',
    storeAuthStateInCookie: false,
  },
};

// Scopes for token requests
export const loginRequest = {
  scopes: ['User.Read', 'GroupMember.Read.All'],
};

// Create MSAL instance
export const msalInstance = new PublicClientApplication(msalConfig);

// Initialize MSAL
export const initializeMsal = async () => {
  try {
    await msalInstance.initialize();
    await msalInstance.handleRedirectPromise();
    console.log('MSAL initialized successfully');
  } catch (error) {
    console.error('MSAL initialization failed:', error);
    // Don't throw - allow app to run without auth if MSAL fails
  }
};
