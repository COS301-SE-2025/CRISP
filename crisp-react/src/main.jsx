import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom/client'
import CRISPApp from './App.jsx'
import CrispLogin from './crisp_login.jsx'
import './index.css'

function AuthWrapper() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true); // Add loading state
  
  // Check if user is already authenticated on app load
  useEffect(() => {
    const validateSession = () => {
      try {
        const token = localStorage.getItem('crisp_auth_token');
        const userStr = localStorage.getItem('crisp_user');
        
        // Check if both token and user data exist
        if (token && userStr) {
          const userData = JSON.parse(userStr);
          
          // Basic validation - check if token is not expired (optional)
          // For demo purposes, we'll check if the token was created within last 24 hours
          const tokenTimestamp = parseInt(token.split('_').pop());
          const currentTime = Date.now();
          const twentyFourHours = 24 * 60 * 60 * 1000;
          
          if (currentTime - tokenTimestamp < twentyFourHours && userData.username) {
            console.log('Valid session found, auto-logging in user:', userData.username);
            setIsAuthenticated(true);
          } else {
            console.log('Session expired or invalid, clearing storage');
            // Clear expired/invalid session
            localStorage.removeItem('crisp_auth_token');
            localStorage.removeItem('crisp_user');
            setIsAuthenticated(false);
          }
        } else {
          console.log('No valid session found');
          setIsAuthenticated(false);
        }
      } catch (error) {
        console.error('Error validating session:', error);
        // Clear corrupted session data
        localStorage.removeItem('crisp_auth_token');
        localStorage.removeItem('crisp_user');
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    };

    // Small delay to show that authentication is being checked
    setTimeout(validateSession, 500);
  }, []);
  
  // Callback for when login is successful
  const handleLoginSuccess = (userData) => {
    console.log('Login successful for user:', userData.user.username);
    
    try {
      // Store authentication data
      localStorage.setItem('crisp_auth_token', userData.token);
      localStorage.setItem('crisp_user', JSON.stringify(userData.user));
      
      // Set authenticated state
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Error storing authentication data:', error);
      alert('Login error: Unable to store session data');
    }
  };
  
  // Function to handle logout (can be called from anywhere in the app)
  const handleLogout = () => {
    console.log('Logging out user');
    localStorage.removeItem('crisp_auth_token');
    localStorage.removeItem('crisp_user');
    setIsAuthenticated(false);
  };

  // Show loading screen while checking authentication
  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        flexDirection: 'column',
        gap: '20px',
        fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif'
      }}>
        <div style={{
          width: '40px',
          height: '40px',
          border: '4px solid #f3f3f3',
          borderTop: '4px solid #0056b3',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }}></div>
        <p style={{ color: '#718096', fontSize: '16px' }}>Checking authentication...</p>
        <style>
          {`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `}
        </style>
      </div>
    );
  }
  
  // Render login screen or main app based on authentication status
  if (!isAuthenticated) {
    console.log('User not authenticated, showing login screen');
    return <CrispLogin onLoginSuccess={handleLoginSuccess} />;
  }
  
  console.log('User authenticated, showing main application');
  return <CRISPApp onLogout={handleLogout} />;
}

// Additional security: Clear any existing sessions on page unload
window.addEventListener('beforeunload', () => {
  // Optional: You can uncomment this if you want sessions to expire when browser closes
  // localStorage.removeItem('crisp_auth_token');
  // localStorage.removeItem('crisp_user');
});

// Prevent back button bypass after logout
window.addEventListener('popstate', () => {
  const token = localStorage.getItem('crisp_auth_token');
  if (!token) {
    window.location.reload();
  }
});

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AuthWrapper />
  </React.StrictMode>,
)