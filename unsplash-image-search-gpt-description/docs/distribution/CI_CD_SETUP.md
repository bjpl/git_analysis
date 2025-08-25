# CI/CD Setup Guide

Comprehensive guide for setting up Continuous Integration and Continuous Deployment for the Unsplash Image Search with GPT application.

## Table of Contents

- [Overview](#overview)
- [GitHub Actions Setup](#github-actions-setup)
- [Automated Testing](#automated-testing)
- [Automated Building](#automated-building)
- [Automated Release Process](#automated-release-process)
- [Quality Gates](#quality-gates)
- [Security Scanning](#security-scanning)
- [Performance Monitoring](#performance-monitoring)
- [Deployment Strategies](#deployment-strategies)
- [Monitoring and Alerts](#monitoring-and-alerts)

## Overview

### CI/CD Pipeline Goals

1. **Continuous Integration**:
   - Automated testing on every commit
   - Code quality checks
   - Security vulnerability scanning
   - Cross-platform compatibility testing

2. **Continuous Deployment**:
   - Automated builds for multiple platforms
   - Automated packaging and distribution
   - Automated release creation
   - Documentation deployment

### Pipeline Architecture

```
[Code Push] → [Tests] → [Quality Gates] → [Build] → [Package] → [Release]
     │              │           │            │         │          │
     └─[Lint]────────┼───[Security]─┼─[Multi-OS]─┼─[Sign]───┼─[Deploy]
                    │           │            │         │
                [Coverage]  [Performance] [Installer] [Notify]
```

### Supported Platforms

- **GitHub Actions** (Primary)
- **GitLab CI** (Alternative)
- **Azure DevOps** (Enterprise)
- **Local Development** (Developer tools)

## GitHub Actions Setup

### Repository Structure

```
.github/
├── workflows/
│   ├── ci.yml                # Main CI pipeline
│   ├── build.yml             # Multi-platform builds
│   ├── release.yml           # Automated releases
│   ├── security.yml          # Security scanning
│   └── docs.yml              # Documentation deployment
├── ISSUE_TEMPLATE/
│   ├── bug_report.md
│   └── feature_request.md
└── PULL_REQUEST_TEMPLATE.md
```

### Main CI Pipeline

Create `.github/workflows/ci.yml`:

```yaml
name: Continuous Integration

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  PYTHON_VERSION: '3.11'
  NODE_VERSION: '18'

jobs:
  test:
    name: Test Suite
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11']
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        fetch-depth: 0  # Full history for better analysis
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        cache: 'pip'
        cache-dependency-path: '**/requirements*.txt'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run linting
      run: |
        black --check --diff .
        isort --check-only --diff .
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
    
    - name: Run type checking
      run: mypy . --ignore-missing-imports
    
    - name: Run tests
      run: |
        pytest --cov=. --cov-report=xml --cov-report=term-missing --cov-fail-under=80
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: false

  security:
    name: Security Scan
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install safety bandit
        pip install -r requirements.txt
    
    - name: Run safety check
      run: safety check --json --output safety-report.json || true
    
    - name: Run bandit security scan
      run: bandit -r . -f json -o bandit-report.json || true
    
    - name: Upload security reports
      uses: actions/upload-artifact@v3
      with:
        name: security-reports
        path: |
          safety-report.json
          bandit-report.json

  integration:
    name: Integration Tests
    runs-on: ubuntu-latest
    needs: [test, security]
    if: github.event_name == 'push' || github.event.pull_request.draft == false
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
        cache: 'pip'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
        sudo apt-get update
        sudo apt-get install -y python3-tk xvfb
    
    - name: Run integration tests
      run: |
        xvfb-run -a pytest tests/integration/ -v --tb=short
    
    - name: Test application startup
      run: |
        timeout 30 xvfb-run -a python main.py --version || exit 1
```

### Multi-Platform Build Pipeline

Create `.github/workflows/build.yml`:

```yaml
name: Multi-Platform Builds

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:
    inputs:
      create_release:
        description: 'Create release after successful build'
        required: false
        default: 'false'
        type: boolean

env:
  PYTHON_VERSION: '3.11'

jobs:
  build:
    name: Build ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        include:
          - os: windows-latest
            artifact_name: unsplash-gpt-tool.exe
            asset_name: unsplash-gpt-tool-windows.exe
          - os: macos-latest
            artifact_name: unsplash-gpt-tool
            asset_name: unsplash-gpt-tool-macos
          - os: ubuntu-latest
            artifact_name: unsplash-gpt-tool
            asset_name: unsplash-gpt-tool-linux
    
    runs-on: ${{ matrix.os }}
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        fetch-depth: 0
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
        cache: 'pip'
    
    - name: Install system dependencies (Linux)
      if: matrix.os == 'ubuntu-latest'
      run: |
        sudo apt-get update
        sudo apt-get install -y python3-tk python3-dev
    
    - name: Install system dependencies (macOS)
      if: matrix.os == 'macos-latest'
      run: |
        brew install python-tk
    
    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller
    
    - name: Build application (Windows)
      if: matrix.os == 'windows-latest'
      run: |
        pyinstaller --clean --onefile --windowed `
          --name unsplash-gpt-tool `
          --icon assets/icon.ico `
          --add-data ".env.example;." `
          --add-data "README.md;." `
          --hidden-import tkinter `
          --hidden-import PIL `
          --hidden-import openai `
          main.py
    
    - name: Build application (Unix)
      if: matrix.os != 'windows-latest'
      run: |
        pyinstaller --clean --onefile --windowed \
          --name unsplash-gpt-tool \
          --add-data ".env.example:." \
          --add-data "README.md:." \
          --hidden-import tkinter \
          --hidden-import PIL \
          --hidden-import openai \
          main.py
    
    - name: Test executable
      shell: bash
      run: |
        if [[ "${{ matrix.os }}" == "windows-latest" ]]; then
          ./dist/unsplash-gpt-tool.exe --version || echo "Version check failed"
        else
          ./dist/unsplash-gpt-tool --version || echo "Version check failed"
        fi
    
    - name: Create portable package (Windows)
      if: matrix.os == 'windows-latest'
      run: |
        mkdir portable
        copy dist\unsplash-gpt-tool.exe portable\
        copy README.md portable\
        copy .env.example portable\
        echo "Portable version - no installation required" > portable\PORTABLE.txt
        Compress-Archive -Path portable\* -DestinationPath unsplash-gpt-tool-portable-windows.zip
    
    - name: Upload build artifacts
      uses: actions/upload-artifact@v3
      with:
        name: builds-${{ matrix.os }}
        path: |
          dist/${{ matrix.artifact_name }}
          *.zip
        retention-days: 30
    
    - name: Upload to release
      if: startsWith(github.ref, 'refs/tags/')
      uses: softprops/action-gh-release@v1
      with:
        files: |
          dist/${{ matrix.artifact_name }}
          *.zip
        draft: true
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Automated Release Pipeline

Create `.github/workflows/release.yml`:

```yaml
name: Automated Release

on:
  push:
    tags:
      - 'v*.*.*'
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to release (e.g., v1.2.3)'
        required: true
        type: string

env:
  PYTHON_VERSION: '3.11'

jobs:
  create-release:
    name: Create Release
    runs-on: ubuntu-latest
    outputs:
      upload_url: ${{ steps.create_release.outputs.upload_url }}
      version: ${{ steps.get_version.outputs.version }}
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        fetch-depth: 0
    
    - name: Get version
      id: get_version
      run: |
        if [[ "${{ github.event_name }}" == "workflow_dispatch" ]]; then
          echo "version=${{ github.event.inputs.version }}" >> $GITHUB_OUTPUT
        else
          echo "version=${GITHUB_REF#refs/tags/}" >> $GITHUB_OUTPUT
        fi
    
    - name: Generate changelog
      run: |
        # Extract changelog for this version
        awk '/^## \[${{ steps.get_version.outputs.version }}\]/{flag=1; next} /^## \[/{flag=0} flag' CHANGELOG.md > RELEASE_NOTES.md
        
        # If no specific changelog, create generic one
        if [ ! -s RELEASE_NOTES.md ]; then
          echo "## Changes in ${{ steps.get_version.outputs.version }}" > RELEASE_NOTES.md
          echo "" >> RELEASE_NOTES.md
          echo "See [CHANGELOG.md](CHANGELOG.md) for detailed changes." >> RELEASE_NOTES.md
        fi
    
    - name: Create Release
      id: create_release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ steps.get_version.outputs.version }}
        release_name: Release ${{ steps.get_version.outputs.version }}
        body_path: RELEASE_NOTES.md
        draft: false
        prerelease: ${{ contains(steps.get_version.outputs.version, 'alpha') || contains(steps.get_version.outputs.version, 'beta') || contains(steps.get_version.outputs.version, 'rc') }}

  build-and-upload:
    name: Build and Upload
    needs: create-release
    strategy:
      matrix:
        include:
          - os: windows-latest
            asset_name: unsplash-gpt-tool-windows.exe
            portable_name: unsplash-gpt-tool-portable-windows.zip
          - os: macos-latest
            asset_name: unsplash-gpt-tool-macos
          - os: ubuntu-latest
            asset_name: unsplash-gpt-tool-linux
    
    runs-on: ${{ matrix.os }}
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
        cache: 'pip'
    
    - name: Install system dependencies
      shell: bash
      run: |
        if [[ "${{ matrix.os }}" == "ubuntu-latest" ]]; then
          sudo apt-get update
          sudo apt-get install -y python3-tk
        elif [[ "${{ matrix.os }}" == "macos-latest" ]]; then
          brew install python-tk
        fi
    
    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller
    
    - name: Build application
      shell: bash
      run: |
        if [[ "${{ matrix.os }}" == "windows-latest" ]]; then
          pyinstaller --clean --onefile --windowed \
            --name unsplash-gpt-tool \
            --icon assets/icon.ico \
            --add-data ".env.example;." \
            --add-data "README.md;." \
            --hidden-import tkinter \
            --hidden-import PIL \
            --hidden-import openai \
            main.py
        else
          pyinstaller --clean --onefile --windowed \
            --name unsplash-gpt-tool \
            --add-data ".env.example:." \
            --add-data "README.md:." \
            --hidden-import tkinter \
            --hidden-import PIL \
            --hidden-import openai \
            main.py
        fi
    
    - name: Create portable package (Windows)
      if: matrix.os == 'windows-latest'
      run: |
        mkdir portable
        copy dist\unsplash-gpt-tool.exe portable\
        copy README.md portable\
        copy .env.example portable\
        copy LICENSE portable\
        echo "Portable version - no installation required" > portable\PORTABLE.txt
        Compress-Archive -Path portable\* -DestinationPath ${{ matrix.portable_name }}
    
    - name: Upload Release Asset
      uses: actions/upload-release-asset@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        upload_url: ${{ needs.create-release.outputs.upload_url }}
        asset_path: dist/unsplash-gpt-tool${{ matrix.os == 'windows-latest' && '.exe' || '' }}
        asset_name: ${{ matrix.asset_name }}
        asset_content_type: application/octet-stream
    
    - name: Upload Portable Package (Windows)
      if: matrix.os == 'windows-latest'
      uses: actions/upload-release-asset@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        upload_url: ${{ needs.create-release.outputs.upload_url }}
        asset_path: ${{ matrix.portable_name }}
        asset_name: ${{ matrix.portable_name }}
        asset_content_type: application/zip

  create-installer:
    name: Create Windows Installer
    needs: create-release
    runs-on: windows-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Install dependencies and build
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pyinstaller
        pyinstaller --clean --onefile --windowed `
          --name unsplash-image-search `
          --icon assets/icon.ico `
          --add-data ".env.example;." `
          --add-data "README.md;." `
          --add-data "docs;docs" `
          main.py
    
    - name: Install NSIS
      run: |
        choco install nsis -y
        refreshenv
    
    - name: Build installer
      run: |
        & "C:\Program Files (x86)\NSIS\makensis.exe" installer\installer.nsi
    
    - name: Upload Installer
      uses: actions/upload-release-asset@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        upload_url: ${{ needs.create-release.outputs.upload_url }}
        asset_path: installer/output/unsplash-image-search-nsis-setup.exe
        asset_name: unsplash-image-search-installer-${{ needs.create-release.outputs.version }}.exe
        asset_content_type: application/octet-stream

  notify:
    name: Notify Release
    needs: [create-release, build-and-upload, create-installer]
    runs-on: ubuntu-latest
    
    steps:
    - name: Notify Discord (if configured)
      if: env.DISCORD_WEBHOOK_URL != ''
      env:
        DISCORD_WEBHOOK_URL: ${{ secrets.DISCORD_WEBHOOK_URL }}
      run: |
        curl -H "Content-Type: application/json" \
          -X POST \
          -d '{"content":"🚀 New release: **${{ needs.create-release.outputs.version }}** is now available!"}' \
          $DISCORD_WEBHOOK_URL
    
    - name: Update documentation site
      # Add steps to deploy updated documentation
      run: echo "Documentation update would go here"
```

## Automated Testing

### Test Categories

#### Unit Tests
```yaml
# In ci.yml
- name: Run unit tests
  run: |
    pytest tests/unit/ -v --cov=src/ --cov-report=term-missing
```

#### Integration Tests
```yaml
- name: Run integration tests
  run: |
    # Test API integrations with mock services
    pytest tests/integration/ -v --tb=short
```

#### UI Tests
```yaml
- name: Run UI tests
  run: |
    # Run GUI tests in headless mode
    xvfb-run -a pytest tests/ui/ -v
```

#### Performance Tests
```yaml
- name: Run performance tests
  run: |
    pytest tests/performance/ -v --benchmark-only
```

### Test Configuration

Create `pytest.ini`:
```ini
[tool:pytest]
minversion = 6.0
addopts = 
    -ra
    --strict-markers
    --strict-config
    --cov=src
    --cov-report=term-missing:skip-covered
    --cov-report=html:htmlcov
    --cov-report=xml
    --cov-fail-under=80
testpaths = 
    tests
markers =
    unit: Unit tests
    integration: Integration tests
    ui: UI/GUI tests
    performance: Performance benchmarks
    slow: Slow tests (skipped in quick runs)
    api: Tests requiring API access
```

### Test Data Management

Create `conftest.py`:
```python
import pytest
import os
from unittest.mock import Mock, patch
from pathlib import Path

@pytest.fixture
def mock_api_keys():
    """Provide mock API keys for testing"""
    with patch.dict(os.environ, {
        'UNSPLASH_ACCESS_KEY': 'test_unsplash_key',
        'OPENAI_API_KEY': 'test_openai_key'
    }):
        yield

@pytest.fixture
def temp_data_dir(tmp_path):
    """Provide temporary directory for test data"""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir

@pytest.fixture
def mock_unsplash_response():
    """Mock Unsplash API response"""
    return {
        'results': [{
            'id': 'test123',
            'urls': {
                'regular': 'https://example.com/test.jpg'
            },
            'description': 'Test image'
        }]
    }

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "Test Spanish description"
    return mock_response
```

## Quality Gates

### Code Quality Checks

#### Linting Configuration

Create `.flake8`:
```ini
[flake8]
max-line-length = 88
max-complexity = 10
select = E,W,F,C,N
ignore = 
    E203,  # whitespace before ':'
    E501,  # line too long (handled by black)
    W503,  # line break before binary operator
exclude = 
    .git,
    __pycache__,
    build,
    dist,
    .eggs,
    *.egg-info,
    .venv,
    venv
per-file-ignores =
    __init__.py:F401
    tests/*:S101,S311
```

#### Type Checking

Create `mypy.ini`:
```ini
[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True
show_error_codes = True

[mypy-tkinter.*]
ignore_missing_imports = True

[mypy-PIL.*]
ignore_missing_imports = True

[mypy-openai.*]
ignore_missing_imports = True
```

### Coverage Requirements

```yaml
# Minimum coverage thresholds
- name: Check coverage
  run: |
    coverage report --fail-under=80
    coverage xml
```

### Performance Benchmarks

```yaml
- name: Run performance benchmarks
  run: |
    pytest tests/performance/ --benchmark-json=benchmark.json
    
- name: Check performance regression
  run: |
    python scripts/check_performance.py benchmark.json
```

## Security Scanning

### Dependency Scanning

```yaml
- name: Security scan dependencies
  run: |
    safety check --json --output safety-report.json
    
- name: Scan for secrets
  uses: trufflesecurity/trufflehog@main
  with:
    path: ./
    base: main
    head: HEAD
```

### Code Security Analysis

```yaml
- name: Run Bandit security scan
  run: |
    bandit -r . -f json -o bandit-report.json
    
- name: Upload security reports
  uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: bandit-report.json
```

### Supply Chain Security

```yaml
- name: Check for known vulnerabilities
  run: |
    pip-audit --format=json --output=audit-report.json
```

## Performance Monitoring

### Build Performance

```yaml
- name: Monitor build time
  run: |
    echo "Build started at: $(date)"
    time pyinstaller --onefile main.py
    echo "Build completed at: $(date)"
```

### Application Performance

```python
# tests/performance/test_startup.py
import pytest
import time
import subprocess

def test_startup_time():
    """Test application startup time"""
    start_time = time.time()
    
    # Start application in test mode
    process = subprocess.Popen(
        ['python', 'main.py', '--test-mode'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for startup
    process.communicate(timeout=30)
    
    startup_time = time.time() - start_time
    
    # Assert startup time is reasonable
    assert startup_time < 10, f"Startup time too slow: {startup_time}s"
```

## Deployment Strategies

### Staging Environment

```yaml
deploy-staging:
  name: Deploy to Staging
  runs-on: ubuntu-latest
  needs: [test, security]
  if: github.ref == 'refs/heads/develop'
  
  steps:
  - name: Deploy to staging
    run: |
      # Deploy to staging environment
      echo "Deploying to staging"
```

### Production Deployment

```yaml
deploy-production:
  name: Deploy to Production
  runs-on: ubuntu-latest
  needs: [create-release]
  if: startsWith(github.ref, 'refs/tags/v')
  
  steps:
  - name: Deploy to production
    run: |
      # Update download links
      # Notify users
      # Update documentation
      echo "Deploying to production"
```

### Rollback Strategy

```yaml
rollback:
  name: Rollback Release
  runs-on: ubuntu-latest
  if: failure()
  
  steps:
  - name: Rollback changes
    run: |
      # Remove faulty release
      # Restore previous version
      # Notify stakeholders
      echo "Rolling back release"
```

## Monitoring and Alerts

### Build Status Notifications

```yaml
- name: Notify on failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: failure
    channel: '#ci-cd'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Performance Alerts

```python
# scripts/check_performance.py
import json
import sys

def check_performance_regression(benchmark_file, threshold=1.5):
    """Check for performance regression"""
    with open(benchmark_file) as f:
        data = json.load(f)
    
    for benchmark in data['benchmarks']:
        if benchmark['stats']['mean'] > threshold:
            print(f"Performance regression detected: {benchmark['name']}")
            sys.exit(1)
    
    print("No performance regression detected")

if __name__ == '__main__':
    check_performance_regression(sys.argv[1])
```

### Health Checks

```yaml
- name: Health check
  run: |
    # Test that executable works
    timeout 30 ./dist/unsplash-gpt-tool --version
    
    # Test basic functionality
    python scripts/health_check.py
```

## Local Development Integration

### Pre-commit Hooks

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
  
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.1
    hooks:
      - id: mypy
        additional_dependencies: [types-requests, types-pillow]
```

### Local Testing Script

Create `scripts/local_ci.py`:
```python
#!/usr/bin/env python3
"""
Local CI script to run the same checks as GitHub Actions
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run command and report results"""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*50}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} PASSED")
    else:
        print(f"❌ {description} FAILED")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False
    
    return True

def main():
    """Run local CI checks"""
    checks = [
        ("black --check --diff .", "Code formatting (Black)"),
        ("isort --check-only --diff .", "Import sorting (isort)"),
        ("flake8 .", "Linting (flake8)"),
        ("mypy . --ignore-missing-imports", "Type checking (mypy)"),
        ("pytest tests/unit/ -v", "Unit tests"),
        ("pytest --cov=. --cov-report=term-missing", "Coverage tests"),
        ("safety check", "Security scan (safety)"),
        ("bandit -r . -f json", "Security scan (bandit)"),
    ]
    
    failed_checks = []
    
    for cmd, description in checks:
        if not run_command(cmd, description):
            failed_checks.append(description)
    
    print(f"\n{'='*50}")
    print("LOCAL CI SUMMARY")
    print(f"{'='*50}")
    
    if failed_checks:
        print(f"❌ {len(failed_checks)} checks failed:")
        for check in failed_checks:
            print(f"  - {check}")
        sys.exit(1)
    else:
        print("✅ All checks passed!")
        print("Ready to push to GitHub")

if __name__ == '__main__':
    main()
```

## Troubleshooting CI/CD Issues

### Common Build Failures

#### Dependency Issues
```yaml
- name: Debug dependencies
  if: failure()
  run: |
    pip list
    pip check
    python -c "import sys; print(sys.version)"
```

#### Test Failures
```yaml
- name: Upload test results
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: test-results
    path: |
      pytest-report.xml
      coverage.xml
      htmlcov/
```

#### Build Artifacts Issues
```yaml
- name: Debug build
  if: failure()
  run: |
    ls -la dist/
    file dist/* || true
    ldd dist/* || true  # Linux
```

---

## Summary

This CI/CD setup provides:

1. **Automated testing** on every commit
2. **Multi-platform builds** for Windows, macOS, and Linux
3. **Security scanning** for vulnerabilities
4. **Quality gates** with code coverage requirements
5. **Automated releases** with proper versioning
6. **Performance monitoring** and regression detection
7. **Local development integration** with pre-commit hooks

The pipeline ensures high code quality, security, and reliable releases while providing fast feedback to developers.

**Next Steps**: Customize the workflows for your specific needs, add any additional quality checks, and configure notification channels for your team.