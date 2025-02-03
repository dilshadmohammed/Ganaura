import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css'; // Optional: Add styles for the login page

const Login: React.FC = () => {
  const navigate = useNavigate();

  const handleLogin = () => {
    // Add your login logic here
    console.log('Login logic goes here');
    navigate('/'); // Redirect to home after login
  };

  return (
    <div className="login-container">
      <h1>Login Page</h1>
      <button onClick={handleLogin}>Login</button>
    </div>
  );
};

export default Login;