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
        team_code: teamCode.trim(),
        employee_name: name.trim()
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

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email.trim() || !password.trim()) {
      setError("Please enter both email and password.");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const { http } = await import('@tauri-apps/api');
      const requestBody = { 
        email: email.trim(), 
        password: password 
      };
      
      const response = await http.fetch(`${API_URL}/api/auth/employee-login`, {
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

      if (data.error) {
        if (data.error.includes("verify your email")) {
          setError("Please verify your email before signing in. Check your inbox for verification instructions.");
        } else {
          setError(data.error);
        }
      } else if (data.success && data.user && data.token) {
        const sessionData = {
          employeeId: data.user.id,
          employeeName: data.user.name,
          teamId: data.user.team_id,
          teamName: data.user.team_name,
          token: data.token
        };
        onAuthSuccess(sessionData);
      } else {
        setError(data.message || 'Sign in failed. Please check your credentials.');
      }
    } catch (err: any) {
      let errorMessage = "An unexpected error occurred. Please try again.";
      
      if (err.message.includes('401') || err.message.includes('Unauthorized')) {
        errorMessage = "Invalid email or password. Please try again.";
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Card className="bg-white/90 backdrop-blur-sm border-0 rounded-2xl shadow-xl">
          <CardHeader className="text-center pb-6">
            <div className="flex items-center justify-center mb-6">
              <div className="p-3 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl">
                <User className="h-8 w-8 text-white" />
              </div>
            </div>
            <CardTitle className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              Employee Tracker
            </CardTitle>
            <p className="text-gray-600 text-lg mt-2">
              Join your team and start tracking productivity
            </p>
            <p className="text-xs text-gray-400 mt-2">
              WorkFlow Employee Monitor • {API_URL}
            </p>
          </CardHeader>
          <CardContent className="space-y-6">
            {success && (
              <div className="flex items-center gap-3 p-4 bg-green-50 border border-green-200 rounded-xl">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span className="text-sm text-green-700 font-medium">{success}</span>
              </div>
            )}

            {error && (
              <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-xl">
                <AlertCircle className="h-5 w-5 text-red-500" />
                <span className="text-sm text-red-700 font-medium">{error}</span>
              </div>
            )}

            <form onSubmit={handleCreateAccount} className="space-y-6">
              <div>
                <label htmlFor="name" className="text-sm font-semibold text-gray-700 mb-2 block">
                  Full Name
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <User className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="name"
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Enter your full name"
                    className="flex h-12 w-full rounded-xl border border-gray-300 bg-white pl-12 pr-4 py-3 text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                    required
                  />
                </div>
              </div>

              <div>
                <label htmlFor="teamCode" className="text-sm font-semibold text-gray-700 mb-2 block">
                  Team Code
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Hash className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="teamCode"
                    type="text"
                    value={teamCode}
                    onChange={(e) => setTeamCode(e.target.value.toUpperCase())}
                    placeholder="Enter your team code"
                    className="flex h-12 w-full rounded-xl border border-gray-300 bg-white pl-12 pr-4 py-3 text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                    required
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  This is the 6-character code provided by your manager
                </p>
              </div>

              <Button
                type="submit"
                disabled={isLoading}
                className="w-full h-12 text-lg font-semibold bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 text-white rounded-xl transition-all duration-200 transform hover:scale-105 shadow-lg"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-3 h-5 w-5 animate-spin" />
                    Joining Team...
                  </>
                ) : (
                  <>
                    <UserPlus className="mr-3 h-5 w-5" />
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