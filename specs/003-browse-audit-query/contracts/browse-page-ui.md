# Browse Page UI Specification

**Feature**: 003-browse-audit-query  
**Date**: 2025-11-12  
**Frontend**: React 19.2, TypeScript 5.9, Tailwind CSS 3.4

## Overview

Complete specification for the Browse page component hierarchy, layout, and interactions. The Browse page is the primary discovery interface for MCP server registrations.

---

## Component Hierarchy

```
BrowsePage (page component)
├── BrowseSearch (search input with debounce)
├── BrowseList (grid/list container)
│   ├── BrowseCard (registration card) × N
│   │   └── StatusBadge (status indicator)
│   └── EmptyState (shown when no results)
├── Pagination (page controls)
└── RegistrationDetailModal (detailed view overlay)
    └── StatusBadge (status indicator)
```

---

## Component Specifications

### BrowsePage (`/frontend/src/pages/BrowsePage.tsx`)

**Purpose**: Main page component at root path `/`

**State**:
```typescript
const [registrations, setRegistrations] = useState<MCPEndpoint[]>([]);
const [filteredRegistrations, setFilteredRegistrations] = useState<MCPEndpoint[]>([]);
const [searchQuery, setSearchQuery] = useState('');
const [currentPage, setCurrentPage] = useState(1);
const [selectedId, setSelectedId] = useState<string | null>(null);
const [isLoading, setIsLoading] = useState(true);
const [error, setError] = useState<string | null>(null);

const { user, getAccessToken } = useAuth(); // From AuthContext
const PAGE_SIZE = 20; // Constant per FR-005
```

**Data Fetching**:
```typescript
useEffect(() => {
  const fetchRegistrations = async () => {
    try {
      setIsLoading(true);
      const token = await getAccessToken();
      
      // Non-admin: only approved; Admin: all
      const filters = user?.isAdmin ? {} : { status: 'Approved' };
      
      const response = await getRegistrations(token, filters);
      setRegistrations(response.results);
      setFilteredRegistrations(response.results);
    } catch (err) {
      setError('Failed to load registrations');
      toast.error('Failed to load registrations');
    } finally {
      setIsLoading(false);
    }
  };
  
  fetchRegistrations();
}, [user?.isAdmin]);
```

**Filtering Logic**:
```typescript
useEffect(() => {
  if (!searchQuery.trim()) {
    setFilteredRegistrations(registrations);
    setCurrentPage(1); // Reset to page 1 on new search
    return;
  }
  
  const query = searchQuery.toLowerCase();
  const filtered = registrations.filter(reg =>
    reg.endpoint_name.toLowerCase().includes(query) ||
    reg.description?.toLowerCase().includes(query) ||
    reg.owner_contact.toLowerCase().includes(query)
  );
  
  setFilteredRegistrations(filtered);
  setCurrentPage(1); // Reset to page 1 on new search
}, [searchQuery, registrations]);
```

**Pagination**:
```typescript
const totalPages = Math.ceil(filteredRegistrations.length / PAGE_SIZE);
const paginatedResults = filteredRegistrations.slice(
  (currentPage - 1) * PAGE_SIZE,
  currentPage * PAGE_SIZE
);
```

**Layout**:
```tsx
return (
  <div className="container mx-auto px-4 py-8">
    <h1 className="text-3xl font-bold mb-6">Browse MCP Servers</h1>
    
    <BrowseSearch 
      value={searchQuery}
      onChange={setSearchQuery}
    />
    
    {isLoading ? (
      <div className="text-center py-12">Loading...</div>
    ) : error ? (
      <div className="text-red-600 text-center py-12">{error}</div>
    ) : (
      <>
        <BrowseList 
          registrations={paginatedResults}
          onCardClick={setSelectedId}
        />
        
        {totalPages > 1 && (
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
          />
        )}
      </>
    )}
    
    <RegistrationDetailModal
      isOpen={selectedId !== null}
      registration={registrations.find(r => r.registration_id === selectedId)}
      onClose={() => setSelectedId(null)}
    />
  </div>
);
```

---

### BrowseSearch (`/frontend/src/components/browse/BrowseSearch.tsx`)

**Purpose**: Search input with icon and clear button

