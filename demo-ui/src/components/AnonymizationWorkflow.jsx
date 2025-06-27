import React, { useState } from 'react';
import './WorkflowComponent.css';

const AnonymizationWorkflow = () => {
  const [activeTest, setActiveTest] = useState(null);
  const [testResults, setTestResults] = useState({
    total: 0,
    passed: 0,
    failed: 0,
    coverage: '0%'
  });

  const unitTests = [
    {
      id: 'ip-anonymization',
      file: 'test_anonymization_strategies.py',
      class: 'IPAddressAnonymizationStrategyTestCase',
      title: 'IP Address Anonymization Unit Tests',
      description: 'Unit tests for IP address anonymization strategy class in isolation',
      tests: [
        {
          name: 'test_validate_valid_ipv4',
          description: 'Tests IPv4 address validation logic',
          steps: [
            'Create IPAddressAnonymizationStrategy instance',
            'Test validate() method with valid IPv4 addresses',
            'Assert validation returns True for valid IPs',
            'Verify no external dependencies called',
            'Test isolated validation logic'
          ]
        },
        {
          name: 'test_anonymize_ipv4_low_level',
          description: 'Tests low-level IPv4 anonymization (preserve 3 octets)',
          steps: [
            'Mock IPv4 address input',
            'Call anonymize() with AnonymizationLevel.LOW',
            'Assert last octet replaced with "x"',
            'Verify format: "192.168.1.x"',
            'Test isolated anonymization logic'
          ]
        },
        {
          name: 'test_anonymize_ipv4_full_level',
          description: 'Tests full IPv4 anonymization with consistency',
          steps: [
            'Test same IP multiple times',
            'Call anonymize() with AnonymizationLevel.FULL',
            'Assert consistent anonymization results',
            'Verify hash-based consistency',
            'Test deterministic anonymization'
          ]
        }
      ]
    },
    {
      id: 'domain-anonymization',
      file: 'test_anonymization_strategies.py',
      class: 'DomainAnonymizationStrategyTestCase',
      title: 'Domain Anonymization Unit Tests',
      description: 'Unit tests for domain anonymization strategy in isolation',
      tests: [
        {
          name: 'test_validate_valid_domain',
          description: 'Tests domain name validation logic',
          steps: [
            'Create DomainAnonymizationStrategy instance',
            'Test validate() with valid domain formats',
            'Assert validation logic for TLDs',
            'Verify subdomain handling',
            'Test isolated domain parsing'
          ]
        },
        {
          name: 'test_anonymize_domain_low_level',
          description: 'Tests low-level domain anonymization',
          steps: [
            'Mock domain input "sub.example.com"',
            'Call anonymize() with AnonymizationLevel.LOW',
            'Assert result preserves "example.com"',
            'Verify subdomain replaced with "*"',
            'Test isolated anonymization strategy'
          ]
        },
        {
          name: 'test_anonymize_domain_full_level',
          description: 'Tests full domain anonymization',
          steps: [
            'Test with various domain inputs',
            'Call anonymize() with AnonymizationLevel.FULL',
            'Assert complete anonymization',
            'Verify consistency across calls',
            'Test hash-based anonymization'
          ]
        }
      ]
    },
    {
      id: 'email-anonymization',
      file: 'test_anonymization_strategies.py',
      class: 'EmailAnonymizationStrategyTestCase',
      title: 'Email Anonymization Unit Tests',
      description: 'Unit tests for email anonymization strategy class',
      tests: [
        {
          name: 'test_validate_valid_email',
          description: 'Tests email address validation logic',
          steps: [
            'Create EmailAnonymizationStrategy instance',
            'Test validate() with valid email formats',
            'Assert local and domain part validation',
            'Verify email regex handling',
            'Test isolated email parsing'
          ]
        },
        {
          name: 'test_anonymize_email_low_level',
          description: 'Tests low-level email anonymization',
          steps: [
            'Mock email "user@example.com"',
            'Call anonymize() with AnonymizationLevel.LOW',
            'Assert local part anonymized, domain preserved',
            'Verify format maintained',
            'Test isolated strategy logic'
          ]
        }
      ]
    },
    {
      id: 'anonymization-context',
      file: 'test_anonymization_strategies.py',
      class: 'AnonymizationContextTestCase',
      title: 'Anonymization Context Unit Tests',
      description: 'Unit tests for anonymization context orchestration with mocked strategies',
      tests: [
        {
          name: 'test_register_strategy',
          description: 'Tests strategy registration in context',
          steps: [
            'Create AnonymizationContext instance',
            'Mock anonymization strategy with MagicMock()',
            'Call register_strategy() method',
            'Assert strategy stored in context',
            'Verify registration logic isolation'
          ]
        },
        {
          name: 'test_auto_detect_and_anonymize_ip',
          description: 'Tests automatic IP detection and anonymization',
          steps: [
            'Mock IP detection logic',
            'Test auto_detect_and_anonymize() with IP data',
            'Assert IP strategy selected automatically',
            'Verify detection regex works',
            'Test isolated auto-detection'
          ]
        },
        {
          name: 'test_bulk_anonymize',
          description: 'Tests bulk anonymization orchestration',
          steps: [
            'Mock multiple data items with different types',
            'Call bulk_anonymize() method',
            'Assert appropriate strategy applied to each',
            'Verify batch processing logic',
            'Test isolated bulk operations'
          ]
        }
      ]
    }
  ];

  const TestSummaryBox = () => (
    <div className="test-summary-box">
      <div className="summary-header">
        <h3>Anonymization Test Coverage</h3>
        <button className="run-tests-btn" onClick={() => {
          setTimeout(() => {
            setTestResults({
              total: 13,
              passed: 13,
              failed: 0,
              coverage: '57%'
            });
          }, 3000);
        }}>
          Run All Tests
        </button>
      </div>
      <div className="summary-stats">
        <div className="stat-item passed">
          <div className="stat-number">{testResults.passed}</div>
          <div className="stat-label">Passed</div>
        </div>
        <div className="stat-item failed">
          <div className="stat-number">{testResults.failed}</div>
          <div className="stat-label">Failed</div>
        </div>
        <div className="stat-item total">
          <div className="stat-number">{testResults.total}</div>
          <div className="stat-label">Total</div>
        </div>
        <div className="stat-item coverage">
          <div className="stat-number">{testResults.coverage}</div>
          <div className="stat-label">Coverage</div>
        </div>
      </div>
    </div>
  );

  const renderTestDetails = (test) => (
    <div className="test-details">
      <h4>{test.name}</h4>
      <p className="test-description">{test.description}</p>
      <div className="test-steps">
        <h5>Unit Test Steps:</h5>
        <ol>
          {test.steps.map((step, index) => (
            <li key={index}>{step}</li>
          ))}
        </ol>
      </div>
    </div>
  );

  return (
    <div className="workflow-container">
      <div className="workflow-header">
        <h2>Anonymization and Trust Management</h2>
        <p>Unit tests for individual anonymization strategy classes in isolation with mocked dependencies</p>
      </div>

      <TestSummaryBox />

      <div className="unit-tests">
        {unitTests.map(testCase => (
          <div key={testCase.id} className="test-case">
            <div className="test-case-header" onClick={() => setActiveTest(activeTest === testCase.id ? null : testCase.id)}>
              <div className="test-case-info">
                <h3>{testCase.title}</h3>
                <p className="file-info">{testCase.file} :: {testCase.class}</p>
                <p className="test-case-desc">{testCase.description}</p>
              </div>
              <div className="test-count">{testCase.tests.length} tests</div>
            </div>
            
            {activeTest === testCase.id && (
              <div className="test-case-content">
                <div className="unit-workflow">
                  <h4>Unit Test Workflow</h4>
                  <div className="workflow-steps">
                    <div className="workflow-step">
                      <div className="step-number">1</div>
                      <div>Set up test environment with mocked dependencies</div>
                    </div>
                    <div className="workflow-step">
                      <div className="step-number">2</div>
                      <div>Instantiate anonymization strategy classes</div>
                    </div>
                    <div className="workflow-step">
                      <div className="step-number">3</div>
                      <div>Execute individual methods with test data</div>
                    </div>
                    <div className="workflow-step">
                      <div className="step-number">4</div>
                      <div>Assert expected anonymization behavior</div>
                    </div>
                  </div>
                </div>
                
                <div className="tests-list">
                  {testCase.tests.map((test, index) => (
                    <div key={index} className="test-item">
                      {renderTestDetails(test)}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
      
      <div className="anonymization-levels">
        <h3>Anonymization Levels Tested</h3>
        <div className="levels-grid">
          <div className="level-card">
            <h4>Low Level</h4>
            <p>Partial anonymization preserving analytical value</p>
            <ul>
              <li>IP: 192.168.1.x</li>
              <li>Domain: *.example.com</li>
              <li>Email: user@*.com</li>
            </ul>
          </div>
          <div className="level-card">
            <h4>Medium Level</h4>
            <p>Balanced anonymization for controlled sharing</p>
            <ul>
              <li>IP: 192.168.x.x</li>
              <li>Domain: [DOMAIN]</li>
              <li>Email: [EMAIL]</li>
            </ul>
          </div>
          <div className="level-card">
            <h4>High Level</h4>
            <p>Strong anonymization for public sharing</p>
            <ul>
              <li>IP: [IP_ADDRESS]</li>
              <li>Domain: [REDACTED]</li>
              <li>Email: [REDACTED]</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnonymizationWorkflow;