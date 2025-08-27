module.exports = {
  root: true,
  env: {
    browser: true,
    es2020: true,
    node: true,
    'vitest-globals/env': true,
  },
  extends: [
    'eslint:recommended',
    '@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
    'plugin:react/recommended',
    'plugin:react/jsx-runtime',
    'plugin:jsx-a11y/recommended',
    'plugin:@tanstack/eslint-plugin-query/recommended',
  ],
  ignorePatterns: [
    'dist',
    'build',
    'coverage',
    'node_modules',
    '*.config.js',
    '*.config.ts',
    'public',
    'test-results',
  ],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true,
    },
  },
  plugins: [
    'react',
    'react-hooks',
    'react-refresh',
    '@typescript-eslint',
    'jsx-a11y',
    'vitest-globals',
  ],
  settings: {
    react: {
      version: 'detect',
    },
  },
  rules: {
    // React specific rules
    'react/prop-types': 'off', // Using TypeScript for prop validation
    'react/react-in-jsx-scope': 'off', // Not needed in React 17+
    'react/jsx-uses-react': 'off', // Not needed in React 17+
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn',
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true },
    ],

    // TypeScript specific rules
    '@typescript-eslint/no-unused-vars': [
      'error',
      {
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^_',
        caughtErrorsIgnorePattern: '^_',
      },
    ],
    '@typescript-eslint/no-explicit-any': 'warn',
    '@typescript-eslint/no-non-null-assertion': 'warn',
    '@typescript-eslint/prefer-const': 'error',

    // Accessibility rules
    'jsx-a11y/anchor-is-valid': 'warn',
    'jsx-a11y/alt-text': 'error',
    'jsx-a11y/aria-props': 'error',
    'jsx-a11y/aria-proptypes': 'error',
    'jsx-a11y/aria-unsupported-elements': 'error',
    'jsx-a11y/role-has-required-aria-props': 'error',
    'jsx-a11y/role-supports-aria-props': 'error',

    // General code quality rules
    'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'warn',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'warn',
    'no-alert': 'warn',
    'no-var': 'error',
    'prefer-const': 'error',
    'no-duplicate-imports': 'error',
    'no-unused-expressions': 'error',
    'no-unreachable': 'error',
    'consistent-return': 'warn',
    'default-case': 'warn',
    'eqeqeq': ['error', 'always'],
    'no-empty': 'warn',
    'no-extra-boolean-cast': 'warn',
    'no-extra-semi': 'error',
    'no-irregular-whitespace': 'error',
    'no-multiple-empty-lines': ['error', { max: 2 }],
    'no-trailing-spaces': 'error',
    'semi': ['error', 'always'],
    'quotes': ['error', 'single', { allowTemplateLiterals: true }],

    // Import/Export rules
    'no-duplicate-imports': 'error',
    'import/no-unused-modules': 'off', // Can be enabled if using eslint-plugin-import
  },
  overrides: [
    {
      files: ['**/*.test.{ts,tsx}', '**/*.spec.{ts,tsx}', '**/tests/**/*'],
      env: {
        'vitest-globals/env': true,
      },
      rules: {
        // Allow any in tests for mocking
        '@typescript-eslint/no-explicit-any': 'off',
        // Allow non-null assertions in tests
        '@typescript-eslint/no-non-null-assertion': 'off',
        // Allow console in tests
        'no-console': 'off',
        // Allow unused expressions in tests (for expect statements)
        'no-unused-expressions': 'off',
      },
    },
    {
      files: ['**/*.config.{js,ts}', '**/vite.config.{js,ts}'],
      rules: {
        // Allow default export in config files
        'import/no-default-export': 'off',
        // Allow console in config files
        'no-console': 'off',
      },
    },
    {
      files: ['src/sw.ts', '**/service-worker.ts'],
      env: {
        serviceworker: true,
      },
      rules: {
        // Allow console in service worker
        'no-console': 'off',
        // Service worker specific allowances
        'no-restricted-globals': 'off',
      },
    },
  ],
};