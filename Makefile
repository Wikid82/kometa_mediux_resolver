.PHONY: install test test-cov lint format clean setup help

# Default target
help:
	@echo "Available commands:"
	@echo "  setup      - Set up development environment"
	@echo "  install    - Install all dependencies"
	@echo "  test       - Run all tests"
	@echo "  test-cov   - Run tests with coverage"
	@echo "  test-fast  - Run tests without selenium"
	@echo "  lint       - Run all linters"
	@echo "  format     - Format code with black and isort"
	@echo "  pre-commit - Run pre-commit hooks"
	@echo "  clean      - Clean up temporary files"
	@echo "  build      - Build distribution packages"

# Set up development environment
setup:
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	pre-commit install
	@echo "Development environment setup complete!"

# Install dependencies
install:
	pip install -r requirements.txt

# Run all tests
test:
	pytest -v

# Run tests with coverage
test-cov:
	pytest -v --cov=. --cov-report=html --cov-report=term-missing --cov-report=xml

# Run tests without selenium (faster)
test-fast:
	pytest tests/test_kometa_mediux_resolver.py tests/test_cli.py tests/test_utilities.py -v

# Run integration tests only
test-integration:
	pytest tests/ -m "integration" -v

# Run selenium tests only
test-selenium:
	pytest tests/ -m "selenium" -v

# Run all linters
lint:
	flake8 .
	black --check .
	isort --check-only .
	mypy . || true
	bandit -r . || true

# Format code
format:
	black .
	isort .
	autoflake --in-place --remove-all-unused-imports --remove-unused-variables --recursive .

# Run pre-commit hooks
pre-commit:
	pre-commit run --all-files

# Clean up temporary files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

# Security check
security:
	bandit -r . -f json -o bandit-report.json
	@echo "Security report saved to bandit-report.json"

# Check dependencies for security vulnerabilities
deps-check:
	pip check
	python -c "import pkg_resources; print('All dependencies are compatible')"

# Run a quick development test
dev-test:
	python kometa_mediux_resolver.py --help
	./kometa-resolver --help
	python -c "import kometa_mediux_resolver; print('Import successful')"

# Generate requirements.txt from current environment
freeze:
	pip freeze > requirements-frozen.txt

# Update pre-commit hooks
update-hooks:
	pre-commit autoupdate

# Dry run on test library
dry-run:
	python kometa_mediux_resolver.py --root ./resolver_test_library --output /tmp/test_output.json -v

# Profile the code
profile:
	python -m cProfile -o profile_output.prof kometa_mediux_resolver.py --help
	@echo "Profile saved to profile_output.prof"

# Install and run in virtual environment
venv-setup:
	python -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	@echo "Virtual environment created in .venv"
	@echo "Activate with: source .venv/bin/activate"

# Run tests in virtual environment
venv-test:
	.venv/bin/pytest -v

# Check code complexity
complexity:
	flake8 --max-complexity=10 --statistics .

# Generate documentation coverage report
doc-coverage:
	python -c "
	import ast
	from pathlib import Path

	total_funcs = 0
	documented_funcs = 0

	for py_file in Path('.').glob('*.py'):
	    if py_file.name.startswith('test_'):
	        continue
	    try:
	        with open(py_file, 'r') as f:
	            tree = ast.parse(f.read())

	        for node in ast.walk(tree):
	            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
	                total_funcs += 1
	                if ast.get_docstring(node):
	                    documented_funcs += 1
	    except:
	        pass

	if total_funcs > 0:
	    coverage = (documented_funcs / total_funcs) * 100
	    print(f'Documentation coverage: {coverage:.1f}% ({documented_funcs}/{total_funcs})')
	else:
	    print('No functions found to check')
	"

# All quality checks
check-all: lint test-cov security doc-coverage
	@echo "All quality checks completed!"
