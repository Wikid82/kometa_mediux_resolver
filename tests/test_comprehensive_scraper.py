"""Test comprehensive mediux_scraper functionality."""
import re
from unittest.mock import Mock, patch

import pytest

# Import the module to test
import mediux_scraper as ms


class TestMediuxScraperInit:
    """Test MediuxScraper initialization."""

    def test_mediux_scraper_init(self):
        """Test basic initialization."""
        scraper = ms.MediuxScraper()
        assert scraper.logger is not None


class TestMediuxScraperImportSelenium:
    """Test selenium import functionality."""

    def test_import_selenium_success(self):
        """Test successful selenium import."""
        scraper = ms.MediuxScraper()

        # Mock successful selenium import
        mock_webdriver = Mock()
        mock_options = Mock()
        mock_by = Mock()
        mock_wait = Mock()
        mock_ec = Mock()

        with patch.dict(
            "sys.modules",
            {
                "selenium": Mock(),
                "selenium.webdriver": mock_webdriver,
                "selenium.webdriver.chrome.options": Mock(Options=mock_options),
                "selenium.webdriver.common.by": Mock(By=mock_by),
                "selenium.webdriver.support.ui": Mock(WebDriverWait=mock_wait),
                "selenium.webdriver.support": Mock(expected_conditions=mock_ec),
            },
        ):
            result = scraper._import_selenium()

        assert len(result) == 5
        assert result[0] == mock_webdriver

    def test_import_selenium_failure(self):
        """Test selenium import failure."""
        scraper = ms.MediuxScraper()

        with patch("builtins.__import__", side_effect=ImportError("selenium not found")):
            with pytest.raises(RuntimeError, match="selenium is required"):
                scraper._import_selenium()


class TestMediuxScraperInitDriver:
    """Test driver initialization."""

    def test_init_driver_basic(self):
        """Test basic driver initialization."""
        scraper = ms.MediuxScraper()

        mock_webdriver = Mock()
        mock_options = Mock()
        mock_driver = Mock()
        mock_webdriver.Chrome.return_value = mock_driver

        with patch.object(scraper, "_import_selenium") as mock_import:
            mock_import.return_value = (mock_webdriver, mock_options, Mock(), Mock(), Mock())

            result = scraper._init_driver()

        assert result == mock_driver
        mock_driver.set_page_load_timeout.assert_called_once_with(60)
        mock_driver.implicitly_wait.assert_called_once_with(3)

    def test_init_driver_with_options(self):
        """Test driver initialization with options."""
        scraper = ms.MediuxScraper()

        mock_webdriver = Mock()
        mock_options = Mock()
        mock_options_instance = Mock()
        mock_options.return_value = mock_options_instance
        mock_driver = Mock()
        mock_webdriver.Chrome.return_value = mock_driver

        with patch.object(scraper, "_import_selenium") as mock_import:
            mock_import.return_value = (mock_webdriver, mock_options, Mock(), Mock(), Mock())

            result = scraper._init_driver(
                headless=False,
                profile_path="/path/to/profile",
                chromedriver_path="/path/to/chromedriver",
            )

        # Verify options were set
        mock_options_instance.add_argument.assert_any_call("--no-sandbox")
        mock_options_instance.add_argument.assert_any_call("--disable-dev-shm-usage")
        mock_options_instance.add_argument.assert_any_call("--user-data-dir=/path/to/profile")
        mock_options_instance.add_argument.assert_any_call("--disable-gpu")

        # Verify chromedriver path was used
        mock_webdriver.Chrome.assert_called_with(
            executable_path="/path/to/chromedriver", options=mock_options_instance
        )

    def test_init_driver_headless(self):
        """Test driver initialization in headless mode."""
        scraper = ms.MediuxScraper()

        mock_webdriver = Mock()
        mock_options = Mock()
        mock_options_instance = Mock()
        mock_options.return_value = mock_options_instance
        mock_driver = Mock()
        mock_webdriver.Chrome.return_value = mock_driver

        with patch.object(scraper, "_import_selenium") as mock_import:
            mock_import.return_value = (mock_webdriver, mock_options, Mock(), Mock(), Mock())

            scraper._init_driver(headless=True)

        mock_options_instance.add_argument.assert_any_call("--headless=new")


