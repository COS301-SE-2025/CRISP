import React, { useState, useEffect } from 'react';
import * as api from '../../api.js';
import LoadingSpinner from './LoadingSpinner.jsx';
import ConfirmationModal from './ConfirmationModal.jsx';
import Pagination from './Pagination.jsx';

function TrustManagement({ active, initialTab = null }) {
  
  // State management
  const [trustData, setTrustData] = useState({
    relationships: [],
    groups: [],
    metrics: {},
    organizations: [],
    trustLevels: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // UI state
  const [activeTab, setActiveTab] = useState(() => {
    if (initialTab && ['relationships', 'groups', 'metrics'].includes(initialTab)) {
      return initialTab;
    }
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('tab') || 'relationships';
  });
  
  // Modal states
  const [showModal, setShowModal] = useState(false);
  const [modalMode, setModalMode] = useState('add'); // 'add', 'edit'
  const [modalType, setModalType] = useState('relationship'); // 'relationship', 'group'
  const [selectedItem, setSelectedItem] = useState(null);
  const [modalLoading, setModalLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  
  // Actions popup
  const [showActionsPopup, setShowActionsPopup] = useState(false);
  const [selectedItemForActions, setSelectedItemForActions] = useState(null);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [confirmationData, setConfirmationData] = useState(null);
  
  // Detail view modal
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [detailItem, setDetailItem] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  
  // Group members modal
  const [showMembersModal, setShowMembersModal] = useState(false);
  const [groupMembers, setGroupMembers] = useState([]);
  const [membersLoading, setMembersLoading] = useState(false);
  const [selectedGroup, setSelectedGroup] = useState(null);
  
  // Search and filter
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);
  
  // Form data
  const [formData, setFormData] = useState({
    source_organization: '',
    target_organization: '',
    trust_level: '',
    relationship_type: 'bilateral',
    notes: '',
    // Group fields
    name: '',
    description: '',
    group_type: 'industry',
    is_public: false,
    requires_approval: true,
    // Organization-to-group fields
    selected_organization: '',
    selected_group: ''
  });

  // Get current user data
  const currentUser = JSON.parse(localStorage.getItem('crisp_user') || '{}');
  const isAdmin = currentUser.role === 'BlueVisionAdmin';

  // Load trust data when component becomes active
  useEffect(() => {
    if (active) {
      fetchTrustData();
    }
  }, [active]);

  // Update tab when initialTab prop changes
  useEffect(() => {
    if (initialTab && ['relationships', 'groups', 'metrics'].includes(initialTab)) {
      setActiveTab(initialTab);
    }
  }, [initialTab]);

  // Refetch data when status filter changes
  useEffect(() => {
    if (active) {
      fetchTrustData();
    }
  }, [statusFilter]);

  const fetchTrustData = async (forceRefresh = false) => {
    try {
      setLoading(true);
      setError(null);
      
      // Clear API cache if forcing refresh
      if (forceRefresh) {
        console.log('🧹 Force refresh: Clearing API cache before fetch...');
        api.clearApiCache();
      }
      
      console.log('TrustManagement: Fetching trust data...', { 
        statusFilter, 
        forceRefresh,
        timestamp: new Date().toISOString()
      });
      
      // Build query parameters for trust relationships
      const trustQueryParams = {};
      if (statusFilter) {
        trustQueryParams.status = statusFilter;
        console.log('TrustManagement: Applying status filter:', statusFilter);
      } else {
        console.log('TrustManagement: No status filter applied - will show all except revoked/expired');
      }
      
      const [
        relationshipsResponse,
        groupsResponse,
        metricsResponse,
        orgsResponse,
        trustLevelsResponse
      ] = await Promise.all([
        api.getTrustRelationships(trustQueryParams).catch(err => {
          console.error('Failed to fetch trust relationships:', err);
          return { data: [] };
        }),
        api.getTrustGroups().catch(err => {
          console.error('Failed to fetch trust groups:', err);
          return { data: [] };
        }).then(response => {
          console.log('🔍 TRUST GROUPS RESPONSE:', response);
          console.log('🔍 Response keys:', Object.keys(response || {}));
          console.log('🔍 community_trusts:', response.community_trusts);
          console.log('🔍 data:', response.data);
          return response;
        }),
        api.getTrustMetrics().catch(err => {
          console.error('Failed to fetch trust metrics:', err);
          return { data: {} };
        }),
        api.getOrganizations().catch(err => {
          console.error('Failed to fetch organizations:', err);
          return { data: { organizations: [] } };
        }),
        api.getTrustLevels().catch(err => {
          console.error('Failed to fetch trust levels:', err);
          return [];
        })
      ]);

      console.log('TrustManagement: API responses:', {
        relationships: relationshipsResponse,
        groups: groupsResponse,
        metrics: metricsResponse,
        organizations: orgsResponse,
        trustLevels: trustLevelsResponse
      });
      
      console.log('🔍 RELATIONSHIPS RESPONSE ANALYSIS:');
      console.log('📊 Response keys:', Object.keys(relationshipsResponse || {}));
      
      // Try to stringify safely
      try {
        console.log('📋 Full JSON:', JSON.stringify(relationshipsResponse, null, 2));
      } catch (e) {
        console.log('❌ JSON stringify failed:', e.message);
        console.log('📋 Raw response:', relationshipsResponse);
      }
      
      console.log('🔍 Property checks:');
      console.log('  - success:', relationshipsResponse?.success);
      console.log('  - trusts:', relationshipsResponse?.trusts);
      console.log('  - data:', relationshipsResponse?.data);
      console.log('  - results:', relationshipsResponse?.results);
      console.log('  - count:', relationshipsResponse?.count);
      console.log('  - next:', relationshipsResponse?.next);
      console.log('  - previous:', relationshipsResponse?.previous);
      
      console.log('🔍 TRUST LEVELS DETAILED:', {
        trustLevelsResponse,
        isArray: Array.isArray(trustLevelsResponse),
        length: Array.isArray(trustLevelsResponse) ? trustLevelsResponse.length : 'N/A',
        firstItem: Array.isArray(trustLevelsResponse) && trustLevelsResponse.length > 0 ? trustLevelsResponse[0] : 'None',
        allItems: Array.isArray(trustLevelsResponse) ? trustLevelsResponse : 'Not an array',
        hasProperty: {
          trust_levels: trustLevelsResponse?.trust_levels !== undefined,
          data: trustLevelsResponse?.data !== undefined,
          success: trustLevelsResponse?.success !== undefined
        },
        trust_levels_content: trustLevelsResponse?.trust_levels,
        data_content: trustLevelsResponse?.data
      });

      // Extract relationships with detailed logging
      let extractedRelationships = [];
      
      console.log('🔄 Attempting relationship extraction...');
      
      if (Array.isArray(relationshipsResponse?.trusts)) {
        extractedRelationships = relationshipsResponse.trusts;
        console.log('✅ Extracted relationships from .trusts property:', extractedRelationships.length);
      } else if (Array.isArray(relationshipsResponse?.results?.trusts)) {
        // Handle paginated response: { results: { trusts: [...] } }
        extractedRelationships = relationshipsResponse.results.trusts;
        console.log('✅ Extracted relationships from .results.trusts property:', extractedRelationships.length);
      } else if (relationshipsResponse?.results?.success && Array.isArray(relationshipsResponse?.results?.trusts)) {
        // Handle DRF paginated response: { results: { success: true, trusts: [...] } }
        extractedRelationships = relationshipsResponse.results.trusts;
        console.log('✅ Extracted relationships from paginated .results.trusts property:', extractedRelationships.length);
      } else if (Array.isArray(relationshipsResponse?.data?.trusts)) {
        // Handle nested response: { data: { trusts: [...] } }
        extractedRelationships = relationshipsResponse.data.trusts;
        console.log('✅ Extracted relationships from .data.trusts property:', extractedRelationships.length);
      } else if (Array.isArray(relationshipsResponse?.data)) {
        extractedRelationships = relationshipsResponse.data;
        console.log('✅ Extracted relationships from .data property:', extractedRelationships.length);
      } else if (Array.isArray(relationshipsResponse?.results)) {
        extractedRelationships = relationshipsResponse.results;
        console.log('✅ Extracted relationships from .results property:', extractedRelationships.length);
      } else if (Array.isArray(relationshipsResponse)) {
        extractedRelationships = relationshipsResponse;
        console.log('✅ Using relationships response directly:', extractedRelationships.length);
      } else {
        console.log('❌ Could not extract relationships array from response');
        console.log('📋 Available properties:', Object.keys(relationshipsResponse || {}));
        console.log('📋 Type of response:', typeof relationshipsResponse);
      }

      // Debug the relationship statuses
      console.log('🔍 RELATIONSHIP STATUS ANALYSIS:');
      console.log('📊 Total relationships found:', extractedRelationships.length);
      if (extractedRelationships.length > 0) {
        const statusCounts = {};
        extractedRelationships.forEach((rel, index) => {
          const status = rel.status || 'no-status';
          statusCounts[status] = (statusCounts[status] || 0) + 1;
          if (index < 3) { // Show first 3 for debugging
            console.log(`  ${index + 1}. ID: ${rel.id}, Status: ${status}, Target: ${rel.target_organization?.name || 'N/A'}`);
          }
        });
        console.log('📊 Status distribution:', statusCounts);
      }

      setTrustData({
        relationships: extractedRelationships,
        groups: Array.isArray(groupsResponse.results?.data) ? groupsResponse.results.data :
                Array.isArray(groupsResponse.results?.community_trusts) ? groupsResponse.results.community_trusts :
                (groupsResponse.results?.success && Array.isArray(groupsResponse.results?.data)) ? groupsResponse.results.data :
                Array.isArray(groupsResponse.community_trusts) ? groupsResponse.community_trusts :
                Array.isArray(groupsResponse.data?.community_trusts) ? groupsResponse.data.community_trusts :
                (groupsResponse.success && groupsResponse.community_trusts) ? groupsResponse.community_trusts :
                Array.isArray(groupsResponse.data) ? groupsResponse.data : 
                Array.isArray(groupsResponse) ? groupsResponse : [],
        metrics: (metricsResponse.data && typeof metricsResponse.data === 'object') ? metricsResponse.data : 
                (metricsResponse && typeof metricsResponse === 'object') ? metricsResponse : {},
        organizations: Array.isArray(orgsResponse.results?.organizations) ? orgsResponse.results.organizations :
                      Array.isArray(orgsResponse.data?.organizations) ? orgsResponse.data.organizations : 
                      Array.isArray(orgsResponse.data) ? orgsResponse.data : 
                      Array.isArray(orgsResponse) ? orgsResponse : [],
        trustLevels: Array.isArray(trustLevelsResponse?.trust_levels) ? trustLevelsResponse.trust_levels : 
                    Array.isArray(trustLevelsResponse?.data) ? trustLevelsResponse.data : 
                    Array.isArray(trustLevelsResponse) ? trustLevelsResponse : []
      });

      // Debug what trust levels were actually extracted
      const extractedTrustLevels = Array.isArray(trustLevelsResponse?.trust_levels) ? trustLevelsResponse.trust_levels : 
                                   Array.isArray(trustLevelsResponse?.data) ? trustLevelsResponse.data : 
                                   Array.isArray(trustLevelsResponse) ? trustLevelsResponse : [];
      
      console.log('✅ EXTRACTED TRUST LEVELS:', {
        count: extractedTrustLevels.length,
        levels: extractedTrustLevels.map(level => ({ id: level.id, name: level.name, level: level.level })),
        firstLevel: extractedTrustLevels.length > 0 ? extractedTrustLevels[0] : null
      });
    } catch (err) {
      console.error('Error fetching trust data:', err);
      setError('Failed to load trust data');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (tabName) => {
    if (!['relationships', 'groups', 'metrics'].includes(tabName) || tabName === activeTab) {
      return;
    }
    
    setActiveTab(tabName);
    
    // Update URL without causing re-renders
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set('tab', tabName);
    const newUrl = `${window.location.pathname}?${urlParams.toString()}`;
    window.history.replaceState(null, '', newUrl);
  };

  const openModal = (mode, type, item = null) => {
    setModalMode(mode);
    setModalType(type);
    setSelectedItem(item);
    
    if (mode === 'edit' && item) {
      if (type === 'relationship') {
        // Map trust level string back to level code for dropdown 
        // Backend returns trust level in format like "Basic Trust (public)" or "Standard Trust (trusted)"
        // We need to extract the level code from parentheses or find by exact name match
        let trustLevelCode = '';
        let trustLevelObj = null;
        
        // Handle trust_level as either object or string
        if (typeof item.trust_level === 'object' && item.trust_level !== null) {
          // trust_level is an object with properties like name, level, etc.
          trustLevelCode = item.trust_level.level || '';
          trustLevelObj = trustData.trustLevels.find(level => level.level === trustLevelCode);
        } else if (typeof item.trust_level === 'string') {
          // trust_level is a string - try to extract level from parentheses like "Basic Trust (public)" -> "public"
          const parenthesesMatch = item.trust_level.match(/\(([^)]+)\)/);
          if (parenthesesMatch) {
            const extractedLevel = parenthesesMatch[1].toLowerCase().trim();
            trustLevelObj = trustData.trustLevels.find(level => level.level === extractedLevel);
            if (trustLevelObj) {
              trustLevelCode = extractedLevel;
            }
          }
          
          // If no match from parentheses, try exact name or level matching
          if (!trustLevelObj) {
            trustLevelObj = trustData.trustLevels.find(
              level => level.name.toLowerCase().trim() === item.trust_level.toLowerCase().trim() ||
                       level.level.toLowerCase().trim() === item.trust_level.toLowerCase().trim() ||
                       level.name === item.trust_level ||
                       level.level === item.trust_level
            );
            trustLevelCode = trustLevelObj?.level || item.trust_level.toLowerCase() || '';
          }
        }
        
        console.log('🔍 TRUST LEVEL MAPPING FOR EDIT:', {
          itemTrustLevel: item.trust_level,
          itemTrustLevelType: typeof item.trust_level,
          mappedCode: trustLevelCode,
          foundTrustLevelObj: trustLevelObj,
          availableLevels: trustData.trustLevels.map(l => ({ id: l.id, name: l.name, level: l.level }))
        });
        
        // Map organization objects to IDs for dropdowns
        // Backend sends: { source_organization: { id, name, domain, organization_type }, ... }
        console.log('🔧 EDIT MODE - Mapping organizations for relationship:', {
          relationshipItem: item,
          sourceOrg: item.source_organization,
          targetOrg: item.target_organization,
          trustLevel: item.trust_level,
          availableOrgs: trustData.organizations.map(o => ({ id: o.id, name: o.name })),
          availableTrustLevels: trustData.trustLevels.map(t => ({ id: t.id, name: t.name, level: t.level }))
        });
        
        // Extract IDs from the organization objects
        const sourceOrgId = item.source_organization?.id || '';
        const targetOrgId = item.target_organization?.id || '';
        
        console.log('✅ MAPPED - Organization IDs:', { 
          sourceOrgId, 
          targetOrgId, 
          trustLevelCode,
          finalFormData: {
            source_organization: sourceOrgId,
            target_organization: targetOrgId,
            trust_level: trustLevelCode,
            relationship_type: item.relationship_type || 'bilateral',
            notes: item.notes || ''
          }
        });
        
        setFormData({
          source_organization: sourceOrgId,
          target_organization: targetOrgId,
          trust_level: trustLevelCode,
          relationship_type: item.relationship_type || 'bilateral',
          notes: item.notes || ''
        });
      } else if (type === 'group') {
        // For groups, we need to map from the trust level ID to the level code
        const groupTrustLevelObj = trustData.trustLevels.find(level => level.id === item.default_trust_level_id);
        const groupTrustLevelCode = groupTrustLevelObj?.level || '';
        
        console.log('🔧 GROUP EDIT - Trust level mapping:', {
          item_default_trust_level_id: item.default_trust_level_id,
          foundTrustLevelObj: groupTrustLevelObj,
          mappedCode: groupTrustLevelCode
        });
        
        setFormData({
          name: item.name || '',
          description: item.description || '',
          group_type: item.group_type || 'industry',
          is_public: item.is_public || false,
          requires_approval: item.requires_approval || true,
          trust_level: groupTrustLevelCode
        });
      }
    } else {
      setFormData({
        source_organization: '',
        target_organization: '',
        trust_level: '',
        relationship_type: 'bilateral',
        notes: '',
        name: '',
        description: '',
        group_type: 'industry',
        is_public: false,
        requires_approval: true,
        selected_organization: '',
        selected_group: ''
      });
    }
    
    // Show the modal
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedItem(null);
    setModalLoading(false);
    setSubmitting(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    // For relationship creation, check if relationship already exists
    if (modalType === 'relationship' && modalMode === 'add') {
      const existingRelationship = trustData.relationships.find(rel => 
        (rel.source_organization?.id === formData.source_organization && rel.target_organization?.id === formData.target_organization) ||
        (rel.source_organization?.id === formData.target_organization && rel.target_organization?.id === formData.source_organization)
      );
      
      if (existingRelationship) {
        const sourceOrgName = trustData.organizations.find(org => org.id === formData.source_organization)?.name || 'Source Org';
        const targetOrgName = trustData.organizations.find(org => org.id === formData.target_organization)?.name || 'Target Org';
        setError(`A trust relationship already exists between ${sourceOrgName} and ${targetOrgName}. Please edit the existing relationship instead.`);
        return;
      }
    }

    // Show confirmation dialog
    const actionText = modalMode === 'add' ? 'create' : 'update';
    const itemName = modalType === 'relationship' ? 
      `relationship with ${trustData.organizations.find(org => org.id === formData.target_organization)?.name || 'selected organization'}` :
      formData.name;
    
    setConfirmationData({
      title: modalType === 'org-to-group' ? 'Add Organization to Group' :
             `${modalMode === 'add' ? 'Create' : 'Update'} ${modalType === 'relationship' ? 'Trust Relationship' : 'Trust Group'}`,
      message: modalType === 'org-to-group' ? 
               `Are you sure you want to add the selected organization to the selected trust group?` :
               `Are you sure you want to ${actionText} ${modalType} "${itemName}"?`,
      confirmText: modalType === 'org-to-group' ? 'Add to Group' :
                   modalMode === 'add' ? `Create ${modalType === 'relationship' ? 'Relationship' : 'Group'}` : `Update ${modalType === 'relationship' ? 'Relationship' : 'Group'}`,
      isDestructive: false,
      actionType: 'default',
      action: async () => {
        try {
          setSubmitting(true);
          
          if (modalType === 'relationship') {
            // Convert IDs to names for the API
            console.log('🚀 SUBMIT - Converting form data to API format:', {
              formData,
              availableTrustLevels: trustData.trustLevels,
              selectedTrustLevelId: formData.trust_level,
              trustLevelCount: trustData.trustLevels.length,
              trustLevelStructure: trustData.trustLevels.map(tl => ({ 
                id: tl.id, 
                name: tl.name, 
                level: tl.level,
                type_id: typeof tl.id,
                type_name: typeof tl.name 
              }))
            });

            const sourceOrgName = trustData.organizations.find(org => org.id === formData.source_organization)?.name || formData.source_organization;
            const targetOrgName = trustData.organizations.find(org => org.id === formData.target_organization)?.name || formData.target_organization;
            
            // Form data now contains the level code directly (e.g., "high", "medium", "low")
            // Backend API expects this level code as-is
            const trustLevelCode = formData.trust_level;
            
            // Verify the trust level exists in our available trust levels
            const trustLevelObj = trustData.trustLevels.find(level => level.level === trustLevelCode);
            if (!trustLevelObj) {
              console.error('❌ TRUST LEVEL ERROR: Could not find trust level for code:', trustLevelCode);
              console.error('Available trust levels:', trustData.trustLevels.map(tl => ({ level: tl.level, name: tl.name })));
              throw new Error(`Trust level not found for code: ${trustLevelCode}`);
            }

            console.log('🔄 CONVERTED - API data:', {
              sourceOrgName,
              targetOrgName, 
              trustLevelCode,
              trustLevelObj,
              backendExpectation: 'Backend expects level code like "high", "medium", "low", "public", etc.'
            });
            
            // Create payload for backend API
            // For edit mode, only send the fields that can be updated (trust_level, notes)
            // Organizations and relationship_type cannot be changed after relationship creation
            const relationshipData = modalMode === 'edit' ? {
              trust_level: trustLevelCode,  // Send level code (e.g., "high", "medium", "low")
              notes: formData.notes,  // Notes field for updates
              message: 'Relationship updated via UI'  // Log message
            } : {
              source_organization: formData.source_organization,  // Send ID, not name
              target_organization: formData.target_organization,  // Send ID, not name
              trust_level: trustLevelCode,  // Send level code (e.g., "high", "medium", "low")
              relationship_type: formData.relationship_type,
              notes: formData.notes
            };

            console.log('📤 FINAL API PAYLOAD:', {
              mode: modalMode,
              payload: relationshipData,
              editableFields: modalMode === 'edit' ? ['trust_level', 'notes'] : ['all fields'],
              readOnlyFields: modalMode === 'edit' ? ['source_organization', 'target_organization', 'relationship_type'] : []
            });
            
            if (modalMode === 'add') {
              console.log('🚀 CREATING trust relationship with data:', relationshipData);
              await api.createTrustRelationship(relationshipData);
              setSuccess('Trust relationship created successfully');
            } else {
              console.log('🔄 UPDATING trust relationship:', {
                id: selectedItem.id,
                originalItem: selectedItem,
                updateData: relationshipData
              });
              await api.updateTrustRelationship(selectedItem.id, relationshipData);
              setSuccess('Trust relationship updated successfully');
            }
          } else if (modalType === 'group') {
            const groupData = { ...formData };
            if (formData.trust_level && formData.trust_level.trim() !== '') {
              // Find the trust level ID by the level value
              const trustLevelObj = trustData.trustLevels.find(level => level.level === formData.trust_level);
              if (trustLevelObj) {
                groupData.default_trust_level_id = trustLevelObj.id;
                console.log('✅ TRUST LEVEL FOUND:', { level: formData.trust_level, id: trustLevelObj.id });
                console.log('🔍 DEBUG: All available trust levels:', trustData.trustLevels.map(tl => ({ level: tl.level, id: tl.id, name: tl.name })));
              } else {
                console.error('❌ TRUST LEVEL ERROR: Could not find trust level for:', formData.trust_level);
                console.error('Available trust levels:', trustData.trustLevels.map(tl => ({ level: tl.level, id: tl.id, name: tl.name })));
                throw new Error(`Trust level not found: ${formData.trust_level}`);
              }
            } else {
              console.log('ℹ️ No trust level selected - backend will use default (public)');
              console.log('🔍 DEBUG: Available trust levels when none selected:', trustData.trustLevels.map(tl => ({ level: tl.level, id: tl.id, name: tl.name })));
            }
            // Always remove trust_level from group data as backend expects default_trust_level_id
            delete groupData.trust_level;
            
            if (modalMode === 'add') {
              console.log('🚀 CREATING trust group with data:', groupData);
              await api.createTrustGroup(groupData);
              setSuccess('Trust group created successfully');
            } else {
              console.log('🔄 UPDATING trust group:', {
                id: selectedItem.id,
                originalItem: selectedItem,
                updateData: groupData
              });
              await api.updateTrustGroup(selectedItem.id, groupData);
              setSuccess('Trust group updated successfully');
            }
          } else if (modalType === 'org-to-group') {
            // Add organization to trust group
            console.log('🚀 ADDING organization to trust group:', {
              organization: formData.selected_organization,
              group: formData.selected_group
            });
            
            if (!formData.selected_organization || !formData.selected_group) {
              throw new Error('Please select both an organization and a trust group');
            }
            
            // Use the new addOrganizationToTrustGroup API
            await api.addOrganizationToTrustGroup(formData.selected_group, formData.selected_organization);
            setSuccess('Organization added to trust group successfully');
          }
          
          // Auto-dismiss success message after 5 seconds
          setTimeout(() => setSuccess(null), 5000);
          
          closeModal();
          console.log('🔄 UPDATE SUCCESS: Clearing trust cache and refreshing data...');
          api.clearCacheForEndpoint('/api/trust/');
          await fetchTrustData(true);
          
        } catch (error) {
          console.error(`Error ${actionText}ing ${modalType}:`, error);
          setError(`Failed to ${actionText} ${modalType}: ${error.message || error}`);
        } finally {
          setSubmitting(false);
        }
      }
    });
    setShowConfirmation(true);
  };

  const openActionsPopup = (item) => {
    setSelectedItemForActions(item);
    setShowActionsPopup(true);
  };

  const closeActionsPopup = () => {
    setShowActionsPopup(false);
    setSelectedItemForActions(null);
  };

  const showGroupMembers = async (group) => {
    try {
      setSelectedGroup(group);
      setMembersLoading(true);
      setShowMembersModal(true);
      
      console.log('🔍 FETCHING members for group:', group.id);
      const response = await api.getTrustGroupMembers(group.id);
      
      if (response.success) {
        setGroupMembers(response.data.members || []);
        console.log('✅ GROUP MEMBERS loaded:', response.data.members);
      } else {
        throw new Error(response.message || 'Failed to fetch group members');
      }
    } catch (error) {
      console.error('❌ Error fetching group members:', error);
      setError(`Failed to fetch group members: ${error.message}`);
      setGroupMembers([]);
    } finally {
      setMembersLoading(false);
    }
  };

  const closeMembersModal = () => {
    setShowMembersModal(false);
    setSelectedGroup(null);
    setGroupMembers([]);
  };

  const handleAction = (actionType) => {
    const item = selectedItemForActions;
    if (!item) return;

    switch (actionType) {
      case 'view':
        closeActionsPopup();
        setDetailItem(item);
        setShowDetailModal(true);
        break;
        
      case 'edit':
        closeActionsPopup();
        openModal('edit', activeTab === 'relationships' ? 'relationship' : 'group', item);
        break;
        
      case 'activate':
        setConfirmationData({
          title: 'Activate Relationship',
          message: `Are you sure you want to activate the relationship with ${item.target_organization?.name || item.target_organization_name || 'the selected organization'}?`,
          confirmText: 'Activate',
          isDestructive: false,
          actionType: 'default',
          action: async () => {
            try {
              // Extract trust level from the item - API expects the trust level name
              let trustLevelName = 'public';
              if (item.trust_level) {
                if (typeof item.trust_level === 'object' && item.trust_level !== null) {
                  // trust_level is an object - use the level property
                  trustLevelName = item.trust_level.level || 'public';
                } else if (typeof item.trust_level === 'string') {
                  // trust_level is a string - extract from parentheses or use as-is
                  const match = item.trust_level.match(/\(([^)]+)\)/);
                  trustLevelName = match ? match[1] : item.trust_level.toLowerCase().split(' ')[0];
                }
              }
              
              // Use the respond API to accept the trust relationship
              await api.respondToTrustRelationship(item.id, 'accept', trustLevelName, 'Relationship activated');
              setSuccess('Relationship activated successfully');
              setTimeout(() => setSuccess(null), 5000);
              closeActionsPopup();
              fetchTrustData();
            } catch (error) {
              setError('Failed to activate relationship: ' + error.message);
            }
          }
        });
        setShowConfirmation(true);
        break;
        
      case 'suspend':
        setConfirmationData({
          title: 'Suspend Relationship',
          message: `Are you sure you want to suspend the relationship with ${item.target_organization?.name || item.target_organization_name || 'the selected organization'}?`,
          confirmText: 'Suspend',
          isDestructive: true,
          actionType: 'destructive',
          action: async () => {
            try {
              // Extract trust level from the item - API expects the trust level name
              let trustLevelName = 'public';
              if (item.trust_level) {
                if (typeof item.trust_level === 'object' && item.trust_level !== null) {
                  // trust_level is an object - use the level property
                  trustLevelName = item.trust_level.level || 'public';
                } else if (typeof item.trust_level === 'string') {
                  // trust_level is a string - extract from parentheses or use as-is
                  const match = item.trust_level.match(/\(([^)]+)\)/);
                  trustLevelName = match ? match[1] : item.trust_level.toLowerCase().split(' ')[0];
                }
              }
              
              await api.updateTrustRelationship(item.id, { 
                status: 'suspended',
                message: 'Relationship suspended'
              });
              setSuccess('Relationship suspended successfully');
              setTimeout(() => setSuccess(null), 5000);
              closeActionsPopup();
              fetchTrustData();
            } catch (error) {
              setError('Failed to suspend relationship: ' + error.message);
            }
          }
        });
        setShowConfirmation(true);
        break;
        
      case 'view_members':
        closeActionsPopup();
        showGroupMembers(item);
        break;
        
      case 'delete':
        const itemName = activeTab === 'relationships' ? 
          `relationship with ${item.target_organization?.name || item.target_organization_name || 'the selected organization'}` :
          `group "${item.name}"`;
          
        setConfirmationData({
          title: `Delete ${activeTab === 'relationships' ? 'Trust Relationship' : 'Trust Group'}`,
          message: `Are you sure you want to delete this ${itemName}? This action cannot be undone.`,
          confirmText: 'Delete',
          isDestructive: true,
          actionType: 'destructive',
          action: async () => {
            try {
              if (activeTab === 'relationships') {
                console.log('🗑️ DELETING TRUST RELATIONSHIP:', item.id);
                await api.deleteTrustRelationship(item.id, 'Relationship deleted by user');
                setSuccess('Trust relationship deleted successfully');
                console.log('✅ DELETE SUCCESS: Trust relationship deleted');
              } else {
                console.log('🗑️ DELETING TRUST GROUP:', item.id);
                await api.deleteTrustGroup(item.id);
                setSuccess('Trust group deleted successfully');
                console.log('✅ DELETE SUCCESS: Trust group deleted');
              }
              setTimeout(() => setSuccess(null), 5000);
              closeActionsPopup();
              console.log('🔄 DELETE SUCCESS: Clearing trust cache and refreshing data...');
              api.clearCacheForEndpoint('/api/trust/');
              await fetchTrustData(true);
            } catch (error) {
              setError(`Failed to delete ${activeTab === 'relationships' ? 'relationship' : 'group'}: ${error.message}`);
            }
          }
        });
        setShowConfirmation(true);
        break;
        
      case 'join':
        setConfirmationData({
          title: 'Join Trust Group',
          message: `Are you sure you want to join the group "${item.name}"?`,
          confirmText: 'Join Group',
          isDestructive: false,
          actionType: 'default',
          action: async () => {
            try {
              await api.joinTrustGroup(item.id);
              setSuccess('Successfully joined trust group!');
              setTimeout(() => setSuccess(null), 5000);
              closeActionsPopup();
              fetchTrustData();
            } catch (error) {
              setError('Failed to join trust group: ' + error.message);
            }
          }
        });
        setShowConfirmation(true);
        break;
    }
  };

  // Filter and paginate data
  const getFilteredData = () => {
    const data = activeTab === 'relationships' ? trustData.relationships : trustData.groups;
    
    let filtered = data.filter(item => {
      const matchesSearch = searchTerm === '' || 
        (activeTab === 'relationships' ? 
          (item.target_organization?.name || item.target_organization_name || item.source_organization?.name || item.source_organization_name || '').toLowerCase().includes(searchTerm.toLowerCase()) :
          (item.name || '').toLowerCase().includes(searchTerm.toLowerCase())
        );
      
      const matchesStatus = statusFilter === '' || 
        (activeTab === 'relationships' ? 
          item.status === statusFilter :
          (statusFilter === 'public' ? item.is_public : !item.is_public)
        );
      
      return matchesSearch && matchesStatus;
    });
    
    return filtered;
  };

  const filteredData = getFilteredData();
  const totalItems = filteredData.length;
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedData = filteredData.slice(startIndex, startIndex + itemsPerPage);

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  if (!active) {
    return null;
  }

  if (loading) {
    return (
      <div className="trust-management">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif', position: 'relative' }}>
      {(loading || submitting) && <LoadingSpinner fullscreen={true} />}
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ marginBottom: '0.5rem', color: '#333' }}>Trust Management</h1>
        {!isAdmin && (
          <div style={{
            padding: '0.75rem 1rem',
            backgroundColor: '#fff3cd',
            color: '#856404',
            borderRadius: '6px',
            border: '1px solid #ffeaa7',
            fontSize: '0.875rem',
            fontWeight: '500'
          }}>
            <strong>Publisher Mode:</strong> You can manage trust relationships and groups for your organization and organizations with trusted relationships.
          </div>
        )}
      </div>

      {/* Error/Success Messages */}
      {error && (
        <div style={{
          backgroundColor: '#f8d7da',
          color: '#721c24',
          border: '1px solid #f5c6cb',
          borderRadius: '4px',
          padding: '0.75rem 1rem',
          marginBottom: '1rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <span>{error}</span>
          <button 
            onClick={() => setError(null)}
            style={{
              background: 'none',
              border: 'none',
              color: '#721c24',
              fontSize: '1.25rem',
              cursor: 'pointer',
              padding: '0',
              lineHeight: '1'
            }}
          >
            ×
          </button>
        </div>
      )}

      {success && (
        <div style={{
          backgroundColor: '#d4edda',
          color: '#155724',
          border: '1px solid #c3e6cb',
          borderRadius: '4px',
          padding: '0.75rem 1rem',
          marginBottom: '1rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <span>{success}</span>
          <button 
            onClick={() => setSuccess(null)}
            style={{
              background: 'none',
              border: 'none',
              color: '#155724',
              fontSize: '1.25rem',
              cursor: 'pointer',
              padding: '0',
              lineHeight: '1'
            }}
          >
            ×
          </button>
        </div>
      )}

      {/* Tabs */}
      <div style={{ marginBottom: '1.5rem' }}>
        <div style={{ borderBottom: '1px solid #dee2e6' }}>
          {['relationships', 'groups', 'metrics'].map(tab => (
            <button
              key={tab}
              onClick={() => handleTabChange(tab)}
              style={{
                padding: '0.75rem 1.5rem',
                border: 'none',
                backgroundColor: activeTab === tab ? '#007bff' : 'transparent',
                color: activeTab === tab ? 'white' : '#495057',
                borderRadius: '4px 4px 0 0',
                marginRight: '0.25rem',
                cursor: 'pointer',
                textTransform: 'capitalize',
                fontWeight: activeTab === tab ? '600' : '400'
              }}
            >
              {tab} ({tab === 'relationships' ? trustData.relationships.length : 
                     tab === 'groups' ? trustData.groups.length : 'N/A'})
            </button>
          ))}
        </div>
      </div>

      {/* Content based on active tab */}
      {activeTab !== 'metrics' && (
        <>
          {/* Controls */}
          <div style={{ 
            display: 'flex', 
            gap: '1rem', 
            marginBottom: '2rem',
            flexWrap: 'wrap',
            alignItems: 'center'
          }}>
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', flex: 1 }}>
              <input
                type="text"
                placeholder={`Search ${activeTab}...`}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{
                  padding: '0.5rem',
                  border: '1px solid #ced4da',
                  borderRadius: '4px',
                  minWidth: '200px'
                }}
              />
              
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                style={{
                  padding: '0.5rem',
                  border: '1px solid #ced4da',
                  borderRadius: '4px',
                  minWidth: '120px'
                }}
              >
                <option value="">All Status</option>
                {activeTab === 'relationships' ? (
                  <>
                    <option value="active">Active</option>
                    <option value="pending">Pending</option>
                    <option value="suspended">Suspended</option>
                    {isAdmin && <option value="revoked">Revoked</option>}
                    {isAdmin && <option value="expired">Expired</option>}
                  </>
                ) : (
                  <>
                    <option value="public">Public</option>
                    <option value="private">Private</option>
                  </>
                )}
              </select>
            </div>
            
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                onClick={() => openModal('add', activeTab === 'relationships' ? 'relationship' : 'group')}
                disabled={!isAdmin && activeTab === 'groups'}
                style={{
                  padding: '0.5rem 1rem',
                  backgroundColor: (!isAdmin && activeTab === 'groups') ? '#6c757d' : '#007bff',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: (!isAdmin && activeTab === 'groups') ? 'not-allowed' : 'pointer',
                  fontWeight: '500'
                }}
                title={(!isAdmin && activeTab === 'groups') ? 'Only administrators can create trust groups' : ''}
              >
                Add {activeTab === 'relationships' ? 'Relationship' : 'Group'}
              </button>
              
              {activeTab === 'groups' && isAdmin && (
                <button
                  onClick={() => openModal('add', 'org-to-group')}
                  style={{
                    padding: '0.5rem 1rem',
                    backgroundColor: '#28a745',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontWeight: '500'
                  }}
                  title="Add organization to trust group"
                >
                  Add Organization
                </button>
              )}
            </div>
          </div>

          {/* Data List */}
          <div style={{ 
            backgroundColor: 'white',
            borderRadius: '8px',
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
            border: '1px solid #e9ecef'
          }}>
            {paginatedData.length === 0 ? (
              <div style={{ 
                textAlign: 'center', 
                padding: '3rem', 
                color: '#6c757d'
              }}>
                <h4 style={{ marginBottom: '0.5rem' }}>No {activeTab} found</h4>
                <p style={{ margin: '0' }}>
                  {filteredData.length === 0 && (searchTerm || statusFilter) ? 
                    'No items match your search criteria.' :
                    `No ${activeTab} available. Click "Add ${activeTab === 'relationships' ? 'Relationship' : 'Group'}" to create the first one.`
                  }
                </p>
              </div>
            ) : (
              paginatedData.map((item) => (
                <div 
                  key={item.id}
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    openActionsPopup(item);
                  }}
                  style={{ 
                    display: 'flex',
                    alignItems: 'center',
                    padding: '1.25rem',
                    borderBottom: '1px solid #e9ecef',
                    transition: 'all 0.2s ease',
                    cursor: 'pointer',
                    backgroundColor: 'transparent'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#f8f9fa';
                    e.currentTarget.style.transform = 'translateX(4px)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'transparent';
                    e.currentTarget.style.transform = 'translateX(0px)';
                  }}
                >
                  <div style={{ flex: '1', minWidth: '0' }}>
                    {activeTab === 'relationships' ? (
                      <>
                        <div style={{ 
                          display: 'flex', 
                          alignItems: 'center', 
                          gap: '1rem',
                          flexWrap: 'wrap'
                        }}>
                          <div style={{ fontWeight: '600', color: '#212529', fontSize: '1.1rem' }}>
                            {item.source_organization?.name || item.source_organization_name || 'Unknown'} → {item.target_organization?.name || item.target_organization_name || 'Unknown'}
                          </div>
                          <span style={{
                            padding: '0.25rem 0.5rem',
                            borderRadius: '4px',
                            fontSize: '0.75rem',
                            fontWeight: '600',
                            textTransform: 'uppercase',
                            backgroundColor: item.trust_level?.name === 'HIGH' ? '#d4edda' : item.trust_level?.name === 'MEDIUM' ? '#fff3cd' : '#f8f9fa',
                            color: item.trust_level?.name === 'HIGH' ? '#155724' : item.trust_level?.name === 'MEDIUM' ? '#856404' : '#495057'
                          }}>
                            {item.trust_level?.name || item.trust_level?.level || 'Unknown'}
                          </span>
                          <span style={{
                            padding: '0.25rem 0.5rem',
                            borderRadius: '4px',
                            fontSize: '0.75rem',
                            fontWeight: '600',
                            textTransform: 'uppercase',
                            backgroundColor: item.status === 'active' ? '#d4edda' : item.status === 'pending' ? '#fff3cd' : '#f8d7da',
                            color: item.status === 'active' ? '#155724' : item.status === 'pending' ? '#856404' : '#721c24'
                          }}>
                            {item.status || 'Unknown'}
                          </span>
                        </div>
                        <div style={{ 
                          marginTop: '0.5rem', 
                          color: '#6c757d', 
                          fontSize: '0.875rem',
                          display: 'flex',
                          gap: '1rem',
                          flexWrap: 'wrap'
                        }}>
                          <span>Type: {item.relationship_type}</span>
                          {item.notes && <span>Notes: {item.notes}</span>}
                        </div>
                      </>
                    ) : (
                      <>
                        <div style={{ 
                          display: 'flex', 
                          alignItems: 'center', 
                          gap: '1rem',
                          flexWrap: 'wrap'
                        }}>
                          <div style={{ fontWeight: '600', color: '#212529', fontSize: '1.1rem' }}>
                            {item.name}
                          </div>
                          <span style={{
                            padding: '0.25rem 0.5rem',
                            borderRadius: '4px',
                            fontSize: '0.75rem',
                            fontWeight: '600',
                            textTransform: 'uppercase',
                            backgroundColor: item.group_type === 'SECURITY' ? '#d4edda' : item.group_type === 'BUSINESS' ? '#fff3cd' : '#f8f9fa',
                            color: item.group_type === 'SECURITY' ? '#155724' : item.group_type === 'BUSINESS' ? '#856404' : '#495057'
                          }}>
                            {item.group_type}
                          </span>
                          <span style={{
                            padding: '0.25rem 0.5rem',
                            borderRadius: '4px',
                            fontSize: '0.75rem',
                            fontWeight: '600',
                            textTransform: 'uppercase',
                            backgroundColor: item.is_public ? '#d4edda' : '#fff3cd',
                            color: item.is_public ? '#155724' : '#856404'
                          }}>
                            {item.is_public ? 'Public' : 'Private'}
                          </span>
                        </div>
                        <div style={{ 
                          marginTop: '0.5rem', 
                          color: '#6c757d', 
                          fontSize: '0.875rem',
                          display: 'flex',
                          gap: '1rem',
                          flexWrap: 'wrap'
                        }}>
                          <span>{item.description}</span>
                          <span>Members: {item.member_count || 0}</span>
                        </div>
                      </>
                    )}
                  </div>
                  <div style={{ 
                    fontSize: '1.2rem', 
                    color: '#6c757d',
                    marginLeft: '1rem',
                    transition: 'transform 0.2s ease'
                  }}>
                    →
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Pagination */}
          {totalItems > itemsPerPage && (
            <div style={{ marginTop: '1rem' }}>
              <Pagination
                currentPage={currentPage}
                totalItems={totalItems}
                itemsPerPage={itemsPerPage}
                onPageChange={handlePageChange}
                showInfo={true}
                showJumpToPage={true}
              />
            </div>
          )}
        </>
      )}

      {/* Metrics Tab */}
      {activeTab === 'metrics' && (
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
          gap: '1rem'
        }}>
          {[
            { 
              title: 'Total Relationships', 
              value: trustData.relationships.length, 
              description: isAdmin ? 'All system relationships' : 'Your organization relationships' 
            },
            { 
              title: 'Active Groups', 
              value: trustData.groups.length, 
              description: isAdmin ? 'All system groups' : 'Your accessible groups' 
            },
            { 
              title: 'Trust Score', 
              value: trustData.metrics.trust_score || 'N/A', 
              description: isAdmin ? 'System average' : 'Organization trust score' 
            },
            { 
              title: 'Connected Organizations', 
              value: trustData.metrics.connected_orgs || 0, 
              description: isAdmin ? 'Total connected orgs' : 'Organizations you trust' 
            }
          ].map((metric, index) => (
            <div key={index} style={{
              backgroundColor: 'white',
              border: '1px solid #dee2e6',
              borderRadius: '8px',
              padding: '1.5rem',
              textAlign: 'center'
            }}>
              <h4 style={{ margin: '0 0 0.5rem 0', color: '#495057', fontSize: '1rem' }}>
                {metric.title}
              </h4>
              <div style={{ 
                fontSize: '2rem', 
                fontWeight: 'bold', 
                color: '#007bff',
                margin: '0.5rem 0'
              }}>
                {metric.value}
              </div>
              <div style={{ 
                fontSize: '0.75rem', 
                color: '#6c757d',
                fontStyle: 'italic'
              }}>
                {metric.description}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            padding: '1.5rem',
            width: '90%',
            maxWidth: '500px',
            maxHeight: '90vh',
            overflowY: 'auto'
          }}>
            <h3 style={{ margin: '0 0 1rem 0' }}>
              {modalType === 'org-to-group' ? 'Add Organization to Trust Group' : 
               `${modalMode === 'add' ? 'Create' : 'Edit'} ${modalType === 'relationship' ? 'Trust Relationship' : 'Trust Group'}`}
              {modalMode === 'edit' && modalType === 'relationship' && (
                <div style={{ 
                  fontSize: '0.875em', 
                  fontWeight: 'normal', 
                  color: '#6c757d', 
                  marginTop: '0.25rem' 
                }}>
                  Only trust level and notes can be modified
                </div>
              )}
            </h3>
            
            <form onSubmit={handleSubmit}>
              {modalType === 'relationship' && (
                <>
                  {isAdmin && (
                    <div style={{ marginBottom: '1rem' }}>
                      <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                        Source Organization *
                      </label>
                      {modalMode === 'edit' ? (
                        <div style={{
                          width: '100%',
                          padding: '0.5rem',
                          border: '1px solid #e9ecef',
                          borderRadius: '4px',
                          backgroundColor: '#f8f9fa',
                          color: '#6c757d'
                        }}>
                          {trustData.organizations.find(org => org.id === formData.source_organization)?.name || 'Unknown Organization'}
                          <small style={{ display: 'block', fontSize: '0.875em', marginTop: '0.25rem' }}>
                            Organizations cannot be changed when editing
                          </small>
                        </div>
                      ) : (
                        <select
                          value={formData.source_organization || ''}
                          onChange={(e) => setFormData({...formData, source_organization: e.target.value})}
                          required={isAdmin}
                          style={{
                            width: '100%',
                            padding: '0.5rem',
                            border: '1px solid #ced4da',
                            borderRadius: '4px'
                          }}
                        >
                          <option value="">Select Source Organization</option>
                          {trustData.organizations.map(org => (
                            <option key={org.id} value={org.id}>{org.name}</option>
                          ))}
                        </select>
                      )}
                    </div>
                  )}
                  
                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                      Target Organization *
                    </label>
                    {modalMode === 'edit' ? (
                      <div style={{
                        width: '100%',
                        padding: '0.5rem',
                        border: '1px solid #e9ecef',
                        borderRadius: '4px',
                        backgroundColor: '#f8f9fa',
                        color: '#6c757d'
                      }}>
                        {trustData.organizations.find(org => org.id === formData.target_organization)?.name || 'Unknown Organization'}
                        <small style={{ display: 'block', fontSize: '0.875em', marginTop: '0.25rem' }}>
                          Organizations cannot be changed when editing
                        </small>
                      </div>
                    ) : (
                      <select
                        value={formData.target_organization}
                        onChange={(e) => setFormData({...formData, target_organization: e.target.value})}
                        required
                        style={{
                          width: '100%',
                          padding: '0.5rem',
                          border: '1px solid #ced4da',
                          borderRadius: '4px'
                        }}
                      >
                        <option value="">Select Organization</option>
                        {trustData.organizations.map(org => (
                          <option key={org.id} value={org.id}>{org.name}</option>
                        ))}
                      </select>
                    )}
                  </div>
                  
                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                      Trust Level *
                    </label>
                    <select
                      value={formData.trust_level}
                      onChange={(e) => {
                        console.log('🔧 TRUST LEVEL SELECTED:', e.target.value);
                        setFormData({...formData, trust_level: e.target.value});
                      }}
                      required
                      style={{
                        width: '100%',
                        padding: '0.5rem',
                        border: '1px solid #ced4da',
                        borderRadius: '4px'
                      }}
                    >
                      <option value="">Select Trust Level</option>
                      {trustData.trustLevels.length === 0 && (
                        <option disabled>No trust levels available</option>
                      )}
                      {trustData.trustLevels.map(level => {
                        console.log('🔧 RENDERING TRUST LEVEL OPTION:', { id: level.id, name: level.name, level: level.level });
                        return (
                          <option key={level.id} value={level.level}>{level.name}</option>
                        );
                      })}
                    </select>
                  </div>
                  
                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                      Relationship Type
                    </label>
                    {modalMode === 'edit' ? (
                      <div style={{
                        width: '100%',
                        padding: '0.5rem',
                        border: '1px solid #e9ecef',
                        borderRadius: '4px',
                        backgroundColor: '#f8f9fa',
                        color: '#6c757d'
                      }}>
                        {formData.relationship_type?.charAt(0).toUpperCase() + formData.relationship_type?.slice(1) || 'Bilateral'}
                        <small style={{ display: 'block', fontSize: '0.875em', marginTop: '0.25rem' }}>
                          Relationship type cannot be changed when editing
                        </small>
                      </div>
                    ) : (
                      <select
                        value={formData.relationship_type}
                        onChange={(e) => setFormData({...formData, relationship_type: e.target.value})}
                        style={{
                          width: '100%',
                          padding: '0.5rem',
                          border: '1px solid #ced4da',
                          borderRadius: '4px'
                        }}
                      >
                        <option value="bilateral">Bilateral</option>
                        <option value="unilateral">Unilateral</option>
                      </select>
                    )}
                  </div>
                  
                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                      Notes
                    </label>
                    <textarea
                      value={formData.notes}
                      onChange={(e) => setFormData({...formData, notes: e.target.value})}
                      rows={3}
                      placeholder="Optional notes about this relationship..."
                      style={{
                        width: '100%',
                        padding: '0.5rem',
                        border: '1px solid #ced4da',
                        borderRadius: '4px',
                        resize: 'vertical'
                      }}
                    />
                  </div>
                </>
              )}
              
              {modalType === 'group' && (
                <>
                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                      Group Name *
                    </label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      required
                      placeholder="Enter group name..."
                      style={{
                        width: '100%',
                        padding: '0.5rem',
                        border: '1px solid #ced4da',
                        borderRadius: '4px'
                      }}
                    />
                  </div>
                  
                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                      Description
                    </label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData({...formData, description: e.target.value})}
                      rows={3}
                      placeholder="Describe the purpose of this group..."
                      style={{
                        width: '100%',
                        padding: '0.5rem',
                        border: '1px solid #ced4da',
                        borderRadius: '4px',
                        resize: 'vertical'
                      }}
                    />
                  </div>
                  
                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                      Group Type
                    </label>
                    <select
                      value={formData.group_type}
                      onChange={(e) => setFormData({...formData, group_type: e.target.value})}
                      style={{
                        width: '100%',
                        padding: '0.5rem',
                        border: '1px solid #ced4da',
                        borderRadius: '4px'
                      }}
                    >
                      <option value="industry">Industry</option>
                      <option value="regional">Regional</option>
                      <option value="security">Security</option>
                      <option value="research">Research</option>
                    </select>
                  </div>
                  
                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                      Trust Level (Optional)
                    </label>
                    <select
                      value={formData.trust_level}
                      onChange={(e) => setFormData({...formData, trust_level: e.target.value})}
                      style={{
                        width: '100%',
                        padding: '0.5rem',
                        border: '1px solid #ced4da',
                        borderRadius: '4px'
                      }}
                    >
                      <option value="">Default (Public)</option>
                      {trustData.trustLevels.map(level => (
                        <option key={level.id} value={level.level}>{level.name}</option>
                      ))}
                    </select>
                    <small style={{ color: '#6c757d', fontSize: '0.875em', display: 'block', marginTop: '0.25rem' }}>
                      If not selected, the group will use Public trust level by default
                    </small>
                  </div>
                  
                  <div style={{ marginBottom: '1rem', display: 'flex', gap: '1rem' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <input
                        type="checkbox"
                        checked={formData.is_public}
                        onChange={(e) => setFormData({...formData, is_public: e.target.checked})}
                      />
                      Public Group
                    </label>
                    
                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <input
                        type="checkbox"
                        checked={formData.requires_approval}
                        onChange={(e) => setFormData({...formData, requires_approval: e.target.checked})}
                      />
                      Requires Approval
                    </label>
                  </div>
                </>
              )}
              
              {modalType === 'org-to-group' && (
                <>
                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                      Select Organization *
                    </label>
                    <select
                      value={formData.selected_organization}
                      onChange={(e) => setFormData({...formData, selected_organization: e.target.value})}
                      required
                      style={{
                        width: '100%',
                        padding: '0.5rem',
                        border: '1px solid #ced4da',
                        borderRadius: '4px'
                      }}
                    >
                      <option value="">Select Organization</option>
                      {trustData.organizations.map(org => (
                        <option key={org.id} value={org.id}>{org.name}</option>
                      ))}
                    </select>
                  </div>
                  
                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                      Select Trust Group *
                    </label>
                    <select
                      value={formData.selected_group}
                      onChange={(e) => setFormData({...formData, selected_group: e.target.value})}
                      required
                      style={{
                        width: '100%',
                        padding: '0.5rem',
                        border: '1px solid #ced4da',
                        borderRadius: '4px'
                      }}
                    >
                      <option value="">Select Trust Group</option>
                      {trustData.groups.map(group => (
                        <option key={group.id} value={group.id}>{group.name}</option>
                      ))}
                    </select>
                  </div>
                </>
              )}
              
              <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end', marginTop: '1.5rem' }}>
                <button
                  type="button"
                  onClick={closeModal}
                  disabled={submitting}
                  style={{
                    padding: '0.5rem 1rem',
                    backgroundColor: '#6c757d',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: submitting ? 'not-allowed' : 'pointer'
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  style={{
                    padding: '0.5rem 1rem',
                    backgroundColor: '#007bff',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: submitting ? 'not-allowed' : 'pointer'
                  }}
                >
                  {submitting ? 'Saving...' : (modalMode === 'add' ? 'Create' : 'Update')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Actions Popup */}
      {showActionsPopup && selectedItemForActions && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1001
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '2rem',
            borderRadius: '12px',
            minWidth: '300px',
            maxWidth: '400px',
            boxShadow: '0 10px 25px rgba(0,0,0,0.1)'
          }}>
            <div style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ 
                margin: '0 0 0.5rem 0', 
                color: '#333',
                fontSize: '1.25rem',
                wordBreak: 'break-word',
                lineHeight: '1.3'
              }}>
                {activeTab === 'relationships' ? 
                  `${selectedItemForActions.source_organization?.name || selectedItemForActions.source_organization_name || 'Unknown'} → ${selectedItemForActions.target_organization?.name || selectedItemForActions.target_organization_name || 'Unknown'}` :
                  selectedItemForActions.name
                }
              </h3>
              <div style={{ 
                color: '#666', 
                fontSize: '0.875rem',
                marginBottom: '0.5rem'
              }}>
                {activeTab === 'relationships' ? 
                  `Trust Level: ${selectedItemForActions.trust_level?.name || selectedItemForActions.trust_level?.level || 'Unknown'}` :
                  selectedItemForActions.description
                }
              </div>
              <div style={{ 
                color: '#666', 
                fontSize: '0.875rem',
                display: 'flex',
                gap: '0.5rem',
                alignItems: 'center'
              }}>
                {activeTab === 'relationships' ? (
                  <>
                    <span style={{
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.75rem',
                      fontWeight: '600',
                      textTransform: 'uppercase',
                      backgroundColor: selectedItemForActions.relationship_type === 'BILATERAL' ? '#d4edda' : '#fff3cd',
                      color: selectedItemForActions.relationship_type === 'BILATERAL' ? '#155724' : '#856404'
                    }}>
                      {selectedItemForActions.relationship_type}
                    </span>
                    <span style={{
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.75rem',
                      fontWeight: '600',
                      textTransform: 'uppercase',
                      backgroundColor: selectedItemForActions.status === 'active' ? '#d4edda' : selectedItemForActions.status === 'pending' ? '#fff3cd' : '#f8d7da',
                      color: selectedItemForActions.status === 'active' ? '#155724' : selectedItemForActions.status === 'pending' ? '#856404' : '#721c24'
                    }}>
                      {selectedItemForActions.status}
                    </span>
                  </>
                ) : (
                  <>
                    <span style={{
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.75rem',
                      fontWeight: '600',
                      textTransform: 'uppercase',
                      backgroundColor: selectedItemForActions.group_type === 'SECURITY' ? '#d4edda' : '#fff3cd',
                      color: selectedItemForActions.group_type === 'SECURITY' ? '#155724' : '#856404'
                    }}>
                      {selectedItemForActions.group_type}
                    </span>
                    <span style={{
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.75rem',
                      fontWeight: '600',
                      textTransform: 'uppercase',
                      backgroundColor: selectedItemForActions.is_public ? '#d4edda' : '#fff3cd',
                      color: selectedItemForActions.is_public ? '#155724' : '#856404'
                    }}>
                      {selectedItemForActions.is_public ? 'Public' : 'Private'}
                    </span>
                  </>
                )}
              </div>
            </div>
            
            <div style={{ 
              display: 'flex', 
              flexDirection: 'column',
              gap: '0.75rem'
            }}>
              <button
                onClick={() => {
                  closeActionsPopup();
                  handleAction('view');
                }}
                style={{
                  padding: '0.75rem 1rem',
                  backgroundColor: '#5D8AA8',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '0.875rem',
                  fontWeight: '500',
                  transition: 'all 0.2s ease',
                  textAlign: 'left'
                }}
                onMouseEnter={(e) => e.target.style.backgroundColor = '#4A7088'}
                onMouseLeave={(e) => e.target.style.backgroundColor = '#5D8AA8'}
              >
                View Details
              </button>
              
              <button
                onClick={() => {
                  closeActionsPopup();
                  handleAction('edit');
                }}
                style={{
                  padding: '0.75rem 1rem',
                  backgroundColor: '#5D8AA8',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '0.875rem',
                  fontWeight: '500',
                  transition: 'all 0.2s ease',
                  textAlign: 'left'
                }}
                onMouseEnter={(e) => e.target.style.backgroundColor = '#4A7088'}
                onMouseLeave={(e) => e.target.style.backgroundColor = '#5D8AA8'}
              >
                Edit Details
              </button>
              
              {activeTab === 'relationships' && selectedItemForActions.status !== 'active' && (
                <button
                  onClick={() => {
                    closeActionsPopup();
                    handleAction('activate');
                  }}
                  style={{
                    padding: '0.75rem 1rem',
                    backgroundColor: '#5D8AA8',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    transition: 'all 0.2s ease',
                    textAlign: 'left'
                  }}
                  onMouseEnter={(e) => e.target.style.backgroundColor = '#4A7088'}
                  onMouseLeave={(e) => e.target.style.backgroundColor = '#5D8AA8'}
                >
                  Activate Relationship
                </button>
              )}
              
              {activeTab === 'relationships' && selectedItemForActions.status === 'active' && (
                <button
                  onClick={() => {
                    closeActionsPopup();
                    handleAction('suspend');
                  }}
                  style={{
                    padding: '0.75rem 1rem',
                    backgroundColor: 'white',
                    color: '#5D8AA8',
                    border: '2px solid #5D8AA8',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    transition: 'all 0.2s ease',
                    textAlign: 'left'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.backgroundColor = '#5D8AA8';
                    e.target.style.color = 'white';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.backgroundColor = 'white';
                    e.target.style.color = '#5D8AA8';
                  }}
                >
                  Suspend Relationship
                </button>
              )}
              
              {activeTab === 'groups' && !isAdmin && (
                <button
                  onClick={() => {
                    closeActionsPopup();
                    handleAction('join');
                  }}
                  style={{
                    padding: '0.75rem 1rem',
                    backgroundColor: '#5D8AA8',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    transition: 'all 0.2s ease',
                    textAlign: 'left'
                  }}
                  onMouseEnter={(e) => e.target.style.backgroundColor = '#4A7088'}
                  onMouseLeave={(e) => e.target.style.backgroundColor = '#5D8AA8'}
                >
                  Join Group
                </button>
              )}
              
              {activeTab === 'groups' && (
                <button
                  onClick={() => {
                    closeActionsPopup();
                    handleAction('view_members');
                  }}
                  style={{
                    padding: '0.75rem 1rem',
                    backgroundColor: '#17a2b8',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    transition: 'all 0.2s ease',
                    textAlign: 'left'
                  }}
                  onMouseEnter={(e) => e.target.style.backgroundColor = '#138496'}
                  onMouseLeave={(e) => e.target.style.backgroundColor = '#17a2b8'}
                >
                  View Members
                </button>
              )}
              
              <button
                onClick={() => {
                  closeActionsPopup();
                  handleAction('delete');
                }}
                style={{
                  padding: '0.75rem 1rem',
                  backgroundColor: '#5D8AA8',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '0.875rem',
                  fontWeight: '500',
                  transition: 'all 0.2s ease',
                  textAlign: 'left'
                }}
                onMouseEnter={(e) => e.target.style.backgroundColor = '#4A7088'}
                onMouseLeave={(e) => e.target.style.backgroundColor = '#5D8AA8'}
              >
                Delete {activeTab === 'relationships' ? 'Relationship' : 'Group'}
              </button>
            </div>
            
            <div style={{ 
              marginTop: '1.5rem',
              paddingTop: '1rem',
              borderTop: '1px solid #e9ecef'
            }}>
              <button
                onClick={closeActionsPopup}
                style={{
                  padding: '0.5rem 1rem',
                  border: '1px solid #ddd',
                  backgroundColor: 'white',
                  color: '#666',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '0.875rem',
                  width: '100%'
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Group Members Modal */}
      {showMembersModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '8px',
            padding: '1.5rem',
            width: '90%',
            maxWidth: '600px',
            maxHeight: '80vh',
            overflowY: 'auto'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3 style={{ margin: 0 }}>
                Group Members: {selectedGroup?.name}
              </h3>
              <button
                onClick={closeMembersModal}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '1.5rem',
                  cursor: 'pointer',
                  color: '#6c757d'
                }}
              >
                ×
              </button>
            </div>
            
            {membersLoading ? (
              <div style={{ textAlign: 'center', padding: '2rem' }}>
                <div>Loading members...</div>
              </div>
            ) : groupMembers.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '2rem', color: '#6c757d' }}>
                <p>No members found in this group.</p>
              </div>
            ) : (
              <div>
                <div style={{ marginBottom: '1rem', color: '#6c757d' }}>
                  Total Members: {groupMembers.length}
                </div>
                
                {groupMembers.map((member) => (
                  <div
                    key={member.id}
                    style={{
                      padding: '1rem',
                      border: '1px solid #e9ecef',
                      borderRadius: '6px',
                      marginBottom: '0.5rem',
                      backgroundColor: '#f8f9fa'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontWeight: '600', marginBottom: '0.25rem' }}>
                          {member.name}
                        </div>
                        <div style={{ fontSize: '0.875rem', color: '#6c757d' }}>
                          {member.domain && <span>Domain: {member.domain}</span>}
                          {member.organization_type && <span> • Type: {member.organization_type}</span>}
                        </div>
                        <div style={{ fontSize: '0.75rem', color: '#6c757d', marginTop: '0.25rem' }}>
                          {member.joined_at && <span>Joined: {new Date(member.joined_at).toLocaleDateString()}</span>}
                          {member.approved_by && <span> • Approved by: {member.approved_by}</span>}
                        </div>
                      </div>
                      <div>
                        <span style={{
                          padding: '0.25rem 0.5rem',
                          borderRadius: '4px',
                          fontSize: '0.75rem',
                          fontWeight: '600',
                          textTransform: 'uppercase',
                          backgroundColor: member.membership_type === 'administrator' ? '#d4edda' : '#e2e3e5',
                          color: member.membership_type === 'administrator' ? '#155724' : '#495057'
                        }}>
                          {member.membership_type}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Confirmation Modal */}
      {showConfirmation && (
        <ConfirmationModal
          isOpen={showConfirmation}
          onClose={() => setShowConfirmation(false)}
          onConfirm={confirmationData?.action}
          title={confirmationData?.title}
          message={confirmationData?.message}
          confirmText={confirmationData?.confirmText}
          isDestructive={confirmationData?.isDestructive}
          actionType={confirmationData?.actionType}
        />
      )}

      {/* Detail View Modal */}
      {showDetailModal && detailItem && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            padding: '2rem',
            width: '90%',
            maxWidth: '600px',
            maxHeight: '90vh',
            overflowY: 'auto',
            boxShadow: '0 10px 25px rgba(0,0,0,0.1)'
          }}>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              marginBottom: '1.5rem'
            }}>
              <h2 style={{ margin: '0', color: '#333' }}>
                {activeTab === 'relationships' ? 'Trust Relationship Details' : 'Trust Group Details'}
              </h2>
              <button
                onClick={() => setShowDetailModal(false)}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '1.5rem',
                  cursor: 'pointer',
                  color: '#666'
                }}
              >
                ×
              </button>
            </div>
            
            {activeTab === 'relationships' ? (
              <div>
                <div style={{ marginBottom: '1.5rem' }}>
                  <h3 style={{ color: '#5D8AA8', marginBottom: '1rem' }}>Relationship Overview</h3>
                  <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: '1fr 1fr', 
                    gap: '1rem',
                    marginBottom: '1rem'
                  }}>
                    <div>
                      <strong>Source Organization:</strong><br/>
                      {detailItem.source_organization?.name || detailItem.source_organization_name || 'Unknown'}
                    </div>
                    <div>
                      <strong>Target Organization:</strong><br/>
                      {detailItem.target_organization?.name || detailItem.target_organization_name || 'Unknown'}
                    </div>
                    <div>
                      <strong>Trust Level:</strong><br/>
                      <span style={{
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                        fontSize: '0.875rem',
                        fontWeight: '600',
                        backgroundColor: detailItem.trust_level?.name === 'HIGH' ? '#d4edda' : detailItem.trust_level?.name === 'MEDIUM' ? '#fff3cd' : '#f8f9fa',
                        color: detailItem.trust_level?.name === 'HIGH' ? '#155724' : detailItem.trust_level?.name === 'MEDIUM' ? '#856404' : '#495057'
                      }}>
                        {detailItem.trust_level?.name || detailItem.trust_level?.level || 'Unknown'}
                      </span>
                    </div>
                    <div>
                      <strong>Status:</strong><br/>
                      <span style={{
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                        fontSize: '0.875rem',
                        fontWeight: '600',
                        backgroundColor: detailItem.status === 'active' ? '#d4edda' : detailItem.status === 'pending' ? '#fff3cd' : '#f8d7da',
                        color: detailItem.status === 'active' ? '#155724' : detailItem.status === 'pending' ? '#856404' : '#721c24'
                      }}>
                        {detailItem.status}
                      </span>
                    </div>
                    <div>
                      <strong>Relationship Type:</strong><br/>
                      {detailItem.relationship_type}
                    </div>
                    <div>
                      <strong>Created:</strong><br/>
                      {detailItem.created_at ? new Date(detailItem.created_at).toLocaleDateString() : 'N/A'}
                    </div>
                  </div>
                  
                  {detailItem.notes && (
                    <div style={{ marginTop: '1rem' }}>
                      <strong>Notes:</strong><br/>
                      <div style={{ 
                        padding: '0.75rem',
                        backgroundColor: '#f8f9fa',
                        borderRadius: '4px',
                        marginTop: '0.5rem',
                        fontStyle: 'italic'
                      }}>
                        {detailItem.notes}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div>
                <div style={{ marginBottom: '1.5rem' }}>
                  <h3 style={{ color: '#5D8AA8', marginBottom: '1rem' }}>Group Overview</h3>
                  <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: '1fr 1fr', 
                    gap: '1rem',
                    marginBottom: '1rem'
                  }}>
                    <div>
                      <strong>Group Name:</strong><br/>
                      {detailItem.name}
                    </div>
                    <div>
                      <strong>Group Type:</strong><br/>
                      <span style={{
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                        fontSize: '0.875rem',
                        fontWeight: '600',
                        backgroundColor: detailItem.group_type === 'SECURITY' ? '#d4edda' : '#fff3cd',
                        color: detailItem.group_type === 'SECURITY' ? '#155724' : '#856404'
                      }}>
                        {detailItem.group_type}
                      </span>
                    </div>
                    <div>
                      <strong>Visibility:</strong><br/>
                      <span style={{
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                        fontSize: '0.875rem',
                        fontWeight: '600',
                        backgroundColor: detailItem.is_public ? '#d4edda' : '#fff3cd',
                        color: detailItem.is_public ? '#155724' : '#856404'
                      }}>
                        {detailItem.is_public ? 'Public' : 'Private'}
                      </span>
                    </div>
                    <div>
                      <strong>Member Count:</strong><br/>
                      {detailItem.member_count || 0}
                    </div>
                    <div>
                      <strong>Requires Approval:</strong><br/>
                      {detailItem.requires_approval ? 'Yes' : 'No'}
                    </div>
                    <div>
                      <strong>Created:</strong><br/>
                      {detailItem.created_at ? new Date(detailItem.created_at).toLocaleDateString() : 'N/A'}
                    </div>
                  </div>
                  
                  <div style={{ marginTop: '1rem' }}>
                    <strong>Description:</strong><br/>
                    <div style={{ 
                      padding: '0.75rem',
                      backgroundColor: '#f8f9fa',
                      borderRadius: '4px',
                      marginTop: '0.5rem'
                    }}>
                      {detailItem.description || 'No description provided'}
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <div style={{ 
              display: 'flex', 
              justifyContent: 'flex-end',
              marginTop: '2rem',
              paddingTop: '1rem',
              borderTop: '1px solid #e9ecef'
            }}>
              <button
                onClick={() => setShowDetailModal(false)}
                style={{
                  padding: '0.5rem 1rem',
                  backgroundColor: '#6c757d',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer'
                }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default TrustManagement;