# Configuration Files Guide

## Overview
Configuration files define application behavior, build processes, and deployment settings. This guide covers essential configuration file types for modern development workflows.

## File Types Reference

| **Config Type** | **Core Files** | **Supporting Files** | **Purpose** |
|----------------|----------------|---------------------|------------|
| **Environment Configs** | `.env`, `.env.local` | `.env.production`, `.env.test` | Application settings and secrets |
| **Docker Configs** | `Dockerfile`, `docker-compose.yml` | `.dockerignore` | Container configuration |
| **CI/CD Configs** | `.github/workflows/*.yml`, `.gitlab-ci.yml` | `jenkinsfile`, `.circleci/config.yml` | Automation pipelines |
| **Build Configs** | `webpack.config.js`, `vite.config.js` | `rollup.config.js`, `tsconfig.json` | Build tool configuration |
| **Linter Configs** | `.eslintrc`, `.prettierrc` | `.stylelintrc`, `.pylintrc` | Code quality rules |

## Use Cases & Examples

### Environment Configuration
**Best For:** Managing secrets, feature flags, environment-specific settings
```bash
# .env.development
NODE_ENV=development
API_URL=http://localhost:3000
DATABASE_URL=postgresql://user:pass@localhost:5432/devdb
DEBUG=true
LOG_LEVEL=debug

# .env.production
NODE_ENV=production
API_URL=https://api.example.com
DATABASE_URL=${DATABASE_CONNECTION_STRING}
DEBUG=false
LOG_LEVEL=error
SENTRY_DSN=${SENTRY_DSN}
```

**Loading Environment Variables:**
```javascript
// config.js
require('dotenv').config({
  path: `.env.${process.env.NODE_ENV || 'development'}`
});

module.exports = {
  port: process.env.PORT || 3000,
  database: {
    url: process.env.DATABASE_URL,
    poolSize: parseInt(process.env.DB_POOL_SIZE || '10')
  },
  features: {
    newDashboard: process.env.FEATURE_NEW_DASHBOARD === 'true'
  }
};
```
**Example Projects:** Multi-environment apps, microservices, API configurations

### Docker Configuration
**Best For:** Container orchestration, development environments, deployment
```dockerfile
# Dockerfile - Multi-stage build
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```
**Example Projects:** Microservice architectures, local development environments

### CI/CD Pipeline Configuration
**Best For:** Automated testing, deployment, code quality checks
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [16, 18, 20]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run linter
        run: npm run lint
      
      - name: Run tests
        run: npm test -- --coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to production
        run: |
          echo "Deploying to production..."
          # Deployment commands here
```
**Example Projects:** Continuous deployment, automated testing, release automation

### Build Configuration
**Best For:** Module bundling, transpilation, optimization
```javascript
// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [
    react(),
    visualizer({ open: true, gzipSize: true })
  ],
  build: {
    target: 'es2015',
    minify: 'terser',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          utils: ['lodash', 'axios']
        }
      }
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
});
```
**Example Projects:** Frontend applications, library builds, development servers

### Linter Configuration
**Best For:** Code consistency, quality enforcement, formatting
```json
// .eslintrc.json
{
  "extends": [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:@typescript-eslint/recommended",
    "prettier"
  ],
  "parser": "@typescript-eslint/parser",
  "plugins": ["react", "@typescript-eslint", "react-hooks"],
  "rules": {
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn",
    "@typescript-eslint/no-explicit-any": "error",
    "no-console": ["warn", { "allow": ["warn", "error"] }]
  },
  "settings": {
    "react": {
      "version": "detect"
    }
  }
}
```

```json
// .prettierrc
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false,
  "bracketSpacing": true,
  "arrowParens": "avoid"
}
```
**Example Projects:** Team projects, open source libraries, code quality automation

## Best Practices

1. **Security:** Never commit secrets, use environment variables
2. **Validation:** Validate configuration on application startup
3. **Documentation:** Document all configuration options
4. **Defaults:** Provide sensible defaults for all settings
5. **Type Safety:** Use TypeScript for configuration objects
6. **Environment Parity:** Keep development and production similar

## File Organization Pattern
```
project/
├── .env.example
├── .env.local (gitignored)
├── docker/
│   ├── Dockerfile.dev
│   └── Dockerfile.prod
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
├── config/
│   ├── webpack.dev.js
│   ├── webpack.prod.js
│   └── jest.config.js
└── .eslintrc.json
```

## Configuration Patterns

### Schema Validation
```javascript
// config-schema.js - Using Joi
const Joi = require('joi');

const configSchema = Joi.object({
  NODE_ENV: Joi.string()
    .valid('development', 'production', 'test')
    .required(),
  PORT: Joi.number().port().default(3000),
  DATABASE_URL: Joi.string().uri().required(),
  JWT_SECRET: Joi.string().min(32).required(),
  RATE_LIMIT: Joi.number().integer().min(1).default(100)
});

const { error, value } = configSchema.validate(process.env);
if (error) {
  throw new Error(`Config validation error: ${error.message}`);
}
```

### TypeScript Configuration
```typescript
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

## Performance Considerations
- Lazy load configuration for faster startup
- Cache parsed configuration values
- Use build-time configuration for static values
- Minimize configuration complexity
- Profile configuration loading time