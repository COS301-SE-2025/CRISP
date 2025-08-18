// Fixed version of main.jsx with proper authentication and admin routing
import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import App from "./App.jsx";
import RegisterUser from "./RegisterUser.jsx";
import CrispLogin from "./crisp_login.jsx";
import LandingPage from "./LandingPage.jsx";
import Construction from "./construction.jsx";
import ForgotPassword from "./components/ForgotPassword.jsx";
import ResetPassword from "./components/ResetPassword.jsx";
import "./assets/index_ut.css";
import "./assets/trust-management.css";

// Import Font Awesome
import "@fortawesome/fontawesome-free/css/all.min.css";

function AuthRoutes() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [userData, setUserData] = useState(null);
  const navigate = useNavigate();

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
        console.error("Error validating session:", error);
        // Clear invalid data
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
      // Store authentication data
      localStorage.setItem("crisp_auth_token", authData.tokens.access);
      localStorage.setItem("crisp_refresh_token", authData.tokens.refresh);
      localStorage.setItem("crisp_user", JSON.stringify(authData.user));

      // Set authenticated state and user data
      setUserData(authData.user);
      setIsAuthenticated(true);
      
      // Redirect to dashboard
      navigate('/dashboard', { replace: true });
    } catch (error) {
      console.error("Error storing authentication data:", error);
      alert("Login error: Unable to store session data");
    }
  };

  // Callback for when registration is successful
  const handleRegisterSuccess = (authData) => {
    try {
      // Store authentication data
      localStorage.setItem("crisp_auth_token", authData.tokens.access);
      localStorage.setItem("crisp_refresh_token", authData.tokens.refresh);
      localStorage.setItem("crisp_user", JSON.stringify(authData.user));

      // Set authenticated state and user data
      setUserData(authData.user);
      setIsAuthenticated(true);
    } catch (error) {
      console.error("Error storing authentication data:", error);
      alert("Registration error: Unable to store session data");
    }
  };

  // Function to handle logout
  const handleLogout = () => {
    localStorage.removeItem("crisp_auth_token");
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
    <Routes>
        {/* Landing page route - accessible to everyone */}
        <Route
          path="/"
          element={<LandingPage />}
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
                  alert("User registered successfully!");
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
              <App user={userData} onLogout={handleLogout} isAdmin={isAdmin} />
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
                <App user={userData} onLogout={handleLogout} isAdmin={isAdmin} />
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
                <App user={userData} onLogout={handleLogout} isAdmin={isAdmin} />
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
  );
}

// Prevent back button bypass after logout
window.addEventListener("popstate", () => {
  const token = localStorage.getItem("crisp_auth_token");
  if (!token) {
    window.location.reload();
  }
});

function AuthWrapper() {
  return (
    <Router basename="/static/react" future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AuthRoutes />
    </Router>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <AuthWrapper />
  </React.StrictMode>
);