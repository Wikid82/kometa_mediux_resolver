---
name: Fix failing tests (priority)
about: Resolve current failing tests to increase coverage and unblock Alpha
labels: [alpha, tests, priority]
assignees: []
---

Steps:

- Run full test suite locally: `pytest -q` and `pytest -q --maxfail=1` to get first failing test
- Focus on mediux_scraper Selenium-related failures first:
  - Update tests to patch internal `_import_selenium` so they don't rely on a real selenium environment
  - Ensure that tests patch `mediux_scraper._import_selenium` at import site
  - Where tests mock WebDriver/ExpectedConditions, use lightweight stand-ins
- Fix any tests that patch the wrong symbol (patch where used, not where defined)
- Re-run tests and iterate until all tests pass

Acceptance criteria:

- Full test suite passes locally
- No tests rely on external network or actual Selenium unless explicitly marked as integration
- Coverage increases (next target: >=85% before continuing to other alpha tasks)

Notes:
- If Selenium integration tests are needed, mark them with `@pytest.mark.selenium` and skip by default in CI unless a runner with selenium is available.
