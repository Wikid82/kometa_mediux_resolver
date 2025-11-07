#!/bin/bash
# Create Labels for Alpha Issues
# Run from repository root: .github/scripts/create_labels.sh

set -e

REPO="Wikid82/kometa_mediux_resolver"

echo "🏷️  Creating labels for $REPO"
echo ""

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Function to create or update label
create_label() {
    local name=$1
    local color=$2
    local description=$3

    echo "Creating label: $name"
    gh label create "$name" --color "$color" --description "$description" --repo "$REPO" 2>/dev/null || \
    gh label edit "$name" --color "$color" --description "$description" --repo "$REPO" 2>/dev/null || \
    echo "  ⚠️  Label '$name' already exists (skipped)"
}

# Alpha milestone label
create_label "alpha" "0052CC" "Part of alpha milestone"

# Priority labels
create_label "priority-critical" "B60205" "P0-P1: Must fix immediately"
create_label "priority-high" "D93F0B" "P2-P3: Required for release"
create_label "priority-medium" "FBCA04" "P4-P5: Strongly recommended"
create_label "priority-low" "0E8A16" "P6-P7: Nice to have"

# Category labels
create_label "tests" "FEF2C0" "Testing related"
create_label "coverage" "BFD4F2" "Test coverage"
create_label "infrastructure" "5319E7" "Development infrastructure"
create_label "bug" "D73A4A" "Something isn't working"
create_label "enhancement" "A2EEEF" "New feature or improvement"
create_label "documentation" "0075CA" "Documentation only"
create_label "ci-cd" "D4C5F9" "Continuous integration"
create_label "reliability" "C5DEF5" "Error handling and stability"
create_label "integration" "BFDADC" "Integration testing"
create_label "release" "E99695" "Release preparation"

echo ""
echo "✅ All labels created/updated successfully!"
echo ""
echo "View labels at: https://github.com/$REPO/labels"
