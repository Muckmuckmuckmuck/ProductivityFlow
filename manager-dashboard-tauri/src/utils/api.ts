import { useState, useEffect } from 'react';

/**
 * Comprehensive API Utilities for ProductivityFlow
 * Handles timeouts, error management, authentication, and security
 */

// API Configuration
const API_URL = "https://my-home-backend-7m6d.onrender.com";
const DEFAULT_TIMEOUT = 30000; // 30 seconds
const RETRY_ATTEMPTS = 3;
const RETRY_DELAY = 1000; // 1 second

// Retry utility
const retry = async <T>(
  fn: () => Promise<T>,
  attempts: number = RETRY_ATTEMPTS,
  delay: number = RETRY_DELAY
): Promise<T> => {
  try {
    return await fn();
  } catch (error) {
    if (attempts <= 1) throw error;
    
    // Wait before retrying
    await new Promise(resolve => setTimeout(resolve, delay));
    
    return retry(fn, attempts - 1, delay * 2); // Exponential backoff
  }
};

// Network status detection
class NetworkManager {
  private static instance: NetworkManager;
  private isOnline: boolean = navigator.onLine;
  private listeners: Array<(online: boolean) => void> = [];

  private constructor() {
    window.addEventListener('online', () => this.updateStatus(true));
    window.addEventListener('offline', () => this.updateStatus(false));
  }

  static getInstance(): NetworkManager {
    if (!NetworkManager.instance) {
      NetworkManager.instance = new NetworkManager();
    }
    return NetworkManager.instance;
  }

  private updateStatus(online: boolean) {
    this.isOnline = online;
    this.listeners.forEach(listener => listener(online));
  }

  isNetworkOnline(): boolean {
    return this.isOnline;
  }

  addListener(listener: (online: boolean) => void) {
    this.listeners.push(listener);
  }

  removeListener(listener: (online: boolean) => void) {
    const index = this.listeners.indexOf(listener);
    if (index > -1) {
      this.listeners.splice(index, 1);
    }
  }
}

// Error types
export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string,
    public details?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export class NetworkError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'NetworkError';
  }
}

export class TimeoutError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'TimeoutError';
  }
}

// Request configuration interface
interface RequestConfig {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  headers?: Record<string, string>;
  body?: any;
  timeout?: number;
  retry?: boolean;
  requireAuth?: boolean;
}

// Response interface
interface APIResponse<T = any> {
  data: T;
  status: number;
  headers: Headers;
}

// Authentication utilities
class AuthManager {
  private static instance: AuthManager;
  private token: string | null = null;

  private constructor() {
    // Load token from localStorage on initialization
    this.token = localStorage.getItem('auth_token');
  }

