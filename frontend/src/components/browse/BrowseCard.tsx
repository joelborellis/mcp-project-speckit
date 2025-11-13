/**
 * BrowseCard Component
 * 
 * Card component displaying registration summary in browse grid.
 * Features:
 * - Endpoint name and URL
 * - Truncated description (3 lines max)
 * - Status badge (Pending/Approved/Rejected)
 * - Owner contact info
 * - Available tools count
 * - Click to open detailed modal
 * - Hover effect with scale transform
 * - Red/white theme with border accent
 * 
 * Usage:
 * ```tsx
 * <BrowseCard 
 *   registration={registration} 
 *   onClick={() => setSelectedReg(registration)} 
 * />
 * ```
 */

import React from 'react';
import type { RegistrationResponse } from '../../types/registration.types';
import { StatusBadge } from '../common/StatusBadge';

interface BrowseCardProps {
  registration: RegistrationResponse;
  onClick: () => void;
}

export const BrowseCard: React.FC<BrowseCardProps> = ({ registration, onClick }) => {
  return (
    <div
      onClick={onClick}
      className="bg-white border border-gray-200 rounded-lg p-5 
                 hover:shadow-lg hover:scale-[1.02] hover:border-red-300
                 transition-all duration-200 cursor-pointer
                 flex flex-col gap-3"
    >
      {/* Header: Name + Status Badge */}
      <div className="flex items-start justify-between gap-3">
        <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">
          {registration.endpoint_name}
        </h3>
        <StatusBadge status={registration.status} />
      </div>

      {/* Endpoint URL */}
      <div className="text-sm text-gray-600 truncate" title={registration.endpoint_url}>
        <span className="font-medium text-gray-700">URL:</span>{' '}
        {registration.endpoint_url}
      </div>

      {/* Description (truncated to 3 lines) */}
      <p className="text-sm text-gray-700 line-clamp-3">
        {registration.description || 'No description provided'}
      </p>

      {/* Footer: Owner + Tools Count */}
      <div className="mt-auto pt-3 border-t border-gray-100 flex items-center justify-between text-sm">
        <div className="text-gray-600">
          <span className="font-medium text-gray-700">Owner:</span>{' '}
          {registration.owner_contact}
        </div>
        <div className="text-gray-600">
          <span className="font-medium text-gray-700">Tools:</span>{' '}
          {registration.available_tools?.length || 0}
        </div>
      </div>
    </div>
  );
};
