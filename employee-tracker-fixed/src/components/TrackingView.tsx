import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { Badge } from './ui/Badge';
import { 
  Play, 
  Square, 
  TrendingUp, 
  Clock, 
  Activity, 
  Target, 
  BarChart3,
  PieChart,
  RefreshCw,
  AlertCircle,
  User,
  Zap,
  Award,
  Timer,
  Monitor,
  Coffee,
  Briefcase,
  Download,
  FileText,
  Sparkles,
  Bell,
  Calendar,
  CheckCircle,
  Copy,
  Clipboard,
  Search
} from 'lucide-react';

const API_URL = "https://productivityflow-backend-496367590729.us-central1.run.app";

interface Session {
  teamId: string;
  teamName: string;
  userId: string;
  userName: string;
  role: string;
  token: string;
}

interface DailySummary {
  total_hours: number;
  productive_hours: number;
  unproductive_hours: number;
  productivity_score: number;
  focus_sessions: number;
  breaks_taken: number;
  apps_used: number;
  websites_visited: number;
}

interface ProductivityData {
  hourly_productivity: Array<{
    hour: number;
    productive: number;
    unproductive: number;
  }>;
  app_breakdown: Array<{
    app: string;
    hours: number;
    category: string;
  }>;
  weekly_trend: Array<{
    day: string;
    productive: number;
    unproductive: number;
  }>;
}

interface DailyReport {
  date: string;
  total_hours: number;
  productive_hours: number;
  productivity_score: number;
  focus_sessions: number;
  breaks_taken: number;
  apps_used: number;
  top_apps: Array<{
    app: string;
    hours: number;
    category: string;
  }>;
  accomplishments: Array<{
    type: string;
    description: string;
    duration: number;
    category: string;
  }>;
  productivity_insights: Array<string>;
  recommendations: Array<string>;
}

interface TrackingViewProps {
  session: Session;
  onLogout: () => void;
}

interface Task {
  id: string;
  title: string;
  description: string;
  assignedTo: string;
  assignedToName: string;
  assignedBy: string;
  assignedByName: string;
  status: 'pending' | 'in_progress' | 'completed' | 'overdue';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  dueDate: string;
  createdAt: string;
  updatedAt: string;
  estimatedHours: number;
  actualHours: number;
  tags: string[];
  comments: Array<{
    id: string;
    userId: string;
    userName: string;
    comment: string;
    timestamp: string;
  }>;
}

