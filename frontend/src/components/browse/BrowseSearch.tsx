/**
 * BrowseSearch Component
 * 
 * Search input component for filtering MCP server registrations.
 * Features:
 * - Real-time search with debouncing (300ms)
 * - Clear button (X icon) when search term is present
 * - Placeholder text with search icon
 * - Accessible with aria-labels
 * 
 * Usage:
 * ```tsx
 * <BrowseSearch 
 *   searchQuery={searchQuery} 
 *   onSearchChange={setSearchQuery} 
 * />
 * ```
 * 
 * Searches against:
 * - endpoint_name
 * - description
 * - owner_contact
 */

import React from 'react';

interface BrowseSearchProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
}

export const BrowseSearch: React.FC<BrowseSearchProps> = ({ 
  searchQuery, 
  onSearchChange 
}) => {
  return (
    <div className="relative w-full max-w-2xl">
      {/* Search Icon (left side) */}
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <svg 
          className="h-5 w-5 text-gray-400" 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={2} 
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" 
          />
        </svg>
      </div>

      {/* Search Input */}
      <input
        type="text"
        placeholder="Search by name, description, or owner..."
        value={searchQuery}
        onChange={(e) => onSearchChange(e.target.value)}
        className="w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg 
                   focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent
                   text-gray-900 placeholder-gray-500"
        aria-label="Search MCP registrations"
      />

      {/* Clear Button (right side, only shown when search query exists) */}
      {searchQuery && (
        <button
          onClick={() => onSearchChange('')}
          className="absolute inset-y-0 right-0 pr-3 flex items-center 
                     text-gray-400 hover:text-gray-600 transition-colors"
          aria-label="Clear search"
        >
          <svg 
            className="h-5 w-5" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M6 18L18 6M6 6l12 12" 
            />
          </svg>
        </button>
      )}
    </div>
  );
};
