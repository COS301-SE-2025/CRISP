import React, { useState, useEffect } from 'react';

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);

  useEffect(() => {
    console.log('UserManagement useEffect triggered, calling fetchUsers');
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    console.log('=== fetchUsers called ===');
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token') || localStorage.getItem('token');
      console.log('Using token:', token ? 'Token found' : 'No token');
      console.log('Available localStorage keys:', Object.keys(localStorage));
      
      const response = await fetch('http://localhost:8000/api/users/', {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : '',
        },
      });
      console.log('Fetch completed, processing response...');
      
      console.log('Response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Full API response:', JSON.stringify(data, null, 2));
        
        // Handle Django Rest Framework pagination response
        let users = [];
        if (data.results && data.results.users) {
          // Paginated response with custom wrapper
          users = data.results.users;
          console.log('Extracted from paginated data.results.users:', users);
        } else if (data.users) {
          // Direct users array
          users = data.users;
          console.log('Extracted from data.users:', users);
        } else if (data.results && Array.isArray(data.results)) {
          // Paginated response with direct array
          users = data.results;
          console.log('Extracted from paginated data.results (array):', users);
        } else if (Array.isArray(data)) {
          // Direct array response
          users = data;
          console.log('Data is direct array:', users);
        } else {
          console.log('Could not find users in response. Available keys:', Object.keys(data));
          console.log('Data structure:', data);
        }
        
        console.log('Final users array:', users);
        console.log('Users array length:', users.length);
        setUsers(users);
      } else {
        const errorText = await response.text();
        console.log('Error response:', errorText);
        throw new Error(`Failed to fetch users: ${response.status} ${errorText}`);
      }
    } catch (err) {
      console.error('Fetch error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="user-management">
        <div className="loading-state">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading users...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="user-management">
        <div className="error-state">
          <i className="fas fa-exclamation-triangle"></i>
          <p>Error loading users: {error}</p>
          <button onClick={fetchUsers} className="btn btn-primary">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="user-management">
      <div className="header">
        <h2>User Management</h2>
        <div className="header-buttons">
          <button 
            className="btn btn-secondary"
            onClick={() => {
              console.log('Debug button clicked - calling fetchUsers');
              fetchUsers();
            }}
          >
            <i className="fas fa-refresh"></i>
            Debug Reload Users
          </button>
          <button 
            className="btn btn-primary"
            onClick={() => setShowAddModal(true)}
          >
            <i className="fas fa-plus"></i>
            Add User
          </button>
        </div>
      </div>

      <div className="users-table">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Organization</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.length === 0 ? (
              <tr>
                <td colSpan="6" className="no-data">
                  No users found. Click "Add User" to get started.
                </td>
              </tr>
            ) : (
              users.map(user => (
                <tr key={user.id}>
                  <td>{user.first_name} {user.last_name}</td>
                  <td>{user.email}</td>
                  <td>
                    <span className={`role-badge ${user.role?.toLowerCase()}`}>
                      {user.role}
                    </span>
                  </td>
                  <td>{user.organization?.name || 'N/A'}</td>
                  <td>
                    <span className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}>
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td>
                    <div className="actions">
                      <button className="btn btn-sm btn-outline">
                        <i className="fas fa-edit"></i>
                      </button>
                      <button className="btn btn-sm btn-outline">
                        <i className="fas fa-key"></i>
                      </button>
                      <button className="btn btn-sm btn-danger">
                        <i className="fas fa-trash"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {showAddModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>Add New User</h3>
              <button 
                className="close-btn"
                onClick={() => setShowAddModal(false)}
              >
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              <p>User creation form will be implemented here.</p>
              <p>This requires authentication integration first.</p>
            </div>
            <div className="modal-footer">
              <button 
                className="btn btn-secondary"
                onClick={() => setShowAddModal(false)}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .user-management {
          padding: 20px;
          max-width: 1200px;
          margin: 0 auto;
        }

        .header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .header-buttons {
          display: flex;
          gap: 10px;
        }

        .header h2 {
          margin: 0;
          color: #333;
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

        .btn-primary:hover {
          background: #004494;
        }

        .btn-secondary {
          background: #6c757d;
          color: white;
        }

        .btn-outline {
          background: transparent;
          border: 1px solid #dee2e6;
          color: #495057;
        }

        .btn-sm {
          padding: 4px 8px;
          font-size: 12px;
        }

        .btn-danger {
          background: #dc3545;
          color: white;
        }

        .users-table table {
          width: 100%;
          border-collapse: collapse;
          background: white;
          border-radius: 8px;
          overflow: hidden;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .users-table th,
        .users-table td {
          padding: 12px;
          text-align: left;
          border-bottom: 1px solid #dee2e6;
        }

        .users-table th {
          background: #f8f9fa;
          font-weight: 600;
          color: #495057;
        }

        .role-badge,
        .status-badge {
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 500;
        }

        .role-badge.admin {
          background: #e3f2fd;
          color: #1976d2;
        }

        .role-badge.user {
          background: #f3e5f5;
          color: #7b1fa2;
        }

        .status-badge.active {
          background: #e8f5e8;
          color: #2e7d32;
        }

        .status-badge.inactive {
          background: #fff3e0;
          color: #f57c00;
        }

        .actions {
          display: flex;
          gap: 8px;
        }

        .no-data {
          text-align: center;
          color: #6c757d;
          font-style: italic;
          padding: 40px;
        }

        .loading-state,
        .error-state {
          text-align: center;
          padding: 40px;
        }

        .loading-state i {
          font-size: 24px;
          color: #0056b3;
          margin-bottom: 10px;
        }

        .error-state i {
          font-size: 24px;
          color: #dc3545;
          margin-bottom: 10px;
        }

        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0,0,0,0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }

        .modal {
          background: white;
          border-radius: 8px;
          width: 90%;
          max-width: 500px;
          box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .modal-header {
          padding: 20px;
          border-bottom: 1px solid #dee2e6;
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
        }

        .modal-body {
          padding: 20px;
        }

        .modal-footer {
          padding: 20px;
          border-top: 1px solid #dee2e6;
          display: flex;
          justify-content: flex-end;
          gap: 10px;
        }
      `}</style>
    </div>
  );
};

export default UserManagement;