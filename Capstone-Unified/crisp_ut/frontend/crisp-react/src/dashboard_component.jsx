import React, { useState, useEffect, useRef } from 'react';
import * as d3 from 'd3';
import * as api from './api.js';

export default function Dashboard({ active, showPage }) {
  // State for dashboard data
  const [dashboardStats, setDashboardStats] = useState({
    threat_feeds: 0,
    indicators: 0,
    ttps: 0,
    status: 'loading'
  });
  
  // State for recent IoC data
  const [recentIoCs, setRecentIoCs] = useState([]);
  const [iocLoading, setIocLoading] = useState(false);
  const [iocError, setIocError] = useState(null);
  
  // D3 Chart References and State
  const chartRef = useRef(null);
  const tooltipRef = useRef(null);
  const cleanupRef = useRef(null);
  const [chartData, setChartData] = useState([]);
  const [chartLoading, setChartLoading] = useState(false);
  const [chartError, setChartError] = useState(null);
  const [chartFilters, setChartFilters] = useState({
    days: 30,
    type: null,
    feed_id: null
  });
  const [chartSummary, setChartSummary] = useState({
    total_indicators: 0,
    avg_daily: 0,
    type_distribution: []
  });

  // System Health Monitoring State
  const [systemHealth, setSystemHealth] = useState({
    status: 'unknown',
    database: { status: 'unknown' },
    services: { redis: { status: 'unknown' } },
    system: { cpu_percent: 0, memory_percent: 0, disk_percent: 0 },
    feeds: { total: 0, active: 0, external: 0, feeds: [] },
    errors: [],
    timestamp: null
  });
  const [healthLoading, setHealthLoading] = useState(false);
  const [healthError, setHealthError] = useState(null);
  
  // Recent Activities State
  const [recentActivities, setRecentActivities] = useState([]);
  const [activitiesLoading, setActivitiesLoading] = useState(false);
  const [activitiesError, setActivitiesError] = useState(null);

  // Dashboard Export State
  const [showDashboardExportModal, setShowDashboardExportModal] = useState(false);
  const [dashboardExportFormat, setDashboardExportFormat] = useState('json');
  const [dashboardExporting, setDashboardExporting] = useState(false);
  
  // Fetch dashboard data from backend
  useEffect(() => {
    if (active) {
      fetchDashboardData();
      fetchRecentIoCs();
      fetchChartData();
      fetchSystemHealth();
      fetchRecentActivities();
    }
  }, [active]);

  // Refetch chart data when filters change
  useEffect(() => {
    if (active) {
      fetchChartData();
    }
  }, [chartFilters, active]);

  // Auto-refresh system health every 30 seconds
  useEffect(() => {
    if (!active) return;
    
    const interval = setInterval(() => {
      fetchSystemHealth();
    }, 30000);
    
    return () => clearInterval(interval);
  }, [active]);
  
  const fetchDashboardData = async () => {
    const feedsData = await api.get('/api/threat-feeds/');
    if (feedsData) {
      let totalIndicators = 0;
      let totalTTPs = 0;
      
      // Get indicator and TTP counts from each feed
      if (feedsData.results) {
        for (const feed of feedsData.results) {
          const feedStatus = await api.get(`/api/threat-feeds/${feed.id}/status/`);
          if (feedStatus) {
            totalIndicators += feedStatus.indicator_count || 0;
            totalTTPs += feedStatus.ttp_count || 0;
          }
        }
      }
      
      setDashboardStats({
        threat_feeds: feedsData.count || 0,
        indicators: totalIndicators,
        ttps: totalTTPs,
        status: 'active'
      });
    }
  };

  // Fetch recent IoCs for dashboard table
  const fetchRecentIoCs = async () => {
    setIocLoading(true);
    setIocError(null);
    
    try {
      const indicatorsData = await api.get('/api/indicators/');
      if (indicatorsData && indicatorsData.results) {
        // Transform and limit to most recent 6 IoCs
        const transformedIoCs = indicatorsData.results
          .slice(0, 6)
          .map(indicator => transformIoCForDashboard(indicator));
        
        setRecentIoCs(transformedIoCs);
      } else {
        setRecentIoCs([]);
      }
    } catch (error) {
      console.error('Error fetching recent IoCs:', error);
      setIocError('Failed to load recent threat intelligence');
      setRecentIoCs([]);
    } finally {
      setIocLoading(false);
    }
  };

  // Fetch chart data from API
  const fetchChartData = async () => {
    setChartLoading(true);
    setChartError(null);
    
    try {
      const queryParams = new URLSearchParams({
        days: chartFilters.days.toString()
      });
      
      if (chartFilters.type) {
        queryParams.append('type', chartFilters.type);
      }
      if (chartFilters.feed_id) {
        queryParams.append('feed_id', chartFilters.feed_id);
      }
      
      const response = await api.get(`/api/threat-activity-chart/?${queryParams}`);
      
      if (response && response.success) {
        setChartData(response.data);
        setChartSummary(response.summary);
        
        // Redraw chart with new data
        if (chartRef.current) {
          createThreatActivityChart(response.data, response.summary);
        }
      } else {
        throw new Error('Failed to fetch chart data');
      }
    } catch (error) {
      console.error('Error fetching chart data:', error);
      setChartError('Failed to load chart data');
      setChartData([]);
    } finally {
      setChartLoading(false);
    }
  };

  // Fetch system health data from API
  const fetchSystemHealth = async () => {
    setHealthLoading(true);
    setHealthError(null);
    
    try {
      const response = await api.get('/api/system-health/');
      
      if (response) {
        setSystemHealth({
          status: response.status || 'unknown',
          database: response.database || { status: 'unknown' },
          services: response.services || { redis: { status: 'unknown' } },
          system: response.system || { cpu_percent: 0, memory_percent: 0, disk_percent: 0 },
          feeds: response.feeds || { total: 0, active: 0, external: 0, feeds: [] },
          errors: response.errors || [],
          timestamp: response.timestamp || new Date().toISOString()
        });
      } else {
        throw new Error('Failed to fetch system health data');
      }
    } catch (error) {
      console.error('Error fetching system health:', error);
      setHealthError('Failed to load system health data');
      // Set fallback data
      setSystemHealth(prev => ({
        ...prev,
        status: 'error',
        timestamp: new Date().toISOString()
      }));
    } finally {
      setHealthLoading(false);
    }
  };

  // Transform IoC data for dashboard display
  const transformIoCForDashboard = (indicator) => {
    // Map indicator types to display names
    const typeMapping = {
      'ip': 'IP Address',
      'domain': 'Domain',
      'url': 'URL',
      'file_hash': 'File Hash',
      'email': 'Email Address',
      'user_agent': 'User Agent'
    };

    // Determine severity based on confidence level
    const getSeverity = (confidence) => {
      if (confidence >= 80) return { level: 'high', label: 'High' };
      if (confidence >= 50) return { level: 'medium', label: 'Medium' };
      return { level: 'low', label: 'Low' };
    };

    // Format IoC value for display (truncate if too long)
    const formatValue = (value, type) => {
      if (type === 'file_hash' && value.length > 16) {
        return value.substring(0, 16) + '...';
      }
      if (value.length > 30) {
        return value.substring(0, 30) + '...';
      }
      return value;
    };

    const severity = getSeverity(indicator.confidence || 50);

    // Type icons mapping
    const typeIcons = {
      'ip': 'fa-network-wired',
      'domain': 'fa-globe',
      'url': 'fa-link',
      'file_hash': 'fa-file-signature',
      'email': 'fa-envelope',
      'user_agent': 'fa-browser'
    };

    // Age calculation
    const getAge = (dateString) => {
      const date = new Date(dateString);
      const now = new Date();
      const diffTime = Math.abs(now - date);
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays === 1) return '1 day ago';
      if (diffDays < 7) return `${diffDays} days ago`;
      if (diffDays < 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
      return `${Math.ceil(diffDays / 30)} months ago`;
    };
    
    return {
      id: indicator.id,
      displayType: typeMapping[indicator.type] || indicator.type.charAt(0).toUpperCase() + indicator.type.slice(1),
      typeIcon: typeIcons[indicator.type] || 'fa-question-circle',
      rawType: indicator.type,
      title: indicator.name || '',
      value: indicator.value,
      truncatedValue: formatValue(indicator.value, indicator.type),
      source: indicator.threat_feed?.name || indicator.source || 'Internal',
      severity: severity.label,
      severityClass: severity.level,
      confidence: indicator.confidence || 50,
      status: indicator.is_active !== false ? 'active' : 'inactive',
      isAnonymized: indicator.is_anonymized || false,
      age: getAge(indicator.created_at || new Date().toISOString()),
      created_at: indicator.created_at || new Date().toISOString()
    };
  };

  // Fetch recent activities
  const fetchRecentActivities = async () => {
    setActivitiesLoading(true);
    setActivitiesError(null);
    
    try {
      const response = await api.get('/api/recent-activities/?limit=10');
      if (response && response.success) {
        setRecentActivities(response.activities || []);
      } else {
        setActivitiesError('Failed to load recent activities');
      }
    } catch (error) {
      console.error('Error fetching recent activities:', error);
      setActivitiesError('Failed to load recent activities');
    } finally {
      setActivitiesLoading(false);
    }
  };

  // Utility functions for system health display
  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
      case 'connected':
      case 'active':
      case 'success':
        return '#28a745';
      case 'warning':
      case 'stale':
        return '#ffc107';
      case 'error':
      case 'disconnected':
      case 'failed':
      case 'inactive':
        return '#dc3545';
      default:
        return '#6c757d';
    }
  };

  const getStatusIcon = (status) => {
    switch (status?.toLowerCase()) {
      case 'healthy':
      case 'connected':
      case 'active':
      case 'success':
        return 'fas fa-check-circle';
      case 'warning':
      case 'stale':
        return 'fas fa-exclamation-triangle';
      case 'error':
      case 'disconnected':
      case 'failed':
      case 'inactive':
        return 'fas fa-times-circle';
      default:
        return 'fas fa-question-circle';
    }
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Unknown';
    
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString();
  };

  const formatUptime = (seconds) => {
    if (!seconds) return 'Unknown';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (hours > 24) {
      const days = Math.floor(hours / 24);
      const remainingHours = hours % 24;
      return `${days}d ${remainingHours}h`;
    }
    
    return `${hours}h ${minutes}m`;
  };

  const testFeedConnection = async (feedId) => {
    try {
      const response = await api.post(`/api/threat-feeds/${feedId}/test-connection/`);
      if (response && response.success) {
        // Refresh system health to show updated connection status
        fetchSystemHealth();
        alert('Connection test successful!');
      } else {
        alert('Connection test failed. Please check the feed configuration.');
      }
    } catch (error) {
      console.error('Error testing feed connection:', error);
      alert('Connection test failed due to an error.');
    }
  };
  
  // Set up D3 charts when component mounts or data changes
  useEffect(() => {
    if (active && chartRef.current && chartData.length > 0) {
      createThreatActivityChart(chartData, chartSummary);
    }
    
    // Cleanup function
    return () => {
      if (cleanupRef.current) {
        cleanupRef.current();
      }
    };
  }, [active, chartData, chartSummary]);

  // Real-time updates - refresh chart data every 5 minutes
  useEffect(() => {
    if (!active) return;

    const interval = setInterval(() => {
      console.log('Auto-refreshing chart data...');
      fetchChartData();
    }, 5 * 60 * 1000); // 5 minutes

    return () => clearInterval(interval);
  }, [active, chartFilters]);

  // Handle window resize for responsive chart
  useEffect(() => {
    const handleResize = () => {
      if (active && chartRef.current && chartData.length > 0) {
        // Debounce resize events
        clearTimeout(window.chartResizeTimeout);
        window.chartResizeTimeout = setTimeout(() => {
          createThreatActivityChart(chartData, chartSummary);
        }, 300);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
      clearTimeout(window.chartResizeTimeout);
    };
  }, [active, chartData, chartSummary]);

  // Cleanup on component unmount
  useEffect(() => {
    return () => {
      // Clean up chart elements
      if (cleanupRef.current) {
        cleanupRef.current();
      }
      
      // Clean up any remaining tooltips
      d3.selectAll('.chart-tooltip').remove();
      
      // Clear any remaining timeouts
      clearTimeout(window.chartResizeTimeout);
    };
  }, []);

  const createThreatActivityChart = (data = [], summary = {}) => {
    // Clean up previous chart and tooltip
    if (cleanupRef.current) {
      cleanupRef.current();
    }
    
    // Clear the container safely
    if (chartRef.current) {
      // Use React-safe approach to clear D3 content
      const container = d3.select(chartRef.current);
      container.selectAll("*").remove();
    }
    
    // Return early if no container or data
    if (!chartRef.current || !data || data.length === 0) {
      if (chartRef.current) {
        const svg = d3.select(chartRef.current)
          .append("svg")
          .attr("width", "100%")
          .attr("height", 300)
          .attr("viewBox", `0 0 ${chartRef.current.clientWidth || 400} 300`);
        
        svg.append("text")
          .attr("x", "50%")
          .attr("y", "50%")
          .attr("text-anchor", "middle")
          .attr("dominant-baseline", "middle")
          .style("font-size", "14px")
          .style("fill", "#666")
          .text(chartLoading ? "Loading chart data..." : "No data available");
      }
      return;
    }

    try {
      // Responsive dimensions
      const containerWidth = chartRef.current.clientWidth || 400;
      const width = Math.max(containerWidth, 400);
      const height = 350;
      const margin = { 
        top: 40, 
        right: 60, 
        bottom: 60, 
        left: 70 
      };
      const innerWidth = width - margin.left - margin.right;
      const innerHeight = height - margin.top - margin.bottom;

      // Create SVG with proper cleanup
      const svg = d3.select(chartRef.current)
        .append("svg")
        .attr("width", "100%")
        .attr("height", height)
        .attr("viewBox", `0 0 ${width} ${height}`)
        .style("max-width", "100%")
        .style("height", "auto");

      const g = svg.append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

      // Parse dates and prepare data
      const parseDate = d3.timeParse("%Y-%m-%d");
      const formattedData = data.map(d => ({
        date: parseDate(d.date),
        count: d.count,
        types: d.types || {},
        originalDate: d.date
      })).filter(d => d.date && !isNaN(d.count));

      if (formattedData.length === 0) {
        svg.append("text")
          .attr("x", "50%")
          .attr("y", "50%")
          .attr("text-anchor", "middle")
          .attr("dominant-baseline", "middle")
          .style("font-size", "14px")
          .style("fill", "#666")
          .text("No valid data to display");
        return;
      }

      // Dynamic scales
      const x = d3.scaleTime()
        .domain(d3.extent(formattedData, d => d.date))
        .range([0, innerWidth]);

      const maxCount = d3.max(formattedData, d => d.count) || 1;
      const y = d3.scaleLinear()
        .domain([0, maxCount * 1.1])
        .range([innerHeight, 0])
        .nice();

      // Create tooltip - ensure it's properly tracked
      let tooltip = tooltipRef.current;
      if (!tooltip) {
        tooltip = d3.select("body").append("div")
          .attr("class", "chart-tooltip")
          .style("opacity", 0)
          .style("position", "absolute")
          .style("background", "rgba(0, 0, 0, 0.9)")
          .style("color", "white")
          .style("padding", "12px")
          .style("border-radius", "6px")
          .style("font-size", "13px")
          .style("pointer-events", "none")
          .style("z-index", "1000")
          .style("box-shadow", "0 4px 12px rgba(0, 0, 0, 0.3)");
        
        tooltipRef.current = tooltip;
      }

      // Add gradient
      const defs = svg.append("defs");
      const gradientId = `areaGradient-${Date.now()}`;
      
      const gradient = defs.append("linearGradient")
        .attr("id", gradientId)
        .attr("x1", "0%")
        .attr("y1", "0%")
        .attr("x2", "0%")
        .attr("y2", "100%");

      gradient.append("stop")
        .attr("offset", "0%")
        .attr("stop-color", "#0056b3")
        .attr("stop-opacity", 0.8);

      gradient.append("stop")
        .attr("offset", "100%")
        .attr("stop-color", "#00a0e9")
        .attr("stop-opacity", 0.1);

      // Add grid lines
      g.append("g")
        .attr("class", "grid")
        .attr("transform", `translate(0,${innerHeight})`)
        .call(d3.axisBottom(x)
          .ticks(Math.min(7, formattedData.length))
          .tickSize(-innerHeight)
          .tickFormat("")
        )
        .style("stroke-dasharray", "3,3")
        .style("opacity", 0.3);

      g.append("g")
        .attr("class", "grid")
        .call(d3.axisLeft(y)
          .ticks(6)
          .tickSize(-innerWidth)
          .tickFormat("")
        )
        .style("stroke-dasharray", "3,3")
        .style("opacity", 0.3);

      // Add area chart
      const area = d3.area()
        .x(d => x(d.date))
        .y0(innerHeight)
        .y1(d => y(d.count))
        .curve(d3.curveCardinal);

      g.append("path")
        .datum(formattedData)
        .attr("fill", `url(#${gradientId})`)
        .attr("d", area);

      // Add line chart
      const line = d3.line()
        .x(d => x(d.date))
        .y(d => y(d.count))
        .curve(d3.curveCardinal);

      g.append("path")
        .datum(formattedData)
        .attr("fill", "none")
        .attr("stroke", "#0056b3")
        .attr("stroke-width", 3)
        .attr("d", line);

      // Add interactive dots
      g.selectAll(".dot")
        .data(formattedData)
        .enter().append("circle")
        .attr("class", "dot")
        .attr("cx", d => x(d.date))
        .attr("cy", d => y(d.count))
        .attr("r", 4)
        .attr("fill", "#0056b3")
        .attr("stroke", "white")
        .attr("stroke-width", 2)
        .style("cursor", "pointer")
        .on("mouseover", function(event, d) {
          d3.select(this)
            .transition().duration(200)
            .attr("r", 6)
            .attr("fill", "#ff6b35");

          const formatDate = d3.timeFormat("%B %d, %Y");
          const typeBreakdown = Object.entries(d.types)
            .map(([type, count]) => `${type}: ${count}`)
            .join("<br>");

          if (tooltip) {
            tooltip.transition().duration(200).style("opacity", .9);
            tooltip.html(`
              <strong>${formatDate(d.date)}</strong><br/>
              Total IoCs: <strong>${d.count}</strong><br/>
              ${typeBreakdown ? `<br/><em>Breakdown:</em><br/>${typeBreakdown}` : ''}
            `)
              .style("left", (event.pageX + 10) + "px")
              .style("top", (event.pageY - 28) + "px");
          }
        })
        .on("mouseout", function(event, d) {
          d3.select(this)
            .transition().duration(200)
            .attr("r", 4)
            .attr("fill", "#0056b3");

          if (tooltip) {
            tooltip.transition().duration(500).style("opacity", 0);
          }
        });

      // Add axes
      const formatTick = d3.timeFormat("%m/%d");
      g.append("g")
        .attr("transform", `translate(0,${innerHeight})`)
        .call(d3.axisBottom(x)
          .ticks(Math.min(7, formattedData.length))
          .tickFormat(formatTick)
        )
        .selectAll("text")
        .style("text-anchor", "end")
        .attr("dx", "-.8em")
        .attr("dy", ".15em")
        .attr("transform", "rotate(-45)");

      g.append("g")
        .call(d3.axisLeft(y).ticks(6))
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", "0.71em")
        .attr("text-anchor", "end")
        .style("fill", "#666")
        .text("IoC Count");

      // Add title
      g.append("text")
        .attr("x", innerWidth / 2)
        .attr("y", -15)
        .attr("text-anchor", "middle")
        .style("font-size", "18px")
        .style("font-weight", "600")
        .style("fill", "#2d3748")
        .text("Threat Activity Trends");

      // Add summary stats
      const statsText = `Total: ${summary.total_indicators || 0} IoCs | Daily Avg: ${summary.avg_daily || 0}`;
      g.append("text")
        .attr("x", innerWidth / 2)
        .attr("y", innerHeight + 50)
        .attr("text-anchor", "middle")
        .style("font-size", "12px")
        .style("fill", "#666")
        .text(statsText);

      // Set up cleanup function
      cleanupRef.current = () => {
        if (tooltipRef.current) {
          tooltipRef.current.remove();
          tooltipRef.current = null;
        }
        if (chartRef.current) {
          d3.select(chartRef.current).selectAll("*").remove();
        }
      };

    } catch (error) {
      console.error('Error creating chart:', error);
      setChartError('Failed to create chart visualization');
    }
  };

  // Dashboard Export Functions
  function closeDashboardExportModal() {
    setShowDashboardExportModal(false);
    setDashboardExportFormat('json');
  }

  async function handleDashboardExport() {
    setDashboardExporting(true);
    
    try {
      let exportData;
      let filename;
      let mimeType;

      const exportPayload = {
        export_date: new Date().toISOString(),
        dashboard_stats: dashboardStats,
        recent_iocs: recentIoCs,
        system_health: systemHealth,
        chart_data: chartData,
        chart_summary: chartSummary,
        chart_filters: chartFilters
      };

      switch (dashboardExportFormat) {
        case 'csv':
          exportData = exportDashboardToCSV(exportPayload);
          filename = `dashboard_export_${new Date().toISOString().split('T')[0]}.csv`;
          mimeType = 'text/csv';
          break;
          
        case 'json':
          exportData = exportDashboardToJSON(exportPayload);
          filename = `dashboard_export_${new Date().toISOString().split('T')[0]}.json`;
          mimeType = 'application/json';
          break;
          
        case 'summary':
          exportData = exportDashboardToSummary(exportPayload);
          filename = `dashboard_summary_${new Date().toISOString().split('T')[0]}.txt`;
          mimeType = 'text/plain';
          break;
          
        default:
          throw new Error('Unsupported export format');
      }

      // Create and download file
      const blob = new Blob([exportData], { type: mimeType });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      closeDashboardExportModal();
      
      console.log(`Successfully exported dashboard data as ${dashboardExportFormat.toUpperCase()}`);
      
    } catch (error) {
      console.error('Dashboard export failed:', error);
      alert('Export failed. Please try again.');
    } finally {
      setDashboardExporting(false);
    }
  }

  function exportDashboardToCSV(data) {
    let csvContent = '';
    
    // Add header
    csvContent += 'CRISP Dashboard Export\n';
    csvContent += `Export Date: ${new Date(data.export_date).toLocaleString()}\n\n`;
    
    // Dashboard Statistics
    csvContent += 'DASHBOARD STATISTICS\n';
    csvContent += 'Metric,Value\n';
    csvContent += `Active IoCs,${data.dashboard_stats.indicators || 0}\n`;
    csvContent += `TTPs,${data.dashboard_stats.ttps || 0}\n`;
    csvContent += `Threat Feeds,${data.dashboard_stats.threat_feeds || 0}\n`;
    csvContent += `Platform Status,${data.dashboard_stats.status || 'Unknown'}\n\n`;

    // Recent IoCs Table
    if (data.recent_iocs && data.recent_iocs.length > 0) {
      csvContent += 'RECENT INDICATORS OF COMPROMISE\n';
      csvContent += 'Type,Indicator,Source,Severity,Status,Created\n';
      
      data.recent_iocs.forEach(ioc => {
        const csvRow = [
          ioc.displayType || '',
          `"${(ioc.value || '').replace(/"/g, '""')}"`,
          ioc.source || '',
          ioc.severity || '',
          'Active',
          ioc.created_at || ''
        ].join(',');
        csvContent += csvRow + '\n';
      });
      csvContent += '\n';
    }

    // System Health Summary
    if (data.system_health) {
      csvContent += 'SYSTEM HEALTH\n';
      csvContent += 'Component,Status,Details\n';
      csvContent += `Overall Status,${data.system_health.status || 'Unknown'},\n`;
      csvContent += `Database,${data.system_health.database?.status || 'Unknown'},${data.system_health.database?.details || ''}\n`;
      csvContent += `Redis,${data.system_health.services?.redis?.status || 'Unknown'},${data.system_health.services?.redis?.details || ''}\n`;
      if (data.system_health.system) {
        csvContent += `CPU Usage,${data.system_health.system.cpu_percent?.toFixed(1) || 'N/A'}%,\n`;
        csvContent += `Memory Usage,${data.system_health.system.memory_percent?.toFixed(1) || 'N/A'}%,\n`;
        csvContent += `Disk Usage,${data.system_health.system.disk_percent?.toFixed(1) || 'N/A'}%,\n`;
      }
    }

    return csvContent;
  }

  function exportDashboardToJSON(data) {
    return JSON.stringify(data, null, 2);
  }

  function exportDashboardToSummary(data) {
    let summary = '';
    
    summary += 'CRISP THREAT INTELLIGENCE DASHBOARD SUMMARY\n';
    summary += '=' + '='.repeat(48) + '\n\n';
    summary += `Export Date: ${new Date(data.export_date).toLocaleString()}\n\n`;

    // Overview
    summary += 'OVERVIEW\n';
    summary += '-'.repeat(20) + '\n';
    summary += `• Active IoCs: ${data.dashboard_stats.indicators || 0}\n`;
    summary += `• TTPs: ${data.dashboard_stats.ttps || 0}\n`;
    summary += `• Threat Feeds: ${data.dashboard_stats.threat_feeds || 0}\n`;
    summary += `• Platform Status: ${data.dashboard_stats.status || 'Unknown'}\n\n`;

    // Recent Activity
    if (data.recent_iocs && data.recent_iocs.length > 0) {
      summary += 'RECENT THREAT INTELLIGENCE\n';
      summary += '-'.repeat(30) + '\n';
      summary += `Total Recent IoCs: ${data.recent_iocs.length}\n\n`;
      
      const typeDistribution = data.recent_iocs.reduce((acc, ioc) => {
        acc[ioc.displayType] = (acc[ioc.displayType] || 0) + 1;
        return acc;
      }, {});
      
      summary += 'Type Distribution:\n';
      Object.entries(typeDistribution).forEach(([type, count]) => {
        summary += `  • ${type}: ${count}\n`;
      });
      summary += '\n';
    }

    // System Health
    if (data.system_health) {
      summary += 'SYSTEM HEALTH\n';
      summary += '-'.repeat(20) + '\n';
      summary += `Overall Status: ${data.system_health.status || 'Unknown'}\n`;
      summary += `Database: ${data.system_health.database?.status || 'Unknown'}\n`;
      summary += `Redis: ${data.system_health.services?.redis?.status || 'Unknown'}\n`;
      
      if (data.system_health.system) {
        summary += `CPU Usage: ${data.system_health.system.cpu_percent?.toFixed(1) || 'N/A'}%\n`;
        summary += `Memory Usage: ${data.system_health.system.memory_percent?.toFixed(1) || 'N/A'}%\n`;
        summary += `Disk Usage: ${data.system_health.system.disk_percent?.toFixed(1) || 'N/A'}%\n`;
      }
      summary += '\n';
    }

    // Chart Summary
    if (data.chart_summary && data.chart_summary.total_indicators > 0) {
      summary += 'THREAT ACTIVITY TRENDS\n';
      summary += '-'.repeat(25) + '\n';
      summary += `Total Indicators (${data.chart_filters.days} days): ${data.chart_summary.total_indicators}\n`;
      summary += `Daily Average: ${data.chart_summary.avg_daily}\n`;
      summary += `Date Range: ${data.chart_summary.start_date} to ${data.chart_summary.end_date}\n\n`;
    }

    summary += 'Generated by CRISP Threat Intelligence Platform\n';
    
    return summary;
  }

  return (
    <section id="dashboard" className={`page-section ${active ? 'active' : ''}`}>
      {/* Dashboard Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Threat Intelligence Dashboard</h1>
          <p className="page-subtitle">Overview of threat intelligence and platform activity</p>
        </div>
        <div className="action-buttons">
          <button className="btn btn-outline" onClick={() => setShowDashboardExportModal(true)}><i className="fas fa-download"></i> Export Data</button>
          <button className="btn btn-primary" onClick={() => showPage('threat-feeds', 'addFeed')}><i className="fas fa-plus"></i> Add New Feed</button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-title">
            <div className="stat-icon"><i className="fas fa-search"></i></div>
            <span>Active IoCs</span>
          </div>
          <div className="stat-value">
            {dashboardStats.indicators || 0}
          </div>
          <div className="stat-change increase">
            <span><i className="fas fa-arrow-up"></i></span>
            <span>Live data</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-title">
            <div className="stat-icon"><i className="fas fa-sitemap"></i></div>
            <span>TTPs</span>
          </div>
          <div className="stat-value">
            {dashboardStats.ttps || 0}
          </div>
          <div className="stat-change increase">
            <span><i className="fas fa-arrow-up"></i></span>
            <span>Live data</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-title">
            <div className="stat-icon"><i className="fas fa-rss"></i></div>
            <span>Threat Feeds</span>
          </div>
          <div className="stat-value">
            {dashboardStats.threat_feeds || 0}
          </div>
          <div className="stat-change increase">
            <span><i className="fas fa-arrow-up"></i></span>
            <span>Live data</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-title">
            <div className="stat-icon"><i className="fas fa-server"></i></div>
            <span>Platform Status</span>
          </div>
          <div className="stat-value">
            {dashboardStats.status === 'active' ? 'Online' : 'Offline'}
          </div>
          <div className="stat-change">
            <span><i className="fas fa-circle" style={{color: dashboardStats.status === 'active' ? '#28a745' : '#dc3545'}}></i></span>
            <span>Live status</span>
          </div>
        </div>
      </div>

      {/* Main Grid */}
      <div className="main-grid">
        {/* Threat Feed */}
        <div>
          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><i className="fas fa-shield-alt card-icon"></i> Recent Threat Intelligence</h2>
              <div className="card-actions">
                <button 
                  className="btn btn-outline btn-sm" 
                  onClick={fetchRecentIoCs}
                  disabled={iocLoading}
                >
                  <i className={`fas fa-sync-alt ${iocLoading ? 'fa-spin' : ''}`}></i> 
                  {iocLoading ? 'Refreshing...' : 'Refresh'}
                </button>
              </div>
            </div>
            <div className="card-content">
              {iocLoading ? (
                <div className="loading-state">
                  <div className="loading-spinner"></div>
                  <p>Loading recent threat intelligence...</p>
                </div>
              ) : iocError ? (
                <div className="error-state">
                  <i className="fas fa-exclamation-triangle"></i>
                  <p>{iocError}</p>
                  <button className="btn btn-primary btn-sm" onClick={fetchRecentIoCs}>
                    <i className="fas fa-retry"></i> Retry
                  </button>
                </div>
              ) : recentIoCs.length === 0 ? (
                <div className="empty-state">
                  <i className="fas fa-shield-alt"></i>
                  <p>No threat intelligence available</p>
                  <p className="text-muted">IoCs will appear here once feeds are consumed</p>
                </div>
              ) : (
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Type</th>
                      <th>Indicator</th>
                      <th>Source</th>
                      <th>Severity</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentIoCs.map((ioc, index) => (
                      <tr key={`${ioc.id || index}`}>
                        <td>
                          <div className="type-indicator">
                            <i className={`fas ${ioc.typeIcon}`}></i>
                            <span>{ioc.displayType}</span>
                          </div>
                        </td>
                        <td>
                          <div className="indicator-value">
                            <span className="value" title={ioc.value}>{ioc.truncatedValue}</span>
                            {ioc.isAnonymized && (
                              <span className="badge badge-anonymized">
                                <i className="fas fa-mask"></i> Anonymized
                              </span>
                            )}
                          </div>
                        </td>
                        <td>
                          <div className="source-info">
                            <span className="source-name">{ioc.source}</span>
                            <div className="source-meta">
                              <span className="age-indicator" title={`Created: ${ioc.created_at}`}>
                                {ioc.age}
                              </span>
                            </div>
                          </div>
                        </td>
                        <td>
                          <span className={`badge badge-${ioc.severityClass}`}>
                            {ioc.severity}
                          </span>
                        </td>
                        <td>
                          <div className="badge-tags">
                            <span className="badge badge-active">Active</span>
                            {ioc.confidence >= 80 && (
                              <span className="badge badge-verified">
                                <i className="fas fa-check-circle"></i> High Confidence
                              </span>
                            )}
                            {ioc.confidence < 50 && (
                              <span className="badge badge-warning">
                                <i className="fas fa-exclamation-triangle"></i> Low Confidence
                              </span>
                            )}
                            <span className="badge badge-realtime" title="Real-time data">
                              <i className="fas fa-broadcast-tower"></i> Live
                            </span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><i className="fas fa-chart-area card-icon"></i> Threat Activity Trends</h2>
              <div className="card-actions">
                <select 
                  className="btn btn-outline btn-sm"
                  value={chartFilters.days}
                  onChange={(e) => setChartFilters({...chartFilters, days: parseInt(e.target.value)})}
                  style={{marginRight: '10px'}}
                >
                  <option value="7">Last 7 Days</option>
                  <option value="14">Last 14 Days</option>
                  <option value="30">Last 30 Days</option>
                  <option value="60">Last 60 Days</option>
                  <option value="90">Last 90 Days</option>
                </select>
                
                <select 
                  className="btn btn-outline btn-sm"
                  value={chartFilters.type || ''}
                  onChange={(e) => setChartFilters({...chartFilters, type: e.target.value || null})}
                  style={{marginRight: '10px'}}
                >
                  <option value="">All Types</option>
                  <option value="ip">IP Address</option>
                  <option value="domain">Domain</option>
                  <option value="url">URL</option>
                  <option value="file_hash">File Hash</option>
                  <option value="email">Email</option>
                </select>
                
                <button 
                  className="btn btn-outline btn-sm"
                  onClick={fetchChartData}
                  disabled={chartLoading}
                  title="Refresh chart data"
                >
                  <i className={`fas fa-sync-alt ${chartLoading ? 'fa-spin' : ''}`}></i>
                  {chartLoading ? ' Loading...' : ' Refresh'}
                </button>
              </div>
            </div>
            
            {/* Chart Status Bar */}
            {chartSummary.total_indicators > 0 && (
              <div className="card-status-bar" style={{
                background: '#f8f9fa', 
                padding: '8px 16px', 
                fontSize: '12px', 
                color: '#666',
                borderBottom: '1px solid #e9ecef'
              }}>
                <span><strong>Total IoCs:</strong> {chartSummary.total_indicators}</span>
                <span style={{margin: '0 15px'}}>|</span>
                <span><strong>Daily Average:</strong> {chartSummary.avg_daily}</span>
                <span style={{margin: '0 15px'}}>|</span>
                <span><strong>Date Range:</strong> {chartSummary.start_date} to {chartSummary.end_date}</span>
              </div>
            )}
            
            <div className="card-content">
              {chartError && (
                <div className="alert alert-error" style={{
                  background: '#fff5f5',
                  border: '1px solid #fed7d7',
                  color: '#c53030',
                  padding: '12px',
                  borderRadius: '4px',
                  marginBottom: '16px'
                }}>
                  <i className="fas fa-exclamation-triangle"></i> {chartError}
                </div>
              )}
              
              <ChartErrorBoundary>
                <div style={{position: 'relative', minHeight: '350px'}}>
                  {chartLoading && (
                    <div style={{
                      position: 'absolute',
                      top: '50%',
                      left: '50%',
                      transform: 'translate(-50%, -50%)',
                      textAlign: 'center',
                      zIndex: 10
                    }}>
                      <i className="fas fa-spinner fa-spin" style={{fontSize: '24px', color: '#0056b3'}}></i>
                      <p style={{marginTop: '10px', color: '#666'}}>Loading chart data...</p>
                    </div>
                  )}
                  <div 
                    className="chart-container" 
                    ref={chartRef} 
                    style={{
                      minHeight: '350px',
                      width: '100%',
                      overflow: 'visible'
                    }}
                  >
                    {/* D3.js Chart will be rendered here */}
                  </div>
                </div>
              </ChartErrorBoundary>
            </div>
          </div>
        </div>

        {/* Side Panel */}
        <div className="side-panels">
          {/* Connected Institutions */}
          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><i className="fas fa-building card-icon"></i> Connected Institutions</h2>
            </div>
            <div className="card-content">
              <ul className="institution-list">
                <li className="institution-item">
                  <div className="institution-logo">UP</div>
                  <div className="institution-details">
                    <div className="institution-name">University of Pretoria</div>
                    <div className="institution-stats">
                      <div className="stat-item"><i className="fas fa-exchange-alt"></i> 125 IoCs</div>
                      <div className="stat-item"><i className="fas fa-clock"></i> 5m ago</div>
                    </div>
                  </div>
                  <div className="trust-level">
                    <div className="trust-fill" style={{ width: '90%' }}></div>
                  </div>
                </li>
                <li className="institution-item">
                  <div className="institution-logo">CS</div>
                  <div className="institution-details">
                    <div className="institution-name">Cyber Security Hub</div>
                    <div className="institution-stats">
                      <div className="stat-item"><i className="fas fa-exchange-alt"></i> 342 IoCs</div>
                      <div className="stat-item"><i className="fas fa-clock"></i> 17m ago</div>
                    </div>
                  </div>
                  <div className="trust-level">
                    <div className="trust-fill" style={{ width: '85%' }}></div>
                  </div>
                </li>
                <li className="institution-item">
                  <div className="institution-logo">SR</div>
                  <div className="institution-details">
                    <div className="institution-name">SANReN CSIRT</div>
                    <div className="institution-stats">
                      <div className="stat-item"><i className="fas fa-exchange-alt"></i> 208 IoCs</div>
                      <div className="stat-item"><i className="fas fa-clock"></i> 32m ago</div>
                    </div>
                  </div>
                  <div className="trust-level">
                    <div className="trust-fill" style={{ width: '75%' }}></div>
                  </div>
                </li>
                <li className="institution-item">
                  <div className="institution-logo">SB</div>
                  <div className="institution-details">
                    <div className="institution-name">SABRIC</div>
                    <div className="institution-stats">
                      <div className="stat-item"><i className="fas fa-exchange-alt"></i> 156 IoCs</div>
                      <div className="stat-item"><i className="fas fa-clock"></i> 1h ago</div>
                    </div>
                  </div>
                  <div className="trust-level">
                    <div className="trust-fill" style={{ width: '70%' }}></div>
                  </div>
                </li>
              </ul>
            </div>
          </div>

          {/* Recent Activity */}
          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><i className="fas fa-history card-icon"></i> Recent Activity</h2>
            </div>
            <div className="card-content">
              {activitiesLoading ? (
                <div className="loading-state">
                  <div className="loading-spinner"></div>
                  <p>Loading recent activities...</p>
                </div>
              ) : activitiesError ? (
                <div className="error-state">
                  <i className="fas fa-exclamation-triangle"></i>
                  <p>{activitiesError}</p>
                  <button className="btn btn-primary btn-sm" onClick={fetchRecentActivities}>
                    <i className="fas fa-retry"></i> Retry
                  </button>
                </div>
              ) : recentActivities.length === 0 ? (
                <div className="empty-state">
                  <i className="fas fa-history"></i>
                  <p>No recent activities</p>
                  <p className="text-muted">System activities will appear here</p>
                </div>
              ) : (
                <ul className="activity-stream">
                  {recentActivities.map((activity) => (
                    <li key={activity.id} className="activity-item">
                      <div className="activity-icon">
                        <i className={activity.icon}></i>
                      </div>
                      <div className="activity-details">
                        <div className="activity-text">{activity.title}</div>
                        {activity.description && (
                          <div className="activity-description">{activity.description}</div>
                        )}
                        <div className="activity-meta">
                          <div className="activity-time">{activity.time_ago}</div>
                          <span className={`badge ${activity.badge_type}`}>
                            {activity.badge_text}
                          </span>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* System Health & Feed Status Monitoring */}
      <div className="card" style={{marginTop: '24px'}}>
        <div className="card-header">
          <h2 className="card-title">
            <i className="fas fa-heartbeat card-icon"></i> System Health & Feed Status
          </h2>
          <div className="card-actions">
            <button 
              className="btn btn-outline btn-sm"
              onClick={fetchSystemHealth}
              disabled={healthLoading}
              title="Refresh system health"
            >
              <i className={`fas fa-sync-alt ${healthLoading ? 'fa-spin' : ''}`}></i>
              {healthLoading ? ' Loading...' : ' Refresh'}
            </button>
          </div>
        </div>

        <div className="card-content">
          {healthError && (
            <div className="alert alert-error" style={{
              background: '#fff5f5',
              border: '1px solid #fed7d7',
              color: '#c53030',
              padding: '12px',
              borderRadius: '4px',
              marginBottom: '16px'
            }}>
              <i className="fas fa-exclamation-triangle"></i> {healthError}
            </div>
          )}

          {/* System Status Overview */}
          <div className="system-status-overview" style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '16px',
            marginBottom: '24px'
          }}>
            <div className="status-card" style={{
              background: '#f8f9fa',
              border: '1px solid #dee2e6',
              borderRadius: '8px',
              padding: '16px',
              textAlign: 'center'
            }}>
              <div style={{
                fontSize: '24px',
                color: getStatusColor(systemHealth.status),
                marginBottom: '8px'
              }}>
                <i className={getStatusIcon(systemHealth.status)}></i>
              </div>
              <h3 style={{margin: '0 0 4px 0', fontSize: '16px'}}>Overall Status</h3>
              <p style={{
                margin: '0',
                color: getStatusColor(systemHealth.status),
                fontWeight: 'bold',
                textTransform: 'capitalize'
              }}>
                {systemHealth.status}
              </p>
              <small style={{color: '#666'}}>
                Last Check: {formatTimestamp(systemHealth.timestamp)}
              </small>
            </div>

            <div className="status-card" style={{
              background: '#f8f9fa',
              border: '1px solid #dee2e6',
              borderRadius: '8px',
              padding: '16px',
              textAlign: 'center'
            }}>
              <div style={{
                fontSize: '24px',
                color: getStatusColor(systemHealth.database?.status || 'unknown'),
                marginBottom: '8px'
              }}>
                <i className="fas fa-database"></i>
              </div>
              <h3 style={{margin: '0 0 4px 0', fontSize: '16px'}}>Database</h3>
              <p style={{
                margin: '0',
                color: getStatusColor(systemHealth.database?.status || 'unknown'),
                fontWeight: 'bold',
                textTransform: 'capitalize'
              }}>
                {systemHealth.database?.status || 'Unknown'}
              </p>
              <small style={{color: '#666'}}>
                {systemHealth.database?.connection_count 
                  ? `${systemHealth.database.connection_count} connections`
                  : 'Connection info unavailable'
                }
              </small>
            </div>

            <div className="status-card" style={{
              background: '#f8f9fa',
              border: '1px solid #dee2e6',
              borderRadius: '8px',
              padding: '16px',
              textAlign: 'center'
            }}>
              <div style={{
                fontSize: '24px',
                color: getStatusColor(systemHealth.services?.redis?.status || 'unknown'),
                marginBottom: '8px'
              }}>
                <i className="fas fa-memory"></i>
              </div>
              <h3 style={{margin: '0 0 4px 0', fontSize: '16px'}}>Redis</h3>
              <p style={{
                margin: '0',
                color: getStatusColor(systemHealth.services?.redis?.status || 'unknown'),
                fontWeight: 'bold',
                textTransform: 'capitalize'
              }}>
                {systemHealth.services?.redis?.status || 'Unknown'}
              </p>
              <small style={{color: '#666'}}>
                {systemHealth.services?.redis?.info 
                  ? `v${systemHealth.services.redis.info}`
                  : 'Version unavailable'
                }
              </small>
            </div>

            <div className="status-card" style={{
              background: '#f8f9fa',
              border: '1px solid #dee2e6',
              borderRadius: '8px',
              padding: '16px',
              textAlign: 'center'
            }}>
              <div style={{
                fontSize: '24px',
                color: systemHealth.system?.cpu_percent > 80 ? '#dc3545' : 
                      systemHealth.system?.cpu_percent > 60 ? '#ffc107' : '#28a745',
                marginBottom: '8px'
              }}>
                <i className="fas fa-microchip"></i>
              </div>
              <h3 style={{margin: '0 0 4px 0', fontSize: '16px'}}>System Resources</h3>
              <p style={{margin: '0', fontWeight: 'bold'}}>
                CPU: {systemHealth.system?.cpu_percent?.toFixed(1) || 'N/A'}%
              </p>
              <small style={{color: '#666'}}>
                RAM: {systemHealth.system?.memory_percent?.toFixed(1) || 'N/A'}% | 
                Disk: {systemHealth.system?.disk_percent?.toFixed(1) || 'N/A'}%
              </small>
            </div>
          </div>

          {/* Feed Status Section */}
          <div className="feed-status-section">
            <h3 style={{
              margin: '0 0 16px 0',
              fontSize: '18px',
              borderBottom: '2px solid #dee2e6',
              paddingBottom: '8px'
            }}>
              Feed Status Monitoring
            </h3>

            {/* Feed Summary */}
            {systemHealth.feeds && systemHealth.feeds.total > 0 && (
              <div className="feed-summary" style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
                gap: '12px',
                marginBottom: '20px',
                padding: '16px',
                background: '#f1f3f4',
                borderRadius: '6px'
              }}>
                <div style={{textAlign: 'center'}}>
                  <div style={{fontSize: '24px', fontWeight: 'bold', color: '#0056b3'}}>
                    {systemHealth.feeds.total}
                  </div>
                  <small>Total Feeds</small>
                </div>
                <div style={{textAlign: 'center'}}>
                  <div style={{fontSize: '24px', fontWeight: 'bold', color: '#28a745'}}>
                    {systemHealth.feeds.active}
                  </div>
                  <small>Active</small>
                </div>
                <div style={{textAlign: 'center'}}>
                  <div style={{fontSize: '24px', fontWeight: 'bold', color: '#17a2b8'}}>
                    {systemHealth.feeds.external}
                  </div>
                  <small>External</small>
                </div>
                <div style={{textAlign: 'center'}}>
                  <div style={{fontSize: '24px', fontWeight: 'bold', color: '#6c757d'}}>
                    {systemHealth.feeds.total - systemHealth.feeds.external}
                  </div>
                  <small>Internal</small>
                </div>
              </div>
            )}

            {/* Quick Feed Management Action */}
            {systemHealth.feeds && systemHealth.feeds.total === 0 ? (
              <div style={{
                textAlign: 'center',
                color: '#666',
                padding: '24px',
                background: '#f8f9fa',
                borderRadius: '6px',
                marginTop: '16px'
              }}>
                <i className="fas fa-rss" style={{fontSize: '32px', marginBottom: '12px'}}></i>
                <p style={{margin: '0 0 12px 0'}}>No threat feeds configured yet.</p>
                <button 
                  className="btn btn-primary btn-sm"
                  onClick={() => showPage('threat-feeds')}
                >
                  <i className="fas fa-plus"></i> Manage Feeds
                </button>
              </div>
            ) : (
              <div style={{
                textAlign: 'center',
                padding: '16px',
                marginTop: '16px'
              }}>
                <button 
                  className="btn btn-outline btn-sm"
                  onClick={() => showPage('threat-feeds')}
                >
                  <i className="fas fa-cog"></i> Manage All Feeds
                </button>
              </div>
            )}
          </div>

          {/* Error Summary */}
          {systemHealth.errors && systemHealth.errors.length > 0 && (
            <div className="error-summary" style={{
              marginTop: '24px',
              padding: '16px',
              background: '#fff5f5',
              border: '1px solid #fed7d7',
              borderRadius: '6px'
            }}>
              <h4 style={{
                margin: '0 0 12px 0',
                color: '#c53030',
                fontSize: '16px'
              }}>
                <i className="fas fa-exclamation-triangle"></i> System Errors ({systemHealth.errors.length})
              </h4>
              <ul style={{margin: '0', paddingLeft: '20px'}}>
                {systemHealth.errors.map((error, index) => (
                  <li key={index} style={{
                    color: '#c53030',
                    marginBottom: '4px'
                  }}>
                    {error}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* System Metrics */}
          {systemHealth.system && Object.keys(systemHealth.system).length > 0 && (
            <div className="system-metrics" style={{
              marginTop: '24px',
              padding: '16px',
              background: '#f8f9fa',
              borderRadius: '6px'
            }}>
              <h4 style={{
                margin: '0 0 12px 0',
                fontSize: '16px'
              }}>
                <i className="fas fa-chart-line"></i> System Metrics
              </h4>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '12px',
                fontSize: '14px'
              }}>
                {systemHealth.system.uptime && (
                  <div>
                    <strong>Uptime:</strong> {formatUptime(systemHealth.system.uptime)}
                  </div>
                )}
                {systemHealth.system.load_average && (
                  <div>
                    <strong>Load Average:</strong> {systemHealth.system.load_average.join(', ')}
                  </div>
                )}
                <div>
                  <strong>Last Updated:</strong> {formatTimestamp(systemHealth.system.last_check)}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Dashboard Export Modal */}
      {showDashboardExportModal && (
        <div className="modal-overlay" onClick={closeDashboardExportModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2><i className="fas fa-download"></i> Export Dashboard Data</h2>
              <button className="modal-close" onClick={closeDashboardExportModal}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label className="form-label">Export Format</label>
                <select 
                  className="form-control"
                  value={dashboardExportFormat} 
                  onChange={(e) => setDashboardExportFormat(e.target.value)}
                >
                  <option value="json">JSON - Complete Data</option>
                  <option value="csv">CSV - Tabular Format</option>
                  <option value="summary">Summary Report</option>
                </select>
              </div>

              <div className="export-info">
                <div className="export-preview">
                  <div>
                    <strong>Export Details:</strong>
                    <p>Dashboard export will include:</p>
                    <ul>
                      <li>System statistics ({dashboardStats.indicators} IoCs, {dashboardStats.ttps} TTPs, {dashboardStats.threat_feeds} feeds)</li>
                      <li>Recent threat intelligence ({recentIoCs.length} items)</li>
                      <li>System health data</li>
                      <li>Threat activity chart data ({chartData.length} data points)</li>
                    </ul>
                    {dashboardExportFormat === 'csv' && (
                      <p><em>CSV format includes IoCs table and summary metrics.</em></p>
                    )}
                    {dashboardExportFormat === 'json' && (
                      <p><em>JSON format includes complete structured data export.</em></p>
                    )}
                    {dashboardExportFormat === 'summary' && (
                      <p><em>Summary report includes key insights and formatted overview.</em></p>
                    )}
                  </div>
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <div className="modal-actions">
                <button type="button" className="btn btn-outline" onClick={closeDashboardExportModal} disabled={dashboardExporting}>
                  Cancel
                </button>
                <button type="button" className="btn btn-primary" onClick={handleDashboardExport} disabled={dashboardExporting}>
                  {dashboardExporting ? (
                    <><i className="fas fa-spinner fa-spin"></i> Exporting...</>
                  ) : (
                    <><i className="fas fa-download"></i> Export Dashboard</>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

// Threat Feeds Component
