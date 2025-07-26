import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { 
  Loader2,
  AlertCircle,
  CheckCircle,
  User,
  Hash,
  Building,
  ArrowRight,
  Mail,
  Lock,
  Eye,
  EyeOff,
  UserPlus,
  LogIn
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
  const [isSignUp, setIsSignUp] = useState(true);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [employeeCode, setEmployeeCode] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleJoinTeam = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name.trim() || !email.trim() || !password.trim() || !employeeCode.trim()) {
      setError("Please fill in all fields.");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }

    setIsLoading(true);
    setError("");
    setSuccess("");

    try {
      const { http } = await import('@tauri-apps/api');
      
      const requestBody = { 
        employee_code: employeeCode.trim().toUpperCase(),
        user_name: name.trim(),
        email: email.trim().toLowerCase(),
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
      console.log(`Join team response:`, data);

      if (response.status >= 400 || data.error) {
        const errorMessage = data.error || data.message || 'Failed to join team. Please check your employee code.';
        setError(errorMessage);
        return;
      }

      if (data.success && data.user && data.team) {
        setSuccess("Successfully joined team! Starting productivity tracking...");
        
        // Create a simple session for the employee
        const sessionData = {
          employeeId: data.user.id,
          employeeName: data.user.name,
          teamId: data.team.id,
          teamName: data.team.name,
          token: 'employee-session' // Simple session for employee tracking
        };
        
        // Small delay to show success message
        setTimeout(() => {
          onAuthSuccess(sessionData);
        }, 1500);
      } else {
        setError('Failed to join team. Please try again.');
      }
    } catch (err: any) {
      console.error(`Error joining team:`, err);
      
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
        email: email.trim().toLowerCase(),
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
        setSuccess("Sign in successful! Starting productivity tracking...");
        
        const sessionData = {
          employeeId: data.user.id,
          employeeName: data.user.name,
          teamId: data.user.team_id,
          teamName: data.user.team_name,
          token: data.token
        };
        
        // Small delay to show success message
        setTimeout(() => {
          onAuthSuccess(sessionData);
        }, 1500);
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
              {isSignUp ? 'Join Your Team' : 'Welcome Back'}
            </CardTitle>
            <p className="text-gray-600 text-lg mt-2">
              {isSignUp ? 'Create your account to start productivity tracking' : 'Sign in to continue tracking'}
            </p>
          </CardHeader>

          <CardContent className="space-y-6">
            {error && (
              <div className="flex items-center space-x-2 p-3 bg-red-50 border border-red-200 rounded-lg">
                <AlertCircle className="h-5 w-5 text-red-500" />
                <span className="text-sm text-red-700">{error}</span>
              </div>
            )}

            {success && (
              <div className="flex items-center space-x-2 p-3 bg-green-50 border border-green-200 rounded-lg">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span className="text-sm text-green-700">{success}</span>
              </div>
            )}

            <form onSubmit={isSignUp ? handleJoinTeam : handleSignIn} className="space-y-6">
              {isSignUp && (
                <>
                  <div>
                    <label htmlFor="name" className="text-sm font-semibold text-gray-700 mb-2 block">
                      Full Name *
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
                    <label htmlFor="employeeCode" className="text-sm font-semibold text-gray-700 mb-2 block">
                      Employee Code *
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <Hash className="h-5 w-5 text-gray-400" />
                      </div>
                      <input
                        id="employeeCode"
                        type="text"
                        value={employeeCode}
                        onChange={(e) => setEmployeeCode(e.target.value.toUpperCase())}
                        placeholder="Enter employee code from your manager"
                        className="flex h-12 w-full rounded-xl border border-gray-300 bg-white pl-12 pr-4 py-3 text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 font-mono text-center text-lg tracking-wider"
                        maxLength={6}
                        required
                      />
                    </div>
                    <p className="text-xs text-gray-500 mt-2">
                      Get this code from your team manager or owner
                    </p>
                  </div>
                </>
              )}

              <div>
                <label htmlFor="email" className="text-sm font-semibold text-gray-700 mb-2 block">
                  Email Address *
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
                    placeholder="Enter your email address"
                    className="flex h-12 w-full rounded-xl border border-gray-300 bg-white pl-12 pr-4 py-3 text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                    required
                  />
                </div>
              </div>

              <div>
                <label htmlFor="password" className="text-sm font-semibold text-gray-700 mb-2 block">
                  Password *
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
                {isSignUp && (
                  <p className="text-xs text-gray-500 mt-2">
                    Password must be at least 8 characters long
                  </p>
                )}
              </div>

              <Button
                type="submit"
                disabled={isLoading}
                className="w-full h-12 text-lg font-semibold bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-xl transition-all duration-200 transform hover:scale-105 shadow-lg"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-3 h-5 w-5 animate-spin" />
                    {isSignUp ? "Joining Team..." : "Signing In..."}
                  </>
                ) : (
                  <>
                    {isSignUp ? (
                      <>
                        <UserPlus className="mr-3 h-5 w-5" />
                        Join Team
                      </>
                    ) : (
                      <>
                        <LogIn className="mr-3 h-5 w-5" />
                        Sign In
                      </>
                    )}
                  </>
                )}
              </Button>

              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setIsSignUp(!isSignUp);
                  setError("");
                  setSuccess("");
                  if (!isSignUp) {
                    setName("");
                    setEmployeeCode("");
                  }
                }}
                disabled={isLoading}
                className="w-full h-12 text-lg font-semibold border-gray-300 hover:bg-gray-50 rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSignUp ? "Already have an account? Sign in" : "Need to join a team? Create account"}
              </Button>
            </form>
            
            <div className="text-center">
              <p className="text-xs text-gray-500">
                This app will track your productivity to help your team succeed
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 