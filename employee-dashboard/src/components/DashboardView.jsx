import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { 
  BarChart3, 
  Clock, 
  TrendingUp, 
  Activity, 
  LogOut, 
  User,
  Calendar,
  Target
} from 'lucide-react';
import axios from 'axios';

export default function DashboardView() {
  const { user, token, logout } = useAuth();
  const navigate = useNavigate();
  const [dailySummary, setDailySummary] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const API_BASE_URL = 'https://my-home-backend-7m6d.onrender.com';

  useEffect(() => {
    fetchDailySummary();
  }, []);

  const fetchDailySummary = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/employee/daily-summary`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDailySummary(response.data);
    } catch (error) {
      console.error('Failed to fetch daily summary:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
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
              <Activity className="h-8 w-8 text-blue-600" />
              <h1 className="ml-2 text-2xl font-bold text-gray-900">
                Employee Dashboard
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Welcome, {user?.name || 'Employee'}
              </span>
              <button
                onClick={handleLogout}
                className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
              >
                <LogOut className="h-4 w-4 mr-1" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Clock className="h-6 w-6 text-blue-600" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Hours Worked Today
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {dailySummary?.hours_worked || '0'}h
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Target className="h-6 w-6 text-green-600" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Productivity Score
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {dailySummary?.productivity_score || '0'}%
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <BarChart3 className="h-6 w-6 text-purple-600" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Active Applications
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {dailySummary?.active_apps || '0'}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <TrendingUp className="h-6 w-6 text-orange-600" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Focus Time
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {dailySummary?.focus_time || '0'}h
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                Today's Activity Summary
              </h3>
              <div className="space-y-4">
                {dailySummary?.activities?.map((activity, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
                          <Activity className="h-4 w-4 text-blue-600" />
                        </div>
                      </div>
                      <div className="ml-4">
                        <p className="text-sm font-medium text-gray-900">
                          {activity.active_app}
                        </p>
                        <p className="text-sm text-gray-500">
                          {new Date(activity.last_active).toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                    <div className="text-sm text-gray-500">
                      {activity.duration || '0'} min
                    </div>
                  </div>
                ))}
                {(!dailySummary?.activities || dailySummary.activities.length === 0) && (
                  <div className="text-center py-8 text-gray-500">
                    No activity recorded today
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
} 