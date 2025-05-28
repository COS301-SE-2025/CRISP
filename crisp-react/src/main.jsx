// Fixed version of main.jsx with proper authentication and admin routing
import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import App from "./App.jsx";
import AppRegister from "./AppRegister.jsx";
import RegisterUser from "./RegisterUser.jsx";
import CrispLogin from "./crisp_login.jsx";
import "./index.css";

// Import Font Awesome
import "@fortawesome/fontawesome-free/css/all.min.css";

function AuthWrapper() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [userData, setUserData] = useState(null);

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
          console.log("Session validated for user:", userObj.username);
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
    console.log("Login successful for user:", authData.user.username);

    try {
      // Store authentication data
      localStorage.setItem("crisp_auth_token", authData.token);
      localStorage.setItem("crisp_user", JSON.stringify(authData.user));

      // Set authenticated state and user data
      setUserData(authData.user);
      setIsAuthenticated(true);
    } catch (error) {
      console.error("Error storing authentication data:", error);
      alert("Login error: Unable to store session data");
    }
  };

  // Callback for when registration is successful
  const handleRegisterSuccess = (authData) => {
    console.log("Registration successful for user:", authData.user.username);

    try {
      // Store authentication data
      localStorage.setItem("crisp_auth_token", authData.token);
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
    console.log("Logging out user");
    localStorage.removeItem("crisp_auth_token");
    localStorage.removeItem("crisp_user");
    setIsAuthenticated(false);
    setUserData(null);
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

  // Check if user is admin
  const isAdmin = userData &&
    (userData.is_admin === true ||
      userData.is_staff === true ||
      (userData.role && userData.role.toLowerCase() === "admin") ||
      (userData.role && userData.role.toLowerCase() === "administrator"));

  console.log("Auth state:", { isAuthenticated, isAdmin, userData });

  return (
    <Router>
      <Routes>
        {/* Login route - only accessible when not authenticated */}
        <Route
          path="/login"
          element={
            !isAuthenticated ? (
              <CrispLogin onLoginSuccess={handleLoginSuccess} />
            ) : (
              <Navigate to="/" replace />
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
                switchView={() => window.location.href = '/login'}
              />
            ) : isAdmin ? (
              <RegisterUser 
                onRegisterSuccess={() => {
                  alert("User registered successfully!");
                  window.location.href = '/';
                }}
                switchView={() => window.location.href = '/'}
              />
            ) : (
              <Navigate to="/" replace />
            )
          }
        />

        {/* Main dashboard route */}
        <Route
          path="/"
          element={
            isAuthenticated ? (
              isAdmin ? (
                <AppRegister user={userData} onLogout={handleLogout} />
              ) : (
                <App user={userData} onLogout={handleLogout} />
              )
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        {/* Catch all route */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

// Prevent back button bypass after logout
window.addEventListener("popstate", () => {
  const token = localStorage.getItem("crisp_auth_token");
  if (!token) {
    window.location.reload();
  }
});

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <AuthWrapper />
  </React.StrictMode>
);