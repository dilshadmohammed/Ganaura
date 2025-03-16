import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import axios from 'axios';

// Auth service to validate token
const authService = {
  async validateToken(token: string): Promise<boolean> {
    try {
      // Make a request to your backend to validate the token
      const response = await axios.get('/api/auth/validate-token', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      return response.status === 200;
    } catch (error) {
      // If token validation fails, remove it from localStorage
      localStorage.removeItem('accessToken');
      return false;
    }
  },
  
  getToken(): string | null {
    return localStorage.getItem('accessToken');
  }
};

// Define the shape of our auth context
interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string) => void;
  logout: () => void;
  validateToken: () => Promise<boolean>;
}

// Create the context with undefined as default value
const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  
  useEffect(() => {
    // Check authentication status on initial load
    const checkAuth = async () => {
      const token = authService.getToken();
      if (token) {
        try {
          const isValid = await authService.validateToken(token);
          setIsAuthenticated(isValid);
        } catch (error) {
          setIsAuthenticated(false);
        }
      }
      setIsLoading(false);
    };
    
    checkAuth();
  }, []);
  
  const login = (token: string) => {
    localStorage.setItem('accessToken', token);
    setIsAuthenticated(true);
  };
  
  const logout = () => {
    localStorage.removeItem('accessToken');
    setIsAuthenticated(false);
  };
  
  const validateToken = async (): Promise<boolean> => {
    const token = authService.getToken();
    if (!token) {
      setIsAuthenticated(false);
      return false;
    }
    
    try {
      const isValid = await authService.validateToken(token);
      setIsAuthenticated(isValid);
      return isValid;
    } catch (error) {
      setIsAuthenticated(false);
      return false;
    }
  };
  
  const value = {
    isAuthenticated,
    isLoading,
    login,
    logout,
    validateToken
  };
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};