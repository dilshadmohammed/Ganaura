import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from './pages/LandingPage/LandingPage';
import Login from './pages/Login/Login';
import ForgotPassword from './pages/ForgotPassword/ForgotPassword';
import SignUp from './pages/SignUp/SignUp';
import { Toaster } from 'react-hot-toast';
import api from './api/api';

// Auth service to validate token
const authService = {
  async validateToken(token: string): Promise<boolean> {
    try {
      // Make a request to your backend to validate the token
      const response = await api.post('/api/user/validate-token/', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      return response.status === 200;
    } catch (error) {
      localStorage.removeItem('accessToken');
      return false;
    }
  },
  
  getToken(): string | null {
    return localStorage.getItem('accessToken');
  }
};

// Protected Route component with token validation
const ProtectedRoute: React.FC<{ element: React.ReactElement }> = ({ element }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const verifyAuthentication = async () => {
      const token = authService.getToken();
      if (!token) {
        setIsAuthenticated(false);
        setIsLoading(false);
        return;
      }
      
      try {
        const isValid = await authService.validateToken(token);
        setIsAuthenticated(isValid);
      } catch (error) {
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    };

    verifyAuthentication();
  }, []);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return isAuthenticated ? element : <Navigate to="/login" replace />;
};

// Auth context for global authentication state management
interface AuthContextType {
  isAuthenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = React.createContext<AuthContextType | undefined>(undefined);

const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  
  useEffect(() => {
    // Check authentication status on initial load
    const checkAuth = async () => {
      const token = authService.getToken();
      if (token) {
        const isValid = await authService.validateToken(token);
        setIsAuthenticated(isValid);
      }
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
  
  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <Toaster position="top-center" reverseOrder={false} />
      <Router>
        <Routes>
          {/* Protected Home route */}
          <Route path="/" element={<ProtectedRoute element={<LandingPage />} />} />

          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/signup" element={<SignUp />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;