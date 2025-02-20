import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './ForgotPassword.css';

const ForgotPassword: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [errors, setErrors] = useState<{ email?: string }>({});

  const validateForm = () => {
    const newErrors: { email?: string } = {};

    // Email validation
    if (!email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Email is invalid';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0; // Return true if no errors
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      // Add logic to send a password reset email
      alert('Password reset link sent to your email.');
      navigate('/login'); // Redirect to login page
    }
  };

  return (
    <div className="forgot-password-page">
      <form className="forgot-password-form" onSubmit={handleSubmit}>
        <h2>Forgot Password</h2>
        <p>Enter your email address to reset your password.</p>

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

        {/* Submit Button */}
        <button type="submit" className="submit-button">
          Send Reset Link
        </button>

        {/* Back to Login */}
        <p className="back-to-login">
          Remember your password?{' '}
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

export default ForgotPassword;