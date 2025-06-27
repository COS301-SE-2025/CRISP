import React, { useState } from 'react';
import './FlowComponent.css';

const StixPublicationFlow = () => {
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
      id: 'stix-indicator-publication',
      title: 'STIX Indicator Factory and Publication',
      file: 'test_stix_factory.py',
      testClass: 'StixIndicatorCreatorTestCase',
      description: 'Unit test flow for creating and publishing STIX indicators using factory pattern',
      backendFlow: [
        {
          step: 1,
          component: 'Frontend Request',
          action: 'User selects indicators for STIX publication',
          code: 'POST /api/stix/publish/indicators\n{\n  "indicator_ids": ["ind-1", "ind-2", "ind-3"],\n  "stix_version": "2.1",\n  "bundle_title": "Threat Intelligence Package",\n  "target_format": "stix_bundle"\n}'
        },
        {
          step: 2,
          component: 'STIX Indicator Creator Factory',
          action: 'Convert internal indicators to STIX format',
          code: 'def create_stix_object_from_indicator(self, indicator):\n    stix_indicator = {\n        "type": "indicator",\n        "spec_version": "2.1",\n        "id": f"indicator--{indicator.stix_id}",\n        "created": indicator.created_at.isoformat(),\n        "modified": indicator.updated_at.isoformat(),\n        "pattern": self.create_stix_pattern(indicator),\n        "labels": self.get_indicator_labels(indicator.type),\n        "confidence": indicator.confidence\n    }\n    \n    return stix_indicator'
        },
        {
          step: 3,
          component: 'STIX Pattern Generation',
          action: 'Generate STIX pattern based on indicator type',
          code: 'def create_stix_pattern(self, indicator):\n    pattern_templates = {\n        "ip": "[ipv4-addr:value = \'{value}\']",\n        "domain": "[domain-name:value = \'{value}\']",\n        "url": "[url:value = \'{value}\']",\n        "email": "[email-addr:value = \'{value}\']",\n        "hash_md5": "[file:hashes.MD5 = \'{value}\']",\n        "hash_sha256": "[file:hashes.\'SHA-256\' = \'{value}\']"\n    }\n    \n    template = pattern_templates.get(indicator.type)\n    if template:\n        return template.format(value=indicator.value)\n    \n    raise ValueError(f"Unsupported indicator type: {indicator.type}")'
        },
        {
          step: 4,
          component: 'STIX Bundle Creation',
          action: 'Package indicators into STIX bundle',
          code: 'def create_stix_bundle(self, indicators, metadata):\n    stix_objects = []\n    \n    # Convert each indicator\n    for indicator in indicators:\n        stix_obj = self.create_stix_object_from_indicator(indicator)\n        stix_objects.append(stix_obj)\n    \n    # Create bundle\n    bundle = {\n        "type": "bundle",\n        "spec_version": "2.1",\n        "id": f"bundle--{uuid.uuid4()}",\n        "created": datetime.utcnow().isoformat(),\n        "objects": stix_objects\n    }\n    \n    return bundle'
        },
        {
          step: 5,
          component: 'Publication Service',
          action: 'Publish STIX bundle to target destination',
          code: 'def publish_stix_bundle(self, bundle, options):\n    if options.get("target") == "taxii_server":\n        # Publish to TAXII server\n        collection = self.get_taxii_collection(options["taxii_config"])\n        result = collection.add_objects(bundle["objects"])\n        \n    elif options.get("target") == "file_export":\n        # Export as JSON file\n        filename = f"stix_bundle_{datetime.now().strftime(\'%Y%m%d_%H%M%S\')}.json"\n        with open(filename, \'w\') as f:\n            json.dump(bundle, f, indent=2)\n        result = {"filename": filename}\n    \n    return result'
        },
        {
          step: 6,
          component: 'Frontend Response',
          action: 'Return publication results with bundle metadata',
          code: 'return {\n  "success": true,\n  "bundle_id": "bundle--a1b2c3d4-e5f6-7890-abcd-ef1234567890",\n  "stix_version": "2.1",\n  "objects_published": 3,\n  "publication_details": {\n    "target": "taxii_server",\n    "published_at": "2024-01-15T10:30:00Z",\n    "bundle_size": "2.4 KB"\n  },\n  "indicators": [\n    {"id": "indicator--123", "pattern": "[ipv4-addr:value = \'192.168.1.100\']"},\n    {"id": "indicator--456", "pattern": "[domain-name:value = \'malicious.com\']"}\n  ]\n}'
        }
      ],
      unitTests: [
        {
          method: 'test_create_stix_object_from_indicator',
          assertion: 'Internal indicator converted to valid STIX 2.1 format',
          mock: 'Mock Indicator model with controlled attributes and timestamps'
        },
        {
          method: 'test_create_stix_pattern',
          assertion: 'STIX patterns generated correctly for each indicator type',
          mock: 'No external dependencies - pure pattern generation logic'
        },
        {
          method: 'test_stix_bundle_creation',
          assertion: 'STIX bundle properly formatted with valid structure',
          mock: 'Mock datetime.utcnow() and uuid.uuid4() for deterministic testing'
        },
        {
          method: 'test_pattern_validation',
          assertion: 'Generated STIX patterns comply with STIX specification',
          mock: 'Mock STIX pattern validator for compliance checking'
        }
      ]
    },
    {
      id: 'stix-ttp-publication',
      title: 'STIX TTP and Attack Pattern Publication',
      file: 'test_stix_factory.py',
      testClass: 'StixTTPCreatorTestCase',
      description: 'Unit test flow for creating and publishing STIX TTPs and attack patterns',
      backendFlow: [
        {
          step: 1,
          component: 'Frontend Request',
          action: 'User selects TTPs for STIX attack pattern publication',
          code: 'POST /api/stix/publish/ttps\n{\n  "ttp_ids": ["ttp-1", "ttp-2"],\n  "include_mitre_mapping": true,\n  "stix_version": "2.1",\n  "publication_scope": "external"\n}'
        },
        {
          step: 2,
          component: 'STIX TTP Creator Factory',
          action: 'Convert TTP data to STIX attack pattern format',
          code: 'def create_stix_object_from_ttp(self, ttp):\n    attack_pattern = {\n        "type": "attack-pattern",\n        "spec_version": "2.1",\n        "id": f"attack-pattern--{ttp.stix_id}",\n        "created": ttp.created_at.isoformat(),\n        "modified": ttp.updated_at.isoformat(),\n        "name": ttp.name,\n        "description": ttp.description,\n        "x_mitre_id": ttp.mitre_technique_id\n    }\n    \n    # Add MITRE ATT&CK references if available\n    if ttp.mitre_technique_id:\n        attack_pattern["external_references"] = [{\n            "source_name": "mitre-attack",\n            "external_id": ttp.mitre_technique_id,\n            "url": f"https://attack.mitre.org/techniques/{ttp.mitre_technique_id}"\n        }]\n    \n    return attack_pattern'
        },
        {
          step: 3,
          component: 'MITRE ATT&CK Integration',
          action: 'Enrich attack patterns with MITRE framework data',
          code: 'def enrich_with_mitre_data(self, attack_pattern, ttp):\n    mitre_data = self.get_mitre_technique_data(ttp.mitre_technique_id)\n    \n    if mitre_data:\n        # Add kill chain phases\n        attack_pattern["kill_chain_phases"] = [{\n            "kill_chain_name": "mitre-attack",\n            "phase_name": ttp.mitre_tactic\n        }]\n        \n        # Add additional metadata\n        attack_pattern["x_mitre_tactic"] = ttp.mitre_tactic\n        attack_pattern["x_mitre_platforms"] = mitre_data.get("platforms", [])\n        attack_pattern["x_mitre_data_sources"] = mitre_data.get("data_sources", [])\n    \n    return attack_pattern'
        },
        {
          step: 4,
          component: 'Relationship Creation',
          action: 'Create relationships between attack patterns and indicators',
          code: 'def create_stix_relationships(self, ttps, indicators):\n    relationships = []\n    \n    for ttp in ttps:\n        related_indicators = indicators.filter(ttp_references__contains=ttp.id)\n        \n        for indicator in related_indicators:\n            relationship = {\n                "type": "relationship",\n                "spec_version": "2.1",\n                "id": f"relationship--{uuid.uuid4()}",\n                "created": datetime.utcnow().isoformat(),\n                "relationship_type": "indicates",\n                "source_ref": f"indicator--{indicator.stix_id}",\n                "target_ref": f"attack-pattern--{ttp.stix_id}"\n            }\n            relationships.append(relationship)\n    \n    return relationships'
        },
        {
          step: 5,
          component: 'Frontend Response',
          action: 'Return published attack patterns with relationships',
          code: 'return {\n  "success": true,\n  "attack_patterns_published": 2,\n  "relationships_created": 5,\n  "mitre_mappings": {\n    "T1566.001": "Spearphishing Attachment",\n    "T1189": "Drive-by Compromise"\n  },\n  "published_objects": [\n    {\n      "type": "attack-pattern",\n      "name": "Phishing Attack",\n      "mitre_id": "T1566.001",\n      "related_indicators": 3\n    }\n  ]\n}'
        }
      ],
      unitTests: [
        {
          method: 'test_create_stix_object_from_ttp',
          assertion: 'TTP converted to valid STIX attack pattern with MITRE references',
          mock: 'Mock TTPData model with controlled MITRE technique IDs'
        },
        {
          method: 'test_mitre_attack_mapping',
          assertion: 'MITRE ATT&CK framework data properly integrated',
          mock: 'Mock MITRE technique data API responses'
        },
        {
          method: 'test_relationship_creation',
          assertion: 'STIX relationships created between indicators and attack patterns',
          mock: 'Mock TTP-indicator relationships from database'
        }
      ]
    },
    {
      id: 'stix-version-compatibility',
      title: 'STIX Version Compatibility and Conversion',
      file: 'test_stix_factory.py',
      testClass: 'StixVersionCompatibilityTestCase',
      description: 'Unit test flow for handling different STIX versions and format conversions',
      backendFlow: [
        {
          step: 1,
          component: 'Frontend Request',
          action: 'User requests publication in specific STIX version',
          code: 'POST /api/stix/publish/convert\n{\n  "source_objects": ["ind-1", "ttp-1"],\n  "source_version": "2.0",\n  "target_version": "2.1",\n  "preserve_custom_properties": true\n}'
        },
        {
          step: 2,
          component: 'Version Detection',
          action: 'Detect source STIX version and validate compatibility',
          code: 'def detect_stix_version(self, stix_object):\n    if "spec_version" in stix_object:\n        return stix_object["spec_version"]\n    elif "version" in stix_object:\n        return "1.x"  # STIX 1.x format\n    else:\n        # Try to infer from structure\n        if "pattern" in stix_object and "labels" in stix_object:\n            return "2.0"  # Likely STIX 2.0\n        return "unknown"'
        },
        {
          step: 3,
          component: 'STIX 2.0 to 2.1 Converter',
          action: 'Convert STIX 2.0 objects to STIX 2.1 format',
          code: 'def convert_stix20_to_21(self, stix20_object):\n    stix21_object = stix20_object.copy()\n    \n    # Update spec version\n    stix21_object["spec_version"] = "2.1"\n    \n    # Handle breaking changes\n    if stix20_object["type"] == "indicator":\n        # STIX 2.1 requires valid_from property\n        if "valid_from" not in stix21_object:\n            stix21_object["valid_from"] = stix20_object.get("created")\n    \n    # Update timestamps to RFC 3339 format if needed\n    for timestamp_field in ["created", "modified", "valid_from", "valid_until"]:\n        if timestamp_field in stix21_object:\n            stix21_object[timestamp_field] = self.normalize_timestamp(\n                stix21_object[timestamp_field]\n            )\n    \n    return stix21_object'
        },
        {
          step: 4,
          component: 'Custom Property Preservation',
          action: 'Preserve custom properties during version conversion',
          code: 'def preserve_custom_properties(self, converted_object, original_object):\n    custom_props = {}\n    \n    for key, value in original_object.items():\n        if key.startswith("x_") or key not in STIX_CORE_PROPERTIES:\n            custom_props[key] = value\n    \n    # Merge custom properties into converted object\n    converted_object.update(custom_props)\n    \n    return converted_object'
        },
        {
          step: 5,
          component: 'Frontend Response',
          action: 'Return converted STIX objects with conversion metadata',
          code: 'return {\n  "success": true,\n  "conversion_summary": {\n    "source_version": "2.0",\n    "target_version": "2.1",\n    "objects_converted": 5,\n    "custom_properties_preserved": 12,\n    "warnings": []\n  },\n  "converted_objects": [\n    {\n      "type": "indicator",\n      "spec_version": "2.1",\n      "valid_from": "2024-01-15T10:30:00.000Z",\n      "conversion_notes": "Added required valid_from property"\n    }\n  ]\n}'
        }
      ],
      unitTests: [
        {
          method: 'test_stix_version_detection',
          assertion: 'STIX version correctly detected from object structure',
          mock: 'Mock STIX objects with different version indicators'
        },
        {
          method: 'test_stix20_to_21_conversion',
          assertion: 'STIX 2.0 objects properly converted to 2.1 format',
          mock: 'Mock STIX 2.0 objects with various types and properties'
        },
        {
          method: 'test_custom_property_preservation',
          assertion: 'Custom x_ properties preserved during conversion',
          mock: 'Mock STIX objects with custom properties and extensions'
        }
      ]
    }
  ];

  const TestSummaryBox = () => (
    <div className="test-summary-box">
      <div className="summary-header">
        <h3>STIX Factory Test Coverage</h3>
        <button className="run-tests-btn" onClick={() => {
          setIsRunningAllTests(true);
          // Simulate test run
          setTimeout(() => {
            setTestSummary({
              total: 101,
              passed: 101,
              failed: 0,
              coverage: '78%'
            });
            setIsRunningAllTests(false);
          }, 7000);
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
    await new Promise(resolve => setTimeout(resolve, 2800));
    
    // Simulate test results based on the flow
    const mockResults = {
      'stix-indicator-publication': {
        status: 'PASSED',
        duration: '2.67s',
        tests_run: 4,
        tests_passed: 4,
        tests_failed: 0,
        coverage: '93%',
        details: [
          { method: 'test_create_stix_object_from_indicator', status: 'PASSED', duration: '0.72s', assertion: '✅ Input: Indicator(type="ip", value="192.168.1.100") → Expected: STIX 2.1 object with pattern → Actual: {"type": "indicator", "spec_version": "2.1", "pattern": "[ipv4-addr:value = \'192.168.1.100\']"} (Valid STIX created)' },
          { method: 'test_create_stix_pattern', status: 'PASSED', duration: '0.58s', assertion: '✅ Input: {"type": "domain", "value": "malicious.com"} → Expected: "[domain-name:value = \'malicious.com\']" → Actual: "[domain-name:value = \'malicious.com\']" (Pattern generated correctly)' },
          { method: 'test_stix_bundle_creation', status: 'PASSED', duration: '0.84s', assertion: '✅ Input: 3 indicators → Expected: Bundle with 3 objects, valid UUID → Actual: Bundle(objects=3, id="bundle--uuid") (Bundle created successfully)' },
          { method: 'test_pattern_validation', status: 'PASSED', duration: '0.53s', assertion: '✅ Input: Generated STIX patterns → Expected: All patterns STIX 2.1 compliant → Actual: All patterns STIX 2.1 compliant (Specification compliance verified)' }
        ]
      },
      'stix-ttp-publication': {
        status: 'PASSED',
        duration: '3.15s',
        tests_run: 3,
        tests_passed: 3,
        tests_failed: 0,
        coverage: '87%',
        details: [
          { method: 'test_create_stix_object_from_ttp', status: 'PASSED', duration: '1.23s', assertion: '✅ Input: TTP(name="Phishing Attack", mitre_id="T1566.001") → Expected: Attack pattern with MITRE reference → Actual: {"type": "attack-pattern", "x_mitre_id": "T1566.001", "external_references": [...]} (MITRE mapping successful)' },
          { method: 'test_mitre_attack_mapping', status: 'PASSED', duration: '0.98s', assertion: '✅ Input: MITRE technique T1566.001 → Expected: Kill chain phases and platforms data → Actual: {"kill_chain_phases": [{"phase_name": "initial-access"}], "platforms": ["Windows"]} (Framework data integrated)' },
          { method: 'test_relationship_creation', status: 'PASSED', duration: '0.94s', assertion: '✅ Input: 2 TTPs, 5 indicators → Expected: 5 "indicates" relationships → Actual: 5 "indicates" relationships created (Relationships established)' }
        ]
      },
      'stix-version-compatibility': {
        status: 'PASSED',
        duration: '1.95s',
        tests_run: 3,
        tests_passed: 3,
        tests_failed: 0,
        coverage: '95%',
        details: [
          { method: 'test_stix_version_detection', status: 'PASSED', duration: '0.43s', assertion: '✅ Input: {"spec_version": "2.0", "pattern": "..."} → Expected: Version "2.0" → Actual: Version "2.0" (Version detected correctly)' },
          { method: 'test_stix20_to_21_conversion', status: 'PASSED', duration: '0.89s', assertion: '✅ Input: STIX 2.0 indicator → Expected: STIX 2.1 with "valid_from" added → Actual: {"spec_version": "2.1", "valid_from": "2024-01-15T10:30:00Z"} (Conversion successful)' },
          { method: 'test_custom_property_preservation', status: 'PASSED', duration: '0.63s', assertion: '✅ Input: Object with "x_custom_field": "value" → Expected: Custom property preserved → Actual: "x_custom_field": "value" still present (Custom properties preserved)' }
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
        <h2>Unit Tests for STIX Publication</h2>
        <p>Backend to Frontend unit test flows for factory-based STIX object creation and publication</p>
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

export default StixPublicationFlow;