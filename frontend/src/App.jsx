import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { NotificationProvider } from './contexts/NotificationContext';
import { ProtectedRoute } from './components/common/ProtectedRoute';
import Login from './pages/Login';
import DashboardEmpleado from './pages/DashboardEmpleado';
import DashboardRH from './pages/DashboardRH';
import DashboardRoot from './pages/DashboardRoot';

function RedirectByRole() {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  if (user.role === 'USUARIO') return <Navigate to="/empleado" replace />;
  return <Navigate to="/rh" replace />;
}

function AppRoutes() {
  return (
    <NotificationProvider>
      <Routes>
        <Route path="/login" element={<Login />} />

        <Route path="/empleado/*" element={
          <ProtectedRoute allowedRoles={['USUARIO']}>
            <DashboardEmpleado />
          </ProtectedRoute>
        } />

        <Route path="/rh/*" element={
          <ProtectedRoute allowedRoles={['ADMIN', 'ROOT']}>
            <DashboardRH />
          </ProtectedRoute>
        } />

        <Route path="/admin/*" element={
          <ProtectedRoute allowedRoles={['ROOT']}>
            <DashboardRoot />
          </ProtectedRoute>
        } />

        <Route path="/" element={<RedirectByRole />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </NotificationProvider>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
