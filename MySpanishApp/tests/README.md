# SpanishMaster Testing Suite

A comprehensive testing framework for the SpanishMaster application, providing unit tests, integration tests, end-to-end tests, performance testing, security testing, and accessibility testing.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -e ".[dev]"

# Run all tests
python tests/test_runner.py --all

# Run with coverage
python tests/test_runner.py --coverage

# Run specific test types
python tests/test_runner.py --unit --verbose
python tests/test_runner.py --integration
python tests/test_runner.py --e2e
```

## 📁 Test Structure

```
tests/
├── conftest.py                     # Shared pytest fixtures and configuration
├── pytest.ini                     # Pytest configuration
├── test_runner.py                  # Unified test runner script
├── Makefile                        # Make targets for test commands
├── README.md                       # This file
│
├── unit/                           # Unit tests
│   ├── test_database.py           # Database class tests
│   ├── test_session_model.py      # Session model tests
│   ├── test_vocab_model.py        # Vocabulary model tests
│   └── test_ui_components.py      # PyQt6 UI component tests
│
├── integration/                    # Integration tests
│   └── test_app_integration.py    # Full application integration
│
├── e2e/                           # End-to-end tests
│   └── test_user_journeys.py     # Complete user workflows
│
├── performance/                    # Performance tests
│   └── test_performance.py       # Load, stress, and performance tests
│
├── security/                      # Security tests
│   └── test_security.py          # Security vulnerability tests
│
└── accessibility/                 # Accessibility tests
    └── test_accessibility.py     # WCAG 2.1 compliance tests
```

## 🧪 Test Types

### Unit Tests (`tests/unit/`)
- **Database Tests**: Connection handling, schema validation, CRUD operations
- **Model Tests**: Session, vocabulary, and grammar model functionality
- **UI Component Tests**: PyQt6 widget testing, user interactions
- **Utility Tests**: Helper functions and utility classes

### Integration Tests (`tests/integration/`)
- **Module Integration**: Testing interactions between different components
- **Database-Model Integration**: End-to-end data flow testing
- **UI-Model Integration**: User interface with backend integration

### End-to-End Tests (`tests/e2e/`)
- **Complete User Journeys**: Full workflows from planning to review
- **Cross-Component Testing**: Testing entire application features
- **User Story Validation**: Ensuring user requirements are met

### Performance Tests (`tests/performance/`)
- **Database Performance**: Query optimization and bulk operation testing
- **Memory Usage**: Memory leak detection and resource management
- **UI Responsiveness**: Interface performance under load
- **Scalability Testing**: Performance with large datasets

### Security Tests (`tests/security/`)
- **SQL Injection Prevention**: Parameterized query validation
- **Input Validation**: XSS and injection attack prevention
- **Data Protection**: Sensitive information handling
- **Access Control**: Authorization and data isolation

### Accessibility Tests (`tests/accessibility/`)
- **WCAG 2.1 Compliance**: Web accessibility guideline adherence
- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Reader Support**: Assistive technology compatibility
- **Color and Contrast**: Visual accessibility requirements

## 🔧 Running Tests

### Using the Test Runner

The `test_runner.py` script provides a unified interface for all testing operations:

```bash
# Basic usage
python tests/test_runner.py --help

# Run specific test types
python tests/test_runner.py --unit                    # Unit tests only
python tests/test_runner.py --integration             # Integration tests only
python tests/test_runner.py --e2e                     # End-to-end tests only
python tests/test_runner.py --performance             # Performance tests only
python tests/test_runner.py --security                # Security tests only
python tests/test_runner.py --accessibility           # Accessibility tests only

# Run with options
python tests/test_runner.py --all --verbose           # All tests with verbose output
python tests/test_runner.py --fast                    # Fast tests only (no slow/performance)
python tests/test_runner.py --smoke                   # Smoke tests (basic functionality)