class TestMediuxScraperLogin:
    """Test login functionality."""

    def test_login_if_needed_already_logged_in(self):
        """Test when user is already logged in."""
        scraper = ms.MediuxScraper()
        mock_driver = Mock()
        mock_by = Mock()
        mock_element = Mock()
        mock_driver.find_elements.return_value = [mock_element]

        with patch.object(scraper, "_import_selenium") as mock_import:
            mock_import.return_value = (Mock(), Mock(), mock_by, Mock(), Mock())

            result = scraper.login_if_needed(mock_driver, "user", "pass", "nickname")

        assert result is True

    def test_login_if_needed_no_credentials(self):
        """Test when no credentials provided."""
        scraper = ms.MediuxScraper()
        mock_driver = Mock()
        mock_driver.find_elements.return_value = []  # No user button found

        with patch.object(scraper, "_import_selenium") as mock_import:
            mock_import.return_value = (Mock(), Mock(), Mock(), Mock(), Mock())

            result = scraper.login_if_needed(mock_driver, None, None, "nickname")

        assert result is False

    def test_login_if_needed_no_sign_in_button(self):
        """Test when sign-in button not found."""
        scraper = ms.MediuxScraper()
        mock_driver = Mock()
        mock_driver.find_elements.side_effect = [[], []]  # No user button, no sign-in button

        with patch.object(scraper, "_import_selenium") as mock_import:
            mock_import.return_value = (Mock(), Mock(), Mock(), Mock(), Mock())

            result = scraper.login_if_needed(mock_driver, "user", "pass", "nickname")

        assert result is False

    def test_login_if_needed_successful_login(self):
        """Test successful login process."""
        scraper = ms.MediuxScraper()
        mock_driver = Mock()

        # Mock elements
        mock_sign_button = Mock()
        mock_email_input = Mock()
        mock_pass_input = Mock()
        mock_submit_button = Mock()
        mock_user_button = Mock()

        # Setup find_elements responses
        find_elements_responses = [
            [],  # No user button initially
            [mock_sign_button],  # Sign-in button found
            [mock_email_input],  # Email input found
            [mock_pass_input],  # Password input found
            [mock_submit_button],  # Submit button found
        ]
        mock_driver.find_elements.side_effect = find_elements_responses
        mock_driver.find_element.return_value = mock_user_button

        with patch.object(scraper, "_import_selenium") as mock_import:
            mock_import.return_value = (Mock(), Mock(), Mock(), Mock(), Mock())
            with patch("mediux_scraper.time.sleep"):  # Speed up test
                result = scraper.login_if_needed(mock_driver, "user", "pass", "nickname")

        assert result is True
        mock_sign_button.click.assert_called_once()
        mock_email_input.clear.assert_called_once()
        mock_email_input.send_keys.assert_called_once_with("user")
        mock_pass_input.clear.assert_called_once()
        mock_pass_input.send_keys.assert_called_once_with("pass")
        mock_submit_button.click.assert_called_once()

    def test_login_if_needed_login_exception(self):
        """Test login process with exception."""
        scraper = ms.MediuxScraper()
        mock_driver = Mock()
        mock_driver.find_elements.side_effect = Exception("Element not found")

        with patch.object(scraper, "_import_selenium") as mock_import:
            mock_import.return_value = (Mock(), Mock(), Mock(), Mock(), Mock())

            result = scraper.login_if_needed(mock_driver, "user", "pass", "nickname")

        assert result is False


