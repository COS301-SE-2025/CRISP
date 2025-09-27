import React, { useState, useEffect } from 'react';
import RippleGrid from './RippleGrid';

function CrispLogin({ onLoginSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const API_BASE_URL = 'http://localhost:8000';

  // Login API function
  const loginUser = async (username, password) => {
    const response = await fetch(`${API_BASE_URL}/api/auth/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username,
        password: password,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || errorData.message || 'Login failed');
    }

    return await response.json();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    
    try {
      const userData = await loginUser(username, password);
      
      onLoginSuccess({
        user: userData.user,
        token: userData.tokens.access
      });
    } catch (error) {
      setError(error.message || 'Invalid username or password');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <style>
        {`
          * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
          }
          
          html, body {
            height: 100%;
            width: 100%;
            overflow-x: hidden;
          }
          
          body {
            background-color: #f5f7fa;
            color: #2d3748;
            min-height: 100vh;
          }
          
          .login-page {
            min-height: 100vh;
            height: 100vh;
            display: flex;
            align-items: stretch;
            background-color: #f5f7fa;
            overflow: hidden;
          }
          
          .login-content {
            display: flex;
            width: 100vw;
            height: 100vh;
            overflow: hidden;
          }
          
          .login-left {
            flex: 3;
            background: linear-gradient(135deg, #0056b3 0%, #00a0e9 100%);
            color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 3rem;
            position: relative;
            overflow: hidden;
          }
          
          /* Disabled old background - replaced with RippleGrid */
          /*
          .login-left::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA4MDAgODAwIiBwcmVzZXJ2ZUFzcGVjdFJhdGlvPSJub25lIj48ZyBmaWxsPSJub25lIiBzdHJva2U9IiNmZmYiIG9wYWNpdHk9IjAuMSIgc3Ryb2tlLXdpZHRoPSIxLjUiPjxjaXJjbGUgcj0iMTAwIiBjeD0iNDAwIiBjeT0iNDAwIi8+PGNpcmNsZSByPSIyMDAiIGN4PSI0MDAiIGN5PSI0MDAiLz48Y2lyY2xlIHI9IjMwMCIgY3g9IjQwMCIgY3k9IjQwMCIvPjxjaXJjbGUgcj0iNDAwIiBjeD0iNDAwIiBjeT0iNDAwIi8+PC9nPjxnIGZpbGw9Im5vbmUiIHN0cm9rZT0iI2ZmZiIgb3BhY2l0eT0iMC4yIiBzdHJva2Utd2lkdGg9IjEiPjxwYXRoIGQ9Ik0yMDAgMjAwIEw2MDAgNjAwIE0yMDAgNjAwIEw2MDAgMjAwIE0zMDAgMTAwIEwzMDAgNzAwIE01MDAgMTAwIEw1MDAgNzAwIE0xMDAgMzAwIEw3MDAgMzAwIE0xMDAgNTAwIEw3MDAgNTAwIi8+PC9nPjxnIGZpbGw9IiNmZmYiIG9wYWNpdHk9IjAuMiI+PGNpcmNsZSByPSIzIiBjeD0iMjAwIiBjeT0iMjAwIi8+PGNpcmNsZSByPSIzIiBjeD0iNDAwIiBjeT0iMjAwIi8+PGNpcmNsZSByPSIzIiBjeD0iNjAwIiBjeT0iMjAwIi8+PGNpcmNsZSByPSIzIiBjeD0iMjAwIiBjeT0iNDAwIi8+PGNpcmNsZSByPSIzIiBjeD0iNDAwIiBjeT0iNDAwIi8+PGNpcmNsZSByPSIzIiBjeD0iNjAwIiBjeT0iNDAwIi8+PGNpcmNsZSByPSIzIiBjeD0iMjAwIiBjeT0iNjAwIi8+PGNpcmNsZSByPSIzIiBjeD0iNDAwIiBjeT0iNjAwIi8+PGNpcmNsZSByPSIzIiBjeD0iNjAwIiBjeT0iNjAwIi8+PC9nPjxnIGZpbGw9Im5vbmUiIHN0cm9rZT0iI2ZmZiIgb3BhY2l0eT0iMC4xIiBzdHJva2Utd2lkdGg9IjEiPjxwYXRoIGQ9Ik0zMDAgMzAwIEw1MDAgNTAwIE0zMDAgNTAwIEw1MDAgMzAwIi8+PC9nPjwvc3ZnPg=='), url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNDAgMjQwIj48ZGVmcz48cGF0dGVybiBpZD0ic21hbGwtZ3JpZCIgd2lkdGg9IjEwIiBoZWlnaHQ9IjEwIiBwYXR0ZXJuVW5pdHM9InVzZXJTcGFjZU9uVXNlIj48cmVjdCB3aWR0aD0iMTAiIGhlaWdodD0iMTAiIGZpbGw9Im5vbmUiLz48cGF0aCBkPSJNIDEwIDAgTCAwIDAgTCAwIDEwIiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmYiIHN0cm9rZS13aWR0aD0iMC41IiBvcGFjaXR5PSIwLjEiLz48L3BhdHRlcm4+PC9kZWZzPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjc21hbGwtZ3JpZCkiLz48L3N2Zz4=');
            background-blend-mode: overlay;
            opacity: 0.3;
          }
          */
          
          .brand-info {
            position: relative;
            z-index: 2;
            max-width: 700px;
            margin: 0 auto;
          }
          
          .logo-container {
            margin-bottom: 1.5rem;
            text-align: center;
          }
          
          .brand-logo {
            font-size: 4rem;
            color: #ffffff;
            margin-bottom: 1rem;
          }
          
          .brand-info h2 {
            font-size: 1.8rem;
            font-weight: 500;
            margin-bottom: 1.5rem;
            opacity: 0.9;
            text-align: center;
          }
          
          .brand-info p {
            font-size: 1.1rem;
            margin-bottom: 3rem;
            opacity: 0.8;
            line-height: 1.6;
            text-align: center;
          }
          
          .feature-list {
            margin-top: 3rem;
          }
          
          .feature-item {
            display: flex;
            align-items: center;
            margin-bottom: 1.5rem;
          }
          
          .feature-icon {
            background-color: rgba(255, 255, 255, 0.2);
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 1rem;
          }
          
          .feature-icon i {
            font-size: 24px;
          }
          
          .feature-text h3 {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 0.3rem;
          }
          
          .feature-text p {
            font-size: 0.95rem;
            opacity: 0.8;
            margin: 0;
          }
          
          .login-right {
            flex: 1;
            background-color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: center;
            min-width: 320px;
            max-width: 400px;
            box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
            position: relative;
            z-index: 2;
          }
          
          .login-form-container {
            width: 100%;
            max-width: 300px;
            padding: 1.5rem;
            position: relative;
          }
          
          .login-form-container h2 {
            font-size: 1.75rem;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 0.5rem;
          }
          
          .subtitle {
            color: #718096;
            margin-bottom: 2rem;
          }
          
          .form-group {
            margin-bottom: 1.5rem;
          }
          
          .form-group label {
            display: block;
            font-weight: 500;
            margin-bottom: 0.5rem;
            color: #2d3748;
          }
          
          .input-with-icon {
            position: relative;
          }
          
          .input-with-icon i {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: #718096;
            font-size: 16px;
          }
          
          .input-with-icon input {
            width: 100%;
            padding: 0.8rem 1rem 0.8rem 2.8rem;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            font-size: 1rem;
            background-color: #f5f7fa;
            transition: all 0.3s;
            color: #000000;
          }
          
          .input-with-icon input:focus {
            outline: none;
            border-color: #0056b3;
            background-color: #ffffff;
            box-shadow: 0 0 0 3px rgba(0, 86, 179, 0.1);
            color: #000000;
          }
          
          .btn-sign-in {
            width: 100%;
            padding: 0.8rem;
            background-color: #0056b3;
            color: #ffffff;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 1rem;
          }
          
          .btn-sign-in:hover {
            background-color: #003366;
          }
          
          .btn-sign-in:disabled {
            opacity: 0.7;
            cursor: not-allowed;
          }
          
          .login-footer {
            margin-top: 2rem;
            text-align: center;
            color: #718096;
            font-size: 0.9rem;
          }
          
          .error-message {
            background-color: rgba(229, 62, 62, 0.1);
            color: #e53e3e;
            padding: 0.8rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.9rem;
          }
          
          .error-message i {
            font-size: 16px;
            flex-shrink: 0;
          }
          
          .loading-spinner {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
          }
          
          .spinner {
            width: 50px;
            height: 50px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #0056b3;
            border-radius: 50%;
            animation: spin 1s linear infinite;
          }
          
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }

          /* RippleGrid Background Effect */
          .ripple-grid-bg {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1;
            /* DEBUG: Add visible background to check positioning */
            /* background: rgba(255, 0, 0, 0.1); */
          }

          .brand-info {
            position: relative;
            z-index: 2;
            max-width: 700px;
            margin: 0 auto;
          }
          
          /* Responsive Design */
          @media (max-width: 992px) {
            .login-content {
              flex-direction: column;
              height: auto;
              overflow: visible;
            }
            
            .login-page {
              height: auto;
              overflow: visible;
            }
            
            .login-left, .login-right {
              flex: none;
              width: 100%;
              min-width: unset;
              max-width: unset;
            }
            
            .login-left {
              padding: 2rem;
              min-height: 300px;
              justify-content: center;
            }
            
            .login-right {
              box-shadow: none;
              border-top: 1px solid #e2e8f0;
            }
            
            .login-form-container {
              padding: 2rem;
              max-width: 400px;
            }
          }
        `}
      </style>
      
      {isLoading && (
        <div className="loading-spinner">
          <div className="spinner"></div>
        </div>
      )}
      
      <div className="login-page">
        <div className="login-content">
          <div className="login-left">
            <div className="ripple-grid-bg">
              <RippleGrid
                gridColor="#ffffff"
                rippleIntensity={0.1}
                gridSize={30}
                gridThickness={20}
                fadeDistance={2.0}
                vignetteStrength={1.0}
                glowIntensity={0.3}
                opacity={0.8}
                mouseInteraction={true}
                mouseInteractionRadius={1.0}
              />
            </div>

            {/* Temporary fallback - animated CSS grid lines */}
            <div className="css-grid-fallback"></div>
            <div className="brand-info">
              <div className="logo-container">
                <i className="fas fa-shield-alt brand-logo"></i>
              </div>
              <h2>Cyber Risk Information Sharing Platform</h2>
              <p>Streamline your threat intelligence sharing and committee management</p>
              
              <div className="feature-list">
                <div className="feature-item">
                  <div className="feature-icon">
                    <i className="fas fa-shield"></i>
                  </div>
                  <div className="feature-text">
                    <h3>Monitor Threats</h3>
                    <p>Track and analyze security threats across institutions</p>
                  </div>
                </div>
                
                <div className="feature-item">
                  <div className="feature-icon">
                    <i className="fas fa-sync"></i>
                  </div>
                  <div className="feature-text">
                    <h3>Share Intelligence</h3>
                    <p>Securely exchange threat data with trusted partners</p>
                  </div>
                </div>
                
                <div className="feature-item">
                  <div className="feature-icon">
                    <i className="fas fa-chart-line"></i>
                  </div>
                  <div className="feature-text">
                    <h3>Analyze Patterns</h3>
                    <p>Identify emerging threat patterns with advanced analytics</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="login-right">
            <div className="login-form-container">
              <h2>Welcome Back</h2>
              <p className="subtitle">Sign in to your account</p>
              
              {error && (
                <div className="error-message">
                  <i className="fas fa-exclamation-circle"></i> 
                  {error}
                </div>
              )}
              
              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label htmlFor="username">Email</label>
                  <div className="input-with-icon">
                    <i className="fas fa-envelope"></i>
                    <input 
                      type="text" 
                      id="username" 
                      value={username} 
                      onChange={(e) => setUsername(e.target.value)} 
                      placeholder="username@example.com"
                      required
                    />
                  </div>
                </div>
                
                <div className="form-group">
                  <label htmlFor="password">Password</label>
                  <div className="input-with-icon">
                    <i className="fas fa-lock"></i>
                    <input 
                      type="password" 
                      id="password" 
                      value={password} 
                      onChange={(e) => setPassword(e.target.value)} 
                      placeholder="••••••••"
                      required
                    />
                  </div>
                </div>
                
                <button 
                  type="submit"
                  className="btn-sign-in" 
                  disabled={isLoading}
                >
                  {isLoading ? 'Signing in...' : 'Sign In'}
                </button>
              </form>
              
              <div className="login-footer">
                <p>Don't have an account? Contact your administrator for access.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default CrispLogin;