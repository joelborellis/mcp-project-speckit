# Research & Technical Decisions

**Feature**: MCP Registry Web Application  
**Date**: 2025-11-11  
**Purpose**: Document technology choices, patterns, and best practices for implementation

## 1. Microsoft Entra ID Authentication with MSAL

### Decision
Use **@azure/msal-browser** (^3.x) and **@azure/msal-react** (^2.x) for Microsoft Entra ID authentication in the React application.

### Rationale
- **Official Microsoft libraries**: First-party support ensures compatibility and security updates
- **React integration**: `@azure/msal-react` provides hooks (`useMsal`, `useIsAuthenticated`) and HOCs for seamless React integration
- **Security group support**: MSAL can retrieve user group memberships via Microsoft Graph API for role determination
- **Token management**: Automatic token acquisition, caching, and renewal
- **Well-documented**: Extensive Microsoft documentation and sample apps available

### Implementation Pattern
```typescript
// Configuration approach
const msalConfig = {
  auth: {
    clientId: import.meta.env.VITE_ENTRA_CLIENT_ID,
    authority: `https://login.microsoftonline.com/${import.meta.env.VITE_ENTRA_TENANT_ID}`,
    redirectUri: window.location.origin
  },
  cache: {
    cacheLocation: 'sessionStorage', // Prevents tokens persisting across browser sessions
    storeAuthStateInCookie: false
  }
};

// Group membership check for admin role
const checkAdminRole = async (instance, accounts) => {
  const request = {
    scopes: ['User.Read', 'GroupMember.Read.All'],
    account: accounts[0]
  };
  const response = await instance.acquireTokenSilent(request);
  // Call Microsoft Graph API to check group membership
  // Look for "MCP-Registry-Admins" group
};
```

### Alternatives Considered
- **Azure AD B2C**: Overkill for internal enterprise app, adds unnecessary complexity
- **Custom OAuth2**: Would require maintaining security implementation, violates Minimal Dependencies
- **Auth0/Okta**: Third-party cost and vendor lock-in, not needed when Entra ID is already available

### References
- [MSAL React Documentation](https://github.com/AzureAD/microsoft-authentication-library-for-js/tree/dev/lib/msal-react)
- [Microsoft Graph API - Check Member Groups](https://learn.microsoft.com/en-us/graph/api/user-checkmembergroups)

---

## 2. IndexedDB for Local Data Persistence

### Decision
Use **Dexie.js** (^4.x) as a wrapper around native IndexedDB for managing endpoint metadata.

### Rationale
- **IndexedDB advantages**: Structured storage, indexing, query capabilities, 50MB+ capacity (exceeds localStorage's 5-10MB)
- **Dexie.js benefits**:
  - Promise-based API (easier than IndexedDB's event-based API)
  - TypeScript support with strong typing
  - Automatic schema versioning and migrations
  - Query syntax similar to LINQ/MongoDB
  - Small footprint (~20KB minified+gzipped)
- **Constitutional alignment**: Well-maintained, focused library (Minimal Dependencies principle)

### Implementation Pattern
```typescript
// Schema definition
import Dexie, { Table } from 'dexie';

class MCPRegistryDB extends Dexie {
  endpoints!: Table<Endpoint, string>; // string = UUID type
  
  constructor() {
    super('MCPRegistryDB');
    this.version(1).stores({
      endpoints: 'id, status, *tools, submitterId, [status+submitterId]' // Indexes
    });
  }
}

const db = new MCPRegistryDB();

// Query examples
const approvedEndpoints = await db.endpoints
  .where('status').equals('Approved')
  .toArray();

const userEndpoints = await db.endpoints
  .where('[status+submitterId]').equals(['Pending', userId])
  .toArray();
