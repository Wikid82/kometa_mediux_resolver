#!/usr/bin/env bash
# Helper to open the Alpha issues defined in .github/ISSUES/alpha
# Requires: gh CLI authenticated (gh auth login) and GITHUB_TOKEN secret set for repo automation

set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
ISSUES_DIR="$ROOT_DIR/.github/ISSUES/alpha"

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI is not installed. Install from https://cli.github.com/"
  exit 1
fi

for f in "$ISSUES_DIR"/*.md; do
  echo "Opening issue from $f"
  title=$(awk -F":" '/^name:/{print substr($0, index($0,$2)+1)}' "$f" | sed 's/^ *//')
  body=$(sed -n '1,200p' "$f")
  labels_raw=$(awk -F":" '/^labels:/{print substr($0, index($0,$2)+1)}' "$f" | sed 's/^ *//')
  # Normalize labels: remove surrounding brackets and whitespace, convert ", " to ","
  labels=$(echo "$labels_raw" | tr -d '[]' | sed 's/, */,/g' | sed 's/^ *//; s/ *$//')
  # Create the issue
  if [ -z "$title" ]; then
    echo "Skipping $f — no title found"
    continue
  fi
  echo "Creating issue: $title"
  # Build gh args dynamically to avoid passing empty --label
  gh_args=("issue" "create" "--title" "$title" "--body-file" "$f")
  if [ -n "$labels" ]; then
    # Ensure labels exist in the repository; create them if missing (lightweight default color)
    OLDIFS="$IFS"
    IFS=','
    read -ra label_array <<< "$labels"
    for lab in "${label_array[@]}"; do
      lab_trimmed=$(echo "$lab" | sed 's/^ *//; s/ *$//')
      if [ -n "$lab_trimmed" ]; then
        if ! gh label view --repo "Wikid82/kometa_mediux_resolver" "$lab_trimmed" >/dev/null 2>&1; then
          echo "Creating missing label: $lab_trimmed"
          # If creation fails (label race), continue without failing the whole script
          gh label create "$lab_trimmed" --color "ededed" --description "auto-created" >/dev/null 2>&1 || true
        fi
      fi
    done
    IFS="$OLDIFS"
    gh_args+=("--label" "$labels")
  fi
  gh_args+=("--assignee" "")
  # Run gh command
  "$(command -v gh)" "${gh_args[@]}"
  sleep 1
done

echo "All alpha issues created. The repository's project automation should add them to the project board."
