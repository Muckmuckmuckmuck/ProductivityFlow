import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import TeamManagement from './pages/TeamManagement';
import Billing from './pages/Billing';
import Compliance from './pages/Compliance';
import Analytics from './pages/Analytics';
import ErrorBoundary from './components/ErrorBoundary';
import { AuthView } from './components/AuthView';
import './styles.css';

interface ManagerSession {
  managerId: string;
  managerName: string;
  organization: string;
  token: string;
  isOwner: boolean;
  ownerCode: string | null;
  managerCode: string | null;
}

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [session, setSession] = useState<ManagerSession | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing session in localStorage
    const savedSession = localStorage.getItem('managerSession');
    if (savedSession) {
      try {
        const sessionData = JSON.parse(savedSession);
        setSession(sessionData);
      } catch (error) {
        console.error('Failed to parse saved session:', error);
        localStorage.removeItem('managerSession');
      }
    }
    setIsLoading(false);
  }, []);

  const handleLoginSuccess = (sessionData: ManagerSession) => {
    setSession(sessionData);
    localStorage.setItem('managerSession', JSON.stringify(sessionData));
  };

  const handleLogout = () => {
    setSession(null);
    localStorage.removeItem('managerSession');
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!session) {
    return <AuthView onAuthSuccess={handleLoginSuccess} />;
  }

  return (
    <ErrorBoundary>
      <Router>
        <div className="flex h-screen bg-gray-50">
          <Sidebar 
            isOpen={sidebarOpen} 
            onToggle={() => setSidebarOpen(!sidebarOpen)} 
            onLogout={handleLogout}
            managerName={session.managerName}
            organization={session.organization}
            isOwner={session.isOwner}
          />
          
          <main className="flex-1 overflow-auto">
            <Routes>
              <Route path="/" element={<Dashboard session={session} />} />
              <Route path="/team" element={<TeamManagement />} />
              <Route path="/billing" element={session.isOwner ? <Billing /> : <div className="p-8 text-center">Access denied. Owner access required.</div>} />
              <Route path="/compliance" element={<Compliance />} />
              <Route path="/analytics" element={<Analytics />} />
            </Routes>
          </main>
        </div>
      </Router>
    </ErrorBoundary>
  );
}

export default App;