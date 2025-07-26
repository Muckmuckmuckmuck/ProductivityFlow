import { useState, useEffect, useRef, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { 
  TrendingUp, 
  Users, 
  Target,
  Download,
  RefreshCw,
  AlertCircle,
  Search,
  Grid3X3,
  List,
  Clock,
  Activity,
  Zap,
  CheckCircle,
  XCircle,
  MoreVertical,
  Filter,
  ChevronDown,
  ChevronUp,
  Star,
  TrendingDown,
  Pause,
  Brain,
  BarChart3,
  Lightbulb,
  Eye,
  EyeOff,
  Gauge,
  Bell
} from 'lucide-react';

const API_URL = "https://my-home-backend-7m6d.onrender.com";

interface TeamMember {
  userId: string;
  name: string;
  role: string;
  department: string;
  productiveHours: number;
  unproductiveHours: number;
  totalHours: number;
  productivityScore: number;
  lastActive: string;
  status: 'online' | 'offline' | 'away';
  teamName?: string;
  isOnline: boolean;
  currentActivity?: string;
  focusSessions: number;
  breaksTaken: number;
  weeklyAverage: number;
  monthlyAverage: number;
  email?: string;
  avatar?: string;
}

interface TeamData {
  id: string;
  name: string;
  members: TeamMember[];
  totalProductiveHours: number;
  totalUnproductiveHours: number;
  averageProductivity: number;
  activeMembers: number;
  totalMembers: number;
}

interface AIInsights {
  summary: string;
  recommendations: string[];
  performance: 'exceptional' | 'strong' | 'good' | 'fair' | 'needs_improvement';
  trends: {
    productivity: 'up' | 'down' | 'stable';
    focus: 'up' | 'down' | 'stable';
    efficiency: 'up' | 'down' | 'stable';
  };
  peakHours: number[];
  focusScore: number;
  productivityTrend: 'improving' | 'stable' | 'declining';
  nextBreak: number;
  optimalWorkPeriods: string[];
}

interface RealTimeAnalytics {
  activeSessions: number;
  totalProductiveTime: number;
  averageProductivity: number;
  teamHealth: 'excellent' | 'good' | 'fair' | 'poor';
  alerts: Array<{
    type: 'warning' | 'info' | 'success';
    message: string;
    timestamp: string;
  }>;
  recentActivities: Array<{
    userId: string;
    name: string;
    action: string;
    timestamp: string;
  }>;
}

interface ComprehensiveAnalytics {
  productivityPatterns: {
    daily: number[];
    weekly: number[];
    monthly: number[];
  };
  focusMetrics: {
    averageSessionLength: number;
    totalSessions: number;
    breakEfficiency: number;
  };
  goalTracking: {
    completed: number;
    inProgress: number;
    behind: number;
    total: number;
  };
  appUsage: Array<{
    name: string;
    time: number;
    productive: boolean;
    category: string;
  }>;
}

type DateRange = 'today' | 'week' | 'month' | 'quarter' | 'custom';
type ViewMode = 'grid' | 'list' | 'detailed';

interface DashboardProps {
  session: {
    managerId: string;
    managerName: string;
    organization: string;
    token: string;
    isOwner: boolean;
    ownerCode: string | null;
    managerCode: string | null;
  };
}

export default function Dashboard({ session }: DashboardProps) {
  // Core state
  const [selectedTeam, setSelectedTeam] = useState<TeamData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Enhanced analytics state
  const [realTimeAnalytics, setRealTimeAnalytics] = useState<RealTimeAnalytics | null>(null);
  const [comprehensiveAnalytics, setComprehensiveAnalytics] = useState<ComprehensiveAnalytics | null>(null);
  const [showAdvancedAnalytics, setShowAdvancedAnalytics] = useState(false);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);

  // UI/UX state
  const [searchQuery, setSearchQuery] = useState('');
  const [dateRange] = useState<DateRange>('week');
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [sortField] = useState<keyof TeamMember>('productivityScore');
  const [sortDirection] = useState<'asc' | 'desc'>('desc');
  const [filters, setFilters] = useState({
    status: 'all',
    department: 'all',
    productivity: 'all'
  });

  // Loading states
  const [loadingSkeleton, setLoadingSkeleton] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [exporting, setExporting] = useState(false);

  // Modal states
  const [showEmployeeModal, setShowEmployeeModal] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState<TeamMember | null>(null);
  const [aiInsights, setAiInsights] = useState<AIInsights | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  // Refs
  const refreshIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Professional data fetching with error handling
  const fetchDashboardData = useCallback(async () => {
    try {
      setError(null);
      setLoadingSkeleton(true);

      const { invoke } = await import('@tauri-apps/api/tauri');
      
      const response = await invoke('http_get', { 
        url: `${API_URL}/api/teams/public`
      });
      
      const data = JSON.parse(response as string);
      
      if (data.success && data.teams && data.teams.length > 0) {
        setSelectedTeam(data.teams[0]);
      } else {
        setError('No team data available');
      }
    } catch (error: any) {
      console.error('Dashboard data fetch error:', error);
      setError('Failed to load dashboard data. Please check your connection and try again.');
    } finally {
      setLoadingSkeleton(false);
    }
  }, []);

  const fetchEmployeeInsights = useCallback(async (userId: string) => {
    try {
      const { invoke } = await import('@tauri-apps/api/tauri');
      
      const response = await invoke('http_get', { 
        url: `${API_URL}/api/employees/${userId}/summary`
      });
      
      const data = JSON.parse(response as string);
      
      if (data.success) {
        // Parse AI summary and extract insights
        const aiSummary = data.aiSummary || '';
        const insights: AIInsights = {
          summary: aiSummary,
          recommendations: extractRecommendations(aiSummary),
          performance: determinePerformance(data.productivityScore),
          trends: {
            productivity: 'stable',
            focus: 'stable',
            efficiency: 'stable'
          },
          peakHours: [9, 10, 14, 15], // Default peak hours
          focusScore: 0.75, // Default focus score
          productivityTrend: 'stable',
          nextBreak: 30, // Default next break time
          optimalWorkPeriods: ['9:00 AM - 11:00 AM', '2:00 PM - 4:00 PM']
        };
        setAiInsights(insights);
      }
    } catch (error: any) {
      console.error('Employee insights fetch error:', error);
      setError('Failed to load employee insights');
    }
  }, []);

  const extractRecommendations = (summary: string): string[] => {
    const recommendations: string[] = [];
    const lines = summary.split('\n');
    
    for (const line of lines) {
      if (line.includes('•') && (line.includes('Recommendation') || line.includes('Focus') || line.includes('Time Management'))) {
        const cleanRec = line.replace(/<[^>]*>/g, '').replace('•', '').trim();
        if (cleanRec) recommendations.push(cleanRec);
      }
    }
    
    return recommendations.length > 0 ? recommendations : [
      'Schedule focused work sessions during peak productivity hours',
      'Minimize context switching between tasks',
      'Take regular short breaks to maintain sustained focus'
    ];
  };

  const determinePerformance = (score: number): AIInsights['performance'] => {
    if (score >= 90) return 'exceptional';
    if (score >= 80) return 'strong';
    if (score >= 70) return 'good';
    if (score >= 60) return 'fair';
    return 'needs_improvement';
  };

  // Real-time data refresh
  const fetchRealTimeData = useCallback(async () => {
    if (!refreshing) {
      setRefreshing(true);
      await fetchDashboardData();
      setRefreshing(false);
    }
  }, [fetchDashboardData, refreshing]);

  // Enhanced analytics functions
  const fetchRealTimeAnalytics = useCallback(async () => {
    if (!selectedTeam) return;
    
    try {
      setAnalyticsLoading(true);
      const response = await fetch(`${API_URL}/api/analytics/realtime?team_id=${selectedTeam.id}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      const data = await response.json();
      if (data.success) {
        setRealTimeAnalytics(data.data);
      }
    } catch (error) {
      console.error('Real-time analytics fetch error:', error);
    } finally {
      setAnalyticsLoading(false);
    }
  }, [selectedTeam]);

  const fetchComprehensiveAnalytics = useCallback(async () => {
    if (!selectedTeam) return;
    
    try {
      setAnalyticsLoading(true);
      const response = await fetch(`${API_URL}/api/analytics/comprehensive?team_id=${selectedTeam.id}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      const data = await response.json();
      if (data.success) {
        setComprehensiveAnalytics(data.data);
      }
    } catch (error) {
      console.error('Comprehensive analytics fetch error:', error);
    } finally {
      setAnalyticsLoading(false);
    }
  }, [selectedTeam]);

  const fetchAIInsights = useCallback(async () => {
    if (!selectedTeam) return;
    
    try {
      const response = await fetch(`${API_URL}/api/analytics/ai-insights?team_id=${selectedTeam.id}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      const data = await response.json();
      if (data.success) {
        setAiInsights(data.data);
      }
    } catch (error) {
      console.error('AI insights fetch error:', error);
    }
  }, [selectedTeam]);

  // Load all analytics data
  const loadAllAnalytics = useCallback(async () => {
    await Promise.all([
      fetchRealTimeAnalytics(),
      fetchComprehensiveAnalytics(),
      fetchAIInsights()
    ]);
  }, [fetchRealTimeAnalytics, fetchComprehensiveAnalytics, fetchAIInsights]);

  // Load analytics when team changes
  useEffect(() => {
    if (selectedTeam) {
      loadAllAnalytics();
    }
  }, [selectedTeam, loadAllAnalytics]);

  // Auto-refresh analytics every 5 minutes
  useEffect(() => {
    if (!selectedTeam) return;
    
    const interval = setInterval(() => {
      loadAllAnalytics();
    }, 5 * 60 * 1000); // 5 minutes
    
    return () => clearInterval(interval);
  }, [selectedTeam, loadAllAnalytics]);

  // Search with debouncing
  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query);
    
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    
    searchTimeoutRef.current = setTimeout(() => {
      // Search logic is handled in filteredAndSortedMembers
    }, 300);
  }, []);

  // Professional filtering and sorting
  const filteredAndSortedMembers = useCallback(() => {
    if (!selectedTeam?.members) return [];
    
    let filtered = selectedTeam.members.filter(member => {
      const matchesSearch = member.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           member.email?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           member.department.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchesStatus = filters.status === 'all' || member.status === filters.status;
      const matchesDepartment = filters.department === 'all' || member.department === filters.department;
      
      let matchesProductivity = true;
      if (filters.productivity === 'high') matchesProductivity = member.productivityScore >= 80;
      else if (filters.productivity === 'medium') matchesProductivity = member.productivityScore >= 60 && member.productivityScore < 80;
      else if (filters.productivity === 'low') matchesProductivity = member.productivityScore < 60;
      
      return matchesSearch && matchesStatus && matchesDepartment && matchesProductivity;
    });
    
    // Professional sorting
    filtered.sort((a, b) => {
      const aValue = a[sortField];
      const bValue = b[sortField];
      
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortDirection === 'asc' 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }
      
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
      }
      
      return 0;
    });
    
    return filtered;
  }, [selectedTeam, searchQuery, filters, sortField, sortDirection]);

  // Professional employee click handler
  const handleEmployeeClick = useCallback(async (employee: TeamMember) => {
    setSelectedEmployee(employee);
    setShowEmployeeModal(true);
    setAiInsights(null); // Reset insights
    
    // Fetch AI insights
    await fetchEmployeeInsights(employee.userId);
  }, [fetchEmployeeInsights]);

  // Professional export functionality
  const handleExport = useCallback(async () => {
    try {
      setExporting(true);
      
      const { invoke } = await import('@tauri-apps/api/tauri');
      
      const reportData = {
        team: selectedTeam,
        dateRange,
        generatedAt: new Date().toISOString(),
        members: filteredAndSortedMembers()
      };
      
      await invoke('http_post', {
        url: `${API_URL}/api/reports/generate`,
        headers: JSON.stringify({
          'Content-Type': 'application/json'
        }),
        body: JSON.stringify(reportData)
      });
      
      setSuccess('Report exported successfully!');
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(null), 3000);
      
    } catch (error: any) {
      console.error('Export error:', error);
      setError('Failed to export report. Please try again.');
    } finally {
      setExporting(false);
    }
  }, [selectedTeam, dateRange, filteredAndSortedMembers]);

  // Professional refresh handler
  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchDashboardData();
    setRefreshing(false);
    setSuccess('Data refreshed successfully!');
    setTimeout(() => setSuccess(null), 2000);
  }, [fetchDashboardData]);

  // Professional status indicators
  const getStatusIndicator = useCallback((status: string, isOnline: boolean) => {
    const baseClasses = "w-2 h-2 rounded-full";
    
    if (isOnline) {
      return <div className={`${baseClasses} bg-green-500 animate-pulse`} title="Online" />;
    }
    
    switch (status) {
      case 'away':
        return <div className={`${baseClasses} bg-yellow-500`} title="Away" />;
      case 'offline':
        return <div className={`${baseClasses} bg-gray-400`} title="Offline" />;
      default:
        return <div className={`${baseClasses} bg-gray-400`} title="Unknown" />;
    }
  }, []);

  const getProductivityColor = useCallback((score: number) => {
    if (score >= 90) return 'text-green-600 bg-green-50 border-green-200';
    if (score >= 80) return 'text-blue-600 bg-blue-50 border-blue-200';
    if (score >= 70) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    if (score >= 60) return 'text-orange-600 bg-orange-50 border-orange-200';
    return 'text-red-600 bg-red-50 border-red-200';
  }, []);

  const getProductivityIcon = useCallback((score: number) => {
    if (score >= 90) return <Star className="w-4 h-4" />;
    if (score >= 80) return <TrendingUp className="w-4 h-4" />;
    if (score >= 70) return <CheckCircle className="w-4 h-4" />;
    if (score >= 60) return <Pause className="w-4 h-4" />;
    return <TrendingDown className="w-4 h-4" />;
  }, []);

  // Effects
  useEffect(() => {
    fetchDashboardData();
    
    // Set up real-time data refresh every 30 seconds
    refreshIntervalRef.current = setInterval(fetchRealTimeData, 30000);
    
    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
      }
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [fetchDashboardData, fetchRealTimeData]);

  // Professional loading skeleton
  const LoadingSkeleton = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader className="pb-2">
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            </CardHeader>
            <CardContent>
              <div className="h-8 bg-gray-200 rounded w-1/2"></div>
            </CardContent>
          </Card>
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {[...Array(6)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-6">
              <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
              <div className="h-6 bg-gray-200 rounded w-3/4"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );

  // Professional empty state
  const EmptyState = ({ title, description, icon: Icon, action }: {
    title: string;
    description: string;
    icon: any;
    action?: { label: string; onClick: () => void };
  }) => (
    <div className="text-center py-12">
      <Icon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
      <h3 className="text-lg font-medium text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-500 mb-6">{description}</p>
      {action && (
        <Button onClick={action.onClick} className="inline-flex items-center gap-2">
          <RefreshCw className="w-4 h-4" />
          {action.label}
        </Button>
      )}
    </div>
  );

  // Professional error display
  const ErrorDisplay = ({ error, onRetry }: { error: string; onRetry: () => void }) => (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
      <div className="flex items-start">
        <AlertCircle className="w-5 h-5 text-red-400 mt-0.5 mr-3 flex-shrink-0" />
        <div className="flex-1">
          <h3 className="text-sm font-medium text-red-800">Error</h3>
          <p className="text-sm text-red-700 mt-1">{error}</p>
          <button
            onClick={onRetry}
            className="text-sm text-red-600 hover:text-red-500 font-medium mt-2"
          >
            Try again
          </button>
        </div>
      </div>
    </div>
  );

  // Professional success display
  const SuccessDisplay = ({ message }: { message: string }) => (
    <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
      <div className="flex items-start">
        <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 mr-3 flex-shrink-0" />
        <div className="flex-1">
          <p className="text-sm text-green-700">{message}</p>
        </div>
      </div>
    </div>
  );

  if (loadingSkeleton) {
    return <LoadingSkeleton />;
  }

  const members = filteredAndSortedMembers();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Team Dashboard</h1>
            <p className="text-sm text-gray-600 mt-1">
              {selectedTeam?.name || 'Loading team data...'}
            </p>
          </div>
          
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              disabled={refreshing}
              className="inline-flex items-center gap-2"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            
            <Button
              onClick={handleExport}
              disabled={exporting}
              className="inline-flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              {exporting ? 'Exporting...' : 'Export Report'}
            </Button>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Error/Success Messages */}
        {error && <ErrorDisplay error={error} onRetry={handleRefresh} />}
        {success && <SuccessDisplay message={success} />}

        {/* Overview Cards */}
        {selectedTeam && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-blue-700 flex items-center gap-2">
                  <Users className="w-4 h-4" />
                  Total Members
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-900">{selectedTeam.totalMembers}</div>
                <p className="text-xs text-blue-600 mt-1">
                  {selectedTeam.activeMembers} active now
                </p>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-green-700 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4" />
                  Productive Hours
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-900">
                  {selectedTeam.totalProductiveHours.toFixed(1)}h
                </div>
                <p className="text-xs text-green-600 mt-1">
                  Today's total
                </p>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-purple-700 flex items-center gap-2">
                  <Target className="w-4 h-4" />
                  Avg Productivity
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-purple-900">
                  {selectedTeam.averageProductivity.toFixed(1)}%
                </div>
                <p className="text-xs text-purple-600 mt-1">
                  Team average
                </p>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-orange-700 flex items-center gap-2">
                  <Activity className="w-4 h-4" />
                  Active Members
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-orange-900">{selectedTeam.activeMembers}</div>
                <p className="text-xs text-orange-600 mt-1">
                  Currently working
                </p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Team Codes Section - Only for Owners */}
        {session.isOwner && selectedTeam && (
          <Card className="bg-gradient-to-br from-indigo-50 to-purple-50 border-indigo-200">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Users className="h-5 w-5 text-indigo-600" />
                <span>Team Access Codes</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl">
                  <h3 className="text-sm font-semibold text-blue-800 mb-2">Employee Code</h3>
                  <div className="flex items-center justify-between">
                    <code className="text-lg font-mono font-bold text-blue-900 bg-blue-100 px-3 py-2 rounded-lg">
                      {selectedTeam.id.slice(0, 8).toUpperCase()}
                    </code>
                    <Button
                      onClick={() => navigator.clipboard.writeText(selectedTeam.id.slice(0, 8).toUpperCase())}
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
                      {session.ownerCode || 'OWNER123'}
                    </code>
                    <Button
                      onClick={() => navigator.clipboard.writeText(session.ownerCode || 'OWNER123')}
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
            </CardContent>
          </Card>
        )}

        {/* Enhanced Analytics Section */}
        {selectedTeam && (
          <div className="space-y-6">
            {/* Analytics Header */}
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-gray-900">Advanced Analytics</h2>
                <p className="text-gray-600">Real-time insights and AI-powered recommendations</p>
              </div>
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={loadAllAnalytics}
                  disabled={analyticsLoading}
                >
                  <RefreshCw className={`h-4 w-4 mr-2 ${analyticsLoading ? 'animate-spin' : ''}`} />
                  Refresh Analytics
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowAdvancedAnalytics(!showAdvancedAnalytics)}
                >
                  {showAdvancedAnalytics ? <EyeOff className="h-4 w-4 mr-2" /> : <Eye className="h-4 w-4 mr-2" />}
                  {showAdvancedAnalytics ? 'Hide' : 'Show'} Advanced
                </Button>
              </div>
            </div>

            {/* Real-Time Analytics */}
            {realTimeAnalytics && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Gauge className="h-5 w-5 text-green-600" />
                      <span>Real-Time Team Health</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Active Sessions</span>
                        <span className="font-semibold">{realTimeAnalytics.activeSessions}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Total Productive Time</span>
                        <span className="font-semibold">{realTimeAnalytics.totalProductiveTime.toFixed(1)}h</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Average Productivity</span>
                        <span className="font-semibold">{realTimeAnalytics.averageProductivity.toFixed(1)}%</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Team Health</span>
                        <Badge variant={
                          realTimeAnalytics.teamHealth === 'excellent' ? 'default' :
                          realTimeAnalytics.teamHealth === 'good' ? 'secondary' :
                          realTimeAnalytics.teamHealth === 'fair' ? 'secondary' : 'destructive'
                        }>
                          {realTimeAnalytics.teamHealth}
                        </Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Bell className="h-5 w-5 text-orange-600" />
                      <span>Recent Alerts</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {realTimeAnalytics.alerts.length > 0 ? (
                        realTimeAnalytics.alerts.slice(0, 3).map((alert, index) => (
                          <div key={index} className="flex items-start space-x-3 p-2 bg-gray-50 rounded-lg">
                            <div className={`w-2 h-2 rounded-full mt-2 ${
                              alert.type === 'warning' ? 'bg-orange-500' :
                              alert.type === 'info' ? 'bg-blue-500' : 'bg-green-500'
                            }`} />
                            <div className="flex-1">
                              <p className="text-sm text-gray-700">{alert.message}</p>
                              <p className="text-xs text-gray-500">{new Date(alert.timestamp).toLocaleTimeString()}</p>
                            </div>
                          </div>
                        ))
                      ) : (
                        <p className="text-sm text-gray-500 text-center py-4">No recent alerts</p>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* AI Insights */}
            {aiInsights && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Brain className="h-5 w-5 text-purple-600" />
                    <span>AI-Powered Insights</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <Zap className="h-4 w-4 text-purple-600" />
                          <div>
                            <p className="font-medium">Peak Productivity Hours</p>
                            <p className="text-sm text-gray-600">
                              {aiInsights.peakHours.length > 0 
                                ? aiInsights.peakHours.map(h => `${h}:00`).join(', ')
                                : '9:00 AM - 11:00 AM, 2:00 PM - 4:00 PM'
                              }
                            </p>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <Target className="h-4 w-4 text-blue-600" />
                          <div>
                            <p className="font-medium">Focus Score</p>
                            <p className="text-sm text-gray-600">{Math.round(aiInsights.focusScore * 100)}% concentration</p>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <TrendingUp className="h-4 w-4 text-green-600" />
                          <div>
                            <p className="font-medium">Productivity Trend</p>
                            <Badge variant={
                              aiInsights.productivityTrend === 'improving' ? 'default' :
                              aiInsights.productivityTrend === 'stable' ? 'secondary' : 'destructive'
                            }>
                              {aiInsights.productivityTrend}
                            </Badge>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-4">
                      <h4 className="font-medium text-gray-900">AI Recommendations</h4>
                      <div className="space-y-2">
                        {aiInsights.recommendations.map((rec, index) => (
                          <div key={index} className="flex items-start space-x-2 p-2 bg-blue-50 rounded-lg">
                            <Lightbulb className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                            <p className="text-sm text-gray-700">{rec}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Advanced Analytics (Collapsible) */}
            {showAdvancedAnalytics && comprehensiveAnalytics && (
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <BarChart3 className="h-5 w-5 text-indigo-600" />
                      <span>Comprehensive Analytics</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div className="space-y-4">
                        <h4 className="font-medium text-gray-900">Focus Metrics</h4>
                        <div className="space-y-3">
                          <div className="flex justify-between">
                            <span className="text-sm text-gray-600">Avg Session Length</span>
                            <span className="font-semibold">{comprehensiveAnalytics.focusMetrics.averageSessionLength} min</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm text-gray-600">Total Sessions</span>
                            <span className="font-semibold">{comprehensiveAnalytics.focusMetrics.totalSessions}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm text-gray-600">Break Efficiency</span>
                            <span className="font-semibold">{comprehensiveAnalytics.focusMetrics.breakEfficiency.toFixed(1)}%</span>
                          </div>
                        </div>
                      </div>

                      <div className="space-y-4">
                        <h4 className="font-medium text-gray-900">Goal Tracking</h4>
                        <div className="space-y-3">
                          <div className="flex justify-between">
                            <span className="text-sm text-gray-600">Completed</span>
                            <span className="font-semibold text-green-600">{comprehensiveAnalytics.goalTracking.completed}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm text-gray-600">In Progress</span>
                            <span className="font-semibold text-blue-600">{comprehensiveAnalytics.goalTracking.inProgress}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm text-gray-600">Behind</span>
                            <span className="font-semibold text-red-600">{comprehensiveAnalytics.goalTracking.behind}</span>
                          </div>
                        </div>
                      </div>

                      <div className="space-y-4">
                        <h4 className="font-medium text-gray-900">App Usage</h4>
                        <div className="space-y-2">
                          {comprehensiveAnalytics.appUsage.slice(0, 3).map((app, index) => (
                            <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                              <div className="flex items-center space-x-2">
                                <div className={`w-2 h-2 rounded-full ${
                                  app.productive ? 'bg-green-500' : 'bg-red-500'
                                }`} />
                                <span className="text-sm font-medium">{app.name}</span>
                              </div>
                              <span className="text-sm text-gray-600">{app.time.toFixed(1)}h</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
        )}

        {/* Controls */}
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="Search members..."
                value={searchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                className="pl-10 w-64"
              />
            </div>
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
              className="inline-flex items-center gap-2"
            >
              <Filter className="w-4 h-4" />
              Filters
              {showFilters ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </Button>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant={viewMode === 'grid' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setViewMode('grid')}
            >
              <Grid3X3 className="w-4 h-4" />
            </Button>
            <Button
              variant={viewMode === 'list' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setViewMode('list')}
            >
              <List className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Filters */}
        {showFilters && (
          <Card className="p-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                <select
                  value={filters.status}
                  onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                >
                  <option value="all">All Status</option>
                  <option value="online">Online</option>
                  <option value="away">Away</option>
                  <option value="offline">Offline</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Department</label>
                <select
                  value={filters.department}
                  onChange={(e) => setFilters(prev => ({ ...prev, department: e.target.value }))}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                >
                  <option value="all">All Departments</option>
                  <option value="Engineering">Engineering</option>
                  <option value="Design">Design</option>
                  <option value="Marketing">Marketing</option>
                  <option value="Sales">Sales</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Productivity</label>
                <select
                  value={filters.productivity}
                  onChange={(e) => setFilters(prev => ({ ...prev, productivity: e.target.value }))}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                >
                  <option value="all">All Levels</option>
                  <option value="high">High (80%+)</option>
                  <option value="medium">Medium (60-79%)</option>
                  <option value="low">Low (&lt;60%)</option>
                </select>
              </div>
            </div>
          </Card>
        )}

        {/* Team Members */}
        {members.length === 0 ? (
          <EmptyState
            title="No members found"
            description="Try adjusting your search or filters to find team members."
            icon={Users}
            action={{ label: 'Clear filters', onClick: () => {
              setSearchQuery('');
              setFilters({ status: 'all', department: 'all', productivity: 'all' });
            }}}
          />
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {members.map((member) => (
              <div
                key={member.userId}
                className="hover:shadow-lg transition-shadow duration-200 cursor-pointer group"
                onClick={() => handleEmployeeClick(member)}
              >
                <Card>
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="relative">
                        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold">
                          {member.name.charAt(0).toUpperCase()}
                        </div>
                        {getStatusIndicator(member.status, member.isOnline)}
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                          {member.name}
                        </h3>
                        <p className="text-sm text-gray-500">{member.role}</p>
                      </div>
                    </div>
                    <MoreVertical className="w-4 h-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Productivity</span>
                      <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium border ${getProductivityColor(member.productivityScore)}`}>
                        {getProductivityIcon(member.productivityScore)}
                        {member.productivityScore.toFixed(1)}%
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">Productive</span>
                        <div className="font-semibold text-green-600">{member.productiveHours.toFixed(1)}h</div>
                      </div>
                      <div>
                        <span className="text-gray-600">Total</span>
                        <div className="font-semibold text-gray-900">{member.totalHours.toFixed(1)}h</div>
                      </div>
                    </div>

                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {member.focusSessions} sessions
                      </span>
                      <span>Last active: {new Date(member.lastActive).toLocaleTimeString()}</span>
                                         </div>
                   </div>
                 </CardContent>
                 </Card>
               </div>
             ))}
          </div>
        )}
      </div>

      {/* Employee Modal */}
      {showEmployeeModal && selectedEmployee && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold text-lg">
                    {selectedEmployee.name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">{selectedEmployee.name}</h2>
                    <p className="text-gray-600">{selectedEmployee.role} • {selectedEmployee.department}</p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowEmployeeModal(false)}
                >
                  <XCircle className="w-5 h-5" />
                </Button>
              </div>
            </div>

            <div className="p-6 space-y-6">
              {/* Performance Overview */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">{selectedEmployee.productivityScore.toFixed(1)}%</div>
                  <div className="text-sm text-blue-600">Productivity</div>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">{selectedEmployee.productiveHours.toFixed(1)}h</div>
                  <div className="text-sm text-green-600">Productive</div>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">{selectedEmployee.focusSessions}</div>
                  <div className="text-sm text-purple-600">Focus Sessions</div>
                </div>
                <div className="text-center p-4 bg-orange-50 rounded-lg">
                  <div className="text-2xl font-bold text-orange-600">{selectedEmployee.weeklyAverage.toFixed(1)}h</div>
                  <div className="text-sm text-orange-600">Weekly Avg</div>
                </div>
              </div>

              {/* AI Insights */}
              {aiInsights ? (
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                    <Zap className="w-5 h-5 text-blue-500" />
                    AI Insights
                  </h3>
                  
                  <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
                    <div 
                      className="prose prose-sm max-w-none"
                      dangerouslySetInnerHTML={{ __html: aiInsights.summary }}
                    />
                  </div>

                  {aiInsights.recommendations.length > 0 && (
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Recommendations</h4>
                      <ul className="space-y-2">
                        {aiInsights.recommendations.map((rec, index) => (
                          <li key={index} className="flex items-start gap-2 text-sm text-gray-700">
                            <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                            {rec}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ) : (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <span className="ml-2 text-gray-600">Loading AI insights...</span>
                </div>
              )}

              {/* Current Activity */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Current Activity</h3>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${selectedEmployee.isOnline ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`} />
                    <div>
                      <div className="font-medium text-gray-900">
                        {selectedEmployee.currentActivity || 'No activity recorded'}
                      </div>
                      <div className="text-sm text-gray-500">
                        Last active: {new Date(selectedEmployee.lastActive).toLocaleString()}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}