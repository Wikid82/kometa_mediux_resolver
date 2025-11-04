---
name: Open Alpha issues and assign priorities
about: Create and add prioritized Alpha issues to the project board
labels: [alpha, maintenance]
assignees: []
---

Overview:

- Use the prepared `BETA_ISSUES_TO_CREATE.md` as the canonical list of issues to open for Alpha
- Open issues in priority order so that they are automatically added to the project board once automation is enabled

Steps:

- Confirm `GITHUB_TOKEN` secret is set
- Use `gh` CLI script (helper in repo `.github/scripts/open_alpha_issues.sh`) to open issues in order
- Verify issues land in the project board and the top-priority issue is moved to "In Progress"

Acceptance criteria:

- All Alpha issues are open on GitHub
- Top-priority issues are visible and assigned to owners or teams where possible

Notes:
- If `gh` CLI is unavailable, issues can be opened manually via the GitHub UI
