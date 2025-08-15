import React, { useEffect, useRef } from 'react';
import { useNotifications } from './NotificationManager';
import * as api from '../api';

const NotificationWatcher = ({ user }) => {
  const { showSuccess, showError, showWarning, showInfo } = useNotifications();
  const intervalRef = useRef(null);
  const lastCheckRef = useRef(new Date());

  useEffect(() => {
    if (!user) return;

    // Function to check for new notifications
    const checkForNewNotifications = async () => {
      try {
        const alerts = await api.getAlerts();
        
        if (alerts.data && Array.isArray(alerts.data)) {
          // Filter for new alerts since last check
          const newAlerts = alerts.data.filter(alert => {
            const alertTime = new Date(alert.timestamp || alert.created_at);
            return alertTime > lastCheckRef.current && !alert.read;
          });

          // Show notifications for new alerts
          newAlerts.forEach(alert => {
            const title = alert.title || 'New Alert';
            const message = alert.message || alert.description || 'You have received a new notification';
            
            switch (alert.type || alert.priority) {
              case 'critical':
              case 'high':
                showError(title, message, { autoCloseDelay: 10000 });
                break;
              case 'warning':
              case 'medium':
                showWarning(title, message);
                break;
              case 'success':
                showSuccess(title, message);
                break;
              default:
                showInfo(title, message);
                break;
            }
          });

          // Update last check time
          lastCheckRef.current = new Date();
        }
      } catch (error) {
        // Silently fail - don't spam user with connection errors
        console.warn('Failed to check for new notifications:', error);
      }
    };

    // Check immediately on mount
    checkForNewNotifications();

    // Set up polling interval (every 30 seconds)
    intervalRef.current = setInterval(checkForNewNotifications, 30000);

    // Cleanup interval on unmount or user change
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [user, showSuccess, showError, showWarning, showInfo]);

  // This component doesn't render anything
  return null;
};

export default NotificationWatcher;