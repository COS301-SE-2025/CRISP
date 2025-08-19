import React, { useState, useEffect } from 'react';

const UserProfile = ({ active = true }) => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [editData, setEditData] = useState({});

  useEffect(() => {
    if (active) {
      fetchProfile();
    }
  }, [active]);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('crisp_auth_token');
      const response = await fetch('http://localhost:8000/api/auth/profile/', {
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
      const token = localStorage.getItem('crisp_auth_token');
      const response = await fetch('http://localhost:8000/api/auth/profile/', {
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
    return (
      <div className="user-profile">
        <div className="loading-state">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading profile...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="user-profile">
        <div className="error-state">
          <i className="fas fa-exclamation-triangle"></i>
          <p>Error loading profile: {error}</p>
          <button onClick={fetchProfile} className="btn btn-primary">
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="user-profile">
        <div className="error-state">
          <i className="fas fa-user-slash"></i>
          <p>No profile data available</p>
          <button onClick={fetchProfile} className="btn btn-primary">
            Refresh
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="user-profile">
      <div className="header">
        <h1>My Profile</h1>
      </div>

      {error && (
        <div className="error-banner">
          <i className="fas fa-exclamation-triangle"></i>
          <span>{error}</span>
          <button onClick={() => setError(null)} className="close-btn">
            <i className="fas fa-times"></i>
          </button>
        </div>
      )}

      <div className="profile-card">
        <div className="profile-header">
          <div className="profile-info">
            <div className="profile-avatar">
              <i className="fas fa-user"></i>
            </div>
            <div className="profile-title">
              <h2>{profile.first_name} {profile.last_name}</h2>
              <span className={`role-badge ${profile.role?.toLowerCase()}`}>
                {profile.role}
              </span>
            </div>
          </div>
          {!editMode && (
            <button 
              className="edit-profile-btn"
              onClick={() => setEditMode(true)}
            >
              <i className="fas fa-edit"></i>
              Edit Profile
            </button>
          )}
        </div>

        <div className="profile-details">
          {editMode ? (
            <form className="edit-form" onSubmit={(e) => e.preventDefault()}>
              <div className="form-group">
                <label>First Name</label>
                <input
                  type="text"
                  value={editData.first_name}
                  onChange={(e) => setEditData({...editData, first_name: e.target.value})}
                  className="form-input"
                />
              </div>
              
              <div className="form-group">
                <label>Last Name</label>
                <input
                  type="text"
                  value={editData.last_name}
                  onChange={(e) => setEditData({...editData, last_name: e.target.value})}
                  className="form-input"
                />
              </div>
              
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={editData.email}
                  onChange={(e) => setEditData({...editData, email: e.target.value})}
                  className="form-input"
                />
              </div>

              <div className="form-actions">
                <button type="button" onClick={handleSave} className="btn btn-primary">
                  <i className="fas fa-save"></i>
                  Save Changes
                </button>
                <button type="button" onClick={handleCancel} className="btn btn-secondary">
                  <i className="fas fa-times"></i>
                  Cancel
                </button>
              </div>
            </form>
          ) : (
            <div className="info-grid">
              <div className="info-item">
                <label>Username</label>
                <span>{profile.username}</span>
              </div>
              
              <div className="info-item">
                <label>Email</label>
                <span>{profile.email || 'Not provided'}</span>
              </div>
              
              <div className="info-item">
                <label>First Name</label>
                <span>{profile.first_name || 'Not set'}</span>
              </div>
              
              <div className="info-item">
                <label>Last Name</label>
                <span>{profile.last_name || 'Not set'}</span>
              </div>
              
              <div className="info-item">
                <label>Organization</label>
                <span>{profile.organization?.name || 'No organization'}</span>
              </div>
              
              <div className="info-item">
                <label>Role</label>
                <span className={`role-badge ${profile.role?.toLowerCase()}`}>
                  {profile.role}
                </span>
              </div>
              
              <div className="info-item">
                <label>Status</label>
                <span className={`status-badge ${profile.is_active ? 'active' : 'inactive'}`}>
                  {profile.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              
              <div className="info-item">
                <label>Member Since</label>
                <span>{profile.created_at ? new Date(profile.created_at).toLocaleDateString() : 'Unknown'}</span>
              </div>
            </div>
          )}
        </div>
      </div>

      <style jsx>{`
        .user-profile {
          padding: 2rem;
          max-width: 1200px;
          margin: 0 auto;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .header {
          margin-bottom: 2rem;
        }

        .header h1 {
          margin: 0;
          color: #333;
          font-size: 2rem;
          font-weight: 600;
        }

        .error-banner {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 1rem 1.25rem;
          background-color: #f8d7da;
          color: #721c24;
          border: 1px solid #f5c6cb;
          border-radius: 8px;
          margin-bottom: 1.5rem;
        }

        .close-btn {
          background: none;
          border: none;
          color: #721c24;
          cursor: pointer;
          margin-left: auto;
          padding: 0.25rem;
          border-radius: 4px;
          transition: background-color 0.2s;
        }

        .close-btn:hover {
          background-color: rgba(0, 0, 0, 0.1);
        }

        .profile-card {
          background: white;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
          border: 1px solid #e9ecef;
          overflow: hidden;
        }

        .profile-header {
          padding: 2rem;
          background: #f8f9fa;
          border-bottom: 1px solid #e9ecef;
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
        }

        .profile-info {
          display: flex;
          align-items: center;
          gap: 1.5rem;
        }

        .profile-avatar {
          width: 80px;
          height: 80px;
          background: #dc3545;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 2rem;
          color: white;
          flex-shrink: 0;
        }

        .profile-title h2 {
          margin: 0 0 0.5rem 0;
          color: #333;
          font-size: 1.75rem;
          font-weight: 600;
        }

        .edit-profile-btn {
          background: #dc3545;
          color: white;
          border: none;
          padding: 0.75rem 1.5rem;
          border-radius: 8px;
          cursor: pointer;
          font-size: 0.875rem;
          font-weight: 500;
          display: flex;
          align-items: center;
          gap: 0.5rem;
          transition: all 0.2s;
        }

        .edit-profile-btn:hover {
          background: #c82333;
          transform: translateY(-1px);
        }

        .profile-details {
          padding: 2rem;
        }

        .info-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 1.5rem;
        }

        .info-item {
          background: #f8f9fa;
          padding: 1.25rem;
          border-radius: 8px;
          border: 1px solid #e9ecef;
          transition: all 0.2s;
        }

        .info-item:hover {
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          transform: translateY(-1px);
        }

        .info-item label {
          display: block;
          font-weight: 600;
          color: #6c757d;
          font-size: 0.75rem;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          margin-bottom: 0.5rem;
        }

        .info-item span {
          font-size: 1rem;
          color: #333;
          font-weight: 500;
        }

        .edit-form {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1.5rem;
          margin-bottom: 2rem;
        }

        .form-group {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .form-group label {
          font-weight: 600;
          color: #495057;
          font-size: 0.875rem;
        }

        .form-input {
          padding: 0.75rem;
          border: 2px solid #e9ecef;
          border-radius: 8px;
          font-size: 1rem;
          transition: all 0.2s;
          background: white;
        }

        .form-input:focus {
          outline: none;
          border-color: #dc3545;
          box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.1);
        }

        .form-actions {
          display: flex;
          gap: 1rem;
          justify-content: flex-end;
          grid-column: 1 / -1;
          padding-top: 1rem;
          border-top: 1px solid #e9ecef;
        }

        .btn {
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          font-size: 0.875rem;
          font-weight: 500;
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          transition: all 0.2s;
          text-decoration: none;
        }

        .btn-primary {
          background: #dc3545;
          color: white;
        }

        .btn-primary:hover {
          background: #c82333;
          transform: translateY(-1px);
          box-shadow: 0 4px 8px rgba(220, 53, 69, 0.3);
        }

        .btn-secondary {
          background: #6c757d;
          color: white;
        }

        .btn-secondary:hover {
          background: #5a6268;
          transform: translateY(-1px);
          box-shadow: 0 4px 8px rgba(108, 117, 125, 0.3);
        }

        .role-badge,
        .status-badge {
          padding: 0.5rem 1rem;
          border-radius: 20px;
          font-size: 0.75rem;
          font-weight: 600;
          width: fit-content;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .role-badge.admin {
          background: #e7f3ff;
          color: #1976d2;
          border: 1px solid #bbdefb;
        }

        .role-badge.viewer {
          background: #f3e5f5;
          color: #7b1fa2;
          border: 1px solid #e1bee7;
        }

        .role-badge.publisher {
          background: #fff8e1;
          color: #f57f17;
          border: 1px solid #ffecb3;
        }

        .role-badge.bluevisionadmin {
          background: #e8f5e8;
          color: #2e7d32;
          border: 1px solid #c8e6c9;
        }

        .status-badge.active {
          background: #e8f5e8;
          color: #2e7d32;
          border: 1px solid #c8e6c9;
        }

        .status-badge.inactive {
          background: #ffebee;
          color: #c62828;
          border: 1px solid #ffcdd2;
        }

        .loading-state,
        .error-state {
          text-align: center;
          padding: 4rem 2rem;
          background: white;
          border-radius: 12px;
          border: 1px solid #e9ecef;
        }

        .loading-state i {
          font-size: 3rem;
          color: #dc3545;
          margin-bottom: 1rem;
          display: block;
        }

        .error-state i {
          font-size: 3rem;
          color: #dc3545;
          margin-bottom: 1rem;
          display: block;
        }

        .loading-state p,
        .error-state p {
          margin: 0 0 1.5rem 0;
          color: #6c757d;
          font-size: 1.125rem;
        }

        @media (max-width: 768px) {
          .user-profile {
            padding: 1rem;
          }
          
          .profile-header {
            flex-direction: column;
            gap: 1.5rem;
            align-items: flex-start;
          }
          
          .profile-info {
            flex-direction: column;
            text-align: center;
            gap: 1rem;
          }
          
          .info-grid {
            grid-template-columns: 1fr;
          }
          
          .edit-form {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default UserProfile;