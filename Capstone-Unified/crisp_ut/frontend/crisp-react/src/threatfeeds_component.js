function ThreatFeeds({ active, navigationState, setNavigationState }) {
  const [threatFeeds, setThreatFeeds] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [activeTab, setActiveTab] = useState('all');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    type: '',
    status: '',
    source: '',
    search: ''
  });
  const itemsPerPage = 10;
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    is_external: true,
    taxii_server_url: '',
    taxii_api_root: '',
    taxii_collection_id: '',
    taxii_username: '',
    taxii_password: ''
  });

  // Feed consumption and deletion states
  const [consumingFeeds, setConsumingFeeds] = useState(new Set());
  const [feedProgress, setFeedProgress] = useState(new Map());
  const [showDeleteFeedModal, setShowDeleteFeedModal] = useState(false);
  const [feedToDelete, setFeedToDelete] = useState(null);
  const [deletingFeed, setDeletingFeed] = useState(false);
  
  // Fetch threat feeds from backend
  useEffect(() => {
    if (active) {
      fetchThreatFeeds();
    }
  }, [active]);

  // Handle navigation state for modal triggers
  useEffect(() => {
    if (active && navigationState?.triggerModal === 'addFeed') {
      setShowAddModal(true);
      // Clear navigation state after handling
      setNavigationState({
        triggerModal: null,
        modalParams: {}
      });
    }
  }, [active, navigationState, setNavigationState]);
  
  const fetchThreatFeeds = async () => {
    setLoading(true);
    const data = await api.get('/api/threat-feeds/');
    if (data && data.results) {
      setThreatFeeds(data.results);
    }
    setLoading(false);
  };
  
  const handleConsumeFeed = async (feedId) => {
    // Add feed to consuming set
    setConsumingFeeds(prev => new Set([...prev, feedId]));
    
    // Initialize progress
    setFeedProgress(prev => new Map(prev.set(feedId, {
      stage: 'Initiating',
      message: 'Starting consumption process...',
      percentage: 0
    })));
    
    try {
      const result = await api.post(`/api/threat-feeds/${feedId}/consume/`);
      if (result) {
        console.log('Feed consumption started:', result);
        
        // Start polling for progress
        const progressInterval = setInterval(async () => {
          try {
            const progressData = await api.get(`/api/threat-feeds/${feedId}/consumption_progress/`);
            if (progressData && progressData.success) {
              const progress = progressData.progress;
              
              setFeedProgress(prev => new Map(prev.set(feedId, {
                stage: progress.stage,
                message: progress.message || `${progress.stage}...`,
                percentage: progress.percentage || 0,
                current: progress.current,
                total: progress.total
              })));
              
              // If completed, stop polling
              if (progress.stage === 'Completed' || progress.percentage >= 100) {
                clearInterval(progressInterval);
                
                // Remove from consuming set after a brief delay to show completion
                setTimeout(() => {
                  setConsumingFeeds(prev => {
                    const newSet = new Set(prev);
                    newSet.delete(feedId);
                    return newSet;
                  });
                  setFeedProgress(prev => {
                    const newMap = new Map(prev);
                    newMap.delete(feedId);
                    return newMap;
                  });
                }, 2000);
                
                // Refresh feeds after consumption
                await fetchThreatFeeds();
              }
            }
          } catch (progressError) {
            console.error('Error fetching progress:', progressError);
            // Continue polling - might be temporary error
          }
        }, 2000); // Poll every 2 seconds
        
        // Set a maximum timeout to prevent infinite polling
        setTimeout(() => {
          clearInterval(progressInterval);
          setConsumingFeeds(prev => {
            const newSet = new Set(prev);
            newSet.delete(feedId);
            return newSet;
          });
          setFeedProgress(prev => {
            const newMap = new Map(prev);
            newMap.delete(feedId);
            return newMap;
          });
        }, 300000); // 5 minutes maximum
        
      }
    } catch (error) {
      console.error('Error consuming feed:', error);
      alert('Failed to consume feed. Please try again.');
      
      // Remove feed from consuming set on error
      setConsumingFeeds(prev => {
        const newSet = new Set(prev);
        newSet.delete(feedId);
        return newSet;
      });
      setFeedProgress(prev => {
        const newMap = new Map(prev);
        newMap.delete(feedId);
        return newMap;
      });
    }
  };

  const handleDeleteFeed = (feed) => {
    setFeedToDelete(feed);
    setShowDeleteFeedModal(true);
  };

  const confirmDeleteFeed = async () => {
    if (!feedToDelete) return;

    setDeletingFeed(true);
    try {
      const result = await api.delete(`/api/threat-feeds/${feedToDelete.id}/`);
      if (result !== null) {
        console.log('Feed deleted successfully:', feedToDelete.name);
        // Refresh feeds list
        await fetchThreatFeeds();
        // Close modal
        closeDeleteFeedModal();
      } else {
        alert('Failed to delete threat feed. Please try again.');
      }
    } catch (error) {
      console.error('Error deleting feed:', error);
      alert('Error deleting threat feed. Please try again.');
    } finally {
      setDeletingFeed(false);
    }
  };

  const closeDeleteFeedModal = () => {
    setShowDeleteFeedModal(false);
    setFeedToDelete(null);
  };

  const handleAddFeed = () => {
    setShowAddModal(true);
  };

  const handleFormChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    const result = await api.post('/api/threat-feeds/', formData);
    if (result) {
      setShowAddModal(false);
      setFormData({
        name: '',
        description: '',
        is_external: true,
        taxii_server_url: '',
        taxii_api_root: '',
        taxii_collection_id: '',
        taxii_username: '',
        taxii_password: ''
      });
      fetchThreatFeeds();
    }
  };

  const closeModal = () => {
    setShowAddModal(false);
  };

  // Filter and paginate feeds
  const getFilteredFeeds = () => {
    let filtered = threatFeeds;

    // Apply tab filter
    if (activeTab === 'active') {
      filtered = filtered.filter(f => f.is_active);
    } else if (activeTab === 'external') {
      filtered = filtered.filter(f => f.is_external);
    } else if (activeTab === 'internal') {
      filtered = filtered.filter(f => !f.is_external);
    }

    // Apply dropdown filters
    if (filters.type) {
      filtered = filtered.filter(f => 
        (filters.type === 'stix-taxii' && f.taxii_server_url) ||
        (filters.type === 'internal' && !f.is_external) ||
        (filters.type === 'external' && f.is_external)
      );
    }

    if (filters.status) {
      filtered = filtered.filter(f => 
        (filters.status === 'active' && f.is_active) ||
        (filters.status === 'disabled' && !f.is_active)
      );
    }

    if (filters.source) {
      filtered = filtered.filter(f => 
        (filters.source === 'external' && f.is_external) ||
        (filters.source === 'internal' && !f.is_external)
      );
    }

    if (filters.search) {
      filtered = filtered.filter(f => 
        f.name.toLowerCase().includes(filters.search.toLowerCase()) ||
        (f.description && f.description.toLowerCase().includes(filters.search.toLowerCase())) ||
        (f.taxii_server_url && f.taxii_server_url.toLowerCase().includes(filters.search.toLowerCase()))
      );
    }

    return filtered;
  };

  const getPaginatedFeeds = () => {
    const filtered = getFilteredFeeds();
    const startIndex = (currentPage - 1) * itemsPerPage;
    return filtered.slice(startIndex, startIndex + itemsPerPage);
  };

  const getTotalPages = () => {
    return Math.ceil(getFilteredFeeds().length / itemsPerPage);
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    setCurrentPage(1);
  };

  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }));
    setCurrentPage(1);
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  const toggleFilters = () => {
    setShowFilters(!showFilters);
  };
  
  return (
    <section id="threat-feeds" className={`page-section ${active ? 'active' : ''}`}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Threat Feeds</h1>
          <p className="page-subtitle">Manage and monitor all threat intelligence feeds</p>
        </div>
        <div className="action-buttons">
          <button className="btn btn-outline" onClick={toggleFilters}>
            <i className="fas fa-filter"></i> Filter Feeds {showFilters ? '▲' : '▼'}
          </button>
          <button className="btn btn-primary" onClick={handleAddFeed}><i className="fas fa-plus"></i> Add New Feed</button>
        </div>
      </div>

      {showFilters && (
        <div className="filters-section">
          <div className="filters-grid">
          <div className="filter-group">
            <label className="filter-label">Feed Type</label>
            <div className="filter-control">
              <select value={filters.type} onChange={(e) => handleFilterChange('type', e.target.value)}>
                <option value="">All Types</option>
                <option value="stix-taxii">STIX/TAXII</option>
                <option value="misp">MISP</option>
                <option value="custom">Custom</option>
                <option value="internal">Internal</option>
              </select>
            </div>
          </div>
          <div className="filter-group">
            <label className="filter-label">Status</label>
            <div className="filter-control">
              <select value={filters.status} onChange={(e) => handleFilterChange('status', e.target.value)}>
                <option value="">All Statuses</option>
                <option value="active">Active</option>
                <option value="disabled">Disabled</option>
                <option value="error">Error</option>
              </select>
            </div>
          </div>
          <div className="filter-group">
            <label className="filter-label">Source</label>
            <div className="filter-control">
              <select value={filters.source} onChange={(e) => handleFilterChange('source', e.target.value)}>
                <option value="">All Sources</option>
                <option value="external">External</option>
                <option value="internal">Internal</option>
                <option value="partner">Partner</option>
              </select>
            </div>
          </div>
          <div className="filter-group">
            <label className="filter-label">Search Feeds</label>
            <div className="filter-control">
              <input 
                type="text" 
                placeholder="Search by name or URL..." 
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
              />
            </div>
          </div>
          </div>
        </div>
      )}

      <div className="tabs">
        <div 
          className={`tab ${activeTab === 'active' ? 'active' : ''}`}
          onClick={() => handleTabChange('active')}
        >
          Active Feeds ({threatFeeds.filter(f => f.is_active).length})
        </div>
        <div 
          className={`tab ${activeTab === 'external' ? 'active' : ''}`}
          onClick={() => handleTabChange('external')}
        >
          External ({threatFeeds.filter(f => f.is_external).length})
        </div>
        <div 
          className={`tab ${activeTab === 'internal' ? 'active' : ''}`}
          onClick={() => handleTabChange('internal')}
        >
          Internal ({threatFeeds.filter(f => !f.is_external).length})
        </div>
        <div 
          className={`tab ${activeTab === 'all' ? 'active' : ''}`}
          onClick={() => handleTabChange('all')}
        >
          All Feeds ({threatFeeds.length})
        </div>
      </div>

      <div className="card">
        <div className="card-content">
          {loading ? (
            <div style={{textAlign: 'center', padding: '2rem'}}>
              <i className="fas fa-spinner fa-spin"></i> Loading feeds...
            </div>
          ) : (
            <ul className="feed-items">
              {getPaginatedFeeds().map((feed) => (
                <li key={feed.id} className="feed-item">
                  <div className="feed-icon">
                    <i className={feed.is_external ? "fas fa-globe" : "fas fa-server"}></i>
                  </div>
                  <div className="feed-details">
                    <div className="feed-name">{feed.name}</div>
                    <div className="feed-description">{feed.description || 'No description available'}</div>
                    <div className="feed-meta">
                      <div className="feed-stats">
                        <div className="stat-item">
                          <i className="fas fa-link"></i> {feed.taxii_collection_id || 'N/A'}
                        </div>
                        <div className="stat-item">
                          <i className="fas fa-sync-alt"></i> {feed.last_sync ? new Date(feed.last_sync).toLocaleString() : 'Never'}
                        </div>
                        <div className="stat-item">
                          <i className="fas fa-globe"></i> {feed.is_external ? 'External' : 'Internal'}
                        </div>
                      </div>
                      <div className="feed-badges">
                        <span className={`badge ${feed.is_public ? 'badge-active' : 'badge-medium'}`}>
                          {feed.is_public ? 'Public' : 'Private'}
                        </span>
                        <span className="badge badge-connected">STIX/TAXII</span>
                        <button 
                          className="btn btn-sm btn-primary"
                          onClick={() => handleConsumeFeed(feed.id)}
                          disabled={consumingFeeds.has(feed.id)}
                          style={{minWidth: '140px'}}
                        >
                          {consumingFeeds.has(feed.id) ? (
                            <>
                              <i className="fas fa-spinner fa-spin"></i>
                              <div style={{display: 'flex', flexDirection: 'column', alignItems: 'flex-start', fontSize: '11px'}}>
                                <span>{feedProgress.get(feed.id)?.stage || 'Processing'}</span>
                                {feedProgress.get(feed.id)?.current && feedProgress.get(feed.id)?.total && (
                                  <span style={{opacity: 0.8}}>
                                    {feedProgress.get(feed.id).current}/{feedProgress.get(feed.id).total}
                                  </span>
                                )}
                                {feedProgress.get(feed.id)?.percentage > 0 && (
                                  <span style={{opacity: 0.8}}>
                                    {feedProgress.get(feed.id).percentage}%
                                  </span>
                                )}
                              </div>
                            </>
                          ) : (
                            <>
                              <i className="fas fa-download"></i> Consume
                            </>
                          )}
                        </button>
                        <button 
                          className="btn btn-sm btn-danger"
                          onClick={() => handleDeleteFeed(feed)}
                          disabled={consumingFeeds.has(feed.id)}
                          title={consumingFeeds.has(feed.id) ? "Cannot delete while consuming" : "Delete this threat feed"}
                        >
                          <i className="fas fa-trash"></i>
                        </button>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {getTotalPages() > 1 && (
        <div className="pagination">
          <div 
            className={`page-item ${currentPage === 1 ? 'disabled' : ''}`}
            onClick={() => currentPage > 1 && handlePageChange(currentPage - 1)}
          >
            <i className="fas fa-chevron-left"></i>
          </div>
          {Array.from({ length: getTotalPages() }, (_, i) => i + 1).map(page => (
            <div 
              key={page}
              className={`page-item ${page === currentPage ? 'active' : ''}`}
              onClick={() => handlePageChange(page)}
            >
              {page}
            </div>
          ))}
          <div 
            className={`page-item ${currentPage === getTotalPages() ? 'disabled' : ''}`}
            onClick={() => currentPage < getTotalPages() && handlePageChange(currentPage + 1)}
          >
            <i className="fas fa-chevron-right"></i>
          </div>
        </div>
      )}

      {/* Add New Feed Modal */}
      {showAddModal && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Add New Threat Feed</h2>
              <button className="modal-close" onClick={closeModal}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <form onSubmit={handleFormSubmit} className="modal-body">
              <div className="form-group">
                <label>Feed Name *</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleFormChange}
                  placeholder="Enter feed name"
                  required
                />
              </div>
              
              <div className="form-group">
                <label>Description</label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleFormChange}
                  placeholder="Enter feed description"
                  rows="3"
                />
              </div>
              
              <div className="form-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    name="is_external"
                    checked={formData.is_external}
                    onChange={handleFormChange}
                  />
                  External Feed
                </label>
              </div>
              
              <div className="form-group">
                <label>TAXII Server URL *</label>
                <input
                  type="url"
                  name="taxii_server_url"
                  value={formData.taxii_server_url}
                  onChange={handleFormChange}
                  placeholder="https://example.com/taxii"
                  required
                />
              </div>
              
              <div className="form-group">
                <label>API Root</label>
                <input
                  type="text"
                  name="taxii_api_root"
                  value={formData.taxii_api_root}
                  onChange={handleFormChange}
                  placeholder="api-root"
                />
              </div>
              
              <div className="form-group">
                <label>Collection ID</label>
                <input
                  type="text"
                  name="taxii_collection_id"
                  value={formData.taxii_collection_id}
                  onChange={handleFormChange}
                  placeholder="collection-id"
                />
              </div>
              
              <div className="form-row">
                <div className="form-group">
                  <label>Username</label>
                  <input
                    type="text"
                    name="taxii_username"
                    value={formData.taxii_username}
                    onChange={handleFormChange}
                    placeholder="Username"
                  />
                </div>
                
                <div className="form-group">
                  <label>Password</label>
                  <input
                    type="password"
                    name="taxii_password"
                    value={formData.taxii_password}
                    onChange={handleFormChange}
                    placeholder="Password"
                  />
                </div>
              </div>
              
              <div className="modal-footer">
                <button type="button" className="btn btn-outline" onClick={closeModal}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  <i className="fas fa-plus"></i> Add Feed
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Feed Confirmation Modal */}
      {showDeleteFeedModal && (
        <div className="modal-overlay" onClick={closeDeleteFeedModal}>
          <div className="modal-content delete-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>
                <i className="fas fa-exclamation-triangle" style={{color: '#dc3545'}}></i>
                Delete Threat Feed
              </h2>
              <button className="modal-close" onClick={closeDeleteFeedModal}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            
            <div className="modal-body">
              <div className="delete-confirmation">
                <p>
                  Are you sure you want to delete the threat feed <strong>"{feedToDelete?.name}"</strong>?
                </p>
                <div className="warning-text">
                  <i className="fas fa-warning"></i>
                  <span>This action cannot be undone. All associated indicators and TTP data will also be removed.</span>
                </div>
                
                {feedToDelete && (
                  <div className="feed-info">
                    <div className="info-row">
                      <strong>Type:</strong> {feedToDelete.is_external ? 'External TAXII' : 'Internal'}
                    </div>
                    <div className="info-row">
                      <strong>Collection:</strong> {feedToDelete.taxii_collection_id || 'N/A'}
                    </div>
                    <div className="info-row">
                      <strong>Last Sync:</strong> {feedToDelete.last_sync ? new Date(feedToDelete.last_sync).toLocaleString() : 'Never'}
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="modal-footer">
              <div className="modal-actions">
                <button 
                  type="button" 
                  className="btn btn-outline" 
                  onClick={closeDeleteFeedModal}
                  disabled={deletingFeed}
                >
                  Cancel
                </button>
                <button 
                  type="button" 
                  className="btn btn-danger" 
                  onClick={confirmDeleteFeed}
                  disabled={deletingFeed}
                >
                  {deletingFeed ? (
                    <>
                      <i className="fas fa-spinner fa-spin"></i> Deleting...
                    </>
                  ) : (
                    <>
                      <i className="fas fa-trash"></i> Delete Feed
                    </>
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

// IoC Management Component