```

### Alternatives Considered
- **localStorage**: Too limited in size (5-10MB), no structured queries, synchronous API
- **SessionStorage**: Clears on tab close, not suitable for persistent registry
- **Native IndexedDB**: Event-based API is verbose and error-prone compared to Dexie's promises
- **LowDB/LocalForage**: Less performant for structured queries, weaker TypeScript support

### References
- [Dexie.js Documentation](https://dexie.org/)
- [IndexedDB Best Practices (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API/Using_IndexedDB)

---

## 3. React Component Architecture & State Management

### Decision
Use **React Context API** with hooks for global state management (auth state, user role). Component-local state (useState) for UI interactions. No external state management library.

### Rationale
- **Minimal Dependencies principle**: Context API is built into React, no additional packages
- **Sufficient for scope**: 4 user stories with limited shared state (auth + current user role)
- **Clean Code principle**: Context keeps auth logic centralized and easily testable through component tree
- **Performance**: React 19 improvements make Context more performant for this scale

### Implementation Pattern
```typescript
// AuthContext for global auth state
export const AuthContext = createContext<AuthContextType>(null);

export const AuthProvider = ({ children }) => {
  const { instance, accounts, inProgress } = useMsal();
  const [isAdmin, setIsAdmin] = useState(false);
  
  useEffect(() => {
    if (accounts[0]) {
      checkAdminRole(instance, accounts).then(setIsAdmin);
    }
  }, [accounts, instance]);
  
  return (
    <AuthContext.Provider value={{ accounts, inProgress, isAdmin }}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook for consuming auth
export const useAuth = () => useContext(AuthContext);
```

### Alternatives Considered
- **Redux/Redux Toolkit**: Overkill for this application's state complexity, adds significant bundle size
- **Zustand/Jotai**: Unnecessary external dependency when Context API suffices
- **MobX**: Observer pattern adds complexity for simple auth/role state

### References
- [React Context Documentation](https://react.dev/reference/react/useContext)
- [React 19 Context Performance](https://react.dev/blog/2024/12/05/react-19#context-as-a-provider)

---

## 4. Form Handling & Validation

### Decision
Use **native HTML5 validation** enhanced with custom TypeScript validation functions. No form library.

### Rationale
- **Minimal Dependencies**: HTML5 validation is built-in, zero additional packages
- **Clean Code**: Custom validation functions are explicit, readable, and easily maintainable
- **Simple UX**: Browser-native validation messages are familiar to users
- **Sufficient complexity**: Only one form (registration) with 5 fields, doesn't justify React Hook Form/Formik overhead

### Implementation Pattern
```typescript
// Validation utility
export const validateEndpointURL = (url: string): string | null => {
  if (!url) return 'URL is required';
  try {
    const parsed = new URL(url);
    if (!['http:', 'https:'].includes(parsed.protocol)) {
      return 'URL must use HTTP or HTTPS protocol';
    }
    return null;
  } catch {
    return 'Invalid URL format';
  }
};

export const validateTools = (tools: string): string | null => {
  if (!tools.trim()) return 'At least one tool must be specified';
  return null;
};

// Component usage
const [errors, setErrors] = useState<Record<string, string>>({});

const handleSubmit = (e: React.FormEvent) => {
  e.preventDefault();
  const newErrors: Record<string, string> = {};
  
  const urlError = validateEndpointURL(formData.url);
  if (urlError) newErrors.url = urlError;
  
  if (Object.keys(newErrors).length > 0) {
    setErrors(newErrors);
    return;
  }
  
  // Submit logic...
};
```

### Alternatives Considered
- **React Hook Form**: Powerful but adds 24KB minified, overkill for single form
- **Formik**: Similar overhead, abandoned maintenance history
- **Yup/Zod schema validation**: Adds bundle size for validation that's simple enough to write manually

---

## 5. Responsive Design with Tailwind CSS

### Decision
Use **Tailwind CSS** (already in stack) with mobile-first approach and custom red/white theme configuration.

### Rationale
- **Already mandated**: Part of constitutional technology stack
- **Mobile-first**: Tailwind's breakpoint system (`sm:`, `md:`, `lg:`, `xl:`, `2xl:`) naturally supports 320px-1920px range
- **Minimal Dependencies**: Utility-first approach avoids additional component libraries
- **Responsive Design principle**: Built for responsive layouts with minimal custom CSS

### Implementation Pattern
```typescript
// tailwind.config.js
export default {
  theme: {
    extend: {
      colors: {
        primary: {
          red: '#DC2626', // Example - to be finalized
          white: '#FFFFFF'
        }
      },
      // Ensure touch targets meet 44x44px minimum
      minHeight: {
        'touch': '44px'
      },
      minWidth: {
        'touch': '44px'
      }
    }
  }
};

// Component usage - mobile-first
<button className="w-full sm:w-auto min-h-touch px-6 py-3 bg-primary-red text-white">
  Register Endpoint
</button>
```

### Alternatives Considered
- **Material-UI/Chakra UI**: Violates Minimal Dependencies, brings heavy component libraries
- **Custom CSS/SCSS**: More code to maintain, slower development than Tailwind utilities
- **Bootstrap**: Older paradigm, conflicts with React component model

### References
- [Tailwind CSS Responsive Design](https://tailwindcss.com/docs/responsive-design)
- [Tailwind Custom Colors](https://tailwindcss.com/docs/customizing-colors)

---

## 6. Routing Strategy

### Decision
Use **React Router v6** for client-side routing with protected route wrappers for authentication.

### Rationale
- **Industry standard**: Most widely used React routing library
- **Type-safe**: Excellent TypeScript support
- **Declarative**: Routes defined as JSX components align with React paradigm
- **Small footprint**: ~10KB minified+gzipped
- **Protected routes**: Easy to implement route guards for auth/admin checks

### Implementation Pattern
```typescript
// Route configuration
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children, requireAdmin = false }) => {
  const { accounts, isAdmin } = useAuth();
  
  if (!accounts[0]) {
    return <Navigate to="/login" replace />;
  }
  
  if (requireAdmin && !isAdmin) {
    return <Navigate to="/" replace />;
  }
  
  return children;
};

