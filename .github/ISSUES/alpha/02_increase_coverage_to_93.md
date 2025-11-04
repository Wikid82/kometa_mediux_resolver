---
name: Increase test coverage to 93% (alpha target)
about: Add tests targeting uncovered lines and edge cases to reach 93% coverage
labels: [alpha, coverage]
assignees: []
---

Tasks:

- Generate coverage HTML report: `pytest --cov=kometa_mediux_resolver --cov-report=html` and open `htmlcov/index.html` to see uncovered lines
- Triage the top 10 files with the largest uncovered counts; create focused tests for each
- Add tests for error branches and rare conditions (e.g., network timeouts, malformed YAML, sqlite lock contention)
- Ensure test fixtures create temporary files/dirs and use `tmp_path` to avoid side effects
- Once coverage >=93%, update CI to require coverage threshold

Acceptance criteria:

- Coverage report shows >=93% total coverage
- CI fails the build if coverage drops below this threshold

Notes:
- Prefer lightweight unit tests using mocks over brittle system tests
- Re-run coverage after each batch of tests to track progress
