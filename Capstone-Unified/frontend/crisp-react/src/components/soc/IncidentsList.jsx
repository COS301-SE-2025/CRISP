import React, { useState, useEffect } from 'react';
import * as api from '../../api.js';

const IncidentsList = ({ active, showPage }) => {
  if (!active) return null;
  
  // Check if user is BlueVisionAdmin
  const currentUser = api.getCurrentUser();
  if (!currentUser || currentUser.role !== 'BlueVisionAdmin') {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <div className="alert alert-warning" role="alert">
          <i className="fas fa-lock mr-2"></i>
          <strong>Access Restricted</strong>
          <p className="mb-0 mt-2">SOC features are only available to BlueVision administrators.</p>
        </div>
      </div>
    );
  }
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
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [availableUsers, setAvailableUsers] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    fetchIncidents();
  }, [filters, currentPage]);

  useEffect(() => {
    fetchAvailableUsers();
  }, []); // Only fetch users once on component mount

  const fetchAvailableUsers = async () => {
    try {
      console.log('=== FETCHING USERS ===');
      console.log('Calling api.getUsersList()...');
      
      const response = await api.getUsersList();
      console.log('Raw API Response:', response);
      console.log('Response structure check:');
      console.log('  - response.results:', response?.results);
      console.log('  - response.results.users:', response?.results?.users);
      console.log('  - Is response.results.users an array?', Array.isArray(response?.results?.users));
      
      // Handle the specific response format: {count, next, previous, results: {success, users}}
      let users = [];
      
      if (response?.results?.users && Array.isArray(response.results.users)) {
        console.log('✓ Using response.results.users (paginated format)');
        users = response.results.users;
      } else if (response?.success && response?.users && Array.isArray(response.users)) {
        console.log('✓ Using response.users (direct success format)');
        users = response.users;
      } else if (response?.success && response?.data && Array.isArray(response.data)) {
        console.log('✓ Using response.data (success format)');
        users = response.data;
      } else if (response?.data && Array.isArray(response.data)) {
        console.log('✓ Using response.data (array format)');
        users = response.data;
      } else if (response?.results && Array.isArray(response.results)) {
        console.log('✓ Using response.results (array format)');
        users = response.results;
      } else if (Array.isArray(response)) {
        console.log('✓ Using response as direct array');
        users = response;
      } else {
        console.warn('❌ Unknown response format, trying to extract from nested structures');
        console.log('Full response:', JSON.stringify(response, null, 2));
        
        // More specific extraction attempts
        if (response?.data?.users) {
          console.log('✓ Found response.data.users');
          users = response.data.users;
        } else if (response?.results?.data?.users) {
          console.log('✓ Found response.results.data.users');
          users = response.results.data.users;
        } else {
          console.error('❌ Could not find users array in response');
        }
      }
      
      console.log('Extracted users:', users);
      console.log('Users array length:', users ? users.length : 'undefined');
      console.log('Users type:', typeof users);
      console.log('Is users array?', Array.isArray(users));
      
      // DIRECT FIX: If users is still an object with a users property, extract it
      if (!Array.isArray(users) && users?.users && Array.isArray(users.users)) {
        console.log('🔧 DIRECT FIX: Extracting users from object format');
        users = users.users;
        console.log('After direct fix - users:', users);
        console.log('After direct fix - length:', users.length);
      }
      
      // Check the structure of the first user
      if (users && users.length > 0) {
        console.log('First user structure:', users[0]);
        console.log('User keys:', Object.keys(users[0]));
      } else {
        console.warn('No users found or users is not an array');
      }
      
      setAvailableUsers(users || []);
    } catch (err) {
      console.error('=== USER FETCH ERROR ===');
      console.error('Error details:', err);
      console.error('Error message:', err.message);
      setAvailableUsers([]);
    }
  };

  const fetchIncidents = async () => {
    try {
      setLoading(true);
      const queryParams = {
        page: currentPage,
        page_size: 20,
        ...Object.fromEntries(Object.entries(filters).filter(([_, v]) => v))
      };
      
      console.log('Fetching incidents with params:', queryParams);
      const response = await api.getSOCIncidents(queryParams);
      console.log('SOC Incidents API Response:', response);
      
      // Handle Django REST framework paginated response
      if (response?.results?.success && response?.results?.data) {
        // Paginated response format: { count, next, previous, results: { success, data: [...] } }
        setIncidents(response.results.data);
        setTotalPages(Math.ceil(response.count / 20));
        setError(null);
      } else if (response?.success && response?.data) {
        // Direct response format: { success, data: [...] }
        setIncidents(response.data);
        setTotalPages(1); // No pagination info available
        setError(null);
      } else if (response?.data && Array.isArray(response.data)) {
        // Simple array response
        setIncidents(response.data);
        setTotalPages(1);
        setError(null);
      } else {
        console.warn('Unexpected response structure:', response);
        setError('No incidents data received');
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

  const handleAssignIncident = (incident) => {
    setSelectedIncident(incident);
    setShowAssignModal(true);
  };

  const assignIncident = async (username) => {
    try {
      console.log('Assigning incident:', selectedIncident.id, 'to user:', username);
      const response = await api.assignSOCIncident(selectedIncident.id, username);
      console.log('Assignment response:', response);
      
      if (response?.success) {
        setShowAssignModal(false);
        setSelectedIncident(null);
        fetchIncidents(); // Refresh the list
        alert(`Incident assigned to ${username} successfully`);
      }
    } catch (err) {
      console.error('Assignment error:', err);
      alert('Failed to assign incident: ' + err.message);
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
        console.log('Creating incident with data:', formData);
        const response = await api.createSOCIncident(formData);
        console.log('Create incident response:', response);
        
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
        console.error('Create incident error:', err);
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

  const AssignIncidentModal = () => {
    const [selectedUser, setSelectedUser] = useState('');
    const [assigning, setAssigning] = useState(false);

    const handleAssign = async (e) => {
      e.preventDefault();
      if (!selectedUser) {
        alert('Please select a user to assign the incident to.');
        return;
      }
      
      try {
        setAssigning(true);
        await assignIncident(selectedUser);
      } finally {
        setAssigning(false);
      }
    };

    if (!showAssignModal || !selectedIncident) return null;

    console.log('Rendering assignment modal. Available users:', availableUsers);

    return (
      <div className="modal" style={{ display: 'block', backgroundColor: 'rgba(0,0,0,0.5)' }}>
        <div className="modal-dialog">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title">Assign Incident</h5>
              <button 
                type="button" 
                className="close" 
                onClick={() => setShowAssignModal(false)}
              >
                <span>&times;</span>
              </button>
            </div>
            <form onSubmit={handleAssign}>
              <div className="modal-body">
                <div className="mb-3">
                  <strong>Incident:</strong> {selectedIncident.incident_id} - {selectedIncident.title}
                </div>
                <div className="mb-3">
                  <strong>Current Assignment:</strong> {selectedIncident.assigned_to || 'Unassigned'}
                </div>
                <div className="form-group">
                  <label>Assign to User *</label>
                  <div className="d-flex">
                    <select
                      className="form-control"
                      value={selectedUser}
                      onChange={(e) => setSelectedUser(e.target.value)}
                      required
                    >
                      <option value="">Select a user...</option>
                      {(() => {
                        // Handle both array format and object format
                        let userList = [];
                        if (Array.isArray(availableUsers)) {
                          userList = availableUsers;
                        } else if (availableUsers?.users && Array.isArray(availableUsers.users)) {
                          userList = availableUsers.users;
                        }
                        
                        console.log('Dropdown rendering - userList:', userList);
                        console.log('Dropdown rendering - userList length:', userList.length);
                        
                        if (userList && userList.length > 0) {
                          return userList.map((user) => {
                            console.log('Rendering user option:', user);
                            return (
                              <option key={user.id || user.username} value={user.username}>
                                {user.first_name && user.last_name ? 
                                  `${user.first_name} ${user.last_name} (${user.username})` : 
                                  user.username}
                              </option>
                            );
                          });
                        } else {
                          return (
                            <option value="" disabled>
                              {availableUsers ? `Found structure: ${JSON.stringify(availableUsers).substring(0, 100)}...` : 'Loading users...'}
                            </option>
                          );
                        }
                      })()}
                    </select>
                    <button
                      type="button"
                      className="btn btn-outline-secondary ml-2"
                      onClick={fetchAvailableUsers}
                      title="Refresh user list"
                    >
                      <i className="fas fa-sync-alt"></i>
                    </button>
                  </div>
                  {(() => {
                    const hasUsers = Array.isArray(availableUsers) ? availableUsers.length > 0 : 
                                   availableUsers?.users ? availableUsers.users.length > 0 : false;
                    
                    if (!hasUsers) {
                      return (
                        <small className="text-muted mt-2 d-block">
                          No users loaded. Click the refresh button to try again or check console for errors.
                          <br />
                          <strong>Debug:</strong> availableUsers = {JSON.stringify(availableUsers)}
                        </small>
                      );
                    }
                    return null;
                  })()}
                </div>
              </div>
              
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={() => setShowAssignModal(false)}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={assigning}
                >
                  {assigning ? (
                    <>
                      <span className="spinner-border spinner-border-sm mr-2"></span>
                      Assigning...
                    </>
                  ) : (
                    'Assign Incident'
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
                        <span 
                          style={{ 
                            backgroundColor: '#6c757d', 
                            color: 'white',
                            padding: '4px 8px',
                            fontSize: '0.75rem',
                            fontWeight: 'bold',
                            textTransform: 'uppercase',
                            borderRadius: '2px',
                            display: 'inline-block'
                          }}
                        >
                          {incident.category_display}
                        </span>
                      </td>
                      <td>
                        <span 
                          style={{ 
                            backgroundColor: getPriorityColor(incident.priority), 
                            color: 'white',
                            padding: '4px 8px',
                            fontSize: '0.75rem',
                            fontWeight: 'bold',
                            textTransform: 'uppercase',
                            borderRadius: '2px',
                            display: 'inline-block'
                          }}
                        >
                          {incident.priority_display}
                        </span>
                      </td>
                      <td>
                        <span 
                          style={{ 
                            backgroundColor: getStatusColor(incident.status), 
                            color: 'white',
                            padding: '4px 8px',
                            fontSize: '0.75rem',
                            fontWeight: 'bold',
                            textTransform: 'uppercase',
                            borderRadius: '2px',
                            display: 'inline-block'
                          }}
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
                      <td>
                        <div style={{ display: 'flex', gap: '5px' }}>
                          <button 
                            className="btn btn-sm btn-outline-primary"
                            onClick={() => alert(`Incident Detail: ${incident.incident_id}`)}
                          >
                            View
                          </button>
                          <button 
                            className="btn btn-sm btn-outline-secondary"
                            onClick={() => handleAssignIncident(incident)}
                            title="Assign incident to user"
                          >
                            <i className="fas fa-user-plus"></i>
                          </button>
                        </div>
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
      <AssignIncidentModal />
    </div>
  );
};

export default IncidentsList;