// App routes
<BrowserRouter>
  <Routes>
    <Route path="/" element={
      <ProtectedRoute>
        <Dashboard />
      </ProtectedRoute>
    } />
    <Route path="/register" element={
      <ProtectedRoute>
        <Register />
      </ProtectedRoute>
    } />
    <Route path="/admin/approvals" element={
      <ProtectedRoute requireAdmin>
        <AdminApprovals />
      </ProtectedRoute>
    } />
  </Routes>
</BrowserRouter>
```

### Alternatives Considered
- **TanStack Router**: Newer, less mature ecosystem
- **Wouter**: Too minimalist, missing features like nested routes
- **No router (manual hash routing)**: Violates Clean Code principle, hard to maintain

### References
- [React Router Documentation](https://reactrouter.com/)
- [Protected Routes Pattern](https://reactrouter.com/en/main/start/concepts#protected-routes)

---

## 7. Search & Filter Implementation

### Decision
Use **client-side filtering with Dexie compound indexes** for real-time search across endpoint name, owner, and tools.

### Rationale
- **Performance**: IndexedDB compound indexes enable sub-500ms queries even with 1000 endpoints
- **No backend dependency**: Aligns with frontend-only specification
- **Real-time UX**: Filter results as user types without API latency
- **Simple implementation**: Single query with `.where()` clause, no complex state management

### Implementation Pattern
```typescript
// Search service
export const searchEndpoints = async (query: string): Promise<Endpoint[]> => {
  const lowerQuery = query.toLowerCase();
  
  return db.endpoints
    .filter(endpoint => 
      endpoint.status === 'Approved' && (
        endpoint.name.toLowerCase().includes(lowerQuery) ||
        endpoint.owner.toLowerCase().includes(lowerQuery) ||
        endpoint.tools.some(tool => tool.toLowerCase().includes(lowerQuery))
      )
    )
    .toArray();
};

// Debounced search hook
const useEndpointSearch = (query: string) => {
  const [results, setResults] = useState<Endpoint[]>([]);
  
  useEffect(() => {
    const timer = setTimeout(async () => {
      if (query.length >= 2) {
        const found = await searchEndpoints(query);
        setResults(found);
      } else {
        setResults([]);
      }
    }, 300); // 300ms debounce
    
    return () => clearTimeout(timer);
  }, [query]);
  
  return results;
};
```

### Alternatives Considered
- **Fuse.js**: Fuzzy search library adds 15KB, unnecessary when exact/substring matching suffices
- **Lunr.js**: Full-text search engine overkill for simple name/owner/tool filtering
- **Backend API search**: Not available in this phase per specification

---

## 8. Date/Time Handling

### Decision
Use **native JavaScript Date with Intl.DateTimeFormat** for timestamp display. No date library.

### Rationale
- **Minimal Dependencies**: No external packages needed
- **Built-in localization**: Intl API provides locale-aware formatting
- **Sufficient functionality**: Only displaying timestamps, not complex date calculations

### Implementation Pattern
```typescript
// Formatting utility
export const formatTimestamp = (timestamp: number): string => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(timestamp));
};