class TestMediuxScraperScrapeSetYaml:
    """Test main scraping functionality."""

    def test_scrape_set_yaml_success_textarea(self):
        """Test successful YAML scraping from textarea."""
        scraper = ms.MediuxScraper()

        mock_driver = Mock()
        mock_yaml_button = Mock()
        mock_textarea = Mock()
        mock_textarea.get_attribute.return_value = "metadata:\n  test: value"

        mock_wait = Mock()
        mock_wait.return_value.until.return_value = mock_yaml_button
        mock_driver.find_element.return_value = mock_textarea

        with patch.object(scraper, "_import_selenium") as mock_import:
            mock_import.return_value = (Mock(), Mock(), Mock(), mock_wait, Mock())
            with patch.object(scraper, "_init_driver", return_value=mock_driver):
                with patch.object(scraper, "login_if_needed", return_value=True):
                    with patch("mediux_scraper.time.sleep"):
                        result = scraper.scrape_set_yaml("https://mediux.pro/sets/123")

        assert result == "metadata:\n  test: value"
        mock_driver.quit.assert_called_once()

    def test_scrape_set_yaml_success_pre_element(self):
        """Test successful YAML scraping from pre element."""
        scraper = ms.MediuxScraper()

        mock_driver = Mock()
        mock_yaml_button = Mock()
        mock_pre = Mock()
        mock_pre.text = "metadata:\n  test: value"

        mock_wait = Mock()
        mock_wait.return_value.until.return_value = mock_yaml_button

        # Mock find_element to fail for textarea but succeed for pre
        def mock_find_element(by, xpath):
            if "textarea" in xpath:
                raise Exception("No textarea")
            elif "pre" in xpath:
                return mock_pre
            raise Exception("Element not found")

        mock_driver.find_element.side_effect = mock_find_element

        with patch.object(scraper, "_import_selenium") as mock_import:
            mock_import.return_value = (Mock(), Mock(), Mock(), mock_wait, Mock())
            with patch.object(scraper, "_init_driver", return_value=mock_driver):
                with patch.object(scraper, "login_if_needed", return_value=True):
                    with patch("mediux_scraper.time.sleep"):
                        result = scraper.scrape_set_yaml("https://mediux.pro/sets/123")

        assert result == "metadata:\n  test: value"

    def test_scrape_set_yaml_fallback_to_large_text_nodes(self):
        """Test fallback to collecting large text nodes."""
        scraper = ms.MediuxScraper()

        mock_driver = Mock()
        mock_yaml_button = Mock()

        mock_wait = Mock()
        mock_wait.return_value.until.return_value = mock_yaml_button

        # Mock find_element to fail for textarea and pre
        mock_driver.find_element.side_effect = Exception("No textarea or pre")

        # Mock find_elements for large text nodes
        mock_element1 = Mock()
        mock_element1.get_attribute.return_value = "Large text content with metadata: info"
        mock_element2 = Mock()
        mock_element2.text = "Another large text block"
        mock_driver.find_elements.return_value = [mock_element1, mock_element2]

        with patch.object(scraper, "_import_selenium") as mock_import:
            mock_import.return_value = (Mock(), Mock(), Mock(), mock_wait, Mock())
            with patch.object(scraper, "_init_driver", return_value=mock_driver):
                with patch.object(scraper, "login_if_needed", return_value=True):
                    with patch("mediux_scraper.time.sleep"):
                        result = scraper.scrape_set_yaml("https://mediux.pro/sets/123")

        assert "Large text content" in result
        assert "Another large text block" in result

    def test_scrape_set_yaml_no_yaml_button(self):
        """Test when YAML button is not found."""
        scraper = ms.MediuxScraper()

        mock_driver = Mock()
        mock_wait = Mock()
        mock_wait.return_value.until.side_effect = Exception("Button not found")

        with patch.object(scraper, "_import_selenium") as mock_import:
            mock_import.return_value = (Mock(), Mock(), Mock(), mock_wait, Mock())
            with patch.object(scraper, "_init_driver", return_value=mock_driver):
                with patch.object(scraper, "login_if_needed", return_value=True):
                    result = scraper.scrape_set_yaml("https://mediux.pro/sets/123")

        assert result == ""
        mock_driver.quit.assert_called_once()

    def test_scrape_set_yaml_click_button_fails(self):
        """Test when clicking YAML button fails."""
        scraper = ms.MediuxScraper()

        mock_driver = Mock()
        mock_yaml_button = Mock()
        mock_yaml_button.click.side_effect = Exception("Click failed")

        mock_wait = Mock()
        mock_wait.return_value.until.return_value = mock_yaml_button

        # No elements found after failed click
        mock_driver.find_element.side_effect = Exception("No content")
        mock_driver.find_elements.return_value = []

        with patch.object(scraper, "_import_selenium") as mock_import:
            mock_import.return_value = (Mock(), Mock(), Mock(), mock_wait, Mock())
            with patch.object(scraper, "_init_driver", return_value=mock_driver):
                with patch.object(scraper, "login_if_needed", return_value=True):
                    with patch("mediux_scraper.time.sleep"):
                        result = scraper.scrape_set_yaml("https://mediux.pro/sets/123")

        assert result == ""

    def test_scrape_set_yaml_driver_exception_cleanup(self):
        """Test that driver is properly cleaned up on exception."""
        scraper = ms.MediuxScraper()

        mock_driver = Mock()

        with patch.object(scraper, "_import_selenium") as mock_import:
            mock_import.return_value = (Mock(), Mock(), Mock(), Mock(), Mock())
            with patch.object(scraper, "_init_driver", return_value=mock_driver):
                with patch.object(
                    scraper, "login_if_needed", side_effect=Exception("Login failed")
                ):
                    result = scraper.scrape_set_yaml("https://mediux.pro/sets/123")

        assert result == ""
        mock_driver.quit.assert_called_once()

    def test_scrape_set_yaml_quit_exception(self):
        """Test that quit exceptions are handled gracefully."""
        scraper = ms.MediuxScraper()

        mock_driver = Mock()
        mock_driver.quit.side_effect = Exception("Quit failed")

        with patch.object(scraper, "_import_selenium") as mock_import:
            mock_import.return_value = (Mock(), Mock(), Mock(), Mock(), Mock())
            with patch.object(scraper, "_init_driver", return_value=mock_driver):
                with patch.object(
                    scraper, "login_if_needed", side_effect=Exception("Login failed")
                ):
                    # Should not raise exception despite quit failure
                    result = scraper.scrape_set_yaml("https://mediux.pro/sets/123")

        assert result == ""


