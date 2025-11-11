import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

/**
 * Header component
 * Application header with navigation and auth controls
 */
export const Header: React.FC = () => {
  const { user, isAuthenticated, login, logout, isLoading } = useAuth();

  return (
    <header className="bg-primary-red text-white shadow-lg">
      <div className="container mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          {/* Logo and title */}
          <Link to="/" className="text-2xl font-bold hover:text-gray-200 transition-colors">
            {import.meta.env.VITE_APP_NAME || 'MCP Registry'}
          </Link>

          {/* Navigation */}
          <nav className="flex items-center gap-6">
            <Link 
              to="/" 
              className="hover:text-gray-200 transition-colors min-h-touch min-w-touch flex items-center"
            >
              Browse
            </Link>
            
            {!isLoading && isAuthenticated && (
              <>
                <Link 
                  to="/my-registrations" 
                  className="hover:text-gray-200 transition-colors min-h-touch min-w-touch flex items-center"
                >
                  My Registrations
                </Link>
                <Link 
                  to="/register" 
                  className="hover:text-gray-200 transition-colors min-h-touch min-w-touch flex items-center"
                >
                  Register Endpoint
                </Link>
                {user?.isAdmin && (
                  <Link 
                    to="/approvals" 
                    className="hover:text-gray-200 transition-colors min-h-touch min-w-touch flex items-center"
                  >
                    Approvals
                  </Link>
                )}
              </>
            )}

            {/* Auth controls */}
            {!isLoading && (
              <div className="flex items-center gap-4 ml-4 border-l border-red-400 pl-4">
                {isAuthenticated ? (
                  <>
                    <span className="text-sm">{user?.displayName}</span>
                    <button
                      onClick={() => logout()}
                      className="bg-white text-primary-red px-4 py-2 rounded hover:bg-gray-100 transition-colors min-h-touch min-w-touch"
                    >
                      Logout
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => login()}
                    className="bg-white text-primary-red px-4 py-2 rounded hover:bg-gray-100 transition-colors min-h-touch min-w-touch"
                  >
                    Login
                  </button>
                )}
              </div>
            )}
          </nav>
        </div>
      </div>
    </header>
  );
};