export default function TrackingView({ session, onLogout }: TrackingViewProps) {
  const [isTracking, setIsTracking] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentActivity, setCurrentActivity] = useState<string>('Not tracking');
  const [dailySummary, setDailySummary] = useState<DailySummary>({
    total_hours: 0,
    productive_hours: 0,
    unproductive_hours: 0,
    productivity_score: 0,
    focus_sessions: 0,
    breaks_taken: 0,
    apps_used: 0,
    websites_visited: 0
  });
  const [productivityData, setProductivityData] = useState<ProductivityData>({
    hourly_productivity: [],
    app_breakdown: [],
    weekly_trend: []
  });
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [dailyReport, setDailyReport] = useState<DailyReport | null>(null);
  const [reportLoading, setReportLoading] = useState(false);
  const [reportCopied, setReportCopied] = useState(false);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [tasksLoading, setTasksLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'tasks' | 'report'>('overview');
  const [searchQuery, setSearchQuery] = useState('');

  const startTracking = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const { invoke } = await import('@tauri-apps/api/tauri');
      await invoke('start_tracking', {
        user_id: session.userId,
        team_id: session.teamId,
        token: session.token
      });
      
      setIsTracking(true);
      setCurrentActivity('Starting tracking...');
      
      // Start activity updates
      const activityInterval = setInterval(async () => {
        try {
          const activityResponse = await invoke('get_current_activity');
          const activity = JSON.parse(activityResponse as string);
          if (activity.success) {
            setCurrentActivity(activity.activity || 'Tracking active...');
          }
        } catch (error) {
          console.error('Error getting activity:', error);
        }
      }, 30000); // Update every 30 seconds
      
      // Store interval for cleanup
      (window as any).activityInterval = activityInterval;
      
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
      
      const { invoke } = await import('@tauri-apps/api/tauri');
      await invoke('stop_tracking');
      
      setIsTracking(false);
      setCurrentActivity('Not tracking');
      
      // Clear activity interval
      if ((window as any).activityInterval) {
        clearInterval((window as any).activityInterval);
        (window as any).activityInterval = null;
      }
      
      // Refresh analytics after stopping
        fetchAnalytics();
      
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

      const { invoke } = await import('@tauri-apps/api/tauri');
      
      // Fetch daily summary
      const summaryResponse = await invoke('http_get', {
        url: `${API_URL}/api/employee/daily-summary`
      });
      const summaryData = JSON.parse(summaryResponse as string);
      
      if (summaryData.success) {
        setDailySummary(summaryData.summary);
      }
      
      // Fetch productivity data
      const productivityResponse = await invoke('http_get', {
        url: `${API_URL}/api/employee/productivity-data`
      });
      const productivityData = JSON.parse(productivityResponse as string);
      
      if (productivityData.success) {
        setProductivityData(productivityData.data);
      }
      
      setLastUpdated(new Date());
    } catch (error: any) {
      console.error('Error fetching analytics:', error);
      setError('Failed to load analytics. Please try again.');
    } finally {
      setAnalyticsLoading(false);
    }
  };

  const exportDailyReport = async (format: 'pdf' | 'csv') => {
    try {
      const { invoke } = await import('@tauri-apps/api/tauri');
      
      const response = await invoke('http_post', {
        url: `${API_URL}/api/employee/export-daily`,
        body: JSON.stringify({
          format: format,
          include_details: true
        })
      });
      
      const data = JSON.parse(response as string);
      
      if (data.success) {
        // Trigger download
        const link = document.createElement('a');
        link.href = data.download_url;
        link.download = `daily-report-${session.userName}-${new Date().toISOString().split('T')[0]}.${format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    } catch (error: any) {
      console.error('Error exporting report:', error);
      setError('Failed to export report. Please try again.');
    }
  };

  const generateDailyReport = async () => {
    try {
      setReportLoading(true);
      setError(null);
      
      const { invoke } = await import('@tauri-apps/api/tauri');
      
      const response = await invoke('http_post', {
        url: `${API_URL}/api/employee/generate-daily-report`,
        body: JSON.stringify({
          include_accomplishments: true,
          include_insights: true,
          include_recommendations: true
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
      const reportText = formatReportForClipboard(dailyReport);
      await navigator.clipboard.writeText(reportText);
      setReportCopied(true);
      setTimeout(() => setReportCopied(false), 2000);
    } catch (error) {
      console.error('Error copying to clipboard:', error);
      setError('Failed to copy report to clipboard.');
    }
  };

  const formatReportForClipboard = (report: DailyReport): string => {
    const today = new Date().toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });

    let reportText = `📊 Daily Report - ${today}\n\n`;

    // Key Metrics
    reportText += `📈 Key Metrics:\n`;
    reportText += `• Total Hours: ${report.total_hours.toFixed(1)}h\n`;
    reportText += `• Productive Hours: ${report.productive_hours.toFixed(1)}h\n`;
    reportText += `• Productivity Score: ${report.productivity_score.toFixed(1)}%\n`;
    reportText += `• Focus Sessions: ${report.focus_sessions}\n`;
    reportText += `• Breaks Taken: ${report.breaks_taken}\n\n`;

    // Accomplishments
    if (report.accomplishments.length > 0) {
      reportText += `✅ Key Accomplishments:\n`;
      report.accomplishments.forEach(accomplishment => {
        const emoji = accomplishment.category === 'productive' ? '🎯' : 
                     accomplishment.category === 'communication' ? '💬' : 
                     accomplishment.category === 'planning' ? '📋' : '📝';
        reportText += `• ${emoji} ${accomplishment.description} (${accomplishment.duration.toFixed(1)}h)\n`;
      });
      reportText += '\n';
    }

    // Top Apps Used
    if (report.top_apps.length > 0) {
      reportText += `🖥️ Most Used Applications:\n`;
      report.top_apps.slice(0, 5).forEach(app => {
        const emoji = app.category === 'productive' ? '💼' : 
                     app.category === 'communication' ? '💬' : 
                     app.category === 'research' ? '🔍' : '📱';
        reportText += `• ${emoji} ${app.app}: ${app.hours.toFixed(1)}h\n`;
      });
      reportText += '\n';
    }

    // Productivity Insights
    if (report.productivity_insights.length > 0) {
      reportText += `💡 Productivity Insights:\n`;
      report.productivity_insights.forEach(insight => {
        reportText += `• ${insight}\n`;
      });
      reportText += '\n';
    }

    // Recommendations
    if (report.recommendations.length > 0) {
      reportText += `🚀 Recommendations for Tomorrow:\n`;
      report.recommendations.forEach(recommendation => {
        reportText += `• ${recommendation}\n`;
      });
      reportText += '\n';
    }

    reportText += `---\nGenerated by ProductivityFlow`;

    return reportText;
  };

  const fetchTasks = async () => {
    try {
      setTasksLoading(true);
      setError(null);
      
      const { invoke } = await import('@tauri-apps/api/tauri');
      
      const response = await invoke('http_get', {
        url: `${API_URL}/api/tasks/employee/${session.userId}`
      });
      
      const data = JSON.parse(response as string);
      
      if (data.success) {
        setTasks(data.tasks);
      }
    } catch (error: any) {
      console.error('Error fetching tasks:', error);
      setError('Failed to load tasks. Please try again.');
    } finally {
      setTasksLoading(false);
    }
  };

  const updateTaskStatus = async (taskId: string, status: Task['status']) => {
    try {
      setError(null);
      
      const { invoke } = await import('@tauri-apps/api/tauri');
      
      const response = await invoke('http_put', {
        url: `${API_URL}/api/tasks/${taskId}/status`,
        body: JSON.stringify({ status })
      });
      
      const data = JSON.parse(response as string);
      
      if (data.success) {
        fetchTasks();
      } else {
        setError('Failed to update task status. Please try again.');
      }
    } catch (error: any) {
      console.error('Error updating task status:', error);
      setError('Failed to update task status. Please try again.');
    }
  };

  useEffect(() => {
      fetchAnalytics();
    fetchTasks();
    
    // Auto-refresh every 5 minutes
    const interval = setInterval(() => {
      fetchAnalytics();
      fetchTasks();
    }, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const getProductivityColor = (score: number) => {
    if (score >= 80) return 'text-emerald-600';
    if (score >= 60) return 'text-amber-600';
    return 'text-red-600';
  };

  const getProductivityBadge = (score: number) => {
    if (score >= 80) return { color: 'bg-emerald-100 text-emerald-800', text: 'Excellent' };
    if (score >= 60) return { color: 'bg-amber-100 text-amber-800', text: 'Good' };
    return { color: 'bg-red-100 text-red-800', text: 'Needs Improvement' };
  };

  const getTaskStatusColor = (status: Task['status']) => {
    switch (status) {
      case 'completed': return 'bg-emerald-100 text-emerald-800';
      case 'in_progress': return 'bg-blue-100 text-blue-800';
      case 'pending': return 'bg-amber-100 text-amber-800';
      case 'overdue': return 'bg-red-100 text-red-800';
      default: return 'bg-slate-100 text-slate-800';
    }
  };

  const getTaskStatusText = (status: Task['status']) => {
    switch (status) {
      case 'completed': return 'Completed';
      case 'in_progress': return 'In Progress';
      case 'pending': return 'Pending';
      case 'overdue': return 'Overdue';
      default: return 'Unknown';
    }
  };

  const getPriorityColor = (priority: Task['priority']) => {
    switch (priority) {
      case 'urgent': return 'bg-red-100 text-red-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'medium': return 'bg-blue-100 text-blue-800';
      case 'low': return 'bg-slate-100 text-slate-800';
      default: return 'bg-slate-100 text-slate-800';
    }
  };

  const getPriorityIcon = (priority: Task['priority']) => {
    switch (priority) {
      case 'urgent': return '🔴';
      case 'high': return '🟠';
      case 'medium': return '🔵';
      case 'low': return '⚪';
      default: return '⚪';
    }
  };

  const filteredTasks = tasks.filter(task =>
    task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    task.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const taskStats = {
    total: tasks.length,
    completed: tasks.filter(t => t.status === 'completed').length,
    inProgress: tasks.filter(t => t.status === 'in_progress').length,
    pending: tasks.filter(t => t.status === 'pending').length,
    overdue: tasks.filter(t => t.status === 'overdue').length
  };

  if (loading) {
  return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="text-center">
          <div className="relative">
            <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
            <Sparkles className="absolute -top-1 -right-1 h-6 w-6 text-blue-600 animate-pulse" />
        </div>
          <p className="text-slate-600 font-medium">Loading your tracker...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-white/80 backdrop-blur-md border-b border-slate-200">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center">
                  <Activity className="h-6 w-6 text-white" />
          </div>
                <div>
                  <h1 className="text-2xl font-bold bg-gradient-to-r from-slate-900 to-slate-700 bg-clip-text text-transparent">
                    ProductivityFlow
                  </h1>
                  <p className="text-sm text-slate-500">Activity Tracker</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2 text-sm text-slate-500">
                <Clock className="h-4 w-4" />
                <span>Updated {lastUpdated.toLocaleTimeString()}</span>
              </div>
              
              <Button
                onClick={() => {
                  fetchAnalytics();
                  fetchTasks();
                }}
                disabled={analyticsLoading || tasksLoading}
                variant="outline"
                size="sm"
                className="border-slate-200 hover:bg-slate-50"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${analyticsLoading || tasksLoading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              
              <Button variant="outline" size="sm" className="border-slate-200 hover:bg-slate-50">
                <Bell className="h-4 w-4" />
              </Button>
              
          <Button 
            onClick={onLogout}
            variant="outline"
            size="sm"
                className="border-slate-200 hover:bg-slate-50"
          >
                Sign Out
          </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
          {error && (
          <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-xl">
            <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
            <span className="text-red-700 font-medium">{error}</span>
            </div>
          )}

        {/* User Info */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-br from-slate-100 to-slate-200 rounded-xl flex items-center justify-center">
                <User className="h-6 w-6 text-slate-600" />
                </div>
              <div>
                <p className="font-semibold text-slate-900">{session.userName}</p>
                <div className="flex items-center space-x-2 text-sm text-slate-500">
                  <Briefcase className="h-4 w-4" />
                  <span>{session.teamName}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <Card className="bg-white/60 backdrop-blur-sm border-0 shadow-lg">
          <CardContent className="p-6">
            <div className="flex items-center space-x-1 bg-slate-100 rounded-lg p-1 mb-6">
              <button
                onClick={() => setActiveTab('overview')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'overview'
                    ? 'bg-white text-slate-900 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <Activity className="h-4 w-4" />
                <span>Overview</span>
              </button>
              <button
                onClick={() => setActiveTab('tasks')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'tasks'
                    ? 'bg-white text-slate-900 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <Target className="h-4 w-4" />
                <span>My Tasks</span>
                {taskStats.total > 0 && (
                  <Badge className="bg-blue-100 text-blue-700 text-xs">
                    {taskStats.total}
                  </Badge>
                )}
              </button>
              <button
                onClick={() => setActiveTab('report')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'report'
                    ? 'bg-white text-slate-900 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <Calendar className="h-4 w-4" />
                <span>Daily Report</span>
              </button>
              </div>

            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* Tracking Control */}
                <Card className="bg-white/60 backdrop-blur-sm border-0 shadow-lg">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-slate-900">
                      <Activity className="h-5 w-5" />
                      Activity Tracking
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className={`w-4 h-4 rounded-full ${isTracking ? 'bg-emerald-500 animate-pulse' : 'bg-slate-400'}`}></div>
                        <div>
                          <p className="font-semibold text-slate-900">
                            {isTracking ? 'Currently Tracking' : 'Not Tracking'}
                          </p>
                          <p className="text-sm text-slate-600">{currentActivity}</p>
                </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        {!isTracking ? (
                <Button 
                  onClick={startTracking} 
                  disabled={loading}
                            className="bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-700 hover:to-emerald-800 border-0 shadow-lg"
                          >
                      <Play className="h-4 w-4 mr-2" />
                            {loading ? 'Starting...' : 'Start Tracking'}
                </Button>
                        ) : (
                          <Button
                            onClick={stopTracking}
                            disabled={loading}
                            className="bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 border-0 shadow-lg"
                          >
                            <Square className="h-4 w-4 mr-2" />
                            {loading ? 'Stopping...' : 'Stop Tracking'}
                          </Button>
                        )}
                      </div>
          </div>
        </CardContent>
      </Card>

                {/* Overview Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <Card className="bg-white/60 backdrop-blur-sm border-0 shadow-lg hover:shadow-xl transition-all duration-300">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-slate-600 mb-1">Total Hours</p>
                          <p className="text-3xl font-bold text-slate-900">{dailySummary.total_hours.toFixed(1)}h</p>
                          <p className="text-xs text-slate-500 mt-1">Today's work</p>
      </div>
                        <div className="p-3 bg-gradient-to-br from-blue-100 to-blue-200 rounded-xl">
                          <Clock className="h-6 w-6 text-blue-600" />
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-white/60 backdrop-blur-sm border-0 shadow-lg hover:shadow-xl transition-all duration-300">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-slate-600 mb-1">Productive Hours</p>
                          <p className="text-3xl font-bold text-emerald-600">{dailySummary.productive_hours.toFixed(1)}h</p>
                          <p className="text-xs text-slate-500 mt-1">Focused work</p>
                  </div>
                        <div className="p-3 bg-gradient-to-br from-emerald-100 to-emerald-200 rounded-xl">
                          <TrendingUp className="h-6 w-6 text-emerald-600" />
                  </div>
                  </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-white/60 backdrop-blur-sm border-0 shadow-lg hover:shadow-xl transition-all duration-300">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-slate-600 mb-1">Productivity Score</p>
                          <p className={`text-3xl font-bold ${getProductivityColor(dailySummary.productivity_score)}`}>
                            {dailySummary.productivity_score.toFixed(1)}%
                          </p>
                          <p className="text-xs text-slate-500 mt-1">Today's performance</p>
                  </div>
                        <div className="p-3 bg-gradient-to-br from-purple-100 to-purple-200 rounded-xl">
                          <Target className="h-6 w-6 text-purple-600" />
                </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-white/60 backdrop-blur-sm border-0 shadow-lg hover:shadow-xl transition-all duration-300">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-slate-600 mb-1">Focus Sessions</p>
                          <p className="text-3xl font-bold text-amber-600">{dailySummary.focus_sessions}</p>
                          <p className="text-xs text-slate-500 mt-1">Deep work periods</p>
                      </div>
                        <div className="p-3 bg-gradient-to-br from-amber-100 to-amber-200 rounded-xl">
                          <Zap className="h-6 w-6 text-amber-600" />
                  </div>
                </div>
              </CardContent>
            </Card>
                </div>

                {/* Productivity Status */}
                <Card className="bg-white/60 backdrop-blur-sm border-0 shadow-lg">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-slate-900">
                      <Award className="h-5 w-5" />
                      Today's Performance
                  </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <Badge className={getProductivityBadge(dailySummary.productivity_score).color}>
                          {getProductivityBadge(dailySummary.productivity_score).text}
                        </Badge>
                        <div>
                          <p className="text-sm text-slate-600">Productivity Score</p>
                          <p className={`text-lg font-bold ${getProductivityColor(dailySummary.productivity_score)}`}>
                            {dailySummary.productivity_score.toFixed(1)}%
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-6">
                        <div className="text-center">
                          <p className="text-sm font-semibold text-emerald-600">{dailySummary.productive_hours.toFixed(1)}h</p>
                          <p className="text-xs text-slate-500">Productive</p>
                        </div>
                        <div className="text-center">
                          <p className="text-sm font-semibold text-red-600">{dailySummary.unproductive_hours.toFixed(1)}h</p>
                          <p className="text-xs text-slate-500">Unproductive</p>
                        </div>
                        <div className="text-center">
                          <p className="text-sm font-semibold text-blue-600">{dailySummary.breaks_taken}</p>
                          <p className="text-xs text-slate-500">Breaks</p>
                        </div>
                      </div>
                    </div>
                </CardContent>
              </Card>

                {/* Analytics Section */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Hourly Productivity Chart */}
                  <Card className="bg-white/60 backdrop-blur-sm border-0 shadow-lg">
                <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-slate-900">
                        <BarChart3 className="h-5 w-5" />
                        Hourly Productivity
                  </CardTitle>
                </CardHeader>
                <CardContent>
                      <div className="space-y-4">
                        {productivityData.hourly_productivity.map((hour, index) => (
                          <div key={index} className="flex items-center space-x-4">
                            <div className="w-12 text-sm font-medium text-slate-600">
                              {hour.hour}:00
                            </div>
                            <div className="flex-1 bg-slate-200 rounded-full h-3 overflow-hidden">
                              <div 
                                className="bg-gradient-to-r from-emerald-500 to-emerald-600 h-full transition-all duration-500 ease-out"
                                style={{ width: `${(hour.productive / (hour.productive + hour.unproductive)) * 100}%` }}
                              ></div>
                            </div>
                            <div className="w-20 text-sm font-medium text-slate-600">
                              {hour.productive.toFixed(1)}h
                            </div>
                          </div>
                        ))}
                      </div>
                </CardContent>
              </Card>

                  {/* App Usage Breakdown */}
                  <Card className="bg-white/60 backdrop-blur-sm border-0 shadow-lg">
                <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-slate-900">
                        <PieChart className="h-5 w-5" />
                        App Usage Breakdown
                  </CardTitle>
                </CardHeader>
                <CardContent>
                      <div className="space-y-3">
                        {productivityData.app_breakdown.slice(0, 8).map((app, index) => (
                          <div key={index} className="flex items-center justify-between p-3 rounded-lg hover:bg-slate-50 transition-colors">
                            <div className="flex items-center space-x-3">
                              <div className={`w-3 h-3 rounded-full ${
                                app.category === 'productive' ? 'bg-emerald-500' : 
                                app.category === 'neutral' ? 'bg-amber-500' : 'bg-red-500'
                              }`}></div>
                              <span className="text-sm font-medium text-slate-900">{app.app}</span>
                            </div>
                            <span className="text-sm font-medium text-slate-600">{app.hours.toFixed(1)}h</span>
                          </div>
                        ))}
                      </div>
                </CardContent>
              </Card>
            </div>

                {/* Activity Insights */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <Card className="bg-white/60 backdrop-blur-sm border-0 shadow-lg hover:shadow-xl transition-all duration-300">
                    <CardContent className="p-6">
                <div className="text-center">
                        <div className="w-12 h-12 bg-gradient-to-br from-blue-100 to-blue-200 rounded-xl flex items-center justify-center mx-auto mb-4">
                          <Monitor className="h-6 w-6 text-blue-600" />
                        </div>
                        <p className="text-2xl font-bold text-slate-900">{dailySummary.apps_used}</p>
                        <p className="text-sm font-medium text-slate-600">Apps Used Today</p>
                </div>
              </CardContent>
            </Card>

                  <Card className="bg-white/60 backdrop-blur-sm border-0 shadow-lg hover:shadow-xl transition-all duration-300">
                    <CardContent className="p-6">
                      <div className="text-center">
                        <div className="w-12 h-12 bg-gradient-to-br from-orange-100 to-orange-200 rounded-xl flex items-center justify-center mx-auto mb-4">
                          <Coffee className="h-6 w-6 text-orange-600" />
                        </div>
                        <p className="text-2xl font-bold text-slate-900">{dailySummary.breaks_taken}</p>
                        <p className="text-sm font-medium text-slate-600">Breaks Taken</p>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-white/60 backdrop-blur-sm border-0 shadow-lg hover:shadow-xl transition-all duration-300">
                    <CardContent className="p-6">
                      <div className="text-center">
                        <div className="w-12 h-12 bg-gradient-to-br from-purple-100 to-purple-200 rounded-xl flex items-center justify-center mx-auto mb-4">
                          <Timer className="h-6 w-6 text-purple-600" />
                        </div>
                        <p className="text-2xl font-bold text-slate-900">{dailySummary.focus_sessions}</p>
                        <p className="text-sm font-medium text-slate-600">Focus Sessions</p>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            )}

            {/* Tasks Tab */}
            {activeTab === 'tasks' && (
              <div className="space-y-6">
                {/* Task Stats */}
                <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                  <div className="text-center p-4 bg-gradient-to-br from-slate-50 to-slate-100 rounded-xl border border-slate-200">
                    <p className="text-2xl font-bold text-slate-900">{taskStats.total}</p>
                    <p className="text-sm font-medium text-slate-700">Total Tasks</p>
                  </div>
                  <div className="text-center p-4 bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-xl border border-emerald-200">
                    <p className="text-2xl font-bold text-emerald-600">{taskStats.completed}</p>
                    <p className="text-sm font-medium text-emerald-700">Completed</p>
                  </div>
                  <div className="text-center p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl border border-blue-200">
                    <p className="text-2xl font-bold text-blue-600">{taskStats.inProgress}</p>
                    <p className="text-sm font-medium text-blue-700">In Progress</p>
                  </div>
                  <div className="text-center p-4 bg-gradient-to-br from-amber-50 to-amber-100 rounded-xl border border-amber-200">
                    <p className="text-2xl font-bold text-amber-600">{taskStats.pending}</p>
                    <p className="text-sm font-medium text-amber-700">Pending</p>
                  </div>
                  <div className="text-center p-4 bg-gradient-to-br from-red-50 to-red-100 rounded-xl border border-red-200">
                    <p className="text-2xl font-bold text-red-600">{taskStats.overdue}</p>
                    <p className="text-sm font-medium text-red-700">Overdue</p>
                  </div>
                </div>

                {/* Task Search */}
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-slate-900 flex items-center">
                    <Target className="h-5 w-5 mr-2" />
                    My Tasks
                  </h3>
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                    <input
                      type="text"
                      placeholder="Search tasks..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white/50 backdrop-blur-sm"
                    />
                  </div>
                </div>

                {/* Tasks List */}
                {tasksLoading ? (
                  <div className="text-center py-8">
                    <div className="w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-slate-600">Loading tasks...</p>
                  </div>
                ) : filteredTasks.length > 0 ? (
                  <div className="space-y-3">
                    {filteredTasks.map((task) => (
                      <div key={task.id} className="group flex items-center justify-between p-4 bg-white/50 backdrop-blur-sm rounded-xl border border-slate-200 hover:shadow-lg transition-all duration-300 hover:border-slate-300">
                        <div className="flex items-center space-x-4">
                          <div className="flex items-center space-x-2">
                            <span className="text-lg">{getPriorityIcon(task.priority)}</span>
                            <Badge className={getPriorityColor(task.priority)}>
                              {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
                            </Badge>
                          </div>
                          <div>
                            <p className="font-semibold text-slate-900 group-hover:text-slate-700 transition-colors">{task.title}</p>
                            <div className="flex items-center space-x-2 text-sm text-slate-500">
                              <span>Assigned by {task.assignedByName}</span>
                              <span>•</span>
                              <span>Due {new Date(task.dueDate).toLocaleDateString()}</span>
                              {task.estimatedHours > 0 && (
                                <>
                                  <span>•</span>
                                  <span>{task.estimatedHours}h estimated</span>
                                </>
                              )}
                            </div>
                            {task.description && (
                              <p className="text-sm text-slate-600 mt-1">{task.description}</p>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center space-x-4">
                          <Badge className={getTaskStatusColor(task.status)}>
                            {getTaskStatusText(task.status)}
                          </Badge>
                          <div className="flex items-center space-x-2">
                            {task.status === 'pending' && (
                              <Button
                                onClick={() => updateTaskStatus(task.id, 'in_progress')}
                                size="sm"
                                variant="outline"
                                className="border-slate-200 hover:bg-slate-50"
                              >
                                Start
                              </Button>
                            )}
                            {task.status === 'in_progress' && (
                              <Button
                                onClick={() => updateTaskStatus(task.id, 'completed')}
                                size="sm"
                                className="bg-emerald-600 hover:bg-emerald-700 border-0"
                              >
                                <CheckCircle className="h-4 w-4 mr-1" />
                                Complete
                              </Button>
                            )}
                            {task.status === 'completed' && (
                              <Button
                                onClick={() => updateTaskStatus(task.id, 'in_progress')}
                                size="sm"
                                variant="outline"
                                className="border-slate-200 hover:bg-slate-50"
                              >
                                Reopen
                              </Button>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="w-16 h-16 bg-gradient-to-br from-slate-100 to-slate-200 rounded-2xl flex items-center justify-center mx-auto mb-4">
                      <Target className="h-8 w-8 text-slate-600" />
                    </div>
                    <h3 className="text-lg font-semibold text-slate-900 mb-2">No Tasks Assigned</h3>
                    <p className="text-slate-600 mb-6 max-w-md mx-auto">
                      You don't have any tasks assigned to you yet. Your manager will assign tasks here.
                    </p>
                  </div>
                )}
        </div>
      )}

            {/* Daily Report Tab */}
            {activeTab === 'report' && (
              <div className="space-y-6">
                {/* End of Day Report Section */}
                <Card className="bg-white/60 backdrop-blur-sm border-0 shadow-lg">
        <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="flex items-center gap-2 text-slate-900">
                        <Calendar className="h-5 w-5" />
                        End of Day Report
          </CardTitle>
                      <div className="flex items-center space-x-3">
                        <Button
                          onClick={generateDailyReport}
                          disabled={reportLoading}
                          className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 border-0 shadow-lg"
                        >
                          <FileText className="h-4 w-4 mr-2" />
                          {reportLoading ? 'Generating...' : 'Generate Report'}
                        </Button>
                        {dailyReport && (
                          <Button
                            onClick={copyReportToClipboard}
                            variant="outline"
                            className="border-slate-200 hover:bg-slate-50"
                          >
                            {reportCopied ? (
                              <>
                                <CheckCircle className="h-4 w-4 mr-2 text-emerald-600" />
                                Copied!
                              </>
                            ) : (
                              <>
                                <Copy className="h-4 w-4 mr-2" />
                                Copy to Clipboard
                              </>
                            )}
                          </Button>
                        )}
                      </div>
                    </div>
        </CardHeader>
        <CardContent>
                    {dailyReport ? (
                      <div className="space-y-6">
                        {/* Report Preview */}
                        <div className="bg-slate-50 rounded-xl p-6 border border-slate-200">
                          <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center">
                            <Clipboard className="h-5 w-5 mr-2" />
                            Report Preview
                          </h3>
                          <div className="space-y-4">
                            {/* Key Metrics */}
              <div>
                              <h4 className="font-medium text-slate-900 mb-2">📈 Key Metrics</h4>
                              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <div className="text-center p-3 bg-white rounded-lg border border-slate-200">
                                  <p className="text-2xl font-bold text-slate-900">{dailyReport.total_hours.toFixed(1)}h</p>
                                  <p className="text-xs text-slate-600">Total Hours</p>
              </div>
                                <div className="text-center p-3 bg-white rounded-lg border border-slate-200">
                                  <p className="text-2xl font-bold text-emerald-600">{dailyReport.productive_hours.toFixed(1)}h</p>
                                  <p className="text-xs text-slate-600">Productive</p>
            </div>
                                <div className="text-center p-3 bg-white rounded-lg border border-slate-200">
                                  <p className="text-2xl font-bold text-blue-600">{dailyReport.productivity_score.toFixed(1)}%</p>
                                  <p className="text-xs text-slate-600">Score</p>
                                </div>
                                <div className="text-center p-3 bg-white rounded-lg border border-slate-200">
                                  <p className="text-2xl font-bold text-amber-600">{dailyReport.focus_sessions}</p>
                                  <p className="text-xs text-slate-600">Focus Sessions</p>
                                </div>
                              </div>
                            </div>

                            {/* Accomplishments */}
                            {dailyReport.accomplishments.length > 0 && (
              <div>
                                <h4 className="font-medium text-slate-900 mb-2">✅ Key Accomplishments</h4>
                                <div className="space-y-2">
                                  {dailyReport.accomplishments.map((accomplishment, index) => (
                                    <div key={index} className="flex items-start space-x-3 p-3 bg-white rounded-lg border border-slate-200">
                                      <div className={`w-2 h-2 rounded-full mt-2 ${
                                        accomplishment.category === 'productive' ? 'bg-emerald-500' : 
                                        accomplishment.category === 'communication' ? 'bg-blue-500' : 
                                        accomplishment.category === 'planning' ? 'bg-purple-500' : 'bg-slate-500'
                                      }`}></div>
                                      <div className="flex-1">
                                        <p className="text-sm font-medium text-slate-900">{accomplishment.description}</p>
                                        <p className="text-xs text-slate-500">{accomplishment.duration.toFixed(1)}h • {accomplishment.type}</p>
              </div>
            </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Top Apps */}
                            {dailyReport.top_apps.length > 0 && (
              <div>
                                <h4 className="font-medium text-slate-900 mb-2">🖥️ Most Used Applications</h4>
                                <div className="space-y-2">
                                  {dailyReport.top_apps.slice(0, 5).map((app, index) => (
                                    <div key={index} className="flex items-center justify-between p-3 bg-white rounded-lg border border-slate-200">
                                      <div className="flex items-center space-x-3">
                                        <div className={`w-3 h-3 rounded-full ${
                                          app.category === 'productive' ? 'bg-emerald-500' : 
                                          app.category === 'communication' ? 'bg-blue-500' : 
                                          app.category === 'research' ? 'bg-purple-500' : 'bg-slate-500'
                                        }`}></div>
                                        <span className="text-sm font-medium text-slate-900">{app.app}</span>
              </div>
                                      <span className="text-sm font-medium text-slate-600">{app.hours.toFixed(1)}h</span>
            </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Insights */}
                            {dailyReport.productivity_insights.length > 0 && (
              <div>
                                <h4 className="font-medium text-slate-900 mb-2">💡 Productivity Insights</h4>
                                <div className="space-y-2">
                                  {dailyReport.productivity_insights.map((insight, index) => (
                                    <div key={index} className="flex items-start space-x-3 p-3 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                                      <Sparkles className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                                      <p className="text-sm text-slate-900">{insight}</p>
              </div>
                                  ))}
            </div>
          </div>
                            )}

                            {/* Recommendations */}
                            {dailyReport.recommendations.length > 0 && (
                              <div>
                                <h4 className="font-medium text-slate-900 mb-2">🚀 Recommendations for Tomorrow</h4>
                                <div className="space-y-2">
                                  {dailyReport.recommendations.map((recommendation, index) => (
                                    <div key={index} className="flex items-start space-x-3 p-3 bg-gradient-to-r from-emerald-50 to-green-50 rounded-lg border border-emerald-200">
                                      <Zap className="h-4 w-4 text-emerald-600 mt-0.5 flex-shrink-0" />
                                      <p className="text-sm text-slate-900">{recommendation}</p>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>

                        <div className="text-center">
                          <p className="text-sm text-slate-600 mb-4">
                            This report is ready to be pasted into your daily stand-up or project management tool.
                          </p>
                          <div className="flex items-center justify-center space-x-4">
                            <Button
                              onClick={copyReportToClipboard}
                              className="bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-700 hover:to-emerald-800 border-0 shadow-lg"
                            >
                              <Copy className="h-4 w-4 mr-2" />
                              Copy Report
                            </Button>
                            <Button
                              onClick={() => exportDailyReport('pdf')}
                              variant="outline"
                              className="border-slate-200 hover:bg-slate-50"
                            >
                              <FileText className="h-4 w-4 mr-2" />
                              Export PDF
                            </Button>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <div className="w-16 h-16 bg-gradient-to-br from-blue-100 to-blue-200 rounded-2xl flex items-center justify-center mx-auto mb-4">
                          <Calendar className="h-8 w-8 text-blue-600" />
                        </div>
                        <h3 className="text-lg font-semibold text-slate-900 mb-2">Generate Your End of Day Report</h3>
                        <p className="text-slate-600 mb-6 max-w-md mx-auto">
                          Automatically create a bulleted list of your key accomplishments and activities for today. 
                          Perfect for daily stand-ups and project management tools.
                        </p>
                        <div className="flex items-center justify-center space-x-4 text-sm text-slate-500">
                          <div className="flex items-center space-x-2">
                            <CheckCircle className="h-4 w-4 text-emerald-600" />
                            <span>Saves 10-15 minutes daily</span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Copy className="h-4 w-4 text-blue-600" />
                            <span>Ready to paste</span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Sparkles className="h-4 w-4 text-purple-600" />
                            <span>AI-powered insights</span>
                          </div>
                        </div>
                      </div>
                    )}
        </CardContent>
      </Card>

                {/* Export Reports */}
                <Card className="bg-white/60 backdrop-blur-sm border-0 shadow-lg">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-slate-900">
                      <Download className="h-5 w-5" />
                      Export Reports
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center space-x-4">
                      <Button
                        onClick={() => exportDailyReport('pdf')}
                        variant="outline"
                        className="border-slate-200 hover:bg-slate-50"
                      >
                        <FileText className="h-4 w-4 mr-2" />
                        Export Daily PDF
                      </Button>
                      <Button
                        onClick={() => exportDailyReport('csv')}
                        variant="outline"
                        className="border-slate-200 hover:bg-slate-50"
                      >
                        <Download className="h-4 w-4 mr-2" />
                        Export Daily CSV
                      </Button>
                      <p className="text-sm text-slate-600">
                        Download detailed reports of your daily activity and productivity metrics
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}