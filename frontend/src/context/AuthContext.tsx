import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import authService, { AuthUser, LoginCredentials } from '../services/authService';

interface AuthContextType {
  user: AuthUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  isAdmin: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshUser = async () => {
    try {
      const currentUser = await authService.getCurrentUser();
      if (currentUser) {
        setUser(currentUser);
        localStorage.setItem('auth_user', JSON.stringify(currentUser));
      } else {
        setUser(null);
        authService.clearAuth();
      }
    } catch (error) {
      console.error('Failed to refresh user:', error);
      setUser(null);
      authService.clearAuth();
    }
  };

  useEffect(() => {
    const initAuth = async () => {
      // First check stored user
      const storedUser = authService.getStoredUser();
      if (storedUser) {
        setUser(storedUser);
        // Then verify with server
        await refreshUser();
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (credentials: LoginCredentials) => {
    const response = await authService.login(credentials);
    setUser(response.user);
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
    // Redirect to login
    window.location.href = '/login';
  };

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'admin',
    login,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};