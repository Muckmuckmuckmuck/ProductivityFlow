import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { Users, Crown, Copy, UserPlus, TrendingUp, TrendingDown, Plus, Loader2, AlertCircle, UserMinus } from 'lucide-react';
import EmployeeSummaryModal from '../components/EmployeeSummaryModal';

// Updated to use the Render backend URL (working)
const API_URL = "https://productivityflow-backend-496367590729.us-central1.run.app";

interface Team {
  id: string;
  name: string;
  code: string;
  memberCount: number;
}

interface TeamMember {
  userId: string;
  name: string;
  role: string;
  productiveHours?: number;
  unproductiveHours?: number;
  goalsCompleted?: number;
}

export default function TeamManagementPage() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([]);
  const [newTeamName, setNewTeamName] = useState("");
  const [loading, setLoading] = useState(true);
  const [loadingMembers, setLoadingMembers] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [creatingTeam, setCreatingTeam] = useState(false);

  const [selectedMember, setSelectedMember] = useState<TeamMember | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [removingMember, setRemovingMember] = useState<string | null>(null);

  useEffect(() => { loadTeams(); }, []);
  useEffect(() => { if (selectedTeam) loadTeamMembers(selectedTeam.id); }, [selectedTeam]);

  // Save selected team to localStorage
  useEffect(() => {
    if (selectedTeam) {
      localStorage.setItem('selectedTeamId', selectedTeam.id);
    }
  }, [selectedTeam]);

  const loadTeams = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const { invoke } = await import('@tauri-apps/api/tauri');
      
      // Get the auth token from localStorage
      const token = localStorage.getItem('authToken');
      if (!token) {
        throw new Error('Authentication token not found');
      }
      
      const response = await invoke('http_get', { 
        url: `${API_URL}/api/teams`,
        headers: JSON.stringify({
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        })
      });
      
      const data = JSON.parse(response as string);
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      const teams = data.teams || [];
      setTeams(teams);
      
      // Try to restore previously selected team
      const savedTeamId = localStorage.getItem('selectedTeamId');
      if (savedTeamId && teams.length > 0) {
        const savedTeam = teams.find((team: Team) => team.id === savedTeamId);
        if (savedTeam) {
          setSelectedTeam(savedTeam);
        } else {
          setSelectedTeam(teams[0]);
        }
      } else if (teams.length > 0 && !selectedTeam) {
        setSelectedTeam(teams[0]);
      }
    } catch (error: any) {
      setError(error.message || "Failed to load teams");
      setTeams([]);
    } finally {
      setLoading(false);
    }
  };

  const loadTeamMembers = async (teamId: string) => {
    setLoadingMembers(true);
    try {
      const { invoke } = await import('@tauri-apps/api/tauri');
      
      // Get the auth token from localStorage
      const token = localStorage.getItem('authToken');
      if (!token) {
        throw new Error('Authentication token not found');
      }
      
      const response = await invoke('http_get', { 
        url: `${API_URL}/api/teams/${teamId}/members`,
        headers: JSON.stringify({
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        })
      });
      
      const data = JSON.parse(response as string);
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      setTeamMembers(data.members || []);
    } catch (error: any) {
      console.error("Failed to load team members:", error);
      setError(error.message || "Failed to load team members");
      setTeamMembers([]);
    } finally {
      setLoadingMembers(false);
    }
  };

  const handleCreateTeam = async () => {
    if (!newTeamName.trim()) return;
    
    setCreatingTeam(true);
    setError(null);
    
    try {
      const { invoke } = await import('@tauri-apps/api/tauri');
      
      // Get the auth token from localStorage
      const token = localStorage.getItem('authToken');
      if (!token) {
        throw new Error('Authentication token not found. Please sign in again.');
      }
      
      const requestBody = { 
        name: newTeamName.trim()
      };
      
      console.log('Creating team with:', { url: `${API_URL}/api/teams`, body: requestBody });
      
      const response = await invoke('http_post', {
        url: `${API_URL}/api/teams`,
        body: JSON.stringify(requestBody),
        headers: JSON.stringify({
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        })
      });
      
      console.log('Team creation response:', response);
      
      const data = JSON.parse(response as string);
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      // Extract team data from the response
      const newTeam = {
        id: data.team.id.toString(),
        name: data.team.name,
        code: `TEAM${data.team.id}`, // Generate a simple team code
        memberCount: 1
      };
      
      console.log('New team created:', newTeam);
      
      setTeams(prevTeams => [...prevTeams, newTeam]);
      setSelectedTeam(newTeam);
      setNewTeamName("");
      
      // Show success message
      alert(`Team "${newTeam.name}" created successfully!`);
    } catch (error: any) {
      console.error('Team creation error:', error);
      const errorMessage = error.message || "Failed to create team";
      setError(errorMessage);
      alert(`Failed to create team: ${errorMessage}`);
    } finally {
      setCreatingTeam(false);
    }
  };

  const handleTeamSelect = (team: Team) => {
    setSelectedTeam(team);
    // localStorage save happens automatically via useEffect
  };

  const handleMemberClick = (member: TeamMember) => {
    setSelectedMember(member);
    setIsModalOpen(true);
  };

  const copyTeamCode = (code: string) => {
    navigator.clipboard.writeText(code).then(() => {
      // Show a more user-friendly notification
      const notification = document.createElement('div');
      notification.className = 'fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded-md shadow-lg z-50';
      notification.textContent = 'Team code copied to clipboard!';
      document.body.appendChild(notification);
      setTimeout(() => document.body.removeChild(notification), 2000);
    }).catch(() => {
      alert("Failed to copy team code. Please copy it manually.");
    });
  };

  const handleRetry = () => {
    loadTeams();
  };

  const handleRemoveMember = async (memberId: string, memberName: string) => {
    if (!selectedTeam) return;
    
    if (!confirm(`Are you sure you want to remove ${memberName} from the team? This action cannot be undone.`)) {
      return;
    }
    
    setRemovingMember(memberId);
    setError(null);
    
    try {
      const { invoke } = await import('@tauri-apps/api/tauri');
      
      // Get the auth token from localStorage
      const token = localStorage.getItem('authToken');
      if (!token) {
        throw new Error('Authentication token not found');
      }
      
      const response = await invoke('http_delete', {
        url: `${API_URL}/api/teams/${selectedTeam.id}/members/${memberId}`,
        headers: JSON.stringify({
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        })
      });
      
      const data = JSON.parse(response as string);
      
      if (data.success) {
        // Remove member from local state
        setTeamMembers(prev => prev.filter(member => member.userId !== memberId));
        
        // Show success notification
        const notification = document.createElement('div');
        notification.className = 'fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded-md shadow-lg z-50';
        notification.textContent = `${memberName} has been removed from the team.`;
        document.body.appendChild(notification);
        setTimeout(() => document.body.removeChild(notification), 3000);
      } else {
        throw new Error(data.error || 'Failed to remove member');
      }
    } catch (error: any) {
      console.error("Failed to remove member:", error);
      setError(error.message || "Failed to remove member from team");
      
      // Show error notification
      const notification = document.createElement('div');
      notification.className = 'fixed top-4 right-4 bg-red-500 text-white px-4 py-2 rounded-md shadow-lg z-50';
      notification.textContent = `Failed to remove ${memberName}: ${error.message}`;
      document.body.appendChild(notification);
      setTimeout(() => document.body.removeChild(notification), 3000);
    } finally {
      setRemovingMember(null);
    }
  };



  return (
    <>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold tracking-tight">Team Management</h1>
        
        <Card>
            <CardHeader><CardTitle>Create a New Team</CardTitle></CardHeader>
            <CardContent>
                <div className="flex items-center space-x-2 max-w-md">
                    <Input 
                      value={newTeamName} 
                      onChange={(e) => setNewTeamName(e.target.value)} 
                      placeholder="E.g., Q3 Engineering Squad"
                      disabled={creatingTeam}
                    />
                    <Button 
                      onClick={handleCreateTeam} 
                      disabled={creatingTeam || !newTeamName.trim()}
                    >
                      {creatingTeam ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
                      Create Team
                    </Button>
                </div>
                
                {/* Simple test button */}
                            
                
                {error && (
                  <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                    <div className="flex items-center">
                      <AlertCircle className="h-4 w-4 text-red-500 mr-2" />
                      <span className="text-red-700">{error}</span>
                    </div>
                  </div>
                )}
            </CardContent>
        </Card>

        {/* Error Display */}
        {error && (
          <Card className="border-red-200">
            <CardContent className="flex items-center justify-center py-6">
              <div className="text-center">
                <AlertCircle className="h-8 w-8 text-red-500 mx-auto mb-2" />
                <p className="text-red-600 mb-2">{error}</p>
                <Button onClick={handleRetry} variant="outline" size="sm">
                  Try Again
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="md:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Users className="mr-2 h-5 w-5"/>My Teams
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {loading ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
                  </div>
                ) : teams.length === 0 ? (
                  <div className="text-center py-8">
                    <Users className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-gray-500 text-sm">No teams found</p>
                    <p className="text-gray-400 text-xs">Create your first team above</p>
                  </div>
                ) : (
                  teams.map(team => (
                    <button 
                      key={team.id} 
                      onClick={() => handleTeamSelect(team)} 
                      className={`w-full text-left p-3 rounded-lg border transition-colors ${
                        selectedTeam?.id === team.id 
                          ? 'bg-indigo-100 border-indigo-300' 
                          : 'hover:bg-gray-100'
                      }`}
                    >
                      <div className="flex justify-between items-center">
                        <span className="font-semibold text-gray-800">{team.name}</span>
                        <Badge>Active</Badge>
                      </div>
                      <p className="text-sm text-gray-500">{team.memberCount} members</p>
                    </button>
                  ))
                )}
              </CardContent>
            </Card>
          </div>
          <div className="md:col-span-3">
            {selectedTeam ? (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Crown className="mr-2 h-6 w-6 text-yellow-500"/>
                    {selectedTeam.name} Details
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                    <div>
                      <label className="text-sm font-medium text-gray-600">Team Join Code</label>
                      <div className="mt-2 flex items-center justify-between p-4 bg-gray-100 rounded-lg">
                        <span className="text-2xl font-mono tracking-widest text-indigo-600">
                          {selectedTeam.code}
                        </span>
                        <Button variant="ghost" size="sm" onClick={() => copyTeamCode(selectedTeam.code)}>
                          <Copy className="h-4 w-4"/>
                        </Button>
                      </div>
                    </div>
                    <div>
                    <div className="flex justify-between items-center mb-4">
                      <h3 className="text-lg font-semibold">Team Members</h3>
                      <Button variant="outline">
                        <UserPlus className="h-4 w-4 mr-2"/>Invite
                      </Button>
                    </div>
                    <div className="space-y-3">
                      {loadingMembers ? (
                        <div className="flex items-center justify-center py-8">
                          <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
                        </div>
                      ) : teamMembers.length === 0 ? (
                        <div className="text-center py-8">
                          <Users className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                          <p className="text-gray-500">No members have joined yet</p>
                          <p className="text-gray-400 text-sm">Share the team code above to invite members</p>
                        </div>
                      ) : (
                        teamMembers.map(member => (
                          <div 
                            key={member.userId} 
                            onClick={() => handleMemberClick(member)} 
                            className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 cursor-pointer"
                          >
                            <div className="flex items-center space-x-3">
                              <div className="w-9 h-9 bg-gray-200 rounded-full flex items-center justify-center">
                                <span className="text-sm font-medium text-gray-600">
                                  {member.name.substring(0, 2).toUpperCase()}
                                </span>
                              </div>
                              <div>
                                <p className="font-semibold text-gray-800">{member.name}</p>
                                <p className="text-sm text-gray-500">{member.role}</p>
                              </div>
                            </div>
                            <div className="flex items-center space-x-4">
                              <div className="flex items-center text-sm text-green-600 font-medium">
                                <TrendingUp className="h-4 w-4 mr-1"/>
                                {member.productiveHours || 0}h
                              </div>
                              <div className="flex items-center text-sm text-orange-600 font-medium">
                                <TrendingDown className="h-4 w-4 mr-1"/>
                                {member.unproductiveHours || 0}h
                              </div>
                              {member.role !== 'manager' && (
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleRemoveMember(member.userId, member.name);
                                  }}
                                  disabled={removingMember === member.userId}
                                  className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                >
                                  {removingMember === member.userId ? (
                                    <Loader2 className="h-4 w-4 animate-spin" />
                                  ) : (
                                    <UserMinus className="h-4 w-4" />
                                  )}
                                </Button>
                              )}
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent className="flex items-center justify-center py-12">
                  <div className="text-center">
                    <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500">Select a team to view details</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
      {isModalOpen && (
        <EmployeeSummaryModal 
          member={selectedMember} 
          isOpen={isModalOpen} 
          onClose={() => setIsModalOpen(false)} 
        />
      )}
    </>
  );
}