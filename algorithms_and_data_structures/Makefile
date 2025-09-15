# Makefile for Algorithms & Data Structures CLI
# Development automation tasks

# Configuration
PYTHON := python3
PIP := pip3
VENV := venv
VENV_BIN := $(VENV)/bin
PROJECT_NAME := algorithms-cli
SRC_DIR := src
TEST_DIR := tests
DOCS_DIR := docs
SCRIPTS_DIR := scripts

# Python executables (adjust for Windows)
ifeq ($(OS),Windows_NT)
    PYTHON := python
    PIP := pip
    VENV_BIN := $(VENV)/Scripts
    ACTIVATE := $(VENV_BIN)/activate.bat
    PYTHON_EXEC := $(VENV_BIN)/python.exe
    PIP_EXEC := $(VENV_BIN)/pip.exe
else
    ACTIVATE := . $(VENV_BIN)/activate
    PYTHON_EXEC := $(VENV_BIN)/python
    PIP_EXEC := $(VENV_BIN)/pip
endif

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

.PHONY: help install install-dev clean test lint format type-check coverage docs build release \
        docker run-examples benchmark profile security audit setup-env setup-dev \
        quickstart uninstall claude-flow hooks pre-commit setup-git

# Default target
.DEFAULT_GOAL := help

# Help target
help: ## Show this help message
	@echo "$(BLUE)Algorithms & Data Structures CLI - Development Makefile$(NC)"
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# Installation targets
install: ## Install CLI for production use
	@echo "$(BLUE)Installing CLI for production...$(NC)"
	$(PYTHON) -m pip install --upgrade pip
	$(PIP) install -e .
	@echo "$(GREEN)✅ Installation complete!$(NC)"

install-dev: setup-env ## Install CLI for development with all dependencies
	@echo "$(BLUE)Installing development environment...$(NC)"
	$(ACTIVATE) && $(PIP_EXEC) install --upgrade pip
	$(ACTIVATE) && $(PIP_EXEC) install -e ".[dev]"
	$(ACTIVATE) && $(PIP_EXEC) install -r requirements-dev.txt
	@echo "$(GREEN)✅ Development environment ready!$(NC)"

setup-env: ## Create and setup virtual environment
	@echo "$(BLUE)Setting up virtual environment...$(NC)"
	$(PYTHON) -m venv $(VENV)
	$(ACTIVATE) && $(PIP_EXEC) install --upgrade pip wheel setuptools
	@echo "$(GREEN)✅ Virtual environment created at $(VENV)$(NC)"

setup-dev: setup-env install-dev setup-git pre-commit ## Complete development setup
	@echo "$(GREEN)✅ Development environment fully configured!$(NC)"

setup-git: ## Setup Git hooks and configuration
	@echo "$(BLUE)Setting up Git configuration...$(NC)"
	git config --local core.autocrlf input
	git config --local pull.rebase true
	git config --local branch.autosetupmerge always
	@echo "$(GREEN)✅ Git configured$(NC)"

pre-commit: ## Install pre-commit hooks
	@echo "$(BLUE)Installing pre-commit hooks...$(NC)"
	$(ACTIVATE) && pre-commit install
	$(ACTIVATE) && pre-commit install --hook-type commit-msg
	@echo "$(GREEN)✅ Pre-commit hooks installed$(NC)"

# Quality assurance targets
test: ## Run test suite
	@echo "$(BLUE)Running tests...$(NC)"
	$(ACTIVATE) && $(PYTHON_EXEC) -m pytest $(TEST_DIR)/ -v
	@echo "$(GREEN)✅ Tests completed$(NC)"

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	$(ACTIVATE) && $(PYTHON_EXEC) -m pytest $(TEST_DIR)/ \
		--cov=$(SRC_DIR) \
		--cov-report=html \
		--cov-report=term \
		--cov-report=xml \
		--cov-fail-under=80
	@echo "$(GREEN)✅ Coverage report generated in htmlcov/$(NC)"

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	$(ACTIVATE) && $(PYTHON_EXEC) -m pytest-watch $(TEST_DIR)/ -- -v

lint: ## Run linting checks
	@echo "$(BLUE)Running linting checks...$(NC)"
	$(ACTIVATE) && flake8 $(SRC_DIR)/ $(TEST_DIR)/ $(SCRIPTS_DIR)/
	@echo "$(GREEN)✅ Linting completed$(NC)"

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	$(ACTIVATE) && black $(SRC_DIR)/ $(TEST_DIR)/ $(SCRIPTS_DIR)/
	$(ACTIVATE) && isort $(SRC_DIR)/ $(TEST_DIR)/ $(SCRIPTS_DIR)/
	@echo "$(GREEN)✅ Code formatted$(NC)"

format-check: ## Check code formatting without making changes
	@echo "$(BLUE)Checking code formatting...$(NC)"
	$(ACTIVATE) && black --check $(SRC_DIR)/ $(TEST_DIR)/ $(SCRIPTS_DIR)/
	$(ACTIVATE) && isort --check-only $(SRC_DIR)/ $(TEST_DIR)/ $(SCRIPTS_DIR)/