**Props**:
```typescript
interface BrowseSearchProps {
  value: string;
  onChange: (value: string) => void;
}
```

**Layout**:
```tsx
export const BrowseSearch: React.FC<BrowseSearchProps> = ({ value, onChange }) => {
  return (
    <div className="mb-6">
      <div className="relative">
        <input
          type="text"
          placeholder="Search by name, description, or owner..."
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
        />
        
        {value && (
          <button
            onClick={() => onChange('')}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            aria-label="Clear search"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
};
```

**Accessibility**:
- Proper label/placeholder
- Clear button with aria-label
- Focus state visible

---

### BrowseList (`/frontend/src/components/browse/BrowseList.tsx`)

**Purpose**: Responsive grid container for registration cards

**Props**:
```typescript
interface BrowseListProps {
  registrations: MCPEndpoint[];
  onCardClick: (id: string) => void;
}
```

**Layout**:
```tsx
export const BrowseList: React.FC<BrowseListProps> = ({ registrations, onCardClick }) => {
  if (registrations.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p className="text-lg">No MCP servers registered yet.</p>
        <p className="mt-2">Be the first to register one!</p>
      </div>
    );
  }
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
      {registrations.map(registration => (
        <BrowseCard
          key={registration.registration_id}
          registration={registration}
          onClick={() => onCardClick(registration.registration_id)}
        />
      ))}
    </div>
  );
};
```

**Responsive Breakpoints**:
- Mobile (default): 1 column
- Tablet (md: 768px+): 2 columns
- Desktop (lg: 1024px+): 3 columns

---

### BrowseCard (`/frontend/src/components/browse/BrowseCard.tsx`)

**Purpose**: Individual registration card with key info

**Props**:
```typescript
interface BrowseCardProps {
  registration: MCPEndpoint;
  onClick: () => void;
}
```

**Layout**:
```tsx
export const BrowseCard: React.FC<BrowseCardProps> = ({ registration, onClick }) => {
  const truncateDescription = (text: string | undefined, maxLength: number = 150) => {
    if (!text) return 'No description provided';
    return text.length > maxLength ? text.slice(0, maxLength) + '...' : text;
  };
  
  return (
    <div
      onClick={onClick}
      className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow cursor-pointer"
    >
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-lg font-semibold text-gray-900 truncate pr-2">
          {registration.endpoint_name}
        </h3>
        <StatusBadge status={registration.status} />
      </div>
      
      <p className="text-sm text-gray-600 mb-3 break-all">
        {registration.endpoint_url}
      </p>
      
      <p className="text-sm text-gray-700 mb-3 line-clamp-3">
        {truncateDescription(registration.description)}
      </p>
      
      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>Owner: {registration.owner_contact}</span>
        <span>{new Date(registration.created_at).toLocaleDateString()}</span>
      </div>
    </div>
  );
};
```

**Styling Notes**:
- Card hover effect for click affordance
- Truncate long descriptions at 150 characters (FR-004)
- Status badge in top-right corner
- Break URL text to prevent overflow
- Line clamp description to 3 lines max

---

### StatusBadge (`/frontend/src/components/common/StatusBadge.tsx`)

**Purpose**: Reusable status indicator (used in Browse, My Registrations, Admin Approvals)

**Props**:
```typescript
interface StatusBadgeProps {
  status: EndpointStatus; // 'Pending' | 'Approved' | 'Rejected'
}
```

