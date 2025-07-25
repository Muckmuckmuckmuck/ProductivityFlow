import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { 
  Loader2,
  AlertCircle,
  CheckCircle,
  User,
  UserPlus,
  Hash
} from 'lucide-react';

const API_URL = "https://my-home-backend-7m6d.onrender.com";

interface AuthViewProps {
  onAuthSuccess: (sessionData: {
    employeeId: string;
    employeeName: string;
    teamId: string;
    teamName: string;
    token: string;
  }) => void;
}

export function AuthView({ onAuthSuccess }: AuthViewProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [teamCode, setTeamCode] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleCreateAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email.trim() || !password.trim() || !name.trim() || !teamCode.trim()) {
      setError("Please fill in all fields.");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters long.");
      return;
    }

    setIsLoading(true);
    setError("");
    setSuccess("");

    try {
      console.log(`Making create account request to: ${API_URL}/api/auth/employee/register`);
      
      const { http } = await import('@tauri-apps/api');
      const requestBody = { 
        employee_code: teamCode.trim(),
        user_name: name.trim()
      };
      
      const response = await http.fetch(`${API_URL}/api/teams/join`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: {
          type: 'Json',
          payload: requestBody
        }
      });
      
      const data = response.data as any;
      console.log(`Create account response:`, data);

      // Check if the response indicates an error (non-2xx status or error field)
      if (response.status >= 400 || data.error) {
        const errorMessage = data.error || data.message || 'Failed to create account. Please try again.';
        setError(errorMessage);
        return;
      }

      // Success case
      if (data.success && data.token) {
        const sessionData = {
          employeeId: data.user.id,
          employeeName: data.user.name,
          teamId: data.team.id,
          teamName: data.team.name,
          token: data.token
        };
        onAuthSuccess(sessionData);
      } else {
        setError('Failed to join team. Please try again.');
      }
    } catch (err: any) {
      console.error(`Error creating account:`, err);
      
      let errorMessage = "An unexpected error occurred. Please try again.";
      
      if (err.message.includes('409') || err.message.includes('already exists')) {
        errorMessage = "An account with this email already exists. Please sign in instead.";
      } else if (err.message.includes('404') || err.message.includes('team not found')) {
        errorMessage = "Invalid team code. Please check your team code and try again.";
      } else if (err.message.includes('Failed to fetch') || err.message.includes('Cannot connect')) {
        errorMessage = "Cannot connect to server. Please check your internet connection.";
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };





  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gray-50">
      <div className="w-full max-w-md">
        <Card>
          <CardHeader className="text-center">
            <div className="flex items-center justify-center mb-4">
              <User className="h-8 w-8 text-blue-600" />
            </div>
            <CardTitle>Join Team</CardTitle>
            <p className="text-sm text-gray-500 mt-1">
              Join your team to start tracking
            </p>
            <p className="text-xs text-gray-400 mt-1">
              Employee Tracker • {API_URL}
            </p>
          </CardHeader>
          <CardContent>
            {success && (
              <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-md mb-4">
                <CheckCircle className="h-4 w-4 text-green-500" />
                <span className="text-sm text-green-700">{success}</span>
              </div>
            )}

            {error && (
              <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-md mb-4">
                <AlertCircle className="h-4 w-4 text-red-500" />
                <span className="text-sm text-red-700">{error}</span>
              </div>
            )}

            <form onSubmit={handleCreateAccount} className="space-y-4">
              {true && (
                <>
                  <div>
                    <label htmlFor="name" className="text-sm font-medium text-gray-700">
                      Full Name
                    </label>
                    <div className="relative mt-1">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <User className="h-5 w-5 text-gray-400" />
                      </div>
                      <input
                        id="name"
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="Enter your full name"
                        className="flex h-10 w-full rounded-md border border-gray-300 bg-transparent pl-10 pr-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        required={true}
                      />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="teamCode" className="text-sm font-medium text-gray-700">
                      Team Code
                    </label>
                    <div className="relative mt-1">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <Hash className="h-5 w-5 text-gray-400" />
                      </div>
                      <input
                        id="teamCode"
                        type="text"
                        value={teamCode}
                        onChange={(e) => setTeamCode(e.target.value)}
                        placeholder="Enter your team code"
                        className="flex h-10 w-full rounded-md border border-gray-300 bg-transparent pl-10 pr-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        required={true}
                      />
                    </div>
                  </div>
                </>
              )}

              <div>
                <label htmlFor="email" className="text-sm font-medium text-gray-700">
                  Team Code
                </label>
                <div className="relative mt-1">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Hash className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="email"
                    type="text"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter your team code"
                    className="flex h-10 w-full rounded-md border border-gray-300 bg-transparent pl-10 pr-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>
              </div>

              <div>
                <label htmlFor="password" className="text-sm font-medium text-gray-700">
                  Employee Name
                </label>
                <div className="relative mt-1">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <User className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="password"
                    type="text"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your name"
                    className="flex h-10 w-full rounded-md border border-gray-300 bg-transparent pl-10 pr-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                  />

                </div>
              </div>

              <Button
                type="submit"
                disabled={isLoading}
                className="w-full"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Joining Team...
                  </>
                ) : (
                  <>
                    <UserPlus className="mr-2 h-4 w-4" />
                    Join Team
                  </>
                )}
              </Button>


            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 