# Coverage and reporting
python tests/test_runner.py --coverage                # Tests with coverage
python tests/test_runner.py --report                  # Generate comprehensive report
python tests/test_runner.py --quality                 # Run quality checks

# GUI testing options
python tests/test_runner.py --gui                     # GUI tests only
python tests/test_runner.py --no-gui                  # Non-GUI tests only
```

### Using Make

```bash
# Install dependencies
make install

# Run tests
make test                          # All tests with coverage
make test-unit                     # Unit tests only
make test-integration              # Integration tests only
make test-e2e                      # End-to-end tests only
make test-performance              # Performance tests only
make test-security                 # Security tests only
make test-accessibility            # Accessibility tests only

# Quality assurance
make lint                          # Code linting
make type-check                    # Type checking
make security-scan                 # Security scanning
make quality                       # All quality checks

# Coverage and reporting
make coverage                      # Generate coverage report
make test-report                   # Generate test report

# Cleanup
make clean                         # Clean test artifacts
```

### Using Pytest Directly

```bash
# Basic pytest usage
pytest                             # Run all tests
pytest -v                          # Verbose output
pytest --cov                       # With coverage

# Run specific test files
pytest tests/unit/test_database.py
pytest tests/integration/test_app_integration.py

# Use markers
pytest -m unit                     # Unit tests only
pytest -m "not gui"                # Exclude GUI tests
pytest -m performance             # Performance tests only

# Other useful options
pytest --maxfail=5                 # Stop after 5 failures
pytest --durations=10              # Show 10 slowest tests
pytest -x                          # Stop on first failure
pytest --lf                        # Run last failed tests only
```

## 📊 Test Configuration

### Pytest Configuration (`pytest.ini`)

Key configuration options:
- **Coverage**: >80% code coverage requirement
- **Markers**: Organized test categorization
- **Timeouts**: 5-minute test timeout limit
- **Warnings**: Filtered deprecation warnings

### Coverage Configuration

Coverage settings in `pyproject.toml`:
- **Source**: All application code
- **Omit**: Test files, virtual environments, cache directories
- **Reports**: HTML, XML, and terminal formats
- **Threshold**: 80% minimum coverage

### Quality Tools

- **Ruff**: Fast Python linter and formatter
- **MyPy**: Static type checking
- **Bandit**: Security vulnerability scanning
- **Safety**: Known vulnerability checking

## 🔍 Test Fixtures and Utilities

### Database Fixtures
- `temp_db`: Temporary test database
- `in_memory_db`: In-memory database for fast tests
- `sample_teacher`: Pre-configured teacher for testing
- `sample_session`: Pre-configured session for testing
- `database_with_sample_data`: Pre-populated test database

### UI Testing Fixtures
- `qt_app`: QApplication instance for UI tests
- `mock_logger`: Mocked logger for testing without output

### Utility Fixtures
- `performance_timer`: Timer for performance measurements
- `test_data_factory`: Factory for generating test data

## 📈 Performance Testing

Performance tests measure:

### Database Performance
- Connection establishment time
- Bulk operation performance
- Query performance with large datasets
- Concurrent operation handling

### Memory Management
- Memory usage during operations
- Memory leak detection
- Garbage collection effectiveness

### UI Performance
- Application startup time
- Large data display performance
- UI responsiveness under load

### Scalability
- Performance with increasing data sizes
- Concurrent user simulation
- Resource usage scaling

## 🔒 Security Testing

Security tests validate:

### Input Validation
- SQL injection prevention
- XSS attack prevention
- Path traversal protection
- Null byte injection handling

### Data Protection
- Sensitive data logging prevention
- Access control validation
- Data isolation verification

### Cryptographic Security
- Secure random number generation
- Password hashing (if implemented)
- Secure temporary file creation

## ♿ Accessibility Testing

Accessibility tests ensure:

### Keyboard Accessibility
- Complete keyboard navigation
- Logical tab order
- Keyboard activation of controls
- Focus indicator visibility

### Screen Reader Support
- Accessible names and descriptions
- Appropriate widget roles
- Semantic markup

### Visual Accessibility
- Color contrast requirements
- Text scalability
- Focus indicators
- Error message accessibility

## 📋 Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.security` - Security tests
- `@pytest.mark.accessibility` - Accessibility tests
- `@pytest.mark.gui` - GUI tests requiring display
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.database` - Database-dependent tests

## 🚀 Continuous Integration

### CI Configuration

For GitHub Actions, Azure Pipelines, or similar:

```yaml
# Example CI test step
- name: Run Tests
  run: |
    python tests/test_runner.py --all --xml
    python tests/test_runner.py --quality

