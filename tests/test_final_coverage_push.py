"""Final push for 93% coverage - working tests targeting highest impact areas."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Import the modules to test
import kometa_mediux_resolver as kmr
import mediux_scraper as ms


class TestWorkingHighImpactCoverage:
    """Working tests targeting the highest impact coverage gaps."""

    def test_touch_activity_correct_usage(self):
        """Test touch_activity with correct parameters."""
        # touch_activity expects a count increment (int)
        kmr.touch_activity(1)
        count, timestamp = kmr.get_activity_snapshot()
        # Count should have incremented
        assert count >= 1
        assert timestamp > 0

    def test_construct_asset_url_working(self):
        """Test construct_asset_url correctly."""
        # The function expects api_base to be a string, not a dict
        api_base = "https://api.test.com"
        asset_id = "test-asset-123"

        url = kmr.construct_asset_url(api_base, asset_id)
        assert url == "https://api.test.com/assets/test-asset-123"

    def test_get_recently_aired_from_sonarr_correct_params(self):
        """Test Sonarr function with correct parameters."""
        sonarr_url = "http://localhost:8989"
        api_key = "test_api_key"

        with patch("kometa_mediux_resolver.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = []
            mock_get.return_value = mock_response

            result = kmr.get_recently_aired_from_sonarr(sonarr_url, api_key, days=7)
            assert isinstance(result, list)

    def test_fetch_set_assets_response_text_handling(self):
        """Test fetch_set_assets response text handling to cover missing lines."""
        with patch("kometa_mediux_resolver.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.text = "This is a very long error response that should be truncated" * 50
            mock_response.raise_for_status.side_effect = Exception("HTTP Error")
            mock_get.return_value = mock_response

            result = kmr.fetch_set_assets("test_set", "https://api.test.com")
            assert result == []

    def test_apply_changes_working_signature(self):
        """Test apply_changes with working parameters."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as temp_file:
            temp_file.write("metadata:\n  test: value")
            temp_file_path = temp_file.name

        changes = [
            {
                "file": temp_file_path,
                "changes": [{"path": ["metadata", "test"], "add": {"new_key": "new_value"}}],
            }
        ]

        try:
            result = kmr.apply_changes(changes, apply=True)
            # Check that the function executed without error
            assert result is not None
        finally:
            Path(temp_file_path).unlink()

    def test_mediux_scraper_more_line_coverage(self):
        """Test mediux scraper to get more line coverage."""
        scraper = ms.MediuxScraper()

        # Test the fallback text extraction logic
        mock_driver = Mock()
        mock_yaml_button = Mock()

        mock_wait = Mock()
        mock_wait.return_value.until.return_value = mock_yaml_button

        # Make find_element fail for textarea and pre
        mock_driver.find_element.side_effect = Exception("Not found")

        # But succeed for find_elements (text nodes)
        mock_element1 = Mock()
        mock_element1.get_attribute.return_value = "Short text"  # Too short
        mock_element2 = Mock()
        mock_element2.text = (
            "This is a much longer text block that should be included in the scraping result because it meets the minimum length requirement"
            * 3
        )
        mock_driver.find_elements.return_value = [mock_element1, mock_element2]

        with patch.object(scraper, "_import_selenium") as mock_import:
            mock_import.return_value = (Mock(), Mock(), Mock(), mock_wait, Mock())
            with patch.object(scraper, "_init_driver", return_value=mock_driver):
                with patch.object(scraper, "login_if_needed", return_value=True):
                    with patch("mediux_scraper.time.sleep"):
                        result = scraper.scrape_set_yaml("https://mediux.pro/sets/123")

        # Should contain the longer text
        assert "longer text block" in result

    def test_extract_asset_ids_comprehensive_regex_coverage(self):
        """Test all regex branches in extract_asset_ids_from_yaml."""

        # Test case 1: Full object with id and fileType (first regex)
        yaml1 = """
        {
            "some_object": {
                "id": "11111111-1111-1111-1111-111111111111",
                "other_field": "value",
                "fileType": "poster"
            }
        }
        """
        result1 = ms.extract_asset_ids_from_yaml(yaml1)
        assert len(result1) > 0
        assert any(item["id"] == "11111111-1111-1111-1111-111111111111" for item in result1)

        # Test case 2: ID-only pattern (second regex)
        yaml2 = """
        {
            "metadata": {
                "id": "22222222-2222-2222-2222-222222222222"
            }
        }
        """
        result2 = ms.extract_asset_ids_from_yaml(yaml2)
        assert len(result2) > 0
        assert any(item["id"] == "22222222-2222-2222-2222-222222222222" for item in result2)

        # Test case 3: Just UUIDs in text (third regex)
        yaml3 = "Just some text with a UUID 33333333-3333-3333-3333-333333333333 here"
        result3 = ms.extract_asset_ids_from_yaml(yaml3)
        assert len(result3) > 0
        assert any(item["id"] == "33333333-3333-3333-3333-333333333333" for item in result3)

        # Test case 4: Empty/invalid input
        result4 = ms.extract_asset_ids_from_yaml("")
        assert result4 == []

        result5 = ms.extract_asset_ids_from_yaml("no uuids here")
        assert result5 == []

    def test_pick_best_asset_edge_cases(self):
        """Test pick_best_asset edge cases."""
        # Empty list
        result1 = kmr.pick_best_asset([])
        assert result1 == []

        # Single asset
        assets = [{"id": "asset1", "fileType": "poster", "fileSize": 1000}]
        result2 = kmr.pick_best_asset(assets)
        assert len(result2) > 0

        # Multiple assets with different types
        assets = [
            {"id": "asset1", "fileType": "poster", "fileSize": 1000},
            {"id": "asset2", "fileType": "backdrop", "fileSize": 2000},
            {"id": "asset3", "fileType": "unknown", "fileSize": 500},
        ]
        result3 = kmr.pick_best_asset(assets)
        assert len(result3) > 0

    def test_gather_yaml_metadata_paths_working(self):
        """Test gather_yaml_metadata_paths with nested dict."""
        # Test with actual dict content (not directory path!)
        test_data = {
            "metadata": {
                "123456": {
                    "title": "Test Show",
                    "url_poster": "https://mediux.pro/sets/12345",
                    "seasons": {"1": {"url_poster": "https://mediux.pro/sets/67890"}},
                }
            }
        }

        result = list(kmr.gather_yaml_metadata_paths(test_data))
        # Should return the root dict plus nested dicts
        assert len(result) > 0
        # First result should be root with empty prefix
        assert result[0] == ((), test_data)

    def test_probe_url_working(self):
        """Test probe_url function."""
        with patch("kometa_mediux_resolver.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "test body content"
            mock_get.return_value = mock_response

            result = kmr.probe_url("https://example.com/test")
            assert result["status"] == 200
            assert result["url"] == "https://example.com/test"
            assert "body" in result

            # Test failure case
            mock_response.status_code = 404
            mock_response.text = "not found"
            result = kmr.probe_url("https://example.com/notfound")
            assert result["status"] == 404

    def test_init_cache_working(self):
        """Test cache initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "test_cache.db"

            # Should not raise an exception
            kmr.init_cache(str(cache_path))
            assert cache_path.exists()

    def test_find_set_ids_in_text_comprehensive(self):
        """Test comprehensive set ID finding."""
        text1 = "Check out https://mediux.pro/sets/12345 for great content"
        result1 = kmr.find_set_ids_in_text(text1)
        assert "12345" in result1

        text2 = "Multiple sets: https://mediux.pro/sets/111 and https://mediux.pro/sets/222/"
        result2 = kmr.find_set_ids_in_text(text2)
        assert "111" in result2
        assert "222" in result2

        text3 = "No set URLs here"
        result3 = kmr.find_set_ids_in_text(text3)
        assert result3 == []

    def test_mediux_scraper_selenium_import_success(self):
        """Test successful selenium import with proper mocking."""
        scraper = ms.MediuxScraper()

        # Create properly structured mocks
        mock_webdriver = Mock()
        mock_options_class = Mock()
        mock_by = Mock()
        mock_wait_class = Mock()
        mock_ec = Mock()

        with patch.dict(
            "sys.modules",
            {
                "selenium": Mock(),
                "selenium.webdriver": mock_webdriver,
                "selenium.webdriver.chrome.options": Mock(Options=mock_options_class),
                "selenium.webdriver.common.by": Mock(By=mock_by),
                "selenium.webdriver.support.ui": Mock(WebDriverWait=mock_wait_class),
                "selenium.webdriver.support": Mock(expected_conditions=mock_ec),
            },
        ):
            result = scraper._import_selenium()

        assert len(result) == 5
        assert result[0] == mock_webdriver
        assert result[1] == mock_options_class
        assert result[2] == mock_by
        assert result[3] == mock_wait_class
        assert result[4] == mock_ec
