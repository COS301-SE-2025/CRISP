// ESLint rules to prevent performance issues
module.exports = {
  rules: {
    // Prevent excessive console logging
    'no-console': ['warn', {
      allow: ['warn', 'error'] // Only allow warnings and errors
    }],

    // Prevent short intervals
    'no-restricted-syntax': [
      'error',
      {
        selector: 'CallExpression[callee.name="setInterval"][arguments.0.type="Literal"][arguments.0.value<60000]',
        message: 'setInterval with less than 60 seconds (60000ms) is prohibited for performance'
      }
    ],

    // Warn about useEffect with many dependencies
    'react-hooks/exhaustive-deps': 'warn'
  }
};