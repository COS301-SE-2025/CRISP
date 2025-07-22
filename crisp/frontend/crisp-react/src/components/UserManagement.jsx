import React, { useState, useEffect } from 'react';
import { getUsersList, createUser, updateUser, deactivateUser, reactivateUser, deleteUser, changeUsername, getUserDetails, getOrganizations } from '../api.js';
import LoadingSpinner from './LoadingSpinner.jsx';

// Import alias for the API to avoid conflicts
import * as api from '../api.js';

const UserManagement = ({ active = true, initialSection = null }) => {
  console.log('UserManagement rendered with props:', { active, initialSection });
  const [users, setUsers] = useState([]);
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(() => {
    // Use initialSection prop first, then URL params
    if (initialSection === 'create') return true;
    const urlParams = new URLSearchParams(window.location.search);
    const section = urlParams.get('section');
    return section === 'create';
  });
  const [modalMode, setModalMode] = useState(() => {
    // Set modal mode based on initialSection prop or URL section
    if (initialSection === 'create') return 'add';
    const urlParams = new URLSearchParams(window.location.search);
    const section = urlParams.get('section');
    return section === 'create' ? 'add' : 'add';
  });
  const [selectedUser, setSelectedUser] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [modalLoading, setModalLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [operationLoading, setOperationLoading] = useState(false);
  const [showActionsPopup, setShowActionsPopup] = useState(false);
  const [selectedUserForActions, setSelectedUserForActions] = useState(null);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    role: 'viewer',
    organization_id: '',
    is_verified: false,
    is_active: true
  });

  const roles = ['admin', 'publisher', 'viewer'];

  useEffect(() => {
    if (active) {
      loadUsers();
      loadOrganizations();
    }
  }, [active]);

  // Handle initialSection prop changes
  useEffect(() => {
    if (initialSection === 'create') {
      console.log('UserManagement: Opening create modal from prop');
      setShowModal(true);
      setModalMode('add');
    } else if (initialSection === 'roles' || initialSection === 'passwords') {
      console.log('UserManagement: Section from prop:', initialSection);
      setShowModal(false);
    }
  }, [initialSection]);

  // Handle URL parameter changes for section navigation
  useEffect(() => {
    const handleUrlChange = () => {
      const urlParams = new URLSearchParams(window.location.search);
      const section = urlParams.get('section');
      
      if (section === 'create') {
        setShowModal(true);
        setModalMode('add');
      } else if (section === 'roles' || section === 'passwords') {
        // For roles and passwords, we can show a message or highlight relevant sections
        setShowModal(false);
      }
    };

    // Listen for popstate events (back/forward navigation)
    window.addEventListener('popstate', handleUrlChange);
    
    return () => {
      window.removeEventListener('popstate', handleUrlChange);
    };
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      // Add delay to show loading spinner
      await new Promise(resolve => setTimeout(resolve, 1000));
      const response = await api.getUsersList();
      console.log('Users API response:', response); // Debug log
      console.log('Full response object:', JSON.stringify(response, null, 2));
      
      // More robust data extraction
      let usersData = [];
      if (response.data && response.data.users) {
        usersData = response.data.users;
      } else if (response.users) {
        usersData = response.users;
      } else if (response.data && Array.isArray(response.data)) {
        usersData = response.data;
      } else if (Array.isArray(response)) {
        usersData = response;
      }
      
      console.log('Extracted users data:', usersData);
      console.log('Users data length:', usersData.length);
      setUsers(Array.isArray(usersData) ? usersData : []);
    } catch (err) {
      console.error('Failed to load users:', err);
      setError('Failed to load users: ' + err.message);
      setUsers([]); // Ensure users is always an array
    } finally {
      setLoading(false);
    }
  };

  const loadOrganizations = async () => {
    try {
      const response = await api.getOrganizations();
      console.log('Organizations API response:', response); // Debug log
      const orgData = response.data?.organizations || response.organizations || response.data || [];
      setOrganizations(Array.isArray(orgData) ? orgData : []);
    } catch (err) {
      console.error('Failed to load organizations:', err);
      setOrganizations([]); // Ensure organizations is always an array
    }
  };

  const handleAddUser = () => {
    setModalMode('add');
    setSelectedUser(null);
    setFormData({
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      password: '',
      role: 'viewer',
      organization_id: '',
      is_verified: false,
      is_active: true
    });
    setShowModal(true);
  };

  const handleEditUser = async (userId) => {
    try {
      setModalLoading(true);
      // Add delay to show loading spinner
      await new Promise(resolve => setTimeout(resolve, 800));
      const response = await api.getUserDetails(userId);
      console.log('Edit user response:', response);
      
      const user = response.data?.user || response.user || response.data;
      console.log('Edit user data:', user);
      
      if (!user) {
        console.error('User data not found in response. Full response:', response);
        throw new Error('User data not found in response');
      }
      
      // Check if user has the required fields - for admin operations, email might not be available
      if (!user.username) {
        console.error('Username is missing from user data:', user);
        throw new Error('Invalid user data: missing username');
      }
      
      setModalMode('edit');
      setSelectedUser(user);
      const formDataToSet = {
        username: user.username || '',
        email: user.email || '', // Email might not be available for basic access level
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        password: '', // Don't pre-fill password
        role: user.role || 'viewer',
        organization_id: user.organization?.id || user.organization_id || '',
        is_verified: Boolean(user.is_verified),
        is_active: user.is_active !== false
      };
      
      console.log('Setting form data for edit:', formDataToSet);
      setFormData(formDataToSet);
      setShowModal(true);
    } catch (err) {
      console.error('Error in handleEditUser:', err);
      setError('Failed to load user details: ' + (err.message || err));
    } finally {
      setModalLoading(false);
    }
  };

  const handleViewUser = async (userId) => {
    try {
      setModalLoading(true);
      // Add delay to show loading spinner
      await new Promise(resolve => setTimeout(resolve, 800));
      const response = await api.getUserDetails(userId);
      console.log('View user response:', response);
      
      const user = response.data?.user || response.user || response.data;
      console.log('View user data:', user);
      
      if (!user) {
        console.error('User data not found in response. Full response:', response);
        throw new Error('User data not found in response');
      }
      
      // Check if user has the required fields
      if (!user.username) {
        console.error('Username is missing from user data:', user);
        throw new Error('Invalid user data: missing username');
      }
      
      setModalMode('view');
      setSelectedUser(user);
      const formDataToSet = {
        username: user.username || '',
        email: user.email || '', // Email might not be available for basic access level
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        password: '',
        role: user.role || 'viewer',
        organization_id: user.organization?.id || user.organization_id || '',
        is_verified: Boolean(user.is_verified),
        is_active: user.is_active !== false
      };
      
      console.log('Setting form data for view:', formDataToSet);
      setFormData(formDataToSet);
      setShowModal(true);
    } catch (err) {
      console.error('Error in handleViewUser:', err);
      setError('Failed to load user details: ' + (err.message || err));
    } finally {
      setModalLoading(false);
    }
  };

  const handleDeleteUser = async (userId, username) => {
    if (window.confirm(`Are you sure you want to deactivate user "${username}"?`)) {
      try {
        setOperationLoading(true);
        await new Promise(resolve => setTimeout(resolve, 800));
        await api.deactivateUser(userId, 'Deactivated by admin');
        loadUsers();
      } catch (err) {
        setError('Failed to deactivate user: ' + err.message);
      } finally {
        setOperationLoading(false);
      }
    }
  };

  const handleReactivateUser = async (userId, username) => {
    if (window.confirm(`Are you sure you want to reactivate user "${username}"?`)) {
      try {
        setOperationLoading(true);
        await new Promise(resolve => setTimeout(resolve, 800));
        await api.reactivateUser(userId, 'Reactivated by admin');
        loadUsers();
      } catch (err) {
        setError('Failed to reactivate user: ' + err.message);
      } finally {
        setOperationLoading(false);
      }
    }
  };

  const handlePermanentDeleteUser = async (userId, username) => {
    if (window.confirm(`Are you sure you want to PERMANENTLY DELETE user "${username}"? This action cannot be undone.`)) {
      const reason = prompt('Please provide a reason for deletion:');
      if (reason !== null) {
        try {
          setOperationLoading(true);
          await new Promise(resolve => setTimeout(resolve, 800));
          await api.deleteUser(userId, reason);
          loadUsers();
        } catch (err) {
          setError('Failed to delete user: ' + err.message);
        } finally {
          setOperationLoading(false);
        }
      }
    }
  };


  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Client-side validation for username in edit mode
    if (modalMode === 'edit' && formData.username) {
      const username = formData.username.trim();
      
      if (username.length < 3) {
        setError('Username must be at least 3 characters long');
        return;
      }
      
      // Check for valid characters (letters, numbers, underscores only)
      const validUsernameRegex = /^[a-zA-Z0-9_]+$/;
      if (!validUsernameRegex.test(username)) {
        setError('Username can only contain letters, numbers, and underscores');
        return;
      }
    }
    
    try {
      setSubmitting(true);
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (modalMode === 'add') {
        console.log('Creating user with data:', formData);
        await api.createUser(formData);
      } else if (modalMode === 'edit') {
        const updateData = { ...formData };
        if (!updateData.password) {
          delete updateData.password; // Don't send empty password
        }
        
        // Handle username change separately if it's different
        if (updateData.username !== selectedUser.username) {
          console.log('Username changed, updating via changeUsername API');
          await api.changeUsername(selectedUser.id, updateData.username);
          // Remove username from updateData to avoid duplicate update
          delete updateData.username;
        }
        
        // Update other fields if there are any remaining
        if (Object.keys(updateData).length > 0) {
          console.log('Updating user with data:', updateData);
          console.log('Selected user ID:', selectedUser.id);
          await api.updateUser(selectedUser.id, updateData);
        }
      }
      setShowModal(false);
      setError(null); // Clear any previous errors
      loadUsers();
    } catch (err) {
      console.error('Error in handleSubmit:', err);
      // Handle different error types
      if (Array.isArray(err)) {
        setError(err.join(', '));
      } else if (typeof err === 'string') {
        setError(err);
      } else {
        setError('Failed to save user: ' + (err.message || 'Unknown error'));
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    console.log('Input change:', { name, value, type, checked });
    setFormData(prev => {
      const newData = {
        ...prev,
        [name]: type === 'checkbox' ? checked : value
      };
      console.log('Updated form data:', newData);
      return newData;
    });
  };

  const filteredUsers = Array.isArray(users) ? users.filter(user => {
    const matchesSearch = !searchTerm || 
      user.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.first_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.last_name?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesRole = !roleFilter || user.role === roleFilter;
    
    return matchesSearch && matchesRole;
  }) : [];

  const getOrganizationName = (orgId) => {
    const org = organizations.find(o => o.id === orgId);
    return org ? org.name : 'N/A';
  };

  const handleUserClick = (user) => {
    setSelectedUserForActions(user);
    setShowActionsPopup(true);
  };

  const closeActionsPopup = () => {
    setShowActionsPopup(false);
    setSelectedUserForActions(null);
  };

  if (!active) return null;
  if (loading) return <LoadingSpinner fullscreen={true} />;
  if (error) return <div style={{ padding: '2rem', color: 'red' }}>{error}</div>;

  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif', position: 'relative' }}>
      {(operationLoading || submitting) && <LoadingSpinner fullscreen={true} />}
      <h1 style={{ marginBottom: '2rem', color: '#333' }}>User Management</h1>
      
      {/* Controls */}
      <div style={{ 
        display: 'flex', 
        gap: '1rem', 
        marginBottom: '2rem',
        flexWrap: 'wrap',
        alignItems: 'center'
      }}>
        <input
          type="text"
          placeholder="Search users..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            padding: '0.5rem',
            border: '1px solid #ddd',
            borderRadius: '4px',
            minWidth: '200px'
          }}
        />
        
        <select
          value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value)}
          style={{
            padding: '0.5rem',
            border: '1px solid #ddd',
            borderRadius: '4px'
          }}
        >
          <option value="">All Roles</option>
          {roles.map(role => (
            <option key={role} value={role}>{role}</option>
          ))}
        </select>
        
        <button
          onClick={handleAddUser}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Add User
        </button>
      </div>

      {/* Hint Text */}
      <div style={{ 
        marginBottom: '1rem', 
        color: '#6c757d', 
        fontSize: '0.875rem',
        textAlign: 'center'
      }}>
        💡 Click on any user row to view available actions
      </div>

      {/* Users List */}
      <div style={{ 
        backgroundColor: 'white',
        borderRadius: '12px',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
        border: '1px solid #e9ecef'
      }}>
        {filteredUsers.map(user => (
          <div 
            key={user.id} 
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              handleUserClick(user);
            }}
            style={{ 
              display: 'flex',
              alignItems: 'center',
              padding: '1.25rem',
              borderBottom: '1px solid #e9ecef',
              transition: 'all 0.2s ease',
              cursor: 'pointer',
              backgroundColor: 'transparent'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#f8f9fa';
              e.currentTarget.style.transform = 'translateX(4px)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
              e.currentTarget.style.transform = 'translateX(0px)';
            }}
          >
            <div style={{ flex: '1', minWidth: '0' }}>
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '1rem',
                flexWrap: 'wrap'
              }}>
                <div style={{ fontWeight: '600', color: '#212529', fontSize: '1.1rem' }}>
                  {user.username}
                </div>
                <div style={{ color: '#495057' }}>
                  {`${user.first_name || ''} ${user.last_name || ''}`.trim() || 'N/A'}
                </div>
                <span style={{
                  padding: '0.25rem 0.5rem',
                  borderRadius: '4px',
                  fontSize: '0.75rem',
                  fontWeight: '600',
                  textTransform: 'uppercase',
                  backgroundColor: user.role === 'admin' ? '#d4edda' : user.role === 'publisher' ? '#fff3cd' : '#f8f9fa',
                  color: user.role === 'admin' ? '#155724' : user.role === 'publisher' ? '#856404' : '#495057'
                }}>
                  {user.role}
                </span>
                <span style={{
                  padding: '0.25rem 0.5rem',
                  borderRadius: '4px',
                  fontSize: '0.75rem',
                  fontWeight: '600',
                  textTransform: 'uppercase',
                  backgroundColor: user.is_active ? '#d4edda' : '#f8d7da',
                  color: user.is_active ? '#155724' : '#721c24'
                }}>
                  {user.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              <div style={{ 
                marginTop: '0.5rem', 
                color: '#6c757d', 
                fontSize: '0.875rem',
                display: 'flex',
                gap: '1rem',
                flexWrap: 'wrap'
              }}>
                <span>{user.email || 'No email'}</span>
                <span>Org: {user.organization?.name || getOrganizationName(user.organization_id) || 'N/A'}</span>
              </div>
            </div>
            <div style={{ 
              fontSize: '1.2rem', 
              color: '#6c757d',
              marginLeft: '1rem',
              transition: 'all 0.2s ease',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              backgroundColor: 'rgba(108, 117, 125, 0.1)'
            }}>
              →
            </div>
          </div>
        ))}
      </div>

      {filteredUsers.length === 0 && (
        <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
          No users found matching your criteria.
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '2rem',
            borderRadius: '8px',
            maxWidth: '500px',
            width: '90%',
            maxHeight: '80vh',
            overflowY: 'auto'
          }}>
            <h2 style={{ marginBottom: '1.5rem', color: '#333' }}>
              {modalMode === 'add' ? 'Add New User' : 
               modalMode === 'edit' ? 'Edit User' : 'View User'}
            </h2>
            
            {modalLoading ? (
              <LoadingSpinner size="medium" />
            ) : (
            
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                  Username
                </label>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  disabled={modalMode === 'view'}
                  required
                  pattern="[a-zA-Z0-9_]+"
                  title="Username can only contain letters, numbers, and underscores"
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    backgroundColor: modalMode === 'view' ? '#f8f9fa' : 'white',
                    color: '#333'
                  }}
                />
                {modalMode === 'edit' && (
                  <div style={{ fontSize: '0.875rem', color: '#666', marginTop: '0.25rem' }}>
                    Only letters, numbers, and underscores allowed (minimum 3 characters)
                  </div>
                )}
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                  Email {!formData.email && modalMode === 'view' && '(Not available at current access level)'}
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  disabled={modalMode === 'view'}
                  required={modalMode === 'add'}
                  placeholder={!formData.email && modalMode !== 'add' ? 'Email not available' : ''}
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    backgroundColor: modalMode === 'view' ? '#f8f9fa' : 'white',
                    color: '#333'
                  }}
                />
              </div>

              <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                    First Name
                  </label>
                  <input
                    type="text"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleInputChange}
                    disabled={modalMode === 'view'}
                    style={{
                      width: '100%',
                      padding: '0.5rem',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      backgroundColor: modalMode === 'view' ? '#f8f9fa' : 'white'
                    }}
                  />
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                    Last Name
                  </label>
                  <input
                    type="text"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleInputChange}
                    disabled={modalMode === 'view'}
                    style={{
                      width: '100%',
                      padding: '0.5rem',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      backgroundColor: modalMode === 'view' ? '#f8f9fa' : 'white'
                    }}
                  />
                </div>
              </div>

              {modalMode === 'add' && (
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                    Password
                  </label>
                  <input
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    required
                    style={{
                      width: '100%',
                      padding: '0.5rem',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      color: '#333'
                    }}
                  />
                </div>
              )}

              {modalMode === 'edit' && (
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                    New Password (leave blank to keep current)
                  </label>
                  <input
                    type="password"
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    style={{
                      width: '100%',
                      padding: '0.5rem',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      color: '#333'
                    }}
                  />
                </div>
              )}

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                  Role
                </label>
                <select
                  name="role"
                  value={formData.role}
                  onChange={handleInputChange}
                  disabled={modalMode === 'view'}
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    backgroundColor: modalMode === 'view' ? '#f8f9fa' : 'white',
                    color: '#333'
                  }}
                >
                  {roles.map(role => (
                    <option key={role} value={role}>{role}</option>
                  ))}
                </select>
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                  Organization *
                </label>
                <select
                  name="organization_id"
                  value={formData.organization_id}
                  onChange={handleInputChange}
                  disabled={modalMode === 'view'}
                  required={modalMode === 'add'}
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    backgroundColor: modalMode === 'view' ? '#f8f9fa' : 'white',
                    color: '#333'
                  }}
                >
                  <option value="">Select Organization</option>
                  {organizations.map(org => (
                    <option key={org.id} value={org.id}>{org.name}</option>
                  ))}
                </select>
              </div>

              <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <input
                    type="checkbox"
                    name="is_verified"
                    checked={formData.is_verified}
                    onChange={handleInputChange}
                    disabled={modalMode === 'view'}
                  />
                  Verified
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <input
                    type="checkbox"
                    name="is_active"
                    checked={formData.is_active}
                    onChange={handleInputChange}
                    disabled={modalMode === 'view'}
                  />
                  Active
                </label>
              </div>

              <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  style={{
                    padding: '0.5rem 1rem',
                    border: '1px solid #ddd',
                    backgroundColor: 'white',
                    color: '#666',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  {modalMode === 'view' ? 'Close' : 'Cancel'}
                </button>
                {modalMode !== 'view' && (
                  <button
                    type="submit"
                    style={{
                      padding: '0.5rem 1rem',
                      backgroundColor: '#007bff',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer'
                    }}
                  >
                    {modalMode === 'add' ? 'Add User' : 'Update User'}
                  </button>
                )}
              </div>
            </form>
            )}
          </div>
        </div>
      )}

      {/* Actions Popup */}
      {showActionsPopup && selectedUserForActions && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1001
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '2rem',
            borderRadius: '12px',
            minWidth: '300px',
            maxWidth: '400px',
            boxShadow: '0 10px 25px rgba(0,0,0,0.1)'
          }}>
            <div style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ 
                margin: '0 0 0.5rem 0', 
                color: '#333',
                fontSize: '1.25rem'
              }}>
                {selectedUserForActions.username}
              </h3>
              <div style={{ 
                color: '#666', 
                fontSize: '0.875rem',
                marginBottom: '0.5rem'
              }}>
                {`${selectedUserForActions.first_name || ''} ${selectedUserForActions.last_name || ''}`.trim() || 'N/A'}
              </div>
              <div style={{ 
                color: '#666', 
                fontSize: '0.875rem',
                display: 'flex',
                gap: '0.5rem',
                alignItems: 'center'
              }}>
                <span style={{
                  padding: '0.25rem 0.5rem',
                  borderRadius: '4px',
                  fontSize: '0.75rem',
                  fontWeight: '600',
                  textTransform: 'uppercase',
                  backgroundColor: selectedUserForActions.role === 'admin' ? '#d4edda' : selectedUserForActions.role === 'publisher' ? '#fff3cd' : '#f8f9fa',
                  color: selectedUserForActions.role === 'admin' ? '#155724' : selectedUserForActions.role === 'publisher' ? '#856404' : '#495057'
                }}>
                  {selectedUserForActions.role}
                </span>
                <span style={{
                  padding: '0.25rem 0.5rem',
                  borderRadius: '4px',
                  fontSize: '0.75rem',
                  fontWeight: '600',
                  textTransform: 'uppercase',
                  backgroundColor: selectedUserForActions.is_active ? '#d4edda' : '#f8d7da',
                  color: selectedUserForActions.is_active ? '#155724' : '#721c24'
                }}>
                  {selectedUserForActions.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>
            
            <div style={{ 
              display: 'flex', 
              flexDirection: 'column',
              gap: '0.75rem'
            }}>
              <button
                onClick={() => {
                  closeActionsPopup();
                  handleViewUser(selectedUserForActions.id);
                }}
                style={{
                  padding: '0.75rem 1rem',
                  backgroundColor: '#17a2b8',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '0.875rem',
                  fontWeight: '500',
                  transition: 'all 0.2s ease',
                  textAlign: 'left'
                }}
                onMouseEnter={(e) => e.target.style.backgroundColor = '#138496'}
                onMouseLeave={(e) => e.target.style.backgroundColor = '#17a2b8'}
              >
                👁️ View Details
              </button>
              
              <button
                onClick={() => {
                  closeActionsPopup();
                  handleEditUser(selectedUserForActions.id);
                }}
                style={{
                  padding: '0.75rem 1rem',
                  backgroundColor: '#ffc107',
                  color: '#212529',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '0.875rem',
                  fontWeight: '500',
                  transition: 'all 0.2s ease',
                  textAlign: 'left'
                }}
                onMouseEnter={(e) => e.target.style.backgroundColor = '#e0a800'}
                onMouseLeave={(e) => e.target.style.backgroundColor = '#ffc107'}
              >
                ✏️ Edit User
              </button>
              
              {selectedUserForActions.is_active ? (
                <button
                  onClick={() => {
                    closeActionsPopup();
                    handleDeleteUser(selectedUserForActions.id, selectedUserForActions.username);
                  }}
                  style={{
                    padding: '0.75rem 1rem',
                    backgroundColor: '#dc3545',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    transition: 'all 0.2s ease',
                    textAlign: 'left'
                  }}
                  onMouseEnter={(e) => e.target.style.backgroundColor = '#c82333'}
                  onMouseLeave={(e) => e.target.style.backgroundColor = '#dc3545'}
                >
                  ⏸️ Deactivate User
                </button>
              ) : (
                <button
                  onClick={() => {
                    closeActionsPopup();
                    handleReactivateUser(selectedUserForActions.id, selectedUserForActions.username);
                  }}
                  style={{
                    padding: '0.75rem 1rem',
                    backgroundColor: '#28a745',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    transition: 'all 0.2s ease',
                    textAlign: 'left'
                  }}
                  onMouseEnter={(e) => e.target.style.backgroundColor = '#218838'}
                  onMouseLeave={(e) => e.target.style.backgroundColor = '#28a745'}
                >
                  ▶️ Reactivate User
                </button>
              )}
              
              <button
                onClick={() => {
                  closeActionsPopup();
                  handlePermanentDeleteUser(selectedUserForActions.id, selectedUserForActions.username);
                }}
                style={{
                  padding: '0.75rem 1rem',
                  backgroundColor: '#6c757d',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '0.875rem',
                  fontWeight: '500',
                  transition: 'all 0.2s ease',
                  textAlign: 'left'
                }}
                onMouseEnter={(e) => e.target.style.backgroundColor = '#5a6268'}
                onMouseLeave={(e) => e.target.style.backgroundColor = '#6c757d'}
              >
                🗑️ Permanently Delete
              </button>
            </div>
            
            <div style={{ 
              marginTop: '1.5rem',
              paddingTop: '1rem',
              borderTop: '1px solid #e9ecef'
            }}>
              <button
                onClick={closeActionsPopup}
                style={{
                  padding: '0.5rem 1rem',
                  border: '1px solid #ddd',
                  backgroundColor: 'white',
                  color: '#666',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  width: '100%',
                  fontSize: '0.875rem'
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserManagement;