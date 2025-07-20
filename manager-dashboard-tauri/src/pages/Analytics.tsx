import { useState, useEffect } from 'react';
import { 
  Activity, 
  AlertTriangle, 
  TrendingDown, 
  Clock, 
  Coffee, 
  Zap,
  PieChart,
  BarChart3,
  Users,
  Target,
  Shield,
  Brain
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Progress } from '../components/ui/Progress';
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
  PieChart as RechartsPieChart,
  Pie,
  Cell
} from 'recharts';

interface BurnoutRiskData {
  user_id: string;
  name: string;
  risk_score: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  risk_factors: {
    factor: string;
    severity: 'low' | 'medium' | 'high';
    description: string;
  }[];
  trends: {
    date: string;
    risk_score: number;
  }[];
  recommendations: string[];
}

interface DistractionProfileData {
  categories: {
    name: string;
    percentage: number;
    hours: number;
    apps: string[];
  }[];
  total_unproductive_hours: number;
  most_distracting_apps: {
    name: string;
    hours: number;
    percentage: number;
  }[];
}

interface AIInsightsData {
  insights: {
    type: 'productivity' | 'wellness' | 'team' | 'security';
    title: string;
    description: string;
    impact: 'positive' | 'negative' | 'neutral';
    recommendations: string[];
  }[];
  trends: {
    metric: string;
    current: number;
    previous: number;
    change: number;
    trend: 'up' | 'down' | 'stable';
  }[];
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

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

