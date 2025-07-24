import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { 
  Mail, 
  Lock, 
  Eye, 
  EyeOff, 
  Loader2,
  AlertCircle,
  CheckCircle,
  User,
  Key
} from 'lucide-react';

const API_URL = "https://productivityflow-backend-496367590729.us-central1.run.app";

interface LoginViewProps {
  onLoginSuccess: (sessionData: {
    employeeId: string;
    employeeName: string;
    teamId: string;
    teamName: string;
    token: string;
  }) => void;
}

export function LoginView({ onLoginSuccess }: LoginViewProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [isForgotPassword, setIsForgotPassword] = useState(false);
  const [forgotEmail, setForgotEmail] = useState("");
  const [forgotLoading, setForgotLoading] = useState(false);
  const [forgotSuccess, setForgotSuccess] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email.trim() || !password.trim()) {
      setError("Please enter both email and password.");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      console.log(`Making login request to: ${API_URL}/api/auth/employee/login`);
      
      const { invoke } = await import('@tauri-apps/api/tauri');
      const requestBody = JSON.stringify({ 
        email: email.trim(), 
        password: password 
      });
      
      const response = await invoke('http_post', {
        url: `${API_URL}/api/auth/employee/login`,
        body: requestBody
      });
      
      const data = JSON.parse(response as string);
      console.log(`Login response:`, data);

      if (data.success) {
        const sessionData = {
          employeeId: data.employee.id,
          employeeName: data.employee.name,
          teamId: data.team.id,
          teamName: data.team.name,
          token: data.token
        };
        onLoginSuccess(sessionData);
      } else {
        setError(data.message || 'Login failed. Please check your credentials.');
      }
    } catch (err: any) {
      console.error(`Error during login:`, err);
      
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

  const handleForgotPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!forgotEmail.trim()) {
      setError("Please enter your email address.");
      return;
    }

    setForgotLoading(true);
    setError("");

    try {
      console.log(`Making forgot password request to: ${API_URL}/api/auth/forgot-password`);
      
      const { invoke } = await import('@tauri-apps/api/tauri');
      const requestBody = JSON.stringify({ 
        email: forgotEmail.trim()
      });
      
      const response = await invoke('http_post', {
        url: `${API_URL}/api/auth/forgot-password`,
        body: requestBody
      });
      
      const data = JSON.parse(response as string);
      console.log(`Forgot password response:`, data);

      if (data.success) {
        setForgotSuccess(true);
        setError("");
      } else {
        setError(data.message || 'Failed to send reset email. Please try again.');
      }
    } catch (err: any) {
      console.error(`Error during forgot password:`, err);
      setError("Failed to send reset email. Please try again.");
    } finally {
      setForgotLoading(false);
    }
  };

  if (isForgotPassword) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-gray-50">
        <div className="w-full max-w-md">
          <Card>
            <CardHeader className="text-center">
              <div className="flex items-center justify-center mb-4">
                <Key className="h-8 w-8 text-blue-600" />
              </div>
              <CardTitle>Reset Password</CardTitle>
              <p className="text-sm text-gray-500 mt-2">
                Enter your email to receive a password reset link
              </p>
            </CardHeader>
            <CardContent>
              {forgotSuccess ? (
                <div className="text-center">
                  <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-green-800 mb-2">
                    Reset Email Sent!
                  </h3>
                  <p className="text-sm text-gray-600 mb-4">
                    We've sent a password reset link to {forgotEmail}. Please check your email.
                  </p>
                  <Button
                    onClick={() => {
                      setIsForgotPassword(false);
                      setForgotSuccess(false);
                      setForgotEmail("");
                    }}
                    className="w-full"
                  >
                    Back to Login
                  </Button>
                </div>
              ) : (
                <form onSubmit={handleForgotPassword} className="space-y-4">
                  {error && (
                    <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-md">
                      <AlertCircle className="h-4 w-4 text-red-500" />
                      <span className="text-sm text-red-700">{error}</span>
                    </div>
                  )}
                  
                  <div>
                    <label htmlFor="forgot-email" className="text-sm font-medium text-gray-700">
                      Email Address
                    </label>
                    <div className="relative mt-1">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <Mail className="h-5 w-5 text-gray-400" />
                      </div>
                      <input
                        id="forgot-email"
                        type="email"
                        value={forgotEmail}
                        onChange={(e) => setForgotEmail(e.target.value)}
                        placeholder="Enter your email"
                        className="flex h-10 w-full rounded-md border border-gray-300 bg-transparent pl-10 pr-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        required
                      />
                    </div>
                  </div>

                  <Button
                    type="submit"
                    disabled={forgotLoading}
                    className="w-full"
                  >
                    {forgotLoading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Sending Reset Email...
                      </>
                    ) : (
                      "Send Reset Email"
                    )}
                  </Button>

                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setIsForgotPassword(false);
                      setForgotEmail("");
                      setError("");
                    }}
                    className="w-full"
                  >
                    Back to Login
                  </Button>
                </form>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gray-50">
      <div className="w-full max-w-md">
        <Card>
          <CardHeader className="text-center">
            <div className="flex items-center justify-center mb-4">
              <User className="h-8 w-8 text-blue-600" />
            </div>
            <CardTitle>Employee Login</CardTitle>
            <p className="text-sm text-gray-500 mt-2">
              Sign in to access your activity tracker
            </p>
            <p className="text-xs text-gray-400 mt-1">
              Employee Tracker • {API_URL}
            </p>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleLogin} className="space-y-4">
              {error && (
                <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-md">
                  <AlertCircle className="h-4 w-4 text-red-500" />
                  <span className="text-sm text-red-700">{error}</span>
                </div>
              )}
              
              <div>
                <label htmlFor="email" className="text-sm font-medium text-gray-700">
                  Email Address
                </label>
                <div className="relative mt-1">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Mail className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter your email"
                    className="flex h-10 w-full rounded-md border border-gray-300 bg-transparent pl-10 pr-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>
              </div>

              <div>
                <label htmlFor="password" className="text-sm font-medium text-gray-700">
                  Password
                </label>
                <div className="relative mt-1">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    className="flex h-10 w-full rounded-md border border-gray-300 bg-transparent pl-10 pr-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
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
                className="w-full"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Signing In...
                  </>
                ) : (
                  "Sign In"
                )}
              </Button>

              <Button
                type="button"
                variant="outline"
                onClick={() => setIsForgotPassword(true)}
                className="w-full"
              >
                Forgot Password?
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 