**Layout**:
```tsx
export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const styles = {
    Pending: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    Approved: 'bg-green-100 text-green-800 border-green-200',
    Rejected: 'bg-red-100 text-red-800 border-red-200'
  };
  
  return (
    <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${styles[status]}`}>
      {status}
    </span>
  );
};
```

**Color Scheme** (red/white theme from feature 001):
- Approved: Green accent (success)
- Pending: Yellow accent (warning)
- Rejected: Red accent (error) - aligns with red theme

---

### Pagination (`/frontend/src/components/browse/Pagination.tsx`)

**Purpose**: Page number controls with prev/next buttons

**Props**:
```typescript
interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}
```

**Layout**:
```tsx
export const Pagination: React.FC<PaginationProps> = ({ 
  currentPage, 
  totalPages, 
  onPageChange 
}) => {
  const pages = Array.from({ length: totalPages }, (_, i) => i + 1);
  
  // Show max 7 page numbers: [1] ... [4] [5] [6] ... [10]
  const getVisiblePages = () => {
    if (totalPages <= 7) return pages;
    
    if (currentPage <= 3) {
      return [...pages.slice(0, 5), '...', totalPages];
    }
    
    if (currentPage >= totalPages - 2) {
      return [1, '...', ...pages.slice(totalPages - 5)];
    }
    
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
  
  return (
    <div className="flex justify-center items-center gap-2 mt-8">
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
      >
        Previous
      </button>
      
      {getVisiblePages().map((page, index) => (
        page === '...' ? (
          <span key={`ellipsis-${index}`} className="px-2">...</span>
        ) : (
          <button
            key={page}
            onClick={() => typeof page === 'number' && onPageChange(page)}
            className={`px-4 py-2 border rounded-lg ${
              currentPage === page
                ? 'bg-red-600 text-white border-red-600'
                : 'hover:bg-gray-50'
            }`}
          >
            {page}
          </button>
        )
      ))}
      
      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        className="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
      >
        Next
      </button>
    </div>
  );
};
```

**Features**:
- Previous/Next buttons with disabled state
- Current page highlighted in red (theme color)
- Ellipsis for large page counts
- Keyboard accessible

---

### RegistrationDetailModal (`/frontend/src/components/browse/RegistrationDetailModal.tsx`)

**Purpose**: Modal overlay showing full registration details

**Props**:
```typescript
interface RegistrationDetailModalProps {
  isOpen: boolean;
  registration: MCPEndpoint | undefined;
  onClose: () => void;
}
```

**Layout**:
```tsx
export const RegistrationDetailModal: React.FC<RegistrationDetailModalProps> = ({
  isOpen,
  registration,
  onClose
}) => {
  if (!isOpen || !registration) return null;
  
  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div 
        className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="border-b px-6 py-4 flex justify-between items-start">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              {registration.endpoint_name}
            </h2>
            <p className="text-sm text-gray-600 mt-1 break-all">
              {registration.endpoint_url}
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
            aria-label="Close modal"
          >
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
        
        {/* Body */}
        <div className="px-6 py-4 space-y-4">
          {/* Status */}
          <div>
            <label className="text-sm font-semibold text-gray-700">Status</label>
            <div className="mt-1">
              <StatusBadge status={registration.status} />
            </div>
          </div>
          
          {/* Description */}
          <div>
            <label className="text-sm font-semibold text-gray-700">Description</label>
            <p className="mt-1 text-gray-900">
              {registration.description || 'No description provided'}
            </p>
          </div>
          
          {/* Owner */}
          <div>
            <label className="text-sm font-semibold text-gray-700">Owner Contact</label>
            <p className="mt-1 text-gray-900">{registration.owner_contact}</p>
          </div>
          
          {/* Available Tools */}
          <div>
            <label className="text-sm font-semibold text-gray-700">Available Tools</label>
            <div className="mt-2 flex flex-wrap gap-2">
              {registration.available_tools.map((tool, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-gray-100 border border-gray-300 rounded-full text-sm"
                >
                  {tool.name}
                </span>
              ))}
            </div>
          </div>
          
          {/* Submission Info */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-semibold text-gray-700">Submitted By</label>
              <p className="mt-1 text-gray-900">{registration.submitter_email || 'N/A'}</p>
            </div>
            <div>
              <label className="text-sm font-semibold text-gray-700">Submitted On</label>
              <p className="mt-1 text-gray-900">
                {new Date(registration.created_at).toLocaleString()}
              </p>
            </div>
          </div>
          
          {/* Approval Info (if approved/rejected) */}
          {(registration.status === 'Approved' || registration.status === 'Rejected') && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-semibold text-gray-700">
                  {registration.status === 'Approved' ? 'Approved By' : 'Rejected By'}
                </label>
                <p className="mt-1 text-gray-900">{registration.approver_email || 'N/A'}</p>
              </div>
              <div>
                <label className="text-sm font-semibold text-gray-700">
                  {registration.status === 'Approved' ? 'Approved On' : 'Rejected On'}
                </label>
                <p className="mt-1 text-gray-900">
                  {registration.approved_at 
                    ? new Date(registration.approved_at).toLocaleString()
                    : 'N/A'
                  }
                </p>
              </div>
            </div>
          )}
        </div>
        
        {/* Footer */}
        <div className="border-t px-6 py-4 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
```

**Features**:
- Full-screen overlay with backdrop click to close
- Scrollable content area for long descriptions
- All metadata displayed (FR-008)
- Responsive max-width with padding
- Close button in header and footer
- ESC key to close (add useEffect with keydown listener)

---

## Routing Configuration

Update `frontend/src/App.tsx`:

```tsx
// Replace placeholder BrowsePage
import { BrowsePage } from './pages/BrowsePage';

// In Routes:
<Route path="/" element={<BrowsePage />} />
```

**Note**: BrowsePage is already in the route as a placeholder. Replace the placeholder component with the real implementation.

---

## API Service Updates

Update `frontend/src/services/api.service.ts`:

```typescript
// Add new function for query by URL
export async function getRegistrationByUrl(
  token: string,
  endpointUrl: string
): Promise<MCPEndpoint> {
  const response = await fetch(
    `${API_BASE_URL}/registrations/by-url?endpoint_url=${encodeURIComponent(endpointUrl)}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
  );
  
  if (!response.ok) {
    if (response.status === 404) {
      throw new APIError('Registration not found', 404);
    }
    throw new APIError('Failed to fetch registration', response.status);
  }
  
  return response.json();
}

// Add new function for audit logs (admin only)
export async function getAuditLogs(
  token: string,
  filters: {
    registration_id?: string;
    user_id?: string;
    action?: string;
    from?: string;
    to?: string;
    limit?: number;
    offset?: number;
  } = {}
): Promise<AuditLogListResponse> {
  const params = new URLSearchParams();
  
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined) {
      params.append(key, String(value));
    }
  });
  
  const response = await fetch(
    `${API_BASE_URL}/audit-logs?${params.toString()}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
  );
  
  if (!response.ok) {
    if (response.status === 403) {
      throw new APIError('Admin privileges required', 403);
    }
    throw new APIError('Failed to fetch audit logs', response.status);
  }
  
  return response.json();
}
```

---

## Accessibility

All components must meet WCAG 2.1 AA standards:

- **Keyboard Navigation**: All interactive elements focusable and operable via keyboard
- **Focus Indicators**: Visible focus states on all buttons/links
- **ARIA Labels**: Meaningful labels on icon buttons (search clear, modal close)
- **Color Contrast**: Text meets 4.5:1 contrast ratio
- **Screen Readers**: Status badges, cards, and modals properly announced
- **Semantic HTML**: Proper heading hierarchy (h1 → h2 → h3)

---

## Performance

- **Initial Load**: <2 seconds for first 20 registrations (SC-002)
- **Search/Filter**: <500ms response time (SC-009)
- **Pagination**: Instant (client-side slicing)
- **Modal Open**: <1 second (SC-006)
- **Image Optimization**: N/A (no images in this feature)

---

## Mobile Responsiveness

**Touch Targets**: All buttons and cards minimum 44×44px (FR-010)

**Breakpoint Behavior**:
- **320px-767px (Mobile)**:
  - Cards stack vertically (1 column)
  - Modal fullscreen
  - Search input full width
  - Pagination controls stack if needed
  
- **768px-1023px (Tablet)**:
  - Cards in 2 columns
  - Modal 2/3 width
  - Search input constrained
  
- **1024px+ (Desktop)**:
  - Cards in 3 columns
  - Modal 1/2 width
  - Optimal layout

**Testing Viewports**:
- iPhone SE (375px)
- iPad (768px)
- MacBook (1440px)

---

## Summary

**New Components**: 6
- BrowsePage (page)
- BrowseSearch
- BrowseList
- BrowseCard
- Pagination
- RegistrationDetailModal

**Shared Component**: 1
- StatusBadge (reusable across pages)

**API Functions**: 2 new
- getRegistrationByUrl()
- getAuditLogs()

**Routes Updated**: 1
- `/` - Browse page (replace placeholder)

**Lines of Code Estimate**: 500-800 LOC total
