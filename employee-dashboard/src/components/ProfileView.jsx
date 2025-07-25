import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { 
  User, 
  ArrowLeft,
  Calendar,
  Building,
  Mail
} from 'lucide-react';
import axios from 'axios';

export default function ProfileView() {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const API_BASE_URL = 'https://my-home-backend-7m6d.onrender.com';

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/employee/profile`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProfile(response.data);
    } catch (error) {
      console.error('Failed to fetch profile:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <button
                onClick={() => navigate('/')}
                className="mr-4 p-2 text-gray-400 hover:text-gray-600"
              >
                <ArrowLeft className="h-5 w-5" />
              </button>
              <User className="h-8 w-8 text-blue-600" />
              <h1 className="ml-2 text-2xl font-bold text-gray-900">
                Profile
              </h1>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-center space-x-4 mb-6">
                <div className="h-16 w-16 bg-blue-100 rounded-full flex items-center justify-center">
                  <User className="h-8 w-8 text-blue-600" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-gray-900">
                    {user?.name || 'Employee'}
                  </h2>
                  <p className="text-sm text-gray-500">
                    Employee Dashboard User
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Personal Information */}
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">
                    Personal Information
                  </h3>
                  <div className="space-y-4">
                    <div className="flex items-center">
                      <User className="h-5 w-5 text-gray-400 mr-3" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">Name</p>
                        <p className="text-sm text-gray-500">{user?.name || 'Not available'}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center">
                      <Mail className="h-5 w-5 text-gray-400 mr-3" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">Email</p>
                        <p className="text-sm text-gray-500">{user?.email || 'Not available'}</p>
                      </div>
                    </div>

                    <div className="flex items-center">
                      <Building className="h-5 w-5 text-gray-400 mr-3" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">Team</p>
                        <p className="text-sm text-gray-500">{profile?.team_name || 'Not assigned'}</p>
                      </div>
                    </div>

                    <div className="flex items-center">
                      <Calendar className="h-5 w-5 text-gray-400 mr-3" />
                      <div>
                        <p className="text-sm font-medium text-gray-900">Member Since</p>
                        <p className="text-sm text-gray-500">
                          {profile?.joined_date ? new Date(profile.joined_date).toLocaleDateString() : 'Not available'}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Work Statistics */}
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">
                    Work Statistics
                  </h3>
                  <div className="space-y-4">
                    <div className="bg-gray-50 rounded-lg p-4">
                      <p className="text-sm font-medium text-gray-900">Total Hours This Week</p>
                      <p className="text-2xl font-bold text-blue-600">
                        {profile?.weekly_hours || '0'}h
                      </p>
                    </div>
                    
                    <div className="bg-gray-50 rounded-lg p-4">
                      <p className="text-sm font-medium text-gray-900">Average Productivity</p>
                      <p className="text-2xl font-bold text-green-600">
                        {profile?.avg_productivity || '0'}%
                      </p>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-4">
                      <p className="text-sm font-medium text-gray-900">Focus Sessions</p>
                      <p className="text-2xl font-bold text-purple-600">
                        {profile?.focus_sessions || '0'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
} 