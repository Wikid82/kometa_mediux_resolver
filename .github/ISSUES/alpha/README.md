# Alpha Release Issue Tracker

This directory contains issue templates for the Alpha release milestone.

## Priority Structure

Issues are prioritized using a P0-P7 system:

| Priority | Label | Description | Blocking |
|----------|-------|-------------|----------|
| **P0** | `priority-critical` | Must complete first - blocks all other work | YES |
| **P1** | `priority-critical` | Critical path - blocks quality validation | YES |
| **P2** | `priority-high` | Core functionality - required for alpha | YES |
| **P3** | `priority-high` | Integration validation - required for alpha | YES |
| **P4** | `priority-medium` | Important for stability - strongly recommended | NO |
| **P5** | `priority-medium` | Quality gates - strongly recommended | NO |
| **P6** | `priority-low` | Documentation - nice to have | NO |
| **P7** | `priority-low` | Release preparation - final step | NO |

## Alpha Issues

### Critical Path (P0-P1)
1. **[P0] Install Test Infrastructure** (`00_install_test_dependencies.md`)
   - Install pytest-cov and coverage tools
   - Blocks: All testing work
   - Status: 🔴 Not Started

2. **[P1] Fix Test Infrastructure** (`01_fix_test_infrastructure.md`)
   - Fix ~70 failing tests
   - Blocks: Coverage measurement
   - Status: 🔴 Not Started

### Core Functionality (P2-P3)
3. **[P2] Core Module Coverage** (`02_core_module_coverage.md`)
   - Achieve 50%+ coverage in kometa_mediux_resolver.py
   - Blocks: Alpha release
   - Status: 🔴 Not Started

4. **[P3] End-to-End Validation** (`03_end_to_end_validation.md`)
   - Validate tool works with real test data
   - Blocks: Alpha release
   - Status: 🔴 Not Started

### Stability & Quality (P4-P5)
5. **[P4] Basic Error Handling** (`04_basic_error_handling.md`)
   - Prevent crashes on common errors
   - Recommended for alpha
   - Status: 🔴 Not Started

6. **[P5] CI/CD Pipeline Green** (`05_ci_pipeline_green.md`)
   - All GitHub Actions passing
   - Recommended for alpha
   - Status: 🔴 Not Started

### Polish (P6-P7)
7. **[P6] Alpha Documentation** (`06_alpha_documentation.md`)
   - Quick start and usage guide
   - Nice to have
   - Status: 🔴 Not Started

8. **[P7] Alpha Release** (`07_alpha_release.md`)
   - Release v0.1.0-alpha
   - Final step
   - Status: 🔴 Not Started

## Opening Issues on GitHub

### Using GitHub CLI (Recommended)

```bash
# From repository root
chmod +x .github/scripts/create_alpha_issues.sh
.github/scripts/create_alpha_issues.sh
```

This will create all issues with proper labels and priority tags.

### Manual Creation

If you prefer to create issues manually:

1. Go to https://github.com/Wikid82/kometa_mediux_resolver/issues
2. Click "New issue"
3. Copy content from each `.md` file in priority order
4. Add labels: `alpha`, `priority-critical`/`priority-high`/`priority-medium`/`priority-low`, and specific labels
5. Create issue

## Labels to Create

Create these labels in your repository settings:

| Label | Color | Description |
|-------|-------|-------------|
| `alpha` | `#0052CC` | Part of alpha milestone |
| `priority-critical` | `#B60205` | P0-P1: Must fix immediately |
| `priority-high` | `#D93F0B` | P2-P3: Required for release |
| `priority-medium` | `#FBCA04` | P4-P5: Strongly recommended |
| `priority-low` | `#0E8A16` | P6-P7: Nice to have |
| `tests` | `#FEF2C0` | Testing related |
| `coverage` | `#BFD4F2` | Test coverage |
| `infrastructure` | `#5319E7` | Development infrastructure |
| `bug` | `#D73A4A` | Something isn't working |
| `enhancement` | `#A2EEEF` | New feature or improvement |
| `documentation` | `#0075CA` | Documentation only |
| `ci-cd` | `#D4C5F9` | Continuous integration |

## Alpha Definition of Done

An Alpha release means:

✅ **Functional Requirements**
- [ ] Tool runs without crashes
- [ ] Core workflow works end-to-end
- [ ] Basic error handling prevents data loss
- [ ] Output is valid and useful

✅ **Quality Requirements**
- [ ] Tests passing (>90%)
- [ ] Core coverage >50%
- [ ] CI/CD pipeline green
- [ ] No critical bugs

✅ **Documentation Requirements**
- [ ] Installation instructions
- [ ] Basic usage guide
- [ ] Configuration example
- [ ] Known issues documented

## Current Status

**Overall Progress**: 🔴 0/8 issues complete (0%)

**Critical Path**: 🔴 P0-P1 not started
**Core Work**: 🔴 P2-P3 not started
**Polish**: 🔴 P4-P7 not started

**Estimated Timeline**:
- P0: 1 hour (install dependencies)
- P1: 2-4 days (fix tests)
- P2: 2-3 days (add coverage)
- P3: 1-2 days (validation)
- P4: 1-2 days (error handling)
- P5: 1 day (CI/CD)
- P6: 1 day (docs)
- P7: 1 day (release)

**Total**: 10-15 days to alpha

## Next Steps

1. **Create GitHub labels** (5 minutes)
2. **Run the issue creation script** (2 minutes)
3. **Review issues on GitHub** (10 minutes)
4. **Assign P0 to yourself** and start immediately
5. **Work through issues in priority order**

## Support

Questions or issues with this tracker? Create an issue with the `alpha` label.
