/**
 * Formatting utility functions
 * FR-020: Timestamp display for submission/review dates
 */

/**
 * Format Unix timestamp to human-readable date/time string
 * @param timestamp Unix timestamp in milliseconds
 * @returns Formatted string like "Jan 15, 2025 at 2:30 PM"
 */
export function formatTimestamp(timestamp: number | null): string {
  if (!timestamp) {
    return 'N/A';
  }
  
  const date = new Date(timestamp);
  
  // Format: "Jan 15, 2025 at 2:30 PM"
  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  };
  
  return date.toLocaleString('en-US', options).replace(',', ' at');
}

/**
 * Format Unix timestamp to short date string
 * @param timestamp Unix timestamp in milliseconds
 * @returns Formatted string like "Jan 15, 2025"
 */
export function formatDate(timestamp: number | null): string {
  if (!timestamp) {
    return 'N/A';
  }
  
  const date = new Date(timestamp);
  
  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  };
  
  return date.toLocaleDateString('en-US', options);
}

/**
 * Format Unix timestamp to relative time string
 * @param timestamp Unix timestamp in milliseconds
 * @returns Formatted string like "2 hours ago" or "3 days ago"
 */
export function formatRelativeTime(timestamp: number | null): string {
  if (!timestamp) {
    return 'N/A';
  }
  
  const now = Date.now();
  const diff = now - timestamp;
  
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  const weeks = Math.floor(days / 7);
  const months = Math.floor(days / 30);
  const years = Math.floor(days / 365);
  
  if (seconds < 60) {
    return 'just now';
  } else if (minutes < 60) {
    return `${minutes} ${minutes === 1 ? 'minute' : 'minutes'} ago`;
  } else if (hours < 24) {
    return `${hours} ${hours === 1 ? 'hour' : 'hours'} ago`;
  } else if (days < 7) {
    return `${days} ${days === 1 ? 'day' : 'days'} ago`;
  } else if (weeks < 4) {
    return `${weeks} ${weeks === 1 ? 'week' : 'weeks'} ago`;
  } else if (months < 12) {
    return `${months} ${months === 1 ? 'month' : 'months'} ago`;
  } else {
    return `${years} ${years === 1 ? 'year' : 'years'} ago`;
  }
}

/**
 * Truncate text to specified length with ellipsis
 * @param text Text to truncate
 * @param maxLength Maximum length before truncation
 * @returns Truncated text with "..." if needed
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) {
    return text;
  }
  
  return text.slice(0, maxLength - 3) + '...';
}
