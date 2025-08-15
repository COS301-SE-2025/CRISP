import React, { useState, useEffect } from 'react';

const Institutions = () => {
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedOrg, setSelectedOrg] = useState(null);

  useEffect(() => {
    fetchOrganizations();
  }, []);

  const fetchOrganizations = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/organizations/');
      if (response.ok) {
        const data = await response.json();
        setOrganizations(data.organizations || []);
      } else {
        throw new Error('Failed to fetch organizations');
      }
    } catch (err) {
      setError(err.message);
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

  if (loading) {
    return (
      <div className="institutions">
        <div className="loading-state">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading institutions...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="institutions">
        <div className="error-state">
          <i className="fas fa-exclamation-triangle"></i>
          <p>Error loading institutions: {error}</p>
          <button onClick={fetchOrganizations} className="btn btn-primary">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="institutions">
      <div className="header">
        <h2>Institutions & Organizations</h2>
        <button 
          className="btn btn-primary"
          onClick={() => setShowCreateModal(true)}
        >
          <i className="fas fa-plus"></i>
          Add Institution
        </button>
      </div>

      <div className="stats-row">
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-building"></i>
          </div>
          <div className="stat-content">
            <h3>{organizations.length}</h3>
            <p>Total Organizations</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-users"></i>
          </div>
          <div className="stat-content">
            <h3>{organizations.reduce((sum, org) => sum + (org.member_count || 0), 0)}</h3>
            <p>Total Members</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-handshake"></i>
          </div>
          <div className="stat-content">
            <h3>{organizations.filter(org => org.trust_relationships_count > 0).length}</h3>
            <p>Connected Orgs</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">
            <i className="fas fa-shield-alt"></i>
          </div>
          <div className="stat-content">
            <h3>{organizations.filter(org => org.is_active).length}</h3>
            <p>Active Orgs</p>
          </div>
        </div>
      </div>

      <div className="organizations-grid">
        {organizations.length === 0 ? (
          <div className="empty-state">
            <i className="fas fa-building-o"></i>
            <h3>No institutions found</h3>
            <p>Create your first institution to get started with threat intelligence sharing.</p>
            <button 
              className="btn btn-primary"
              onClick={() => setShowCreateModal(true)}
            >
              <i className="fas fa-plus"></i>
              Create Institution
            </button>
          </div>
        ) : (
          organizations.map(org => (
            <div key={org.id} className="organization-card">
              <div className="org-header">
                <div className="org-icon">
                  <i 
                    className={getOrganizationTypeIcon(org.type)}
                    style={{ color: getOrganizationTypeColor(org.type) }}
                  ></i>
                </div>
                <div className="org-status">
                  <span className={`status-badge ${org.is_active ? 'active' : 'inactive'}`}>
                    {org.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>
              
              <div className="org-content">
                <h3>{org.name}</h3>
                <p className="org-description">{org.description || 'No description provided'}</p>
                
                <div className="org-details">
                  <div className="detail-item">
                    <i className="fas fa-tag"></i>
                    <span>{org.type || 'Unknown'}</span>
                  </div>
                  <div className="detail-item">
                    <i className="fas fa-users"></i>
                    <span>{org.member_count || 0} members</span>
                  </div>
                  <div className="detail-item">
                    <i className="fas fa-handshake"></i>
                    <span>{org.trust_relationships_count || 0} relationships</span>
                  </div>
                </div>
                
                <div className="org-metadata">
                  <small>Created {new Date(org.created_at).toLocaleDateString()}</small>
                </div>
              </div>
              
              <div className="org-actions">
                <button 
                  className="btn btn-sm btn-outline"
                  onClick={() => setSelectedOrg(org)}
                >
                  <i className="fas fa-eye"></i>
                  View Details
                </button>
                <button className="btn btn-sm btn-outline">
                  <i className="fas fa-edit"></i>
                  Edit
                </button>
                <button className="btn btn-sm btn-outline">
                  <i className="fas fa-handshake"></i>
                  Trust
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {showCreateModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>Create New Institution</h3>
              <button 
                className="close-btn"
                onClick={() => setShowCreateModal(false)}
              >
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              <p>Institution creation form will be implemented here.</p>
              <p>This requires backend integration for organization management.</p>
            </div>
            <div className="modal-footer">
              <button 
                className="btn btn-secondary"
                onClick={() => setShowCreateModal(false)}
              >
                Cancel
              </button>
            </div>
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
        .institutions {
          padding: 20px;
          max-width: 1400px;
          margin: 0 auto;
        }

        .header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 30px;
        }

        .header h2 {
          margin: 0;
          color: #333;
        }

        .stats-row {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 20px;
          margin-bottom: 30px;
        }

        .stat-card {
          background: white;
          border-radius: 8px;
          padding: 20px;
          display: flex;
          align-items: center;
          gap: 15px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .stat-icon {
          width: 50px;
          height: 50px;
          background: #f8f9fa;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 20px;
          color: #0056b3;
        }

        .stat-content h3 {
          margin: 0 0 5px 0;
          font-size: 24px;
          font-weight: 700;
          color: #333;
        }

        .stat-content p {
          margin: 0;
          color: #6c757d;
          font-size: 14px;
        }

        .organizations-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
          gap: 20px;
        }

        .organization-card {
          background: white;
          border-radius: 12px;
          padding: 20px;
          box-shadow: 0 4px 6px rgba(0,0,0,0.1);
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .organization-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 15px rgba(0,0,0,0.15);
        }

        .org-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 15px;
        }

        .org-icon {
          width: 50px;
          height: 50px;
          background: #f8f9fa;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 20px;
        }

        .org-content h3 {
          margin: 0 0 10px 0;
          color: #333;
          font-size: 18px;
        }

        .org-description {
          color: #6c757d;
          margin-bottom: 15px;
          line-height: 1.4;
          font-size: 14px;
        }

        .org-details {
          display: flex;
          flex-direction: column;
          gap: 8px;
          margin-bottom: 15px;
        }

        .detail-item {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 14px;
          color: #495057;
        }

        .detail-item i {
          width: 16px;
          color: #6c757d;
        }

        .org-metadata {
          color: #6c757d;
          font-size: 12px;
          margin-bottom: 15px;
          padding-top: 10px;
          border-top: 1px solid #dee2e6;
        }

        .org-actions {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
        }

        .status-badge {
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 500;
        }

        .status-badge.active {
          background: #e8f5e8;
          color: #2e7d32;
        }

        .status-badge.inactive {
          background: #fff3e0;
          color: #f57c00;
        }

        .btn {
          padding: 8px 16px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          display: inline-flex;
          align-items: center;
          gap: 6px;
          transition: background-color 0.2s;
          text-decoration: none;
        }

        .btn-primary {
          background: #0056b3;
          color: white;
        }

        .btn-primary:hover {
          background: #004494;
        }

        .btn-secondary {
          background: #6c757d;
          color: white;
        }

        .btn-outline {
          background: transparent;
          border: 1px solid #dee2e6;
          color: #495057;
        }

        .btn-outline:hover {
          background: #f8f9fa;
        }

        .btn-sm {
          padding: 6px 12px;
          font-size: 12px;
        }

        .empty-state {
          grid-column: 1 / -1;
          text-align: center;
          padding: 60px 20px;
          color: #6c757d;
        }

        .empty-state i {
          font-size: 64px;
          margin-bottom: 20px;
          opacity: 0.3;
        }

        .empty-state h3 {
          margin: 0 0 10px 0;
          color: #495057;
        }

        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0,0,0,0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }

        .modal {
          background: white;
          border-radius: 8px;
          width: 90%;
          max-width: 500px;
          max-height: 80vh;
          overflow-y: auto;
          box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        .modal.large {
          max-width: 800px;
        }

        .modal-header {
          padding: 20px;
          border-bottom: 1px solid #dee2e6;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .modal-header h3 {
          margin: 0;
          color: #333;
        }

        .close-btn {
          background: none;
          border: none;
          font-size: 18px;
          color: #6c757d;
          cursor: pointer;
        }

        .modal-body {
          padding: 20px;
        }

        .modal-footer {
          padding: 20px;
          border-top: 1px solid #dee2e6;
          display: flex;
          justify-content: flex-end;
          gap: 10px;
        }

        .org-detail-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 30px;
        }

        .detail-section h4 {
          margin: 0 0 15px 0;
          color: #333;
          font-size: 16px;
        }

        .detail-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 8px 0;
          border-bottom: 1px solid #f8f9fa;
        }

        .detail-row label {
          font-weight: 600;
          color: #495057;
        }

        .loading-state,
        .error-state {
          text-align: center;
          padding: 60px 20px;
        }

        .loading-state i {
          font-size: 32px;
          color: #0056b3;
          margin-bottom: 15px;
        }

        .error-state i {
          font-size: 32px;
          color: #dc3545;
          margin-bottom: 15px;
        }
      `}</style>
    </div>
  );
};

export default Institutions;