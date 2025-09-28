import React, { useState, useEffect, useCallback } from 'react';
import * as api from '../../api.js';

const InteractiveTtpAnalysis = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [timeRange, setTimeRange] = useState(30);
  
  // Interactive states
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTactic, setSelectedTactic] = useState(null);
  const [selectedTechnique, setSelectedTechnique] = useState(null);
  const [showTechniqueModal, setShowTechniqueModal] = useState(false);
  const [hoveredTactic, setHoveredTactic] = useState(null);
  const [filterBySeverity, setFilterBySeverity] = useState('all');
  const [sortBy, setSortBy] = useState('frequency');
  const [viewMode, setViewMode] = useState('grid'); // grid or list
  const [animationEnabled, setAnimationEnabled] = useState(true);
  
  // Data states
  const [mitreMatrix, setMitreMatrix] = useState(null);
  const [feedComparison, setFeedComparison] = useState(null);
  const [seasonalPatterns, setSeasonalPatterns] = useState(null);
  const [techniqueFreqs, setTechniqueFreqs] = useState(null);
  const [techniqueDetails, setTechniqueDetails] = useState({});

  useEffect(() => {
    fetchAllTtpData();
  }, [timeRange]);

  const fetchAllTtpData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [matrixData, comparisonData, patternsData, freqData] = await Promise.allSettled([
        api.getMitreMatrix(),
        api.getTtpFeedComparison(timeRange),
        api.getTtpSeasonalPatterns(timeRange * 6),
        api.getTtpTechniqueFrequencies(timeRange)
      ]);

      if (matrixData.status === 'fulfilled') {
        setMitreMatrix(matrixData.value);
      }
      if (comparisonData.status === 'fulfilled') {
        setFeedComparison(comparisonData.value);
      }
      if (patternsData.status === 'fulfilled') {
        setSeasonalPatterns(patternsData.value);
      }
      if (freqData.status === 'fulfilled') {
        setTechniqueFreqs(freqData.value);
      }

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchTechniqueDetails = useCallback(async (techniqueId) => {
    if (techniqueDetails[techniqueId]) return techniqueDetails[techniqueId];
    
    try {
      const details = await api.getTechniqueDetails(techniqueId);
      setTechniqueDetails(prev => ({ ...prev, [techniqueId]: details }));
      return details;
    } catch (err) {
      console.warn('Failed to fetch technique details:', err);
      return null;
    }
  }, [techniqueDetails]);

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

  const getFilteredTechniques = () => {
    if (!techniqueFreqs?.top_techniques) return [];
    
    let filtered = techniqueFreqs.top_techniques;
    
    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(tech => 
        tech.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tech.technique_id?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    // Severity filter
    if (filterBySeverity !== 'all') {
      const thresholds = { high: 10, medium: 5, low: 1 };
      const threshold = thresholds[filterBySeverity];
      filtered = filtered.filter(tech => tech.frequency >= threshold);
    }
    
    // Sort
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'frequency': return b.frequency - a.frequency;
        case 'name': return a.name?.localeCompare(b.name) || 0;
        case 'id': return a.technique_id?.localeCompare(b.technique_id) || 0;
        default: return 0;
      }
    });
    
    return filtered;
  };

  // Interactive Matrix Component
  const InteractiveMatrix = () => (
    <div className="interactive-matrix">
      <div className="matrix-controls">
        <div className="search-box">
          <i className="fas fa-search"></i>
          <input
            type="text"
            placeholder="Search techniques..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          {searchTerm && (
            <button 
              className="clear-search"
              onClick={() => setSearchTerm('')}
            >
              <i className="fas fa-times"></i>
            </button>
          )}
        </div>
        
        <div className="filter-controls">
          <select 
            value={filterBySeverity} 
            onChange={(e) => setFilterBySeverity(e.target.value)}
          >
            <option value="all">All Severities</option>
            <option value="high">High (10+ occurrences)</option>
            <option value="medium">Medium (5+ occurrences)</option>
            <option value="low">Low (1+ occurrences)</option>
          </select>
          
          <select 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="frequency">Sort by Frequency</option>
            <option value="name">Sort by Name</option>
            <option value="id">Sort by ID</option>
          </select>
          
          <div className="view-toggle">
            <button 
              className={viewMode === 'grid' ? 'active' : ''}
              onClick={() => setViewMode('grid')}
              title="Grid View"
            >
              <i className="fas fa-th"></i>
            </button>
            <button 
              className={viewMode === 'list' ? 'active' : ''}
              onClick={() => setViewMode('list')}
              title="List View"
            >
              <i className="fas fa-list"></i>
            </button>
          </div>
        </div>
      </div>

      {mitreMatrix?.tactics && (
        <div className={`tactics-container ${viewMode}`}>
          {Object.entries(mitreMatrix.tactics).map(([tacticId, tacticData]) => (
            <div 
              key={tacticId} 
              className={`interactive-tactic-card ${selectedTactic === tacticId ? 'selected' : ''}`}
              onMouseEnter={() => setHoveredTactic(tacticId)}
              onMouseLeave={() => setHoveredTactic(null)}
              onClick={() => setSelectedTactic(selectedTactic === tacticId ? null : tacticId)}
              style={{
                transform: hoveredTactic === tacticId && animationEnabled ? 'translateY(-5px)' : 'translateY(0)',
                transition: 'all 0.3s ease'
              }}
            >
              <div 
                className="tactic-header"
                style={{ 
                  background: `linear-gradient(135deg, ${getTacticColor(tacticId, 0.8)}, ${getTacticColor(tacticId, 1)})`,
                  boxShadow: hoveredTactic === tacticId ? `0 8px 25px ${getTacticColor(tacticId, 0.3)}` : 'none'
                }}
              >
                <h4>{tacticData.name || tacticId}</h4>
                <div className="tactic-stats">
                  <span className="technique-count">
                    {tacticData.techniques?.length || 0}
                  </span>
                  <span className="techniques-label">techniques</span>
                </div>
              </div>
              
              <div className="tactic-techniques">
                {tacticData.techniques?.slice(0, selectedTactic === tacticId ? undefined : 6).map((technique) => (
                  <div 
                    key={technique.technique_id} 
                    className="interactive-technique-chip"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleTechniqueClick(technique);
                    }}
                    title={`${technique.technique_id}: ${technique.name}`}
                  >
                    <span className="technique-id">{technique.technique_id}</span>
                    <span className="technique-frequency">{technique.frequency || 0}</span>
                  </div>
                ))}
                
                {selectedTactic !== tacticId && tacticData.techniques?.length > 6 && (
                  <div className="show-more-chip">
                    <i className="fas fa-plus"></i>
                    {tacticData.techniques.length - 6} more
                  </div>
                )}
              </div>
              
              {selectedTactic === tacticId && (
                <div className="expanded-details">
                  <div className="tactic-description">
                    <p>Click on any technique to view detailed information and related threats.</p>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );

  // Enhanced Technique Modal
  const TechniqueModal = () => {
    if (!showTechniqueModal || !selectedTechnique) return null;
    
    const details = techniqueDetails[selectedTechnique.technique_id];
    
    return (
      <div className="technique-modal-overlay" onClick={() => setShowTechniqueModal(false)}>
        <div className="technique-modal" onClick={(e) => e.stopPropagation()}>
          <div className="modal-header">
            <div className="technique-title">
              <h2>{selectedTechnique.technique_id}</h2>
              <h3>{selectedTechnique.name}</h3>
            </div>
            <button 
              className="close-modal"
              onClick={() => setShowTechniqueModal(false)}
            >
              <i className="fas fa-times"></i>
            </button>
          </div>
          
          <div className="modal-content">
            <div className="technique-stats">
              <div className="stat-item">
                <span className="stat-label">Frequency</span>
                <span className="stat-value">{selectedTechnique.frequency || 0}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Tactic</span>
                <span className="stat-value">{selectedTechnique.tactic || 'Unknown'}</span>
              </div>
              <div className="stat-item">
                <span className="stat-label">Risk Level</span>
                <span className={`stat-value risk-${selectedTechnique.frequency > 10 ? 'high' : selectedTechnique.frequency > 5 ? 'medium' : 'low'}`}>
                  {selectedTechnique.frequency > 10 ? 'High' : selectedTechnique.frequency > 5 ? 'Medium' : 'Low'}
                </span>
              </div>
            </div>
            
            {details && (
              <div className="technique-details">
                <div className="detail-section">
                  <h4>Description</h4>
                  <p>{details.description || 'No description available.'}</p>
                </div>
                
                {details.related_techniques && (
                  <div className="detail-section">
                    <h4>Related Techniques</h4>
                    <div className="related-techniques">
                      {details.related_techniques.map((related, index) => (
                        <span key={index} className="related-chip">
                          {related}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {details.mitigation && (
                  <div className="detail-section">
                    <h4>Mitigation</h4>
                    <p>{details.mitigation}</p>
                  </div>
                )}
              </div>
            )}
            
            <div className="modal-actions">
              <button 
                className="btn btn-primary"
                onClick={() => {
                  // Add to investigation or create alert
                  console.log('Add to investigation:', selectedTechnique);
                }}
              >
                <i className="fas fa-plus"></i>
                Add to Investigation
              </button>
              <button 
                className="btn btn-outline"
                onClick={() => {
                  // Export or share
                  console.log('Export technique:', selectedTechnique);
                }}
              >
                <i className="fas fa-share"></i>
                Share
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Interactive Top Techniques List
  const InteractiveTechniquesList = () => {
    const filteredTechniques = getFilteredTechniques();
    
    return (
      <div className="interactive-techniques-list">
        <div className="list-header">
          <h3>Most Frequent Techniques</h3>
          <span className="result-count">
            {filteredTechniques.length} technique{filteredTechniques.length !== 1 ? 's' : ''} found
          </span>
        </div>
        
        <div className="techniques-grid">
          {filteredTechniques.slice(0, 20).map((technique, index) => (
            <div 
              key={technique.technique_id || index} 
              className="interactive-technique-item"
              onClick={() => handleTechniqueClick(technique)}
            >
              <div className="technique-rank">#{index + 1}</div>
              <div className="technique-info">
                <div className="technique-header">
                  <span className="technique-id">{technique.technique_id}</span>
                  <span className="frequency-badge">{technique.frequency}</span>
                </div>
                <div className="technique-name">{technique.name}</div>
                <div className="technique-meta">
                  <span className="tactic-tag" style={{ backgroundColor: getTacticColor(technique.tactic, 0.2) }}>
                    {technique.tactic || 'Unknown'}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="ttp-analysis">
        <div className="loading-state">
          <div className="loading-animation">
            <div className="spinner"></div>
            <div className="loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
          <p>Loading MITRE ATT&CK analysis...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="ttp-analysis">
        <div className="error-state">
          <i className="fas fa-exclamation-triangle"></i>
          <h3>Error Loading Data</h3>
          <p>{error}</p>
          <button onClick={fetchAllTtpData} className="btn btn-primary">
            <i className="fas fa-refresh"></i>
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="interactive-ttp-analysis">
      <div className="analysis-header">
        <div className="header-content">
          <h1>
            <i className="fas fa-chess-board"></i>
            Interactive MITRE ATT&CK Analysis
          </h1>
          <p>Explore tactics, techniques, and procedures with interactive visualizations</p>
        </div>
        
        <div className="header-controls">
          <div className="time-range-selector">
            <label>Analysis Period:</label>
            <select 
              value={timeRange} 
              onChange={(e) => setTimeRange(parseInt(e.target.value))}
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
              <option value={180}>Last 180 days</option>
            </select>
          </div>
          
          <div className="animation-toggle">
            <label>
              <input
                type="checkbox"
                checked={animationEnabled}
                onChange={(e) => setAnimationEnabled(e.target.checked)}
              />
              Animations
            </label>
          </div>
          
          <button onClick={fetchAllTtpData} className="btn btn-outline">
            <i className="fas fa-refresh"></i>
            Refresh
          </button>
        </div>
      </div>

      <div className="interactive-tabs">
        <button 
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          <i className="fas fa-chart-pie"></i>
          <span>Overview</span>
        </button>
        
        <button 
          className={`tab-button ${activeTab === 'matrix' ? 'active' : ''}`}
          onClick={() => setActiveTab('matrix')}
        >
          <i className="fas fa-chess-board"></i>
          <span>Interactive Matrix</span>
        </button>
        
        <button 
          className={`tab-button ${activeTab === 'techniques' ? 'active' : ''}`}
          onClick={() => setActiveTab('techniques')}
        >
          <i className="fas fa-list"></i>
          <span>Techniques</span>
        </button>
        
        <button 
          className={`tab-button ${activeTab === 'trends' ? 'active' : ''}`}
          onClick={() => setActiveTab('trends')}
        >
          <i className="fas fa-chart-line"></i>
          <span>Trends</span>
        </button>
      </div>

      <div className="analysis-content">
        {activeTab === 'overview' && (
          <div className="overview-content">
            <div className="stats-dashboard">
              <div className="stat-card animated">
                <div className="stat-icon">
                  <i className="fas fa-chess-board"></i>
                </div>
                <div className="stat-content">
                  <h3>{mitreMatrix?.total_techniques || 0}</h3>
                  <p>MITRE Techniques</p>
                </div>
              </div>
              
              <div className="stat-card animated">
                <div className="stat-icon">
                  <i className="fas fa-chart-line"></i>
                </div>
                <div className="stat-content">
                  <h3>{techniqueFreqs?.total_observed || 0}</h3>
                  <p>Observed in Feeds</p>
                </div>
              </div>
              
              <div className="stat-card animated">
                <div className="stat-icon">
                  <i className="fas fa-exclamation-triangle"></i>
                </div>
                <div className="stat-content">
                  <h3>{techniqueFreqs?.high_frequency_count || 0}</h3>
                  <p>High Frequency TTPs</p>
                </div>
              </div>
              
              <div className="stat-card animated">
                <div className="stat-icon">
                  <i className="fas fa-rss"></i>
                </div>
                <div className="stat-content">
                  <h3>{feedComparison?.total_feeds || 0}</h3>
                  <p>Active Threat Feeds</p>
                </div>
              </div>
            </div>
            <InteractiveTechniquesList />
          </div>
        )}
        
        {activeTab === 'matrix' && <InteractiveMatrix />}
        {activeTab === 'techniques' && <InteractiveTechniquesList />}
        
        {activeTab === 'trends' && (
          <div className="trends-content">
            <h3>TTP Trends and Patterns</h3>
            <p>Trend analysis will be displayed here with interactive charts.</p>
          </div>
        )}
      </div>

      <TechniqueModal />

      <style jsx>{`
        .interactive-ttp-analysis {
          padding: 20px;
          max-width: 1600px;
          margin: 0 auto;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          min-height: 100vh;
          color: white;
        }

        .analysis-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 30px;
          background: rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(10px);
          padding: 25px;
          border-radius: 15px;
          border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .header-content h1 {
          margin: 0 0 8px 0;
          font-size: 32px;
          font-weight: 700;
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .header-content p {
          margin: 0;
          opacity: 0.9;
          font-size: 16px;
        }

        .header-controls {
          display: flex;
          align-items: center;
          gap: 20px;
        }

        .time-range-selector {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .time-range-selector select {
          padding: 10px 15px;
          border: 1px solid rgba(255, 255, 255, 0.3);
          border-radius: 8px;
          background: rgba(255, 255, 255, 0.1);
          color: white;
          backdrop-filter: blur(5px);
        }

        .animation-toggle label {
          display: flex;
          align-items: center;
          gap: 8px;
          cursor: pointer;
        }

        .interactive-tabs {
          display: flex;
          gap: 0;
          margin-bottom: 25px;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 12px;
          padding: 6px;
          backdrop-filter: blur(10px);
        }

        .tab-button {
          flex: 1;
          padding: 15px 25px;
          border: none;
          background: transparent;
          cursor: pointer;
          font-size: 14px;
          font-weight: 600;
          color: rgba(255, 255, 255, 0.7);
          border-radius: 8px;
          transition: all 0.3s ease;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 10px;
        }

        .tab-button:hover {
          background: rgba(255, 255, 255, 0.1);
          color: white;
          transform: translateY(-2px);
        }

        .tab-button.active {
          background: rgba(255, 255, 255, 0.2);
          color: white;
          box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }

        .analysis-content {
          background: rgba(255, 255, 255, 0.95);
          border-radius: 15px;
          padding: 30px;
          backdrop-filter: blur(10px);
          color: #333;
          min-height: 600px;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }

        .stats-dashboard {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 25px;
          margin-bottom: 40px;
        }

        .stat-card {
          display: flex;
          align-items: center;
          padding: 25px;
          background: linear-gradient(135deg, #667eea, #764ba2);
          border-radius: 12px;
          color: white;
          transition: all 0.3s ease;
          cursor: pointer;
        }

        .stat-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }

        .stat-card.animated {
          animation: slideInUp 0.6s ease-out;
        }

        .stat-icon {
          width: 60px;
          height: 60px;
          background: rgba(255, 255, 255, 0.2);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 24px;
          margin-right: 20px;
        }

        .stat-content h3 {
          margin: 0;
          font-size: 32px;
          font-weight: 700;
        }

        .stat-content p {
          margin: 5px 0 0 0;
          opacity: 0.9;
          font-size: 14px;
        }

        .interactive-matrix {
          margin-top: 20px;
        }

        .matrix-controls {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 25px;
          flex-wrap: wrap;
          gap: 15px;
        }

        .search-box {
          position: relative;
          flex: 1;
          max-width: 400px;
        }

        .search-box input {
          width: 100%;
          padding: 12px 45px 12px 45px;
          border: 2px solid #e9ecef;
          border-radius: 25px;
          font-size: 14px;
          transition: all 0.3s ease;
        }

        .search-box input:focus {
          outline: none;
          border-color: #007bff;
          box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
        }

        .search-box i {
          position: absolute;
          left: 15px;
          top: 50%;
          transform: translateY(-50%);
          color: #6c757d;
        }

        .clear-search {
          position: absolute;
          right: 15px;
          top: 50%;
          transform: translateY(-50%);
          background: none;
          border: none;
          color: #6c757d;
          cursor: pointer;
        }

        .filter-controls {
          display: flex;
          gap: 15px;
          align-items: center;
        }

        .filter-controls select {
          padding: 10px 15px;
          border: 2px solid #e9ecef;
          border-radius: 8px;
          background: white;
          cursor: pointer;
        }

        .view-toggle {
          display: flex;
          border: 2px solid #e9ecef;
          border-radius: 8px;
          overflow: hidden;
        }

        .view-toggle button {
          padding: 10px 15px;
          border: none;
          background: white;
          cursor: pointer;
          color: #6c757d;
          transition: all 0.2s ease;
        }

        .view-toggle button.active {
          background: #007bff;
          color: white;
        }

        .tactics-container {
          display: grid;
          gap: 20px;
        }

        .tactics-container.grid {
          grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
        }

        .tactics-container.list {
          grid-template-columns: 1fr;
        }

        .interactive-tactic-card {
          border: 2px solid transparent;
          border-radius: 12px;
          overflow: hidden;
          cursor: pointer;
          transition: all 0.3s ease;
          background: white;
        }

        .interactive-tactic-card:hover {
          border-color: rgba(0, 123, 255, 0.3);
          box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }

        .interactive-tactic-card.selected {
          border-color: #007bff;
          box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
        }

        .tactic-header {
          padding: 20px;
          color: white;
          display: flex;
          justify-content: space-between;
          align-items: center;
          transition: all 0.3s ease;
        }

        .tactic-header h4 {
          margin: 0;
          font-size: 18px;
          font-weight: 600;
        }

        .tactic-stats {
          text-align: right;
        }

        .technique-count {
          font-size: 24px;
          font-weight: 700;
          display: block;
        }

        .techniques-label {
          font-size: 12px;
          opacity: 0.9;
        }

        .tactic-techniques {
          padding: 20px;
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
        }

        .interactive-technique-chip {
          background: #f8f9fa;
          padding: 8px 12px;
          border-radius: 20px;
          font-size: 11px;
          font-family: monospace;
          color: #495057;
          cursor: pointer;
          transition: all 0.2s ease;
          display: flex;
          align-items: center;
          gap: 6px;
          border: 2px solid transparent;
        }

        .interactive-technique-chip:hover {
          background: #007bff;
          color: white;
          transform: translateY(-2px);
          border-color: #0056b3;
        }

        .technique-id {
          font-weight: 600;
        }

        .technique-frequency {
          background: rgba(0, 0, 0, 0.1);
          padding: 2px 6px;
          border-radius: 10px;
          font-size: 10px;
        }

        .show-more-chip {
          background: #e9ecef;
          padding: 8px 12px;
          border-radius: 20px;
          font-size: 11px;
          color: #6c757d;
          display: flex;
          align-items: center;
          gap: 4px;
        }

        .expanded-details {
          padding: 0 20px 20px;
          border-top: 1px solid #dee2e6;
          margin-top: 15px;
          padding-top: 15px;
        }

        .interactive-techniques-list {
          margin-top: 30px;
        }

        .list-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .list-header h3 {
          margin: 0;
          color: #333;
        }

        .result-count {
          color: #6c757d;
          font-size: 14px;
        }

        .techniques-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 15px;
        }

        .interactive-technique-item {
          display: flex;
          align-items: center;
          padding: 20px;
          background: white;
          border-radius: 12px;
          border: 2px solid #e9ecef;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .interactive-technique-item:hover {
          border-color: #007bff;
          transform: translateY(-3px);
          box-shadow: 0 8px 25px rgba(0, 123, 255, 0.1);
        }

        .technique-rank {
          width: 45px;
          height: 45px;
          background: linear-gradient(135deg, #28a745, #20c997);
          color: white;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 700;
          margin-right: 15px;
          font-size: 14px;
        }

        .technique-info {
          flex: 1;
        }

        .technique-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }

        .technique-id {
          font-family: monospace;
          font-weight: 700;
          color: #007bff;
          font-size: 14px;
        }

        .frequency-badge {
          background: #ffc107;
          color: white;
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 600;
        }

        .technique-name {
          color: #495057;
          font-size: 14px;
          margin-bottom: 8px;
          font-weight: 500;
        }

        .technique-meta {
          display: flex;
          gap: 8px;
        }

        .tactic-tag {
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 11px;
          font-weight: 600;
          color: #333;
        }

        .technique-modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.8);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          padding: 20px;
        }

        .technique-modal {
          background: white;
          border-radius: 15px;
          max-width: 600px;
          width: 100%;
          max-height: 80vh;
          overflow-y: auto;
          position: relative;
        }

        .modal-header {
          padding: 25px;
          border-bottom: 1px solid #dee2e6;
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
        }

        .technique-title h2 {
          margin: 0;
          color: #007bff;
          font-family: monospace;
          font-size: 24px;
        }

        .technique-title h3 {
          margin: 5px 0 0 0;
          color: #333;
          font-size: 18px;
          font-weight: 500;
        }

        .close-modal {
          background: none;
          border: none;
          font-size: 20px;
          color: #6c757d;
          cursor: pointer;
          padding: 5px;
        }

        .modal-content {
          padding: 25px;
        }

        .technique-stats {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
          gap: 20px;
          margin-bottom: 25px;
        }

        .stat-item {
          text-align: center;
          padding: 15px;
          background: #f8f9fa;
          border-radius: 8px;
        }

        .stat-label {
          display: block;
          font-size: 12px;
          color: #6c757d;
          margin-bottom: 5px;
          text-transform: uppercase;
          font-weight: 600;
        }

        .stat-value {
          font-size: 18px;
          font-weight: 700;
          color: #333;
        }

        .stat-value.risk-high { color: #dc3545; }
        .stat-value.risk-medium { color: #ffc107; }
        .stat-value.risk-low { color: #28a745; }

        .technique-details {
          margin-bottom: 25px;
        }

        .detail-section {
          margin-bottom: 20px;
        }

        .detail-section h4 {
          margin: 0 0 10px 0;
          color: #333;
          font-size: 16px;
        }

        .detail-section p {
          margin: 0;
          color: #6c757d;
          line-height: 1.6;
        }

        .related-techniques {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .related-chip {
          background: #e9ecef;
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 12px;
          color: #495057;
        }

        .modal-actions {
          display: flex;
          gap: 10px;
          padding-top: 20px;
          border-top: 1px solid #dee2e6;
        }

        .btn {
          padding: 12px 20px;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 600;
          transition: all 0.2s ease;
          display: inline-flex;
          align-items: center;
          gap: 8px;
          text-decoration: none;
        }

        .btn-primary {
          background: #007bff;
          color: white;
        }

        .btn-primary:hover {
          background: #0056b3;
          transform: translateY(-2px);
        }

        .btn-outline {
          background: transparent;
          border: 2px solid #007bff;
          color: #007bff;
        }

        .btn-outline:hover {
          background: #007bff;
          color: white;
        }

        .loading-state, .error-state {
          text-align: center;
          padding: 80px 20px;
        }

        .loading-animation {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 20px;
          margin-bottom: 20px;
        }

        .spinner {
          width: 50px;
          height: 50px;
          border: 4px solid rgba(255, 255, 255, 0.3);
          border-top: 4px solid white;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        .loading-dots {
          display: flex;
          gap: 5px;
        }

        .loading-dots span {
          width: 8px;
          height: 8px;
          background: white;
          border-radius: 50%;
          animation: bounce 1.4s ease-in-out infinite both;
        }

        .loading-dots span:nth-child(1) { animation-delay: -0.32s; }
        .loading-dots span:nth-child(2) { animation-delay: -0.16s; }

        .error-state i {
          font-size: 48px;
          color: #ffc107;
          margin-bottom: 20px;
        }

        .error-state h3 {
          margin: 0 0 15px 0;
          color: white;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        @keyframes bounce {
          0%, 80%, 100% { transform: scale(0); }
          40% { transform: scale(1); }
        }

        @keyframes slideInUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @media (max-width: 768px) {
          .analysis-header {
            flex-direction: column;
            gap: 20px;
            text-align: center;
          }

          .interactive-tabs {
            flex-direction: column;
          }

          .matrix-controls {
            flex-direction: column;
            align-items: stretch;
          }

          .search-box {
            max-width: none;
          }

          .filter-controls {
            justify-content: center;
            flex-wrap: wrap;
          }

          .tactics-container {
            grid-template-columns: 1fr;
          }

          .techniques-grid {
            grid-template-columns: 1fr;
          }

          .technique-modal {
            margin: 10px;
            max-height: 90vh;
          }
        }
      `}</style>
    </div>
  );
};

export default InteractiveTtpAnalysis;