import React, { useState, useEffect } from 'react';
import LoadingSpinner from './LoadingSpinner.jsx';

const STIXViewer = ({ active = true, stixObject = null, stixId = null, userRole }) => {
  console.log('STIXViewer rendered with props:', { active, stixObject, stixId });
  
  // States following existing patterns
  const [stixData, setStixData] = useState(stixObject);
  const [loading, setLoading] = useState(!stixObject && !!stixId);
  const [error, setError] = useState(null);
  const [activeView, setActiveView] = useState('formatted');
  const [copySuccess, setCopySuccess] = useState(false);

  // Permission checks following existing patterns
  const isAdmin = userRole === 'admin' || userRole === 'BlueVisionAdmin';
  const isPublisher = userRole === 'publisher' || isAdmin;
  const isViewer = userRole === 'viewer';

  useEffect(() => {
    if (active && stixId && !stixObject) {
      loadSTIXObject();
    }
  }, [active, stixId, stixObject]);

  useEffect(() => {
    if (stixObject) {
      setStixData(stixObject);
      setLoading(false);
    }
  }, [stixObject]);

  const loadSTIXObject = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('crisp_auth_token');
      const response = await fetch(`http://localhost:8000/api/v1/stix-objects/${stixId}/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to fetch STIX object`);
      }

      const data = await response.json();
      console.log('STIX object loaded:', data);
      setStixData(data);
    } catch (err) {
      console.error('Error loading STIX object:', err);
      setError(err.message || 'Failed to load STIX object');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async (content) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
      alert('Failed to copy to clipboard');
    }
  };

  const formatSTIXProperty = (key, value) => {
    if (value === null || value === undefined) return 'N/A';
    
    if (typeof value === 'boolean') {
      return value ? 'true' : 'false';
    }
    
    if (Array.isArray(value)) {
      if (value.length === 0) return 'None';
      return value.map((item, index) => (
        <div key={index} className="array-item">
          {typeof item === 'object' ? JSON.stringify(item) : String(item)}
        </div>
      ));
    }
    
    if (typeof value === 'object') {
      return <pre className="object-content">{JSON.stringify(value, null, 2)}</pre>;
    }
    
    if (key === 'created' || key === 'modified' || key.includes('time') || key.includes('date')) {
      try {
        return new Date(value).toLocaleString();
      } catch {
        return String(value);
      }
    }
    
    if (key === 'pattern' && String(value).length > 100) {
      return (
        <div className="pattern-content">
          <code>{value}</code>
          <button 
            className="btn btn-icon btn-small copy-btn"
            onClick={() => copyToClipboard(value)}
            title="Copy pattern"
          >
            <i className="fas fa-copy"></i>
          </button>
        </div>
      );
    }
    
    return String(value);
  };

  const getSTIXTypeIcon = (type) => {
    const iconMap = {
      'indicator': 'fas fa-search',
      'malware': 'fas fa-bug',
      'threat-actor': 'fas fa-user-secret',
      'attack-pattern': 'fas fa-crosshairs',
      'campaign': 'fas fa-flag',
      'intrusion-set': 'fas fa-users',
      'course-of-action': 'fas fa-shield-alt',
      'vulnerability': 'fas fa-exclamation-triangle',
      'tool': 'fas fa-wrench',
      'identity': 'fas fa-id-card',
      'location': 'fas fa-map-marker-alt',
      'infrastructure': 'fas fa-server',
      'observed-data': 'fas fa-eye',
      'report': 'fas fa-file-alt'
    };
    
    return iconMap[type] || 'fas fa-cube';
  };

  const getSTIXTypeColor = (type) => {
    const colorMap = {
      'indicator': '#e74c3c',
      'malware': '#e67e22',
      'threat-actor': '#9b59b6',
      'attack-pattern': '#f39c12',
      'campaign': '#3498db',
      'intrusion-set': '#2ecc71',
      'course-of-action': '#1abc9c',
      'vulnerability': '#e74c3c',
      'tool': '#34495e',
      'identity': '#95a5a6',
      'location': '#16a085',
      'infrastructure': '#27ae60',
      'observed-data': '#8e44ad',
      'report': '#2980b9'
    };
    
    return colorMap[type] || '#7f8c8d';
  };

  const renderSTIXProperties = (obj) => {
    if (!obj || typeof obj !== 'object') return null;
    
    // Group properties by importance
    const coreProperties = ['id', 'type', 'spec_version', 'created', 'modified'];
    const nameProperties = ['name', 'pattern', 'value', 'title', 'description'];
    const otherProperties = Object.keys(obj).filter(
      key => !coreProperties.includes(key) && !nameProperties.includes(key)
    );
    
    const allProperties = [...coreProperties, ...nameProperties, ...otherProperties];
    
    return (
      <div className="stix-properties">
        {allProperties.map(key => {
          if (!obj.hasOwnProperty(key)) return null;
          
          const value = obj[key];
          const isCore = coreProperties.includes(key);
          const isName = nameProperties.includes(key);
          
          return (
            <div 
              key={key} 
              className={`property-item ${isCore ? 'core' : ''} ${isName ? 'name' : ''}`}
            >
              <label className="property-label">{key.replace(/_/g, ' ')}:</label>
              <div className="property-value">
                {formatSTIXProperty(key, value)}
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  // Don't render if not active
  if (!active) return null;

  if (loading) {
    return <LoadingSpinner message="Loading STIX object..." />;
  }

  if (error) {
    return (
      <div className="error-container">
        <div className="error-message">
          <i className="fas fa-exclamation-triangle"></i>
          <h3>Error Loading STIX Object</h3>
          <p>{error}</p>
          <button className="btn btn-primary" onClick={loadSTIXObject}>
            <i className="fas fa-redo"></i> Retry
          </button>
        </div>
      </div>
    );
  }

  if (!stixData) {
    return (
      <div className="error-container">
        <div className="error-message">
          <i className="fas fa-cube"></i>
          <h3>No STIX Object</h3>
          <p>No STIX object data available to display.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="stix-viewer-container">
      {/* Header */}
      <div className="stix-header">
        <div className="stix-title-section">
          <div 
            className="stix-type-badge"
            style={{ backgroundColor: getSTIXTypeColor(stixData.type) }}
          >
            <i className={getSTIXTypeIcon(stixData.type)}></i>
            {stixData.type?.replace(/-/g, ' ').toUpperCase()}
          </div>
          
          <div className="stix-title-content">
            <h1 className="stix-title">
              {stixData.name || stixData.pattern || stixData.value || stixData.title || 'STIX Object'}
            </h1>
            {stixData.id && (
              <p className="stix-id">ID: {stixData.id}</p>
            )}
          </div>
        </div>
        
        <div className="stix-actions">
          {copySuccess && (
            <span className="copy-success">
              <i className="fas fa-check"></i> Copied!
            </span>
          )}
          <button 
            className="btn btn-outline"
            onClick={() => copyToClipboard(JSON.stringify(stixData, null, 2))}
          >
            <i className="fas fa-copy"></i>
            Copy JSON
          </button>
          {isPublisher && (
            <button className="btn btn-primary">
              <i className="fas fa-download"></i>
              Export
            </button>
          )}
        </div>
      </div>

      {/* View Toggle */}
      <div className="view-toggle">
        <button 
          className={`toggle-btn ${activeView === 'formatted' ? 'active' : ''}`}
          onClick={() => setActiveView('formatted')}
        >
          <i className="fas fa-list"></i>
          Formatted View
        </button>
        <button 
          className={`toggle-btn ${activeView === 'raw' ? 'active' : ''}`}
          onClick={() => setActiveView('raw')}
        >
          <i className="fas fa-code"></i>
          Raw JSON
        </button>
      </div>

      {/* Content */}
      <div className="stix-content">
        {activeView === 'formatted' ? (
          <div className="formatted-view">
            {/* Core Information */}
            {(stixData.name || stixData.description) && (
              <div className="stix-section">
                <h3>Overview</h3>
                {stixData.name && (
                  <div className="overview-item">
                    <strong>Name:</strong> {stixData.name}
                  </div>
                )}
                {stixData.description && (
                  <div className="overview-item">
                    <strong>Description:</strong>
                    <div className="description-content">{stixData.description}</div>
                  </div>
                )}
              </div>
            )}

            {/* Pattern (for indicators) */}
            {stixData.pattern && (
              <div className="stix-section">
                <h3>Pattern</h3>
                <div className="pattern-display">
                  <code>{stixData.pattern}</code>
                  <button 
                    className="btn btn-icon copy-pattern-btn"
                    onClick={() => copyToClipboard(stixData.pattern)}
                    title="Copy pattern"
                  >
                    <i className="fas fa-copy"></i>
                  </button>
                </div>
              </div>
            )}

            {/* Labels and Classification */}
            {(stixData.labels || stixData.confidence || stixData.lang) && (
              <div className="stix-section">
                <h3>Classification</h3>
                <div className="classification-grid">
                  {stixData.labels && stixData.labels.length > 0 && (
                    <div className="classification-item">
                      <strong>Labels:</strong>
                      <div className="labels-container">
                        {stixData.labels.map((label, index) => (
                          <span key={index} className="label-tag">
                            {label}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  {stixData.confidence !== undefined && (
                    <div className="classification-item">
                      <strong>Confidence:</strong>
                      <span className={`confidence-badge ${
                        stixData.confidence >= 75 ? 'high' : 
                        stixData.confidence >= 50 ? 'medium' : 'low'
                      }`}>
                        {stixData.confidence}%
                      </span>
                    </div>
                  )}
                  {stixData.lang && (
                    <div className="classification-item">
                      <strong>Language:</strong> {stixData.lang}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Timestamps */}
            <div className="stix-section">
              <h3>Timeline</h3>
              <div className="timeline-grid">
                <div className="timeline-item">
                  <strong>Created:</strong>
                  <span>{stixData.created ? new Date(stixData.created).toLocaleString() : 'Unknown'}</span>
                </div>
                <div className="timeline-item">
                  <strong>Modified:</strong>
                  <span>{stixData.modified ? new Date(stixData.modified).toLocaleString() : 'Unknown'}</span>
                </div>
                {stixData.valid_from && (
                  <div className="timeline-item">
                    <strong>Valid From:</strong>
                    <span>{new Date(stixData.valid_from).toLocaleString()}</span>
                  </div>
                )}
                {stixData.valid_until && (
                  <div className="timeline-item">
                    <strong>Valid Until:</strong>
                    <span>{new Date(stixData.valid_until).toLocaleString()}</span>
                  </div>
                )}
              </div>
            </div>

            {/* All Properties */}
            <div className="stix-section">
              <h3>All Properties</h3>
              {renderSTIXProperties(stixData)}
            </div>
          </div>
        ) : (
          <div className="raw-view">
            <div className="raw-json-container">
              <pre className="raw-json">
                {JSON.stringify(stixData, null, 2)}
              </pre>
            </div>
            <div className="raw-actions">
              <button 
                className="btn btn-outline"
                onClick={() => copyToClipboard(JSON.stringify(stixData, null, 2))}
              >
                <i className="fas fa-copy"></i>
                Copy All
              </button>
              <button 
                className="btn btn-outline"
                onClick={() => {
                  const formatted = JSON.stringify(stixData, null, 2);
                  const blob = new Blob([formatted], { type: 'application/json' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `${stixData.type || 'stix-object'}-${stixData.id || 'unknown'}.json`;
                  document.body.appendChild(a);
                  a.click();
                  document.body.removeChild(a);
                  URL.revokeObjectURL(url);
                }}
              >
                <i className="fas fa-download"></i>
                Download JSON
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default STIXViewer;