- name: Upload Coverage
  run: |
    codecov --file tests/coverage.xml
```

### Quality Gates

The test suite enforces:
- **Code Coverage**: Minimum 80% coverage
- **Security**: No high-severity vulnerabilities
- **Performance**: Response time thresholds
- **Accessibility**: WCAG 2.1 AA compliance

## 🛠️ Development Workflow

### Before Committing
```bash
# Run quality checks
make quality

# Run fast tests
python tests/test_runner.py --fast

# Run full test suite (optional)
python tests/test_runner.py --all
```

### Adding New Tests

1. **Choose appropriate test type** (unit, integration, e2e)
2. **Use existing fixtures** where possible
3. **Follow naming conventions** (`test_*` functions)
4. **Add appropriate markers** (`@pytest.mark.*`)
5. **Include docstrings** describing test purpose
6. **Test edge cases and error conditions**

### Test Data Management

- Use factories for generating test data
- Prefer in-memory databases for unit tests
- Clean up temporary files and databases
- Use realistic but non-sensitive test data

## 📝 Troubleshooting

### Common Issues

**GUI Tests Failing on Headless Systems**
```bash
# Use Xvfb for headless GUI testing
pytest -m gui --xvfb-run
```

**Database Lock Errors**
- Ensure proper database cleanup in fixtures
- Use in-memory databases for faster tests
- Check for unclosed database connections

**Performance Test Variations**
- Run performance tests on consistent hardware
- Account for system load variations
- Use relative performance comparisons

**Import Errors**
- Ensure PYTHONPATH includes project root
- Install package in development mode: `pip install -e .`

### Debugging Tests

```bash
# Run with debugging
pytest --pdb                       # Drop into debugger on failure
pytest -s                          # Show print statements
pytest -vvv                        # Maximum verbosity
pytest --tb=long                   # Detailed tracebacks
```

## 📚 Resources

### Documentation
- [Pytest Documentation](https://docs.pytest.org/)
- [PyQt6 Testing](https://doc.qt.io/qtforpython/tutorials/testing/testing.html)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

### Tools
- [Ruff](https://github.com/astral-sh/ruff) - Fast Python linter
- [MyPy](https://mypy.readthedocs.io/) - Static type checker
- [Bandit](https://bandit.readthedocs.io/) - Security scanner
- [pytest-cov](https://pytest-cov.readthedocs.io/) - Coverage plugin

## 🤝 Contributing

When adding tests:

1. **Follow the existing test structure**
2. **Use descriptive test names**
3. **Include both positive and negative test cases**
4. **Test edge cases and error conditions**
5. **Keep tests independent and isolated**
6. **Use appropriate assertions**
7. **Document complex test logic**

## 📊 Test Coverage Goals

| Component | Target Coverage | Current Status |
|-----------|----------------|----------------|
| Models    | 90%            | 🎯 Target      |
| Views     | 75%            | 🎯 Target      |
| Utils     | 85%            | 🎯 Target      |
| Controllers| 85%           | 🎯 Target      |
| Overall   | 80%            | 🎯 Target      |

---

For questions or issues with the testing suite, please create an issue in the project repository.