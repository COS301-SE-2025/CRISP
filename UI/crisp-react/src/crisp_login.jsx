import React, { useState, useEffect } from 'react';
import { loginUser } from './api.js'; // Import the API function
import BlueVLogo from './assets/BlueV.png';
import CrispHelp from './crisp_help.jsx'; // Import the help component
import Construction from './construction.jsx'; // Import construction component

// Login Component that works with the AuthWrapper in main.jsx
function CrispLogin({ onLoginSuccess, switchView }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isHelpOpen, setIsHelpOpen] = useState(false); // State for help modal
  const [showConstruction, setShowConstruction] = useState(false); // State for construction page

  // Initialize Feather icons when component mounts
  useEffect(() => {
    // Load Feather icons script if not already loaded
    if (!window.feather) {
      const script = document.createElement('script');
      script.src = 'https://cdnjs.cloudflare.com/ajax/libs/feather-icons/4.29.0/feather.min.js';
      script.onload = () => {
        if (window.feather) {
          window.feather.replace();
        }
      };
      document.head.appendChild(script);
    } else {
      // If already loaded, just replace the icons
      window.feather.replace();
    }
  }, []);

  // Re-run feather.replace() when error state changes to ensure new icons are rendered
  useEffect(() => {
    if (window.feather) {
      setTimeout(() => window.feather.replace(), 100);
    }
  }, [error, isLoading, isHelpOpen]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    
    try {
      // Call the API function
      const userData = await loginUser(username, password);
      
      // Call the onLoginSuccess callback with user data
      onLoginSuccess({
        user: userData.user,
        token: userData.token
      });
    } catch (error) {
      setError(error.message || 'Invalid username or password');
    } finally {
      setIsLoading(false);
    }
  };

  const openHelp = () => {
    setIsHelpOpen(true);
  };

  const closeHelp = () => {
    setIsHelpOpen(false);
  };

  // Handle navigation from help component
  const handleNavigate = (page, context) => {
    console.log(`Navigate to ${page} from login page with context:`, context);
    
    // Close help modal first
    closeHelp();
    
    if (page === 'construction') {
      // Option 1: Use parent component routing if available
      if (switchView && typeof switchView === 'function') {
        switchView('Construction');
      } 
      // Option 2: Show construction component directly
      else {
        setShowConstruction(true);
      }
    }
  };

  // If construction page should be shown, render it instead of login
  if (showConstruction) {
    return <Construction />;
  }

  return (
    <>
      <CSSStyles />
      <div className="login-page">
        <div className="login-content">
          <div className="login-left">
            <div className="brand-info">
              <div className="logo-container">
                <img src={BlueVLogo} alt="BlueV Logo" className="brand-logo" />
              </div>
              <h2>Cyber Risk Information Sharing Platform</h2>
              <p>Streamline your threat intelligence sharing and committee management</p>
              
              <div className="feature-list">
                <div className="feature-item">
                  <div className="feature-icon"><i data-feather="shield"></i></div>
                  <div className="feature-text">
                    <h3>Monitor Threats</h3>
                    <p>Track and analyze security threats across institutions</p>
                  </div>
                </div>
                
                <div className="feature-item">
                  <div className="feature-icon"><i data-feather="repeat"></i></div>
                  <div className="feature-text">
                    <h3>Share Intelligence</h3>
                    <p>Securely exchange threat data with trusted partners</p>
                  </div>
                </div>
                
                <div className="feature-item">
                  <div className="feature-icon"><i data-feather="trending-up"></i></div>
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
              {/* Help button in top right corner */}
              <div className="login-header">
                <button 
                  className="help-button" 
                  onClick={openHelp}
                  title="Help & Support"
                  type="button"
                >
                  <i data-feather="help-circle"></i>
                </button>
              </div>

              <h2>Welcome Back</h2>
              <p className="subtitle">Sign in to your account</p>
              
              {error && <div className="error-message"><i data-feather="alert-circle"></i> {error}</div>}
              
              <div className="form-group">
                <label htmlFor="username">Email</label>
                <div className="input-with-icon">
                  <i data-feather="mail"></i>
                  <input 
                    type="text" 
                    id="username" 
                    value={username} 
                    onChange={(e) => setUsername(e.target.value)} 
                    placeholder="username@example.com"
                    onKeyPress={(e) => e.key === 'Enter' && handleSubmit(e)}
                  />
                </div>
              </div>
              
              <div className="form-group">
                <label htmlFor="password">Password</label>
                <div className="input-with-icon">
                  <i data-feather="lock"></i>
                  <input 
                    type="password" 
                    id="password" 
                    value={password} 
                    onChange={(e) => setPassword(e.target.value)} 
                    placeholder="••••••••"
                    onKeyPress={(e) => e.key === 'Enter' && handleSubmit(e)}
                  />
                </div>
              </div>
              
              <button 
                className="btn-sign-in" 
                onClick={handleSubmit}
                disabled={isLoading}
              >
                {isLoading ? 'Signing in...' : 'Sign In'}
              </button>
              
              <div className="login-footer">
                <p>Don't have an account? Contact <a href="#" className="register-link">BlueVision ITM</a> for account registration.</p>
                <div className="footer-links">
                  <button 
                    className="help-link" 
                    onClick={openHelp}
                    type="button"
                  >
                    <i data-feather="help-circle"></i>
                    Need Help?
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Help Modal - Now with navigation support */}
      <CrispHelp 
        isOpen={isHelpOpen} 
        onClose={closeHelp} 
        onNavigate={handleNavigate}
      />
    </>
  );
}

