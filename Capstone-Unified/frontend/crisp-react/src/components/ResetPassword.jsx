import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import logoImage from '../assets/BlueV.png';
import './ResetPassword.css';

function ResetPassword() {
  const [searchParams] = useSearchParams();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [token, setToken] = useState('');
  const [tokenValid, setTokenValid] = useState(null);
  const [passwordStrength, setPasswordStrength] = useState('');

  // Extract token from URL on component mount
  useEffect(() => {
    const urlToken = searchParams.get('token');
    if (urlToken) {
      setToken(urlToken);
      // Optionally validate token with backend
      validateToken(urlToken);
    } else {
      setError('Invalid or missing reset token. Please request a new password reset.');
      setTokenValid(false);
    }
  }, [searchParams]);

  const validateToken = async (token) => {
    try {
      // For now, just assume token is valid if it exists
      // We'll validate it during the actual password reset
      if (token && token.length > 10) {
        setTokenValid(true);
      } else {
        setError('Invalid reset token format.');
        setTokenValid(false);
      }
    } catch (error) {
      console.error('Token validation error:', error);
      setError('Unable to validate reset token. Please try again.');
      setTokenValid(false);
    }
  };

  const checkPasswordStrength = (password) => {
    if (password.length < 6) return 'weak';
    if (password.length < 8) return 'fair';
    if (password.length >= 8 && /[A-Z]/.test(password) && /[0-9]/.test(password)) return 'strong';
    if (password.length >= 8 && (/[A-Z]/.test(password) || /[0-9]/.test(password))) return 'good';
    return 'fair';
  };

  const handlePasswordChange = (e) => {
    const newPassword = e.target.value;
    setPassword(newPassword);
    setPasswordStrength(checkPasswordStrength(newPassword));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    // Validation
    if (!token) {
      setError('Invalid reset token');
      setIsLoading(false);
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters long');
      setIsLoading(false);
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch('/api/auth/reset-password/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token: token,
          new_password: password
        }),
      });

      const data = await response.json();
      
      if (response.ok && data.success) {
        setIsSubmitted(true);
      } else {
        setError(data.message || 'Failed to reset password. Please try again.');
      }
    } catch (error) {
      console.error('Password reset error:', error);
      setError('An error occurred while resetting your password. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Show loading while validating token
  if (tokenValid === null) {
    return (
      <div className="reset-container">
        <div className="reset-card">
          <div className="reset-header">
            <img src={logoImage} alt="CRISP Logo" className="reset-logo" />
            <h1>Validating Reset Token</h1>
            <p>Please wait while we validate your reset link...</p>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div className="loading-spinner"></div>
          </div>
        </div>
      </div>
    );
  }

  // Show error if token is invalid
  if (tokenValid === false) {
    return (
      <div className="reset-container">
        <div className="reset-card">
          <div className="reset-header">
            <img src={logoImage} alt="CRISP Logo" className="reset-logo" />
            <h1>Invalid Reset Link</h1>
            <p>This password reset link is invalid or has expired.</p>
          </div>
          
          {error && (
            <div className="alert alert-error">
              {error}
            </div>
          )}

          <div className="reset-footer">
            <div className="reset-links">
              <Link to="/forgot-password" className="reset-link">
                <i className="fas fa-envelope"></i>
                Request New Reset Link
              </Link>
              <Link to="/login" className="reset-link">
                <i className="fas fa-arrow-left"></i>
                Back to Login
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="reset-container">
      <div className="reset-card">
        <div className="reset-header">
          <img src={logoImage} alt="CRISP Logo" className="reset-logo" />
          <h1>{isSubmitted ? 'Password Reset Complete' : 'Reset Your Password'}</h1>
          <p>
            {isSubmitted 
              ? 'Your password has been successfully updated.' 
              : 'Please enter your new password below.'
            }
          </p>
        </div>

        {!isSubmitted ? (
          <>
            {error && (
              <div className="alert alert-error">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="reset-form">
              <div className="form-group">
                <label htmlFor="password">New Password</label>
                <input
                  type="password"
                  id="password"
                  value={password}
                  onChange={handlePasswordChange}
                  className="form-control"
                  placeholder="Enter your new password"
                  disabled={isLoading}
                  required
                />
                
                {password && (
                  <div className="password-strength">
                    <div className={`strength-bar strength-${passwordStrength}`}></div>
                    <span style={{ color: passwordStrength === 'strong' ? '#2e7d32' : '#5d4e75' }}>
                      Password strength: {passwordStrength}
                    </span>
                  </div>
                )}

                <div className="password-requirements">
                  <strong>Password Requirements:</strong>
                  <ul>
                    <li>At least 6 characters long</li>
                    <li>Include uppercase and numbers for stronger security</li>
                    <li>Avoid common words or personal information</li>
                  </ul>
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="confirmPassword">Confirm New Password</label>
                <input
                  type="password"
                  id="confirmPassword"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="form-control"
                  placeholder="Confirm your new password"
                  disabled={isLoading}
                  required
                />
              </div>

              <button 
                type="submit" 
                className="btn btn-primary btn-full"
                disabled={isLoading || !password || !confirmPassword}
              >
                {isLoading ? (
                  <>
                    <div className="loading-spinner"></div>
                    Updating Password...
                  </>
                ) : (
                  <>
                    <i className="fas fa-lock"></i>
                    Update My Password
                  </>
                )}
              </button>
            </form>
          </>
        ) : (
          <>
            <div style={{ textAlign: 'center' }}>
              <div className="success-icon">
                <i className="fas fa-check-circle"></i>
              </div>
            </div>

            <div className="alert alert-success">
              <strong>Success!</strong> Your password has been successfully reset. You can now log in with your new password.
            </div>

            <div className="reset-footer">
              <div className="reset-links">
                <Link to="/login" className="reset-link">
                  <i className="fas fa-sign-in-alt"></i>
                  Continue to Login
                </Link>
              </div>
            </div>
          </>
        )}

        {!isSubmitted && (
          <div className="reset-footer">
            <div className="reset-links">
              <Link to="/login" className="reset-link">
                <i className="fas fa-arrow-left"></i>
                Back to Login
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ResetPassword;