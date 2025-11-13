/**
 * BrowsePage Component
 * 
 * Main page for browsing approved MCP server registrations.
 * Features:
 * - Admin users: See all registrations (Pending/Approved/Rejected)
 * - Non-admin users: See only Approved registrations
 * - Real-time search filtering (name, description, owner)
 * - Client-side pagination (20 items per page)
 * - Responsive grid layout (1/2/3 columns)
 * - Registration detail modal
 * - Loading state with spinner
 * - Empty state messaging
 * 
 * User Story: US1 - Browse Approved MCP Registrations
 * Success Criteria: SC-001, SC-002, SC-003, SC-004, SC-005
 */

import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';  // T046: Error toast notifications
import { useAuth } from '../hooks/useAuth';
import { getRegistrations } from '../services/api.service';
import type { RegistrationResponse } from '../types/registration.types';
import { BrowseSearch } from '../components/browse/BrowseSearch';
import { BrowseList } from '../components/browse/BrowseList';
import { Pagination } from '../components/browse/Pagination';
import { RegistrationDetailModal } from '../components/browse/RegistrationDetailModal';

const ITEMS_PER_PAGE = 20;

export const BrowsePage: React.FC = () => {
  const { user, login, getAccessToken } = useAuth();
  
  // State management
  const [registrations, setRegistrations] = useState<RegistrationResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedRegistration, setSelectedRegistration] = useState<RegistrationResponse | null>(null);

  // T023: Fetch registrations on mount (admin vs non-admin filtering)
  useEffect(() => {
    const fetchRegistrations = async () => {
      // Skip if user is not authenticated
      if (!user) {
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setError(null);
      
      try {
        const token = await getAccessToken();
        
        // Admin: fetch all registrations (no status filter)
        // Non-admin: fetch only Approved registrations
        const statusFilter = user?.isAdmin ? undefined : 'Approved';
        
        const response = await getRegistrations({
          status: statusFilter,
          limit: 1000, // Fetch all for client-side filtering/pagination
          offset: 0
        }, token);
        
        setRegistrations(response.results);
      } catch (err) {
        console.error('Failed to fetch registrations:', err);
        const errorMessage = 'Failed to load registrations. Please try again later.';
        setError(errorMessage);
        // T046: Show error toast notification
        toast.error(errorMessage);
      } finally {
        setIsLoading(false);
      }
    };

    fetchRegistrations();
  }, [user, user?.isAdmin, getAccessToken]);

  // T021: Client-side filtering by search query
  const filteredRegistrations = registrations.filter((reg) => {
    if (!searchQuery) return true;
    
    const query = searchQuery.toLowerCase();
    const name = reg.endpoint_name.toLowerCase();
    const description = reg.description?.toLowerCase() || '';
    const owner = reg.owner_contact.toLowerCase();
    
    return name.includes(query) || description.includes(query) || owner.includes(query);
  });

  // T022: Pagination logic
  const totalPages = Math.ceil(filteredRegistrations.length / ITEMS_PER_PAGE);
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const endIndex = startIndex + ITEMS_PER_PAGE;
  const paginatedRegistrations = filteredRegistrations.slice(startIndex, endIndex);

  // Reset to page 1 when search query changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery]);

  // Handle modal close
  const handleCloseModal = () => {
    setSelectedRegistration(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            MCP Server Registry
          </h1>
          {!user ? (
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-blue-700">
                Please{' '}
                <button 
                  onClick={login}
                  className="underline font-medium hover:text-blue-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 rounded"
                >
                  log in
                </button>{' '}
                to browse MCP server registrations.
              </p>
            </div>
          ) : (
            <p className="text-gray-600">
              {user.isAdmin
                ? 'Browse all MCP server registrations (admin view)'
                : 'Browse approved MCP server registrations'}
            </p>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Show content only if user is authenticated */}
        {!user ? (
          <div className="flex justify-center items-center py-16">
            <div className="text-center">
              <svg 
                className="mx-auto h-12 w-12 text-gray-400" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
                aria-hidden="true"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" 
                />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">Authentication Required</h3>
              <p className="mt-1 text-sm text-gray-500">
                Please log in to access the MCP server registry.
              </p>
            </div>
          </div>
        ) : (
          <>
            {/* Search Bar */}
            <div className="mb-8 flex justify-center">
              <BrowseSearch 
                searchQuery={searchQuery} 
                onSearchChange={setSearchQuery} 
              />
            </div>

            {/* Results Summary */}
            {!isLoading && (
              <div className="mb-4 text-sm text-gray-600">
                Showing {paginatedRegistrations.length} of {filteredRegistrations.length} registrations
                {searchQuery && ` matching "${searchQuery}"`}
              </div>
            )}

            {/* Loading Spinner (T045: added in Phase 6) */}
            {isLoading && (
              <div className="flex justify-center items-center py-16">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600" />
              </div>
            )}

            {/* Error State */}
            {error && !isLoading && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
                {error}
              </div>
            )}

            {/* Registration List */}
            {!isLoading && !error && (
              <BrowseList 
                registrations={paginatedRegistrations} 
                onCardClick={setSelectedRegistration}
              />
            )}

            {/* Pagination */}
            {!isLoading && !error && totalPages > 1 && (
              <Pagination 
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={setCurrentPage}
              />
            )}
          </>
        )}
      </div>

      {/* Registration Detail Modal */}
      {selectedRegistration && (
        <RegistrationDetailModal 
          registration={selectedRegistration}
          onClose={handleCloseModal}
        />
      )}
    </div>
  );
};
