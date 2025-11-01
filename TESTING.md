# Testing Guide

This document explains the comprehensive testing setup for the Kometa MediUX Resolver project.

## Test Structure

```
tests/
├── conftest.py              # Pytest fixtures and test configuration
├── test_kometa_mediux_resolver.py  # Main module tests
├── test_mediux_scraper.py   # Scraper module tests
├── test_cli.py              # CLI and argument parsing tests
└── test_utilities.py        # Utility functions and edge cases
```

## Test Categories

### Unit Tests

- **Module**: `test_kometa_mediux_resolver.py`
- **Coverage**: Core functionality, URL parsing, asset fetching, cache operations
- **Markers**: `@pytest.mark.unit`

### Integration Tests

- **Module**: All test files
- **Coverage**: Full workflow tests, file operations, config loading
- **Markers**: `@pytest.mark.integration`

### Selenium Tests

- **Module**: `test_mediux_scraper.py`
- **Coverage**: Web scraping functionality
- **Markers**: `@pytest.mark.selenium`
- **Note**: Requires selenium dependencies

## Running Tests

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test categories
pytest -m "unit"                    # Unit tests only
pytest -m "integration"             # Integration tests only
pytest -m "not selenium"            # Skip selenium tests
```

### Using Makefile

```bash
make test          # Run all tests
make test-cov      # Run with coverage report
make test-fast     # Run without selenium (faster)
make test-selenium # Run only selenium tests
```

### Development Workflow

```bash
# Setup development environment
make setup

# Run pre-commit checks
make pre-commit

# Quick development test
make dev-test

# Run all quality checks
make check-all
```

## Test Configuration

### pytest.ini (in pyproject.toml)

- **Coverage target**: 85%
- **Coverage reports**: HTML, XML, terminal
- **Test markers**: unit, integration, selenium, slow
- **Automatic coverage collection**

### Coverage Configuration

- **Source**: All Python files except tests
- **Branch coverage**: Enabled
- **Exclusions**: Test files, virtual environments, caches
- **Reports**: HTML (htmlcov/), XML (coverage.xml), terminal

## Test Fixtures

### Common Fixtures (conftest.py)

- `temp_dir`: Temporary directory for file operations
- `sample_yaml_content`: Sample YAML structure
- `sample_yaml_file`: YAML file with test content
- `yaml_with_mediux_urls`: YAML with MediUX URLs
- `config_file`: Sample configuration file
- `mock_response`: HTTP response mock
- `mock_assets_response`: MediUX API response mock
- `central_mapping_file`: Central mapping configuration
- `metadata_schema`: JSON schema for validation

### Usage Example

```python
def test_my_function(temp_dir, sample_yaml_file):
    # temp_dir and sample_yaml_file are automatically provided
    result = my_function(sample_yaml_file)
    assert result is not None
```

## Code Quality Tools

### Formatting

- **Black**: Code formatting (line length: 100)
- **isort**: Import sorting
- **autoflake**: Remove unused imports/variables

### Linting

- **flake8**: Style and error checking
- **mypy**: Type checking
- **bandit**: Security scanning

### Pre-commit Hooks

Automatically run on every commit:

- Code formatting (black, isort)
- Linting (flake8)
- Type checking (mypy)
- Security scanning (bandit)
- YAML/JSON validation
- Documentation checks

## Continuous Integration

### GitHub Actions Workflows

#### Main CI (`ci.yml`)

- **Matrix testing**: Python 3.8, 3.9, 3.10, 3.11
- **Coverage reporting**: Codecov integration
- **Artifact uploads**: Test reports, coverage data

#### Test Jobs

1. **test**: Full test suite with coverage
2. **lint**: Code quality checks
3. **test-without-selenium**: Core tests without selenium
4. **integration-test**: Integration tests and workflow validation
5. **security**: Vulnerability scanning
6. **docs**: Documentation validation

### Coverage Reporting

- **Codecov**: Automatic coverage reporting
- **Target**: 85% overall coverage
- **PR checks**: Coverage diff analysis

## Test Data and Mocking

### Mock Strategies

- **HTTP requests**: Using `responses` library and `unittest.mock`
- **File operations**: Temporary directories and files
- **External APIs**: Mock responses with realistic data
- **Selenium**: Mock WebDriver interactions

### Test Data

- **YAML files**: Various structures and edge cases
- **API responses**: Realistic MediUX API data
- **Configuration files**: Different config scenarios
- **Error conditions**: Invalid files, network errors

## Performance Testing

### Profiling

```bash
# Profile the application
make profile

# Check code complexity
make complexity
```

### Load Testing

- Large file handling tests
- Memory usage validation
- Concurrent operation tests

## Security Testing

### Tools

- **bandit**: Python security linting
- **detect-secrets**: Secret detection
- **Trivy**: Vulnerability scanning

### Security Checks

```bash
# Run security scan
make security

# Check dependencies
make deps-check
```

## Writing New Tests

### Test Structure Template

```python
import pytest
from unittest.mock import patch, Mock

class TestMyFeature:
    """Test description."""

    def test_basic_functionality(self, temp_dir):
        """Test basic case."""
        # Arrange
        input_data = "test"

        # Act
        result = my_function(input_data)

        # Assert
        assert result == expected_result

    @patch('module.external_call')
    def test_with_mocking(self, mock_external):
        """Test with external dependency mocked."""
        mock_external.return_value = "mocked_result"

        result = my_function()

        assert result == "processed_mocked_result"
        mock_external.assert_called_once()

    @pytest.mark.integration
    def test_integration_scenario(self, sample_yaml_file):
        """Test integration case."""
        # Integration test implementation
        pass
```

### Best Practices

1. **AAA Pattern**: Arrange, Act, Assert
2. **Descriptive names**: Clear test purpose
3. **One assertion per test**: Focus on single behavior
4. **Use fixtures**: Reuse test data and setup
5. **Mock external dependencies**: Isolate units under test
6. **Test edge cases**: Error conditions, empty inputs, large data

### Test Markers

```python
@pytest.mark.unit          # Unit test
@pytest.mark.integration   # Integration test
@pytest.mark.selenium      # Requires selenium
@pytest.mark.slow          # Slow-running test
```

## Debugging Tests

### Debugging Tips

```bash
# Run specific test with verbose output
pytest tests/test_file.py::TestClass::test_method -v -s

# Drop into debugger on failure
pytest --pdb

# Run last failed tests only
pytest --lf

# Run tests matching pattern
pytest -k "test_pattern"
```

### Common Issues

1. **Import errors**: Check PYTHONPATH and module structure
2. **Fixture not found**: Verify fixture definition and scope
3. **Mock not working**: Check patch target and import paths
4. **Selenium issues**: Verify WebDriver installation and PATH

## Test Coverage Goals

### Current Coverage Targets

- **Overall**: 85%
- **Critical modules**: 90%+
- **New code**: 80%+

### Coverage Exclusions

- Test files themselves
- Development utilities
- Error handling for rare edge cases (marked with `# pragma: no cover`)

## Maintenance

### Regular Tasks

- Update test dependencies
- Review and update test data
- Add tests for new features
- Maintain test documentation
- Monitor CI performance

### Test Data Refresh

- Update sample YAML files periodically
- Refresh API response mocks
- Review and update configuration examples

This comprehensive testing setup ensures high code quality, reliability, and maintainability of the Kometa MediUX Resolver project.
