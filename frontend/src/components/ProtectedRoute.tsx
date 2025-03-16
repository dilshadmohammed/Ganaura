import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface ProtectedRouteProps {
  element: React.ReactElement;
  redirectPath?: string;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  element, 
  redirectPath = '/login' 
}) => {
  const { isAuthenticated, isLoading, validateToken } = useAuth();
  const [isValidating, setIsValidating] = useState(true);

  useEffect(() => {
    const verifyAuth = async () => {
      await validateToken();
      setIsValidating(false);
    };

    verifyAuth();
  }, [validateToken]);

  // Show loading while checking authentication
  if (isLoading || isValidating) {
    return <div>Loading...</div>;
  }

  // Redirect to login if not authenticated, otherwise render the protected component
  return isAuthenticated ? element : <Navigate to={redirectPath} replace />;
};

export default ProtectedRoute;