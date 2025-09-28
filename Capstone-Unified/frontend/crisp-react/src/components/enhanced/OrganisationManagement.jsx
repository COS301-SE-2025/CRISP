import React, { useState, useEffect, useMemo } from 'react';
import { getOrganizations, createOrganization, updateOrganization, deactivateOrganization, reactivateOrganization, deleteOrganizationPermanently, getOrganizationDetails, getOrganizationTypes, getOrganizationTrustRelationships, getOrganizationTrustGroups } from '../../api.js';
import LoadingSpinner from './LoadingSpinner.jsx';
import ConfirmationModal from './ConfirmationModal.jsx';
import Pagination from './Pagination.jsx';
import refreshManager from '../../utils/RefreshManager.js';

import * as api from '../../api.js';

const OrganisationManagement = ({ active = true, initialSection = null, navigationState, setNavigationState }) => {
  const [organizations, setOrganizations] = useState([]); // This will be filtered/paginated organizations
  const [organizationTypes, setOrganizationTypes] = useState(['educational', 'government', 'private']);
  const [trustRelationships, setTrustRelationships] = useState([]);
  const [trustGroups, setTrustGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(() => {
    if (initialSection === 'create') return true;
    const urlParams = new URLSearchParams(window.location.search);
    const section = urlParams.get('section');
    return section === 'create';
  });
  const [modalMode, setModalMode] = useState(() => {
    if (initialSection === 'create') return 'add';
    const urlParams = new URLSearchParams(window.location.search);
    const section = urlParams.get('section');
    return section === 'create' ? 'add' : 'add';
  });
  const [selectedOrganization, setSelectedOrganization] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [modalLoading, setModalLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [operationLoading, setOperationLoading] = useState(false);
  const [showActionsPopup, setShowActionsPopup] = useState(false);
  const [selectedOrganizationForActions, setSelectedOrganizationForActions] = useState(null);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [confirmationData, setConfirmationData] = useState(null);
  // Trust relationship modal state
  const [showTrustModal, setShowTrustModal] = useState(false);
  const [selectedOrgForTrust, setSelectedOrgForTrust] = useState(null);
  const [trustModalMode, setTrustModalMode] = useState('view'); // 'view' or 'manage'
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);
  const [allOrganizations, setAllOrganizations] = useState([]);
  const [formData, setFormData] = useState({
    name: '',
    domain: '',
    contact_email: '',
    description: '',
    website: '',
    organization_type: 'educational',
    primary_user: {
      username: '',
      email: '',
      password: '',
      first_name: '',
      last_name: ''
    }
  });

  // Real-time validation state
  const [validationErrors, setValidationErrors] = useState({});
  const [validationChecking, setValidationChecking] = useState({});
  const [isFormValid, setIsFormValid] = useState(false);

  const loadOrganizationTypes = async () => {
    try {
      const response = await api.getOrganizationTypes();
      console.log('Organization types response:', response);
      
      if (response.success && response.data?.organization_types) {
        const types = response.data.organization_types.map(type => type.value);
        setOrganizationTypes(types);
        console.log('Loaded organization types:', types);
      }
    } catch (err) {
      console.error('Failed to load organization types:', err);
      // Keep default types if API fails
    }
  };

  const loadTrustRelationships = async () => {
    try {
      const response = await api.getTrustRelationships();
      
      let trustRelationshipsData = [];
      
      // Extract data from the correct response structure
      if (response.results && response.results.trusts) {
        trustRelationshipsData = response.results.trusts;
      } else if (response.success && response.trusts) {
        trustRelationshipsData = response.trusts;
      } else if (response.data?.trusts) {
        trustRelationshipsData = response.data.trusts;
      } else if (response.trusts) {
        trustRelationshipsData = response.trusts;
      } else if (Array.isArray(response)) {
        trustRelationshipsData = response;
      } else if (response.data && Array.isArray(response.data)) {
        trustRelationshipsData = response.data;
      }
      
      setTrustRelationships(trustRelationshipsData);
    } catch (err) {
      console.error('Failed to load trust relationships:', err);
      setTrustRelationships([]);
    }
  };

  const loadTrustGroups = async () => {
    try {
      console.log('Loading trust groups...');
      const response = await api.getTrustGroups();
      console.log('Trust groups response:', response);
      
      let trustGroupsData = [];
      if (response.success && response.community_trusts) {
        trustGroupsData = response.community_trusts;
      } else if (response.data?.community_trusts) {
        trustGroupsData = response.data.community_trusts;
      } else if (response.community_trusts) {
        trustGroupsData = response.community_trusts;
      } else if (Array.isArray(response)) {
        trustGroupsData = response;
      }
      
      console.log('Loaded trust groups:', trustGroupsData);
      setTrustGroups(trustGroupsData);
    } catch (err) {
      console.error('Failed to load trust groups:', err);
      setTrustGroups([]);
    }
  };

  useEffect(() => {
    if (active) {
      loadOrganizations();
      loadOrganizationTypes();
      loadTrustRelationships();
      loadTrustGroups();

      // Subscribe to RefreshManager for cross-component updates
      refreshManager.subscribe('organizations', () => {
        console.log('🔄 RefreshManager: Refreshing organization data');
        loadOrganizations();
        loadTrustRelationships();
        loadTrustGroups();
      }, {
        backgroundRefresh: true,
        isVisible: () => active
      });

      return () => {
        refreshManager.unsubscribe('organizations');
      };
    }
  }, [active]);

  useEffect(() => {
    if (initialSection === 'create') {
      console.log('OrganisationManagement: Opening create modal from prop');
      setShowModal(true);
      setModalMode('add');
    } else if (initialSection === 'roles' || initialSection === 'passwords') {
      console.log('OrganisationManagement: Section from prop:', initialSection);
      setShowModal(false);
    }
  }, [initialSection]);

  useEffect(() => {
    const handleUrlChange = () => {
      const urlParams = new URLSearchParams(window.location.search);
      const section = urlParams.get('section');
      
      if (section === 'create') {
        setShowModal(true);
        setModalMode('add');
      }
    };

    window.addEventListener('popstate', handleUrlChange);
    
    return () => {
      window.removeEventListener('popstate', handleUrlChange);
    };
  }, []);

  // Handle navigation state for search functionality
  useEffect(() => {
    if (navigationState && navigationState.triggerModal === 'viewOrganization') {
      console.log('🏢 OrganisationManagement: Handling search navigation:', navigationState);
      const orgData = navigationState.modalParams?.organization;
      if (orgData) {
        console.log('🏢 OrganisationManagement: Opening organization modal for:', orgData);
        // Use handleViewOrganization to properly populate form data
        handleViewOrganization(orgData.id);

        // Clear navigation state
        if (setNavigationState) {
          setNavigationState({ triggerModal: null, modalParams: {} });
        }
      }
    }
  }, [navigationState, setNavigationState]);

  const loadOrganizations = async () => {
    try {
      setLoading(true);
      setError(null);
      await new Promise(resolve => setTimeout(resolve, 1000));
      const response = await api.getOrganizations();
      console.log('Organizations API response:', response);
      console.log('Full response object:', JSON.stringify(response, null, 2));
      
      let organizationsData = [];
      if (response.results && response.results.organizations) {
        // Django REST Framework pagination with custom wrapper
        organizationsData = response.results.organizations;
      } else if (response.data && response.data.organizations) {
        organizationsData = response.data.organizations;
      } else if (response.organizations) {
        organizationsData = response.organizations;
      } else if (response.data && Array.isArray(response.data)) {
        organizationsData = response.data;
      } else if (Array.isArray(response)) {
        organizationsData = response;
      }
      
      console.log('Extracted organizations data:', organizationsData);
      console.log('Organizations data length:', organizationsData.length);
      const orgsList = Array.isArray(organizationsData) ? organizationsData : [];
      setAllOrganizations(orgsList);
      setOrganizations(orgsList); // Initially show all organizations
    } catch (err) {
      console.error('Failed to load organizations:', err);
      setError('Failed to load organizations: ' + err.message);
      setOrganizations([]);
    } finally {
      setLoading(false);
    }
  };

  // Memoized filtered organizations
  const filteredOrganizations = useMemo(() => {
    let filtered = [...allOrganizations];

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(org =>
        org.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        org.domain?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        org.contact_email?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply type filter
    if (typeFilter) {
      filtered = filtered.filter(org => org.organization_type === typeFilter);
    }

    return filtered;
  }, [allOrganizations, searchTerm, typeFilter]);

  // Memoized paginated organizations
  const paginatedOrganizations = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return filteredOrganizations.slice(startIndex, endIndex);
  }, [filteredOrganizations, currentPage, itemsPerPage]);

  // Update organizations state when pagination changes
  useEffect(() => {
    setOrganizations(paginatedOrganizations);
  }, [paginatedOrganizations]);

  // Handle page change
  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  // Handle items per page change
  const handleItemsPerPageChange = (newItemsPerPage) => {
    setItemsPerPage(newItemsPerPage);
    setCurrentPage(1); // Reset to first page
  };

  const handleAddOrganization = () => {
    setModalMode('add');
    setSelectedOrganization(null);
    setError(null); // Clear any previous errors
    setValidationErrors({}); // Clear validation errors
    setValidationChecking({}); // Clear validation checking states
    setIsFormValid(false); // Start with invalid form
    setFormData({
      name: '',
      domain: '',
      contact_email: '',
      description: '',
      website: '',
      organization_type: 'educational',
      primary_user: {
        username: '',
        email: '',
        password: '',
        first_name: '',
        last_name: ''
      }
    });
    setShowModal(true);
  };

  const handleEditOrganization = async (organizationId) => {
    console.log('handleEditOrganization called with ID:', organizationId);
    try {
      setModalLoading(true);
      setError(null); // Clear any previous errors
      await new Promise(resolve => setTimeout(resolve, 800));
      const response = await api.getOrganizationDetails(organizationId);
      console.log('Edit organization response:', response);
      
      let organization = null;
      if (response.success && response.data?.organization) {
        organization = response.data.organization;
      } else if (response.data?.organization) {
        organization = response.data.organization;  
      } else if (response.organization) {
        organization = response.organization;
      } else if (response.data && typeof response.data === 'object' && response.data.name) {
        organization = response.data;
      } else {
        console.error('Unable to extract organization from response:', response);
        throw new Error('Invalid response format');
      }
      console.log('Edit organization data:', organization);
      
      if (!organization || !organization.name) {
        console.error('Organization data not found or invalid in response. Full response:', response);
        throw new Error('Organization data not found or invalid in response');
      }
      
      setModalMode('edit');
      setSelectedOrganization(organization);
      const formDataToSet = {
        name: organization.name || '',
        domain: organization.domain || '',
        contact_email: organization.contact_email || '',
        description: organization.description || '',
        website: organization.website || '',
        organization_type: organization.organization_type || 'educational',
        primary_user: {
          username: '',
          email: '',
          password: '',
          first_name: '',
          last_name: ''
        }
      };
      
      console.log('Setting form data for edit:', formDataToSet);
      setFormData(formDataToSet);
      setValidationErrors({}); // Clear validation errors
      setValidationChecking({}); // Clear validation checking states
      setIsFormValid(true); // Edit starts with valid data
      setShowModal(true);
    } catch (err) {
      console.error('Error in handleEditOrganization:', err);
      setError('Failed to load organization details: ' + (err.message || err));
    } finally {
      setModalLoading(false);
    }
  };

  const handleViewOrganization = async (organizationId) => {
    console.log('handleViewOrganization called with ID:', organizationId);
    try {
      setModalLoading(true);
      setError(null); // Clear any previous errors
      await new Promise(resolve => setTimeout(resolve, 800));
      const response = await api.getOrganizationDetails(organizationId);
      console.log('View organization response:', response);
      
      let organization = null;
      if (response.success && response.data?.organization) {
        organization = response.data.organization;
      } else if (response.data?.organization) {
        organization = response.data.organization;  
      } else if (response.organization) {
        organization = response.organization;
      } else if (response.data && typeof response.data === 'object' && response.data.name) {
        organization = response.data;
      } else {
        console.error('Unable to extract organization from response:', response);
        throw new Error('Invalid response format');
      }
      console.log('View organization data:', organization);
      
      if (!organization || !organization.name) {
        console.error('Organization data not found or invalid in response. Full response:', response);
        throw new Error('Organization data not found or invalid in response');
      }
      
      setModalMode('view');
      setSelectedOrganization(organization);
      const formDataToSet = {
        name: organization.name || '',
        domain: organization.domain || '',
        contact_email: organization.contact_email || '',
        description: organization.description || '',
        website: organization.website || '',
        organization_type: organization.organization_type || 'educational',
        primary_user: {
          username: '',
          email: '',
          password: '',
          first_name: '',
          last_name: ''
        }
      };
      
      console.log('Setting form data for view:', formDataToSet);
      setFormData(formDataToSet);
      setModalMode('view');
      setShowModal(true);
    } catch (err) {
      console.error('Error in handleViewOrganization:', err);
      setError('Failed to load organization details: ' + (err.message || err));
    } finally {
      setModalLoading(false);
    }
  };

  const handleDeleteOrganization = (organizationId, organizationName) => {
    setConfirmationData({
      title: 'Deactivate Organization',
      message: `Are you sure you want to deactivate organisation "${organizationName}"?`,
      confirmText: 'Deactivate',
      isDestructive: true,
      actionType: 'deactivate',
      action: async () => {
        try {
          setOperationLoading(true);
          await new Promise(resolve => setTimeout(resolve, 800));
          await api.deactivateOrganization(organizationId, 'Deactivated by admin');
          loadOrganizations();
        } catch (err) {
          setError('Failed to deactivate organization: ' + err.message);
        } finally {
          setOperationLoading(false);
        }
      }
    });
    setShowConfirmation(true);
  };

  const handleReactivateOrganization = (organizationId, organizationName) => {
    setConfirmationData({
      title: 'Reactivate Organization',
      message: `Are you sure you want to reactivate organisation "${organizationName}"?`,
      confirmText: 'Reactivate',
      isDestructive: false,
      actionType: 'reactivate',
      action: async () => {
        try {
          setOperationLoading(true);
          await new Promise(resolve => setTimeout(resolve, 800));
          await api.reactivateOrganization(organizationId, 'Reactivated by admin');
          loadOrganizations();
        } catch (err) {
          setError('Failed to reactivate organization: ' + err.message);
        } finally {
          setOperationLoading(false);
        }
      }
    });
    setShowConfirmation(true);
  };

  const handlePermanentDeleteOrganization = (organizationId, organizationName) => {
    setConfirmationData({
      title: 'Permanently Delete Organization',
      message: `Are you sure you want to PERMANENTLY DELETE organization "${organizationName}"? This action cannot be undone.`,
      confirmText: 'Delete Permanently',
      isDestructive: true,
      actionType: 'delete',
      action: async () => {
        try {
          setOperationLoading(true);
          await new Promise(resolve => setTimeout(resolve, 800));
          await api.deleteOrganizationPermanently(organizationId, 'Deleted by admin');
          loadOrganizations();
          // Ensure actions popup is closed after successful deletion
          setShowActionsPopup(false);
          setSelectedOrganizationForActions(null);
        } catch (err) {
          setError('Failed to delete organization: ' + err.message);
        } finally {
          setOperationLoading(false);
        }
      }
    });
    setShowConfirmation(true);
  };

  // Real-time validation functions
  const validateOrganizationName = async (name) => {
    if (!name || name.length === 0) {
      return { isValid: modalMode === 'view', message: modalMode === 'add' || modalMode === 'edit' ? 'Organization name is required' : '' };
    }
    
    if (name.length < 2) {
      return { isValid: false, message: 'Organization name must be at least 2 characters' };
    }
    
    if (name.length > 100) {
      return { isValid: false, message: 'Organization name cannot exceed 100 characters' };
    }
    
    // Check if organization name exists (only for new organizations or when name changes)
    if (modalMode === 'add' || (modalMode === 'edit' && selectedOrganization?.name !== name)) {
      const existingOrg = allOrganizations.find(org => org.name.toLowerCase() === name.toLowerCase());
      if (existingOrg) {
        return { isValid: false, message: 'Organization name already exists. Please choose a different name.' };
      }
    }
    
    return { isValid: true, message: '' };
  };

  const validateDomain = (domain) => {
    if (!domain || domain.length === 0) {
      return { isValid: true, message: '' }; // Domain is optional
    }
    
    // Basic domain validation
    const domainRegex = /^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?\.[a-zA-Z]{2,}$/;
    if (!domainRegex.test(domain)) {
      return { isValid: false, message: 'Please enter a valid domain (e.g., university.edu)' };
    }
    
    // Check if domain exists (only for new organizations or when domain changes)
    if (modalMode === 'add' || (modalMode === 'edit' && selectedOrganization?.domain !== domain)) {
      const existingOrg = allOrganizations.find(org => org.domain && org.domain.toLowerCase() === domain.toLowerCase());
      if (existingOrg) {
        return { isValid: false, message: 'Domain already exists. Please use a different domain.' };
      }
    }
    
    return { isValid: true, message: '' };
  };

  const validateContactEmail = (email) => {
    if (!email || email.length === 0) {
      return { isValid: modalMode === 'view', message: modalMode === 'add' || modalMode === 'edit' ? 'Contact email is required' : '' };
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return { isValid: false, message: 'Please enter a valid email address' };
    }
    
    // Check if contact email exists (only for new organizations or when email changes)
    if (modalMode === 'add' || (modalMode === 'edit' && selectedOrganization?.contact_email !== email)) {
      const existingOrg = allOrganizations.find(org => org.contact_email && org.contact_email.toLowerCase() === email.toLowerCase());
      if (existingOrg) {
        return { isValid: false, message: 'Contact email already exists. Please use a different email.' };
      }
    }
    
    return { isValid: true, message: '' };
  };

  const validateAdminUsername = async (username) => {
    if (!username || username.length === 0) {
      return { isValid: modalMode !== 'add', message: modalMode === 'add' ? 'Username is required' : '' };
    }
    
    if (username.length < 3) {
      return { isValid: false, message: 'Username must be at least 3 characters' };
    }
    
    if (username.length > 30) {
      return { isValid: false, message: 'Username cannot exceed 30 characters' };
    }
    
    if (!/^[a-zA-Z0-9_]+$/.test(username)) {
      return { isValid: false, message: 'Username can only contain letters, numbers, and underscores' };
    }
    
    // For new organizations, check if username exists across all users
    if (modalMode === 'add') {
      // We need to check against existing users - we'll assume we have access to users list
      // This would typically require an API call or access to users from the parent component
      // For now, we'll do a basic validation
      const commonUsernames = ['admin', 'administrator', 'root', 'user', 'test'];
      if (commonUsernames.includes(username.toLowerCase())) {
        return { isValid: false, message: 'Username is not available. Please choose a different username.' };
      }
    }
    
    return { isValid: true, message: '' };
  };

  const validateAdminEmail = (email) => {
    if (!email || email.length === 0) {
      return { isValid: modalMode !== 'add', message: modalMode === 'add' ? 'Email is required' : '' };
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return { isValid: false, message: 'Please enter a valid email address' };
    }
    
    // Check if admin email is the same as contact email
    if (formData.contact_email && email.toLowerCase() === formData.contact_email.toLowerCase()) {
      return { isValid: false, message: 'Admin email cannot be the same as organization contact email.' };
    }
    
    return { isValid: true, message: '' };
  };

  const validateField = async (fieldName, value) => {
    let result = { isValid: true, message: '' };
    
    switch (fieldName) {
      case 'name':
        result = await validateOrganizationName(value);
        break;
      case 'domain':
        result = validateDomain(value);
        break;
      case 'contact_email':
        result = validateContactEmail(value);
        break;
      case 'primary_user.username':
        result = await validateAdminUsername(value);
        break;
      case 'primary_user.email':
        result = validateAdminEmail(value);
        break;
      case 'primary_user.first_name':
        if (modalMode === 'add' && (!value || value.length === 0)) {
          result = { isValid: false, message: 'First name is required' };
        } else if (value && value.length > 150) {
          result = { isValid: false, message: 'First name cannot exceed 150 characters' };
        }
        break;
      case 'primary_user.last_name':
        if (modalMode === 'add' && (!value || value.length === 0)) {
          result = { isValid: false, message: 'Last name is required' };
        } else if (value && value.length > 150) {
          result = { isValid: false, message: 'Last name cannot exceed 150 characters' };
        }
        break;
      case 'primary_user.password':
        if (modalMode === 'add' && (!value || value.length === 0)) {
          result = { isValid: false, message: 'Password is required for admin user' };
        } else if (value && value.length > 0 && value.length < 6) {
          result = { isValid: false, message: 'Password must be at least 6 characters' };
        }
        break;
    }
    
    return result;
  };

  // Update validation state and check overall form validity
  const updateValidation = async (fieldName, value) => {
    setValidationChecking(prev => ({ ...prev, [fieldName]: true }));
    
    const validation = await validateField(fieldName, value);
    
    setValidationErrors(prev => ({
      ...prev,
      [fieldName]: validation.message
    }));
    
    setValidationChecking(prev => ({ ...prev, [fieldName]: false }));
    
    // Check overall form validity
    const updatedErrors = { ...validationErrors, [fieldName]: validation.message };
    const hasErrors = Object.values(updatedErrors).some(error => error.length > 0);
    
    // Required fields check (skip for view mode)
    if (modalMode === 'view') {
      setIsFormValid(true);
      return;
    }
    
    const orgRequiredFieldsFilled = formData.name && formData.contact_email;
    const adminRequiredFieldsFilled = modalMode !== 'add' || (
      formData.primary_user.username && formData.primary_user.email && 
      formData.primary_user.first_name && formData.primary_user.last_name && 
      formData.primary_user.password
    );
    
    setIsFormValid(!hasErrors && orgRequiredFieldsFilled && adminRequiredFieldsFilled);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Show confirmation dialog
    const actionText = modalMode === 'add' ? 'create' : 'update';
    const orgName = modalMode === 'add' ? formData.name : selectedOrganization?.name;
    
    setConfirmationData({
      title: `${modalMode === 'add' ? 'Create' : 'Update'} Organization`,
      message: `Are you sure you want to ${actionText} organization "${orgName}"?`,
      confirmText: modalMode === 'add' ? 'Create Organization' : 'Update Organization',
      isDestructive: false,
      actionType: modalMode === 'add' ? 'default' : 'default',
      action: async () => {
        try {
          setSubmitting(true);
          await new Promise(resolve => setTimeout(resolve, 1000));
          
          if (modalMode === 'add') {
            console.log('Creating organization with data:', formData);
            await api.createOrganization(formData);
          } else if (modalMode === 'edit') {
            const updateData = { ...formData };
            delete updateData.primary_user;
            console.log('Updating organization with data:', updateData);
            console.log('Selected organization ID:', selectedOrganization.id);
            await api.updateOrganization(selectedOrganization.id, updateData);
          }
          setShowModal(false);
          setError(null);
          loadOrganizations();
        } catch (err) {
          console.error('Error in handleSubmit:', err);
          if (Array.isArray(err)) {
            setError(err.join(', '));
          } else if (typeof err === 'string') {
            setError(err);
          } else {
            setError('Failed to save organization: ' + (err.message || 'Unknown error'));
          }
        } finally {
          setSubmitting(false);
        }
      }
    });
    setShowConfirmation(true);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    console.log('Input change:', { name, value });
    
    if (name.startsWith('primary_user.')) {
      const field = name.substring(13);
      setFormData(prev => ({
        ...prev,
        primary_user: {
          ...prev.primary_user,
          [field]: value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
    
    // Trigger real-time validation
    if (modalMode !== 'view') {
      updateValidation(name, value);
      
      // Cross-validate contact email and admin email
      if (name === 'contact_email') {
        // Re-validate admin email when contact email changes
        updateValidation('primary_user.email', formData.primary_user.email);
      } else if (name === 'primary_user.email') {
        // Re-validate contact email when admin email changes  
        updateValidation('contact_email', formData.contact_email);
      }
    }
  };

  // Get total items for pagination
  const totalItems = filteredOrganizations.length;

  const handleOrganizationClick = (organization) => {
    console.log('Organization card clicked:', organization.name, organization.id);
    setSelectedOrganizationForActions(organization);
    setShowActionsPopup(true);
  };

  const closeActionsPopup = () => {
    setShowActionsPopup(false);
    setSelectedOrganizationForActions(null);
  };

  const handleViewTrustRelationships = async (organization) => {
    setSelectedOrgForTrust(organization);
    setTrustModalMode('view');
    setShowTrustModal(true);
    closeActionsPopup();
    
    // Reload trust relationships when opening the modal
    console.log('🔄 Reloading trust relationships for modal...');
    await loadTrustRelationships();
  };

  const handleManageTrustRelationships = (organization) => {
    setSelectedOrgForTrust(organization);
    setTrustModalMode('manage');
    setShowTrustModal(true);
    closeActionsPopup();
  };

  const closeTrustModal = () => {
    setShowTrustModal(false);
    setSelectedOrgForTrust(null);
    setTrustModalMode('view');
  };

  if (!active) return null;
  if (loading) return <LoadingSpinner fullscreen={true} />;
  if (error) return <div style={{ padding: '2rem', color: 'red' }}>{error}</div>;

  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif', position: 'relative' }}>
      {(operationLoading || submitting) && <LoadingSpinner fullscreen={true} />}
      <h1 style={{ marginBottom: '2rem', color: '#333' }}>Organisation Management</h1>
      
      {/* Controls */}
      <div style={{ 
        display: 'flex', 
        gap: '1rem', 
        marginBottom: '2rem',
        flexWrap: 'wrap',
        alignItems: 'center'
      }}>
        <input
          type="text"
          placeholder="Search organisations..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            padding: '0.5rem',
            border: '1px solid #ddd',
            borderRadius: '4px',
            minWidth: '200px',
            backgroundColor: 'white',
            color: '#666'
          }}
        />
        
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          style={{
            padding: '0.5rem',
            border: '1px solid #ddd',
            borderRadius: '4px',
            backgroundColor: 'white',
            color: '#666'
          }}
        >
          <option value="">All Types</option>
          {organizationTypes.map(type => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
        
        <button
          onClick={handleAddOrganization}
          style={{
            padding: '0.5rem 1rem',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Add Organisation
        </button>

        <div className="items-per-page">
          <label>
            Show:
            <select 
              value={itemsPerPage} 
              onChange={(e) => handleItemsPerPageChange(parseInt(e.target.value))}
            >
              <option value={5}>5</option>
              <option value={10}>10</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
            </select>
            items per page
          </label>
        </div>
      </div>

      {/* Hint Text */}
      <div style={{ 
        marginBottom: '1rem', 
        color: '#6c757d', 
        fontSize: '0.875rem',
        textAlign: 'center'
      }}>
        💡 Click on any organisation row to view available actions
      </div>

      {/* Organizations List */}
      <div style={{ 
        backgroundColor: 'white',
        borderRadius: '12px',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
        border: '1px solid #e9ecef'
      }}>
        {organizations.map(organization => (
          <div 
            key={organization.id} 
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              handleOrganizationClick(organization);
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
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '1rem',
                flexWrap: 'wrap'
              }}>
                <div style={{ fontWeight: '600', color: '#212529', fontSize: '1.1rem' }}>
                  {organization.name}
                </div>
                <div style={{ color: '#495057' }}>
                  {organization.domain || 'N/A'}
                </div>
                <span style={{
                  padding: '0.25rem 0.5rem',
                  borderRadius: '4px',
                  fontSize: '0.75rem',
                  fontWeight: '600',
                  textTransform: 'uppercase',
                  backgroundColor: organization.organization_type === 'educational' ? '#d4edda' : 
                                   organization.organization_type === 'government' ? '#fff3cd' : '#f8f9fa',
                  color: organization.organization_type === 'educational' ? '#155724' : 
                         organization.organization_type === 'government' ? '#856404' : '#495057'
                }}>
                  {organization.organization_type}
                </span>
                <span style={{
                  padding: '0.25rem 0.5rem',
                  borderRadius: '4px',
                  fontSize: '0.75rem',
                  fontWeight: '600',
                  textTransform: 'uppercase',
                  backgroundColor: organization.is_active ? '#d4edda' : '#f8d7da',
                  color: organization.is_active ? '#155724' : '#721c24'
                }}>
                  {organization.is_active ? 'Active' : 'Inactive'}
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
                <span>{organization.contact_email || 'No email'}</span>
                {organization.description && <span>{organization.description.substring(0, 50)}...</span>}
              </div>
              <div style={{ 
                marginTop: '0.5rem', 
                color: '#495057', 
                fontSize: '0.75rem',
                display: 'flex',
                gap: '1rem',
                flexWrap: 'wrap'
              }}>
                <span style={{
                  padding: '0.15rem 0.4rem',
                  borderRadius: '3px',
                  backgroundColor: '#e3f2fd',
                  color: '#1565c0'
                }}>
                  Trust Relationships: {trustRelationships.filter(tr => 
                    tr.source_organization?.id === organization.id || 
                    tr.target_organization?.id === organization.id
                  ).length}
                </span>
                <span style={{
                  padding: '0.15rem 0.4rem',
                  borderRadius: '3px',
                  backgroundColor: '#f3e5f5',
                  color: '#7b1fa2'
                }}>
                  Trust Groups: {trustGroups.filter(tg => 
                    tg.organizations?.some(org => org.id === organization.id) ||
                    tg.members?.some(member => member.organization_id === organization.id)
                  ).length}
                </span>
              </div>
            </div>
            <div style={{ 
              fontSize: '1.2rem', 
              color: '#6c757d',
              marginLeft: '1rem',
              transition: 'all 0.2s ease',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              backgroundColor: 'rgba(108, 117, 125, 0.1)'
            }}>
              →
            </div>
          </div>
        ))}
      </div>

      {organizations.length === 0 && allOrganizations.length > 0 && (
        <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
          No organisations found matching your criteria.
        </div>
      )}

      {allOrganizations.length === 0 && (
        <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
          No organisations available. Click "Add Organisation" to create the first organization.
        </div>
      )}

      {/* Pagination */}
      {allOrganizations.length > 0 && (
        <Pagination
          currentPage={currentPage}
          totalItems={totalItems}
          itemsPerPage={itemsPerPage}
          onPageChange={handlePageChange}
          showInfo={true}
          showJumpToPage={true}
        />
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
            padding: '2rem',
            borderRadius: '8px',
            maxWidth: '600px',
            width: '90%',
            maxHeight: '80vh',
            overflowY: 'auto'
          }}>
            <h2 style={{ marginBottom: '1.5rem', color: '#333' }}>
              {modalMode === 'add' ? 'Add New Organisation' : 
               modalMode === 'edit' ? 'Edit Organisation' : 'View Organisation'}
            </h2>
            
            {modalLoading ? (
              <LoadingSpinner size="medium" />
            ) : (
            <>
            {error && (
              <div style={{
                padding: '1rem',
                backgroundColor: '#f8d7da',
                color: '#721c24',
                borderRadius: '4px',
                marginBottom: '1rem',
                border: '1px solid #f5c6cb'
              }}>
                {error}
              </div>
            )}
            
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                  Organisation Name {!formData.name && modalMode === 'add' && <span style={{ color: 'red' }}>*</span>}
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  disabled={modalMode === 'view'}
                  required
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: `1px solid ${validationErrors.name ? '#dc3545' : '#ddd'}`,
                    borderRadius: '4px',
                    backgroundColor: modalMode === 'view' ? '#f8f9fa' : 'white',
                    color: '#333'
                  }}
                />
                {validationChecking.name && (
                  <div style={{ fontSize: '0.875rem', color: '#6c757d', marginTop: '0.25rem' }}>
                    Checking availability...
                  </div>
                )}
                {validationErrors.name && !validationChecking.name && (
                  <div style={{ fontSize: '0.875rem', color: '#dc3545', marginTop: '0.25rem' }}>
                    {validationErrors.name}
                  </div>
                )}
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                  Domain
                </label>
                <input
                  type="text"
                  name="domain"
                  value={formData.domain}
                  onChange={handleInputChange}
                  disabled={modalMode === 'view'}
                  placeholder="e.g., university.edu"
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: `1px solid ${validationErrors.domain ? '#dc3545' : '#ddd'}`,
                    borderRadius: '4px',
                    backgroundColor: modalMode === 'view' ? '#f8f9fa' : 'white',
                    color: '#333'
                  }}
                />
                {validationChecking.domain && (
                  <div style={{ fontSize: '0.875rem', color: '#6c757d', marginTop: '0.25rem' }}>
                    Checking availability...
                  </div>
                )}
                {validationErrors.domain && !validationChecking.domain && (
                  <div style={{ fontSize: '0.875rem', color: '#dc3545', marginTop: '0.25rem' }}>
                    {validationErrors.domain}
                  </div>
                )}
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                  Contact Email {!formData.contact_email && modalMode === 'add' && <span style={{ color: 'red' }}>*</span>}
                </label>
                <input
                  type="email"
                  name="contact_email"
                  value={formData.contact_email}
                  onChange={handleInputChange}
                  disabled={modalMode === 'view'}
                  required
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: `1px solid ${validationErrors.contact_email ? '#dc3545' : '#ddd'}`,
                    borderRadius: '4px',
                    backgroundColor: modalMode === 'view' ? '#f8f9fa' : 'white',
                    color: '#333'
                  }}
                />
                {validationChecking.contact_email && (
                  <div style={{ fontSize: '0.875rem', color: '#6c757d', marginTop: '0.25rem' }}>
                    Checking availability...
                  </div>
                )}
                {validationErrors.contact_email && !validationChecking.contact_email && (
                  <div style={{ fontSize: '0.875rem', color: '#dc3545', marginTop: '0.25rem' }}>
                    {validationErrors.contact_email}
                  </div>
                )}
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                  Organisation Type *
                </label>
                <select
                  name="organization_type"
                  value={formData.organization_type}
                  onChange={handleInputChange}
                  disabled={modalMode === 'view'}
                  required
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    backgroundColor: modalMode === 'view' ? '#f8f9fa' : 'white',
                    color: '#333'
                  }}
                >
                  {organizationTypes.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                  Description
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  disabled={modalMode === 'view'}
                  rows="3"
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    backgroundColor: modalMode === 'view' ? '#f8f9fa' : 'white',
                    color: '#333',
                    resize: 'vertical'
                  }}
                />
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                  Website
                </label>
                <input
                  type="url"
                  name="website"
                  value={formData.website}
                  onChange={handleInputChange}
                  disabled={modalMode === 'view'}
                  placeholder="https://www.example.com"
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    backgroundColor: modalMode === 'view' ? '#f8f9fa' : 'white',
                    color: '#333'
                  }}
                />
              </div>

              {modalMode === 'add' && (
                <div>
                  <h3 style={{ marginBottom: '1rem', color: '#333', borderTop: '1px solid #ddd', paddingTop: '1rem' }}>
                    Primary User (Administrator)
                  </h3>
                  
                  <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
                    <div style={{ flex: 1 }}>
                      <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                        Username {!formData.primary_user.username && <span style={{ color: 'red' }}>*</span>}
                      </label>
                      <input
                        type="text"
                        name="primary_user.username"
                        value={formData.primary_user.username}
                        onChange={handleInputChange}
                        required
                        pattern="[a-zA-Z0-9_]+"
                        title="Username can only contain letters, numbers, and underscores"
                        style={{
                          width: '100%',
                          padding: '0.5rem',
                          border: `1px solid ${validationErrors['primary_user.username'] ? '#dc3545' : '#ddd'}`,
                          borderRadius: '4px',
                          backgroundColor: 'white',
                          color: '#000'
                        }}
                      />
                      {validationChecking['primary_user.username'] && (
                        <div style={{ fontSize: '0.875rem', color: '#6c757d', marginTop: '0.25rem' }}>
                          Checking availability...
                        </div>
                      )}
                      {validationErrors['primary_user.username'] && !validationChecking['primary_user.username'] && (
                        <div style={{ fontSize: '0.875rem', color: '#dc3545', marginTop: '0.25rem' }}>
                          {validationErrors['primary_user.username']}
                        </div>
                      )}
                      <div style={{ fontSize: '0.875rem', color: '#666', marginTop: '0.25rem' }}>
                        Only letters, numbers, and underscores allowed (minimum 3 characters)
                      </div>
                    </div>
                    <div style={{ flex: 1 }}>
                      <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                        Email {!formData.primary_user.email && <span style={{ color: 'red' }}>*</span>}
                      </label>
                      <input
                        type="email"
                        name="primary_user.email"
                        value={formData.primary_user.email}
                        onChange={handleInputChange}
                        required
                        style={{
                          width: '100%',
                          padding: '0.5rem',
                          border: `1px solid ${validationErrors['primary_user.email'] ? '#dc3545' : '#ddd'}`,
                          borderRadius: '4px',
                          backgroundColor: 'white',
                          color: '#000'
                        }}
                      />
                      {validationErrors['primary_user.email'] && (
                        <div style={{ fontSize: '0.875rem', color: '#dc3545', marginTop: '0.25rem' }}>
                          {validationErrors['primary_user.email']}
                        </div>
                      )}
                    </div>
                  </div>

                  <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
                    <div style={{ flex: 1 }}>
                      <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                        First Name {!formData.primary_user.first_name && <span style={{ color: 'red' }}>*</span>}
                      </label>
                      <input
                        type="text"
                        name="primary_user.first_name"
                        value={formData.primary_user.first_name}
                        onChange={handleInputChange}
                        required
                        style={{
                          width: '100%',
                          padding: '0.5rem',
                          border: `1px solid ${validationErrors['primary_user.first_name'] ? '#dc3545' : '#ddd'}`,
                          borderRadius: '4px',
                          backgroundColor: 'white',
                          color: '#000'
                        }}
                      />
                      {validationErrors['primary_user.first_name'] && (
                        <div style={{ fontSize: '0.875rem', color: '#dc3545', marginTop: '0.25rem' }}>
                          {validationErrors['primary_user.first_name']}
                        </div>
                      )}
                    </div>
                    <div style={{ flex: 1 }}>
                      <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                        Last Name {!formData.primary_user.last_name && <span style={{ color: 'red' }}>*</span>}
                      </label>
                      <input
                        type="text"
                        name="primary_user.last_name"
                        value={formData.primary_user.last_name}
                        onChange={handleInputChange}
                        required
                        style={{
                          width: '100%',
                          padding: '0.5rem',
                          border: `1px solid ${validationErrors['primary_user.last_name'] ? '#dc3545' : '#ddd'}`,
                          borderRadius: '4px',
                          backgroundColor: 'white',
                          color: '#000'
                        }}
                      />
                      {validationErrors['primary_user.last_name'] && (
                        <div style={{ fontSize: '0.875rem', color: '#dc3545', marginTop: '0.25rem' }}>
                          {validationErrors['primary_user.last_name']}
                        </div>
                      )}
                    </div>
                  </div>

                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
                      Password {!formData.primary_user.password && <span style={{ color: 'red' }}>*</span>}
                    </label>
                    <input
                      type="password"
                      name="primary_user.password"
                      value={formData.primary_user.password}
                      onChange={handleInputChange}
                      required
                      style={{
                        width: '100%',
                        padding: '0.5rem',
                        border: `1px solid ${validationErrors['primary_user.password'] ? '#dc3545' : '#ddd'}`,
                        borderRadius: '4px',
                        backgroundColor: 'white',
                        color: '#999'
                      }}
                    />
                    {validationErrors['primary_user.password'] && (
                      <div style={{ fontSize: '0.875rem', color: '#dc3545', marginTop: '0.25rem' }}>
                        {validationErrors['primary_user.password']}
                      </div>
                    )}
                  </div>
                </div>
              )}

              <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  style={{
                    padding: '0.5rem 1rem',
                    border: '1px solid #ddd',
                    backgroundColor: 'white',
                    color: '#666',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  {modalMode === 'view' ? 'Close' : 'Cancel'}
                </button>
                {modalMode !== 'view' && (
                  <button
                    type="submit"
                    disabled={!isFormValid || submitting}
                    style={{
                      padding: '0.5rem 1rem',
                      backgroundColor: (!isFormValid || submitting) ? '#6c757d' : '#007bff',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: (!isFormValid || submitting) ? 'not-allowed' : 'pointer',
                      opacity: (!isFormValid || submitting) ? 0.6 : 1
                    }}
                  >
                    {submitting ? 'Processing...' : (modalMode === 'add' ? 'Add Organisation' : 'Update Organisation')}
                  </button>
                )}
              </div>
            </form>
            </>
            )}
          </div>
        </div>
      )}

      {/* Actions Popup */}
      {showActionsPopup && selectedOrganizationForActions && (
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
                fontSize: '1.25rem'
              }}>
                {selectedOrganizationForActions.name}
              </h3>
              <div style={{ 
                color: '#666', 
                fontSize: '0.875rem',
                marginBottom: '0.5rem'
              }}>
                {selectedOrganizationForActions.domain || 'No domain'}
              </div>
              <div style={{ 
                color: '#666', 
                fontSize: '0.875rem',
                display: 'flex',
                gap: '0.5rem',
                alignItems: 'center'
              }}>
                <span style={{
                  padding: '0.25rem 0.5rem',
                  borderRadius: '4px',
                  fontSize: '0.75rem',
                  fontWeight: '600',
                  textTransform: 'uppercase',
                  backgroundColor: selectedOrganizationForActions.organization_type === 'educational' ? '#d4edda' : 
                                   selectedOrganizationForActions.organization_type === 'government' ? '#fff3cd' : '#f8f9fa',
                  color: selectedOrganizationForActions.organization_type === 'educational' ? '#155724' : 
                         selectedOrganizationForActions.organization_type === 'government' ? '#856404' : '#495057'
                }}>
                  {selectedOrganizationForActions.organization_type}
                </span>
                <span style={{
                  padding: '0.25rem 0.5rem',
                  borderRadius: '4px',
                  fontSize: '0.75rem',
                  fontWeight: '600',
                  textTransform: 'uppercase',
                  backgroundColor: selectedOrganizationForActions.is_active ? '#d4edda' : '#f8d7da',
                  color: selectedOrganizationForActions.is_active ? '#155724' : '#721c24'
                }}>
                  {selectedOrganizationForActions.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>
            
            <div style={{ 
              display: 'flex', 
              flexDirection: 'column',
              gap: '0.75rem'
            }}>
              <button
                onClick={() => {
                  console.log('View Details clicked for organization:', selectedOrganizationForActions.id);
                  closeActionsPopup();
                  handleViewOrganization(selectedOrganizationForActions.id);
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
                  console.log('Edit Organisation clicked for organization:', selectedOrganizationForActions.id);
                  closeActionsPopup();
                  handleEditOrganization(selectedOrganizationForActions.id);
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
                Edit Organisation
              </button>
              
              {selectedOrganizationForActions.is_active ? (
                <button
                  onClick={() => {
                    closeActionsPopup();
                    handleDeleteOrganization(selectedOrganizationForActions.id, selectedOrganizationForActions.name);
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
                    e.target.style.borderColor = '#dc3545';
                    e.target.style.color = '#dc3545';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.borderColor = '#5D8AA8';
                    e.target.style.color = '#5D8AA8';
                  }}
                >
                  Deactivate Organisation
                </button>
              ) : (
                <button
                  onClick={() => {
                    closeActionsPopup();
                    handleReactivateOrganization(selectedOrganizationForActions.id, selectedOrganizationForActions.name);
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
                    e.target.style.borderColor = '#28a745';
                    e.target.style.color = '#28a745';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.borderColor = '#5D8AA8';
                    e.target.style.color = '#5D8AA8';
                  }}
                >
                  Reactivate Organisation
                </button>
              )}

              <button
                onClick={() => handleViewTrustRelationships(selectedOrganizationForActions)}
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
                View Trust Relationships
              </button>


              <button
                onClick={() => {
                  closeActionsPopup();
                  handlePermanentDeleteOrganization(selectedOrganizationForActions.id, selectedOrganizationForActions.name);
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
                Permanently Delete
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
                  width: '100%',
                  fontSize: '0.875rem'
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

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

      {/* Trust Relationships Modal */}
      {showTrustModal && selectedOrgForTrust && (
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
          zIndex: 1002
        }}>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            padding: '2rem',
            width: '90%',
            maxWidth: '900px',
            maxHeight: '80vh',
            overflowY: 'auto',
            boxShadow: '0 10px 25px rgba(0,0,0,0.1)'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '1.5rem'
            }}>
              <div>
                <h2 style={{ margin: '0 0 0.5rem 0', color: '#333' }}>
                  Trust Relationships
                </h2>
                <div style={{ color: '#666', fontSize: '1rem' }}>
                  Organization: <strong>{selectedOrgForTrust.name}</strong>
                </div>
              </div>
              <button
                onClick={closeTrustModal}
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

            {/* Trust Relationships Content */}
            <div style={{ minHeight: '300px' }}>
              <div>
                <h3 style={{ color: '#5D8AA8', marginBottom: '1rem' }}>
                  Trust Relationships for {selectedOrgForTrust.name}
                </h3>

                {/* Filter relationships for this organization */}
                {(() => {
                  const orgRelationships = trustRelationships.filter(tr => {
                    // Handle different possible data formats from backend
                    const sourceOrgId = tr.source_organization?.id || tr.source_organization_id;
                    const targetOrgId = tr.target_organization?.id || tr.target_organization_id;
                    const currentOrgId = selectedOrgForTrust.id;
                    
                    return sourceOrgId === currentOrgId || targetOrgId === currentOrgId;
                  });

                  if (orgRelationships.length === 0) {
                    return (
                      <div style={{
                        textAlign: 'center',
                        padding: '3rem',
                        color: '#6c757d',
                        backgroundColor: '#f8f9fa',
                        borderRadius: '8px'
                      }}>
                        <h4 style={{ marginBottom: '0.5rem' }}>No Trust Relationships</h4>
                        <p style={{ margin: '0' }}>
                          This organization has no active trust relationships.
                        </p>
                      </div>
                    );
                  }

                  return orgRelationships.map((relationship) => (
                    <div
                      key={relationship.id}
                      style={{
                        border: '1px solid #e9ecef',
                        borderRadius: '8px',
                        padding: '1.25rem',
                        marginBottom: '1rem',
                        backgroundColor: '#f8f9fa'
                      }}
                    >
                      <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'flex-start',
                        marginBottom: '0.75rem'
                      }}>
                        <div style={{ flex: 1 }}>
                          <div style={{ fontWeight: '600', marginBottom: '0.5rem', fontSize: '1.1rem' }}>
                            {relationship.source_organization?.name || 'Unknown'}
                            <span style={{ margin: '0 0.5rem', color: '#6c757d' }}>→</span>
                            {relationship.target_organization?.name || 'Unknown'}
                          </div>
                          <div style={{
                            display: 'flex',
                            gap: '0.75rem',
                            flexWrap: 'wrap',
                            marginBottom: '0.5rem'
                          }}>
                            <span style={{
                              padding: '0.25rem 0.5rem',
                              borderRadius: '4px',
                              fontSize: '0.75rem',
                              fontWeight: '600',
                              textTransform: 'uppercase',
                              backgroundColor: relationship.trust_level?.name === 'HIGH' ? '#d4edda' :
                                             relationship.trust_level?.name === 'MEDIUM' ? '#fff3cd' : '#f8f9fa',
                              color: relationship.trust_level?.name === 'HIGH' ? '#155724' :
                                     relationship.trust_level?.name === 'MEDIUM' ? '#856404' : '#495057'
                            }}>
                              {relationship.trust_level?.name || relationship.trust_level?.level || 'Unknown'}
                            </span>
                            <span style={{
                              padding: '0.25rem 0.5rem',
                              borderRadius: '4px',
                              fontSize: '0.75rem',
                              fontWeight: '600',
                              textTransform: 'uppercase',
                              backgroundColor: relationship.status === 'active' ? '#d4edda' :
                                             relationship.status === 'pending' ? '#fff3cd' : '#f8d7da',
                              color: relationship.status === 'active' ? '#155724' :
                                     relationship.status === 'pending' ? '#856404' : '#721c24'
                            }}>
                              {relationship.status}
                            </span>
                            <span style={{
                              padding: '0.25rem 0.5rem',
                              borderRadius: '4px',
                              fontSize: '0.75rem',
                              fontWeight: '600',
                              backgroundColor: '#e3f2fd',
                              color: '#1565c0'
                            }}>
                              {relationship.relationship_type}
                            </span>
                          </div>
                          {relationship.notes && (
                            <div style={{
                              fontSize: '0.875rem',
                              color: '#6c757d',
                              fontStyle: 'italic'
                            }}>
                              Notes: {relationship.notes}
                            </div>
                          )}
                        </div>
                      </div>
                      <div style={{
                        fontSize: '0.75rem',
                        color: '#6c757d',
                        display: 'flex',
                        justifyContent: 'space-between'
                      }}>
                        <span>
                          Created: {relationship.created_at ? new Date(relationship.created_at).toLocaleDateString() : 'N/A'}
                        </span>
                        {relationship.updated_at && (
                          <span>
                            Updated: {new Date(relationship.updated_at).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    </div>
                  ));
                })()}

              </div>
            </div>

            <div style={{
              display: 'flex',
              justifyContent: 'flex-end',
              marginTop: '2rem',
              paddingTop: '1rem',
              borderTop: '1px solid #e9ecef'
            }}>
              <button
                onClick={closeTrustModal}
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
};

export default OrganisationManagement;