type-check: ## Run type checking with mypy
	@echo "$(BLUE)Running type checking...$(NC)"
	$(ACTIVATE) && mypy $(SRC_DIR)/ --ignore-missing-imports
	@echo "$(GREEN)✅ Type checking completed$(NC)"

security: ## Run security checks
	@echo "$(BLUE)Running security checks...$(NC)"
	$(ACTIVATE) && bandit -r $(SRC_DIR)/ -f json -o bandit-report.json
	$(ACTIVATE) && safety check --json --output safety-report.json
	@echo "$(GREEN)✅ Security scan completed$(NC)"

audit: ## Run comprehensive code audit
	@echo "$(BLUE)Running comprehensive audit...$(NC)"
	$(MAKE) lint
	$(MAKE) type-check  
	$(MAKE) security
	$(MAKE) test-coverage
	@echo "$(GREEN)✅ Audit completed successfully$(NC)"

# Documentation targets
docs: ## Generate documentation
	@echo "$(BLUE)Generating documentation...$(NC)"
	$(ACTIVATE) && sphinx-build -b html $(DOCS_DIR)/ $(DOCS_DIR)/_build/html/
	@echo "$(GREEN)✅ Documentation generated in $(DOCS_DIR)/_build/html/$(NC)"

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Starting documentation server...$(NC)"
	$(ACTIVATE) && python -m http.server 8000 -d $(DOCS_DIR)/_build/html/
	@echo "$(GREEN)Documentation available at http://localhost:8000$(NC)"

docs-clean: ## Clean documentation build
	rm -rf $(DOCS_DIR)/_build/

# Build and release targets  
build: ## Build distribution packages
	@echo "$(BLUE)Building distribution packages...$(NC)"
	$(ACTIVATE) && $(PYTHON_EXEC) -m build
	@echo "$(GREEN)✅ Distribution packages built in dist/$(NC)"

build-clean: ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info/ .eggs/

release-check: ## Check if ready for release
	@echo "$(BLUE)Checking release readiness...$(NC)"
	$(ACTIVATE) && $(PYTHON_EXEC) -m twine check dist/*
	$(MAKE) audit
	@echo "$(GREEN)✅ Ready for release$(NC)"

release: build release-check ## Build and publish release
	@echo "$(BLUE)Publishing release...$(NC)"
	$(ACTIVATE) && $(PYTHON_EXEC) -m twine upload dist/*
	@echo "$(GREEN)✅ Release published$(NC)"

release-test: build ## Test release on test PyPI
	@echo "$(BLUE)Publishing to test PyPI...$(NC)"
	$(ACTIVATE) && $(PYTHON_EXEC) -m twine upload --repository testpypi dist/*

# Performance and profiling
benchmark: ## Run performance benchmarks
	@echo "$(BLUE)Running benchmarks...$(NC)"
	$(ACTIVATE) && $(PYTHON_EXEC) -m pytest benchmarks/ -v --benchmark-only
	@echo "$(GREEN)✅ Benchmarks completed$(NC)"

profile: ## Profile CLI performance
	@echo "$(BLUE)Profiling CLI performance...$(NC)"
	$(ACTIVATE) && $(PYTHON_EXEC) -m cProfile -o profile.stats $(SRC_DIR)/main.py --help
	$(ACTIVATE) && $(PYTHON_EXEC) -c "import pstats; p=pstats.Stats('profile.stats'); p.sort_stats('cumulative'); p.print_stats(20)"
	@echo "$(GREEN)✅ Profiling completed$(NC)"

# Docker targets
docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker build -t $(PROJECT_NAME):latest .
	@echo "$(GREEN)✅ Docker image built$(NC)"

docker-run: ## Run CLI in Docker container
	@echo "$(BLUE)Running CLI in Docker...$(NC)"
	docker run --rm -it $(PROJECT_NAME):latest

docker-test: ## Run tests in Docker container
	@echo "$(BLUE)Running tests in Docker...$(NC)"
	docker run --rm $(PROJECT_NAME):latest pytest tests/ -v

# Example and demo targets
run-examples: ## Run example algorithms
	@echo "$(BLUE)Running example algorithms...$(NC)"
	$(ACTIVATE) && $(PYTHON_EXEC) examples/sorting_demo.py
	$(ACTIVATE) && $(PYTHON_EXEC) examples/search_demo.py
	@echo "$(GREEN)✅ Examples completed$(NC)"

demo: ## Run interactive demo
	@echo "$(BLUE)Starting interactive demo...$(NC)"
	$(ACTIVATE) && $(PYTHON_EXEC) -m algorithms_cli demo

quickstart: ## Run quickstart wizard
	@echo "$(BLUE)Starting quickstart wizard...$(NC)"
	$(PYTHON) $(SCRIPTS_DIR)/quickstart.py

# Claude Flow integration
claude-flow: ## Setup Claude Flow integration
	@echo "$(BLUE)Setting up Claude Flow integration...$(NC)"
	npm install -g claude-flow@alpha
	npx claude-flow@alpha mcp add
	@echo "$(GREEN)✅ Claude Flow configured$(NC)"

sparc: ## Run SPARC workflow
	@echo "$(BLUE)Starting SPARC workflow...$(NC)"
	$(ACTIVATE) && npx claude-flow sparc tdd "$(filter-out $@,$(MAKECMDGOALS))"

hooks: ## Setup development hooks
	@echo "$(BLUE)Setting up development hooks...$(NC)"
	npx claude-flow@alpha hooks setup
	@echo "$(GREEN)✅ Development hooks configured$(NC)"

# Installation script targets
install-unix: ## Run Unix installation script
	@echo "$(BLUE)Running Unix installation script...$(NC)"
	chmod +x install.sh
	./install.sh

install-windows: ## Run Windows installation script
	@echo "$(BLUE)Running Windows installation script...$(NC)"
	powershell -ExecutionPolicy Bypass -File install.ps1

install-python: ## Run Python setup script
	@echo "$(BLUE)Running Python setup script...$(NC)"
	$(PYTHON) $(SCRIPTS_DIR)/setup.py

# Cleanup targets
clean: ## Clean build and cache files
	@echo "$(BLUE)Cleaning build and cache files...$(NC)"
	rm -rf build/ dist/ *.egg-info/ .eggs/
	rm -rf .pytest_cache/ .coverage htmlcov/ .tox/
	rm -rf $(SRC_DIR)/**/__pycache__/ $(TEST_DIR)/**/__pycache__/
	rm -rf .mypy_cache/ .ruff_cache/
	rm -f *.log profile.stats bandit-report.json safety-report.json
	@echo "$(GREEN)✅ Cleanup completed$(NC)"

