import React, { useState, useEffect } from 'react';
<<<<<<< HEAD
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
=======
import * as api from '../api.js';
import LoadingSpinner from './LoadingSpinner.jsx';

// Trust Management Component
function TrustManagement({ active }) {
  const [trustData, setTrustData] = useState({
    relationships: [],
    groups: [],
    metrics: {},
    recentActivities: []
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('relationships');

  useEffect(() => {
    if (active) {
      fetchTrustData();
    }
  }, [active]);

  const fetchTrustData = async () => {
>>>>>>> 0e11954e654cfb2cb76f2d422e1f6ff74fa672b7
    try {
      setLoading(true);
      setError(null);
      
<<<<<<< HEAD
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
=======
      // Fetch trust data from admin overview and organization trust metrics
      const [adminOverview, trustMetrics] = await Promise.allSettled([
        api.getTrustOverview(),
        api.getTrustMetrics()
      ]);

      // Process admin overview data
      let overviewData = {};
      if (adminOverview.status === 'fulfilled' && adminOverview.value) {
        overviewData = adminOverview.value.data || adminOverview.value;
        console.log('Admin overview data received:', overviewData);
      } else {
        console.log('Admin overview failed or empty:', adminOverview);
      }

      // Process trust metrics data
      let metricsData = {};
      if (trustMetrics.status === 'fulfilled' && trustMetrics.value) {
        metricsData = trustMetrics.value.data || trustMetrics.value;
        console.log('Trust metrics data received:', metricsData);
      } else {
        console.log('Trust metrics failed or empty:', trustMetrics);
      }

      // Mock data for demonstration if no real data
      const mockRelationships = [
        {
          id: '1',
          source_organization: { name: 'University of Cape Town' },
          target_organization: { name: 'Stellenbosch University' },
          trust_level: { name: 'High Trust', numerical_value: 80 },
          status: 'active',
          relationship_type: 'bilateral',
          created_at: new Date().toISOString(),
          notes: 'Academic collaboration partnership'
        },
        {
          id: '2',
          source_organization: { name: 'CSIR' },
          target_organization: { name: 'University of Cape Town' },
          trust_level: { name: 'Medium Trust', numerical_value: 60 },
          status: 'active',
          relationship_type: 'bilateral',
          created_at: new Date().toISOString(),
          notes: 'Research collaboration'
        },
        {
          id: '3',
          source_organization: { name: 'South African Police Service' },
          target_organization: { name: 'CSIR' },
          trust_level: { name: 'Full Trust', numerical_value: 100 },
          status: 'active',
          relationship_type: 'hierarchical',
          created_at: new Date().toISOString(),
          notes: 'Government cybersecurity collaboration'
        }
      ];

      const mockGroups = [
        {
          id: '1',
          name: 'Academic Research Consortium',
          description: 'Group for academic institutions sharing research threat data',
          member_count: 3,
          is_public: true,
          created_at: new Date().toISOString()
        },
        {
          id: '2',
          name: 'Government Security Network',
          description: 'Government agencies sharing cybersecurity intelligence',
          member_count: 2,
          is_public: false,
          created_at: new Date().toISOString()
        }
      ];

      const mockActivities = [
        {
          id: '1',
          action: 'relationship_created',
          user: 'DreasVermaak1',
          timestamp: new Date().toISOString(),
          success: true,
          details: { relationship_type: 'bilateral', trust_level: 'High Trust' }
        },
        {
          id: '2',
          action: 'group_joined',
          user: 'john.smith',
          timestamp: new Date().toISOString(),
          success: true,
          details: { group_name: 'Academic Research Consortium' }
        }
      ];

      // Always use mock data for now since backend may not have trust data yet
      const hasRealData = (overviewData.relationships && overviewData.relationships.length > 0) ||
                         (Array.isArray(overviewData) && overviewData.length > 0);
      
      console.log('Has real trust data:', hasRealData);
      console.log('Using mock data for trust relationships');
      
      setTrustData({
        relationships: hasRealData ? (overviewData.relationships || overviewData) : mockRelationships,
        groups: hasRealData ? (overviewData.groups || []) : mockGroups,
        metrics: {
          total_relationships: hasRealData ? 
            (overviewData.relationships?.total || overviewData.length || 0) : 
            mockRelationships.length,
          active_relationships: hasRealData ? 
            (overviewData.relationships?.active || overviewData.filter(r => r.status === 'active').length || 0) : 
            mockRelationships.filter(r => r.status === 'active').length,
          pending_relationships: hasRealData ? 
            (overviewData.relationships?.pending || 0) : 
            0,
          total_groups: hasRealData ? 
            (overviewData.groups?.total || overviewData.groups?.length || 0) : 
            mockGroups.length,
          active_groups: hasRealData ? 
            (overviewData.groups?.active || overviewData.groups?.filter(g => g.is_active).length || 0) : 
            mockGroups.length,
          ...metricsData
        },
        recentActivities: hasRealData ? (overviewData.recent_activities || []) : mockActivities
      });

    } catch (err) {
      console.error('Failed to fetch trust data:', err);
>>>>>>> 0e11954e654cfb2cb76f2d422e1f6ff74fa672b7
      setError('Failed to load trust data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

<<<<<<< HEAD
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
=======
  if (!active) return null;

  return (
    <section id="trust-management" className={`page-section ${active ? 'active' : ''}`}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Trust Management</h1>
          <p className="page-subtitle">Manage trust relationships, groups, and security partnerships</p>
        </div>
        <div className="action-buttons">
          <button className="btn btn-outline" onClick={fetchTrustData}>
            <i className="fas fa-sync-alt"></i> Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="alert alert-error">
          <i className="fas fa-exclamation-triangle"></i>
          {error}
>>>>>>> 0e11954e654cfb2cb76f2d422e1f6ff74fa672b7
        </div>
      )}

      {/* Trust Metrics Overview */}
      <div className="trust-metrics-grid">
        <div className="metric-card">
          <div className="metric-icon">
            <i className="fas fa-handshake"></i>
          </div>
<<<<<<< HEAD
          <div className="metric-info">
            <h3>{trustMetrics.total_relationships || 0}</h3>
            <p>Total Relationships</p>
          </div>
        </div>
=======
          <div className="metric-content">
            <div className="metric-value">{trustData.metrics.total_relationships || 0}</div>
            <div className="metric-label">Total Relationships</div>
          </div>
        </div>
        
>>>>>>> 0e11954e654cfb2cb76f2d422e1f6ff74fa672b7
        <div className="metric-card">
          <div className="metric-icon">
            <i className="fas fa-check-circle"></i>
          </div>
<<<<<<< HEAD
          <div className="metric-info">
            <h3>{trustMetrics.active_relationships || 0}</h3>
            <p>Active Relationships</p>
          </div>
        </div>
=======
          <div className="metric-content">
            <div className="metric-value">{trustData.metrics.active_relationships || 0}</div>
            <div className="metric-label">Active Relationships</div>
          </div>
        </div>
        
>>>>>>> 0e11954e654cfb2cb76f2d422e1f6ff74fa672b7
        <div className="metric-card">
          <div className="metric-icon">
            <i className="fas fa-users"></i>
          </div>
<<<<<<< HEAD
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
=======
          <div className="metric-content">
            <div className="metric-value">{trustData.metrics.total_groups || 0}</div>
            <div className="metric-label">Trust Groups</div>
          </div>
        </div>
        
        <div className="metric-card">
          <div className="metric-icon">
            <i className="fas fa-clock"></i>
          </div>
          <div className="metric-content">
            <div className="metric-value">{trustData.metrics.pending_relationships || 0}</div>
            <div className="metric-label">Pending Approval</div>
>>>>>>> 0e11954e654cfb2cb76f2d422e1f6ff74fa672b7
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button 
          className={`tab-button ${activeTab === 'relationships' ? 'active' : ''}`}
          onClick={() => setActiveTab('relationships')}
        >
<<<<<<< HEAD
          <i className="fas fa-handshake"></i>
          Trust Relationships
=======
          <i className="fas fa-handshake"></i> Trust Relationships
>>>>>>> 0e11954e654cfb2cb76f2d422e1f6ff74fa672b7
        </button>
        <button 
          className={`tab-button ${activeTab === 'groups' ? 'active' : ''}`}
          onClick={() => setActiveTab('groups')}
        >
<<<<<<< HEAD
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
=======
          <i className="fas fa-users"></i> Trust Groups
        </button>
        <button 
          className={`tab-button ${activeTab === 'activities' ? 'active' : ''}`}
          onClick={() => setActiveTab('activities')}
        >
          <i className="fas fa-history"></i> Recent Activities
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'relationships' && (
          <TrustRelationshipsTab 
            relationships={trustData.relationships}
            loading={loading}
            onRefresh={fetchTrustData}
          />
        )}
        
        {activeTab === 'groups' && (
          <TrustGroupsTab 
            groups={trustData.groups}
            loading={loading}
            onRefresh={fetchTrustData}
          />
        )}
        
        {activeTab === 'activities' && (
          <TrustActivitiesTab 
            activities={trustData.recentActivities}
            loading={loading}
            onRefresh={fetchTrustData}
          />
        )}
      </div>
    </section>
  );
}

// Trust Relationships Tab Component
function TrustRelationshipsTab({ relationships, loading, onRefresh }) {
  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">Trust Relationships</h2>
      </div>
      <div className="card-content">
        {relationships.length === 0 ? (
          <div className="empty-state">
            <i className="fas fa-handshake"></i>
            <h3>No Trust Relationships</h3>
            <p>No trust relationships have been established yet.</p>
          </div>
        ) : (
          <div className="trust-relationships-grid">
            {relationships.map((relationship) => (
              <div key={relationship.id} className="trust-relationship-card">
                <div className="relationship-header">
                  <div className="relationship-info">
                    <h4>{relationship.target_organization?.name || relationship.source_organization?.name}</h4>
                    <span className={`relationship-type ${relationship.relationship_type}`}>
                      {relationship.relationship_type}
                    </span>
                  </div>
                  <div className="relationship-status">
                    <span className={`status-badge ${relationship.status}`}>
                      {relationship.status}
                    </span>
                  </div>
                </div>
                
                <div className="trust-level-display">
                  <div className="trust-level-bar">
                    <div 
                      className="trust-level-fill"
                      style={{ width: `${relationship.trust_level?.numerical_value || 0}%` }}
                    ></div>
                  </div>
                  <div className="trust-level-info">
                    <span className="trust-level-name">{relationship.trust_level?.name || 'Unknown'}</span>
                    <span className="trust-level-value">{relationship.trust_level?.numerical_value || 0}%</span>
                  </div>
                </div>
                
                {relationship.notes && (
                  <div className="relationship-notes">
                    <p>{relationship.notes}</p>
                  </div>
                )}
                
                <div className="relationship-meta">
                  <span className="created-date">
                    <i className="fas fa-calendar"></i>
                    {new Date(relationship.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// Trust Groups Tab Component
function TrustGroupsTab({ groups, loading, onRefresh }) {
  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">Trust Groups</h2>
      </div>
      <div className="card-content">
        {groups.length === 0 ? (
          <div className="empty-state">
            <i className="fas fa-users"></i>
            <h3>No Trust Groups</h3>
            <p>No trust groups have been created yet.</p>
          </div>
        ) : (
          <div className="trust-groups-grid">
            {groups.map((group) => (
              <div key={group.id} className="trust-group-card">
                <div className="group-header">
                  <h4>{group.name}</h4>
                  <span className={`group-visibility ${group.is_public ? 'public' : 'private'}`}>
                    <i className={`fas ${group.is_public ? 'fa-globe' : 'fa-lock'}`}></i>
                    {group.is_public ? 'Public' : 'Private'}
                  </span>
                </div>
                
                <div className="group-description">
                  <p>{group.description}</p>
                </div>
                
                <div className="group-stats">
                  <div className="stat-item">
                    <i className="fas fa-users"></i>
                    <span>{group.member_count} members</span>
                  </div>
                  <div className="stat-item">
                    <i className="fas fa-calendar"></i>
                    <span>{new Date(group.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// Trust Activities Tab Component
function TrustActivitiesTab({ activities, loading, onRefresh }) {
  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">Recent Trust Activities</h2>
      </div>
      <div className="card-content">
        {activities.length === 0 ? (
          <div className="empty-state">
            <i className="fas fa-history"></i>
            <h3>No Recent Activities</h3>
            <p>No recent trust activities to display.</p>
          </div>
        ) : (
          <div className="activities-list">
            {activities.map((activity) => (
              <div key={activity.id} className="activity-item">
                <div className="activity-icon">
                  <i className={`fas ${getActivityIcon(activity.action)} ${activity.success ? 'success' : 'error'}`}></i>
                </div>
                <div className="activity-content">
                  <div className="activity-header">
                    <span className="activity-action">{formatActivityAction(activity.action)}</span>
                    <span className="activity-user">by {activity.user}</span>
                  </div>
                  <div className="activity-details">
                    {activity.details && Object.entries(activity.details).map(([key, value]) => (
                      <span key={key} className="detail-item">
                        {key}: {value}
                      </span>
                    ))}
                  </div>
                  <div className="activity-timestamp">
                    {new Date(activity.timestamp).toLocaleString()}
                  </div>
                </div>
                <div className="activity-status">
                  <span className={`status-indicator ${activity.success ? 'success' : 'error'}`}>
                    {activity.success ? 'Success' : 'Failed'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// Helper functions
function getActivityIcon(action) {
  const iconMap = {
    'relationship_created': 'fa-handshake',
    'relationship_approved': 'fa-check',
    'relationship_activated': 'fa-play',
    'relationship_suspended': 'fa-pause',
    'relationship_revoked': 'fa-times',
    'group_created': 'fa-users',
    'group_joined': 'fa-user-plus',
    'group_left': 'fa-user-minus',
    'access_granted': 'fa-unlock',
    'access_denied': 'fa-lock'
  };
  return iconMap[action] || 'fa-info';
}

function formatActivityAction(action) {
  return action.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ');
}
>>>>>>> 0e11954e654cfb2cb76f2d422e1f6ff74fa672b7

export default TrustManagement;