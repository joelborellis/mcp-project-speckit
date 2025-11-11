import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { Layout } from './components/layout/Layout';
import { ProtectedRoute } from './components/common/ProtectedRoute';
import { RegisterPage } from './pages/RegisterPage';
import { MyRegistrationsPage } from './pages/MyRegistrationsPage';
import { AdminApprovalsPage } from './pages/AdminApprovalsPage';

// Placeholder pages (will be created in subsequent phases)
const BrowsePage = () => <div>Browse Page - Coming Soon</div>;
const LoginPage = () => <div>Login Page - Coming Soon</div>;

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginPage />} />
          
          {/* Protected routes with layout */}
          <Route element={<Layout />}>
            <Route path="/" element={<BrowsePage />} />
            <Route 
              path="/my-registrations" 
              element={
                <ProtectedRoute>
                  <MyRegistrationsPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/register" 
              element={
                <ProtectedRoute>
                  <RegisterPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/approvals" 
              element={
                <ProtectedRoute requireAdmin>
                  <AdminApprovalsPage />
                </ProtectedRoute>
              } 
            />
          </Route>
          
          {/* Catch-all redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;

