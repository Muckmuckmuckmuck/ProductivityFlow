import { useState, useRef } from "react";
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
  Building,
  User,
  UserPlus,
  LogIn
} from 'lucide-react';

const API_URL = "https://my-home-backend-7m6d.onrender.com";

interface AuthViewProps {
  onAuthSuccess: (sessionData: {
    managerId: string;
    managerName: string;
    organization: string;
    token: string;
  }) => void;
}

export function AuthView({ onAuthSuccess }: AuthViewProps) {
  const [isSignIn, setIsSignIn] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [organization, setOrganization] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isModeTransitioning, setIsModeTransitioning] = useState(false);
  const currentOperation = useRef<string>('');

  const handleCreateAccount = async () => {
    if (isSubmitting || isLoading) {
      return;
    }
    
    currentOperation.current = 'createAccount';
    
    if (!email.trim() || !password.trim() || !name.trim() || !organization.trim()) {
      setError("Please fill in all fields.");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters long.");
      return;
    }

    setIsLoading(true);
    setIsSubmitting(true);
    setError("");
    setSuccess("");

    try {
      const { invoke } = await import('@tauri-apps/api/tauri');
      const requestBody = { 
        email: email.trim(),
        password: password,
        name: name.trim()
      };
      
      const response = await invoke('http_post', {
        url: `${API_URL}/api/auth/register`,
        body: JSON.stringify(requestBody),
        headers: JSON.stringify({
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        })
      });
      
      const data = JSON.parse(response as string);

      if (data.error) {
        setError(data.error);
      } else if (data.message && data.message.includes("created successfully")) {
        setSuccess(data.message || "Account created successfully!");
        setEmail("");
        setPassword("");
        setName("");
        setOrganization("");
        setIsSignIn(true);
      } else {
        setError(data.message || 'Failed to create account. Please try again.');
      }
    } catch (err: any) {
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
      setIsSubmitting(false);
      currentOperation.current = '';
    }
  };

  const handleSignIn = async () => {
    if (isSubmitting || isLoading) {
      return;
    }
    
    currentOperation.current = 'signIn';
    
    if (!email.trim() || !password.trim()) {
      setError("Please enter both email and password.");
      return;
    }

    setIsLoading(true);
    setIsSubmitting(true);
    setError("");

    try {
      const { invoke } = await import('@tauri-apps/api/tauri');
      const requestBody = { 
        email: email.trim(), 
        password: password 
      };
      
      const response = await invoke('http_post', {
        url: `${API_URL}/api/auth/login`,
        body: JSON.stringify(requestBody),
        headers: JSON.stringify({
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        })
      });
      
      const data = JSON.parse(response as string);

      if (data.error) {
        if (data.error.includes("verify your email")) {
          setError("Please verify your email before signing in. Check your inbox for verification instructions.");
        } else {
          setError(data.error);
        }
      } else if (data.message && data.message.includes("Login successful") && data.user && data.token) {
        // Store token in localStorage
        localStorage.setItem('authToken', data.token);
        
        const sessionData = {
          managerId: data.user.id.toString(),
          managerName: data.user.name,
          organization: "Default Organization",
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
      setIsSubmitting(false);
      currentOperation.current = '';
    }
  };

  const toggleMode = () => {
    if (isLoading || isSubmitting) {
      return;
    }
    
    setIsModeTransitioning(true);
    
    // Clear error unless it's a "user already exists" error
    if (!error.includes("already exists")) {
      setError("");
    }
    
    setIsSignIn(!isSignIn);
    setSuccess("");
    
    // Reset form fields
    setEmail("");
    setPassword("");
    setName("");
    setOrganization("");
    
    setIsModeTransitioning(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Card className="bg-white/90 backdrop-blur-sm border-0 rounded-2xl shadow-xl">
          <CardHeader className="text-center pb-6">
            <div className="flex items-center justify-center mb-6">
              <div className="p-3 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-xl">
                <Building className="h-8 w-8 text-white" />
              </div>
            </div>
            <CardTitle className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              {isSignIn ? "Sign In" : "Create Account"}
            </CardTitle>
            <p className="text-gray-600 text-lg mt-2">
              {isSignIn 
                ? "Sign in to access your manager console"
                : "Create your manager account"
              }
            </p>
            <p className="text-xs text-gray-400 mt-2">
              WorkFlow Manager Console • {API_URL}
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

            <form 
              onSubmit={(e) => {
                e.preventDefault();
                
                // Prevent submission during loading or if mode is changing
                if (isLoading || isSubmitting || isModeTransitioning) {
                  return;
                }
                
                // Call appropriate handler
                if (isSignIn) {
                  handleSignIn();
                } else {
                  handleCreateAccount();
                }
              }} 
              className="space-y-6"
            >
              {!isSignIn && (
                <>
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
                        className="flex h-12 w-full rounded-xl border border-gray-300 bg-white pl-12 pr-4 py-3 text-base focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200"
                        required={!isSignIn}
                      />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="organization" className="text-sm font-semibold text-gray-700 mb-2 block">
                      Organization
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <Building className="h-5 w-5 text-gray-400" />
                      </div>
                      <input
                        id="organization"
                        type="text"
                        value={organization}
                        onChange={(e) => setOrganization(e.target.value)}
                        placeholder="Enter your organization name"
                        className="flex h-12 w-full rounded-xl border border-gray-300 bg-white pl-12 pr-4 py-3 text-base focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200"
                        required={!isSignIn}
                      />
                    </div>
                  </div>
                </>
              )}

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
                    className="flex h-12 w-full rounded-xl border border-gray-300 bg-white pl-12 pr-4 py-3 text-base focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200"
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
                    className="flex h-12 w-full rounded-xl border border-gray-300 bg-white pl-12 pr-12 py-3 text-base focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200"
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
                className="w-full h-12 text-lg font-semibold bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600 text-white rounded-xl transition-all duration-200 transform hover:scale-105 shadow-lg"
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
                disabled={isLoading || isSubmitting}
                className="w-full h-12 text-lg font-semibold border-gray-300 hover:bg-gray-50 rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
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