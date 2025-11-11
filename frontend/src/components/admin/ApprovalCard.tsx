import React from 'react';
import type { MCPEndpoint } from '../../types/endpoint.types';
import { formatTimestamp } from '../../utils/formatting';

interface ApprovalCardProps {
  endpoint: MCPEndpoint;
  currentUserId: string;
  onApprove: (endpoint: MCPEndpoint) => void;
  onReject: (endpoint: MCPEndpoint) => void;
  onRemove?: (endpoint: MCPEndpoint) => void;
  isProcessing?: boolean;
}

/**
 * ApprovalCard component
 * Displays an endpoint with approval/rejection/removal actions
 * Prevents self-review per FR-011
 */
export const ApprovalCard: React.FC<ApprovalCardProps> = ({
  endpoint,
  currentUserId,
  onApprove,
  onReject,
  onRemove,
  isProcessing = false,
}) => {
  const isSelfSubmission = endpoint.submitterId === currentUserId;
  const isPending = endpoint.status === 'Pending';
  const isApproved = endpoint.status === 'Approved';

  return (
    <div className="bg-white border-2 border-gray-200 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
      {/* Header with status badge */}
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-xl font-bold text-gray-900 mb-1">{endpoint.name}</h3>
          <p className="text-sm text-gray-600">
            Submitted by <span className="font-medium">{endpoint.submitterName}</span> on{' '}
            {formatTimestamp(endpoint.submissionTimestamp)}
          </p>
        </div>
        <span
          className={`px-3 py-1 rounded-full text-sm font-semibold ${
            endpoint.status === 'Pending'
              ? 'bg-yellow-100 text-yellow-800'
              : endpoint.status === 'Approved'
              ? 'bg-green-100 text-green-800'
              : 'bg-red-100 text-red-800'
          }`}
        >
          {endpoint.status}
        </span>
      </div>

      {/* Endpoint details */}
      <div className="space-y-3 mb-4">
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1">URL</label>
          <a
            href={endpoint.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary-red hover:underline break-all"
          >
            {endpoint.url}
          </a>
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1">Owner</label>
          <p className="text-gray-900">{endpoint.owner}</p>
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1">Tools</label>
          <div className="flex flex-wrap gap-2">
            {endpoint.tools.map((tool, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
              >
                {tool}
              </span>
            ))}
          </div>
        </div>

        {endpoint.description && (
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">Description</label>
            <p className="text-gray-700 whitespace-pre-wrap">{endpoint.description}</p>
          </div>
        )}
      </div>

      {/* Review information (if reviewed) */}
      {endpoint.reviewTimestamp && (
        <div className="mb-4 p-3 bg-gray-50 rounded border border-gray-200">
          <p className="text-sm text-gray-600">
            Reviewed by <span className="font-medium">{endpoint.reviewerName}</span> on{' '}
            {formatTimestamp(endpoint.reviewTimestamp)}
          </p>
        </div>
      )}

      {/* Self-review warning */}
      {isSelfSubmission && isPending && (
        <div className="mb-4 p-3 bg-yellow-50 rounded border border-yellow-200">
          <p className="text-sm text-yellow-800">
            ⚠️ You cannot approve or reject your own submission
          </p>
        </div>
      )}

      {/* Action buttons */}
      <div className="flex gap-3 mt-4">
        {isPending && (
          <>
            <button
              onClick={() => onApprove(endpoint)}
              disabled={isSelfSubmission || isProcessing}
              className={`flex-1 py-2 px-4 rounded font-semibold transition-colors min-h-touch ${
                isSelfSubmission || isProcessing
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-green-600 text-white hover:bg-green-700'
              }`}
            >
              {isProcessing ? 'Processing...' : '✓ Approve'}
            </button>
            <button
              onClick={() => onReject(endpoint)}
              disabled={isSelfSubmission || isProcessing}
              className={`flex-1 py-2 px-4 rounded font-semibold transition-colors min-h-touch ${
                isSelfSubmission || isProcessing
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-red-600 text-white hover:bg-red-700'
              }`}
            >
              {isProcessing ? 'Processing...' : '✗ Reject'}
            </button>
          </>
        )}

        {isApproved && onRemove && (
          <button
            onClick={() => onRemove(endpoint)}
            disabled={isProcessing}
            className={`flex-1 py-2 px-4 rounded font-semibold transition-colors min-h-touch ${
              isProcessing
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-red-600 text-white hover:bg-red-700'
            }`}
          >
            {isProcessing ? 'Processing...' : 'Remove'}
          </button>
        )}
      </div>
    </div>
  );
};
