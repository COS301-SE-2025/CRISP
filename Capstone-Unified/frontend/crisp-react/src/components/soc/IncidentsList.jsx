import React, { useState, useEffect } from 'react';
import * as api from '../../api.js';

const IncidentsList = ({ active }) => {
  if (!active) return null;
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    status: '',
    priority: '',
    category: '',
    search: ''
  });
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    fetchIncidents();
  }, [filters, currentPage]);

  const fetchIncidents = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: currentPage,
        page_size: 20,
        ...Object.fromEntries(Object.entries(filters).filter(([_, v]) => v))
      });
      
      const response = await api.get(`/api/soc/incidents/?${params.toString()}`);
      if (response?.data) {
        setIncidents(response.data);
        setTotalPages(Math.ceil(response.count / 20));
        setError(null);
      }
    } catch (err) {
      setError('Failed to load incidents');
      console.error('Incidents List Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setCurrentPage(1); // Reset to first page when filtering
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
      case 'false_positive': return '#6f42c1';
      default: return '#6c757d';
    }
  };

  const CreateIncidentModal = () => {
    const [formData, setFormData] = useState({
      title: '',
      description: '',
      category: 'other',
      priority: 'medium',
      severity: 'medium',
      source: 'manual',
      tags: []
    });
    const [creating, setCreating] = useState(false);

    const handleSubmit = async (e) => {
      e.preventDefault();
      try {
        setCreating(true);
        await api.post('/api/soc/incidents/', formData);
        setShowCreateModal(false);
        setFormData({
          title: '',
          description: '',
          category: 'other',
          priority: 'medium',
          severity: 'medium',
          source: 'manual',
          tags: []
        });
        fetchIncidents(); // Refresh the list
      } catch (err) {
        alert('Failed to create incident: ' + err.message);
      } finally {
        setCreating(false);
      }
    };

    if (!showCreateModal) return null;

    return (
      <div className="modal" style={{ display: 'block', backgroundColor: 'rgba(0,0,0,0.5)' }}>
        <div className="modal-dialog modal-lg">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title">Create New Incident</h5>
              <button 
                type="button" 
                className="close" 
                onClick={() => setShowCreateModal(false)}
              >
                <span>&times;</span>
              </button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                <div className="form-group">
                  <label>Title *</label>
                  <input
                    type="text"
                    className="form-control"
                    value={formData.title}
                    onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                    required
                  />
                </div>
                
                <div className="form-group">
                  <label>Description *</label>
                  <textarea
                    className="form-control"
                    rows="4"
                    value={formData.description}
                    onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                    required
                  />
                </div>

                <div className="row">
                  <div className="col-md-4">
                    <div className="form-group">
                      <label>Category *</label>
                      <select
                        className="form-control"
                        value={formData.category}
                        onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                      >
                        <option value="malware">Malware</option>
                        <option value="phishing">Phishing</option>
                        <option value="data_breach">Data Breach</option>
                        <option value="unauthorized_access">Unauthorized Access</option>
                        <option value="ddos">DDoS Attack</option>
                        <option value="insider_threat">Insider Threat</option>
                        <option value="ransomware">Ransomware</option>
                        <option value="apt">Advanced Persistent Threat</option>
                        <option value="vulnerability">Vulnerability</option>
                        <option value="policy_violation">Policy Violation</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                  </div>
                  
                  <div className="col-md-4">
                    <div className="form-group">
                      <label>Priority *</label>
                      <select
                        className="form-control"
                        value={formData.priority}
                        onChange={(e) => setFormData(prev => ({ ...prev, priority: e.target.value }))}
                      >
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                        <option value="critical">Critical</option>
                      </select>
                    </div>
                  </div>
                  
                  <div className="col-md-4">
                    <div className="form-group">
                      <label>Severity *</label>
                      <select
                        className="form-control"
                        value={formData.severity}
                        onChange={(e) => setFormData(prev => ({ ...prev, severity: e.target.value }))}
                      >
                        <option value="informational">Informational</option>
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                        <option value="critical">Critical</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={() => setShowCreateModal(false)}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={creating}
                >
                  {creating ? (
                    <>
                      <span className="spinner-border spinner-border-sm mr-2"></span>
                      Creating...
                    </>
                  ) : (
                    'Create Incident'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <div className="spinner-border" role="status">
          <span className="sr-only">Loading incidents...</span>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>
          <i className="fas fa-exclamation-circle mr-2"></i>
          SOC Incidents
        </h2>
        <button 
          className="btn btn-primary"
          onClick={() => setShowCreateModal(true)}
        >
          <i className="fas fa-plus mr-2"></i>
          Create Incident
        </button>
      </div>

      {/* Filters */}
      <div className="card mb-4">
        <div className="card-body">
          <div className="row">
            <div className="col-md-3">
              <div className="form-group">
                <label>Status</label>
                <select
                  className="form-control"
                  value={filters.status}
                  onChange={(e) => handleFilterChange('status', e.target.value)}
                >
                  <option value="">All Statuses</option>
                  <option value="new">New</option>
                  <option value="assigned">Assigned</option>
                  <option value="in_progress">In Progress</option>
                  <option value="resolved">Resolved</option>
                  <option value="closed">Closed</option>
                  <option value="false_positive">False Positive</option>
                </select>
              </div>
            </div>
            
            <div className="col-md-3">
              <div className="form-group">
                <label>Priority</label>
                <select
                  className="form-control"
                  value={filters.priority}
                  onChange={(e) => handleFilterChange('priority', e.target.value)}
                >
                  <option value="">All Priorities</option>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
            </div>
            
            <div className="col-md-3">
              <div className="form-group">
                <label>Category</label>
                <select
                  className="form-control"
                  value={filters.category}
                  onChange={(e) => handleFilterChange('category', e.target.value)}
                >
                  <option value="">All Categories</option>
                  <option value="malware">Malware</option>
                  <option value="phishing">Phishing</option>
                  <option value="data_breach">Data Breach</option>
                  <option value="unauthorized_access">Unauthorized Access</option>
                  <option value="ddos">DDoS Attack</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>
            
            <div className="col-md-3">
              <div className="form-group">
                <label>Search</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Search title or ID..."
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {error && (
        <div className="alert alert-danger" role="alert">
          <i className="fas fa-exclamation-triangle mr-2"></i>
          {error}
          <button 
            className="btn btn-outline-danger btn-sm ml-3"
            onClick={fetchIncidents}
          >
            Retry
          </button>
        </div>
      )}

      {/* Incidents Table */}
      <div className="card">
        <div className="card-body p-0">
          {incidents.length === 0 ? (
            <div className="text-center p-4 text-muted">
              <i className="fas fa-info-circle mr-2"></i>
              No incidents found
            </div>
          ) : (
            <div className="table-responsive">
              <table className="table table-hover mb-0">
                <thead className="thead-light">
                  <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Category</th>
                    <th>Priority</th>
                    <th>Status</th>
                    <th>Assigned To</th>
                    <th>Created</th>
                    <th>SLA</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {incidents.map((incident) => (
                    <tr 
                      key={incident.id}
                      style={{ cursor: 'pointer' }}
                      onClick={() => window.location.hash = `dashboard?page=soc-incident-detail&id=${incident.id}`}
                    >
                      <td>
                        <code>{incident.incident_id}</code>
                      </td>
                      <td>
                        <div style={{ maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {incident.title}
                        </div>
                      </td>
                      <td>
                        <span className="badge badge-secondary">
                          {incident.category_display}
                        </span>
                      </td>
                      <td>
                        <span 
                          className="badge" 
                          style={{ backgroundColor: getPriorityColor(incident.priority), color: 'white' }}
                        >
                          {incident.priority_display}
                        </span>
                      </td>
                      <td>
                        <span 
                          className="badge" 
                          style={{ backgroundColor: getStatusColor(incident.status), color: 'white' }}
                        >
                          {incident.status_display}
                        </span>
                      </td>
                      <td>
                        {incident.assigned_to || <span className="text-muted">Unassigned</span>}
                      </td>
                      <td>
                        <small>{new Date(incident.created_at).toLocaleString()}</small>
                      </td>
                      <td>
                        {incident.is_overdue && (
                          <span className="badge badge-danger">
                            <i className="fas fa-exclamation-triangle mr-1"></i>
                            Overdue
                          </span>
                        )}
                        {incident.sla_deadline && !incident.is_overdue && (
                          <small className="text-muted">
                            {new Date(incident.sla_deadline).toLocaleDateString()}
                          </small>
                        )}
                      </td>
                      <td onClick={(e) => e.stopPropagation()}>
                        <button 
                          className="btn btn-sm btn-outline-primary"
                          onClick={() => window.location.hash = `dashboard?page=soc-incident-detail&id=${incident.id}`}
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="card-footer">
            <nav>
              <ul className="pagination justify-content-center mb-0">
                <li className={`page-item ${currentPage === 1 ? 'disabled' : ''}`}>
                  <button 
                    className="page-link" 
                    onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                    disabled={currentPage === 1}
                  >
                    Previous
                  </button>
                </li>
                
                {[...Array(totalPages)].map((_, index) => {
                  const page = index + 1;
                  if (page === 1 || page === totalPages || (page >= currentPage - 2 && page <= currentPage + 2)) {
                    return (
                      <li key={page} className={`page-item ${currentPage === page ? 'active' : ''}`}>
                        <button 
                          className="page-link" 
                          onClick={() => setCurrentPage(page)}
                        >
                          {page}
                        </button>
                      </li>
                    );
                  }
                  return null;
                })}
                
                <li className={`page-item ${currentPage === totalPages ? 'disabled' : ''}`}>
                  <button 
                    className="page-link" 
                    onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                    disabled={currentPage === totalPages}
                  >
                    Next
                  </button>
                </li>
              </ul>
            </nav>
          </div>
        )}
      </div>

      <CreateIncidentModal />
    </div>
  );
};

export default IncidentsList;