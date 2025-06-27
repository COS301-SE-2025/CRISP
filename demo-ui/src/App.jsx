import React, { useState } from 'react';
import './App.css';
import StixAnonymizationFlow from './components/StixAnonymizationFlow';
import TaxiiFeedConsumptionFlow from './components/TaxiiFeedConsumptionFlow';
import UserManagementFlow from './components/UserManagementFlow';
import StixPublicationFlow from './components/StixPublicationFlow';
import TrustRelationshipFlow from './components/TrustRelationshipFlow';
import AlertSystemWorkflow from './components/AlertSystemWorkflow';
import IntegrationTestingFlow from './components/IntegrationTestingFlow';

function App() {
  const [selectedUseCase, setSelectedUseCase] = useState('stix-anonymization');

  const useCases = [
    {
      id: 'stix-anonymization',
      title: 'Unit Tests for STIX Anonymization',
      description: 'Backend to Frontend flow for anonymizing STIX objects with strategy patterns',
      file: 'test_anonymization_strategies.py'
    },
    {
      id: 'taxii-consumption',
      title: 'Unit Testing for TAXII Feed Consumption',
      description: 'Complete workflow for consuming threat intelligence from TAXII feeds',
      file: 'test_taxii_service.py'
    },
    {
      id: 'user-management',
      title: 'Unit Tests for Adding Users and User Management',
      description: 'Factory pattern implementation for user creation and management',
      file: 'test_user_management.py'
    },
    {
      id: 'stix-publication',
      title: 'Unit Tests for STIX Publication',
      description: 'Factory-based STIX object creation and publication workflows',
      file: 'test_stix_factory.py'
    },
    {
      id: 'trust-relationship',
      title: 'Unit Tests for Trust Relationship',
      description: 'Trust relationship management and sharing policy enforcement',
      file: 'trust_models/models.py'
    },
    {
      id: 'alert-system',
      title: 'Alert System Implementation',
      description: 'Observer pattern for real-time threat alerts with email notifications',
      file: 'test_email_datadefenders.py'
    },
    {
      id: 'integration-testing',
      title: 'Integration Testing - Consumption & Anonymization',
      description: 'End-to-end integration tests for TAXII consumption and anonymization pipeline',
      file: 'test_anonymization_service_integration.py'
    }
  ];

  const renderWorkflow = () => {
    switch (selectedUseCase) {
      case 'stix-anonymization':
        return <StixAnonymizationFlow />;
      case 'taxii-consumption':
        return <TaxiiFeedConsumptionFlow />;
      case 'user-management':
        return <UserManagementFlow />;
      case 'stix-publication':
        return <StixPublicationFlow />;
      case 'trust-relationship':
        return <TrustRelationshipFlow />;
      case 'alert-system':
        return <AlertSystemWorkflow />;
      case 'integration-testing':
        return <IntegrationTestingFlow />;
      default:
        return <StixAnonymizationFlow />;
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>CRISP Platform - Unit & Integration Test Demo Flows</h1>
        <p>Backend to Frontend Test Workflows: 6 Unit Test Use Cases + Integration Testing</p>
      </header>

      <div className="use-case-selector">
        {useCases.map(useCase => (
          <button
            key={useCase.id}
            className={`use-case-btn ${selectedUseCase === useCase.id ? 'active' : ''}`}
            onClick={() => setSelectedUseCase(useCase.id)}
          >
            <div className="use-case-title">{useCase.title}</div>
            <div className="use-case-desc">{useCase.description}</div>
            <div className="use-case-file">📁 {useCase.file}</div>
          </button>
        ))}
      </div>

      <main className="main-content">
        {renderWorkflow()}
      </main>
    </div>
  );
}

export default App
