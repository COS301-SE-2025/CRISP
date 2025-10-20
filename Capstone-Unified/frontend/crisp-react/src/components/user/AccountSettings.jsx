const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
import React, { useState, useEffect } from 'react';

const ChangePasswordModal = ({ isOpen, onClose, onPasswordChanged }) => {
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    if (newPassword !== confirmPassword) {
      setError('New passwords do not match');
      setIsLoading(false);
      return;
    }

    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters long');
      setIsLoading(false);
      return;
    }

    try {
      const token = localStorage.getItem('crisp_auth_token');
      const response = await fetch(`${API_BASE_URL}/api/auth/change-password/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
          confirm_password: confirmPassword
        })
      });

      if (response.ok) {
        onPasswordChanged();
        onClose();
        setCurrentPassword('');
        setNewPassword('');
        setConfirmPassword('');
      } else {
        const data = await response.json();
        setError(data.error || 'Failed to change password');
      }
    } catch (error) {
      setError('Failed to change password');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h3>Change Password</h3>
          <button className="close-btn" onClick={onClose}>
            <i className="fas fa-times"></i>
          </button>
        </div>
        
        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleSubmit} className="password-form">
          <div className="form-group">
            <label>Current Password</label>
            <input
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              className="form-input"
              required
            />
          </div>
          
          <div className="form-group">
            <label>New Password</label>
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="form-input"
              required
              minLength="8"
            />
          </div>
          
          <div className="form-group">
            <label>Confirm New Password</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="form-input"
              required
            />
          </div>
          
          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose} disabled={isLoading}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={isLoading}>
              {isLoading ? 'Changing...' : 'Change Password'}
            </button>
          </div>
        </form>
      </div>

      <style jsx>{`
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          justify-content: center;
          align-items: center;
          z-index: 9999;
        }

        .modal-content {
          background: white;
          border-radius: 12px;
          max-width: 500px;
          width: 90%;
          max-height: 90vh;
          overflow-y: auto;
          box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }

        .modal-header {
          padding: 20px 30px;
          border-bottom: 1px solid #e9ecef;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .modal-header h3 {
          margin: 0;
          color: #333;
        }

        .close-btn {
          background: none;
          border: none;
          font-size: 18px;
          color: #6c757d;
          cursor: pointer;
          padding: 5px;
          border-radius: 4px;
          transition: background-color 0.2s;
        }

        .close-btn:hover {
          background: #f8f9fa;
        }

        .password-form {
          padding: 30px;
        }

        .form-group {
          margin-bottom: 20px;
        }

        .form-group label {
          display: block;
          margin-bottom: 8px;
          font-weight: 600;
          color: #495057;
        }

        .form-input {
          width: 100%;
          padding: 12px;
          border: 1px solid #dee2e6;
          border-radius: 6px;
          font-size: 14px;
          transition: border-color 0.2s;
          box-sizing: border-box;
        }

        .form-input:focus {
          outline: none;
          border-color: #0056b3;
        }

        .error-message {
          background: #f8d7da;
          color: #721c24;
          padding: 12px;
          border-radius: 6px;
          margin: 20px 30px;
          border: 1px solid #f5c6cb;
        }

        .modal-actions {
          display: flex;
          gap: 12px;
          justify-content: flex-end;
        }

        .btn {
          padding: 12px 24px;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          transition: background-color 0.2s;
        }

        .btn-primary {
          background: #0056b3;
          color: white;
        }

        .btn-primary:hover:not(:disabled) {
          background: #004494;
        }

        .btn-secondary {
          background: #6c757d;
          color: white;
        }

        .btn-secondary:hover:not(:disabled) {
          background: #5a6268;
        }

        .btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  );
};

