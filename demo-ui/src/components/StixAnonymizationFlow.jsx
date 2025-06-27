import React, { useState } from 'react';
import './FlowComponent.css';

const StixAnonymizationFlow = () => {
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
      id: 'ip-anonymization',
      title: 'IP Address Anonymization Strategy',
      file: 'test_anonymization_strategies.py',
      testClass: 'IPAddressAnonymizationStrategyTestCase',
      description: 'Unit test flow for anonymizing IP addresses in STIX objects',
      backendFlow: [
        {
          step: 1,
          component: 'Frontend Request',
          action: 'User submits STIX object with IP: "192.168.1.100"',
          code: 'POST /api/stix/anonymize\n{\n  "stix_object": {...},\n  "level": "MEDIUM"\n}'
        },
        {
          step: 2,
          component: 'AnonymizationService',
          action: 'Detect data types and select IP strategy',
          code: 'strategy = IPAddressAnonymizationStrategy()\nresult = strategy.anonymize("192.168.1.100", AnonymizationLevel.MEDIUM)'
        },
        {
          step: 3,
          component: 'IPAddressAnonymizationStrategy',
          action: 'Apply medium-level anonymization (preserve 2 octets)',
          code: 'def anonymize_ipv4_medium_level(self, ip):\n    octets = ip.split(".")\n    return f"{octets[0]}.{octets[1]}.x.x"'
        },
        {
          step: 4,
          component: 'Response Generation',
          action: 'Return anonymized STIX object',
          code: 'return {\n  "anonymized_stix": {...},\n  "original_ip": "192.168.1.100",\n  "anonymized_ip": "192.168.x.x"\n}'
        }
      ],
      unitTests: [
        {
          method: 'test_anonymize_ipv4_low_level',
          assertion: 'Preserves first 3 octets: "192.168.1.x"',
          mock: 'No external dependencies - pure logic test'
        },
        {
          method: 'test_anonymize_ipv4_medium_level', 
          assertion: 'Preserves first 2 octets: "192.168.x.x"',
          mock: 'No external dependencies - pure logic test'
        },
        {
          method: 'test_anonymize_ipv4_full_level',
          assertion: 'Consistent hash-based anonymization',
          mock: 'Mock hash function for deterministic results'
        }
      ]
    },
    {
      id: 'stix-object-anonymization',
      title: 'Complete STIX Object Anonymization',
      file: 'test_anonymization_strategies.py',
      testClass: 'AnonymizationContextTestCase',
      description: 'End-to-end flow for anonymizing complete STIX objects',
      backendFlow: [
        {
          step: 1,
          component: 'Frontend Request',
          action: 'User requests anonymization of STIX bundle',
          code: 'POST /api/stix/anonymize-bundle\n{\n  "stix_bundle": {...},\n  "anonymization_level": "HIGH"\n}'
        },
        {
          step: 2,
          component: 'AnonymizationContext',
          action: 'Register all available strategies',
          code: 'context = AnonymizationContext()\ncontext.register_strategy(DataType.IP_ADDRESS, IPAddressAnonymizationStrategy())\ncontext.register_strategy(DataType.DOMAIN, DomainAnonymizationStrategy())'
        },
        {
          step: 3,
          component: 'Auto-Detection Engine',
          action: 'Scan STIX object for sensitive data types',
          code: 'def auto_detect_and_anonymize(self, data, level):\n    if self.ip_pattern.match(data):\n        return self.strategies[DataType.IP_ADDRESS].anonymize(data, level)\n    elif self.domain_pattern.match(data):\n        return self.strategies[DataType.DOMAIN].anonymize(data, level)'
        },
        {
          step: 4,
          component: 'Bulk Processing',
          action: 'Apply anonymization to all detected elements',
          code: 'def bulk_anonymize(self, items, level):\n    results = []\n    for item in items:\n        anonymized = self.auto_detect_and_anonymize(item, level)\n        results.append(anonymized)\n    return results'
        },
        {
          step: 5,
          component: 'Frontend Response',
          action: 'Return anonymized STIX bundle with statistics',
          code: 'return {\n  "anonymized_bundle": {...},\n  "statistics": {\n    "ips_anonymized": 5,\n    "domains_anonymized": 3,\n    "emails_anonymized": 2\n  }\n}'
        }
      ],
      unitTests: [
        {
          method: 'test_register_strategy',
          assertion: 'Strategy properly registered in context',
          mock: 'MagicMock() for strategy instances'
        },
        {
          method: 'test_auto_detect_and_anonymize_ip',
          assertion: 'IP addresses automatically detected and anonymized',
          mock: 'Mock regex patterns for controlled detection'
        },
        {
          method: 'test_anonymize_stix_object',
          assertion: 'Complete STIX object anonymized while preserving structure',
          mock: 'Mock STIX object with controllable properties'
        }
      ]
    },
    {
      id: 'domain-anonymization',
      title: 'Domain Name Anonymization Strategy',
      file: 'test_anonymization_strategies.py',
      testClass: 'DomainAnonymizationStrategyTestCase',
      description: 'Unit test flow for anonymizing domain names in threat intelligence',
      backendFlow: [
        {
          step: 1,
          component: 'Frontend Request',
          action: 'User submits domain for anonymization',
          code: 'POST /api/anonymize/domain\n{\n  "domain": "malicious.example.com",\n  "level": "LOW"\n}'
        },
        {
          step: 2,
          component: 'DomainAnonymizationStrategy',
          action: 'Validate domain format and apply strategy',
          code: 'def anonymize_domain_low_level(self, domain):\n    parts = domain.split(".")\n    if len(parts) >= 3:\n        return f"*.{parts[-2]}.{parts[-1]}"\n    return domain'
        },
        {
          step: 3,
          component: 'Validation Engine',
          action: 'Ensure anonymization preserves analytical value',
          code: 'def validate_domain(self, domain):\n    domain_pattern = r"^[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"\n    return bool(re.match(domain_pattern, domain))'
        },
        {
          step: 4,
          component: 'Frontend Response',
          action: 'Return anonymized domain with metadata',
          code: 'return {\n  "original": "malicious.example.com",\n  "anonymized": "*.example.com",\n  "level": "LOW",\n  "preserved_parts": ["example", "com"]\n}'
        }
      ],
      unitTests: [
        {
          method: 'test_anonymize_domain_low_level',
          assertion: 'Preserves second-level domain and TLD',
          mock: 'No external dependencies - pure string manipulation'
        },
        {
          method: 'test_anonymize_domain_medium_level',
          assertion: 'Preserves only TLD for medium anonymization',
          mock: 'No external dependencies - deterministic logic'
        },
        {
          method: 'test_validate_domain',
          assertion: 'Domain format validation works correctly',
          mock: 'Mock regex patterns for edge case testing'
        }
      ]
    }
  ];

  const runTest = async (flowId) => {
    setRunningTest(flowId);
    
    // Show "before" state
    setTestResults(prev => ({
      ...prev,
      [flowId]: {
        status: 'RUNNING',
        phase: 'BEFORE',
        message: 'Setting up test environment and mocking dependencies...'
      }
    }));
    
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Show "during" state  
    setTestResults(prev => ({
      ...prev,
      [flowId]: {
        status: 'RUNNING',
        phase: 'EXECUTING',
        message: 'Running unit tests and validating assertions...'
      }
    }));
    
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Simulate test results based on the flow
    const mockResults = {
      'ip-anonymization': {
        status: 'PASSED',
        duration: '1.23s',
        tests_run: 3,
        tests_passed: 3,
        tests_failed: 0,
        coverage: '95%',
        details: [
          { method: 'test_anonymize_ipv4_low_level', status: 'PASSED', duration: '0.45s', assertion: '✅ Input: "192.168.1.100" → Expected: "192.168.1.x" → Actual: "192.168.1.x" (PASSED)' },
          { method: 'test_anonymize_ipv4_medium_level', status: 'PASSED', duration: '0.38s', assertion: '✅ Input: "192.168.1.100" → Expected: "192.168.x.x" → Actual: "192.168.x.x" (PASSED)' },
          { method: 'test_anonymize_ipv4_full_level', status: 'PASSED', duration: '0.40s', assertion: '✅ Input: "192.168.1.100" → Expected: "hash_a1b2c3d4" → Actual: "hash_a1b2c3d4" (Consistent hash verified)' }
        ]
      },
      'stix-object-anonymization': {
        status: 'PASSED',
        duration: '2.15s',
        tests_run: 3,
        tests_passed: 3,
        tests_failed: 0,
        coverage: '92%',
        details: [
          { method: 'test_register_strategy', status: 'PASSED', duration: '0.67s', assertion: '✅ Strategy registered successfully in context with proper type validation' },
          { method: 'test_auto_detect_and_anonymize_ip', status: 'PASSED', duration: '0.89s', assertion: '✅ Input: ["192.168.1.1", "malicious.com"] → Expected: ["192.168.x.x", "malicious.com"] → Actual: ["192.168.x.x", "malicious.com"] (IP auto-detected)' },
          { method: 'test_anonymize_stix_object', status: 'PASSED', duration: '0.59s', assertion: '✅ STIX object structure preserved during anonymization with correct pattern transformation' }
        ]
      },
      'domain-anonymization': {
        status: 'PASSED',
        duration: '0.89s',
        tests_run: 3,
        tests_passed: 3,
        tests_failed: 0,
        coverage: '98%',
        details: [
          { method: 'test_anonymize_domain_low_level', status: 'PASSED', duration: '0.31s', assertion: '✅ Input: "malicious.example.com" → Expected: "*.example.com" → Actual: "*.example.com" (PASSED)' },
          { method: 'test_anonymize_domain_medium_level', status: 'PASSED', duration: '0.29s', assertion: '✅ Input: "malicious.example.com" → Expected: "*.com" → Actual: "*.com" (TLD preserved)' },
          { method: 'test_validate_domain', status: 'PASSED', duration: '0.29s', assertion: '✅ Input: ["example.com", "invalid", "test.co.uk"] → Expected: [True, False, True] → Actual: [True, False, True] (Validation working)' }
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

    // Show running state with before/during phases
    if (result.status === 'RUNNING') {
      return (
        <div className="test-results running">
          <div className="test-results-header">
            <h4>Test Execution in Progress</h4>
            <div className="test-status running">
              {result.phase}
            </div>
          </div>
          <div className="test-progress">
            <div className="progress-message">
              <span className="progress-icon">⚡</span>
              {result.message}
            </div>
            <div className="progress-bar">
              <div className={`progress-fill ${result.phase.toLowerCase()}`}></div>
            </div>
          </div>
        </div>
      );
    }

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

  const TestSummaryBox = () => (
    <div className="test-summary-box">
      <div className="summary-header">
        <h3>STIX Anonymization Test Coverage</h3>
        <button className="run-tests-btn" onClick={() => {
          setIsRunningAllTests(true);
          setTimeout(() => {
            setTestSummary({
              total: 13,
              passed: 13,
              failed: 0,
              coverage: '57%'
            });
            setIsRunningAllTests(false);
          }, 3000);
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
        <h2>Unit Tests for STIX Anonymization</h2>
        <p>Backend to Frontend unit test flows demonstrating STIX object anonymization with strategy patterns</p>
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

export default StixAnonymizationFlow;