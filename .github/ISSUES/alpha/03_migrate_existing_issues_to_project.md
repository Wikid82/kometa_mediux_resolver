---
name: Migrate existing issues/PRs to Beta project (one-time)
about: Run the project-migration-v2 workflow to add current issues/PRs to project board
labels: [alpha, infra]
assignees: []
---

Steps:

- Add the repository secret `GITHUB_TOKEN` with the PAT that has `repo` and `project` scopes
- Manually trigger the workflow `project-migration-v2.yml` from Actions with `dry_run=true` to see changes
- Review the run logs and confirm which issues will be added
- Re-run the workflow with `dry_run=false` to actually add items to the project
- Verify items appear in project #3 and columns match expected defaults

Acceptance criteria:

- All existing issues/PRs are present in the project board
- No duplicates; migration handles already-existing items gracefully

Notes:
- Migration is one-time; keep a record of which issues were added in a release note
