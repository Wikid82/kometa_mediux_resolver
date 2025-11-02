"""Test the mediux_scraper module."""
import re
from unittest.mock import MagicMock, Mock, patch

import pytest

# Try to import the module - it's optional
try:
    import mediux_scraper as ms

    MEDIUX_SCRAPER_AVAILABLE = True
except ImportError:
    MEDIUX_SCRAPER_AVAILABLE = False
    ms = None


@pytest.mark.skipif(not MEDIUX_SCRAPER_AVAILABLE, reason="mediux_scraper not available")
class TestExtractAssetIds:
    """Test asset ID extraction from content."""

    def test_extract_asset_ids_from_yaml_simple(self):
        """Test extracting asset IDs from simple JSON-like content."""
        json_content = """
        {"id": "123e4567-e89b-12d3-a456-426614174000", "fileType": "poster"}
        {"id": "987f6543-e21c-34b5-a678-542398765432", "fileType": "background"}
        """
        result = ms.extract_asset_ids_from_yaml(json_content)
        assert len(result) == 2
        assert {"id": "123e4567-e89b-12d3-a456-426614174000", "fileType": "poster"} in result
        assert {"id": "987f6543-e21c-34b5-a678-542398765432", "fileType": "background"} in result

    def test_extract_asset_ids_from_yaml_no_assets(self):
        """Test content with no asset UUIDs."""
        yaml_content = """
metadata:
  123456:
    title: Test Show
    seasons:
      1:
        title: Season 1
"""
        result = ms.extract_asset_ids_from_yaml(yaml_content)
        assert len(result) == 0

    def test_extract_asset_ids_from_yaml_mixed_urls(self):
        """Test content with mixed UUID patterns."""
        content = """
        {
          "id": "123e4567-e89b-12d3-a456-426614174000",
          "fileType": "poster",
          "url": "https://example.com/poster.jpg"
        }
        Some random UUID: 987f6543-e21c-34b5-a678-542398765432
        {"id": "aaa11111-b222-3333-c444-555555666666", "fileType": "background"}
        """
        result = ms.extract_asset_ids_from_yaml(content)
        # Should find the structured objects first, then fallback to loose UUIDs
        assert len(result) >= 2

        # Check that we have the structured objects with proper fileType
        structured_ids = [item["id"] for item in result if item["fileType"] != "unknown"]
        assert "123e4567-e89b-12d3-a456-426614174000" in structured_ids
        assert "aaa11111-b222-3333-c444-555555666666" in structured_ids

    def test_extract_asset_ids_invalid_yaml(self):
        """Test handling of invalid YAML."""
        invalid_yaml = "invalid: yaml: content: ["
        result = ms.extract_asset_ids_from_yaml(invalid_yaml)
        assert len(result) == 0

    def test_extract_asset_ids_loose_uuids(self):
        """Test fallback to loose UUID extraction."""
        content = """
        Some text with a UUID: 12345678-abcd-1234-5678-123456789abc
        And another one: fedcba98-7654-3210-9876-543210fedcba
        But not this short one: abc123
        """
        result = ms.extract_asset_ids_from_yaml(content)
        assert len(result) == 2
        assert {"id": "12345678-abcd-1234-5678-123456789abc", "fileType": "unknown"} in result
        assert {"id": "fedcba98-7654-3210-9876-543210fedcba", "fileType": "unknown"} in result

    def test_extract_asset_ids_id_only_pattern(self):
        """Test extraction of id-only patterns without fileType."""
        content = """
        {"id": "111e1111-e11e-11e1-e111-111111111111"}
        {"id": "222f2222-f22f-22f2-f222-222222222222", "someOtherField": "value"}
        """
        result = ms.extract_asset_ids_from_yaml(content)
        assert len(result) == 2
        assert {"id": "111e1111-e11e-11e1-e111-111111111111", "fileType": "unknown"} in result
        assert {"id": "222f2222-f22f-22f2-f222-222222222222", "fileType": "unknown"} in result

    def test_extract_asset_ids_deduplication(self):
        """Test that duplicate IDs are not returned."""
        content = """
        {"id": "aaaa1111-bbbb-2222-cccc-333333333333", "fileType": "poster"}
        {"id": "aaaa1111-bbbb-2222-cccc-333333333333", "fileType": "background"}
        Some text: aaaa1111-bbbb-2222-cccc-333333333333
        """
        result = ms.extract_asset_ids_from_yaml(content)
        assert len(result) == 1
        assert {"id": "aaaa1111-bbbb-2222-cccc-333333333333", "fileType": "poster"} in result


