---
name: CI: Ensure pre-commit and dev deps installed in Actions
about: Fix CI to install developer dependencies so pre-commit runs in Actions
labels: [alpha, ci]
assignees: []
---

Steps:
- Add `requirements-dev.txt` listing dev-only packages (pre-commit, ruff, pytest, pytest-cov)
- Update `.github/workflows/ci.yml` to pip install -r requirements-dev.txt before running pre-commit
- Run CI and confirm pre-commit hooks run successfully in the Actions runner

Acceptance criteria:
- CI Actions job runs pre-commit without "command not found" errors
- Linting and formatting checks produce consistent behavior locally and in CI

Notes:
- This is mostly implemented but re-run CI after secret changes and issue creations.
