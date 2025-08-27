# Multi-stage Dockerfile for development and production

# Stage 1: Python Base
FROM python:3.11-slim as python-base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Node Base
FROM node:20-slim as node-base

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install Node.js dependencies
RUN npm ci --only=production

# Stage 3: Development
FROM python-base as development

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Install development dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy Node.js dependencies
COPY --from=node-base /app/node_modules ./node_modules
COPY package*.json ./

# Install all npm dependencies for development
RUN npm ci

# Copy application code
COPY . .

# Expose ports for development
EXPOSE 3000 8000 5678

# Development command
CMD ["npm", "run", "dev"]

# Stage 4: Build
FROM node-base as build

COPY . .
COPY --from=node-base /app/node_modules ./node_modules

# Build the application
RUN npm run build

# Stage 5: Production
FROM python-base as production

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app

# Copy Python application
COPY --chown=app:app . .

# Copy built web assets
COPY --from=build --chown=app:app /app/dist ./dist

# Switch to non-root user
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production ports
EXPOSE 8000

# Production command
CMD ["python", "main.py"]

# Stage 6: Testing
FROM development as testing

# Copy test files
COPY tests/ ./tests/
COPY playwright.config.ts jest.config.js ./

# Run tests
RUN npm run test && python -m pytest

# Default stage for docker build
FROM production