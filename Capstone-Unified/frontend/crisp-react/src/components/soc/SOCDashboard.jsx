import React, { useState, useEffect, useRef } from 'react';
import * as api from '../../api.js';
import { useNotifications } from '../enhanced/NotificationManager.jsx';

const SOCDashboard = ({ active, showPage }) => {
  const { showError, showInfo } = useNotifications();
  const wsRef = useRef(null);
  const intervalRef = useRef(null);

  // All hooks must be called before any early returns
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [downloading, setDownloading] = useState(false);
  const [systemHealth, setSystemHealth] = useState(null);
  const [realTimeAlerts, setRealTimeAlerts] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [criticalAlerts, setCriticalAlerts] = useState([]);
  const [networkActivity, setNetworkActivity] = useState(null);
  const [topThreats, setTopThreats] = useState([]);
  const [mitreTactics, setMitreTactics] = useState([]);
  const [threatIntelligence, setThreatIntelligence] = useState(null);

  useEffect(() => {
    if (active) {
      initializeSOCDashboard();
      setupWebSocketConnection();
      setupRealTimeRefresh();
    }
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [active]);

  const initializeSOCDashboard = async () => {
    setLoading(true);
    try {
      await Promise.all([
        fetchDashboardData(),
        fetchSystemHealth(),
        fetchNetworkActivity(),
        fetchTopThreats(),
        fetchMitreTactics(),
        fetchThreatIntelligence()
      ]);
    } catch (err) {
      console.error('Error initializing SOC dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const setupWebSocketConnection = () => {
    try {
      const token = localStorage.getItem('access_token');
      const wsUrl = `ws://localhost:8000/ws/soc/?token=${token}`;
      wsRef.current = new WebSocket(wsUrl);
      
      wsRef.current.onopen = () => {
        console.log('SOC WebSocket connected');
        showInfo('Real-time monitoring connected');
      };
      
      wsRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      };
      
      wsRef.current.onclose = () => {
        console.log('SOC WebSocket disconnected');
        // Attempt to reconnect after 5 seconds
        setTimeout(() => {
          if (active) setupWebSocketConnection();
        }, 5000);
      };
      
      wsRef.current.onerror = (error) => {
        console.error('SOC WebSocket error:', error);
      };
    } catch (err) {
      console.error('Failed to setup WebSocket:', err);
    }
  };

  const handleWebSocketMessage = (data) => {
    switch (data.type) {
      case 'new_alert':
        setRealTimeAlerts(prev => [data.alert, ...prev.slice(0, 9)]);
        if (data.alert.priority === 'critical') {
          setCriticalAlerts(prev => [data.alert, ...prev.slice(0, 4)]);
          showError('Critical Alert', data.alert.title);
        }
        break;
      case 'incident_update':
        fetchDashboardData();
        break;
      case 'threat_intel_update':
        fetchThreatIntelligence();
        break;
      case 'system_health':
        setSystemHealth(data.health);
        break;
      default:
        console.log('Unknown WebSocket message type:', data.type);
    }
  };

  const setupRealTimeRefresh = () => {
    // Refresh data every 30 seconds
    intervalRef.current = setInterval(() => {
      fetchDashboardData();
      fetchSystemHealth();
      fetchNetworkActivity();
    }, 30000);
  };

  const fetchDashboardData = async () => {
    try {
      const response = await api.get('/api/soc/dashboard/');
      if (response?.data) {
        setDashboardData(response.data);
        setError(null);
      }
    } catch (err) {
      setError('Failed to load SOC dashboard data');
      console.error('SOC Dashboard Error:', err);
    }
  };

  // Check if component is active and user has access
  if (!active) return null;

  // Check if user is BlueVisionAdmin
  const currentUser = api.getCurrentUser();
  if (!currentUser || currentUser.role !== 'BlueVisionAdmin') {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <div className="alert alert-warning" role="alert">
          <i className="fas fa-lock mr-2"></i>
          <strong>Access Restricted</strong>
          <p className="mb-0 mt-2">SOC features are only available to BlueVision administrators.</p>
        </div>
      </div>
    );
  }

  const fetchSystemHealth = async () => {
    try {
      const response = await fetch('/api/soc/system-health/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setSystemHealth(data);
      }
    } catch (err) {
      console.error('Failed to fetch system health:', err);
    }
  };

  const fetchNetworkActivity = async () => {
    try {
      const response = await fetch('/api/soc/network-activity/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setNetworkActivity(data);
      }
    } catch (err) {
      console.error('Failed to fetch network activity:', err);
    }
  };

  const fetchTopThreats = async () => {
    try {
      const response = await fetch('/api/soc/top-threats/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setTopThreats(data.threats || []);
      }
    } catch (err) {
      console.error('Failed to fetch top threats:', err);
    }
  };

  const fetchMitreTactics = async () => {
    try {
      const response = await fetch('/api/soc/mitre-tactics/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setMitreTactics(data.tactics || []);
      }
    } catch (err) {
      console.error('Failed to fetch MITRE tactics:', err);
    }
  };

  const fetchThreatIntelligence = async () => {
    try {
      const response = await fetch('/api/soc/threat-intelligence/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setThreatIntelligence(data);
      }
    } catch (err) {
      console.error('Failed to fetch threat intelligence:', err);
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

  const handleDownload = async (format) => {
    try {
      setDownloading(true);
      
      // Use the API function for SOC incidents export
      const response = await api.exportSOCIncidents(format, { days: 30 });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        
        // Create a temporary link element to trigger download
        const link = document.createElement('a');
        link.href = url;
        
        // Get filename from Content-Disposition header or generate one
        const contentDisposition = response.headers.get('content-disposition');
        let filename = `soc_incidents_export.${format}`;
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
          if (filenameMatch) {
            filename = filenameMatch[1];
          }
        }
        
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } else {
        throw new Error('Failed to download file');
      }
    } catch (err) {
      console.error('Download error:', err);
      showError('Download Failed', 'Failed to download incidents: ' + err.message);
    } finally {
      setDownloading(false);
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

  const renderTabNavigation = () => (
    <div className="nav nav-tabs mb-4" style={{ borderBottom: '2px solid #dee2e6' }}>
      {[
        { key: 'overview', label: 'Overview', icon: 'fa-chart-line' },
        { key: 'threats', label: 'Threat Intelligence', icon: 'fa-shield-virus' },
        { key: 'network', label: 'Network Activity', icon: 'fa-network-wired' },
        { key: 'mitre', label: 'MITRE ATT&CK', icon: 'fa-crosshairs' },
        { key: 'alerts', label: 'Live Alerts', icon: 'fa-bell' }
      ].map(tab => (
        <button
          key={tab.key}
          className={`nav-link ${activeTab === tab.key ? 'active' : ''}`}
          onClick={() => setActiveTab(tab.key)}
          style={{
            padding: '12px 20px',
            border: 'none',
            background: activeTab === tab.key ? '#007bff' : 'transparent',
            color: activeTab === tab.key ? 'white' : '#495057',
            fontWeight: '500',
            borderRadius: '8px 8px 0 0',
            marginRight: '5px'
          }}
        >
          <i className={`fas ${tab.icon} mr-2`}></i>
          {tab.label}
        </button>
      ))}
    </div>
  );

  const renderSystemHealthBar = () => (
    <div className="alert alert-info mb-4" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', border: 'none', color: 'white' }}>
      <div className="row align-items-center">
        <div className="col-md-8">
          <div className="d-flex align-items-center">
            <div className="mr-4">
              <i className="fas fa-server fa-2x"></i>
            </div>
            <div>
              <h5 className="mb-1">Security Operations Center Status</h5>
              <div className="d-flex align-items-center">
                <span className="badge badge-success mr-2">
                  <i className="fas fa-check-circle mr-1"></i>
                  Systems Online
                </span>
                {systemHealth && (
                  <>
                    <span className="mr-3">CPU: {systemHealth.cpu_usage}%</span>
                    <span className="mr-3">Memory: {systemHealth.memory_usage}%</span>
                    <span>Alerts: {systemHealth.active_alerts}</span>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-4 text-right">
          <div className="d-flex justify-content-end align-items-center">
            <div className="mr-3">
              <small>Connected Users: {systemHealth?.connected_users || 0}</small>
            </div>
            <div className="text-success">
              <i className="fas fa-circle fa-xs mr-1" style={{ animation: 'pulse 2s infinite' }}></i>
              Live
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div style={{ padding: '20px', background: '#f8f9fa', minHeight: '100vh' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ color: '#495057', fontWeight: '600' }}>
          <i className="fas fa-shield-alt mr-2" style={{ color: '#007bff' }}></i>
          Security Operations Center
        </h2>
        <div className="d-flex align-items-center">
          <div style={{ fontSize: '0.9em', color: '#6c757d', marginRight: '15px' }}>
            <i className="fas fa-sync-alt mr-1"></i>
            Last updated: {new Date(dashboardData?.last_updated || Date.now()).toLocaleTimeString()}
          </div>
          <button
            className="btn btn-outline-primary btn-sm"
            onClick={initializeSOCDashboard}
            title="Refresh Dashboard"
          >
            <i className="fas fa-sync-alt"></i>
          </button>
        </div>
      </div>

      {renderSystemHealthBar()}
      {renderTabNavigation()}

      {activeTab === 'overview' && (
        <>
          {/* Critical Alerts Banner */}
          {criticalAlerts.length > 0 && (
            <div className="alert alert-danger mb-4" style={{ borderLeft: '5px solid #dc3545' }}>
              <div className="d-flex align-items-center">
                <div className="mr-3">
                  <i className="fas fa-exclamation-triangle fa-2x"></i>
                </div>
                <div className="flex-grow-1">
                  <h5 className="alert-heading mb-2">Critical Security Alerts</h5>
                  <div className="row">
                    {criticalAlerts.slice(0, 2).map((alert, index) => (
                      <div key={index} className="col-md-6 mb-2">
                        <strong>{alert.title}</strong>
                        <div className="small">{alert.description}</div>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <button className="btn btn-outline-danger btn-sm" onClick={() => setActiveTab('alerts')}>
                    View All Alerts
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Enhanced Key Metrics Cards */}
          <div className="row mb-4">
            <div className="col-md-3 mb-3">
              <div className="card h-100" style={{ border: 'none', boxShadow: '0 4px 6px rgba(0,123,255,0.1)', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
                <div className="card-body text-center text-white">
                  <div style={{ fontSize: '2.5rem', marginBottom: '15px' }}>
                    <i className="fas fa-exclamation-circle"></i>
                  </div>
                  <h2 style={{ fontSize: '2.5rem', fontWeight: 'bold', marginBottom: '5px' }}>{metrics.open_incidents}</h2>
                  <p className="mb-2" style={{ fontSize: '1.1rem' }}>Open Incidents</p>
                  <div className="small">
                    <i className="fas fa-arrow-up mr-1"></i>
                    +{metrics.incidents_today} today
                  </div>
                </div>
              </div>
            </div>
            
            <div className="col-md-3 mb-3">
              <div className="card h-100" style={{ border: 'none', boxShadow: '0 4px 6px rgba(220,53,69,0.1)', background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
                <div className="card-body text-center text-white">
                  <div style={{ fontSize: '2.5rem', marginBottom: '15px' }}>
                    <i className="fas fa-fire"></i>
                  </div>
                  <h2 style={{ fontSize: '2.5rem', fontWeight: 'bold', marginBottom: '5px' }}>{metrics.critical_incidents}</h2>
                  <p className="mb-2" style={{ fontSize: '1.1rem' }}>Critical</p>
                  <div className="small">
                    <i className="fas fa-clock mr-1"></i>
                    Immediate attention
                  </div>
                </div>
              </div>
            </div>
            
            <div className="col-md-3 mb-3">
              <div className="card h-100" style={{ border: 'none', boxShadow: '0 4px 6px rgba(255,193,7,0.1)', background: 'linear-gradient(135deg, #fdbb2d 0%, #22c1c3 100%)' }}>
                <div className="card-body text-center text-white">
                  <div style={{ fontSize: '2.5rem', marginBottom: '15px' }}>
                    <i className="fas fa-clock"></i>
                  </div>
                  <h2 style={{ fontSize: '2.5rem', fontWeight: 'bold', marginBottom: '5px' }}>{metrics.overdue_incidents}</h2>
                  <p className="mb-2" style={{ fontSize: '1.1rem' }}>Overdue</p>
                  <div className="small">
                    <i className="fas fa-exclamation-triangle mr-1"></i>
                    SLA breached
                  </div>
                </div>
              </div>
            </div>
            
            <div className="col-md-3 mb-3">
              <div className="card h-100" style={{ border: 'none', boxShadow: '0 4px 6px rgba(40,167,69,0.1)', background: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)' }}>
                <div className="card-body text-center text-dark">
                  <div style={{ fontSize: '2.5rem', marginBottom: '15px', color: '#28a745' }}>
                    <i className="fas fa-check-circle"></i>
                  </div>
                  <h2 style={{ fontSize: '2.5rem', fontWeight: 'bold', marginBottom: '5px', color: '#28a745' }}>{metrics.resolved_today}</h2>
                  <p className="mb-2" style={{ fontSize: '1.1rem' }}>Resolved Today</p>
                  <div className="small text-success">
                    <i className="fas fa-arrow-up mr-1"></i>
                    +{metrics.resolved_week} this week
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {activeTab === 'overview' && (
        <>
          {/* Enhanced Activity Metrics */}
          <div className="row mb-4">
            <div className="col-md-4 mb-3">
              <div className="card h-100" style={{ border: 'none', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
                <div className="card-header" style={{ background: 'linear-gradient(90deg, #4facfe 0%, #00f2fe 100%)', color: 'white', border: 'none' }}>
                  <h5 className="mb-0">
                    <i className="fas fa-chart-line mr-2"></i>
                    Activity Metrics
                  </h5>
                </div>
                <div className="card-body">
                  <div className="d-flex justify-content-between mb-3 p-2" style={{ background: '#f8f9fa', borderRadius: '5px' }}>
                    <span className="text-muted">Today:</span>
                    <strong className="text-primary">{metrics.incidents_today} created</strong>
                  </div>
                  <div className="d-flex justify-content-between mb-3 p-2">
                    <span className="text-muted">This Week:</span>
                    <strong className="text-info">{metrics.incidents_week} created</strong>
                  </div>
                  <div className="d-flex justify-content-between mb-3 p-2" style={{ background: '#f8f9fa', borderRadius: '5px' }}>
                    <span className="text-muted">This Month:</span>
                    <strong className="text-warning">{metrics.incidents_month} created</strong>
                  </div>
                  <div className="d-flex justify-content-between p-2" style={{ background: '#d4edda', borderRadius: '5px' }}>
                    <span className="text-muted">Resolved This Week:</span>
                    <strong className="text-success">{metrics.resolved_week}</strong>
                  </div>
                  <div className="mt-3 pt-3 border-top">
                    <div className="small text-center text-muted">
                      Resolution Rate: {metrics.resolved_week && metrics.incidents_week ? 
                        Math.round((metrics.resolved_week / metrics.incidents_week) * 100) : 0}%
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Enhanced Status Breakdown */}
            <div className="col-md-4 mb-3">
              <div className="card h-100" style={{ border: 'none', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
                <div className="card-header" style={{ background: 'linear-gradient(90deg, #a8edea 0%, #fed6e3 100%)', color: '#495057', border: 'none' }}>
                  <h5 className="mb-0">
                    <i className="fas fa-pie-chart mr-2"></i>
                    Status Distribution
                  </h5>
                </div>
                <div className="card-body">
                  {Object.entries(breakdowns.status).map(([status, count]) => {
                    const total = Object.values(breakdowns.status).reduce((a, b) => a + b, 0);
                    const percentage = total > 0 ? Math.round((count / total) * 100) : 0;
                    return (
                      <div key={status} className="mb-3">
                        <div className="d-flex justify-content-between align-items-center mb-1">
                          <span className="d-flex align-items-center">
                            <span 
                              className="mr-2" 
                              style={{ 
                                backgroundColor: getStatusColor(status), 
                                color: 'white',
                                padding: '4px 8px',
                                fontSize: '0.7rem',
                                fontWeight: 'bold',
                                textTransform: 'uppercase',
                                borderRadius: '12px',
                                display: 'inline-block',
                                minWidth: '60px',
                                textAlign: 'center'
                              }}
                            >
                              {status.replace('_', ' ')}
                            </span>
                            <small className="text-muted">{percentage}%</small>
                          </span>
                          <strong style={{ color: getStatusColor(status) }}>{count}</strong>
                        </div>
                        <div className="progress" style={{ height: '4px' }}>
                          <div 
                            className="progress-bar" 
                            style={{ 
                              width: `${percentage}%`, 
                              backgroundColor: getStatusColor(status),
                              transition: 'width 0.6s ease'
                            }}
                          ></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Enhanced Priority Breakdown */}
            <div className="col-md-4 mb-3">
              <div className="card h-100" style={{ border: 'none', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
                <div className="card-header" style={{ background: 'linear-gradient(90deg, #fdbb2d 0%, #22c1c3 100%)', color: 'white', border: 'none' }}>
                  <h5 className="mb-0">
                    <i className="fas fa-exclamation-triangle mr-2"></i>
                    Risk Priority Matrix
                  </h5>
                </div>
                <div className="card-body">
                  {Object.entries(breakdowns.priority).map(([priority, count]) => {
                    const total = Object.values(breakdowns.priority).reduce((a, b) => a + b, 0);
                    const percentage = total > 0 ? Math.round((count / total) * 100) : 0;
                    const riskLevel = priority === 'critical' ? 'EXTREME' : priority === 'high' ? 'HIGH' : priority === 'medium' ? 'MODERATE' : 'LOW';
                    return (
                      <div key={priority} className="mb-3">
                        <div className="d-flex justify-content-between align-items-center mb-1">
                          <span className="d-flex align-items-center">
                            <span 
                              className="mr-2" 
                              style={{ 
                                backgroundColor: getPriorityColor(priority), 
                                color: 'white',
                                padding: '4px 8px',
                                fontSize: '0.7rem',
                                fontWeight: 'bold',
                                textTransform: 'uppercase',
                                borderRadius: '12px',
                                display: 'inline-block',
                                minWidth: '70px',
                                textAlign: 'center'
                              }}
                            >
                              {priority}
                            </span>
                            <small className="text-muted">{riskLevel}</small>
                          </span>
                          <div className="text-right">
                            <strong style={{ color: getPriorityColor(priority) }}>{count}</strong>
                            <div className="small text-muted">{percentage}%</div>
                          </div>
                        </div>
                        <div className="progress" style={{ height: '6px' }}>
                          <div 
                            className="progress-bar" 
                            style={{ 
                              width: `${percentage}%`, 
                              backgroundColor: getPriorityColor(priority),
                              transition: 'width 0.6s ease'
                            }}
                          ></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Tab Content */}
      {activeTab === 'threats' && (
        <div className="row">
          <div className="col-md-6 mb-4">
            <div className="card h-100">
              <div className="card-header">
                <h5 className="mb-0">
                  <i className="fas fa-shield-virus mr-2"></i>
                  Top Threats
                </h5>
              </div>
              <div className="card-body">
                {topThreats.length > 0 ? topThreats.map((threat, index) => (
                  <div key={index} className="d-flex justify-content-between align-items-center mb-3 p-2" style={{ background: '#f8f9fa', borderRadius: '5px' }}>
                    <div>
                      <strong>{threat.name}</strong>
                      <div className="small text-muted">{threat.category}</div>
                    </div>
                    <div className="text-right">
                      <span className="badge badge-danger">{threat.severity}</span>
                      <div className="small text-muted">{threat.incidents} incidents</div>
                    </div>
                  </div>
                )) : (
                  <div className="text-center text-muted py-4">
                    <i className="fas fa-shield-alt fa-3x mb-3"></i>
                    <p>No threat intelligence data available</p>
                  </div>
                )}
              </div>
            </div>
          </div>
          <div className="col-md-6 mb-4">
            <div className="card h-100">
              <div className="card-header">
                <h5 className="mb-0">
                  <i className="fas fa-globe mr-2"></i>
                  Threat Intelligence Summary
                </h5>
              </div>
              <div className="card-body">
                {threatIntelligence ? (
                  <>
                    <div className="row mb-3">
                      <div className="col-6">
                        <div className="text-center">
                          <h4 className="text-primary">{threatIntelligence.iocs_count}</h4>
                          <small className="text-muted">IOCs</small>
                        </div>
                      </div>
                      <div className="col-6">
                        <div className="text-center">
                          <h4 className="text-warning">{threatIntelligence.feeds_active}</h4>
                          <small className="text-muted">Active Feeds</small>
                        </div>
                      </div>
                    </div>
                    <div className="border-top pt-3">
                      <div className="d-flex justify-content-between mb-2">
                        <span>Last Update:</span>
                        <small className="text-muted">{new Date(threatIntelligence.last_update).toLocaleString()}</small>
                      </div>
                      <div className="d-flex justify-content-between">
                        <span>Confidence Level:</span>
                        <span className="badge badge-success">{threatIntelligence.confidence}</span>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="text-center text-muted py-4">
                    <i className="fas fa-satellite-dish fa-3x mb-3"></i>
                    <p>Loading threat intelligence...</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'network' && (
        <div className="row">
          <div className="col-12 mb-4">
            <div className="card">
              <div className="card-header">
                <h5 className="mb-0">
                  <i className="fas fa-network-wired mr-2"></i>
                  Network Activity Monitor
                </h5>
              </div>
              <div className="card-body">
                {networkActivity ? (
                  <div className="row">
                    <div className="col-md-3 text-center mb-3">
                      <h4 className="text-info">{networkActivity.connections_count}</h4>
                      <small className="text-muted">Active Connections</small>
                    </div>
                    <div className="col-md-3 text-center mb-3">
                      <h4 className="text-success">{networkActivity.bandwidth_usage}%</h4>
                      <small className="text-muted">Bandwidth Usage</small>
                    </div>
                    <div className="col-md-3 text-center mb-3">
                      <h4 className="text-warning">{networkActivity.suspicious_ips}</h4>
                      <small className="text-muted">Suspicious IPs</small>
                    </div>
                    <div className="col-md-3 text-center mb-3">
                      <h4 className="text-danger">{networkActivity.blocked_attempts}</h4>
                      <small className="text-muted">Blocked Attempts</small>
                    </div>
                  </div>
                ) : (
                  <div className="text-center text-muted py-4">
                    <i className="fas fa-chart-line fa-3x mb-3"></i>
                    <p>Loading network activity data...</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'mitre' && (
        <div className="row">
          <div className="col-12 mb-4">
            <div className="card">
              <div className="card-header">
                <h5 className="mb-0">
                  <i className="fas fa-crosshairs mr-2"></i>
                  MITRE ATT&CK Tactics Detection
                </h5>
              </div>
              <div className="card-body">
                {mitreTactics.length > 0 ? (
                  <div className="row">
                    {mitreTactics.map((tactic, index) => (
                      <div key={index} className="col-md-4 mb-3">
                        <div className="card h-100" style={{ border: '1px solid #dee2e6' }}>
                          <div className="card-body">
                            <h6 className="card-title">{tactic.name}</h6>
                            <p className="card-text small text-muted">{tactic.description}</p>
                            <div className="d-flex justify-content-between align-items-center">
                              <span className="badge badge-primary">{tactic.technique_count} techniques</span>
                              <span className="badge badge-warning">{tactic.detection_count} detected</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center text-muted py-4">
                    <i className="fas fa-crosshairs fa-3x mb-3"></i>
                    <p>No MITRE ATT&CK data available</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'alerts' && (
        <div className="row">
          <div className="col-12 mb-4">
            <div className="card">
              <div className="card-header">
                <h5 className="mb-0">
                  <i className="fas fa-bell mr-2"></i>
                  Live Security Alerts
                  <span className="badge badge-danger ml-2">{realTimeAlerts.length}</span>
                </h5>
              </div>
              <div className="card-body">
                {realTimeAlerts.length > 0 ? (
                  <div className="list-group list-group-flush">
                    {realTimeAlerts.map((alert, index) => (
                      <div key={index} className="list-group-item d-flex justify-content-between align-items-center">
                        <div>
                          <h6 className="mb-1">{alert.title}</h6>
                          <p className="mb-1 text-muted">{alert.description}</p>
                          <small className="text-muted">{new Date(alert.timestamp).toLocaleString()}</small>
                        </div>
                        <span className={`badge badge-${alert.priority === 'critical' ? 'danger' : alert.priority === 'high' ? 'warning' : 'info'}`}>
                          {alert.priority}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center text-muted py-4">
                    <i className="fas fa-shield-check fa-3x mb-3"></i>
                    <p>No active alerts - All systems secure</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'overview' && (
        <>
          {/* Recent Incidents */}
          <div className="card" style={{ border: 'none', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
            <div className="card-header d-flex justify-content-between align-items-center" style={{ background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)', color: 'white', border: 'none' }}>
              <h5 className="mb-0">
                <i className="fas fa-list mr-2"></i>
                Recent Security Incidents
              </h5>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <button 
                  className="btn btn-light btn-sm"
                  onClick={() => handleDownload('csv')}
                  disabled={downloading}
                  style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '0.5rem'
                  }}
                >
                  {downloading ? (
                    <>
                      <span className="spinner-border spinner-border-sm"></span>
                      Exporting...
                    </>
                  ) : (
                    <>
                      <i className="fas fa-file-csv"></i>
                      CSV
                    </>
                  )}
                </button>
                <button 
                  className="btn btn-light btn-sm"
                  onClick={() => handleDownload('json')}
                  disabled={downloading}
                  style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '0.5rem'
                  }}
                >
                  <i className="fas fa-file-code"></i>
                  JSON
                </button>
                <button 
                  className="btn btn-light btn-sm"
                  onClick={() => showPage('soc-incidents')}
                >
                  <i className="fas fa-external-link-alt mr-1"></i>
                  View All
                </button>
              </div>
            </div>
            <div className="card-body p-0">
              {recent_incidents.length === 0 ? (
                <div className="text-center p-5 text-muted">
                  <i className="fas fa-shield-check fa-3x mb-3" style={{ color: '#28a745' }}></i>
                  <h5>No Recent Incidents</h5>
                  <p>All systems are operating normally</p>
                </div>
              ) : (
                <div className="table-responsive">
                  <table className="table table-hover mb-0" style={{ fontSize: '0.9rem' }}>
                    <thead style={{ background: '#f8f9fa' }}>
                      <tr>
                        <th style={{ borderTop: 'none', padding: '12px' }}>ID</th>
                        <th style={{ borderTop: 'none', padding: '12px' }}>Title</th>
                        <th style={{ borderTop: 'none', padding: '12px' }}>Priority</th>
                        <th style={{ borderTop: 'none', padding: '12px' }}>Status</th>
                        <th style={{ borderTop: 'none', padding: '12px' }}>Created</th>
                        <th style={{ borderTop: 'none', padding: '12px' }}>SLA Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recent_incidents.map((incident, index) => (
                        <tr 
                          key={incident.id}
                          style={{ 
                            cursor: 'pointer',
                            background: index % 2 === 0 ? '#fafafa' : 'white'
                          }}
                          onMouseEnter={(e) => e.target.closest('tr').style.background = '#e3f2fd'}
                          onMouseLeave={(e) => e.target.closest('tr').style.background = index % 2 === 0 ? '#fafafa' : 'white'}
                        >
                          <td style={{ padding: '12px' }}>
                            <code style={{ 
                              background: '#f8f9fa', 
                              padding: '4px 8px', 
                              borderRadius: '4px',
                              fontSize: '0.8rem'
                            }}>
                              {incident.incident_id}
                            </code>
                          </td>
                          <td style={{ padding: '12px' }}>
                            <div style={{ 
                              maxWidth: '250px', 
                              overflow: 'hidden', 
                              textOverflow: 'ellipsis', 
                              whiteSpace: 'nowrap',
                              fontWeight: '500'
                            }}>
                              {incident.title}
                            </div>
                          </td>
                          <td style={{ padding: '12px' }}>
                            <span 
                              style={{ 
                                backgroundColor: getPriorityColor(incident.priority), 
                                color: 'white',
                                padding: '6px 12px',
                                fontSize: '0.7rem',
                                fontWeight: 'bold',
                                textTransform: 'uppercase',
                                borderRadius: '12px',
                                display: 'inline-block',
                                minWidth: '60px',
                                textAlign: 'center'
                              }}
                            >
                              {incident.priority}
                            </span>
                          </td>
                          <td style={{ padding: '12px' }}>
                            <span 
                              style={{ 
                                backgroundColor: getStatusColor(incident.status), 
                                color: 'white',
                                padding: '6px 12px',
                                fontSize: '0.7rem',
                                fontWeight: 'bold',
                                textTransform: 'uppercase',
                                borderRadius: '12px',
                                display: 'inline-block',
                                minWidth: '80px',
                                textAlign: 'center'
                              }}
                            >
                              {incident.status.replace('_', ' ')}
                            </span>
                          </td>
                          <td style={{ padding: '12px' }}>
                            <div className="small">
                              <div>{new Date(incident.created_at).toLocaleDateString()}</div>
                              <div className="text-muted">{new Date(incident.created_at).toLocaleTimeString()}</div>
                            </div>
                          </td>
                          <td style={{ padding: '12px' }}>
                            {incident.is_overdue ? (
                              <span className="badge badge-danger" style={{ padding: '6px 10px' }}>
                                <i className="fas fa-exclamation-triangle mr-1"></i>
                                Overdue
                              </span>
                            ) : (
                              <span className="badge badge-success" style={{ padding: '6px 10px' }}>
                                <i className="fas fa-check mr-1"></i>
                                On Track
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
        </>
      )}
    </div>
  );
};

// Add CSS for animations
const style = document.createElement('style');
style.textContent = `
@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}
`;
document.head.appendChild(style);

export default SOCDashboard;