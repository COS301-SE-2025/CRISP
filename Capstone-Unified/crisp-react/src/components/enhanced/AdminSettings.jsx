import React, { useState, useEffect } from 'react';
import LoadingSpinner from './LoadingSpinner.jsx';
import ConfirmationModal from './ConfirmationModal.jsx';
import * as api from '../../api.js';

const AdminSettings = ({ active = true }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('system');
  const [saving, setSaving] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [confirmationData, setConfirmationData] = useState(null);

  // System settings
  const [systemSettings, setSystemSettings] = useState({
    system_name: 'CRISP Trust Management',
    maintenance_mode: false,
    registration_enabled: true,
    max_trust_relationships: 100,
    trust_expiry_days: 365
  });

  // Security settings
  const [securitySettings, setSecuritySettings] = useState({
    password_min_length: 8,
    password_require_uppercase: true,
    password_require_numbers: true,
    password_require_special: false,
    session_timeout_minutes: 480,
    max_login_attempts: 5
  });

  // Trust settings
  const [trustSettings, setTrustSettings] = useState({
    auto_accept_trust: false,
    trust_verification_required: true,
    trust_decay_enabled: false,
    trust_decay_rate: 0.1,
    bilateral_trust_only: false
  });

  useEffect(() => {
    if (active) {
      loadCurrentUser();
      loadSystemSettings();
    }
  }, [active]);

  const loadCurrentUser = () => {
    const user = api.getCurrentUser();
    setCurrentUser(user);
    if (user && user.role !== 'BlueVisionAdmin' && user.role !== 'admin') {
      setError('Access denied. Administrator privileges required.');
    }
  };

  const loadSystemSettings = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Load settings from localStorage for now (since no backend endpoint exists)
      const savedSystemSettings = localStorage.getItem('crisp_system_settings');
      const savedSecuritySettings = localStorage.getItem('crisp_security_settings');
      const savedTrustSettings = localStorage.getItem('crisp_trust_settings');
      
      if (savedSystemSettings) {
        setSystemSettings(JSON.parse(savedSystemSettings));
      }
      if (savedSecuritySettings) {
        setSecuritySettings(JSON.parse(savedSecuritySettings));
      }
      if (savedTrustSettings) {
        setTrustSettings(JSON.parse(savedTrustSettings));
      }
    } catch (err) {
      console.error('Settings load error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSystemSettingsSave = async () => {
    setConfirmationData({
      title: 'Update System Settings',
      message: 'Are you sure you want to update the system settings? This may affect all users.',
      confirmText: 'Update Settings',
      isDestructive: false,
      action: async () => {
        try {
          setSaving(true);
          setError(null);
          
          // Save to localStorage for now
          localStorage.setItem('crisp_system_settings', JSON.stringify(systemSettings));
          
          setError('System settings updated successfully!');
          setTimeout(() => setError(null), 3000);
        } catch (err) {
          console.error('System settings update error:', err);
          setError(err.message);
        } finally {
          setSaving(false);
        }
      }
    });
    setShowConfirmation(true);
  };

  const handleSecuritySettingsSave = async () => {
    setConfirmationData({
      title: 'Update Security Settings',
      message: 'Are you sure you want to update the security settings? This will affect password policies and session management.',
      confirmText: 'Update Settings',
      isDestructive: false,
      action: async () => {
        try {
          setSaving(true);
          setError(null);
          
          // Save to localStorage for now
          localStorage.setItem('crisp_security_settings', JSON.stringify(securitySettings));
          
          setError('Security settings updated successfully!');
          setTimeout(() => setError(null), 3000);
        } catch (err) {
          console.error('Security settings update error:', err);
          setError(err.message);
        } finally {
          setSaving(false);
        }
      }
    });
    setShowConfirmation(true);
  };

  const handleTrustSettingsSave = async () => {
    setConfirmationData({
      title: 'Update Trust Settings',
      message: 'Are you sure you want to update the trust management settings? This will affect how trust relationships work.',
      confirmText: 'Update Settings',
      isDestructive: false,
      action: async () => {
        try {
          setSaving(true);
          setError(null);
          
          // Save to localStorage for now
          localStorage.setItem('crisp_trust_settings', JSON.stringify(trustSettings));
          
          setError('Trust settings updated successfully!');
          setTimeout(() => setError(null), 3000);
        } catch (err) {
          console.error('Trust settings update error:', err);
          setError(err.message);
        } finally {
          setSaving(false);
        }
      }
    });
    setShowConfirmation(true);
  };

  const tabs = [
    { id: 'system', label: 'System Settings', icon: 'fas fa-cogs' },
    { id: 'security', label: 'Security', icon: 'fas fa-shield-alt' },
    { id: 'trust', label: 'Trust Management', icon: 'fas fa-handshake' },
    { id: 'audit', label: 'Audit Logs', icon: 'fas fa-file-alt' }
  ];

  if (!active) return null;

  // Check admin permissions
  if (currentUser && currentUser.role !== 'BlueVisionAdmin' && currentUser.role !== 'admin') {
    return (
      <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
        <div style={{
          textAlign: 'center',
          padding: '3rem 2rem',
          backgroundColor: 'white',
          borderRadius: '12px',
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
          border: '1px solid #e9ecef'
        }}>
          <i className="fas fa-lock" style={{
            fontSize: '3rem',
            color: '#dc3545',
            marginBottom: '1rem',
            display: 'block'
          }}></i>
          <h3 style={{ color: '#dc3545', marginBottom: '1rem' }}>Access Denied</h3>
          <p style={{ color: '#666' }}>Administrator privileges are required to access this page.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return <LoadingSpinner fullscreen={true} />;
  }

  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif', position: 'relative' }}>
      {saving && <LoadingSpinner fullscreen={true} />}
      
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ margin: '0 0 0.5rem 0', color: '#333' }}>Admin Settings</h1>
        <p style={{ margin: 0, color: '#666' }}>System administration and configuration</p>
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
                borderLeft: activeTab === tab.id ? '4px solid #dc3545' : '4px solid transparent',
                textAlign: 'left',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                transition: 'all 0.2s ease'
              }}
            >
              <i className={tab.icon} style={{
                color: activeTab === tab.id ? '#dc3545' : '#6c757d',
                fontSize: '1.1rem'
              }}></i>
              <span style={{
                fontWeight: activeTab === tab.id ? '600' : '400',
                color: activeTab === tab.id ? '#dc3545' : '#333'
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
          {activeTab === 'system' && (
            <div>
              <h3 style={{ margin: '0 0 1.5rem 0', color: '#333' }}>System Settings</h3>
              <div style={{
                display: 'flex',
                flexDirection: 'column',
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
                    System Name
                  </label>
                  <input
                    type="text"
                    value={systemSettings.system_name}
                    onChange={(e) => setSystemSettings({...systemSettings, system_name: e.target.value})}
                    style={{
                      width: '100%',
                      maxWidth: '400px',
                      padding: '0.75rem',
                      border: '1px solid #dee2e6',
                      borderRadius: '6px',
                      fontSize: '0.875rem'
                    }}
                  />
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
                    id="maintenance_mode"
                    checked={systemSettings.maintenance_mode}
                    onChange={(e) => setSystemSettings({...systemSettings, maintenance_mode: e.target.checked})}
                    style={{ transform: 'scale(1.2)' }}
                  />
                  <div>
                    <label htmlFor="maintenance_mode" style={{
                      fontWeight: '600',
                      color: '#333',
                      cursor: 'pointer'
                    }}>
                      Maintenance Mode
                    </label>
                    <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.875rem', color: '#666' }}>
                      Put the system in maintenance mode to prevent user access
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
                    id="registration_enabled"
                    checked={systemSettings.registration_enabled}
                    onChange={(e) => setSystemSettings({...systemSettings, registration_enabled: e.target.checked})}
                    style={{ transform: 'scale(1.2)' }}
                  />
                  <div>
                    <label htmlFor="registration_enabled" style={{
                      fontWeight: '600',
                      color: '#333',
                      cursor: 'pointer'
                    }}>
                      User Registration Enabled
                    </label>
                    <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.875rem', color: '#666' }}>
                      Allow new users to register accounts
                    </p>
                  </div>
                </div>

                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
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
                      Max Trust Relationships
                    </label>
                    <input
                      type="number"
                      value={systemSettings.max_trust_relationships}
                      onChange={(e) => setSystemSettings({...systemSettings, max_trust_relationships: parseInt(e.target.value)})}
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
                      Trust Expiry (Days)
                    </label>
                    <input
                      type="number"
                      value={systemSettings.trust_expiry_days}
                      onChange={(e) => setSystemSettings({...systemSettings, trust_expiry_days: parseInt(e.target.value)})}
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

                <div>
                  <button
                    onClick={handleSystemSettingsSave}
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
                    Save System Settings
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div>
              <h3 style={{ margin: '0 0 1.5rem 0', color: '#333' }}>Security Settings</h3>
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '1.5rem'
              }}>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
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
                      Password Min Length
                    </label>
                    <input
                      type="number"
                      min="6"
                      max="32"
                      value={securitySettings.password_min_length}
                      onChange={(e) => setSecuritySettings({...securitySettings, password_min_length: parseInt(e.target.value)})}
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
                      Session Timeout (Minutes)
                    </label>
                    <input
                      type="number"
                      min="30"
                      max="1440"
                      value={securitySettings.session_timeout_minutes}
                      onChange={(e) => setSecuritySettings({...securitySettings, session_timeout_minutes: parseInt(e.target.value)})}
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
                      Max Login Attempts
                    </label>
                    <input
                      type="number"
                      min="3"
                      max="10"
                      value={securitySettings.max_login_attempts}
                      onChange={(e) => setSecuritySettings({...securitySettings, max_login_attempts: parseInt(e.target.value)})}
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

                <div>
                  <h4 style={{ margin: '0 0 1rem 0', color: '#333' }}>Password Requirements</h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {[
                      { key: 'password_require_uppercase', label: 'Require Uppercase Letters', desc: 'Passwords must contain at least one uppercase letter' },
                      { key: 'password_require_numbers', label: 'Require Numbers', desc: 'Passwords must contain at least one number' },
                      { key: 'password_require_special', label: 'Require Special Characters', desc: 'Passwords must contain at least one special character' }
                    ].map((setting) => (
                      <div key={setting.key} style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '1rem',
                        padding: '1rem',
                        border: '1px solid #dee2e6',
                        borderRadius: '6px'
                      }}>
                        <input
                          type="checkbox"
                          id={setting.key}
                          checked={securitySettings[setting.key]}
                          onChange={(e) => setSecuritySettings({...securitySettings, [setting.key]: e.target.checked})}
                          style={{ transform: 'scale(1.2)' }}
                        />
                        <div>
                          <label htmlFor={setting.key} style={{
                            fontWeight: '600',
                            color: '#333',
                            cursor: 'pointer'
                          }}>
                            {setting.label}
                          </label>
                          <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.875rem', color: '#666' }}>
                            {setting.desc}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <button
                    onClick={handleSecuritySettingsSave}
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
                    Save Security Settings
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'trust' && (
            <div>
              <h3 style={{ margin: '0 0 1.5rem 0', color: '#333' }}>Trust Management Settings</h3>
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '1.5rem'
              }}>
                {[
                  { key: 'auto_accept_trust', label: 'Auto-Accept Trust Requests', desc: 'Automatically accept incoming trust relationship requests' },
                  { key: 'trust_verification_required', label: 'Trust Verification Required', desc: 'Require verification before establishing trust relationships' },
                  { key: 'trust_decay_enabled', label: 'Trust Decay Enabled', desc: 'Enable automatic trust level degradation over time' },
                  { key: 'bilateral_trust_only', label: 'Bilateral Trust Only', desc: 'Only allow bilateral (mutual) trust relationships' }
                ].map((setting) => (
                  <div key={setting.key} style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '1rem',
                    padding: '1rem',
                    border: '1px solid #dee2e6',
                    borderRadius: '6px'
                  }}>
                    <input
                      type="checkbox"
                      id={setting.key}
                      checked={trustSettings[setting.key]}
                      onChange={(e) => setTrustSettings({...trustSettings, [setting.key]: e.target.checked})}
                      style={{ transform: 'scale(1.2)' }}
                    />
                    <div>
                      <label htmlFor={setting.key} style={{
                        fontWeight: '600',
                        color: '#333',
                        cursor: 'pointer'
                      }}>
                        {setting.label}
                      </label>
                      <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.875rem', color: '#666' }}>
                        {setting.desc}
                      </p>
                    </div>
                  </div>
                ))}

                {trustSettings.trust_decay_enabled && (
                  <div>
                    <label style={{
                      display: 'block',
                      marginBottom: '0.5rem',
                      fontWeight: '600',
                      color: '#495057',
                      fontSize: '0.875rem'
                    }}>
                      Trust Decay Rate (0.01 - 1.0)
                    </label>
                    <input
                      type="number"
                      min="0.01"
                      max="1.0"
                      step="0.01"
                      value={trustSettings.trust_decay_rate}
                      onChange={(e) => setTrustSettings({...trustSettings, trust_decay_rate: parseFloat(e.target.value)})}
                      style={{
                        width: '200px',
                        padding: '0.75rem',
                        border: '1px solid #dee2e6',
                        borderRadius: '6px',
                        fontSize: '0.875rem'
                      }}
                    />
                    <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.875rem', color: '#666' }}>
                      Rate at which trust levels decrease over time
                    </p>
                  </div>
                )}

                <div>
                  <button
                    onClick={handleTrustSettingsSave}
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
                    Save Trust Settings
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'audit' && (
            <div>
              <h3 style={{ margin: '0 0 1.5rem 0', color: '#333' }}>Audit Logs</h3>
              <div style={{
                textAlign: 'center',
                padding: '3rem 2rem',
                color: '#666'
              }}>
                <i className="fas fa-file-alt" style={{
                  fontSize: '3rem',
                  marginBottom: '1rem',
                  display: 'block'
                }}></i>
                <h4 style={{ margin: '0 0 1rem 0' }}>Audit Logs Coming Soon</h4>
                <p>Comprehensive audit logging and analysis features will be available in a future update.</p>
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

export default AdminSettings;