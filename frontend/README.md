# Frontend

This directory contains the React frontend code for CRISP.

## Getting Started

1. Place your React project files here
2. Include `package.json` in this directory
3. Add your components, styles, and assets
4. The CI/CD pipeline will automatically detect and test your code

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