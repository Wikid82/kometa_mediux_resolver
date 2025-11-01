# Renovate Bot Setup

This repository is configured with Renovate bot to automatically manage dependency updates.

## Configuration

- **Main Config**: `renovate.json` - Primary Renovate configuration with auto-merge enabled
- **Workflow**: `.github/workflows/renovate.yml` - GitHub Actions workflow to run Renovate
- **CI/CD**: `.github/workflows/ci.yml` - Continuous integration for testing PRs
- **Code Owners**: `.github/CODEOWNERS` - Defines code owners for review assignments

## Features

### Automated Dependency Updates

- **Python packages**: Automatically updates dependencies in `requirements.txt` files
- **Minor/Patch updates**: Auto-merged after passing CI checks
- **Major updates**: Require manual approval via dependency dashboard
- **Selenium updates**: Require manual approval (potential breaking changes)
- **Semantic commits**: Uses conventional commit format

### Auto-Merge Configuration

- **Platform auto-merge**: Uses GitHub's native auto-merge feature
- **Status checks**: Waits for CI to pass before merging
- **Strategy**: Uses merge commits to maintain history

### Scheduling

- Runs every Monday at 5:30 AM UTC
- Limits to 2 PRs per hour, 3 concurrent PRs max
- Can be triggered manually via GitHub Actions

## Setup Instructions

### Option 1: Renovate GitHub App (Recommended)

#### 1. Install Renovate App

1. Go to [GitHub Marketplace - Renovate](https://github.com/marketplace/renovate)
2. Click "Set up a plan" and choose "Free"
3. Select "Only select repositories" and choose your repository
4. Install the app

#### 2. Configure Branch Protection (Required for Auto-merge)

1. Go to repository **Settings** → **Branches**
2. Click **Add rule** for your main branch
3. Configure these settings:

   ```
   Branch name pattern: main
   ☑️ Require a pull request before merging
   ☑️ Require status checks to pass before merging
   ☑️ Require branches to be up to date before merging
   ☑️ Allow auto-merge
   ☑️ Allow force pushes
   ☑️ Allow deletions
   ```

4. Under "Status checks", add: `test` (from the CI workflow)

#### 3. That's it

The Renovate app will automatically use the `renovate.json` configuration.

### Option 2: Self-Hosted via GitHub Actions

#### 1. Create Personal Access Token

1. Go to GitHub **Settings** → **Developer settings** → **Personal access tokens**
2. Click **Generate new token (classic)**
3. Select scopes: `repo` and `workflow`
4. Copy the token

#### 2. Add Repository Secret

1. Go to repository **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `RENOVATE_TOKEN`, Value: your token

#### 3. Configure Branch Protection

Follow the same branch protection steps as Option 1.

## How Auto-Merge Works

### For Minor/Patch Updates

1. Renovate creates a PR
2. CI workflow runs automatically
3. If CI passes, PR is auto-merged
4. If CI fails, PR stays open for manual review

### For Major Updates

1. Renovate creates a "Request" in the Dependency Dashboard
2. You manually approve the update
3. Renovate creates a PR
4. Manual review and merge required

### For Selenium Updates

1. Always require manual approval
2. No auto-merge (due to WebDriver compatibility concerns)

## Configuration Details

### Package Rules

```json
{
  "matchUpdateTypes": ["minor", "patch"],
  "automerge": true,
  "automergeType": "pr"
}
```

### Auto-merge Settings

- **platformAutomerge**: Uses GitHub's native auto-merge
- **automergeStrategy**: "merge-commit" (preserves history)
- **Status checks**: Must pass before merge

## Monitoring

### Dependency Dashboard

- Check the **Issues** tab for "Dependency Dashboard"
- Shows all pending updates
- Allows manual triggering of updates

### Pull Requests

- Auto-merged PRs will show "Merged" status
- Failed auto-merges will remain open

### Actions Tab

- Monitor CI workflow runs
- Check Renovate workflow logs (self-hosted only)

## Troubleshooting

### Auto-merge Not Working

1. **Check branch protection**: Ensure "Allow auto-merge" is enabled
2. **Verify CI status**: Make sure the `test` job is passing
3. **Check Renovate config**: Verify `platformAutomerge: true` is set
4. **Token permissions**: Ensure the token has `repo` scope (self-hosted)

### CI Failures

1. **Python syntax errors**: Check the flake8 output
2. **Import errors**: Verify all dependencies are in requirements.txt
3. **Script failures**: Check the test logs in Actions tab

### Manual Override

If you need to merge a PR manually:

1. Go to the PR
2. Click "Enable auto-merge" if not already enabled
3. Or use the normal "Merge pull request" button

## Security Considerations

- **Token scope**: Use minimal required permissions
- **Branch protection**: Prevents direct pushes to main
- **Status checks**: Ensure code quality before merge
- **Manual approval**: For potentially breaking changes

## References

- [Renovate Documentation](https://docs.renovatebot.com/)
- [GitHub Auto-merge](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/automatically-merging-a-pull-request)
- [Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)