// Usage
<span className="text-sm text-gray-600">
  Submitted: {formatTimestamp(endpoint.submissionTimestamp)}
</span>
```

### Alternatives Considered
- **date-fns**: Modular but adds bundle size for functionality we don't need
- **Day.js**: Lightweight but still unnecessary for simple timestamp display
- **Moment.js**: Deprecated and bloated

---

## 9. Error Handling & User Feedback

### Decision
Use **React Error Boundaries** for component errors, **toast notifications** (react-hot-toast - 3KB) for user feedback, and inline validation messages for forms.

### Rationale
- **Error Boundaries**: Built-in React feature for graceful component error handling
- **Toast library justified**: Very small footprint (3KB), significantly better UX than alerts
- **Simple UX principle**: Immediate feedback for user actions without page navigation

### Implementation Pattern
```typescript
// Error boundary
class ErrorBoundary extends React.Component<Props, State> {
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }
  
  render() {
    if (this.state.hasError) {
      return (
        <div className="p-6 text-center">
          <h2>Something went wrong</h2>
          <button onClick={() => window.location.reload()}>
            Reload Page
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

// Toast usage
import toast from 'react-hot-toast';

const handleApprove = async (endpointId: string) => {
  try {
    await approveEndpoint(endpointId);
    toast.success('Endpoint approved successfully');
  } catch (error) {
    toast.error('Failed to approve endpoint');
  }
};
```

### Alternatives Considered
- **No error boundaries**: Would result in white screen on errors, poor UX
- **Custom toast**: Reinventing wheel violates Clean Code principle
- **react-toastify**: Heavier (8KB), more features than needed

### References
- [React Error Boundaries](https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary)
- [react-hot-toast Documentation](https://react-hot-toast.com/)

---

## 10. Environment Configuration

### Decision
Use **Vite's environment variables** (import.meta.env) with .env files for Entra ID configuration.

### Rationale
- **Built into Vite**: No additional packages required
- **Type-safe**: Can extend vite-env.d.ts for TypeScript autocomplete
- **Secure**: Only VITE_ prefixed variables exposed to client code
- **Environment-specific**: .env.local for development, build-time substitution for production

### Implementation Pattern
```typescript
// vite-env.d.ts
interface ImportMetaEnv {
  readonly VITE_ENTRA_CLIENT_ID: string;
  readonly VITE_ENTRA_TENANT_ID: string;
  readonly VITE_ENTRA_ADMIN_GROUP_ID: string;
}

// .env.local (not committed)
VITE_ENTRA_CLIENT_ID=your-client-id-here
VITE_ENTRA_TENANT_ID=your-tenant-id-here
VITE_ENTRA_ADMIN_GROUP_ID=group-object-id-here

// Usage in code
const clientId = import.meta.env.VITE_ENTRA_CLIENT_ID;
```

### Alternatives Considered
- **dotenv**: Not needed, Vite handles .env natively
- **Hardcoded values**: Security risk, environment-specific configuration impossible
- **Config service**: Over-engineering for static configuration

### References
- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)

---

## Summary of Dependencies to Add

| Package | Version | Purpose | Bundle Size | Justification |
|---------|---------|---------|-------------|---------------|
| @azure/msal-browser | ^3.x | Entra ID auth | ~80KB | Required for auth, official Microsoft library |
| @azure/msal-react | ^2.x | React MSAL integration | ~15KB | First-party React bindings for MSAL |
| dexie | ^4.x | IndexedDB wrapper | ~20KB | Clean API for structured storage, TypeScript support |
| react-router-dom | ^6.x | Client-side routing | ~10KB | Industry standard, type-safe routing |
| react-hot-toast | ^2.x | Toast notifications | ~3KB | Minimal, excellent UX for feedback |

**Total Added Bundle Size**: ~128KB (minified+gzipped)

All additions align with **Minimal Dependencies** principle - each library is:
- Well-maintained with active development
- Focused on single responsibility
- Justified by significant complexity reduction or required functionality
- Small footprint relative to value provided
