import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import logoImage from '../../assets/BlueV.png';
import './ForgotPassword.css';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [isSuccess, setIsSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!email.trim()) {
      setMessage('Please enter your email address');
      setIsSuccess(false);
      return;
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setMessage('Please enter a valid email address');
      setIsSuccess(false);
      return;
    }

    setIsLoading(true);
    setMessage('');

    try {
      const response = await fetch('/api/auth/forgot-password/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setIsSuccess(true);
        setMessage('Password reset instructions have been sent to your email address. Please check your inbox and follow the instructions to reset your password.');
      } else if (response.status === 404 || (data.message && data.message.includes('not found'))) {
        setIsSuccess(false);
        setMessage('Email not registered. Please contact an admin for assistance.');
      } else {
        setIsSuccess(false);
        setMessage(data.message || 'Failed to send password reset email. Please try again.');
      }
    } catch (error) {
      console.error('Forgot password error:', error);
      setIsSuccess(false);
      setMessage('An error occurred while sending the password reset email. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>Reset Your Password</h1>
          <p>Enter your email address and we'll send you instructions to reset your password.</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email address"
              className="form-control"
              disabled={isLoading}
              required
            />
          </div>

          {message && (
            <div className={`alert ${isSuccess ? 'alert-success' : 'alert-error'}`}>
              {message}
            </div>
          )}

          <button 
            type="submit" 
            className="btn btn-primary btn-full"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <i className="fas fa-spinner fa-spin"></i>
                Sending...
              </>
            ) : (
              <>
                <i className="fas fa-envelope"></i>
                Send Reset Instructions
              </>
            )}
          </button>
        </form>

        <div className="auth-footer">
          <div className="auth-links">
            <Link to="/login" className="auth-link">
              <i className="fas fa-arrow-left"></i>
              Back to Login
            </Link>
            <Link to="/register" className="auth-link">
              Don't have an account? Contact a Admin
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;