import React, { useState } from 'react';
import './WorkflowComponent.css';

const ThreatIntelWorkflow = () => {
  const [activeTest, setActiveTest] = useState(null);

  const unitTests = [
    {
      id: 'stix-factory',
      file: 'test_stix_factory.py',
      class: 'StixIndicatorCreatorTestCase',
      title: 'STIX Indicator Factory Unit Tests',
      description: 'Unit tests for STIX indicator factory classes with mocked dependencies',
      tests: [
        {
          name: 'test_create_from_stix20_indicator',
          description: 'Tests StixIndicatorCreator.create_from_stix20_indicator() method',
          steps: [
            'Mock STIX 2.0 indicator object with MagicMock()',
            'Instantiate StixIndicatorCreator class',
            'Call create method with mocked indicator',
            'Assert CRISP Indicator model created correctly',
            'Verify datetime and attribute mapping isolated'
          ]
        },
        {
          name: 'test_parse_indicator_pattern',
          description: 'Tests pattern parsing logic in isolation',
          steps: [
            'Create test STIX pattern strings',
            'Mock external pattern parsing dependencies',
            'Test parse_indicator_pattern() method',
            'Assert pattern type detection',
            'Verify pattern validation logic'
          ]
        },
        {
          name: 'test_create_stix_pattern',
          description: 'Tests STIX pattern creation from CRISP data',
          steps: [
            'Mock CRISP indicator data',
            'Test create_stix_pattern() method',
            'Assert valid STIX pattern syntax',
            'Verify pattern format correctness',
            'Test isolated pattern generation'
          ]
        }
      ]
    },
    {
      id: 'stix-ttp-factory',
      file: 'test_stix_factory.py',
      class: 'StixTTPCreatorTestCase',
      title: 'STIX TTP Factory Unit Tests',
      description: 'Unit tests for STIX TTP factory classes in isolation',
      tests: [
        {
          name: 'test_create_from_stix20_ttp',
          description: 'Tests StixTTPCreator.create_from_stix20_ttp() method',
          steps: [
            'Mock STIX 2.0 attack pattern object',
            'Create StixTTPCreator instance',
            'Test TTP creation logic',
            'Assert TTPData model attributes',
            'Verify MITRE mapping isolation'
          ]
        },
        {
          name: 'test_create_stix_object_from_ttp',
          description: 'Tests STIX object creation from CRISP TTP',
          steps: [
            'Mock TTPData model instance',
            'Test create_stix_object_from_ttp() method',
            'Assert STIX attack pattern structure',
            'Verify STIX specification compliance',
            'Test isolated object creation'
          ]
        }
      ]
    }
  ];

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
        <h2>Threat Intelligence Publication and Sharing</h2>
        <p>Unit tests for individual STIX factory components in isolation with mocked dependencies</p>
      </div>

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
                      <div>Set up test environment with mocked STIX objects</div>
                    </div>
                    <div className="workflow-step">
                      <div className="step-number">2</div>
                      <div>Instantiate factory classes in isolation</div>
                    </div>
                    <div className="workflow-step">
                      <div className="step-number">3</div>
                      <div>Execute individual methods with test data</div>
                    </div>
                    <div className="workflow-step">
                      <div className="step-number">4</div>
                      <div>Assert expected object creation and verify mocks</div>
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
    </div>
  );
};

export default ThreatIntelWorkflow;