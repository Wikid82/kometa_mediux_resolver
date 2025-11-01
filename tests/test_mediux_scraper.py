"""Test the mediux_scraper module."""
from unittest.mock import Mock, patch

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
    """Test asset ID extraction from YAML content."""

    def test_extract_asset_ids_from_yaml_simple(self):
        """Test extracting asset IDs from simple YAML."""
        yaml_content = """
metadata:
  123456:
    url_poster: https://api.mediux.pro/assets/asset-123
    seasons:
      1:
        url_poster: https://api.mediux.pro/assets/asset-456
"""
        result = ms.extract_asset_ids_from_yaml(yaml_content)
        assert "asset-123" in result
        assert "asset-456" in result
        assert len(result) == 2

    def test_extract_asset_ids_from_yaml_no_assets(self):
        """Test YAML with no asset URLs."""
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
        """Test YAML with mixed URL types."""
        yaml_content = """
metadata:
  123456:
    url_poster: https://api.mediux.pro/assets/asset-123
    url_backdrop: https://example.com/backdrop.jpg
    seasons:
      1:
        url_poster: https://api.mediux.pro/assets/asset-456
        url_title_card: https://api.mediux.pro/assets/asset-789
"""
        result = ms.extract_asset_ids_from_yaml(yaml_content)
        assert "asset-123" in result
        assert "asset-456" in result
        assert "asset-789" in result
        assert len(result) == 3

    def test_extract_asset_ids_invalid_yaml(self):
        """Test handling of invalid YAML."""
        invalid_yaml = "invalid: yaml: content: ["
        result = ms.extract_asset_ids_from_yaml(invalid_yaml)
        assert len(result) == 0


@pytest.mark.skipif(not MEDIUX_SCRAPER_AVAILABLE, reason="mediux_scraper not available")
@pytest.mark.selenium
class TestMediuxScraper:
    """Test MediuxScraper class."""

    def test_mediux_scraper_init_default(self):
        """Test MediuxScraper initialization with defaults."""
        scraper = ms.MediuxScraper()

        assert scraper.mediux_username is None
        assert scraper.mediux_password is None
        assert scraper.mediux_nickname is None
        assert scraper.headless is True
        assert scraper.driver is None

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
