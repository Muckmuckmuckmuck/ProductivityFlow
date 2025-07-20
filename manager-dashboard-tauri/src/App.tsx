import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import TeamManagement from './pages/TeamManagement';
import Analytics from './pages/Analytics';
import Compliance from './pages/Compliance';
import Billing from './pages/Billing';
import ErrorBoundary from './components/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <div className="flex h-screen bg-gray-100">
          <Sidebar />
          <main className="flex-1 overflow-auto">
            <div className="p-8">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/team" element={<TeamManagement />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/compliance" element={<Compliance />} />
                <Route path="/billing" element={<Billing />} />
              </Routes>
            </div>
          </main>
        </div>
      </Router>
    </ErrorBoundary>
  );
}

export default App;