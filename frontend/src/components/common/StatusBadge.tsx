/**
 * StatusBadge Component
 * 
 * Reusable status indicator for registration approval statuses.
 * Used across Browse, My Registrations, and Admin Approvals pages.
 * 
 * Color scheme aligns with red/white theme from feature 001:
 * - Approved: Green accent (success)
 * - Pending: Yellow accent (warning)
 * - Rejected: Red accent (error) - aligns with red theme
 */

import React from 'react';

export type EndpointStatus = 'Pending' | 'Approved' | 'Rejected';

export interface StatusBadgeProps {
  status: EndpointStatus;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  // Color classes for each status
  const styles: Record<EndpointStatus, string> = {
    Pending: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    Approved: 'bg-green-100 text-green-800 border-green-200',
    Rejected: 'bg-red-100 text-red-800 border-red-200'
  };
  
  return (
    <span 
      className={`px-3 py-1 rounded-full text-xs font-semibold border ${styles[status]}`}
      aria-label={`Status: ${status}`}
    >
      {status}
    </span>
  );
};
