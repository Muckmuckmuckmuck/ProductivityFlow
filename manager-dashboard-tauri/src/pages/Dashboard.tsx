import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { 
  Users, 
  Clock, 
  TrendingUp, 
  Target, 
  AlertCircle, 
  Loader2, 
  Calendar,
  BarChart3,
  Activity,
  Shield,
  Download,
  Eye
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell
} from 'recharts';

// Updated to use the correct backend URL
const API_URL = "https://productivityflow-backend-v3.onrender.com";

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ComponentType<any>;
  change?: string;
  changeText?: string;
  color: string;
  trend?: 'up' | 'down' | 'neutral';
}

interface Analytics {
  totalHours: number;
  avgProductivity: number;
  goalsCompleted: number;
  activeMembers: number;
  totalMembers: number;
  hoursChange?: string;
  productivityChange?: string;
  weeklyTrends: WeeklyTrend[];
  dailyActivity: DailyActivity[];
  topApplications: TopApplication[];
  securityAlerts: SecurityAlert[];
}

interface WeeklyTrend {
  day: string;
  productivity: number;
  hours: number;
  members: number;
}

interface DailyActivity {
  hour: string;
  activeUsers: number;
  avgProductivity: number;
}

interface TopApplication {
  name: string;
  usage: number;
  productivity: number;
}

interface SecurityAlert {
  id: string;
  userId: string;
  userName: string;
  type: 'auto_clicker' | 'suspicious_pattern' | 'idle_time' | 'irregular_activity';
  timestamp: string;
  severity: 'low' | 'medium' | 'high';
  description: string;
}

interface Performance {
  topPerformers: Array<{
    userName: string;
    overallScore: number;
  }>;
  needsImprovement: Array<{
    userName: string;
    overallScore: number;
  }>;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, change, changeText, color, trend }) => {
  const Icon = icon;
  const getTrendColor = () => {
    if (trend === 'up') return 'text-green-600';
    if (trend === 'down') return 'text-red-600';
    return 'text-gray-600';
  };

  const getTrendIcon = () => {
    if (trend === 'up') return '↗';
    if (trend === 'down') return '↘';
    return '→';
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium text-gray-500">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <div className="text-3xl font-bold text-gray-800">{value}</div>
          <div className={`p-2 rounded-full bg-${color}-100`}>
            <Icon className={`h-6 w-6 text-${color}-600`} />
          </div>
        </div>
        {change && (
          <p className="text-xs text-gray-500 mt-2">
            <span className={`font-semibold ${getTrendColor()}`}>
              {getTrendIcon()} {change}
            </span> {changeText}
          </p>
        )}
      </CardContent>
    </Card>
  );
};

