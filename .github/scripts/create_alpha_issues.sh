#!/bin/bash
# Create Alpha Issues on GitHub with Priority Labels
# Run from repository root: .github/scripts/create_alpha_issues.sh

set -e

REPO="Wikid82/kometa_mediux_resolver"
ISSUES_DIR=".github/ISSUES/alpha"

echo "🚀 Creating Alpha Issues for $REPO"
echo ""

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub"
    echo "Run: gh auth login"
    exit 1
fi

# Function to create issue from markdown file
create_issue() {
    local file=$1
    local priority=$2

    echo "📝 Creating issue from: $(basename $file)"

    # Extract title from the markdown file
    title=$(grep "^title:" "$file" | sed 's/title: "\(.*\)"/\1/' | sed 's/title: //')

    # Extract labels from the markdown file - clean up whitespace
    labels=$(grep "^labels:" "$file" | sed 's/labels: \[\(.*\)\]/\1/' | sed 's/labels: //' | tr -d '"[]' | sed 's/, */,/g')

    # Remove frontmatter and create issue
    body=$(sed '1,/^---$/d; /^---$/,/^---$/d' "$file")

    # Create the issue
    issue_url=$(gh issue create \
        --repo "$REPO" \
        --title "$title" \
        --body "$body" \
        --label "$labels")

    echo "✅ Created: $issue_url"
    echo ""
}

# Create issues in priority order
echo "Creating P0 (Critical) issues..."
if [ -f "$ISSUES_DIR/00_install_test_dependencies.md" ]; then
    create_issue "$ISSUES_DIR/00_install_test_dependencies.md" "P0"
fi

echo "Creating P1 (Critical) issues..."
if [ -f "$ISSUES_DIR/01_fix_test_infrastructure.md" ]; then
    create_issue "$ISSUES_DIR/01_fix_test_infrastructure.md" "P1"
fi

echo "Creating P2 (High) issues..."
if [ -f "$ISSUES_DIR/02_core_module_coverage.md" ]; then
    create_issue "$ISSUES_DIR/02_core_module_coverage.md" "P2"
fi

echo "Creating P3 (High) issues..."
if [ -f "$ISSUES_DIR/03_end_to_end_validation.md" ]; then
    create_issue "$ISSUES_DIR/03_end_to_end_validation.md" "P3"
fi

echo "Creating P4 (Medium) issues..."
if [ -f "$ISSUES_DIR/04_basic_error_handling.md" ]; then
    create_issue "$ISSUES_DIR/04_basic_error_handling.md" "P4"
fi

echo "Creating P5 (Medium) issues..."
if [ -f "$ISSUES_DIR/05_ci_pipeline_green.md" ]; then
    create_issue "$ISSUES_DIR/05_ci_pipeline_green.md" "P5"
fi

echo "Creating P6 (Low) issues..."
if [ -f "$ISSUES_DIR/06_alpha_documentation.md" ]; then
    create_issue "$ISSUES_DIR/06_alpha_documentation.md" "P6"
fi

echo "Creating P7 (Low) issues..."
if [ -f "$ISSUES_DIR/07_alpha_release.md" ]; then
    create_issue "$ISSUES_DIR/07_alpha_release.md" "P7"
fi

echo "🎉 All Alpha issues created successfully!"
echo ""
echo "📊 View issues at: https://github.com/$REPO/issues"
echo ""
echo "💡 Next steps:"
echo "  1. Review issues and assign to yourself"
echo "  2. Add issues to your project board"
echo "  3. Start with P0 (Install Test Dependencies)"
