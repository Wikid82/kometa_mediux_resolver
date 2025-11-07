# Alpha Release Roadmap - Quick Reference

## 🎯 Goal: v0.1.0-alpha Release

**Definition**: Tool works reliably for basic use cases with 50%+ test coverage.

---

## 📋 Priority Checklist

### 🔴 CRITICAL - Must Complete (Blocking)

- [ ] **P0: Install Test Dependencies** (1 hour)
  - Command: `pip install pytest-cov coverage`
  - Add to `requirements-dev.txt`
  - Verify: `python3 -m pytest --version`

- [ ] **P1: Fix Failing Tests** (2-4 days)
  - Run: `python3 -m pytest -v > test_results.txt 2>&1`
  - Fix Selenium mocking issues
  - Fix function signature mismatches
  - Target: >90% pass rate

- [ ] **P2: Achieve 50% Coverage** (2-3 days)
  - Focus on `kometa_mediux_resolver.py`
  - Cover core functions and error paths
  - Command: `python3 -m pytest --cov=. --cov-report=html`

- [ ] **P3: End-to-End Validation** (1-2 days)
  - Test with `resolver_test_library/`
  - Verify no crashes
  - Validate output correctness

### 🟡 RECOMMENDED - Should Complete

- [ ] **P4: Basic Error Handling** (1-2 days)
  - Network failures
  - File system errors
  - API errors
  - Configuration validation

- [ ] **P5: CI/CD Green** (1 day)
  - Fix pre-commit hooks
  - Pass all GitHub Actions
  - Review security scans

### 🟢 OPTIONAL - Nice to Have

- [ ] **P6: Documentation** (1 day)
  - Quick start guide
  - Configuration docs
  - Troubleshooting guide

- [ ] **P7: Release** (1 day)
  - Tag v0.1.0-alpha
  - Write release notes
  - Create GitHub release

---

## ⏱️ Estimated Timeline

| Phase | Duration | Total |
|-------|----------|-------|
| Critical (P0-P3) | 6-10 days | Required |
| Recommended (P4-P5) | 2-3 days | Strongly suggested |
| Optional (P6-P7) | 2 days | Nice to have |
| **Alpha Release** | **10-15 days** | **Total** |

---

## 🚀 Quick Start Commands

### Setup
```bash
# Install dependencies
pip install pytest-cov coverage
pip install -r requirements-dev.txt

# Run pre-commit setup
pre-commit install
```

### Testing
```bash
# Run all tests
python3 -m pytest -v

# Run with coverage
python3 -m pytest --cov=. --cov-report=html --cov-report=term-missing

# View coverage
open htmlcov/index.html  # or xdg-open on Linux

# Run specific test file
python3 -m pytest tests/test_kometa_mediux_resolver.py -v

# Stop at first failure
python3 -m pytest -x
```

### Validation
```bash
# Test end-to-end
python3 kometa_mediux_resolver.py --root ./resolver_test_library --output /tmp/test.json -v

# Check formatting
black --check .
isort --check .
flake8 .

# Run pre-commit
pre-commit run --all-files
```

---

## 📊 Success Metrics

### Alpha Release Criteria

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Test Coverage | 7.6% | 50%+ | 🔴 |
| Tests Passing | Unknown | >90% | 🔴 |
| CI/CD Status | Unknown | Green | 🔴 |
| End-to-End | Not tested | Working | 🔴 |
| Documentation | Basic | Adequate | 🔴 |

---

## 💡 Tips for Success

1. **Work in Priority Order**: Don't skip to easier tasks. P0 → P1 → P2 → P3.

2. **Commit Often**: Each fix should be a commit. Makes rollback easier.

3. **Test as You Go**: Run tests after each fix to avoid regression.

4. **Document Issues**: If you find bugs, create issues for them.

5. **Ask for Help**: If stuck >2 hours, ask for help or skip temporarily.

6. **Celebrate Wins**: Mark issues complete and track progress!

---

## 🔗 Resources

- **Issues Directory**: `.github/ISSUES/alpha/`
- **Test Files**: `tests/`
- **Main Script**: `kometa_mediux_resolver.py`
- **Test Data**: `resolver_test_library/`
- **CI Config**: `.github/workflows/ci.yml`

---

## 📞 Getting Help

- **Create Issue**: Use GitHub issues for bugs
- **Review Docs**: Check TESTING.md and README.md
- **Check CI**: Look at GitHub Actions output
- **Coverage Report**: Open htmlcov/index.html

---

## ✅ When Ready to Release

Run this checklist before tagging:

```bash
# 1. All tests pass
python3 -m pytest -v
# Result: All passing ✅

# 2. Coverage meets target
python3 -m pytest --cov=. --cov-report=term
# Result: >50% coverage ✅

# 3. End-to-end works
python3 kometa_mediux_resolver.py --root ./resolver_test_library --output /tmp/test.json
# Result: Success, valid output ✅

# 4. CI is green
# Check: https://github.com/Wikid82/kometa_mediux_resolver/actions
# Result: All jobs passing ✅

# 5. Pre-commit passes
pre-commit run --all-files
# Result: All hooks passing ✅

# 6. Documentation is updated
# Check: README.md has current info ✅
```

If all ✅, then:

```bash
git tag v0.1.0-alpha
git push origin v0.1.0-alpha
# Create release on GitHub with notes
```

---

**Start Here**: Run `.github/scripts/create_alpha_issues.sh` to create all issues on GitHub!