      // Simulate API calls with mock data
      await Promise.all([
        loadBurnoutData(),
        loadDistractionData(),
        loadInsightsData()
      ]);

    } catch (err) {
      setError('Failed to load analytics data. Please try again.');
      console.error('Analytics loading error:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadBurnoutData = async () => {
    // Mock data for burnout risk
    const mockBurnoutData: BurnoutRiskData[] = [
      {
        user_id: 'user1',
        name: 'Sarah Johnson',
        risk_score: 78,
        risk_level: 'high',
        risk_factors: [
          {
            factor: 'Long Working Hours',
            severity: 'high',
            description: 'Consistently working 10+ hours daily'
          },
          {
            factor: 'Late Night Work',
            severity: 'medium',
            description: 'Frequent work after 9 PM'
          },
          {
            factor: 'Weekend Work',
            severity: 'high',
            description: 'Working on weekends for 3 consecutive weeks'
          }
        ],
        trends: [
          { date: '2024-01-01', risk_score: 45 },
          { date: '2024-01-08', risk_score: 52 },
          { date: '2024-01-15', risk_score: 61 },
          { date: '2024-01-22', risk_score: 78 }
        ],
        recommendations: [
          'Implement strict work hours (9 AM - 6 PM)',
          'Take regular breaks every 2 hours',
          'Avoid weekend work for the next 2 weeks',
          'Consider workload redistribution'
        ]
      },
      {
        user_id: 'user2',
        name: 'Mike Chen',
        risk_score: 45,
        risk_level: 'medium',
        risk_factors: [
          {
            factor: 'Context Switching',
            severity: 'medium',
            description: 'High frequency of task switching'
          }
        ],
        trends: [
          { date: '2024-01-01', risk_score: 35 },
          { date: '2024-01-08', risk_score: 38 },
          { date: '2024-01-15', risk_score: 42 },
          { date: '2024-01-22', risk_score: 45 }
        ],
        recommendations: [
          'Batch similar tasks together',
          'Use time blocking techniques',
          'Reduce meeting frequency'
        ]
      }
    ];

    setBurnoutData(mockBurnoutData);
  };

  const loadDistractionData = async () => {
    // Mock data for distraction profile
    const mockDistractionData: DistractionProfileData = {
      categories: [
        {
          name: 'Social Media',
          percentage: 35,
          hours: 12.5,
          apps: ['Facebook', 'Instagram', 'Twitter']
        },
        {
          name: 'News & Entertainment',
          percentage: 25,
          hours: 9.0,
          apps: ['YouTube', 'Netflix', 'CNN']
        },
        {
          name: 'Internal Chat',
          percentage: 20,
          hours: 7.2,
          apps: ['Slack', 'Teams', 'Discord']
        },
        {
          name: 'Email',
          percentage: 15,
          hours: 5.4,
          apps: ['Gmail', 'Outlook']
        },
        {
          name: 'Other',
          percentage: 5,
          hours: 1.8,
          apps: ['Reddit', 'Pinterest']
        }
      ],
      total_unproductive_hours: 35.9,
      most_distracting_apps: [
        { name: 'Facebook', hours: 6.2, percentage: 17.3 },
        { name: 'YouTube', hours: 4.8, percentage: 13.4 },
        { name: 'Slack', hours: 3.9, percentage: 10.9 },
        { name: 'Instagram', hours: 3.2, percentage: 8.9 },
        { name: 'Gmail', hours: 2.8, percentage: 7.8 }
      ]
    };

    setDistractionData(mockDistractionData);
  };

  const loadInsightsData = async () => {
    // Mock data for AI insights
    const mockInsightsData: AIInsightsData = {
      insights: [
        {
          type: 'wellness',
          title: 'Burnout Risk Increasing',
          description: 'Team burnout risk has increased by 23% this week',
          impact: 'negative',
          recommendations: [
            'Implement mandatory breaks',
            'Review workload distribution',
            'Schedule wellness check-ins'
          ]
        },
        {
          type: 'productivity',
          title: 'Focus Time Optimization',
          description: 'Productive hours peak between 9-11 AM',
          impact: 'positive',
          recommendations: [
            'Schedule important tasks in morning hours',
            'Minimize meetings during peak focus time',
            'Use time blocking for deep work'
          ]
        },
        {
          type: 'team',
          title: 'Collaboration Patterns',
          description: 'Cross-team collaboration has improved by 15%',
          impact: 'positive',
          recommendations: [
            'Continue cross-functional projects',
            'Recognize collaborative achievements',
            'Share best practices across teams'
          ]
        }
      ],
      trends: [
        {
          metric: 'Productivity Score',
          current: 78,
          previous: 72,
          change: 8.3,
          trend: 'up'
        },
        {
          metric: 'Focus Time',
          current: 6.2,
          previous: 5.8,
          change: 6.9,
          trend: 'up'
        },
        {
          metric: 'Distraction Rate',
          current: 22,
          previous: 28,
          change: -21.4,
          trend: 'down'
        }
      ]
    };

    setInsightsData(mockInsightsData);
  };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'low': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'critical': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'low': return 'bg-green-100 text-green-700';
      case 'medium': return 'bg-yellow-100 text-yellow-700';
      case 'high': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <Card>
          <CardContent className="flex items-center justify-center h-64">
            <div className="text-center">
              <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading Analytics</h3>
              <p className="text-gray-600 mb-4">{error}</p>
              <Button onClick={loadAnalyticsData}>Try Again</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Analytics Dashboard</h1>
        <p className="text-gray-600">Comprehensive insights into team productivity and wellness</p>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg mb-8">
        <button
          onClick={() => setActiveTab('burnout')}
          className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'burnout'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Activity className="w-4 h-4 mr-2" />
          Burnout Risk
        </button>
        <button
          onClick={() => setActiveTab('distraction')}
          className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'distraction'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <PieChart className="w-4 h-4 mr-2" />
          Distraction Profile
        </button>
        <button
          onClick={() => setActiveTab('insights')}
          className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'insights'
              ? 'bg-white text-blue-600 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Brain className="w-4 h-4 mr-2" />
          AI Insights
        </button>
      </div>

      {/* Burnout Risk Tab */}
      {activeTab === 'burnout' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <AlertTriangle className="w-5 h-5 mr-2 text-orange-500" />
                  High Risk
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-orange-600 mb-2">
                  {burnoutData.filter(u => u.risk_level === 'high' || u.risk_level === 'critical').length}
                </div>
                <p className="text-gray-600">Team members at risk</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <TrendingDown className="w-5 h-5 mr-2 text-red-500" />
                  Average Risk Score
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-red-600 mb-2">
                  {Math.round(burnoutData.reduce((sum, user) => sum + user.risk_score, 0) / burnoutData.length)}
                </div>
                <p className="text-gray-600">Out of 100</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Clock className="w-5 h-5 mr-2 text-blue-500" />
                  Action Required
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-blue-600 mb-2">
                  {burnoutData.filter(u => u.risk_level === 'high' || u.risk_level === 'critical').length}
                </div>
                <p className="text-gray-600">Immediate interventions needed</p>
              </CardContent>
            </Card>
          </div>

          {/* Individual Risk Analysis */}
          <Card>
            <CardHeader>
              <CardTitle>Individual Risk Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {burnoutData.map((user) => (
                  <div key={user.user_id} className="border border-gray-200 rounded-lg p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{user.name}</h3>
                        <div className="flex items-center mt-1">
                          <Badge className={getRiskLevelColor(user.risk_level)}>
                            {user.risk_level.toUpperCase()} RISK
                          </Badge>
                          <span className="ml-3 text-sm text-gray-600">
                            Score: {user.risk_score}/100
                          </span>
                        </div>
                      </div>
                      <Progress value={user.risk_score} className="w-32" />
                    </div>

                    {/* Risk Factors */}
                    <div className="mb-4">
                      <h4 className="font-medium text-gray-900 mb-2">Risk Factors</h4>
                      <div className="space-y-2">
                        {user.risk_factors.map((factor, index) => (
                          <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                            <div>
                              <div className="flex items-center">
                                <span className="font-medium text-gray-900">{factor.factor}</span>
                                <Badge className={`ml-2 ${getSeverityColor(factor.severity)}`}>
                                  {factor.severity}
                                </Badge>
                              </div>
                              <p className="text-sm text-gray-600 mt-1">{factor.description}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Risk Trend */}
                    <div className="mb-4">
                      <h4 className="font-medium text-gray-900 mb-2">Risk Trend (Last 4 Weeks)</h4>
                      <div className="h-32">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={user.trends}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="date" />
                            <YAxis />
                            <Tooltip />
                            <Line type="monotone" dataKey="risk_score" stroke="#ef4444" strokeWidth={2} />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    </div>

                    {/* Recommendations */}
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Recommendations</h4>
                      <ul className="space-y-1">
                        {user.recommendations.map((rec, index) => (
                          <li key={index} className="flex items-start">
                            <Coffee className="w-4 h-4 text-blue-500 mr-2 mt-0.5 flex-shrink-0" />
                            <span className="text-sm text-gray-700">{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Distraction Profile Tab */}
      {activeTab === 'distraction' && distractionData && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <PieChart className="w-5 h-5 mr-2 text-blue-500" />
                  Distraction Categories
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <RechartsPieChart>
                      <Pie
                        data={distractionData.categories}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percentage }) => `${name} ${percentage}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="percentage"
                      >
                        {distractionData.categories.map((_, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </RechartsPieChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2 text-green-500" />
                  Most Distracting Apps
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={distractionData.most_distracting_apps}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="hours" fill="#10b981" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Detailed Breakdown</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {distractionData.categories.map((category, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center">
                      <div 
                        className="w-4 h-4 rounded-full mr-3"
                        style={{ backgroundColor: COLORS[index % COLORS.length] }}
                      ></div>
                      <div>
                        <h4 className="font-medium text-gray-900">{category.name}</h4>
                        <p className="text-sm text-gray-600">
                          {category.apps.join(', ')}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold text-gray-900">{category.hours}h</div>
                      <div className="text-sm text-gray-600">{category.percentage}%</div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* AI Insights Tab */}
      {activeTab === 'insights' && insightsData && (
        <div className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {insightsData.trends.map((trend, index) => (
              <Card key={index}>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    {trend.trend === 'up' ? (
                      <TrendingDown className="w-5 h-5 mr-2 text-green-500" />
                    ) : (
                      <TrendingDown className="w-5 h-5 mr-2 text-red-500" />
                    )}
                    {trend.metric}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-gray-900 mb-2">
                    {trend.current}
                    {trend.metric === 'Productivity Score' && '%'}
                    {trend.metric === 'Focus Time' && 'h'}
                    {trend.metric === 'Distraction Rate' && '%'}
                  </div>
                  <div className={`flex items-center text-sm ${
                    trend.change > 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {trend.change > 0 ? '+' : ''}{trend.change.toFixed(1)}%
                    <span className="ml-1">vs last week</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* AI Insights */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Brain className="w-5 h-5 mr-2 text-purple-500" />
                AI-Powered Insights
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {insightsData.insights.map((insight, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center">
                        {insight.type === 'wellness' && <Coffee className="w-5 h-5 mr-2 text-orange-500" />}
                        {insight.type === 'productivity' && <Zap className="w-5 h-5 mr-2 text-blue-500" />}
                        {insight.type === 'team' && <Users className="w-5 h-5 mr-2 text-green-500" />}
                        {insight.type === 'security' && <Shield className="w-5 h-5 mr-2 text-purple-500" />}
                        <h3 className="text-lg font-semibold text-gray-900">{insight.title}</h3>
                      </div>
                      <Badge className={
                        insight.impact === 'positive' ? 'bg-green-100 text-green-800' :
                        insight.impact === 'negative' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }>
                        {insight.impact}
                      </Badge>
                    </div>
                    <p className="text-gray-600 mb-4">{insight.description}</p>
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Recommendations</h4>
                      <ul className="space-y-1">
                        {insight.recommendations.map((rec, recIndex) => (
                          <li key={recIndex} className="flex items-start">
                            <Target className="w-4 h-4 text-blue-500 mr-2 mt-0.5 flex-shrink-0" />
                            <span className="text-sm text-gray-700">{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
} 