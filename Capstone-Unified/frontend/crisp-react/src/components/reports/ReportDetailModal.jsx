import React, { useState, useEffect } from 'react';

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

    const reportData = fullReportData || report;

    // Generate a comprehensive PDF-ready view with all report data
    const printWindow = window.open('', '_blank');

    // Create comprehensive PDF content
    const pdfContent = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>${reportData.title || report?.title}</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            margin: 40px;
            background: white;
            color: black;
            line-height: 1.6;
            font-size: 12px;
          }
          .report-header {
            border-bottom: 2px solid #333;
            padding-bottom: 20px;
            margin-bottom: 30px;
          }
          .report-title {
            font-size: 24px;
            font-weight: bold;
            margin: 0 0 10px 0;
            color: #333;
          }
          .report-meta {
            color: #666;
            font-size: 14px;
          }
          .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin: 30px 0;
          }
          .stat-card {
            border: 1px solid #ddd;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
          }
          .stat-number {
            font-size: 20px;
            font-weight: bold;
            color: #333;
          }
          .stat-label {
            font-size: 10px;
            color: #666;
            text-transform: uppercase;
          }
          .section {
            margin: 30px 0;
            page-break-inside: avoid;
          }
          .section-title {
            font-size: 18px;
            font-weight: bold;
            color: #333;
            border-bottom: 1px solid #ddd;
            padding-bottom: 5px;
            margin-bottom: 15px;
          }
          .ioc-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 10px;
          }
          .ioc-table th,
          .ioc-table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
          }
          .ioc-table th {
            background: #f8f9fa;
            font-weight: bold;
          }
          .ioc-value {
            font-family: monospace;
            word-break: break-all;
            max-width: 200px;
          }
          .chart-section {
            margin: 20px 0;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 8px;
          }
          .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #666;
            font-size: 10px;
          }
          @media print {
            body { margin: 20px; font-size: 11px; }
            .stats-grid { page-break-inside: avoid; }
            .section { page-break-inside: avoid; }
          }
        </style>
      </head>
      <body>
        <div class="report-header">
          <div class="report-title">${reportData.title || report?.title}</div>
          <div class="report-meta">
            Generated: ${report?.date || new Date().toLocaleDateString()} |
            Sector: ${reportData.sector_focus || 'General'}
          </div>
        </div>

        <div class="stats-grid">
          ${(reportData.statistics || report?.stats || []).map(stat => `
            <div class="stat-card">
              <div class="stat-number">${stat.value}</div>
              <div class="stat-label">${stat.label}</div>
            </div>
          `).join('')}
        </div>

        <div class="section">
          <div class="section-title">Summary</div>
          <p>${reportData.description || report?.description}</p>
        </div>

        ${reportData.indicators && reportData.indicators.length > 0 ? `
          <div class="section">
            <div class="section-title">Indicators of Compromise (IOCs) - Sample</div>
            <table class="ioc-table">
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Value</th>
                  <th>Target Organization</th>
                  <th>First Seen</th>
                </tr>
              </thead>
              <tbody>
                ${reportData.indicators.slice(0, 20).map(ioc => `
                  <tr>
                    <td>${ioc.type?.toUpperCase() || 'UNKNOWN'}</td>
                    <td class="ioc-value">${ioc.value || 'N/A'}</td>
                    <td>${ioc.target_organization || 'General'}</td>
                    <td>${new Date(ioc.first_seen || ioc.created_at).toLocaleDateString()}</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
            <p><em>Showing 20 of ${reportData.indicators.length} total indicators</em></p>
          </div>
        ` : ''}

        <div class="chart-section">
          <div class="section-title">Threat Type Distribution</div>
          <p>This report analyzed ${reportData.indicators?.length || 0} threat indicators across multiple types:</p>
          <ul>
            <li><strong>Domains:</strong> Primary threat vector detected</li>
            <li><strong>File Hashes:</strong> Malicious files identified</li>
            <li><strong>IP Addresses:</strong> Malicious infrastructure</li>
            <li><strong>URLs:</strong> Malicious web resources</li>
          </ul>
        </div>

        <div class="footer">
          <p>CRISP - Cyber Threat Intelligence Report</p>
          <p>Generated on ${new Date().toLocaleDateString()} at ${new Date().toLocaleTimeString()}</p>
          <p>This report contains ${reportData.indicators?.length || 0} indicators and ${reportData.ttps?.length || 0} TTPs</p>
        </div>
      </body>
      </html>
    `;

    printWindow.document.write(pdfContent);
    printWindow.document.close();

    // Wait for content to load, then trigger print
    setTimeout(() => {
      printWindow.focus();
      printWindow.print();
    }, 500);
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
              </div>

              {/* IOC Breakdown Section */}
              {fullReportData && fullReportData.indicators && (
                <div className="ioc-breakdown-section">
                  <h3>Indicators of Compromise (IOCs)</h3>

                  <div className="ioc-details">
                    <h4>IOC Details</h4>
                    <div className="ioc-table-container">
                      <table className="ioc-table">
                        <thead>
                          <tr>
                            <th>Type</th>
                            <th>Value</th>
                            <th>Source</th>
                            <th>Hash Type</th>
                            <th>Target Organization</th>
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
                                <span className={`source-badge`}>
                                  {ioc.threat_feed?.name || ioc.source || 'AlienVault OTX'}
                                </span>
                              </td>
                              <td>
                                {ioc.hash_type ? (
                                  <span className={`hash-type-badge ${ioc.hash_type}`}>
                                    {ioc.hash_type.toUpperCase()}
                                  </span>
                                ) : (
                                  <span className="hash-type-badge none">N/A</span>
                                )}
                              </td>
                              <td>
                                <span className={`target-org-badge ${
                                  ioc.target_organization === 'General' ? 'general' : 'targeted'
                                }`}>
                                  {ioc.target_organization || 'General'}
                                </span>
                              </td>
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

              {/* Key Metrics Visualization */}
              {fullReportData && (fullReportData.indicators || fullReportData.ttps) && (
                <div className="key-metrics-section">
                  <h3>Threat Intelligence Overview</h3>

                  <div className="metrics-chart-container">
                    <div className="metrics-chart">
                      <h4>Threat Indicator Distribution by Type</h4>
                      <div className="threat-type-chart">
                        {(() => {
                          if (!fullReportData.indicators || fullReportData.indicators.length === 0) {
                            return <div className="no-data">No threat indicators available</div>;
                          }

                          const typeCounts = fullReportData.indicators.reduce((acc, indicator) => {
                            const type = indicator.type || 'unknown';
                            acc[type] = (acc[type] || 0) + 1;
                            return acc;
                          }, {});

                          const total = Object.values(typeCounts).reduce((sum, count) => sum + count, 0);
                          const typeColors = {
                            domain: '#2196f3',
                            file_hash: '#f44336',
                            ip: '#ff9800',
                            url: '#9c27b0',
                            email: '#4caf50',
                            other: '#607d8b',
                            unknown: '#757575'
                          };

                          const typeLabels = {
                            domain: 'Malicious Domains',
                            file_hash: 'File Hashes',
                            ip: 'IP Addresses',
                            url: 'URLs',
                            email: 'Email Addresses',
                            other: 'Other Indicators',
                            unknown: 'Unknown Type'
                          };

                          return (
                            <div className="threat-type-bars">
                              {Object.entries(typeCounts)
                                .sort(([,a], [,b]) => b - a)
                                .map(([type, count]) => {
                                const percentage = total > 0 ? (count / total) * 100 : 0;
                                return (
                                  <div key={type} className="threat-type-bar-item">
                                    <div className="threat-type-label">
                                      <span className="threat-type-name">{typeLabels[type] || type.toUpperCase()}</span>
                                      <span className="threat-type-count">{count.toLocaleString()}</span>
                                    </div>
                                    <div className="threat-type-bar">
                                      <div
                                        className="threat-type-fill"
                                        style={{
                                          width: `${percentage}%`,
                                          backgroundColor: typeColors[type] || '#757575'
                                        }}
                                      />
                                    </div>
                                    <span className="threat-type-percentage">{percentage.toFixed(1)}%</span>
                                  </div>
                                );
                              })}
                            </div>
                          );
                        })()}
                      </div>
                    </div>
                  </div>


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

        .confidence-badge {
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 600;
          color: white;
        }

        .confidence-badge.high {
          background: #28a745;
        }

        .confidence-badge.medium {
          background: #ffc107;
          color: #212529;
        }

        .confidence-badge.low {
          background: #dc3545;
        }

        .target-org-badge {
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 600;
          color: white;
        }

        .target-org-badge.general {
          background: #6c757d;
        }

        .target-org-badge.targeted {
          background: #dc3545;
          animation: pulse 2s infinite;
        }

        @keyframes pulse {
          0% { opacity: 1; }
          50% { opacity: 0.7; }
          100% { opacity: 1; }
        }

        .source-badge {
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 600;
          background: #17a2b8;
          color: white;
        }

        .hash-type-badge {
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 600;
          color: white;
        }

        .hash-type-badge.sha1 {
          background: #28a745;
        }

        .hash-type-badge.sha256 {
          background: #007bff;
        }

        .hash-type-badge.md5 {
          background: #ffc107;
          color: #212529;
        }

        .hash-type-badge.sha512 {
          background: #6f42c1;
        }

        .hash-type-badge.none {
          background: #6c757d;
        }

        .ioc-value {
          background: white !important;
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

        /* Enhanced IOC Cards Styles */
        .ioc-cards-container {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
          gap: 20px;
          margin-bottom: 20px;
        }

        .ioc-card {
          background: white;
          border: 1px solid #e9ecef;
          border-radius: 12px;
          padding: 20px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
          transition: all 0.2s;
        }

        .ioc-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        }

        .ioc-card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }

        .confidence-score {
          display: flex;
          flex-direction: column;
          align-items: flex-end;
        }

        .confidence-label {
          font-size: 11px;
          color: #666;
          margin-bottom: 2px;
        }

        .confidence-value {
          font-size: 14px;
          font-weight: 600;
          padding: 2px 6px;
          border-radius: 4px;
        }

        .confidence-value.high {
          background: #d4edda;
          color: #155724;
        }

        .confidence-value.medium {
          background: #fff3cd;
          color: #856404;
        }

        .confidence-value.low {
          background: #f8d7da;
          color: #721c24;
        }

        .ioc-value-section {
          margin-bottom: 12px;
          padding: 12px;
          background: #f8f9fa;
          border-radius: 8px;
        }

        .ioc-value-label {
          font-size: 11px;
          font-weight: 600;
          color: #666;
          margin-bottom: 4px;
          text-transform: uppercase;
        }

        .ioc-value {
          font-family: 'Courier New', monospace;
          font-size: 13px;
          color: #333;
          word-break: break-all;
          line-height: 1.4;
        }

        .ioc-description {
          margin-bottom: 12px;
          padding: 10px;
          background: #fff8e1;
          border-left: 3px solid #ffc107;
          border-radius: 0 6px 6px 0;
        }

        .ioc-description-label {
          font-size: 11px;
          font-weight: 600;
          color: #856404;
          margin-bottom: 4px;
          text-transform: uppercase;
        }

        .ioc-description-text {
          font-size: 12px;
          color: #333;
          line-height: 1.4;
        }

        .ioc-metadata {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 8px;
          border-top: 1px solid #f1f3f4;
          padding-top: 12px;
        }

        .ioc-meta-item {
          display: flex;
          flex-direction: column;
          gap: 2px;
        }

        .meta-label {
          font-size: 10px;
          font-weight: 600;
          color: #666;
          text-transform: uppercase;
        }

        .meta-value {
          font-size: 12px;
          color: #333;
        }

        .ioc-summary-footer {
          text-align: center;
          padding: 16px;
          background: #f8f9fa;
          border-radius: 8px;
          border: 1px solid #e9ecef;
        }

        .ioc-summary-footer p {
          margin: 0;
          color: #666;
          font-size: 13px;
          font-weight: 500;
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

        /* Key Metrics Section Styles */
        .key-metrics-section {
          background: white;
          border-radius: 12px;
          padding: 24px;
          margin-bottom: 20px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          width: 100% !important;
          box-sizing: border-box !important;
        }

        .key-metrics-section h3 {
          margin: 0 0 20px 0;
          color: #333;
          font-size: 18px;
          font-weight: 600;
        }

        .metrics-chart-container {
          width: 100%;
          display: flex;
          justify-content: center;
        }

        .metrics-chart {
          width: 100%;
          max-width: 600px;
          background: white;
          border-radius: 12px;
          padding: 20px;
          border: 1px solid #e9ecef;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }

        .metrics-chart h4 {
          margin: 0 0 20px 0;
          color: #333;
          font-size: 16px;
          font-weight: 600;
          text-align: center;
        }

        .threat-type-chart {
          width: 100%;
        }

        .threat-type-bars {
          display: flex;
          flex-direction: column;
          gap: 12px;
          width: 100%;
        }

        .threat-type-bar-item {
          display: flex;
          align-items: center;
          gap: 12px;
          width: 100%;
        }

        .threat-type-label {
          display: flex;
          flex-direction: column;
          min-width: 120px;
          text-align: left;
        }

        .threat-type-name {
          font-size: 12px;
          font-weight: 600;
          color: #333;
        }

        .threat-type-count {
          font-size: 11px;
          color: #666;
        }

        .threat-type-bar {
          flex: 1;
          height: 20px;
          background: #f1f3f4;
          border-radius: 10px;
          overflow: hidden;
          position: relative;
        }

        .threat-type-fill {
          height: 100%;
          border-radius: 10px;
          transition: width 0.3s ease;
          position: relative;
        }

        .threat-type-percentage {
          font-size: 12px;
          font-weight: 600;
          color: #333;
          min-width: 40px;
          text-align: right;
        }

        .no-data {
          text-align: center;
          color: #666;
          font-style: italic;
          padding: 40px 20px;
          background: #f8f9fa;
          border-radius: 8px;
          border: 1px solid #e9ecef;
        }
      `}</style>
    </div>
  );
};

export default ReportDetailModal;