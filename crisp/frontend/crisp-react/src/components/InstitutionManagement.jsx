import React, { useState, useEffect } from 'react';
import { getOrganizations, createOrganization, updateOrganization, deactivateOrganization, getOrganizationDetails } from '../api.js';
import LoadingSpinner from './LoadingSpinner.jsx';

const InstitutionManagement = ({ active = true }) => {
  const [institutions, setInstitutions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [modalMode, setModalMode] = useState('add'); // 'add', 'edit', 'view'
  const [selectedInstitution, setSelectedInstitution] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [modalLoading, setModalLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [operationLoading, setOperationLoading] = useState(false);
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

  const organizationTypes = ['educational', 'government', 'private'];

  useEffect(() => {
    if (active) {
      loadInstitutions();
    }
  }, [active]);

  const loadInstitutions = async () => {
    try {
      setLoading(true);
      await new Promise(resolve => setTimeout(resolve, 1000));
      const response = await getOrganizations();
      console.log('Institutions API response:', response);
      const institutionsData = response.data?.organizations || response.organizations || response.data || [];
      setInstitutions(Array.isArray(institutionsData) ? institutionsData : []);
    } catch (err) {
      console.error('Failed to load institutions:', err);
      setError('Failed to load institutions: ' + err.message);
      setInstitutions([]);
    } finally {
      setLoading(false);
    }
  };

  const handleAddInstitution = () => {
    setModalMode('add');
    setSelectedInstitution(null);
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

  const handleEditInstitution = async (institutionId) => {
    try {
      setModalLoading(true);
      await new Promise(resolve => setTimeout(resolve, 800));
      const response = await getOrganizationDetails(institutionId);
      console.log('Edit institution response:', response);
      
      const institution = response.data?.organization || response.organization || response.data;
      console.log('Edit institution data:', institution);
      
      if (!institution) {
        console.error('Institution data not found in response. Full response:', response);
        throw new Error('Institution data not found in response');
      }
      
      if (!institution.name) {
        console.error('Institution name is missing from institution data:', institution);
        throw new Error('Invalid institution data: missing name');
      }
      
      setModalMode('edit');
      setSelectedInstitution(institution);
      const formDataToSet = {
        name: institution.name || '',
        domain: institution.domain || '',
        contact_email: institution.contact_email || '',
        description: institution.description || '',
        website: institution.website || '',
        organization_type: institution.organization_type || 'educational',
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
      console.error('Error in handleEditInstitution:', err);
      setError('Failed to load institution details: ' + (err.message || err));
    } finally {
      setModalLoading(false);
    }
  };

  const handleViewInstitution = async (institutionId) => {
    try {
      setModalLoading(true);
      await new Promise(resolve => setTimeout(resolve, 800));
      const response = await getOrganizationDetails(institutionId);
      console.log('View institution response:', response);
      
      const institution = response.data?.organization || response.organization || response.data;
      console.log('View institution data:', institution);
      
      if (!institution) {
        console.error('Institution data not found in response. Full response:', response);
        throw new Error('Institution data not found in response');
      }
      
      if (!institution.name) {
        console.error('Institution name is missing from institution data:', institution);
        throw new Error('Invalid institution data: missing name');
      }
      
      setModalMode('view');
      setSelectedInstitution(institution);
      const formDataToSet = {
        name: institution.name || '',
        domain: institution.domain || '',
        contact_email: institution.contact_email || '',
        description: institution.description || '',
        website: institution.website || '',
        organization_type: institution.organization_type || 'educational',
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
      console.error('Error in handleViewInstitution:', err);
      setError('Failed to load institution details: ' + (err.message || err));
    } finally {
      setModalLoading(false);
    }
  };

  const handleDeleteInstitution = async (institutionId, institutionName) => {
    if (window.confirm(`Are you sure you want to deactivate institution "${institutionName}"?`)) {
      try {
        setOperationLoading(true);
        await new Promise(resolve => setTimeout(resolve, 800));
        await deactivateOrganization(institutionId, 'Deactivated by admin');
        loadInstitutions();
      } catch (err) {
        setError('Failed to deactivate institution: ' + err.message);
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
        console.log('Creating institution with data:', formData);
        await createOrganization(formData);
      } else if (modalMode === 'edit') {
        const updateData = { ...formData };
        delete updateData.primary_user; // Don't send primary_user for updates
        console.log('Updating institution with data:', updateData);
        console.log('Selected institution ID:', selectedInstitution.id);
        await updateOrganization(selectedInstitution.id, updateData);
      }
      setShowModal(false);
      loadInstitutions();
    } catch (err) {
      console.error('Error in handleSubmit:', err);
      setError('Failed to save institution: ' + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    console.log('Input change:', { name, value });
    
    if (name.startsWith('primary_user.')) {
      const field = name.substring(13); // Remove 'primary_user.'
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

  const filteredInstitutions = Array.isArray(institutions) ? institutions.filter(institution => {
    const matchesSearch = !searchTerm || 
      institution.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      institution.domain?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      institution.contact_email?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesType = !typeFilter || institution.organization_type === typeFilter;
    const matchesStatus = !statusFilter || 
      (statusFilter === 'active' && institution.is_active) ||
      (statusFilter === 'inactive' && !institution.is_active);
    
    return matchesSearch && matchesType && matchesStatus;
  }) : [];

  if (!active) return null;
  if (loading) return <LoadingSpinner fullscreen={true} />;
  if (error) return <div style={{ padding: '2rem', color: 'red' }}>{error}</div>;

  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif', position: 'relative' }}>
      {(operationLoading || submitting) && <LoadingSpinner fullscreen={true} />}
      <h1 style={{ marginBottom: '2rem', color: '#333' }}>Institution Management</h1>
      
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
          placeholder="Search institutions..."
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
        
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          style={{
            padding: '0.5rem',
            border: '1px solid #ddd',
            borderRadius: '4px'
          }}
        >
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
        
        <button
          onClick={handleAddInstitution}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Add Institution
        </button>
      </div>

      {/* Institutions Table */}
      <div style={{ overflowX: 'auto' }}>
        <table style={{ 
          width: '100%', 
          borderCollapse: 'collapse',
          backgroundColor: 'white',
          borderRadius: '8px',
          overflow: 'hidden',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <thead>
            <tr style={{ backgroundColor: '#f8f9fa' }}>
              <th style={{ padding: '1rem', textAlign: 'left', borderBottom: '1px solid #ddd' }}>Name</th>
              <th style={{ padding: '1rem', textAlign: 'left', borderBottom: '1px solid #ddd' }}>Domain</th>
              <th style={{ padding: '1rem', textAlign: 'left', borderBottom: '1px solid #ddd' }}>Type</th>
              <th style={{ padding: '1rem', textAlign: 'left', borderBottom: '1px solid #ddd' }}>Contact Email</th>
              <th style={{ padding: '1rem', textAlign: 'left', borderBottom: '1px solid #ddd' }}>Status</th>
              <th style={{ padding: '1rem', textAlign: 'left', borderBottom: '1px solid #ddd' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredInstitutions.map(institution => (
              <tr key={institution.id} style={{ borderBottom: '1px solid #eee' }}>
                <td style={{ padding: '1rem' }}>{institution.name}</td>
                <td style={{ padding: '1rem' }}>{institution.domain || 'N/A'}</td>
                <td style={{ padding: '1rem' }}>
                  <span style={{
                    padding: '0.25rem 0.5rem',
                    borderRadius: '4px',
                    fontSize: '0.875rem',
                    backgroundColor: institution.organization_type === 'educational' ? '#d4edda' : 
                                     institution.organization_type === 'government' ? '#fff3cd' : '#f8f9fa',
                    color: institution.organization_type === 'educational' ? '#155724' : 
                           institution.organization_type === 'government' ? '#856404' : '#495057'
                  }}>
                    {institution.organization_type}
                  </span>
                </td>
                <td style={{ padding: '1rem' }}>{institution.contact_email || 'N/A'}</td>
                <td style={{ padding: '1rem' }}>
                  <span style={{
                    padding: '0.25rem 0.5rem',
                    borderRadius: '4px',
                    fontSize: '0.875rem',
                    backgroundColor: institution.is_active ? '#d4edda' : '#f8d7da',
                    color: institution.is_active ? '#155724' : '#721c24'
                  }}>
                    {institution.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td style={{ padding: '1rem' }}>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button
                      onClick={() => handleViewInstitution(institution.id)}
                      style={{
                        padding: '0.25rem 0.5rem',
                        backgroundColor: '#17a2b8',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '0.875rem'
                      }}
                    >
                      View
                    </button>
                    <button
                      onClick={() => handleEditInstitution(institution.id)}
                      style={{
                        padding: '0.25rem 0.5rem',
                        backgroundColor: '#ffc107',
                        color: 'black',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '0.875rem'
                      }}
                    >
                      Edit
                    </button>
                    {institution.is_active && (
                      <button
                        onClick={() => handleDeleteInstitution(institution.id, institution.name)}
                        style={{
                          padding: '0.25rem 0.5rem',
                          backgroundColor: '#dc3545',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '0.875rem'
                        }}
                      >
                        Deactivate
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredInstitutions.length === 0 && (
        <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
          No institutions found matching your criteria.
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
              {modalMode === 'add' ? 'Add New Institution' : 
               modalMode === 'edit' ? 'Edit Institution' : 'View Institution'}
            </h2>
            
            {modalLoading ? (
              <LoadingSpinner size="medium" />
            ) : (
            
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                  Institution Name *
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
                  Organization Type *
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
                    {modalMode === 'add' ? 'Add Institution' : 'Update Institution'}
                  </button>
                )}
              </div>
            </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default InstitutionManagement;