import React, { useState, useEffect } from 'react';
import * as api from '../api.js';
import LoadingSpinner from './LoadingSpinner.jsx';
import ConfirmationModal from './ConfirmationModal.jsx';
import Pagination from './Pagination.jsx';

function TrustManagement({ active, initialTab = null }) {
  console.log('TrustManagement rendered with props:', { active, initialTab });
  
  // State management
  const [trustData, setTrustData] = useState({
    relationships: [],
    groups: [],
    metrics: {},
    organizations: [],
    trustLevels: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // UI state
  const [activeTab, setActiveTab] = useState(() => {
    if (initialTab && ['relationships', 'groups', 'metrics'].includes(initialTab)) {
      return initialTab;
    }
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('tab') || 'relationships';
  });
  
  // Modal states
  const [showModal, setShowModal] = useState(false);
  const [modalMode, setModalMode] = useState('add'); // 'add', 'edit'
  const [modalType, setModalType] = useState('relationship'); // 'relationship', 'group'
  const [selectedItem, setSelectedItem] = useState(null);
  const [modalLoading, setModalLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  
  // Actions popup
  const [showActionsPopup, setShowActionsPopup] = useState(false);
  const [selectedItemForActions, setSelectedItemForActions] = useState(null);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [confirmationData, setConfirmationData] = useState(null);
  
  // Detail view modal
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [detailItem, setDetailItem] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  
  // Search and filter
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);
  
  // Form data
  const [formData, setFormData] = useState({
    source_organization: '',
    target_organization: '',
    trust_level: '',
    relationship_type: 'bilateral',
    notes: '',
    // Group fields
    name: '',
    description: '',
    group_type: 'industry',
    is_public: false,
    requires_approval: true
  });

  // Get current user data
  const currentUser = JSON.parse(localStorage.getItem('crisp_user') || '{}');
  const isAdmin = currentUser.role === 'BlueVisionAdmin';

  // Load trust data when component becomes active
  useEffect(() => {
    if (active) {
      fetchTrustData();
    }
  }, [active]);

  // Update tab when initialTab prop changes
  useEffect(() => {
    if (initialTab && ['relationships', 'groups', 'metrics'].includes(initialTab)) {
      setActiveTab(initialTab);
    }
  }, [initialTab]);

  const fetchTrustData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [
        relationshipsResponse,
        groupsResponse,
        metricsResponse,
        orgsResponse,
        trustLevelsResponse
      ] = await Promise.all([
        api.getTrustRelationships().catch(err => ({ data: [] })),
        api.getTrustGroups().catch(err => ({ data: [] })),
        api.getTrustMetrics().catch(err => ({ data: {} })),
        api.getOrganizations().catch(err => ({ data: [] })),
        api.getTrustLevels().catch(err => [])
      ]);

      setTrustData({
        relationships: Array.isArray(relationshipsResponse.data) ? relationshipsResponse.data : 
                      Array.isArray(relationshipsResponse) ? relationshipsResponse : [],
        groups: Array.isArray(groupsResponse.data) ? groupsResponse.data : 
                Array.isArray(groupsResponse) ? groupsResponse : [],
        metrics: (metricsResponse.data && typeof metricsResponse.data === 'object') ? metricsResponse.data : 
                (metricsResponse && typeof metricsResponse === 'object') ? metricsResponse : {},
        organizations: Array.isArray(orgsResponse.data?.organizations) ? orgsResponse.data.organizations : 
                      Array.isArray(orgsResponse.data) ? orgsResponse.data : 
                      Array.isArray(orgsResponse) ? orgsResponse : [],
        trustLevels: Array.isArray(trustLevelsResponse) ? trustLevelsResponse : []
      });
    } catch (err) {
      console.error('Error fetching trust data:', err);
      setError('Failed to load trust data');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (tabName) => {
    if (!['relationships', 'groups', 'metrics'].includes(tabName) || tabName === activeTab) {
      return;
    }
    
    setActiveTab(tabName);
    
    // Update URL without causing re-renders
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set('tab', tabName);
    const newUrl = `${window.location.pathname}?${urlParams.toString()}`;
    window.history.replaceState(null, '', newUrl);
  };

  const openModal = (mode, type, item = null) => {
    setModalMode(mode);
    setModalType(type);
    setSelectedItem(item);
    
    if (mode === 'edit' && item) {
      if (type === 'relationship') {
        setFormData({
          target_organization: item.target_organization || '',
          trust_level: item.trust_level_id || '',
          relationship_type: item.relationship_type || 'bilateral',
          notes: item.notes || ''
        });
      } else if (type === 'group') {
        setFormData({
          name: item.name || '',
          description: item.description || '',
          group_type: item.group_type || 'industry',
          is_public: item.is_public || false,
          requires_approval: item.requires_approval || true,
          trust_level: item.default_trust_level_id || ''
        });
      }
    } else {
      setFormData({
        target_organization: '',
        trust_level: '',
        relationship_type: 'bilateral',
        notes: '',
        name: '',
        description: '',
        group_type: 'industry',
        is_public: false,
        requires_approval: true
      });
    }
    
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedItem(null);
    setModalLoading(false);
    setSubmitting(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    // Show confirmation dialog
    const actionText = modalMode === 'add' ? 'create' : 'update';
    const itemName = modalType === 'relationship' ? 
      `relationship with ${trustData.organizations.find(org => org.id === formData.target_organization)?.name || 'selected organization'}` :
      formData.name;
    
    setConfirmationData({
      title: `${modalMode === 'add' ? 'Create' : 'Update'} ${modalType === 'relationship' ? 'Trust Relationship' : 'Trust Group'}`,
      message: `Are you sure you want to ${actionText} ${modalType} "${itemName}"?`,
      confirmText: modalMode === 'add' ? `Create ${modalType === 'relationship' ? 'Relationship' : 'Group'}` : `Update ${modalType === 'relationship' ? 'Relationship' : 'Group'}`,
      isDestructive: false,
      actionType: 'default',
      action: async () => {
        try {
          setSubmitting(true);
          
          if (modalType === 'relationship') {
            if (modalMode === 'add') {
              await api.createTrustRelationship(formData);
              setSuccess('Trust relationship created successfully');
            } else {
              await api.updateTrustRelationship(selectedItem.id, formData);
              setSuccess('Trust relationship updated successfully');
            }
          } else if (modalType === 'group') {
            const groupData = { ...formData };
            if (formData.trust_level) {
              groupData.default_trust_level_id = formData.trust_level;
              delete groupData.trust_level;
            }
            
            if (modalMode === 'add') {
              await api.createTrustGroup(groupData);
              setSuccess('Trust group created successfully');
            } else {
              await api.updateTrustGroup(selectedItem.id, groupData);
              setSuccess('Trust group updated successfully');
            }
          }
          
          // Auto-dismiss success message after 5 seconds
          setTimeout(() => setSuccess(null), 5000);
          
          closeModal();
          fetchTrustData();
          
        } catch (error) {
          console.error(`Error ${actionText}ing ${modalType}:`, error);
          setError(`Failed to ${actionText} ${modalType}: ${error.message || error}`);
        } finally {
          setSubmitting(false);
        }
      }
    });
    setShowConfirmation(true);
  };

  const openActionsPopup = (item) => {
    setSelectedItemForActions(item);
    setShowActionsPopup(true);
  };

  const closeActionsPopup = () => {
    setShowActionsPopup(false);
    setSelectedItemForActions(null);
  };

  const handleAction = (actionType) => {
    const item = selectedItemForActions;
    if (!item) return;

    switch (actionType) {
      case 'view':
        closeActionsPopup();
        setDetailItem(item);
        setShowDetailModal(true);
        break;
        
      case 'edit':
        closeActionsPopup();
        openModal('edit', activeTab === 'relationships' ? 'relationship' : 'group', item);
        break;
        
      case 'activate':
        setConfirmationData({
          title: 'Activate Relationship',
          message: `Are you sure you want to activate the relationship with ${item.target_organization_name || item.target_organization}?`,
          confirmText: 'Activate',
          isDestructive: false,
          actionType: 'default',
          action: async () => {
            try {
              await api.updateTrustRelationship(item.id, { status: 'active' });
              setSuccess('Relationship activated successfully');
              setTimeout(() => setSuccess(null), 5000);
              closeActionsPopup();
              fetchTrustData();
            } catch (error) {
              setError('Failed to activate relationship: ' + error.message);
            }
          }
        });
        setShowConfirmation(true);
        break;
        
      case 'suspend':
        setConfirmationData({
          title: 'Suspend Relationship',
          message: `Are you sure you want to suspend the relationship with ${item.target_organization_name || item.target_organization}?`,
          confirmText: 'Suspend',
          isDestructive: true,
          actionType: 'destructive',
          action: async () => {
            try {
              await api.updateTrustRelationship(item.id, { status: 'suspended' });
              setSuccess('Relationship suspended successfully');
              setTimeout(() => setSuccess(null), 5000);
              closeActionsPopup();
              fetchTrustData();
            } catch (error) {
              setError('Failed to suspend relationship: ' + error.message);
            }
          }
        });
        setShowConfirmation(true);
        break;
        
      case 'delete':
        const itemName = activeTab === 'relationships' ? 
          `relationship with ${item.target_organization_name || item.target_organization}` :
          `group "${item.name}"`;
          
        setConfirmationData({
          title: `Delete ${activeTab === 'relationships' ? 'Trust Relationship' : 'Trust Group'}`,
          message: `Are you sure you want to delete this ${itemName}? This action cannot be undone.`,
          confirmText: 'Delete',
          isDestructive: true,
          actionType: 'destructive',
          action: async () => {
            try {
              if (activeTab === 'relationships') {
                await api.deleteTrustRelationship(item.id);
                setSuccess('Trust relationship deleted successfully');
              } else {
                await api.deleteTrustGroup(item.id);
                setSuccess('Trust group deleted successfully');
              }
              setTimeout(() => setSuccess(null), 5000);
              closeActionsPopup();
              fetchTrustData();
            } catch (error) {
              setError(`Failed to delete ${activeTab === 'relationships' ? 'relationship' : 'group'}: ${error.message}`);
            }
          }
        });
        setShowConfirmation(true);
        break;
        
      case 'join':
        setConfirmationData({
          title: 'Join Trust Group',
          message: `Are you sure you want to join the group "${item.name}"?`,
          confirmText: 'Join Group',
          isDestructive: false,
          actionType: 'default',
          action: async () => {
            try {
              await api.joinTrustGroup(item.id);
              setSuccess('Successfully joined trust group!');
              setTimeout(() => setSuccess(null), 5000);
              closeActionsPopup();
              fetchTrustData();
            } catch (error) {
              setError('Failed to join trust group: ' + error.message);
            }
          }
        });
        setShowConfirmation(true);
        break;
    }
  };

  // Filter and paginate data
  const getFilteredData = () => {
    const data = activeTab === 'relationships' ? trustData.relationships : trustData.groups;
    
    let filtered = data.filter(item => {
      const matchesSearch = searchTerm === '' || 
        (activeTab === 'relationships' ? 
          (item.target_organization_name || item.target_organization || '').toLowerCase().includes(searchTerm.toLowerCase()) :
          (item.name || '').toLowerCase().includes(searchTerm.toLowerCase())
        );
      
      const matchesStatus = statusFilter === '' || 
        (activeTab === 'relationships' ? 
          item.status === statusFilter :
          (statusFilter === 'public' ? item.is_public : !item.is_public)
        );
      
      return matchesSearch && matchesStatus;
    });
    
    return filtered;
  };

  const filteredData = getFilteredData();
  const totalItems = filteredData.length;
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedData = filteredData.slice(startIndex, startIndex + itemsPerPage);

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  if (!active) {
    return null;
  }

  if (loading) {
    return (
      <div className="trust-management">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif', position: 'relative' }}>
      {(loading || submitting) && <LoadingSpinner fullscreen={true} />}
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ marginBottom: '0.5rem', color: '#333' }}>Trust Management</h1>
        {!isAdmin && (
          <div style={{
            padding: '0.75rem 1rem',
            backgroundColor: '#fff3cd',
            color: '#856404',
            borderRadius: '6px',
            border: '1px solid #ffeaa7',
            fontSize: '0.875rem',
            fontWeight: '500'
          }}>
            <strong>Publisher Mode:</strong> You can manage trust relationships and groups for your organization and organizations with trusted relationships.
          </div>
        )}
      </div>

      {/* Error/Success Messages */}
      {error && (
        <div style={{
          backgroundColor: '#f8d7da',
          color: '#721c24',
          border: '1px solid #f5c6cb',
          borderRadius: '4px',
          padding: '0.75rem 1rem',
          marginBottom: '1rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <span>{error}</span>
          <button 
            onClick={() => setError(null)}
            style={{
              background: 'none',
              border: 'none',
              color: '#721c24',
              fontSize: '1.25rem',
              cursor: 'pointer',
              padding: '0',
              lineHeight: '1'
            }}
          >
            ×
          </button>
        </div>
      )}

      {success && (
        <div style={{
          backgroundColor: '#d4edda',
          color: '#155724',
          border: '1px solid #c3e6cb',
          borderRadius: '4px',
          padding: '0.75rem 1rem',
          marginBottom: '1rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <span>{success}</span>
          <button 
            onClick={() => setSuccess(null)}
            style={{
              background: 'none',
              border: 'none',
              color: '#155724',
              fontSize: '1.25rem',
              cursor: 'pointer',
              padding: '0',
              lineHeight: '1'
            }}
          >
            ×
          </button>
        </div>
      )}

      {/* Tabs */}
      <div style={{ marginBottom: '1.5rem' }}>
        <div style={{ borderBottom: '1px solid #dee2e6' }}>
          {['relationships', 'groups', 'metrics'].map(tab => (
            <button
              key={tab}
              onClick={() => handleTabChange(tab)}
              style={{
                padding: '0.75rem 1.5rem',
                border: 'none',
                backgroundColor: activeTab === tab ? '#007bff' : 'transparent',
                color: activeTab === tab ? 'white' : '#495057',
                borderRadius: '4px 4px 0 0',
                marginRight: '0.25rem',
                cursor: 'pointer',
                textTransform: 'capitalize',
                fontWeight: activeTab === tab ? '600' : '400'
              }}
            >
              {tab} ({tab === 'relationships' ? trustData.relationships.length : 
                     tab === 'groups' ? trustData.groups.length : 'N/A'})
            </button>
          ))}
        </div>
      </div>

      {/* Content based on active tab */}
      {activeTab !== 'metrics' && (
        <>
          {/* Controls */}
          <div style={{ 
            display: 'flex', 
            gap: '1rem', 
            marginBottom: '2rem',
            flexWrap: 'wrap',
            alignItems: 'center'
          }}>
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flex: 1 }}>
              <input
                type="text"
                placeholder={`Search ${activeTab}...`}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{
                  padding: '0.5rem',
                  border: '1px solid #ced4da',
                  borderRadius: '4px',
                  minWidth: '200px'
                }}
              />
              
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                style={{
                  padding: '0.5rem',
                  border: '1px solid #ced4da',
                  borderRadius: '4px',
                  minWidth: '120px'
                }}
              >
                <option value="">All Status</option>
                {activeTab === 'relationships' ? (
                  <>
                    <option value="active">Active</option>
                    <option value="pending">Pending</option>
                    <option value="suspended">Suspended</option>
                  </>
                ) : (
                  <>
                    <option value="public">Public</option>
                    <option value="private">Private</option>
                  </>
                )}
              </select>
            </div>
            
            <button
              onClick={() => openModal('add', activeTab === 'relationships' ? 'relationship' : 'group')}
              disabled={!isAdmin && activeTab === 'groups'}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: (!isAdmin && activeTab === 'groups') ? '#6c757d' : '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: (!isAdmin && activeTab === 'groups') ? 'not-allowed' : 'pointer',
                fontWeight: '500'
              }}
              title={(!isAdmin && activeTab === 'groups') ? 'Only administrators can create trust groups' : ''}
            >
              Add {activeTab === 'relationships' ? 'Relationship' : 'Group'}
            </button>
          </div>

          {/* Data List */}
          <div style={{ 
            backgroundColor: 'white',
            borderRadius: '8px',
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
            border: '1px solid #e9ecef'
          }}>
            {paginatedData.length === 0 ? (
              <div style={{ 
                textAlign: 'center', 
                padding: '3rem', 
                color: '#6c757d'
              }}>
                <h4 style={{ marginBottom: '0.5rem' }}>No {activeTab} found</h4>
                <p style={{ margin: '0' }}>
                  {filteredData.length === 0 && (searchTerm || statusFilter) ? 
                    'No items match your search criteria.' :
                    `No ${activeTab} available. Click "Add ${activeTab === 'relationships' ? 'Relationship' : 'Group'}" to create the first one.`
                  }
                </p>
              </div>
            ) : (
              paginatedData.map((item) => (
                <div 
                  key={item.id}
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    openActionsPopup(item);
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
                    {activeTab === 'relationships' ? (
                      <>
                        <div style={{ 
                          display: 'flex', 
                          alignItems: 'center', 
                          gap: '1rem',
                          flexWrap: 'wrap'
                        }}>
                          <div style={{ fontWeight: '600', color: '#212529', fontSize: '1.1rem' }}>
                            {item.source_organization_name} → {item.target_organization_name || item.target_organization}
                          </div>
                          <span style={{
                            padding: '0.25rem 0.5rem',
                            borderRadius: '4px',
                            fontSize: '0.75rem',
                            fontWeight: '600',
                            textTransform: 'uppercase',
                            backgroundColor: item.trust_level === 'HIGH' ? '#d4edda' : item.trust_level === 'MEDIUM' ? '#fff3cd' : '#f8f9fa',
                            color: item.trust_level === 'HIGH' ? '#155724' : item.trust_level === 'MEDIUM' ? '#856404' : '#495057'
                          }}>
                            {item.trust_level}
                          </span>
                          <span style={{
                            padding: '0.25rem 0.5rem',
                            borderRadius: '4px',
                            fontSize: '0.75rem',
                            fontWeight: '600',
                            textTransform: 'uppercase',
                            backgroundColor: item.status === 'active' ? '#d4edda' : item.status === 'pending' ? '#fff3cd' : '#f8d7da',
                            color: item.status === 'active' ? '#155724' : item.status === 'pending' ? '#856404' : '#721c24'
                          }}>
                            {item.status || 'Unknown'}
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
                          <span>Type: {item.relationship_type}</span>
                          {item.notes && <span>Notes: {item.notes}</span>}
                        </div>
                      </>
                    ) : (
                      <>
                        <div style={{ 
                          display: 'flex', 
                          alignItems: 'center', 
                          gap: '1rem',
                          flexWrap: 'wrap'
                        }}>
                          <div style={{ fontWeight: '600', color: '#212529', fontSize: '1.1rem' }}>
                            {item.name}
                          </div>
                          <span style={{
                            padding: '0.25rem 0.5rem',
                            borderRadius: '4px',
                            fontSize: '0.75rem',
                            fontWeight: '600',
                            textTransform: 'uppercase',
                            backgroundColor: item.group_type === 'SECURITY' ? '#d4edda' : item.group_type === 'BUSINESS' ? '#fff3cd' : '#f8f9fa',
                            color: item.group_type === 'SECURITY' ? '#155724' : item.group_type === 'BUSINESS' ? '#856404' : '#495057'
                          }}>
                            {item.group_type}
                          </span>
                          <span style={{
                            padding: '0.25rem 0.5rem',
                            borderRadius: '4px',
                            fontSize: '0.75rem',
                            fontWeight: '600',
                            textTransform: 'uppercase',
                            backgroundColor: item.is_public ? '#d4edda' : '#fff3cd',
                            color: item.is_public ? '#155724' : '#856404'
                          }}>
                            {item.is_public ? 'Public' : 'Private'}
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
                          <span>{item.description}</span>
                          <span>Members: {item.member_count || 0}</span>
                        </div>
                      </>
                    )}
                  </div>
                  <div style={{ 
                    fontSize: '1.2rem', 
                    color: '#6c757d',
                    marginLeft: '1rem',
                    transition: 'transform 0.2s ease'
                  }}>
                    →
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Pagination */}
          {totalItems > itemsPerPage && (
            <div style={{ marginTop: '1rem' }}>
              <Pagination
                currentPage={currentPage}
                totalItems={totalItems}
                itemsPerPage={itemsPerPage}
                onPageChange={handlePageChange}
                showInfo={true}
                showJumpToPage={true}
              />
            </div>
          )}
        </>
      )}

      {/* Metrics Tab */}
      {activeTab === 'metrics' && (
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
          gap: '1rem'
        }}>
          {[
            { 
              title: 'Total Relationships', 
              value: trustData.relationships.length, 
              description: isAdmin ? 'All system relationships' : 'Your organization relationships' 
            },
            { 
              title: 'Active Groups', 
              value: trustData.groups.length, 
              description: isAdmin ? 'All system groups' : 'Your accessible groups' 
            },
            { 
              title: 'Trust Score', 
              value: trustData.metrics.trust_score || 'N/A', 
              description: isAdmin ? 'System average' : 'Organization trust score' 
            },
            { 
              title: 'Connected Organizations', 
              value: trustData.metrics.connected_orgs || 0, 
              description: isAdmin ? 'Total connected orgs' : 'Organizations you trust' 
            }
          ].map((metric, index) => (
            <div key={index} style={{
              backgroundColor: 'white',
              border: '1px solid #dee2e6',
              borderRadius: '8px',
              padding: '1.5rem',
              textAlign: 'center'
            }}>
              <h4 style={{ margin: '0 0 0.5rem 0', color: '#495057', fontSize: '1rem' }}>
                {metric.title}
              </h4>
              <div style={{ 
                fontSize: '2rem', 
                fontWeight: 'bold', 
                color: '#007bff',
                margin: '0.5rem 0'
              }}>
                {metric.value}
              </div>
              <div style={{ 
                fontSize: '0.75rem', 
                color: '#6c757d',
                fontStyle: 'italic'
              }}>
                {metric.description}
              </div>
            </div>
          ))}
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
            borderRadius: '8px',
            padding: '1.5rem',
            width: '90%',
            maxWidth: '500px',
            maxHeight: '90vh',
            overflowY: 'auto'
          }}>
            <h3 style={{ margin: '0 0 1rem 0' }}>
              {modalMode === 'add' ? 'Create' : 'Edit'} {modalType === 'relationship' ? 'Trust Relationship' : 'Trust Group'}
            </h3>
            
            <form onSubmit={handleSubmit}>
              {modalType === 'relationship' ? (
                <>
                  {isAdmin && (
                    <div style={{ marginBottom: '1rem' }}>
                      <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                        Source Organization *
                      </label>
                      <select
                        value={formData.source_organization || ''}
                        onChange={(e) => setFormData({...formData, source_organization: e.target.value})}
                        required={isAdmin}
                        style={{
                          width: '100%',
                          padding: '0.5rem',
                          border: '1px solid #ced4da',
                          borderRadius: '4px'
                        }}
                      >
                        <option value="">Select Source Organization</option>
                        {trustData.organizations.map(org => (
                          <option key={org.id} value={org.id}>{org.name}</option>
                        ))}
                      </select>
                    </div>
                  )}
                  
                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                      Target Organization *
                    </label>
                    <select
                      value={formData.target_organization}
                      onChange={(e) => setFormData({...formData, target_organization: e.target.value})}
                      required
                      style={{
                        width: '100%',
                        padding: '0.5rem',
                        border: '1px solid #ced4da',
                        borderRadius: '4px'
                      }}
                    >
                      <option value="">Select Organization</option>
                      {trustData.organizations.map(org => (
                        <option key={org.id} value={org.id}>{org.name}</option>
                      ))}
                    </select>
                  </div>
                  
                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                      Trust Level *
                    </label>
                    <select
                      value={formData.trust_level}
                      onChange={(e) => setFormData({...formData, trust_level: e.target.value})}
                      required
                      style={{
                        width: '100%',
                        padding: '0.5rem',
                        border: '1px solid #ced4da',
                        borderRadius: '4px'
                      }}
                    >
                      <option value="">Select Trust Level</option>
                      {trustData.trustLevels.map(level => (
                        <option key={level.id} value={level.id}>{level.name}</option>
                      ))}
                    </select>
                  </div>
                  
                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                      Relationship Type
                    </label>
                    <select
                      value={formData.relationship_type}
                      onChange={(e) => setFormData({...formData, relationship_type: e.target.value})}
                      style={{
                        width: '100%',
                        padding: '0.5rem',
                        border: '1px solid #ced4da',
                        borderRadius: '4px'
                      }}
                    >
                      <option value="bilateral">Bilateral</option>
                      <option value="unilateral">Unilateral</option>
                    </select>
                  </div>
                  
                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                      Notes
                    </label>
                    <textarea
                      value={formData.notes}
                      onChange={(e) => setFormData({...formData, notes: e.target.value})}
                      rows={3}
                      placeholder="Optional notes about this relationship..."
                      style={{
                        width: '100%',
                        padding: '0.5rem',
                        border: '1px solid #ced4da',
                        borderRadius: '4px',
                        resize: 'vertical'
                      }}
                    />
                  </div>
                </>
              ) : (
                <>
                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                      Group Name *
                    </label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      required
                      placeholder="Enter group name..."
                      style={{
                        width: '100%',
                        padding: '0.5rem',
                        border: '1px solid #ced4da',
                        borderRadius: '4px'
                      }}
                    />
                  </div>
                  
                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                      Description
                    </label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData({...formData, description: e.target.value})}
                      rows={3}
                      placeholder="Describe the purpose of this group..."
                      style={{
                        width: '100%',
                        padding: '0.5rem',
                        border: '1px solid #ced4da',
                        borderRadius: '4px',
                        resize: 'vertical'
                      }}
                    />
                  </div>
                  
                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                      Group Type
                    </label>
                    <select
                      value={formData.group_type}
                      onChange={(e) => setFormData({...formData, group_type: e.target.value})}
                      style={{
                        width: '100%',
                        padding: '0.5rem',
                        border: '1px solid #ced4da',
                        borderRadius: '4px'
                      }}
                    >
                      <option value="industry">Industry</option>
                      <option value="regional">Regional</option>
                      <option value="security">Security</option>
                      <option value="research">Research</option>
                    </select>
                  </div>
                  
                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                      Trust Level
                    </label>
                    <select
                      value={formData.trust_level}
                      onChange={(e) => setFormData({...formData, trust_level: e.target.value})}
                      style={{
                        width: '100%',
                        padding: '0.5rem',
                        border: '1px solid #ced4da',
                        borderRadius: '4px'
                      }}
                    >
                      <option value="">Select Trust Level</option>
                      {trustData.trustLevels.map(level => (
                        <option key={level.id} value={level.id}>{level.name}</option>
                      ))}
                    </select>
                  </div>
                  
                  <div style={{ marginBottom: '1rem', display: 'flex', gap: '1rem' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <input
                        type="checkbox"
                        checked={formData.is_public}
                        onChange={(e) => setFormData({...formData, is_public: e.target.checked})}
                      />
                      Public Group
                    </label>
                    
                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <input
                        type="checkbox"
                        checked={formData.requires_approval}
                        onChange={(e) => setFormData({...formData, requires_approval: e.target.checked})}
                      />
                      Requires Approval
                    </label>
                  </div>
                </>
              )}
              
              <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end', marginTop: '1.5rem' }}>
                <button
                  type="button"
                  onClick={closeModal}
                  disabled={submitting}
                  style={{
                    padding: '0.5rem 1rem',
                    backgroundColor: '#6c757d',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: submitting ? 'not-allowed' : 'pointer'
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  style={{
                    padding: '0.5rem 1rem',
                    backgroundColor: '#007bff',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: submitting ? 'not-allowed' : 'pointer'
                  }}
                >
                  {submitting ? 'Saving...' : (modalMode === 'add' ? 'Create' : 'Update')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Actions Popup */}
      {showActionsPopup && selectedItemForActions && (
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
                {activeTab === 'relationships' ? 
                  `${selectedItemForActions.source_organization_name} → ${selectedItemForActions.target_organization_name || selectedItemForActions.target_organization}` :
                  selectedItemForActions.name
                }
              </h3>
              <div style={{ 
                color: '#666', 
                fontSize: '0.875rem',
                marginBottom: '0.5rem'
              }}>
                {activeTab === 'relationships' ? 
                  `Trust Level: ${selectedItemForActions.trust_level}` :
                  selectedItemForActions.description
                }
              </div>
              <div style={{ 
                color: '#666', 
                fontSize: '0.875rem',
                display: 'flex',
                gap: '0.5rem',
                alignItems: 'center'
              }}>
                {activeTab === 'relationships' ? (
                  <>
                    <span style={{
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.75rem',
                      fontWeight: '600',
                      textTransform: 'uppercase',
                      backgroundColor: selectedItemForActions.relationship_type === 'BILATERAL' ? '#d4edda' : '#fff3cd',
                      color: selectedItemForActions.relationship_type === 'BILATERAL' ? '#155724' : '#856404'
                    }}>
                      {selectedItemForActions.relationship_type}
                    </span>
                    <span style={{
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.75rem',
                      fontWeight: '600',
                      textTransform: 'uppercase',
                      backgroundColor: selectedItemForActions.status === 'active' ? '#d4edda' : selectedItemForActions.status === 'pending' ? '#fff3cd' : '#f8d7da',
                      color: selectedItemForActions.status === 'active' ? '#155724' : selectedItemForActions.status === 'pending' ? '#856404' : '#721c24'
                    }}>
                      {selectedItemForActions.status}
                    </span>
                  </>
                ) : (
                  <>
                    <span style={{
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.75rem',
                      fontWeight: '600',
                      textTransform: 'uppercase',
                      backgroundColor: selectedItemForActions.group_type === 'SECURITY' ? '#d4edda' : '#fff3cd',
                      color: selectedItemForActions.group_type === 'SECURITY' ? '#155724' : '#856404'
                    }}>
                      {selectedItemForActions.group_type}
                    </span>
                    <span style={{
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.75rem',
                      fontWeight: '600',
                      textTransform: 'uppercase',
                      backgroundColor: selectedItemForActions.is_public ? '#d4edda' : '#fff3cd',
                      color: selectedItemForActions.is_public ? '#155724' : '#856404'
                    }}>
                      {selectedItemForActions.is_public ? 'Public' : 'Private'}
                    </span>
                  </>
                )}
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
                  handleAction('view');
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
                  handleAction('edit');
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
                Edit Details
              </button>
              
              {activeTab === 'relationships' && selectedItemForActions.status !== 'active' && (
                <button
                  onClick={() => {
                    closeActionsPopup();
                    handleAction('activate');
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
                  Activate Relationship
                </button>
              )}
              
              {activeTab === 'relationships' && selectedItemForActions.status === 'active' && (
                <button
                  onClick={() => {
                    closeActionsPopup();
                    handleAction('suspend');
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
                    e.target.style.backgroundColor = '#5D8AA8';
                    e.target.style.color = 'white';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.backgroundColor = 'white';
                    e.target.style.color = '#5D8AA8';
                  }}
                >
                  Suspend Relationship
                </button>
              )}
              
              {activeTab === 'groups' && !isAdmin && (
                <button
                  onClick={() => {
                    closeActionsPopup();
                    handleAction('join');
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
                  Join Group
                </button>
              )}
              
              <button
                onClick={() => {
                  closeActionsPopup();
                  handleAction('delete');
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
                Delete {activeTab === 'relationships' ? 'Relationship' : 'Group'}
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
                  fontSize: '0.875rem',
                  width: '100%'
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Confirmation Modal */}
      {showConfirmation && (
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
      )}

      {/* Detail View Modal */}
      {showDetailModal && detailItem && (
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
            borderRadius: '12px',
            padding: '2rem',
            width: '90%',
            maxWidth: '600px',
            maxHeight: '90vh',
            overflowY: 'auto',
            boxShadow: '0 10px 25px rgba(0,0,0,0.1)'
          }}>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              marginBottom: '1.5rem'
            }}>
              <h2 style={{ margin: '0', color: '#333' }}>
                {activeTab === 'relationships' ? 'Trust Relationship Details' : 'Trust Group Details'}
              </h2>
              <button
                onClick={() => setShowDetailModal(false)}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '1.5rem',
                  cursor: 'pointer',
                  color: '#666'
                }}
              >
                ×
              </button>
            </div>
            
            {activeTab === 'relationships' ? (
              <div>
                <div style={{ marginBottom: '1.5rem' }}>
                  <h3 style={{ color: '#5D8AA8', marginBottom: '1rem' }}>Relationship Overview</h3>
                  <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: '1fr 1fr', 
                    gap: '1rem',
                    marginBottom: '1rem'
                  }}>
                    <div>
                      <strong>Source Organization:</strong><br/>
                      {detailItem.source_organization_name}
                    </div>
                    <div>
                      <strong>Target Organization:</strong><br/>
                      {detailItem.target_organization_name || detailItem.target_organization}
                    </div>
                    <div>
                      <strong>Trust Level:</strong><br/>
                      <span style={{
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                        fontSize: '0.875rem',
                        fontWeight: '600',
                        backgroundColor: detailItem.trust_level === 'HIGH' ? '#d4edda' : detailItem.trust_level === 'MEDIUM' ? '#fff3cd' : '#f8f9fa',
                        color: detailItem.trust_level === 'HIGH' ? '#155724' : detailItem.trust_level === 'MEDIUM' ? '#856404' : '#495057'
                      }}>
                        {detailItem.trust_level}
                      </span>
                    </div>
                    <div>
                      <strong>Status:</strong><br/>
                      <span style={{
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                        fontSize: '0.875rem',
                        fontWeight: '600',
                        backgroundColor: detailItem.status === 'active' ? '#d4edda' : detailItem.status === 'pending' ? '#fff3cd' : '#f8d7da',
                        color: detailItem.status === 'active' ? '#155724' : detailItem.status === 'pending' ? '#856404' : '#721c24'
                      }}>
                        {detailItem.status}
                      </span>
                    </div>
                    <div>
                      <strong>Relationship Type:</strong><br/>
                      {detailItem.relationship_type}
                    </div>
                    <div>
                      <strong>Created:</strong><br/>
                      {detailItem.created_at ? new Date(detailItem.created_at).toLocaleDateString() : 'N/A'}
                    </div>
                  </div>
                  
                  {detailItem.notes && (
                    <div style={{ marginTop: '1rem' }}>
                      <strong>Notes:</strong><br/>
                      <div style={{ 
                        padding: '0.75rem',
                        backgroundColor: '#f8f9fa',
                        borderRadius: '4px',
                        marginTop: '0.5rem',
                        fontStyle: 'italic'
                      }}>
                        {detailItem.notes}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div>
                <div style={{ marginBottom: '1.5rem' }}>
                  <h3 style={{ color: '#5D8AA8', marginBottom: '1rem' }}>Group Overview</h3>
                  <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: '1fr 1fr', 
                    gap: '1rem',
                    marginBottom: '1rem'
                  }}>
                    <div>
                      <strong>Group Name:</strong><br/>
                      {detailItem.name}
                    </div>
                    <div>
                      <strong>Group Type:</strong><br/>
                      <span style={{
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                        fontSize: '0.875rem',
                        fontWeight: '600',
                        backgroundColor: detailItem.group_type === 'SECURITY' ? '#d4edda' : '#fff3cd',
                        color: detailItem.group_type === 'SECURITY' ? '#155724' : '#856404'
                      }}>
                        {detailItem.group_type}
                      </span>
                    </div>
                    <div>
                      <strong>Visibility:</strong><br/>
                      <span style={{
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                        fontSize: '0.875rem',
                        fontWeight: '600',
                        backgroundColor: detailItem.is_public ? '#d4edda' : '#fff3cd',
                        color: detailItem.is_public ? '#155724' : '#856404'
                      }}>
                        {detailItem.is_public ? 'Public' : 'Private'}
                      </span>
                    </div>
                    <div>
                      <strong>Member Count:</strong><br/>
                      {detailItem.member_count || 0}
                    </div>
                    <div>
                      <strong>Requires Approval:</strong><br/>
                      {detailItem.requires_approval ? 'Yes' : 'No'}
                    </div>
                    <div>
                      <strong>Created:</strong><br/>
                      {detailItem.created_at ? new Date(detailItem.created_at).toLocaleDateString() : 'N/A'}
                    </div>
                  </div>
                  
                  <div style={{ marginTop: '1rem' }}>
                    <strong>Description:</strong><br/>
                    <div style={{ 
                      padding: '0.75rem',
                      backgroundColor: '#f8f9fa',
                      borderRadius: '4px',
                      marginTop: '0.5rem'
                    }}>
                      {detailItem.description || 'No description provided'}
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <div style={{ 
              display: 'flex', 
              justifyContent: 'flex-end',
              marginTop: '2rem',
              paddingTop: '1rem',
              borderTop: '1px solid #e9ecef'
            }}>
              <button
                onClick={() => setShowDetailModal(false)}
                style={{
                  padding: '0.5rem 1rem',
                  backgroundColor: '#6c757d',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer'
                }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default TrustManagement;