const AccountSettings = ({ active }) => {
  if (!active) return null;
  
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [editData, setEditData] = useState({});
  const [showChangePassword, setShowChangePassword] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('crisp_auth_token');
      const response = await fetch(`${API_BASE_URL}/api/auth/profile/`, {
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
      const response = await fetch(`${API_BASE_URL}/api/auth/profile/update/`, {
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

  const handlePasswordChanged = () => {
    setSuccessMessage('Password changed successfully!');
    setTimeout(() => setSuccessMessage(''), 3000);
  };

  if (loading) {
    return (
      <div className="account-settings">
        <div className="loading-state">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading account settings...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="account-settings">
        <div className="error-state">
          <i className="fas fa-exclamation-triangle"></i>
          <p>Error loading settings: {error}</p>
          <button onClick={fetchProfile} className="btn btn-primary">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="account-settings">
      <div className="settings-header">
        <h2>Account Settings</h2>
        <p>Manage your account information and security settings</p>
      </div>

      {successMessage && (
        <div className="success-message">
          <i className="fas fa-check-circle"></i>
          {successMessage}
        </div>
      )}

      <div className="settings-container">
        {/* Profile Information Section */}
        <div className="settings-card">
          <div className="card-header">
            <h3>Profile Information</h3>
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

          <div className="profile-section">
            <div className="profile-avatar-section">
              <div className="profile-avatar">
                <i className="fas fa-user"></i>
              </div>
              <div className="profile-info">
                <h4>{profile.first_name} {profile.last_name}</h4>
                <p className="profile-role">{profile.role}</p>
                <p className="profile-org">{profile.organization?.name || 'No organization'}</p>
              </div>
            </div>

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
                  <label>Status</label>
                  <span className={`status-badge ${profile.is_active ? 'active' : 'inactive'}`}>
                    {profile.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                
                <div className="info-item">
                  <label>Member Since</label>
                  <span>{new Date(profile.created_at || profile.date_joined).toLocaleDateString()}</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Security Section */}
        <div className="settings-card">
          <div className="card-header">
            <h3>Security</h3>
          </div>

          <div className="security-section">
            <div className="security-item">
              <div className="security-info">
                <h4>Password</h4>
                <p>Change your account password</p>
              </div>
              <button 
                className="btn btn-outline"
                onClick={() => setShowChangePassword(true)}
              >
                <i className="fas fa-key"></i>
                Change Password
              </button>
            </div>
          </div>
        </div>

        {/* Account Information Section */}
        <div className="settings-card">
          <div className="card-header">
            <h3>Account Information</h3>
          </div>

          <div className="account-info">
            <div className="info-grid">
              <div className="info-item">
                <label>Role</label>
                <span className={`role-badge ${profile.role?.toLowerCase()}`}>
                  {profile.role}
                </span>
              </div>
              
              <div className="info-item">
                <label>Organization</label>
                <span>{profile.organization?.name || 'No organization'}</span>
              </div>
              
              <div className="info-item">
                <label>Last Login</label>
                <span>{profile.last_login ? new Date(profile.last_login).toLocaleString() : 'Never'}</span>
              </div>
              
              <div className="info-item">
                <label>Account Created</label>
                <span>{new Date(profile.created_at || profile.date_joined).toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <ChangePasswordModal
        isOpen={showChangePassword}
        onClose={() => setShowChangePassword(false)}
        onPasswordChanged={handlePasswordChanged}
      />

      <style jsx>{`
        .account-settings {
          padding: 20px;
          max-width: 1200px;
          margin: 0 auto;
        }

        .settings-header {
          margin-bottom: 30px;
        }

        .settings-header h2 {
          margin: 0 0 8px 0;
          color: #333;
          font-size: 28px;
        }

        .settings-header p {
          margin: 0;
          color: #6c757d;
          font-size: 16px;
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

        .settings-container {
          display: flex;
          flex-direction: column;
          gap: 24px;
        }

        .settings-card {
          background: white;
          border-radius: 12px;
          box-shadow: 0 4px 6px rgba(0,0,0,0.1);
          overflow: hidden;
        }

        .card-header {
          background: #f8f9fa;
          padding: 20px 30px;
          border-bottom: 1px solid #e9ecef;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .card-header h3 {
          margin: 0;
          color: #333;
          font-size: 20px;
        }

        .profile-section,
        .security-section,
        .account-info {
          padding: 30px;
        }

        .profile-avatar-section {
          display: flex;
          align-items: center;
          gap: 20px;
          margin-bottom: 30px;
        }

        .profile-avatar {
          width: 80px;
          height: 80px;
          background: linear-gradient(135deg, #0056b3, #004494);
          color: white;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 32px;
        }

        .profile-info h4 {
          margin: 0 0 5px 0;
          color: #333;
          font-size: 24px;
        }

        .profile-role {
          margin: 0 0 5px 0;
          color: #0056b3;
          font-weight: 600;
        }

        .profile-org {
          margin: 0;
          color: #6c757d;
          font-size: 14px;
        }

        .edit-form {
          display: flex;
          flex-direction: column;
          gap: 20px;
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
          transition: border-color 0.2s;
        }

        .form-input:focus {
          outline: none;
          border-color: #0056b3;
        }

        .form-actions {
          display: flex;
          gap: 12px;
          justify-content: flex-end;
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

        .security-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 20px 0;
        }

        .security-info h4 {
          margin: 0 0 5px 0;
          color: #333;
        }

        .security-info p {
          margin: 0;
          color: #6c757d;
          font-size: 14px;
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
          transition: all 0.2s;
          text-decoration: none;
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

        .btn-outline {
          background: transparent;
          color: #0056b3;
          border: 1px solid #0056b3;
        }

        .btn-outline:hover {
          background: #0056b3;
          color: white;
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

        @media (max-width: 768px) {
          .account-settings {
            padding: 10px;
          }

          .form-row {
            grid-template-columns: 1fr;
          }

          .profile-avatar-section {
            flex-direction: column;
            text-align: center;
          }

          .security-item {
            flex-direction: column;
            gap: 15px;
            align-items: flex-start;
          }
        }
      `}</style>
    </div>
  );
};

export default AccountSettings;