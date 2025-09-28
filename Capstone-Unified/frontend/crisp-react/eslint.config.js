import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'

export default [
  { ignores: ['dist'] },
  {
    files: ['**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
      parserOptions: {
        ecmaVersion: 'latest',
        ecmaFeatures: { jsx: true },
        sourceType: 'module',
      },
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...js.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      // PERFORMANCE: Relax strict rules for development speed
      'no-unused-vars': ['warn', { varsIgnorePattern: '^[A-Z_]' }], // Warn instead of error
      'react-refresh/only-export-components': 'off', // Disable for performance
      'react-hooks/exhaustive-deps': 'warn', // Warn instead of error for deps
      'no-console': 'off', // Allow console in development
    },
  },
]
