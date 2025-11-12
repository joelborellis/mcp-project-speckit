import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { ApprovalCard } from '../components/admin/ApprovalCard';
import { ConfirmDialog } from '../components/common/ConfirmDialog';
import { getPendingApprovals, updateEndpointStatus, deleteEndpoint, APIError } from '../services/api.service';
import { EndpointStatus } from '../types/endpoint.types';
import type { MCPEndpoint } from '../types/endpoint.types';
import toast from 'react-hot-toast';

interface ConfirmAction {
  type: 'approve' | 'reject' | 'remove';
  endpoint: MCPEndpoint;
}

/**
 * AdminApprovalsPage
 * Admin-only page for reviewing and managing endpoint registrations
 */
export const AdminApprovalsPage: React.FC = () => {
  const { user, getAccessToken } = useAuth();
  const [pendingEndpoints, setPendingEndpoints] = useState<MCPEndpoint[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [processingId, setProcessingId] = useState<string | null>(null);
  const [confirmAction, setConfirmAction] = useState<ConfirmAction | null>(null);

  // Load pending approvals
  useEffect(() => {
    loadPendingApprovals();
  }, []);

  const loadPendingApprovals = async () => {
    try {
      setIsLoading(true);
      const token = await getAccessToken();
      const endpoints = await getPendingApprovals(token);
      setPendingEndpoints(endpoints);
    } catch (error) {
      console.error('Failed to load pending approvals:', error);
      
      // Handle specific API errors
      if (error instanceof APIError) {
        if (error.statusCode === 401 || error.statusCode === 403) {
          toast.error('Authentication failed. You may not have admin access.');
        } else if (error.statusCode >= 500) {
          toast.error('Server error. Please try again later.');
        } else {
          const errorMsg = typeof error.details === 'string' ? error.details : error.message;
          toast.error(errorMsg || 'Failed to load pending approvals.');
        }
      } else {
        toast.error('Failed to load pending approvals. Please check your connection.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleApprove = (endpoint: MCPEndpoint) => {
    setConfirmAction({ type: 'approve', endpoint });
  };

  const handleReject = (endpoint: MCPEndpoint) => {
    setConfirmAction({ type: 'reject', endpoint });
  };

  const handleRemove = (endpoint: MCPEndpoint) => {
    setConfirmAction({ type: 'remove', endpoint });
  };

  const confirmApproval = async () => {
    if (!confirmAction || !user) return;

    const { endpoint } = confirmAction;
    setProcessingId(endpoint.id);
    setConfirmAction(null);

    try {
      const token = await getAccessToken();
      await updateEndpointStatus(
        endpoint.id,
        EndpointStatus.Approved,
        token
      );

      setPendingEndpoints((prev) => prev.filter((e) => e.id !== endpoint.id));
      toast.success(`Approved "${endpoint.name}"`);
    } catch (error) {
      console.error('Failed to approve endpoint:', error);
      
      // Handle specific API errors
      if (error instanceof APIError) {
        if (error.statusCode === 401 || error.statusCode === 403) {
          toast.error('Authentication failed. You may not have admin access.');
        } else if (error.statusCode === 404) {
          toast.error('Endpoint not found. It may have been deleted.');
          setPendingEndpoints((prev) => prev.filter((e) => e.id !== endpoint.id));
        } else if (error.statusCode >= 500) {
          toast.error('Server error. Please try again later.');
        } else {
          const errorMsg = typeof error.details === 'string' ? error.details : error.message;
          toast.error(errorMsg || 'Failed to approve endpoint.');
        }
      } else {
        toast.error('Failed to approve endpoint. Please check your connection.');
      }
    } finally {
      setProcessingId(null);
    }
  };

  const confirmRejection = async () => {
    if (!confirmAction || !user) return;

    const { endpoint } = confirmAction;
    setProcessingId(endpoint.id);
    setConfirmAction(null);

    try {
      const token = await getAccessToken();
      await updateEndpointStatus(
        endpoint.id,
        EndpointStatus.Rejected,
        token
      );

      setPendingEndpoints((prev) => prev.filter((e) => e.id !== endpoint.id));
      toast.success(`Rejected "${endpoint.name}"`);
    } catch (error) {
      console.error('Failed to reject endpoint:', error);
      
      // Handle specific API errors
      if (error instanceof APIError) {
        if (error.statusCode === 401 || error.statusCode === 403) {
          toast.error('Authentication failed. You may not have admin access.');
        } else if (error.statusCode === 404) {
          toast.error('Endpoint not found. It may have been deleted.');
          setPendingEndpoints((prev) => prev.filter((e) => e.id !== endpoint.id));
        } else if (error.statusCode >= 500) {
          toast.error('Server error. Please try again later.');
        } else {
          const errorMsg = typeof error.details === 'string' ? error.details : error.message;
          toast.error(errorMsg || 'Failed to reject endpoint.');
        }
      } else {
        toast.error('Failed to reject endpoint. Please check your connection.');
      }
    } finally {
      setProcessingId(null);
    }
  };

  const confirmRemoval = async () => {
    if (!confirmAction) return;

    const { endpoint } = confirmAction;
    setProcessingId(endpoint.id);
    setConfirmAction(null);

    try {
      const token = await getAccessToken();
      await deleteEndpoint(endpoint.id, token);
      setPendingEndpoints((prev) => prev.filter((e) => e.id !== endpoint.id));
      toast.success(`Removed "${endpoint.name}"`);
    } catch (error) {
      console.error('Failed to remove endpoint:', error);
      
      // Handle specific API errors
      if (error instanceof APIError) {
        if (error.statusCode === 401 || error.statusCode === 403) {
          toast.error('Authentication failed. You may not have admin access.');
        } else if (error.statusCode === 404) {
          toast.error('Endpoint not found. It may have been already removed.');
          setPendingEndpoints((prev) => prev.filter((e) => e.id !== endpoint.id));
        } else if (error.statusCode >= 500) {
          toast.error('Server error. Please try again later.');
        } else {
          const errorMsg = typeof error.details === 'string' ? error.details : error.message;
          toast.error(errorMsg || 'Failed to remove endpoint.');
        }
      } else {
        toast.error('Failed to remove endpoint. Please check your connection.');
      }
    } finally {
      setProcessingId(null);
    }
  };

  const handleConfirm = () => {
    if (!confirmAction) return;

    switch (confirmAction.type) {
      case 'approve':
        confirmApproval();
        break;
      case 'reject':
        confirmRejection();
        break;
      case 'remove':
        confirmRemoval();
        break;
    }
  };

  const handleCancel = () => {
    setConfirmAction(null);
  };

  if (!user) {
    return (
      <div className="container mx-auto px-4 py-8">
        <p className="text-center text-gray-600">Please log in to access this page.</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Pending Approvals</h1>
        <p className="text-gray-600">
          Review and approve endpoint registrations submitted by users
        </p>
      </div>

      {/* Loading state */}
      {isLoading && (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-red"></div>
        </div>
      )}

      {/* Empty state */}
      {!isLoading && pendingEndpoints.length === 0 && (
        <div className="text-center py-12">
          <svg
            className="mx-auto h-24 w-24 text-gray-400 mb-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">All Caught Up!</h2>
          <p className="text-gray-600 mb-6">There are no pending approvals at this time.</p>
        </div>
      )}

      {/* Approvals list */}
      {!isLoading && pendingEndpoints.length > 0 && (
        <div className="space-y-6">
          {pendingEndpoints.map((endpoint) => (
            <ApprovalCard
              key={endpoint.id}
              endpoint={endpoint}
              currentUserId={user.id}
              onApprove={handleApprove}
              onReject={handleReject}
              onRemove={handleRemove}
              isProcessing={processingId === endpoint.id}
            />
          ))}
        </div>
      )}

      {/* Confirmation dialog */}
      <ConfirmDialog
        isOpen={!!confirmAction}
        title={
          confirmAction?.type === 'approve'
            ? 'Approve Endpoint'
            : confirmAction?.type === 'reject'
            ? 'Reject Endpoint'
            : 'Remove Endpoint'
        }
        message={
          confirmAction?.type === 'approve'
            ? `Are you sure you want to approve "${confirmAction.endpoint.name}"?\n\nThis will make it visible to all users in the registry.`
            : confirmAction?.type === 'reject'
            ? `Are you sure you want to reject "${confirmAction.endpoint.name}"?\n\nThe submitter will see this rejection in their registrations.`
            : `Are you sure you want to permanently remove "${confirmAction?.endpoint.name}"?\n\nThis action cannot be undone.`
        }
        confirmText={
          confirmAction?.type === 'approve'
            ? 'Approve'
            : confirmAction?.type === 'reject'
            ? 'Reject'
            : 'Remove'
        }
        confirmButtonClass={
          confirmAction?.type === 'approve'
            ? 'bg-green-600 hover:bg-green-700'
            : 'bg-red-600 hover:bg-red-700'
        }
        onConfirm={handleConfirm}
        onCancel={handleCancel}
      />
    </div>
  );
};
