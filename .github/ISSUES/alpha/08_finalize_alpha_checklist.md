---
name: Finalize alpha checklist and release
about: Prepare the repository for the Alpha release and run final checks
labels: [alpha, release]
assignees: []
---

Checklist:
- All tests pass and coverage >= 93%
- CI is green and pre-commit hooks run in Actions
- Project board contains all Alpha issues and top priority items are assigned
- README and developer docs updated
- Tag release v0.1.0-alpha and create release notes summarizing changes

Post-release:
- Add tasks for Beta and plan integration testing
