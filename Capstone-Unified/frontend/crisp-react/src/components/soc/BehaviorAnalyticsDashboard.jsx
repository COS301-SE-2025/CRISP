import React, { useState, useEffect } from 'react';
import * as api from '../../api.js';
import { useNotifications } from '../enhanced/NotificationManager.jsx';

const BehaviorAnalyticsDashboard = ({ active }) => {
  const { showError, showSuccess } = useNotifications();
  const [dashboardData, setDashboardData] = useState(null);
  const [anomalies, setAnomalies] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTimeframe, setSelectedTimeframe] = useState(7);
  const [selectedUser, setSelectedUser] = useState(null);
  const [showUserProfile, setShowUserProfile] = useState(false);
  const [systemLogs, setSystemLogs] = useState([]);
  const [logsLoading, setLogsLoading] = useState(false);
  const [selectedLogType, setSelectedLogType] = useState('all');
  const [downloadingLogs, setDownloadingLogs] = useState(false);

  useEffect(() => {
    if (active) {
      fetchDashboardData();
      fetchAnomalies();
      fetchAlerts();
      fetchSystemLogs();
    }
  }, [active, selectedTimeframe]);

  useEffect(() => {
    if (active) {
      fetchSystemLogs();
    }
  }, [selectedLogType]);

  const fetchDashboardData = async () => {
    try {
      const response = await api.get(`/api/behavior-analytics/dashboard/?days=${selectedTimeframe}`);
      setDashboardData(response.data);
    } catch (err) {
      console.error('Error fetching behavior analytics dashboard:', err);
      showError('Failed to load behavior analytics data');
    }
  };

  const fetchAnomalies = async () => {
    try {
      const response = await api.get(`/api/behavior-analytics/anomalies/?days=${selectedTimeframe}&page_size=10`);
      setAnomalies(response.results || []);
    } catch (err) {
      console.error('Error fetching anomalies:', err);
    }
  };

  const fetchAlerts = async () => {
    try {
      const response = await api.get('/api/behavior-analytics/alerts/?is_acknowledged=false&page_size=10');
      setAlerts(response.results || []);
    } catch (err) {
      console.error('Error fetching alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInvestigateAnomaly = async (anomalyId, notes, isFalsePositive, isConfirmedThreat) => {
    try {
      await api.post(`/api/behavior-analytics/anomalies/${anomalyId}/investigate/`, {
        investigation_notes: notes,
        is_false_positive: isFalsePositive,
        is_confirmed_threat: isConfirmedThreat
      });
      showSuccess('Anomaly investigation completed');
      fetchAnomalies();
      fetchAlerts();
    } catch (err) {
      showError('Failed to update investigation status');
    }
  };

  const handleAcknowledgeAlert = async (alertId) => {
    try {
      await api.post(`/api/behavior-analytics/alerts/${alertId}/acknowledge/`);
      showSuccess('Alert acknowledged');
      fetchAlerts();
    } catch (err) {
      showError('Failed to acknowledge alert');
    }
  };

  const fetchSystemLogs = async () => {
    setLogsLoading(true);
    try {
      const response = await api.getSystemActivityLogs({
        days: selectedTimeframe,
        log_type: selectedLogType,
        format: 'json'
      });
      if (response.success && response.data) {
        setSystemLogs(response.data.logs.slice(0, 20)); // Show latest 20 logs
      }
    } catch (err) {
      console.error('Error fetching system logs:', err);
      showError('Failed to load system logs');
    } finally {
      setLogsLoading(false);
    }
  };

  const handleDownloadLogs = async (format = 'csv') => {
    setDownloadingLogs(true);
    try {
      const response = await api.downloadSystemLogs({
        days: selectedTimeframe,
        log_type: selectedLogType,
        format: format
      });

      // Create blob and download file
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      
      // Extract filename from response headers
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = `system_logs_${selectedLogType}_${selectedTimeframe}days_${new Date().toISOString().slice(0, 10)}.${format}`;
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }
      
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      showSuccess(`System logs downloaded as ${format.toUpperCase()}`);
    } catch (err) {
      console.error('Error downloading logs:', err);
      showError('Failed to download system logs');
    } finally {
      setDownloadingLogs(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return '#dc3545';
      case 'high': return '#fd7e14';
      case 'medium': return '#ffc107';
      case 'low': return '#28a745';
      default: return '#6c757d';
    }
  };

  const getAlertTypeIcon = (alertType) => {
    switch (alertType) {
      case 'immediate': return 'fas fa-exclamation-triangle';
      case 'suspicious': return 'fas fa-eye';
      case 'policy_violation': return 'fas fa-shield-alt';
      case 'data_exfiltration': return 'fas fa-download';
      default: return 'fas fa-bell';
    }
  };

  const getLogTypeColor = (logType) => {
    switch (logType) {
      case 'activity': return '#17a2b8';
      case 'session': return '#28a745';
      case 'anomaly': return '#dc3545';
      case 'alert': return '#ffc107';
      default: return '#6c757d';
    }
  };

  const getLogTypeIcon = (logType) => {
    switch (logType) {
      case 'activity': return 'fas fa-mouse-pointer';
      case 'session': return 'fas fa-desktop';
      case 'anomaly': return 'fas fa-exclamation-triangle';
      case 'alert': return 'fas fa-bell';
      default: return 'fas fa-file-alt';
    }
  };

  if (!active) return null;

  if (loading) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <i className="fas fa-spinner fa-spin" style={{ fontSize: '3rem', color: '#007bff' }}></i>
        <p style={{ marginTop: '1rem', color: '#666' }}>Loading behavior analytics...</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '1.5rem' }}>
      {/* Header */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '2rem',
        padding: '1rem',
        background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        borderRadius: '8px'
      }}>
        <div>
          <h2 style={{ margin: '0', fontSize: '1.5rem', fontWeight: '600' }}>
            <i className="fas fa-brain" style={{ marginRight: '0.5rem' }}></i>
            User Behavior Analytics
          </h2>
          <p style={{ margin: '0.5rem 0 0 0', opacity: '0.9', fontSize: '0.9rem' }}>
            Statistical detection of suspicious user activities and behavioral anomalies
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <select
            value={selectedTimeframe}
            onChange={(e) => setSelectedTimeframe(parseInt(e.target.value))}
            style={{
              padding: '0.5rem',
              borderRadius: '4px',
              border: 'none',
              fontSize: '0.875rem'
            }}
          >
            <option value={1}>Last 24 hours</option>
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
        </div>
      </div>

      {/* Statistics Cards */}
      {dashboardData && (
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
          gap: '1.5rem', 
          marginBottom: '2rem' 
        }}>
          <div style={{
            background: '#007bff',
            color: 'white',
            padding: '1.5rem',
            borderRadius: '8px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>
              <i className="fas fa-users"></i>
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>
              {dashboardData.statistics.total_users}
            </div>
            <div style={{ fontSize: '0.9rem', opacity: '0.9' }}>Total Users Monitored</div>
          </div>

          <div style={{
            background: '#28a745',
            color: 'white',
            padding: '1.5rem',
            borderRadius: '8px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>
              <i className="fas fa-desktop"></i>
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>
              {dashboardData.statistics.active_sessions}
            </div>
            <div style={{ fontSize: '0.9rem', opacity: '0.9' }}>Active Sessions</div>
          </div>

          <div style={{
            background: '#ffc107',
            color: 'white',
            padding: '1.5rem',
            borderRadius: '8px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>
              <i className="fas fa-exclamation-circle"></i>
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>
              {dashboardData.statistics.total_anomalies}
            </div>
            <div style={{ fontSize: '0.9rem', opacity: '0.9' }}>Anomalies Detected</div>
          </div>

          <div style={{
            background: '#dc3545',
            color: 'white',
            padding: '1.5rem',
            borderRadius: '8px',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>
              <i className="fas fa-bell"></i>
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>
              {dashboardData.statistics.active_alerts}
            </div>
            <div style={{ fontSize: '0.9rem', opacity: '0.9' }}>Active Alerts</div>
          </div>
        </div>
      )}

      {/* Main Content Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        
        {/* Recent Anomalies */}
        <div style={{ 
          backgroundColor: 'white', 
          borderRadius: '8px', 
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)', 
          overflow: 'hidden' 
        }}>
          <div style={{
            background: '#007bff',
            color: 'white',
            padding: '1rem'
          }}>
            <h3 style={{ margin: '0', fontSize: '1.125rem', fontWeight: '600' }}>
              <i className="fas fa-search" style={{ marginRight: '0.5rem' }}></i>
              Recent High-Confidence Anomalies
            </h3>
          </div>
          <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
            {anomalies.length === 0 ? (
              <div style={{ padding: '2rem', textAlign: 'center', color: '#666' }}>
                <i className="fas fa-shield-check" style={{ fontSize: '3rem', marginBottom: '1rem', color: '#28a745' }}></i>
                <p>No high-confidence anomalies detected</p>
              </div>
            ) : (
              anomalies.map((anomaly, index) => (
                <div 
                  key={anomaly.id}
                  style={{ 
                    padding: '1rem',
                    borderBottom: index < anomalies.length - 1 ? '1px solid #dee2e6' : 'none',
                    cursor: 'pointer'
                  }}
                  onMouseEnter={(e) => e.target.closest('div').style.background = '#f8f9fa'}
                  onMouseLeave={(e) => e.target.closest('div').style.background = 'white'}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                        <span style={{
                          backgroundColor: getSeverityColor(anomaly.severity),
                          color: 'white',
                          padding: '0.25rem 0.5rem',
                          borderRadius: '12px',
                          fontSize: '0.75rem',
                          fontWeight: '600',
                          textTransform: 'uppercase'
                        }}>
                          {anomaly.severity}
                        </span>
                        <span style={{ fontSize: '0.875rem', color: '#666' }}>
                          {anomaly.confidence_score}% confidence
                        </span>
                      </div>
                      <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.9rem', fontWeight: '600' }}>
                        {anomaly.title}
                      </h4>
                      <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.8rem', color: '#666', lineHeight: '1.4' }}>
                        {anomaly.description}
                      </p>
                      <div style={{ fontSize: '0.75rem', color: '#999' }}>
                        User: <strong>{anomaly.user.username}</strong> • 
                        {new Date(anomaly.detected_at).toLocaleString()}
                      </div>
                    </div>
                    <div style={{ marginLeft: '1rem' }}>
                      {!anomaly.is_investigated && (
                        <button
                          onClick={() => handleInvestigateAnomaly(anomaly.id, 'Investigated from dashboard', false, false)}
                          style={{
                            padding: '0.375rem 0.75rem',
                            backgroundColor: '#007bff',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            fontSize: '0.75rem',
                            cursor: 'pointer'
                          }}
                        >
                          Investigate
                        </button>
                      )}
                      {anomaly.is_investigated && (
                        <span style={{
                          color: '#28a745',
                          fontSize: '0.75rem',
                          fontWeight: '600'
                        }}>
                          <i className="fas fa-check-circle"></i> Investigated
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Active Alerts */}
        <div style={{ 
          backgroundColor: 'white', 
          borderRadius: '8px', 
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)', 
          overflow: 'hidden' 
        }}>
          <div style={{
            background: '#dc3545',
            color: 'white',
            padding: '1rem'
          }}>
            <h3 style={{ margin: '0', fontSize: '1.125rem', fontWeight: '600' }}>
              <i className="fas fa-bell" style={{ marginRight: '0.5rem' }}></i>
              Active Behavior Alerts
            </h3>
          </div>
          <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
            {alerts.length === 0 ? (
              <div style={{ padding: '2rem', textAlign: 'center', color: '#666' }}>
                <i className="fas fa-shield-check" style={{ fontSize: '3rem', marginBottom: '1rem', color: '#28a745' }}></i>
                <p>No active behavior alerts</p>
              </div>
            ) : (
              alerts.map((alert, index) => (
                <div 
                  key={alert.id}
                  style={{ 
                    padding: '1rem',
                    borderBottom: index < alerts.length - 1 ? '1px solid #dee2e6' : 'none',
                    borderLeft: `4px solid ${getSeverityColor(alert.priority)}`
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                        <i className={getAlertTypeIcon(alert.alert_type)} style={{ color: getSeverityColor(alert.priority) }}></i>
                        <span style={{
                          backgroundColor: getSeverityColor(alert.priority),
                          color: 'white',
                          padding: '0.25rem 0.5rem',
                          borderRadius: '12px',
                          fontSize: '0.75rem',
                          fontWeight: '600',
                          textTransform: 'uppercase'
                        }}>
                          {alert.priority}
                        </span>
                      </div>
                      <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.9rem', fontWeight: '600' }}>
                        {alert.title}
                      </h4>
                      <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.8rem', color: '#666', lineHeight: '1.4' }}>
                        {alert.message}
                      </p>
                      {alert.recommended_actions && alert.recommended_actions.length > 0 && (
                        <div style={{ fontSize: '0.75rem', color: '#007bff', marginBottom: '0.5rem' }}>
                          <strong>Recommended:</strong> {alert.recommended_actions[0]}
                        </div>
                      )}
                      <div style={{ fontSize: '0.75rem', color: '#999' }}>
                        User: <strong>{alert.user.username}</strong> • 
                        {new Date(alert.created_at).toLocaleString()}
                      </div>
                    </div>
                    <div style={{ marginLeft: '1rem' }}>
                      <button
                        onClick={() => handleAcknowledgeAlert(alert.id)}
                        style={{
                          padding: '0.375rem 0.75rem',
                          backgroundColor: '#28a745',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          fontSize: '0.75rem',
                          cursor: 'pointer'
                        }}
                      >
                        Acknowledge
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Anomaly Types Breakdown */}
      {dashboardData && dashboardData.anomaly_breakdown && dashboardData.anomaly_breakdown.length > 0 && (
        <div style={{ 
          backgroundColor: 'white', 
          borderRadius: '8px', 
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)', 
          marginTop: '2rem',
          overflow: 'hidden' 
        }}>
          <div style={{
            background: '#6f42c1',
            color: 'white',
            padding: '1rem'
          }}>
            <h3 style={{ margin: '0', fontSize: '1.125rem', fontWeight: '600' }}>
              <i className="fas fa-chart-pie" style={{ marginRight: '0.5rem' }}></i>
              Anomaly Types Distribution
            </h3>
          </div>
          <div style={{ padding: '1.5rem' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
              {dashboardData.anomaly_breakdown.map((item, index) => {
                const total = dashboardData.anomaly_breakdown.reduce((sum, i) => sum + i.count, 0);
                const percentage = ((item.count / total) * 100).toFixed(1);
                
                return (
                  <div key={index} style={{ 
                    padding: '1rem', 
                    border: '1px solid #dee2e6', 
                    borderRadius: '6px',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#007bff', marginBottom: '0.5rem' }}>
                      {item.count}
                    </div>
                    <div style={{ fontSize: '0.875rem', fontWeight: '600', marginBottom: '0.25rem', textTransform: 'capitalize' }}>
                      {item.anomaly_type.replace('_', ' ')}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#666' }}>
                      {percentage}% of total
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Risky Users */}
      {dashboardData && dashboardData.risky_users && dashboardData.risky_users.length > 0 && (
        <div style={{ 
          backgroundColor: 'white', 
          borderRadius: '8px', 
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)', 
          marginTop: '2rem',
          overflow: 'hidden' 
        }}>
          <div style={{
            background: '#fd7e14',
            color: 'white',
            padding: '1rem'
          }}>
            <h3 style={{ margin: '0', fontSize: '1.125rem', fontWeight: '600' }}>
              <i className="fas fa-user-shield" style={{ marginRight: '0.5rem' }}></i>
              High-Risk Users (Most Anomalies)
            </h3>
          </div>
          <div style={{ padding: '1rem' }}>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f8f9fa' }}>
                    <th style={{ padding: '0.75rem', textAlign: 'left', borderBottom: '2px solid #dee2e6' }}>User</th>
                    <th style={{ padding: '0.75rem', textAlign: 'center', borderBottom: '2px solid #dee2e6' }}>Anomalies</th>
                    <th style={{ padding: '0.75rem', textAlign: 'center', borderBottom: '2px solid #dee2e6' }}>Avg Confidence</th>
                    <th style={{ padding: '0.75rem', textAlign: 'center', borderBottom: '2px solid #dee2e6' }}>Risk Level</th>
                  </tr>
                </thead>
                <tbody>
                  {dashboardData.risky_users.slice(0, 5).map((user, index) => {
                    const riskLevel = user.anomaly_count >= 5 ? 'High' : user.anomaly_count >= 3 ? 'Medium' : 'Low';
                    const riskColor = user.anomaly_count >= 5 ? '#dc3545' : user.anomaly_count >= 3 ? '#ffc107' : '#28a745';
                    
                    return (
                      <tr key={index} style={{ borderBottom: '1px solid #dee2e6' }}>
                        <td style={{ padding: '0.75rem' }}>
                          <div>
                            <div style={{ fontWeight: '600' }}>{user.user__username}</div>
                            {user.user__first_name && (
                              <div style={{ fontSize: '0.8rem', color: '#666' }}>
                                {user.user__first_name} {user.user__last_name}
                              </div>
                            )}
                          </div>
                        </td>
                        <td style={{ padding: '0.75rem', textAlign: 'center' }}>
                          <span style={{
                            backgroundColor: riskColor,
                            color: 'white',
                            padding: '0.25rem 0.5rem',
                            borderRadius: '12px',
                            fontSize: '0.875rem',
                            fontWeight: '600'
                          }}>
                            {user.anomaly_count}
                          </span>
                        </td>
                        <td style={{ padding: '0.75rem', textAlign: 'center' }}>
                          {user.avg_confidence.toFixed(1)}%
                        </td>
                        <td style={{ padding: '0.75rem', textAlign: 'center' }}>
                          <span style={{ color: riskColor, fontWeight: '600' }}>
                            {riskLevel}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* System Logs Section */}
      <div style={{ 
        backgroundColor: 'white', 
        borderRadius: '8px', 
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)', 
        marginTop: '2rem',
        overflow: 'hidden' 
      }}>
        <div style={{
          background: '#20c997',
          color: 'white',
          padding: '1rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <h3 style={{ margin: '0', fontSize: '1.125rem', fontWeight: '600' }}>
            <i className="fas fa-file-text" style={{ marginRight: '0.5rem' }}></i>
            System Activity Logs
          </h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <select
              value={selectedLogType}
              onChange={(e) => setSelectedLogType(e.target.value)}
              style={{
                padding: '0.375rem 0.75rem',
                borderRadius: '4px',
                border: 'none',
                fontSize: '0.875rem',
                backgroundColor: 'white',
                color: '#333'
              }}
            >
              <option value="all">All Logs</option>
              <option value="activities">User Activities</option>
              <option value="sessions">User Sessions</option>
              <option value="anomalies">Anomalies</option>
              <option value="alerts">Alerts</option>
            </select>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                onClick={() => handleDownloadLogs('csv')}
                disabled={downloadingLogs}
                style={{
                  padding: '0.375rem 0.75rem',
                  backgroundColor: '#007bff',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  fontSize: '0.875rem',
                  cursor: downloadingLogs ? 'not-allowed' : 'pointer',
                  opacity: downloadingLogs ? 0.6 : 1,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.25rem'
                }}
              >
                {downloadingLogs ? (
                  <i className="fas fa-spinner fa-spin"></i>
                ) : (
                  <i className="fas fa-download"></i>
                )}
                CSV
              </button>
              <button
                onClick={() => handleDownloadLogs('json')}
                disabled={downloadingLogs}
                style={{
                  padding: '0.375rem 0.75rem',
                  backgroundColor: '#6f42c1',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  fontSize: '0.875rem',
                  cursor: downloadingLogs ? 'not-allowed' : 'pointer',
                  opacity: downloadingLogs ? 0.6 : 1,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.25rem'
                }}
              >
                {downloadingLogs ? (
                  <i className="fas fa-spinner fa-spin"></i>
                ) : (
                  <i className="fas fa-download"></i>
                )}
                JSON
              </button>
            </div>
          </div>
        </div>
        
        <div style={{ padding: '1rem' }}>
          {logsLoading ? (
            <div style={{ textAlign: 'center', padding: '2rem' }}>
              <i className="fas fa-spinner fa-spin" style={{ fontSize: '2rem', color: '#20c997' }}></i>
              <p style={{ marginTop: '1rem', color: '#666' }}>Loading system logs...</p>
            </div>
          ) : systemLogs.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
              <i className="fas fa-inbox" style={{ fontSize: '3rem', marginBottom: '1rem', color: '#20c997' }}></i>
              <p>No logs found for the selected criteria</p>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f8f9fa' }}>
                    <th style={{ padding: '0.75rem', textAlign: 'left', borderBottom: '2px solid #dee2e6', fontSize: '0.875rem' }}>Timestamp</th>
                    <th style={{ padding: '0.75rem', textAlign: 'left', borderBottom: '2px solid #dee2e6', fontSize: '0.875rem' }}>Type</th>
                    <th style={{ padding: '0.75rem', textAlign: 'left', borderBottom: '2px solid #dee2e6', fontSize: '0.875rem' }}>User</th>
                    <th style={{ padding: '0.75rem', textAlign: 'left', borderBottom: '2px solid #dee2e6', fontSize: '0.875rem' }}>Action/Event</th>
                    <th style={{ padding: '0.75rem', textAlign: 'left', borderBottom: '2px solid #dee2e6', fontSize: '0.875rem' }}>Details</th>
                    <th style={{ padding: '0.75rem', textAlign: 'left', borderBottom: '2px solid #dee2e6', fontSize: '0.875rem' }}>IP Address</th>
                  </tr>
                </thead>
                <tbody>
                  {systemLogs.map((log, index) => (
                    <tr key={index} style={{ 
                      borderBottom: '1px solid #dee2e6',
                      backgroundColor: index % 2 === 0 ? 'white' : '#f8f9fa'
                    }}>
                      <td style={{ padding: '0.75rem', fontSize: '0.8rem' }}>
                        {new Date(log.timestamp).toLocaleString()}
                      </td>
                      <td style={{ padding: '0.75rem' }}>
                        <span style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.25rem',
                          color: getLogTypeColor(log.log_type),
                          fontSize: '0.8rem',
                          fontWeight: '600'
                        }}>
                          <i className={getLogTypeIcon(log.log_type)}></i>
                          {log.log_type}
                        </span>
                      </td>
                      <td style={{ padding: '0.75rem', fontSize: '0.8rem' }}>
                        {log.username}
                      </td>
                      <td style={{ padding: '0.75rem', fontSize: '0.8rem' }}>
                        {log.action_type || log.anomaly_type || log.alert_type || 'Session'}
                      </td>
                      <td style={{ padding: '0.75rem', fontSize: '0.8rem', maxWidth: '300px' }}>
                        <div style={{ 
                          overflow: 'hidden', 
                          textOverflow: 'ellipsis', 
                          whiteSpace: 'nowrap',
                          color: '#666'
                        }}>
                          {log.description || log.message || log.endpoint || 
                           (log.duration_minutes ? `Session duration: ${log.duration_minutes}min` : 'N/A')}
                        </div>
                      </td>
                      <td style={{ padding: '0.75rem', fontSize: '0.8rem', color: '#666' }}>
                        {log.ip_address || 'N/A'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          
          {systemLogs.length > 0 && (
            <div style={{ 
              marginTop: '1rem', 
              padding: '0.75rem',
              backgroundColor: '#f8f9fa',
              borderRadius: '4px',
              fontSize: '0.8rem',
              color: '#666',
              textAlign: 'center'
            }}>
              Showing latest 20 logs. Use download buttons above to get complete logs for the selected timeframe.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default BehaviorAnalyticsDashboard;