import React, { useState, useEffect } from 'react';

const UserProfile = ({ active }) => {
  if (!active) return null;
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [editData, setEditData] = useState({});

  useEffect(() => {
    fetchProfile();
  }, []);

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
        setProfile(data.user);
        setEditData({
          first_name: data.user.first_name || '',
          last_name: data.user.last_name || '',
          email: data.user.email || ''
        });
      } else {
        throw new Error('Failed to fetch profile');
      }
    } catch (err) {
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
        setProfile(data.user);
        setEditMode(false);
      } else {
        throw new Error('Failed to update profile');
      }
    } catch (err) {
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
  };

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

  return (
    <div className="user-profile">
      <div className="header">
        <h2>User Profile</h2>
        {!editMode && (
          <button 
            className="btn btn-primary"
            onClick={() => setEditMode(true)}
          >
            <i className="fas fa-edit"></i>
            Edit Profile
          </button>
        )}
      </div>

      <div className="profile-card">
        <div className="profile-header">
          <div className="profile-avatar">
            <i className="fas fa-user"></i>
          </div>
          <div className="profile-title">
            <h3>{profile.first_name} {profile.last_name}</h3>
            <p className="profile-role">{profile.role}</p>
          </div>
        </div>

        <div className="profile-details">
          {editMode ? (
            <form className="edit-form">
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
                <span>{profile.email}</span>
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
                <label>Joined</label>
                <span>{new Date(profile.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          )}
        </div>
      </div>

      <style jsx>{`
        .user-profile {
          padding: 20px;
          max-width: 800px;
          margin: 0 auto;
        }

        .header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .header h2 {
          margin: 0;
          color: #333;
        }

        .profile-card {
          background: white;
          border-radius: 12px;
          box-shadow: 0 4px 6px rgba(0,0,0,0.1);
          overflow: hidden;
        }

        .profile-header {
          background: linear-gradient(135deg, #0056b3, #004494);
          color: white;
          padding: 30px;
          display: flex;
          align-items: center;
          gap: 20px;
        }

        .profile-avatar {
          width: 80px;
          height: 80px;
          background: rgba(255,255,255,0.2);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 32px;
        }

        .profile-title h3 {
          margin: 0 0 5px 0;
          font-size: 24px;
          font-weight: 600;
        }

        .profile-role {
          margin: 0;
          opacity: 0.9;
          font-size: 16px;
        }

        .profile-details {
          padding: 30px;
        }

        .info-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 20px;
        }

        .info-item {
          display: flex;
          flex-direction: column;
          gap: 5px;
        }

        .info-item label {
          font-weight: 600;
          color: #495057;
          font-size: 14px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .info-item span {
          font-size: 16px;
          color: #333;
        }

        .edit-form {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .form-group {
          display: flex;
          flex-direction: column;
          gap: 5px;
        }

        .form-group label {
          font-weight: 600;
          color: #495057;
          font-size: 14px;
        }

        .form-input {
          padding: 12px;
          border: 1px solid #dee2e6;
          border-radius: 6px;
          font-size: 14px;
          transition: border-color 0.2s;
        }

        .form-input:focus {
          outline: none;
          border-color: #0056b3;
        }

        .form-actions {
          display: flex;
          gap: 10px;
          justify-content: flex-end;
        }

        .btn {
          padding: 10px 20px;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          display: inline-flex;
          align-items: center;
          gap: 8px;
          transition: background-color 0.2s;
        }

        .btn-primary {
          background: #0056b3;
          color: white;
        }

        .btn-primary:hover {
          background: #004494;
        }

        .btn-secondary {
          background: #6c757d;
          color: white;
        }

        .btn-secondary:hover {
          background: #5a6268;
        }

        .role-badge,
        .status-badge {
          padding: 6px 12px;
          border-radius: 15px;
          font-size: 12px;
          font-weight: 600;
          width: fit-content;
        }

        .role-badge.admin {
          background: #e3f2fd;
          color: #1976d2;
        }

        .role-badge.user {
          background: #f3e5f5;
          color: #7b1fa2;
        }

        .role-badge.bluevisionadmin {
          background: #e8f5e8;
          color: #2e7d32;
        }

        .status-badge.active {
          background: #e8f5e8;
          color: #2e7d32;
        }

        .status-badge.inactive {
          background: #fff3e0;
          color: #f57c00;
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

export default UserProfile;