import { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/tauri';
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { Badge } from './ui/Badge';
import { 
  Play, 
  Square, 
  Activity, 
  Clock, 
  TrendingUp, 
  Target, 
  Loader2,
  AlertCircle,
  CheckCircle,
  BarChart3,
  Calendar,
  Zap,
  Brain,
  Copy
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
const API_URL = "https://my-home-backend-7m6d.onrender.com";

interface DailySummary {
  summary: string;
  accomplishments: string[];
  focus_time_hours: number;
  breaks_taken: number;
  productivity_score: number;
  total_time_hours: number;
  date: string;
}

interface ProductivityData {
  hourly_productivity: Array<{
    hour: string;
    productivity: number;
  }>;
  app_breakdown: Array<{
    app: string;
    time_minutes: number;
    productivity: number;
  }>;
  weekly_trend: Array<{
    day: string;
    productivity: number;
    hours: number;
  }>;
}

interface Session {
  teamId: string;
  teamName: string;
  userId: string;
  userName: string;
  role: string;
  token: string;
}

interface TrackingViewProps {
  session: Session;
  onLogout: () => void;
}

export default function TrackingView({ session, onLogout }: TrackingViewProps) {
  const [isTracking, setIsTracking] = useState(false);
  const [currentActivity, setCurrentActivity] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [dailySummary, setDailySummary] = useState<DailySummary | null>(null);
  const [productivityData, setProductivityData] = useState<ProductivityData | null>(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [reportLoading, setReportLoading] = useState(false);
  const [dailyReport, setDailyReport] = useState<string | null>(null);
  const [reportCopied, setReportCopied] = useState(false);

  useEffect(() => {
    // Check if tracking is already active on component mount
    checkTrackingStatus();
  }, []);

  const checkTrackingStatus = async () => {
    try {
      const activity = await invoke('get_current_activity');
      // activity is an object, not a string
      const activityData = activity as any;
      setIsTracking(!!activityData);
      setCurrentActivity(activityData ? `${activityData.active_app} - ${activityData.window_title}` : '');
    } catch (error) {
      console.error('Error checking tracking status:', error);
    }
  };

  const startTracking = async () => {
    try {
      setLoading(true);
      setError(null);
      
      await invoke('start_tracking', {
        user_id: session.userId,
        team_id: session.teamId,
        token: session.token
      });
      setIsTracking(true);
      setCurrentActivity('Starting tracking...');
      
      // Update activity every 30 seconds
      const interval = setInterval(async () => {
        try {
          const activity = await invoke('get_current_activity');
          const activityData = activity as any;
          setCurrentActivity(activityData ? `${activityData.active_app} - ${activityData.window_title}` : 'No activity detected');
        } catch (error) {
          console.error('Error updating activity:', error);
        }
      }, 30000);
      
      // Cleanup interval on component unmount
      return () => clearInterval(interval);
      
    } catch (error: any) {
      console.error('Error starting tracking:', error);
      setError('Failed to start tracking. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const stopTracking = async () => {
    try {
      setLoading(true);
      setError(null);
      
      await invoke('stop_tracking');
      setIsTracking(false);
      setCurrentActivity('');
      
      // Refresh analytics after stopping
      if (showAnalytics) {
        fetchAnalytics();
      }
      
    } catch (error: any) {
      console.error('Error stopping tracking:', error);
      setError('Failed to stop tracking. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    try {
      setAnalyticsLoading(true);
      setError(null);

      // Fetch daily summary with authentication using Tauri HTTP
      const summaryResponse = await invoke('http_get', {
        url: `${API_URL}/api/employee/daily-summary`,
        headers: JSON.stringify({
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.token}`
        })
      });

      if (summaryResponse) {
        const summaryData = JSON.parse(summaryResponse as string);
        setDailySummary(summaryData);
      } else {
        // Set empty summary if API call fails
        setDailySummary({
          summary: "No activity data available yet",
          accomplishments: [],
          focus_time_hours: 0,
          breaks_taken: 0,
          productivity_score: 0,
          total_time_hours: 0,
          date: new Date().toISOString().split('T')[0]
        });
      }

      // For now, set empty productivity data since we don't have that endpoint yet
      // This can be populated with real API calls when those endpoints are available
      setProductivityData({
        hourly_productivity: [],
        app_breakdown: [],
        weekly_trend: []
      });

    } catch (error: any) {
      console.error('Error fetching analytics:', error);
      setError('Failed to load analytics. Please try again.');
      
      // Set empty data on error
      setDailySummary({
        summary: "Unable to load activity data",
        accomplishments: [],
        focus_time_hours: 0,
        breaks_taken: 0,
        productivity_score: 0,
        total_time_hours: 0,
        date: new Date().toISOString().split('T')[0]
      });
      
      setProductivityData({
        hourly_productivity: [],
        app_breakdown: [],
        weekly_trend: []
      });
    } finally {
      setAnalyticsLoading(false);
    }
  };

  const toggleAnalytics = () => {
    if (!showAnalytics) {
      fetchAnalytics();
    }
    setShowAnalytics(!showAnalytics);
  };

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

  const formatReportForClipboard = (report: string) => {
    // Simple formatting for demonstration. In a real app, you'd parse JSON and format it nicely.
    return `Productivity Report:\n\n${report}`;
  };

  const generateDailyReport = async () => {
    try {
      setReportLoading(true);
      setError(null);
      
      const { invoke } = await import('@tauri-apps/api/tauri');
      
      const response = await invoke('http_post', {
        url: `${API_URL}/api/employee/generate-daily-report`,
        body: JSON.stringify({
          include_hourly_summaries: true,
          include_productivity_insights: true,
          format: 'claude_3_haiku'
        }),
        headers: JSON.stringify({
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.token}`
        })
      });
      
      const data = JSON.parse(response as string);
      
      if (data.success) {
        setDailyReport(data.report);
      } else {
        setError('Failed to generate daily report. Please try again.');
      }
    } catch (error: any) {
      console.error('Error generating daily report:', error);
      setError('Failed to generate daily report. Please try again.');
    } finally {
      setReportLoading(false);
    }
  };

  const copyReportToClipboard = async () => {
    if (!dailyReport) return;
    
    try {
      const formattedReport = formatReportForClipboard(dailyReport);
      await navigator.clipboard.writeText(formattedReport);
      setReportCopied(true);
      setTimeout(() => setReportCopied(false), 2000);
    } catch (error) {
      console.error('Error copying to clipboard:', error);
      setError('Failed to copy report to clipboard. Please try again.');
    }
  };

  // Enhanced error handling and loading states
  const handleStartTracking = async () => {
    if (isTracking) return; // Prevent multiple clicks
    await startTracking();
  };

  const handleStopTracking = async () => {
    if (!isTracking) return; // Prevent multiple clicks
    await stopTracking();
  };

  const handleGenerateReport = async () => {
    if (reportLoading) return; // Prevent multiple clicks
    await generateDailyReport();
  };

  const handleCopyReport = async () => {
    if (reportCopied) return; // Prevent multiple clicks
    await copyReportToClipboard();
  };

  // Keyboard shortcuts and QOL improvements
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      // Spacebar to start/stop tracking
      const target = event.target as HTMLElement;
      if (event.code === 'Space' && !target?.matches('input, textarea')) {
        event.preventDefault();
        if (isTracking) {
          handleStopTracking();
        } else {
          handleStartTracking();
        }
      }
      
      // Ctrl/Cmd + R to refresh data
      if ((event.ctrlKey || event.metaKey) && event.key === 'r') {
        event.preventDefault();
        fetchAnalytics();
      }
      
      // Ctrl/Cmd + G to generate report
      if ((event.ctrlKey || event.metaKey) && event.key === 'g') {
        event.preventDefault();
        handleGenerateReport();
      }
      
      // Escape to clear errors
      if (event.key === 'Escape' && error) {
        setError(null);
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [isTracking, error, reportLoading]);

  // Auto-refresh analytics every 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      if (showAnalytics) {
        fetchAnalytics();
      }
    }, 5 * 60 * 1000); // 5 minutes

    return () => clearInterval(interval);
  }, [showAnalytics]);



  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      <div className="max-w-4xl mx-auto p-6 space-y-6">
        {/* Header */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/20">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-2">
                WorkFlow Monitor
              </h1>
              <p className="text-gray-600 text-lg">Track your productivity and boost performance</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm font-semibold text-gray-900">{session.userName}</p>
                <p className="text-xs text-gray-500">{session.teamName}</p>
              </div>
              <Button 
                onClick={onLogout}
                variant="outline"
                size="sm"
                className="text-red-600 border-red-300 hover:bg-red-50 transition-colors"
              >
                Logout
              </Button>
            </div>
          </div>
        </div>

        {/* Main Tracking Card */}
        <Card className="bg-white/90 backdrop-blur-sm border-0 shadow-xl">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center justify-between text-2xl">
              <span className="flex items-center">
                <div className="p-2 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg mr-3">
                  <Activity className="h-6 w-6 text-white" />
                </div>
                Activity Tracking
              </span>
              <Badge className={`px-4 py-2 text-sm font-semibold ${
                isTracking 
                  ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-lg' 
                  : 'bg-gradient-to-r from-gray-400 to-gray-500 text-white'
              }`}>
                {isTracking ? '🟢 Active' : '⚪ Inactive'}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {error && (
              <div className="flex items-center p-4 bg-red-50 border border-red-200 rounded-xl">
                <AlertCircle className="h-5 w-5 text-red-600 mr-3" />
                <span className="text-red-800 text-sm font-medium">{error}</span>
              </div>
            )}

            <div className="text-center py-8">
              {isTracking ? (
                <div className="space-y-6">
                  <div className="flex items-center justify-center space-x-3">
                    <div className="w-4 h-4 bg-green-500 rounded-full animate-pulse shadow-lg"></div>
                    <span className="text-lg font-medium text-gray-700">Currently tracking your activity...</span>
                  </div>
                  <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-6 rounded-2xl border border-green-200">
                    <p className="text-xl font-semibold text-gray-900 mb-2">Current Activity</p>
                    <p className="text-lg text-gray-700 font-medium">{currentActivity}</p>
                  </div>
                  <Button 
                    onClick={handleStopTracking} 
                    disabled={loading}
                    className="bg-gradient-to-r from-red-500 to-pink-500 hover:from-red-600 hover:to-pink-600 text-white px-8 py-3 text-lg font-semibold rounded-xl shadow-lg transition-all duration-200 transform hover:scale-105"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="h-5 w-5 mr-3 animate-spin" />
                        Stopping...
                      </>
                    ) : (
                      <>
                        <Square className="h-5 w-5 mr-3" />
                        Stop Tracking
                      </>
                    )}
                  </Button>
                </div>
              ) : (
                <div className="space-y-6">
                  <div className="flex items-center justify-center space-x-3">
                    <div className="w-4 h-4 bg-gray-400 rounded-full"></div>
                    <span className="text-lg font-medium text-gray-700">Ready to start tracking</span>
                  </div>
                  <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-2xl border border-blue-200">
                    <p className="text-xl font-semibold text-gray-900 mb-2">Start Your Work Session</p>
                    <p className="text-lg text-gray-700">Click the button below to begin monitoring your productivity</p>
                  </div>
                  <Button 
                    onClick={handleStartTracking} 
                    disabled={loading}
                    className="bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 text-white px-8 py-3 text-lg font-semibold rounded-xl shadow-lg transition-all duration-200 transform hover:scale-105"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="h-5 w-5 mr-3 animate-spin" />
                        Starting...
                      </>
                    ) : (
                      <>
                        <Play className="h-5 w-5 mr-3" />
                        Start Tracking
                      </>
                    )}
                  </Button>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Analytics Toggle */}
        <div className="text-center">
          <Button 
            onClick={toggleAnalytics}
            variant="outline"
            className="flex items-center space-x-2"
          >
            <BarChart3 className="h-4 w-4" />
            <span>{showAnalytics ? 'Hide' : 'Show'} Personal Analytics</span>
          </Button>
        </div>

        {/* Analytics Section */}
        {showAnalytics && (
          <div className="space-y-6">
            {/* Daily Summary */}
            {dailySummary && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Calendar className="mr-2 h-5 w-5" />
                    Today's Summary
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                    <div className="text-center p-4 bg-blue-50 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">{dailySummary.productivity_score}%</div>
                      <div className="text-sm text-blue-800">Productivity</div>
                    </div>
                    <div className="text-center p-4 bg-green-50 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">{dailySummary.focus_time_hours.toFixed(1)}h</div>
                      <div className="text-sm text-green-800">Focus Time</div>
                    </div>
                    <div className="text-center p-4 bg-orange-50 rounded-lg">
                      <div className="text-2xl font-bold text-orange-600">{dailySummary.total_time_hours.toFixed(1)}h</div>
                      <div className="text-sm text-orange-800">Total Time</div>
                    </div>
                    <div className="text-center p-4 bg-purple-50 rounded-lg">
                      <div className="text-2xl font-bold text-purple-600">{dailySummary.breaks_taken}</div>
                      <div className="text-sm text-purple-800">Breaks Taken</div>
                    </div>
                  </div>

                  <div className="mt-6">
                    <h4 className="font-medium text-gray-900 mb-3">Today's Accomplishments</h4>
                    <div className="space-y-2">
                      {dailySummary.accomplishments.map((accomplishment, index) => (
                        <div key={index} className="flex items-start space-x-2">
                          <CheckCircle className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                          <span className="text-sm text-gray-700">{accomplishment}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Productivity Charts */}
            {productivityData && (
              <div className="grid gap-6 md:grid-cols-2">
                {/* Hourly Productivity */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <TrendingUp className="mr-2 h-5 w-5" />
                      Hourly Productivity
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={200}>
                      <LineChart data={productivityData.hourly_productivity}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="hour" />
                        <YAxis />
                        <Tooltip />
                        <Line type="monotone" dataKey="productivity" stroke="#3b82f6" strokeWidth={2} />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                {/* App Breakdown */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Target className="mr-2 h-5 w-5" />
                      App Usage
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={200}>
                      <PieChart>
                        <Pie
                          data={productivityData.app_breakdown}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ app, time_minutes }) => `${app} (${time_minutes}m)`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="time_minutes"
                        >
                          {productivityData.app_breakdown.map((_, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                {/* Weekly Trend */}
                <Card className="md:col-span-2">
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <BarChart3 className="mr-2 h-5 w-5" />
                      Weekly Productivity Trend
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={200}>
                      <BarChart data={productivityData.weekly_trend}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="day" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="productivity" fill="#10b981" name="Productivity %" />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Loading State */}
            {analyticsLoading && (
              <Card>
                <CardContent className="flex items-center justify-center py-12">
                  <div className="text-center">
                    <Loader2 className="h-8 w-8 animate-spin text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">Loading your analytics...</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* End of Day Report */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center text-gray-900">
                <Calendar className="mr-2 h-5 w-5" />
                End of Day Report (Claude 3 Haiku)
              </CardTitle>
              <Button
                onClick={handleGenerateReport}
                disabled={reportLoading}
                className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 border-0 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {reportLoading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                    Generating...
                  </>
                ) : (
                  <>
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Generate Report
                  </>
                )}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {dailyReport && (
              <div className="space-y-4">
                <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200 p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="font-semibold text-blue-900 flex items-center">
                      <Calendar className="h-4 w-4 mr-2" />
                      Daily Report Summary
                    </h4>
                    <Badge className="bg-blue-100 text-blue-800 text-xs">
                      Claude 3 Haiku Generated
                    </Badge>
                  </div>
                  <div className="prose prose-sm max-w-none">
                    <p className="text-blue-800 leading-relaxed whitespace-pre-wrap">{dailyReport}</p>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <p className="text-sm text-gray-600">
                    💡 This report is optimized for daily stand-ups and project management tools
                  </p>
                  <Button
                    onClick={handleCopyReport}
                    disabled={reportCopied}
                    variant="outline"
                    className="border-blue-200 hover:bg-blue-50 transition-all duration-200"
                  >
                    {reportCopied ? (
                      <>
                        <CheckCircle className="h-4 w-4 mr-2 text-green-600" />
                        Copied!
                      </>
                    ) : (
                      <>
                        <Copy className="h-4 w-4 mr-2" />
                        Copy to Clipboard
                      </>
                    )}
                  </Button>
                </div>
              </div>
            )}
            
            {!dailyReport && !reportLoading && (
              <div className="text-center py-8">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <Calendar className="h-8 w-8 text-blue-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Generate Your Daily Report</h3>
                <p className="text-gray-600 mb-4">
                  Get an AI-powered summary of your day's work, ready for stand-ups and project updates.
                </p>
                <div className="flex items-center justify-center space-x-2 text-sm text-gray-500">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span>Claude 3 Haiku powered</span>
                  <span>•</span>
                  <span>~$5/year per employee</span>
                  <span>•</span>
                  <span>2 paragraphs optimized</span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Tips Section */}
        <Card className="bg-blue-50 border-blue-200">
          <CardHeader>
            <CardTitle className="flex items-center text-blue-800">
              <Brain className="mr-2 h-5 w-5" />
              Productivity Tips
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3 md:grid-cols-2">
              <div className="flex items-start space-x-2">
                <Zap className="h-4 w-4 text-blue-600 mt-0.5" />
                <div>
                  <div className="font-medium text-blue-800">Take Regular Breaks</div>
                  <div className="text-sm text-blue-700">Every 90 minutes for optimal focus</div>
                </div>
              </div>
              <div className="flex items-start space-x-2">
                <Target className="h-4 w-4 text-blue-600 mt-0.5" />
                <div>
                  <div className="font-medium text-blue-800">Set Clear Goals</div>
                  <div className="text-sm text-blue-700">Define what you want to accomplish</div>
                </div>
              </div>
              <div className="flex items-start space-x-2">
                <Clock className="h-4 w-4 text-blue-600 mt-0.5" />
                <div>
                  <div className="font-medium text-blue-800">Time Blocking</div>
                  <div className="text-sm text-blue-700">Dedicate specific time to tasks</div>
                </div>
              </div>
              <div className="flex items-start space-x-2">
                <TrendingUp className="h-4 w-4 text-blue-600 mt-0.5" />
                <div>
                  <div className="font-medium text-blue-800">Track Progress</div>
                  <div className="text-sm text-blue-700">Monitor your productivity trends</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}