import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { Badge } from './ui/Badge';
import { 
  Activity, 
  Clock, 
  Target, 
  TrendingUp, 
  TrendingDown, 
  Play, 
  Pause, 
  Settings,
  BarChart3,
  Brain,
  Zap,
  Coffee,
  Bell,
  BellOff,
  Maximize2,
  Minimize2,
  Monitor,
  Calendar,
  Lightbulb,
  Target as TargetIcon,
  CheckCircle,
  AlertCircle,
  Info,
  RefreshCw,
  Download,
  Plus,
  Shield,
  User,
  Save,
  Trash2,
  LogOut,
  HelpCircle,
  MessageSquare,
  Copy
} from 'lucide-react';

interface TrackingData {
  isTracking: boolean;
  currentActivity: string;
  productiveTime: number;
  unproductiveTime: number;
  totalTime: number;
  productivityScore: number;
  focusSessions: number;
  breaksTaken: number;
  currentSession: number;
  lastBreak: number;
}

interface AppActivity {
  name: string;
  time: number;
  productive: boolean;
  category: string;
}

interface AIInsights {
  peakHours: number[];
  focusScore: number;
  recommendations: string[];
  productivityTrend: 'improving' | 'stable' | 'declining';
  nextBreak: number;
  optimalWorkPeriods: string[];
}

interface Goal {
  id: string;
  title: string;
  target: number;
  current: number;
  unit: string;
  type: 'daily' | 'weekly' | 'focus' | 'productivity';
  status: 'on_track' | 'behind' | 'achieved';
}

const API_URL = "https://my-home-backend-7m6d.onrender.com";

