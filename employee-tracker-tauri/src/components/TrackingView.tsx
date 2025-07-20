import React, { useState, useEffect } from 'react';
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
  Brain
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

export default function TrackingView() {
  const [isTracking, setIsTracking] = useState(false);
  const [currentActivity, setCurrentActivity] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [dailySummary, setDailySummary] = useState<DailySummary | null>(null);
  const [productivityData, setProductivityData] = useState<ProductivityData | null>(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);

  useEffect(() => {
    // Check if tracking is already active on component mount
    checkTrackingStatus();
  }, []);

  const checkTrackingStatus = async () => {
    try {
      const activity = await invoke('get_current_activity');
      setIsTracking(!!activity);
      setCurrentActivity(activity as string || '');
    } catch (error) {
      console.error('Error checking tracking status:', error);
    }
  };

  const startTracking = async () => {
    try {
      setLoading(true);
      setError(null);
      
      await invoke('start_tracking');
      setIsTracking(true);
      setCurrentActivity('Starting tracking...');
      
      // Update activity every 30 seconds
      const interval = setInterval(async () => {
        try {
          const activity = await invoke('get_current_activity');
          setCurrentActivity(activity as string || 'No activity detected');
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

      // Fetch daily summary
      const summaryResponse = await fetch(`${API_URL}/api/employee/daily-summary`, {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });

      if (summaryResponse.ok) {
        const summaryData = await summaryResponse.json();
        setDailySummary(summaryData);
      } else {
        // Mock data for demonstration
        setDailySummary({
          summary: "Today you worked for 7.5 hours with 78.5% productivity",
          accomplishments: [
            "Spent 120.0 minutes focused on VS Code",
            "Completed a 90.0-minute focused work session",
            "Took 3 breaks throughout the day",
            "Maintained good productivity throughout the day"
          ],
          focus_time_hours: 5.9,
          breaks_taken: 3,
          productivity_score: 78.5,
          total_time_hours: 7.5,
          date: new Date().toISOString().split('T')[0]
        });
      }

      // Generate mock productivity data for visualizations
      const mockProductivityData: ProductivityData = {
        hourly_productivity: Array.from({ length: 24 }, (_, i) => ({
          hour: `${i}:00`,
          productivity: Math.floor(Math.random() * 40) + 60
        })),
        app_breakdown: [
          { app: 'VS Code', time_minutes: 180, productivity: 95 },
          { app: 'Chrome', time_minutes: 120, productivity: 75 },
          { app: 'Slack', time_minutes: 60, productivity: 60 },
          { app: 'Terminal', time_minutes: 45, productivity: 90 }
        ],
        weekly_trend: [
          { day: 'Mon', productivity: 82, hours: 8.2 },
          { day: 'Tue', productivity: 78, hours: 7.8 },
          { day: 'Wed', productivity: 85, hours: 8.5 },
          { day: 'Thu', productivity: 76, hours: 7.6 },
          { day: 'Fri', productivity: 80, hours: 8.0 }
        ]
      };

      setProductivityData(mockProductivityData);

    } catch (error: any) {
      console.error("Error fetching analytics:", error);
      setError("Failed to load analytics. Please try again.");
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

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Productivity Tracker</h1>
        <p className="text-gray-600">Track your work activity and boost productivity</p>
      </div>

      {/* Main Tracking Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="flex items-center">
              <Activity className="mr-2 h-5 w-5" />
              Activity Tracking
            </span>
            <Badge className={isTracking ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
              {isTracking ? 'Active' : 'Inactive'}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {error && (
            <div className="flex items-center p-3 bg-red-50 border border-red-200 rounded-lg">
              <AlertCircle className="h-5 w-5 text-red-600 mr-2" />
              <span className="text-red-800 text-sm">{error}</span>
            </div>
          )}

          <div className="text-center">
            {isTracking ? (
              <div className="space-y-4">
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm text-gray-600">Currently tracking...</span>
                </div>
                <p className="text-lg font-medium text-gray-900">{currentActivity}</p>
                <Button 
                  onClick={stopTracking} 
                  disabled={loading}
                  variant="outline"
                  className="bg-red-50 border-red-200 text-red-700 hover:bg-red-100"
                >
                  {loading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Stopping...
                    </>
                  ) : (
                    <>
                      <Square className="h-4 w-4 mr-2" />
                      Stop Tracking
                    </>
                  )}
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-3 h-3 bg-gray-400 rounded-full"></div>
                  <span className="text-sm text-gray-600">Not tracking</span>
                </div>
                <p className="text-lg font-medium text-gray-900">Ready to start tracking</p>
                <Button 
                  onClick={startTracking} 
                  disabled={loading}
                  className="bg-green-600 hover:bg-green-700"
                >
                  {loading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Starting...
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 mr-2" />
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
                        {productivityData.app_breakdown.map((entry, index) => (
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
  );
}