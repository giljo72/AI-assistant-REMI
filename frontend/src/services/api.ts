import axios from 'axios';

// Get API URL from environment or auto-detect based on current host
const getApiUrl = () => {
  // If env variable is set, use it
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // Otherwise, use the same host as the frontend
  const host = window.location.hostname;
  return `http://${host}:8000/api`;
};

export const API_BASE_URL = getApiUrl();

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Include cookies
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth data and redirect to login
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth_user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Helper function for API requests
export async function apiRequest<T = any>(
  endpoint: string, 
  options: {
    method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
    body?: string;
    headers?: Record<string, string>;
  } = {}
): Promise<T> {
  const { method = 'GET', body, headers = {} } = options;
  
  const token = localStorage.getItem('auth_token');
  const authHeaders: Record<string, string> = token ? { 'Authorization': `Bearer ${token}` } : {};
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...authHeaders,
      ...headers,
    },
    body,
    credentials: 'include', // Include cookies
  });
  
  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || `API request failed: ${response.statusText}`);
  }
  
  return response.json();
}

export default api;