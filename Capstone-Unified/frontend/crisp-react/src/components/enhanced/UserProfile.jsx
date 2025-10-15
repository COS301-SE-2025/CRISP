import React, { useState, useEffect } from 'react';
import LoadingSpinner from './LoadingSpinner.jsx';
import * as api from '../../api.js';

const UserProfile = ({ active = true }) => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [editData, setEditData] = useState({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (active) {
      fetchProfile();
    }
  }, [active]);

  const fetchProfile = async () => {
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
        console.log('Profile data:', data);
        
        let userProfile = null;
        if (data.success && data.data?.user) {
          userProfile = data.data.user;
        } else if (data.user) {
          userProfile = data.user;
        } else if (data.success && data.user) {
          userProfile = data.user;
        } else {
          throw new Error('Invalid profile response format');
        }
        
        setProfile(userProfile);
        setEditData({
          first_name: userProfile.first_name || '',
          last_name: userProfile.last_name || '',
          email: userProfile.email || ''
        });
      } else {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || 'Failed to fetch profile');
      }
    } catch (err) {
      console.error('Profile fetch error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
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
        body: JSON.stringify(editData)
      });

      if (response.ok) {
        const data = await response.json();
        
        let updatedProfile = null;
        if (data.success && data.data?.user) {
          updatedProfile = data.data.user;
        } else if (data.user) {
          updatedProfile = data.user;
        } else {
          throw new Error('Invalid update response format');
        }
        
        setProfile(updatedProfile);
        setEditMode(false);
        setError(null);
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
  };

  const handleCancel = () => {
    setEditData({
      first_name: profile.first_name || '',
      last_name: profile.last_name || '',
      email: profile.email || ''
    });
    setEditMode(false);
    setError(null);
  };

  if (!active) return null;

  if (loading) {
    return <LoadingSpinner fullscreen={true} />;
  }

  if (error && !profile) {
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
          <i className="fas fa-exclamation-triangle" style={{
            fontSize: '3rem',
            color: '#dc3545',
            marginBottom: '1rem',
            display: 'block'
          }}></i>
          <h3 style={{ color: '#dc3545', marginBottom: '1rem' }}>Error Loading Profile</h3>
          <p style={{ color: '#666', marginBottom: '1.5rem' }}>{error}</p>
          <button 
            onClick={fetchProfile} 
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '1rem',
              fontWeight: '500'
            }}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!profile) {
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
          <i className="fas fa-user-slash" style={{
            fontSize: '3rem',
            color: '#6c757d',
            marginBottom: '1rem',
            display: 'block'
          }}></i>
          <h3 style={{ color: '#6c757d', marginBottom: '1rem' }}>No Profile Data</h3>
          <p style={{ color: '#666', marginBottom: '1.5rem' }}>Unable to load profile information</p>
          <button 
            onClick={fetchProfile} 
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '1rem',
              fontWeight: '500'
            }}
          >
            Refresh
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif', position: 'relative' }}>
      {saving && <LoadingSpinner fullscreen={true} />}
      
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '2rem'
      }}>
        <h1 style={{ margin: 0, color: '#333' }}>User Profile</h1>
        {!editMode && (
          <button 
            onClick={() => setEditMode(true)}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '0.875rem',
              fontWeight: '500',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
          >
            <i className="fas fa-edit"></i>
            Edit Profile
          </button>
        )}
      </div>

      {error && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          padding: '1rem 1.25rem',
          backgroundColor: '#f8d7da',
          color: '#721c24',
          border: '1px solid #f5c6cb',
          borderRadius: '6px',
          marginBottom: '2rem'
        }}>
          <i className="fas fa-exclamation-triangle"></i>
          <span style={{ flex: 1 }}>{error}</span>
          <button 
            onClick={() => setError(null)}
            style={{
              background: 'none',
              border: 'none',
              color: '#721c24',
              cursor: 'pointer',
              padding: '0.25rem'
            }}
          >
            <i className="fas fa-times"></i>
          </button>
        </div>
      )}

      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
        overflow: 'hidden',
        border: '1px solid #e9ecef'
      }}>
        {/* Profile Header */}
        <div style={{
          background: 'linear-gradient(135deg, #0056b3, #004494)',
          color: 'white',
          padding: '2rem',
          display: 'flex',
          alignItems: 'center',
          gap: '1.5rem'
        }}>
          <div style={{
            width: '80px',
            height: '80px',
            background: 'rgba(255,255,255,0.2)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '2rem'
          }}>
            <i className="fas fa-user"></i>
          </div>
          <div>
            <h3 style={{ 
              margin: '0 0 0.5rem 0', 
              fontSize: '1.5rem', 
              fontWeight: '600' 
            }}>
              {profile.first_name || profile.last_name ? 
                `${profile.first_name || ''} ${profile.last_name || ''}`.trim() : 
                profile.username
              }
            </h3>
            <p style={{ 
              margin: 0, 
              opacity: 0.9, 
              fontSize: '1rem' 
            }}>
              {profile.role}
            </p>
          </div>
        </div>

        {/* Profile Details */}
        <div style={{ padding: '2rem' }}>
          {editMode ? (
            <form 
              onSubmit={(e) => e.preventDefault()}
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '1.5rem'
              }}
            >
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
                    value={editData.first_name}
                    onChange={(e) => setEditData({...editData, first_name: e.target.value})}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #dee2e6',
                      borderRadius: '6px',
                      fontSize: '0.875rem',
                      transition: 'border-color 0.2s'
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#0056b3'}
                    onBlur={(e) => e.target.style.borderColor = '#dee2e6'}
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
                    value={editData.last_name}
                    onChange={(e) => setEditData({...editData, last_name: e.target.value})}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      border: '1px solid #dee2e6',
                      borderRadius: '6px',
                      fontSize: '0.875rem',
                      transition: 'border-color 0.2s'
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#0056b3'}
                    onBlur={(e) => e.target.style.borderColor = '#dee2e6'}
                  />
                </div>
              </div>
              
              <div>
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
                  value={editData.email}
                  onChange={(e) => setEditData({...editData, email: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #dee2e6',
                    borderRadius: '6px',
                    fontSize: '0.875rem',
                    transition: 'border-color 0.2s'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#0056b3'}
                  onBlur={(e) => e.target.style.borderColor = '#dee2e6'}
                />
              </div>

              <div style={{
                display: 'flex',
                gap: '1rem',
                justifyContent: 'flex-end',
                marginTop: '1rem'
              }}>
                <button 
                  type="button" 
                  onClick={handleCancel}
                  style={{
                    padding: '0.75rem 1.5rem',
                    border: '1px solid #6c757d',
                    backgroundColor: 'white',
                    color: '#6c757d',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}
                >
                  <i className="fas fa-times"></i>
                  Cancel
                </button>
                <button 
                  type="button" 
                  onClick={handleSave}
                  disabled={saving}
                  style={{
                    padding: '0.75rem 1.5rem',
                    backgroundColor: '#28a745',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: saving ? 'not-allowed' : 'pointer',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    opacity: saving ? 0.6 : 1
                  }}
                >
                  {saving ? (
                    <i className="fas fa-spinner fa-spin"></i>
                  ) : (
                    <i className="fas fa-save"></i>
                  )}
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          ) : (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
              gap: '1.5rem'
            }}>
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '0.5rem'
              }}>
                <label style={{
                  fontWeight: '600',
                  color: '#495057',
                  fontSize: '0.75rem',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}>
                  Username
                </label>
                <span style={{
                  fontSize: '1rem',
                  color: '#333',
                  padding: '0.5rem 0'
                }}>
                  {profile.username}
                </span>
              </div>
              
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '0.5rem'
              }}>
                <label style={{
                  fontWeight: '600',
                  color: '#495057',
                  fontSize: '0.75rem',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}>
                  Email
                </label>
                <span style={{
                  fontSize: '1rem',
                  color: '#333',
                  padding: '0.5rem 0'
                }}>
                  {profile.email || 'Not provided'}
                </span>
              </div>
              
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '0.5rem'
              }}>
                <label style={{
                  fontWeight: '600',
                  color: '#495057',
                  fontSize: '0.75rem',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}>
                  First Name
                </label>
                <span style={{
                  fontSize: '1rem',
                  color: '#333',
                  padding: '0.5rem 0'
                }}>
                  {profile.first_name || 'Not set'}
                </span>
              </div>
              
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '0.5rem'
              }}>
                <label style={{
                  fontWeight: '600',
                  color: '#495057',
                  fontSize: '0.75rem',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}>
                  Last Name
                </label>
                <span style={{
                  fontSize: '1rem',
                  color: '#333',
                  padding: '0.5rem 0'
                }}>
                  {profile.last_name || 'Not set'}
                </span>
              </div>
              
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '0.5rem'
              }}>
                <label style={{
                  fontWeight: '600',
                  color: '#495057',
                  fontSize: '0.75rem',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}>
                  Organization
                </label>
                <span style={{
                  fontSize: '1rem',
                  color: '#333',
                  padding: '0.5rem 0'
                }}>
                  {profile.organization?.name || 'No organization'}
                </span>
              </div>
              
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '0.5rem'
              }}>
                <label style={{
                  fontWeight: '600',
                  color: '#495057',
                  fontSize: '0.75rem',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}>
                  Role
                </label>
                <span style={{
                  display: 'inline-block',
                  padding: '0.4rem 0.8rem',
                  borderRadius: '15px',
                  fontSize: '0.75rem',
                  fontWeight: '600',
                  textTransform: 'uppercase',
                  backgroundColor: 
                    profile.role === 'admin' ? '#e3f2fd' :
                    profile.role === 'publisher' ? '#fff3cd' :
                    profile.role === 'BlueVisionAdmin' ? '#e8f5e8' : '#f3e5f5',
                  color:
                    profile.role === 'admin' ? '#1976d2' :
                    profile.role === 'publisher' ? '#856404' :
                    profile.role === 'BlueVisionAdmin' ? '#2e7d32' : '#7b1fa2'
                }}>
                  {profile.role}
                </span>
              </div>
              
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '0.5rem'
              }}>
                <label style={{
                  fontWeight: '600',
                  color: '#495057',
                  fontSize: '0.75rem',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}>
                  Status
                </label>
                <span style={{
                  display: 'inline-block',
                  padding: '0.4rem 0.8rem',
                  borderRadius: '15px',
                  fontSize: '0.75rem',
                  fontWeight: '600',
                  textTransform: 'uppercase',
                  backgroundColor: profile.is_active ? '#d4edda' : '#f8d7da',
                  color: profile.is_active ? '#155724' : '#721c24'
                }}>
                  {profile.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '0.5rem'
              }}>
                <label style={{
                  fontWeight: '600',
                  color: '#495057',
                  fontSize: '0.75rem',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}>
                  Member Since
                </label>
                <span style={{
                  fontSize: '1rem',
                  color: '#333',
                  padding: '0.5rem 0'
                }}>
                  {profile.created_at ? new Date(profile.created_at).toLocaleDateString() : 'Unknown'}
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UserProfile;