import { useState, useEffect } from 'react';
import { 
  Users, 
  TrendingUp, 
  Clock, 
  Target,
  Activity,
  BarChart3,
  Eye,
  Download
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Progress } from '../components/ui/Progress';
import { 
   
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

interface TeamMember {
  id: string;
  name: string;
  role: string;
  productivity_score: number;
  focus_time: number;
  unproductive_time: number;
  status: 'online' | 'offline' | 'away';
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
  category: 'productive' | 'unproductive' | 'neutral';
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

      // Mock data for demonstration
      const mockTeamMembers: TeamMember[] = [
        {
          id: '1',
          name: 'Sarah Johnson',
          role: 'Software Engineer',
          productivity_score: 85,
          focus_time: 6.5,
          unproductive_time: 1.5,
          status: 'online',
          last_active: '2 minutes ago'
        },
        {
          id: '2',
          name: 'Mike Chen',
          role: 'Product Manager',
          productivity_score: 78,
          focus_time: 5.8,
          unproductive_time: 2.2,
          status: 'away',
          last_active: '15 minutes ago'
        },
        {
          id: '3',
          name: 'Emily Davis',
          role: 'UX Designer',
          productivity_score: 92,
          focus_time: 7.2,
          unproductive_time: 0.8,
          status: 'online',
          last_active: '1 minute ago'
        }
      ];

      const mockProductivityData: ProductivityData[] = [
        { date: 'Mon', productive_hours: 6.2, unproductive_hours: 1.8, focus_score: 78 },
        { date: 'Tue', productive_hours: 7.1, unproductive_hours: 0.9, focus_score: 89 },
        { date: 'Wed', productive_hours: 5.8, unproductive_hours: 2.2, focus_score: 72 },
        { date: 'Thu', productive_hours: 6.5, unproductive_hours: 1.5, focus_score: 81 },
        { date: 'Fri', productive_hours: 5.9, unproductive_hours: 2.1, focus_score: 74 }
      ];

      const mockAppUsage: AppUsage[] = [
        { app: 'VS Code', hours: 4.2, percentage: 35, category: 'productive' },
        { app: 'Slack', hours: 2.1, percentage: 18, category: 'neutral' },
        { app: 'Chrome', hours: 1.8, percentage: 15, category: 'productive' },
        { app: 'Figma', hours: 1.5, percentage: 13, category: 'productive' },
        { app: 'Spotify', hours: 1.2, percentage: 10, category: 'unproductive' },
        { app: 'Other', hours: 1.2, percentage: 9, category: 'neutral' }
      ];

      setTeamMembers(mockTeamMembers);
      setProductivityData(mockProductivityData);
      setAppUsage(mockAppUsage);

    } catch (err) {
      setError('Failed to load dashboard data. Please try again.');
      console.error('Dashboard loading error:', err);
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
  const averageProductivity = Math.round(teamMembers.reduce((sum, member) => sum + member.productivity_score, 0) / teamMembers.length);

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
              <Activity className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading Dashboard</h3>
              <p className="text-gray-600 mb-4">{error}</p>
              <Button onClick={loadDashboardData}>Try Again</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Team Dashboard</h1>
        <p className="text-gray-600">Monitor team productivity and performance in real-time</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Team Members</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{teamMembers.length}</div>
            <p className="text-xs text-muted-foreground">
              {teamMembers.filter(m => m.status === 'online').length} online
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Productive Hours</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalProductiveHours.toFixed(1)}h</div>
            <p className="text-xs text-muted-foreground">
              +12% from yesterday
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Focus Score</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{averageProductivity}%</div>
            <p className="text-xs text-muted-foreground">
              Team average
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Unproductive Time</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalUnproductiveHours.toFixed(1)}h</div>
            <p className="text-xs text-muted-foreground">
              -8% from yesterday
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Productivity Trend */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <BarChart3 className="w-5 h-5 mr-2 text-blue-500" />
              Weekly Productivity Trend
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={productivityData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="focus_score" stroke="#3b82f6" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* App Usage */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <PieChart className="w-5 h-5 mr-2 text-green-500" />
              App Usage Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={appUsage}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ app, percentage }) => `${app} ${percentage}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="percentage"
                  >
                    {appUsage.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={getCategoryColor(entry.category)} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Team Members */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center">
              <Users className="w-5 h-5 mr-2 text-purple-500" />
              Team Members
            </div>
            <div className="flex space-x-2">
              <Button variant="outline" size="sm">
                <Eye className="w-4 h-4 mr-2" />
                View Details
              </Button>
              <Button variant="outline" size="sm">
                <Download className="w-4 h-4 mr-2" />
                Export Report
              </Button>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {teamMembers.map((member) => (
              <div key={member.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium text-gray-700">
                        {member.name.split(' ').map(n => n[0]).join('')}
                      </span>
                    </div>
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-gray-900">{member.name}</h3>
                    <p className="text-sm text-gray-500">{member.role}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <div className={`text-sm font-medium ${getProductivityColor(member.productivity_score)}`}>
                      {member.productivity_score}%
                    </div>
                    <div className="text-xs text-gray-500">
                      {member.focus_time}h productive
                    </div>
                  </div>
                  
                  <Progress value={member.productivity_score} className="w-20" />
                  
                  <Badge className={getStatusColor(member.status)}>
                    {member.status}
                  </Badge>
                  
                  <div className="text-xs text-gray-500">
                    {member.last_active}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}