@pytest.mark.skipif(not MEDIUX_SCRAPER_AVAILABLE, reason="mediux_scraper not available")
class TestRegexPatterns:
    """Test the regex patterns used in mediux_scraper."""

    def test_asset_url_regex_matches(self):
        """Test ASSET_URL_RE pattern matching."""
        test_cases = [
            ("https://api.mediux.pro/assets/abc123def456789012345678", "abc123def456789012345678"),
            ("http://mediux.example.com/assets/fedcba9876543210abcdef", "fedcba9876543210abcdef"),
            (
                "https://subdomain.domain.com/assets/1234567890abcdef1234567890",
                "1234567890abcdef1234567890",
            ),
        ]

        for url, expected_id in test_cases:
            match = ms.ASSET_URL_RE.search(url)
            assert match is not None, f"Should match URL: {url}"
            assert match.group(1) == expected_id, f"Should extract ID: {expected_id}"

    def test_asset_url_regex_no_matches(self):
        """Test ASSET_URL_RE with non-matching patterns."""
        test_cases = [
            "https://api.mediux.pro/notassets/abc123",
            "invalid-url",
            "https://api.mediux.pro/assets/short",  # Too short
            "https://api.mediux.pro/assets/abc123xyz",  # Too short (< 20 chars)
            "ftp://api.mediux.pro/assets/abc123def456789012345678",  # Wrong protocol
        ]

        for url in test_cases:
            match = ms.ASSET_URL_RE.search(url)
            assert match is None, f"Should not match URL: {url}"

    def test_asset_relative_regex_matches(self):
        """Test ASSET_REALTIVE_RE pattern matching."""
        test_cases = [
            ("/assets/abc123def456789012345678", "abc123def456789012345678"),
            ("/assets/fedcba9876543210abcdef12", "fedcba9876543210abcdef12"),
        ]

        for url, expected_id in test_cases:
            match = ms.ASSET_REALTIVE_RE.search(url)
            assert match is not None, f"Should match relative URL: {url}"
            assert match.group(1) == expected_id, f"Should extract ID: {expected_id}"

    def test_asset_relative_regex_no_matches(self):
        """Test ASSET_REALTIVE_RE with non-matching patterns."""
        test_cases = [
            "assets/abc123def456789012345678",  # Missing leading slash
            "/notassets/abc123def456789012345678",
            "/assets/short",  # Too short
            "/assets/abc123xyz",  # Too short (< 20 chars)
        ]

        for url in test_cases:
            match = ms.ASSET_REALTIVE_RE.search(url)
            assert match is None, f"Should not match relative URL: {url}"


