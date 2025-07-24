import { useState, useEffect } from "react";
import ErrorBoundary from "./components/ErrorBoundary";
import { OnboardingView } from "./components/OnboardingView";
import TrackingView from "./components/TrackingView";
import { AuthView } from "./components/AuthView";

interface Session {
  teamId: string;
  teamName: string;
  userId: string;
  userName: string;
  role: string;
  token: string;
}

interface EmployeeSession {
  employeeId: string;
  employeeName: string;
  teamId: string;
  teamName: string;
  token: string;
}

export default function App() {
  const [session, setSession] = useState<Session | null>(null);
  const [employeeSession, setEmployeeSession] = useState<EmployeeSession | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showLogin, setShowLogin] = useState(false);

  useEffect(() => {
    // Load saved session on app start
    const loadSession = async () => {
      try {
        const savedSession = localStorage.getItem("tracker_session");
        const savedEmployeeSession = localStorage.getItem("employee_session");
        
        if (savedEmployeeSession) {
          const sessionData = JSON.parse(savedEmployeeSession);
          setEmployeeSession(sessionData);
        } else if (savedSession) {
          const sessionData = JSON.parse(savedSession);
          setSession(sessionData);
        }
      } catch (error) {
        console.error("Error loading session:", error);
        localStorage.removeItem("tracker_session");
        localStorage.removeItem("employee_session");
      } finally {
        setIsLoading(false);
      }
    };

    loadSession();
  }, []);

  const handleTeamJoin = (sessionData: Session) => {
    setSession(sessionData);
    localStorage.setItem("tracker_session", JSON.stringify(sessionData));
  };

  const handleLoginSuccess = (sessionData: EmployeeSession) => {
    setEmployeeSession(sessionData);
    localStorage.setItem("employee_session", JSON.stringify(sessionData));
  };

  const handleLogout = () => {
    setSession(null);
    setEmployeeSession(null);
    localStorage.removeItem("tracker_session");
    localStorage.removeItem("employee_session");
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50">
        {!session && !employeeSession ? (
          <div className="flex flex-col items-center justify-center min-h-screen p-4">
            <div className="w-full max-w-md space-y-4">
              <div className="text-center mb-8">
                <h1 className="text-2xl font-bold text-gray-900 mb-2">Welcome to ProductivityFlow</h1>
                <p className="text-gray-600">Choose how you'd like to access the tracker</p>
              </div>
              
              <div className="grid grid-cols-1 gap-4">
                <button
                  onClick={() => setShowLogin(true)}
                  className="p-4 border-2 border-blue-200 rounded-lg hover:bg-blue-50 transition-colors text-left"
                >
                  <h3 className="font-semibold text-blue-900">Sign In</h3>
                  <p className="text-sm text-blue-700">I have an account with email and password</p>
                </button>
                
                <button
                  onClick={() => setShowLogin(false)}
                  className="p-4 border-2 border-green-200 rounded-lg hover:bg-green-50 transition-colors text-left"
                >
                  <h3 className="font-semibold text-green-900">Join Team</h3>
                  <p className="text-sm text-green-700">I have a team code to join</p>
                </button>
              </div>
            </div>
          </div>
        ) : employeeSession ? (
          <TrackingView 
            session={{
              teamId: employeeSession.teamId,
              teamName: employeeSession.teamName,
              userId: employeeSession.employeeId,
              userName: employeeSession.employeeName,
              role: 'employee',
              token: employeeSession.token
            }} 
            onLogout={handleLogout} 
          />
        ) : session ? (
          <TrackingView session={session} onLogout={handleLogout} />
        ) : showLogin ? (
          <AuthView onAuthSuccess={handleLoginSuccess} />
        ) : (
          <OnboardingView onTeamJoin={handleTeamJoin} />
        )}
      </div>
    </ErrorBoundary>
  );
}