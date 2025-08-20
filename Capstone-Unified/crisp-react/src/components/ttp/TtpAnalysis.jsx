import React, { useState, useEffect } from 'react';
import * as api from '../../api.js';

const TtpAnalysis = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [timeRange, setTimeRange] = useState(30);
  
  // Data states
  const [mitreMatrix, setMitreMatrix] = useState(null);
  const [feedComparison, setFeedComparison] = useState(null);
  const [seasonalPatterns, setSeasonalPatterns] = useState(null);
  const [techniqueFreqs, setTechniqueFreqs] = useState(null);

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
        api.getTtpSeasonalPatterns(timeRange * 6), // 6x time range for seasonal analysis
        api.getTtpTechniqueFrequencies(timeRange)
      ]);

      if (matrixData.status === 'fulfilled') {
        setMitreMatrix(matrixData.value);
      } else {
        console.warn('Failed to fetch MITRE matrix:', matrixData.reason);
      }

      if (comparisonData.status === 'fulfilled') {
        setFeedComparison(comparisonData.value);
      } else {
        console.warn('Failed to fetch feed comparison:', comparisonData.reason);
      }

      if (patternsData.status === 'fulfilled') {
        setSeasonalPatterns(patternsData.value);
      } else {
        console.warn('Failed to fetch seasonal patterns:', patternsData.reason);
      }

      if (freqData.status === 'fulfilled') {
        setTechniqueFreqs(freqData.value);
      } else {
        console.warn('Failed to fetch technique frequencies:', freqData.reason);
      }

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getTacticColor = (tactic) => {
    const colors = {
      'initial-access': '#FF6B6B',
      'execution': '#4ECDC4',
      'persistence': '#45B7D1',
      'privilege-escalation': '#96CEB4',
      'defense-evasion': '#FECA57',
      'credential-access': '#FF9FF3',
      'discovery': '#54A0FF',
      'lateral-movement': '#5F27CD',
      'collection': '#00D2D3',
      'command-and-control': '#FF9F43',
      'exfiltration': '#EE5A24',
      'impact': '#EA2027'
    };
    return colors[tactic?.toLowerCase()] || '#6c757d';
  };

  const renderOverviewTab = () => (
    <div className="overview-content">
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-chess-board"></i>
          </div>
          <div className="stat-content">
            <h3>{mitreMatrix?.total_techniques || 0}</h3>
            <p>MITRE Techniques</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-chart-line"></i>
          </div>
          <div className="stat-content">
            <h3>{techniqueFreqs?.total_observed || 0}</h3>
            <p>Observed in Feeds</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-exclamation-triangle"></i>
          </div>
          <div className="stat-content">
            <h3>{techniqueFreqs?.high_frequency_count || 0}</h3>
            <p>High Frequency TTPs</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-rss"></i>
          </div>
          <div className="stat-content">
            <h3>{feedComparison?.total_feeds || 0}</h3>
            <p>Active Threat Feeds</p>
          </div>
        </div>
      </div>

      {techniqueFreqs?.top_techniques && (
        <div className="top-techniques">
          <h3>Most Frequent Techniques (Last {timeRange} days)</h3>
          <div className="techniques-list">
            {techniqueFreqs.top_techniques.slice(0, 10).map((technique, index) => (
              <div key={technique.technique_id || index} className="technique-item">
                <div className="technique-rank">#{index + 1}</div>
                <div className="technique-info">
                  <div className="technique-id">{technique.technique_id}</div>
                  <div className="technique-name">{technique.name}</div>
                </div>
                <div className="technique-stats">
                  <span className="frequency-count">{technique.frequency}</span>
                  <span className="frequency-label">occurrences</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderMatrixTab = () => (
    <div className="matrix-content">
      <div className="matrix-header">
        <h3>MITRE ATT&CK Matrix Coverage</h3>
        <div className="matrix-legend">
          <div className="legend-item">
            <div className="legend-color high-coverage"></div>
            <span>High Coverage (5+ techniques)</span>
          </div>
          <div className="legend-item">
            <div className="legend-color medium-coverage"></div>
            <span>Medium Coverage (2-4 techniques)</span>
          </div>
          <div className="legend-item">
            <div className="legend-color low-coverage"></div>
            <span>Low Coverage (1 technique)</span>
          </div>
          <div className="legend-item">
            <div className="legend-color no-coverage"></div>
            <span>No Coverage</span>
          </div>
        </div>
      </div>
      
      {mitreMatrix?.tactics && (
        <div className="tactics-grid">
          {Object.entries(mitreMatrix.tactics).map(([tacticId, tacticData]) => (
            <div key={tacticId} className="tactic-card">
              <div 
                className="tactic-header"
                style={{ backgroundColor: getTacticColor(tacticId) }}
              >
                <h4>{tacticData.name}</h4>
                <span className="technique-count">
                  {tacticData.techniques?.length || 0} techniques
                </span>
              </div>
              <div className="tactic-techniques">
                {tacticData.techniques?.slice(0, 8).map((technique) => (
                  <div 
                    key={technique.technique_id} 
                    className="technique-chip"
                    title={`${technique.technique_id}: ${technique.name}`}
                  >
                    {technique.technique_id}
                  </div>
                ))}
                {tacticData.techniques?.length > 8 && (
                  <div className="technique-chip more">
                    +{tacticData.techniques.length - 8} more
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderFeedComparisonTab = () => (
    <div className="feed-comparison-content">
      <h3>TTP Coverage by Threat Feed</h3>
      
      {feedComparison?.feeds && (
        <div className="feeds-comparison">
          {feedComparison.feeds.map((feed, index) => (
            <div key={feed.feed_id || index} className="feed-card">
              <div className="feed-header">
                <h4>{feed.name}</h4>
                <div className="feed-stats">
                  <span className="ttp-count">{feed.ttp_count} TTPs</span>
                  <span className="coverage-percent">
                    {((feed.ttp_count / feedComparison.total_unique_ttps) * 100).toFixed(1)}% coverage
                  </span>
                </div>
              </div>
              
              <div className="feed-progress">
                <div 
                  className="feed-progress-bar"
                  style={{ 
                    width: `${(feed.ttp_count / feedComparison.total_unique_ttps) * 100}%`,
                    backgroundColor: getTacticColor(`feed-${index}`)
                  }}
                ></div>
              </div>
              
              {feed.top_tactics && (
                <div className="feed-tactics">
                  <strong>Top Tactics:</strong>
                  {feed.top_tactics.slice(0, 3).map((tactic, i) => (
                    <span key={i} className="tactic-tag">
                      {tactic.name} ({tactic.count})
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderTrendsTab = () => (
    <div className="trends-content">
      <h3>TTP Trends and Patterns</h3>
      
      {seasonalPatterns?.trends && (
        <div className="trends-section">
          <h4>Seasonal Patterns</h4>
          <div className="patterns-grid">
            {seasonalPatterns.trends.map((trend, index) => (
              <div key={index} className="trend-card">
                <h5>{trend.technique_name}</h5>
                <div className="trend-metric">
                  <span className="trend-value">{trend.change_percent}%</span>
                  <span className={`trend-direction ${trend.direction}`}>
                    <i className={`fas fa-arrow-${trend.direction === 'up' ? 'up' : 'down'}`}></i>
                    {trend.direction}
                  </span>
                </div>
                <p className="trend-description">{trend.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {techniqueFreqs?.emerging_techniques && (
        <div className="emerging-section">
          <h4>Emerging Techniques</h4>
          <div className="emerging-list">
            {techniqueFreqs.emerging_techniques.map((technique, index) => (
              <div key={index} className="emerging-item">
                <div className="emerging-icon">
                  <i className="fas fa-exclamation-circle"></i>
                </div>
                <div className="emerging-content">
                  <h5>{technique.technique_id}: {technique.name}</h5>
                  <p>First observed: {technique.first_seen}</p>
                  <p>Current frequency: {technique.frequency} occurrences</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  if (loading) {
    return (
      <div className="ttp-analysis">
        <div className="loading-state">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading TTP analysis data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="ttp-analysis">
        <div className="error-state">
          <i className="fas fa-exclamation-triangle"></i>
          <p>Error loading TTP analysis: {error}</p>
          <button onClick={fetchAllTtpData} className="btn btn-primary">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="ttp-analysis">
      <div className="analysis-header">
        <div className="header-content">
          <h1>TTP Analysis</h1>
          <p>Tactics, Techniques, and Procedures analysis based on MITRE ATT&CK framework</p>
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
          
          <button onClick={fetchAllTtpData} className="btn btn-outline">
            <i className="fas fa-refresh"></i>
            Refresh
          </button>
        </div>
      </div>

      <div className="analysis-tabs">
        <button 
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          <i className="fas fa-chart-pie"></i>
          Overview
        </button>
        
        <button 
          className={`tab-button ${activeTab === 'matrix' ? 'active' : ''}`}
          onClick={() => setActiveTab('matrix')}
        >
          <i className="fas fa-chess-board"></i>
          MITRE Matrix
        </button>
        
        <button 
          className={`tab-button ${activeTab === 'feeds' ? 'active' : ''}`}
          onClick={() => setActiveTab('feeds')}
        >
          <i className="fas fa-rss"></i>
          Feed Comparison
        </button>
        
        <button 
          className={`tab-button ${activeTab === 'trends' ? 'active' : ''}`}
          onClick={() => setActiveTab('trends')}
        >
          <i className="fas fa-chart-line"></i>
          Trends
        </button>
      </div>

      <div className="analysis-content">
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'matrix' && renderMatrixTab()}
        {activeTab === 'feeds' && renderFeedComparisonTab()}
        {activeTab === 'trends' && renderTrendsTab()}
      </div>

      <style jsx>{`
        .ttp-analysis {
          padding: 20px;
          max-width: 1400px;
          margin: 0 auto;
          background: #f8f9fa;
          min-height: 100vh;
        }

        .analysis-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 30px;
          background: white;
          padding: 20px;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .header-content h1 {
          margin: 0 0 5px 0;
          color: #333;
          font-size: 28px;
        }

        .header-content p {
          margin: 0;
          color: #6c757d;
          font-size: 16px;
        }

        .header-controls {
          display: flex;
          align-items: center;
          gap: 15px;
        }

        .time-range-selector {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .time-range-selector label {
          font-weight: 500;
          color: #495057;
        }

        .time-range-selector select {
          padding: 8px 12px;
          border: 1px solid #dee2e6;
          border-radius: 6px;
          background: white;
          cursor: pointer;
        }

        .analysis-tabs {
          display: flex;
          gap: 0;
          margin-bottom: 20px;
          background: white;
          border-radius: 8px;
          padding: 4px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .tab-button {
          flex: 1;
          padding: 12px 20px;
          border: none;
          background: transparent;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          color: #6c757d;
          border-radius: 6px;
          transition: all 0.2s;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
        }

        .tab-button:hover {
          background: #f8f9fa;
          color: #495057;
        }

        .tab-button.active {
          background: #007bff;
          color: white;
        }

        .analysis-content {
          background: white;
          border-radius: 12px;
          padding: 30px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          min-height: 500px;
        }

        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 20px;
          margin-bottom: 30px;
        }

        .stat-card {
          display: flex;
          align-items: center;
          padding: 20px;
          background: #f8f9ff;
          border-radius: 8px;
          border-left: 4px solid #007bff;
        }

        .stat-icon {
          width: 50px;
          height: 50px;
          background: #007bff;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 20px;
          margin-right: 15px;
        }

        .stat-content h3 {
          margin: 0;
          font-size: 24px;
          font-weight: 700;
          color: #333;
        }

        .stat-content p {
          margin: 5px 0 0 0;
          color: #6c757d;
          font-size: 14px;
        }

        .top-techniques {
          margin-top: 30px;
        }

        .top-techniques h3 {
          margin-bottom: 20px;
          color: #333;
        }

        .techniques-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .technique-item {
          display: flex;
          align-items: center;
          padding: 15px;
          background: #f8f9fa;
          border-radius: 8px;
          border-left: 4px solid #28a745;
        }

        .technique-rank {
          width: 40px;
          height: 40px;
          background: #28a745;
          color: white;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 600;
          margin-right: 15px;
        }

        .technique-info {
          flex: 1;
        }

        .technique-id {
          font-family: monospace;
          font-weight: 600;
          color: #007bff;
          margin-bottom: 4px;
        }

        .technique-name {
          color: #495057;
          font-size: 14px;
        }

        .technique-stats {
          text-align: right;
        }

        .frequency-count {
          font-size: 18px;
          font-weight: 600;
          color: #333;
          display: block;
        }

        .frequency-label {
          font-size: 12px;
          color: #6c757d;
        }

        .matrix-header {
          margin-bottom: 30px;
        }

        .matrix-legend {
          display: flex;
          flex-wrap: wrap;
          gap: 20px;
          margin-top: 15px;
        }

        .legend-item {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .legend-color {
          width: 16px;
          height: 16px;
          border-radius: 3px;
        }

        .high-coverage { background: #28a745; }
        .medium-coverage { background: #ffc107; }
        .low-coverage { background: #fd7e14; }
        .no-coverage { background: #dee2e6; }

        .tactics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 20px;
        }

        .tactic-card {
          border: 1px solid #dee2e6;
          border-radius: 8px;
          overflow: hidden;
        }

        .tactic-header {
          padding: 15px;
          color: white;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .tactic-header h4 {
          margin: 0;
          font-size: 16px;
        }

        .technique-count {
          font-size: 12px;
          opacity: 0.9;
        }

        .tactic-techniques {
          padding: 15px;
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .technique-chip {
          background: #e9ecef;
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 11px;
          font-family: monospace;
          color: #495057;
        }

        .technique-chip.more {
          background: #007bff;
          color: white;
        }

        .feeds-comparison {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .feed-card {
          border: 1px solid #dee2e6;
          border-radius: 8px;
          padding: 20px;
        }

        .feed-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 15px;
        }

        .feed-header h4 {
          margin: 0;
          color: #333;
        }

        .feed-stats {
          display: flex;
          gap: 15px;
          font-size: 14px;
        }

        .ttp-count {
          color: #007bff;
          font-weight: 600;
        }

        .coverage-percent {
          color: #28a745;
          font-weight: 600;
        }

        .feed-progress {
          background: #f8f9fa;
          border-radius: 10px;
          height: 8px;
          margin-bottom: 15px;
        }

        .feed-progress-bar {
          height: 100%;
          border-radius: 10px;
          transition: width 0.3s ease;
        }

        .feed-tactics {
          font-size: 14px;
          color: #6c757d;
        }

        .tactic-tag {
          display: inline-block;
          background: #e9ecef;
          padding: 2px 6px;
          border-radius: 3px;
          font-size: 12px;
          margin-left: 8px;
        }

        .trends-section, .emerging-section {
          margin-bottom: 40px;
        }

        .trends-section h4, .emerging-section h4 {
          margin-bottom: 20px;
          color: #333;
          padding-bottom: 10px;
          border-bottom: 2px solid #e9ecef;
        }

        .patterns-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 20px;
        }

        .trend-card {
          background: #f8f9fa;
          padding: 20px;
          border-radius: 8px;
          border-left: 4px solid #007bff;
        }

        .trend-card h5 {
          margin: 0 0 10px 0;
          color: #333;
        }

        .trend-metric {
          display: flex;
          align-items: center;
          gap: 10px;
          margin-bottom: 10px;
        }

        .trend-value {
          font-size: 18px;
          font-weight: 600;
          color: #007bff;
        }

        .trend-direction {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 12px;
          text-transform: uppercase;
          font-weight: 600;
        }

        .trend-direction.up {
          color: #dc3545;
        }

        .trend-direction.down {
          color: #28a745;
        }

        .trend-description {
          font-size: 14px;
          color: #6c757d;
          margin: 0;
        }

        .emerging-list {
          display: flex;
          flex-direction: column;
          gap: 15px;
        }

        .emerging-item {
          display: flex;
          align-items: flex-start;
          padding: 15px;
          background: #fff3cd;
          border-radius: 8px;
          border-left: 4px solid #ffc107;
        }

        .emerging-icon {
          width: 40px;
          height: 40px;
          background: #ffc107;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          margin-right: 15px;
          flex-shrink: 0;
        }

        .emerging-content h5 {
          margin: 0 0 8px 0;
          color: #333;
        }

        .emerging-content p {
          margin: 4px 0;
          font-size: 14px;
          color: #6c757d;
        }

        .btn {
          padding: 10px 20px;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          transition: all 0.2s;
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
        }

        .btn-outline {
          background: transparent;
          border: 1px solid #dee2e6;
          color: #495057;
        }

        .btn-outline:hover {
          background: #f8f9fa;
        }

        .loading-state, .error-state {
          text-align: center;
          padding: 60px 20px;
        }

        .loading-state i {
          font-size: 32px;
          color: #007bff;
          margin-bottom: 15px;
        }

        .error-state i {
          font-size: 32px;
          color: #dc3545;
          margin-bottom: 15px;
        }

        @media (max-width: 768px) {
          .analysis-header {
            flex-direction: column;
            gap: 20px;
          }

          .analysis-tabs {
            flex-direction: column;
          }

          .header-controls {
            flex-direction: column;
            width: 100%;
          }

          .stats-grid {
            grid-template-columns: 1fr;
          }

          .tactics-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default TtpAnalysis;