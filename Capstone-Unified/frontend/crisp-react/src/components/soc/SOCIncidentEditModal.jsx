import React, { useState, useEffect } from 'react';
import * as api from '../../api.js';
import { useNotifications } from '../enhanced/NotificationManager.jsx';

const SOCIncidentEditModal = ({ isOpen, onClose, incident, onIncidentUpdated }) => {
  const { showSuccess, showError } = useNotifications();
  const [isUpdating, setIsUpdating] = useState(false);
  const [users, setUsers] = useState([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    priority: 'medium',
    severity: 'medium',
    status: 'new',
    assigned_to: '',
    tags: []
  });

  const [tagInput, setTagInput] = useState('');

  const incidentCategories = [
    { value: 'malware', label: 'Malware' },
    { value: 'phishing', label: 'Phishing' },
    { value: 'data_breach', label: 'Data Breach' },
    { value: 'unauthorized_access', label: 'Unauthorized Access' },
    { value: 'ddos', label: 'DDoS Attack' },
    { value: 'insider_threat', label: 'Insider Threat' },
    { value: 'ransomware', label: 'Ransomware' },
    { value: 'apt', label: 'Advanced Persistent Threat' },
    { value: 'vulnerability', label: 'Vulnerability' },
    { value: 'policy_violation', label: 'Policy Violation' },
    { value: 'other', label: 'Other' }
  ];

  const priorityOptions = [
    { value: 'low', label: 'Low', color: '#28a745' },
    { value: 'medium', label: 'Medium', color: '#ffc107' },
    { value: 'high', label: 'High', color: '#fd7e14' },
    { value: 'critical', label: 'Critical', color: '#dc3545' }
  ];

  const severityOptions = [
    { value: 'informational', label: 'Informational', color: '#17a2b8' },
    { value: 'low', label: 'Low', color: '#28a745' },
    { value: 'medium', label: 'Medium', color: '#ffc107' },
    { value: 'high', label: 'High', color: '#fd7e14' },
    { value: 'critical', label: 'Critical', color: '#dc3545' }
  ];

  const statusOptions = [
    { value: 'new', label: 'New', color: '#007bff' },
    { value: 'assigned', label: 'Assigned', color: '#17a2b8' },
    { value: 'in_progress', label: 'In Progress', color: '#ffc107' },
    { value: 'resolved', label: 'Resolved', color: '#28a745' },
    { value: 'closed', label: 'Closed', color: '#6c757d' }
  ];

  // Load incident data when modal opens
  useEffect(() => {
    if (isOpen && incident) {
      setFormData({
        title: incident.title || '',
        description: incident.description || '',
        category: incident.category || '',
        priority: incident.priority || 'medium',
        severity: incident.severity || 'medium',
        status: incident.status || 'new',
        assigned_to: incident.assigned_to || '',
        tags: incident.tags || []
      });
      fetchUsers();
    }
  }, [isOpen, incident]);

  const fetchUsers = async () => {
    setLoadingUsers(true);
    try {
      console.log('=== FETCHING USERS FOR EDIT MODAL ===');
      console.log('Calling api.getUsersList()...');
      
      const response = await api.getUsersList();
      console.log('Raw API Response:', response);
      
      // Handle the specific response format: {count, next, previous, results: {success, users}}
      let users = [];
      
      if (response?.results?.users && Array.isArray(response.results.users)) {
        console.log('✓ Using response.results.users (paginated format)');
        users = response.results.users;
      } else if (response?.success && response?.users && Array.isArray(response.users)) {
        console.log('✓ Using response.users (direct success format)');
        users = response.users;
      } else if (response?.success && response?.data && Array.isArray(response.data)) {
        console.log('✓ Using response.data (success format)');
        users = response.data;
      } else if (response?.data && Array.isArray(response.data)) {
        console.log('✓ Using response.data (array format)');
        users = response.data;
      } else if (response?.results && Array.isArray(response.results)) {
        console.log('✓ Using response.results (array format)');
        users = response.results;
      } else if (Array.isArray(response)) {
        console.log('✓ Using response as direct array');
        users = response;
      } else {
        console.warn('❌ Unknown response format, trying to extract from nested structures');
        console.log('Full response:', JSON.stringify(response, null, 2));
        
        // More specific extraction attempts
        if (response?.data?.users) {
          console.log('✓ Found response.data.users');
          users = response.data.users;
        } else if (response?.results?.data?.users) {
          console.log('✓ Found response.results.data.users');
          users = response.results.data.users;
        } else {
          console.error('❌ Could not find users array in response');
        }
      }
      
      // DIRECT FIX: If users is still an object with a users property, extract it
      if (!Array.isArray(users) && users?.users && Array.isArray(users.users)) {
        console.log('🔧 DIRECT FIX: Extracting users from object format');
        users = users.users;
      }
      
      console.log('Extracted users:', users);
      console.log('Users array length:', users ? users.length : 'undefined');
      
      if (users && users.length > 0) {
        console.log('First user structure:', users[0]);
      } else {
        console.warn('No users found or users is not an array');
      }
      
      setUsers(users || []);
    } catch (err) {
      console.error('=== USER FETCH ERROR ===');
      console.error('Error details:', err);
      showError('Failed to load users for assignment: ' + err.message);
      setUsers([]);
    } finally {
      setLoadingUsers(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleTagAdd = (e) => {
    if (e.key === 'Enter' && tagInput.trim()) {
      e.preventDefault();
      if (!formData.tags.includes(tagInput.trim())) {
        setFormData(prev => ({
          ...prev,
          tags: [...prev.tags, tagInput.trim()]
        }));
      }
      setTagInput('');
    }
  };

  const handleTagRemove = (tagToRemove) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  const validateForm = () => {
    const errors = [];
    if (!formData.title.trim()) errors.push('Title is required');
    if (!formData.description.trim()) errors.push('Description is required');
    if (!formData.category) errors.push('Category is required');
    return errors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const errors = validateForm();
    if (errors.length > 0) {
      showError('Please fix the following errors: ' + errors.join(', '));
      return;
    }

    setIsUpdating(true);
    try {
      const response = await api.updateSOCIncident(incident.id, formData);
      
      if (response?.success) {
        showSuccess(`Incident updated successfully! ID: ${incident.incident_id}`);
        
        if (onIncidentUpdated) {
          onIncidentUpdated(response.data);
        }
        
        onClose();
      } else {
        throw new Error(response?.message || 'Failed to update incident');
      }
    } catch (err) {
      console.error('Error updating incident:', err);
      showError('Failed to update incident: ' + err.message);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleClose = () => {
    if (!isUpdating) {
      onClose();
    }
  };

  if (!isOpen || !incident) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '1rem'
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        width: '100%',
        maxWidth: '900px',
        maxHeight: '90vh',
        overflow: 'auto',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
      }}>
        {/* Header */}
        <div style={{
          padding: '1.5rem',
          borderBottom: '1px solid #e9ecef',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          backgroundColor: '#f8f9fa'
        }}>
          <h3 style={{ margin: 0, fontSize: '1.25rem', fontWeight: '600' }}>
            Edit SOC Incident - {incident.incident_id}
          </h3>
          <button
            onClick={handleClose}
            disabled={isUpdating}
            style={{
              backgroundColor: 'transparent',
              border: 'none',
              fontSize: '1.5rem',
              cursor: isUpdating ? 'not-allowed' : 'pointer',
              color: '#6c757d'
            }}
          >
            ×
          </button>
        </div>

        {/* Form Content */}
        <form onSubmit={handleSubmit} style={{ padding: '1.5rem' }}>
          {/* Basic Information */}
          <div style={{ marginBottom: '2rem' }}>
            <h4 style={{ marginBottom: '1rem', fontSize: '1.125rem', fontWeight: '600' }}>
              Basic Information
            </h4>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1rem', marginBottom: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem', display: 'block' }}>
                  Title <span style={{ color: '#dc3545' }}>*</span>
                </label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  placeholder="Enter incident title..."
                  required
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #dee2e6',
                    borderRadius: '4px',
                    fontSize: '0.875rem'
                  }}
                />
              </div>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem', display: 'block' }}>
                Description <span style={{ color: '#dc3545' }}>*</span>
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                placeholder="Provide detailed description of the incident..."
                required
                rows={4}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '1px solid #dee2e6',
                  borderRadius: '4px',
                  fontSize: '0.875rem',
                  resize: 'vertical'
                }}
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem', display: 'block' }}>
                  Category <span style={{ color: '#dc3545' }}>*</span>
                </label>
                <select
                  name="category"
                  value={formData.category}
                  onChange={handleInputChange}
                  required
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #dee2e6',
                    borderRadius: '4px',
                    fontSize: '0.875rem'
                  }}
                >
                  <option value="">Select category...</option>
                  {incidentCategories.map(cat => (
                    <option key={cat.value} value={cat.value}>{cat.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem', display: 'block' }}>
                  Priority
                </label>
                <select
                  name="priority"
                  value={formData.priority}
                  onChange={handleInputChange}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #dee2e6',
                    borderRadius: '4px',
                    fontSize: '0.875rem'
                  }}
                >
                  {priorityOptions.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem', display: 'block' }}>
                  Severity
                </label>
                <select
                  name="severity"
                  value={formData.severity}
                  onChange={handleInputChange}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #dee2e6',
                    borderRadius: '4px',
                    fontSize: '0.875rem'
                  }}
                >
                  {severityOptions.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Status and Assignment */}
          <div style={{ marginBottom: '2rem' }}>
            <h4 style={{ marginBottom: '1rem', fontSize: '1.125rem', fontWeight: '600' }}>
              Status and Assignment
            </h4>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem', display: 'block' }}>
                  Status
                </label>
                <select
                  name="status"
                  value={formData.status}
                  onChange={handleInputChange}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #dee2e6',
                    borderRadius: '4px',
                    fontSize: '0.875rem'
                  }}
                >
                  {statusOptions.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem', display: 'block' }}>
                  Assign to User
                </label>
                <select
                  name="assigned_to"
                  value={formData.assigned_to}
                  onChange={handleInputChange}
                  disabled={loadingUsers}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    border: '1px solid #dee2e6',
                    borderRadius: '4px',
                    fontSize: '0.875rem'
                  }}
                >
                  <option value="">Unassigned</option>
                  {users.map(user => (
                    <option key={user.id} value={user.username}>
                      {user.first_name} {user.last_name} ({user.username})
                    </option>
                  ))}
                </select>
                {loadingUsers && (
                  <div style={{ fontSize: '0.75rem', color: '#666', marginTop: '0.25rem' }}>
                    Loading users...
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Tags */}
          <div style={{ marginBottom: '2rem' }}>
            <label style={{ fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem', display: 'block' }}>
              Tags
            </label>
            <input
              type="text"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyDown={handleTagAdd}
              placeholder="Type a tag and press Enter..."
              style={{
                width: '100%',
                padding: '0.75rem',
                border: '1px solid #dee2e6',
                borderRadius: '4px',
                fontSize: '0.875rem',
                marginBottom: '0.5rem'
              }}
            />
            {formData.tags.length > 0 && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {formData.tags.map((tag, index) => (
                  <span
                    key={index}
                    style={{
                      backgroundColor: '#e9ecef',
                      color: '#495057',
                      padding: '0.25rem 0.75rem',
                      borderRadius: '12px',
                      fontSize: '0.75rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem'
                    }}
                  >
                    {tag}
                    <button
                      type="button"
                      onClick={() => handleTagRemove(tag)}
                      style={{
                        backgroundColor: 'transparent',
                        border: 'none',
                        cursor: 'pointer',
                        fontSize: '0.75rem',
                        padding: 0
                      }}
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Submit Buttons */}
          <div style={{ 
            display: 'flex', 
            gap: '1rem', 
            justifyContent: 'flex-end',
            borderTop: '1px solid #e9ecef',
            paddingTop: '1.5rem'
          }}>
            <button
              type="button"
              onClick={handleClose}
              disabled={isUpdating}
              style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: '#6c757d',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                fontSize: '0.875rem',
                cursor: isUpdating ? 'not-allowed' : 'pointer'
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isUpdating}
              style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: isUpdating ? '#6c757d' : '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                fontSize: '0.875rem',
                cursor: isUpdating ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}
            >
              {isUpdating && (
                <div style={{
                  width: '16px',
                  height: '16px',
                  border: '2px solid transparent',
                  borderTop: '2px solid white',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }}></div>
              )}
              {isUpdating ? 'Updating...' : 'Update Incident'}
            </button>
          </div>
        </form>
      </div>

      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
};

export default SOCIncidentEditModal;