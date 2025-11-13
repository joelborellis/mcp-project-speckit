/**
 * Pagination Component
 * 
 * Pagination controls for navigating through pages of results.
 * Features:
 * - Previous/Next buttons (disabled at boundaries)
 * - Page number buttons (shows max 7 pages with ellipsis)
 * - Current page highlighted in red
 * - Keyboard accessible
 * - Responsive design
 * 
 * Usage:
 * ```tsx
 * <Pagination 
 *   currentPage={currentPage}
 *   totalPages={totalPages}
 *   onPageChange={setCurrentPage}
 * />
 * ```
 * 
 * Page Number Display Logic:
 * - If totalPages <= 7: Show all page numbers
 * - If currentPage <= 4: Show [1,2,3,4,5,...,last]
 * - If currentPage >= totalPages-3: Show [1,...,n-4,n-3,n-2,n-1,n]
 * - Otherwise: Show [1,...,current-1,current,current+1,...,last]
 */

import React from 'react';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export const Pagination: React.FC<PaginationProps> = ({ 
  currentPage, 
  totalPages, 
  onPageChange 
}) => {
  // Don't render if only 1 page or no pages
  if (totalPages <= 1) {
    return null;
  }

  const handlePrevious = () => {
    if (currentPage > 1) {
      onPageChange(currentPage - 1);
    }
  };

  const handleNext = () => {
    if (currentPage < totalPages) {
      onPageChange(currentPage + 1);
    }
  };

  // Calculate which page numbers to display
  const getPageNumbers = (): (number | string)[] => {
    if (totalPages <= 7) {
      // Show all pages
      return Array.from({ length: totalPages }, (_, i) => i + 1);
    }

    if (currentPage <= 4) {
      // Near start: [1,2,3,4,5,...,last]
      return [1, 2, 3, 4, 5, '...', totalPages];
    }

    if (currentPage >= totalPages - 3) {
      // Near end: [1,...,n-4,n-3,n-2,n-1,n]
      return [
        1,
        '...',
        totalPages - 4,
        totalPages - 3,
        totalPages - 2,
        totalPages - 1,
        totalPages
      ];
    }

    // Middle: [1,...,current-1,current,current+1,...,last]
    return [
      1,
      '...',
      currentPage - 1,
      currentPage,
      currentPage + 1,
      '...',
      totalPages
    ];
  };

  const pageNumbers = getPageNumbers();

  return (
    <div className="flex items-center justify-center gap-2 mt-8">
      {/* Previous Button */}
      <button
        onClick={handlePrevious}
        disabled={currentPage === 1}
        className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 font-medium
                   hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed
                   transition-colors"
        aria-label="Previous page"
      >
        Previous
      </button>

      {/* Page Number Buttons */}
      <div className="flex items-center gap-1">
        {pageNumbers.map((pageNum, index) => {
          if (pageNum === '...') {
            // Ellipsis
            return (
              <span 
                key={`ellipsis-${index}`} 
                className="px-3 py-2 text-gray-500"
              >
                ...
              </span>
            );
          }

          const isCurrentPage = pageNum === currentPage;
          
          return (
            <button
              key={pageNum}
              onClick={() => onPageChange(pageNum as number)}
              className={`
                px-4 py-2 rounded-lg font-medium transition-colors
                ${isCurrentPage
                  ? 'bg-red-600 text-white'
                  : 'text-gray-700 hover:bg-gray-100 border border-gray-300'
                }
              `}
              aria-label={`Page ${pageNum}`}
              aria-current={isCurrentPage ? 'page' : undefined}
            >
              {pageNum}
            </button>
          );
        })}
      </div>

      {/* Next Button */}
      <button
        onClick={handleNext}
        disabled={currentPage === totalPages}
        className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 font-medium
                   hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed
                   transition-colors"
        aria-label="Next page"
      >
        Next
      </button>
    </div>
  );
};
