"""Test fetch functions and API interactions."""
import json
import re
from unittest.mock import Mock, patch

import pytest
import requests

import kometa_mediux_resolver as kmr


class TestFetchSetAssets:
    """Test fetch_set_assets function with various API responses."""

    @patch("kometa_mediux_resolver.requests.get")
    def test_fetch_set_assets_success_with_assets_key(self, mock_get):
        """Test successful fetch with 'assets' key response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "assets": [
                {"id": "asset-123", "name": "poster.jpg", "type": "poster"},
                {"uuid": "asset-456", "filename": "backdrop.jpg", "asset_type": "backdrop"},
            ]
        }
        mock_get.return_value = mock_response

        result = kmr.fetch_set_assets("https://api.example.com", "set123", "key123")

        assert len(result) == 2
        assert result[0]["id"] == "asset-123"
        assert result[0]["name"] == "poster.jpg"
        assert result[0]["type"] == "poster"
        assert result[1]["id"] == "asset-456"
        assert result[1]["name"] == "backdrop.jpg"
        assert result[1]["type"] == "backdrop"

    @patch("kometa_mediux_resolver.requests.get")
    def test_fetch_set_assets_with_data_assets_key(self, mock_get):
        """Test successful fetch with nested 'data.assets' structure."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "assets": [{"asset_id": "asset-789", "title": "season1.jpg", "type": "title_card"}]
            }
        }
        mock_get.return_value = mock_response

        result = kmr.fetch_set_assets("https://api.example.com", "set123", "key123")

        assert len(result) == 1
        assert result[0]["id"] == "asset-789"
        assert result[0]["name"] == "season1.jpg"
        assert result[0]["type"] == "title_card"

    @patch("kometa_mediux_resolver.requests.get")
    def test_fetch_set_assets_with_data_list(self, mock_get):
        """Test successful fetch with data as direct list."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"id": "asset-999", "name": "logo.png"}]}
        mock_get.return_value = mock_response

        result = kmr.fetch_set_assets("https://api.example.com", "set123", "key123")

        assert len(result) == 1
        assert result[0]["id"] == "asset-999"
        assert result[0]["name"] == "logo.png"

    @patch("kometa_mediux_resolver.requests.get")
    def test_fetch_set_assets_direct_list(self, mock_get):
        """Test successful fetch with response as direct list."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "asset-abc", "name": "banner.jpg", "type": "banner"}
        ]
        mock_get.return_value = mock_response

        result = kmr.fetch_set_assets("https://api.example.com", "set123", "key123")

        assert len(result) == 1
        assert result[0]["id"] == "asset-abc"

    @patch("kometa_mediux_resolver.requests.get")
    def test_fetch_set_assets_no_id_but_uuid_in_values(self, mock_get):
        """Test asset ID extraction from nested values when main ID fields missing."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "assets": [
                {"name": "test.jpg", "metadata": {"uuid": "12345678-1234-1234-1234-123456789abc"}}
            ]
        }
        mock_get.return_value = mock_response

        result = kmr.fetch_set_assets("https://api.example.com", "set123", "key123")

        assert len(result) == 1
        assert result[0]["id"] == "12345678-1234-1234-1234-123456789abc"

    @patch("kometa_mediux_resolver.requests.get")
    def test_fetch_set_assets_non_dict_asset_skipped(self, mock_get):
        """Test that non-dict assets are skipped."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "assets": ["invalid_asset_string", {"id": "valid-asset", "name": "valid.jpg"}, 123]
        }
        mock_get.return_value = mock_response

        result = kmr.fetch_set_assets("https://api.example.com", "set123", "key123")

        assert len(result) == 1
        assert result[0]["id"] == "valid-asset"

    @patch("kometa_mediux_resolver.requests.get")
    def test_fetch_set_assets_no_assets_found(self, mock_get):
        """Test when no assets are found in response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"other_data": "value"}
        mock_get.return_value = mock_response

        result = kmr.fetch_set_assets("https://api.example.com", "set123", "key123")

        assert result == []

    @patch("kometa_mediux_resolver.requests.get")
    def test_fetch_set_assets_http_error(self, mock_get):
        """Test fetch with HTTP error status."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        result = kmr.fetch_set_assets("https://api.example.com", "set123", "key123")

        assert result == []

    @patch("kometa_mediux_resolver.requests.get")
    def test_fetch_set_assets_json_decode_error(self, mock_get):
        """Test fetch with invalid JSON response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Invalid JSON response"
        mock_get.return_value = mock_response

        result = kmr.fetch_set_assets("https://api.example.com", "set123", "key123")

        assert result == []

    @patch("kometa_mediux_resolver.requests.get")
    def test_fetch_set_assets_connection_error(self, mock_get):
        """Test fetch with connection error."""
        mock_get.side_effect = requests.ConnectionError("Connection failed")

        result = kmr.fetch_set_assets("https://api.example.com", "set123", "key123")

        assert result == []

    @patch("kometa_mediux_resolver.requests.get")
    def test_fetch_set_assets_timeout_error(self, mock_get):
        """Test fetch with timeout error."""
        mock_get.side_effect = requests.Timeout("Request timed out")

        result = kmr.fetch_set_assets("https://api.example.com", "set123", "key123")

        assert result == []

    @patch("kometa_mediux_resolver.requests.get")
    def test_fetch_set_assets_with_api_key(self, mock_get):
        """Test fetch with API key header."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"assets": []}
        mock_get.return_value = mock_response

        kmr.fetch_set_assets("https://api.example.com", "set123", "key123")

        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]["headers"]["Authorization"] == "Bearer key123"

    @patch("kometa_mediux_resolver.requests.get")
    def test_fetch_set_assets_without_api_key(self, mock_get):
        """Test fetch without API key."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"assets": []}
        mock_get.return_value = mock_response

        kmr.fetch_set_assets("https://api.example.com", "set123", None)

        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "Authorization" not in call_args[1]["headers"]


class TestFetchSetAssetsWithScrape:
    """Test fetch_set_assets_with_scrape function."""

    @patch("kometa_mediux_resolver.fetch_set_assets")
    def test_fetch_with_scrape_api_success_no_scrape_needed(self, mock_fetch):
        """Test when API succeeds, no scraping needed."""
        mock_fetch.return_value = [{"id": "asset-123", "type": "poster"}]

        result = kmr.fetch_set_assets_with_scrape(
            "https://api.example.com", "set123", "key123", use_scrape=True
        )

        assert len(result) == 1
        assert result[0]["id"] == "asset-123"

    @patch("kometa_mediux_resolver.fetch_set_assets")
    def test_fetch_with_scrape_disabled(self, mock_fetch):
        """Test when API fails and scraping is disabled."""
        mock_fetch.return_value = []

        result = kmr.fetch_set_assets_with_scrape(
            "https://api.example.com", "set123", "key123", use_scrape=False
        )

        assert result == []

    @patch("kometa_mediux_resolver.fetch_set_assets")
    def test_fetch_with_scrape_import_failure_first_attempt(self, mock_fetch):
        """Test scraper import failure on first attempt."""
        mock_fetch.return_value = []

        # Mock the import to fail on first attempt
        with patch("kometa_mediux_resolver.Path") as mock_path:
            mock_path(__file__).resolve.return_value.parent = "/fake/path"
            with patch("builtins.__import__", side_effect=ImportError("No module")):
                result = kmr.fetch_set_assets_with_scrape(
                    "https://api.example.com", "set123", "key123", use_scrape=True
                )

        assert result == []

    @patch("kometa_mediux_resolver.fetch_set_assets")
    def test_fetch_with_scrape_scraper_exception(self, mock_fetch):
        """Test when scraper raises exception."""
        mock_fetch.return_value = []

        # Create a mock scraper that raises an exception
        mock_scraper_class = Mock()
        mock_scraper_instance = Mock()
        mock_scraper_instance.scrape_set_yaml.side_effect = Exception("Scraper failed")
        mock_scraper_class.return_value = mock_scraper_instance

        with patch.dict("sys.modules", {"mediux_scraper": Mock()}):
            with patch("kometa_mediux_resolver.MediuxScraper", mock_scraper_class):
                result = kmr.fetch_set_assets_with_scrape(
                    "https://api.example.com", "set123", "key123", use_scrape=True
                )

        assert result == []

    @patch("kometa_mediux_resolver.fetch_set_assets")
    def test_fetch_with_scrape_no_yaml_returned(self, mock_fetch):
        """Test when scraper returns no YAML."""
        mock_fetch.return_value = []

        # Create a mock scraper that returns empty string
        mock_scraper_class = Mock()
        mock_scraper_instance = Mock()
        mock_scraper_instance.scrape_set_yaml.return_value = ""
        mock_scraper_class.return_value = mock_scraper_instance

        with patch.dict("sys.modules", {"mediux_scraper": Mock()}):
            with patch("kometa_mediux_resolver.MediuxScraper", mock_scraper_class):
                result = kmr.fetch_set_assets_with_scrape(
                    "https://api.example.com", "set123", "key123", use_scrape=True
                )

        assert result == []

    @patch("kometa_mediux_resolver.fetch_set_assets")
    def test_fetch_with_scrape_success_with_dict_assets(self, mock_fetch):
        """Test successful scraping with dict-format assets."""
        mock_fetch.return_value = []

        # Create mocks for scraper
        mock_scraper_class = Mock()
        mock_scraper_instance = Mock()
        mock_scraper_instance.scrape_set_yaml.return_value = "yaml content"
        mock_scraper_class.return_value = mock_scraper_instance

        mock_extract = Mock()
        mock_extract.return_value = [
            {"id": "asset-123", "fileType": "poster"},
            {"id": "asset-456", "fileType": "backdrop"},
        ]

        with patch.dict("sys.modules", {"mediux_scraper": Mock()}):
            with patch("kometa_mediux_resolver.MediuxScraper", mock_scraper_class):
                with patch("kometa_mediux_resolver.extract_asset_ids_from_yaml", mock_extract):
                    result = kmr.fetch_set_assets_with_scrape(
                        "https://api.example.com", "set123", "key123", use_scrape=True
                    )

        assert len(result) == 2
        assert result[0]["id"] == "asset-123"
        assert result[0]["type"] == "poster"
        assert result[1]["id"] == "asset-456"
        assert result[1]["type"] == "backdrop"

    @patch("kometa_mediux_resolver.fetch_set_assets")
    def test_fetch_with_scrape_success_with_string_assets(self, mock_fetch):
        """Test successful scraping with string-format assets."""
        mock_fetch.return_value = []

        # Create mocks for scraper
        mock_scraper_class = Mock()
        mock_scraper_instance = Mock()
        mock_scraper_instance.scrape_set_yaml.return_value = "yaml content"
        mock_scraper_class.return_value = mock_scraper_instance

        mock_extract = Mock()
        mock_extract.return_value = ["asset-123", "asset-456"]

        with patch.dict("sys.modules", {"mediux_scraper": Mock()}):
            with patch("kometa_mediux_resolver.MediuxScraper", mock_scraper_class):
                with patch("kometa_mediux_resolver.extract_asset_ids_from_yaml", mock_extract):
                    result = kmr.fetch_set_assets_with_scrape(
                        "https://api.example.com", "set123", "key123", use_scrape=True
                    )

        assert len(result) == 2
        assert result[0]["id"] == "asset-123"
        assert result[0]["type"] is None
        assert result[1]["id"] == "asset-456"
        assert result[1]["type"] is None

    @patch("kometa_mediux_resolver.fetch_set_assets")
    def test_fetch_with_scrape_no_extracted_assets(self, mock_fetch):
        """Test when scraper returns YAML but no assets extracted."""
        mock_fetch.return_value = []

        # Create mocks for scraper
        mock_scraper_class = Mock()
        mock_scraper_instance = Mock()
        mock_scraper_instance.scrape_set_yaml.return_value = "yaml content"
        mock_scraper_class.return_value = mock_scraper_instance

        mock_extract = Mock()
        mock_extract.return_value = []

        with patch.dict("sys.modules", {"mediux_scraper": Mock()}):
            with patch("kometa_mediux_resolver.MediuxScraper", mock_scraper_class):
                with patch("kometa_mediux_resolver.extract_asset_ids_from_yaml", mock_extract):
                    result = kmr.fetch_set_assets_with_scrape(
                        "https://api.example.com", "set123", "key123", use_scrape=True
                    )

        assert result == []

    @patch("kometa_mediux_resolver.fetch_set_assets")
    def test_fetch_with_scrape_with_mediux_opts(self, mock_fetch):
        """Test scraping with mediux options."""
        mock_fetch.return_value = []

        mock_scraper_class = Mock()
        mock_scraper_instance = Mock()
        mock_scraper_instance.scrape_set_yaml.return_value = "yaml content"
        mock_scraper_class.return_value = mock_scraper_instance

        mock_extract = Mock()
        mock_extract.return_value = ["asset-123"]

        mediux_opts = {
            "username": "testuser",
            "password": "testpass",
            "nickname": "testnick",
            "headless": False,
            "profile_path": "/path/to/profile",
            "chromedriver_path": "/path/to/chromedriver",
        }

        with patch.dict("sys.modules", {"mediux_scraper": Mock()}):
            with patch("kometa_mediux_resolver.MediuxScraper", mock_scraper_class):
                with patch("kometa_mediux_resolver.extract_asset_ids_from_yaml", mock_extract):
                    result = kmr.fetch_set_assets_with_scrape(
                        "https://api.example.com",
                        "set123",
                        "key123",
                        use_scrape=True,
                        mediux_opts=mediux_opts,
                    )

        # Verify scraper was called with correct options
        mock_scraper_instance.scrape_set_yaml.assert_called_once()
        call_args = mock_scraper_instance.scrape_set_yaml.call_args[1]
        assert call_args["username"] == "testuser"
        assert call_args["password"] == "testpass"
        assert call_args["nickname"] == "testnick"
        assert call_args["headless"] is False
        assert call_args["profile_path"] == "/path/to/profile"
        assert call_args["chromedriver_path"] == "/path/to/chromedriver"
