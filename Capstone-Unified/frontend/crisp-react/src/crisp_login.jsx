import React, { useState, useEffect } from 'react';
import { loginUser } from './api.js'; // Import the API function
import BlueVLogo from './assets/BlueV.png';
import CrispHelp from './crisp_help.jsx'; // Import the help component
import Construction from './construction.jsx'; // Import construction component
import ChangePassword from './components/ChangePassword.jsx'; // Import change password component
import LoadingSpinner from './components/LoadingSpinner.jsx'; // Import loading spinner
import { useNotifications } from './components/enhanced/NotificationManager.jsx';
import './crisp_login.css'; // Import CSS styles

// Login Component that works with the AuthWrapper in main.jsx
function CrispLogin({ onLoginSuccess, switchView }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isHelpOpen, setIsHelpOpen] = useState(false); // State for help modal
  const { showSuccess } = useNotifications();
  const [showConstruction, setShowConstruction] = useState(false); // State for construction page
  const [showChangePassword, setShowChangePassword] = useState(false); // State for change password modal

  // Removed Feather icons loading to fix CSP violations
  // Icons are now handled using inline SVG or CSS classes

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    
    try {
      // Add delay to show loading spinner
      await new Promise(resolve => setTimeout(resolve, 1000));
      // Call the API function
      const userData = await loginUser(username, password);
      
      // Call the onLoginSuccess callback with user data
      onLoginSuccess(userData);
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

  const openChangePassword = () => {
    setShowChangePassword(true);
  };

  const closeChangePassword = () => {
    setShowChangePassword(false);
  };

  const handlePasswordChanged = () => {
    setError('');
    showSuccess('Password Changed', 'Password changed successfully! You can now log in with your new password.');
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
      {isLoading && <LoadingSpinner fullscreen={true} />}
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
                <p>Don't have an account? Contact <a href="https://bitm.co.za/" className="register-link">BlueVision ITM</a> for account registration.</p>
                <div className="footer-links">
                  <button 
                    className="help-link" 
                    onClick={openHelp}
                    type="button"
                  >
                    <i data-feather="help-circle"></i>
                    Need Help?
                  </button>
                  <button 
                    className="help-link" 
                    onClick={openChangePassword}
                    type="button"
                  >
                    <i data-feather="lock"></i>
                    Change Password
                  </button>
                  <a href="/forgot-password" className="help-link">
                    <i data-feather="key"></i>
                    Forgot Password?
                  </a>
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

      {/* Change Password Modal */}
      <ChangePassword 
        isOpen={showChangePassword}
        onClose={closeChangePassword}
        onPasswordChanged={handlePasswordChanged}
      />
    </>
  );
}

export default CrispLogin;