import React, { useState, useEffect } from 'react';

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchNotifications();
  }, [filter]);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      // Simulated API call - replace with actual endpoint
      const mockNotifications = [
        {
          id: '1',
          type: 'threat_alert',
          title: 'New High-Priority Threat Detected',
          message: 'A new malware strain has been identified in your organization\'s threat feed.',
          severity: 'high',
          read: false,
          created_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
          source: 'Threat Intelligence'
        },
        {
          id: '2',
          type: 'trust_request',
          title: 'Trust Relationship Request',
          message: 'Organization "CyberSecure Inc." has requested a bilateral trust relationship.',
          severity: 'medium',
          read: false,
          created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          source: 'Trust Management'
        },
        {
          id: '3',
          type: 'feed_update',
          title: 'Threat Feed Updated',
          message: 'Your subscribed threat feed "MITRE ATT&CK" has been updated with 15 new indicators.',
          severity: 'low',
          read: true,
          created_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
          source: 'Feed Management'
        },
        {
          id: '4',
          type: 'system',
          title: 'System Maintenance Scheduled',
          message: 'Scheduled maintenance window on Sunday 2 AM - 4 AM UTC.',
          severity: 'medium',
          read: true,
          created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
          source: 'System'
        }
      ];

      let filteredNotifications = mockNotifications;
      if (filter !== 'all') {
        filteredNotifications = mockNotifications.filter(n => {
          if (filter === 'unread') return !n.read;
          if (filter === 'read') return n.read;
          return n.type === filter;
        });
      }

      setNotifications(filteredNotifications);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      // Simulated API call
      setNotifications(prev =>
        prev.map(n =>
          n.id === notificationId ? { ...n, read: true } : n
        )
      );
    } catch (err) {
      setError('Failed to mark notification as read');
    }
  };

  const markAllAsRead = async () => {
    try {
      // Simulated API call
      setNotifications(prev =>
        prev.map(n => ({ ...n, read: true }))
      );
    } catch (err) {
      setError('Failed to mark all notifications as read');
    }
  };

  const deleteNotification = async (notificationId) => {
    try {
      // Simulated API call
      setNotifications(prev =>
        prev.filter(n => n.id !== notificationId)
      );
    } catch (err) {
      setError('Failed to delete notification');
    }
  };

  const getNotificationIcon = (type) => {
    const icons = {
      threat_alert: 'fas fa-exclamation-triangle',
      trust_request: 'fas fa-handshake',
      feed_update: 'fas fa-rss',
      system: 'fas fa-cog',
      user_invitation: 'fas fa-user-plus'
    };
    return icons[type] || 'fas fa-bell';
  };

  const getSeverityColor = (severity) => {
    const colors = {
      high: '#dc3545',
      medium: '#ffc107',
      low: '#28a745'
    };
    return colors[severity] || '#6c757d';
  };

  const formatTimeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMs = now - date;
    const diffInHours = Math.floor(diffInMs / (1000 * 60 * 60));
    const diffInDays = Math.floor(diffInHours / 24);

    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    if (diffInDays < 7) return `${diffInDays}d ago`;
    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="notifications">
        <div className="loading-state">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading notifications...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="notifications">
        <div className="error-state">
          <i className="fas fa-exclamation-triangle"></i>
          <p>Error loading notifications: {error}</p>
          <button onClick={fetchNotifications} className="btn btn-primary">
            Retry
          </button>
        </div>
      </div>
    );
  }

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <div className="notifications">
      <div className="header">
        <div className="title-section">
          <h2>Notifications</h2>
          {unreadCount > 0 && (
            <span className="unread-badge">{unreadCount}</span>
          )}
        </div>
        <div className="header-actions">
          {unreadCount > 0 && (
            <button onClick={markAllAsRead} className="btn btn-outline">
              <i className="fas fa-check-double"></i>
              Mark All Read
            </button>
          )}
        </div>
      </div>

      <div className="filters">
        <button
          className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          All
        </button>
        <button
          className={`filter-btn ${filter === 'unread' ? 'active' : ''}`}
          onClick={() => setFilter('unread')}
        >
          Unread
        </button>
        <button
          className={`filter-btn ${filter === 'threat_alert' ? 'active' : ''}`}
          onClick={() => setFilter('threat_alert')}
        >
          Threats
        </button>
        <button
          className={`filter-btn ${filter === 'trust_request' ? 'active' : ''}`}
          onClick={() => setFilter('trust_request')}
        >
          Trust
        </button>
        <button
          className={`filter-btn ${filter === 'feed_update' ? 'active' : ''}`}
          onClick={() => setFilter('feed_update')}
        >
          Feeds
        </button>
      </div>

      <div className="notifications-list">
        {notifications.length === 0 ? (
          <div className="empty-state">
            <i className="fas fa-bell-slash"></i>
            <h3>No notifications</h3>
            <p>You're all caught up! No notifications to show.</p>
          </div>
        ) : (
          notifications.map(notification => (
            <div
              key={notification.id}
              className={`notification-item ${!notification.read ? 'unread' : ''}`}
            >
              <div className="notification-content">
                <div className="notification-header">
                  <div className="notification-icon">
                    <i
                      className={getNotificationIcon(notification.type)}
                      style={{ color: getSeverityColor(notification.severity) }}
                    ></i>
                  </div>
                  <div className="notification-meta">
                    <h4>{notification.title}</h4>
                    <div className="meta-info">
                      <span className="source">{notification.source}</span>
                      <span className="separator">•</span>
                      <span className="time">{formatTimeAgo(notification.created_at)}</span>
                      {!notification.read && <span className="unread-dot"></span>}
                    </div>
                  </div>
                </div>
                <p className="notification-message">{notification.message}</p>
              </div>
              <div className="notification-actions">
                {!notification.read && (
                  <button
                    onClick={() => markAsRead(notification.id)}
                    className="btn btn-sm btn-outline"
                    title="Mark as read"
                  >
                    <i className="fas fa-check"></i>
                  </button>
                )}
                <button
                  onClick={() => deleteNotification(notification.id)}
                  className="btn btn-sm btn-danger"
                  title="Delete notification"
                >
                  <i className="fas fa-trash"></i>
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      <style jsx>{`
        .notifications {
          padding: 20px;
          max-width: 900px;
          margin: 0 auto;
        }

        .header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .title-section {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .header h2 {
          margin: 0;
          color: #333;
        }

        .unread-badge {
          background: #dc3545;
          color: white;
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 600;
          min-width: 20px;
          text-align: center;
        }

        .filters {
          display: flex;
          gap: 8px;
          margin-bottom: 20px;
          padding-bottom: 15px;
          border-bottom: 1px solid #dee2e6;
        }

        .filter-btn {
          padding: 8px 16px;
          background: none;
          border: 1px solid #dee2e6;
          border-radius: 20px;
          cursor: pointer;
          font-size: 14px;
          color: #6c757d;
          transition: all 0.2s;
        }

        .filter-btn:hover {
          background: #f8f9fa;
          color: #495057;
        }

        .filter-btn.active {
          background: #0056b3;
          color: white;
          border-color: #0056b3;
        }

        .notifications-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .notification-item {
          background: white;
          border: 1px solid #dee2e6;
          border-radius: 8px;
          padding: 16px;
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          transition: all 0.2s;
        }

        .notification-item:hover {
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .notification-item.unread {
          border-left: 4px solid #0056b3;
          background: #f8f9ff;
        }

        .notification-content {
          flex: 1;
          display: flex;
          flex-direction: column;
          padding-right: 1rem;
        }

        .notification-header {
          display: flex;
          align-items: flex-start;
          gap: 12px;
          margin-bottom: 8px;
        }

        .notification-icon {
          width: 40px;
          height: 40px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #f8f9fa;
          border-radius: 50%;
          font-size: 16px;
          flex-shrink: 0;
        }

        .notification-meta {
          flex: 1;
        }

        .notification-meta h4 {
          margin: 0 0 4px 0;
          font-size: 16px;
          font-weight: 600;
          color: #333;
        }

        .meta-info {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 12px;
          color: #6c757d;
        }

        .separator {
          opacity: 0.5;
        }

        .unread-dot {
          width: 6px;
          height: 6px;
          background: #0056b3;
          border-radius: 50%;
        }

        .notification-message {
          margin: 0;
          color: #495057;
          line-height: 1.4;
        }

        .notification-actions {
          display: flex;
          gap: 8px;
          flex-shrink: 0;
          margin-left: 16px;
        }

        .btn {
          padding: 8px 16px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          display: inline-flex;
          align-items: center;
          gap: 8px;
          transition: background-color 0.2s;
        }

        .btn-primary {
          background: #0056b3;
          color: white;
        }

        .btn-outline {
          background: transparent;
          border: 1px solid #dee2e6;
          color: #495057;
        }

        .btn-outline:hover {
          background: #f8f9fa;
        }

        .btn-sm {
          padding: 4px 8px;
          font-size: 12px;
        }

        .btn-danger {
          background: #dc3545;
          color: white;
        }

        .btn-danger:hover {
          background: #c82333;
        }

        .empty-state {
          text-align: center;
          padding: 60px 20px;
          color: #6c757d;
        }

        .empty-state i {
          font-size: 48px;
          margin-bottom: 20px;
          opacity: 0.5;
        }

        .empty-state h3 {
          margin: 0 0 10px 0;
          color: #495057;
        }

        .loading-state,
        .error-state {
          text-align: center;
          padding: 60px 20px;
        }

        .loading-state i {
          font-size: 32px;
          color: #0056b3;
          margin-bottom: 15px;
        }

        .error-state i {
          font-size: 32px;
          color: #dc3545;
          margin-bottom: 15px;
        }
      `}</style>
    </div>
  );
};

export default Notifications;