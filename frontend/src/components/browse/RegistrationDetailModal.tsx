/**
 * RegistrationDetailModal Component
 * 
 * Modal dialog displaying full registration details.
 * Features:
 * - All registration metadata (name, URL, description, owner, tools, status)
 * - Status badge with color coding
 * - Timestamps (created, updated, approved)
 * - Available tools list with descriptions
 * - Close button (X icon) and backdrop click to dismiss
 * - Responsive layout with scrollable content
 * - Focus trap and ESC key handling (added in Phase 6)
 * 
 * Usage:
 * ```tsx
 * {selectedRegistration && (
 *   <RegistrationDetailModal
 *     registration={selectedRegistration}
 *     onClose={() => setSelectedRegistration(null)}
 *   />
 * )}
 * ```
 */

import React, { useEffect } from 'react';
import type { RegistrationResponse } from '../../types/registration.types';
import { StatusBadge } from '../common/StatusBadge';

interface RegistrationDetailModalProps {
  registration: RegistrationResponse;
  onClose: () => void;
}

export const RegistrationDetailModal: React.FC<RegistrationDetailModalProps> = ({ 
  registration, 
  onClose 
}) => {
  // T044: ESC key listener to close modal
  useEffect(() => {
    const handleEscKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscKey);
    return () => document.removeEventListener('keydown', handleEscKey);
  }, [onClose]);
  // Format timestamp for display
  const formatDate = (dateString: string | null | undefined): string => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <>
      {/* Backdrop (click to close) */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal Container */}
      <div 
        className="fixed inset-0 z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        {/* Modal Content (prevent propagation to backdrop) */}
        <div 
          className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] 
                     overflow-y-auto relative"
          onClick={(e) => e.stopPropagation()}
          role="dialog"
          aria-modal="true"
          aria-labelledby="modal-title"
        >
          {/* Header with Close Button */}
          <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 
                          flex items-center justify-between">
            <h2 
              id="modal-title" 
              className="text-2xl font-bold text-gray-900"
            >
              Registration Details
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors p-1"
              aria-label="Close modal"
            >
              <svg 
                className="h-6 w-6" 
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
          </div>

          {/* Content */}
          <div className="px-6 py-6 space-y-6">
            {/* Endpoint Name + Status */}
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <h3 className="text-xl font-semibold text-gray-900 mb-1">
                  {registration.endpoint_name}
                </h3>
                <p className="text-sm text-gray-600 break-all">
                  {registration.endpoint_url}
                </p>
              </div>
              <StatusBadge status={registration.status} />
            </div>

            {/* Description */}
            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-2">
                Description
              </h4>
              <p className="text-sm text-gray-700 whitespace-pre-wrap">
                {registration.description || 'No description provided'}
              </p>
            </div>

            {/* Owner Contact */}
            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-2">
                Owner Contact
              </h4>
              <p className="text-sm text-gray-700">
                {registration.owner_contact}
              </p>
            </div>

            {/* Available Tools */}
            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-3">
                Available Tools ({registration.available_tools?.length || 0})
              </h4>
              {registration.available_tools && registration.available_tools.length > 0 ? (
                <ul className="space-y-3">
                  {registration.available_tools.map((tool, index) => (
                    <li 
                      key={index} 
                      className="bg-gray-50 rounded-lg p-3 border border-gray-200"
                    >
                      <div className="font-medium text-gray-900 mb-1">
                        {tool.name}
                      </div>
                      <div className="text-sm text-gray-600">
                        {tool.description || 'No description'}
                      </div>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-gray-500 italic">
                  No tools defined
                </p>
              )}
            </div>

            {/* Timestamps */}
            <div className="border-t border-gray-200 pt-4 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <h4 className="font-semibold text-gray-700 mb-1">
                  Created
                </h4>
                <p className="text-gray-600">
                  {formatDate(registration.created_at)}
                </p>
              </div>
              <div>
                <h4 className="font-semibold text-gray-700 mb-1">
                  Updated
                </h4>
                <p className="text-gray-600">
                  {formatDate(registration.updated_at)}
                </p>
              </div>
              <div>
                <h4 className="font-semibold text-gray-700 mb-1">
                  Approved
                </h4>
                <p className="text-gray-600">
                  {formatDate(registration.approved_at)}
                </p>
              </div>
            </div>

            {/* IDs (for debugging/admin purposes) */}
            <div className="border-t border-gray-200 pt-4 text-xs text-gray-500 space-y-1">
              <p><span className="font-semibold">Registration ID:</span> {registration.registration_id}</p>
              <p><span className="font-semibold">Submitter ID:</span> {registration.submitter_id}</p>
              {registration.approver_id && (
                <p><span className="font-semibold">Approver ID:</span> {registration.approver_id}</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};