class TestExtractAssetIdsFromYaml:
    """Test asset ID extraction from YAML/JSON content."""

    def test_extract_asset_ids_with_file_type(self):
        """Test extracting assets with both id and fileType."""
        yaml_text = """
        {
            "assets": [
                {"id": "12345678-1234-1234-1234-123456789abc", "fileType": "poster"},
                {"id": "87654321-4321-4321-4321-210987654321", "fileType": "backdrop"}
            ]
        }
        """
        result = ms.extract_asset_ids_from_yaml(yaml_text)

        assert len(result) == 2
        assert {"id": "12345678-1234-1234-1234-123456789abc", "fileType": "poster"} in result
        assert {"id": "87654321-4321-4321-4321-210987654321", "fileType": "backdrop"} in result

    def test_extract_asset_ids_id_only_fallback(self):
        """Test fallback to id-only pattern when no fileType found."""
        yaml_text = """
        {
            "data": {
                "id": "12345678-1234-1234-1234-123456789abc",
                "name": "test asset"
            }
        }
        """
        result = ms.extract_asset_ids_from_yaml(yaml_text)

        assert len(result) == 1
        assert {"id": "12345678-1234-1234-1234-123456789abc", "fileType": "unknown"} in result

    def test_extract_asset_ids_uuid_only_fallback(self):
        """Test final fallback to any UUID-like tokens."""
        yaml_text = """
        Some text with a UUID: 12345678-1234-1234-1234-123456789abc
        And another one: 87654321-4321-4321-4321-210987654321
        """
        result = ms.extract_asset_ids_from_yaml(yaml_text)

        assert len(result) == 2
        assert {"id": "12345678-1234-1234-1234-123456789abc", "fileType": "unknown"} in result
        assert {"id": "87654321-4321-4321-4321-210987654321", "fileType": "unknown"} in result

    def test_extract_asset_ids_no_duplicates(self):
        """Test that duplicate IDs are not returned."""
        yaml_text = """
        {
            "assets": [
                {"id": "12345678-1234-1234-1234-123456789abc", "fileType": "poster"},
                {"id": "12345678-1234-1234-1234-123456789abc", "fileType": "backdrop"}
            ]
        }
        """
        result = ms.extract_asset_ids_from_yaml(yaml_text)

        assert len(result) == 1
        assert result[0]["id"] == "12345678-1234-1234-1234-123456789abc"

    def test_extract_asset_ids_empty_input(self):
        """Test with empty or invalid input."""
        assert ms.extract_asset_ids_from_yaml("") == []
        assert ms.extract_asset_ids_from_yaml("No UUIDs here") == []
        assert ms.extract_asset_ids_from_yaml("invalid-uuid-format") == []

    def test_extract_asset_ids_mixed_patterns(self):
        """Test with mixed patterns in complex JSON."""
        yaml_text = """
        {
            "data": {
                "assets": [
                    {"id": "11111111-1111-1111-1111-111111111111", "fileType": "poster"}
                ],
                "metadata": {
                    "id": "22222222-2222-2222-2222-222222222222"
                }
            },
            "description": "Contains UUID: 33333333-3333-3333-3333-333333333333"
        }
        """
        result = ms.extract_asset_ids_from_yaml(yaml_text)

        # Should find the first one with fileType
        assert len(result) == 1
        assert {"id": "11111111-1111-1111-1111-111111111111", "fileType": "poster"} in result

    def test_extract_asset_ids_complex_object_structure(self):
        """Test extraction from complex nested object structure."""
        yaml_text = """
        {
            "nested": {
                "deep": {
                    "object": {
                        "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
                        "other": "data",
                        "fileType": "title_card"
                    }
                }
            }
        }
        """
        result = ms.extract_asset_ids_from_yaml(yaml_text)

        assert len(result) == 1
        assert {"id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", "fileType": "title_card"} in result

    def test_extract_asset_ids_regex_patterns(self):
        """Test that regex patterns work correctly."""
        # Test the compiled regex patterns directly
        obj_re = re.compile(
            r'\{[^}]{0,400}?"id"\s*:\s*"([0-9a-fA-F-]{36})"[^}]{0,200}?"fileType"\s*:\s*"([a-zA-Z0-9_-]+)"',
            re.DOTALL,
        )

        test_text = '{"id": "12345678-1234-1234-1234-123456789abc", "fileType": "poster"}'
        match = obj_re.search(test_text)
        assert match is not None
        assert match.group(1) == "12345678-1234-1234-1234-123456789abc"
        assert match.group(2) == "poster"

    def test_extract_asset_ids_case_sensitivity(self):
        """Test case sensitivity in extraction."""
        yaml_text = """
        {
            "ID": "12345678-1234-1234-1234-123456789abc",
            "FILETYPE": "poster"
        }
        """
        result = ms.extract_asset_ids_from_yaml(yaml_text)

        # Should not match because patterns are case-sensitive
        assert len(result) == 1  # Should fall back to UUID pattern
        assert result[0]["fileType"] == "unknown"
