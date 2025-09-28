// Fixed version of main.jsx with proper authentication and admin routing
import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import CRISPApp from "./App.jsx";
import RegisterUser from "./RegisterUser.jsx";
import CrispLogin from "./crisp_login.jsx";
import LandingPage from "./LandingPage.jsx";
import Construction from "./construction.jsx";
import ForgotPassword from "./components/enhanced/ForgotPassword.jsx";
import ResetPassword from "./components/ResetPassword.jsx";
import SessionTimeout from "./components/enhanced/SessionTimeout.jsx";
import { NotificationProvider, useNotifications } from "./components/enhanced/NotificationManager.jsx";
import NotificationWatcher from "./components/enhanced/NotificationWatcher.jsx";
import "./assets/index_ut.css";
import "./assets/trust-management.css";
import "./assets/enhanced/notifications.css";

// Import Font Awesome
import "@fortawesome/fontawesome-free/css/all.min.css";

// Wrapper component to ensure props are passed correctly
function AppWrapper({ user, onLogout, isAdmin }) {
  return <CRISPApp user={user} onLogout={onLogout} isAdmin={isAdmin} />;
}

function AuthRoutesWithNotifications() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [userData, setUserData] = useState(null);
  const navigate = useNavigate();
  const { showSuccess, showError } = useNotifications();
  

  // Check if user is already authenticated on app load
  useEffect(() => {
    const validateSession = () => {
      try {
        const token = localStorage.getItem("crisp_auth_token");
        const userStr = localStorage.getItem("crisp_user");

        if (token && userStr) {
          const userObj = JSON.parse(userStr);
          setUserData(userObj);
          setIsAuthenticated(true);
        }
      } catch (error) {
        // Continue with login page if validation fails
        localStorage.removeItem("crisp_auth_token");
        localStorage.removeItem("crisp_user");
      } finally {
        setIsLoading(false);
      }
    };

    validateSession();
  }, []);

  // Callback for when login is successful
  const handleLoginSuccess = (authData) => {
    try {
      // Store authentication data (using both keys for compatibility)
      localStorage.setItem("crisp_auth_token", authData.tokens.access);
      localStorage.setItem("access_token", authData.tokens.access);
      localStorage.setItem("crisp_refresh_token", authData.tokens.refresh);
      localStorage.setItem("crisp_user", JSON.stringify(authData.user));

      // Set authenticated state and user data
      setUserData(authData.user);
      setIsAuthenticated(true);
      
      // Redirect to dashboard
      navigate('/dashboard', { replace: true });
    } catch (error) {
      showError('Login Error', 'Unable to store session data');
    }
  };

  // Callback for when registration is successful
  const handleRegisterSuccess = (authData) => {
    try {
      // Store authentication data (using both keys for compatibility)
      localStorage.setItem("crisp_auth_token", authData.tokens.access);
      localStorage.setItem("access_token", authData.tokens.access);
      localStorage.setItem("crisp_refresh_token", authData.tokens.refresh);
      localStorage.setItem("crisp_user", JSON.stringify(authData.user));

      // Set authenticated state and user data
      setUserData(authData.user);
      setIsAuthenticated(true);
    } catch (error) {
      showError('Registration Error', 'Unable to store session data');
    }
  };

  // Function to handle logout
  const handleLogout = () => {
    localStorage.removeItem("crisp_auth_token");
    localStorage.removeItem("access_token");
    localStorage.removeItem("crisp_refresh_token");
    localStorage.removeItem("crisp_user");
    setIsAuthenticated(false);
    setUserData(null);
    // Redirect to landing page
    navigate('/', { replace: true });
  };

  // Show loading screen while checking authentication
  if (isLoading) {
    return (
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
          flexDirection: "column",
          gap: "20px",
          fontFamily: "Segoe UI, Tahoma, Geneva, Verdana, sans-serif",
        }}
      >
        <div
          style={{
            width: "40px",
            height: "40px",
            border: "4px solid #f3f3f3",
            borderTop: "4px solid #0056b3",
            borderRadius: "50%",
            animation: "spin 1s linear infinite",
          }}
        ></div>
        <p style={{ color: "#718096", fontSize: "16px" }}>
          Checking authentication...
        </p>
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

  // Check if user is admin - robust detection with multiple fallbacks
  const isAdmin = userData && (
    // Primary admin flags
    userData.is_admin === true ||
    userData.is_staff === true ||
    // Role-based detection (case-insensitive)
    (userData.role && [
      'admin', 'administrator', 'bluevisionadmin', 'superuser', 'super_user'
    ].includes(userData.role.toLowerCase())) ||
    // Legacy role check for backwards compatibility
    (userData.role && userData.role.toLowerCase().includes('admin'))
  );



  return (
    <NotificationProvider>
      {/* PERFORMANCE RESTORED: SessionTimeout and NotificationWatcher re-enabled */}
      {isAuthenticated && (
        <SessionTimeout
          isAuthenticated={isAuthenticated}
          onLogout={handleLogout}
          timeoutMinutes={10}
          warningMinutes={2}
        />
      )}

      {isAuthenticated && userData && (
        <NotificationWatcher user={userData} />
      )}
      <Routes>
        {/* Landing page route - redirect to dashboard if authenticated */}
        <Route
          path="/"
          element={
            isAuthenticated ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <LandingPage />
            )
          }
        />

        {/* Construction page route - accessible to everyone */}
        <Route
          path="/construction"
          element={<Construction />}
        />

        {/* Login route - only accessible when not authenticated */}
        <Route
          path="/login"
          element={
            !isAuthenticated ? (
              <CrispLogin onLoginSuccess={handleLoginSuccess} />
            ) : (
              <Navigate to="/dashboard" replace />
            )
          }
        />

        {/* Forgot Password route - only accessible when not authenticated */}
        <Route
          path="/forgot-password"
          element={
            !isAuthenticated ? (
              <ForgotPassword />
            ) : (
              <Navigate to="/dashboard" replace />
            )
          }
        />

        {/* Reset Password route - only accessible when not authenticated */}
        <Route
          path="/reset-password"
          element={
            !isAuthenticated ? (
              <ResetPassword />
            ) : (
              <Navigate to="/dashboard" replace />
            )
          }
        />

        {/* Register user route - accessible by admins or unauthenticated users */}
        <Route
          path="/register-user"
          element={
            !isAuthenticated ? (
              <RegisterUser 
                onRegisterSuccess={handleRegisterSuccess}
                switchView={() => navigate('/login')}
              />
            ) : isAdmin ? (
              <RegisterUser 
                onRegisterSuccess={() => {
                  showSuccess('Registration Successful', 'User registered successfully!');
                  navigate('/dashboard');
                }}
                switchView={() => navigate('/dashboard')}
              />
            ) : (
              <Navigate to="/dashboard" replace />
            )
          }
        />

        {/* Main dashboard route */}
        <Route
          path="/dashboard"
          element={
            isAuthenticated ? (
              <AppWrapper user={userData} onLogout={handleLogout} isAdmin={isAdmin} />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        {/* User Management route - Admin only */}
        <Route
          path="/user-management"
          element={
            isAuthenticated ? (
              isAdmin ? (
                <AppWrapper user={userData} onLogout={handleLogout} isAdmin={isAdmin} />
              ) : (
                <Navigate to="/dashboard" replace />
              )
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        {/* Trust Management route - Publisher and Admin access */}
        <Route
          path="/trust-management"
          element={
            isAuthenticated ? (
              (userData?.role === 'publisher' || userData?.role === 'BlueVisionAdmin' || isAdmin) ? (
                <AppWrapper user={userData} onLogout={handleLogout} isAdmin={isAdmin} />
              ) : (
                <Navigate to="/dashboard" replace />
              )
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        {/* Asset Management route - Publisher and Admin access (WOW Factor #1) */}
        <Route
          path="/assets"
          element={
            isAuthenticated ? (
              (userData?.role === 'publisher' || userData?.role === 'BlueVisionAdmin' || isAdmin) ? (
                <AppWrapper user={userData} onLogout={handleLogout} isAdmin={isAdmin} />
              ) : (
                <Navigate to="/dashboard" replace />
              )
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        {/* Asset Alerts route - Publisher and Admin access (WOW Factor #1) */}
        <Route
          path="/asset-alerts"
          element={
            isAuthenticated ? (
              (userData?.role === 'publisher' || userData?.role === 'BlueVisionAdmin' || isAdmin) ? (
                <AppWrapper user={userData} onLogout={handleLogout} isAdmin={isAdmin} />
              ) : (
                <Navigate to="/dashboard" replace />
              )
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        {/* Catch all route */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </NotificationProvider>
  );
}

// Prevent back button bypass after logout
window.addEventListener("popstate", () => {
  const token = localStorage.getItem("crisp_auth_token");
  if (!token) {
    window.location.reload();
  }
});

function AuthRoutes() {
  return (
    <NotificationProvider>
      <AuthRoutesWithNotifications />
    </NotificationProvider>
  );
}

function AuthWrapper() {
  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AuthRoutes />
    </Router>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <AuthWrapper />
  </React.StrictMode>
);