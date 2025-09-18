import React, { useState, useEffect, useRef, useCallback } from 'react';
import './SessionTimeout.css';

const SessionTimeout = ({ 
  isAuthenticated, 
  onLogout, 
  timeoutMinutes = 10,
  warningMinutes = 2 
}) => {
  const [showWarning, setShowWarning] = useState(false);
  const [remainingTime, setRemainingTime] = useState(warningMinutes * 60);
  const [isActive, setIsActive] = useState(true);
  
  const timeoutRef = useRef(null);
  const warningTimeoutRef = useRef(null);
  const countdownRef = useRef(null);
  const lastActivityRef = useRef(Date.now());

  // Events that indicate user activity
  const activityEvents = [
    'mousedown',
    'mousemove', 
    'keypress',
    'scroll',
    'touchstart',
    'click',
    'focus'
  ];

  // Reset the inactivity timer
  const resetTimer = useCallback(() => {
    if (!isAuthenticated) return;

    lastActivityRef.current = Date.now();
    setIsActive(true);
    setShowWarning(false);

    // Clear existing timers
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    if (warningTimeoutRef.current) {
      clearTimeout(warningTimeoutRef.current);
    }
    if (countdownRef.current) {
      clearInterval(countdownRef.current);
    }

    // Set warning timer (show popup 2 minutes before logout)
    const warningTime = (timeoutMinutes - warningMinutes) * 60 * 1000;
    warningTimeoutRef.current = setTimeout(() => {
      setShowWarning(true);
      setRemainingTime(warningMinutes * 60);
      
      // Start countdown
      countdownRef.current = setInterval(() => {
        setRemainingTime(prev => {
          if (prev <= 1) {
            handleLogout();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }, warningTime);

    // Set final logout timer
    timeoutRef.current = setTimeout(() => {
      handleLogout();
    }, timeoutMinutes * 60 * 1000);
  }, [isAuthenticated, timeoutMinutes, warningMinutes]);

  // Handle logout
  const handleLogout = useCallback(() => {
    setShowWarning(false);
    setIsActive(false);
    
    // Clear all timers
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    if (warningTimeoutRef.current) clearTimeout(warningTimeoutRef.current);
    if (countdownRef.current) clearInterval(countdownRef.current);
    
    // Call the logout function passed from parent
    onLogout();
  }, [onLogout]);

  // Handle "Stay Logged In" button
  const handleStayLoggedIn = useCallback(() => {
    resetTimer();
  }, [resetTimer]);

  // Activity event handler
  const handleActivity = useCallback(() => {
    if (!isAuthenticated) return;
    
    const now = Date.now();
    const timeSinceLastActivity = now - lastActivityRef.current;
    
    // Only reset if it's been more than 1 second since last activity
    // This prevents excessive timer resets from rapid events
    if (timeSinceLastActivity > 1000) {
      resetTimer();
    }
  }, [isAuthenticated, resetTimer]);

  // Set up activity listeners
  useEffect(() => {
    if (!isAuthenticated) {
      // Clear timers if not authenticated
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      if (warningTimeoutRef.current) clearTimeout(warningTimeoutRef.current);
      if (countdownRef.current) clearInterval(countdownRef.current);
      setShowWarning(false);
      return;
    }

    // Add event listeners for user activity
    activityEvents.forEach(event => {
      document.addEventListener(event, handleActivity, true);
    });

    // Start the timer
    resetTimer();

    // Cleanup function
    return () => {
      activityEvents.forEach(event => {
        document.removeEventListener(event, handleActivity, true);
      });
      
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      if (warningTimeoutRef.current) clearTimeout(warningTimeoutRef.current);
      if (countdownRef.current) clearInterval(countdownRef.current);
    };
  }, [isAuthenticated, handleActivity, resetTimer]);

  // Format time display
  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  // Don't render anything if not authenticated or warning not shown
  if (!isAuthenticated || !showWarning) {
    return null;
  }

  return (
    <div className="session-timeout-overlay">
      <div className="session-timeout-modal">
        <div className="session-timeout-icon">⚠️</div>
        
        <h2 className="session-timeout-title">
          Session Timeout Warning
        </h2>

        <p className="session-timeout-message">
          You've been inactive for a while. Your session will automatically log out in:
        </p>

        <div className={`session-timeout-countdown ${remainingTime <= 30 ? 'critical' : ''}`}>
          {formatTime(remainingTime)}
        </div>

        <div className="session-timeout-buttons">
          <button
            className="session-timeout-btn session-timeout-btn-primary"
            onClick={handleStayLoggedIn}
          >
            Yes, Keep Me Logged In
          </button>

          <button
            className="session-timeout-btn session-timeout-btn-danger"
            onClick={handleLogout}
          >
            Logout Now
          </button>
        </div>

        <p className="session-timeout-info">
          Any activity will keep you logged in and reset this timer.
        </p>
      </div>
    </div>
  );
};

export default SessionTimeout;