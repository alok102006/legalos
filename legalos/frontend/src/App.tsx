import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './lib/auth/AuthContext';
import AppShell from './design-system/layout/AppShell';
import Dashboard from './workspaces/contract-intelligence/pages/Dashboard';
import ContractDetail from './workspaces/contract-intelligence/pages/ContractDetail';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppShell>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/contracts/:id" element={<ContractDetail />} />
            {/* Fallback route */}
            <Route path="*" element={<Dashboard />} />
          </Routes>
        </AppShell>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
