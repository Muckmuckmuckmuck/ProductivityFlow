import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Input } from '../components/ui/Input';
import { 
  TrendingUp, 
  Users, 
  Target,
  Download,
  BarChart3,
  RefreshCw,
  AlertCircle,
  User,
  Building,
  Search,
  Eye,
  Moon,
  Sun,
  Filter,
  MoreVertical,
  Download as DownloadIcon,
  MessageSquare,
  ChevronDown,
  ChevronUp,
  Grid3X3,
  List,
  Circle
} from 'lucide-react';

const API_URL = "https://productivityflow-backend-496367590729.us-central1.run.app";

interface TeamMember {
  userId: string;
  name: string;
  role: string;
  department: string;
  productiveHours: number;
  unproductiveHours: number;
  totalHours: number;
  productivityScore: number;
  lastActive: string;
  status: 'online' | 'offline' | 'away';
  teamName?: string;
  isOnline: boolean;
  currentActivity?: string;
  focusSessions: number;
  breaksTaken: number;
  weeklyAverage: number;
  monthlyAverage: number;
}

interface TeamData {
  id: string;
  name: string;
  members: TeamMember[];
  totalProductiveHours: number;
  totalUnproductiveHours: number;
  averageProductivity: number;
  activeMembers: number;
  totalMembers: number;
}







type SortField = 'name' | 'productiveHours' | 'productivityScore' | 'lastActive' | 'role';
type SortDirection = 'asc' | 'desc';
type DateRange = 'today' | 'week' | 'month' | 'quarter' | 'custom';

