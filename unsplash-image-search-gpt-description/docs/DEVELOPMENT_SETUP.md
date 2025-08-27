# Development Setup Guide

This guide will help you set up the development environment for the Unsplash Image Search & GPT Description Tool.

## Prerequisites

- **Node.js** (>= 18.0.0) - [Download](https://nodejs.org/)
- **Python** (>= 3.9.0) - [Download](https://python.org/)
- **Git** - [Download](https://git-scm.com/)
- **Docker** (optional, for containerized development) - [Download](https://docker.com/)

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd unsplash-image-search-gpt-description
   ```

2. **Install dependencies**
   ```bash
   # Install Node.js dependencies
   npm install
   
   # Create Python virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   
   # Install Python dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

4. **Set up Git hooks**
   ```bash
   npx husky install
   ```

5. **Run the development server**
   ```bash
   npm run dev
   ```

## Development Scripts

### Main Commands

- `npm run dev` - Start both web and Python development servers
- `npm run build` - Build for production
- `npm run test` - Run all tests
- `npm run lint` - Lint all code
- `npm run format` - Format all code

### Web Development

- `npm run dev:web` - Start web development server only
- `npm run build:web` - Build web application
- `npm run preview` - Preview production build

### Python Development

- `npm run dev:python` - Start Python application only
- `npm run build:python` - Compile and build Python application

### Testing

- `npm run test:unit` - Run unit tests
- `npm run test:unit:watch` - Run unit tests in watch mode
- `npm run test:integration` - Run integration tests with Playwright
- `npm run test:python` - Run Python tests
- `npm run test:e2e` - Run end-to-end tests with UI

### Code Quality

- `npm run lint:js` - Lint JavaScript/TypeScript
- `npm run lint:python` - Lint Python code
- `npm run lint:fix` - Auto-fix linting issues
- `npm run format:js` - Format JavaScript/TypeScript
- `npm run format:python` - Format Python code
- `npm run type-check` - Run TypeScript type checking

## Docker Development

### Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up --build

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### Using Docker directly

```bash
# Build development image
docker build --target development -t unsplash-gpt:dev .

# Run development container
docker run -p 3000:3000 -p 8000:8000 -v $(pwd):/app unsplash-gpt:dev
```

## VS Code Setup

### Recommended Extensions

The project includes a `.vscode/extensions.json` file with recommended extensions:

- **ESLint** - Code linting
- **Prettier** - Code formatting
- **Python** - Python language support
- **Tailwind CSS IntelliSense** - CSS utilities
- **GitLens** - Enhanced Git capabilities
- **Playwright** - Test automation

### Settings

The workspace includes pre-configured VS Code settings for:
- Automatic formatting on save
- ESLint integration
- Python environment configuration
- Integrated terminal setup

## Environment Variables

Create a `.env` file in the project root:

```env
# API Keys
VITE_UNSPLASH_ACCESS_KEY=your_unsplash_key
VITE_OPENAI_API_KEY=your_openai_key

# Monitoring (Optional)
VITE_SENTRY_DSN=your_sentry_dsn
VITE_POSTHOG_KEY=your_posthog_key
VITE_POSTHOG_HOST=https://app.posthog.com

# Development
NODE_ENV=development
DEBUG=true
PYTHONPATH=.

# Database (for Docker)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres
```

## Code Style and Standards

### JavaScript/TypeScript

- **ESLint** with strict rules for React and TypeScript
- **Prettier** for consistent formatting
- **Import organization** with automatic sorting
- **Path aliases** for clean imports (`@/components`, `@/hooks`, etc.)

### Python

- **Black** for code formatting
- **isort** for import sorting
- **Flake8** for linting
- **MyPy** for type checking

### Git Workflow

- **Conventional Commits** for commit messages
- **Husky** pre-commit hooks for quality checks
- **Semantic Release** for automated versioning

## Testing Strategy

### Unit Tests
- **Vitest** for JavaScript/TypeScript tests
- **pytest** for Python tests
- **Testing Library** for React component tests

### Integration Tests
- **Playwright** for browser automation
- **API testing** with mock services

### End-to-End Tests
- Full user workflow testing
- Cross-browser compatibility
- Performance testing

## Project Structure

```
├── src/                    # Source code
│   ├── components/         # React components
│   ├── hooks/             # Custom React hooks
│   ├── stores/            # State management
│   ├── types/             # TypeScript definitions
│   └── utils/             # Utility functions
├── tests/                 # Test files
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── setup/             # Test configuration
├── config/                # Configuration files
├── docs/                  # Documentation
├── scripts/               # Build and utility scripts
└── .vscode/               # VS Code configuration
```

## Common Issues and Solutions

### Python Virtual Environment Issues

```bash
# If activation fails on Windows
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# If packages not found
pip install -r requirements.txt --force-reinstall
```

### Node.js Dependency Issues

```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Git Hooks Not Working

```bash
# Reinstall Husky hooks
npx husky install
chmod +x .husky/*
```

## Performance Optimization

### Development
- **Hot Module Replacement** for fast development
- **Incremental TypeScript compilation**
- **Parallel processing** for tests and builds

### Production
- **Code splitting** for optimal loading
- **Tree shaking** to eliminate dead code
- **Asset optimization** and compression

## Contributing

1. Create a feature branch from `main`
2. Make your changes following the code style
3. Add tests for new functionality
4. Ensure all checks pass: `npm run test && npm run lint`
5. Create a pull request

## Getting Help

- Check the [troubleshooting guide](./TROUBLESHOOTING.md)
- Review the [API documentation](./API.md)
- Open an issue for bugs or feature requests
- Join our development Discord for real-time help

## Next Steps

- [API Configuration Guide](./API_SETUP.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [Architecture Overview](../ARCHITECTURE.md)
- [Contributing Guidelines](../CONTRIBUTING.md)