  static getInstance(): AuthManager {
    if (!AuthManager.instance) {
      AuthManager.instance = new AuthManager();
    }
    return AuthManager.instance;
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  getToken(): string | null {
    return this.token;
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  isAuthenticated(): boolean {
    return !!this.token;
  }
}

// Main API client
class APIClient {
  private networkManager = NetworkManager.getInstance();
  private authManager = AuthManager.getInstance();

  private async makeRequest<T>(
    endpoint: string,
    config: RequestConfig = {}
  ): Promise<APIResponse<T>> {
    const {
      method = 'GET',
      headers = {},
      body,
      timeout = DEFAULT_TIMEOUT,
      retry: shouldRetry = true,
      requireAuth = false
    } = config;

    // Check network status
    if (!this.networkManager.isNetworkOnline()) {
      throw new NetworkError('No internet connection. Please check your network and try again.');
    }

    // Check authentication
    if (requireAuth && !this.authManager.isAuthenticated()) {
      throw new APIError('Authentication required', 401, 'AUTH_REQUIRED');
    }

    // Prepare headers
    const requestHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      ...headers
    };

    // Add authentication header
    if (requireAuth && this.authManager.getToken()) {
      requestHeaders['Authorization'] = `Bearer ${this.authManager.getToken()}`;
    }

    // Prepare request configuration
    const requestConfig: RequestInit = {
      method,
      headers: requestHeaders,
      credentials: 'include'
    };

    // Add body for non-GET requests
    if (body && method !== 'GET') {
      requestConfig.body = JSON.stringify(body);
    }

    // Create request function
    const makeRequest = async (): Promise<APIResponse<T>> => {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      try {
        const response = await fetch(`${API_URL}${endpoint}`, {
          ...requestConfig,
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        // Handle different response types
        if (!response.ok) {
          let errorData;
          try {
            errorData = await response.json();
          } catch {
            errorData = { error: 'Unknown error occurred' };
          }

          throw new APIError(
            errorData.error || `HTTP ${response.status}`,
            response.status,
            errorData.code,
            errorData
          );
        }

        // Parse response
        let data: T;
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('application/json')) {
          data = await response.json();
        } else {
          data = await response.text() as T;
        }

        return {
          data,
          status: response.status,
          headers: response.headers
        };

      } catch (error: unknown) {
        clearTimeout(timeoutId);
        
        if (error instanceof APIError) {
          throw error;
        }
        
        if (error instanceof Error && error.name === 'AbortError') {
          throw new TimeoutError(`Request timed out after ${timeout}ms`);
        }
        
        if (error instanceof TypeError && error.message.includes('fetch')) {
          throw new NetworkError('Network error. Please check your connection.');
        }
        
        throw new Error(`Request failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    };

    // Execute request with retry if enabled
    if (shouldRetry) {
      return retry(makeRequest);
    }
    
    return makeRequest();
  }

  // Public API methods
  async get<T>(endpoint: string, config?: Omit<RequestConfig, 'method'>): Promise<APIResponse<T>> {
    return this.makeRequest<T>(endpoint, { ...config, method: 'GET' });
  }

  async post<T>(endpoint: string, body?: any, config?: Omit<RequestConfig, 'method' | 'body'>): Promise<APIResponse<T>> {
    return this.makeRequest<T>(endpoint, { ...config, method: 'POST', body });
  }

  async put<T>(endpoint: string, body?: any, config?: Omit<RequestConfig, 'method' | 'body'>): Promise<APIResponse<T>> {
    return this.makeRequest<T>(endpoint, { ...config, method: 'PUT', body });
  }

  async delete<T>(endpoint: string, config?: Omit<RequestConfig, 'method'>): Promise<APIResponse<T>> {
    return this.makeRequest<T>(endpoint, { ...config, method: 'DELETE' });
  }

  async patch<T>(endpoint: string, body?: any, config?: Omit<RequestConfig, 'method' | 'body'>): Promise<APIResponse<T>> {
    return this.makeRequest<T>(endpoint, { ...config, method: 'PATCH', body });
  }

  // Authentication methods
  async login(email: string, password: string): Promise<{ token: string; user: any }> {
    const response = await this.post<{ token: string; user: any }>('/api/auth/login', { email, password });
    const { token, user } = response.data;
    
    if (token) {
      this.authManager.setToken(token);
    }
    
    return { token, user };
  }

  async register(email: string, password: string, name: string): Promise<{ user_id: string }> {
    const response = await this.post<{ user_id: string }>('/api/auth/register', { email, password, name });
    return response.data;
  }

  logout(): void {
    this.authManager.clearToken();
  }

  isAuthenticated(): boolean {
    return this.authManager.isAuthenticated();
  }

  // Network status
  isOnline(): boolean {
    return this.networkManager.isNetworkOnline();
  }

  addNetworkListener(listener: (online: boolean) => void): void {
    this.networkManager.addListener(listener);
  }

  removeNetworkListener(listener: (online: boolean) => void): void {
    this.networkManager.removeListener(listener);
  }
}

// Create singleton instance
const apiClient = new APIClient();

// Export the client and utilities
export default apiClient;

// Export types for use in components
export type { APIResponse, RequestConfig };

// Utility functions for common API operations
export const api = {
  // Teams
  getTeams: () => apiClient.get('/api/teams', { requireAuth: true }),
  createTeam: (name: string) => apiClient.post('/api/teams', { name }, { requireAuth: true }),
  joinTeam: (teamCode: string) => apiClient.post('/api/teams/join', { team_code: teamCode }),
  getTeamMembers: (teamId: string) => apiClient.get(`/api/teams/${teamId}/members`, { requireAuth: true }),
  
  // Activity
  submitActivity: (teamId: string, activityData: any) => 
    apiClient.post(`/api/teams/${teamId}/activity`, activityData),
  
  // Analytics
  getBurnoutRisk: (teamId?: string) => 
    apiClient.get('/api/analytics/burnout-risk', { 
      requireAuth: true,
      headers: teamId ? { 'X-Team-ID': teamId } : {}
    }),
  
  getDistractionProfile: (teamId?: string) => 
    apiClient.get('/api/analytics/distraction-profile', { 
      requireAuth: true,
      headers: teamId ? { 'X-Team-ID': teamId } : {}
    }),
  
  getDailySummary: () => 
    apiClient.get('/api/employee/daily-summary', { requireAuth: true }),
  
  // Subscription
  getSubscriptionStatus: () => 
    apiClient.get('/api/subscription/status', { requireAuth: true }),
  
  getCustomerPortal: () => 
    apiClient.get('/api/subscription/customer-portal', { requireAuth: true }),
  
  // Health check
  healthCheck: () => apiClient.get('/health'),
  
  // Authentication
  login: (email: string, password: string) => apiClient.login(email, password),
  register: (email: string, password: string, name: string) => apiClient.register(email, password, name),
  logout: () => apiClient.logout(),
  
  // Network status
  isOnline: () => apiClient.isOnline(),
  addNetworkListener: (listener: (online: boolean) => void) => apiClient.addNetworkListener(listener),
  removeNetworkListener: (listener: (online: boolean) => void) => apiClient.removeNetworkListener(listener)
};

// React hook for network status
export const useNetworkStatus = () => {
  const [isOnline, setIsOnline] = useState(apiClient.isOnline());

  useEffect(() => {
    const handleNetworkChange = (online: boolean) => setIsOnline(online);
    
    apiClient.addNetworkListener(handleNetworkChange);
    
    return () => {
      apiClient.removeNetworkListener(handleNetworkChange);
    };
  }, []);

  return isOnline;
};

// Error boundary utility
export const handleAPIError = (error: any): string => {
  if (error instanceof APIError) {
    switch (error.status) {
      case 401:
        return 'Authentication required. Please log in again.';
      case 403:
        return 'Access denied. You do not have permission to perform this action.';
      case 404:
        return 'The requested resource was not found.';
      case 429:
        return 'Too many requests. Please wait a moment and try again.';
      case 500:
        return 'Server error. Please try again later.';
      default:
        return error.message || 'An unexpected error occurred.';
    }
  }
  
  if (error instanceof NetworkError) {
    return error.message;
  }
  
  if (error instanceof TimeoutError) {
    return 'Request timed out. Please check your connection and try again.';
  }
  
  return 'An unexpected error occurred. Please try again.';
}; 