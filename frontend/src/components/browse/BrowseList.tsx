/**
 * BrowseList Component
 * 
 * Responsive grid container for registration cards.
 * Features:
 * - Responsive grid: 1 column (mobile 320px), 2 columns (tablet 768px), 3 columns (desktop 1024px)
 * - Empty state message when no registrations found
 * - Loading state support (renders nothing when loading)
 * - Gap spacing between cards
 * 
 * Usage:
 * ```tsx
 * <BrowseList 
 *   registrations={filteredRegistrations} 
 *   onCardClick={setSelectedRegistration}
 *   isLoading={isLoading}
 * />
 * ```
 * 
 * Responsive Breakpoints:
 * - Mobile: 320px - 1 column
 * - Tablet: 768px - 2 columns
 * - Desktop: 1024px - 3 columns
 */

import React from 'react';
import type { RegistrationResponse } from '../../types/registration.types';
import { BrowseCard } from './BrowseCard';

interface BrowseListProps {
  registrations: RegistrationResponse[];
  onCardClick: (registration: RegistrationResponse) => void;
  isLoading?: boolean;
}

export const BrowseList: React.FC<BrowseListProps> = ({ 
  registrations, 
  onCardClick,
  isLoading = false
}) => {
  // Loading state - don't render anything (handled by parent with spinner)
  if (isLoading) {
    return null;
  }

  // Empty state - no registrations found
  if (registrations.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 px-4">
        <svg 
          className="h-16 w-16 text-gray-400 mb-4" 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={2} 
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" 
          />
        </svg>
        <p className="text-lg font-medium text-gray-700 mb-2">
          No MCP registrations found
        </p>
        <p className="text-sm text-gray-500 text-center max-w-md">
          Try adjusting your search terms or filters. If you're a regular user, 
          only approved registrations are visible.
        </p>
      </div>
    );
  }

  // Render grid of cards
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {registrations.map((registration) => (
        <BrowseCard
          key={registration.registration_id}
          registration={registration}
          onClick={() => onCardClick(registration)}
        />
      ))}
    </div>
  );
};
