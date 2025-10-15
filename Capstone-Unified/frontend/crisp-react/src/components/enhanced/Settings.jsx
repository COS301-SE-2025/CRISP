import React, { useState, useEffect } from 'react';
import LoadingSpinner from './LoadingSpinner.jsx';
import ConfirmationModal from './ConfirmationModal.jsx';
import * as api from '../../api.js';

const Settings = ({ active = true }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('profile');
  const [saving, setSaving] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [confirmationData, setConfirmationData] = useState(null);

  // Profile settings
  const [profileData, setProfileData] = useState({
    first_name: '',
    last_name: '',
    email: ''
  });

  // Password settings
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });

  // Notification settings
  const [notificationData, setNotificationData] = useState({
    email_notifications: true,
    trust_notifications: true,
    security_alerts: true
  });

  useEffect(() => {
    if (active) {
      loadCurrentUser();
      loadUserProfile();
    }
  }, [active]);

  const loadCurrentUser = () => {
    const user = api.getCurrentUser();
    setCurrentUser(user);
  };

  const loadUserProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      const token = localStorage.getItem('crisp_auth_token');
      const response = await fetch('/api/auth/profile/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        let userProfile = null;
        if (data.success && data.data?.user) {
          userProfile = data.data.user;
        } else if (data.user) {
          userProfile = data.user;
        }
        
        if (userProfile) {
          setProfileData({
            first_name: userProfile.first_name || '',
            last_name: userProfile.last_name || '',
            email: userProfile.email || ''
          });
        }
      } else {
        throw new Error('Failed to load profile');
      }
    } catch (err) {
      console.error('Profile load error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleProfileSave = async () => {
    setConfirmationData({
      title: 'Update Profile',
      message: 'Are you sure you want to update your profile information?',
      confirmText: 'Update Profile',
      isDestructive: false,
      action: async () => {
        try {
          setSaving(true);
          setError(null);
          const token = localStorage.getItem('crisp_auth_token');
          const response = await fetch('/api/auth/profile/', {
            method: 'PUT',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(profileData)
          });

          if (response.ok) {
            setError(null);
            // Show success message
            setError('Profile updated successfully!');
            setTimeout(() => setError(null), 3000);
          } else {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || 'Failed to update profile');
          }
        } catch (err) {
          console.error('Profile update error:', err);
          setError(err.message);
        } finally {
          setSaving(false);
        }
      }
    });
    setShowConfirmation(true);
  };

  const handlePasswordSave = async () => {
    if (passwordData.new_password !== passwordData.confirm_password) {
      setError('New passwords do not match');
      return;
    }

    if (passwordData.new_password.length < 8) {
      setError('New password must be at least 8 characters long');
      return;
    }

    setConfirmationData({
      title: 'Change Password',
      message: 'Are you sure you want to change your password?',
      confirmText: 'Change Password',
      isDestructive: false,
      action: async () => {
        try {
          setSaving(true);
          setError(null);
          const token = localStorage.getItem('crisp_auth_token');
          const response = await fetch('/api/auth/change-password/', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              current_password: passwordData.current_password,
              new_password: passwordData.new_password
            })
          });

          if (response.ok) {
            setPasswordData({
              current_password: '',
              new_password: '',
              confirm_password: ''
            });
            setError('Password changed successfully!');
            setTimeout(() => setError(null), 3000);
          } else {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || 'Failed to change password');
          }
        } catch (err) {
          console.error('Password change error:', err);
          setError(err.message);
        } finally {
          setSaving(false);
        }
      }
    });
    setShowConfirmation(true);
  };

  const handleNotificationSave = async () => {
    setConfirmationData({
      title: 'Update Notification Settings',
      message: 'Are you sure you want to update your notification preferences?',
      confirmText: 'Update Settings',
      isDestructive: false,
      action: async () => {
        try {
          setSaving(true);
          setError(null);
          // For now, just save to localStorage since there's no backend endpoint
          localStorage.setItem('crisp_notification_settings', JSON.stringify(notificationData));
          setError('Notification settings updated successfully!');
          setTimeout(() => setError(null), 3000);
        } catch (err) {
          console.error('Notification settings error:', err);
          setError(err.message);
        } finally {
          setSaving(false);
        }
      }
    });
    setShowConfirmation(true);
  };

  const tabs = [
    { id: 'profile', label: 'Profile Settings', icon: 'fas fa-user' },
    { id: 'password', label: 'Password', icon: 'fas fa-lock' },
    { id: 'notifications', label: 'Notifications', icon: 'fas fa-bell' }
  ];

  if (!active) return null;

  if (loading) {
    return <LoadingSpinner fullscreen={true} />;
  }

  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif', position: 'relative' }}>
      {saving && <LoadingSpinner fullscreen={true} />}
      
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ margin: '0 0 0.5rem 0', color: '#333' }}>Settings</h1>
        <p style={{ margin: 0, color: '#666' }}>Manage your account settings and preferences</p>
      </div>

      {error && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          padding: '1rem 1.25rem',
          backgroundColor: error.includes('successfully') ? '#d4edda' : '#f8d7da',
          color: error.includes('successfully') ? '#155724' : '#721c24',
          border: `1px solid ${error.includes('successfully') ? '#c3e6cb' : '#f5c6cb'}`,
          borderRadius: '6px',
          marginBottom: '2rem'
        }}>
          <i className={`fas ${error.includes('successfully') ? 'fa-check-circle' : 'fa-exclamation-triangle'}`}></i>
          <span style={{ flex: 1 }}>{error}</span>
          <button 
            onClick={() => setError(null)}
            style={{
              background: 'none',
              border: 'none',
              color: 'inherit',
              cursor: 'pointer',
              padding: '0.25rem'
            }}
          >
            <i className="fas fa-times"></i>
          </button>
        </div>
      )}

      <div style={{
        display: 'flex',
        gap: '2rem',
        alignItems: 'flex-start'
      }}>
        {/* Tab Navigation */}
        <div style={{
          minWidth: '250px',
          backgroundColor: 'white',
          borderRadius: '12px',
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
          border: '1px solid #e9ecef',
          overflow: 'hidden'
        }}>
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                width: '100%',
                padding: '1.25rem 1.5rem',
                border: 'none',
                backgroundColor: activeTab === tab.id ? '#f8f9fa' : 'white',
                borderLeft: activeTab === tab.id ? '4px solid #007bff' : '4px solid transparent',
                textAlign: 'left',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                transition: 'all 0.2s ease'
              }}
            >
              <i className={tab.icon} style={{
                color: activeTab === tab.id ? '#007bff' : '#6c757d',
                fontSize: '1.1rem'
              }}></i>
              <span style={{
                fontWeight: activeTab === tab.id ? '600' : '400',
                color: activeTab === tab.id ? '#007bff' : '#333'
              }}>
                {tab.label}
              </span>
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div style={{
          flex: 1,
          backgroundColor: 'white',
          borderRadius: '12px',
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
          border: '1px solid #e9ecef',
          padding: '2rem'
        }}>
          {activeTab === 'profile' && (
            <div>
              <h3 style={{ margin: '0 0 1.5rem 0', color: '#333' }}>Profile Settings</h3>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                gap: '1.5rem'
              }}>
                <div>
                  <label style={{
                    display: 'block',
                    marginBottom: '0.5rem',
                    fontWeight: '600',
                    color: '#495057',
                    fontSize: '0.875rem'
                  }}>
                    First Name
                  </label>
                  <input
                    type="text"
                    value={profileData.first_name}
                    onChange={(e) => setProfileData({...profileData, first_name: e.target.value})}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #dee2e6',
                      borderRadius: '6px',
                      fontSize: '0.875rem'
                    }}
                  />
                </div>
                
                <div>
                  <label style={{
                    display: 'block',
                    marginBottom: '0.5rem',
                    fontWeight: '600',
                    color: '#495057',
                    fontSize: '0.875rem'
                  }}>
                    Last Name
                  </label>
                  <input
                    type="text"
                    value={profileData.last_name}
                    onChange={(e) => setProfileData({...profileData, last_name: e.target.value})}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #dee2e6',
                      borderRadius: '6px',
                      fontSize: '0.875rem'
                    }}
                  />
                </div>
              </div>
              
              <div style={{ marginTop: '1.5rem' }}>
                <label style={{
                  display: 'block',
                  marginBottom: '0.5rem',
                  fontWeight: '600',
                  color: '#495057',
                  fontSize: '0.875rem'
                }}>
                  Email
                </label>
                <input
                  type="email"
                  value={profileData.email}
                  onChange={(e) => setProfileData({...profileData, email: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #dee2e6',
                    borderRadius: '6px',
                    fontSize: '0.875rem'
                  }}
                />
              </div>

              <div style={{ marginTop: '2rem' }}>
                <button
                  onClick={handleProfileSave}
                  style={{
                    padding: '0.75rem 1.5rem',
                    backgroundColor: '#007bff',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    fontWeight: '500'
                  }}
                >
                  Save Profile Changes
                </button>
              </div>
            </div>
          )}

          {activeTab === 'password' && (
            <div>
              <h3 style={{ margin: '0 0 1.5rem 0', color: '#333' }}>Change Password</h3>
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '1.5rem',
                maxWidth: '400px'
              }}>
                <div>
                  <label style={{
                    display: 'block',
                    marginBottom: '0.5rem',
                    fontWeight: '600',
                    color: '#495057',
                    fontSize: '0.875rem'
                  }}>
                    Current Password
                  </label>
                  <input
                    type="password"
                    value={passwordData.current_password}
                    onChange={(e) => setPasswordData({...passwordData, current_password: e.target.value})}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #dee2e6',
                      borderRadius: '6px',
                      fontSize: '0.875rem'
                    }}
                  />
                </div>
                
                <div>
                  <label style={{
                    display: 'block',
                    marginBottom: '0.5rem',
                    fontWeight: '600',
                    color: '#495057',
                    fontSize: '0.875rem'
                  }}>
                    New Password
                  </label>
                  <input
                    type="password"
                    value={passwordData.new_password}
                    onChange={(e) => setPasswordData({...passwordData, new_password: e.target.value})}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #dee2e6',
                      borderRadius: '6px',
                      fontSize: '0.875rem'
                    }}
                  />
                </div>
                
                <div>
                  <label style={{
                    display: 'block',
                    marginBottom: '0.5rem',
                    fontWeight: '600',
                    color: '#495057',
                    fontSize: '0.875rem'
                  }}>
                    Confirm New Password
                  </label>
                  <input
                    type="password"
                    value={passwordData.confirm_password}
                    onChange={(e) => setPasswordData({...passwordData, confirm_password: e.target.value})}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #dee2e6',
                      borderRadius: '6px',
                      fontSize: '0.875rem'
                    }}
                  />
                </div>

                <div>
                  <button
                    onClick={handlePasswordSave}
                    style={{
                      padding: '0.75rem 1.5rem',
                      backgroundColor: '#dc3545',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontSize: '0.875rem',
                      fontWeight: '500'
                    }}
                  >
                    Change Password
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div>
              <h3 style={{ margin: '0 0 1.5rem 0', color: '#333' }}>Notification Preferences</h3>
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '1.5rem'
              }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '1rem',
                  padding: '1rem',
                  border: '1px solid #dee2e6',
                  borderRadius: '6px'
                }}>
                  <input
                    type="checkbox"
                    id="email_notifications"
                    checked={notificationData.email_notifications}
                    onChange={(e) => setNotificationData({...notificationData, email_notifications: e.target.checked})}
                    style={{ transform: 'scale(1.2)' }}
                  />
                  <div>
                    <label htmlFor="email_notifications" style={{
                      fontWeight: '600',
                      color: '#333',
                      cursor: 'pointer'
                    }}>
                      Email Notifications
                    </label>
                    <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.875rem', color: '#666' }}>
                      Receive email notifications for important updates
                    </p>
                  </div>
                </div>

                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '1rem',
                  padding: '1rem',
                  border: '1px solid #dee2e6',
                  borderRadius: '6px'
                }}>
                  <input
                    type="checkbox"
                    id="trust_notifications"
                    checked={notificationData.trust_notifications}
                    onChange={(e) => setNotificationData({...notificationData, trust_notifications: e.target.checked})}
                    style={{ transform: 'scale(1.2)' }}
                  />
                  <div>
                    <label htmlFor="trust_notifications" style={{
                      fontWeight: '600',
                      color: '#333',
                      cursor: 'pointer'
                    }}>
                      Trust Relationship Notifications
                    </label>
                    <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.875rem', color: '#666' }}>
                      Get notified about trust relationship changes and requests
                    </p>
                  </div>
                </div>

                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '1rem',
                  padding: '1rem',
                  border: '1px solid #dee2e6',
                  borderRadius: '6px'
                }}>
                  <input
                    type="checkbox"
                    id="security_alerts"
                    checked={notificationData.security_alerts}
                    onChange={(e) => setNotificationData({...notificationData, security_alerts: e.target.checked})}
                    style={{ transform: 'scale(1.2)' }}
                  />
                  <div>
                    <label htmlFor="security_alerts" style={{
                      fontWeight: '600',
                      color: '#333',
                      cursor: 'pointer'
                    }}>
                      Security Alerts
                    </label>
                    <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.875rem', color: '#666' }}>
                      Important security notifications and alerts
                    </p>
                  </div>
                </div>

                <div>
                  <button
                    onClick={handleNotificationSave}
                    style={{
                      padding: '0.75rem 1.5rem',
                      backgroundColor: '#28a745',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontSize: '0.875rem',
                      fontWeight: '500'
                    }}
                  >
                    Save Notification Settings
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <ConfirmationModal
        isOpen={showConfirmation}
        onClose={() => setShowConfirmation(false)}
        onConfirm={confirmationData?.action}
        title={confirmationData?.title}
        message={confirmationData?.message}
        confirmText={confirmationData?.confirmText}
        isDestructive={confirmationData?.isDestructive}
      />
    </div>
  );
};

export default Settings;