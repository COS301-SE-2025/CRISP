import React, { useState, useEffect } from 'react';
import * as api from '../../api.js';

const IOCSelector = ({ selectedIOCs, onIOCsChange, maxSelections = 10 }) => {
  const [iocs, setIOCs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [confidenceFilter, setConfidenceFilter] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchIOCs();
  }, [searchTerm, typeFilter, confidenceFilter, currentPage]);

  const fetchIOCs = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        page: currentPage,
        page_size: 20,
        ...(searchTerm && { search: searchTerm }),
        ...(typeFilter && { type: typeFilter }),
        ...(confidenceFilter && { confidence_min: confidenceFilter })
      };

      const response = await api.getIndicators(params);
      if (response) {
        // Handle direct response format (not wrapped in success/data)
        setIOCs(response.results || response.data?.results || []);
        setTotalPages(Math.ceil((response.count || response.data?.count || 0) / 20));
      }
    } catch (err) {
      setError('Failed to fetch IOCs: ' + err.message);
      console.error('Error fetching IOCs:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleIOCToggle = (ioc) => {
    const isSelected = selectedIOCs.some(selected => selected.id === ioc.id);
    
    if (isSelected) {
      // Remove from selection
      onIOCsChange(selectedIOCs.filter(selected => selected.id !== ioc.id));
    } else {
      // Add to selection (check max limit)
      if (selectedIOCs.length < maxSelections) {
        onIOCsChange([...selectedIOCs, ioc]);
      }
    }
  };

  const clearSearch = () => {
    setSearchTerm('');
    setTypeFilter('');
    setConfidenceFilter('');
    setCurrentPage(1);
  };

  const getTypeColor = (type) => {
    const colors = {
      'ip': '#007bff',
      'domain': '#28a745',
      'url': '#ffc107',
      'file_hash': '#dc3545',
      'email': '#17a2b8',
      'mutex': '#6f42c1'
    };
    return colors[type] || '#6c757d';
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 80) return '#28a745';
    if (confidence >= 60) return '#ffc107';
    return '#dc3545';
  };

  return (
    <div style={{ marginBottom: '1rem' }}>
      <h4 style={{ marginBottom: '1rem', fontSize: '1.125rem', fontWeight: '600' }}>
        Select Related IOCs ({selectedIOCs.length}/{maxSelections})
      </h4>

      {/* Search and Filter Controls */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
        gap: '1rem', 
        marginBottom: '1rem',
        padding: '1rem',
        backgroundColor: '#f8f9fa',
        borderRadius: '6px'
      }}>
        <div>
          <label style={{ fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem', display: 'block' }}>
            Search IOCs
          </label>
          <input
            type="text"
            placeholder="Search by value..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              width: '100%',
              padding: '0.5rem',
              border: '1px solid #dee2e6',
              borderRadius: '4px',
              fontSize: '0.875rem'
            }}
          />
        </div>

        <div>
          <label style={{ fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem', display: 'block' }}>
            IOC Type
          </label>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            style={{
              width: '100%',
              padding: '0.5rem',
              border: '1px solid #dee2e6',
              borderRadius: '4px',
              fontSize: '0.875rem'
            }}
          >
            <option value="">All Types</option>
            <option value="ip">IP Address</option>
            <option value="domain">Domain</option>
            <option value="url">URL</option>
            <option value="file_hash">File Hash</option>
            <option value="email">Email</option>
            <option value="mutex">Mutex</option>
          </select>
        </div>

        <div>
          <label style={{ fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.5rem', display: 'block' }}>
            Min Confidence
          </label>
          <select
            value={confidenceFilter}
            onChange={(e) => setConfidenceFilter(e.target.value)}
            style={{
              width: '100%',
              padding: '0.5rem',
              border: '1px solid #dee2e6',
              borderRadius: '4px',
              fontSize: '0.875rem'
            }}
          >
            <option value="">Any Confidence</option>
            <option value="90">90%+ (High)</option>
            <option value="70">70%+ (Medium)</option>
            <option value="50">50%+ (Low)</option>
          </select>
        </div>

        <div style={{ display: 'flex', alignItems: 'end' }}>
          <button
            onClick={clearSearch}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#6c757d',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              fontSize: '0.875rem',
              cursor: 'pointer'
            }}
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Selected IOCs Display */}
      {selectedIOCs.length > 0 && (
        <div style={{ marginBottom: '1rem' }}>
          <h5 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '0.5rem' }}>Selected IOCs:</h5>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {selectedIOCs.map((ioc) => (
              <span
                key={ioc.id}
                style={{
                  backgroundColor: getTypeColor(ioc.type),
                  color: 'white',
                  padding: '0.25rem 0.75rem',
                  borderRadius: '12px',
                  fontSize: '0.75rem',
                  fontWeight: '600',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem'
                }}
              >
                {ioc.type.toUpperCase()}: {ioc.value.length > 20 ? ioc.value.substring(0, 20) + '...' : ioc.value}
                <button
                  onClick={() => handleIOCToggle(ioc)}
                  style={{
                    backgroundColor: 'transparent',
                    border: 'none',
                    color: 'white',
                    cursor: 'pointer',
                    fontSize: '0.75rem',
                    padding: '0'
                  }}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div style={{ 
          backgroundColor: '#f8d7da', 
          color: '#721c24', 
          padding: '0.75rem', 
          borderRadius: '4px', 
          marginBottom: '1rem' 
        }}>
          {error}
        </div>
      )}

      {/* IOCs List */}
      <div style={{ 
        maxHeight: '400px', 
        overflowY: 'auto', 
        border: '1px solid #dee2e6', 
        borderRadius: '6px' 
      }}>
        {loading ? (
          <div style={{ padding: '2rem', textAlign: 'center' }}>
            <div style={{ color: '#666' }}>Loading IOCs...</div>
          </div>
        ) : iocs.length === 0 ? (
          <div style={{ padding: '2rem', textAlign: 'center', color: '#666' }}>
            No IOCs found matching your criteria
          </div>
        ) : (
          <div>
            {iocs.map((ioc) => {
              const isSelected = selectedIOCs.some(selected => selected.id === ioc.id);
              const canSelect = selectedIOCs.length < maxSelections || isSelected;
              
              return (
                <div
                  key={ioc.id}
                  onClick={() => canSelect && handleIOCToggle(ioc)}
                  style={{
                    padding: '1rem',
                    borderBottom: '1px solid #e9ecef',
                    cursor: canSelect ? 'pointer' : 'not-allowed',
                    backgroundColor: isSelected ? '#e3f2fd' : 'white',
                    opacity: canSelect ? 1 : 0.5,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}
                  onMouseEnter={(e) => {
                    if (canSelect && !isSelected) {
                      e.target.style.backgroundColor = '#f8f9fa';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (canSelect && !isSelected) {
                      e.target.style.backgroundColor = 'white';
                    }
                  }}
                >
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                      <span style={{
                        backgroundColor: getTypeColor(ioc.type),
                        color: 'white',
                        padding: '0.125rem 0.5rem',
                        borderRadius: '8px',
                        fontSize: '0.7rem',
                        fontWeight: '600'
                      }}>
                        {ioc.type.toUpperCase()}
                      </span>
                      <span style={{
                        backgroundColor: getConfidenceColor(ioc.confidence),
                        color: 'white',
                        padding: '0.125rem 0.5rem',
                        borderRadius: '8px',
                        fontSize: '0.7rem',
                        fontWeight: '600'
                      }}>
                        {ioc.confidence}%
                      </span>
                    </div>
                    <div style={{ fontSize: '0.875rem', fontWeight: '500', marginBottom: '0.25rem' }}>
                      {ioc.value}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#666' }}>
                      Source: {ioc.source || 'Manual Entry'}
                      {ioc.stix_id && ` • STIX ID: ${ioc.stix_id}`}
                    </div>
                  </div>
                  <div style={{ marginLeft: '1rem' }}>
                    {isSelected ? (
                      <span style={{ color: '#007bff', fontWeight: '600' }}>✓ Selected</span>
                    ) : canSelect ? (
                      <span style={{ color: '#28a745' }}>Click to select</span>
                    ) : (
                      <span style={{ color: '#dc3545' }}>Limit reached</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          gap: '0.5rem', 
          marginTop: '1rem' 
        }}>
          <button
            onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
            disabled={currentPage === 1}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: currentPage === 1 ? '#f8f9fa' : '#007bff',
              color: currentPage === 1 ? '#6c757d' : 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: currentPage === 1 ? 'not-allowed' : 'pointer'
            }}
          >
            Previous
          </button>
          <span style={{ fontSize: '0.875rem' }}>
            Page {currentPage} of {totalPages}
          </span>
          <button
            onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
            disabled={currentPage === totalPages}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: currentPage === totalPages ? '#f8f9fa' : '#007bff',
              color: currentPage === totalPages ? '#6c757d' : 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: currentPage === totalPages ? 'not-allowed' : 'pointer'
            }}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default IOCSelector;