import React, { useState } from 'react';
import { Button } from './ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { Building, User, Mail, Lock, Eye, EyeOff, Loader2, LogIn, UserPlus } from 'lucide-react';

const API_URL = "https://my-home-backend-7m6d.onrender.com";

interface OnboardingViewProps {
  onTeamJoin: (sessionData: {
    teamId: string;
    teamName: string;
    userId: string;
    userName: string;
    role: string;
    token: string;
  }) => void;
}

export function OnboardingView({ onTeamJoin }: OnboardingViewProps) {
  const [isSignIn, setIsSignIn] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [teamCode, setTeamCode] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      setError('Please fill in all fields');
      return;
    }
    
    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const { invoke } = await import('@tauri-apps/api/tauri');
      
      const requestBody = {
        email: email.trim().toLowerCase(),
        password: password
      };
      
      const response = await invoke('http_post', {
        url: `${API_URL}/api/auth/employee-login`,
        body: JSON.stringify(requestBody),
        headers: JSON.stringify({
          'Content-Type': 'application/json'
        })
      });
      
      const data = JSON.parse(response as string);

      if (data.success && data.user) {
        setSuccess('Login successful!');
        
        // Call the onTeamJoin callback with the session data
        onTeamJoin({
          teamId: data.user.team_id,
          teamName: data.user.team_name || 'Unknown Team',
          userId: data.user.id,
          userName: data.user.name,
          role: data.user.role,
          token: data.token,
        });
      } else {
        setError(data.message || 'Login failed');
      }
    } catch (err: any) {
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
    if (!name.trim() || !teamCode.trim()) {
      setError('Please fill in all required fields');
      return;
    }
    
    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const { invoke } = await import('@tauri-apps/api/tauri');
      
      // Join team directly (this will create the user account)
      const requestBody = {
        employee_code: teamCode.trim().toUpperCase(),
        user_name: name.trim(),
        email: email.trim() || undefined,
        password: password || undefined
      };
      
      const response = await invoke('http_post', {
        url: `${API_URL}/api/teams/join`,
        body: JSON.stringify(requestBody),
        headers: JSON.stringify({
          'Content-Type': 'application/json'
        })
      });
      
      const data = JSON.parse(response as string);

      if (data.success && data.user) {
        setSuccess('Account created successfully!');
        
        // Call the onTeamJoin callback with the session data
        onTeamJoin({
          teamId: data.user.team_id,
          teamName: data.team.name,
          userId: data.user.id,
          userName: data.user.name,
          role: data.user.role,
          token: data.token,
        });
      } else {
        setError(data.message || 'Failed to create account');
      }
    } catch (err: any) {
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

  const toggleMode = () => {
    setIsSignIn(!isSignIn);
    setError("");
    setSuccess("");
    setEmail("");
    setPassword("");
    setName("");
    setTeamCode("");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Card className="bg-white border-0 rounded-3xl shadow-2xl">
          <CardHeader className="text-center pb-6">
            <div className="flex items-center justify-center mb-6">
              <div className="p-4 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl">
                <Building className="h-8 w-8 text-white" />
              </div>
            </div>
            <CardTitle className="text-2xl font-bold text-gray-900">
              {isSignIn ? "Welcome Back" : "Join Your Team"}
            </CardTitle>
            <p className="text-gray-600 mt-2">
              {isSignIn 
                ? "Sign in to access your productivity dashboard"
                : "Create your account and start tracking productivity"
              }
            </p>
          </CardHeader>
          <CardContent className="space-y-6">
            {success && (
              <div className="flex items-center gap-3 p-4 bg-green-50 border border-green-200 rounded-xl">
                <div className="h-5 w-5 text-green-500">✓</div>
                <span className="text-sm text-green-700 font-medium">{success}</span>
              </div>
            )}

            {error && (
              <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-xl">
                <div className="h-5 w-5 text-red-500">✗</div>
                <span className="text-sm text-red-700 font-medium">{error}</span>
              </div>
            )}

            <form onSubmit={isSignIn ? handleSignIn : handleCreateAccount} className="space-y-6">
              {!isSignIn && (
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
                        required={!isSignIn}
                      />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="teamCode" className="text-sm font-semibold text-gray-700 mb-2 block">
                      Team Code *
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <Building className="h-5 w-5 text-gray-400" />
                      </div>
                      <input
                        id="teamCode"
                        type="text"
                        value={teamCode}
                        onChange={(e) => setTeamCode(e.target.value.toUpperCase())}
                        placeholder="Enter your team code"
                        className="flex h-12 w-full rounded-xl border border-gray-300 bg-white pl-12 pr-4 py-3 text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                        required={!isSignIn}
                      />
                    </div>
                    <p className="text-xs text-gray-500 mt-2">
                      Get this code from your manager
                    </p>
                  </div>
                </>
              )}

              <div>
                <label htmlFor="email" className="text-sm font-semibold text-gray-700 mb-2 block">
                  Email Address {!isSignIn && '(Optional)'}
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
                    required={isSignIn}
                  />
                </div>
              </div>

              <div>
                <label htmlFor="password" className="text-sm font-semibold text-gray-700 mb-2 block">
                  Password {!isSignIn && '(Optional)'}
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
                    required={isSignIn}
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
                {!isSignIn && (
                  <p className="text-xs text-gray-500 mt-2">
                    Leave blank to use default password
                  </p>
                )}
              </div>

              <Button
                type="submit"
                disabled={isLoading}
                className="w-full h-12 text-lg font-semibold bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition-all duration-200 shadow-lg"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-3 h-5 w-5 animate-spin" />
                    {isSignIn ? "Signing In..." : "Creating Account..."}
                  </>
                ) : (
                  <>
                    {isSignIn ? (
                      <>
                        <LogIn className="mr-3 h-5 w-5" />
                        Sign In
                      </>
                    ) : (
                      <>
                        <UserPlus className="mr-3 h-5 w-5" />
                        Create Account
                      </>
                    )}
                  </>
                )}
              </Button>

              <Button
                type="button"
                variant="outline"
                onClick={toggleMode}
                className="w-full h-12 text-lg font-semibold border-gray-300 hover:bg-gray-50 rounded-xl transition-all duration-200"
              >
                {isSignIn ? "Need an account? Create one" : "Already have an account? Sign in"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}