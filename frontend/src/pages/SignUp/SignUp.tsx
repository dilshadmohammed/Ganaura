import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './SignUp.css';

const SignUp: React.FC = () => {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errors, setErrors] = useState<{
    name?: string;
    email?: string;
    password?: string;
    confirmPassword?: string;
  }>({});

  const validateForm = () => {
    const newErrors: {
      name?: string;
      email?: string;
      password?: string;
      confirmPassword?: string;
    } = {};

    // Name validation
    if (!name) {
      newErrors.name = 'Name is required';
    }

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

    // Confirm Password validation
    if (!confirmPassword) {
      newErrors.confirmPassword = 'Confirm Password is required';
    } else if (confirmPassword !== password) {
      newErrors.confirmPassword = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0; // Return true if no errors
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      // Add sign-up logic here
      alert('Account created successfully!');
      navigate('/login'); // Redirect to login page
    }
  };

  return (
    <div className="sign-up-page">
      <form className="sign-up-form" onSubmit={handleSubmit}>
        <h2>Sign Up</h2>

        {/* Name Input */}
        <div className="input-group">
          <label htmlFor="name">Name</label>
          <input
            type="text"
            id="name"
            placeholder="Enter your Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          {errors.name && <span className="error">{errors.name}</span>}
        </div>

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

        {/* Confirm Password Input */}
        <div className="input-group">
          <label htmlFor="confirm-password">Confirm Password</label>
          <input
            type="password"
            id="confirm-password"
            placeholder="Confirm your Password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
          {errors.confirmPassword && (
            <span className="error">{errors.confirmPassword}</span>
          )}
        </div>

        {/* Submit Button */}
        <button type="submit" className="submit-button">
          Sign Up
        </button>

        {/* Back to Login */}
        <p className="back-to-login">
          Already have an account?{' '}
          <button
            type="button"
            className="back-to-login-link"
            onClick={() => navigate('/login')}
          >
            Login
          </button>
        </p>
      </form>
    </div>
  );
};

export default SignUp;