import React, { useState, useEffect } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import logoImage from '../assets/BlueV2.png';

const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    newPassword: '',
    confirmPassword: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [isSuccess, setIsSuccess] = useState(false);
  const [isValidToken, setIsValidToken] = useState(null);
  
  const token = searchParams.get('token');

  useEffect(() => {
    // Validate token on component mount
    if (!token) {
      setIsValidToken(false);
      setMessage('Invalid or missing reset token. Please request a new password reset.');
      return;
    }
    
    validateToken();
  }, [token]);

  const validateToken = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/validate-reset-token/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token }),
      });

      const data = await response.json();
      
      if (response.ok && data.success) {
        setIsValidToken(true);
      } else {
        setIsValidToken(false);
        setMessage(data.message || 'Invalid or expired reset token. Please request a new password reset.');
      }
    } catch (error) {
      console.error('Token validation error:', error);
      setIsValidToken(false);
      setMessage('Failed to validate reset token. Please try again.');
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear messages when user starts typing
    if (message && !isSuccess) {
      setMessage('');
    }
  };

  const validatePassword = (password) => {
    if (password.length < 8) {
      return 'Password must be at least 8 characters long';
    }
    if (!/(?=.*[a-z])/.test(password)) {
      return 'Password must contain at least one lowercase letter';
    }
    if (!/(?=.*[A-Z])/.test(password)) {
      return 'Password must contain at least one uppercase letter';
    }
    if (!/(?=.*\d)/.test(password)) {
      return 'Password must contain at least one number';
    }
    if (!/(?=.*[@$!%*?&])/.test(password)) {
      return 'Password must contain at least one special character (@$!%*?&)';
    }
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.newPassword || !formData.confirmPassword) {
      setMessage('Please fill in all fields');
      setIsSuccess(false);
      return;
    }

    // Validate password strength
    const passwordError = validatePassword(formData.newPassword);
    if (passwordError) {
      setMessage(passwordError);
      setIsSuccess(false);
      return;
    }

    if (formData.newPassword !== formData.confirmPassword) {
      setMessage('Passwords do not match');
      setIsSuccess(false);
      return;
    }

    setIsLoading(true);
    setMessage('');

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/reset-password/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token,
          new_password: formData.newPassword,
        }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setIsSuccess(true);
        setMessage('Your password has been successfully reset! You can now log in with your new password.');
        
        // Redirect to login after 3 seconds
        setTimeout(() => {
          navigate('/login');
        }, 3000);
      } else {
        setIsSuccess(false);
        setMessage(data.message || 'Failed to reset password. Please try again.');
      }
    } catch (error) {
      console.error('Password reset error:', error);
      setIsSuccess(false);
      setMessage('An error occurred while resetting your password. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  if (isValidToken === null) {
    // Still validating token
    return (
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <img src={logoImage} alt="CRISP Logo" className="auth-logo" />
            <h1>Validating Reset Token</h1>
            <div className="loading-spinner">
              <i className="fas fa-spinner fa-spin"></i>
              <p>Please wait while we validate your reset token...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (isValidToken === false) {
    // Invalid token
    return (
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <img src={logoImage} alt="CRISP Logo" className="auth-logo" />
            <h1>Invalid Reset Token</h1>
          </div>
          
          <div className="alert alert-error">
            {message}
          </div>

          <div className="auth-footer">
            <div className="auth-links">
              <Link to="/forgot-password" className="auth-link">
                <i className="fas fa-envelope"></i>
                Request New Reset Link
              </Link>
              <Link to="/login" className="auth-link">
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
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <img src={logoImage} alt="CRISP Logo" className="auth-logo" />
          <h1>Reset Your Password</h1>
          <p>Enter your new password below. Make sure it's strong and secure.</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="newPassword">New Password</label>
            <input
              type="password"
              id="newPassword"
              name="newPassword"
              value={formData.newPassword}
              onChange={handleInputChange}
              placeholder="Enter your new password"
              className="form-control"
              disabled={isLoading}
              required
            />
            <div className="password-requirements">
              <p>Password must contain:</p>
              <ul>
                <li className={formData.newPassword.length >= 8 ? 'met' : ''}>
                  At least 8 characters
                </li>
                <li className={/(?=.*[a-z])/.test(formData.newPassword) ? 'met' : ''}>
                  One lowercase letter
                </li>
                <li className={/(?=.*[A-Z])/.test(formData.newPassword) ? 'met' : ''}>
                  One uppercase letter
                </li>
                <li className={/(?=.*\d)/.test(formData.newPassword) ? 'met' : ''}>
                  One number
                </li>
                <li className={/(?=.*[@$!%*?&])/.test(formData.newPassword) ? 'met' : ''}>
                  One special character (@$!%*?&)
                </li>
              </ul>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm New Password</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleInputChange}
              placeholder="Confirm your new password"
              className="form-control"
              disabled={isLoading}
              required
            />
            {formData.confirmPassword && formData.newPassword !== formData.confirmPassword && (
              <div className="password-mismatch">
                <i className="fas fa-exclamation-triangle"></i>
                Passwords do not match
              </div>
            )}
          </div>

          {message && (
            <div className={`alert ${isSuccess ? 'alert-success' : 'alert-error'}`}>
              {message}
              {isSuccess && (
                <div className="redirect-notice">
                  <i className="fas fa-info-circle"></i>
                  Redirecting to login page in 3 seconds...
                </div>
              )}
            </div>
          )}

          <button 
            type="submit" 
            className="btn btn-primary btn-full"
            disabled={isLoading || formData.newPassword !== formData.confirmPassword}
          >
            {isLoading ? (
              <>
                <i className="fas fa-spinner fa-spin"></i>
                Resetting Password...
              </>
            ) : (
              <>
                <i className="fas fa-key"></i>
                Reset Password
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
          </div>
        </div>
      </div>

      <style>{`
        .auth-container {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          padding: 2rem;
        }

        .auth-card {
          background: white;
          border-radius: 12px;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
          padding: 3rem;
          width: 100%;
          max-width: 500px;
        }

        .auth-header {
          text-align: center;
          margin-bottom: 2rem;
        }

        .auth-logo {
          height: 60px;
          margin-bottom: 1.5rem;
        }

        .auth-header h1 {
          color: #2d3748;
          font-size: 1.8rem;
          font-weight: 600;
          margin-bottom: 0.5rem;
        }

        .auth-header p {
          color: #718096;
          font-size: 0.95rem;
          line-height: 1.5;
        }

        .loading-spinner {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 1rem;
          padding: 2rem;
        }

        .loading-spinner i {
          font-size: 2rem;
          color: #667eea;
        }

        .loading-spinner p {
          color: #718096;
          margin: 0;
        }

        .auth-form {
          margin-bottom: 2rem;
        }

        .form-group {
          margin-bottom: 1.5rem;
        }

        .form-group label {
          display: block;
          color: #4a5568;
          font-weight: 500;
          margin-bottom: 0.5rem;
        }

        .form-control {
          width: 100%;
          padding: 0.75rem 1rem;
          border: 2px solid #e2e8f0;
          border-radius: 8px;
          font-size: 1rem;
          transition: border-color 0.2s, box-shadow 0.2s;
        }

        .form-control:focus {
          outline: none;
          border-color: #667eea;
          box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .form-control:disabled {
          background-color: #f7fafc;
          cursor: not-allowed;
        }

        .password-requirements {
          margin-top: 0.75rem;
          padding: 1rem;
          background-color: #f7fafc;
          border-radius: 6px;
          font-size: 0.85rem;
        }

        .password-requirements p {
          margin: 0 0 0.5rem 0;
          color: #4a5568;
          font-weight: 500;
        }

        .password-requirements ul {
          margin: 0;
          padding-left: 1.25rem;
          list-style: none;
        }

        .password-requirements li {
          margin-bottom: 0.25rem;
          color: #718096;
          position: relative;
        }

        .password-requirements li::before {
          content: '✗';
          position: absolute;
          left: -1.25rem;
          color: #e53e3e;
          font-weight: bold;
        }

        .password-requirements li.met {
          color: #38a169;
        }

        .password-requirements li.met::before {
          content: '✓';
          color: #38a169;
        }

        .password-mismatch {
          margin-top: 0.5rem;
          color: #e53e3e;
          font-size: 0.85rem;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .alert {
          padding: 1rem;
          border-radius: 8px;
          margin-bottom: 1.5rem;
          font-size: 0.9rem;
          line-height: 1.4;
        }

        .alert-success {
          background-color: #f0fff4;
          border: 1px solid #9ae6b4;
          color: #22543d;
        }

        .alert-error {
          background-color: #fed7d7;
          border: 1px solid #fc8181;
          color: #742a2a;
        }

        .redirect-notice {
          margin-top: 0.75rem;
          padding-top: 0.75rem;
          border-top: 1px solid #9ae6b4;
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.85rem;
        }

        .btn {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 8px;
          font-size: 1rem;
          font-weight: 500;
          text-decoration: none;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-primary {
          background: linear-gradient(135deg, #667eea, #764ba2);
          color: white;
        }

        .btn-primary:hover:not(:disabled) {
          transform: translateY(-1px);
          box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }

        .btn-primary:disabled {
          opacity: 0.6;
          cursor: not-allowed;
          transform: none;
        }

        .btn-full {
          width: 100%;
        }

        .auth-footer {
          text-align: center;
        }

        .auth-links {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .auth-link {
          color: #667eea;
          text-decoration: none;
          font-size: 0.9rem;
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          justify-content: center;
          transition: color 0.2s;
        }

        .auth-link:hover {
          color: #5a67d8;
          text-decoration: underline;
        }

        @media (max-width: 480px) {
          .auth-card {
            padding: 2rem 1.5rem;
          }
          
          .auth-header h1 {
            font-size: 1.5rem;
          }
        }
      `}</style>
    </div>
  );
};

export default ResetPassword;