export default function Dashboard() {
  // Core state
  const [teams, setTeams] = useState<TeamData[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<TeamData | null>(null);
  const [error, setError] = useState<string | null>(null);

  // UI/UX state
  const [darkMode, setDarkMode] = useState(false);
  const [hoveredEmployee, setHoveredEmployee] = useState<string | null>(null);
  const [compareMode, setCompareMode] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortField, setSortField] = useState<SortField>('name');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
  const [filterRole, setFilterRole] = useState<string>('all');
  const [filterDepartment, setFilterDepartment] = useState<string>('all');
  const [dateRange, setDateRange] = useState<DateRange>('week');
  const [customDateRange, setCustomDateRange] = useState<{start: string, end: string}>({
    start: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0]
  });
  const [showFilters, setShowFilters] = useState(false);
  const [dashboardLayout, setDashboardLayout] = useState<'grid' | 'list'>('grid');
  const [selectedEmployees, setSelectedEmployees] = useState<string[]>([]);
  const [contextMenu, setContextMenu] = useState<{x: number, y: number, employee: TeamMember} | null>(null);

  // Loading states
  const [loadingSkeleton, setLoadingSkeleton] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [generatingReport, setGeneratingReport] = useState(false);

  const searchRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Load dark mode preference
    const savedDarkMode = localStorage.getItem('darkMode') === 'true';
    setDarkMode(savedDarkMode);
    
    // Apply dark mode to body
    if (savedDarkMode) {
      document.body.classList.add('dark');
    }
    
    fetchDashboardData();
    
    // Set up real-time updates
    const interval = setInterval(() => {
      fetchRealTimeData();
    }, 30000); // Update every 30 seconds
    
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedTeam) {
      // Analytics and tasks will be fetched when needed
    }
  }, [selectedTeam, dateRange, customDateRange]);

  const toggleDarkMode = () => {
    const newDarkMode = !darkMode;
    setDarkMode(newDarkMode);
    localStorage.setItem('darkMode', newDarkMode.toString());
    if (newDarkMode) {
      document.body.classList.add('dark');
    } else {
      document.body.classList.remove('dark');
    }
  };

  const fetchDashboardData = async () => {
    setLoadingSkeleton(true);
    setError(null);
    
    try {
      const { invoke } = await import('@tauri-apps/api/tauri');
      
      const response = await invoke('http_get', { 
        url: `${API_URL}/api/teams/public` 
      });
      
      const data = JSON.parse(response as string);
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      const teamsData = data.teams || [];
      setTeams(teamsData);
      
      // Select first team by default
      if (teamsData.length > 0 && !selectedTeam) {
        setSelectedTeam(teamsData[0]);
      }
    } catch (error: any) {
      console.error("Failed to load dashboard data:", error);
      setError(error.message || "Failed to load dashboard data");
    } finally {
      setLoadingSkeleton(false);
    }
  };

  const fetchRealTimeData = async () => {
    if (!selectedTeam) return;
    
    try {
      const { invoke } = await import('@tauri-apps/api/tauri');
      
      const response = await invoke('http_get', { 
        url: `${API_URL}/api/teams/${selectedTeam.id}/members` 
      });
      
      const data = JSON.parse(response as string);
      
      if (data.success) {
        // Update team members with real-time data
        setSelectedTeam(prev => prev ? {
          ...prev,
          members: data.members.map((member: any) => ({
            ...member,
            isOnline: member.status === 'online',
            lastActive: member.lastActive || new Date().toISOString()
          }))
        } : null);
      }
    } catch (error) {
      console.error("Failed to fetch real-time data:", error);
    }
  };



  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const filteredAndSortedMembers = () => {
    if (!selectedTeam) return [];
    
    let members = [...selectedTeam.members];
    
    // Apply search filter
    if (searchQuery) {
      members = members.filter(member => 
        member.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        member.role.toLowerCase().includes(searchQuery.toLowerCase()) ||
        member.department.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
    
    // Apply role filter
    if (filterRole !== 'all') {
      members = members.filter(member => member.role === filterRole);
    }
    
    // Apply department filter
    if (filterDepartment !== 'all') {
      members = members.filter(member => member.department === filterDepartment);
    }
    
    // Apply sorting
    members.sort((a, b) => {
      let aValue: any = a[sortField];
      let bValue: any = b[sortField];
      
      if (sortField === 'lastActive') {
        aValue = new Date(aValue).getTime();
        bValue = new Date(bValue).getTime();
      }
      
      if (sortDirection === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });
    
    return members;
  };

  const handleEmployeeHover = (employeeId: string | null) => {
    setHoveredEmployee(employeeId);
  };

  const handleEmployeeClick = (employee: TeamMember) => {
    // Handle employee click - could open modal or navigate to details
    console.log('Employee clicked:', employee.name);
  };

  const handleContextMenu = (e: React.MouseEvent, employee: TeamMember) => {
    e.preventDefault();
    setContextMenu({
      x: e.clientX,
      y: e.clientY,
      employee
    });
  };

  const closeContextMenu = () => {
    setContextMenu(null);
  };

  const handleBulkAction = (action: 'select' | 'deselect', employeeId: string) => {
    if (action === 'select') {
      setSelectedEmployees(prev => [...prev, employeeId]);
    } else {
      setSelectedEmployees(prev => prev.filter(id => id !== employeeId));
    }
  };

  const generatePDFReport = async () => {
    setGeneratingReport(true);
    try {
      // Simulate PDF generation
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Create download link
      const link = document.createElement('a');
      link.href = 'data:text/plain;charset=utf-8,Report generated successfully';
      link.download = `team-report-${new Date().toISOString().split('T')[0]}.pdf`;
      link.click();
    } catch (error) {
      console.error('Failed to generate report:', error);
    } finally {
      setGeneratingReport(false);
    }
  };

  const refreshData = async () => {
    setRefreshing(true);
    await fetchDashboardData();
    setRefreshing(false);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'text-green-600 bg-green-100';
      case 'away': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'online': return 'Online';
      case 'away': return 'Away';
      default: return 'Offline';
    }
  };

  // Loading skeleton component
  const LoadingSkeleton = () => (
    <div className="space-y-6 animate-pulse">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <Card key={i} className="bg-gray-100 dark:bg-gray-800">
            <CardContent className="p-6">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2"></div>
              <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
            </CardContent>
          </Card>
        ))}
      </div>
      <Card className="bg-gray-100 dark:bg-gray-800">
        <CardContent className="p-6">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-12 bg-gray-200 dark:bg-gray-700 rounded"></div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );

  // Empty state component
  const EmptyState = ({ title, description, icon: Icon, action }: {
    title: string;
    description: string;
    icon: any;
    action?: { label: string; onClick: () => void };
  }) => (
    <div className="text-center py-12">
      <Icon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
      <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">{title}</h3>
      <p className="text-gray-500 dark:text-gray-400 mb-6">{description}</p>
      {action && (
        <Button onClick={action.onClick} className="bg-indigo-600 hover:bg-indigo-700">
          {action.label}
        </Button>
      )}
    </div>
  );

  if (loadingSkeleton) {
    return <LoadingSkeleton />;
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">Error Loading Dashboard</h3>
        <p className="text-gray-500 dark:text-gray-400 mb-6">{error}</p>
        <Button onClick={fetchDashboardData} variant="outline">
          Try Again
        </Button>
      </div>
    );
  }

  const filteredMembers = filteredAndSortedMembers();
  const onlineMembers = selectedTeam?.members.filter(m => m.isOnline) || [];
  const totalProductiveHours = selectedTeam?.totalProductiveHours || 0;
  const averageProductivity = selectedTeam?.averageProductivity || 0;
  const activeMembers = selectedTeam?.activeMembers || 0;

  return (
    <div className={`min-h-screen ${darkMode ? 'dark bg-gray-900' : 'bg-gray-50'}`}>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
            <p className="text-gray-600 dark:text-gray-400">
              {selectedTeam ? `${selectedTeam.name} • ${activeMembers} active members` : 'Select a team to view data'}
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <Button
              onClick={toggleDarkMode}
              variant="outline"
              size="sm"
              className="flex items-center space-x-2"
            >
              {darkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
              <span>{darkMode ? 'Light' : 'Dark'}</span>
            </Button>
            <Button
              onClick={refreshData}
              variant="outline"
              size="sm"
              disabled={refreshing}
              className="flex items-center space-x-2"
            >
              <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </Button>
            <Button
              onClick={generatePDFReport}
              disabled={generatingReport}
              className="bg-indigo-600 hover:bg-indigo-700 flex items-center space-x-2"
            >
              <DownloadIcon className="h-4 w-4" />
              <span>{generatingReport ? 'Generating...' : 'Download PDF'}</span>
            </Button>
          </div>
        </div>

        {/* Team Selector */}
        {teams.length > 0 && (
          <div className="flex items-center space-x-4">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Team:</label>
            <select
              value={selectedTeam?.id || ''}
              onChange={(e) => {
                const team = teams.find(t => t.id === e.target.value);
                setSelectedTeam(team || null);
              }}
              className="border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            >
              {teams.map(team => (
                <option key={team.id} value={team.id}>{team.name}</option>
              ))}
            </select>
          </div>
        )}

        {selectedTeam ? (
          <>
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card className="bg-white dark:bg-gray-800 shadow-sm hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Productive Hours</p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">{totalProductiveHours.toFixed(1)}h</p>
                    </div>
                    <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
                      <TrendingUp className="h-6 w-6 text-green-600 dark:text-green-400" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-white dark:bg-gray-800 shadow-sm hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Average Productivity</p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">{averageProductivity.toFixed(1)}%</p>
                    </div>
                    <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
                      <Target className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-white dark:bg-gray-800 shadow-sm hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Members</p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">{activeMembers}</p>
                    </div>
                    <div className="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
                      <Users className="h-6 w-6 text-purple-600 dark:text-purple-400" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-white dark:bg-gray-800 shadow-sm hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Online Now</p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">{onlineMembers.length}</p>
                    </div>
                    <div className="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
                      <Circle className="h-6 w-6 text-green-600 dark:text-green-400 fill-current" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Search and Filters */}
            <Card className="bg-white dark:bg-gray-800 shadow-sm">
              <CardContent className="p-6">
                <div className="flex flex-col lg:flex-row gap-4">
                  {/* Search */}
                  <div className="flex-1 relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      ref={searchRef}
                      placeholder="Search employees, teams, or projects..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>

                  {/* Date Range */}
                  <select
                    value={dateRange}
                    onChange={(e) => setDateRange(e.target.value as DateRange)}
                    className="border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  >
                    <option value="today">Today</option>
                    <option value="week">Last 7 Days</option>
                    <option value="month">This Month</option>
                    <option value="quarter">Last Quarter</option>
                    <option value="custom">Custom Range</option>
                  </select>

                  {/* Filters Toggle */}
                  <Button
                    onClick={() => setShowFilters(!showFilters)}
                    variant="outline"
                    className="flex items-center space-x-2"
                  >
                    <Filter className="h-4 w-4" />
                    <span>Filters</span>
                  </Button>

                  {/* Layout Toggle */}
                  <Button
                    onClick={() => setDashboardLayout(dashboardLayout === 'grid' ? 'list' : 'grid')}
                    variant="outline"
                    className="flex items-center space-x-2"
                  >
                    {dashboardLayout === 'grid' ? <List className="h-4 w-4" /> : <Grid3X3 className="h-4 w-4" />}
                    <span>{dashboardLayout === 'grid' ? 'List' : 'Grid'}</span>
                  </Button>
                </div>

                {/* Expanded Filters */}
                {showFilters && (
                  <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Role</label>
                      <select
                        value={filterRole}
                        onChange={(e) => setFilterRole(e.target.value)}
                        className="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                      >
                        <option value="all">All Roles</option>
                        <option value="manager">Manager</option>
                        <option value="employee">Employee</option>
                        <option value="intern">Intern</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Department</label>
                      <select
                        value={filterDepartment}
                        onChange={(e) => setFilterDepartment(e.target.value)}
                        className="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                      >
                        <option value="all">All Departments</option>
                        <option value="engineering">Engineering</option>
                        <option value="design">Design</option>
                        <option value="marketing">Marketing</option>
                        <option value="sales">Sales</option>
                      </select>
                    </div>
                    <div className="flex items-end">
                      <Button
                        onClick={() => {
                          setFilterRole('all');
                          setFilterDepartment('all');
                          setSearchQuery('');
                        }}
                        variant="outline"
                        size="sm"
                      >
                        Clear Filters
                      </Button>
                    </div>
                  </div>
                )}

                {/* Custom Date Range */}
                {dateRange === 'custom' && (
                  <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Start Date</label>
                      <input
                        type="date"
                        value={customDateRange.start}
                        onChange={(e) => setCustomDateRange(prev => ({ ...prev, start: e.target.value }))}
                        className="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">End Date</label>
                      <input
                        type="date"
                        value={customDateRange.end}
                        onChange={(e) => setCustomDateRange(prev => ({ ...prev, end: e.target.value }))}
                        className="w-full border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                      />
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Team Members */}
            <Card className="bg-white dark:bg-gray-800 shadow-sm">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Team Members ({filteredMembers.length})</span>
                  <div className="flex items-center space-x-2">
                    <Button
                      onClick={() => setCompareMode(!compareMode)}
                      variant={compareMode ? "default" : "outline"}
                      size="sm"
                    >
                      <BarChart3 className="h-4 w-4 mr-2" />
                      Compare
                    </Button>
                    {selectedEmployees.length > 0 && (
                      <Badge variant="secondary">
                        {selectedEmployees.length} selected
                      </Badge>
                    )}
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {filteredMembers.length === 0 ? (
                  <EmptyState
                    title="No team members found"
                    description="Try adjusting your search or filters to find what you're looking for."
                    icon={Users}
                    action={{ label: "Clear Filters", onClick: () => {
                      setSearchQuery('');
                      setFilterRole('all');
                      setFilterDepartment('all');
                    }}}
                  />
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="sticky top-0 bg-white dark:bg-gray-800 z-10">
                        <tr className="border-b border-gray-200 dark:border-gray-700">
                          <th className="text-left py-3 px-4">
                            <div className="flex items-center space-x-2">
                              <input
                                type="checkbox"
                                checked={selectedEmployees.length === filteredMembers.length}
                                onChange={(e) => {
                                  if (e.target.checked) {
                                    setSelectedEmployees(filteredMembers.map(m => m.userId));
                                  } else {
                                    setSelectedEmployees([]);
                                  }
                                }}
                                className="rounded"
                              />
                              <span>Select</span>
                            </div>
                          </th>
                          <th className="text-left py-3 px-4">
                            <button
                              onClick={() => handleSort('name')}
                              className="flex items-center space-x-1 hover:text-gray-600 dark:hover:text-gray-300"
                            >
                              <span>Name</span>
                              {sortField === 'name' && (
                                sortDirection === 'asc' ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />
                              )}
                            </button>
                          </th>
                          <th className="text-left py-3 px-4">
                            <button
                              onClick={() => handleSort('role')}
                              className="flex items-center space-x-1 hover:text-gray-600 dark:hover:text-gray-300"
                            >
                              <span>Role</span>
                              {sortField === 'role' && (
                                sortDirection === 'asc' ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />
                              )}
                            </button>
                          </th>
                          <th className="text-left py-3 px-4">Status</th>
                          <th className="text-left py-3 px-4">
                            <button
                              onClick={() => handleSort('productiveHours')}
                              className="flex items-center space-x-1 hover:text-gray-600 dark:hover:text-gray-300"
                            >
                              <span>Productive Hours</span>
                              {sortField === 'productiveHours' && (
                                sortDirection === 'asc' ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />
                              )}
                            </button>
                          </th>
                          <th className="text-left py-3 px-4">
                            <button
                              onClick={() => handleSort('productivityScore')}
                              className="flex items-center space-x-1 hover:text-gray-600 dark:hover:text-gray-300"
                            >
                              <span>Productivity</span>
                              {sortField === 'productivityScore' && (
                                sortDirection === 'asc' ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />
                              )}
                            </button>
                          </th>
                          <th className="text-left py-3 px-4">
                            <button
                              onClick={() => handleSort('lastActive')}
                              className="flex items-center space-x-1 hover:text-gray-600 dark:hover:text-gray-300"
                            >
                              <span>Last Active</span>
                              {sortField === 'lastActive' && (
                                sortDirection === 'asc' ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />
                              )}
                            </button>
                          </th>
                          <th className="text-left py-3 px-4">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredMembers.map((member) => (
                          <tr
                            key={member.userId}
                            className={`border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                              hoveredEmployee === member.userId ? 'bg-blue-50 dark:bg-blue-900/20' : ''
                            }`}
                            onMouseEnter={() => handleEmployeeHover(member.userId)}
                            onMouseLeave={() => handleEmployeeHover(null)}
                            onContextMenu={(e) => handleContextMenu(e, member)}
                          >
                            <td className="py-3 px-4">
                              <input
                                type="checkbox"
                                checked={selectedEmployees.includes(member.userId)}
                                onChange={(e) => handleBulkAction(e.target.checked ? 'select' : 'deselect', member.userId)}
                                className="rounded"
                              />
                            </td>
                            <td className="py-3 px-4">
                              <div className="flex items-center space-x-3">
                                <div className="relative">
                                  <div className="w-8 h-8 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center justify-center">
                                    <User className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                                  </div>
                                  {member.isOnline && (
                                    <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white dark:border-gray-800"></div>
                                  )}
                                </div>
                                <div>
                                  <div className="font-medium text-gray-900 dark:text-white">{member.name}</div>
                                  <div className="text-sm text-gray-500 dark:text-gray-400">{member.department}</div>
                                </div>
                              </div>
                            </td>
                            <td className="py-3 px-4">
                              <Badge variant="secondary">{member.role}</Badge>
                            </td>
                            <td className="py-3 px-4">
                              <Badge className={getStatusColor(member.status)}>
                                {getStatusText(member.status)}
                              </Badge>
                            </td>
                            <td className="py-3 px-4">
                              <div className="text-sm text-gray-900 dark:text-white">{member.productiveHours.toFixed(1)}h</div>
                              {compareMode && (
                                <div className="text-xs text-gray-500 dark:text-gray-400">
                                  vs {averageProductivity.toFixed(1)}h avg
                                </div>
                              )}
                            </td>
                            <td className="py-3 px-4">
                              <div className="flex items-center space-x-2">
                                <div className="text-sm font-medium text-gray-900 dark:text-white">
                                  {member.productivityScore.toFixed(1)}%
                                </div>
                                <div className="w-16 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                                  <div
                                    className={`h-2 rounded-full ${
                                      member.productivityScore >= 80 ? 'bg-green-500' :
                                      member.productivityScore >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                                    }`}
                                    style={{ width: `${member.productivityScore}%` }}
                                  ></div>
                                </div>
                              </div>
                            </td>
                            <td className="py-3 px-4">
                              <div className="text-sm text-gray-500 dark:text-gray-400">
                                {new Date(member.lastActive).toLocaleDateString()}
                              </div>
                              <div className="text-xs text-gray-400 dark:text-gray-500">
                                {new Date(member.lastActive).toLocaleTimeString()}
                              </div>
                            </td>
                            <td className="py-3 px-4">
                              <div className="flex items-center space-x-2">
                                <Button
                                  onClick={() => handleEmployeeClick(member)}
                                  variant="outline"
                                  size="sm"
                                >
                                  <Eye className="h-4 w-4" />
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                >
                                  <MessageSquare className="h-4 w-4" />
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                >
                                  <MoreVertical className="h-4 w-4" />
                                </Button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
          </>
        ) : (
          <EmptyState
            title="No team selected"
            description="Select a team from the dropdown above to view dashboard data."
            icon={Building}
          />
        )}
      </div>

      {/* Context Menu */}
      {contextMenu && (
        <div
          className="fixed z-50 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg py-1"
          style={{ top: contextMenu.y, left: contextMenu.x }}
        >
          <button
            onClick={() => {
              handleEmployeeClick(contextMenu.employee);
              closeContextMenu();
            }}
            className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center space-x-2"
          >
            <Eye className="h-4 w-4" />
            <span>View Details</span>
          </button>
          <button
            onClick={() => {
              // Handle send message
              closeContextMenu();
            }}
            className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center space-x-2"
          >
            <MessageSquare className="h-4 w-4" />
            <span>Send Message</span>
          </button>
          <button
            onClick={() => {
              // Handle download report
              closeContextMenu();
            }}
            className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center space-x-2"
          >
            <Download className="h-4 w-4" />
            <span>Download Report</span>
          </button>
        </div>
      )}

      {/* Click outside to close context menu */}
      {contextMenu && (
        <div
          className="fixed inset-0 z-40"
          onClick={closeContextMenu}
        />
      )}
    </div>
  );
}