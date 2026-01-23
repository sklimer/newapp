import axios, { AxiosResponse } from 'axios';
import { API_BASE_URL } from '../config/api';

interface LoginResponse {
  success: boolean;
  user: any;
  telegram: any;
  tokens: {
    access_token: string;
    refresh_token: string;
    expires_in: number;
  };
}

interface TokenRefreshResponse {
  success: boolean;
  tokens: {
    access_token: string;
    refresh_token: string;
    expires_in: number;
  };
}

interface UserResponse {
  success: boolean;
  user: any;
  telegram_id: string;
}

interface SessionValidationResponse {
  valid: boolean;
  user_id?: string;
  reason?: string;
}

class AuthApi {
  private apiClient;

  constructor() {
    this.apiClient = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      withCredentials: true, // Important: Enable credentials to handle cookies
    });

    // Add request interceptor to include Telegram init data when available
    this.apiClient.interceptors.request.use(
      (config) => {
        // Check if we're running in Telegram Web App and add init data
        if (typeof window !== 'undefined' && (window as any).Telegram?.WebApp?.initData) {
          const initData = (window as any).Telegram.WebApp.initData;
          config.headers['X-Telegram-WebApp-Init-Data'] = initData;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Add response interceptor for handling token refresh
    this.apiClient.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        // If we get a 401 and haven't retried yet
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            // Attempt to refresh the token
            await this.refreshToken();
            // Retry the original request
            return this.apiClient(originalRequest);
          } catch (refreshError) {
            // If refresh fails, redirect to login
            this.logout();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  async loginWithTelegram(initData: string): Promise<AxiosResponse<LoginResponse>> {
    try {
      const response = await this.apiClient.post('/auth-jwt/telegram-auth', {
        initData
      });
      return response;
    } catch (error) {
      console.error('Telegram login error:', error);
      throw error;
    }
  }

  async refreshToken(): Promise<AxiosResponse<TokenRefreshResponse>> {
    try {
      const response = await this.apiClient.post('/auth-jwt/refresh-token');
      return response;
    } catch (error) {
      console.error('Token refresh error:', error);
      throw error;
    }
  }

  async logout(): Promise<AxiosResponse<{ success: boolean; message: string }>> {
    try {
      const response = await this.apiClient.post('/auth-jwt/logout');
      return response;
    } catch (error) {
      console.error('Logout error:', error);
      // Even if server logout fails, clear local state
      return { data: { success: true, message: 'Logged out successfully' }, status: 200, statusText: 'OK', headers: {}, config: {} as any };
    }
  }

  async getCurrentUser(): Promise<AxiosResponse<UserResponse>> {
    try {
      const response = await this.apiClient.get('/auth-jwt/me');
      return response;
    } catch (error) {
      console.error('Get current user error:', error);
      throw error;
    }
  }

  async validateSession(): Promise<SessionValidationResponse> {
    try {
      const response = await this.apiClient.get('/auth-jwt/validate-session');
      return response.data;
    } catch (error) {
      console.error('Session validation error:', error);
      return { valid: false, reason: 'server_error' };
    }
  }

  // Method to manually set auth header if needed (fallback)
  setAuthToken(token: string) {
    this.apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  // Method to remove auth header
  removeAuthToken() {
    delete this.apiClient.defaults.headers.common['Authorization'];
  }
}

export const authApi = new AuthApi();