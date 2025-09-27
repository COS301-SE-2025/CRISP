import React, { useEffect, useRef } from 'react';
import { useNotifications } from './NotificationManager';
import * as api from '../../api';

const NotificationWatcher = ({ user }) => {
  const { showSuccess, showError, showWarning, showInfo } = useNotifications();
  const intervalRef = useRef(null);
  const lastCheckRef = useRef(new Date());

  useEffect(() => {
    if (!user) return;

    // Request browser notification permission
    const requestNotificationPermission = async () => {
      if ('Notification' in window && Notification.permission === 'default') {
        try {
          const permission = await Notification.requestPermission();
          console.log('🔔 Browser notification permission:', permission);
        } catch (error) {
          console.warn('Failed to request notification permission:', error);
        }
      }
    };

    requestNotificationPermission();

    // Function to check for new notifications
    const checkForNewNotifications = async () => {
      try {
        // Get only unread notifications from API
        const alerts = await api.getAlerts({ unread_only: 'true' });
        
        if (alerts.success && alerts.data && Array.isArray(alerts.data)) {
          // Filter for new alerts since last check
          const newAlerts = alerts.data.filter(alert => {
            const alertTime = new Date(alert.created_at);
            return alertTime > lastCheckRef.current && !alert.is_read;
          });

          // Show notifications for new alerts
          newAlerts.forEach(alert => {
            const title = alert.title || 'New Alert';
            const message = alert.message || 'You have received a new notification';
            
            // Trigger browser notification if permission granted
            if (Notification.permission === 'granted') {
              new Notification(title, {
                body: message,
                icon: '/favicon.ico',
                tag: alert.id // Prevent duplicate notifications
              });
            }
            
            // Show in-app toast notification
            const alertType = alert.type || alert.notification_type;
            const priority = alert.priority || alert.severity;

            // Special handling for asset-based alerts
            if (alertType === 'asset_based_alert') {
              const assetMessage = `Asset Security Alert: ${message}`;

              switch (priority) {
                case 'critical':
                  showError(`🔴 ${title}`, assetMessage, { autoCloseDelay: 15000 });
                  break;
                case 'high':
                  showError(`🟠 ${title}`, assetMessage, { autoCloseDelay: 12000 });
                  break;
                case 'medium':
                  showWarning(`🟡 ${title}`, assetMessage, { autoCloseDelay: 10000 });
                  break;
                case 'low':
                  showInfo(`🟢 ${title}`, assetMessage, { autoCloseDelay: 8000 });
                  break;
                default:
                  showWarning(`🛡️ ${title}`, assetMessage, { autoCloseDelay: 10000 });
                  break;
              }
            } else {
              // Standard notification handling
              switch (priority) {
                case 'critical':
                  showError(title, message, { autoCloseDelay: 12000 });
                  break;
                case 'high':
                  showError(title, message, { autoCloseDelay: 10000 });
                  break;
                case 'medium':
                  showWarning(title, message, { autoCloseDelay: 8000 });
                  break;
                case 'low':
                  showInfo(title, message, { autoCloseDelay: 6000 });
                  break;
                case 'success':
                  showSuccess(title, message);
                  break;
                default:
                  showInfo(title, message);
                  break;
              }
            }
          });

          // Update last check time only if we found new alerts
          if (newAlerts.length > 0) {
            lastCheckRef.current = new Date();
            console.log(`🔔 Displayed ${newAlerts.length} new notifications`);
          }
        }
      } catch (error) {
        // Silently fail - don't spam user with connection errors
        console.warn('Failed to check for new notifications:', error);
      }
    };

    // Check immediately on mount
    checkForNewNotifications();

    // Set up polling interval (every 2 minutes to reduce server load)
    intervalRef.current = setInterval(checkForNewNotifications, 120000);

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