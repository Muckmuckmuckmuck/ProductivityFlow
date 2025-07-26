import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { 
  Loader2,
  AlertCircle,
  CheckCircle,
  User,
  UserPlus,
  Hash,
  Mail,
  Lock,
  Eye,
  EyeOff
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
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email.trim() || !password.trim()) {
      setError("Please fill in all fields.");
      return;
    }

    setIsLoading(true);
    setError("");
    setSuccess("");

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
      console.log(`Sign in response:`, data);

      if (response.status >= 400 || data.error) {
        const errorMessage = data.error || data.message || 'Failed to sign in. Please try again.';
        setError(errorMessage);
        return;
      }

      if (data.success && data.user && data.token) {
        const sessionData = {
          employeeId: data.user.id,
          employeeName: data.user.name,
          teamId: data.user.team_id,
          teamName: data.user.team_name,
          token: data.token
        };
        onAuthSuccess(sessionData);
      } else {
        setError('Failed to sign in. Please try again.');
      }
    } catch (err: any) {
      console.error(`Error signing in:`, err);
      
      let errorMessage = "An unexpected error occurred. Please try again.";
      
      if (err.message.includes('Failed to fetch') || err.message.includes('Cannot connect')) {
        errorMessage = "Cannot connect to server. Please check your internet connection.";
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

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
      const { http } = await import('@tauri-apps/api');
      const requestBody = { 
        employee_code: teamCode.trim().toUpperCase(),
        user_name: name.trim(),
        email: email.trim(),
        password: password
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

      if (response.status >= 400 || data.error) {
        const errorMessage = data.error || data.message || 'Failed to create account. Please try again.';
        setError(errorMessage);
        return;
      }

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
        errorMessage = "A user with this name already exists in the team.";
      } else if (err.message.includes('404') || err.message.includes('Invalid')) {
        errorMessage = "Invalid team code. Please check with your manager.";
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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Card className="bg-white border-0 rounded-3xl shadow-2xl">
          <CardHeader className="text-center pb-6">
            <div className="flex items-center justify-center mb-6">
              <div className="p-4 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl">
                <User className="h-8 w-8 text-white" />
              </div>
            </div>
            <CardTitle className="text-2xl font-bold text-gray-900">
              Welcome to ProductivityFlow
            </CardTitle>
            <p className="text-gray-600 mt-2">
              Sign in to your account or create a new one
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

            <form onSubmit={handleSignIn} className="space-y-6">
              <div>
                <label htmlFor="email" className="text-sm font-semibold text-gray-700 mb-2 block">
                  Email Address
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Mail className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter your email"
                    className="flex h-12 w-full rounded-xl border border-gray-300 bg-white pl-12 pr-4 py-3 text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                    required
                  />
                </div>
              </div>

              <div>
                <label htmlFor="password" className="text-sm font-semibold text-gray-700 mb-2 block">
                  Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    className="flex h-12 w-full rounded-xl border border-gray-300 bg-white pl-12 pr-12 py-3 text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-4 flex items-center"
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5 text-gray-400" />
                    ) : (
                      <Eye className="h-5 w-5 text-gray-400" />
                    )}
                  </button>
                </div>
              </div>

              <Button
                type="submit"
                disabled={isLoading}
                className="w-full h-12 text-lg font-semibold bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition-all duration-200 shadow-lg"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-3 h-5 w-5 animate-spin" />
                    Signing In...
                  </>
                ) : (
                  <>
                    <User className="mr-3 h-5 w-5" />
                    Sign In
                  </>
                )}
              </Button>
            </form>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">Or create a new account</span>
              </div>
            </div>

            <form onSubmit={handleCreateAccount} className="space-y-6">
              <div>
                <label htmlFor="create-name" className="text-sm font-semibold text-gray-700 mb-2 block">
                  Full Name
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <User className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="create-name"
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Enter your full name"
                    className="flex h-12 w-full rounded-xl border border-gray-300 bg-white pl-12 pr-4 py-3 text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="team-code" className="text-sm font-semibold text-gray-700 mb-2 block">
                  Team Code
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Hash className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="team-code"
                    type="text"
                    value={teamCode}
                    onChange={(e) => setTeamCode(e.target.value.toUpperCase())}
                    placeholder="Enter your team code"
                    className="flex h-12 w-full rounded-xl border border-gray-300 bg-white pl-12 pr-4 py-3 text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                  />
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Get this code from your manager
                </p>
              </div>

              <Button
                type="submit"
                disabled={isLoading}
                className="w-full h-12 text-lg font-semibold bg-green-600 hover:bg-green-700 text-white rounded-xl transition-all duration-200 shadow-lg"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-3 h-5 w-5 animate-spin" />
                    Creating Account...
                  </>
                ) : (
                  <>
                    <UserPlus className="mr-3 h-5 w-5" />
                    Create Account
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