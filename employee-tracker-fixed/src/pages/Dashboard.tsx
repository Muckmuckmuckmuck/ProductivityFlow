import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Users, TrendingUp, TrendingDown, Target, Activity, Loader2, AlertCircle } from 'lucide-react';

// Updated to use the correct backend URL
const API_URL = "https://my-home-backend-7m6d.onrender.com";

interface TeamMember {
  id: string;
  name: string;
  role: string;
  productivity_score: number;
  focus_time: number;
  unproductive_time: number;
  status: string;
  last_active: string;
}

interface ProductivityData {
  date: string;
  productive_hours: number;
  unproductive_hours: number;
  focus_score: number;
}

interface AppUsage {
  app: string;
  hours: number;
  percentage: number;
  category: string;
}

export default function Dashboard() {
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([]);
  const [productivityData, setProductivityData] = useState<ProductivityData[]>([]);
  const [appUsage, setAppUsage] = useState<AppUsage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
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

      // Load team members
      const membersResponse = await fetch(`${API_URL}/api/teams/${selectedTeamId}/members`, {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });

      if (membersResponse.ok) {
        const membersData = await membersResponse.json();
        const members = membersData.members || [];
        
        // Transform API data to match our interface
        const transformedMembers: TeamMember[] = members.map((member: any) => ({
          id: member.user_id,
          name: member.user_name,
          role: member.role,
          productivity_score: member.productive_hours > 0 ? 
            Math.round((member.productive_hours / (member.productive_hours + member.unproductive_hours)) * 100) : 0,
          focus_time: member.productive_hours || 0,
          unproductive_time: member.unproductive_hours || 0,
          status: 'online', // Default status
          last_active: 'Recently' // Default last active
        }));
        
        setTeamMembers(transformedMembers);
      } else {
        setTeamMembers([]);
      }

      // For now, set empty arrays for productivity and app usage data
      // These can be populated with real API calls when those endpoints are available
      setProductivityData([]);
      setAppUsage([]);

    } catch (err) {
      setError('Failed to load dashboard data. Please try again.');
      console.error('Dashboard loading error:', err);
      setTeamMembers([]);
      setProductivityData([]);
      setAppUsage([]);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'bg-green-100 text-green-800';
      case 'away': return 'bg-yellow-100 text-yellow-800';
      case 'offline': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getProductivityColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 80) return 'text-blue-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'productive': return '#10b981';
      case 'unproductive': return '#ef4444';
      case 'neutral': return '#6b7280';
      default: return '#6b7280';
    }
  };

  const totalProductiveHours = teamMembers.reduce((sum, member) => sum + member.focus_time, 0);
  const totalUnproductiveHours = teamMembers.reduce((sum, member) => sum + member.unproductive_time, 0);
  const averageProductivity = teamMembers.length > 0 ? 
    Math.round(teamMembers.reduce((sum, member) => sum + member.productivity_score, 0) / teamMembers.length) : 0;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-2">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span>Loading dashboard...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading Dashboard</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button 
            onClick={loadDashboardData}
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
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <div className="flex items-center space-x-2">
          <Users className="h-5 w-5 text-gray-500" />
          <span className="text-sm text-gray-600">{teamMembers.length} team members</span>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Productive Hours</p>
                <p className="text-2xl font-bold text-green-600">{totalProductiveHours.toFixed(1)}h</p>
              </div>
              <TrendingUp className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Unproductive Hours</p>
                <p className="text-2xl font-bold text-red-600">{totalUnproductiveHours.toFixed(1)}h</p>
              </div>
              <TrendingDown className="h-8 w-8 text-red-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Average Productivity</p>
                <p className="text-2xl font-bold text-blue-600">{averageProductivity}%</p>
              </div>
              <Target className="h-8 w-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Members</p>
                <p className="text-2xl font-bold text-purple-600">
                  {teamMembers.filter(m => m.status === 'online').length}
                </p>
              </div>
              <Activity className="h-8 w-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Team Members */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Users className="h-5 w-5" />
            <span>Team Members</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {teamMembers.length === 0 ? (
            <div className="text-center py-8">
              <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Team Members</h3>
              <p className="text-gray-600">Team members will appear here once they join using the team code.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {teamMembers.map((member) => (
                <div key={member.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium text-gray-600">
                        {member.name.split(' ').map(n => n[0]).join('')}
                      </span>
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">{member.name}</h3>
                      <p className="text-sm text-gray-600">{member.role}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <Badge className={getStatusColor(member.status)}>
                      {member.status}
                    </Badge>
                    <div className="text-right">
                      <p className={`text-sm font-medium ${getProductivityColor(member.productivity_score)}`}>
                        {member.productivity_score}% productivity
                      </p>
                      <p className="text-xs text-gray-500">{member.last_active}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Productivity Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <TrendingUp className="h-5 w-5" />
            <span>Productivity Overview</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {productivityData.length === 0 ? (
            <div className="text-center py-8">
              <TrendingUp className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Productivity Data</h3>
              <p className="text-gray-600">Productivity data will appear here once team members start tracking their activity.</p>
            </div>
          ) : (
            <div className="grid grid-cols-5 gap-4">
              {productivityData.map((data, index) => (
                <div key={index} className="text-center">
                  <p className="text-sm font-medium text-gray-600">{data.date}</p>
                  <p className="text-lg font-bold text-green-600">{data.focus_score}%</p>
                  <p className="text-xs text-gray-500">{data.productive_hours}h productive</p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* App Usage */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Activity className="h-5 w-5" />
            <span>App Usage</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {appUsage.length === 0 ? (
            <div className="text-center py-8">
              <Activity className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No App Usage Data</h3>
              <p className="text-gray-600">App usage data will appear here once team members start tracking their activity.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {appUsage.map((app, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div 
                      className="w-3 h-3 rounded-full" 
                      style={{ backgroundColor: getCategoryColor(app.category) }}
                    />
                    <span className="font-medium">{app.app}</span>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium">{app.hours}h</p>
                    <p className="text-xs text-gray-500">{app.percentage}%</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}