# Makefile for SpanishMaster Testing Suite
# Provides convenient commands for running different types of tests

.PHONY: help install test test-unit test-integration test-e2e test-performance test-security test-accessibility test-all coverage security-scan type-check lint format clean

# Default target
help:  ## Show this help message
	@echo "SpanishMaster Testing Suite"
	@echo "=========================="
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Installation
install:  ## Install all dependencies including dev dependencies
	pip install -e ".[dev]"

install-ci:  ## Install dependencies for CI environment
	pip install -e ".[dev]"
	pip install pytest-github-actions-annotate-failures

# Test commands
test:  ## Run all tests with coverage
	pytest --cov --cov-report=term-missing --cov-report=html

test-unit:  ## Run unit tests only
	pytest tests/unit/ -v

test-integration:  ## Run integration tests only
	pytest tests/integration/ -v

test-e2e:  ## Run end-to-end tests only
	pytest tests/e2e/ -v --maxfail=3

test-performance:  ## Run performance tests only
	pytest tests/performance/ -v -m performance --durations=0

test-security:  ## Run security tests only
	pytest tests/security/ -v -m security

test-accessibility:  ## Run accessibility tests only
	pytest tests/accessibility/ -v -m accessibility

test-gui:  ## Run GUI tests only (requires display)
	pytest -v -m gui

test-no-gui:  ## Run non-GUI tests only
	pytest -v -m "not gui"

test-fast:  ## Run fast tests only (exclude slow and performance)
	pytest -v -m "not slow and not performance"

test-all:  ## Run comprehensive test suite
	pytest --cov --cov-report=term-missing --cov-report=html --cov-report=xml

# Test with different markers
test-database:  ## Run database-related tests
	pytest -v -m database

test-network:  ## Run network-related tests (if any)
	pytest -v -m network

# Coverage commands
coverage:  ## Generate coverage report
	pytest --cov --cov-report=term-missing --cov-report=html
	@echo "Coverage report generated in tests/coverage_html/index.html"

coverage-xml:  ## Generate XML coverage report for CI
	pytest --cov --cov-report=xml

# Quality assurance
security-scan:  ## Run security scanning with bandit
	bandit -r models/ views/ utils/ controllers/ -f json -o tests/security_report.json
	bandit -r models/ views/ utils/ controllers/

safety-check:  ## Check for known security vulnerabilities
	safety check

type-check:  ## Run type checking with mypy
	mypy models/ views/ utils/ controllers/

lint:  ## Run linting with ruff
	ruff check models/ views/ utils/ controllers/ tests/

lint-fix:  ## Fix auto-fixable linting issues
	ruff check --fix models/ views/ utils/ controllers/ tests/

format:  ## Format code with ruff
	ruff format models/ views/ utils/ controllers/ tests/

format-check:  ## Check if code is properly formatted
	ruff format --check models/ views/ utils/ controllers/ tests/

# Quality checks (all)
quality:  ## Run all quality checks
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) security-scan
	$(MAKE) safety-check

# CI/CD commands
ci-test:  ## Run tests for CI environment
	pytest --cov --cov-report=xml --cov-report=term --maxfail=5 -v

ci-quality:  ## Run quality checks for CI
	ruff check models/ views/ utils/ controllers/
	mypy models/ views/ utils/ controllers/
	bandit -r models/ views/ utils/ controllers/

# Performance and profiling
profile:  ## Run tests with profiling
	pytest --profile-svg tests/performance/

benchmark:  ## Run performance benchmarks
	pytest tests/performance/ -v --benchmark-only

# Stress testing
stress-test:  ## Run stress tests
	pytest tests/performance/ -v -k "stress or concurrent" --maxfail=1

load-test:  ## Run load tests (if implemented with locust)
	@echo "Load testing not implemented yet. Would use locust for web components."

# Database testing
test-db-migrations:  ## Test database migrations and schema
	pytest tests/ -v -k "migration or schema"

test-db-performance:  ## Test database performance
	pytest tests/performance/ -v -k "database"

