import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAuth } from '../hooks/useAuth';
import { createEndpoint, isURLUnique, APIError } from '../services/api.service';
import {
  validateRegistrationForm,
  sanitizeString,
  sanitizeURL,
  sanitizeToolsInput,
  VALIDATION_LIMITS,
  type RegistrationFormData,
} from '../utils/validation';
import { EndpointStatus, type MCPEndpoint } from '../types/endpoint.types';

/**
 * RegisterPage component
 * Form for registering new MCP endpoints
 */
export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { user, getAccessToken } = useAuth();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState<RegistrationFormData>({
    name: '',
    url: '',
    description: '',
    owner: '',
    tools: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!user) {
      toast.error('You must be logged in to register an endpoint');
      return;
    }

    // Validate form
    const validation = validateRegistrationForm(formData);
    if (!validation.isValid) {
      setErrors(validation.errors);
      toast.error('Please fix the errors in the form');
      return;
    }

    setIsSubmitting(true);

    try {
      // Get access token
      const token = await getAccessToken();

      // Check URL uniqueness
      const sanitizedUrl = sanitizeURL(formData.url);
      const isUnique = await isURLUnique(sanitizedUrl, token);
      
      if (!isUnique) {
        setErrors({ url: 'This URL is already registered' });
        toast.error('This URL is already registered');
        setIsSubmitting(false);
        return;
      }

      // Create endpoint object
      const endpoint: MCPEndpoint = {
        id: crypto.randomUUID(),
        name: sanitizeString(formData.name, VALIDATION_LIMITS.NAME_MAX_LENGTH),
        url: sanitizedUrl,
        description: sanitizeString(formData.description, VALIDATION_LIMITS.DESCRIPTION_MAX_LENGTH),
        owner: sanitizeString(formData.owner, VALIDATION_LIMITS.OWNER_MAX_LENGTH),
        tools: sanitizeToolsInput(formData.tools),
        status: EndpointStatus.Pending,
        submitterId: user.id,
        submitterName: user.displayName,
        submissionTimestamp: Date.now(),
        reviewerId: null,
        reviewerName: null,
        reviewTimestamp: null,
      };

      // Save to backend
      await createEndpoint(endpoint, token);
      
      toast.success('Endpoint registered successfully! Awaiting admin approval.');
      navigate('/my-registrations');
    } catch (error) {
      console.error('Failed to register endpoint:', error);
      
      // Handle specific API errors
      if (error instanceof APIError) {
        if (error.statusCode === 401 || error.statusCode === 403) {
          toast.error('Authentication failed. Please log in again.');
        } else if (error.statusCode === 409) {
          toast.error('This endpoint URL is already registered.');
          setErrors({ url: 'This URL is already registered' });
        } else if (error.statusCode >= 500) {
          toast.error('Server error. Please try again later.');
        } else {
          const errorMsg = typeof error.details === 'string' ? error.details : error.message;
          toast.error(errorMsg || 'Failed to register endpoint.');
        }
      } else {
        toast.error('Failed to register endpoint. Please check your connection.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Register MCP Endpoint</h1>
      
      <div className="bg-white shadow-md rounded-lg p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Name */}
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
              Endpoint Name <span className="text-primary-red">*</span>
            </label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              maxLength={VALIDATION_LIMITS.NAME_MAX_LENGTH}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-red focus:border-transparent ${
                errors.name ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="e.g., My MCP Server"
            />
            {errors.name && (
              <p className="mt-1 text-sm text-red-600">{errors.name}</p>
            )}
            <p className="mt-1 text-xs text-gray-500">
              {formData.name.length}/{VALIDATION_LIMITS.NAME_MAX_LENGTH} characters
            </p>
          </div>

          {/* URL */}
          <div>
            <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-2">
              Endpoint URL <span className="text-primary-red">*</span>
            </label>
            <input
              type="text"
              id="url"
              name="url"
              value={formData.url}
              onChange={handleChange}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-red focus:border-transparent ${
                errors.url ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="https://example.com/mcp"
            />
            {errors.url && (
              <p className="mt-1 text-sm text-red-600">{errors.url}</p>
            )}
            <p className="mt-1 text-xs text-gray-500">
              Must be a valid HTTP/HTTPS URL
            </p>
          </div>

          {/* Owner */}
          <div>
            <label htmlFor="owner" className="block text-sm font-medium text-gray-700 mb-2">
              Owner/Contact <span className="text-primary-red">*</span>
            </label>
            <input
              type="text"
              id="owner"
              name="owner"
              value={formData.owner}
              onChange={handleChange}
              maxLength={VALIDATION_LIMITS.OWNER_MAX_LENGTH}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-red focus:border-transparent ${
                errors.owner ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="e.g., team@example.com"
            />
            {errors.owner && (
              <p className="mt-1 text-sm text-red-600">{errors.owner}</p>
            )}
          </div>

          {/* Tools */}
          <div>
            <label htmlFor="tools" className="block text-sm font-medium text-gray-700 mb-2">
              Available Tools <span className="text-primary-red">*</span>
            </label>
            <input
              type="text"
              id="tools"
              name="tools"
              value={formData.tools}
              onChange={handleChange}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-red focus:border-transparent ${
                errors.tools ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="tool1, tool2, tool3"
            />
            {errors.tools && (
              <p className="mt-1 text-sm text-red-600">{errors.tools}</p>
            )}
            <p className="mt-1 text-xs text-gray-500">
              Comma-separated list of tools/capabilities
            </p>
          </div>

          {/* Description */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              maxLength={VALIDATION_LIMITS.DESCRIPTION_MAX_LENGTH}
              rows={4}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-red focus:border-transparent ${
                errors.description ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Describe the purpose and functionality of this endpoint..."
            />
            {errors.description && (
              <p className="mt-1 text-sm text-red-600">{errors.description}</p>
            )}
            <p className="mt-1 text-xs text-gray-500">
              {formData.description.length}/{VALIDATION_LIMITS.DESCRIPTION_MAX_LENGTH} characters
            </p>
          </div>

          {/* Submit Button */}
          <div className="flex gap-4">
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 bg-primary-red text-white py-3 px-6 rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {isSubmitting ? 'Registering...' : 'Register Endpoint'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/')}
              className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
