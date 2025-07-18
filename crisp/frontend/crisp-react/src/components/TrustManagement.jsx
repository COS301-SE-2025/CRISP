import React, { useState, useEffect } from 'react';
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
    try {
      setLoading(true);
      setError(null);
      
      // Fetch trust data from admin overview and organization trust metrics
      const [adminOverview, trustMetrics] = await Promise.allSettled([
        api.getTrustOverview(),
        api.getTrustMetrics()
      ]);

      // Process admin overview data
      let overviewData = {};
      if (adminOverview.status === 'fulfilled' && adminOverview.value) {
        overviewData = adminOverview.value.data || adminOverview.value;
      }

      // Process trust metrics data
      let metricsData = {};
      if (trustMetrics.status === 'fulfilled' && trustMetrics.value) {
        metricsData = trustMetrics.value.data || trustMetrics.value;
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

      setTrustData({
        relationships: overviewData.relationships || mockRelationships,
        groups: overviewData.groups || mockGroups,
        metrics: {
          total_relationships: overviewData.relationships?.total || mockRelationships.length,
          active_relationships: overviewData.relationships?.active || mockRelationships.filter(r => r.status === 'active').length,
          pending_relationships: overviewData.relationships?.pending || 0,
          total_groups: overviewData.groups?.total || mockGroups.length,
          active_groups: overviewData.groups?.active || mockGroups.length,
          ...metricsData
        },
        recentActivities: overviewData.recent_activities || mockActivities
      });

    } catch (err) {
      console.error('Failed to fetch trust data:', err);
      setError('Failed to load trust data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

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
        </div>
      )}

      {/* Trust Metrics Overview */}
      <div className="trust-metrics-grid">
        <div className="metric-card">
          <div className="metric-icon">
            <i className="fas fa-handshake"></i>
          </div>
          <div className="metric-content">
            <div className="metric-value">{trustData.metrics.total_relationships || 0}</div>
            <div className="metric-label">Total Relationships</div>
          </div>
        </div>
        
        <div className="metric-card">
          <div className="metric-icon">
            <i className="fas fa-check-circle"></i>
          </div>
          <div className="metric-content">
            <div className="metric-value">{trustData.metrics.active_relationships || 0}</div>
            <div className="metric-label">Active Relationships</div>
          </div>
        </div>
        
        <div className="metric-card">
          <div className="metric-icon">
            <i className="fas fa-users"></i>
          </div>
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
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button 
          className={`tab-button ${activeTab === 'relationships' ? 'active' : ''}`}
          onClick={() => setActiveTab('relationships')}
        >
          <i className="fas fa-handshake"></i> Trust Relationships
        </button>
        <button 
          className={`tab-button ${activeTab === 'groups' ? 'active' : ''}`}
          onClick={() => setActiveTab('groups')}
        >
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

export default TrustManagement;