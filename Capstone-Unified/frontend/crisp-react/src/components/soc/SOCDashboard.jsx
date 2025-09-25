import React, { useState, useEffect } from 'react';
import * as api from '../../api.js';

const SOCDashboard = ({ active, showPage }) => {
  if (!active) return null;
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
    // Refresh every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/soc/dashboard/');
      if (response?.data) {
        setDashboardData(response.data);
        setError(null);
      }
    } catch (err) {
      setError('Failed to load SOC dashboard data');
      console.error('SOC Dashboard Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'critical': return '#dc3545';
      case 'high': return '#fd7e14';
      case 'medium': return '#ffc107';
      case 'low': return '#28a745';
      default: return '#6c757d';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'new': return '#007bff';
      case 'assigned': return '#17a2b8';
      case 'in_progress': return '#ffc107';
      case 'resolved': return '#28a745';
      case 'closed': return '#6c757d';
      default: return '#6c757d';
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <div className="spinner-border" role="status">
          <span className="sr-only">Loading SOC Dashboard...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '20px' }}>
        <div className="alert alert-danger" role="alert">
          <i className="fas fa-exclamation-triangle mr-2"></i>
          {error}
          <button 
            className="btn btn-outline-danger btn-sm ml-3"
            onClick={fetchDashboardData}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <p>No SOC data available</p>
      </div>
    );
  }

  const { metrics, breakdowns, recent_incidents } = dashboardData;

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>
          <i className="fas fa-shield-alt mr-2"></i>
          SOC Dashboard
        </h2>
        <div style={{ fontSize: '0.9em', color: '#6c757d' }}>
          <i className="fas fa-sync-alt mr-1"></i>
          Last updated: {new Date(dashboardData.last_updated).toLocaleTimeString()}
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="row mb-4">
        <div className="col-md-3 mb-3">
          <div className="card border-primary">
            <div className="card-body text-center">
              <div style={{ fontSize: '2rem', color: '#007bff', marginBottom: '10px' }}>
                <i className="fas fa-exclamation-circle"></i>
              </div>
              <h3 className="text-primary">{metrics.open_incidents}</h3>
              <p className="text-muted mb-0">Open Incidents</p>
            </div>
          </div>
        </div>
        
        <div className="col-md-3 mb-3">
          <div className="card border-danger">
            <div className="card-body text-center">
              <div style={{ fontSize: '2rem', color: '#dc3545', marginBottom: '10px' }}>
                <i className="fas fa-fire"></i>
              </div>
              <h3 className="text-danger">{metrics.critical_incidents}</h3>
              <p className="text-muted mb-0">Critical</p>
            </div>
          </div>
        </div>
        
        <div className="col-md-3 mb-3">
          <div className="card border-warning">
            <div className="card-body text-center">
              <div style={{ fontSize: '2rem', color: '#ffc107', marginBottom: '10px' }}>
                <i className="fas fa-clock"></i>
              </div>
              <h3 className="text-warning">{metrics.overdue_incidents}</h3>
              <p className="text-muted mb-0">Overdue</p>
            </div>
          </div>
        </div>
        
        <div className="col-md-3 mb-3">
          <div className="card border-success">
            <div className="card-body text-center">
              <div style={{ fontSize: '2rem', color: '#28a745', marginBottom: '10px' }}>
                <i className="fas fa-check-circle"></i>
              </div>
              <h3 className="text-success">{metrics.resolved_today}</h3>
              <p className="text-muted mb-0">Resolved Today</p>
            </div>
          </div>
        </div>
      </div>

      {/* Activity Metrics */}
      <div className="row mb-4">
        <div className="col-md-4 mb-3">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">
                <i className="fas fa-chart-line mr-2"></i>
                Activity Metrics
              </h5>
            </div>
            <div className="card-body">
              <div className="d-flex justify-content-between mb-2">
                <span>Today:</span>
                <strong>{metrics.incidents_today} created</strong>
              </div>
              <div className="d-flex justify-content-between mb-2">
                <span>This Week:</span>
                <strong>{metrics.incidents_week} created</strong>
              </div>
              <div className="d-flex justify-content-between mb-2">
                <span>This Month:</span>
                <strong>{metrics.incidents_month} created</strong>
              </div>
              <div className="d-flex justify-content-between">
                <span>Resolved This Week:</span>
                <strong>{metrics.resolved_week}</strong>
              </div>
            </div>
          </div>
        </div>

        {/* Status Breakdown */}
        <div className="col-md-4 mb-3">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">
                <i className="fas fa-pie-chart mr-2"></i>
                Status Breakdown
              </h5>
            </div>
            <div className="card-body">
              {Object.entries(breakdowns.status).map(([status, count]) => (
                <div key={status} className="d-flex justify-content-between mb-2">
                  <span>
                    <span 
                      className="mr-2" 
                      style={{ 
                        backgroundColor: getStatusColor(status), 
                        color: 'white',
                        padding: '4px 8px',
                        fontSize: '0.75rem',
                        fontWeight: 'bold',
                        textTransform: 'uppercase',
                        borderRadius: '2px',
                        display: 'inline-block'
                      }}
                    >
                      {status.replace('_', ' ')}
                    </span>
                  </span>
                  <strong>{count}</strong>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Priority Breakdown */}
        <div className="col-md-4 mb-3">
          <div className="card">
            <div className="card-header">
              <h5 className="mb-0">
                <i className="fas fa-exclamation-triangle mr-2"></i>
                Priority Breakdown
              </h5>
            </div>
            <div className="card-body">
              {Object.entries(breakdowns.priority).map(([priority, count]) => (
                <div key={priority} className="d-flex justify-content-between mb-2">
                  <span>
                    <span 
                      className="mr-2" 
                      style={{ 
                        backgroundColor: getPriorityColor(priority), 
                        color: 'white',
                        padding: '4px 8px',
                        fontSize: '0.75rem',
                        fontWeight: 'bold',
                        textTransform: 'uppercase',
                        borderRadius: '2px',
                        display: 'inline-block'
                      }}
                    >
                      {priority}
                    </span>
                  </span>
                  <strong>{count}</strong>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Recent Incidents */}
      <div className="card">
        <div className="card-header d-flex justify-content-between align-items-center">
          <h5 className="mb-0">
            <i className="fas fa-list mr-2"></i>
            Recent Incidents
          </h5>
          <button 
            className="btn btn-primary btn-sm"
            onClick={() => showPage('soc-incidents')}
          >
            View All
          </button>
        </div>
        <div className="card-body p-0">
          {recent_incidents.length === 0 ? (
            <div className="text-center p-4 text-muted">
              <i className="fas fa-info-circle mr-2"></i>
              No recent incidents
            </div>
          ) : (
            <div className="table-responsive">
              <table className="table table-hover mb-0">
                <thead className="thead-light">
                  <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Priority</th>
                    <th>Status</th>
                    <th>Created</th>
                    <th>SLA</th>
                  </tr>
                </thead>
                <tbody>
                  {recent_incidents.map((incident) => (
                    <tr 
                      key={incident.id}
                    >
                      <td>
                        <code>{incident.incident_id}</code>
                      </td>
                      <td>
                        <div style={{ maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {incident.title}
                        </div>
                      </td>
                      <td>
                        <span 
                          style={{ 
                            backgroundColor: getPriorityColor(incident.priority), 
                            color: 'white',
                            padding: '4px 8px',
                            fontSize: '0.75rem',
                            fontWeight: 'bold',
                            textTransform: 'uppercase',
                            borderRadius: '2px',
                            display: 'inline-block'
                          }}
                        >
                          {incident.priority}
                        </span>
                      </td>
                      <td>
                        <span 
                          style={{ 
                            backgroundColor: getStatusColor(incident.status), 
                            color: 'white',
                            padding: '4px 8px',
                            fontSize: '0.75rem',
                            fontWeight: 'bold',
                            textTransform: 'uppercase',
                            borderRadius: '2px',
                            display: 'inline-block'
                          }}
                        >
                          {incident.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td>
                        <small>{new Date(incident.created_at).toLocaleString()}</small>
                      </td>
                      <td>
                        {incident.is_overdue && (
                          <span className="badge badge-danger">
                            <i className="fas fa-exclamation-triangle mr-1"></i>
                            Overdue
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SOCDashboard;