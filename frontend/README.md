# Frontend

This directory contains the React frontend code for CRISP.

## Structure
```
frontend/
├── package.json
├── package-lock.json
├── src/
│   ├── components/
│   ├── pages/
│   ├── styles/
│   └── App.js
├── public/
└── tests/
```

The CI/CD will automatically:
- Install npm/yarn dependencies
- Run frontend tests
- Build production bundle
- Perform linting checks

## Supported Technologies
- React.js
- TypeScript
- Material-UI (as per README specs)
- D3.js for data visualization