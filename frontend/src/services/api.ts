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

const API_BASE_URL = getApiUrl();

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;