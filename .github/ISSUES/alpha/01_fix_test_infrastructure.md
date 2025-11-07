---
name: "[ALPHA-P1] Fix Test Infrastructure and Failing Tests"
about: Resolve ~70 failing tests blocking coverage measurement
title: "[ALPHA-P1] Fix Test Infrastructure and Failing Tests"
labels: ["alpha", "priority-critical", "tests", "bug"]
assignees: []
---

## 🎯 Objective
Fix failing tests that are blocking accurate coverage measurement and CI/CD validation.

## 📊 Current Status
- **Test Results**: ~70 failing tests (need to run to get exact count)
- **Target**: 90%+ pass rate for alpha
- **Root Causes**: API signature mismatches, mock setup issues, import problems

## 🔍 Major Failure Categories

### 1. Selenium/Scraper Tests (~30 failures estimated)
- WebDriver mock setup issues
- Selenium import/availability problems
- Method signature mismatches in scraper tests
- Fix: Update tests to patch `mediux_scraper._import_selenium`

### 2. Function Signature Mismatches (~25 failures estimated)
- `touch_activity` parameter expectations
- `probe_url` return format assumptions
- Database table name inconsistencies
- Fix: Update test expectations to match actual implementation

### 3. Import/Module Issues (~16 failures estimated)
- mediux_scraper optional import handling
- sys.path configuration in test environment
- Mock target path corrections
- Fix: Correct import paths and mock targets

## 📝 Tasks

### Phase 1: Identify Failures
- [ ] Run full test suite: `python3 -m pytest -v`
- [ ] Collect failure output to file: `python3 -m pytest -v > test_results.txt 2>&1`
- [ ] Categorize failures by type
- [ ] Identify top 5 most common failure patterns

### Phase 2: Fix Core Module Tests
- [ ] Fix `test_kometa_mediux_resolver.py` failures
- [ ] Fix import and patching issues
- [ ] Update function signatures to match actual code
- [ ] Verify core functionality tests pass

### Phase 3: Fix Scraper Tests
- [ ] Fix `test_mediux_scraper.py::TestScraperErrorHandling` methods
- [ ] Update WebDriver mocking approach
- [ ] Handle optional Selenium imports correctly
- [ ] Mark integration tests with `@pytest.mark.selenium`

### Phase 4: Fix Utility Tests
- [ ] Fix `test_utilities.py::TestFetchSetAssetsWithScrape`
- [ ] Fix `test_missing_coverage.py` edge cases
- [ ] Update CLI argument parsing tests
- [ ] Fix configuration loading tests

## ✅ Definition of Done
- [ ] Test pass rate > 90% (< 10 failures)
- [ ] All core functionality tests pass
- [ ] Coverage can be measured accurately
- [ ] CI/CD pipeline tests run without errors

## 🔗 Related Files
- `tests/conftest.py`
- `tests/test_kometa_mediux_resolver.py`
- `tests/test_mediux_scraper.py`
- `tests/test_utilities.py`
- `tests/test_missing_coverage.py`

## ⚠️ Priority
**CRITICAL - P1**: Blocks coverage measurement and quality validation. Must complete after P0.

## 📝 Notes
- Focus on making tests pass, not achieving coverage yet
- Run `pytest -x` to stop at first failure for faster iteration
- Use `pytest -k test_name` to run specific test categories
- Consider temporarily skipping some Selenium tests with `@pytest.mark.skip`