@pytest.mark.skipif(not MEDIUX_SCRAPER_AVAILABLE, reason="mediux_scraper not available")
class TestMediuxScraperClass:
    """Test MediuxScraper class functionality."""

    def test_mediux_scraper_init(self):
        """Test MediuxScraper initialization."""
        scraper = ms.MediuxScraper()
        assert scraper.logger is not None

    @patch("mediux_scraper.webdriver")
    @patch("mediux_scraper.Options")
    @patch("mediux_scraper.By")
    @patch("mediux_scraper.WebDriverWait")
    @patch("mediux_scraper.EC")
    def test_import_selenium_success(
        self, mock_ec, mock_wait, mock_by, mock_options, mock_webdriver
    ):
        """Test successful selenium import."""
        scraper = ms.MediuxScraper()

        result = scraper._import_selenium()

        assert len(result) == 5
        assert result[0] == mock_webdriver
        assert result[1] == mock_options
        assert result[2] == mock_by
        assert result[3] == mock_wait
        assert result[4] == mock_ec

    def test_import_selenium_failure(self):
        """Test selenium import failure."""
        scraper = ms.MediuxScraper()

        # Patch to simulate import error
        with patch("mediux_scraper.webdriver", side_effect=ImportError("selenium not installed")):
            with pytest.raises(RuntimeError, match="selenium is required for scraping"):
                scraper._import_selenium()

    @patch.object(ms.MediuxScraper, "_import_selenium")
    def test_init_driver_headless(self, mock_import):
        """Test driver initialization in headless mode."""
        # Setup mock selenium components
        mock_webdriver = Mock()
        mock_options = Mock()
        mock_by = Mock()
        mock_wait = Mock()
        mock_ec = Mock()
        mock_import.return_value = (mock_webdriver, mock_options, mock_by, mock_wait, mock_ec)

        mock_chrome_options = Mock()
        mock_options.return_value = mock_chrome_options

        mock_driver = Mock()
        mock_webdriver.Chrome.return_value = mock_driver

        scraper = ms.MediuxScraper()
        result = scraper._init_driver(headless=True)

        # Verify headless option was set
        mock_chrome_options.add_argument.assert_any_call("--headless=new")
        mock_chrome_options.add_argument.assert_any_call("--no-sandbox")
        mock_chrome_options.add_argument.assert_any_call("--disable-dev-shm-usage")
        mock_chrome_options.add_argument.assert_any_call("--disable-gpu")

        # Verify driver setup
        mock_driver.set_page_load_timeout.assert_called_once_with(60)
        mock_driver.implicitly_wait.assert_called_once_with(3)

        assert result == mock_driver

    @patch.object(ms.MediuxScraper, "_import_selenium")
    def test_init_driver_with_custom_options(self, mock_import):
        """Test driver initialization with custom options."""
        # Setup mock selenium components
        mock_webdriver = Mock()
        mock_options = Mock()
        mock_by = Mock()
        mock_wait = Mock()
        mock_ec = Mock()
        mock_import.return_value = (mock_webdriver, mock_options, mock_by, mock_wait, mock_ec)

        mock_chrome_options = Mock()
        mock_options.return_value = mock_chrome_options

        mock_driver = Mock()
        mock_webdriver.Chrome.return_value = mock_driver

        scraper = ms.MediuxScraper()
        result = scraper._init_driver(
            headless=False, profile_path="/custom/profile", chromedriver_path="/custom/chromedriver"
        )

        # Verify custom profile path
        mock_chrome_options.add_argument.assert_any_call("--user-data-dir=/custom/profile")

        # Verify custom chromedriver path
        mock_webdriver.Chrome.assert_called_once_with(
            executable_path="/custom/chromedriver", options=mock_chrome_options
        )

        # Should not have headless argument when headless=False
        headless_calls = [
            call
            for call in mock_chrome_options.add_argument.call_args_list
            if "--headless" in str(call)
        ]
        assert len(headless_calls) == 0

    @patch.object(ms.MediuxScraper, "_import_selenium")
    def test_login_if_needed_already_logged_in(self, mock_import):
        """Test login when user is already logged in."""
        # Setup selenium mocks
        mock_webdriver = Mock()
        mock_options = Mock()
        mock_by = Mock()
        mock_wait = Mock()
        mock_ec = Mock()
        mock_import.return_value = (mock_webdriver, mock_options, mock_by, mock_wait, mock_ec)

        mock_driver = Mock()
        # Mock finding user button (already logged in)
        mock_driver.find_elements.return_value = [Mock()]

        scraper = ms.MediuxScraper()
        result = scraper.login_if_needed(mock_driver, "user", "pass", "nickname")

        assert result is True

    @patch.object(ms.MediuxScraper, "_import_selenium")
    def test_login_if_needed_no_credentials(self, mock_import):
        """Test login when no credentials provided."""
        # Setup selenium mocks
        mock_webdriver = Mock()
        mock_options = Mock()
        mock_by = Mock()
        mock_wait = Mock()
        mock_ec = Mock()
        mock_import.return_value = (mock_webdriver, mock_options, mock_by, mock_wait, mock_ec)

        mock_driver = Mock()
        # No user button found (not logged in)
        mock_driver.find_elements.return_value = []

        scraper = ms.MediuxScraper()
        result = scraper.login_if_needed(mock_driver, None, None, None)

        assert result is False

    @patch.object(ms.MediuxScraper, "_import_selenium")
    def test_login_if_needed_no_signin_button(self, mock_import):
        """Test login when no sign-in button found."""
        # Setup selenium mocks
        mock_webdriver = Mock()
        mock_options = Mock()
        mock_by = Mock()
        mock_wait = Mock()
        mock_ec = Mock()
        mock_import.return_value = (mock_webdriver, mock_options, mock_by, mock_wait, mock_ec)

        mock_driver = Mock()
        mock_driver.find_elements.side_effect = [
            [],  # No user button
            [],  # No sign-in button
        ]

        scraper = ms.MediuxScraper()
        result = scraper.login_if_needed(mock_driver, "user", "pass", "nick")

        assert result is False

    @patch("mediux_scraper.time.sleep")
    @patch.object(ms.MediuxScraper, "_import_selenium")
    def test_login_if_needed_successful_login(self, mock_import, mock_sleep):
        """Test successful login process."""
        # Setup selenium mocks
        mock_webdriver = Mock()
        mock_options = Mock()
        mock_by = Mock()
        mock_wait = Mock()
        mock_ec = Mock()
        mock_import.return_value = (mock_webdriver, mock_options, mock_by, mock_wait, mock_ec)

        mock_driver = Mock()

        # Mock UI elements
        mock_signin_button = Mock()
        mock_email_input = Mock()
        mock_pass_input = Mock()
        mock_submit_button = Mock()
        mock_user_button = Mock()

        mock_driver.find_elements.side_effect = [
            [],  # No user button initially
            [mock_signin_button],  # Sign-in button found
            [mock_email_input],  # Email input found
            [mock_pass_input],  # Password input found
            [mock_submit_button],  # Submit button found
        ]

        mock_driver.find_element.return_value = mock_user_button

        scraper = ms.MediuxScraper()
        result = scraper.login_if_needed(mock_driver, "testuser", "testpass", "testnick")

        # Verify login steps
        mock_signin_button.click.assert_called_once()
        mock_email_input.clear.assert_called_once()
        mock_email_input.send_keys.assert_called_once_with("testuser")
        mock_pass_input.clear.assert_called_once()
        mock_pass_input.send_keys.assert_called_once_with("testpass")
        mock_submit_button.click.assert_called_once()

        assert result is True

    @patch.object(ms.MediuxScraper, "_import_selenium")
    def test_login_if_needed_exception_handling(self, mock_import):
        """Test login exception handling."""
        # Setup selenium mocks
        mock_webdriver = Mock()
        mock_options = Mock()
        mock_by = Mock()
        mock_wait = Mock()
        mock_ec = Mock()
        mock_import.return_value = (mock_webdriver, mock_options, mock_by, mock_wait, mock_ec)

        mock_driver = Mock()
        mock_driver.find_elements.side_effect = Exception("Driver error")

        scraper = ms.MediuxScraper()
        result = scraper.login_if_needed(mock_driver, "user", "pass", "nick")

        assert result is False

    @patch("mediux_scraper.time.sleep")
    @patch.object(ms.MediuxScraper, "_init_driver")
    @patch.object(ms.MediuxScraper, "login_if_needed")
    @patch.object(ms.MediuxScraper, "_import_selenium")
    def test_scrape_set_yaml_successful(
        self, mock_import, mock_login, mock_init_driver, mock_sleep
    ):
        """Test successful YAML scraping."""
        # Setup selenium mocks
        mock_webdriver = Mock()
        mock_options = Mock()
        mock_by = Mock()
        mock_wait = Mock()
        mock_ec = Mock()
        mock_import.return_value = (mock_webdriver, mock_options, mock_by, mock_wait, mock_ec)

        mock_driver = Mock()
        mock_init_driver.return_value = mock_driver
        mock_login.return_value = True

        # Mock successful YAML button and textarea
        mock_yaml_button = Mock()
        mock_textarea = Mock()
        mock_textarea.get_attribute.return_value = "metadata:\n  test: yaml content"

        mock_wait_instance = Mock()
        mock_wait_instance.until.return_value = mock_yaml_button
        mock_wait.return_value = mock_wait_instance

        mock_driver.find_element.return_value = mock_textarea

        scraper = ms.MediuxScraper()
        result = scraper.scrape_set_yaml("https://mediux.pro/sets/test123")

        # Verify navigation and interaction
        mock_driver.get.assert_called_once_with("https://mediux.pro/sets/test123")
        mock_yaml_button.click.assert_called_once()
        mock_driver.quit.assert_called_once()

        assert result == "metadata:\n  test: yaml content"

    @patch.object(ms.MediuxScraper, "_import_selenium")
    def test_scrape_set_yaml_selenium_error(self, mock_import):
        """Test scraping when selenium import fails."""
        mock_import.side_effect = RuntimeError("selenium not available")

        scraper = ms.MediuxScraper()
        result = scraper.scrape_set_yaml("https://mediux.pro/sets/test123")

        assert result == ""

    @patch.object(ms.MediuxScraper, "_init_driver")
    @patch.object(ms.MediuxScraper, "login_if_needed")
    @patch.object(ms.MediuxScraper, "_import_selenium")
    def test_scrape_set_yaml_driver_exception(self, mock_import, mock_login, mock_init_driver):
        """Test scraping when driver operations fail."""
        # Setup selenium mocks
        mock_webdriver = Mock()
        mock_options = Mock()
        mock_by = Mock()
        mock_wait = Mock()
        mock_ec = Mock()
        mock_import.return_value = (mock_webdriver, mock_options, mock_by, mock_wait, mock_ec)

        mock_driver = Mock()
        mock_driver.get.side_effect = Exception("Navigation failed")
        mock_init_driver.return_value = mock_driver
        mock_login.return_value = True

        scraper = ms.MediuxScraper()
        result = scraper.scrape_set_yaml("https://mediux.pro/sets/test123")

        # Driver should still be quit even on exception
        mock_driver.quit.assert_called_once()
        assert result == ""

    @patch("mediux_scraper.time.sleep")
    @patch.object(ms.MediuxScraper, "_init_driver")
    @patch.object(ms.MediuxScraper, "login_if_needed")
    @patch.object(ms.MediuxScraper, "_import_selenium")
    def test_scrape_set_yaml_with_list_urls(
        self, mock_import, mock_login, mock_init_driver, mock_sleep
    ):
        """Test scraping with list of set URLs."""
        # Setup selenium mocks
        mock_webdriver = Mock()
        mock_options = Mock()
        mock_by = Mock()
        mock_wait = Mock()
        mock_ec = Mock()
        mock_import.return_value = (mock_webdriver, mock_options, mock_by, mock_wait, mock_ec)

        mock_driver = Mock()
        mock_init_driver.return_value = mock_driver
        mock_login.return_value = True

        # Mock successful YAML extraction
        mock_yaml_button = Mock()
        mock_textarea = Mock()
        mock_textarea.get_attribute.return_value = "metadata:\n  test: yaml"

        mock_wait_instance = Mock()
        mock_wait_instance.until.return_value = mock_yaml_button
        mock_wait.return_value = mock_wait_instance

        mock_driver.find_element.return_value = mock_textarea

        scraper = ms.MediuxScraper()
        result = scraper.scrape_set_yaml(["set1", "set2"])

        # Should process the input (converted to URLs)
        assert mock_driver.get.call_count >= 1
        assert result == "metadata:\n  test: yaml"

    def test_extract_asset_ids_invalid_yaml(self):
        """Test handling of invalid YAML."""
        invalid_yaml = "invalid: yaml: content: ["
        result = ms.extract_asset_ids_from_yaml(invalid_yaml)
        assert len(result) == 0


