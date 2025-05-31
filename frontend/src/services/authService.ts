import axios from 'axios';
import { API_BASE_URL } from './api';

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthUser {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'user';
  is_active: boolean;
  is_first_login: boolean;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

export interface SetupStatus {
  needs_setup: boolean;
  has_admin: boolean;
}

export interface CreateAdminData {
  username: string;
  email: string;
  password: string;
  recovery_pin: string;
}

class AuthService {
  private tokenKey = 'auth_token';
  private userKey = 'auth_user';

  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await axios.post<LoginResponse>(
      `${API_BASE_URL}/auth/login`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        withCredentials: true, // Important for cookies
      }
    );

    // Store token and user info
    localStorage.setItem(this.tokenKey, response.data.access_token);
    localStorage.setItem(this.userKey, JSON.stringify(response.data.user));

    return response.data;
  }

  async logout(): Promise<void> {
    try {
      await axios.post(
        `${API_BASE_URL}/auth/logout`,
        {},
        { withCredentials: true }
      );
    } finally {
      // Clear local storage regardless
      localStorage.removeItem(this.tokenKey);
      localStorage.removeItem(this.userKey);
    }
  }

  async getCurrentUser(): Promise<AuthUser | null> {
    try {
      const response = await axios.get<AuthUser>(
        `${API_BASE_URL}/auth/me`,
        { withCredentials: true }
      );
      return response.data;
    } catch {
      return null;
    }
  }

  getStoredUser(): AuthUser | null {
    const userStr = localStorage.getItem(this.userKey);
    return userStr ? JSON.parse(userStr) : null;
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  isAdmin(): boolean {
    const user = this.getStoredUser();
    return user?.role === 'admin';
  }

  clearAuth(): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.userKey);
  }

  async checkSetupStatus(): Promise<SetupStatus> {
    const response = await axios.get<SetupStatus>(`${API_BASE_URL}/auth/setup-status`);
    return response.data;
  }

  async createAdminAccount(data: CreateAdminData): Promise<LoginResponse> {
    const response = await axios.post<LoginResponse>(
      `${API_BASE_URL}/auth/setup-admin`,
      data,
      { withCredentials: true }
    );

    // Store token and user info
    localStorage.setItem(this.tokenKey, response.data.access_token);
    localStorage.setItem(this.userKey, JSON.stringify(response.data.user));

    return response.data;
  }
}

export default new AuthService();