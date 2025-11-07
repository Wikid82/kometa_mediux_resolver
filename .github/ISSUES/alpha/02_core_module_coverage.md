---
name: "[ALPHA-P2] Achieve 50% Core Module Coverage"
about: Get kometa_mediux_resolver.py from 0% to 50%+ coverage for alpha
title: "[ALPHA-P2] Achieve 50% Core Module Coverage"
labels: ["alpha", "priority-high", "coverage", "tests"]
assignees: []
---

## 🎯 Objective
Increase coverage of `kometa_mediux_resolver.py` from 0% to 50%+ for alpha release.

## 📊 Current Status
- **kometa_mediux_resolver.py**: 0% coverage (0 statements covered)
- **Overall coverage**: 7.6%
- **Alpha target**: 50%+ overall, focusing on core module
- **Beta target**: 93%

## 🔍 Priority Areas to Cover

### 1. Core Functionality (Must Have - 30%)
- [ ] URL parsing and set ID extraction
- [ ] `fetch_set_assets()` basic flow
- [ ] Configuration loading
- [ ] Main CLI entry point
- [ ] File scanning and YAML parsing

### 2. Error Handling (Should Have - 15%)
- [ ] Network error handling
- [ ] Invalid YAML handling
- [ ] Missing configuration handling
- [ ] File I/O errors
- [ ] API error responses (4xx, 5xx)

### 3. Integration Points (Nice to Have - 5%)
- [ ] Cache operations (basic reads/writes)
- [ ] Activity tracking
- [ ] Output file generation
- [ ] Backup creation

## 📝 Tasks

### Phase 1: Measure Current State
- [ ] Generate coverage report: `python3 -m pytest --cov=. --cov-report=html`
- [ ] Open htmlcov/kometa_mediux_resolver_py.html
- [ ] Identify completely uncovered functions
- [ ] List critical paths with 0% coverage

### Phase 2: Add Core Tests
- [ ] Test URL parsing functions
- [ ] Test asset fetching (mocked API responses)
- [ ] Test YAML file loading and parsing
- [ ] Test CLI argument handling
- [ ] Test main workflow coordination

### Phase 3: Add Error Handling Tests
- [ ] Test network timeout handling
- [ ] Test malformed YAML handling
- [ ] Test missing file handling
- [ ] Test invalid configuration handling
- [ ] Test API error responses

### Phase 4: Validate Coverage
- [ ] Run coverage: `python3 -m pytest --cov=kometa_mediux_resolver --cov-report=term-missing`
- [ ] Verify 50%+ coverage achieved
- [ ] Identify any critical gaps remaining
- [ ] Document known uncovered areas

## ✅ Definition of Done
- [ ] kometa_mediux_resolver.py has 50%+ line coverage
- [ ] All core functions have at least basic test coverage
- [ ] Critical error paths are tested
- [ ] Coverage report shows progress
- [ ] Documentation updated with testing approach

## 🔗 Related Files
- `kometa_mediux_resolver.py` (main module)
- `tests/test_kometa_mediux_resolver.py`
- `tests/conftest.py` (fixtures)
- `coverage.xml` and `htmlcov/`

## ⚠️ Priority
**HIGH - P2**: Required for alpha quality, but tests must be passing first (depends on P0, P1).

## 📝 Notes
- Focus on breadth over depth for alpha
- Cover main happy paths first
- Don't worry about edge cases yet (beta goal)
- Use mocks liberally to avoid external dependencies
- Selenium scraper coverage is beta goal, not alpha
