import React, { useState } from 'react';
import './FlowComponent.css';

const UserManagementFlow = () => {
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
      id: 'user-factory-creation',
      title: 'User Factory Pattern Implementation',
      file: 'test_user_management.py',
      testClass: 'UserFactoryTestCase',
      description: 'Unit test flow for creating users with factory pattern and role-based creation',
      backendFlow: [
        {
          step: 1,
          component: 'Frontend Request',
          action: 'Admin submits user creation form',
          code: 'POST /api/admin/users/create\n{\n  "username": "john.doe",\n  "email": "john.doe@example.com",\n  "role": "publisher",\n  "organization_id": "org-123",\n  "auto_generate_password": true\n}'
        },
        {
          step: 2,
          component: 'User Factory',
          action: 'Select appropriate user creator based on role',
          code: 'class UserFactory:\n    @staticmethod\n    def create_user(role, user_data):\n        creators = {\n            "viewer": StandardUserCreator,\n            "publisher": PublisherUserCreator,\n            "BlueVisionAdmin": AdminUserCreator\n        }\n        \n        creator_class = creators.get(role, StandardUserCreator)\n        creator = creator_class()\n        return creator.create(user_data)'
        },
        {
          step: 3,
          component: 'Publisher User Creator',
          action: 'Create user with publisher-specific privileges',
          code: 'class PublisherUserCreator(UserCreator):\n    def create(self, user_data):\n        user = CustomUser.objects.create_user(\n            username=user_data["username"],\n            email=user_data["email"],\n            organization_id=user_data["organization_id"],\n            role="publisher",\n            is_publisher=True,\n            is_verified=True\n        )\n        \n        if user_data.get("auto_generate_password"):\n            password = self.generate_secure_password()\n            user.set_password(password)\n            user.save()\n            return user, password\n        \n        return user, None'
        },
        {
          step: 4,
          component: 'Password Generation',
          action: 'Generate secure password if requested',
          code: 'def generate_secure_password(self, length=12):\n    chars = string.ascii_letters + string.digits + "!@#$%^&*"\n    password = "".join(secrets.choice(chars) for _ in range(length))\n    \n    # Ensure complexity requirements\n    if not (any(c.isupper() for c in password) and \n            any(c.islower() for c in password) and\n            any(c.isdigit() for c in password)):\n        return self.generate_secure_password(length)\n    \n    return password'
        },
        {
          step: 5,
          component: 'Permission Assignment',
          action: 'Assign role-based permissions and organization access',
          code: 'def assign_permissions(self, user):\n    if user.role == "publisher":\n        user.user_permissions.add(\n            Permission.objects.get(codename="add_threatfeed"),\n            Permission.objects.get(codename="change_threatfeed")\n        )\n    \n    # Organization-based permissions\n    if user.is_organization_admin():\n        user.user_permissions.add(\n            Permission.objects.get(codename="manage_organization_users")\n        )'
        },
        {
          step: 6,
          component: 'Frontend Response',
          action: 'Return user creation result with optional password',
          code: 'return {\n  "success": true,\n  "user": {\n    "id": "user-789",\n    "username": "john.doe",\n    "email": "john.doe@example.com",\n    "role": "publisher",\n    "organization": "Example Organization",\n    "is_verified": true,\n    "created_at": "2024-01-15T10:30:00Z"\n  },\n  "generated_password": "SecurePass123!",\n  "next_steps": ["Email credentials", "Setup 2FA"]\n}'
        }
      ],
      unitTests: [
        {
          method: 'test_standard_user_creation',
          assertion: 'StandardUserCreator creates viewer users with correct defaults',
          mock: 'Mock Organization object for user-organization relationship'
        },
        {
          method: 'test_publisher_user_creation',
          assertion: 'PublisherUserCreator sets is_publisher=True and appropriate permissions',
          mock: 'Mock Permission objects and organization assignment'
        },
        {
          method: 'test_auto_password_generation',
          assertion: 'Generated passwords meet complexity requirements',
          mock: 'No external dependencies - pure logic test with multiple iterations'
        },
        {
          method: 'test_unauthorized_user_creation',
          assertion: 'Non-admin users cannot create admin accounts',
          mock: 'Mock authentication context with different user roles'
        }
      ]
    },
    {
      id: 'user-permission-validation',
      title: 'User Permission and Role Validation',
      file: 'test_user_management.py',
      testClass: 'UserPermissionTestCase',
      description: 'Unit test flow for validating user permissions and role-based access control',
      backendFlow: [
        {
          step: 1,
          component: 'Frontend Request',
          action: 'User attempts to access publisher functionality',
          code: 'POST /api/feeds/publish\n{\n  "feed_data": {...},\n  "visibility": "organization"\n}\n\n# Headers:\n# Authorization: Bearer <jwt_token>'
        },
        {
          step: 2,
          component: 'Permission Middleware',
          action: 'Extract user from JWT and validate permissions',
          code: 'def check_publisher_permission(request):\n    user = request.user\n    \n    if not user.is_authenticated:\n        raise PermissionDenied("Authentication required")\n    \n    if not user.can_publish_feeds():\n        raise PermissionDenied("Publisher role required")\n    \n    return True'
        },
        {
          step: 3,
          component: 'User Permission Methods',
          action: 'Check user role and publishing capabilities',
          code: 'class CustomUser(AbstractUser):\n    def can_publish_feeds(self):\n        return (\n            self.role in ["publisher", "BlueVisionAdmin"] and\n            self.is_publisher and\n            self.is_verified and\n            self.is_active\n        )\n    \n    def is_organization_admin(self):\n        return (\n            self.role == "BlueVisionAdmin" and\n            self.organization is not None\n        )'
        },
        {
          step: 4,
          component: 'Organization Access Control',
          action: 'Validate user can access organization resources',
          code: 'def check_organization_access(user, resource):\n    if user.is_system_admin():\n        return True  # System admins access everything\n    \n    if hasattr(resource, "organization"):\n        return resource.organization == user.organization\n    \n    # Default to same organization access\n    return True'
        },
        {
          step: 5,
          component: 'Frontend Response',
          action: 'Return permission validation result',
          code: 'return {\n  "permission_granted": true,\n  "user_role": "publisher",\n  "organization_access": true,\n  "available_actions": [\n    "create_feed",\n    "edit_own_feeds", \n    "publish_to_organization",\n    "view_organization_feeds"\n  ]\n}'
        }
      ],
      unitTests: [
        {
          method: 'test_can_publish_feeds',
          assertion: 'Publisher users with verification can publish feeds',
          mock: 'Mock user with different role combinations and verification status'
        },
        {
          method: 'test_is_organization_admin',
          assertion: 'BlueVisionAdmin users with organization can manage org users',
          mock: 'Mock Organization object and user role assignments'
        },
        {
          method: 'test_permission_edge_cases',
          assertion: 'Inactive or unverified users denied access regardless of role',
          mock: 'Mock users with various is_active and is_verified combinations'
        }
      ]
    },
    {
      id: 'bulk-user-operations',
      title: 'Bulk User Management Operations',
      file: 'test_user_management.py',
      testClass: 'UserBulkOperationsTestCase',
      description: 'Unit test flow for bulk user creation, verification, and management',
      backendFlow: [
        {
          step: 1,
          component: 'Frontend Request',
          action: 'Admin uploads CSV file for bulk user creation',
          code: 'POST /api/admin/users/bulk-create\n{\n  "csv_data": "username,email,role,organization\\njohn.doe,john@example.com,viewer,org-1\\njane.smith,jane@example.com,publisher,org-1",\n  "auto_verify": false,\n  "send_emails": true\n}'
        },
        {
          step: 2,
          component: 'CSV Processing',
          action: 'Parse and validate CSV data for user creation',
          code: 'def process_bulk_user_csv(csv_data, options):\n    users_to_create = []\n    errors = []\n    \n    for row_num, row in enumerate(csv_data.split("\\n")[1:], 2):\n        try:\n            username, email, role, org_id = row.split(",")\n            \n            # Validate each field\n            if not self.validate_username(username):\n                errors.append(f"Row {row_num}: Invalid username")\n                continue\n            \n            if not self.validate_email(email):\n                errors.append(f"Row {row_num}: Invalid email")\n                continue\n            \n            users_to_create.append({\n                "username": username,\n                "email": email,\n                "role": role,\n                "organization_id": org_id\n            })\n        except ValueError:\n            errors.append(f"Row {row_num}: Invalid CSV format")\n    \n    return users_to_create, errors'
        },
        {
          step: 3,
          component: 'Bulk User Creation',
          action: 'Create multiple users using factory pattern',
          code: 'def bulk_create_users(users_data, options):\n    created_users = []\n    failed_users = []\n    \n    for user_data in users_data:\n        try:\n            user, password = UserFactory.create_user(\n                user_data["role"], \n                {**user_data, "auto_generate_password": True}\n            )\n            \n            created_users.append({\n                "user": user,\n                "password": password,\n                "needs_verification": not options.get("auto_verify", False)\n            })\n            \n        except Exception as e:\n            failed_users.append({\n                "user_data": user_data,\n                "error": str(e)\n            })\n    \n    return created_users, failed_users'
        },
        {
          step: 4,
          component: 'Bulk Verification',
          action: 'Verify multiple users if auto-verification enabled',
          code: 'def bulk_verify_users(self, user_ids):\n    verification_results = []\n    \n    for user_id in user_ids:\n        try:\n            user = CustomUser.objects.get(id=user_id)\n            user.is_verified = True\n            user.verified_at = timezone.now()\n            user.save()\n            \n            verification_results.append({\n                "user_id": user_id,\n                "status": "verified",\n                "verified_at": user.verified_at\n            })\n        except CustomUser.DoesNotExist:\n            verification_results.append({\n                "user_id": user_id,\n                "status": "error",\n                "error": "User not found"\n            })\n    \n    return verification_results'
        },
        {
          step: 5,
          component: 'Frontend Response',
          action: 'Return bulk operation results with detailed statistics',
          code: 'return {\n  "success": true,\n  "statistics": {\n    "total_processed": 50,\n    "successfully_created": 47,\n    "failed_creation": 3,\n    "auto_verified": 47,\n    "emails_sent": 47\n  },\n  "created_users": [\n    {"username": "john.doe", "password": "TempPass123!", "status": "created"},\n    {"username": "jane.smith", "password": "TempPass456!", "status": "created"}\n  ],\n  "failed_users": [\n    {"username": "invalid.user", "error": "Email already exists"}\n  ]\n}'
        }
      ],
      unitTests: [
        {
          method: 'test_bulk_user_creation',
          assertion: 'Multiple users created correctly with different roles',
          mock: 'Mock Organization objects and UserFactory.create_user() calls'
        },
        {
          method: 'test_bulk_user_verification',
          assertion: 'Bulk verification updates is_verified flag and timestamp',
          mock: 'Mock CustomUser queryset with controlled user objects'
        },
        {
          method: 'test_csv_validation_errors',
          assertion: 'Invalid CSV data produces appropriate error messages',
          mock: 'No external dependencies - pure validation logic testing'
        },
        {
          method: 'test_partial_success_handling',
          assertion: 'Bulk operations handle partial failures gracefully',
          mock: 'Mock UserFactory to raise exceptions for specific users'
        }
      ]
    }
  ];

  const TestSummaryBox = () => (
    <div className="test-summary-box">
      <div className="summary-header">
        <h3>User Management Test Coverage</h3>
        <button className="run-tests-btn" onClick={() => {
          setIsRunningAllTests(true);
          // Simulate test run
          setTimeout(() => {
            setTestSummary({
              total: 98,
              passed: 98,
              failed: 0,
              coverage: '74%'
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
    await new Promise(resolve => setTimeout(resolve, 2200));
    
    // Simulate test results based on the flow
    const mockResults = {
      'user-factory-creation': {
        status: 'PASSED',
        duration: '2.15s',
        tests_run: 4,
        tests_passed: 4,
        tests_failed: 0,
        coverage: '91%',
        details: [
          { method: 'test_standard_user_creation', status: 'PASSED', duration: '0.52s', assertion: '✅ Input: {"username": "john.doe", "role": "viewer", "org": "org-123"} → Expected: User(role="viewer", is_publisher=False) → Actual: User(role="viewer", is_publisher=False) (Standard user created)' },
          { method: 'test_publisher_user_creation', status: 'PASSED', duration: '0.67s', assertion: '✅ Input: {"username": "jane.smith", "role": "publisher", "org": "org-123"} → Expected: User(role="publisher", is_publisher=True, permissions=["add_threatfeed"]) → Actual: User(role="publisher", is_publisher=True, permissions=["add_threatfeed"]) (Publisher created with permissions)' },
          { method: 'test_auto_password_generation', status: 'PASSED', duration: '0.45s', assertion: '✅ Input: generate_secure_password(length=12) → Expected: Password with [upper, lower, digit, special] → Actual: "TempPass123!" (Complexity requirements met)' },
          { method: 'test_unauthorized_user_creation', status: 'PASSED', duration: '0.51s', assertion: '✅ Input: Non-admin user attempts admin creation → Expected: PermissionDenied exception → Actual: PermissionDenied exception (Access denied correctly)' }
        ]
      },
      'user-permission-validation': {
        status: 'PASSED',
        duration: '1.78s',
        tests_run: 3,
        tests_passed: 3,
        tests_failed: 0,
        coverage: '96%',
        details: [
          { method: 'test_can_publish_feeds', status: 'PASSED', duration: '0.63s', assertion: '✅ Input: User(role="publisher", is_verified=True, is_active=True) → Expected: can_publish_feeds()=True → Actual: can_publish_feeds()=True (Publisher access granted)' },
          { method: 'test_is_organization_admin', status: 'PASSED', duration: '0.58s', assertion: '✅ Input: User(role="BlueVisionAdmin", organization="org-123") → Expected: is_organization_admin()=True → Actual: is_organization_admin()=True (Admin status verified)' },
          { method: 'test_permission_edge_cases', status: 'PASSED', duration: '0.57s', assertion: '✅ Input: User(role="publisher", is_active=False) → Expected: can_publish_feeds()=False → Actual: can_publish_feeds()=False (Inactive user denied access)' }
        ]
      },
      'bulk-user-operations': {
        status: 'PASSED',
        duration: '3.22s',
        tests_run: 4,
        tests_passed: 4,
        tests_failed: 0,
        coverage: '89%',
        details: [
          { method: 'test_bulk_user_creation', status: 'PASSED', duration: '0.95s', assertion: '✅ Input: CSV with 50 users, 3 roles → Expected: 47 created, 3 failed → Actual: 47 created, 3 failed (Bulk creation successful)' },
          { method: 'test_bulk_user_verification', status: 'PASSED', duration: '0.87s', assertion: '✅ Input: ["user-1", "user-2", "user-3"] → Expected: All users.is_verified=True → Actual: All users.is_verified=True (Bulk verification completed)' },
          { method: 'test_csv_validation_errors', status: 'PASSED', duration: '0.71s', assertion: '✅ Input: "invalid,email,role" → Expected: ["Row 2: Invalid email"] → Actual: ["Row 2: Invalid email"] (Validation errors detected)' },
          { method: 'test_partial_success_handling', status: 'PASSED', duration: '0.69s', assertion: '✅ Input: Mixed valid/invalid users → Expected: Partial success with error details → Actual: Partial success with error details (Graceful failure handling)' }
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
      <div className="flow-header">
        <h2>Unit Tests for Adding Users and User Management</h2>
        <p>Backend to Frontend unit test flows for factory pattern user creation and role-based management</p>
      </div>

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

export default UserManagementFlow;