// CSS Styles for Login (with help button styles added)
function CSSStyles() {
  return (
    <style>
      {`
        :root {
            --primary-color: #0056b3;
            --primary-dark: #003366;
            --primary-light: #007bff;
            --accent-color: #00a0e9;
            --text-light: #ffffff;
            --text-dark: #2d3748;
            --text-muted: #718096;
            --danger: #e53e3e;
            --success: #38a169;
            --warning: #f6ad55;
            --info: #4299e1;
            --bg-light: #f5f7fa;
            --bg-medium: #e2e8f0;
            --bg-dark: #1a202c;
        }
        
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
            background-color: var(--bg-light);
            color: var(--text-dark);
            min-height: 100vh;
        }
        
        /* Global Feather icon styling */
        i[data-feather] {
            stroke: currentColor;
            stroke-width: 2;
            stroke-linecap: round;
            stroke-linejoin: round;
            fill: none;
        }
        
        /* Login Styles */
        .login-page {
            min-height: 100vh;
            height: 100vh;
            display: flex;
            align-items: stretch;
            background-color: var(--bg-light);
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
            color: var(--text-light);
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 3rem;
            position: relative;
            overflow: hidden;
        }
        
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
        
        /* Logo container styles */
        .logo-container {
            margin-bottom: 1.5rem;
        }
        
        .brand-logo {
            max-width: 250px;
            height: auto;
        }
        
        .brand-info {
            position: relative;
            z-index: 2;
            max-width: 700px;
            margin: 0 auto;
        }
        
        .brand-info h2 {
            font-size: 1.8rem;
            font-weight: 500;
            margin-bottom: 1.5rem;
            opacity: 0.9;
        }
        
        .brand-info p {
            font-size: 1.1rem;
            margin-bottom: 3rem;
            opacity: 0.8;
            line-height: 1.6;
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
            width: 24px;
            height: 24px;
            stroke-width: 2;
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
            background-color: var(--text-light);
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

        /* Login Header with Help Button */
        .login-header {
            display: flex;
            justify-content: flex-end;
            margin-bottom: 1rem;
        }

        .help-button {
            background: var(--bg-light);
            border: 1px solid var(--bg-medium);
            border-radius: 50%;
            width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            color: var(--primary-color);
            transition: all 0.2s ease;
            font-size: 0;
        }

        .help-button:hover {
            background: var(--primary-color);
            color: var(--text-light);
            transform: scale(1.05);
        }

        .help-button i {
            width: 18px;
            height: 18px;
        }
        
        .login-form-container h2 {
            font-size: 1.75rem;
            font-weight: 600;
            color: var(--text-dark);
            margin-bottom: 0.5rem;
        }
        
        .subtitle {
            color: var(--text-muted);
            margin-bottom: 2rem;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-group label {
            display: block;
            font-weight: 500;
            margin-bottom: 0.5rem;
            color: var(--text-dark);
        }
        
        .input-with-icon {
            position: relative;
        }
        
        .input-with-icon i {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
            width: 16px;
            height: 16px;
        }
        
        .input-with-icon input {
            width: 100%;
            padding: 0.8rem 1rem 0.8rem 2.8rem;
            border: 1px solid var(--bg-medium);
            border-radius: 8px;
            font-size: 1rem;
            background-color: var(--bg-light);
            transition: all 0.3s;
            color: #000000;
        }
        
        .input-with-icon input:focus {
            outline: none;
            border-color: var(--primary-color);
            background-color: var(--text-light);
            box-shadow: 0 0 0 3px rgba(0, 86, 179, 0.1);
            color: #000000;
        }
        
        .btn-sign-in {
            width: 100%;
            padding: 0.8rem;
            background-color: var(--primary-color);
            color: var(--text-light);
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 1rem;
        }
        
        .btn-sign-in:hover {
            background-color: var(--primary-dark);
        }
        
        .btn-sign-in:disabled {
            opacity: 0.7;
            cursor: not-allowed;
        }
        
        .login-footer {
            margin-top: 2rem;
            text-align: center;
            color: var(--text-muted);
            font-size: 0.9rem;
        }

        .footer-links {
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid var(--bg-medium);
        }

        .help-link {
            background: none;
            border: none;
            color: var(--primary-color);
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s ease;
        }

        .help-link:hover {
            color: var(--primary-dark);
            text-decoration: underline;
        }

        .help-link i {
            width: 14px;
            height: 14px;
        }
        
        .demo-credentials {
            margin-top: 1rem;
            padding: 0.75rem;
            background-color: var(--bg-light);
            border-radius: 6px;
            border: 1px solid var(--bg-medium);
        }
        
        .demo-credentials p {
            margin: 0.2rem 0;
            font-size: 0.8rem;
        }
        
        .register-link {
            color: var(--primary-color);
            text-decoration: none;
            font-weight: 600;
        }
        
        .register-link:hover {
            text-decoration: underline;
        }
        
        .error-message {
            background-color: rgba(229, 62, 62, 0.1);
            color: var(--danger);
            padding: 0.8rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.9rem;
        }
        
        .error-message i {
            width: 16px;
            height: 16px;
            flex-shrink: 0;
        }
        
        /* Responsive Design */
        @media (max-width: 1400px) {
            .login-left {
                flex: 2.5;
                justify-content: center;
            }
            
            .login-right {
                flex: 1;
                min-width: 300px;
                max-width: 350px;
            }
            
            .brand-info {
                max-width: 600px;
            }
        }
        
        @media (max-width: 1200px) {
            .login-left {
                flex: 2;
                justify-content: center;
            }
            
            .login-right {
                flex: 1;
                min-width: 280px;
                max-width: 320px;
            }
            
            .brand-info {
                max-width: 500px;
            }
            
            .login-form-container {
                max-width: 280px;
                padding: 1.25rem;
            }
        }
        
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
                border-top: 1px solid var(--bg-medium);
            }
            
            .login-form-container {
                padding: 2rem;
                max-width: 400px;
            }
        }
        
        @media (max-width: 768px) {
            .brand-logo {
                max-width: 200px;
            }
            
            .brand-info h2 {
                font-size: 1.3rem;
            }
            
            .brand-info p {
                font-size: 1rem;
            }
            
            .login-form-container {
                padding: 1.5rem;
            }
        }
        
        @media (max-width: 576px) {
            .login-left {
                padding: 1.5rem;
            }
            
            .brand-logo {
                max-width: 180px;
            }
            
            .brand-info h2 {
                font-size: 1.1rem;
            }
            
            .feature-icon {
                width: 40px;
                height: 40px;
                font-size: 1.2rem;
            }
            
            .feature-text h3 {
                font-size: 1rem;
            }
            
            .feature-text p {
                font-size: 0.85rem;
            }
        }
      `}
    </style>
  );
}

export default CrispLogin;