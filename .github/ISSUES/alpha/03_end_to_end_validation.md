---
name: "[ALPHA-P3] End-to-End Workflow Validation"
about: Validate the tool works with real test data from resolver_test_library
title: "[ALPHA-P3] End-to-End Workflow Validation"
labels: ["alpha", "priority-high", "testing", "integration"]
assignees: []
---

## 🎯 Objective
Validate that the core workflow works end-to-end with the test library files.

## 📊 Current Status
- **Test library**: 35+ YAML files in `resolver_test_library/`
- **End-to-end tests**: Not validated
- **Integration status**: Unknown if tool works on real data

## 🔍 Workflow to Validate

### 1. Basic Dry Run
```bash
python3 kometa_mediux_resolver.py --root ./resolver_test_library --output /tmp/test_output.json -v
```

### 2. Expected Behaviors
- Scans all YAML files in test library
- Parses metadata correctly
- Fetches assets from MediUX API
- Generates output JSON with proposed changes
- No crashes or unhandled exceptions

### 3. Error Scenarios
- Network unavailable
- Malformed YAML file
- Missing configuration
- Invalid MediUX URLs

## 📝 Tasks

### Phase 1: Basic Validation
- [ ] Run dry-run command on test library
- [ ] Verify no crashes occur
- [ ] Check that YAML files are discovered
- [ ] Verify output JSON is generated
- [ ] Inspect output for reasonable asset data

### Phase 2: Functionality Checks
- [ ] Test URL parsing from YAML files
- [ ] Test asset ID extraction
- [ ] Test API communication (or mock)
- [ ] Test URL probe functionality
- [ ] Test backup creation logic

### Phase 3: Error Handling
- [ ] Test with network disabled
- [ ] Test with invalid YAML file
- [ ] Test with missing config
- [ ] Test with invalid MediUX URL
- [ ] Verify graceful error messages

### Phase 4: Apply Mode (if safe)
- [ ] Create test copies of YAML files
- [ ] Run with --apply on test copies
- [ ] Verify files are modified correctly
- [ ] Verify backups are created
- [ ] Check YAML structure is preserved

## ✅ Definition of Done
- [ ] Tool runs successfully on test library
- [ ] Core workflow completes without errors
- [ ] Output JSON contains expected data
- [ ] Error handling works gracefully
- [ ] Basic integration documented

## 🔗 Related Files
- `resolver_test_library/*.yml` (test data)
- `kometa_mediux_resolver.py` (main script)
- `config/config.yml.example`
- Test output: `/tmp/test_output.json`

## ⚠️ Priority
**HIGH - P3**: Validates real-world usage. Required for alpha release confidence.

## 📝 Notes
- Use test data only, not production YAMLs
- Document any issues found
- This validates the "happy path" works
- Comprehensive testing is beta goal
- Focus on proving the tool is usable
