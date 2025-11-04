---
name: Review and merge PRs for Alpha
about: Review open PRs, ensure tests pass, and merge to main in an ordered fashion
labels: [alpha, review]
assignees: []
---

Steps:
- List open PRs in priority order that address tests, CI, and coverage
- Run CI locally or via Actions to reproduce failures
- Leave review comments and request changes or approve
- Merge PRs once passing and ensure project board reflects the change

Acceptance criteria:
- Critical PRs merged and pipeline green
- Project board updated for each merged PR