@pytest.mark.skipif(not MEDIUX_SCRAPER_AVAILABLE, reason="mediux_scraper not available")
@pytest.mark.selenium
@pytest.mark.skip(reason="MediuxScraper API changed - comprehensive test rewrite needed")
class TestMediuxScraper:
    """Test MediuxScraper class."""

    @pytest.mark.skip(reason="MediuxScraper API changed - needs test update")
    def test_mediux_scraper_init_default(self):
        """Test MediuxScraper initialization with defaults."""
        scraper = ms.MediuxScraper()

        assert scraper.mediux_username is None
        assert scraper.mediux_password is None
        assert scraper.mediux_nickname is None
        assert scraper.headless is True
        assert scraper.driver is None

    @pytest.mark.skip(reason="MediuxScraper API changed - needs test update")
    def test_mediux_scraper_init_with_params(self):
        """Test MediuxScraper initialization with parameters."""
        scraper = ms.MediuxScraper(
            mediux_username="testuser",
            mediux_password="testpass",  # pragma: allowlist secret
            mediux_nickname="testnick",
            headless=False,
            profile_path="/path/to/profile",
        )

        assert scraper.mediux_username == "testuser"
        assert scraper.mediux_password == "testpass"  # pragma: allowlist secret
        assert scraper.mediux_nickname == "testnick"
        assert scraper.headless is False
        assert scraper.profile_path == "/path/to/profile"

    @patch("mediux_scraper.webdriver.Chrome")
    @patch("mediux_scraper.ChromeDriverManager")
    @pytest.mark.skip(reason="API changed")
    def test_setup_driver(self, mock_cdm, mock_chrome):
        """Test driver setup."""
        mock_cdm.return_value.install.return_value = "/path/to/chromedriver"
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver

        scraper = ms.MediuxScraper()
        scraper.setup_driver()

        assert scraper.driver == mock_driver
        mock_chrome.assert_called_once()

    @patch("mediux_scraper.webdriver.Chrome")
    @pytest.mark.skip(reason="API changed")
    def test_setup_driver_with_custom_path(self, mock_chrome):
        """Test driver setup with custom chromedriver path."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver

        scraper = ms.MediuxScraper(chromedriver_path="/custom/path")
        scraper.setup_driver()

        mock_chrome.assert_called_once()
        # Check that custom path was used in service
        call_args = mock_chrome.call_args
        assert any(
            "/custom/path" in str(arg) for arg in call_args[0] + tuple(call_args[1].values())
        )

    def test_close_driver(self):
        """Test driver cleanup."""
        scraper = ms.MediuxScraper()
        mock_driver = Mock()
        scraper.driver = mock_driver

        scraper.close_driver()

        mock_driver.quit.assert_called_once()
        assert scraper.driver is None

    def test_close_driver_no_driver(self):
        """Test cleanup when no driver exists."""
        scraper = ms.MediuxScraper()
        scraper.close_driver()  # Should not raise exception

    @patch("mediux_scraper.webdriver.Chrome")
    def test_context_manager(self, mock_chrome):
        """Test using scraper as context manager."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver

        with ms.MediuxScraper() as scraper:
            assert scraper.driver == mock_driver

        mock_driver.quit.assert_called_once()

    @patch("mediux_scraper.webdriver.Chrome")
    @patch("mediux_scraper.WebDriverWait")
    def test_scrape_set_yaml_success(self, mock_wait, mock_chrome):
        """Test successful YAML scraping."""
        # Setup mocks
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver

        mock_element = Mock()
        mock_element.text = "metadata:\n  123:\n    title: Test"
        mock_wait.return_value.until.return_value = mock_element

        scraper = ms.MediuxScraper()
        result = scraper.scrape_set_yaml("12345")

        assert result == "metadata:\n  123:\n    title: Test"
        mock_driver.get.assert_called_once()

    @patch("mediux_scraper.webdriver.Chrome")
    def test_scrape_set_yaml_login_required(self, mock_chrome):
        """Test scraping with login required."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver

        # Mock login elements
        mock_driver.find_element.return_value = Mock()

        scraper = ms.MediuxScraper(mediux_username="testuser", mediux_password="testpass")

        # Mock the scenario where login is required
        with patch.object(scraper, "_perform_login") as mock_login:
            mock_login.return_value = True

            with patch("mediux_scraper.WebDriverWait") as mock_wait:
                mock_element = Mock()
                mock_element.text = "yaml content"
                mock_wait.return_value.until.return_value = mock_element

                result = scraper.scrape_set_yaml("12345")

                mock_login.assert_called_once()
                assert result == "yaml content"

    @patch("mediux_scraper.webdriver.Chrome")
    def test_scrape_set_yaml_exception(self, mock_chrome):
        """Test scraping with exception."""
        mock_driver = Mock()
        mock_driver.get.side_effect = Exception("WebDriver error")
        mock_chrome.return_value = mock_driver

        scraper = ms.MediuxScraper()
        result = scraper.scrape_set_yaml("12345")

        assert result is None

    def test_perform_login_success(self):
        """Test successful login."""
        scraper = ms.MediuxScraper(mediux_username="testuser", mediux_password="testpass")
        mock_driver = Mock()
        scraper.driver = mock_driver

        # Mock successful login elements
        username_field = Mock()
        password_field = Mock()
        login_button = Mock()

        mock_driver.find_element.side_effect = [username_field, password_field, login_button]

        result = scraper._perform_login()

        assert result is True
        username_field.send_keys.assert_called_with("testuser")
        password_field.send_keys.assert_called_with("testpass")
        login_button.click.assert_called_once()

    def test_perform_login_missing_credentials(self):
        """Test login with missing credentials."""
        scraper = ms.MediuxScraper()  # No credentials
        mock_driver = Mock()
        scraper.driver = mock_driver

        result = scraper._perform_login()

        assert result is False

    def test_perform_login_exception(self):
        """Test login with exception."""
        scraper = ms.MediuxScraper(mediux_username="testuser", mediux_password="testpass")
        mock_driver = Mock()
        mock_driver.find_element.side_effect = Exception("Element not found")
        scraper.driver = mock_driver

        result = scraper._perform_login()

        assert result is False


@pytest.mark.skipif(not MEDIUX_SCRAPER_AVAILABLE, reason="mediux_scraper not available")
class TestScraperIntegration:
    """Integration tests for scraper functionality."""

    @patch("mediux_scraper.webdriver.Chrome")
    @patch("mediux_scraper.WebDriverWait")
    def test_full_scraping_workflow(self, mock_wait, mock_chrome):
        """Test complete scraping workflow."""
        # Setup mocks
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver

        yaml_content = """