export default function DashboardPage() {
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [performance, setPerformance] = useState<Performance | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const [selectedTimeframe, setSelectedTimeframe] = useState<'week' | 'month'>('week');

  useEffect(() => {
    fetchAnalytics();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchAnalytics, 30000);
    
    return () => clearInterval(interval);
  }, [retryCount, selectedTimeframe]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log("Fetching teams...");
      
      // Add timeout for requests
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000);
      
      const teamsResponse = await fetch(`${API_URL}/api/teams`, {
        signal: controller.signal,
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
      
      clearTimeout(timeoutId);
      
      if (!teamsResponse.ok) {
        if (teamsResponse.status === 401) {
          throw new Error("Authentication required. Please log in again.");
        } else if (teamsResponse.status >= 500) {
          throw new Error("Server error. Please try again later.");
        } else {
          throw new Error(`Failed to fetch teams (${teamsResponse.status})`);
        }
      }
      
      const teamsData = await teamsResponse.json();
      console.log("Teams data:", teamsData);
      
      // Handle API errors gracefully
      if (teamsData.error) {
        throw new Error(teamsData.error);
      }
      
      const teams = teamsData.teams || [];
      
      if (teams.length === 0) {
        setError("No teams found. Create a team to get started.");
        return;
      }
      
      const firstTeamId = teams[0].id;
      console.log("Fetching stats for team:", firstTeamId);
      
      // Fetch both analytics and performance data with timeout
      const fetchWithTimeout = (url: string) => {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 15000);
        
        return fetch(url, { 
          signal: controller.signal,
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        }).finally(() => clearTimeout(timeoutId));
      };
      
      const [analyticsResponse, performanceResponse] = await Promise.allSettled([
        fetchWithTimeout(`${API_URL}/api/teams/${firstTeamId}/stats`),
        fetchWithTimeout(`${API_URL}/api/teams/${firstTeamId}/performance`)
      ]);
      
      // Handle analytics response
      if (analyticsResponse.status === 'fulfilled' && analyticsResponse.value.ok) {
        const analyticsData = await analyticsResponse.value.json();
        console.log("Analytics data:", analyticsData);
        
        // Enhance with mock data for visualizations
        const enhancedAnalytics = {
          ...analyticsData,
          weeklyTrends: generateWeeklyTrends(),
          dailyActivity: generateDailyActivity(),
          topApplications: generateTopApplications(),
          securityAlerts: generateSecurityAlerts()
        };
        
        setAnalytics(enhancedAnalytics);
      } else {
        console.error("Failed to fetch analytics:", analyticsResponse);
        // Set default analytics with mock visualization data
        setAnalytics({
          totalHours: 0,
          avgProductivity: 0,
          goalsCompleted: 0,
          activeMembers: 0,
          totalMembers: teams[0]?.memberCount || 0,
          weeklyTrends: generateWeeklyTrends(),
          dailyActivity: generateDailyActivity(),
          topApplications: generateTopApplications(),
          securityAlerts: generateSecurityAlerts()
        });
      }
      
      // Handle performance response
      if (performanceResponse.status === 'fulfilled' && performanceResponse.value.ok) {
        const performanceData = await performanceResponse.value.json();
        console.log("Performance data:", performanceData);
        setPerformance(performanceData);
      } else {
        console.error("Failed to fetch performance:", performanceResponse);
        // Set default performance to prevent white screen
        setPerformance({
          topPerformers: [],
          needsImprovement: []
        });
      }
      
    } catch (error: any) {
      console.error("Error fetching analytics:", error);
      
      let errorMessage = "Failed to load dashboard data. Please try again.";
      
      if (error.name === 'AbortError') {
        errorMessage = "Request timed out. Please check your connection.";
      } else if (error.message.includes('Failed to fetch')) {
        errorMessage = "Cannot connect to server. Please check your internet connection.";
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Mock data generators for visualizations
  const generateWeeklyTrends = (): WeeklyTrend[] => {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    return days.map(day => ({
      day,
      productivity: Math.floor(Math.random() * 40) + 60, // 60-100%
      hours: Math.floor(Math.random() * 4) + 6, // 6-10 hours
      members: Math.floor(Math.random() * 3) + 2 // 2-5 members
    }));
  };

  const generateDailyActivity = (): DailyActivity[] => {
    return Array.from({ length: 24 }, (_, i) => ({
      hour: `${i}:00`,
      activeUsers: Math.floor(Math.random() * 5) + 1,
      avgProductivity: Math.floor(Math.random() * 30) + 70
    }));
  };

  const generateTopApplications = (): TopApplication[] => {
    const apps = [
      { name: 'VS Code', usage: 45, productivity: 95 },
      { name: 'Chrome', usage: 30, productivity: 75 },
      { name: 'Slack', usage: 15, productivity: 60 },
      { name: 'Terminal', usage: 10, productivity: 90 }
    ];
    return apps;
  };

  const generateSecurityAlerts = (): SecurityAlert[] => {
    return [
      {
        id: '1',
        userId: 'user1',
        userName: 'John Doe',
        type: 'suspicious_pattern',
        timestamp: new Date().toISOString(),
        severity: 'medium',
        description: 'Unusual activity pattern detected - consistent clicking intervals'
      }
    ];
  };

  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
  };

  const displayValue = (value: number | null | undefined, suffix = '') => {
    if (loading) return '...';
    return value !== null && value !== undefined ? `${value}${suffix}` : '0' + suffix;
  };

  const getProductivityTrend = () => {
    if (!analytics?.weeklyTrends) return 'neutral';
    const current = analytics.weeklyTrends[analytics.weeklyTrends.length - 1]?.productivity || 0;
    const previous = analytics.weeklyTrends[analytics.weeklyTrends.length - 2]?.productivity || 0;
    if (current > previous) return 'up';
    if (current < previous) return 'down';
    return 'neutral';
  };

  const renderPerformanceSection = () => {
    if (loading) {
      return (
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <h4 className="font-semibold text-green-600 mb-2">🏆 Top Performers (Raise Candidates)</h4>
            <div className="text-sm text-gray-500">Loading...</div>
          </div>
          <div>
            <h4 className="font-semibold text-orange-600 mb-2">⚠️ Needs Improvement</h4>
            <div className="text-sm text-gray-500">Loading...</div>
          </div>
        </div>
      );
    }

    if (!performance || (!performance.topPerformers?.length && !performance.needsImprovement?.length)) {
      return (
        <div className="text-center py-8">
          <p className="text-gray-500">No performance data available yet.</p>
          <p className="text-sm text-gray-400">Add some activity data to see performance analysis.</p>
        </div>
      );
    }

    return (
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <h4 className="font-semibold text-green-600 mb-2">🏆 Top Performers (Raise Candidates)</h4>
          <div className="space-y-2 text-sm">
            {performance.topPerformers?.length > 0 ? (
              performance.topPerformers.map((performer, index) => (
                <div key={index} className="flex justify-between items-center p-2 bg-green-50 rounded">
                  <span>{performer.userName}</span>
                  <span className="text-green-600 font-medium">{performer.overallScore}% score</span>
                </div>
              ))
            ) : (
              <div className="text-gray-500 text-center py-4">
                No top performers yet (need 90%+ score)
              </div>
            )}
          </div>
        </div>
        <div>
          <h4 className="font-semibold text-orange-600 mb-2">⚠️ Needs Improvement</h4>
          <div className="space-y-2 text-sm">
            {performance.needsImprovement?.length > 0 ? (
              performance.needsImprovement.map((performer, index) => (
                <div key={index} className="flex justify-between items-center p-2 bg-orange-50 rounded">
                  <span>{performer.userName}</span>
                  <span className="text-orange-600 font-medium">{performer.overallScore}% score</span>
                </div>
              ))
            ) : (
              <div className="text-gray-500 text-center py-4">
                No underperformers (everyone above 60%)
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const renderWeeklyTrendsChart = () => {
    if (!analytics?.weeklyTrends) return null;

    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <TrendingUp className="mr-2 h-5 w-5" />
            Weekly Productivity Trends
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={analytics.weeklyTrends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="productivity" fill="#3b82f6" name="Productivity %" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    );
  };

  const renderDailyActivityChart = () => {
    if (!analytics?.dailyActivity) return null;

    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Activity className="mr-2 h-5 w-5" />
            Daily Activity Pattern
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={analytics.dailyActivity}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="avgProductivity" stroke="#10b981" name="Avg Productivity %" />
              <Line type="monotone" dataKey="activeUsers" stroke="#f59e0b" name="Active Users" />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    );
  };

  const renderTopApplicationsChart = () => {
    if (!analytics?.topApplications) return null;

    const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'];

    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <BarChart3 className="mr-2 h-5 w-5" />
            Top Productive Applications
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={analytics.topApplications}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, usage }) => `${name} (${usage}%)`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="usage"
                >
                  {analytics.topApplications.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="space-y-2">
              {analytics.topApplications.map((app, index) => (
                <div key={app.name} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <span className="text-sm font-medium">{app.name}</span>
                  <div className="text-right">
                    <div className="text-sm text-gray-600">{app.usage}% usage</div>
                    <div className="text-xs text-green-600">{app.productivity}% productive</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  const renderSecurityAlerts = () => {
    if (!analytics?.securityAlerts?.length) return null;

    return (
      <Card className="border-orange-200">
        <CardHeader>
          <CardTitle className="flex items-center text-orange-600">
            <Shield className="mr-2 h-5 w-5" />
            Security Alerts
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {analytics.securityAlerts.map(alert => (
              <div key={alert.id} className="flex items-center justify-between p-3 bg-orange-50 border border-orange-200 rounded-lg">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-medium">{alert.userName}</span>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      alert.severity === 'high' ? 'bg-red-100 text-red-800' :
                      alert.severity === 'medium' ? 'bg-orange-100 text-orange-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {alert.severity}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">{alert.description}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(alert.timestamp).toLocaleString()}
                  </p>
                </div>
                <button className="px-3 py-1 text-sm bg-orange-100 text-orange-700 rounded hover:bg-orange-200">
                  Review
                </button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  };

  // Show error state
  if (error && !loading) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-800">Welcome back, Manager!</h1>
          <p className="text-gray-500">Dashboard</p>
        </div>
        
        <Card className="border-red-200">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <AlertCircle className="h-12 w-12 text-red-500 mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Unable to Load Dashboard</h3>
            <p className="text-gray-600 text-center mb-4 max-w-md">{error}</p>
            <button
              onClick={handleRetry}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              <span>Try Again</span>
            </button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Show loading state
  if (loading) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-800">Welcome back, Manager!</h1>
          <p className="text-gray-500">Loading your dashboard...</p>
        </div>
        
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardContent className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
              </CardContent>
            </Card>
          ))}
        </div>
        
        <Card>
          <CardContent className="flex items-center justify-center py-12">
            <div className="text-center">
              <Loader2 className="h-8 w-8 animate-spin text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">Loading performance data...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-800">Welcome back, Manager!</h1>
          <p className="text-gray-500">Here's what's happening with your team's productivity today.</p>
          <p className="text-xs text-gray-400 mt-1">Auto-refreshing every 30 seconds</p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setSelectedTimeframe('week')}
            className={`px-3 py-1 rounded-md text-sm ${
              selectedTimeframe === 'week' 
                ? 'bg-blue-100 text-blue-700' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Week
          </button>
          <button
            onClick={() => setSelectedTimeframe('month')}
            className={`px-3 py-1 rounded-md text-sm ${
              selectedTimeframe === 'month' 
                ? 'bg-blue-100 text-blue-700' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Month
          </button>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <StatCard 
          title="Total Team Hours" 
          value={displayValue(analytics?.totalHours, 'h')} 
          icon={Clock} 
          change={analytics?.hoursChange || ""} 
          changeText="from yesterday" 
          color="blue"
          trend={getProductivityTrend()}
        />
        <StatCard 
          title="Avg Productivity" 
          value={displayValue(analytics?.avgProductivity, '%')} 
          icon={TrendingUp} 
          change={analytics?.productivityChange || ""} 
          changeText="from last week" 
          color="green"
          trend={getProductivityTrend()}
        />
        <StatCard 
          title="Goals Completed" 
          value={displayValue(analytics?.goalsCompleted)} 
          icon={Target} 
          change="" 
          changeText="" 
          color="orange" 
        />
        <StatCard 
          title="Active Members" 
          value={displayValue(analytics?.activeMembers)} 
          icon={Users} 
          change={analytics?.totalMembers ? `/ ${analytics.totalMembers}` : ""} 
          changeText="currently tracking" 
          color="teal" 
        />
      </div>

      {/* Security Alerts */}
      {renderSecurityAlerts()}

      {/* Charts Grid */}
      <div className="grid gap-6 md:grid-cols-2">
        {renderWeeklyTrendsChart()}
        {renderDailyActivityChart()}
      </div>

      {/* Top Applications */}
      {renderTopApplicationsChart()}

      {/* Performance Analysis Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <TrendingUp className="mr-2 h-5 w-5" />
            Performance Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          {renderPerformanceSection()}
          <div className="mt-4 p-3 bg-blue-50 rounded">
            <p className="text-sm text-blue-700">
              <strong>Analysis:</strong> Efficiency calculated as (Productive Hours / Total Hours) × 100. 
              Consider raises for 90%+ efficiency, coaching for &lt;60% efficiency.
            </p>
          </div>
        </CardContent>
      </Card>
      
      {/* Debug info */}
      <Card className="bg-gray-50">
        <CardHeader>
          <CardTitle className="text-sm">Debug Info</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-xs text-gray-600">
            <p>API URL: {API_URL}</p>
            <p>Loading: {loading ? 'Yes' : 'No'}</p>
            <p>Analytics: {analytics ? 'Loaded' : 'Not loaded'}</p>
            <p>Timeframe: {selectedTimeframe}</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}