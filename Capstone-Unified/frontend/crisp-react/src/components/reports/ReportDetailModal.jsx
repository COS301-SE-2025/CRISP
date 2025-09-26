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

  const handleExportPDF = () => {
    if (!fullReportData && !report) {
      console.warn('No report data available for export');
      return;
    }

    // For now, open print dialog which can save as PDF
    // TODO: Implement proper PDF generation with report data
    window.print();
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
            <button className="report-btn report-btn-outline report-btn-sm" onClick={handleExportPDF}>
              <i className="fas fa-file-pdf"></i> Export PDF
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

              {/* IOC Breakdown Section */}
              {fullReportData && fullReportData.indicators && (
                <div className="ioc-breakdown-section">
                  <h3>Indicators of Compromise (IOCs)</h3>
                  <div className="ioc-stats-grid">
                    <div className="ioc-stat-card">
                      <div className="ioc-stat-number">{fullReportData.indicators.length}</div>
                      <div className="ioc-stat-label">Total IOCs</div>
                    </div>
                    <div className="ioc-stat-card">
                      <div className="ioc-stat-number">
                        {fullReportData.indicators.filter(ioc => ioc.severity === 'high' || ioc.severity === 'critical').length}
                      </div>
                      <div className="ioc-stat-label">High/Critical Severity</div>
                    </div>
                    <div className="ioc-stat-card">
                      <div className="ioc-stat-number">
                        {[...new Set(fullReportData.indicators.map(ioc => ioc.type))].length}
                      </div>
                      <div className="ioc-stat-label">IOC Types</div>
                    </div>
                  </div>

                  <div className="ioc-details">
                    <h4>IOC Details</h4>
                    <div className="ioc-table-container">
                      <table className="ioc-table">
                        <thead>
                          <tr>
                            <th>Type</th>
                            <th>Value</th>
                            <th>Severity</th>
                            <th>First Seen</th>
                            <th>Source</th>
                          </tr>
                        </thead>
                        <tbody>
                          {fullReportData.indicators.slice(0, 10).map((ioc, index) => (
                            <tr key={index}>
                              <td>
                                <span className={`ioc-type-badge ${ioc.type}`}>
                                  {ioc.type?.toUpperCase() || 'UNKNOWN'}
                                </span>
                              </td>
                              <td className="ioc-value">{ioc.value || 'N/A'}</td>
                              <td>
                                <span className={`severity-badge ${ioc.severity || 'medium'}`}>
                                  {(ioc.severity || 'medium').toUpperCase()}
                                </span>
                              </td>
                              <td>{new Date(ioc.first_seen || ioc.created_at).toLocaleDateString()}</td>
                              <td>{ioc.source || 'Internal'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      {fullReportData.indicators.length > 10 && (
                        <div className="ioc-table-footer">
                          <p>Showing 10 of {fullReportData.indicators.length} indicators</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* TTP Analysis Section */}
              {fullReportData && fullReportData.ttps && (
                <div className="ttp-analysis-section">
                  <h3>Tactics, Techniques & Procedures (TTPs)</h3>
                  <div className="ttp-stats-grid">
                    <div className="ttp-stat-card">
                      <div className="ttp-stat-number">{fullReportData.ttps.length}</div>
                      <div className="ttp-stat-label">Total TTPs</div>
                    </div>
                    <div className="ttp-stat-card">
                      <div className="ttp-stat-number">
                        {[...new Set(fullReportData.ttps.map(ttp => ttp.tactic))].filter(t => t).length}
                      </div>
                      <div className="ttp-stat-label">MITRE Tactics</div>
                    </div>
                    <div className="ttp-stat-card">
                      <div className="ttp-stat-number">
                        {[...new Set(fullReportData.ttps.map(ttp => ttp.mitre_technique_id))].filter(t => t).length}
                      </div>
                      <div className="ttp-stat-label">Unique Techniques</div>
                    </div>
                  </div>

                  <div className="ttp-details">
                    <h4>MITRE ATT&CK Techniques</h4>
                    <div className="ttp-grid">
                      {fullReportData.ttps.slice(0, 12).map((ttp, index) => (
                        <div key={index} className="ttp-card">
                          <div className="ttp-header">
                            <div className="ttp-technique-id">
                              {ttp.mitre_technique_id || 'N/A'}
                            </div>
                            <div className={`ttp-tactic ${(ttp.tactic || '').toLowerCase().replace(/\s+/g, '-')}`}>
                              {ttp.tactic || 'Unknown'}
                            </div>
                          </div>
                          <div className="ttp-title">
                            {ttp.technique || ttp.name || 'Unknown Technique'}
                          </div>
                          <div className="ttp-description">
                            {ttp.description ?
                              (ttp.description.length > 100 ?
                                `${ttp.description.substring(0, 100)}...` :
                                ttp.description
                              ) :
                              'No description available'
                            }
                          </div>
                          <div className="ttp-meta">
                            <small>First seen: {new Date(ttp.created_at).toLocaleDateString()}</small>
                          </div>
                        </div>
                      ))}
                    </div>
                    {fullReportData.ttps.length > 12 && (
                      <div className="ttp-footer">
                        <p>Showing 12 of {fullReportData.ttps.length} techniques</p>
                      </div>
                    )}
                  </div>

                  <div className="mitre-attack-chain">
                    <h4>Attack Chain Analysis</h4>
                    <div className="attack-phases">
                      {['initial-access', 'execution', 'persistence', 'privilege-escalation', 'defense-evasion', 'credential-access', 'discovery', 'lateral-movement', 'collection', 'exfiltration', 'impact'].map(phase => {
                        const phaseTtps = fullReportData.ttps.filter(ttp =>
                          (ttp.tactic || '').toLowerCase().includes(phase.replace('-', ' ')) ||
                          (ttp.tactic || '').toLowerCase().includes(phase.replace('-', '_'))
                        );
                        return phaseTtps.length > 0 ? (
                          <div key={phase} className="attack-phase">
                            <div className="phase-header">
                              <span className={`phase-icon ${phase}`}></span>
                              <span className="phase-name">{phase.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                              <span className="phase-count">{phaseTtps.length}</span>
                            </div>
                          </div>
                        ) : null;
                      })}
                    </div>
                  </div>
                </div>
              )}

              {/* Organization Impact Assessment Section */}
              {fullReportData && (
                <div className="organization-impact-section">
                  <h3>Organization Impact Assessment</h3>

                  {/* Impact Overview */}
                  <div className="impact-stats-grid">
                    <div className="impact-stat-card">
                      <div className="impact-stat-number">
                        {fullReportData.organizations ? fullReportData.organizations.length : 1}
                      </div>
                      <div className="impact-stat-label">Organizations Analyzed</div>
                    </div>
                    <div className="impact-stat-card">
                      <div className="impact-stat-number">
                        {report?.sector ? 1 : '3+'}
                      </div>
                      <div className="impact-stat-label">Sectors Affected</div>
                    </div>
                    <div className="impact-stat-card">
                      <div className="impact-stat-number">
                        {fullReportData.indicators ? fullReportData.indicators.filter(ioc =>
                          ioc.severity === 'high' || ioc.severity === 'critical'
                        ).length : 0}
                      </div>
                      <div className="impact-stat-label">Critical Threats</div>
                    </div>
                    <div className="impact-stat-card">
                      <div className="impact-stat-number">
                        {fullReportData.ttps ? [...new Set(fullReportData.ttps.map(ttp => ttp.tactic))].filter(t => t).length : 0}
                      </div>
                      <div className="impact-stat-label">Attack Vectors</div>
                    </div>
                  </div>

                  {/* Sector Analysis */}
                  <div className="sector-analysis">
                    <h4>Sector-Specific Analysis</h4>
                    <div className="sector-cards">
                      <div className="sector-card">
                        <div className="sector-header">
                          <div className="sector-icon">
                            {report?.sector === 'education' ? 'EDU' :
                             report?.sector === 'financial' ? 'FIN' :
                             report?.sector === 'government' ? 'GOV' : 'ORG'}
                          </div>
                          <div className="sector-name">
                            {report?.sector ?
                              `${report.sector.charAt(0).toUpperCase() + report.sector.slice(1)} Sector` :
                              'Multi-Sector Analysis'
                            }
                          </div>
                        </div>
                        <div className="sector-details">
                          <div className="sector-metric">
                            <span className="metric-label">Primary Risk Level:</span>
                            <span className={`risk-level ${
                              (fullReportData.indicators?.filter(ioc =>
                                ioc.severity === 'critical'
                              ).length || 0) > 5 ? 'critical' :
                              (fullReportData.indicators?.filter(ioc =>
                                ioc.severity === 'high'
                              ).length || 0) > 10 ? 'high' : 'medium'
                            }`}>
                              {(fullReportData.indicators?.filter(ioc =>
                                ioc.severity === 'critical'
                              ).length || 0) > 5 ? 'Critical' :
                              (fullReportData.indicators?.filter(ioc =>
                                ioc.severity === 'high'
                              ).length || 0) > 10 ? 'High' : 'Medium'}
                            </span>
                          </div>
                          <div className="sector-metric">
                            <span className="metric-label">Common Attack Patterns:</span>
                            <span className="metric-value">
                              {fullReportData.ttps ?
                                [...new Set(fullReportData.ttps.slice(0, 3).map(ttp => ttp.tactic))].filter(t => t).join(', ') :
                                'Data Breach, Phishing, Malware'
                              }
                            </span>
                          </div>
                          <div className="sector-metric">
                            <span className="metric-label">Compliance Impact:</span>
                            <span className="metric-value">
                              {report?.sector === 'financial' ? 'PCI DSS, SOX' :
                               report?.sector === 'government' ? 'FedRAMP, FISMA' :
                               report?.sector === 'education' ? 'FERPA, COPPA' :
                               'Industry Standards'}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Vulnerability Assessment */}
                  <div className="vulnerability-assessment">
                    <h4>Key Vulnerabilities & Recommendations</h4>
                    <div className="vulnerability-grid">
                      <div className="vulnerability-card">
                        <div className="vuln-header">
                          <div className="vuln-severity critical">Critical</div>
                          <div className="vuln-title">Advanced Persistent Threats</div>
                        </div>
                        <div className="vuln-description">
                          Multiple sophisticated attack patterns detected targeting {report?.sector || 'multiple sectors'}.
                          Immediate response and enhanced monitoring recommended.
                        </div>
                        <div className="vuln-recommendations">
                          <h5>Recommendations:</h5>
                          <ul>
                            <li>Implement zero-trust architecture</li>
                            <li>Deploy advanced endpoint detection</li>
                            <li>Enhance security awareness training</li>
                          </ul>
                        </div>
                      </div>

                      <div className="vulnerability-card">
                        <div className="vuln-header">
                          <div className="vuln-severity high">High</div>
                          <div className="vuln-title">Data Exfiltration Risks</div>
                        </div>
                        <div className="vuln-description">
                          Indicators suggest potential data exfiltration attempts with focus on sensitive information.
                        </div>
                        <div className="vuln-recommendations">
                          <h5>Recommendations:</h5>
                          <ul>
                            <li>Implement data loss prevention (DLP)</li>
                            <li>Review access controls and permissions</li>
                            <li>Monitor network traffic for anomalies</li>
                          </ul>
                        </div>
                      </div>

                      <div className="vulnerability-card">
                        <div className="vuln-header">
                          <div className="vuln-severity medium">Medium</div>
                          <div className="vuln-title">Supply Chain Concerns</div>
                        </div>
                        <div className="vuln-description">
                          Third-party vendor and supply chain security may be compromised based on threat patterns.
                        </div>
                        <div className="vuln-recommendations">
                          <h5>Recommendations:</h5>
                          <ul>
                            <li>Conduct vendor security assessments</li>
                            <li>Implement secure software development</li>
                            <li>Review third-party access controls</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Organization Details */}
                  {fullReportData.organizations && fullReportData.organizations.length > 0 && (
                    <div className="organization-details">
                      <h4>Affected Organizations</h4>
                      <div className="org-list">
                        {fullReportData.organizations.slice(0, 5).map((org, index) => (
                          <div key={index} className="org-item">
                            <div className="org-info">
                              <div className="org-name">{org.name || `Organization ${index + 1}`}</div>
                              <div className="org-type">{org.organization_type || 'Unknown Type'}</div>
                            </div>
                            <div className="org-risk">
                              <div className={`risk-indicator ${
                                (org.threat_level || Math.random() > 0.5) ? 'high' : 'medium'
                              }`}>
                                {(org.threat_level || Math.random() > 0.5) ? 'High Risk' : 'Medium Risk'}
                              </div>
                            </div>
                          </div>
                        ))}
                        {fullReportData.organizations.length > 5 && (
                          <div className="org-footer">
                            <p>+{fullReportData.organizations.length - 5} more organizations</p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}

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
          background: #f8f9fa;
          border-radius: 12px;
          width: 95%;
          max-width: 1200px;
          max-height: 90vh;
          overflow: hidden;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          display: flex;
          flex-direction: column;
          position: relative;
        }

        .report-detail-header {
          padding: 20px;
          background: white;
          border-radius: 12px 12px 0 0;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .report-detail-title {
          font-size: 28px;
          font-weight: 700;
          color: #333;
          margin: 0 0 5px 0;
        }

        .report-detail-subtitle {
          font-size: 16px;
          color: #6c757d;
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
          padding: 0 20px 20px 20px;
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
          background: white;
          border-radius: 12px;
          padding: 24px;
          margin-bottom: 20px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          width: 100% !important;
          box-sizing: border-box !important;
          display: block !important;
          position: relative;
        }

        .overview-stats {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
          gap: 15px;
          margin-bottom: 24px;
          width: 100%;
          box-sizing: border-box;
        }

        .overview-stat {
          text-align: center;
          padding: 16px;
          background: white;
          border-radius: 8px;
          border: 1px solid #dee2e6;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .stat-value {
          font-size: 24px;
          font-weight: 700;
          color: #333;
          margin-bottom: 4px;
        }

        .stat-label {
          font-size: 12px;
          color: #6c757d;
          font-weight: 500;
        }

        .overview-description {
          width: 100%;
          box-sizing: border-box;
          display: block;
        }

        .overview-description h3 {
          font-size: 18px;
          font-weight: 600;
          color: #333;
          margin-bottom: 16px;
        }

        .overview-description p {
          font-size: 16px;
          line-height: 1.6;
          color: #495057;
          margin: 0;
        }

        .ioc-breakdown-section {
          background: white;
          border-radius: 12px;
          padding: 24px;
          margin-bottom: 20px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          width: 100% !important;
          box-sizing: border-box !important;
        }

        .ioc-breakdown-section h3 {
          margin: 0 0 20px 0;
          color: #333;
          font-size: 18px;
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .ioc-breakdown-section h3:before {
          content: "◆";
          font-size: 20px;
        }

        .ioc-breakdown-section h4 {
          margin: 20px 0 15px 0;
          color: #333;
          font-size: 16px;
          font-weight: 600;
        }

        .ioc-stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
          gap: 15px;
          margin-bottom: 24px;
        }

        .ioc-stat-card {
          text-align: center;
          padding: 16px;
          background: white;
          border-radius: 8px;
          border: 1px solid #dee2e6;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .ioc-stat-number {
          font-size: 24px;
          font-weight: 700;
          color: #dc3545;
          margin-bottom: 4px;
        }

        .ioc-stat-label {
          font-size: 12px;
          color: #6c757d;
          font-weight: 500;
        }

        .ioc-details {
          margin-top: 24px;
        }

        .ioc-table-container {
          background: white;
          border-radius: 12px;
          overflow: hidden;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
          border: 1px solid #f1f3f4;
        }

        .ioc-table {
          width: 100%;
          border-collapse: collapse;
        }

        .ioc-table th {
          background: #f8f9fa;
          padding: 16px 12px;
          text-align: left;
          font-weight: 600;
          color: #495057;
          font-size: 14px;
          border-bottom: 2px solid #e9ecef;
        }

        .ioc-table td {
          padding: 12px;
          border-bottom: 1px solid #f1f3f4;
          font-size: 14px;
        }

        .ioc-table tbody tr:hover {
          background: #f8f9fa;
        }

        .ioc-type-badge {
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 600;
          color: white;
          background: #6c757d;
        }

        .ioc-type-badge.ip {
          background: #007bff;
        }

        .ioc-type-badge.domain {
          background: #28a745;
        }

        .ioc-type-badge.hash {
          background: #dc3545;
        }

        .ioc-type-badge.url {
          background: #fd7e14;
        }

        .ioc-type-badge.email {
          background: #6f42c1;
        }

        .ioc-value {
          font-family: 'Courier New', monospace;
          color: #495057;
          word-break: break-all;
          max-width: 200px;
        }

        .severity-badge {
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 600;
          color: white;
        }

        .severity-badge.low {
          background: #28a745;
        }

        .severity-badge.medium {
          background: #ffc107;
          color: #212529;
        }

        .severity-badge.high {
          background: #fd7e14;
        }

        .severity-badge.critical {
          background: #dc3545;
        }

        .ioc-table-footer {
          padding: 16px;
          background: #f8f9fa;
          text-align: center;
          border-top: 1px solid #e9ecef;
        }

        .ioc-table-footer p {
          margin: 0;
          color: #666;
          font-size: 14px;
        }

        .ttp-analysis-section {
          background: white;
          border-radius: 12px;
          padding: 24px;
          margin-bottom: 20px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          width: 100% !important;
          box-sizing: border-box !important;
        }

        .ttp-analysis-section h3 {
          margin: 0 0 20px 0;
          color: #333;
          font-size: 18px;
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .ttp-analysis-section h3:before {
          content: "▲";
          font-size: 20px;
        }

        .ttp-analysis-section h4 {
          margin: 20px 0 15px 0;
          color: #333;
          font-size: 16px;
          font-weight: 600;
        }

        .ttp-stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
          gap: 15px;
          margin-bottom: 24px;
        }

        .ttp-stat-card {
          text-align: center;
          padding: 16px;
          background: white;
          border-radius: 8px;
          border: 1px solid #dee2e6;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .ttp-stat-number {
          font-size: 24px;
          font-weight: 700;
          color: #007bff;
          margin-bottom: 4px;
        }

        .ttp-stat-label {
          font-size: 12px;
          color: #6c757d;
          font-weight: 500;
        }

        .ttp-details {
          margin-bottom: 32px;
        }

        .ttp-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 20px;
          margin-bottom: 16px;
        }

        .ttp-card {
          background: white;
          border: 1px solid #e9ecef;
          border-radius: 12px;
          padding: 20px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
          transition: all 0.2s;
        }

        .ttp-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        }

        .ttp-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }

        .ttp-technique-id {
          background: #495057;
          color: white;
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 600;
          font-family: 'Courier New', monospace;
        }

        .ttp-tactic {
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 600;
          color: white;
          background: #6c757d;
        }

        .ttp-tactic.initial-access {
          background: #e74c3c;
        }

        .ttp-tactic.execution {
          background: #f39c12;
        }

        .ttp-tactic.persistence {
          background: #f1c40f;
        }

        .ttp-tactic.privilege-escalation {
          background: #e67e22;
        }

        .ttp-tactic.defense-evasion {
          background: #9b59b6;
        }

        .ttp-tactic.credential-access {
          background: #3498db;
        }

        .ttp-tactic.discovery {
          background: #1abc9c;
        }

        .ttp-tactic.lateral-movement {
          background: #27ae60;
        }

        .ttp-tactic.collection {
          background: #2980b9;
        }

        .ttp-tactic.exfiltration {
          background: #8e44ad;
        }

        .ttp-tactic.impact {
          background: #c0392b;
        }

        .ttp-title {
          font-size: 16px;
          font-weight: 600;
          color: #2c5aa0;
          margin-bottom: 8px;
          line-height: 1.3;
        }

        .ttp-description {
          font-size: 14px;
          color: #666;
          line-height: 1.4;
          margin-bottom: 12px;
        }

        .ttp-meta {
          border-top: 1px solid #f1f3f4;
          padding-top: 8px;
        }

        .ttp-meta small {
          color: #999;
          font-size: 12px;
        }

        .ttp-footer {
          text-align: center;
          padding: 16px;
          color: #666;
          font-size: 14px;
        }

        .mitre-attack-chain {
          margin-top: 24px;
        }

        .attack-phases {
          display: flex;
          flex-wrap: wrap;
          gap: 12px;
          justify-content: center;
        }

        .attack-phase {
          background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
          border: 1px solid #dee2e6;
          border-radius: 8px;
          padding: 12px 16px;
          min-width: 140px;
          text-align: center;
        }

        .phase-header {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 4px;
        }

        .phase-icon {
          width: 12px;
          height: 12px;
          border-radius: 50%;
          background: #6c757d;
        }

        .phase-name {
          font-size: 12px;
          font-weight: 600;
          color: #495057;
        }

        .phase-count {
          background: #007bff;
          color: white;
          padding: 2px 6px;
          border-radius: 10px;
          font-size: 11px;
          font-weight: 600;
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


          .chart-container {
            padding: 12px;
          }
        }

        @media (max-width: 480px) {
          .overview-stats,

          .report-detail-footer {
            flex-direction: column;
            gap: 12px;
            text-align: center;
          }
        }

        /* Organization Impact Assessment Styles */
        .organization-impact-section {
          background: white;
          border-radius: 12px;
          padding: 24px;
          margin-bottom: 20px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          width: 100% !important;
          box-sizing: border-box !important;
        }

        .organization-impact-section h3 {
          margin: 0 0 20px 0;
          color: #333;
          font-size: 18px;
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .organization-impact-section h3:before {
          content: "■";
          font-size: 20px;
        }

        .organization-impact-section h4 {
          margin: 20px 0 15px 0;
          color: #333;
          font-size: 16px;
          font-weight: 600;
        }

        .impact-stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
          gap: 15px;
          margin-bottom: 24px;
        }

        .impact-stat-card {
          text-align: center;
          padding: 16px;
          background: white;
          border-radius: 8px;
          border: 1px solid #dee2e6;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .impact-stat-number {
          font-size: 24px;
          font-weight: 700;
          color: #007bff;
          margin-bottom: 4px;
        }

        .impact-stat-label {
          font-size: 12px;
          color: #6c757d;
          font-weight: 500;
        }

        .sector-analysis {
          margin-bottom: 24px;
        }

        .sector-cards {
          display: grid;
          gap: 16px;
        }

        .sector-card {
          background: white;
          border: 1px solid #e9ecef;
          border-radius: 12px;
          padding: 20px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }

        .sector-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 16px;
        }

        .sector-icon {
          width: 40px;
          height: 40px;
          background: #007bff;
          color: white;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 600;
          font-size: 12px;
        }

        .sector-name {
          font-size: 16px;
          font-weight: 600;
          color: #333;
        }

        .sector-details {
          display: grid;
          gap: 12px;
        }

        .sector-metric {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 8px 0;
          border-bottom: 1px solid #f1f3f4;
        }

        .metric-label {
          font-weight: 500;
          color: #666;
          font-size: 14px;
        }

        .metric-value {
          color: #333;
          font-size: 14px;
        }

        .risk-level {
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 600;
          text-transform: uppercase;
        }

        .risk-level.critical {
          background: #ffeaa7;
          color: #d63031;
        }

        .risk-level.high {
          background: #ffeaa7;
          color: #e17055;
        }

        .risk-level.medium {
          background: #dff0d8;
          color: #3c763d;
        }

        .vulnerability-assessment {
          margin-bottom: 24px;
        }

        .vulnerability-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
          gap: 20px;
        }

        .vulnerability-card {
          background: white;
          border: 1px solid #e9ecef;
          border-radius: 12px;
          padding: 20px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }

        .vuln-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 12px;
        }

        .vuln-severity {
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 11px;
          font-weight: 600;
          text-transform: uppercase;
        }

        .vuln-severity.critical {
          background: #ffeaa7;
          color: #d63031;
        }

        .vuln-severity.high {
          background: #ffeaa7;
          color: #e17055;
        }

        .vuln-severity.medium {
          background: #dff0d8;
          color: #3c763d;
        }

        .vuln-title {
          font-weight: 600;
          color: #333;
          font-size: 14px;
        }

        .vuln-description {
          color: #666;
          font-size: 14px;
          line-height: 1.5;
          margin-bottom: 16px;
        }

        .vuln-recommendations {
          border-top: 1px solid #f1f3f4;
          padding-top: 12px;
        }

        .vuln-recommendations h5 {
          margin: 0 0 8px 0;
          font-size: 13px;
          color: #333;
          font-weight: 600;
        }

        .vuln-recommendations ul {
          margin: 0;
          padding-left: 16px;
          color: #666;
          font-size: 13px;
        }

        .vuln-recommendations li {
          margin-bottom: 4px;
        }

        .organization-details {
          margin-bottom: 24px;
        }

        .org-list {
          display: grid;
          gap: 12px;
        }

        .org-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px;
          background: white;
          border: 1px solid #e9ecef;
          border-radius: 8px;
          box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }

        .org-info {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .org-name {
          font-weight: 600;
          color: #333;
          font-size: 14px;
        }

        .org-type {
          color: #666;
          font-size: 12px;
          text-transform: capitalize;
        }

        .org-risk {
          display: flex;
          align-items: center;
        }

        .risk-indicator {
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 11px;
          font-weight: 600;
          text-transform: uppercase;
        }

        .risk-indicator.high {
          background: #ffeaa7;
          color: #e17055;
        }

        .risk-indicator.medium {
          background: #dff0d8;
          color: #3c763d;
        }

        .org-footer {
          text-align: center;
          padding: 12px;
          color: #666;
          font-size: 13px;
          border-top: 1px solid #f1f3f4;
          margin-top: 8px;
        }
      `}</style>
    </div>
  );
};

export default ReportDetailModal;