import React, { useState, useEffect } from 'react';
import * as api from '../api.js';
import LoadingSpinner from './LoadingSpinner.jsx';

// Trust Management Component
function TrustManagement({ active, initialTab = null }) {
  console.log('TrustManagement rendered with props:', { active, initialTab });
  const [trustData, setTrustData] = useState({
    relationships: [],
    groups: [],
    metrics: {},
    organizations: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState(() => {
    // Use initialTab prop first, then URL params, then default
    if (initialTab && ['relationships', 'groups', 'metrics'].includes(initialTab)) {
      return initialTab;
    }
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('tab') || 'relationships';
  });
  const [showNewRelationshipModal, setShowNewRelationshipModal] = useState(false);
  const [showNewGroupModal, setShowNewGroupModal] = useState(false);

  // New relationship form state
  const [newRelationship, setNewRelationship] = useState({
    target_organization: '',
    trust_level: '',
    relationship_type: 'bilateral',
    notes: ''
  });

  // New group form state
  const [newGroup, setNewGroup] = useState({
    name: '',
    description: '',
    trust_level: '',
    group_type: 'industry'
  });

  // Load trust data when component becomes active
  useEffect(() => {
    if (active) {
      fetchTrustData();
    }
  }, [active]);

  // Update tab when initialTab prop changes
  useEffect(() => {
    if (initialTab && ['relationships', 'groups', 'metrics'].includes(initialTab) && initialTab !== activeTab) {
      console.log('TrustManagement: Setting tab from prop:', initialTab);
      setActiveTab(initialTab);
    }
  }, [initialTab, activeTab]);

  // Listen for URL changes to update active tab
  useEffect(() => {
    const handleUrlChange = () => {
      const urlParams = new URLSearchParams(window.location.search);
      const tabFromUrl = urlParams.get('tab');
      if (tabFromUrl && ['relationships', 'groups', 'metrics'].includes(tabFromUrl)) {
        setActiveTab(tabFromUrl);
      }
    };

    // Check URL immediately when component mounts or becomes active
    if (active) {
      handleUrlChange();
    }

    // Listen for popstate events (back/forward navigation)
    window.addEventListener('popstate', handleUrlChange);
    
    return () => {
      window.removeEventListener('popstate', handleUrlChange);
    };
  }, [active]);

  // Function to handle tab switching with URL update
  const handleTabChange = (tabName) => {
    try {
      console.log('TrustManagement: Changing tab to:', tabName);
      if (!['relationships', 'groups', 'metrics'].includes(tabName)) {
        console.error('Invalid tab name:', tabName);
        return;
      }
      
      setActiveTab(tabName);
      
      // Update URL to reflect tab change
      const urlParams = new URLSearchParams(window.location.search);
      urlParams.set('tab', tabName);
      const newUrl = `${window.location.pathname}?${urlParams.toString()}`;
      window.history.pushState(null, '', newUrl);
      console.log('TrustManagement: Updated URL to:', newUrl);
    } catch (error) {
      console.error('TrustManagement: Error changing tab:', error);
    }
  };

  const fetchTrustData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [
        relationshipsResponse,
        groupsResponse,
        metricsResponse,
        orgsResponse
      ] = await Promise.all([
        api.getTrustRelationships().catch(err => ({ data: [] })),
        api.getTrustGroups().catch(err => ({ data: [] })),
        api.getTrustMetrics().catch(err => ({ data: {} })),
        api.getOrganizations().catch(err => ({ data: [] }))
      ]);

      setTrustData({
        relationships: Array.isArray(relationshipsResponse.data) ? relationshipsResponse.data : 
                      Array.isArray(relationshipsResponse) ? relationshipsResponse : [],
        groups: Array.isArray(groupsResponse.data) ? groupsResponse.data : 
                Array.isArray(groupsResponse) ? groupsResponse : [],
        metrics: (metricsResponse.data && typeof metricsResponse.data === 'object') ? metricsResponse.data : 
                (metricsResponse && typeof metricsResponse === 'object') ? metricsResponse : {},
        organizations: Array.isArray(orgsResponse.data) ? orgsResponse.data : 
                      Array.isArray(orgsResponse) ? orgsResponse : []
      });
    } catch (err) {
      console.error('Error fetching trust data:', err);
      setError('Failed to load trust data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRelationship = async () => {
    try {
      await api.createTrustRelationship(newRelationship);
      setShowNewRelationshipModal(false);
      setNewRelationship({
        target_organization: '',
        trust_level: '',
        relationship_type: 'bilateral',
        notes: ''
      });
      fetchTrustData(); // Refresh data
    } catch (err) {
      console.error('Error creating trust relationship:', err);
      setError('Failed to create trust relationship');
    }
  };

  const handleCreateGroup = async () => {
    try {
      await api.createTrustGroup(newGroup);
      setShowNewGroupModal(false);
      setNewGroup({
        name: '',
        description: '',
        trust_level: '',
        group_type: 'industry'
      });
      fetchTrustData(); // Refresh data
    } catch (err) {
      console.error('Error creating trust group:', err);
      setError('Failed to create trust group');
    }
  };

  const handleUpdateRelationship = async (id, updateData) => {
    try {
      await api.updateTrustRelationship(id, updateData);
      fetchTrustData(); // Refresh data
    } catch (err) {
      console.error('Error updating trust relationship:', err);
      setError('Failed to update trust relationship');
    }
  };

  const handleDeleteRelationship = async (id) => {
    try {
      await api.deleteTrustRelationship(id);
      fetchTrustData(); // Refresh data
    } catch (err) {
      console.error('Error deleting trust relationship:', err);
      setError('Failed to delete trust relationship');
    }
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
    <div className="trust-management">
      <div className="trust-management-header">
        <h2>Trust Management</h2>
        <button 
          className="btn btn-primary"
          onClick={() => fetchTrustData()}
        >
          Refresh
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      <div className="trust-tabs">
        <button 
          className={`tab ${activeTab === 'relationships' ? 'active' : ''}`}
          onClick={() => handleTabChange('relationships')}
        >
          Trust Relationships ({Array.isArray(trustData.relationships) ? trustData.relationships.length : 0})
        </button>
        <button 
          className={`tab ${activeTab === 'groups' ? 'active' : ''}`}
          onClick={() => handleTabChange('groups')}
        >
          Trust Groups ({Array.isArray(trustData.groups) ? trustData.groups.length : 0})
        </button>
        <button 
          className={`tab ${activeTab === 'metrics' ? 'active' : ''}`}
          onClick={() => handleTabChange('metrics')}
        >
          Trust Metrics
        </button>
      </div>

      {activeTab === 'relationships' && (
        <div className="trust-relationships">
          <div className="section-header">
            <h3>Trust Relationships</h3>
            <button 
              className="btn btn-primary"
              onClick={() => setShowNewRelationshipModal(true)}
            >
              Create New Relationship
            </button>
          </div>

          <div className="relationships-grid">
            {!Array.isArray(trustData.relationships) || trustData.relationships.length === 0 ? (
              <div className="no-data">
                <p>No trust relationships found.</p>
                <p>Create your first trust relationship to start collaborating with other organizations.</p>
              </div>
            ) : (
              trustData.relationships.map(relationship => (
                <div key={relationship.id} className="relationship-card">
                  <div className="relationship-header">
                    <h4>{relationship.target_organization_name || relationship.target_organization}</h4>
                    <span className={`trust-level ${relationship.trust_level}`}>
                      {relationship.trust_level}
                    </span>
                  </div>
                  <div className="relationship-details">
                    <p><strong>Type:</strong> {relationship.relationship_type}</p>
                    <p><strong>Status:</strong> {relationship.status}</p>
                    <p><strong>Created:</strong> {new Date(relationship.created_at).toLocaleDateString()}</p>
                    {relationship.notes && (
                      <p><strong>Notes:</strong> {relationship.notes}</p>
                    )}
                  </div>
                  <div className="relationship-actions">
                    <button 
                      className="btn btn-sm btn-secondary"
                      onClick={() => handleUpdateRelationship(relationship.id, { status: 'active' })}
                    >
                      Update
                    </button>
                    <button 
                      className="btn btn-sm btn-danger"
                      onClick={() => handleDeleteRelationship(relationship.id)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {activeTab === 'groups' && (
        <div className="trust-groups">
          <div className="section-header">
            <h3>Trust Groups</h3>
            <button 
              className="btn btn-primary"
              onClick={() => setShowNewGroupModal(true)}
            >
              Create New Group
            </button>
          </div>

          <div className="groups-grid">
            {!Array.isArray(trustData.groups) || trustData.groups.length === 0 ? (
              <div className="no-data">
                <p>No trust groups found.</p>
                <p>Create or join trust groups to collaborate with multiple organizations.</p>
              </div>
            ) : (
              trustData.groups.map(group => (
                <div key={group.id} className="group-card">
                  <div className="group-header">
                    <h4>{group.name}</h4>
                    <span className={`trust-level ${group.default_trust_level}`}>
                      {group.default_trust_level}
                    </span>
                  </div>
                  <div className="group-details">
                    <p><strong>Type:</strong> {group.group_type}</p>
                    <p><strong>Members:</strong> {group.member_count || 0}</p>
                    <p><strong>Public:</strong> {group.is_public ? 'Yes' : 'No'}</p>
                    <p><strong>Description:</strong> {group.description}</p>
                  </div>
                  <div className="group-actions">
                    <button className="btn btn-sm btn-secondary">
                      View Details
                    </button>
                    <button className="btn btn-sm btn-primary">
                      Join Group
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {activeTab === 'metrics' && (
        <div className="trust-metrics">
          <h3>Trust Metrics</h3>
          <div className="metrics-grid">
            <div className="metric-card">
              <h4>Total Relationships</h4>
              <div className="metric-value">{Array.isArray(trustData.relationships) ? trustData.relationships.length : 0}</div>
            </div>
            <div className="metric-card">
              <h4>Active Groups</h4>
              <div className="metric-value">{Array.isArray(trustData.groups) ? trustData.groups.length : 0}</div>
            </div>
            <div className="metric-card">
              <h4>Trust Score</h4>
              <div className="metric-value">{trustData.metrics.trust_score || 'N/A'}</div>
            </div>
            <div className="metric-card">
              <h4>Connected Organizations</h4>
              <div className="metric-value">{trustData.metrics.connected_orgs || 0}</div>
            </div>
          </div>
        </div>
      )}

      {/* New Relationship Modal */}
      {showNewRelationshipModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>Create New Trust Relationship</h3>
              <button 
                className="close-btn"
                onClick={() => setShowNewRelationshipModal(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Target Organization:</label>
                <select 
                  value={newRelationship.target_organization}
                  onChange={(e) => setNewRelationship({...newRelationship, target_organization: e.target.value})}
                >
                  <option value="">Select Organization</option>
                  {Array.isArray(trustData.organizations) ? trustData.organizations.map(org => (
                    <option key={org.id} value={org.id}>{org.name}</option>
                  )) : null}
                </select>
              </div>
              <div className="form-group">
                <label>Trust Level:</label>
                <select 
                  value={newRelationship.trust_level}
                  onChange={(e) => setNewRelationship({...newRelationship, trust_level: e.target.value})}
                >
                  <option value="">Select Trust Level</option>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>
              <div className="form-group">
                <label>Relationship Type:</label>
                <select 
                  value={newRelationship.relationship_type}
                  onChange={(e) => setNewRelationship({...newRelationship, relationship_type: e.target.value})}
                >
                  <option value="bilateral">Bilateral</option>
                  <option value="unilateral">Unilateral</option>
                </select>
              </div>
              <div className="form-group">
                <label>Notes:</label>
                <textarea 
                  value={newRelationship.notes}
                  onChange={(e) => setNewRelationship({...newRelationship, notes: e.target.value})}
                  placeholder="Optional notes about this relationship..."
                />
              </div>
            </div>
            <div className="modal-footer">
              <button 
                className="btn btn-secondary"
                onClick={() => setShowNewRelationshipModal(false)}
              >
                Cancel
              </button>
              <button 
                className="btn btn-primary"
                onClick={handleCreateRelationship}
              >
                Create Relationship
              </button>
            </div>
          </div>
        </div>
      )}

      {/* New Group Modal */}
      {showNewGroupModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>Create New Trust Group</h3>
              <button 
                className="close-btn"
                onClick={() => setShowNewGroupModal(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Group Name:</label>
                <input 
                  type="text"
                  value={newGroup.name}
                  onChange={(e) => setNewGroup({...newGroup, name: e.target.value})}
                  placeholder="Enter group name..."
                />
              </div>
              <div className="form-group">
                <label>Description:</label>
                <textarea 
                  value={newGroup.description}
                  onChange={(e) => setNewGroup({...newGroup, description: e.target.value})}
                  placeholder="Describe the purpose of this group..."
                />
              </div>
              <div className="form-group">
                <label>Trust Level:</label>
                <select 
                  value={newGroup.trust_level}
                  onChange={(e) => setNewGroup({...newGroup, trust_level: e.target.value})}
                >
                  <option value="">Select Trust Level</option>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>
              <div className="form-group">
                <label>Group Type:</label>
                <select 
                  value={newGroup.group_type}
                  onChange={(e) => setNewGroup({...newGroup, group_type: e.target.value})}
                >
                  <option value="industry">Industry</option>
                  <option value="regional">Regional</option>
                  <option value="security">Security</option>
                  <option value="research">Research</option>
                </select>
              </div>
            </div>
            <div className="modal-footer">
              <button 
                className="btn btn-secondary"
                onClick={() => setShowNewGroupModal(false)}
              >
                Cancel
              </button>
              <button 
                className="btn btn-primary"
                onClick={handleCreateGroup}
              >
                Create Group
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default TrustManagement;