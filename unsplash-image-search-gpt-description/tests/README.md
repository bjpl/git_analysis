# Test Suite for Unsplash Image Search GPT Description

This directory contains a comprehensive test suite for the Unsplash Image Search application, designed to ensure code quality, reliability, and performance.

## Test Structure

```
tests/
├── __init__.py                    # Package initialization
├── conftest.py                   # Global test configuration and fixtures
├── pytest.ini                   # Pytest configuration (in root)
├── README.md                     # This file
├── unit/                         # Unit tests
│   ├── test_services/           # API service tests
│   │   ├── test_unsplash_service.py      # Unsplash API tests
│   │   ├── test_openai_service.py        # OpenAI API tests
│   │   └── test_translation_service.py   # Translation service tests
│   ├── test_models/             # Data model tests
│   │   ├── test_session.py      # Session management tests
│   │   ├── test_vocabulary.py   # Vocabulary management tests
│   │   └── test_image.py        # Image handling tests
│   └── test_utils/              # Utility function tests
│       ├── test_cache.py        # Caching mechanism tests
│       └── test_data_export.py  # Data export tests
├── integration/                  # Integration tests
│   ├── test_api_workflow.py     # End-to-end API workflows
│   └── test_data_persistence.py # Data persistence integration
├── fixtures/                    # Test fixtures and sample data
│   └── sample_data.py           # Test data and fixtures
├── test_performance.py          # Performance and benchmark tests
└── test_error_handling.py       # Error handling and edge cases
```

## Test Categories

### Unit Tests (`tests/unit/`)
Fast, isolated tests that test individual components:
- **Service Tests**: API interactions, mocking external services
- **Model Tests**: Data structures and business logic
- **Utility Tests**: Helper functions and caching mechanisms

### Integration Tests (`tests/integration/`)
Tests that verify component interactions:
- **API Workflows**: Complete user workflows involving multiple APIs
- **Data Persistence**: File I/O and data consistency across sessions

### Performance Tests (`tests/test_performance.py`)
Benchmarks and stress tests:
- API response time benchmarks
- Memory usage validation
- Concurrent operation performance
- Large dataset handling

### Error Handling Tests (`tests/test_error_handling.py`)
Edge cases and error scenarios:
- Network failures
- API errors and rate limiting
- File system errors
- Data corruption recovery

## Running Tests

### Using the Test Runner (Recommended)

```bash
# Quick tests (excludes slow tests)
python run_tests.py

# All unit tests
python run_tests.py --suite unit

# Integration tests
python run_tests.py --suite integration

# Performance tests
python run_tests.py --suite performance

# All tests with coverage
python run_tests.py --suite coverage

# Verbose output
python run_tests.py --suite all --verbose

# Parallel execution
python run_tests.py --suite unit --parallel 4
```

### Using pytest directly

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run specific test categories
pytest -m unit                    # Unit tests only
pytest -m integration            # Integration tests only
pytest -m slow                   # Performance tests
pytest -m "not slow"             # Quick tests only

# Run specific test files
pytest tests/unit/test_services/test_unsplash_service.py
pytest tests/integration/test_api_workflow.py

# Run with coverage
pytest --cov=main --cov=config_manager --cov-report=html

# Run in parallel
pytest -n auto

# Verbose output
pytest -v

# Run only failed tests
pytest --lf
```

## Test Markers

Tests are categorized using pytest markers:

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (may require external services)
- `@pytest.mark.slow` - Slow tests (performance, stress tests)
- `@pytest.mark.api` - Tests requiring actual API calls
- `@pytest.mark.gui` - Tests involving GUI components
- `@pytest.mark.performance` - Performance benchmarks
- `@pytest.mark.stress` - Stress and load tests

## Test Configuration

### Pytest Configuration (`pytest.ini`)
- Test discovery patterns
- Coverage settings (>80% required)
- Markers and warnings configuration
- Output formatting

### Global Fixtures (`conftest.py`)
- Mock configurations
- Test data directories
- API response mocks
- Performance thresholds

## Coverage Requirements

The test suite aims for >80% code coverage:
- **Statements**: >80%
- **Branches**: >75%  
- **Functions**: >80%
- **Lines**: >80%

Coverage reports are generated in:
- Terminal (summary)
- HTML (`htmlcov/index.html`)
- XML (for CI/CD)

## Mock Data and Fixtures

### Sample Data (`tests/fixtures/sample_data.py`)
Contains realistic test data:
- Unsplash API responses
- OpenAI API responses  
- CSV vocabulary data
- Error scenarios
- Performance benchmarks

### Test Fixtures
Global fixtures available in all tests:
- `app_instance` - Configured app instance
- `mock_config_manager` - Configuration mock
- `sample_data` - Test data sets
- `temp_data_dir` - Temporary directories
- Error simulation fixtures

## Performance Benchmarks

Tests validate against performance thresholds:
- API calls: <10s timeout
- Image processing: <2s
- UI responsiveness: <0.5s
- File operations: <1s
- Memory usage: <200MB
- Cache operations: <1ms

## Error Scenarios Tested

- Network connectivity failures
- API authentication errors
- Rate limiting and quotas
- Malformed responses
- File system errors
- Memory constraints
- Concurrent access issues
- Data corruption recovery

## Best Practices

1. **Test Organization**: Tests mirror source code structure
2. **Naming**: Descriptive test names explaining what and why
3. **Isolation**: Each test is independent and can run alone
4. **Mocking**: External dependencies are mocked for reliability
5. **Data**: Use realistic test data from fixtures
6. **Performance**: Validate against realistic benchmarks
7. **Error Handling**: Test both success and failure paths

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure >80% coverage for new code
3. Add appropriate test markers
4. Update fixtures for new data structures
5. Test both success and error scenarios
6. Validate performance impact

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure Python path includes project root
2. **Missing Dependencies**: Install with `pip install -r requirements-dev.txt`
3. **Slow Tests**: Use `--markers "not slow"` to skip performance tests
4. **GUI Tests**: May require display server (skip in headless environments)

### Debug Mode

```bash
# Run with debugging
pytest --pdb                     # Drop into debugger on failures
pytest --pdb-trace              # Drop into debugger at start
pytest -s                       # Don't capture output
```

### CI/CD Integration

The test suite is designed for CI/CD pipelines:
- Parallel execution support
- XML coverage reports  
- Exit codes for pass/fail
- Minimal external dependencies
- Configurable timeouts

## Metrics and Reporting

Test results include:
- Pass/fail counts
- Execution time
- Coverage percentages
- Performance benchmarks
- Memory usage stats
- Error categorization

Reports are generated in multiple formats for different audiences:
- Developers: Terminal output with details
- QA: HTML coverage reports
- CI/CD: XML reports for integration
- Management: Summary metrics