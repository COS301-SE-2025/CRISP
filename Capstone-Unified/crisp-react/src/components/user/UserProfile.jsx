import React, { useState, useEffect } from 'react';

const UserProfile = ({ active }) => {
  if (!active) return null;
  
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [editData, setEditData] = useState({});
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      setError(null);
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
      const response = await fetch('http://localhost:8000/api/auth/profile/update/', {
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
        setSuccessMessage('Profile updated successfully!');
        setTimeout(() => setSuccessMessage(''), 3000);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to update profile');
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
    setError(null);
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
      {successMessage && (
        <div className="success-message">
          <i className="fas fa-check-circle"></i>
          {successMessage}
        </div>
      )}

      {error && !loading && (
        <div className="error-message">
          <i className="fas fa-exclamation-triangle"></i>
          {error}
        </div>
      )}

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
              <div className="form-row">
                <div className="form-group">
                  <label>First Name</label>
                  <input
                    type="text"
                    value={editData.first_name}
                    onChange={(e) => setEditData({...editData, first_name: e.target.value})}
                    className="form-input"
                    placeholder="Enter your first name"
                  />
                </div>
                
                <div className="form-group">
                  <label>Last Name</label>
                  <input
                    type="text"
                    value={editData.last_name}
                    onChange={(e) => setEditData({...editData, last_name: e.target.value})}
                    className="form-input"
                    placeholder="Enter your last name"
                  />
                </div>
              </div>
              
              <div className="form-group">
                <label>Email Address</label>
                <input
                  type="email"
                  value={editData.email}
                  onChange={(e) => setEditData({...editData, email: e.target.value})}
                  className="form-input"
                  placeholder="Enter your email address"
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
            <div className="profile-content">
              <div className="info-section">
                <h4>Personal Information</h4>
                <div className="info-grid">
                  <div className="info-item">
                    <label>Username</label>
                    <span>{profile.username}</span>
                  </div>
                  
                  <div className="info-item">
                    <label>Email Address</label>
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
                </div>
              </div>

              <div className="info-section">
                <h4>Account Information</h4>
                <div className="info-grid">
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
                    <label>Account Status</label>
                    <span className={`status-badge ${profile.is_active ? 'active' : 'inactive'}`}>
                      {profile.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  
                  <div className="info-item">
                    <label>Verified</label>
                    <span className={`status-badge ${profile.is_verified ? 'verified' : 'unverified'}`}>
                      {profile.is_verified ? 'Verified' : 'Unverified'}
                    </span>
                  </div>
                  
                  <div className="info-item">
                    <label>Member Since</label>
                    <span>{new Date(profile.created_at || profile.date_joined).toLocaleDateString()}</span>
                  </div>
                  
                  <div className="info-item">
                    <label>Last Login</label>
                    <span>{profile.last_login ? new Date(profile.last_login).toLocaleString() : 'Never'}</span>
                  </div>
                </div>
              </div>

              <div className="profile-actions">
                <h2>My Profile</h2>
                <button 
                  className="btn btn-primary"
                  onClick={() => setEditMode(true)}
                >
                  <i className="fas fa-edit"></i>
                  Edit Profile
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      <style jsx>{`
        .user-profile {
          padding: 20px;
          max-width: 1000px;
          margin: 0 auto;
        }

        .profile-actions {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-top: 30px;
          padding-top: 20px;
          border-top: 2px solid #f1f3f4;
        }

        .profile-actions h2 {
          margin: 0;
          color: #333;
          font-size: 28px;
        }

        .success-message {
          background: #d4edda;
          color: #155724;
          padding: 12px 16px;
          border-radius: 6px;
          margin-bottom: 20px;
          border: 1px solid #c3e6cb;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .error-message {
          background: #f8d7da;
          color: #721c24;
          padding: 12px 16px;
          border-radius: 6px;
          margin-bottom: 20px;
          border: 1px solid #f5c6cb;
          display: flex;
          align-items: center;
          gap: 8px;
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

        .profile-content {
          display: flex;
          flex-direction: column;
          gap: 30px;
        }

        .info-section h4 {
          margin: 0 0 20px 0;
          color: #333;
          font-size: 18px;
          font-weight: 600;
          border-bottom: 2px solid #f1f3f4;
          padding-bottom: 10px;
        }

        .info-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 20px;
        }

        .info-item {
          display: flex;
          flex-direction: column;
          gap: 8px;
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
          gap: 25px;
        }

        .form-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
        }

        .form-group {
          display: flex;
          flex-direction: column;
          gap: 8px;
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
          transition: border-color 0.2s, box-shadow 0.2s;
        }

        .form-input:focus {
          outline: none;
          border-color: #0056b3;
          box-shadow: 0 0 0 2px rgba(0, 86, 179, 0.1);
        }

        .form-input::placeholder {
          color: #adb5bd;
        }

        .form-actions {
          display: flex;
          gap: 12px;
          justify-content: flex-end;
          margin-top: 10px;
        }

        .btn {
          padding: 12px 24px;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          display: inline-flex;
          align-items: center;
          gap: 8px;
          transition: all 0.2s;
          text-decoration: none;
        }

        .btn-primary {
          background: #0056b3;
          color: white;
        }

        .btn-primary:hover {
          background: #004494;
          transform: translateY(-1px);
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

        .status-badge.active,
        .status-badge.verified {
          background: #e8f5e8;
          color: #2e7d32;
        }

        .status-badge.inactive,
        .status-badge.unverified {
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

        .error-state p {
          margin-bottom: 20px;
          color: #dc3545;
        }

        @media (max-width: 768px) {
          .user-profile {
            padding: 10px;
          }

          .profile-actions {
            flex-direction: column;
            gap: 15px;
            align-items: flex-start;
          }

          .form-row {
            grid-template-columns: 1fr;
          }

          .profile-header {
            flex-direction: column;
            text-align: center;
          }

          .info-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default UserProfile;