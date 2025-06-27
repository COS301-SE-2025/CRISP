import React, { useState } from 'react';
import './FlowComponent.css';

const IntegrationTestingFlow = () => {
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

  const integrationTestFlows = [
    {
      id: 'consumption-anonymization-integration',
      title: 'Consumption & Anonymization Integration',
      file: 'test_anonymization_service_integration.py',
      testClass: 'EndToEndAnonymizationTestCase',
      description: 'Integration tests for TAXII consumption with anonymization pipeline',
      integrationFlow: [
        {
          step: 1,
          component: 'TAXII Client',
          action: 'Connect to external TAXII server and discover collections',
          integration: 'Real TAXII server communication with mock responses for testing'
        },
        {
          step: 2,
          component: 'Feed Consumption Service',
          action: 'Poll TAXII collection and retrieve STIX objects',
          integration: 'OTXTaxiiService + StixTaxiiService working with real STIX data formats'
        },
        {
          step: 3,
          component: 'STIX Parser Integration',
          action: 'Parse STIX 1.x and 2.x objects into CRISP models',
          integration: 'STIX1Parser + StixFactory integration with database persistence'
        },
        {
          step: 4,
          component: 'Anonymization Pipeline',
          action: 'Apply anonymization strategies to consumed threat intelligence',
          integration: 'AnonymizationContext + Strategy patterns + Database transactions'
        },
        {
          step: 5,
          component: 'Repository Integration',
          action: 'Store anonymized indicators and TTPs with relationship tracking',
          integration: 'IndicatorRepository + TTPRepository + ThreatFeedRepository coordination'
        },
        {
          step: 6,
          component: 'Observer Notification',
          action: 'Trigger observer notifications for new threat intelligence',
          integration: 'Observer pattern + Email notifications + Real-time updates'
        }
      ],
      testCategories: [
        {
          category: 'End-to-End Anonymization Tests',
          tests: [
            'test_end_to_end_indicator_anonymization',
            'test_end_to_end_ttp_anonymization'
          ],
          description: 'Tests complete flow from TAXII consumption to anonymized storage'
        },
        {
          category: 'Service Integration Tests',
          tests: [
            'test_anonymize_indicator_description',
            'test_bulk_anonymize_indicators',
            'test_create_anonymized_indicator',
            'test_share_indicator_with_anonymization'
          ],
          description: 'Tests integration between IndicatorService and AnonymizationService'
        },
        {
          category: 'TTP Service Integration',
          tests: [
            'test_anonymize_ttp_description',
            'test_bulk_anonymize_ttps',
            'test_share_ttp_with_anonymization'
          ],
          description: 'Tests integration between TTPService and anonymization pipeline'
        }
      ]
    },
    {
      id: 'taxii-repository-integration',
      title: 'TAXII Repository Integration Tests',
      file: 'test_taxii_integration.py',
      testClass: 'TaxiiConsumptionIntegrationTestCase',
      description: 'Integration tests for TAXII services with repository pattern',
      integrationFlow: [
        {
          step: 1,
          component: 'TAXII Discovery',
          action: 'Discover available TAXII collections from multiple servers',
          integration: 'Multiple TAXII client implementations with unified interface'
        },
        {
          step: 2,
          component: 'Collection Polling',
          action: 'Poll collections with time-based filtering and pagination',
          integration: 'Polling logic + Database state management + Time filtering'
        },
        {
          step: 3,
          component: 'Content Processing',
          action: 'Process STIX content blocks with deduplication',
          integration: 'Content parsing + Duplicate detection + Database constraints'
        },
        {
          step: 4,
          component: 'Repository Coordination',
          action: 'Coordinate between multiple repositories for data consistency',
          integration: 'Repository pattern + Transaction management + Referential integrity'
        },
        {
          step: 5,
          component: 'Error Recovery',
          action: 'Handle network failures and data corruption gracefully',
          integration: 'Retry mechanisms + Error logging + State recovery'
        }
      ],
      testCategories: [
        {
          category: 'Feed Consumption Integration',
          tests: [
            'test_otx_feed_consumption',
            'test_stix2_feed_consumption',
            'test_deduplicate_indicators'
          ],
          description: 'Tests integration of different TAXII feed types with repositories'
        },
        {
          category: 'Repository Usage Tests',
          tests: [
            'test_repository_usage',
            'test_force_days_parameter'
          ],
          description: 'Tests proper usage of repository pattern in TAXII services'
        }
      ]
    },
    {
      id: 'end-to-end-consumption',
      title: 'End-to-End Consumption Integration',
      file: 'test_end_to_end.py',
      testClass: 'EndToEndConsumptionTestCase',
      description: 'Complete end-to-end integration tests for threat feed consumption',
      integrationFlow: [
        {
          step: 1,
          component: 'API Gateway',
          action: 'Receive consumption request via REST API',
          integration: 'Django views + Serializers + Authentication middleware'
        },
        {
          step: 2,
          component: 'Service Layer',
          action: 'Route request to appropriate TAXII service',
          integration: 'Service discovery + Configuration management + Load balancing'
        },
        {
          step: 3,
          component: 'External Integration',
          action: 'Connect to external threat intelligence providers',
          integration: 'Multiple TAXII standards + Authentication + Rate limiting'
        },
        {
          step: 4,
          component: 'Data Processing Pipeline',
          action: 'Process, validate, and transform incoming threat data',
          integration: 'Validation + Transformation + Enrichment + Quality checks'
        },
        {
          step: 5,
          component: 'Storage Integration',
          action: 'Persist data with relationships and metadata',
          integration: 'Database transactions + Indexing + Relationship management'
        },
        {
          step: 6,
          component: 'API Response',
          action: 'Return comprehensive consumption statistics',
          integration: 'Response serialization + Metrics collection + Logging'
        }
      ],
      testCategories: [
        {
          category: 'API Endpoint Integration',
          tests: [
            'test_consume_endpoint',
            'test_consume_endpoint_with_parameters',
            'test_consume_endpoint_error_handling',
            'test_status_endpoint',
            'test_available_collections_endpoint'
          ],
          description: 'Tests API endpoints with complete request/response cycle'
        },
        {
          category: 'Batch Processing Integration',
          tests: [
            'test_batch_feed_consumption',
            'test_otx_feed_end_to_end',
            'test_stix2_feed_end_to_end'
          ],
          description: 'Tests batch processing of multiple feeds simultaneously'
        }
      ]
    },
    {
      id: 'management-command-integration',
      title: 'Management Command Integration',
      file: 'test_management_commands.py',
      testClass: 'TaxiiOperationsCommandTestCase',
      description: 'Integration tests for Django management commands with TAXII operations',
      integrationFlow: [
        {
          step: 1,
          component: 'Command Line Interface',
          action: 'Parse command arguments and options',
          integration: 'Django management commands + Argument parsing + Validation'
        },
        {
          step: 2,
          component: 'Service Integration',
          action: 'Initialize and configure TAXII services',
          integration: 'Service instantiation + Configuration loading + Dependency injection'
        },
        {
          step: 3,
          component: 'Operation Execution',
          action: 'Execute TAXII operations with proper error handling',
          integration: 'Service methods + Exception handling + Progress reporting'
        },
        {
          step: 4,
          component: 'Output Generation',
          action: 'Generate formatted output and status reports',
          integration: 'Output formatting + Status tracking + Log integration'
        }
      ],
      testCategories: [
        {
          category: 'TAXII Operations Commands',
          tests: [
            'test_add_command',
            'test_consume_command',
            'test_consume_command_nonexistent_feed',
            'test_discover_command',
            'test_discover_command_error',
            'test_invalid_command'
          ],
          description: 'Tests Django management commands for TAXII operations'
        },
        {
          category: 'Test Command Integration',
          tests: [
            'test_consume_option',
            'test_consume_option_error',
            'test_consume_without_collection',
            'test_list_collections',
            'test_list_collections_error'
          ],
          description: 'Tests specialized testing commands with TAXII integration'
        }
      ]
    }
  ];

  const TestSummaryBox = () => (
    <div className="test-summary-box">
      <div className="summary-header">
        <h3>Integration Test Coverage</h3>
        <button className="run-tests-btn" onClick={() => {
          setIsRunningAllTests(true);
          setTimeout(() => {
            setTestSummary({
              total: 130,
              passed: 130,
              failed: 0,
              coverage: '85%'
            });
            setIsRunningAllTests(false);
          }, 5000);
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
    
    // Simulate integration test execution with realistic timing
    await new Promise(resolve => setTimeout(resolve, 4000));
    
    // Simulate test results based on the flow
    const mockResults = {
      'consumption-anonymization-integration': {
        status: 'PASSED',
        duration: '12.45s',
        tests_run: 11,
        tests_passed: 11,
        tests_failed: 0,
        coverage: '88%',
        details: [
          { method: 'test_end_to_end_indicator_anonymization', status: 'PASSED', duration: '3.21s', assertion: '✅ Full pipeline: TAXII → STIX Parser → Anonymization → Storage → Verification complete' },
          { method: 'test_end_to_end_ttp_anonymization', status: 'PASSED', duration: '2.89s', assertion: '✅ TTP pipeline: STIX 2.x → MITRE ATT&CK mapping → Anonymization → Repository storage verified' },
          { method: 'test_anonymize_indicator_description', status: 'PASSED', duration: '1.45s', assertion: '✅ IndicatorService + AnonymizationService integration: Description anonymized successfully' },
          { method: 'test_bulk_anonymize_indicators', status: 'PASSED', duration: '2.78s', assertion: '✅ Bulk processing: 50 indicators anonymized in batch with transaction consistency' },
          { method: 'test_create_anonymized_indicator', status: 'PASSED', duration: '1.12s', assertion: '✅ Factory + Anonymization: New indicator created with applied anonymization strategies' }
        ]
      },
      'taxii-repository-integration': {
        status: 'PASSED',
        duration: '8.92s',
        tests_run: 6,
        tests_passed: 6,
        tests_failed: 0,
        coverage: '91%',
        details: [
          { method: 'test_otx_feed_consumption', status: 'PASSED', duration: '2.34s', assertion: '✅ OTX TAXII 1.x integration: Feed consumed, parsed, and stored with repository coordination' },
          { method: 'test_stix2_feed_consumption', status: 'PASSED', duration: '1.98s', assertion: '✅ STIX 2.x TAXII integration: Collection polling and repository persistence verified' },
          { method: 'test_deduplicate_indicators', status: 'PASSED', duration: '1.67s', assertion: '✅ Deduplication logic: Duplicate indicators handled correctly across repositories' },
          { method: 'test_repository_usage', status: 'PASSED', duration: '1.45s', assertion: '✅ Repository pattern: All repositories used correctly in TAXII service integration' },
          { method: 'test_force_days_parameter', status: 'PASSED', duration: '1.48s', assertion: '✅ Time filtering: force_days parameter working with repository queries' }
        ]
      },
      'end-to-end-consumption': {
        status: 'PASSED',
        duration: '15.23s',
        tests_run: 10,
        tests_passed: 10,
        tests_failed: 0,
        coverage: '87%',
        details: [
          { method: 'test_consume_endpoint', status: 'PASSED', duration: '2.45s', assertion: '✅ API endpoint: Complete consumption flow from HTTP request to database storage' },
          { method: 'test_consume_endpoint_with_parameters', status: 'PASSED', duration: '1.89s', assertion: '✅ Parameterized consumption: Query parameters properly integrated with service layer' },
          { method: 'test_consume_endpoint_error_handling', status: 'PASSED', duration: '1.67s', assertion: '✅ Error handling: API gracefully handles service failures and returns proper responses' },
          { method: 'test_batch_feed_consumption', status: 'PASSED', duration: '4.12s', assertion: '✅ Batch processing: Multiple external feeds consumed simultaneously with coordination' },
          { method: 'test_otx_feed_end_to_end', status: 'PASSED', duration: '2.89s', assertion: '✅ OTX end-to-end: Complete flow from API to external OTX TAXII to database verified' }
        ]
      },
      'management-command-integration': {
        status: 'PASSED',
        duration: '6.78s',
        tests_run: 12,
        tests_passed: 12,
        tests_failed: 0,
        coverage: '89%',
        details: [
          { method: 'test_add_command', status: 'PASSED', duration: '0.89s', assertion: '✅ Add command: Management command integration with service layer successful' },
          { method: 'test_consume_command', status: 'PASSED', duration: '1.23s', assertion: '✅ Consume command: CLI integration with TAXII consumption services verified' },
          { method: 'test_discover_command', status: 'PASSED', duration: '1.45s', assertion: '✅ Discover command: External service discovery integrated with command interface' },
          { method: 'test_list_collections', status: 'PASSED', duration: '0.98s', assertion: '✅ List collections: Command integration with collection discovery services working' }
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
          <h4>Integration Test Results</h4>
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
          <h5>Integration Test Results:</h5>
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

  const renderIntegrationFlow = (flow) => (
    <div className="integration-flow">
      <h4>Integration Test Flow</h4>
      <div className="flow-steps">
        {flow.integrationFlow.map((step, index) => (
          <div key={index} className="flow-step">
            <div className="step-header">
              <div className="step-number">{step.step}</div>
              <div className="step-info">
                <div className="step-component">{step.component}</div>
                <div className="step-action">{step.action}</div>
              </div>
            </div>
            <div className="step-integration">
              <strong>Integration:</strong> {step.integration}
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderTestCategories = (flow) => (
    <div className="test-categories-section">
      <h4>Test Categories</h4>
      <div className="test-class-info">
        <span className="test-file">📁 {flow.file}</span>
        <span className="test-class">🧪 {flow.testClass}</span>
      </div>
      <div className="test-categories">
        {flow.testCategories.map((category, index) => (
          <div key={index} className="test-category">
            <div className="category-title">{category.category}</div>
            <div className="category-description">{category.description}</div>
            <div className="category-tests">
              {category.tests.map((test, testIndex) => (
                <div key={testIndex} className="test-item">
                  <div className="test-method">🔧 {test}</div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="flow-container">
      <div className="flow-header">
        <h2>Integration Tests for Consumption & Anonymization</h2>
        <p>End-to-end integration testing flows for TAXII consumption, STIX processing, and anonymization pipeline</p>
      </div>

      <TestSummaryBox />

      <div className="test-flows">
        {integrationTestFlows.map(flow => (
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
                    {runningTest === flow.id ? 'Running Integration Tests...' : 'Run Integration Tests'}
                  </button>
                </div>
                {renderIntegrationFlow(flow)}
                {renderTestCategories(flow)}
                {renderTestResults(flow.id)}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default IntegrationTestingFlow;