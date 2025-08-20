# CRISP Trust Management Platform - Testing Guide

This document provides comprehensive information about the testing infrastructure for the CRISP Trust Management Platform.

## 🧪 Test Architecture

The testing suite is organized into multiple layers:

### 1. **Unit Tests**
- **Backend**: Django model, service, and utility tests
- **Frontend**: React component tests using Vitest + Testing Library
- **Coverage**: Individual functions and components in isolation

### 2. **Integration Tests** 
- **API Integration**: Real API calls between frontend and backend
- **Component Integration**: Multi-component interactions
- **Data Flow**: End-to-end data processing workflows

### 3. **End-to-End Tests**
- **User Workflows**: Complete user journeys using Playwright
- **Cross-browser**: Chrome, Firefox, Safari testing
- **Real Environment**: Tests against actual running application

## 🚀 Quick Start

### Install Dependencies
```bash
# Install all dependencies (backend + frontend)
npm run setup:test
```

### Run Tests

**Quick Development Tests (2-3 minutes)**
```bash
./run-quick-tests.sh
# or
npm run dev:test
```

**Complete Test Suite (10-15 minutes)**
```bash
./run-all-tests.sh
# or  
npm run test:all
```

**Specific Test Types**
```bash
# Backend only
npm run test:backend

# Frontend only
npm run test:frontend

# Integration tests
npm run test:integration  

# End-to-end tests
npm run test:e2e
```

## 📁 Test File Organization

```
Capstone-Unified/
├── core/tests/                          # Django Backend Tests
│   ├── test_repository.py               # Data layer tests
│   ├── test_utils.py                    # Utility function tests
│   ├── test_integration.py              # Backend integration tests
│   └── ...
│
├── crisp-react/src/
│   ├── **/*.test.jsx                    # Unit tests (co-located)
│   ├── test/
│   │   ├── integration/                 # API integration tests
│   │   │   ├── auth-integration.test.jsx
│   │   │   └── settings-integration.test.jsx
│   │   ├── e2e/                         # End-to-end tests
│   │   │   ├── login-flow.spec.js
│   │   │   ├── user-profile-flow.spec.js
│   │   │   └── admin-flow.spec.js
│   │   └── utils/                       # Test utilities
│   └── test/setup.js                    # Global test setup
│
├── run-all-tests.sh                     # Master test runner
├── run-quick-tests.sh                   # Quick development tests
└── package.json                         # Unified NPM scripts
```

## 🔧 Test Configuration

### Frontend Testing Stack
- **Test Runner**: Vitest (fast, modern)
- **Component Testing**: React Testing Library
- **E2E Testing**: Playwright (cross-browser)
- **Coverage**: Built-in Vitest coverage

### Backend Testing Stack
- **Test Runner**: Django's built-in test runner + Custom Orchestrator
- **Database**: SQLite in-memory for tests
- **Coverage**: Django test coverage tools

## 📊 Test Commands Reference

### Development Workflow
```bash
# Quick smoke tests during development
./run-quick-tests.sh

# Test specific component  
cd crisp-react && npm test UserProfile.test.jsx

# Watch mode for development
cd crisp-react && npm run test:watch
```

### CI/CD Pipeline
```bash
# Full test suite with verbose output (for CI)
./run-all-tests.sh --verbose

# Specific test types for parallel CI jobs
./run-all-tests.sh --skip-e2e          # Skip E2E (for unit test job)
./run-all-tests.sh --skip-backend      # Frontend only
./run-all-tests.sh --skip-frontend     # Backend only
```

### Test Options
```bash
# Skip certain test types
./run-all-tests.sh --skip-backend
./run-all-tests.sh --skip-frontend  
./run-all-tests.sh --skip-e2e

# Verbose output
./run-all-tests.sh --verbose

# Parallel execution (where supported)
./run-all-tests.sh --parallel
```

## 🎯 Test Coverage Goals

- **Unit Tests**: >80% code coverage
- **Integration Tests**: All major API endpoints
- **E2E Tests**: Critical user workflows
- **Cross-browser**: Chrome, Firefox, Safari

## 🐛 Writing New Tests

### Frontend Unit Test Example
```javascript
// src/components/MyComponent.test.jsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import MyComponent from './MyComponent'

describe('MyComponent', () => {
  test('renders correctly', () => {
    render(<MyComponent />)
    expect(screen.getByText('Expected Text')).toBeInTheDocument()
  })

  test('handles user interaction', async () => {
    const user = userEvent.setup()
    render(<MyComponent />)
    
    const button = screen.getByRole('button')
    await user.click(button)
    
    expect(screen.getByText('Updated Text')).toBeInTheDocument()
  })
})
```

### Backend Test Example  
```python
# core/tests/test_my_feature.py
from django.test import TestCase
from core.models import MyModel

class MyFeatureTest(TestCase):
    def test_model_creation(self):
        instance = MyModel.objects.create(name='test')
        self.assertEqual(instance.name, 'test')
        
    def test_api_endpoint(self):
        response = self.client.get('/api/my-endpoint/')
        self.assertEqual(response.status_code, 200)
```

### E2E Test Example
```javascript  
// src/test/e2e/my-workflow.spec.js
import { test, expect } from '@playwright/test'

test('user can complete workflow', async ({ page }) => {
  await page.goto('/')
  
  await page.click('button:has-text("Start")')
  await page.fill('input[name="data"]', 'test data')
  await page.click('button:has-text("Submit")')
  
  await expect(page.locator('text=Success')).toBeVisible()
})
```

## 🔍 Debugging Tests

### Frontend Test Debugging
```bash
# Run tests with UI (interactive debugging)
cd crisp-react && npm run test:ui

# Run specific test file
cd crisp-react && npm test -- UserProfile.test.jsx

# Debug E2E tests with browser
cd crisp-react && npm run test:e2e:ui
```

### Backend Test Debugging
```bash
# Run specific test class
python manage.py test core.tests.TestMyFeature

# Run with verbose output
python manage.py test --verbosity=2

# Keep test database for inspection
python manage.py test --keepdb
```

## 🚦 Continuous Integration

The test suite is designed for CI/CD pipelines:

### GitHub Actions Example
```yaml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Set up Node.js  
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Run tests
        run: ./run-all-tests.sh --verbose
```

## 📈 Performance Monitoring

- **Quick Tests**: Target <3 minutes
- **Full Suite**: Target <15 minutes  
- **E2E Tests**: Target <5 minutes
- **Parallel Execution**: Supported where possible

## ❗ Troubleshooting

### Common Issues

1. **Port Conflicts**: E2E tests expect dev server on port 5173
2. **Database Issues**: Backend tests use in-memory SQLite
3. **Browser Issues**: Run `npm run playwright:install` if E2E tests fail
4. **Permission Issues**: Make sure test scripts are executable (`chmod +x`)

### Test Failures

1. Check the specific error output
2. Run individual test files to isolate issues  
3. Verify dependencies are installed (`npm run setup:test`)
4. Check if services are running (for integration tests)

## 🎉 Success Criteria

When all tests pass, you'll see:

```
🎉 ALL TESTS PASSED! System is ready for deployment.

✓ Backend API functionality verified
✓ Frontend components tested  
✓ Integration between systems validated
✓ End-to-end user workflows confirmed

The CRISP Trust Management Platform is ready for production!
```

This indicates the system is fully tested and production-ready!