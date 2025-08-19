import React, { useState, useEffect } from 'react';
import TrendVisualization from './TrendVisualization';
import ThreatPatternChart from './ThreatPatternChart';

const ReportDetailModal = ({ report, isOpen, onClose, api }) => {
  const [fullReportData, setFullReportData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen && report && api) {
      fetchFullReportData();
    }
  }, [isOpen, report, api]);

  const fetchFullReportData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Determine endpoint based on report data
      let endpoint = '';
      const sector = report.sector_focus || report.sector || '';
      const title = (report.title || '').toLowerCase();
      
      // Map sectors to endpoints
      const sectorEndpoints = {
        educational: '/api/reports/education-sector-analysis/',
        education: '/api/reports/education-sector-analysis/',
        financial: '/api/reports/financial-sector-analysis/',
        finance: '/api/reports/financial-sector-analysis/',
        government: '/api/reports/government-sector-analysis/',
        govt: '/api/reports/government-sector-analysis/'
      };
      
      // Try to find endpoint by sector first
      endpoint = sectorEndpoints[sector.toLowerCase()];
      
      // If not found, try by title keywords
      if (!endpoint) {
        for (const [key, value] of Object.entries(sectorEndpoints)) {
          if (title.includes(key)) {
            endpoint = value;
            break;
          }
        }
      }
      
      // Default to education sector if nothing matches
      if (!endpoint) {
        endpoint = '/api/reports/education-sector-analysis/';
      }

      const response = await api.get(endpoint);
      if (response && response.success && response.report) {
        setFullReportData(response.report);
      } else {
        throw new Error('Failed to fetch full report data');
      }
    } catch (err) {
      console.error('Error fetching full report data:', err);
      setError('Failed to load detailed report data');
      setFullReportData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = (format) => {
    if (!fullReportData && !report) {
      console.warn('No report data available for export');
      return;
    }

    const reportData = fullReportData || report;
    const filename = `${report?.title || 'Report'}_${new Date().toISOString().split('T')[0]}`;
    
    if (format === 'pdf') {
      // For now, open print dialog which can save as PDF
      window.print();
    } else if (format === 'csv') {
      // Create CSV from statistics data
      const stats = reportData.statistics || reportData.stats || [];
      if (stats.length === 0) {
        console.warn('No statistics data available for CSV export');
        return;
      }
      
      const csvContent = [
        'Label,Value',
        ...stats.map(stat => `"${stat.label}","${stat.value}"`)
      ].join('\n');
      
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', `${filename}.csv`);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="report-detail-modal-overlay" onClick={onClose}>
      <div className="report-detail-modal" onClick={(e) => e.stopPropagation()}>
        <div className="report-detail-header">
          <div>
            <h2 className="report-detail-title">{report?.title || 'Report Details'}</h2>
            <p className="report-detail-subtitle">
              {report?.type} • {report?.date}
            </p>
          </div>
          <div className="report-detail-actions">
            <button className="report-btn report-btn-outline report-btn-sm" onClick={() => handleExport('pdf')}>
              <i className="fas fa-file-pdf"></i> Export PDF
            </button>
            <button className="report-btn report-btn-outline report-btn-sm" onClick={() => handleExport('csv')}>
              <i className="fas fa-file-csv"></i> Export CSV
            </button>
            <button className="report-close-btn" onClick={onClose}>
              <i className="fas fa-times"></i>
            </button>
          </div>
        </div>

        <div className="report-detail-content">
          {loading ? (
            <div className="loading-section">
              <i className="fas fa-spinner fa-spin"></i>
              <p>Loading detailed report data...</p>
            </div>
          ) : error ? (
            <div className="error-section">
              <i className="fas fa-exclamation-triangle"></i>
              <h3>Error Loading Report</h3>
              <p>{error}</p>
              <button className="report-btn report-btn-primary" onClick={fetchFullReportData}>
                <i className="fas fa-redo"></i> Retry
              </button>
            </div>
          ) : (
            <div className="report-detail-wrapper">
              {/* Report Overview Section */}
              <div className="report-overview">
                <div className="overview-stats">
                  {(report?.statistics || report?.stats)?.map((stat, index) => (
                    <div key={index} className="overview-stat">
                      <div className="stat-value">{stat.value}</div>
                      <div className="stat-label">{stat.label}</div>
                    </div>
                  ))}
                </div>
                <div className="overview-description">
                  <h3>Executive Summary</h3>
                  <p>{report?.description || fullReportData?.description}</p>
                </div>
              </div>

              {/* Visualizations Section */}
              {fullReportData && (
                <div className="visualizations-section">
                  <h3>Analytics & Trends</h3>
                  
                  {/* Temporal Trends Chart */}
                  {fullReportData.temporal_trends && fullReportData.temporal_trends.length > 0 && (
                    <div className="chart-container">
                      <TrendVisualization 
                        temporalTrends={fullReportData.temporal_trends}
                        title="Temporal Threat Trends"
                      />
                    </div>
                  )}

                  {/* Threat Patterns Chart */}
                  {fullReportData.threat_patterns && (
                    <div className="chart-container">
                      <ThreatPatternChart 
                        threatPatterns={fullReportData.threat_patterns}
                        title="Threat Pattern Distribution"
                      />
                    </div>
                  )}

                  {/* Trust Insights */}
                  {fullReportData.trust_insights && (
                    <div className="trust-insights">
                      <h4>Trust Network Analysis</h4>
                      <div className="trust-metrics">
                        <div className="trust-metric">
                          <span className="metric-label">Total Relationships:</span>
                          <span className="metric-value">{fullReportData.trust_insights.total_relationships || 0}</span>
                        </div>
                        <div className="trust-metric">
                          <span className="metric-label">Internal Relationships:</span>
                          <span className="metric-value">{fullReportData.trust_insights.internal_relationships || 0}</span>
                        </div>
                        <div className="trust-metric">
                          <span className="metric-label">External Relationships:</span>
                          <span className="metric-value">{fullReportData.trust_insights.external_relationships || 0}</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Data Summary */}
                  {fullReportData.data_summary && (
                    <div className="data-summary">
                      <h4>Data Sources Summary</h4>
                      <div className="summary-grid">
                        <div className="summary-item">
                          <i className="fas fa-shield-alt"></i>
                          <span className="summary-label">Indicators Analyzed</span>
                          <span className="summary-value">{fullReportData.data_summary.indicators_analyzed}</span>
                        </div>
                        <div className="summary-item">
                          <i className="fas fa-crosshairs"></i>
                          <span className="summary-label">TTPs Analyzed</span>
                          <span className="summary-value">{fullReportData.data_summary.ttps_analyzed}</span>
                        </div>
                        <div className="summary-item">
                          <i className="fas fa-handshake"></i>
                          <span className="summary-label">Trust Relationships</span>
                          <span className="summary-value">{fullReportData.data_summary.trust_relationships}</span>
                        </div>
                        <div className="summary-item">
                          <i className="fas fa-building"></i>
                          <span className="summary-label">Organizations</span>
                          <span className="summary-value">{fullReportData.organizations_analyzed || 0}</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="report-detail-footer">
          <div className="report-meta">
            {fullReportData?.meta && (
              <small>
                Generated on {new Date(fullReportData.meta.generated_at).toLocaleString()} 
                by {fullReportData.meta.generated_by}
              </small>
            )}
          </div>
          <div className="report-detail-footer-actions">
            <button className="report-btn report-btn-secondary" onClick={onClose}>
              Close
            </button>
          </div>
        </div>
      </div>

      <style>{`
        /* Reset styles for modal */
        .report-detail-modal *, 
        .report-detail-modal *::before, 
        .report-detail-modal *::after {
          box-sizing: border-box;
        }

        .report-detail-modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.7);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          padding: 20px;
        }

        .report-detail-modal {
          background: white;
          border-radius: 16px;
          width: 95%;
          max-width: 1200px;
          max-height: 90vh;
          overflow: hidden;
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
          display: flex;
          flex-direction: column;
          position: relative;
        }

        .report-detail-header {
          padding: 24px 32px;
          border-bottom: 2px solid #f1f3f4;
          background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .report-detail-title {
          font-size: 24px;
          font-weight: 700;
          color: #1e3d59;
          margin: 0 0 4px 0;
        }

        .report-detail-subtitle {
          font-size: 14px;
          color: #666;
          margin: 0;
        }

        .report-detail-actions {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .report-close-btn {
          background: none;
          border: none;
          font-size: 20px;
          color: #666;
          cursor: pointer;
          padding: 8px;
          border-radius: 8px;
          transition: all 0.2s;
        }

        .report-close-btn:hover {
          background: #f8f9fa;
          color: #333;
        }

        .report-detail-content {
          flex: 1;
          overflow-y: auto;
          padding: 0;
          width: 100%;
          position: relative;
          display: flex;
          flex-direction: column;
        }

        .report-detail-content > * {
          width: 100%;
          flex-shrink: 0;
        }

        .report-detail-wrapper {
          width: 100% !important;
          display: flex !important;
          flex-direction: column !important;
          min-height: 100%;
          box-sizing: border-box !important;
        }

        .loading-section,
        .error-section {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 60px 20px;
          text-align: center;
        }

        .loading-section i {
          font-size: 40px;
          color: #1e3d59;
          margin-bottom: 20px;
        }

        .error-section i {
          font-size: 40px;
          color: #dc3545;
          margin-bottom: 20px;
        }

        .report-overview {
          padding: 32px;
          background: white;
          border-bottom: 1px solid #f1f3f4;
          width: 100% !important;
          box-sizing: border-box !important;
          display: block !important;
          position: relative;
        }

        .overview-stats {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 24px;
          margin-bottom: 32px;
          width: 100%;
          box-sizing: border-box;
        }

        .overview-stat {
          text-align: center;
          padding: 20px;
          background: linear-gradient(135deg, #f8f9ff 0%, #f0f8ff 100%);
          border-radius: 12px;
          border: 1px solid #e1e8ff;
        }

        .stat-value {
          font-size: 32px;
          font-weight: 700;
          color: #1e3d59;
          margin-bottom: 8px;
        }

        .stat-label {
          font-size: 14px;
          color: #666;
          font-weight: 500;
        }

        .overview-description {
          width: 100%;
          box-sizing: border-box;
          display: block;
        }

        .overview-description h3 {
          font-size: 20px;
          font-weight: 600;
          color: #1e3d59;
          margin-bottom: 16px;
        }

        .overview-description p {
          font-size: 16px;
          line-height: 1.6;
          color: #495057;
          margin: 0;
        }

        .visualizations-section {
          padding: 32px;
          background: #fafbfc;
          width: 100% !important;
          box-sizing: border-box !important;
          display: block !important;
          position: relative;
        }

        .visualizations-section > h3 {
          font-size: 24px;
          font-weight: 600;
          color: #1e3d59;
          margin-bottom: 32px;
          text-align: center;
        }

        .chart-container {
          margin-bottom: 32px;
          background: white;
          border-radius: 16px;
          padding: 20px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }

        .trust-insights {
          background: white;
          border-radius: 16px;
          padding: 24px;
          margin-bottom: 24px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }

        .trust-insights h4 {
          font-size: 18px;
          font-weight: 600;
          color: #1e3d59;
          margin-bottom: 20px;
        }

        .trust-metrics {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 16px;
        }

        .trust-metric {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 16px;
          background: #f8f9fa;
          border-radius: 8px;
          border-left: 4px solid #5a9fd4;
        }

        .metric-label {
          font-weight: 500;
          color: #495057;
        }

        .metric-value {
          font-weight: 700;
          color: #1e3d59;
          font-size: 18px;
        }

        .data-summary {
          background: white;
          border-radius: 16px;
          padding: 24px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }

        .data-summary h4 {
          font-size: 18px;
          font-weight: 600;
          color: #1e3d59;
          margin-bottom: 20px;
        }

        .summary-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 20px;
        }

        .summary-item {
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 20px;
          background: linear-gradient(135deg, #f8f9ff 0%, #f0f8ff 100%);
          border-radius: 12px;
          border: 1px solid #e1e8ff;
          text-align: center;
        }

        .summary-item i {
          font-size: 24px;
          color: #5a9fd4;
          margin-bottom: 12px;
        }

        .summary-label {
          font-size: 14px;
          color: #666;
          margin-bottom: 8px;
        }

        .summary-value {
          font-size: 24px;
          font-weight: 700;
          color: #1e3d59;
        }

        .report-detail-footer {
          padding: 20px 32px;
          border-top: 1px solid #f1f3f4;
          background: #fafbfc;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .report-meta small {
          color: #666;
          font-size: 13px;
        }

        .report-detail-footer-actions {
          display: flex;
          gap: 12px;
        }

        .report-btn {
          padding: 10px 20px;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
          display: inline-flex;
          align-items: center;
          gap: 8px;
          transition: all 0.2s;
          text-decoration: none;
        }

        .report-btn-primary {
          background: linear-gradient(135deg, #1e3d59 0%, #5a9fd4 100%);
          color: white;
        }

        .report-btn-primary:hover {
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(30, 61, 89, 0.3);
        }

        .report-btn-secondary {
          background: #6c757d;
          color: white;
        }

        .report-btn-secondary:hover {
          background: #5a6268;
        }

        .report-btn-outline {
          background: transparent;
          border: 2px solid #5a9fd4;
          color: #5a9fd4;
        }

        .report-btn-outline:hover {
          background: #5a9fd4;
          color: white;
        }

        .report-btn-sm {
          padding: 8px 16px;
          font-size: 12px;
        }

        @media (max-width: 768px) {
          .report-detail-modal {
            width: 100%;
            max-width: 100%;
            margin: 10px;
          }

          .report-detail-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 16px;
            padding: 20px;
          }

          .report-detail-actions {
            width: 100%;
            justify-content: space-between;
          }

          .report-overview,
          .visualizations-section {
            padding: 20px;
          }

          .overview-stats {
            grid-template-columns: 1fr 1fr;
            gap: 16px;
          }

          .trust-metrics {
            grid-template-columns: 1fr;
          }

          .summary-grid {
            grid-template-columns: 1fr 1fr;
          }

          .chart-container {
            padding: 12px;
          }
        }

        @media (max-width: 480px) {
          .overview-stats,
          .summary-grid {
            grid-template-columns: 1fr;
          }

          .report-detail-footer {
            flex-direction: column;
            gap: 12px;
            text-align: center;
          }
        }
      `}</style>
    </div>
  );
};

export default ReportDetailModal;