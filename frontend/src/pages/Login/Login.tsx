import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css';
import api from '../../api/api';
import toast from 'react-hot-toast';


const Login: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({});

  const validateForm = () => {
    const newErrors: { email?: string; password?: string } = {};

    // Email validation
    if (!email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Email is invalid';
    }

    // Password validation
    if (!password) {
      newErrors.password = 'Password is required';
    } else if (password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0; // Return true if no errors
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
<<<<<<< HEAD
      // Add login logic here (e.g., API call to authenticate user)
      // For now, simulate a successful login
      alert('Login successful!');
      navigate('/post-login'); // Redirect to the PostLogin page
=======
      toast.promise(
        api.post('/api/user/auth/', {
          username: email,
          password: password
        }),
        {
          loading: 'Logging in...',
          success: (response) => {
            localStorage.setItem('accessToken', response.data.response.accessToken);
            setTimeout(() => {
              window.location.href = '/'; // Redirect to home after success
            }, 2000);
            return 'Login successful! Redirecting...';
          },
          error: 'Invalid credentials. Please try again.',
        }
      );
>>>>>>> a4ac87146d3785e6bc31f1c8eab812cb4f792c52
    }
  };

  return (
    <div className="login-page">
      <form className="login-form" onSubmit={handleSubmit}>
        <h2>Login</h2>

        {/* Email Input */}
        <div className="input-group">
          <label htmlFor="email">Email</label>
          <input
            type="email"
            id="email"
            placeholder="Enter your Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          {errors.email && <span className="error">{errors.email}</span>}
        </div>

        {/* Password Input */}
        <div className="input-group">
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            placeholder="Enter your Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          {errors.password && <span className="error">{errors.password}</span>}
        </div>

        {/* Remember Me and Forgot Password */}
        <div className="options">
          <div className="remember-me">
            <input type="checkbox" id="remember-me" />
            <label htmlFor="remember-me">Remember me</label>
          </div>
          <button
            type="button"
            className="forgot-password"
            onClick={() => navigate('/forgot-password')}
          >
            Forgot password?
          </button>
        </div>

        {/* Sign In Button */}
        <button type="submit" className="sign-in-button">
          Sign In
        </button>

        {/* Sign Up Link */}
        <p className="sign-up">
          Don't have an account?{' '}
          <button
            type="button"
            className="sign-up-link"
            onClick={() => navigate('/signup')}
          >
            Sign Up
          </button>
        </p>
      </form>
    </div>
  );
};

export default Login;