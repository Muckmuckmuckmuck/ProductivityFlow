import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { Badge } from './ui/Badge';
import { 
  Clock, 
  TrendingUp, 
  TrendingDown, 
  Brain,
  Activity,
  Target,
  CheckCircle,
  AlertCircle,
  RefreshCw,
  Download,
  BarChart3,
  Zap,
  Coffee,
  Monitor,
  Calendar,
  Lightbulb
} from 'lucide-react';

const API_URL = "https://my-home-backend-7m6d.onrender.com";

interface HourlySummary {
  hour: number;
  totalMinutes: number;
  productiveMinutes: number;
  unproductiveMinutes: number;
  productivityScore: number;
  apps: AppActivity[];
  summary: string;
  timestamp: string;
}

interface AppActivity {
  name: string;
  time: number;
  productive: boolean;
  category: string;
  confidence: number;
}

interface ProductivityData {
  isTracking: boolean;
  currentHour: number;
  currentMinute: number;
  totalMinutes: number;
  productiveMinutes: number;
  unproductiveMinutes: number;
  productivityScore: number;
  hourlySummaries: HourlySummary[];
  currentApps: AppActivity[];
  lastUpdate: string;
}

// AI-powered app categorization
const PRODUCTIVE_APPS = [
  'vscode', 'code', 'visual studio', 'sublime', 'atom', 'intellij', 'eclipse',
  'chrome', 'firefox', 'safari', 'edge', 'brave',
  'slack', 'teams', 'discord', 'zoom', 'meet', 'webex',
  'notion', 'evernote', 'onenote', 'obsidian', 'roam',
  'figma', 'sketch', 'adobe xd', 'invision', 'framer',
  'excel', 'sheets', 'numbers', 'tableau', 'powerbi',
  'word', 'docs', 'pages', 'confluence', 'jira',
  'terminal', 'iterm', 'powershell', 'git', 'github',
  'postman', 'insomnia', 'swagger', 'docker', 'kubernetes',
  'trello', 'asana', 'clickup', 'monday', 'linear',
  'calendar', 'outlook', 'gmail', 'mail', 'thunderbird'
];

const UNPRODUCTIVE_APPS = [
  'youtube', 'netflix', 'hulu', 'disney+', 'prime video',
  'facebook', 'instagram', 'twitter', 'tiktok', 'snapchat',
  'reddit', 'imgur', '9gag', 'buzzfeed',
  'spotify', 'apple music', 'pandora', 'soundcloud',
  'games', 'steam', 'epic', 'origin', 'battle.net',
  'twitch', 'mixer', 'discord gaming',
  'amazon', 'ebay', 'etsy', 'shopify',
  'pinterest', 'tumblr', 'medium', 'quora',
  'whatsapp', 'telegram', 'signal', 'wechat',
  'candy crush', 'solitaire', 'minesweeper'
];

const NEUTRAL_APPS = [
  'finder', 'explorer', 'file manager', 'desktop',
  'settings', 'preferences', 'system preferences',
  'calculator', 'notes', 'textedit', 'notepad',
  'screenshot', 'camera', 'photos', 'gallery',
  'weather', 'clock', 'calendar', 'reminders'
];

