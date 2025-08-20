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
      <div className="user-profile-page">
        <div className="loading-state">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading profile...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="user-profile-page">
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
    <div className="user-profile-page">
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
          <div className="profile-info">
            <div className="profile-avatar">
              <i className="fas fa-user"></i>
            </div>
            <div className="profile-title">
              <h3>{editMode ? `${editData.first_name} ${editData.last_name}` : `${profile.first_name || ''} ${profile.last_name || ''}`.trim() || profile.username}</h3>
              <p className="profile-role">{profile.role}</p>
            </div>
          </div>
          {!editMode && (
            <div className="header-actions">
              <button 
                className="btn btn-primary"
                onClick={() => setEditMode(true)}
              >
                <i className="fas fa-edit"></i>
                Edit Profile
              </button>
            </div>
          )}
        </div>

        <div className="profile-details">
          <div className="profile-grid">
            <div className="info-section">
              <h4>Personal Information</h4>
              <table className="profile-table">
                <tbody>
                  <tr>
                    <th>Username</th>
                    <td>{profile.username}</td>
                  </tr>
                  <tr>
                    <th>Email Address</th>
                    <td>
                      {editMode ? (
                        <input
                          type="email"
                          value={editData.email}
                          onChange={(e) => setEditData({...editData, email: e.target.value})}
                          className="form-input inline-edit"
                          placeholder="Enter your email address"
                        />
                      ) : (
                        profile.email
                      )}
                    </td>
                  </tr>
                  <tr>
                    <th>First Name</th>
                    <td>
                      {editMode ? (
                        <input
                          type="text"
                          value={editData.first_name}
                          onChange={(e) => setEditData({...editData, first_name: e.target.value})}
                          className="form-input inline-edit"
                          placeholder="Enter your first name"
                        />
                      ) : (
                        profile.first_name || 'Not set'
                      )}
                    </td>
                  </tr>
                  <tr>
                    <th>Last Name</th>
                    <td>
                      {editMode ? (
                        <input
                          type="text"
                          value={editData.last_name}
                          onChange={(e) => setEditData({...editData, last_name: e.target.value})}
                          className="form-input inline-edit"
                          placeholder="Enter your last name"
                        />
                      ) : (
                        profile.last_name || 'Not set'
                      )}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div className="info-section">
              <h4>Account Information</h4>
              <table className="profile-table">
                <tbody>
                  <tr>
                    <th>Organization</th>
                    <td>{profile.organization?.name || 'No organization'}</td>
                  </tr>
                  <tr>
                    <th>Role</th>
                    <td>
                      <span className={`role-badge ${profile.role?.toLowerCase()}`}>
                        {profile.role}
                      </span>
                    </td>
                  </tr>
                  <tr>
                    <th>Account Status</th>
                    <td>
                      <span className={`status-badge ${profile.is_active ? 'active' : 'inactive'}`}>
                        {profile.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                  </tr>
                  <tr>
                    <th>Verified</th>
                    <td>
                      <span className={`status-badge ${profile.is_verified ? 'verified' : 'unverified'}`}>
                        {profile.is_verified ? 'Verified' : 'Unverified'}
                      </span>
                    </td>
                  </tr>
                  <tr>
                    <th>Member Since</th>
                    <td>{new Date(profile.created_at || profile.date_joined).toLocaleDateString()}</td>
                  </tr>
                  <tr>
                    <th>Last Login</th>
                    <td>{profile.last_login ? new Date(profile.last_login).toLocaleString() : 'Never'}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {editMode && (
            <div className="save-section">
              <div className="form-actions">
                <button type="button" onClick={handleCancel} className="btn btn-secondary">
                  <i className="fas fa-times"></i>
                  Cancel
                </button>
                <button type="button" onClick={handleSave} className="btn btn-primary">
                  <i className="fas fa-save"></i>
                  Save Changes
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      <style jsx>{`
        .user-profile-page {
          max-width: 1200px;
          margin: 0 auto;
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
          box-shadow: 0 4px 12px rgba(0,0,0,0.08);
          overflow: hidden;
          border: 1px solid #dee2e6;
        }

        .profile-header {
          background: #f8f9fa;
          color: #333;
          padding: 24px 30px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 20px;
          border-bottom: 1px solid #dee2e6;
        }

        .profile-header .profile-info {
          display: flex;
          align-items: center;
          gap: 20px;
        }

        .header-actions {
          display: flex;
          gap: 10px;
        }

        .profile-avatar {
          width: 60px;
          height: 60px;
          background: linear-gradient(135deg, #0056b3, #004494);
          color: white;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 28px;
        }

        .profile-title h3 {
          margin: 0 0 4px 0;
          font-size: 22px;
          font-weight: 600;
        }

        .profile-role {
          margin: 0;
          opacity: 0.8;
          font-size: 16px;
          color: #0056b3;
          font-weight: 500;
        }

        .profile-details {
          padding: 30px;
        }

        .profile-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
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

        .profile-table {
          width: 100%;
          border-collapse: collapse;
        }

        .profile-table th,
        .profile-table td {
          padding: 15px 10px;
          text-align: left;
          border-bottom: 1px solid #f1f3f4;
          font-size: 15px;
          vertical-align: middle;
        }

        .profile-table th {
          font-weight: 600;
          color: #6c757d;
          width: 150px;
        }

        .profile-table td {
          color: #333;
        }

        .profile-table tbody tr:last-child th,
        .profile-table tbody tr:last-child td {
          border-bottom: none;
        }

        .form-input.inline-edit {
          padding: 8px 12px;
          border-radius: 6px;
          border: 1px solid var(--medium-gray);
          width: 240px;
          background-color: white;
          font-size: 14px;
          transition: all 0.3s;
          color: black;
        }

        .form-input.inline-edit:focus {
          outline: none;
          border-color: #0056b3;
          box-shadow: 0 0 0 2px rgba(0, 86, 179, 0.1);
        }

        .save-section {
          margin-top: 30px;
          padding-top: 20px;
          border-top: 1px solid #dee2e6;
        }

        .form-actions {
          display: flex;
          gap: 12px;
          justify-content: flex-end;
          margin-top: 0;
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

        @media (max-width: 992px) {
          .profile-grid {
            grid-template-columns: 1fr;
          }
        }

        @media (max-width: 768px) {
          .user-profile-page {
            padding: 10px;
          }

          .profile-header {
            flex-direction: column;
            text-align: center;
            gap: 15px;
          }

          .header-actions {
            width: 100%;
            justify-content: center;
          }
        }
      `}</style>
    </div>
  );
};

export default UserProfile;