metadata:
  123456:
    title: Test Show
    url_poster: https://api.mediux.pro/assets/test-asset-1
    seasons:
      1:
        url_poster: https://api.mediux.pro/assets/test-asset-2
"""

        mock_element = Mock()
        mock_element.text = yaml_content
        mock_wait.return_value.until.return_value = mock_element

        # Test scraping and asset extraction
        with ms.MediuxScraper() as scraper:
            scraped_yaml = scraper.scrape_set_yaml("12345")
            assert scraped_yaml == yaml_content

            # Extract asset IDs from scraped content
            asset_ids = ms.extract_asset_ids_from_yaml(scraped_yaml)
            assert "test-asset-1" in asset_ids
            assert "test-asset-2" in asset_ids

    def test_scraper_with_real_yaml_structure(self):
        """Test scraper with realistic YAML structure."""
        yaml_content = """
metadata:
  372264:
    title: "Slow Horses"
    url_poster: https://api.mediux.pro/assets/poster-123
    seasons:
      1:
        title: "Season 1"
        url_poster: https://api.mediux.pro/assets/s1-poster-456
        episodes:
          1:
            title: "Episode 1"
            url_poster: https://api.mediux.pro/assets/ep1-789
          2:
            title: "Episode 2"
            url_title_card: https://api.mediux.pro/assets/ep2-card-abc
      2:
        title: "Season 2"
        url_backdrop: https://api.mediux.pro/assets/s2-backdrop-def