# Accessibility testing
test-a11y:  ## Run accessibility tests (alias for test-accessibility)
	$(MAKE) test-accessibility

# Cleanup commands
clean:  ## Clean up test artifacts and cache
	rm -rf tests/coverage_html/
	rm -f tests/coverage.xml
	rm -f tests/security_report.json
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

clean-db:  ## Clean up test databases
	find . -name "*.db" -path "*/tests/*" -delete
	find . -name "test_*.db" -delete

# Development helpers
watch:  ## Run tests in watch mode (requires pytest-watch)
	ptw --runner "pytest --testmon"

debug:  ## Run tests with debugging enabled
	pytest -v -s --pdb

test-verbose:  ## Run tests with maximum verbosity
	pytest -vvv --tb=long

# Test data management
generate-test-data:  ## Generate test data for manual testing
	python -m tests.fixtures.generate_test_data

# Reporting
test-report:  ## Generate comprehensive test report
	pytest --html=tests/test_report.html --self-contained-html

coverage-badge:  ## Generate coverage badge (requires coverage-badge)
	coverage-badge -f -o coverage.svg

# Documentation testing
test-docs:  ## Test code examples in documentation
	@echo "Documentation testing not implemented yet"

# Environment testing
test-python-versions:  ## Test against multiple Python versions (requires tox)
	@echo "Multi-version testing not implemented yet. Would use tox or nox."

# Platform testing
test-windows:  ## Run Windows-specific tests
	pytest -v -m "not gui or windows"

test-linux:  ## Run Linux-specific tests
	pytest -v -m "not gui or linux"

test-macos:  ## Run macOS-specific tests
	pytest -v -m "not gui or macos"

# Integration with external tools
test-with-coverage-threshold:  ## Run tests and fail if coverage below threshold
	pytest --cov --cov-fail-under=80

# Parallel testing
test-parallel:  ## Run tests in parallel (requires pytest-xdist)
	pytest -n auto --cov

# Memory testing
test-memory:  ## Run tests with memory profiling
	pytest tests/performance/ -v -k "memory"

# Test specific modules
test-models:  ## Test models only
	pytest tests/unit/test_*model* tests/integration/ -v

test-views:  ## Test views only  
	pytest tests/unit/test_ui* tests/unit/test_*view* -v

test-utils:  ## Test utilities only
	pytest tests/unit/ -v -k "util"

# Special test runs
test-regression:  ## Run regression test suite
	pytest tests/ -v --maxfail=1 -m "not performance"

test-smoke:  ## Run smoke tests (basic functionality)
	pytest tests/unit/test_database.py tests/integration/test_app_integration.py::TestDatabaseModelIntegration::test_session_vocab_integration -v

# Export test results
export-junit:  ## Export test results in JUnit XML format
	pytest --junitxml=tests/junit_results.xml

export-coverage:  ## Export coverage in multiple formats
	pytest --cov --cov-report=html --cov-report=xml --cov-report=json

# Utility targets
list-tests:  ## List all available tests
	pytest --collect-only -q

list-markers:  ## List all test markers
	pytest --markers

# Help for specific test categories
help-performance:  ## Show help for performance testing
	@echo "Performance Testing Commands:"
	@echo "  test-performance     - Run all performance tests"
	@echo "  benchmark           - Run benchmarks only"  
	@echo "  stress-test         - Run stress tests"
	@echo "  test-memory         - Run memory profiling tests"
	@echo "  profile             - Run with profiling enabled"

help-security:  ## Show help for security testing
	@echo "Security Testing Commands:"
	@echo "  test-security       - Run security-specific tests"
	@echo "  security-scan       - Run bandit security scanner"
	@echo "  safety-check        - Check for known vulnerabilities"

help-accessibility:  ## Show help for accessibility testing
	@echo "Accessibility Testing Commands:"
	@echo "  test-accessibility  - Run WCAG 2.1 compliance tests"
	@echo "  test-a11y          - Alias for accessibility tests"