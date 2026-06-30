import { Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { PrivateRoute, AdminRoute } from './components/RouteGuard';
import Sidebar from './components/layout/Sidebar';
import TopBar from './components/layout/TopBar';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Transactions from './pages/Transactions';
import Fees from './pages/Fees';
import Reconciliation from './pages/Reconciliation';
import Merchants from './pages/Merchants';
import ApiKeys from './pages/ApiKeys';
import Users from './pages/Users';
import AuditLogs from './pages/AuditLogs';
import QrTest from './pages/QrTest';

function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden ml-60">
        <TopBar />
        <main className="flex-1 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Public route */}
        <Route path="/login" element={<Login />} />

        {/* Protected routes */}
        <Route
          path="/"
          element={
            <PrivateRoute>
              <AppLayout>
                <Dashboard />
              </AppLayout>
            </PrivateRoute>
          }
        />
        <Route
          path="/transactions"
          element={
            <PrivateRoute>
              <AppLayout>
                <Transactions />
              </AppLayout>
            </PrivateRoute>
          }
        />
        <Route
          path="/fees"
          element={
            <PrivateRoute>
              <AppLayout>
                <Fees />
              </AppLayout>
            </PrivateRoute>
          }
        />
        <Route
          path="/reconciliation"
          element={
            <PrivateRoute>
              <AppLayout>
                <Reconciliation />
              </AppLayout>
            </PrivateRoute>
          }
        />
        <Route
          path="/merchants"
          element={
            <PrivateRoute>
              <AppLayout>
                <Merchants />
              </AppLayout>
            </PrivateRoute>
          }
        />

        <Route
          path="/qr-test"
          element={
            <PrivateRoute>
              <AppLayout>
                <QrTest />
              </AppLayout>
            </PrivateRoute>
          }
        />

        {/* Admin-only routes */}
        <Route
          path="/api-keys"
          element={
            <AdminRoute>
              <AppLayout>
                <ApiKeys />
              </AppLayout>
            </AdminRoute>
          }
        />
        <Route
          path="/users"
          element={
            <AdminRoute>
              <AppLayout>
                <Users />
              </AppLayout>
            </AdminRoute>
          }
        />
        <Route
          path="/audit-logs"
          element={
            <AdminRoute>
              <AppLayout>
                <AuditLogs />
              </AppLayout>
            </AdminRoute>
          }
        />
      </Routes>
    </AuthProvider>
  );
}
