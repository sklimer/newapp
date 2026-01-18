import axios from 'axios';
import apiClient from './api';
// Import specific APIs to copy their functionality
import { userApi } from './api';

// Create a separate API client without Telegram interceptor for Telegram auth
const baseApiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Copy request interceptors except Telegram one
baseApiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Copy response interceptor
baseApiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    } else if (error.response?.status === 400 && error.response?.data?.detail?.includes('Telegram')) {
      console.error('Telegram authentication error:', error.response.data.detail);
    }
    return Promise.reject(error);
  }
);

export const userApiExtended = {
  ...userApi,
  get_current_user_from_telegram: (initData: string) => 
    // Pass initData in the request body for Telegram authentication
    baseApiClient.post('/auth/telegram', { initData })
};

// Export userApiExtended as userApi to maintain compatibility
export { userApiExtended as userApi };