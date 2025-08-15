import React, { useState, useEffect } from 'react';

const TrustManagement = () => {
  const [trustRelationships, setTrustRelationships] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('relationships');

  useEffect(() => {
    fetchTrustData();
  }, []);

  const fetchTrustData = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/trust/bilateral/');
      if (response.ok) {
        const data = await response.json();
        setTrustRelationships(data.relationships || []);
      } else {
        throw new Error('Failed to fetch trust relationships');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="trust-management">
        <div className="loading-state">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading trust relationships...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="trust-management">
        <div className="error-state">
          <i className="fas fa-exclamation-triangle"></i>
          <p>Error loading trust data: {error}</p>
          <button onClick={fetchTrustData} className="btn btn-primary">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="trust-management">
      <div className="header">
        <h2>Trust Management</h2>
        <button className="btn btn-primary">
          <i className="fas fa-handshake"></i>
          Create Trust Relationship
        </button>
      </div>

      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'relationships' ? 'active' : ''}`}
          onClick={() => setActiveTab('relationships')}
        >
          <i className="fas fa-link"></i>
          Relationships
        </button>
        <button 
          className={`tab ${activeTab === 'groups' ? 'active' : ''}`}
          onClick={() => setActiveTab('groups')}
        >
          <i className="fas fa-users"></i>
          Trust Groups
        </button>
        <button 
          className={`tab ${activeTab === 'levels' ? 'active' : ''}`}
          onClick={() => setActiveTab('levels')}
        >
          <i className="fas fa-shield-alt"></i>
          Trust Levels
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'relationships' && (
          <div className="relationships-tab">
            <div className="trust-table">
              <table>
                <thead>
                  <tr>
                    <th>Organization</th>
                    <th>Trust Level</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Established</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {trustRelationships.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="no-data">
                        No trust relationships found. Create your first relationship to get started.
                      </td>
                    </tr>
                  ) : (
                    trustRelationships.map(relationship => (
                      <tr key={relationship.id}>
                        <td>
                          <div className="org-info">
                            <i className="fas fa-building"></i>
                            {relationship.organization?.name || 'Unknown'}
                          </div>
                        </td>
                        <td>
                          <span className={`trust-level ${relationship.trust_level?.toLowerCase()}`}>
                            {relationship.trust_level}
                          </span>
                        </td>
                        <td>
                          <span className="relationship-type">
                            {relationship.relationship_type}
                          </span>
                        </td>
                        <td>
                          <span className={`status-badge ${relationship.status?.toLowerCase()}`}>
                            {relationship.status}
                          </span>
                        </td>
                        <td>
                          {relationship.established_at ? 
                            new Date(relationship.established_at).toLocaleDateString() : 
                            'Pending'
                          }
                        </td>
                        <td>
                          <div className="actions">
                            <button className="btn btn-sm btn-outline">
                              <i className="fas fa-edit"></i>
                            </button>
                            <button className="btn btn-sm btn-outline">
                              <i className="fas fa-cog"></i>
                            </button>
                            <button className="btn btn-sm btn-danger">
                              <i className="fas fa-unlink"></i>
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

        {activeTab === 'groups' && (
          <div className="groups-tab">
            <div className="placeholder-content">
              <i className="fas fa-users" style={{fontSize: '48px', color: '#dee2e6'}}></i>
              <h3>Trust Groups</h3>
              <p>Community-based trust groups management will be available here.</p>
              <button className="btn btn-primary">
                Create Trust Group
              </button>
            </div>
          </div>
        )}

        {activeTab === 'levels' && (
          <div className="levels-tab">
            <div className="placeholder-content">
              <i className="fas fa-shield-alt" style={{fontSize: '48px', color: '#dee2e6'}}></i>
              <h3>Trust Levels</h3>
              <p>Configure trust levels and their associated permissions.</p>
              <button className="btn btn-primary">
                Configure Levels
              </button>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .trust-management {
          padding: 20px;
          max-width: 1200px;
          margin: 0 auto;
        }

        .header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .header h2 {
          margin: 0;
          color: #333;
        }

        .tabs {
          display: flex;
          border-bottom: 2px solid #dee2e6;
          margin-bottom: 20px;
        }

        .tab {
          background: none;
          border: none;
          padding: 12px 24px;
          cursor: pointer;
          color: #6c757d;
          font-size: 14px;
          font-weight: 500;
          display: flex;
          align-items: center;
          gap: 8px;
          border-bottom: 3px solid transparent;
          transition: all 0.2s;
        }

        .tab:hover {
          color: #495057;
          background: #f8f9fa;
        }

        .tab.active {
          color: #0056b3;
          border-bottom-color: #0056b3;
        }

        .btn {
          padding: 8px 16px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          display: inline-flex;
          align-items: center;
          gap: 8px;
          transition: background-color 0.2s;
        }

        .btn-primary {
          background: #0056b3;
          color: white;
        }

        .btn-primary:hover {
          background: #004494;
        }

        .btn-outline {
          background: transparent;
          border: 1px solid #dee2e6;
          color: #495057;
        }

        .btn-sm {
          padding: 4px 8px;
          font-size: 12px;
        }

        .btn-danger {
          background: #dc3545;
          color: white;
        }

        .trust-table table {
          width: 100%;
          border-collapse: collapse;
          background: white;
          border-radius: 8px;
          overflow: hidden;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .trust-table th,
        .trust-table td {
          padding: 12px;
          text-align: left;
          border-bottom: 1px solid #dee2e6;
        }

        .trust-table th {
          background: #f8f9fa;
          font-weight: 600;
          color: #495057;
        }

        .org-info {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .org-info i {
          color: #6c757d;
        }

        .trust-level {
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 500;
        }

        .trust-level.high {
          background: #e8f5e8;
          color: #2e7d32;
        }

        .trust-level.standard {
          background: #e3f2fd;
          color: #1976d2;
        }

        .trust-level.minimal {
          background: #fff3e0;
          color: #f57c00;
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

        .status-badge.pending {
          background: #fff3e0;
          color: #f57c00;
        }

        .relationship-type {
          color: #6c757d;
          font-size: 12px;
          text-transform: capitalize;
        }

        .actions {
          display: flex;
          gap: 8px;
        }

        .no-data {
          text-align: center;
          color: #6c757d;
          font-style: italic;
          padding: 40px;
        }

        .placeholder-content {
          text-align: center;
          padding: 60px 20px;
          color: #6c757d;
        }

        .placeholder-content h3 {
          margin: 20px 0 10px 0;
          color: #495057;
        }

        .placeholder-content p {
          margin-bottom: 20px;
        }

        .loading-state,
        .error-state {
          text-align: center;
          padding: 40px;
        }

        .loading-state i {
          font-size: 24px;
          color: #0056b3;
          margin-bottom: 10px;
        }

        .error-state i {
          font-size: 24px;
          color: #dc3545;
          margin-bottom: 10px;
        }
      `}</style>
    </div>
  );
};

export default TrustManagement;