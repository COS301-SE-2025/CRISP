import React, { useState, useEffect } from 'react';

const NotificationToast = ({ notification, onClose, autoCloseDelay = 5000 }) => {
  const [isVisible, setIsVisible] = useState(true);
  const [isClosing, setIsClosing] = useState(false);

  useEffect(() => {
    if (autoCloseDelay > 0) {
      const timer = setTimeout(() => {
        handleClose();
      }, autoCloseDelay);

      return () => clearTimeout(timer);
    }
  }, [autoCloseDelay]);

  const handleClose = () => {
    setIsClosing(true);
    setTimeout(() => {
      setIsVisible(false);
      onClose && onClose();
    }, 300); // Animation duration
  };

  if (!isVisible || !notification) return null;

  const getToastClass = (type) => {
    const baseClass = `notification-toast ${isClosing ? 'closing' : 'entering'}`;
    switch (type) {
      case 'success':
        return `${baseClass} toast-success`;
      case 'error':
        return `${baseClass} toast-error`;
      case 'warning':
        return `${baseClass} toast-warning`;
      case 'info':
        return `${baseClass} toast-info`;
      default:
        return `${baseClass} toast-info`;
    }
  };

  const getIcon = (type) => {
    switch (type) {
      case 'success':
        return 'fas fa-check-circle';
      case 'error':
        return 'fas fa-exclamation-triangle';
      case 'warning':
        return 'fas fa-exclamation-circle';
      case 'info':
        return 'fas fa-info-circle';
      default:
        return 'fas fa-bell';
    }
  };

  return (
    <div className={getToastClass(notification.type)}>
      <div className="toast-icon">
        <i className={getIcon(notification.type)}></i>
      </div>
      <div className="toast-content">
        <div className="toast-title">{notification.title}</div>
        {notification.message && (
          <div className="toast-message">{notification.message}</div>
        )}
      </div>
      <button className="toast-close" onClick={handleClose}>
        <i className="fas fa-times"></i>
      </button>
    </div>
  );
};

export default NotificationToast;