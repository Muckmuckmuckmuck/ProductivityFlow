import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { 
  TrendingUp, 
  AlertTriangle, 
  Users, 
  Clock, 
  BarChart3, 
  Loader2,
  Eye,
  Shield,
  Activity,
  Target,
  Heart,
  Brain,
  Zap
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line
} from 'recharts';

// Updated to use the correct backend URL
const API_URL = "https://productivityflow-backend-v3.onrender.com";

interface BurnoutAnalysis {
  user_id: string;
  user_name: string;
  risk_score: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  factors: Array<{
    type: string;
    severity: 'low' | 'medium' | 'high';
    description: string;
    impact: number;
  }>;
  trends: {
    hours_trend: string;
    productivity_trend: string;
    work_pattern: string;
  };
  recommendations: string[];
}

interface DistractionProfile {
  category: string;
  time_minutes: number;
  percentage: number;
  impact: 'low' | 'medium' | 'high';
}

interface AnalyticsData {
  burnout_analysis: BurnoutAnalysis[];
  distraction_profile: DistractionProfile[];
  insights: string[];
  team_size: number;
  total_unproductive_time_minutes: number;
}

export default function AnalyticsPage() {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'burnout' | 'distractions' | 'insights'>('burnout');

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch teams first
      const teamsResponse = await fetch(`${API_URL}/api/teams`, {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });

      if (!teamsResponse.ok) {
        throw new Error('Failed to fetch teams');
      }

      const teamsData = await teamsResponse.json();
      const teamId = teamsData.teams?.[0]?.id;

      if (!teamId) {
        throw new Error('No teams found');
      }

      // Fetch both burnout and distraction data
      const [burnoutResponse, distractionResponse] = await Promise.allSettled([
        fetch(`${API_URL}/api/analytics/burnout-risk?team_id=${teamId}`, {
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        }),
        fetch(`${API_URL}/api/analytics/distraction-profile?team_id=${teamId}`, {
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        })
      ]);

      // Handle burnout data
      let burnoutData: BurnoutAnalysis[] = [];
      if (burnoutResponse.status === 'fulfilled' && burnoutResponse.value.ok) {
        const burnoutResult = await burnoutResponse.value.json();
        burnoutData = burnoutResult.burnout_analysis || [];
      } else {
        // Mock data for demonstration
        burnoutData = [
          {
            user_id: '1',
            user_name: 'John Doe',
            risk_score: 75,
            risk_level: 'high',
            factors: [
              {
                type: 'long_hours',
                severity: 'high',
                description: 'Average 10.5 hours per day',
                impact: 25
              },
              {
                type: 'late_night_work',
                severity: 'medium',
                description: 'Late night work on 5 days',
                impact: 15
              }
            ],
            trends: {
              hours_trend: 'increasing',
              productivity_trend: 'declining',
              work_pattern: 'irregular'
            },
            recommendations: [
              'Monitor closely',
              'Encourage regular breaks',
              'Review workload distribution'
            ]
          },
          {
            user_id: '2',
            user_name: 'Jane Smith',
            risk_score: 45,
            risk_level: 'medium',
            factors: [
              {
                type: 'high_context_switching',
                severity: 'medium',
                description: 'Average 65 context switches per day',
                impact: 15
              }
            ],
            trends: {
              hours_trend: 'stable',
              productivity_trend: 'stable',
              work_pattern: 'regular'
            },
            recommendations: [
              'Regular check-ins',
              'Encourage work-life balance'
            ]
          }
        ];
      }

      // Handle distraction data
      let distractionData: DistractionProfile[] = [];
      let insights: string[] = [];
      let teamSize = 0;
      let totalUnproductiveTime = 0;

      if (distractionResponse.status === 'fulfilled' && distractionResponse.value.ok) {
        const distractionResult = await distractionResponse.value.json();
        distractionData = distractionResult.distraction_profile || [];
        insights = distractionResult.insights || [];
        teamSize = distractionResult.team_size || 0;
        totalUnproductiveTime = distractionResult.total_unproductive_time_minutes || 0;
      } else {
        // Mock data for demonstration
        distractionData = [
          {
            category: 'Social Media',
            time_minutes: 120,
            percentage: 35,
            impact: 'high'
          },
          {
            category: 'Internal Chat',
            time_minutes: 90,
            percentage: 26,
            impact: 'medium'
          },
          {
            category: 'News Sites',
            time_minutes: 60,
            percentage: 17,
            impact: 'medium'
          },
          {
            category: 'Email',
            time_minutes: 45,
            percentage: 13,
            impact: 'low'
          },
          {
            category: 'Other',
            time_minutes: 35,
            percentage: 9,
            impact: 'low'
          }
        ];
        insights = [
          'Social Media is the biggest team distraction (35% of unproductive time)',
          'Internal communication tools may be causing context switching'
        ];
        teamSize = 3;
        totalUnproductiveTime = 350;
      }

      setAnalyticsData({
        burnout_analysis: burnoutData,
        distraction_profile: distractionData,
        insights,
        team_size: teamSize,
        total_unproductive_time_minutes: totalUnproductiveTime
      });

    } catch (error: any) {
      console.error("Error fetching analytics data:", error);
      setError("Failed to load analytics data. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getRiskIcon = (riskLevel: string) => {
    switch (riskLevel) {
      case 'critical':
        return <AlertTriangle className="h-5 w-5" />;
      case 'high':
        return <AlertTriangle className="h-5 w-5" />;
      case 'medium':
        return <Clock className="h-5 w-5" />;
      case 'low':
        return <Heart className="h-5 w-5" />;
      default:
        return <Activity className="h-5 w-5" />;
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const COLORS = ['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899'];

  if (loading) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Advanced Analytics</h1>
          <p className="text-gray-500">Loading team insights and predictions...</p>
        </div>
        
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Card key={i}>
              <CardContent className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Advanced Analytics</h1>
          <p className="text-gray-500">Team insights and predictions</p>
        </div>
        
        <Card className="border-red-200">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <AlertTriangle className="h-12 w-12 text-red-500 mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Unable to Load Analytics</h3>
            <p className="text-gray-600 text-center mb-4 max-w-md">{error}</p>
            <Button onClick={fetchAnalyticsData}>
              Try Again
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Advanced Analytics</h1>
        <p className="text-gray-500">AI-powered insights for team wellness and productivity</p>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
        <button
          onClick={() => setActiveTab('burnout')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'burnout'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Heart className="h-4 w-4" />
          <span>Burnout Risk</span>
        </button>
        <button
          onClick={() => setActiveTab('distractions')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'distractions'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Eye className="h-4 w-4" />
          <span>Distraction Profile</span>
        </button>
        <button
          onClick={() => setActiveTab('insights')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'insights'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Brain className="h-4 w-4" />
          <span>AI Insights</span>
        </button>
      </div>

      {/* Burnout Risk Analysis */}
      {activeTab === 'burnout' && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Heart className="mr-2 h-5 w-5 text-red-600" />
                Burnout Risk Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-6">
                AI-powered analysis of work patterns to identify employees at risk of burnout. 
                Based on 30 days of activity data including hours, context switching, and productivity trends.
              </p>

              {analyticsData?.burnout_analysis?.length === 0 ? (
                <div className="text-center py-8">
                  <Heart className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">No burnout risk data available</p>
                  <p className="text-sm text-gray-400">Team members need more activity data for analysis</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {analyticsData?.burnout_analysis?.map((member) => (
                    <Card key={member.user_id} className={`border-l-4 ${getRiskColor(member.risk_level)}`}>
                      <CardContent className="p-6">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex items-center space-x-3">
                            {getRiskIcon(member.risk_level)}
                            <div>
                              <h3 className="font-semibold text-lg">{member.user_name}</h3>
                              <p className="text-sm text-gray-600">
                                Risk Score: {member.risk_score}/100
                              </p>
                            </div>
                          </div>
                          <Badge className={getRiskColor(member.risk_level)}>
                            {member.risk_level.toUpperCase()}
                          </Badge>
                        </div>

                        {/* Risk Factors */}
                        {member.factors.length > 0 && (
                          <div className="mb-4">
                            <h4 className="font-medium text-sm text-gray-700 mb-2">Risk Factors:</h4>
                            <div className="space-y-2">
                              {member.factors.map((factor, index) => (
                                <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                                  <span className="text-sm">{factor.description}</span>
                                  <Badge className={getImpactColor(factor.severity)}>
                                    {factor.severity}
                                  </Badge>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Trends */}
                        <div className="mb-4">
                          <h4 className="font-medium text-sm text-gray-700 mb-2">Trends:</h4>
                          <div className="grid grid-cols-3 gap-2 text-sm">
                            <div className="text-center p-2 bg-gray-50 rounded">
                              <div className="font-medium">Hours</div>
                              <div className={`text-xs ${
                                member.trends.hours_trend === 'increasing' ? 'text-red-600' : 'text-green-600'
                              }`}>
                                {member.trends.hours_trend}
                              </div>
                            </div>
                            <div className="text-center p-2 bg-gray-50 rounded">
                              <div className="font-medium">Productivity</div>
                              <div className={`text-xs ${
                                member.trends.productivity_trend === 'declining' ? 'text-red-600' : 'text-green-600'
                              }`}>
                                {member.trends.productivity_trend}
                              </div>
                            </div>
                            <div className="text-center p-2 bg-gray-50 rounded">
                              <div className="font-medium">Pattern</div>
                              <div className={`text-xs ${
                                member.trends.work_pattern === 'irregular' ? 'text-red-600' : 'text-green-600'
                              }`}>
                                {member.trends.work_pattern}
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Recommendations */}
                        {member.recommendations.length > 0 && (
                          <div>
                            <h4 className="font-medium text-sm text-gray-700 mb-2">Recommendations:</h4>
                            <ul className="space-y-1">
                              {member.recommendations.map((rec, index) => (
                                <li key={index} className="text-sm text-gray-600 flex items-start">
                                  <span className="text-blue-600 mr-2">•</span>
                                  {rec}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Distraction Profile */}
      {activeTab === 'distractions' && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Eye className="mr-2 h-5 w-5 text-blue-600" />
                Team Distraction Profile
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-6">
                Anonymous analysis of team-wide distraction patterns. 
                Helps identify systemic productivity issues without singling out individuals.
              </p>

              {analyticsData?.distraction_profile?.length === 0 ? (
                <div className="text-center py-8">
                  <Eye className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">No distraction data available</p>
                  <p className="text-sm text-gray-400">Team needs more activity data for analysis</p>
                </div>
              ) : (
                <div className="grid gap-6 md:grid-cols-2">
                  {/* Pie Chart */}
                  <div>
                    <h4 className="font-medium text-sm text-gray-700 mb-4">Distribution of Unproductive Time</h4>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={analyticsData?.distraction_profile}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ category, percentage }) => `${category} (${percentage}%)`}
                          outerRadius={100}
                          fill="#8884d8"
                          dataKey="percentage"
                        >
                          {analyticsData?.distraction_profile?.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>

                  {/* Detailed Breakdown */}
                  <div>
                    <h4 className="font-medium text-sm text-gray-700 mb-4">Detailed Breakdown</h4>
                    <div className="space-y-3">
                      {analyticsData?.distraction_profile?.map((item, index) => (
                        <div key={item.category} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div className="flex items-center space-x-3">
                            <div 
                              className="w-4 h-4 rounded-full" 
                              style={{ backgroundColor: COLORS[index % COLORS.length] }}
                            />
                            <div>
                              <div className="font-medium text-sm">{item.category}</div>
                              <div className="text-xs text-gray-500">
                                {item.time_minutes.toFixed(0)} minutes
                              </div>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="font-semibold text-sm">{item.percentage}%</div>
                            <Badge className={getImpactColor(item.impact)}>
                              {item.impact}
                            </Badge>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Summary Stats */}
                    <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                      <h5 className="font-medium text-sm text-blue-900 mb-2">Summary</h5>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <div className="text-blue-600">Team Size</div>
                          <div className="font-medium">{analyticsData?.team_size} members</div>
                        </div>
                        <div>
                          <div className="text-blue-600">Total Unproductive Time</div>
                          <div className="font-medium">
                            {analyticsData?.total_unproductive_time_minutes?.toFixed(0)} minutes
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* AI Insights */}
      {activeTab === 'insights' && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Brain className="mr-2 h-5 w-5 text-purple-600" />
                AI-Powered Insights
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-6">
                Intelligent analysis of team patterns and recommendations for improvement.
              </p>

              {/* Insights */}
              {analyticsData?.insights?.length === 0 ? (
                <div className="text-center py-8">
                  <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">No insights available yet</p>
                  <p className="text-sm text-gray-400">More data needed for AI analysis</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {analyticsData?.insights?.map((insight, index) => (
                    <div key={index} className="flex items-start space-x-3 p-4 bg-purple-50 border border-purple-200 rounded-lg">
                      <Zap className="h-5 w-5 text-purple-600 mt-0.5" />
                      <p className="text-sm text-purple-800">{insight}</p>
                    </div>
                  ))}
                </div>
              )}

              {/* Actionable Recommendations */}
              <div className="mt-8">
                <h4 className="font-medium text-sm text-gray-700 mb-4">Recommended Actions</h4>
                <div className="grid gap-4 md:grid-cols-2">
                  <Card className="border-green-200">
                    <CardContent className="p-4">
                      <h5 className="font-medium text-green-800 mb-2">For High Burnout Risk</h5>
                      <ul className="space-y-1 text-sm text-green-700">
                        <li>• Schedule wellness check-ins</li>
                        <li>• Consider workload redistribution</li>
                        <li>• Encourage time-off</li>
                        <li>• Implement flexible hours</li>
                      </ul>
                    </CardContent>
                  </Card>

                  <Card className="border-blue-200">
                    <CardContent className="p-4">
                      <h5 className="font-medium text-blue-800 mb-2">For Distraction Management</h5>
                      <ul className="space-y-1 text-sm text-blue-700">
                        <li>• Set communication boundaries</li>
                        <li>• Implement focus time blocks</li>
                        <li>• Provide productivity training</li>
                        <li>• Review notification policies</li>
                      </ul>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
} 