clean-all: clean docs-clean build-clean ## Deep clean all generated files
	rm -rf $(VENV)/
	rm -rf node_modules/
	@echo "$(GREEN)✅ Deep cleanup completed$(NC)"

uninstall: ## Uninstall CLI and cleanup
	@echo "$(BLUE)Uninstalling CLI...$(NC)"
	$(PIP) uninstall -y $(PROJECT_NAME) || true
	$(MAKE) clean-all
	@echo "$(GREEN)✅ CLI uninstalled$(NC)"

# Development workflow shortcuts
dev: setup-dev ## Quick development setup
	@echo "$(GREEN)🚀 Development environment ready!$(NC)"
	@echo "Next steps:"
	@echo "  make test     - Run tests"
	@echo "  make format   - Format code"
	@echo "  make audit    - Full quality check"
	@echo "  make demo     - Try the CLI"

check: audit ## Run all quality checks

fix: format ## Auto-fix code issues
	@echo "$(GREEN)✅ Code issues fixed$(NC)"

# CI/CD helpers
ci-setup: ## Setup for CI environment
	$(PYTHON) -m pip install --upgrade pip wheel setuptools
	$(PIP) install -e ".[dev]"

ci-test: ## Run CI test suite
	$(PYTHON) -m pytest $(TEST_DIR)/ \
		--cov=$(SRC_DIR) \
		--cov-report=xml \
		--cov-report=term \
		--junitxml=pytest-report.xml \
		-v

ci-lint: ## Run CI linting
	flake8 $(SRC_DIR)/ $(TEST_DIR)/ $(SCRIPTS_DIR)/ --format=github
	black --check $(SRC_DIR)/ $(TEST_DIR)/ $(SCRIPTS_DIR)/
	isort --check-only $(SRC_DIR)/ $(TEST_DIR)/ $(SCRIPTS_DIR)/
	mypy $(SRC_DIR)/ --ignore-missing-imports

# Information targets
info: ## Show project information
	@echo "$(BLUE)Project Information:$(NC)"
	@echo "Name: $(PROJECT_NAME)"
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "Virtual Environment: $(VENV)"
	@echo "Source Directory: $(SRC_DIR)"
	@echo "Test Directory: $(TEST_DIR)"
	@echo "Documentation: $(DOCS_DIR)"
	@echo ""
	@echo "$(GREEN)Quick Commands:$(NC)"
	@echo "  make dev      - Setup development environment"
	@echo "  make test     - Run tests"
	@echo "  make format   - Format code"
	@echo "  make audit    - Full quality check"
	@echo "  make build    - Build distribution"

env: ## Show environment information
	@echo "$(BLUE)Environment Information:$(NC)"
	@echo "OS: $(OS)"
	@echo "Python: $(shell $(PYTHON) --version 2>&1)"
	@echo "Pip: $(shell $(PIP) --version 2>&1)"
	@echo "Git: $(shell git --version 2>&1)"
	@echo "Node: $(shell node --version 2>/dev/null || echo 'Not installed')"
	@echo "NPM: $(shell npm --version 2>/dev/null || echo 'Not installed')"
	@echo ""
	@echo "$(GREEN)Python Packages:$(NC)"
	@$(PIP) list 2>/dev/null | head -10 || echo "Virtual environment not activated"

# Allow passing arguments to specific targets
%:
	@: