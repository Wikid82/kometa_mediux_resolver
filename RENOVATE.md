# Renovate Bot Setup

This repository is configured with Renovate bot to automatically manage dependency updates.

## Configuration

- **Main Config**: `renovate.json` - Primary Renovate configuration with auto-merge enabled
- **Legacy Config**: `.renovaterc` - Legacy configuration file (superseded by `renovate.json`)
- **Workflow**: `.github/workflows/renovate.yml` - GitHub Actions workflow to run Renovate
- **CI/CD**: `.github/workflows/ci.yml` - Continuous integration for testing PRs
- **Code Owners**: `.github/CODEOWNERS` - Defines code owners for review assignments

**Note**: Renovate will use `renovate.json` as the primary configuration. The `.renovaterc` file is kept for backwards compatibility but is superseded by the more comprehensive `renovate.json` configuration.

## Features

### Automated Dependency Updates

- **Python packages**: Automatically updates dependencies in `requirements*.txt` files
- **Minor/Patch updates**: Auto-merged after passing CI checks
- **Major updates**: Require manual approval via dependency dashboard
- **Selenium updates**: Require manual approval (potential breaking changes)
- **Semantic commits**: Uses conventional commit format
- **GitHub Actions**: Auto-updates with pinned digests for security
- **Closed PRs/Issues**: Creates new PRs/issues instead of reopening closed ones (`recreateClosed: false`)

### Auto-Merge Configuration

- **Platform auto-merge**: Uses GitHub's native auto-merge feature
- **Status checks**: Waits for CI to pass before merging
- **Strategy**: Uses merge commits to maintain history

### Scheduling

- Runs every Monday at 5:30 AM UTC
- Limits to 2 PRs per hour, 3 concurrent PRs max
- Can be triggered manually via GitHub Actions

## Python-Specific Presets

This configuration uses several Renovate presets optimized for Python projects:

### Core Presets

- **config:recommended**: Base recommended configuration
- **:dependencyDashboard**: Enables dependency dashboard issue
- **:semanticCommits**: Uses semantic commit messages
- **:preserveSemverRanges**: Maintains semver range operators (>=, ~=, etc.)
- **group:linters**: Groups linter updates together
- **group:test**: Groups test tool updates together
- **helpers:pinGitHubActionDigests**: Pins GitHub Actions to specific SHA digests

### Package Grouping

Updates are intelligently grouped to reduce PR noise:

- **Python linting tools**: black, flake8, isort, mypy, bandit, pylint, ruff
- **Python testing tools**: pytest, coverage, and related packages
- **Core dependencies**: jsonschema, PyYAML, requests, ruamel.yaml (non-major updates)

## Python-Specific Workarounds

This configuration includes several workarounds for common Python packaging issues:

### 1. Selenium and WebDriver Manager

**Issue**: Selenium updates can break due to WebDriver compatibility changes.

**Workaround**: 
- Both `selenium` and `webdriver-manager` require manual approval
- Updates are marked in the dependency dashboard
- Allows time to test WebDriver compatibility before merging

```json
{
  "matchPackageNames": ["selenium", "webdriver-manager"],
  "automerge": false,
  "dependencyDashboardApproval": true
}
```

### 2. Setuptools

**Issue**: Setuptools can introduce breaking changes in minor/patch versions.

**Workaround**:
- Requires manual approval for all updates
- Prevents automatic updates that could break the build

```json
{
  "matchPackageNames": ["setuptools"],
  "automerge": false,
  "dependencyDashboardApproval": true
}
```

### 3. Pip Updates

**Issue**: Pip updates can cause resolver issues and break installations.

**Workaround**:
- Pip updates are disabled in Renovate
- Pip should be updated manually when needed
- System pip is typically managed by the environment

```json
{
  "matchPackageNames": ["pip"],
  "enabled": false
}
```

### 4. Requirements File Detection

**Issue**: Renovate may not detect all requirements files with custom names.

**Workaround**:
- Custom file pattern configured to match all `requirements*.txt` files
- Includes: `requirements.txt`, `requirements-dev.txt`, `requirements-core.txt`

```json
{
  "pip_requirements": {
    "fileMatch": ["(^|/)requirements.*\\.txt$"]
  }
}
```

### 5. Semver Range Preservation

**Issue**: Renovate might change `>=` to `==` or remove version constraints.

**Workaround**:
- Uses `:preserveSemverRanges` preset
- Maintains the original range operators in requirements files
- Example: `requests>=2.28` stays as `>=` instead of changing to `==`

### 6. Lock File Maintenance

**Issue**: Python projects without lock files can have inconsistent builds.

**Workaround**:
- Lock file maintenance is disabled (not using Poetry/Pipenv)
- This project uses pip with requirements files only
- Dependencies are constrained via version ranges

```json
{
  "lockFileMaintenance": {
    "enabled": false
  }
}
```

### 7. Vulnerability Alerts

**Issue**: Security vulnerabilities need immediate attention but careful review.

**Workaround**:
- Vulnerability alerts are labeled with "security"
- Auto-merge is disabled for security updates
- Allows manual review of security patches before applying

```json
{
  "vulnerabilityAlerts": {
    "labels": ["security"],
    "automerge": false
  }
}
```

### 8. GitHub Actions Digest Pinning

**Issue**: GitHub Actions can be compromised if not pinned to specific commits.

**Workaround**:
- Uses `helpers:pinGitHubActionDigests` preset
- Automatically pins actions to SHA digests
- Improves security by preventing tag hijacking

### 9. Closed PR/Issue Recreation

**Issue**: By default, Renovate may reopen previously closed PRs or issues, which can clutter the repository with reopened items.

**Workaround**:
- Sets `recreateClosed: false` in the configuration
- When a PR or issue is closed, Renovate will create a new one instead of reopening
- Helps maintain a cleaner issue/PR history
- Particularly useful for dependency dashboard issues that are manually closed

```json
{
  "recreateClosed": false
}
```

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

### Python-Specific Issues

#### Issue: Renovate creates conflicting version constraints

**Symptom**: Multiple requirements files have conflicting versions for the same package.

**Solution**: 
- Ensure `requirements-dev.txt` includes `-r requirements.txt` at the top
- Use `requirements-core.txt` for minimal installations
- Core dependencies should be defined in `requirements.txt` only

#### Issue: Selenium updates break tests

**Symptom**: Tests fail after Selenium auto-update.

**Solution**:
- Selenium updates require manual approval (already configured)
- Test with latest Chrome/Firefox/Edge versions
- Check WebDriver Manager compatibility
- Update browser drivers if needed

#### Issue: Package groups not working

**Symptom**: Linting tools create separate PRs instead of grouped updates.

**Solution**:
- Check package name patterns in `renovate.json`
- Verify package names match the regex patterns
- Common patterns: `^pytest.*`, `^(black|flake8|isort).*`

#### Issue: Requirements file not detected

**Symptom**: Renovate doesn't update a requirements file.

**Solution**:
- File must match pattern: `requirements*.txt`
- File must be in repository root or subdirectories
- Check `pip_requirements.fileMatch` in `renovate.json`

#### Issue: Unwanted package updates

**Symptom**: Renovate updates packages that should stay pinned.

**Solution**:
- Add package to `ignoreDeps` array in `renovate.json`
- Or create a package rule with `enabled: false`
- Example: pip is already disabled in the configuration

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
- **Digest pinning**: GitHub Actions are pinned to specific SHAs
- **Vulnerability alerts**: Security issues labeled and require manual review

## Best Practices for Python Projects

### Requirements File Structure

This project uses a three-tier requirements structure:

1. **requirements.txt**: Production dependencies only
   - Core packages needed to run the application
   - Version constraints using `>=` for flexibility

2. **requirements-core.txt**: Minimal core dependencies
   - Subset of production dependencies
   - Excludes heavy dependencies like Selenium
   - Used for lightweight testing and installations

3. **requirements-dev.txt**: Development dependencies
   - Includes production dependencies via `-r requirements.txt`
   - Testing tools (pytest, coverage)
   - Code quality tools (black, flake8, mypy)
   - Development utilities

### Version Constraint Guidelines

- **Use `>=` for flexibility**: `requests>=2.28` allows minor/patch updates
- **Pin exact versions sparingly**: Only when absolutely necessary
- **Avoid upper bounds**: Don't use `<` unless there's a known incompatibility
- **Let Renovate manage versions**: Trust the automation for routine updates

### Handling Major Updates

1. **Review the changelog**: Check for breaking changes
2. **Test locally**: Run full test suite before approving
3. **Check compatibility**: Ensure all dependencies work together
4. **Approve in dashboard**: Use Renovate's dependency dashboard
5. **Monitor CI**: Watch for failures after merge

### Grouping Strategy

The configuration groups related packages to reduce PR volume:

- **Linting tools**: Updated together to maintain consistent code style
- **Testing tools**: Updated together to ensure test compatibility
- **Core dependencies**: Non-major updates grouped for easier review

### Auto-merge Strategy

Auto-merge is enabled for:
- Minor and patch updates of most packages
- Grouped linting and testing tool updates
- GitHub Actions updates (with digest pinning)

Auto-merge is disabled for:
- Major version updates (breaking changes)
- Selenium and WebDriver Manager (compatibility issues)
- Setuptools (potential build breakage)
- Security vulnerabilities (require review)

## References

- [Renovate Documentation](https://docs.renovatebot.com/)
- [GitHub Auto-merge](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/automatically-merging-a-pull-request)
- [Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)
