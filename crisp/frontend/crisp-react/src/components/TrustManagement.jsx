import React, { useState, useEffect } from 'react';
import { 
  getTrustOverview, 
  getTrustRelationships, 
  createTrustRelationship, 
  updateTrustRelationship, 
  deleteTrustRelationship,
  getTrustGroups, 
  createTrustGroup, 
  getTrustMetrics,
  getOrganizations 
} from '../api.js';

const TrustManagement = ({ active }) => {
  const [trustRelationships, setTrustRelationships] = useState([]);
  const [trustGroups, setTrustGroups] = useState([]);
  const [trustMetrics, setTrustMetrics] = useState({});
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('relationships');
  const [showNewRelationshipModal, setShowNewRelationshipModal] = useState(false);
  const [showNewGroupModal, setShowNewGroupModal] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

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

  // Load all trust data
  const loadTrustData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [
        relationshipsResponse,
        groupsResponse,
        metricsResponse,
        orgsResponse
      ] = await Promise.all([
        getTrustRelationships(),
        getTrustGroups(),
        getTrustMetrics(),
        getOrganizations()
      ]);

      if (relationshipsResponse.success) {
        setTrustRelationships(relationshipsResponse.data || []);
      }
      
      if (groupsResponse.success) {
        setTrustGroups(groupsResponse.data || []);
      }
      
      if (metricsResponse.success) {
        setTrustMetrics(metricsResponse.data || {});
      }
      
      if (orgsResponse.success) {
        setOrganizations(orgsResponse.data || []);
      }
    } catch (err) {
      console.error('Error loading trust data:', err);
      setError('Failed to load trust data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Handle refresh
  const handleRefresh = async () => {
    setRefreshing(true);
    await loadTrustData();
    setRefreshing(false);
  };

  // Handle new relationship submission
  const handleCreateRelationship = async (e) => {
    e.preventDefault();
    try {
      const response = await createTrustRelationship(newRelationship);
      if (response.success) {
        setShowNewRelationshipModal(false);
        setNewRelationship({
          target_organization: '',
          trust_level: '',
          relationship_type: 'bilateral',
          notes: ''
        });
        await loadTrustData();
      } else {
        setError(response.message || 'Failed to create trust relationship');
      }
    } catch (err) {
      console.error('Error creating trust relationship:', err);
      setError('Failed to create trust relationship. Please try again.');
    }
  };

  // Handle new group submission
  const handleCreateGroup = async (e) => {
    e.preventDefault();
    try {
      const response = await createTrustGroup(newGroup);
      if (response.success) {
        setShowNewGroupModal(false);
        setNewGroup({
          name: '',
          description: '',
          trust_level: '',
          group_type: 'industry'
        });
        await loadTrustData();
      } else {
        setError(response.message || 'Failed to create trust group');
      }
    } catch (err) {
      console.error('Error creating trust group:', err);
      setError('Failed to create trust group. Please try again.');
    }
  };

  // Handle delete relationship
  const handleDeleteRelationship = async (relationshipId) => {
    if (window.confirm('Are you sure you want to delete this trust relationship?')) {
      try {
        const response = await deleteTrustRelationship(relationshipId);
        if (response.success) {
          await loadTrustData();
        } else {
          setError(response.message || 'Failed to delete trust relationship');
        }
      } catch (err) {
        console.error('Error deleting trust relationship:', err);
        setError('Failed to delete trust relationship. Please try again.');
      }
    }
  };

  // Load data when component becomes active
  useEffect(() => {
    if (active) {
      loadTrustData();
    }
  }, [active]);

  if (!active) return null;

  if (loading) {
    return (
      <div className="trust-management-container">
        <div className="loading-spinner">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading trust data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="trust-management-container">
      <div className="trust-management-header">
        <h1>
          <i className="fas fa-handshake"></i>
          Trust Management
        </h1>
        <p className="page-subtitle">
          Manage trust relationships, groups, and security partnerships
        </p>
        <button 
          className="btn btn-refresh" 
          onClick={handleRefresh}
          disabled={refreshing}
        >
          <i className={`fas fa-sync-alt ${refreshing ? 'fa-spin' : ''}`}></i>
          {refreshing ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          <i className="fas fa-exclamation-triangle"></i>
          {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      {/* Trust Metrics Overview */}
      <div className="trust-metrics-grid">
        <div className="metric-card">
          <div className="metric-icon">
            <i className="fas fa-handshake"></i>
          </div>
          <div className="metric-info">
            <h3>{trustMetrics.total_relationships || 0}</h3>
            <p>Total Relationships</p>
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-icon">
            <i className="fas fa-check-circle"></i>
          </div>
          <div className="metric-info">
            <h3>{trustMetrics.active_relationships || 0}</h3>
            <p>Active Relationships</p>
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-icon">
            <i className="fas fa-users"></i>
          </div>
          <div className="metric-info">
            <h3>{trustMetrics.total_groups || 0}</h3>
            <p>Trust Groups</p>
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-icon">
            <i className="fas fa-chart-line"></i>
          </div>
          <div className="metric-info">
            <h3>{trustMetrics.average_trust_score || 0}%</h3>
            <p>Average Trust Score</p>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button 
          className={`tab-button ${activeTab === 'relationships' ? 'active' : ''}`}
          onClick={() => setActiveTab('relationships')}
        >
          <i className="fas fa-handshake"></i>
          Trust Relationships
        </button>
        <button 
          className={`tab-button ${activeTab === 'groups' ? 'active' : ''}`}
          onClick={() => setActiveTab('groups')}
        >
          <i className="fas fa-users"></i>
          Trust Groups
        </button>
        <button 
          className={`tab-button ${activeTab === 'analytics' ? 'active' : ''}`}
          onClick={() => setActiveTab('analytics')}
        >
          <i className="fas fa-chart-bar"></i>
          Analytics
        </button>
      </div>

      {/* Trust Relationships Tab */}
      {activeTab === 'relationships' && (
        <div className="trust-relationships-section">
          <div className="section-header">
            <h2>Trust Relationships</h2>
            <button 
              className="btn btn-primary"
              onClick={() => setShowNewRelationshipModal(true)}
            >
              <i className="fas fa-plus"></i>
              New Relationship
            </button>
          </div>

          {trustRelationships.length === 0 ? (
            <div className="empty-state">
              <i className="fas fa-handshake"></i>
              <h3>No Trust Relationships</h3>
              <p>Create your first trust relationship to start sharing data securely</p>
              <button 
                className="btn btn-primary"
                onClick={() => setShowNewRelationshipModal(true)}
              >
                <i className="fas fa-plus"></i>
                Create Trust Relationship
              </button>
            </div>
          ) : (
            <div className="relationships-grid">
              {trustRelationships.map((relationship) => (
                <div key={relationship.id} className="relationship-card">
                  <div className="relationship-header">
                    <h3>{relationship.target_organization_name}</h3>
                    <div className="relationship-actions">
                      <button 
                        className="btn btn-sm btn-danger"
                        onClick={() => handleDeleteRelationship(relationship.id)}
                      >
                        <i className="fas fa-trash"></i>
                      </button>
                    </div>
                  </div>
                  <div className="relationship-details">
                    <div className="trust-level">
                      <span>Trust Level:</span>
                      <div className="trust-progress">
                        <div 
                          className="trust-fill" 
                          style={{ width: `${relationship.trust_score || 0}%` }}
                        ></div>
                        <span className="trust-percentage">{relationship.trust_score || 0}%</span>
                      </div>
                    </div>
                    <div className="relationship-meta">
                      <span className={`status ${relationship.status}`}>
                        {relationship.status}
                      </span>
                      <span className="relationship-type">
                        {relationship.relationship_type}
                      </span>
                    </div>
                    {relationship.notes && (
                      <div className="relationship-notes">
                        <p>{relationship.notes}</p>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Trust Groups Tab */}
      {activeTab === 'groups' && (
        <div className="trust-groups-section">
          <div className="section-header">
            <h2>Trust Groups</h2>
            <button 
              className="btn btn-primary"
              onClick={() => setShowNewGroupModal(true)}
            >
              <i className="fas fa-plus"></i>
              New Group
            </button>
          </div>

          {trustGroups.length === 0 ? (
            <div className="empty-state">
              <i className="fas fa-users"></i>
              <h3>No Trust Groups</h3>
              <p>Create trust groups to organize multiple organizations with shared trust levels</p>
              <button 
                className="btn btn-primary"
                onClick={() => setShowNewGroupModal(true)}
              >
                <i className="fas fa-plus"></i>
                Create Trust Group
              </button>
            </div>
          ) : (
            <div className="groups-grid">
              {trustGroups.map((group) => (
                <div key={group.id} className="group-card">
                  <div className="group-header">
                    <h3>{group.name}</h3>
                    <span className={`group-type ${group.group_type}`}>
                      {group.group_type}
                    </span>
                  </div>
                  <div className="group-details">
                    <p>{group.description}</p>
                    <div className="group-stats">
                      <span><i className="fas fa-users"></i> {group.member_count || 0} Members</span>
                      <span><i className="fas fa-shield-alt"></i> {group.trust_level}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Analytics Tab */}
      {activeTab === 'analytics' && (
        <div className="trust-analytics-section">
          <h2>Trust Analytics</h2>
          <div className="analytics-grid">
            <div className="analytics-card">
              <h3>Trust Score Distribution</h3>
              <div className="chart-placeholder">
                <i className="fas fa-chart-pie"></i>
                <p>Trust score distribution chart would be displayed here</p>
              </div>
            </div>
            <div className="analytics-card">
              <h3>Relationship Growth</h3>
              <div className="chart-placeholder">
                <i className="fas fa-chart-line"></i>
                <p>Relationship growth over time chart would be displayed here</p>
              </div>
            </div>
            <div className="analytics-card">
              <h3>Trust Network Map</h3>
              <div className="chart-placeholder">
                <i className="fas fa-project-diagram"></i>
                <p>Trust network visualization would be displayed here</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* New Relationship Modal */}
      {showNewRelationshipModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Create New Trust Relationship</h3>
              <button onClick={() => setShowNewRelationshipModal(false)}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <form onSubmit={handleCreateRelationship}>
              <div className="form-group">
                <label>Target Organization *</label>
                <select 
                  value={newRelationship.target_organization}
                  onChange={(e) => setNewRelationship({...newRelationship, target_organization: e.target.value})}
                  required
                >
                  <option value="">Select Organization</option>
                  {organizations.map(org => (
                    <option key={org.id} value={org.id}>{org.name}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Trust Level *</label>
                <select 
                  value={newRelationship.trust_level}
                  onChange={(e) => setNewRelationship({...newRelationship, trust_level: e.target.value})}
                  required
                >
                  <option value="">Select Trust Level</option>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
              <div className="form-group">
                <label>Relationship Type</label>
                <select 
                  value={newRelationship.relationship_type}
                  onChange={(e) => setNewRelationship({...newRelationship, relationship_type: e.target.value})}
                >
                  <option value="bilateral">Bilateral</option>
                  <option value="hierarchical">Hierarchical</option>
                  <option value="community">Community</option>
                </select>
              </div>
              <div className="form-group">
                <label>Notes</label>
                <textarea 
                  value={newRelationship.notes}
                  onChange={(e) => setNewRelationship({...newRelationship, notes: e.target.value})}
                  placeholder="Optional notes about this relationship"
                />
              </div>
              <div className="modal-actions">
                <button type="button" onClick={() => setShowNewRelationshipModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Create Relationship
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* New Group Modal */}
      {showNewGroupModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Create New Trust Group</h3>
              <button onClick={() => setShowNewGroupModal(false)}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <form onSubmit={handleCreateGroup}>
              <div className="form-group">
                <label>Group Name *</label>
                <input 
                  type="text"
                  value={newGroup.name}
                  onChange={(e) => setNewGroup({...newGroup, name: e.target.value})}
                  placeholder="Enter group name"
                  required
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea 
                  value={newGroup.description}
                  onChange={(e) => setNewGroup({...newGroup, description: e.target.value})}
                  placeholder="Describe the purpose of this trust group"
                />
              </div>
              <div className="form-group">
                <label>Trust Level *</label>
                <select 
                  value={newGroup.trust_level}
                  onChange={(e) => setNewGroup({...newGroup, trust_level: e.target.value})}
                  required
                >
                  <option value="">Select Trust Level</option>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
              <div className="form-group">
                <label>Group Type</label>
                <select 
                  value={newGroup.group_type}
                  onChange={(e) => setNewGroup({...newGroup, group_type: e.target.value})}
                >
                  <option value="industry">Industry</option>
                  <option value="regional">Regional</option>
                  <option value="strategic">Strategic</option>
                </select>
              </div>
              <div className="modal-actions">
                <button type="button" onClick={() => setShowNewGroupModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Create Group
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default TrustManagement;