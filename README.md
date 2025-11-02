# Kometa MediUX Resolver

This repository contains the resolver tool and its helpers. The tool discovers MediUX assets
and proposes safe `url_poster` additions to existing Kometa YAML metadata files.

Entry points

- `kometa_mediux_resolver.py` — main CLI script (recommended alias: `kometa-resolver`).
- `mediux_scraper.py` — optional Selenium-based scraper fallback (only used with `--use-scrape`).
- `kometa_metadata_schema.json` — optional JSON Schema used for validation before writes.

Dependencies

- `requirements.txt` — production dependencies.
- `requirements-dev.txt` — development dependencies (includes production dependencies).

Installation

```bash
# Production use (minimal dependencies)
pip install -r requirements.txt

# Development (includes all production + development tools)
pip install -r requirements-dev.txt
```

Usage examples (from repository root):

```
python3 kometa_mediux_resolver.py --root . --output /tmp/changes.json

# Dry-run that scrapes when API listing fails
python3 kometa_mediux_resolver.py --root . --use-scrape --output /tmp/changes.json -vv

# Apply changes (writes files; creates backups)
python3 kometa_mediux_resolver.py --root . --apply --require-probe-ok --output /tmp/changes.json
```

Notes

- The resolver updates existing Kometa metadata files only; it will not create new metadata files.
- For Docker: mount the folder containing your Kometa YAMLs and pass that path to `--root`.
- If you want a short CLI name, create a small wrapper script or an installed entry point named `kometa-resolver` that calls the script above.
