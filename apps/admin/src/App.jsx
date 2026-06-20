import React from 'react';
import { Route, Routes, BrowserRouter as Router, Navigate } from 'react-router-dom';
import { AuthProvider } from '@/contexts/AuthContext';
import { Toaster } from 'sonner';
import AdminRoute from '@/components/AdminRoute';
import AdminLayout from '@/layouts/AdminLayout';
import DashboardPage from '@/pages/DashboardPage';
import OrdersPage from '@/pages/OrdersPage';
import ProductsPage from '@/pages/ProductsPage';
import LoginPage from '@/pages/LoginPage';
import { useIdleTimeout } from '@/hooks/useIdleTimeout';

function AdminAppContent() {
  // Activa el cierre de sesión automático tras 30 minutos de inactividad
  useIdleTimeout(30 * 60 * 1000);

  return (
    <Routes>
      {/* Public Auth Routes */}
      <Route path="/login" element={<LoginPage />} />

      {/* Protected Administration Panel Routes */}
      <Route
        path="/"
        element={
          <AdminRoute>
            <AdminLayout />
          </AdminRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="orders" element={<OrdersPage />} />
        <Route path="products" element={<ProductsPage />} />
      </Route>

      {/* Catch-all Redirect */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AdminAppContent />
        <Toaster richColors position="top-right" closeButton />
      </AuthProvider>
    </Router>
  );
}

export default App;
