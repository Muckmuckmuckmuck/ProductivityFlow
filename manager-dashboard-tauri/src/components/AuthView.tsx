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
  CheckCircle2,
  Crown,
  Users,
  ArrowLeft
} from 'lucide-react';

const API_URL = "https://my-home-backend-7m6d.onrender.com";

interface AuthViewProps {
  onAuthSuccess: (sessionData: {
    managerId: string;
    managerName: string;
    organization: string;
    token: string;
    isOwner: boolean;
    ownerCode: string | null;
    managerCode: string | null;
  }) => void;
}

export function AuthView({ onAuthSuccess }: AuthViewProps) {
  // Simple flow: 1. Choose role, 2. Sign up/Sign in
  const [step, setStep] = useState<'choose-role' | 'owner-signup' | 'owner-signin' | 'manager-signup' | 'manager-signin' | 'email-verification' | 'team-codes'>('choose-role');
  const [role, setRole] = useState<'owner' | 'manager'>('owner');
  
  // Form fields
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [organization, setOrganization] = useState("");
  const [teamCode, setTeamCode] = useState("");
  
  // UI states
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [verificationCode, setVerificationCode] = useState("");
  const [isVerifying, setIsVerifying] = useState(false);
  const [teamData, setTeamData] = useState<any>(null);
  
  const currentOperation = useRef<string>('');

  const handleChooseRole = (selectedRole: 'owner' | 'manager') => {
    setRole(selectedRole);
    setStep(selectedRole === 'owner' ? 'owner-signup' : 'manager-signup');
    setError("");
    setSuccess("");
  };

  const handleBackToRoleSelection = () => {
    setStep('choose-role');
    setError("");
    setSuccess("");
    setEmail("");
    setPassword("");
    setName("");
    setOrganization("");
    setTeamCode("");
    setVerificationCode("");
    setTeamData(null);
  };

  const handleCreateAccount = async () => {
    if (isLoading) return;
    
    // Validation
    if (!email.trim() || !password.trim() || !name.trim()) {
      setError("Please fill in all required fields.");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }

    if (role === 'owner' && !organization.trim()) {
      setError("Please enter your organization name.");
      return;
    }

    if (role === 'manager' && !teamCode.trim()) {
      setError("Please enter the manager code provided by your team owner.");
      return;
    }

    setIsLoading(true);
    setError("");
    setSuccess("");

    try {
      const { invoke } = await import('@tauri-apps/api/tauri');
      
      let requestBody: any;
      let endpoint: string;
      
      if (role === 'owner') {
        // Owner creates new team
        endpoint = `${API_URL}/api/auth/register`;
        requestBody = { 
          email: email.trim().toLowerCase(),
          password: password,
          name: name.trim(),
          organization: organization.trim()
        };
      } else {
        // Manager joins existing team
        endpoint = `${API_URL}/api/teams/join-manager`;
        requestBody = {
          manager_code: teamCode.trim(),
          email: email.trim().toLowerCase(),
          password: password,
          name: name.trim()
        };
      }
      
      const response = await invoke('http_post', {
        url: endpoint,
        body: JSON.stringify(requestBody),
        headers: JSON.stringify({
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        })
      });
      
      const data = JSON.parse(response as string);

      if (data.success) {
        if (role === 'owner') {
          // Show team codes if available
          if (data.team && data.team.employee_code) {
            setTeamData(data.team);
            setStep('team-codes');
          } else {
            setSuccess("Account created successfully! Please check your email for verification code.");
            setStep('email-verification');
            if (data.team) {
              localStorage.setItem('pendingTeamData', JSON.stringify(data.team));
            }
          }
        } else {
          // Manager account created, go to sign in
          setSuccess("Manager account created successfully! You can now sign in.");
          setStep('manager-signin');
          setPassword("");
        }
      } else {
        // Check if it's actually a success but with a different message format
        if ("Manager registered successfully" in data.message) {
          setSuccess("Account created successfully! Please check your email for verification code.");
          setStep('email-verification');
          if (data.team) {
            localStorage.setItem('pendingTeamData', JSON.stringify(data.team));
          }
        } else {
          setError(data.message || 'Failed to create account. Please try again.');
        }
      }
    } catch (error) {
      console.error('Create account error:', error);
      setError('Failed to create account. Please check your connection and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSignIn = async () => {
    if (isLoading) return;
    
    if (!email.trim() || !password.trim()) {
      setError("Please fill in all fields.");
      return;
    }

    // For manager sign-in, require team code
    if (role === 'manager' && !teamCode.trim()) {
      setError("Please enter the manager code provided by your team owner.");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const { invoke } = await import('@tauri-apps/api/tauri');
      
      let requestBody: any = {
        email: email.trim().toLowerCase(),
        password: password
      };

      // Add team code for manager sign-in
      if (role === 'manager') {
        requestBody.team_code = teamCode.trim();
      }

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
        localStorage.setItem('authToken', data.token);
        
        const sessionData = {
          managerId: data.user.id,
          managerName: data.user.name,
          organization: data.user.organization || "Default Organization",
          token: data.token,
          isOwner: role === 'owner',
          ownerCode: role === 'owner' ? (teamData?.manager_code || 'OWNER') : null,
          managerCode: role === 'manager' ? teamCode : null
        };
        onAuthSuccess(sessionData);
      } else {
        setError(data.message || 'Sign in failed. Please check your credentials and try again.');
      }
    } catch (error) {
      console.error('Sign in error:', error);
      setError('Failed to sign in. Please check your connection and try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEmailVerification = async () => {
    if (isVerifying) return;

    if (!verificationCode.trim()) {
      setError("Please enter the verification code.");
      return;
    }

    setIsVerifying(true);
    setError("");

    try {
      const { invoke } = await import('@tauri-apps/api/tauri');
      const requestBody = {
        email: email.trim().toLowerCase(),
        verification_code: verificationCode.trim()
      };

      const response = await invoke('http_post', {
        url: `${API_URL}/api/auth/verify-email`,
        body: JSON.stringify(requestBody),
        headers: JSON.stringify({
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        })
      });

      const data = JSON.parse(response as string);

      if (data.success && data.user && data.token) {
        const storedTeamData = localStorage.getItem('pendingTeamData');
        if (storedTeamData) {
          const team = JSON.parse(storedTeamData);
          setTeamData(team);
          setStep('team-codes');
          localStorage.removeItem('pendingTeamData');
        } else {
          setSuccess("Email verified successfully! You can now sign in.");
          setStep('owner-signin');
          setPassword("");
        }
      } else {
        setError(data.message || 'Email verification failed. Please try again.');
      }
    } catch (error) {
      console.error('Email verification error:', error);
      setError('Failed to verify email. Please check your connection and try again.');
    } finally {
      setIsVerifying(false);
    }
  };

  // Role Selection Screen
  if (step === 'choose-role') {
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
                Welcome to ProductivityFlow
              </CardTitle>
              <p className="text-gray-600 text-lg mt-2">
                Choose your role to get started
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button
                onClick={() => handleChooseRole('owner')}
                className="w-full h-16 text-lg font-semibold bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white rounded-xl transition-all duration-200 transform hover:scale-105 shadow-lg"
              >
                <div className="flex items-center space-x-3">
                  <Crown className="h-6 w-6" />
                  <div className="text-left">
                    <div className="font-bold">I'm a Team Owner</div>
                    <div className="text-sm opacity-90">Create a new team and manage everything</div>
                  </div>
                </div>
              </Button>

              <Button
                onClick={() => handleChooseRole('manager')}
                className="w-full h-16 text-lg font-semibold bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-xl transition-all duration-200 transform hover:scale-105 shadow-lg"
              >
                <div className="flex items-center space-x-3">
                  <Users className="h-6 w-6" />
                  <div className="text-left">
                    <div className="font-bold">I'm a Team Manager</div>
                    <div className="text-sm opacity-90">Join an existing team with a manager code</div>
                  </div>
                </div>
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // Team Codes Display
  if (step === 'team-codes') {
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
                    Share this code with managers for team access
                  </p>
                </div>
              </div>

              <div className="flex flex-col space-y-3">
                <Button
                  onClick={() => setStep('owner-signin')}
                  className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold py-3 rounded-xl transition-all duration-200 transform hover:scale-105"
                >
                  Continue to Sign In
                </Button>
                
                <Button
                  onClick={handleBackToRoleSelection}
                  variant="outline"
                  className="w-full border-gray-300 text-gray-700 hover:bg-gray-50 font-semibold py-3 rounded-xl"
                >
                  Create Another Team
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // Email Verification
  if (step === 'email-verification') {
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
                We've sent a verification code to:
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
              <div>
                <label htmlFor="verificationCode" className="text-sm font-semibold text-gray-700 mb-2 block">
                  Verification Code *
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <CheckCircle className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="verificationCode"
                    type="text"
                    value={verificationCode}
                    onChange={(e) => setVerificationCode(e.target.value)}
                    placeholder="Enter 6-digit code"
                    className="flex h-12 w-full rounded-xl border border-gray-300 bg-white pl-12 pr-4 py-3 text-base focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all duration-200"
                    maxLength={6}
                  />
                </div>
              </div>

              <Button
                onClick={handleEmailVerification}
                disabled={isVerifying}
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
                onClick={handleBackToRoleSelection}
                variant="outline"
                className="w-full h-12 text-lg font-semibold border-gray-300 hover:bg-gray-50 rounded-xl transition-all duration-200"
              >
                <ArrowLeft className="mr-3 h-5 w-5" />
                Back to Role Selection
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // Main form (Sign up or Sign in)
  const isSignUp = step.includes('signup');
  const isOwner = role === 'owner';
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Card className="bg-white/90 backdrop-blur-sm border-0 rounded-2xl shadow-xl">
          <CardHeader className="text-center pb-6">
            <div className="flex items-center justify-center mb-6">
              <div className="p-3 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-xl">
                {isOwner ? <Crown className="h-8 w-8 text-white" /> : <Users className="h-8 w-8 text-white" />}
              </div>
            </div>
            <CardTitle className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              {isOwner ? 'Team Owner' : 'Team Manager'}
            </CardTitle>
            <p className="text-gray-600 text-lg mt-2">
              {isSignUp ? (isOwner ? 'Create your team' : 'Join an existing team') : 'Welcome back!'}
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

            <form onSubmit={(e) => { e.preventDefault(); isSignUp ? handleCreateAccount() : handleSignIn(); }} className="space-y-6">
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
                        className="flex h-12 w-full rounded-xl border border-gray-300 bg-white pl-12 pr-4 py-3 text-base focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200"
                        required
                      />
                    </div>
                  </div>

                  {isOwner && (
                    <div>
                      <label htmlFor="organization" className="text-sm font-semibold text-gray-700 mb-2 block">
                        Organization Name *
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
                          required
                        />
                      </div>
                    </div>
                  )}

                  {!isOwner && (
                    <div>
                      <label htmlFor="teamCode" className="text-sm font-semibold text-gray-700 mb-2 block">
                        Manager Code *
                      </label>
                      <div className="relative">
                        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                          <Users className="h-5 w-5 text-gray-400" />
                        </div>
                        <input
                          id="teamCode"
                          type="text"
                          value={teamCode}
                          onChange={(e) => setTeamCode(e.target.value)}
                          placeholder="Enter manager code from team owner"
                          className="flex h-12 w-full rounded-xl border border-gray-300 bg-white pl-12 pr-4 py-3 text-base focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200"
                          required
                        />
                      </div>
                      <p className="text-xs text-gray-500 mt-2">
                        Get this code from your team owner
                      </p>
                    </div>
                  )}
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
                {isSignUp && (
                  <p className="text-xs text-gray-500 mt-2">
                    Password must be at least 8 characters long
                  </p>
                )}
              </div>

              {!isSignUp && !isOwner && (
                <div>
                  <label htmlFor="teamCode" className="text-sm font-semibold text-gray-700 mb-2 block">
                    Manager Code *
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <Users className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                      id="teamCode"
                      type="text"
                      value={teamCode}
                      onChange={(e) => setTeamCode(e.target.value)}
                      placeholder="Enter manager code from team owner"
                      className="flex h-12 w-full rounded-xl border border-gray-300 bg-white pl-12 pr-4 py-3 text-base focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200"
                      required
                    />
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    Get this code from your team owner
                  </p>
                </div>
              )}

              <Button
                type="submit"
                disabled={isLoading}
                className="w-full h-12 text-lg font-semibold bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600 text-white rounded-xl transition-all duration-200 transform hover:scale-105 shadow-lg"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-3 h-5 w-5 animate-spin" />
                    {isSignUp ? "Creating Account..." : "Signing In..."}
                  </>
                ) : (
                  <>
                    {isSignUp ? (
                      <>
                        <UserPlus className="mr-3 h-5 w-5" />
                        {isOwner ? "Create Team" : "Join Team"}
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
                onClick={() => setStep(isSignUp ? (isOwner ? 'owner-signin' : 'manager-signin') : (isOwner ? 'owner-signup' : 'manager-signup'))}
                disabled={isLoading}
                className="w-full h-12 text-lg font-semibold border-gray-300 hover:bg-gray-50 rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSignUp ? "Already have an account? Sign in" : "Need an account? Create one"}
              </Button>
            </form>
            
            <Button
              onClick={handleBackToRoleSelection}
              variant="ghost"
              className="w-full text-gray-500 hover:text-gray-700"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Choose Different Role
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 