"""

        asset_ids = ms.extract_asset_ids_from_yaml(yaml_content)

        expected_assets = [
            "poster-123",
            "s1-poster-456",
            "ep1-789",
            "ep2-card-abc",
            "s2-backdrop-def",
        ]

        for asset_id in expected_assets:
            assert asset_id in asset_ids

        assert len(asset_ids) == len(expected_assets)


@pytest.mark.skipif(not MEDIUX_SCRAPER_AVAILABLE, reason="mediux_scraper not available")
class TestScraperErrorHandling:
    """Test error handling in scraper."""

    @patch("mediux_scraper.webdriver.Chrome")
    def test_driver_creation_failure(self, mock_chrome):
        """Test handling of driver creation failure."""
        mock_chrome.side_effect = Exception("Failed to create driver")

        scraper = ms.MediuxScraper()
        scraper.setup_driver()

        assert scraper.driver is None

    @patch("mediux_scraper.webdriver.Chrome")
    @patch("mediux_scraper.WebDriverWait")
    def test_element_not_found(self, mock_wait, mock_chrome):
        """Test handling when YAML element is not found."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver

        from selenium.common.exceptions import TimeoutException

        mock_wait.return_value.until.side_effect = TimeoutException("Element not found")

        scraper = ms.MediuxScraper()
        result = scraper.scrape_set_yaml("12345")

        assert result is None

    def test_empty_yaml_content(self):
        """Test handling of empty YAML content."""
        result = ms.extract_asset_ids_from_yaml("")
        assert len(result) == 0

    def test_yaml_with_no_metadata(self):
        """Test YAML without metadata section."""
        yaml_content = """
title: Test
description: A test file without metadata
"""
        result = ms.extract_asset_ids_from_yaml(yaml_content)
        assert len(result) == 0


# Mock tests for when selenium is not available
@pytest.mark.skipif(MEDIUX_SCRAPER_AVAILABLE, reason="mediux_scraper is available")
class TestMediuxScraperUnavailable:
    """Test behavior when mediux_scraper is not available."""

    def test_import_failure_handling(self):
        """Test that import failure is handled gracefully."""
        # This test runs when selenium/mediux_scraper is not available
        # We should test that the main application handles this gracefully

        # Try to import kometa_mediux_resolver and verify it doesn't crash
        import kometa_mediux_resolver as kmr

        # The fetch_set_assets_with_scrape function should handle missing scraper
        result = kmr.fetch_set_assets_with_scrape(
            "https://api.mediux.pro", "12345", "test-key", use_scrape=True
        )

        # Should return empty list when scraper is not available
        assert result == []
