import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { getUserRegistrations } from '../services/db.service';
import { formatTimestamp } from '../utils/formatting';
import type { MCPEndpoint } from '../types/endpoint.types';
import { EndpointStatus } from '../types/endpoint.types';

/**
 * MyRegistrationsPage component
 * Displays user's endpoint submissions
 */
export const MyRegistrationsPage: React.FC = () => {
  const { user } = useAuth();
  const [registrations, setRegistrations] = useState<MCPEndpoint[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadRegistrations = async () => {
      if (!user) return;
      
      try {
        const data = await getUserRegistrations(user.id);
        setRegistrations(data);
      } catch (error) {
        console.error('Failed to load registrations:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadRegistrations();
  }, [user]);

  const getStatusBadgeClass = (status: typeof EndpointStatus[keyof typeof EndpointStatus]) => {
    switch (status) {
      case EndpointStatus.Approved:
        return 'bg-green-100 text-green-800';
      case EndpointStatus.Rejected:
        return 'bg-red-100 text-red-800';
      case EndpointStatus.Pending:
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-red mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading registrations...</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">My Registrations</h1>
        <Link
          to="/register"
          className="bg-primary-red text-white px-6 py-2 rounded-lg hover:bg-red-700 transition-colors"
        >
          Register New Endpoint
        </Link>
      </div>

      {registrations.length === 0 ? (
        <div className="bg-white shadow-md rounded-lg p-12 text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 className="mt-4 text-lg font-medium text-gray-900">No registrations yet</h3>
          <p className="mt-2 text-gray-500">Get started by registering your first MCP endpoint.</p>
          <Link
            to="/register"
            className="mt-6 inline-block bg-primary-red text-white px-6 py-3 rounded-lg hover:bg-red-700 transition-colors"
          >
            Register Endpoint
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {registrations.map((endpoint) => (
            <div key={endpoint.id} className="bg-white shadow-md rounded-lg p-6">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h2 className="text-xl font-semibold text-gray-900">{endpoint.name}</h2>
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusBadgeClass(
                        endpoint.status
                      )}`}
                    >
                      {endpoint.status}
                    </span>
                  </div>
                  
                  <p className="text-gray-600 mb-3">{endpoint.url}</p>
                  
                  {endpoint.description && (
                    <p className="text-gray-700 mb-3">{endpoint.description}</p>
                  )}
                  
                  <div className="flex flex-wrap gap-2 mb-3">
                    {endpoint.tools.map((tool, index) => (
                      <span
                        key={index}
                        className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm"
                      >
                        {tool}
                      </span>
                    ))}
                  </div>
                  
                  <div className="text-sm text-gray-500 space-y-1">
                    <p>
                      <span className="font-medium">Owner:</span> {endpoint.owner}
                    </p>
                    <p>
                      <span className="font-medium">Submitted:</span>{' '}
                      {formatTimestamp(endpoint.submissionTimestamp)}
                    </p>
                    {endpoint.reviewTimestamp && (
                      <p>
                        <span className="font-medium">Reviewed:</span>{' '}
                        {formatTimestamp(endpoint.reviewTimestamp)} by {endpoint.reviewerName}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
