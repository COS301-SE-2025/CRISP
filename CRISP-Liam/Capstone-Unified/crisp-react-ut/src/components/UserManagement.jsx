import React, { useState, useEffect, useMemo } from 'react';
import { getUsersList, createUser, updateUser, deactivateUser, reactivateUser, deleteUser, changeUsername, getUserDetails, getOrganizations, getCurrentUser } from '../api.js';
import LoadingSpinner from './LoadingSpinner.jsx';
import ConfirmationModal from './ConfirmationModal.jsx';
import Pagination from './Pagination.jsx';

// Import alias for the API to avoid conflicts
import * as api from '../api.js';

const UserManagement = ({ active = true, initialSection = null }) => {
  console.log('UserManagement rendered with props:', { active, initialSection });
  const [users, setUsers] = useState([]); // This will be filtered/paginated users
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
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
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [confirmationData, setConfirmationData] = useState(null);
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);
  const [allUsers, setAllUsers] = useState([]);
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

  // Get current user and check if user is a publisher
  const isPublisher = currentUser?.role === 'publisher';
  const isAdmin = currentUser?.role === 'admin' || currentUser?.role === 'BlueVisionAdmin';
  
  // Get allowed roles based on current user's permissions
  const getAllowedRoles = () => {
    if (isPublisher) {
      return ['viewer']; // Publishers can only create viewers
    }
    return roles; // Admins can create any role
  };

  // Helper function to check if current user can manage target user
  const canManageUser = (targetUser) => {
    if (!isPublisher) return true; // Admins can manage anyone
    if (!targetUser) return false;
    
    // Publishers cannot manage users with higher or equal roles
    const restrictedRoles = ['publisher', 'admin', 'BlueVisionAdmin'];
    return !restrictedRoles.includes(targetUser.role);
  };

  useEffect(() => {
    if (active) {
      // Get current user info
      const user = getCurrentUser();
      setCurrentUser(user);
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
      const usersList = Array.isArray(usersData) ? usersData : [];
      setAllUsers(usersList);
      setUsers(usersList); // Initially show all users
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

  // Memoized filtered users
  const filteredUsers = useMemo(() => {
    let filtered = [...allUsers];

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(user =>
        user.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.first_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.last_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.email?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply role filter
    if (roleFilter) {
      filtered = filtered.filter(user => user.role === roleFilter);
    }

    return filtered;
  }, [allUsers, searchTerm, roleFilter]);

  // Memoized paginated users
  const paginatedUsers = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return filteredUsers.slice(startIndex, endIndex);
  }, [filteredUsers, currentPage, itemsPerPage]);

  // Update users state when pagination changes
  useEffect(() => {
    setUsers(paginatedUsers);
  }, [paginatedUsers]);

  // Handle page change
  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  // Handle items per page change
  const handleItemsPerPageChange = (newItemsPerPage) => {
    setItemsPerPage(newItemsPerPage);
    setCurrentPage(1); // Reset to first page
  };

  const handleAddUser = () => {
    setModalMode('add');
    setSelectedUser(null);
    setError(null); // Clear any previous errors
    const defaultRole = isPublisher ? 'viewer' : 'viewer'; // Publishers can only create viewers
    setFormData({
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      password: '',
      role: defaultRole,
      organization_id: '',
      is_verified: false,
      is_active: true
    });
    setShowModal(true);
  };

  const handleEditUser = async (userId) => {
    try {
      setModalLoading(true);
      setError(null); // Clear any previous errors
      // Add delay to show loading spinner
      await new Promise(resolve => setTimeout(resolve, 800));
      const response = await api.getUserDetails(userId);
      console.log('Edit user response:', response);
      
      let user = null;
      if (response.success && response.data?.user) {
        user = response.data.user;
      } else if (response.data?.user) {
        user = response.data.user;  
      } else if (response.user) {
        user = response.user;
      } else if (response.data && typeof response.data === 'object' && response.data.username) {
        user = response.data;
      } else {
        console.error('Unable to extract user from response:', response);
        throw new Error('Invalid response format');
      }
      console.log('Edit user data:', user);
      
      // Role hierarchy check: Publishers cannot edit users with higher or equal roles
      if (isPublisher && user) {
        const userRole = user.role;
        if (userRole === 'publisher' || userRole === 'admin' || userRole === 'BlueVisionAdmin') {
          setError('Publishers cannot edit users with publisher, admin, or BlueVisionAdmin roles');
          setModalLoading(false);
          return;
        }
      }
      
      if (!user || !user.username) {
        console.error('User data not found or invalid in response. Full response:', response);
        throw new Error('User data not found or invalid in response');
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
      setError(null); // Clear any previous errors
      // Add delay to show loading spinner
      await new Promise(resolve => setTimeout(resolve, 800));
      const response = await api.getUserDetails(userId);
      console.log('View user response:', response);
      
      let user = null;
      if (response.success && response.data?.user) {
        user = response.data.user;
      } else if (response.data?.user) {
        user = response.data.user;  
      } else if (response.user) {
        user = response.user;
      } else if (response.data && typeof response.data === 'object' && response.data.username) {
        user = response.data;
      } else {
        console.error('Unable to extract user from response:', response);
        throw new Error('Invalid response format');
      }
      console.log('View user data:', user);
      
      // Role hierarchy check: Publishers cannot view users with higher or equal roles
      if (isPublisher && user) {
        const userRole = user.role;
        if (userRole === 'publisher' || userRole === 'admin' || userRole === 'BlueVisionAdmin') {
          setError('Publishers cannot view users with publisher, admin, or BlueVisionAdmin roles');
          setModalLoading(false);
          return;
        }
      }
      
      if (!user || !user.username) {
        console.error('User data not found or invalid in response. Full response:', response);
        throw new Error('User data not found or invalid in response');
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

  const handleDeleteUser = (userId, username) => {
    // Role hierarchy check: Publishers cannot deactivate users with higher or equal roles
    if (isPublisher) {
      const targetUser = allUsers.find(u => u.id === userId);
      if (targetUser && (targetUser.role === 'publisher' || targetUser.role === 'admin' || targetUser.role === 'BlueVisionAdmin')) {
        setError('Publishers cannot deactivate users with publisher, admin, or BlueVisionAdmin roles');
        return;
      }
    }

    setConfirmationData({
      title: 'Deactivate User',
      message: `Are you sure you want to deactivate user "${username}"?`,
      confirmText: 'Deactivate',
      isDestructive: true,
      actionType: 'deactivate',
      action: async () => {
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
    });
    setShowConfirmation(true);
  };

  const handleReactivateUser = (userId, username) => {
    // Role hierarchy check: Publishers cannot reactivate users with higher or equal roles
    if (isPublisher) {
      const targetUser = allUsers.find(u => u.id === userId);
      if (targetUser && (targetUser.role === 'publisher' || targetUser.role === 'admin' || targetUser.role === 'BlueVisionAdmin')) {
        setError('Publishers cannot reactivate users with publisher, admin, or BlueVisionAdmin roles');
        return;
      }
    }

    setConfirmationData({
      title: 'Reactivate User',
      message: `Are you sure you want to reactivate user "${username}"?`,
      confirmText: 'Reactivate',
      isDestructive: false,
      actionType: 'reactivate',
      action: async () => {
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
    });
    setShowConfirmation(true);
  };

  const handlePermanentDeleteUser = (userId, username) => {
    setConfirmationData({
      title: 'Permanently Delete User',
      message: `Are you sure you want to PERMANENTLY DELETE user "${username}"? This action cannot be undone.`,
      confirmText: 'Delete Permanently',
      isDestructive: true,
      actionType: 'delete',
      action: async () => {
        try {
          setOperationLoading(true);
          await new Promise(resolve => setTimeout(resolve, 800));
          await api.deleteUser(userId, 'Deleted by admin');
          loadUsers();
          // Ensure actions popup is closed after successful deletion
          setShowActionsPopup(false);
          setSelectedUserForActions(null);
        } catch (err) {
          setError('Failed to delete user: ' + err.message);
        } finally {
          setOperationLoading(false);
        }
      }
    });
    setShowConfirmation(true);
  };


  const handleSubmit = (e) => {
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

    // Show confirmation dialog
    const actionText = modalMode === 'add' ? 'create' : 'update';
    const userName = modalMode === 'add' ? formData.username : selectedUser?.username;
    
    setConfirmationData({
      title: `${modalMode === 'add' ? 'Create' : 'Update'} User`,
      message: `Are you sure you want to ${actionText} user "${userName}"?`,
      confirmText: modalMode === 'add' ? 'Create User' : 'Update User',
      isDestructive: false,
      actionType: modalMode === 'add' ? 'default' : 'default',
      action: async () => {
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
      }
    });
    setShowConfirmation(true);
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

  // Get total items for pagination
  const totalItems = filteredUsers.length;

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
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ marginBottom: '0.5rem', color: '#333' }}>User Management</h1>
        {isPublisher && (
          <div style={{
            padding: '0.75rem 1rem',
            backgroundColor: '#fff3cd',
            color: '#856404',
            borderRadius: '6px',
            border: '1px solid #ffeaa7',
            fontSize: '0.875rem',
            fontWeight: '500'
          }}>
            <strong>Publisher Mode:</strong> You can view and manage users from your organization and organizations with trusted relationships. You can only create viewer users, and role changes are restricted.
          </div>
        )}
      </div>
      
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
            minWidth: '200px',
            backgroundColor: 'white',
            color: '#666'
          }}
        />
        
        <select
          value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value)}
          style={{
            padding: '0.5rem',
            border: '1px solid #ddd',
            borderRadius: '4px',
            backgroundColor: 'white',
            color: '#666'
          }}
        >
          <option value="">All Roles</option>
          {getAllowedRoles().map(role => (
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

        <div className="items-per-page">
          <label>
            Show:
            <select 
              value={itemsPerPage} 
              onChange={(e) => handleItemsPerPageChange(parseInt(e.target.value))}
            >
              <option value={5}>5</option>
              <option value={10}>10</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
            </select>
            items per page
          </label>
        </div>
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
        {users.map(user => (
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

      {users.length === 0 && allUsers.length > 0 && (
        <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
          No users found matching your criteria.
        </div>
      )}

      {allUsers.length === 0 && (
        <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
          No users available. Click "Add User" to create the first user.
        </div>
      )}

      {/* Pagination */}
      {allUsers.length > 0 && (
        <Pagination
          currentPage={currentPage}
          totalItems={totalItems}
          itemsPerPage={itemsPerPage}
          onPageChange={handlePageChange}
          showInfo={true}
          showJumpToPage={true}
        />
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
            <>
            {error && (
              <div style={{
                padding: '1rem',
                backgroundColor: '#f8d7da',
                color: '#721c24',
                borderRadius: '4px',
                marginBottom: '1rem',
                border: '1px solid #f5c6cb'
              }}>
                {error}
              </div>
            )}
            
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                  Username {!formData.username && modalMode === 'add' && <span style={{ color: 'red' }}>*</span>}
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
                    color: modalMode === 'view' ? '#333' : '#000'
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
                  Email {modalMode === 'add' && !formData.email && <span style={{ color: 'red' }}>*</span>} {!formData.email && modalMode === 'view' && '(Not available at current access level)'}
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
                    color: modalMode === 'view' ? '#333' : '#000'
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
                      backgroundColor: modalMode === 'view' ? '#f8f9fa' : 'white',
                      color: modalMode === 'view' ? '#333' : '#000'
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
                      backgroundColor: modalMode === 'view' ? '#f8f9fa' : 'white',
                      color: modalMode === 'view' ? '#333' : '#000'
                    }}
                  />
                </div>
              </div>

              {modalMode === 'add' && (
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                    Password {!formData.password && <span style={{ color: 'red' }}>*</span>}
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
                      backgroundColor: 'white',
                      color: '#999'
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
                      backgroundColor: 'white',
                      color: '#999'
                    }}
                  />
                </div>
              )}

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                  Role
                  {isPublisher && modalMode !== 'view' && (
                    <span style={{ fontSize: '0.75rem', color: '#856404', marginLeft: '0.5rem' }}>
                      (Limited to viewer role)
                    </span>
                  )}
                </label>
                <select
                  name="role"
                  value={formData.role}
                  onChange={handleInputChange}
                  disabled={modalMode === 'view' || (isPublisher && modalMode === 'edit')}
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    backgroundColor: modalMode === 'view' || (isPublisher && modalMode === 'edit') ? '#f8f9fa' : 'white',
                    color: modalMode === 'view' || (isPublisher && modalMode === 'edit') ? '#666' : '#000'
                  }}
                >
                  {getAllowedRoles().map(role => (
                    <option key={role} value={role}>{role}</option>
                  ))}
                </select>
                {isPublisher && modalMode === 'edit' && (
                  <div style={{ fontSize: '0.75rem', color: '#666', marginTop: '0.25rem' }}>
                    Role changes are restricted for publisher users
                  </div>
                )}
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                  Organization {modalMode === 'add' && !formData.organization_id && <span style={{ color: 'red' }}>*</span>}
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
                    color: modalMode === 'view' ? '#333' : '#000'
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
            </>
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
                fontSize: '1.25rem',
                wordBreak: 'break-word',
                lineHeight: '1.3'
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
              {/* Only show View Details if user can manage target user */}
              {canManageUser(selectedUserForActions) && (
                <button
                  onClick={() => {
                    closeActionsPopup();
                    handleViewUser(selectedUserForActions.id);
                  }}
                  style={{
                    padding: '0.75rem 1rem',
                    backgroundColor: '#5D8AA8',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    transition: 'all 0.2s ease',
                    textAlign: 'left'
                  }}
                  onMouseEnter={(e) => e.target.style.backgroundColor = '#4A7088'}
                  onMouseLeave={(e) => e.target.style.backgroundColor = '#5D8AA8'}
                >
                  View Details
                </button>
              )}
              
              {/* Only show Edit User if user can manage target user */}
              {canManageUser(selectedUserForActions) && (
                <button
                  onClick={() => {
                    closeActionsPopup();
                    handleEditUser(selectedUserForActions.id);
                  }}
                  style={{
                    padding: '0.75rem 1rem',
                    backgroundColor: '#5D8AA8',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    transition: 'all 0.2s ease',
                    textAlign: 'left'
                  }}
                  onMouseEnter={(e) => e.target.style.backgroundColor = '#4A7088'}
                  onMouseLeave={(e) => e.target.style.backgroundColor = '#5D8AA8'}
                >
                  Edit User
                </button>
              )}
              
              {/* Only show Deactivate/Reactivate if user can manage target user */}
              {canManageUser(selectedUserForActions) && (
                selectedUserForActions.is_active ? (
                  <button
                    onClick={() => {
                      closeActionsPopup();
                      handleDeleteUser(selectedUserForActions.id, selectedUserForActions.username);
                    }}
                    style={{
                      padding: '0.75rem 1rem',
                      backgroundColor: 'white',
                      color: '#5D8AA8',
                      border: '2px solid #5D8AA8',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontSize: '0.875rem',
                      fontWeight: '500',
                      transition: 'all 0.2s ease',
                      textAlign: 'left'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.borderColor = '#dc3545';
                      e.target.style.color = '#dc3545';
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.borderColor = '#5D8AA8';
                      e.target.style.color = '#5D8AA8';
                    }}
                  >
                    Deactivate User
                  </button>
                ) : (
                  <button
                    onClick={() => {
                      closeActionsPopup();
                      handleReactivateUser(selectedUserForActions.id, selectedUserForActions.username);
                    }}
                    style={{
                      padding: '0.75rem 1rem',
                      backgroundColor: 'white',
                      color: '#5D8AA8',
                      border: '2px solid #5D8AA8',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontSize: '0.875rem',
                      fontWeight: '500',
                      transition: 'all 0.2s ease',
                      textAlign: 'left'
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.borderColor = '#28a745';
                      e.target.style.color = '#28a745';
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.borderColor = '#5D8AA8';
                      e.target.style.color = '#5D8AA8';
                    }}
                  >
                    Reactivate User
                  </button>
                )
              )}
              
              <button
                onClick={() => {
                  closeActionsPopup();
                  handlePermanentDeleteUser(selectedUserForActions.id, selectedUserForActions.username);
                }}
                style={{
                  padding: '0.75rem 1rem',
                  backgroundColor: '#5D8AA8',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '0.875rem',
                  fontWeight: '500',
                  transition: 'all 0.2s ease',
                  textAlign: 'left'
                }}
                onMouseEnter={(e) => e.target.style.backgroundColor = '#4A7088'}
                onMouseLeave={(e) => e.target.style.backgroundColor = '#5D8AA8'}
              >
                Permanently Delete
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

      <ConfirmationModal
        isOpen={showConfirmation}
        onClose={() => setShowConfirmation(false)}
        onConfirm={confirmationData?.action}
        title={confirmationData?.title}
        message={confirmationData?.message}
        confirmText={confirmationData?.confirmText}
        isDestructive={confirmationData?.isDestructive}
        actionType={confirmationData?.actionType}
      />
    </div>
  );
};

export default UserManagement;