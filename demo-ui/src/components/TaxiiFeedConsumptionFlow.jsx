import React, { useState } from 'react';
import './FlowComponent.css';

const TaxiiFeedConsumptionFlow = () => {
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
      id: 'otx-taxii-consumption',
      title: 'OTX TAXII 1.x Feed Consumption',
      file: 'test_taxii_service.py',
      testClass: 'OTXTaxiiServiceTestCase',
      description: 'Unit test flow for consuming AlienVault OTX TAXII 1.x feeds',
      backendFlow: [
        {
          step: 1,
          component: 'Frontend Request',
          action: 'User initiates feed consumption from UI',
          code: 'POST /api/feeds/consume\n{\n  "feed_id": "otx-feed-123",\n  "collection": "user_AlienVault",\n  "limit": 100\n}'
        },
        {
          step: 2,
          component: 'OTXTaxiiService',
          action: 'Initialize TAXII client with credentials',
          code: 'def get_client(self):\n    client = create_client(\n        url=self.feed.taxii_server_url,\n        username=self.feed.taxii_username,\n        password=self.feed.taxii_password\n    )\n    return client'
        },
        {
          step: 3,
          component: 'Collection Discovery',
          action: 'Discover and validate available collections',
          code: 'def get_collections(self):\n    client = self.get_client()\n    collections = client.get_collections()\n    return [{\n        "name": col.name,\n        "description": col.description,\n        "available": col.available\n    } for col in collections]'
        },
        {
          step: 4,
          component: 'Content Polling',
          action: 'Poll collection for STIX content blocks',
          code: 'def poll_collection(self, collection_name, begin_date=None):\n    client = self.get_client()\n    collection = client.get_collection(collection_name)\n    content_blocks = collection.poll(\n        begin_date=begin_date,\n        content_bindings=[CB_STIX_XML_111]\n    )\n    return content_blocks'
        },
        {
          step: 5,
          component: 'STIX Parsing',
          action: 'Parse STIX 1.x content into indicators and TTPs',
          code: 'def consume_feed(self, threat_feed_id):\n    content_blocks = self.poll_collection(collection_name)\n    stats = {"indicators_created": 0, "ttp_created": 0}\n    \n    for block in content_blocks:\n        parser_result = STIX1Parser.parse_content_block(\n            block.content, threat_feed\n        )\n        stats["indicators_created"] += parser_result["indicators_created"]\n        stats["ttp_created"] += parser_result["ttp_created"]\n    \n    return stats'
        },
        {
          step: 6,
          component: 'Frontend Response',
          action: 'Return consumption statistics to UI',
          code: 'return {\n  "success": true,\n  "statistics": {\n    "indicators_created": 15,\n    "indicators_updated": 3,\n    "ttp_created": 8,\n    "ttp_updated": 1,\n    "total_processed": 27\n  },\n  "last_sync": "2024-01-15T10:30:00Z"\n}'
        }
      ],
      unitTests: [
        {
          method: 'test_get_client',
          assertion: 'TAXII client created with correct credentials',
          mock: '@patch("taxii.create_client") to mock external TAXII connections'
        },
        {
          method: 'test_get_collections',
          assertion: 'Available collections discovered and formatted correctly',
          mock: 'Mock TAXII client response with controlled collection data'
        },
        {
          method: 'test_poll_collection',
          assertion: 'Content blocks retrieved from specified date range',
          mock: 'Mock collection.poll() with predefined STIX content blocks'
        },
        {
          method: 'test_consume_feed',
          assertion: 'Statistics reflect actual parsing results',
          mock: 'Mock STIX1Parser.parse_content_block() with controlled stats'
        }
      ]
    },
    {
      id: 'stix2-taxii-consumption',
      title: 'STIX 2.x TAXII Feed Consumption',
      file: 'test_taxii_service.py',
      testClass: 'StixTaxiiServiceTestCase',
      description: 'Unit test flow for consuming STIX 2.x TAXII feeds',
      backendFlow: [
        {
          step: 1,
          component: 'Frontend Request',
          action: 'User configures STIX 2.x feed consumption',
          code: 'POST /api/feeds/stix2/consume\n{\n  "feed_id": "stix2-feed-456",\n  "api_root": "/taxii2/api/v2",\n  "collection_id": "threat-intel-collection"\n}'
        },
        {
          step: 2,
          component: 'StixTaxiiService',
          action: 'Initialize TAXII 2.x collection connection',
          code: 'def discover_collections(self):\n    collection_url = f"{self.feed.taxii_server_url}/{self.feed.taxii_api_root}/collections/{self.feed.taxii_collection_id}/"\n    collection = Collection(\n        collection_url,\n        user=self.feed.taxii_username,\n        password=self.feed.taxii_password\n    )\n    return collection'
        },
        {
          step: 3,
          component: 'STIX Object Retrieval',
          action: 'Fetch STIX 2.x objects from collection',
          code: 'def consume_feed(self, threat_feed_id):\n    collection = self.discover_collections()\n    \n    # Get objects from collection\n    stix_objects = collection.get_objects(\n        limit=self.batch_size,\n        added_after=self.last_sync_date\n    )\n    \n    return self.process_stix_objects(stix_objects["objects"])'
        },
        {
          step: 4,
          component: 'STIX 2.x Processing',
          action: 'Parse and convert STIX 2.x objects to internal format',
          code: 'def process_stix_objects(self, stix_objects):\n    stats = {"indicators_created": 0, "ttp_created": 0}\n    \n    for stix_obj in stix_objects:\n        parsed_obj = stix2_parse(stix_obj)\n        \n        if parsed_obj.type == "indicator":\n            indicator = StixIndicatorCreator.create_from_stix20_indicator(parsed_obj)\n            stats["indicators_created"] += 1\n        elif parsed_obj.type == "attack-pattern":\n            ttp = StixTTPCreator.create_from_stix20_ttp(parsed_obj)\n            stats["ttp_created"] += 1\n    \n    return stats'
        },
        {
          step: 5,
          component: 'Frontend Response',
          action: 'Return STIX 2.x consumption results',
          code: 'return {\n  "success": true,\n  "stix_version": "2.1",\n  "statistics": {\n    "indicators_created": 12,\n    "attack_patterns_created": 5,\n    "malware_created": 3,\n    "total_objects": 20\n  }\n}'
        }
      ],
      unitTests: [
        {
          method: 'test_discover_collections',
          assertion: 'TAXII 2.x collection properly initialized with authentication',
          mock: '@patch("taxii2client.Collection") to mock TAXII 2.x client'
        },
        {
          method: 'test_consume_feed',
          assertion: 'STIX 2.x objects retrieved and processed correctly',
          mock: 'Mock collection.get_objects() with controlled STIX 2.x data'
        },
        {
          method: 'test_process_stix_objects',
          assertion: 'Different STIX object types handled appropriately',
          mock: 'Mock stix2_parse() and factory methods for object creation'
        }
      ]
    },
    {
      id: 'feed-status-monitoring',
      title: 'Feed Status and Error Handling',
      file: 'test_taxii_service.py',
      testClass: 'TaxiiServiceErrorHandlingTestCase',
      description: 'Unit test flow for monitoring feed status and handling errors',
      backendFlow: [
        {
          step: 1,
          component: 'Frontend Request',
          action: 'User checks feed consumption status',
          code: 'GET /api/feeds/status/{feed_id}\n{\n  "include_errors": true,\n  "include_statistics": true\n}'
        },
        {
          step: 2,
          component: 'Feed Status Service',
          action: 'Gather feed health and consumption metrics',
          code: 'def get_feed_status(self, feed_id):\n    feed = ThreatFeed.objects.get(id=feed_id)\n    \n    status = {\n        "last_sync": feed.last_sync,\n        "total_indicators": feed.indicators.count(),\n        "total_ttps": feed.ttps.count(),\n        "health_status": self.check_feed_health(feed)\n    }\n    \n    return status'
        },
        {
          step: 3,
          component: 'Error Detection',
          action: 'Check for consumption errors and connectivity issues',
          code: 'def check_feed_health(self, feed):\n    try:\n        # Test TAXII connection\n        service = self.get_service_for_feed(feed)\n        collections = service.get_collections()\n        \n        if not collections:\n            return {"status": "warning", "message": "No collections available"}\n        \n        return {"status": "healthy", "last_check": timezone.now()}\n    except Exception as e:\n        return {"status": "error", "message": str(e)}'
        },
        {
          step: 4,
          component: 'Frontend Response',
          action: 'Return comprehensive feed status',
          code: 'return {\n  "feed_id": feed_id,\n  "name": "OTX Threat Feed",\n  "status": "healthy",\n  "last_sync": "2024-01-15T10:30:00Z",\n  "statistics": {\n    "total_indicators": 1205,\n    "total_ttps": 89,\n    "last_24h_added": 15\n  },\n  "health_check": {\n    "connectivity": "ok",\n    "authentication": "ok",\n    "collections_available": 3\n  }\n}'
        }
      ],
      unitTests: [
        {
          method: 'test_get_feed_status',
          assertion: 'Feed status calculated correctly from database',
          mock: 'Mock ThreatFeed model with controlled indicator/TTP counts'
        },
        {
          method: 'test_check_feed_health',
          assertion: 'Health check detects connectivity and authentication issues',
          mock: 'Mock TAXII service calls to simulate various error conditions'
        },
        {
          method: 'test_error_handling',
          assertion: 'Service gracefully handles TAXII server errors',
          mock: 'Mock TAXII exceptions and network timeout scenarios'
        }
      ]
    }
  ];

  const TestSummaryBox = () => (
    <div className="test-summary-box">
      <div className="summary-header">
        <h3>TAXII Service Test Coverage</h3>
        <button className="run-tests-btn" onClick={() => {
          setIsRunningAllTests(true);
          // Simulate test run
          setTimeout(() => {
            setTestSummary({
              total: 125,
              passed: 125,
              failed: 0,
              coverage: '81%'
            });
            setIsRunningAllTests(false);
          }, 6000);
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
    await new Promise(resolve => setTimeout(resolve, 2500));
    
    // Simulate test results based on the flow
    const mockResults = {
      'otx-taxii-consumption': {
        status: 'PASSED',
        duration: '3.45s',
        tests_run: 4,
        tests_passed: 4,
        tests_failed: 0,
        coverage: '88%',
        details: [
          { method: 'test_get_client', status: 'PASSED', duration: '0.89s', assertion: '✅ Input: {"url": "https://otx.alienvault.com/taxii/", "username": "test", "password": "***"} → Expected: <TaxiiClient connected=True> → Actual: <TaxiiClient connected=True> (Connection successful)' },
          { method: 'test_get_collections', status: 'PASSED', duration: '1.23s', assertion: '✅ Input: <TaxiiClient> → Expected: ["user_AlienVault", "user_AlienVault_Pulse"] → Actual: ["user_AlienVault", "user_AlienVault_Pulse"] (Collections discovered)' },
          { method: 'test_poll_collection', status: 'PASSED', duration: '0.67s', assertion: '✅ Input: {"collection": "user_AlienVault", "begin_date": "2024-01-01"} → Expected: 15 content blocks → Actual: 15 content blocks (Poll successful)' },
          { method: 'test_consume_feed', status: 'PASSED', duration: '0.66s', assertion: '✅ Input: 15 STIX content blocks → Expected: {"indicators": 27, "ttps": 8} → Actual: {"indicators": 27, "ttps": 8} (Statistics match)' }
        ]
      },
      'stix2-taxii-consumption': {
        status: 'PASSED',
        duration: '2.78s',
        tests_run: 3,
        tests_passed: 3,
        tests_failed: 0,
        coverage: '92%',
        details: [
          { method: 'test_discover_collections', status: 'PASSED', duration: '0.95s', assertion: '✅ Input: {"url": "https://cti-taxii.mitre.org/stix/collections/", "auth": "bearer_token"} → Expected: <Collection id="enterprise-attack"> → Actual: <Collection id="enterprise-attack"> (TAXII 2.x connected)' },
          { method: 'test_consume_feed', status: 'PASSED', duration: '1.12s', assertion: '✅ Input: Collection.get_objects(limit=100) → Expected: 20 STIX 2.x objects → Actual: 20 STIX 2.x objects (Retrieved successfully)' },
          { method: 'test_process_stix_objects', status: 'PASSED', duration: '0.71s', assertion: '✅ Input: [{"type": "indicator"}, {"type": "attack-pattern"}, {"type": "malware"}] → Expected: {"indicators": 1, "attack_patterns": 1, "malware": 1} → Actual: {"indicators": 1, "attack_patterns": 1, "malware": 1} (All types handled)' }
        ]
      },
      'feed-status-monitoring': {
        status: 'PASSED',
        duration: '1.89s',
        tests_run: 3,
        tests_passed: 3,
        tests_failed: 0,
        coverage: '94%',
        details: [
          { method: 'test_get_feed_status', status: 'PASSED', duration: '0.45s', assertion: '✅ Input: ThreatFeed(id="otx-feed-123") → Expected: {"indicators": 1205, "ttps": 89, "status": "healthy"} → Actual: {"indicators": 1205, "ttps": 89, "status": "healthy"} (Status accurate)' },
          { method: 'test_check_feed_health', status: 'PASSED', duration: '0.78s', assertion: '✅ Input: Feed health check → Expected: {"connectivity": "ok", "auth": "ok", "collections": 3} → Actual: {"connectivity": "ok", "auth": "ok", "collections": 3} (Health verified)' },
          { method: 'test_error_handling', status: 'PASSED', duration: '0.66s', assertion: '✅ Input: Simulated TAXII timeout → Expected: {"status": "error", "retry_scheduled": True} → Actual: {"status": "error", "retry_scheduled": True} (Error handled gracefully)' }
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
        <h2>Unit Testing for TAXII Feed Consumption</h2>
        <p>Backend to Frontend unit test flows for consuming threat intelligence from TAXII feeds</p>
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

export default TaxiiFeedConsumptionFlow;