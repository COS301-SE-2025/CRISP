import React, { useState, useEffect, useRef } from 'react';
import * as d3 from 'd3';

const Institutions = ({ active, api, showPage, user }) => {
  const [organizations, setOrganizations] = useState([]);
  const [trustRelationships, setTrustRelationships] = useState([]);
  const [trustGroups, setTrustGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedOrg, setSelectedOrg] = useState(null);
  const [activeView, setActiveView] = useState('overview');
  
  // D3 chart refs
  const orgTypeChartRef = useRef(null);
  const trustNetworkRef = useRef(null);
  const activityTimelineRef = useRef(null);
  const trustLevelChartRef = useRef(null);

  useEffect(() => {
    if (active && user) {
      const token = localStorage.getItem('crisp_auth_token');
      if (token) {
        fetchData();
      }
    }
  }, [active, user]);

  useEffect(() => {
    if (organizations.length > 0 && !loading) {
      createCharts();
    }
  }, [organizations, trustRelationships, activeView, loading]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch all data in parallel
      const [orgData, trustData, groupsData] = await Promise.all([
        api.get('/api/organizations/'),
        api.get('/api/trust/bilateral/'),
        api.get('/api/trust/community/')
      ]);

      // Handle multiple possible API response formats
      if (orgData && orgData.results && orgData.results.organizations) {
        setOrganizations(orgData.results.organizations);
      } else if (orgData && Array.isArray(orgData)) {
        setOrganizations(orgData);
      } else if (orgData && orgData.data && Array.isArray(orgData.data)) {
        setOrganizations(orgData.data);
      } else {
        setOrganizations([]);
        console.log("Organizations API response:", orgData);
      }

      if (trustData && trustData.results && trustData.results.trusts) {
        setTrustRelationships(trustData.results.trusts);
      } else {
        setTrustRelationships([]);
         console.error("Could not fetch trust relationships", trustData);
      }

      if (groupsData && groupsData.results) {
        setTrustGroups(groupsData.results.community_trusts || []);
      } else {
        setTrustGroups([]);
         console.error("Could not fetch trust groups", groupsData);
      }

      if (!orgData || !orgData.results || !orgData.results.organizations || orgData.results.organizations.length === 0) {
        setError('No organizations found. The dashboard requires at least one organization.');
      }
    } catch (err) {
      setError(err.message);
      console.error("Error fetching dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  const getOrganizationTypeIcon = (type) => {
    const icons = {
      'government': 'fas fa-landmark',
      'private': 'fas fa-building',
      'nonprofit': 'fas fa-heart',
      'academic': 'fas fa-graduation-cap',
      'healthcare': 'fas fa-hospital',
      'financial': 'fas fa-university'
    };
    return icons[type?.toLowerCase()] || 'fas fa-building';
  };

  const getOrganizationTypeColor = (type) => {
    const colors = {
      'government': '#28a745',
      'private': '#0056b3',
      'nonprofit': '#dc3545',
      'academic': '#6f42c1',
      'healthcare': '#20c997',
      'financial': '#fd7e14'
    };
    return colors[type?.toLowerCase()] || '#6c757d';
  };

  const createCharts = () => {
    if (activeView === 'overview') {
      createOrganizationTypeChart();
      createTrustLevelChart();
    } else if (activeView === 'network') {
      createTrustNetworkChart();
    } else if (activeView === 'activity') {
      createActivityTimelineChart();
    }
  };

  const createOrganizationTypeChart = () => {
    const container = d3.select(orgTypeChartRef.current);
    container.selectAll("*").remove();

    if (!organizations.length) return;

    const margin = { top: 20, right: 20, bottom: 40, left: 40 };
    const width = 400 - margin.left - margin.right;
    const height = 300 - margin.bottom - margin.top;

    const svg = container
      .append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Process data
    const typeCounts = {};
    organizations.forEach(org => {
      const type = org.organization_type || org.type || 'private';
      typeCounts[type] = (typeCounts[type] || 0) + 1;
    });

    const data = Object.entries(typeCounts).map(([type, count]) => ({ type, count }));

    // Create scales
    const xScale = d3.scaleBand()
      .domain(data.map(d => d.type))
      .range([0, width])
      .padding(0.1);

    const yScale = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.count)])
      .range([height, 0]);

    // Create bars
    g.selectAll('.bar')
      .data(data)
      .enter().append('rect')
      .attr('class', 'bar')
      .attr('x', d => xScale(d.type))
      .attr('width', xScale.bandwidth())
      .attr('y', height)
      .attr('height', 0)
      .attr('fill', d => getOrganizationTypeColor(d.type))
      .transition()
      .duration(800)
      .attr('y', d => yScale(d.count))
      .attr('height', d => height - yScale(d.count));

    // Add value labels
    g.selectAll('.bar-label')
      .data(data)
      .enter().append('text')
      .attr('class', 'bar-label')
      .attr('x', d => xScale(d.type) + xScale.bandwidth() / 2)
      .attr('y', d => yScale(d.count) - 5)
      .attr('text-anchor', 'middle')
      .style('font-size', '12px')
      .style('fill', '#333')
      .text(d => d.count);

    // Add axes
    g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale))
      .selectAll('text')
      .style('text-transform', 'capitalize');

    g.append('g')
      .call(d3.axisLeft(yScale));
  };

  const createTrustLevelChart = () => {
    const container = d3.select(trustLevelChartRef.current);
    container.selectAll("*").remove();

    if (!trustRelationships.length) {
      container.append('div')
        .style('text-align', 'center')
        .style('color', '#6c757d')
        .style('padding', '40px')
        .text('No trust relationship data available');
      return;
    }

    const margin = { top: 20, right: 20, bottom: 20, left: 20 };
    const width = 300;
    const height = 300;
    const radius = Math.min(width, height) / 2 - margin.top;

    const svg = container
      .append('svg')
      .attr('width', width)
      .attr('height', height);

    const g = svg.append('g')
      .attr('transform', `translate(${width/2},${height/2})`);

    // Process trust level data
    const trustLevelCounts = {};
    trustRelationships.forEach(rel => {
      const level = rel.trust_level?.name || 'Unknown';
      trustLevelCounts[level] = (trustLevelCounts[level] || 0) + 1;
    });

    const data = Object.entries(trustLevelCounts).map(([level, count]) => ({ level, count }));

    const color = d3.scaleOrdinal()
      .domain(data.map(d => d.level))
      .range(['#28a745', '#fd7e14', '#dc3545', '#6f42c1']);

    const pie = d3.pie()
      .value(d => d.count);

    const arc = d3.arc()
      .innerRadius(0)
      .outerRadius(radius);

    const arcs = g.selectAll('.arc')
      .data(pie(data))
      .enter().append('g')
      .attr('class', 'arc');

    arcs.append('path')
      .attr('d', arc)
      .attr('fill', d => color(d.data.level))
      .transition()
      .duration(800)
      .attrTween('d', function(d) {
        const interpolate = d3.interpolate({ startAngle: 0, endAngle: 0 }, d);
        return function(t) {
          return arc(interpolate(t));
        };
      });

    arcs.append('text')
      .attr('transform', d => `translate(${arc.centroid(d)})`)
      .attr('text-anchor', 'middle')
      .style('font-size', '12px')
      .style('fill', 'white')
      .text(d => d.data.count);
  };

  const createTrustNetworkChart = () => {
    const container = d3.select(trustNetworkRef.current);
    container.selectAll("*").remove();

    if (!organizations.length || !trustRelationships.length) {
      container.append('div')
        .style('text-align', 'center')
        .style('color', '#6c757d')
        .style('padding', '40px')
        .text('No network data available');
      return;
    }

    const width = 800;
    const height = 600;

    const svg = container
      .append('svg')
      .attr('width', width)
      .attr('height', height);

    // Create network data
    const nodes = organizations.slice(0, 20).map(org => ({
      id: org.id,
      name: org.name,
      type: org.organization_type || org.type || 'private',
      group: org.organization_type || org.type || 'private'
    }));

    const links = trustRelationships
      .filter(rel => 
        nodes.find(n => n.id === rel.source_organization?.id) &&
        nodes.find(n => n.id === rel.target_organization?.id)
      )
      .map(rel => ({
        source: rel.source_organization.id,
        target: rel.target_organization.id,
        value: rel.trust_level?.numerical_value || 50
      }));

    // Create force simulation
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2));

    const color = d3.scaleOrdinal()
      .domain(['government', 'private', 'nonprofit', 'academic', 'healthcare', 'financial'])
      .range(['#28a745', '#0056b3', '#dc3545', '#6f42c1', '#20c997', '#fd7e14']);

    // Add links
    const link = svg.append('g')
      .selectAll('line')
      .data(links)
      .enter().append('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', d => Math.sqrt(d.value / 10));

    // Add nodes
    const node = svg.append('g')
      .selectAll('circle')
      .data(nodes)
      .enter().append('circle')
      .attr('r', 8)
      .attr('fill', d => color(d.group))
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));

    // Add labels
    const label = svg.append('g')
      .selectAll('text')
      .data(nodes)
      .enter().append('text')
      .text(d => d.name.length > 15 ? d.name.substring(0, 15) + '...' : d.name)
      .style('font-size', '10px')
      .style('fill', '#333')
      .attr('dx', 12)
      .attr('dy', 4);

    simulation
      .nodes(nodes)
      .on('tick', ticked);

    simulation.force('link')
      .links(links);

    function ticked() {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);

      label
        .attr('x', d => d.x)
        .attr('y', d => d.y);
    }

    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
  };

  const createActivityTimelineChart = () => {
    const container = d3.select(activityTimelineRef.current);
    container.selectAll("*").remove();

    if (!organizations.length) return;

    const margin = { top: 20, right: 30, bottom: 40, left: 50 };
    const width = 800 - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;

    const svg = container
      .append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Generate timeline data
    const now = new Date();
    const timelineData = [];
    for (let i = 29; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);
      const count = Math.floor(Math.random() * 10) + 1;
      timelineData.push({ date, count });
    }

    const xScale = d3.scaleTime()
      .domain(d3.extent(timelineData, d => d.date))
      .range([0, width]);

    const yScale = d3.scaleLinear()
      .domain([0, d3.max(timelineData, d => d.count)])
      .range([height, 0]);

    const line = d3.line()
      .x(d => xScale(d.date))
      .y(d => yScale(d.count))
      .curve(d3.curveMonotoneX);

    // Add line
    g.append('path')
      .datum(timelineData)
      .attr('fill', 'none')
      .attr('stroke', '#0056b3')
      .attr('stroke-width', 2)
      .attr('d', line);

    // Add dots
    g.selectAll('.dot')
      .data(timelineData)
      .enter().append('circle')
      .attr('class', 'dot')
      .attr('cx', d => xScale(d.date))
      .attr('cy', d => yScale(d.count))
      .attr('r', 3)
      .attr('fill', '#0056b3');

    // Add axes
    g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale).tickFormat(d3.timeFormat('%m/%d')));

    g.append('g')
      .call(d3.axisLeft(yScale));
  };

  if (!active) return null;

  if (loading) {
    return (
      <div className="institutions-page">
        <div className="loading-state">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading organizations dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="institutions-page">
        <div className="error-state">
          <i className="fas fa-exclamation-triangle"></i>
          <p>Error loading organizations: {error}</p>
          <button onClick={fetchData} className="btn btn-primary">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <section id="organizations" className={`page-section ${active ? 'active' : ''}`}>
      {/* Page Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Organizations</h1>
          <p className="page-subtitle">Manage connected organizations and trust relationships</p>
        </div>
        <div className="action-buttons">
          <button className="btn btn-outline" onClick={() => setActiveView('organizations')}>
            <i className="fas fa-building"></i> All Organizations
          </button>
          <button className="btn btn-outline" onClick={() => setActiveView('trust-relationships')}>
            <i className="fas fa-handshake"></i> Trust Relationships  
          </button>
          <button className="btn btn-outline" onClick={() => setActiveView('trust-groups')}>
            <i className="fas fa-users"></i> Trust Groups
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-title">
            <div className="stat-icon"><i className="fas fa-building"></i></div>
            <span>Total Organizations</span>
          </div>
          <div className="stat-value">
            {organizations.length}
          </div>
          <div className="stat-change neutral">
            <span><i className="fas fa-circle"></i></span>
            <span>All registered</span>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-title">
            <div className="stat-icon"><i className="fas fa-users"></i></div>
            <span>Total Members</span>
          </div>
          <div className="stat-value">
            {organizations.reduce((sum, org) => sum + (org.member_count || 0), 0)}
          </div>
          <div className="stat-change increase">
            <span><i className="fas fa-arrow-up"></i></span>
            <span>Across all orgs</span>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-title">
            <div className="stat-icon"><i className="fas fa-handshake"></i></div>
            <span>Trust Relationships</span>
          </div>
          <div className="stat-value">
            {trustRelationships.length}
          </div>
          <div className="stat-change neutral">
            <span><i className="fas fa-link"></i></span>
            <span>Active connections</span>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-title">
            <div className="stat-icon"><i className="fas fa-shield-check"></i></div>
            <span>Active Organizations</span>
          </div>
          <div className="stat-value">
            {organizations.filter(org => org.is_active !== false).length}
          </div>
          <div className="stat-change increase">
            <span><i className="fas fa-check"></i></span>
            <span>Online now</span>
          </div>
        </div>
      </div>

      {/* Overview Content */}
      {activeView === 'overview' && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '2rem',
          alignItems: 'start'
        }}>
          {/* Left Column - Organizations and Trust Groups stacked */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
            {/* Organizations Preview */}
            <div style={{
              background: 'white',
              borderRadius: '8px',
              padding: '1.5rem',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
              border: '1px solid #e5e7eb'
            }}>
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem'}}>
              <h3 style={{margin: 0, fontSize: '1.125rem', fontWeight: '600', color: '#333'}}>Recent Organizations</h3>
              <button 
                className="btn btn-sm btn-outline"
                onClick={() => setActiveView('organizations')}
              >
                <i className="fas fa-arrow-right"></i> View All ({organizations.length})
              </button>
            </div>
            
            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Organization</th>
                    <th>Type</th>
                    <th>Members</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {organizations.length === 0 ? (
                    <tr>
                      <td colSpan="4" style={{textAlign: 'center', padding: '2rem', color: '#666'}}>
                        <i className="fas fa-building" style={{fontSize: '2rem', marginBottom: '1rem', opacity: 0.3}}></i>
                        <div>No organizations found</div>
                      </td>
                    </tr>
                  ) : (
                    organizations.slice(0, 5).map(org => (
                      <tr key={org.id}>
                        <td>
                          <div style={{display: 'flex', alignItems: 'center', gap: '0.75rem'}}>
                            <i 
                              className={getOrganizationTypeIcon(org.organization_type || org.type)}
                              style={{ 
                                color: getOrganizationTypeColor(org.organization_type || org.type),
                                fontSize: '1.25rem' 
                              }}
                            ></i>
                            <div>
                              <div style={{fontWeight: '600', color: '#333'}}>{org.name}</div>
                              {org.description && (
                                <div style={{fontSize: '0.75rem', color: '#666', marginTop: '0.125rem'}}>
                                  {org.description.length > 40 ? org.description.substring(0, 40) + '...' : org.description}
                                </div>
                              )}
                            </div>
                          </div>
                        </td>
                        <td>
                          <span style={{
                            backgroundColor: getOrganizationTypeColor(org.organization_type || org.type) + '20',
                            color: getOrganizationTypeColor(org.organization_type || org.type),
                            padding: '0.25rem 0.5rem',
                            borderRadius: '4px',
                            fontSize: '0.75rem',
                            fontWeight: '600',
                            textTransform: 'capitalize'
                          }}>
                            {org.organization_type || org.type || 'Unknown'}
                          </span>
                        </td>
                        <td style={{color: '#333', fontWeight: '500'}}>
                          {org.member_count || 0}
                        </td>
                        <td>
                          <span style={{
                            padding: '0.25rem 0.5rem',
                            borderRadius: '4px',
                            fontSize: '0.75rem',
                            fontWeight: '600',
                            backgroundColor: org.is_active !== false ? '#e8f5e8' : '#fff3e0',
                            color: org.is_active !== false ? '#2e7d32' : '#f57c00'
                          }}>
                            {org.is_active !== false ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

            {/* Trust Groups Preview - Now in left column under Organizations */}
            <div style={{
              background: 'white',
              borderRadius: '8px',
              padding: '1.5rem',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
              border: '1px solid #e5e7eb'
            }}>
              <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem'}}>
                <h3 style={{margin: 0, fontSize: '1.125rem', fontWeight: '600', color: '#333'}}>Trust Groups</h3>
                <button 
                  className="btn btn-sm btn-outline"
                  onClick={() => setActiveView('trust-groups')}
                >
                  <i className="fas fa-arrow-right"></i> View All ({trustGroups.length})
                </button>
              </div>
              
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '1rem'
              }}>
                {trustGroups.length === 0 ? (
                  <div style={{
                    textAlign: 'center',
                    padding: '2rem',
                    color: '#666'
                  }}>
                    <i className="fas fa-users" style={{fontSize: '2rem', marginBottom: '1rem', opacity: 0.3}}></i>
                    <div>No trust groups found</div>
                  </div>
                ) : (
                  trustGroups.slice(0, 3).map((group, index) => (
                    <div key={index} style={{
                      padding: '1rem',
                      border: '1px solid #e5e7eb',
                      borderRadius: '6px',
                      background: '#f9fafb'
                    }}>
                      <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem'}}>
                        <i className="fas fa-users" style={{
                          color: '#667eea',
                          fontSize: '1rem'
                        }}></i>
                        <h4 style={{margin: 0, fontSize: '0.875rem', fontWeight: '600', color: '#333'}}>
                          {group.name}
                        </h4>
                      </div>
                      
                      {group.description && (
                        <p style={{
                          fontSize: '0.75rem',
                          color: '#666',
                          margin: '0 0 0.5rem 0',
                          lineHeight: 1.4
                        }}>
                          {group.description.length > 60 ? group.description.substring(0, 60) + '...' : group.description}
                        </p>
                      )}
                      
                      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
                        <span style={{fontSize: '0.625rem', color: '#666'}}>
                          {group.member_count || 0} members
                        </span>
                        <span style={{
                          fontSize: '0.5rem',
                          padding: '0.125rem 0.25rem',
                          borderRadius: '3px',
                          backgroundColor: group.is_active ? '#dcfce7' : '#fee2e2',
                          color: group.is_active ? '#166534' : '#dc2626',
                          textTransform: 'uppercase',
                          fontWeight: '600'
                        }}>
                          {group.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Right Column - Trust Relationships */}
          <div style={{
            background: 'white',
            borderRadius: '8px',
            padding: '1.5rem',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            border: '1px solid #e5e7eb'
          }}>
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem'}}>
              <h3 style={{margin: 0, fontSize: '1.125rem', fontWeight: '600', color: '#333'}}>Trust Relationships</h3>
              <button 
                className="btn btn-sm btn-outline"
                onClick={() => setActiveView('trust-relationships')}
              >
                <i className="fas fa-arrow-right"></i> View All ({trustRelationships.length})
              </button>
            </div>
            
            <div style={{display: 'flex', flexDirection: 'column', gap: '1rem'}}>
              {trustRelationships.length === 0 ? (
                <div style={{textAlign: 'center', padding: '2rem', color: '#666'}}>
                  <i className="fas fa-handshake" style={{fontSize: '2rem', marginBottom: '1rem', opacity: 0.3}}></i>
                  <div style={{fontSize: '0.875rem'}}>No trust relationships</div>
                </div>
              ) : (
                trustRelationships.slice(0, 4).map((trust, index) => (
                  <div key={index} style={{
                    padding: '1rem',
                    border: '1px solid #e5e7eb',
                    borderRadius: '6px',
                    background: '#f9fafb'
                  }}>
                    <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem'}}>
                      <i className="fas fa-handshake" style={{color: '#667eea', fontSize: '1rem'}}></i>
                      <span style={{fontSize: '0.875rem', fontWeight: '600', color: '#333'}}>
                        {trust.relationship_type || 'Partnership'}
                      </span>
                    </div>
                    <div style={{fontSize: '0.75rem', color: '#666', lineHeight: 1.4}}>
                      <div><strong>{trust.source_organization?.name || 'Organization A'}</strong></div>
                      <div style={{margin: '0.25rem 0', color: '#999'}}>↔</div>
                      <div><strong>{trust.target_organization?.name || 'Organization B'}</strong></div>
                    </div>
                    <div style={{marginTop: '0.5rem'}}>
                      <span style={{
                        fontSize: '0.625rem',
                        padding: '0.125rem 0.375rem',
                        borderRadius: '3px',
                        backgroundColor: trust.status === 'active' ? '#dcfce7' : '#fef3c7',
                        color: trust.status === 'active' ? '#166534' : '#92400e',
                        textTransform: 'uppercase',
                        fontWeight: '600'
                      }}>
                        {trust.status || 'pending'}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* All Organizations View */}
      {activeView === 'organizations' && (
        <div style={{
          background: 'white',
          borderRadius: '8px',
          padding: '1.5rem',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          border: '1px solid #e5e7eb'
        }}>
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem'}}>
            <h3 style={{margin: 0, fontSize: '1.125rem', fontWeight: '600', color: '#333'}}>All Organizations ({organizations.length})</h3>
            <button 
              className="btn btn-sm btn-outline"
              onClick={() => setActiveView('overview')}
            >
              <i className="fas fa-arrow-left"></i> Back to Overview
            </button>
          </div>
          
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Organization</th>
                  <th>Type</th>
                  <th>Members</th>
                  <th>Trust Relationships</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {organizations.length === 0 ? (
                  <tr>
                    <td colSpan="7" style={{textAlign: 'center', padding: '2rem', color: '#666'}}>
                      <i className="fas fa-building" style={{fontSize: '2rem', marginBottom: '1rem', opacity: 0.3}}></i>
                      <div>No organizations found</div>
                    </td>
                  </tr>
                ) : (
                  organizations.map(org => (
                    <tr key={org.id}>
                      <td>
                        <div style={{display: 'flex', alignItems: 'center', gap: '0.75rem'}}>
                          <i 
                            className={getOrganizationTypeIcon(org.organization_type || org.type)}
                            style={{ 
                              color: getOrganizationTypeColor(org.organization_type || org.type),
                              fontSize: '1.25rem' 
                            }}
                          ></i>
                          <div>
                            <div style={{fontWeight: '600', color: '#333'}}>{org.name}</div>
                            {org.description && (
                              <div style={{fontSize: '0.75rem', color: '#666', marginTop: '0.125rem'}}>
                                {org.description.length > 50 ? org.description.substring(0, 50) + '...' : org.description}
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td>
                        <span style={{
                          backgroundColor: getOrganizationTypeColor(org.organization_type || org.type) + '20',
                          color: getOrganizationTypeColor(org.organization_type || org.type),
                          padding: '0.25rem 0.5rem',
                          borderRadius: '4px',
                          fontSize: '0.75rem',
                          fontWeight: '600',
                          textTransform: 'capitalize'
                        }}>
                          {org.organization_type || org.type || 'Unknown'}
                        </span>
                      </td>
                      <td style={{color: '#333', fontWeight: '500'}}>
                        {org.member_count || 0}
                      </td>
                      <td style={{color: '#333', fontWeight: '500'}}>
                        {org.trust_relationships_count || 0}
                      </td>
                      <td>
                        <span style={{
                          padding: '0.25rem 0.5rem',
                          borderRadius: '4px',
                          fontSize: '0.75rem',
                          fontWeight: '600',
                          backgroundColor: org.is_active !== false ? '#e8f5e8' : '#fff3e0',
                          color: org.is_active !== false ? '#2e7d32' : '#f57c00'
                        }}>
                          {org.is_active !== false ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td style={{color: '#666', fontSize: '0.875rem'}}>
                        {org.created_at ? new Date(org.created_at).toLocaleDateString() : 'Unknown'}
                      </td>
                      <td>
                        <div style={{display: 'flex', gap: '0.5rem'}}>
                          <button 
                            className="btn btn-sm btn-outline"
                            onClick={() => setSelectedOrg(org)}
                            style={{padding: '0.25rem 0.5rem', fontSize: '0.75rem'}}
                          >
                            <i className="fas fa-eye"></i>
                          </button>
                          <button 
                            className="btn btn-sm btn-outline"
                            style={{padding: '0.25rem 0.5rem', fontSize: '0.75rem'}}
                          >
                            <i className="fas fa-edit"></i>
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* All Trust Relationships View */}
      {activeView === 'trust-relationships' && (
        <div style={{
          background: 'white',
          borderRadius: '8px',
          padding: '1.5rem',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          border: '1px solid #e5e7eb'
        }}>
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem'}}>
            <h3 style={{margin: 0, fontSize: '1.125rem', fontWeight: '600', color: '#333'}}>All Trust Relationships ({trustRelationships.length})</h3>
            <button 
              className="btn btn-sm btn-outline"
              onClick={() => setActiveView('overview')}
            >
              <i className="fas fa-arrow-left"></i> Back to Overview
            </button>
          </div>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
            gap: '1rem'
          }}>
            {trustRelationships.length === 0 ? (
              <div style={{
                gridColumn: '1 / -1',
                textAlign: 'center',
                padding: '3rem',
                color: '#666'
              }}>
                <i className="fas fa-handshake" style={{fontSize: '3rem', marginBottom: '1rem', opacity: 0.3}}></i>
                <div>No trust relationships found</div>
              </div>
            ) : (
              trustRelationships.map((trust, index) => (
                <div key={index} style={{
                  padding: '1.5rem',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  background: '#f9fafb'
                }}>
                  <div style={{display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem'}}>
                    <i className="fas fa-handshake" style={{color: '#667eea', fontSize: '1.25rem'}}></i>
                    <h4 style={{margin: 0, fontSize: '1rem', fontWeight: '600', color: '#333'}}>
                      {trust.relationship_type || 'Partnership'}
                    </h4>
                    <span style={{
                      fontSize: '0.625rem',
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      backgroundColor: trust.status === 'active' ? '#dcfce7' : '#fef3c7',
                      color: trust.status === 'active' ? '#166534' : '#92400e',
                      textTransform: 'uppercase',
                      fontWeight: '600',
                      marginLeft: 'auto'
                    }}>
                      {trust.status || 'pending'}
                    </span>
                  </div>
                  <div style={{fontSize: '0.875rem', color: '#666', lineHeight: 1.5}}>
                    <div style={{marginBottom: '0.5rem'}}>
                      <strong>From:</strong> {trust.source_organization?.name || 'Organization A'}
                    </div>
                    <div style={{marginBottom: '0.5rem'}}>
                      <strong>To:</strong> {trust.target_organization?.name || 'Organization B'}
                    </div>
                    {trust.trust_level && (
                      <div style={{marginBottom: '0.5rem'}}>
                        <strong>Trust Level:</strong> {trust.trust_level.name || trust.trust_level}
                      </div>
                    )}
                    {trust.notes && (
                      <div style={{marginTop: '0.75rem', fontSize: '0.75rem', fontStyle: 'italic'}}>
                        "{trust.notes}"
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* All Trust Groups View */}
      {activeView === 'trust-groups' && (
        <div style={{
          background: 'white',
          borderRadius: '8px',
          padding: '1.5rem',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          border: '1px solid #e5e7eb'
        }}>
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem'}}>
            <h3 style={{margin: 0, fontSize: '1.125rem', fontWeight: '600', color: '#333'}}>All Trust Groups ({trustGroups.length})</h3>
            <button 
              className="btn btn-sm btn-outline"
              onClick={() => setActiveView('overview')}
            >
              <i className="fas fa-arrow-left"></i> Back to Overview
            </button>
          </div>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
            gap: '1.5rem'
          }}>
            {trustGroups.length === 0 ? (
              <div style={{
                gridColumn: '1 / -1',
                textAlign: 'center',
                padding: '3rem',
                color: '#666'
              }}>
                <i className="fas fa-users" style={{fontSize: '3rem', marginBottom: '1rem', opacity: 0.3}}></i>
                <div>No trust groups found</div>
              </div>
            ) : (
              trustGroups.map((group, index) => (
                <div key={index} style={{
                  padding: '1.5rem',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  background: '#f9fafb'
                }}>
                  <div style={{display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem'}}>
                    <i className="fas fa-users" style={{
                      color: '#667eea',
                      fontSize: '1.25rem'
                    }}></i>
                    <h4 style={{margin: 0, fontSize: '1.125rem', fontWeight: '600', color: '#333'}}>
                      {group.name}
                    </h4>
                    <span style={{
                      fontSize: '0.625rem',
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      backgroundColor: group.is_active ? '#dcfce7' : '#fee2e2',
                      color: group.is_active ? '#166534' : '#dc2626',
                      textTransform: 'uppercase',
                      fontWeight: '600',
                      marginLeft: 'auto'
                    }}>
                      {group.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  
                  {group.description && (
                    <p style={{
                      fontSize: '0.875rem',
                      color: '#666',
                      margin: '0 0 1rem 0',
                      lineHeight: 1.5
                    }}>
                      {group.description}
                    </p>
                  )}
                  
                  <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem'}}>
                    <span style={{fontSize: '0.875rem', color: '#666'}}>
                      <strong>{group.member_count || 0}</strong> members
                    </span>
                    {group.group_type && (
                      <span style={{
                        fontSize: '0.75rem',
                        color: '#667eea',
                        backgroundColor: '#667eea20',
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                        textTransform: 'capitalize'
                      }}>
                        {group.group_type}
                      </span>
                    )}
                  </div>
                  
                  {group.default_trust_level && (
                    <div style={{fontSize: '0.75rem', color: '#666', marginBottom: '0.5rem'}}>
                      <strong>Default Trust:</strong> {group.default_trust_level.name || group.default_trust_level}
                    </div>
                  )}
                  
                  <div style={{display: 'flex', gap: '0.5rem', marginTop: '1rem'}}>
                    <button className="btn btn-sm btn-outline" style={{flex: 1}}>
                      <i className="fas fa-eye"></i> View Details
                    </button>
                    <button className="btn btn-sm btn-outline" style={{flex: 1}}>
                      <i className="fas fa-edit"></i> Edit
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}


      {selectedOrg && (
        <div className="modal-overlay">
          <div className="modal large">
            <div className="modal-header">
              <h3>{selectedOrg.name}</h3>
              <button 
                className="close-btn"
                onClick={() => setSelectedOrg(null)}
              >
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              <div className="org-detail-grid">
                <div className="detail-section">
                  <h4>Basic Information</h4>
                  <div className="detail-row">
                    <label>Name:</label>
                    <span>{selectedOrg.name}</span>
                  </div>
                  <div className="detail-row">
                    <label>Type:</label>
                    <span>{selectedOrg.type || 'Not specified'}</span>
                  </div>
                  <div className="detail-row">
                    <label>Description:</label>
                    <span>{selectedOrg.description || 'No description provided'}</span>
                  </div>
                </div>
                
                <div className="detail-section">
                  <h4>Statistics</h4>
                  <div className="detail-row">
                    <label>Members:</label>
                    <span>{selectedOrg.member_count || 0}</span>
                  </div>
                  <div className="detail-row">
                    <label>Trust Relationships:</label>
                    <span>{selectedOrg.trust_relationships_count || 0}</span>
                  </div>
                  <div className="detail-row">
                    <label>Status:</label>
                    <span className={`status-badge ${selectedOrg.is_active ? 'active' : 'inactive'}`}>
                      {selectedOrg.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button
                className="btn btn-secondary"
                onClick={() => setSelectedOrg(null)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
    .table-responsive {
      width: 100%;
      min-width: 0;
      height: 100%;
    }
  `}</style>
    </section>
  );
};

export default Institutions;