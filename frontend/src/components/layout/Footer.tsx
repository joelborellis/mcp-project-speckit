import React from 'react';

/**
 * Footer component
 * Application footer with copyright information
 */
export const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-100 border-t border-gray-200 py-6 mt-auto">
      <div className="container mx-auto px-4">
        <div className="text-center text-gray-600 text-sm">
          <p>© {currentYear} {import.meta.env.VITE_APP_NAME || 'MCP Registry'}. All rights reserved.</p>
          <p className="mt-2">Model Context Protocol Registry Application</p>
        </div>
      </div>
    </footer>
  );
};
