import React, { useState, useEffect, useRef } from 'react';
import * as api from '../../api.js';
import { useNotifications } from '../enhanced/NotificationManager.jsx';
import SOCIncidentModal from './SOCIncidentModal.jsx';
import SOCIncidentEditModal from './SOCIncidentEditModal.jsx';
import BehaviorAnalyticsDashboard from './BehaviorAnalyticsDashboard.jsx';

const SOCDashboard = ({ active, showPage }) => {
  const { showError, showInfo, showSuccess } = useNotifications();
  const wsRef = useRef(null);
  const intervalRef = useRef(null);

  // All hooks must be called before any early returns
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [downloading, setDownloading] = useState(false);
  const [realTimeAlerts, setRealTimeAlerts] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [criticalAlerts, setCriticalAlerts] = useState([]);
  const [topThreats, setTopThreats] = useState([]);
  const [mitreTactics, setMitreTactics] = useState([]);
  const [threatIntelligence, setThreatIntelligence] = useState(null);
  const [liveIOCAlerts, setLiveIOCAlerts] = useState([]);
  const [iocCorrelation, setIOCCorrelation] = useState(null);
  
  // Interactive MITRE states
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTactic, setSelectedTactic] = useState(null);
  const [selectedTechnique, setSelectedTechnique] = useState(null);
  const [showTechniqueModal, setShowTechniqueModal] = useState(false);
  const [hoveredTactic, setHoveredTactic] = useState(null);
  const [filterBySeverity, setFilterBySeverity] = useState('all');
  const [sortBy, setSortBy] = useState('detection_count');
  const [viewMode, setViewMode] = useState('grid');
  const [animationEnabled, setAnimationEnabled] = useState(true);
  const [mitreMatrix, setMitreMatrix] = useState(null);
  const [techniqueDetails, setTechniqueDetails] = useState({});
  
  // Incident management states
  const [showIncidentModal, setShowIncidentModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingIncident, setEditingIncident] = useState(null);
  const [deletingIncidentId, setDeletingIncidentId] = useState(null);

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
        fetchTopThreats(),
        fetchMitreTactics(),
        fetchMitreMatrix(),
        fetchThreatIntelligence(),
        fetchLiveIOCAlerts(),
        fetchIOCCorrelation()
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
      const wsUrl = `ws://${window.location.hostname}:8000/ws/soc/?token=${token}`;
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
      default:
        console.log('Unknown WebSocket message type:', data.type);
    }
  };

  const setupRealTimeRefresh = () => {
    // Refresh data every 2 minutes to reduce server load
    intervalRef.current = setInterval(() => {
      fetchDashboardData();
    }, 120000);
  };

  const fetchDashboardData = async () => {
    try {
      const response = await api.getSOCDashboard();
      if (response?.success && response?.data) {
        setDashboardData(response.data);
        setError(null);
      }
    } catch (err) {
      setError('Failed to load SOC dashboard data');
      console.error('SOC Dashboard Error:', err);
    }
  };



  const fetchMitreMatrix = async () => {
    try {
      const response = await api.getMitreMatrix();
      if (response) {
        setMitreMatrix(response);
      }
    } catch (err) {
      console.error('Failed to fetch MITRE matrix:', err);
    }
  };

  const fetchTechniqueDetails = async (techniqueId) => {
    if (techniqueDetails[techniqueId]) return techniqueDetails[techniqueId];
    
    try {
      const details = await api.getTechniqueDetails(techniqueId);
      setTechniqueDetails(prev => ({ ...prev, [techniqueId]: details }));
      return details;
    } catch (err) {
      console.warn('Failed to fetch technique details:', err);
      return null;
    }
  };

  const handleTechniqueClick = async (technique) => {
    setSelectedTechnique(technique);
    setShowTechniqueModal(true);
    await fetchTechniqueDetails(technique.technique_id);
  };

  const getTacticColor = (tactic, intensity = 1) => {
    const colors = {
      'initial-access': `rgba(255, 107, 107, ${intensity})`,
      'execution': `rgba(78, 205, 196, ${intensity})`,
      'persistence': `rgba(69, 183, 209, ${intensity})`,
      'privilege-escalation': `rgba(150, 206, 180, ${intensity})`,
      'defense-evasion': `rgba(254, 202, 87, ${intensity})`,
      'credential-access': `rgba(255, 159, 243, ${intensity})`,
      'discovery': `rgba(84, 160, 255, ${intensity})`,
      'lateral-movement': `rgba(95, 39, 205, ${intensity})`,
      'collection': `rgba(0, 210, 211, ${intensity})`,
      'command-and-control': `rgba(255, 159, 67, ${intensity})`,
      'exfiltration': `rgba(238, 90, 36, ${intensity})`,
      'impact': `rgba(234, 32, 39, ${intensity})`,
      'unknown': `rgba(108, 117, 125, ${intensity})`
    };
    return colors[tactic?.toLowerCase()] || colors['unknown'];
  };

  const getFilteredTactics = () => {
    if (!mitreTactics || mitreTactics.length === 0) return [];
    
    let filtered = [...mitreTactics];
    
    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(tactic => 
        tactic.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tactic.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    // Severity filter
    if (filterBySeverity !== 'all') {
      const thresholds = { high: 5, medium: 3, low: 1 };
      const threshold = thresholds[filterBySeverity];
      filtered = filtered.filter(tactic => (tactic.detection_count || 0) >= threshold);
    }
    
    // Sort
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'detection_count': return (b.detection_count || 0) - (a.detection_count || 0);
        case 'name': return a.name?.localeCompare(b.name) || 0;
        case 'technique_count': return (b.technique_count || 0) - (a.technique_count || 0);
        default: return 0;
      }
    });
    
    return filtered;
  };

  const fetchTopThreats = async () => {
    try {
      const response = await api.getSOCTopThreats();
      if (response?.success && response?.threats) {
        setTopThreats(response.threats);
      }
    } catch (err) {
      console.error('Failed to fetch top threats:', err);
    }
  };

  const fetchMitreTactics = async () => {
    try {
      const response = await api.getSOCMitreTactics();
      if (response?.success && response?.tactics) {
        setMitreTactics(response.tactics);
      }
    } catch (err) {
      console.error('Failed to fetch MITRE tactics:', err);
    }
  };

  const fetchThreatIntelligence = async () => {
    try {
      const response = await api.getSOCThreatIntelligence();
      if (response?.success && response?.data) {
        setThreatIntelligence(response.data);
      }
    } catch (err) {
      console.error('Failed to fetch threat intelligence:', err);
    }
  };

  const fetchLiveIOCAlerts = async () => {
    try {
      const response = await api.getLiveIOCAlerts();
      if (response?.success && response?.data) {
        setLiveIOCAlerts(response.data.live_alerts || []);
      }
    } catch (err) {
      console.error('Failed to fetch live IOC alerts:', err);
    }
  };

  const fetchIOCCorrelation = async () => {
    try {
      const response = await api.getIOCIncidentCorrelation();
      if (response?.success && response?.data) {
        setIOCCorrelation(response.data);
      }
    } catch (err) {
      console.error('Failed to fetch IOC correlation data:', err);
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

  const handleDeleteIncident = async (incidentId) => {
    if (!window.confirm('Are you sure you want to delete this incident? This action cannot be undone.')) {
      return;
    }

    setDeletingIncidentId(incidentId);
    try {
      await api.deleteSOCIncident(incidentId);
      showSuccess('Incident deleted successfully');
      
      // Refresh dashboard data
      await fetchDashboardData();
    } catch (err) {
      console.error('Error deleting incident:', err);
      showError('Failed to delete incident: ' + err.message);
    } finally {
      setDeletingIncidentId(null);
    }
  };

  const handleIncidentCreated = async (newIncident) => {
    showSuccess(`Incident created successfully! ID: ${newIncident?.incident_id || 'N/A'}`);
    
    // Refresh dashboard data to show the new incident
    await fetchDashboardData();
  };

  const handleEditIncident = (incident) => {
    setEditingIncident(incident);
    setShowEditModal(true);
  };

  const handleIncidentUpdated = async (updatedIncident) => {
    showSuccess(`Incident updated successfully! ID: ${updatedIncident?.incident_id || 'N/A'}`);
    
    // Refresh dashboard data to show the updated incident
    await fetchDashboardData();
    setShowEditModal(false);
    setEditingIncident(null);
  };

  // Check if component is active and user has access
  if (!active) return null;

  // Check if user is BlueVisionAdmin
  const currentUser = api.getCurrentUser();
  if (!currentUser || currentUser.role !== 'BlueVisionAdmin') {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <div style={{
          backgroundColor: '#fff3cd',
          color: '#856404',
          border: '1px solid #ffeaa7',
          borderRadius: '4px',
          padding: '1rem',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <i className="fas fa-lock" style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}></i>
          <strong>Access Restricted</strong>
          <p style={{ margin: '0.5rem 0 0 0' }}>SOC features are only available to BlueVision administrators.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div style={{ 
        padding: '2rem', 
        textAlign: 'center',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '1rem'
      }}>
        <div style={{
          width: '40px',
          height: '40px',
          border: '4px solid #f3f3f3',
          borderTop: '4px solid #007bff',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }}></div>
        <span style={{ color: '#666', fontSize: '1rem' }}>Loading SOC Dashboard...</span>
        <style>
          {`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `}
        </style>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '2rem' }}>
        <div style={{
          backgroundColor: '#f8d7da',
          color: '#721c24',
          border: '1px solid #f5c6cb',
          borderRadius: '4px',
          padding: '1rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '1rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <i className="fas fa-exclamation-triangle"></i>
            <span>{error}</span>
          </div>
          <button 
            onClick={fetchDashboardData}
            style={{
              backgroundColor: 'transparent',
              color: '#dc3545',
              border: '1px solid #dc3545',
              borderRadius: '4px',
              padding: '0.375rem 0.75rem',
              fontSize: '0.875rem',
              cursor: 'pointer',
              fontWeight: '500'
            }}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <p style={{ color: '#666', fontSize: '1rem' }}>No SOC data available</p>
      </div>
    );
  }

  const { metrics = {}, breakdowns = { status: {}, priority: {} }, recent_incidents = [] } = dashboardData || {};

  const renderTabNavigation = () => (
    <div style={{ marginBottom: '2rem' }}>
      <div style={{ 
        display: 'flex', 
        gap: '0.5rem', 
        borderBottom: '2px solid #dee2e6',
        flexWrap: 'wrap'
      }}>
        {[
          { key: 'overview', label: 'Overview', icon: 'fa-chart-line' },
          { key: 'threats', label: 'Threat Intelligence', icon: 'fa-shield-virus' },
          { key: 'ioc-alerts', label: 'IOC Alerts', icon: 'fa-exclamation-triangle' },
          { key: 'mitre', label: 'MITRE ATT&CK', icon: 'fa-crosshairs' },
          { key: 'behavior', label: 'Behavior Analytics', icon: 'fa-brain' },
          { key: 'alerts', label: 'Live Alerts', icon: 'fa-bell' }
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            style={{
              padding: '0.75rem 1.5rem',
              border: 'none',
              background: activeTab === tab.key ? '#007bff' : 'white',
              color: activeTab === tab.key ? 'white' : '#666',
              fontWeight: '500',
              borderRadius: '8px 8px 0 0',
              cursor: 'pointer',
              fontSize: '0.875rem',
              transition: 'all 0.3s ease',
              borderBottom: activeTab === tab.key ? '2px solid #007bff' : '2px solid transparent',
              marginBottom: '-2px'
            }}
            onMouseEnter={(e) => {
              if (activeTab !== tab.key) {
                e.target.style.backgroundColor = '#f8f9fa';
                e.target.style.color = '#007bff';
              }
            }}
            onMouseLeave={(e) => {
              if (activeTab !== tab.key) {
                e.target.style.backgroundColor = 'white';
                e.target.style.color = '#666';
              }
            }}
          >
            <i className={`fas ${tab.icon}`} style={{ marginRight: '0.5rem' }}></i>
            {tab.label}
          </button>
        ))}
      </div>
    </div>
  );


  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif', position: 'relative' }}>
      {/* Page Header */}
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ marginBottom: '0.5rem', color: '#333', fontSize: '2rem', fontWeight: '600' }}>
          <i className="fas fa-shield-alt" style={{ color: '#007bff', marginRight: '0.5rem' }}></i>
          Security Operations Center
        </h1>
        <p style={{ color: '#666', fontSize: '1rem', margin: '0' }}>Real-time security monitoring and incident management</p>
      </div>

      {/* Action Bar */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        marginBottom: '2rem',
        flexWrap: 'wrap',
        gap: '1rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ fontSize: '0.875rem', color: '#666' }}>
            <i className="fas fa-sync-alt" style={{ marginRight: '0.5rem' }}></i>
            Last updated: {new Date(dashboardData?.last_updated || Date.now()).toLocaleTimeString()}
          </div>
        </div>
        <button
          onClick={initializeSOCDashboard}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '0.875rem',
            fontWeight: '500',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}
        >
          <i className="fas fa-sync-alt"></i>
          Refresh
        </button>
      </div>

      {renderTabNavigation()}

      {/* Tab Content Container */}
      <div>
        {activeTab === 'overview' && (
        <>
          {/* Critical Alerts Banner */}
          {criticalAlerts.length > 0 && (
            <div style={{ 
              backgroundColor: '#f8d7da', 
              color: '#721c24', 
              border: '1px solid #f5c6cb', 
              borderLeft: '5px solid #dc3545',
              borderRadius: '4px',
              padding: '1rem',
              marginBottom: '2rem'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div>
                  <i className="fas fa-exclamation-triangle" style={{ fontSize: '2rem', color: '#dc3545' }}></i>
                </div>
                <div style={{ flex: '1' }}>
                  <h5 style={{ margin: '0 0 0.5rem 0', fontWeight: '600', color: '#721c24' }}>Critical Security Alerts</h5>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '0.5rem' }}>
                    {criticalAlerts.slice(0, 2).map((alert, index) => (
                      <div key={index} style={{ marginBottom: '0.5rem' }}>
                        <strong style={{ color: '#721c24' }}>{alert.title}</strong>
                        <div style={{ fontSize: '0.875rem', color: '#856404' }}>{alert.description}</div>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <button 
                    onClick={() => setActiveTab('alerts')}
                    style={{
                      backgroundColor: 'transparent',
                      color: '#dc3545',
                      border: '1px solid #dc3545',
                      borderRadius: '4px',
                      padding: '0.375rem 0.75rem',
                      fontSize: '0.875rem',
                      cursor: 'pointer',
                      fontWeight: '500'
                    }}
                  >
                    View All Alerts
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Key Metrics Cards */}
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
              textAlign: 'center',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>
                <i className="fas fa-exclamation-circle"></i>
              </div>
              <div style={{ fontSize: '2.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>{metrics.open_incidents || 0}</div>
              <div style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>Open Incidents</div>
              <div style={{ fontSize: '0.875rem', opacity: '0.9' }}>
                <i className="fas fa-arrow-up" style={{ marginRight: '0.25rem' }}></i>
                +{metrics.incidents_today || 0} today
              </div>
            </div>
            
            <div style={{
              background: '#007bff',
              color: 'white',
              padding: '1.5rem',
              borderRadius: '8px',
              textAlign: 'center',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>
                <i className="fas fa-fire"></i>
              </div>
              <div style={{ fontSize: '2.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>{metrics.critical_incidents || 0}</div>
              <div style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>Critical</div>
              <div style={{ fontSize: '0.875rem', opacity: '0.9' }}>
                <i className="fas fa-clock" style={{ marginRight: '0.25rem' }}></i>
                Immediate attention
              </div>
            </div>
            
            <div style={{
              background: '#007bff',
              color: 'white',
              padding: '1.5rem',
              borderRadius: '8px',
              textAlign: 'center',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>
                <i className="fas fa-clock"></i>
              </div>
              <div style={{ fontSize: '2.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>{metrics.overdue_incidents || 0}</div>
              <div style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>Overdue</div>
              <div style={{ fontSize: '0.875rem', opacity: '0.9' }}>
                <i className="fas fa-exclamation-triangle" style={{ marginRight: '0.25rem' }}></i>
                SLA breached
              </div>
            </div>
            
            <div style={{
              background: '#007bff',
              color: 'white',
              padding: '1.5rem',
              borderRadius: '8px',
              textAlign: 'center',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>
                <i className="fas fa-check-circle"></i>
              </div>
              <div style={{ fontSize: '2.5rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>{metrics.resolved_today || 0}</div>
              <div style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>Resolved Today</div>
              <div style={{ fontSize: '0.875rem', opacity: '0.9' }}>
                <i className="fas fa-arrow-up" style={{ marginRight: '0.25rem' }}></i>
                +{metrics.resolved_week || 0} this week
              </div>
            </div>
          </div>
          {/* Activity Metrics */}
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
            gap: '1.5rem', 
            marginBottom: '2rem' 
          }}>
            <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
              <div style={{ 
                background: '#007bff', 
                color: 'white', 
                padding: '1rem' 
              }}>
                <h3 style={{ margin: '0', fontSize: '1.125rem', fontWeight: '600' }}>
                  <i className="fas fa-chart-line" style={{ marginRight: '0.5rem' }}></i>
                  Activity Metrics
                </h3>
              </div>
              <div style={{ padding: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.75rem', backgroundColor: '#007bff', borderRadius: '4px', marginBottom: '1rem' }}>
                  <span style={{ color: 'white' }}>Today:</span>
                  <strong style={{ color: 'white' }}>{metrics.incidents_today || 0} created</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.75rem', marginBottom: '1rem' }}>
                  <span style={{ color: 'white' }}>This Week:</span>
                  <strong style={{ color: 'white' }}>{metrics.incidents_week || 0} created</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.75rem', backgroundColor: '#007bff', borderRadius: '4px', marginBottom: '1rem' }}>
                  <span style={{ color: 'white' }}>This Month:</span>
                  <strong style={{ color: 'white' }}>{metrics.incidents_month || 0} created</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.75rem', backgroundColor: '#007bff', borderRadius: '4px', marginBottom: '1rem' }}>
                  <span style={{ color: 'white' }}>Resolved This Week:</span>
                  <strong style={{ color: 'white' }}>{metrics.resolved_week || 0}</strong>
                </div>
                <div style={{ paddingTop: '1rem', borderTop: '1px solid #dee2e6' }}>
                  <div style={{ fontSize: '0.875rem', textAlign: 'center', color: '#666' }}>
                    Resolution Rate: {(metrics.resolved_week || 0) && (metrics.incidents_week || 0) ? 
                      Math.round(((metrics.resolved_week || 0) / (metrics.incidents_week || 0)) * 100) : 0}%
                  </div>
                </div>
                </div>
              </div>
            </div>

          {/* Status and Priority Breakdown */}
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', 
            gap: '1.5rem', 
            marginBottom: '2rem' 
          }}>
            {/* Status Breakdown */}
            <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
              <div style={{ 
                background: 'linear-gradient(90deg, #a8edea 0%, #fed6e3 100%)', 
                color: '#495057', 
                padding: '1rem' 
              }}>
                <h3 style={{ margin: '0', fontSize: '1.125rem', fontWeight: '600' }}>
                  <i className="fas fa-pie-chart" style={{ marginRight: '0.5rem' }}></i>
                  Status Distribution
                </h3>
              </div>
              <div style={{ padding: '1.5rem' }}>
                {Object.entries(breakdowns.status).map(([status, count]) => {
                  const total = Object.values(breakdowns.status).reduce((a, b) => a + b, 0);
                  const percentage = total > 0 ? Math.round((count / total) * 100) : 0;
                  return (
                    <div key={status} style={{ marginBottom: '1rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                        <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <span style={{ 
                            backgroundColor: getStatusColor(status), 
                            color: 'white',
                            padding: '0.25rem 0.75rem',
                            fontSize: '0.75rem',
                            fontWeight: '600',
                            textTransform: 'uppercase',
                            borderRadius: '12px',
                            minWidth: '80px',
                            textAlign: 'center'
                          }}>
                            {status.replace('_', ' ')}
                          </span>
                          <span style={{ fontSize: '0.875rem', color: '#666' }}>{percentage}%</span>
                        </span>
                        <strong style={{ color: getStatusColor(status), fontSize: '1.125rem' }}>{count}</strong>
                      </div>
                      <div style={{ 
                        height: '6px', 
                        backgroundColor: '#007bff', 
                        borderRadius: '3px', 
                        overflow: 'hidden' 
                      }}>
                        <div style={{ 
                          width: `${percentage}%`, 
                          height: '100%',
                          backgroundColor: getStatusColor(status),
                          transition: 'width 0.6s ease',
                          borderRadius: '3px'
                        }}></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Priority Breakdown */}
            <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
              <div style={{ 
                background: 'linear-gradient(90deg, #fdbb2d 0%, #22c1c3 100%)', 
                color: 'white', 
                padding: '1rem' 
              }}>
                <h3 style={{ margin: '0', fontSize: '1.125rem', fontWeight: '600' }}>
                  <i className="fas fa-exclamation-triangle" style={{ marginRight: '0.5rem' }}></i>
                  Risk Priority Matrix
                </h3>
              </div>
              <div style={{ padding: '1.5rem' }}>
                {Object.entries(breakdowns.priority).map(([priority, count]) => {
                  const total = Object.values(breakdowns.priority).reduce((a, b) => a + b, 0);
                  const percentage = total > 0 ? Math.round((count / total) * 100) : 0;
                  const riskLevel = priority === 'critical' ? 'EXTREME' : 
                                    priority === 'high' ? 'HIGH' : 
                                    priority === 'medium' ? 'MODERATE' : 'LOW';
                  return (
                    <div key={priority} style={{ marginBottom: '1rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                        <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <span style={{ 
                            backgroundColor: getPriorityColor(priority), 
                            color: 'white',
                            padding: '0.25rem 0.75rem',
                            fontSize: '0.75rem',
                            fontWeight: '600',
                            textTransform: 'uppercase',
                            borderRadius: '12px',
                            minWidth: '80px',
                            textAlign: 'center'
                          }}>
                            {priority}
                          </span>
                          <span style={{ fontSize: '0.875rem', color: '#666' }}>{riskLevel}</span>
                        </span>
                        <div style={{ textAlign: 'right' }}>
                          <strong style={{ color: getPriorityColor(priority), fontSize: '1.125rem' }}>{count}</strong>
                          <div style={{ fontSize: '0.875rem', color: 'white' }}>{percentage}%</div>
                        </div>
                      </div>
                      <div style={{ 
                        height: '8px', 
                        backgroundColor: '#007bff', 
                        borderRadius: '4px', 
                        overflow: 'hidden' 
                      }}>
                        <div style={{ 
                          width: `${percentage}%`, 
                          height: '100%',
                          backgroundColor: getPriorityColor(priority),
                          transition: 'width 0.6s ease',
                          borderRadius: '4px'
                        }}></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </>
      )}

      {/* Tab Content */}
      {activeTab === 'threats' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
          {/* Enhanced Threat Intelligence Summary */}
          <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
            <div style={{ 
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
              color: 'white', 
              padding: '1rem', 
              borderBottom: '1px solid #dee2e6' 
            }}>
              <h3 style={{ margin: '0', fontSize: '1.125rem', fontWeight: '600' }}>
                <i className="fas fa-globe" style={{ marginRight: '0.5rem' }}></i>
                IOC Threat Intelligence
              </h3>
            </div>
            <div style={{ padding: '1.5rem' }}>
              {threatIntelligence ? (
                <>
                  {/* Enhanced Metrics Grid */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
                    <div style={{ textAlign: 'center', padding: '1rem', backgroundColor: '#007bff', borderRadius: '6px' }}>
                      <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'white', marginBottom: '0.5rem' }}>
                        {threatIntelligence.iocs_count || 0}
                      </div>
                      <div style={{ fontSize: '0.875rem', color: 'white' }}>Total IOCs</div>
                    </div>
                    <div style={{ textAlign: 'center', padding: '1rem', backgroundColor: '#007bff', borderRadius: '6px' }}>
                      <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'white', marginBottom: '0.5rem' }}>
                        {threatIntelligence.high_confidence_iocs || 0}
                      </div>
                      <div style={{ fontSize: '0.875rem', color: 'white' }}>High Confidence</div>
                    </div>
                    <div style={{ textAlign: 'center', padding: '1rem', backgroundColor: '#007bff', borderRadius: '6px' }}>
                      <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'white', marginBottom: '0.5rem' }}>
                        {threatIntelligence.feeds_active || 0}
                      </div>
                      <div style={{ fontSize: '0.875rem', color: 'white' }}>Active Feeds</div>
                    </div>
                    <div style={{ textAlign: 'center', padding: '1rem', backgroundColor: '#007bff', borderRadius: '6px' }}>
                      <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'white', marginBottom: '0.5rem' }}>
                        {threatIntelligence.recent_iocs_24h || 0}
                      </div>
                      <div style={{ fontSize: '0.875rem', color: 'white' }}>Last 24h</div>
                    </div>
                  </div>

                  {/* IOC Trend Analysis */}
                  {threatIntelligence.ioc_trend && (
                    <div style={{ marginBottom: '1.5rem', padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '6px' }}>
                      <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '1rem', fontWeight: '600' }}>IOC Trends</h4>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <span style={{
                          backgroundColor: threatIntelligence.ioc_trend.direction === 'increasing' ? '#dc3545' : 
                                         threatIntelligence.ioc_trend.direction === 'decreasing' ? '#28a745' : '#6c757d',
                          color: 'white',
                          padding: '0.25rem 0.75rem',
                          borderRadius: '12px',
                          fontSize: '0.75rem',
                          fontWeight: '600',
                          textTransform: 'capitalize'
                        }}>
                          {threatIntelligence.ioc_trend.direction}
                        </span>
                        <span style={{ fontSize: '0.875rem' }}>
                          {threatIntelligence.ioc_trend.change_percentage > 0 ? '+' : ''}{threatIntelligence.ioc_trend.change_percentage}%
                        </span>
                      </div>
                    </div>
                  )}

                  {/* IOC Types Breakdown */}
                  {threatIntelligence.ioc_types_breakdown && (
                    <div style={{ marginBottom: '1.5rem' }}>
                      <h4 style={{ margin: '0 0 1rem 0', fontSize: '1rem', fontWeight: '600' }}>IOC Types</h4>
                      {threatIntelligence.ioc_types_breakdown.slice(0, 5).map((type, index) => (
                        <div key={index} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                          <span style={{ fontSize: '0.875rem', textTransform: 'capitalize' }}>{type.type.replace('_', ' ')}</span>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <span style={{ fontSize: '0.875rem', fontWeight: '600' }}>{type.count}</span>
                            <span style={{ fontSize: '0.75rem', color: '#666' }}>({type.percentage}%)</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  <div style={{ borderTop: '1px solid #dee2e6', paddingTop: '1rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <div style={{ fontSize: '0.875rem', color: 'white' }}>Threat Level</div>
                        <span style={{
                          backgroundColor: threatIntelligence.threat_level === 'High' ? '#dc3545' : 
                                         threatIntelligence.threat_level === 'Medium' ? '#ffc107' : '#28a745',
                          color: 'white',
                          padding: '0.25rem 0.75rem',
                          borderRadius: '12px',
                          fontSize: '0.75rem',
                          fontWeight: '600'
                        }}>{threatIntelligence.threat_level}</span>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: '0.875rem', color: 'white' }}>Confidence</div>
                        <span style={{
                          backgroundColor: '#28a745',
                          color: 'white',
                          padding: '0.25rem 0.75rem',
                          borderRadius: '12px',
                          fontSize: '0.75rem',
                          fontWeight: '600'
                        }}>{threatIntelligence.confidence}</span>
                      </div>
                    </div>
                  </div>
                </>
              ) : (
                <div style={{ textAlign: 'center', color: '#666', padding: '2rem' }}>
                  <i className="fas fa-satellite-dish" style={{ fontSize: '3rem', marginBottom: '1rem', color: '#dee2e6' }}></i>
                  <p>Loading threat intelligence...</p>
                </div>
              )}
            </div>
          </div>

          {/* Recent Critical IOCs */}
          <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
            <div style={{ 
              background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', 
              color: 'white', 
              padding: '1rem', 
              borderBottom: '1px solid #dee2e6' 
            }}>
              <h3 style={{ margin: '0', fontSize: '1.125rem', fontWeight: '600' }}>
                <i className="fas fa-exclamation-triangle" style={{ marginRight: '0.5rem' }}></i>
                Recent Critical IOCs
              </h3>
            </div>
            <div style={{ padding: '1.5rem' }}>
              {threatIntelligence && threatIntelligence.recent_critical_iocs && threatIntelligence.recent_critical_iocs.length > 0 ? (
                <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                  {threatIntelligence.recent_critical_iocs.map((ioc, index) => (
                    <div key={index} style={{ 
                      padding: '1rem', 
                      backgroundColor: '#007bff', 
                      borderRadius: '6px', 
                      marginBottom: '1rem',
                      border: '1px solid #e9ecef'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                        <div style={{ flex: 1 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                            <span style={{
                              backgroundColor: '#007bff',
                              color: 'white',
                              padding: '0.125rem 0.5rem',
                              borderRadius: '8px',
                              fontSize: '0.7rem',
                              fontWeight: '600',
                              textTransform: 'uppercase'
                            }}>{ioc.type}</span>
                            <span style={{
                              backgroundColor: ioc.confidence >= 90 ? '#28a745' : ioc.confidence >= 70 ? '#ffc107' : '#dc3545',
                              color: 'white',
                              padding: '0.125rem 0.5rem',
                              borderRadius: '8px',
                              fontSize: '0.7rem',
                              fontWeight: '600'
                            }}>{ioc.confidence}%</span>
                          </div>
                          <div style={{ fontSize: '0.875rem', fontWeight: '600', marginBottom: '0.25rem', wordBreak: 'break-all' }}>
                            {ioc.value}
                          </div>
                          <div style={{ fontSize: '0.75rem', color: 'white' }}>
                            Source: {ioc.source}
                          </div>
                        </div>
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#999' }}>
                        {new Date(ioc.created_at).toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ textAlign: 'center', color: '#666', padding: '2rem' }}>
                  <i className="fas fa-shield-check" style={{ fontSize: '3rem', marginBottom: '1rem', color: '#28a745' }}></i>
                  <p>No critical IOCs detected recently</p>
                </div>
              )}
            </div>
          </div>

          {/* Top Threats */}
          <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
            <div style={{ backgroundColor: '#007bff', padding: '1rem', borderBottom: '1px solid #dee2e6' }}>
              <h3 style={{ margin: '0', fontSize: '1.125rem', fontWeight: '600', color: 'white' }}>
                <i className="fas fa-shield-virus" style={{ marginRight: '0.5rem', color: 'white' }}></i>
                Trending Threats
              </h3>
            </div>
            <div style={{ padding: '1.5rem' }}>
              {threatIntelligence && threatIntelligence.trending_threats ? (
                threatIntelligence.trending_threats.map((threat, index) => (
                  <div key={index} style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center', 
                    padding: '1rem', 
                    backgroundColor: '#007bff', 
                    borderRadius: '6px', 
                    marginBottom: '1rem',
                    border: '1px solid #e9ecef'
                  }}>
                    <div>
                      <div style={{ fontWeight: '600', fontSize: '1rem', marginBottom: '0.25rem' }}>{threat.name}</div>
                      <div style={{ fontSize: '0.875rem', color: 'white' }}>Count: {threat.count}</div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <span style={{
                        backgroundColor: threat.trend === 'increasing' ? '#dc3545' : '#28a745',
                        color: 'white',
                        padding: '0.25rem 0.75rem',
                        borderRadius: '12px',
                        fontSize: '0.75rem',
                        fontWeight: '600',
                        textTransform: 'capitalize'
                      }}>{threat.trend}</span>
                    </div>
                  </div>
                ))
              ) : topThreats.length > 0 ? topThreats.map((threat, index) =>
                <div key={index} style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center', 
                  padding: '1rem', 
                  backgroundColor: '#f8f9fa', 
                  borderRadius: '6px', 
                  marginBottom: '1rem',
                  border: '1px solid #e9ecef'
                }}>
                  <div>
                    <div style={{ fontWeight: '600', fontSize: '1rem', marginBottom: '0.25rem' }}>{threat.name}</div>
                    <div style={{ fontSize: '0.875rem', color: 'white' }}>{threat.category}</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <span style={{
                      backgroundColor: '#dc3545',
                      color: 'white',
                      padding: '0.25rem 0.75rem',
                      borderRadius: '12px',
                      fontSize: '0.75rem',
                      fontWeight: '600'
                    }}>{threat.severity}</span>
                    <div style={{ fontSize: '0.875rem', color: '#666', marginTop: '0.25rem' }}>{threat.incidents} incidents</div>
                  </div>
                </div>
              ) : (
                <div style={{ textAlign: 'center', color: '#666', padding: '2rem' }}>
                  <i className="fas fa-shield-alt" style={{ fontSize: '3rem', marginBottom: '1rem', color: '#dee2e6' }}></i>
                  <p>No threat intelligence data available</p>
                </div>
              )}
            </div>
          </div>

          {/* Feed Status */}
          {threatIntelligence && threatIntelligence.feed_status && (
            <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
              <div style={{ backgroundColor: '#007bff', padding: '1rem', borderBottom: '1px solid #dee2e6' }}>
                <h3 style={{ margin: '0', fontSize: '1.125rem', fontWeight: '600', color: 'white' }}>
                  <i className="fas fa-rss" style={{ marginRight: '0.5rem', color: 'white' }}></i>
                  Threat Feed Status
                </h3>
              </div>
              <div style={{ padding: '1.5rem' }}>
                {threatIntelligence.feed_status.map((feed, index) => (
                  <div key={index} style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center', 
                    padding: '0.75rem', 
                    backgroundColor: '#87ceeb', 
                    borderRadius: '6px', 
                    marginBottom: '0.75rem',
                    border: '1px solid #e9ecef'
                  }}>
                    <div>
                      <div style={{ fontWeight: '600', fontSize: '0.875rem', marginBottom: '0.25rem' }}>{feed.name}</div>
                      <div style={{ fontSize: '0.75rem', color: 'white' }}>
                        {feed.indicator_count} indicators
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <span style={{
                        backgroundColor: feed.status === 'success' ? '#28a745' : 
                                       feed.status === 'processing' ? '#ffc107' : '#dc3545',
                        color: 'white',
                        padding: '0.25rem 0.5rem',
                        borderRadius: '8px',
                        fontSize: '0.7rem',
                        fontWeight: '600',
                        textTransform: 'uppercase'
                      }}>{feed.status}</span>
                      {feed.last_update && (
                        <div style={{ fontSize: '0.7rem', color: '#666', marginTop: '0.25rem' }}>
                          {new Date(feed.last_update).toLocaleDateString()}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'ioc-alerts' && (
        <div style={{ marginBottom: '2rem' }}>
          {/* IOC Alerts Overview */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
            <div style={{
              background: 'linear-gradient(135deg, #dc3545 0%, #fd7e14 100%)',
              color: 'white',
              padding: '1.5rem',
              borderRadius: '8px',
              textAlign: 'center',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>
                <i className="fas fa-exclamation-triangle"></i>
              </div>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
                {liveIOCAlerts.length}
              </div>
              <div style={{ fontSize: '1.1rem' }}>Live IOC Alerts</div>
            </div>
            
            <div style={{
              background: 'linear-gradient(135deg, #ffc107 0%, #fd7e14 100%)',
              color: 'white',
              padding: '1.5rem',
              borderRadius: '8px',
              textAlign: 'center',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>
                <i className="fas fa-link"></i>
              </div>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
                {iocCorrelation?.statistics?.correlation_rate || 0}%
              </div>
              <div style={{ fontSize: '1.1rem' }}>IOC Correlation Rate</div>
            </div>
            
            <div style={{
              background: 'linear-gradient(135deg, #007bff 0%, #6f42c1 100%)',
              color: 'white',
              padding: '1.5rem',
              borderRadius: '8px',
              textAlign: 'center',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>
                <i className="fas fa-project-diagram"></i>
              </div>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
                {iocCorrelation?.statistics?.incidents_with_iocs || 0}
              </div>
              <div style={{ fontSize: '1.1rem' }}>IOC-Linked Incidents</div>
            </div>
          </div>

          {/* Live IOC Alerts */}
          <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', overflow: 'hidden', marginBottom: '2rem' }}>
            <div style={{ 
              background: 'linear-gradient(90deg, #dc3545 0%, #fd7e14 100%)', 
              color: 'white', 
              padding: '1rem', 
              borderBottom: '1px solid #dee2e6' 
            }}>
              <h3 style={{ margin: '0', fontSize: '1.125rem', fontWeight: '600' }}>
                <i className="fas fa-exclamation-triangle" style={{ marginRight: '0.5rem' }}></i>
                Live IOC-Based Alerts
              </h3>
            </div>
            <div style={{ padding: '1.5rem' }}>
              {liveIOCAlerts.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {liveIOCAlerts.map((alert, index) => (
                    <div key={index} style={{ 
                      padding: '1.5rem', 
                      backgroundColor: '#007bff', 
                      borderRadius: '8px', 
                      border: '1px solid #e9ecef',
                      borderLeft: `5px solid ${alert.severity === 'critical' ? '#dc3545' : 
                                                alert.severity === 'high' ? '#fd7e14' : 
                                                alert.severity === 'medium' ? '#ffc107' : '#28a745'}`
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                        <div style={{ flex: 1 }}>
                          <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '1.125rem', fontWeight: '600', color: '#333' }}>
                            {alert.title}
                          </h4>
                          <p style={{ margin: '0 0 1rem 0', color: '#666', fontSize: '0.875rem' }}>
                            {alert.description}
                          </p>
                          
                          {/* Alert Details */}
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1rem' }}>
                            <span style={{
                              backgroundColor: alert.severity === 'critical' ? '#dc3545' : 
                                             alert.severity === 'high' ? '#fd7e14' : 
                                             alert.severity === 'medium' ? '#ffc107' : '#28a745',
                              color: 'white',
                              padding: '0.25rem 0.75rem',
                              borderRadius: '12px',
                              fontSize: '0.75rem',
                              fontWeight: '600',
                              textTransform: 'uppercase'
                            }}>
                              {alert.severity}
                            </span>
                            <span style={{
                              backgroundColor: '#007bff',
                              color: 'white',
                              padding: '0.25rem 0.75rem',
                              borderRadius: '12px',
                              fontSize: '0.75rem',
                              fontWeight: '600'
                            }}>
                              {alert.alert_type}
                            </span>
                            {alert.organization && (
                              <span style={{
                                backgroundColor: '#6c757d',
                                color: 'white',
                                padding: '0.25rem 0.75rem',
                                borderRadius: '12px',
                                fontSize: '0.75rem',
                                fontWeight: '600'
                              }}>
                                {alert.organization}
                              </span>
                            )}
                          </div>
                          
                          {/* Related IOCs */}
                          {alert.related_iocs && alert.related_iocs.length > 0 && (
                            <div style={{ marginBottom: '1rem' }}>
                              <h5 style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem', fontWeight: '600', color: '#495057' }}>
                                Related IOCs:
                              </h5>
                              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                                {alert.related_iocs.map((ioc, iocIndex) => (
                                  <div key={iocIndex} style={{
                                    backgroundColor: 'white',
                                    border: '1px solid #dee2e6',
                                    borderRadius: '6px',
                                    padding: '0.5rem',
                                    fontSize: '0.75rem'
                                  }}>
                                    <div style={{ fontWeight: '600', color: '#007bff', marginBottom: '0.25rem' }}>
                                      {ioc.type.toUpperCase()}
                                    </div>
                                    <div style={{ fontFamily: 'monospace', fontSize: '0.7rem', marginBottom: '0.25rem' }}>
                                      {ioc.value}
                                    </div>
                                    <div style={{ color: '#666' }}>
                                      Confidence: {ioc.confidence}%
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                          
                          {/* Matched Assets */}
                          {alert.matched_assets && alert.matched_assets.length > 0 && (
                            <div style={{ marginBottom: '1rem' }}>
                              <h5 style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem', fontWeight: '600', color: '#495057' }}>
                                Affected Assets:
                              </h5>
                              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                                {alert.matched_assets.map((asset, assetIndex) => (
                                  <span key={assetIndex} style={{
                                    backgroundColor: asset.criticality === 'critical' ? '#dc3545' : 
                                                   asset.criticality === 'high' ? '#fd7e14' : '#28a745',
                                    color: 'white',
                                    padding: '0.25rem 0.75rem',
                                    borderRadius: '12px',
                                    fontSize: '0.75rem',
                                    fontWeight: '600'
                                  }}>
                                    {asset.name} ({asset.type})
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                        
                        <div style={{ textAlign: 'right', marginLeft: '1rem' }}>
                          {alert.is_acknowledged ? (
                            <span style={{
                              backgroundColor: '#28a745',
                              color: 'white',
                              padding: '0.5rem 1rem',
                              borderRadius: '6px',
                              fontSize: '0.875rem',
                              fontWeight: '600'
                            }}>
                              <i className="fas fa-check" style={{ marginRight: '0.5rem' }}></i>
                              Acknowledged
                            </span>
                          ) : (
                            <button style={{
                              backgroundColor: '#ffc107',
                              color: '#212529',
                              border: 'none',
                              padding: '0.5rem 1rem',
                              borderRadius: '6px',
                              fontSize: '0.875rem',
                              fontWeight: '600',
                              cursor: 'pointer'
                            }}>
                              <i className="fas fa-eye" style={{ marginRight: '0.5rem' }}></i>
                              Acknowledge
                            </button>
                          )}
                        </div>
                      </div>
                      
                      <div style={{ fontSize: '0.75rem', color: '#999', borderTop: '1px solid #dee2e6', paddingTop: '0.5rem' }}>
                        Created: {new Date(alert.created_at).toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ textAlign: 'center', color: '#666', padding: '3rem' }}>
                  <i className="fas fa-shield-check" style={{ fontSize: '4rem', marginBottom: '1rem', color: '#28a745' }}></i>
                  <h4 style={{ margin: '0 0 0.5rem 0', color: '#28a745' }}>No Active IOC Alerts</h4>
                  <p style={{ margin: '0' }}>All IOC monitoring systems are clear</p>
                </div>
              )}
            </div>
          </div>

          {/* IOC-Incident Correlation */}
          {iocCorrelation && (
            <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
              <div style={{ 
                background: 'linear-gradient(90deg, #6f42c1 0%, #007bff 100%)', 
                color: 'white', 
                padding: '1rem', 
                borderBottom: '1px solid #dee2e6' 
              }}>
                <h3 style={{ margin: '0', fontSize: '1.125rem', fontWeight: '600' }}>
                  <i className="fas fa-project-diagram" style={{ marginRight: '0.5rem' }}></i>
                  IOC-Incident Correlation Analysis
                </h3>
              </div>
              <div style={{ padding: '1.5rem' }}>
                {/* Correlation Statistics */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
                  <div style={{ textAlign: 'center', padding: '1rem', backgroundColor: '#007bff', borderRadius: '6px' }}>
                    <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'white', marginBottom: '0.5rem' }}>
                      {iocCorrelation.statistics.total_incidents}
                    </div>
                    <div style={{ fontSize: '0.875rem', color: 'white' }}>Total Incidents</div>
                  </div>
                  <div style={{ textAlign: 'center', padding: '1rem', backgroundColor: '#007bff', borderRadius: '6px' }}>
                    <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'white', marginBottom: '0.5rem' }}>
                      {iocCorrelation.statistics.incidents_with_iocs}
                    </div>
                    <div style={{ fontSize: '0.875rem', color: 'white' }}>With IOCs</div>
                  </div>
                  <div style={{ textAlign: 'center', padding: '1rem', backgroundColor: '#007bff', borderRadius: '6px' }}>
                    <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'white', marginBottom: '0.5rem' }}>
                      {iocCorrelation.statistics.correlation_rate}%
                    </div>
                    <div style={{ fontSize: '0.875rem', color: 'white' }}>Correlation Rate</div>
                  </div>
                </div>

                {/* Top IOC Types */}
                {iocCorrelation.statistics.top_ioc_types && (
                  <div style={{ marginBottom: '2rem' }}>
                    <h4 style={{ margin: '0 0 1rem 0', fontSize: '1rem', fontWeight: '600' }}>Top IOC Types in Incidents</h4>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                      {iocCorrelation.statistics.top_ioc_types.map((type, index) => (
                        <div key={index} style={{ 
                          padding: '1rem', 
                          backgroundColor: '#007bff', 
                          borderRadius: '6px', 
                          border: '1px solid #e9ecef' 
                        }}>
                          <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'white', marginBottom: '0.5rem' }}>
                            {type.count}
                          </div>
                          <div style={{ fontSize: '0.875rem', fontWeight: '600', marginBottom: '0.25rem', textTransform: 'capitalize', color: 'white' }}>
                            {type.type.replace('_', ' ')}
                          </div>
                          <div style={{ fontSize: '0.75rem', color: 'white' }}>
                            {type.incidents_affected} incidents affected
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}


      {activeTab === 'mitre' && (
        <div style={{ marginBottom: '2rem' }}>
          {/* Interactive Controls */}
          <div style={{ 
            backgroundColor: 'white', 
            borderRadius: '8px', 
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)', 
            overflow: 'hidden',
            marginBottom: '1.5rem'
          }}>
            <div style={{ 
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
              color: 'white', 
              padding: '1rem' 
            }}>
              <h3 style={{ margin: '0', fontSize: '1.125rem', fontWeight: '600' }}>
                <i className="fas fa-crosshairs" style={{ marginRight: '0.5rem' }}></i>
                Interactive MITRE ATT&CK Analysis
              </h3>
            </div>
            <div style={{ padding: '1.5rem' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {/* Search Box */}
                <div style={{ position: 'relative', maxWidth: '400px' }}>
                  <i className="fas fa-search" style={{
                    position: 'absolute',
                    left: '12px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    color: '#6c757d',
                    zIndex: 1
                  }}></i>
                  <input
                    type="text"
                    placeholder="Search tactics or techniques..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '12px 40px 12px 40px',
                      border: '2px solid #dee2e6',
                      borderRadius: '25px',
                      fontSize: '14px',
                      transition: 'all 0.2s ease'
                    }}
                    onFocus={(e) => {
                      e.target.style.borderColor = '#007bff';
                      e.target.style.boxShadow = '0 0 0 3px rgba(0, 123, 255, 0.1)';
                    }}
                    onBlur={(e) => {
                      e.target.style.borderColor = '#dee2e6';
                      e.target.style.boxShadow = 'none';
                    }}
                  />
                  {searchTerm && (
                    <button 
                      onClick={() => setSearchTerm('')}
                      style={{
                        position: 'absolute',
                        right: '12px',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        background: 'none',
                        border: 'none',
                        color: '#6c757d',
                        cursor: 'pointer',
                        padding: '4px',
                        borderRadius: '50%',
                        transition: 'all 0.2s ease'
                      }}
                      onMouseEnter={(e) => {
                        e.target.style.background = '#e9ecef';
                        e.target.style.color = '#495057';
                      }}
                      onMouseLeave={(e) => {
                        e.target.style.background = 'none';
                        e.target.style.color = '#6c757d';
                      }}
                    >
                      <i className="fas fa-times"></i>
                    </button>
                  )}
                </div>

                {/* Filter Controls */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', alignItems: 'center' }}>
                  <select 
                    value={filterBySeverity} 
                    onChange={(e) => setFilterBySeverity(e.target.value)}
                    style={{
                      padding: '8px 12px',
                      border: '1px solid #dee2e6',
                      borderRadius: '6px',
                      background: 'white',
                      cursor: 'pointer',
                      fontSize: '14px'
                    }}
                  >
                    <option value="all">All Detection Levels</option>
                    <option value="high">High (5+ detections)</option>
                    <option value="medium">Medium (3+ detections)</option>
                    <option value="low">Low (1+ detections)</option>
                  </select>
                  
                  <select 
                    value={sortBy} 
                    onChange={(e) => setSortBy(e.target.value)}
                    style={{
                      padding: '8px 12px',
                      border: '1px solid #dee2e6',
                      borderRadius: '6px',
                      background: 'white',
                      cursor: 'pointer',
                      fontSize: '14px'
                    }}
                  >
                    <option value="detection_count">Sort by Detections</option>
                    <option value="name">Sort by Name</option>
                    <option value="technique_count">Sort by Techniques</option>
                  </select>
                  
                  <div style={{ display: 'flex', border: '1px solid #dee2e6', borderRadius: '6px', overflow: 'hidden' }}>
                    <button 
                      onClick={() => setViewMode('grid')}
                      style={{
                        padding: '8px 12px',
                        border: 'none',
                        background: viewMode === 'grid' ? '#007bff' : 'white',
                        color: viewMode === 'grid' ? 'white' : '#666',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease'
                      }}
                      title="Grid View"
                    >
                      <i className="fas fa-th"></i>
                    </button>
                    <button 
                      onClick={() => setViewMode('list')}
                      style={{
                        padding: '8px 12px',
                        border: 'none',
                        background: viewMode === 'list' ? '#007bff' : 'white',
                        color: viewMode === 'list' ? 'white' : '#666',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease'
                      }}
                      title="List View"
                    >
                      <i className="fas fa-list"></i>
                    </button>
                  </div>

                  <button 
                    onClick={() => setAnimationEnabled(!animationEnabled)}
                    style={{
                      padding: '8px 12px',
                      border: '1px solid #dee2e6',
                      borderRadius: '6px',
                      background: animationEnabled ? '#007bff' : 'white',
                      color: animationEnabled ? 'white' : '#666',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease'
                    }}
                    title="Toggle Animations"
                  >
                    <i className="fas fa-magic"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Interactive MITRE Matrix */}
          <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
            <div style={{ 
              background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', 
              color: 'white', 
              padding: '1rem', 
              borderBottom: '1px solid #dee2e6' 
            }}>
              <h3 style={{ margin: '0', fontSize: '1.125rem', fontWeight: '600' }}>
                <i className="fas fa-shield-alt" style={{ marginRight: '0.5rem' }}></i>
                MITRE ATT&CK Tactics Matrix ({getFilteredTactics().length} tactics)
              </h3>
            </div>
            <div style={{ padding: '1.5rem' }}>
              {getFilteredTactics().length > 0 ? (
                <div style={{ 
                  display: 'grid', 
                  gridTemplateColumns: viewMode === 'grid' ? 'repeat(auto-fit, minmax(320px, 1fr))' : '1fr',
                  gap: '1.5rem' 
                }}>
                  {getFilteredTactics().map((tactic, index) => (
                    <div 
                      key={index} 
                      onClick={() => setSelectedTactic(selectedTactic === tactic.name ? null : tactic.name)}
                      onMouseEnter={() => setHoveredTactic(tactic.name)}
                      onMouseLeave={() => setHoveredTactic(null)}
                      style={{ 
                        border: '2px solid #dee2e6',
                        borderRadius: '12px', 
                        padding: '1.5rem',
                        backgroundColor: 'white',
                        boxShadow: hoveredTactic === tactic.name ? '0 8px 25px rgba(0, 123, 255, 0.2)' : '0 2px 8px rgba(0,0,0,0.1)',
                        cursor: 'pointer',
                        transition: 'all 0.3s ease',
                        transform: hoveredTactic === tactic.name && animationEnabled ? 'translateY(-5px)' : 'translateY(0)',
                        borderColor: selectedTactic === tactic.name ? '#007bff' : '#dee2e6'
                      }}
                    >
                      <div style={{ 
                        background: `linear-gradient(135deg, ${getTacticColor(tactic.name, 0.8)}, ${getTacticColor(tactic.name, 1)})`,
                        padding: '1rem',
                        borderRadius: '8px',
                        marginBottom: '1rem',
                        color: 'white'
                      }}>
                        <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '1.125rem', fontWeight: '600' }}>
                          {tactic.name}
                        </h4>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontSize: '0.875rem', opacity: '0.9' }}>
                            {tactic.technique_count || 0} techniques
                          </span>
                          <span style={{ fontSize: '0.875rem', opacity: '0.9' }}>
                            {tactic.detection_count || 0} detected
                          </span>
                        </div>
                      </div>
                      
                      <p style={{ 
                        fontSize: '0.875rem', 
                        color: '#666', 
                        marginBottom: '1rem', 
                        lineHeight: '1.4',
                        display: '-webkit-box',
                        WebkitLineClamp: selectedTactic === tactic.name ? 'none' : 3,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden'
                      }}>
                        {tactic.description}
                      </p>
                      
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '0.5rem' }}>
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                          <span style={{
                            backgroundColor: '#007bff',
                            color: 'white',
                            padding: '0.25rem 0.75rem',
                            borderRadius: '12px',
                            fontSize: '0.75rem',
                            fontWeight: '600'
                          }}>
                            {tactic.technique_count || 0} techniques
                          </span>
                          <span style={{
                            backgroundColor: (tactic.detection_count || 0) > 5 ? '#dc3545' : 
                                           (tactic.detection_count || 0) > 3 ? '#ffc107' : '#28a745',
                            color: 'white',
                            padding: '0.25rem 0.75rem',
                            borderRadius: '12px',
                            fontSize: '0.75rem',
                            fontWeight: '600'
                          }}>
                            {tactic.detection_count || 0} detected
                          </span>
                        </div>
                        
                        {selectedTactic === tactic.name && (
                          <div style={{ fontSize: '0.875rem', color: '#007bff', fontWeight: '600' }}>
                            <i className="fas fa-chevron-up"></i> Click to collapse
                          </div>
                        )}
                      </div>
                      
                      {selectedTactic === tactic.name && (
                        <div style={{ 
                          marginTop: '1rem', 
                          padding: '1rem', 
                          backgroundColor: '#f8f9fa', 
                          borderRadius: '8px',
                          borderTop: '3px solid #007bff'
                        }}>
                          <h5 style={{ margin: '0 0 0.5rem 0', color: '#333' }}>Detection Details</h5>
                          <p style={{ margin: '0', fontSize: '0.875rem', color: '#666' }}>
                            This tactic has been detected {tactic.detection_count || 0} times across your environment. 
                            Click on individual techniques to view detailed information and mitigation strategies.
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ textAlign: 'center', color: '#666', padding: '3rem' }}>
                  {searchTerm || filterBySeverity !== 'all' ? (
                    <>
                      <i className="fas fa-search" style={{ fontSize: '3rem', marginBottom: '1rem', color: '#dee2e6' }}></i>
                      <h4 style={{ margin: '0 0 0.5rem 0', color: '#666' }}>No tactics match your filters</h4>
                      <p style={{ margin: '0' }}>Try adjusting your search term or detection level filter</p>
                    </>
                  ) : (
                    <>
                      <i className="fas fa-crosshairs" style={{ fontSize: '3rem', marginBottom: '1rem', color: '#dee2e6' }}></i>
                      <h4 style={{ margin: '0 0 0.5rem 0', color: '#666' }}>No MITRE ATT&CK data available</h4>
                      <p style={{ margin: '0' }}>Connect threat intelligence feeds to populate this view</p>
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Behavior Analytics Tab */}
      {activeTab === 'behavior' && (
        <BehaviorAnalyticsDashboard active={true} />
      )}

      {activeTab === 'alerts' && (
        <div style={{ marginBottom: '2rem' }}>
          <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
            <div style={{ backgroundColor: '#f8f9fa', padding: '1rem', borderBottom: '1px solid #dee2e6', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <h3 style={{ margin: '0', fontSize: '1.125rem', fontWeight: '600', color: 'black' }}>
                <i className="fas fa-bell" style={{ marginRight: '0.5rem', color: 'yellow' }}></i>
                Live Security Alerts
              </h3>
              <span style={{
                backgroundColor: '#dc3545',
                color: 'white',
                padding: '0.25rem 0.75rem',
                borderRadius: '12px',
                fontSize: '0.75rem',
                fontWeight: '600'
              }}>{realTimeAlerts.length}</span>
            </div>
            <div style={{ padding: '1.5rem' }}>
              {realTimeAlerts.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {realTimeAlerts.map((alert, index) => (
                    <div key={index} style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'center',
                      padding: '1rem',
                      backgroundColor: '#f8f9fa',
                      borderRadius: '6px',
                      border: '1px solid #e9ecef'
                    }}>
                      <div style={{ flex: 1 }}>
                        <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '1rem', fontWeight: '600' }}>{alert.title}</h4>
                        <p style={{ margin: '0 0 0.5rem 0', color: '#666', fontSize: '0.875rem' }}>{alert.description}</p>
                        <div style={{ fontSize: '0.75rem', color: '#999' }}>{new Date(alert.timestamp).toLocaleString()}</div>
                      </div>
                      <span style={{
                        backgroundColor: alert.priority === 'critical' ? '#dc3545' : alert.priority === 'high' ? '#ffc107' : '#17a2b8',
                        color: 'white',
                        padding: '0.25rem 0.75rem',
                        borderRadius: '12px',
                        fontSize: '0.75rem',
                        fontWeight: '600',
                        textTransform: 'uppercase'
                      }}>
                        {alert.priority}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ textAlign: 'center', color: '#666', padding: '2rem' }}>
                  <i className="fas fa-shield-check" style={{ fontSize: '3rem', marginBottom: '1rem', color: '#28a745' }}></i>
                  <p>No active alerts - All systems secure</p>
                </div>
              )}
            </div>
          </div>

          {/* Recent Incidents */}
          <div style={{ backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)', overflow: 'hidden', marginTop: '2rem' }}>
            <div style={{ 
              background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)', 
              color: 'white', 
              padding: '1rem',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <h3 style={{ margin: '0', fontSize: '1.125rem', fontWeight: '600' }}>
                <i className="fas fa-list" style={{ marginRight: '0.5rem' }}></i>
                Recent Security Incidents
              </h3>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <button 
                  onClick={() => setShowIncidentModal(true)}
                  style={{ 
                    padding: '0.5rem 1rem',
                    backgroundColor: 'rgba(255,255,255,0.2)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '0.75rem',
                    fontWeight: '500',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}
                >
                  <i className="fas fa-plus"></i>
                  Create Incident
                </button>
                <button 
                  onClick={() => handleDownload('csv')}
                  disabled={downloading}
                  style={{ 
                    padding: '0.5rem 1rem',
                    backgroundColor: 'rgba(255,255,255,0.2)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '0.75rem',
                    fontWeight: '500',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}
                >
                  {downloading ? (
                    <>
                      <span style={{ width: '12px', height: '12px', border: '2px solid transparent', borderTop: '2px solid white', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></span>
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
                  onClick={() => handleDownload('json')}
                  disabled={downloading}
                  style={{ 
                    padding: '0.5rem 1rem',
                    backgroundColor: 'rgba(255,255,255,0.2)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '0.75rem',
                    fontWeight: '500',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}
                >
                  <i className="fas fa-file-code"></i>
                  JSON
                </button>
                <button 
                  onClick={() => showPage('soc-incidents')}
                  style={{ 
                    padding: '0.5rem 1rem',
                    backgroundColor: 'rgba(255,255,255,0.2)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '0.75rem',
                    fontWeight: '500',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem'
                  }}
                >
                  <i className="fas fa-external-link-alt"></i>
                  View All
                </button>
              </div>
            </div>
            <div>
              {recent_incidents && recent_incidents.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '3rem', color: '#666' }}>
                  <i className="fas fa-shield-check" style={{ fontSize: '3rem', marginBottom: '1rem', color: '#28a745' }}></i>
                  <h4 style={{ margin: '0 0 0.5rem 0', color: '#28a745' }}>No Recent Incidents</h4>
                  <p style={{ margin: '0' }}>All systems are operating normally</p>
                </div>
              ) : recent_incidents && recent_incidents.length > 0 ? (
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                    <thead>
                      <tr style={{ backgroundColor: '#f8f9fa' }}>
                        <th style={{ padding: '1rem', textAlign: 'left', borderBottom: '2px solid #dee2e6', fontWeight: '600' }}>ID</th>
                        <th style={{ padding: '1rem', textAlign: 'left', borderBottom: '2px solid #dee2e6', fontWeight: '600' }}>Title</th>
                        <th style={{ padding: '1rem', textAlign: 'left', borderBottom: '2px solid #dee2e6', fontWeight: '600' }}>Priority</th>
                        <th style={{ padding: '1rem', textAlign: 'left', borderBottom: '2px solid #dee2e6', fontWeight: '600' }}>Status</th>
                        <th style={{ padding: '1rem', textAlign: 'left', borderBottom: '2px solid #dee2e6', fontWeight: '600' }}>Created</th>
                        <th style={{ padding: '1rem', textAlign: 'left', borderBottom: '2px solid #dee2e6', fontWeight: '600' }}>SLA Status</th>
                        <th style={{ padding: '1rem', textAlign: 'center', borderBottom: '2px solid #dee2e6', fontWeight: '600' }}>Actions</th>
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
                            <div style={{ fontSize: '0.875rem' }}>
                              <div>{new Date(incident.created_at).toLocaleDateString()}</div>
                              <div style={{ color: '#666', fontSize: '0.75rem' }}>{new Date(incident.created_at).toLocaleTimeString()}</div>
                            </div>
                          </td>
                          <td style={{ padding: '12px' }}>
                            {incident.is_overdue ? (
                              <span style={{ 
                                backgroundColor: '#dc3545',
                                color: 'white',
                                padding: '6px 10px',
                                borderRadius: '12px',
                                fontSize: '0.75rem',
                                fontWeight: '600'
                              }}>
                                <i className="fas fa-exclamation-triangle" style={{ marginRight: '0.25rem' }}></i>
                                Overdue
                              </span>
                            ) : (
                              <span style={{ 
                                backgroundColor: '#28a745',
                                color: 'white',
                                padding: '6px 10px',
                                borderRadius: '12px',
                                fontSize: '0.75rem',
                                fontWeight: '600'
                              }}>
                                <i className="fas fa-check" style={{ marginRight: '0.25rem' }}></i>
                                On Track
                              </span>
                            )}
                          </td>
                          <td style={{ padding: '12px', textAlign: 'center' }}>
                            <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center' }}>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleEditIncident(incident);
                                }}
                                style={{
                                  backgroundColor: '#007bff',
                                  color: 'white',
                                  border: 'none',
                                  padding: '0.375rem 0.75rem',
                                  borderRadius: '4px',
                                  fontSize: '0.75rem',
                                  cursor: 'pointer',
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: '0.25rem'
                                }}
                                title="Edit incident"
                              >
                                <i className="fas fa-edit"></i>
                                Edit
                              </button>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleDeleteIncident(incident.id);
                                }}
                                disabled={deletingIncidentId === incident.id}
                                style={{
                                  backgroundColor: deletingIncidentId === incident.id ? '#6c757d' : '#dc3545',
                                  color: 'white',
                                  border: 'none',
                                  padding: '0.375rem 0.75rem',
                                  borderRadius: '4px',
                                  fontSize: '0.75rem',
                                  cursor: deletingIncidentId === incident.id ? 'not-allowed' : 'pointer',
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: '0.25rem'
                                }}
                                title="Delete incident"
                              >
                                {deletingIncidentId === incident.id ? (
                                  <>
                                    <span style={{ 
                                      width: '12px', 
                                      height: '12px', 
                                      border: '2px solid transparent', 
                                      borderTop: '2px solid white', 
                                      borderRadius: '50%', 
                                      animation: 'spin 1s linear infinite' 
                                    }}></span>
                                    Deleting...
                                  </>
                                ) : (
                                  <>
                                    <i className="fas fa-trash"></i>
                                    Delete
                                  </>
                                )}
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div style={{ textAlign: 'center', padding: '3rem', color: '#666' }}>
                  <i className="fas fa-spinner fa-spin" style={{ fontSize: '3rem', marginBottom: '1rem', color: '#dee2e6' }}></i>
                  <p>Loading incidents...</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      </div>

      {/* SOC Incident Creation Modal */}
      <SOCIncidentModal
        isOpen={showIncidentModal}
        onClose={() => setShowIncidentModal(false)}
        onIncidentCreated={handleIncidentCreated}
      />

      {/* SOC Incident Edit Modal */}
      <SOCIncidentEditModal
        isOpen={showEditModal}
        onClose={() => {
          setShowEditModal(false);
          setEditingIncident(null);
        }}
        incident={editingIncident}
        onIncidentUpdated={handleIncidentUpdated}
      />

      {/* Technique Details Modal */}
      {showTechniqueModal && selectedTechnique && (
        <div 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            backdropFilter: 'blur(5px)'
          }}
          onClick={() => setShowTechniqueModal(false)}
        >
          <div 
            style={{
              background: 'white',
              borderRadius: '12px',
              maxWidth: '600px',
              width: '90%',
              maxHeight: '80vh',
              overflowY: 'auto',
              boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'flex-start',
              padding: '25px',
              borderBottom: '1px solid #dee2e6',
              background: 'linear-gradient(135deg, #007bff, #0056b3)',
              color: 'white',
              borderRadius: '12px 12px 0 0'
            }}>
              <div>
                <h2 style={{ margin: '0 0 5px 0', fontFamily: 'monospace', fontSize: '24px' }}>
                  {selectedTechnique.technique_id}
                </h2>
                <h3 style={{ margin: '0', fontSize: '18px', opacity: '0.9' }}>
                  {selectedTechnique.name}
                </h3>
              </div>
              <button 
                onClick={() => setShowTechniqueModal(false)}
                style={{
                  background: 'rgba(255, 255, 255, 0.2)',
                  border: 'none',
                  borderRadius: '50%',
                  width: '40px',
                  height: '40px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => e.target.style.background = 'rgba(255, 255, 255, 0.3)'}
                onMouseLeave={(e) => e.target.style.background = 'rgba(255, 255, 255, 0.2)'}
              >
                <i className="fas fa-times"></i>
              </button>
            </div>
            
            <div style={{ padding: '25px' }}>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                gap: '15px',
                marginBottom: '25px'
              }}>
                <div style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  padding: '15px',
                  background: '#f8f9fa',
                  borderRadius: '8px',
                  border: '1px solid #dee2e6'
                }}>
                  <span style={{
                    fontSize: '12px',
                    color: '#6c757d',
                    textTransform: 'uppercase',
                    fontWeight: '600',
                    marginBottom: '5px'
                  }}>Detections</span>
                  <span style={{ fontSize: '18px', fontWeight: '700', color: '#333' }}>
                    {selectedTechnique.detection_count || 0}
                  </span>
                </div>
                <div style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  padding: '15px',
                  background: '#f8f9fa',
                  borderRadius: '8px',
                  border: '1px solid #dee2e6'
                }}>
                  <span style={{
                    fontSize: '12px',
                    color: '#6c757d',
                    textTransform: 'uppercase',
                    fontWeight: '600',
                    marginBottom: '5px'
                  }}>Tactic</span>
                  <span style={{ fontSize: '18px', fontWeight: '700', color: '#333' }}>
                    {selectedTechnique.tactic || 'Unknown'}
                  </span>
                </div>
                <div style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  padding: '15px',
                  background: '#f8f9fa',
                  borderRadius: '8px',
                  border: '1px solid #dee2e6'
                }}>
                  <span style={{
                    fontSize: '12px',
                    color: '#6c757d',
                    textTransform: 'uppercase',
                    fontWeight: '600',
                    marginBottom: '5px'
                  }}>Risk Level</span>
                  <span style={{
                    fontSize: '18px',
                    fontWeight: '700',
                    color: (selectedTechnique.detection_count || 0) > 5 ? '#dc3545' : 
                           (selectedTechnique.detection_count || 0) > 3 ? '#ffc107' : '#28a745'
                  }}>
                    {(selectedTechnique.detection_count || 0) > 5 ? 'High' : 
                     (selectedTechnique.detection_count || 0) > 3 ? 'Medium' : 'Low'}
                  </span>
                </div>
              </div>
              
              {techniqueDetails[selectedTechnique.technique_id] && (
                <div>
                  <h4 style={{ margin: '20px 0 10px 0', color: '#333', borderBottom: '2px solid #e9ecef', paddingBottom: '5px' }}>
                    Description
                  </h4>
                  <p style={{ color: '#666', lineHeight: '1.6' }}>
                    {techniqueDetails[selectedTechnique.technique_id].description || 'No description available.'}
                  </p>
                  
                  {techniqueDetails[selectedTechnique.technique_id].platforms && (
                    <div style={{ margin: '20px 0' }}>
                      <h4 style={{ margin: '0 0 10px 0', color: '#333' }}>Platforms</h4>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                        {techniqueDetails[selectedTechnique.technique_id].platforms.map((platform, i) => (
                          <span key={i} style={{
                            background: '#e9ecef',
                            padding: '4px 8px',
                            borderRadius: '4px',
                            fontSize: '12px',
                            color: '#495057'
                          }}>
                            {platform}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {techniqueDetails[selectedTechnique.technique_id].data_sources && (
                    <div style={{ margin: '20px 0' }}>
                      <h4 style={{ margin: '0 0 10px 0', color: '#333' }}>Data Sources</h4>
                      <ul style={{ margin: '10px 0 0 20px', padding: '0' }}>
                        {techniqueDetails[selectedTechnique.technique_id].data_sources.map((source, i) => (
                          <li key={i} style={{ margin: '5px 0', color: '#6c757d' }}>{source}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
              
              <div style={{
                display: 'flex',
                gap: '15px',
                justifyContent: 'flex-end',
                marginTop: '25px',
                paddingTop: '20px',
                borderTop: '1px solid #dee2e6'
              }}>
                <button 
                  onClick={() => window.open(`https://attack.mitre.org/techniques/${selectedTechnique.technique_id}/`, '_blank')}
                  style={{
                    backgroundColor: '#007bff',
                    color: 'white',
                    border: 'none',
                    padding: '10px 20px',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    fontWeight: '500',
                    transition: 'all 0.2s',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                  onMouseEnter={(e) => e.target.style.backgroundColor = '#0056b3'}
                  onMouseLeave={(e) => e.target.style.backgroundColor = '#007bff'}
                >
                  <i className="fas fa-external-link-alt"></i>
                  View on MITRE
                </button>
                <button 
                  onClick={() => setShowTechniqueModal(false)}
                  style={{
                    backgroundColor: 'transparent',
                    border: '1px solid #dee2e6',
                    color: '#495057',
                    padding: '10px 20px',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    fontWeight: '500',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={(e) => e.target.style.backgroundColor = '#f8f9fa'}
                  onMouseLeave={(e) => e.target.style.backgroundColor = 'transparent'}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
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