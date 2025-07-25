import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('employee_token'));

  const API_BASE_URL = 'https://my-home-backend-7m6d.onrender.com';

  useEffect(() => {
    if (token) {
      // Verify token and get user data
      verifyToken();
    } else {
      setIsLoading(false);
    }
  }, [token]);

  const verifyToken = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/employee/daily-summary`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data) {
        setUser(response.data.user || {});
      }
    } catch (error) {
      console.error('Token verification failed:', error);
      logout();
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/employee-login`, {
        email: email,
        password: password
      });

      if (response.data.token) {
        const newToken = response.data.token;
        setToken(newToken);
        localStorage.setItem('employee_token', newToken);
        setUser(response.data.user);
        return { success: true };
      }
    } catch (error) {
      console.error('Login failed:', error);
      return { 
        success: false, 
        error: error.response?.data?.error || 'Login failed' 
      };
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('employee_token');
  };

  const value = {
    user,
    token,
    isAuthenticated: !!token && !!user,
    isLoading,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 