export default function TrackingView() {
  // Core tracking state
  const [trackingData, setTrackingData] = useState<TrackingData>({
    isTracking: false,
    currentActivity: 'No activity detected',
    productiveTime: 0,
    unproductiveTime: 0,
    totalTime: 0,
    productivityScore: 0,
    focusSessions: 0,
    breaksTaken: 0,
    currentSession: 0,
    lastBreak: 0
  });

  // Enhanced UI state
  const [currentView, setCurrentView] = useState<'dashboard' | 'analytics' | 'goals' | 'settings'>('dashboard');
  const [isMinimized, setIsMinimized] = useState(false);
  const [showNotifications, setShowNotifications] = useState(true);
  const [theme, setTheme] = useState<'light' | 'dark' | 'auto'>('auto');
  const [focusMode, setFocusMode] = useState(false);
  const [breakReminders, setBreakReminders] = useState(true);
    const [productivityAlerts] = useState<any[]>([]); // Changed to any[] for flexibility
  
  // Analytics state
  const [appActivities] = useState<AppActivity[]>([]);
  const [aiInsights, setAiInsights] = useState<AIInsights>({
    peakHours: [9, 10, 11, 14, 15],
    focusScore: 0.75,
    recommendations: ['Take a 5-minute break', 'Focus on high-priority tasks'],
    productivityTrend: 'stable',
    nextBreak: 25,
    optimalWorkPeriods: ['9:00 AM - 11:00 AM', '2:00 PM - 4:00 PM']
  });

  // Goals state
  const [goals, setGoals] = useState<Goal[]>([
    {
      id: '1',
      title: 'Daily Focus Hours',
      target: 6,
      current: 0,
      unit: 'hours',
      type: 'daily',
      status: 'on_track'
    },
    {
      id: '2',
      title: 'Productivity Score',
      target: 85,
      current: 0,
      unit: '%',
      type: 'productivity',
      status: 'on_track'
    },
    {
      id: '3',
      title: 'Focus Sessions',
      target: 8,
      current: 0,
      unit: 'sessions',
      type: 'focus',
      status: 'on_track'
    }
  ]);

  // Session management
  const [session, setSession] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadSession();
  }, []);

  useEffect(() => {
    if (session) {
      startTracking();
      loadAnalytics();
      loadGoals();
    }
  }, [session]);

  const loadSession = () => {
    try {
      const savedSession = localStorage.getItem("tracker_session");
      if (savedSession) {
        const sessionData = JSON.parse(savedSession);
        setSession(sessionData);
      }
    } catch (error) {
      console.error("Error loading session:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const startTracking = useCallback(() => {
    if (!session) return;

    const interval = setInterval(async () => {
      try {
        // Simulate activity tracking with more realistic app detection
        const apps = [
          "Visual Studio Code", "Terminal", "Safari", "Chrome", "Firefox", "Slack", "Teams", "Zoom",
          "YouTube", "Facebook", "Twitter", "Instagram", "TikTok", "Netflix", "Reddit", "Discord"
        ];
        
        // Simulate current app (in real app, this would come from system monitoring)
        const currentApp = apps[Math.floor(Math.random() * apps.length)];
        
        const productiveApps = ["Visual Studio Code", "Terminal", "Safari", "Chrome", "Firefox", "Slack", "Teams", "Zoom"];
        const unproductiveApps = ["YouTube", "Facebook", "Twitter", "Instagram", "TikTok", "Netflix", "Reddit", "Discord"];
        
        const newTrackingData = {
          ...trackingData,
          totalTime: trackingData.totalTime + 1,
          currentSession: trackingData.currentSession + 1,
          lastBreak: trackingData.lastBreak + 1,
          currentActivity: currentApp
        };

        // Categorize activity based on app
        if (productiveApps.includes(currentApp)) {
          newTrackingData.productiveTime += 1;
        } else if (unproductiveApps.includes(currentApp)) {
          newTrackingData.unproductiveTime += 1;
        }

        // Calculate productivity score
        const totalActiveTime = newTrackingData.productiveTime + newTrackingData.unproductiveTime;
        newTrackingData.productivityScore = totalActiveTime > 0 ? Math.round((newTrackingData.productiveTime / totalActiveTime) * 100) : 0;

        // Update focus sessions
        if (newTrackingData.currentSession % 25 === 0 && newTrackingData.currentSession > 0) {
          newTrackingData.focusSessions += 1;
          newTrackingData.currentSession = 0;
        }

        // Break reminders
        if (newTrackingData.lastBreak >= 25 && breakReminders) {
          showBreakReminder();
        }

        setTrackingData(newTrackingData);

        // Update goals
        updateGoals(newTrackingData);

        // Send activity to backend
        await sendActivityToBackend(newTrackingData);

      } catch (error) {
        console.error("Error updating tracking data:", error);
      }
    }, 60000); // Update every minute

    return () => clearInterval(interval);
  }, [trackingData, session, breakReminders]);

  const loadAnalytics = async () => {
    if (!session) return;

    try {
      const response = await fetch(`${API_URL}/api/analytics/ai-insights?user_id=${session.userId}&team_id=${session.teamId}`);
      if (response.ok) {
        const data = await response.json();
        setAiInsights({
          peakHours: data.peak_hours?.peak_hours || [9, 10, 11, 14, 15],
          focusScore: data.focus_patterns?.focus_score || 0.75,
          recommendations: data.ai_recommendations?.map((r: any) => r.message) || [],
          productivityTrend: data.productivity_trends?.trend || 'stable',
          nextBreak: data.break_optimization?.break_duration || 25,
          optimalWorkPeriods: data.break_optimization?.break_times?.map((h: number) => `${h}:00`) || []
        });
      }
    } catch (error) {
      console.error("Error loading analytics:", error);
    }
  };

  const loadGoals = async () => {
    if (!session) return;

    try {
      const response = await fetch(`${API_URL}/api/analytics/goal-tracking?user_id=${session.userId}&team_id=${session.teamId}`);
      if (response.ok) {
        const data = await response.json();
        // Update goals with real data
        setGoals(prevGoals => prevGoals.map(goal => {
          switch (goal.type) {
            case 'daily':
              return { ...goal, current: data.daily_goals?.completed || 0 };
            case 'productivity':
              return { ...goal, current: Math.round((data.productivity_goals?.current_rate || 0) * 100) };
            case 'focus':
              return { ...goal, current: data.focus_goals?.avg_session || 0 };
            default:
              return goal;
          }
        }));
      }
    } catch (error) {
      console.error("Error loading goals:", error);
    }
  };

  const updateGoals = (data: TrackingData) => {
    setGoals(prevGoals => prevGoals.map(goal => {
      switch (goal.type) {
        case 'daily':
          return { ...goal, current: Math.round(data.productiveTime / 60) };
        case 'productivity':
          return { ...goal, current: data.productivityScore };
        case 'focus':
          return { ...goal, current: data.focusSessions };
        default:
          return goal;
      }
    }));
  };

  const sendActivityToBackend = async (data: TrackingData) => {
    if (!session) return;

    try {
      await fetch(`${API_URL}/api/activity/track`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.token}`
        },
        body: JSON.stringify({
          user_id: session.userId,
          team_id: session.teamId,
          active_app: data.currentActivity,
          productive: data.productiveTime > data.unproductiveTime,
          duration: 1, // 1 minute
          productive_hours: data.productiveTime / 60,
          unproductive_hours: data.unproductiveTime / 60
        })
      });
    } catch (error) {
      console.error("Error sending activity to backend:", error);
    }
  };

  const showBreakReminder = () => {
    if (showNotifications) {
      // Show notification
      if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('Time for a Break!', {
          body: 'You\'ve been working for 25 minutes. Take a 5-minute break to stay productive.',
          icon: '/icon.png'
        });
      }
    }
  };

  const toggleTracking = () => {
    setTrackingData(prev => ({
      ...prev,
      isTracking: !prev.isTracking
    }));
    
    // Start or stop the tracking interval
    if (!trackingData.isTracking) {
      // Start tracking
      const trackingInterval = setInterval(() => {
        setTrackingData(prev => {
          // Simulate activity detection (in real app, this would come from system monitoring)
          const currentApp = "Chrome"; // This would be detected from system
          const productiveApps = ["Visual Studio Code", "Terminal", "Safari", "Chrome"];
          const unproductiveApps = ["YouTube", "Facebook", "Twitter", "Instagram", "TikTok"];
          const isProductive = productiveApps.includes(currentApp);
          const isUnproductive = unproductiveApps.includes(currentApp);
          
          const newData = {
            ...prev,
            totalTime: prev.totalTime + 1,
            currentSession: prev.currentSession + 1,
            lastBreak: prev.lastBreak + 1
          };
          
          // Update productive/unproductive time based on current app
          if (isProductive) {
            newData.productiveTime += 1;
          } else if (isUnproductive) {
            newData.unproductiveTime += 1;
          }
          
          // Calculate productivity score
          const totalActiveTime = newData.productiveTime + newData.unproductiveTime;
          newData.productivityScore = totalActiveTime > 0 ? Math.round((newData.productiveTime / totalActiveTime) * 100) : 0;
          
          // Update current activity
          newData.currentActivity = currentApp;
          
          return newData;
        });
      }, 60000); // Update every minute
      
      // Store interval ID for cleanup
      (window as any).trackingInterval = trackingInterval;
    } else {
      // Stop tracking
      if ((window as any).trackingInterval) {
        clearInterval((window as any).trackingInterval);
        (window as any).trackingInterval = null;
      }
    }
  };

  const takeBreak = () => {
    setTrackingData(prev => ({
      ...prev,
      breaksTaken: prev.breaksTaken + 1,
      lastBreak: 0,
      currentSession: 0
    }));
  };



  const formatTime = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
  };

  const getProductivityColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getProductivityIcon = (score: number) => {
    if (score >= 80) return <TrendingUp className="h-4 w-4" />;
    if (score >= 60) return <Target className="h-4 w-4" />;
    return <TrendingDown className="h-4 w-4" />;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <Card className="w-96">
          <CardContent className="text-center py-8">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold mb-2">Session Expired</h2>
            <p className="text-gray-600 mb-4">Please log in again to continue tracking.</p>
            <Button onClick={() => window.location.reload()}>Reload</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className={`min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 transition-all duration-300 ${
      isMinimized ? 'max-w-md mx-auto' : ''
    }`}>
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Activity className="h-8 w-8 text-blue-600" />
                <h1 className="text-xl font-bold text-gray-900">ProductivityFlow</h1>
              </div>
              <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                {session.teamName}
              </Badge>
            </div>
            
            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowNotifications(!showNotifications)}
                className={showNotifications ? 'text-blue-600' : 'text-gray-400'}
              >
                {showNotifications ? <Bell className="h-4 w-4" /> : <BellOff className="h-4 w-4" />}
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsMinimized(!isMinimized)}
              >
                {isMinimized ? <Maximize2 className="h-4 w-4" /> : <Minimize2 className="h-4 w-4" />}
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setCurrentView('settings')}
              >
                <Settings className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {[
              { id: 'dashboard', label: 'Dashboard', icon: Activity },
              { id: 'analytics', label: 'Analytics', icon: BarChart3 },
              { id: 'goals', label: 'Goals', icon: TargetIcon },
              { id: 'settings', label: 'Settings', icon: Settings }
            ].map((item) => (
              <button
                key={item.id}
                onClick={() => setCurrentView(item.id as any)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  currentView === item.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <item.icon className="h-4 w-4" />
                <span>{item.label}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentView === 'dashboard' && (
          <div className="space-y-6">
            {/* Main Tracking Card */}
            <Card className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h2 className="text-2xl font-bold">Employee Tracker</h2>
                    <p className="text-blue-100">Real-time activity monitoring</p>
                  </div>
                  <div className="flex items-center space-x-4">
                    <Button
                      onClick={toggleTracking}
                      variant={trackingData.isTracking ? "outline" : "primary"}
                      size="lg"
                      className={trackingData.isTracking ? "border-white text-white hover:bg-white hover:text-blue-600" : "bg-white text-blue-600 hover:bg-gray-100"}
                    >
                      {trackingData.isTracking ? (
                        <>
                          <Pause className="h-4 w-4 mr-2" />
                          Pause
                        </>
                      ) : (
                        <>
                          <Play className="h-4 w-4 mr-2" />
                          Start
                        </>
                      )}
                    </Button>
                    
                    <Button
                      onClick={takeBreak}
                      variant="outline"
                      size="lg"
                      className="border-white text-white hover:bg-white hover:text-blue-600"
                    >
                      <Coffee className="h-4 w-4 mr-2" />
                      Break
                    </Button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold">{formatTime(trackingData.productiveTime)}</div>
                    <div className="text-blue-100">Productive Time</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold">{formatTime(trackingData.unproductiveTime)}</div>
                    <div className="text-blue-100">Unproductive Time</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold">{trackingData.focusSessions}</div>
                    <div className="text-blue-100">Focus Sessions</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold">{trackingData.breaksTaken}</div>
                    <div className="text-blue-100">Breaks Taken</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Productivity Score */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  {getProductivityIcon(trackingData.productivityScore)}
                  <span>Productivity Score</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center">
                  <div className={`text-6xl font-bold ${getProductivityColor(trackingData.productivityScore)}`}>
                    {trackingData.productivityScore}%
                  </div>
                  <div className="mt-4">
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div
                        className={`h-3 rounded-full transition-all duration-500 ${
                          trackingData.productivityScore >= 80 ? 'bg-green-500' :
                          trackingData.productivityScore >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${trackingData.productivityScore}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* AI Insights */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Brain className="h-5 w-5 text-purple-600" />
                  <span>AI Insights</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Focus Score</span>
                    <span className="font-semibold">{Math.round(aiInsights.focusScore * 100)}%</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Productivity Trend</span>
                    <Badge variant={
                      aiInsights.productivityTrend === 'improving' ? 'default' :
                      aiInsights.productivityTrend === 'stable' ? 'secondary' : 'destructive'
                    }>
                      {aiInsights.productivityTrend}
                    </Badge>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Next Break</span>
                    <span className="font-semibold">in {aiInsights.nextBreak} minutes</span>
                  </div>
                  
                  <div className="mt-4">
                    <h4 className="font-medium mb-2">Recommendations</h4>
                    <ul className="space-y-1">
                      {aiInsights.recommendations.map((rec, index) => (
                        <li key={index} className="flex items-center space-x-2 text-sm text-gray-600">
                          <Lightbulb className="h-3 w-3 text-yellow-500" />
                          <span>{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Goals Overview */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <TargetIcon className="h-5 w-5 text-green-600" />
                  <span>Today's Goals</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {goals.map((goal) => (
                    <div key={goal.id} className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">{goal.current}</div>
                      <div className="text-sm text-gray-600">of {goal.target} {goal.unit}</div>
                      <div className="mt-2">
                        <Badge variant={
                          goal.status === 'achieved' ? 'default' :
                          goal.status === 'on_track' ? 'secondary' : 'destructive'
                        }>
                          {goal.status}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {currentView === 'analytics' && (
          <div className="space-y-6">
            {/* Analytics Header */}
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h2>
                <p className="text-gray-600">Comprehensive productivity insights and trends</p>
              </div>
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={loadAnalytics}
                  disabled={isLoading}
                >
                  <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                  Refresh
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {/* Export functionality */}}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
              </div>
            </div>

            {/* Key Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Today's Productivity</p>
                      <p className="text-2xl font-bold text-gray-900">{trackingData.productivityScore}%</p>
                    </div>
                    <div className={`p-2 rounded-full ${getProductivityColor(trackingData.productivityScore).replace('text-', 'bg-').replace('-500', '-100')}`}>
                      {getProductivityIcon(trackingData.productivityScore)}
                    </div>
                  </div>
                  <div className="mt-4">
                    <div className="flex items-center text-sm">
                      {trackingData.productivityScore > 80 ? (
                        <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
                      ) : trackingData.productivityScore > 60 ? (
                        <TrendingUp className="h-4 w-4 text-yellow-500 mr-1" />
                      ) : (
                        <TrendingDown className="h-4 w-4 text-red-500 mr-1" />
                      )}
                      <span className="text-gray-600">
                        {trackingData.productivityScore > 80 ? 'Excellent' : 
                         trackingData.productivityScore > 60 ? 'Good' : 'Needs improvement'}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Focus Sessions</p>
                      <p className="text-2xl font-bold text-gray-900">{trackingData.focusSessions}</p>
                    </div>
                    <div className="p-2 rounded-full bg-blue-100">
                      <Target className="h-5 w-5 text-blue-600" />
                    </div>
                  </div>
                  <div className="mt-4">
                    <div className="flex items-center text-sm">
                      <Clock className="h-4 w-4 text-blue-500 mr-1" />
                      <span className="text-gray-600">Avg: 25 min per session</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Breaks Taken</p>
                      <p className="text-2xl font-bold text-gray-900">{trackingData.breaksTaken}</p>
                    </div>
                    <div className="p-2 rounded-full bg-green-100">
                      <Coffee className="h-5 w-5 text-green-600" />
                    </div>
                  </div>
                  <div className="mt-4">
                    <div className="flex items-center text-sm">
                      <CheckCircle className="h-4 w-4 text-green-500 mr-1" />
                      <span className="text-gray-600">Well balanced</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Total Time</p>
                      <p className="text-2xl font-bold text-gray-900">{formatTime(trackingData.totalTime)}</p>
                    </div>
                    <div className="p-2 rounded-full bg-purple-100">
                      <Activity className="h-5 w-5 text-purple-600" />
                    </div>
                  </div>
                  <div className="mt-4">
                    <div className="flex items-center text-sm">
                      <Calendar className="h-4 w-4 text-purple-500 mr-1" />
                      <span className="text-gray-600">Today's work</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* AI Insights and Productivity Patterns */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Brain className="h-5 w-5 text-purple-600" />
                    <span>AI Productivity Insights</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="p-2 rounded-full bg-blue-100">
                          <Zap className="h-4 w-4 text-blue-600" />
                        </div>
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

                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="p-2 rounded-full bg-green-100">
                          <Target className="h-4 w-4 text-green-600" />
                        </div>
                        <div>
                          <p className="font-medium">Focus Score</p>
                          <p className="text-sm text-gray-600">{Math.round(aiInsights.focusScore * 100)}% concentration</p>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="p-2 rounded-full bg-yellow-100">
                          <Coffee className="h-4 w-4 text-yellow-600" />
                        </div>
                        <div>
                          <p className="font-medium">Next Break</p>
                          <p className="text-sm text-gray-600">in {aiInsights.nextBreak} minutes</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="mt-4">
                    <h4 className="font-medium mb-3">AI Recommendations</h4>
                    <div className="space-y-2">
                      {aiInsights.recommendations.map((rec, index) => (
                        <div key={index} className="flex items-start space-x-2 p-2 bg-blue-50 rounded-lg">
                          <Lightbulb className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
                          <p className="text-sm text-gray-700">{rec}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <BarChart3 className="h-5 w-5 text-indigo-600" />
                    <span>Productivity Trends</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-600">Weekly Trend</span>
                      <Badge variant={
                        aiInsights.productivityTrend === 'improving' ? 'default' :
                        aiInsights.productivityTrend === 'stable' ? 'secondary' : 'destructive'
                      }>
                        {aiInsights.productivityTrend}
                      </Badge>
                    </div>

                    {/* Simple productivity chart visualization */}
                    <div className="space-y-2">
                      {['Mon', 'Tue', 'Wed', 'Thu', 'Fri'].map((day) => {
                        const productivity = 60 + Math.random() * 30; // Simulated data
                        return (
                          <div key={day} className="flex items-center space-x-3">
                            <span className="text-sm font-medium text-gray-600 w-8">{day}</span>
                            <div className="flex-1 bg-gray-200 rounded-full h-2">
                              <div
                                className={`h-2 rounded-full transition-all duration-300 ${
                                  productivity >= 80 ? 'bg-green-500' :
                                  productivity >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                                }`}
                                style={{ width: `${productivity}%` }}
                              ></div>
                            </div>
                            <span className="text-sm text-gray-600 w-12">{Math.round(productivity)}%</span>
                          </div>
                        );
                      })}
                    </div>

                    <div className="mt-4 p-3 bg-indigo-50 rounded-lg">
                      <h4 className="font-medium text-indigo-900 mb-2">Optimal Work Periods</h4>
                      <div className="space-y-1">
                        {aiInsights.optimalWorkPeriods.map((period, index) => (
                          <p key={index} className="text-sm text-indigo-700 flex items-center">
                            <Clock className="h-3 w-3 mr-2" />
                            {period}
                          </p>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* App Activity Breakdown */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Monitor className="h-5 w-5 text-gray-600" />
                  <span>Application Activity</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {appActivities.length > 0 ? (
                    appActivities.map((app, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className={`p-2 rounded-full ${
                            app.productive ? 'bg-green-100' : 'bg-red-100'
                          }`}>
                            {app.productive ? (
                              <CheckCircle className="h-4 w-4 text-green-600" />
                            ) : (
                              <AlertCircle className="h-4 w-4 text-red-600" />
                            )}
                          </div>
                          <div>
                            <p className="font-medium">{app.name}</p>
                            <p className="text-sm text-gray-600">{app.category}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-medium">{formatTime(app.time)}</p>
                          <Badge variant={app.productive ? "default" : "destructive"}>
                            {app.productive ? 'Productive' : 'Distracting'}
                          </Badge>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8">
                      <Monitor className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600">No app activity data available</p>
                      <p className="text-sm text-gray-500">Start tracking to see your app usage patterns</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Productivity Alerts */}
            {productivityAlerts.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Bell className="h-5 w-5 text-orange-600" />
                    <span>Productivity Alerts</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {productivityAlerts.map((alert, index) => (
                      <div key={index} className="flex items-start space-x-3 p-3 bg-orange-50 border border-orange-200 rounded-lg">
                        <AlertCircle className="h-5 w-5 text-orange-600 mt-0.5 flex-shrink-0" />
                        <div>
                          <p className="font-medium text-orange-900">{alert.title}</p>
                          <p className="text-sm text-orange-700">{alert.message}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {currentView === 'goals' && (
          <div className="space-y-6">
            {/* Goals Header */}
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Goal Management</h2>
                <p className="text-gray-600">Set, track, and achieve your productivity goals</p>
              </div>
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={loadGoals}
                  disabled={isLoading}
                >
                  <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                  Refresh
                </Button>
                <Button
                  onClick={() => {/* Add new goal functionality */}}
                  size="sm"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Goal
                </Button>
              </div>
            </div>

            {/* Goals Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="p-2 rounded-full bg-green-100">
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    </div>
                    <Badge variant="default">Achieved</Badge>
                  </div>
                  <h3 className="text-lg font-semibold mb-2">Daily Focus Time</h3>
                  <div className="text-3xl font-bold text-green-600 mb-2">6.5h</div>
                  <div className="text-sm text-gray-600">Target: 6h</div>
                  <div className="mt-4">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-green-500 h-2 rounded-full" style={{ width: '108%' }}></div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="p-2 rounded-full bg-blue-100">
                      <Target className="h-5 w-5 text-blue-600" />
                    </div>
                    <Badge variant="secondary">On Track</Badge>
                  </div>
                  <h3 className="text-lg font-semibold mb-2">Productivity Score</h3>
                  <div className="text-3xl font-bold text-blue-600 mb-2">78%</div>
                  <div className="text-sm text-gray-600">Target: 80%</div>
                  <div className="mt-4">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-blue-500 h-2 rounded-full" style={{ width: '78%' }}></div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="p-2 rounded-full bg-yellow-100">
                      <AlertCircle className="h-5 w-5 text-yellow-600" />
                    </div>
                    <Badge variant="destructive">Behind</Badge>
                  </div>
                  <h3 className="text-lg font-semibold mb-2">Break Balance</h3>
                  <div className="text-3xl font-bold text-yellow-600 mb-2">3</div>
                  <div className="text-sm text-gray-600">Target: 5</div>
                  <div className="mt-4">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-yellow-500 h-2 rounded-full" style={{ width: '60%' }}></div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Active Goals List */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <TargetIcon className="h-5 w-5 text-green-600" />
                  <span>Active Goals</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {goals.map((goal) => (
                    <div key={goal.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          <div className={`p-2 rounded-full ${
                            goal.status === 'achieved' ? 'bg-green-100' :
                            goal.status === 'on_track' ? 'bg-blue-100' : 'bg-yellow-100'
                          }`}>
                            {goal.status === 'achieved' ? (
                              <CheckCircle className="h-4 w-4 text-green-600" />
                            ) : goal.status === 'on_track' ? (
                              <Target className="h-4 w-4 text-blue-600" />
                            ) : (
                              <AlertCircle className="h-4 w-4 text-yellow-600" />
                            )}
                          </div>
                          <div>
                            <h4 className="font-medium">{goal.title}</h4>
                            <p className="text-sm text-gray-600">{goal.type} goal</p>
                          </div>
                        </div>
                        <Badge variant={
                          goal.status === 'achieved' ? 'default' :
                          goal.status === 'on_track' ? 'secondary' : 'destructive'
                        }>
                          {goal.status}
                        </Badge>
                      </div>
                      
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Progress</span>
                          <span className="font-medium">{goal.current} / {goal.target} {goal.unit}</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full transition-all duration-300 ${
                              goal.status === 'achieved' ? 'bg-green-500' :
                              goal.status === 'on_track' ? 'bg-blue-500' : 'bg-yellow-500'
                            }`}
                            style={{ width: `${Math.min((goal.current / goal.target) * 100, 100)}%` }}
                          ></div>
                        </div>
                      </div>
                      
                      <div className="mt-3 flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {/* Update progress */}}
                          >
                            <Plus className="h-3 w-3 mr-1" />
                            Update
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {/* View details */}}
                          >
                            <Info className="h-3 w-3 mr-1" />
                            Details
                          </Button>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {/* Edit goal */}}
                        >
                          <Settings className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* AI Goal Recommendations */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Brain className="h-5 w-5 text-purple-600" />
                  <span>AI Goal Recommendations</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                    <div className="flex items-start space-x-3">
                      <Lightbulb className="h-5 w-5 text-purple-600 mt-0.5 flex-shrink-0" />
                      <div>
                        <h4 className="font-medium text-purple-900 mb-2">Smart Goal Suggestions</h4>
                        <div className="space-y-2">
                          <p className="text-sm text-purple-700">
                            Based on your productivity patterns, we recommend setting a daily focus time goal of 7 hours.
                          </p>
                          <p className="text-sm text-purple-700">
                            Your peak productivity hours are 9-11 AM and 2-4 PM. Consider scheduling important tasks during these times.
                          </p>
                          <p className="text-sm text-purple-700">
                            You're taking fewer breaks than recommended. Aim for 5 breaks per day to maintain focus.
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 border rounded-lg">
                      <h4 className="font-medium mb-2">Suggested Goals</h4>
                      <div className="space-y-2">
                        <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                          <span className="text-sm">Daily Focus Time: 7h</span>
                          <Button size="sm" variant="outline">Add</Button>
                        </div>
                        <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                          <span className="text-sm">Weekly Productivity: 85%</span>
                          <Button size="sm" variant="outline">Add</Button>
                        </div>
                        <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                          <span className="text-sm">Daily Breaks: 5</span>
                          <Button size="sm" variant="outline">Add</Button>
                        </div>
                      </div>
                    </div>

                    <div className="p-4 border rounded-lg">
                      <h4 className="font-medium mb-2">Goal Insights</h4>
                      <div className="space-y-3">
                        <div className="flex items-center space-x-2">
                          <TrendingUp className="h-4 w-4 text-green-500" />
                          <span className="text-sm">You're 15% more productive on Tuesdays</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Clock className="h-4 w-4 text-blue-500" />
                          <span className="text-sm">Optimal work session length: 45 minutes</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Coffee className="h-4 w-4 text-yellow-500" />
                          <span className="text-sm">Take breaks every 90 minutes for best results</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Goal History */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Calendar className="h-5 w-5 text-gray-600" />
                  <span>Goal History</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {[
                    { date: 'Yesterday', goal: 'Daily Focus Time', target: '6h', achieved: '6.5h', status: 'achieved' },
                    { date: '2 days ago', goal: 'Productivity Score', target: '80%', achieved: '75%', status: 'behind' },
                    { date: '3 days ago', goal: 'Daily Focus Time', target: '6h', achieved: '5.8h', status: 'on_track' },
                    { date: '1 week ago', goal: 'Weekly Productivity', target: '85%', achieved: '82%', status: 'on_track' }
                  ].map((item, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className={`p-2 rounded-full ${
                          item.status === 'achieved' ? 'bg-green-100' :
                          item.status === 'on_track' ? 'bg-blue-100' : 'bg-yellow-100'
                        }`}>
                          {item.status === 'achieved' ? (
                            <CheckCircle className="h-4 w-4 text-green-600" />
                          ) : item.status === 'on_track' ? (
                            <Target className="h-4 w-4 text-blue-600" />
                          ) : (
                            <AlertCircle className="h-4 w-4 text-yellow-600" />
                          )}
                        </div>
                        <div>
                          <p className="font-medium">{item.goal}</p>
                          <p className="text-sm text-gray-600">{item.date}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">{item.achieved}</p>
                        <p className="text-sm text-gray-600">Target: {item.target}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {currentView === 'settings' && (
          <div className="space-y-6">
            {/* Settings Header */}
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Settings</h2>
                <p className="text-gray-600">Customize your productivity tracking experience</p>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {/* Save settings */}}
              >
                <CheckCircle className="h-4 w-4 mr-2" />
                Save Changes
              </Button>
            </div>

            {/* General Settings */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Settings className="h-5 w-5 text-gray-600" />
                  <span>General Settings</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">Notifications</p>
                        <p className="text-sm text-gray-600">Receive productivity alerts and reminders</p>
                      </div>
                                              <Button
                          variant={showNotifications ? "primary" : "outline"}
                          size="sm"
                          onClick={() => setShowNotifications(!showNotifications)}
                        >
                          {showNotifications ? 'On' : 'Off'}
                        </Button>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">Break Reminders</p>
                        <p className="text-sm text-gray-600">Get notified when it's time to take a break</p>
                      </div>
                      <Button
                        variant={breakReminders ? "primary" : "outline"}
                        size="sm"
                        onClick={() => setBreakReminders(!breakReminders)}
                      >
                        {breakReminders ? 'On' : 'Off'}
                      </Button>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">Focus Mode</p>
                        <p className="text-sm text-gray-600">Block distracting notifications during work</p>
                      </div>
                      <Button
                        variant={focusMode ? "primary" : "outline"}
                        size="sm"
                        onClick={() => setFocusMode(!focusMode)}
                      >
                        {focusMode ? 'On' : 'Off'}
                      </Button>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Theme</label>
                      <select
                        value={theme}
                        onChange={(e) => setTheme(e.target.value as any)}
                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
                      >
                        <option value="light">Light</option>
                        <option value="dark">Dark</option>
                        <option value="auto">Auto (System)</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Language</label>
                      <select
                        defaultValue="en"
                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
                      >
                        <option value="en">English</option>
                        <option value="es">Español</option>
                        <option value="fr">Français</option>
                        <option value="de">Deutsch</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Time Zone</label>
                      <select
                        defaultValue="auto"
                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
                      >
                        <option value="auto">Auto-detect</option>
                        <option value="utc">UTC</option>
                        <option value="est">Eastern Time</option>
                        <option value="pst">Pacific Time</option>
                      </select>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Productivity Settings */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Target className="h-5 w-5 text-green-600" />
                  <span>Productivity Settings</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Work Session Length (minutes)
                      </label>
                      <input
                        type="number"
                        defaultValue="45"
                        min="15"
                        max="120"
                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Break Duration (minutes)
                      </label>
                      <input
                        type="number"
                        defaultValue="15"
                        min="5"
                        max="30"
                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Daily Work Goal (hours)
                      </label>
                      <input
                        type="number"
                        defaultValue="8"
                        min="1"
                        max="12"
                        step="0.5"
                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Productivity Threshold (%)
                      </label>
                      <input
                        type="number"
                        defaultValue="80"
                        min="50"
                        max="100"
                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Auto-pause after inactivity (minutes)
                      </label>
                      <input
                        type="number"
                        defaultValue="5"
                        min="1"
                        max="30"
                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="auto-start"
                        defaultChecked
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <label htmlFor="auto-start" className="text-sm font-medium text-gray-700">
                        Auto-start tracking when app opens
                      </label>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Data & Privacy */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Shield className="h-5 w-5 text-blue-600" />
                  <span>Data & Privacy</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">Data Collection</p>
                        <p className="text-sm text-gray-600">Allow app usage analytics for insights</p>
                      </div>
                      <Button
                        variant="primary"
                        size="sm"
                      >
                        On
                      </Button>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">AI Insights</p>
                        <p className="text-sm text-gray-600">Enable AI-powered productivity recommendations</p>
                      </div>
                      <Button
                        variant="primary"
                        size="sm"
                      >
                        On
                      </Button>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">Sync Across Devices</p>
                        <p className="text-sm text-gray-600">Keep your data synchronized</p>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                      >
                        Off
                      </Button>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <Button
                      variant="outline"
                      className="w-full justify-start"
                      onClick={() => {/* Export data */}}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Export My Data
                    </Button>
                    
                    <Button
                      variant="outline"
                      className="w-full justify-start"
                      onClick={() => {/* Backup data */}}
                    >
                      <Save className="h-4 w-4 mr-2" />
                      Backup Settings
                    </Button>
                    
                    <Button
                      variant="outline"
                      className="w-full justify-start text-red-600 hover:text-red-700"
                      onClick={() => {/* Clear data */}}
                    >
                      <Trash2 className="h-4 w-4 mr-2" />
                      Clear All Data
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Account & Team */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <User className="h-5 w-5 text-purple-600" />
                  <span>Account & Team</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
                      <input
                        type="text"
                        defaultValue={session?.name || 'Employee'}
                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                      <input
                        type="email"
                        defaultValue={session?.email || 'employee@company.com'}
                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Team</label>
                      <input
                        type="text"
                        defaultValue={session?.teamName || 'Development Team'}
                        disabled
                        className="w-full border border-gray-300 rounded-md px-3 py-2 bg-gray-50 text-gray-500"
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">Team Code</p>
                        <p className="text-sm text-gray-600">{session?.teamCode || 'TEAM001'}</p>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {/* Copy team code */}}
                      >
                        <Copy className="h-4 w-4 mr-2" />
                        Copy
                      </Button>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">Last Sync</p>
                        <p className="text-sm text-gray-600">2 minutes ago</p>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {/* Force sync */}}
                      >
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Sync Now
                      </Button>
                    </div>
                    
                    <Button
                      variant="outline"
                      className="w-full justify-start text-red-600 hover:text-red-700"
                      onClick={() => {/* Sign out */}}
                    >
                      <LogOut className="h-4 w-4 mr-2" />
                      Sign Out
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* About & Support */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Info className="h-5 w-5 text-gray-600" />
                  <span>About & Support</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <p className="text-sm text-gray-600">
                      <span className="font-medium">Version:</span> 3.1.0
                    </p>
                    <p className="text-sm text-gray-600">
                      <span className="font-medium">Build:</span> 2024.01.15
                    </p>
                    <p className="text-sm text-gray-600">
                      <span className="font-medium">Platform:</span> macOS
                    </p>
                  </div>
                  
                  <div className="space-y-2">
                    <Button
                      variant="outline"
                      className="w-full justify-start"
                      onClick={() => {/* Open help */}}
                    >
                      <HelpCircle className="h-4 w-4 mr-2" />
                      Help & Documentation
                    </Button>
                    
                    <Button
                      variant="outline"
                      className="w-full justify-start"
                      onClick={() => {/* Contact support */}}
                    >
                      <MessageSquare className="h-4 w-4 mr-2" />
                      Contact Support
                    </Button>
                    
                    <Button
                      variant="outline"
                      className="w-full justify-start"
                      onClick={() => {/* Check for updates */}}
                    >
                      <RefreshCw className="h-4 w-4 mr-2" />
                      Check for Updates
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}