export default function HourlyProductivityTracker() {
  const [productivityData, setProductivityData] = useState<ProductivityData>({
    isTracking: false,
    currentHour: 0,
    currentMinute: 0,
    totalMinutes: 0,
    productiveMinutes: 0,
    unproductiveMinutes: 0,
    productivityScore: 0,
    hourlySummaries: [],
    currentApps: [],
    lastUpdate: new Date().toISOString()
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // AI-powered app categorization
  const categorizeApp = (appName: string): { productive: boolean; category: string; confidence: number } => {
    const lowerAppName = appName.toLowerCase();
    
    // Check productive apps
    for (const app of PRODUCTIVE_APPS) {
      if (lowerAppName.includes(app)) {
        return { productive: true, category: 'Productive', confidence: 0.9 };
      }
    }
    
    // Check unproductive apps
    for (const app of UNPRODUCTIVE_APPS) {
      if (lowerAppName.includes(app)) {
        return { productive: false, category: 'Unproductive', confidence: 0.9 };
      }
    }
    
    // Check neutral apps
    for (const app of NEUTRAL_APPS) {
      if (lowerAppName.includes(app)) {
        return { productive: true, category: 'Neutral', confidence: 0.5 };
      }
    }
    
    // Default categorization based on context
    if (lowerAppName.includes('browser') || lowerAppName.includes('web')) {
      return { productive: true, category: 'Web Browsing', confidence: 0.7 };
    }
    
    return { productive: true, category: 'Unknown', confidence: 0.3 };
  };

  // Track current app activity
  const trackCurrentApp = async () => {
    try {
      const { invoke } = await import('@tauri-apps/api/tauri');
      
      // Get current active window/app
      const activeApp = await invoke('get_active_window') as string;
      const categorization = categorizeApp(activeApp);
      
      const newAppActivity: AppActivity = {
        name: activeApp,
        time: 1, // 1 minute increment
        productive: categorization.productive,
        category: categorization.category,
        confidence: categorization.confidence
      };
      
      setProductivityData(prev => {
        const currentHour = new Date().getHours();
        const currentMinute = new Date().getMinutes();
        
        // Update current apps
        const updatedApps = [...prev.currentApps];
        const existingAppIndex = updatedApps.findIndex(app => app.name === activeApp);
        
        if (existingAppIndex >= 0) {
          updatedApps[existingAppIndex].time += 1;
        } else {
          updatedApps.push(newAppActivity);
        }
        
        // Update time tracking
        const newTotalMinutes = prev.totalMinutes + 1;
        const newProductiveMinutes = prev.productiveMinutes + (categorization.productive ? 1 : 0);
        const newUnproductiveMinutes = prev.unproductiveMinutes + (categorization.productive ? 0 : 1);
        const newProductivityScore = newTotalMinutes > 0 ? (newProductiveMinutes / newTotalMinutes) * 100 : 0;
        
        return {
          ...prev,
          currentHour,
          currentMinute,
          totalMinutes: newTotalMinutes,
          productiveMinutes: newProductiveMinutes,
          unproductiveMinutes: newUnproductiveMinutes,
          productivityScore: newProductivityScore,
          currentApps: updatedApps,
          lastUpdate: new Date().toISOString()
        };
      });
      
    } catch (error) {
      console.error('Error tracking app activity:', error);
    }
  };

  // Generate hourly summary
  const generateHourlySummary = async () => {
    const currentHour = new Date().getHours();
    
    if (productivityData.currentApps.length === 0) return;
    
    const summary: HourlySummary = {
      hour: currentHour,
      totalMinutes: productivityData.totalMinutes,
      productiveMinutes: productivityData.productiveMinutes,
      unproductiveMinutes: productivityData.unproductiveMinutes,
      productivityScore: productivityData.productivityScore,
      apps: [...productivityData.currentApps],
      summary: generateAISummary(productivityData.currentApps, productivityData.productivityScore),
      timestamp: new Date().toISOString()
    };
    
    setProductivityData(prev => ({
      ...prev,
      hourlySummaries: [...prev.hourlySummaries, summary],
      currentApps: [], // Reset for next hour
      totalMinutes: 0,
      productiveMinutes: 0,
      unproductiveMinutes: 0,
      productivityScore: 0
    }));
    
    // Send to backend
    await sendHourlySummaryToBackend(summary);
  };

  // AI-powered summary generation
  const generateAISummary = (apps: AppActivity[], productivityScore: number): string => {
    const productiveApps = apps.filter(app => app.productive);
    const unproductiveApps = apps.filter(app => !app.productive);
    
    const topProductiveApp = productiveApps.sort((a, b) => b.time - a.time)[0];
    const topUnproductiveApp = unproductiveApps.sort((a, b) => b.time - a.time)[0];
    
    let summary = `Hour ${new Date().getHours()}:00 Summary - `;
    
    if (productivityScore >= 80) {
      summary += `Excellent productivity! You spent ${Math.round(productivityScore)}% of your time on productive activities.`;
    } else if (productivityScore >= 60) {
      summary += `Good productivity with ${Math.round(productivityScore)}% productive time.`;
    } else if (productivityScore >= 40) {
      summary += `Moderate productivity at ${Math.round(productivityScore)}%. Consider reducing distractions.`;
    } else {
      summary += `Low productivity at ${Math.round(productivityScore)}%. Focus on work-related tasks.`;
    }
    
    if (topProductiveApp) {
      summary += ` Most productive: ${topProductiveApp.name} (${topProductiveApp.time} mins).`;
    }
    
    if (topUnproductiveApp) {
      summary += ` Main distraction: ${topUnproductiveApp.name} (${topUnproductiveApp.time} mins).`;
    }
    
    return summary;
  };

  // Send hourly summary to backend
  const sendHourlySummaryToBackend = async (summary: HourlySummary) => {
    try {
      const { invoke } = await import('@tauri-apps/api/tauri');
      
      const response = await invoke('http_post', {
        url: `${API_URL}/api/activity/hourly-summary`,
        body: JSON.stringify(summary),
        headers: JSON.stringify({
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        })
      });
      
      console.log('Hourly summary sent:', response);
    } catch (error) {
      console.error('Error sending hourly summary:', error);
    }
  };

  // Start tracking
  const startTracking = () => {
    setProductivityData(prev => ({ ...prev, isTracking: true }));
    
    // Track every minute
    intervalRef.current = setInterval(() => {
      trackCurrentApp();
    }, 60000); // 1 minute
    
    setSuccess("Productivity tracking started!");
  };

  // Stop tracking
  const stopTracking = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    
    setProductivityData(prev => ({ ...prev, isTracking: false }));
    setSuccess("Productivity tracking stopped!");
  };

  // Check for hourly summary generation
  useEffect(() => {
    const checkHourlySummary = () => {
      const now = new Date();
      const currentMinute = now.getMinutes();
      
      // Generate summary at the start of each hour (minute 0)
      if (currentMinute === 0 && productivityData.isTracking && productivityData.currentApps.length > 0) {
        generateHourlySummary();
      }
    };
    
    const minuteInterval = setInterval(checkHourlySummary, 60000); // Check every minute
    
    return () => {
      clearInterval(minuteInterval);
    };
  }, [productivityData.isTracking, productivityData.currentApps]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  const formatTime = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
  };

  const getProductivityColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-blue-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      {/* Main Tracking Card */}
      <Card className="bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Activity className="h-5 w-5 text-blue-600" />
            <span>Hourly Productivity Tracker</span>
            <Badge variant={productivityData.isTracking ? "default" : "secondary"}>
              {productivityData.isTracking ? "Active" : "Inactive"}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Current Status */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-white rounded-xl border border-blue-200">
              <div className="text-2xl font-bold text-blue-600">
                {formatTime(productivityData.totalMinutes)}
              </div>
              <div className="text-sm text-gray-600">Total Time</div>
            </div>
            
            <div className="text-center p-4 bg-white rounded-xl border border-green-200">
              <div className="text-2xl font-bold text-green-600">
                {formatTime(productivityData.productiveMinutes)}
              </div>
              <div className="text-sm text-gray-600">Productive</div>
            </div>
            
            <div className="text-center p-4 bg-white rounded-xl border border-red-200">
              <div className="text-2xl font-bold text-red-600">
                {formatTime(productivityData.unproductiveMinutes)}
              </div>
              <div className="text-sm text-gray-600">Unproductive</div>
            </div>
            
            <div className="text-center p-4 bg-white rounded-xl border border-purple-200">
              <div className={`text-2xl font-bold ${getProductivityColor(productivityData.productivityScore)}`}>
                {productivityData.productivityScore.toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600">Productivity</div>
            </div>
          </div>

          {/* Control Buttons */}
          <div className="flex justify-center space-x-4">
            <Button
              onClick={productivityData.isTracking ? stopTracking : startTracking}
              className={`flex items-center space-x-2 ${
                productivityData.isTracking 
                  ? 'bg-red-600 hover:bg-red-700' 
                  : 'bg-green-600 hover:bg-green-700'
              }`}
            >
              {productivityData.isTracking ? (
                <>
                  <TrendingDown className="h-4 w-4" />
                  Stop Tracking
                </>
              ) : (
                <>
                  <TrendingUp className="h-4 w-4" />
                  Start Tracking
                </>
              )}
            </Button>
          </div>

          {/* Current Apps */}
          {productivityData.currentApps.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-3">Current Session Apps</h3>
              <div className="space-y-2">
                {productivityData.currentApps
                  .sort((a, b) => b.time - a.time)
                  .slice(0, 5)
                  .map((app, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-white rounded-lg border">
                      <div className="flex items-center space-x-3">
                        <div className={`w-3 h-3 rounded-full ${
                          app.productive ? 'bg-green-500' : 'bg-red-500'
                        }`} />
                        <span className="font-medium">{app.name}</span>
                        <Badge variant="outline" className="text-xs">
                          {app.category}
                        </Badge>
                      </div>
                      <div className="text-sm text-gray-600">
                        {app.time} mins
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Hourly Summaries */}
      {productivityData.hourlySummaries.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Clock className="h-5 w-5" />
              <span>Hourly Summaries</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {productivityData.hourlySummaries
                .slice(-5) // Show last 5 summaries
                .reverse()
                .map((summary, index) => (
                  <div key={index} className="p-4 bg-gray-50 rounded-lg border">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-semibold">Hour {summary.hour}:00</h4>
                      <Badge variant="outline">
                        {summary.productivityScore.toFixed(1)}% Productive
                      </Badge>
                    </div>
                    
                    <div className="grid grid-cols-3 gap-4 mb-3">
                      <div className="text-center">
                        <div className="text-lg font-bold text-blue-600">
                          {summary.totalMinutes}m
                        </div>
                        <div className="text-xs text-gray-600">Total</div>
                      </div>
                      <div className="text-center">
                        <div className="text-lg font-bold text-green-600">
                          {summary.productiveMinutes}m
                        </div>
                        <div className="text-xs text-gray-600">Productive</div>
                      </div>
                      <div className="text-center">
                        <div className="text-lg font-bold text-red-600">
                          {summary.unproductiveMinutes}m
                        </div>
                        <div className="text-xs text-gray-600">Unproductive</div>
                      </div>
                    </div>
                    
                    <p className="text-sm text-gray-700">{summary.summary}</p>
                    
                    <div className="mt-3 pt-3 border-t">
                      <div className="text-xs text-gray-600 mb-2">Top Apps:</div>
                      <div className="flex flex-wrap gap-2">
                        {summary.apps
                          .sort((a, b) => b.time - a.time)
                          .slice(0, 3)
                          .map((app, appIndex) => (
                            <Badge key={appIndex} variant="outline" className="text-xs">
                              {app.name} ({app.time}m)
                            </Badge>
                          ))}
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Messages */}
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
    </div>
  );
} 