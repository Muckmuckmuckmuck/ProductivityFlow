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
  LogIn,
  CheckCircle2
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
  const [showEmailVerification, setShowEmailVerification] = useState(false);
  const [verificationCode, setVerificationCode] = useState("");
  const [isVerifying, setIsVerifying] = useState(false);
  const [showTeamCodes, setShowTeamCodes] = useState(false);
  const [teamData, setTeamData] = useState<any>(null);
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

    if (password.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }

    setIsLoading(true);
    setIsSubmitting(true);
    setError("");
    setSuccess("");

    try {
      const { invoke } = await import('@tauri-apps/api/tauri');
      const requestBody = { 
        email: email.trim().toLowerCase(),
        password: password,
        name: name.trim(),
        organization: organization.trim()
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

      if (data.success) {
        // Show team codes if available
        if (data.team && data.team.employee_code) {
          setSuccess(`Account created successfully! Your team codes are ready. Employee Code: ${data.team.employee_code}`);
        } else {
          setSuccess("Account created successfully! Please check your email for verification code.");
        }
        setShowEmailVerification(true);
        // Store team data for later use
        if (data.team) {
          localStorage.setItem('pendingTeamData', JSON.stringify(data.team));
        }
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

  const handleEmailVerification = async () => {
    if (!verificationCode.trim()) {
      setError("Please enter the verification code.");
      return;
    }

    setIsVerifying(true);
    setError("");

    try {
      const { invoke } = await import('@tauri-apps/api/tauri');
      
      const response = await invoke('http_post', {
        url: `${API_URL}/api/auth/verify-email`,
        body: JSON.stringify({
          email: email.trim().toLowerCase(),
          verification_code: verificationCode.trim()
        }),
        headers: JSON.stringify({
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        })
      });
      
      const data = JSON.parse(response as string);

      if (data.success && data.user && data.token) {
        // Check if we have team data stored
        const storedTeamData = localStorage.getItem('pendingTeamData');
        if (storedTeamData) {
          const team = JSON.parse(storedTeamData);
          setTeamData(team);
          setShowTeamCodes(true);
          localStorage.removeItem('pendingTeamData');
        } else {
          setSuccess("Email verified successfully! You can now sign in.");
          setShowEmailVerification(false);
          setIsSignIn(true);
          // Clear the form for sign in
          setPassword("");
          setVerificationCode("");
        }
      } else {
        setError(data.message || 'Email verification failed. Please try again.');
      }
    } catch (err: any) {
      let errorMessage = "Email verification failed. Please try again.";
      
      if (err.message.includes('Failed to fetch') || err.message.includes('Cannot connect')) {
        errorMessage = "Cannot connect to server. Please check your internet connection.";
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setIsVerifying(false);
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
        email: email.trim().toLowerCase(), 
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

      if (data.success && data.user && data.token) {
        // Store token in localStorage
        localStorage.setItem('authToken', data.token);
        
        const sessionData = {
          managerId: data.user.id,
          managerName: data.user.name,
          organization: data.user.organization || "Default Organization",
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
    setShowEmailVerification(false);
    
    // Reset form fields
    setEmail("");
    setPassword("");
    setName("");
    setOrganization("");
    setVerificationCode("");
    
    setIsModeTransitioning(false);
  };

  // Team codes display view
  if (showTeamCodes && teamData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <Card className="bg-white/90 backdrop-blur-sm border-0 rounded-2xl shadow-xl">
            <CardHeader className="text-center pb-6">
              <div className="flex items-center justify-center mb-6">
                <div className="p-3 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl">
                  <Building className="h-8 w-8 text-white" />
                </div>
              </div>
              <CardTitle className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                Your Team is Ready!
              </CardTitle>
              <p className="text-gray-600 text-lg mt-2">
                Share these codes with your team members
              </p>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl">
                  <h3 className="text-sm font-semibold text-blue-800 mb-2">Employee Code</h3>
                  <div className="flex items-center justify-between">
                    <code className="text-lg font-mono font-bold text-blue-900 bg-blue-100 px-3 py-2 rounded-lg">
                      {teamData.employee_code}
                    </code>
                    <Button
                      onClick={() => navigator.clipboard.writeText(teamData.employee_code)}
                      className="text-blue-600 hover:text-blue-700"
                      variant="ghost"
                      size="sm"
                    >
                      Copy
                    </Button>
                  </div>
                  <p className="text-xs text-blue-700 mt-2">
                    Share this code with employees to join your team
                  </p>
                </div>

                <div className="p-4 bg-purple-50 border border-purple-200 rounded-xl">
                  <h3 className="text-sm font-semibold text-purple-800 mb-2">Manager Code</h3>
                  <div className="flex items-center justify-between">
                    <code className="text-lg font-mono font-bold text-purple-900 bg-purple-100 px-3 py-2 rounded-lg">
                      {teamData.manager_code}
                    </code>
                    <Button
                      onClick={() => navigator.clipboard.writeText(teamData.manager_code)}
                      className="text-purple-600 hover:text-purple-700"
                      variant="ghost"
                      size="sm"
                    >
                      Copy
                    </Button>
                  </div>
                  <p className="text-xs text-purple-700 mt-2">
                    Keep this code secure for administrative access
                  </p>
                </div>
              </div>

              <div className="flex flex-col space-y-3">
                <Button
                  onClick={() => {
                    setShowTeamCodes(false);
                    setIsSignIn(true);
                    setPassword("");
                  }}
                  className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold py-3 rounded-xl transition-all duration-200 transform hover:scale-105"
                >
                  Continue to Sign In
                </Button>
                
                <Button
                  onClick={() => {
                    setShowTeamCodes(false);
                    setShowEmailVerification(false);
                    setIsSignIn(false);
                    setEmail("");
                    setPassword("");
                    setName("");
                    setOrganization("");
                  }}
                  variant="outline"
                  className="w-full border-gray-300 text-gray-700 hover:bg-gray-50 font-semibold py-3 rounded-xl"
                >
                  Create Another Account
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // Email verification view
  if (showEmailVerification) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <Card className="bg-white/90 backdrop-blur-sm border-0 rounded-2xl shadow-xl">
            <CardHeader className="text-center pb-6">
              <div className="flex items-center justify-center mb-6">
                <div className="p-3 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl">
                  <CheckCircle2 className="h-8 w-8 text-white" />
                </div>
              </div>
              <CardTitle className="text-2xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                Verify Your Email
              </CardTitle>
              <p className="text-gray-600 text-lg mt-2">
                We've sent a verification code to your email
              </p>
              <p className="text-sm text-gray-500 mt-2">
                {email}
              </p>
              <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-xs text-yellow-800">
                  <strong>For testing:</strong> Use verification code <code className="bg-yellow-100 px-1 rounded">123456</code>
                </p>
              </div>
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

              <div>
                <label htmlFor="verificationCode" className="text-sm font-semibold text-gray-700 mb-2 block">
                  Verification Code *
                </label>
                <input
                  id="verificationCode"
                  type="text"
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value)}
                  placeholder="Enter the 6-digit code"
                  className="flex h-12 w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-base focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all duration-200 text-center text-lg tracking-widest"
                  maxLength={6}
                  required
                />
              </div>

              <Button
                onClick={handleEmailVerification}
                disabled={isVerifying || !verificationCode.trim()}
                className="w-full h-12 text-lg font-semibold bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white rounded-xl transition-all duration-200 transform hover:scale-105 shadow-lg"
              >
                {isVerifying ? (
                  <>
                    <Loader2 className="mr-3 h-5 w-5 animate-spin" />
                    Verifying...
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="mr-3 h-5 w-5" />
                    Verify Email
                  </>
                )}
              </Button>

              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setShowEmailVerification(false);
                  setSuccess("");
                  setError("");
                }}
                disabled={isVerifying}
                className="w-full h-12 text-lg font-semibold border-gray-300 hover:bg-gray-50 rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Back to Sign In
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

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
                        className="flex h-12 w-full rounded-xl border border-gray-300 bg-white pl-12 pr-4 py-3 text-base focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200"
                        required={!isSignIn}
                      />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="organization" className="text-sm font-semibold text-gray-700 mb-2 block">
                      Organization *
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
                    placeholder="Enter your email"
                    className="flex h-12 w-full rounded-xl border border-gray-300 bg-white pl-12 pr-4 py-3 text-base focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200"
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
                {!isSignIn && (
                  <p className="text-xs text-gray-500 mt-2">
                    Password must be at least 8 characters long
                  </p>
                )}
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