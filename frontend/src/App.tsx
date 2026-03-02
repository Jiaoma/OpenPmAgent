import { useEffect } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import Layout from './components/Layout';
import Login from './pages/Login';
import TeamPages from './pages/Team';
import BackupPage from './pages/Backup';

// Protected Route Component
const ProtectedRoute = ({ children, isAdmin = false }: { children: React.ReactNode; isAdmin?: boolean }) => {
  const { isAuthenticated, isAdmin: isUserAdmin, fetchUser } = useAuthStore();
  const location = useLocation();

  useEffect(() => {
    if (isAuthenticated) {
      fetchUser();
    }
  }, [isAuthenticated, fetchUser]);

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (isAdmin && !isUserAdmin) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
};

function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<Login />} />
      
      {/* Protected routes */}
      <Route element={<Layout />}>
        <Route path="/" element={<ProtectedRoute><div>Dashboard</div></ProtectedRoute>} />
        <Route path="/team/*" element={<TeamPages />} />
        <Route path="/backup" element={<ProtectedRoute isAdmin={true}><BackupPage /></ProtectedRoute>} />
      </Route>

      {/* Default redirect */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
