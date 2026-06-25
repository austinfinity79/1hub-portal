import { Routes, Route } from 'react-router-dom';
import Sidebar from './components/layout/Sidebar';
import TopBar from './components/layout/TopBar';
import Dashboard from './pages/Dashboard';
import Transactions from './pages/Transactions';
import Fees from './pages/Fees';
import Reconciliation from './pages/Reconciliation';
import Merchants from './pages/Merchants';

export default function App() {
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden ml-60">
        <TopBar />
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/transactions" element={<Transactions />} />
            <Route path="/fees" element={<Fees />} />
            <Route path="/reconciliation" element={<Reconciliation />} />
            <Route path="/merchants" element={<Merchants />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}
