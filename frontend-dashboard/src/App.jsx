import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router';
import { Layout } from './components/layout';
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="*" element={<div className="p-8 text-center text-gray-500">Feature Coming Soon</div>} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
