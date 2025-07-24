import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { TrendingUp, TrendingDown, AlertTriangle, Activity, Loader2, AlertCircle } from 'lucide-react';

// Updated to use the correct backend URL
const API_URL = "https://productivityflow-backend-496367590729.us-central1.run.app";

interface BurnoutRiskData {
  user_id: string;
  name: string;
  risk_score: number;
  risk_level: string;
  risk_factors: Array<{
    factor: string;
    severity: string;
    description: string;
  }>;
  trends: Array<{
    date: string;
    risk_score: number;
  }>;
  recommendations: string[];
}

interface DistractionProfileData {
  categories: Array<{
    name: string;
    percentage: number;
    hours: number;
    apps: string[];
  }>;
  total_unproductive_hours: number;
  most_distracting_apps: Array<{
    name: string;
    hours: number;
    percentage: number;
  }>;
}

interface AIInsightsData {
  insights: Array<{
    type: string;
    title: string;
    description: string;
    impact: string;
    recommendations: string[];
  }>;
  trends: Array<{
    metric: string;
    current: number;
    previous: number;
    change: number;
    trend: string;
  }>;
}

export default function Analytics() {
  const [activeTab, setActiveTab] = useState<'burnout' | 'distraction' | 'insights'>('burnout');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [burnoutData, setBurnoutData] = useState<BurnoutRiskData[]>([]);
  const [distractionData, setDistractionData] = useState<DistractionProfileData | null>(null);
  const [insightsData, setInsightsData] = useState<AIInsightsData | null>(null);

  useEffect(() => {
    loadAnalyticsData();
  }, []);

  const loadAnalyticsData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get selected team from localStorage
      const selectedTeamId = localStorage.getItem('selectedTeamId');
      
      if (!selectedTeamId) {
        setError('No team selected. Please select a team first.');
        setLoading(false);
        return;
      }

      // Load analytics data from API endpoints
      await Promise.all([
        loadBurnoutData(selectedTeamId),
        loadDistractionData(selectedTeamId),
        loadInsightsData()
      ]);

    } catch (err) {
      setError('Failed to load analytics data. Please try again.');
      console.error('Analytics loading error:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadBurnoutData = async (teamId: string) => {
    try {
      const response = await fetch(`${API_URL}/api/analytics/burnout-risk?team_id=${teamId}`, {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setBurnoutData(data.burnout_risks || []);
      } else {
        setBurnoutData([]);
      }
    } catch (error) {
      console.error('Failed to load burnout data:', error);
      setBurnoutData([]);
    }
  };

  const loadDistractionData = async (teamId: string) => {
    try {
      const response = await fetch(`${API_URL}/api/analytics/distraction-profile?team_id=${teamId}`, {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setDistractionData(data);
      } else {
        setDistractionData(null);
      }
    } catch (error) {
      console.error('Failed to load distraction data:', error);
      setDistractionData(null);
    }
  };

  const loadInsightsData = async () => {
    // For now, set null since we don't have an insights endpoint yet
    setInsightsData(null);
  };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'text-red-600';
      case 'medium': return 'text-yellow-600';
      case 'low': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-2">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span>Loading analytics...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading Analytics</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button 
            onClick={loadAnalyticsData}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <div className="flex items-center space-x-2">
          <Activity className="h-5 w-5 text-gray-500" />
          <span className="text-sm text-gray-600">Team Insights</span>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
        <button
          onClick={() => setActiveTab('burnout')}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'burnout'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Burnout Risk
        </button>
        <button
          onClick={() => setActiveTab('distraction')}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'distraction'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Distraction Profile
        </button>
        <button
          onClick={() => setActiveTab('insights')}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'insights'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          AI Insights
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'burnout' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-orange-500" />
              <span>Burnout Risk Analysis</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {burnoutData.length === 0 ? (
              <div className="text-center py-8">
                <AlertTriangle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Burnout Data</h3>
                <p className="text-gray-600">Burnout risk data will appear here once team members start tracking their activity.</p>
              </div>
            ) : (
              <div className="space-y-6">
                {burnoutData.map((user) => (
                  <div key={user.user_id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="font-medium text-gray-900">{user.name}</h3>
                        <p className="text-sm text-gray-600">Risk Score: {user.risk_score}%</p>
                      </div>
                      <Badge className={getRiskLevelColor(user.risk_level)}>
                        {user.risk_level.toUpperCase()} RISK
                      </Badge>
                    </div>
                    
                    <div className="space-y-3">
                      <h4 className="font-medium text-gray-900">Risk Factors:</h4>
                      {user.risk_factors.map((factor, index) => (
                        <div key={index} className="ml-4">
                          <p className={`text-sm font-medium ${getSeverityColor(factor.severity)}`}>
                            {factor.factor} ({factor.severity})
                          </p>
                          <p className="text-sm text-gray-600 ml-2">{factor.description}</p>
                        </div>
                      ))}
                    </div>
                    
                    {user.recommendations.length > 0 && (
                      <div className="mt-4">
                        <h4 className="font-medium text-gray-900 mb-2">Recommendations:</h4>
                        <ul className="list-disc list-inside space-y-1">
                          {user.recommendations.map((rec, index) => (
                            <li key={index} className="text-sm text-gray-600">{rec}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {activeTab === 'distraction' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Activity className="h-5 w-5 text-blue-500" />
              <span>Distraction Profile</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {!distractionData ? (
              <div className="text-center py-8">
                <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Distraction Data</h3>
                <p className="text-gray-600">Distraction profile data will appear here once team members start tracking their activity.</p>
              </div>
            ) : (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="font-medium text-gray-900 mb-4">Distraction Categories</h3>
                    <div className="space-y-3">
                      {distractionData.categories.map((category, index) => (
                        <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                          <div>
                            <p className="font-medium">{category.name}</p>
                            <p className="text-sm text-gray-600">{category.hours}h ({category.percentage}%)</p>
                          </div>
                          <div className="text-right">
                            <p className="text-sm text-gray-600">
                              {category.apps.slice(0, 2).join(', ')}
                              {category.apps.length > 2 && '...'}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-medium text-gray-900 mb-4">Most Distracting Apps</h3>
                    <div className="space-y-3">
                      {distractionData.most_distracting_apps.map((app, index) => (
                        <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                          <div>
                            <p className="font-medium">{app.name}</p>
                            <p className="text-sm text-gray-600">{app.hours}h</p>
                          </div>
                          <div className="text-right">
                            <p className="text-sm font-medium text-red-600">{app.percentage}%</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2">
                    <TrendingDown className="h-5 w-5 text-red-500" />
                    <h3 className="font-medium text-red-900">Total Unproductive Time</h3>
                  </div>
                  <p className="text-2xl font-bold text-red-600 mt-2">{distractionData.total_unproductive_hours.toFixed(1)} hours</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {activeTab === 'insights' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="h-5 w-5 text-green-500" />
              <span>AI Insights</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {!insightsData ? (
              <div className="text-center py-8">
                <TrendingUp className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No AI Insights</h3>
                <p className="text-gray-600">AI insights will appear here once team members start tracking their activity and patterns emerge.</p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* AI insights content would go here */}
                <p className="text-gray-600">AI insights feature coming soon...</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
} 