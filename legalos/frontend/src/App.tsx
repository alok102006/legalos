import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './lib/auth/AuthContext';
import AppShell from './design-system/layout/AppShell';
import Dashboard from './workspaces/contract-intelligence/pages/Dashboard';
import ContractDetail from './workspaces/contract-intelligence/pages/ContractDetail';
import VendorDashboard from './workspaces/vendor-intelligence/pages/Dashboard';
import NoticeDashboard from './workspaces/legal-notice-center/pages/Dashboard';
import NoticeDetail from './workspaces/legal-notice-center/pages/NoticeDetail';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppShell>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/contracts/:id" element={<ContractDetail />} />
            <Route path="/vendors" element={<VendorDashboard />} />
            <Route path="/notices" element={<NoticeDashboard />} />
            <Route path="/notices/:id" element={<NoticeDetail />} />
            {/* Fallback route */}
            <Route path="*" element={<Dashboard />} />
          </Routes>
        </AppShell>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
