import React, { useState, useEffect } from 'react';
import { getOrganizations, createOrganization, updateOrganization, deactivateOrganization, reactivateOrganization, getOrganizationDetails, getOrganizationTypes } from '../api.js';
import LoadingSpinner from './LoadingSpinner.jsx';

import * as api from '../api.js';

const OrganisationManagement = ({ active = true, initialSection = null }) => {
  console.log('OrganisationManagement rendered with props:', { active, initialSection });
  const [organizations, setOrganizations] = useState([]);
  const [organizationTypes, setOrganizationTypes] = useState(['educational', 'government', 'private']);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(() => {
    if (initialSection === 'create') return true;
    const urlParams = new URLSearchParams(window.location.search);
    const section = urlParams.get('section');
    return section === 'create';
  });
  const [modalMode, setModalMode] = useState(() => {
    if (initialSection === 'create') return 'add';
    const urlParams = new URLSearchParams(window.location.search);
    const section = urlParams.get('section');
    return section === 'create' ? 'add' : 'add';
  });
  const [selectedOrganization, setSelectedOrganization] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [modalLoading, setModalLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [operationLoading, setOperationLoading] = useState(false);
  const [showActionsPopup, setShowActionsPopup] = useState(false);
  const [selectedOrganizationForActions, setSelectedOrganizationForActions] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    domain: '',
    contact_email: '',
    description: '',
    website: '',
    organization_type: 'educational',
    primary_user: {
      username: '',
      email: '',
      password: '',
      first_name: '',
      last_name: ''
    }
  });

  const loadOrganizationTypes = async () => {
    try {
      const response = await api.getOrganizationTypes();
      console.log('Organization types response:', response);
      
      if (response.success && response.data?.organization_types) {
        const types = response.data.organization_types.map(type => type.value);
        setOrganizationTypes(types);
        console.log('Loaded organization types:', types);
      }
    } catch (err) {
      console.error('Failed to load organization types:', err);
      // Keep default types if API fails
    }
  };

  useEffect(() => {
    if (active) {
      loadOrganizations();
      loadOrganizationTypes();
    }
  }, [active]);

  useEffect(() => {
    if (initialSection === 'create') {
      console.log('OrganisationManagement: Opening create modal from prop');
      setShowModal(true);
      setModalMode('add');
    } else if (initialSection === 'roles' || initialSection === 'passwords') {
      console.log('OrganisationManagement: Section from prop:', initialSection);
      setShowModal(false);
    }
  }, [initialSection]);

  useEffect(() => {
    const handleUrlChange = () => {
      const urlParams = new URLSearchParams(window.location.search);
      const section = urlParams.get('section');
      
      if (section === 'create') {
        setShowModal(true);
        setModalMode('add');
      }
    };

    window.addEventListener('popstate', handleUrlChange);
    
    return () => {
      window.removeEventListener('popstate', handleUrlChange);
    };
  }, []);

  const loadOrganizations = async () => {
    try {
      setLoading(true);
      setError(null);
      await new Promise(resolve => setTimeout(resolve, 1000));
      const response = await api.getOrganizations();
      console.log('Organizations API response:', response);
      console.log('Full response object:', JSON.stringify(response, null, 2));
      
      let organizationsData = [];
      if (response.data && response.data.organizations) {
        organizationsData = response.data.organizations;
      } else if (response.organizations) {
        organizationsData = response.organizations;
      } else if (response.data && Array.isArray(response.data)) {
        organizationsData = response.data;
      } else if (Array.isArray(response)) {
        organizationsData = response;
      }
      
      console.log('Extracted organizations data:', organizationsData);
      console.log('Organizations data length:', organizationsData.length);
      setOrganizations(Array.isArray(organizationsData) ? organizationsData : []);
    } catch (err) {
      console.error('Failed to load organizations:', err);
      setError('Failed to load organizations: ' + err.message);
      setOrganizations([]);
    } finally {
      setLoading(false);
    }
  };

  const handleAddOrganization = () => {
    setModalMode('add');
    setSelectedOrganization(null);
    setFormData({
      name: '',
      domain: '',
      contact_email: '',
      description: '',
      website: '',
      organization_type: 'educational',
      primary_user: {
        username: '',
        email: '',
        password: '',
        first_name: '',
        last_name: ''
      }
    });
    setShowModal(true);
  };

  const handleEditOrganization = async (organizationId) => {
    try {
      setModalLoading(true);
      await new Promise(resolve => setTimeout(resolve, 800));
      const response = await api.getOrganizationDetails(organizationId);
      console.log('Edit organization response:', response);
      
      const organization = response.data?.organization || response.organization || response.data;
      console.log('Edit organization data:', organization);
      
      if (!organization) {
        console.error('Organization data not found in response. Full response:', response);
        throw new Error('Organization data not found in response');
      }
      
      if (!organization.name) {
        console.error('Organization name is missing from organization data:', organization);
        throw new Error('Invalid organization data: missing name');
      }
      
      setModalMode('edit');
      setSelectedOrganization(organization);
      const formDataToSet = {
        name: organization.name || '',
        domain: organization.domain || '',
        contact_email: organization.contact_email || '',
        description: organization.description || '',
        website: organization.website || '',
        organization_type: organization.organization_type || 'educational',
        primary_user: {
          username: '',
          email: '',
          password: '',
          first_name: '',
          last_name: ''
        }
      };
      
      console.log('Setting form data for edit:', formDataToSet);
      setFormData(formDataToSet);
      setShowModal(true);
    } catch (err) {
      console.error('Error in handleEditOrganization:', err);
      setError('Failed to load organization details: ' + (err.message || err));
    } finally {
      setModalLoading(false);
    }
  };

  const handleViewOrganization = async (organizationId) => {
    try {
      setModalLoading(true);
      await new Promise(resolve => setTimeout(resolve, 800));
      const response = await api.getOrganizationDetails(organizationId);
      console.log('View organization response:', response);
      
      const organization = response.data?.organization || response.organization || response.data;
      console.log('View organization data:', organization);
      
      if (!organization) {
        console.error('Organization data not found in response. Full response:', response);
        throw new Error('Organization data not found in response');
      }
      
      if (!organization.name) {
        console.error('Organization name is missing from organization data:', organization);
        throw new Error('Invalid organization data: missing name');
      }
      
      setModalMode('view');
      setSelectedOrganization(organization);
      const formDataToSet = {
        name: organization.name || '',
        domain: organization.domain || '',
        contact_email: organization.contact_email || '',
        description: organization.description || '',
        website: organization.website || '',
        organization_type: organization.organization_type || 'educational',
        primary_user: {
          username: '',
          email: '',
          password: '',
          first_name: '',
          last_name: ''
        }
      };
      
      console.log('Setting form data for view:', formDataToSet);
      setFormData(formDataToSet);
      setShowModal(true);
    } catch (err) {
      console.error('Error in handleViewOrganization:', err);
      setError('Failed to load organization details: ' + (err.message || err));
    } finally {
      setModalLoading(false);
    }
  };

  const handleDeleteOrganization = async (organizationId, organizationName) => {
    if (window.confirm(`Are you sure you want to deactivate organisation "${organizationName}"?`)) {
      try {
        setOperationLoading(true);
        await new Promise(resolve => setTimeout(resolve, 800));
        await api.deactivateOrganization(organizationId, 'Deactivated by admin');
        loadOrganizations();
      } catch (err) {
        setError('Failed to deactivate organization: ' + err.message);
      } finally {
        setOperationLoading(false);
      }
    }
  };

  const handleReactivateOrganization = async (organizationId, organizationName) => {
    if (window.confirm(`Are you sure you want to reactivate organisation "${organizationName}"?`)) {
      try {
        setOperationLoading(true);
        await new Promise(resolve => setTimeout(resolve, 800));
        await api.reactivateOrganization(organizationId, 'Reactivated by admin');
        loadOrganizations();
      } catch (err) {
        setError('Failed to reactivate organization: ' + err.message);
      } finally {
        setOperationLoading(false);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (modalMode === 'add') {
        console.log('Creating organization with data:', formData);
        await api.createOrganization(formData);
      } else if (modalMode === 'edit') {
        const updateData = { ...formData };
        delete updateData.primary_user;
        console.log('Updating organization with data:', updateData);
        console.log('Selected organization ID:', selectedOrganization.id);
        await api.updateOrganization(selectedOrganization.id, updateData);
      }
      setShowModal(false);
      setError(null);
      loadOrganizations();
    } catch (err) {
      console.error('Error in handleSubmit:', err);
      if (Array.isArray(err)) {
        setError(err.join(', '));
      } else if (typeof err === 'string') {
        setError(err);
      } else {
        setError('Failed to save organization: ' + (err.message || 'Unknown error'));
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    console.log('Input change:', { name, value });
    
    if (name.startsWith('primary_user.')) {
      const field = name.substring(13);
      setFormData(prev => ({
        ...prev,
        primary_user: {
          ...prev.primary_user,
          [field]: value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const filteredOrganizations = Array.isArray(organizations) ? organizations.filter(organization => {
    const matchesSearch = !searchTerm || 
      organization.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      organization.domain?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      organization.contact_email?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesType = !typeFilter || organization.organization_type === typeFilter;
    
    return matchesSearch && matchesType;
  }) : [];

  const handleOrganizationClick = (organization) => {
    setSelectedOrganizationForActions(organization);
    setShowActionsPopup(true);
  };

  const closeActionsPopup = () => {
    setShowActionsPopup(false);
    setSelectedOrganizationForActions(null);
  };

  if (!active) return null;
  if (loading) return <LoadingSpinner fullscreen={true} />;
  if (error) return <div style={{ padding: '2rem', color: 'red' }}>{error}</div>;

  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif', position: 'relative' }}>
      {(operationLoading || submitting) && <LoadingSpinner fullscreen={true} />}
      <h1 style={{ marginBottom: '2rem', color: '#333' }}>Organisation Management</h1>
      
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
          placeholder="Search organisations..."
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
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          style={{
            padding: '0.5rem',
            border: '1px solid #ddd',
            borderRadius: '4px'
          }}
        >
          <option value="">All Types</option>
          {organizationTypes.map(type => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
        
        <button
          onClick={handleAddOrganization}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Add Organisation
        </button>
      </div>

      {/* Hint Text */}
      <div style={{ 
        marginBottom: '1rem', 
        color: '#6c757d', 
        fontSize: '0.875rem',
        textAlign: 'center'
      }}>
        💡 Click on any organisation row to view available actions
      </div>

      {/* Organizations List */}
      <div style={{ 
        backgroundColor: 'white',
        borderRadius: '12px',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
        border: '1px solid #e9ecef'
      }}>
        {filteredOrganizations.map(organization => (
          <div 
            key={organization.id} 
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              handleOrganizationClick(organization);
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
                  {organization.name}
                </div>
                <div style={{ color: '#495057' }}>
                  {organization.domain || 'N/A'}
                </div>
                <span style={{
                  padding: '0.25rem 0.5rem',
                  borderRadius: '4px',
                  fontSize: '0.75rem',
                  fontWeight: '600',
                  textTransform: 'uppercase',
                  backgroundColor: organization.organization_type === 'educational' ? '#d4edda' : 
                                   organization.organization_type === 'government' ? '#fff3cd' : '#f8f9fa',
                  color: organization.organization_type === 'educational' ? '#155724' : 
                         organization.organization_type === 'government' ? '#856404' : '#495057'
                }}>
                  {organization.organization_type}
                </span>
                <span style={{
                  padding: '0.25rem 0.5rem',
                  borderRadius: '4px',
                  fontSize: '0.75rem',
                  fontWeight: '600',
                  textTransform: 'uppercase',
                  backgroundColor: organization.is_active ? '#d4edda' : '#f8d7da',
                  color: organization.is_active ? '#155724' : '#721c24'
                }}>
                  {organization.is_active ? 'Active' : 'Inactive'}
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
                <span>{organization.contact_email || 'No email'}</span>
                {organization.description && <span>{organization.description.substring(0, 50)}...</span>}
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

      {filteredOrganizations.length === 0 && (
        <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
          No organisations found matching your criteria.
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
            maxWidth: '600px',
            width: '90%',
            maxHeight: '80vh',
            overflowY: 'auto'
          }}>
            <h2 style={{ marginBottom: '1.5rem', color: '#333' }}>
              {modalMode === 'add' ? 'Add New Organisation' : 
               modalMode === 'edit' ? 'Edit Organisation' : 'View Organisation'}
            </h2>
            
            {modalLoading ? (
              <LoadingSpinner size="medium" />
            ) : (
            
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                  Organisation Name *
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  disabled={modalMode === 'view'}
                  required
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

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                  Domain
                </label>
                <input
                  type="text"
                  name="domain"
                  value={formData.domain}
                  onChange={handleInputChange}
                  disabled={modalMode === 'view'}
                  placeholder="e.g., university.edu"
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

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                  Contact Email *
                </label>
                <input
                  type="email"
                  name="contact_email"
                  value={formData.contact_email}
                  onChange={handleInputChange}
                  disabled={modalMode === 'view'}
                  required
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

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                  Organisation Type *
                </label>
                <select
                  name="organization_type"
                  value={formData.organization_type}
                  onChange={handleInputChange}
                  disabled={modalMode === 'view'}
                  required
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    backgroundColor: modalMode === 'view' ? '#f8f9fa' : 'white',
                    color: '#333'
                  }}
                >
                  {organizationTypes.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                  Description
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  disabled={modalMode === 'view'}
                  rows="3"
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    backgroundColor: modalMode === 'view' ? '#f8f9fa' : 'white',
                    color: '#333',
                    resize: 'vertical'
                  }}
                />
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                  Website
                </label>
                <input
                  type="url"
                  name="website"
                  value={formData.website}
                  onChange={handleInputChange}
                  disabled={modalMode === 'view'}
                  placeholder="https://www.example.com"
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

              {modalMode === 'add' && (
                <div>
                  <h3 style={{ marginBottom: '1rem', color: '#333', borderTop: '1px solid #ddd', paddingTop: '1rem' }}>
                    Primary User (Administrator)
                  </h3>
                  
                  <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
                    <div style={{ flex: 1 }}>
                      <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                        Username *
                      </label>
                      <input
                        type="text"
                        name="primary_user.username"
                        value={formData.primary_user.username}
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
                    <div style={{ flex: 1 }}>
                      <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                        Email *
                      </label>
                      <input
                        type="email"
                        name="primary_user.email"
                        value={formData.primary_user.email}
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
                  </div>

                  <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
                    <div style={{ flex: 1 }}>
                      <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                        First Name *
                      </label>
                      <input
                        type="text"
                        name="primary_user.first_name"
                        value={formData.primary_user.first_name}
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
                    <div style={{ flex: 1 }}>
                      <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                        Last Name *
                      </label>
                      <input
                        type="text"
                        name="primary_user.last_name"
                        value={formData.primary_user.last_name}
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
                  </div>

                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                      Password *
                    </label>
                    <input
                      type="password"
                      name="primary_user.password"
                      value={formData.primary_user.password}
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
                </div>
              )}

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
                    {modalMode === 'add' ? 'Add Organisation' : 'Update Organisation'}
                  </button>
                )}
              </div>
            </form>
            )}
          </div>
        </div>
      )}

      {/* Actions Popup */}
      {showActionsPopup && selectedOrganizationForActions && (
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
                {selectedOrganizationForActions.name}
              </h3>
              <div style={{ 
                color: '#666', 
                fontSize: '0.875rem',
                marginBottom: '0.5rem'
              }}>
                {selectedOrganizationForActions.domain || 'No domain'}
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
                  backgroundColor: selectedOrganizationForActions.organization_type === 'educational' ? '#d4edda' : 
                                   selectedOrganizationForActions.organization_type === 'government' ? '#fff3cd' : '#f8f9fa',
                  color: selectedOrganizationForActions.organization_type === 'educational' ? '#155724' : 
                         selectedOrganizationForActions.organization_type === 'government' ? '#856404' : '#495057'
                }}>
                  {selectedOrganizationForActions.organization_type}
                </span>
                <span style={{
                  padding: '0.25rem 0.5rem',
                  borderRadius: '4px',
                  fontSize: '0.75rem',
                  fontWeight: '600',
                  textTransform: 'uppercase',
                  backgroundColor: selectedOrganizationForActions.is_active ? '#d4edda' : '#f8d7da',
                  color: selectedOrganizationForActions.is_active ? '#155724' : '#721c24'
                }}>
                  {selectedOrganizationForActions.is_active ? 'Active' : 'Inactive'}
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
                  handleViewOrganization(selectedOrganizationForActions.id);
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
              
              <button
                onClick={() => {
                  closeActionsPopup();
                  handleEditOrganization(selectedOrganizationForActions.id);
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
                Edit Organisation
              </button>
              
              {selectedOrganizationForActions.is_active ? (
                <button
                  onClick={() => {
                    closeActionsPopup();
                    handleDeleteOrganization(selectedOrganizationForActions.id, selectedOrganizationForActions.name);
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
                  Deactivate Organisation
                </button>
              ) : (
                <button
                  onClick={() => {
                    closeActionsPopup();
                    handleReactivateOrganization(selectedOrganizationForActions.id, selectedOrganizationForActions.name);
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
                  Reactivate Organisation
                </button>
              )}
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

export default OrganisationManagement;