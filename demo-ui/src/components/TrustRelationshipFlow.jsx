import React, { useState } from 'react';
import './FlowComponent.css';

const TrustRelationshipFlow = () => {
  const [activeFlow, setActiveFlow] = useState(null);
  const [runningTest, setRunningTest] = useState(null);
  const [testResults, setTestResults] = useState({});
  const [testSummary, setTestSummary] = useState({
    total: 0,
    passed: 0,
    failed: 0,
    coverage: '0%'
  });
  const [isRunningAllTests, setIsRunningAllTests] = useState(false);

  const testFlows = [
    {
      id: 'trust-level-management',
      title: 'Trust Level Creation and Validation',
      file: 'trust_models/models.py',
      testClass: 'TrustLevelTestCase',
      description: 'Unit test flow for creating and managing trust levels between organizations',
      backendFlow: [
        {
          step: 1,
          component: 'Frontend Request',
          action: 'Admin creates new trust level between organizations',
          code: 'POST /api/trust/levels\n{\n  "name": "Strategic Partner",\n  "description": "High trust level for strategic partnerships",\n  "sharing_level": "HIGH",\n  "anonymization_required": false,\n  "data_retention_days": 365\n}'
        },
        {
          step: 2,
          component: 'Trust Level Model',
          action: 'Create and validate trust level configuration',
          code: 'class TrustLevel(models.Model):\n    name = models.CharField(max_length=100, unique=True)\n    description = models.TextField(blank=True)\n    sharing_level = models.CharField(\n        max_length=20,\n        choices=[\n            ("LOW", "Low - Anonymized data only"),\n            ("MEDIUM", "Medium - Limited data sharing"),\n            ("HIGH", "High - Full data sharing"),\n            ("FULL", "Full - Complete intelligence sharing")\n        ]\n    )\n    anonymization_required = models.BooleanField(default=True)\n    data_retention_days = models.IntegerField(default=90)\n    \n    def validate_sharing_policies(self):\n        if self.sharing_level == "HIGH" and self.anonymization_required:\n            raise ValidationError("High sharing level conflicts with anonymization requirement")\n        \n        if self.data_retention_days < 1:\n            raise ValidationError("Data retention must be at least 1 day")'
        },
        {
          step: 3,
          component: 'Trust Policy Engine',
          action: 'Apply trust level policies to data sharing',
          code: 'def apply_trust_policies(self, data, trust_level):\n    sharing_policies = {\n        "LOW": {\n            "anonymization_level": AnonymizationLevel.FULL,\n            "data_types_allowed": ["indicators_only"],\n            "metadata_sharing": False\n        },\n        "MEDIUM": {\n            "anonymization_level": AnonymizationLevel.MEDIUM,\n            "data_types_allowed": ["indicators", "basic_ttps"],\n            "metadata_sharing": True\n        },\n        "HIGH": {\n            "anonymization_level": AnonymizationLevel.LOW,\n            "data_types_allowed": ["indicators", "ttps", "reports"],\n            "metadata_sharing": True\n        }\n    }\n    \n    policy = sharing_policies.get(trust_level.sharing_level)\n    return self.filter_data_by_policy(data, policy)'
        },
        {
          step: 4,
          component: 'Frontend Response',
          action: 'Return created trust level with policy details',
          code: 'return {\n  "success": true,\n  "trust_level": {\n    "id": "trust-level-123",\n    "name": "Strategic Partner",\n    "sharing_level": "HIGH",\n    "policies": {\n      "anonymization_required": false,\n      "data_retention_days": 365,\n      "allowed_data_types": ["indicators", "ttps", "reports"],\n      "metadata_sharing": true\n    }\n  }\n}'
        }
      ],
      unitTests: [
        {
          method: 'test_trust_level_creation',
          assertion: 'Trust level created with valid sharing policies',
          mock: 'No external dependencies - pure model validation'
        },
        {
          method: 'test_validate_sharing_policies',
          assertion: 'Policy validation prevents conflicting configurations',
          mock: 'Mock ValidationError scenarios for edge cases'
        },
        {
          method: 'test_apply_trust_policies',
          assertion: 'Data filtering applied correctly based on trust level',
          mock: 'Mock data objects with controlled sharing policy application'
        }
      ]
    },
    {
      id: 'trust-group-management',
      title: 'Trust Group and Membership Management',
      file: 'trust_models/models.py',
      testClass: 'TrustGroupTestCase',
      description: 'Unit test flow for managing trust groups and organization memberships',
      backendFlow: [
        {
          step: 1,
          component: 'Frontend Request',
          action: 'Admin creates trust group for sector collaboration',
          code: 'POST /api/trust/groups\n{\n  "name": "Financial Sector Intelligence",\n  "description": "Trust group for financial institutions",\n  "group_type": "SECTOR_BASED",\n  "default_trust_level": "MEDIUM",\n  "requires_approval": true\n}'
        },
        {
          step: 2,
          component: 'Trust Group Model',
          action: 'Create trust group with membership policies',
          code: 'class TrustGroup(models.Model):\n    name = models.CharField(max_length=200, unique=True)\n    description = models.TextField(blank=True)\n    group_type = models.CharField(\n        max_length=20,\n        choices=[\n            ("SECTOR_BASED", "Sector-based collaboration"),\n            ("GEOGRAPHIC", "Geographic region-based"),\n            ("THREAT_FOCUSED", "Threat-specific sharing"),\n            ("BILATERAL", "Bilateral partnership")\n        ]\n    )\n    default_trust_level = models.ForeignKey(TrustLevel, on_delete=models.PROTECT)\n    requires_approval = models.BooleanField(default=True)\n    created_by = models.ForeignKey(Organization, on_delete=models.CASCADE)\n    \n    def add_member(self, organization, trust_level=None):\n        if trust_level is None:\n            trust_level = self.default_trust_level\n        \n        membership, created = TrustGroupMembership.objects.get_or_create(\n            group=self,\n            organization=organization,\n            defaults={\n                "trust_level": trust_level,\n                "status": "PENDING" if self.requires_approval else "ACTIVE"\n            }\n        )\n        \n        return membership, created'
        },
        {
          step: 3,
          component: 'Membership Approval Workflow',
          action: 'Process membership requests and approvals',
          code: 'def process_membership_request(self, membership_id, action, approver):\n    membership = TrustGroupMembership.objects.get(id=membership_id)\n    \n    if action == "APPROVE":\n        membership.status = "ACTIVE"\n        membership.approved_by = approver\n        membership.approved_at = timezone.now()\n        \n        # Create trust relationships with existing members\n        self.create_bilateral_relationships(membership)\n        \n    elif action == "REJECT":\n        membership.status = "REJECTED"\n        membership.rejected_by = approver\n        membership.rejected_at = timezone.now()\n    \n    membership.save()\n    return membership\n\ndef create_bilateral_relationships(self, new_membership):\n    existing_members = TrustGroupMembership.objects.filter(\n        group=new_membership.group,\n        status="ACTIVE"\n    ).exclude(id=new_membership.id)\n    \n    for existing_member in existing_members:\n        TrustRelationship.objects.get_or_create(\n            source_org=new_membership.organization,\n            target_org=existing_member.organization,\n            trust_level=new_membership.trust_level,\n            relationship_type="GROUP_BASED"\n        )'
        },
        {
          step: 4,
          component: 'Frontend Response',
          action: 'Return trust group with membership status',
          code: 'return {\n  "success": true,\n  "trust_group": {\n    "id": "group-456",\n    "name": "Financial Sector Intelligence",\n    "member_count": 8,\n    "pending_requests": 2,\n    "active_relationships": 28\n  },\n  "membership_status": {\n    "organization": "Example Bank",\n    "status": "ACTIVE",\n    "trust_level": "MEDIUM",\n    "joined_at": "2024-01-15T10:30:00Z"\n  }\n}'
        }
      ],
      unitTests: [
        {
          method: 'test_trust_group_creation',
          assertion: 'Trust group created with appropriate default settings',
          mock: 'Mock TrustLevel and Organization objects for relationships'
        },
        {
          method: 'test_add_member_workflow',
          assertion: 'Organization membership added with correct approval status',
          mock: 'Mock TrustGroupMembership creation and status handling'
        },
        {
          method: 'test_bilateral_relationship_creation',
          assertion: 'Trust relationships created between all group members',
          mock: 'Mock existing group memberships for relationship testing'
        }
      ]
    },
    {
      id: 'sharing-policy-enforcement',
      title: 'Sharing Policy and Enforcement Engine',
      file: 'trust_models/models.py',
      testClass: 'SharingPolicyTestCase',
      description: 'Unit test flow for enforcing trust-based sharing policies and data access control',
      backendFlow: [
        {
          step: 1,
          component: 'Frontend Request',
          action: 'User attempts to share intelligence with partner organization',
          code: 'POST /api/share/intelligence\n{\n  "target_organization": "partner-org-789",\n  "data_items": ["indicator-1", "ttp-2", "report-3"],\n  "sharing_scope": "BILATERAL",\n  "requested_anonymization": "LOW"\n}'
        },
        {
          step: 2,
          component: 'Trust Relationship Lookup',
          action: 'Find trust relationship between organizations',
          code: 'def get_trust_relationship(self, source_org, target_org):\n    # Try direct bilateral relationship first\n    direct_relationship = TrustRelationship.objects.filter(\n        source_org=source_org,\n        target_org=target_org,\n        status="ACTIVE"\n    ).first()\n    \n    if direct_relationship:\n        return direct_relationship\n    \n    # Check for group-based relationships\n    common_groups = TrustGroup.objects.filter(\n        members__organization=source_org\n    ).filter(\n        members__organization=target_org\n    ).filter(\n        members__status="ACTIVE"\n    )\n    \n    if common_groups.exists():\n        # Use the highest trust level from common groups\n        group_memberships = TrustGroupMembership.objects.filter(\n            group__in=common_groups,\n            organization__in=[source_org, target_org]\n        ).order_by("-trust_level__sharing_level")\n        \n        return group_memberships.first().trust_level\n    \n    return None'
        },
        {
          step: 3,
          component: 'Sharing Policy Enforcement',
          action: 'Apply trust level policies to requested data sharing',
          code: 'def enforce_sharing_policy(self, trust_relationship, data_items, requested_options):\n    if not trust_relationship:\n        raise PermissionDenied("No trust relationship exists")\n    \n    trust_level = trust_relationship.trust_level\n    policy = SharingPolicy.objects.get(trust_level=trust_level)\n    \n    # Check if requested anonymization level is sufficient\n    min_anonymization = policy.minimum_anonymization_level\n    if requested_options["anonymization"] < min_anonymization:\n        requested_options["anonymization"] = min_anonymization\n    \n    # Filter data items based on allowed types\n    allowed_items = []\n    for item in data_items:\n        if item.data_type in policy.allowed_data_types:\n            allowed_items.append(item)\n    \n    # Apply data retention policies\n    sharing_record = SharingRecord.objects.create(\n        source_org=trust_relationship.source_org,\n        target_org=trust_relationship.target_org,\n        data_items=allowed_items,\n        expires_at=timezone.now() + timedelta(days=policy.data_retention_days)\n    )\n    \n    return {\n        "allowed_items": allowed_items,\n        "anonymization_level": requested_options["anonymization"],\n        "sharing_record_id": sharing_record.id\n    }'
        },
        {
          step: 4,
          component: 'Data Anonymization Application',
          action: 'Apply anonymization based on trust level policies',
          code: 'def apply_trust_based_anonymization(self, data_items, trust_level):\n    anonymization_context = AnonymizationContext()\n    anonymized_items = []\n    \n    for item in data_items:\n        if trust_level.anonymization_required:\n            anonymized_item = anonymization_context.anonymize_stix_object(\n                item, \n                trust_level.anonymization_level\n            )\n            anonymized_items.append(anonymized_item)\n        else:\n            # Share original data for high trust relationships\n            anonymized_items.append(item)\n    \n    return anonymized_items'
        },
        {
          step: 5,
          component: 'Frontend Response',
          action: 'Return sharing result with applied policies',
          code: 'return {\n  "success": true,\n  "sharing_summary": {\n    "items_requested": 3,\n    "items_shared": 2,\n    "items_filtered": 1,\n    "anonymization_applied": "MEDIUM",\n    "trust_level": "Strategic Partner"\n  },\n  "shared_items": [\n    {\n      "type": "indicator",\n      "original_value": "192.168.1.100",\n      "shared_value": "192.168.x.x",\n      "anonymization_level": "MEDIUM"\n    }\n  ],\n  "policy_details": {\n    "data_retention_days": 365,\n    "sharing_expires_at": "2025-01-15T10:30:00Z"\n  }\n}'
        }
      ],
      unitTests: [
        {
          method: 'test_trust_relationship_lookup',
          assertion: 'Trust relationships found via direct and group-based connections',
          mock: 'Mock TrustRelationship and TrustGroup models with various scenarios'
        },
        {
          method: 'test_sharing_policy_enforcement',
          assertion: 'Data sharing filtered and anonymized according to trust policies',
          mock: 'Mock SharingPolicy objects with different trust level configurations'
        },
        {
          method: 'test_data_retention_policies',
          assertion: 'Sharing records created with appropriate expiration dates',
          mock: 'Mock timezone.now() for deterministic expiration testing'
        },
        {
          method: 'test_anonymization_integration',
          assertion: 'Trust level policies properly integrated with anonymization system',
          mock: 'Mock AnonymizationContext to verify anonymization level application'
        }
      ]
    }
  ];

  const TestSummaryBox = () => (
    <div className="test-summary-box">
      <div className="summary-header">
        <h3>Trust Models Test Coverage</h3>
        <button className="run-tests-btn" onClick={() => {
          setIsRunningAllTests(true);
          setTimeout(() => {
            setTestSummary({
              total: 134,
              passed: 134,
              failed: 0,
              coverage: '85%'
            });
            setIsRunningAllTests(false);
          }, 4000);
        }} disabled={isRunningAllTests}>
          {isRunningAllTests ? 'Running All Tests...' : 'Run All Tests'}
        </button>
      </div>
      <div className="summary-stats">
        <div className="stat-item passed">
          <div className="stat-number">{testSummary.passed}</div>
          <div className="stat-label">Passed</div>
        </div>
        <div className="stat-item failed">
          <div className="stat-number">{testSummary.failed}</div>
          <div className="stat-label">Failed</div>
        </div>
        <div className="stat-item total">
          <div className="stat-number">{testSummary.total}</div>
          <div className="stat-label">Total</div>
        </div>
        <div className="stat-item coverage">
          <div className="stat-number">{testSummary.coverage}</div>
          <div className="stat-label">Coverage</div>
        </div>
      </div>
    </div>
  );

  const runTest = async (flowId) => {
    setRunningTest(flowId);
    
    // Simulate test execution with realistic timing
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Simulate test results based on the flow
    const mockResults = {
      'trust-level-management': {
        status: 'PASSED',
        duration: '2.89s',
        tests_run: 3,
        tests_passed: 3,
        tests_failed: 0,
        coverage: '86%',
        details: [
          { method: 'test_trust_level_creation', status: 'PASSED', duration: '0.92s', assertion: '✅ Input: {"name": "Strategic Partner", "sharing_level": "HIGH", "anonymization_required": false} → Expected: TrustLevel created → Actual: TrustLevel(id=123, sharing_level="HIGH", anonymization_required=False) (Trust level created successfully)' },
          { method: 'test_validate_sharing_policies', status: 'PASSED', duration: '0.67s', assertion: '✅ Input: HIGH sharing + anonymization required → Expected: ValidationError → Actual: ValidationError("High sharing level conflicts with anonymization requirement") (Policy conflict detected)' },
          { method: 'test_apply_trust_policies', status: 'PASSED', duration: '1.30s', assertion: '✅ Input: Data + MEDIUM trust level → Expected: Filtered data with medium anonymization → Actual: {"allowed_items": 5, "anonymization_level": "MEDIUM"} (Policies applied correctly)' }
        ]
      },
      'trust-group-management': {
        status: 'PASSED',
        duration: '3.45s',
        tests_run: 3,
        tests_passed: 3,
        tests_failed: 0,
        coverage: '91%',
        details: [
          { method: 'test_trust_group_creation', status: 'PASSED', duration: '1.15s', assertion: '✅ Input: {"name": "Financial Sector", "group_type": "SECTOR_BASED", "requires_approval": true} → Expected: TrustGroup with default trust level → Actual: TrustGroup(name="Financial Sector", default_trust_level="MEDIUM") (Group created with defaults)' },
          { method: 'test_add_member_workflow', status: 'PASSED', duration: '1.23s', assertion: '✅ Input: Organization + Group requiring approval → Expected: Membership status "PENDING" → Actual: TrustGroupMembership(status="PENDING", trust_level="MEDIUM") (Member added with pending status)' },
          { method: 'test_bilateral_relationship_creation', status: 'PASSED', duration: '1.07s', assertion: '✅ Input: New member + 3 existing members → Expected: 3 bilateral relationships created → Actual: 3 TrustRelationship objects created (Bilateral relationships established)' }
        ]
      },
      'sharing-policy-enforcement': {
        status: 'PASSED',
        duration: '4.12s',
        tests_run: 4,
        tests_passed: 4,
        tests_failed: 0,
        coverage: '88%',
        details: [
          { method: 'test_trust_relationship_lookup', status: 'PASSED', duration: '1.03s', assertion: '✅ Input: Source org + Target org → Expected: Trust relationship via group membership → Actual: TrustRelationship found through "Financial Sector" group (Group-based relationship found)' },
          { method: 'test_sharing_policy_enforcement', status: 'PASSED', duration: '1.28s', assertion: '✅ Input: 3 data items + MEDIUM trust → Expected: 2 items shared, 1 filtered → Actual: {"items_shared": 2, "items_filtered": 1, "anonymization": "MEDIUM"} (Policy enforcement successful)' },
          { method: 'test_data_retention_policies', status: 'PASSED', duration: '0.89s', assertion: '✅ Input: Sharing with 365-day retention → Expected: Expiration date set → Actual: SharingRecord(expires_at="2025-01-15T10:30:00Z") (Retention policy applied)' },
          { method: 'test_anonymization_integration', status: 'PASSED', duration: '0.92s', assertion: '✅ Input: Trust level requiring anonymization → Expected: AnonymizationContext called → Actual: Data anonymized with trust level policies (Anonymization integration working)' }
        ]
      }
    };

    setTestResults(prev => ({
      ...prev,
      [flowId]: mockResults[flowId]
    }));
    setRunningTest(null);
  };

  const renderTestResults = (flowId) => {
    const result = testResults[flowId];
    if (!result) return null;

    return (
      <div className="test-results">
        <div className="test-results-header">
          <h4>Test Execution Results</h4>
          <div className={`test-status ${result.status.toLowerCase()}`}>
            {result.status}
          </div>
        </div>
        <div className="test-summary">
          <div className="test-stat">
            <span className="stat-label">Duration:</span>
            <span className="stat-value">{result.duration}</span>
          </div>
          <div className="test-stat">
            <span className="stat-label">Tests Run:</span>
            <span className="stat-value">{result.tests_run}</span>
          </div>
          <div className="test-stat">
            <span className="stat-label">Passed:</span>
            <span className="stat-value passed">{result.tests_passed}</span>
          </div>
          <div className="test-stat">
            <span className="stat-label">Failed:</span>
            <span className="stat-value failed">{result.tests_failed}</span>
          </div>
          <div className="test-stat">
            <span className="stat-label">Coverage:</span>
            <span className="stat-value">{result.coverage}</span>
          </div>
        </div>
        <div className="test-details">
          <h5>Test Method Results:</h5>
          {result.details.map((test, index) => (
            <div key={index} className="test-method-result">
              <div className="method-header">
                <span className={`method-status ${test.status.toLowerCase()}`}>
                  {test.status === 'PASSED' ? '✅' : '❌'}
                </span>
                <span className="method-name">{test.method}</span>
                <span className="method-duration">{test.duration}</span>
              </div>
              <div className="method-assertion">{test.assertion}</div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderBackendFlow = (flow) => (
    <div className="backend-flow">
      <h4>Backend to Frontend Flow</h4>
      <div className="flow-steps">
        {flow.backendFlow.map((step, index) => (
          <div key={index} className="flow-step">
            <div className="step-header">
              <div className="step-number">{step.step}</div>
              <div className="step-info">
                <div className="step-component">{step.component}</div>
                <div className="step-action">{step.action}</div>
              </div>
            </div>
            <div className="step-code">
              <pre><code>{step.code}</code></pre>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderUnitTests = (flow) => (
    <div className="unit-tests-section">
      <h4>Unit Test Implementation</h4>
      <div className="test-class-info">
        <span className="test-file">📁 {flow.file}</span>
        <span className="test-class">🧪 {flow.testClass}</span>
      </div>
      <div className="unit-test-methods">
        {flow.unitTests.map((test, index) => (
          <div key={index} className="unit-test-item">
            <div className="test-method">def {test.method}(self):</div>
            <div className="test-assertion">✅ Assert: {test.assertion}</div>
            <div className="test-mock">🔧 Mock: {test.mock}</div>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="flow-container">


      <TestSummaryBox />

      <div className="test-flows">
        {testFlows.map(flow => (
          <div key={flow.id} className="test-flow-card">
            <div className="flow-card-header" onClick={() => setActiveFlow(activeFlow === flow.id ? null : flow.id)}>
              <div className="flow-info">
                <h3>{flow.title}</h3>
                <p className="flow-description">{flow.description}</p>
                <div className="flow-meta">
                  <span className="flow-file">📁 {flow.file}</span>
                  <span className="flow-class">🧪 {flow.testClass}</span>
                </div>
              </div>
              <div className="flow-expand">{activeFlow === flow.id ? '▼' : '▶'}</div>
            </div>
            
            {activeFlow === flow.id && (
              <div className="flow-content">
                <div className="run-test-section">
                  <button 
                    className={`run-test-btn ${runningTest === flow.id ? 'running' : ''}`}
                    onClick={() => runTest(flow.id)}
                    disabled={runningTest === flow.id}
                  >
                    {runningTest === flow.id ? 'Running Tests...' : 'Run Test'}
                  </button>
                </div>
                {renderBackendFlow(flow)}
                {renderUnitTests(flow)}
                {renderTestResults(flow.id)}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default TrustRelationshipFlow;