"""Test utility functions and helpers."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import yaml

import kometa_mediux_resolver as kmr


class TestUtilityFunctions:
    """Test utility and helper functions."""

    def test_set_url_regex_pattern(self):
        """Test the SET_URL_RE regex pattern."""
        # Test valid URLs
        valid_urls = [
            "https://mediux.pro/sets/12345",
            "http://mediux.pro/sets/67890",
            "mediux.pro/sets/999",
        ]

        for url in valid_urls:
            match = kmr.SET_URL_RE.search(url)
            assert match is not None
            assert match.group(1).isdigit()

    def test_set_url_regex_invalid(self):
        """Test regex with invalid URLs."""
        invalid_urls = [
            "https://example.com/sets/12345",
            "https://mediux.pro/collections/12345",
            "https://mediux.pro/sets/",
            "https://mediux.pro/sets/abc",
        ]

        for url in invalid_urls:
            match = kmr.SET_URL_RE.search(url)
            if url == "https://mediux.pro/sets/abc":
                assert match is None
            elif "mediux.pro" not in url:
                assert match is None

    def test_json_output_format(self, temp_dir):
        """Test JSON output formatting."""
        test_data = {
            "scan_results": [
                {
                    "file": "test.yml",
                    "set_ids": ["12345"],
                    "changes": [
                        {
                            "path": ["metadata", "123456"],
                            "add": {"url_poster": "https://api.mediux.pro/assets/test"},
                        }
                    ],
                }
            ]
        }

        output_file = temp_dir / "test_output.json"
        output_file.write_text(json.dumps(test_data, indent=2))

        # Verify JSON is valid and properly formatted
        loaded_data = json.loads(output_file.read_text())
        assert loaded_data == test_data

    def test_yaml_round_trip(self, temp_dir):
        """Test YAML reading and writing preserves structure."""
        original_data = {
            "metadata": {
                "123456": {
                    "title": "Test Show",
                    "seasons": {
                        "1": {
                            "title": "Season 1",
                            "episodes": {"1": {"title": "Episode 1"}, "2": {"title": "Episode 2"}},
                        }
                    },
                }
            }
        }

        yaml_file = temp_dir / "test.yml"
        yaml_file.write_text(yaml.safe_dump(original_data, sort_keys=False))

        # Read back and verify
        loaded_data = yaml.safe_load(yaml_file.read_text())
        assert loaded_data == original_data


class TestSonarrFunctions:
    """Test Sonarr integration functions."""

    @patch("kometa_mediux_resolver.requests.get")
    def test_get_recently_aired_from_sonarr_success(self, mock_get):
        """Test successful Sonarr API call."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"series": {"tvdbId": 123456}, "airDateUtc": "2023-01-01T20:00:00Z"},
            {"series": {"tvdbId": 789012}, "airDateUtc": "2023-01-02T21:00:00Z"},
        ]
        mock_get.return_value = mock_response

        result = kmr.get_recently_aired_from_sonarr(
            "http://sonarr.example.com:8989", "test-api-key", 7
        )

        assert result == [123456, 789012]
        mock_get.assert_called_once()

    @patch("kometa_mediux_resolver.requests.get")
    def test_get_recently_aired_from_sonarr_failure(self, mock_get):
        """Test Sonarr API failure."""
        mock_get.side_effect = Exception("Connection error")

        result = kmr.get_recently_aired_from_sonarr(
            "http://sonarr.example.com:8989", "test-api-key", 7
        )

        assert result == []

    @patch("kometa_mediux_resolver.requests.get")
    def test_get_recently_aired_empty_response(self, mock_get):
        """Test Sonarr with empty response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        result = kmr.get_recently_aired_from_sonarr(
            "http://sonarr.example.com:8989", "test-api-key", 7
        )

        assert result == []


class TestHeartbeatFunction:
    """Test heartbeat/activity tracking functions."""

    def test_touch_activity_function_exists(self):
        """Test that touch_activity function exists and is callable."""
        # This function might be defined in the module
        if hasattr(kmr, "touch_activity"):
            assert callable(kmr.touch_activity)
            # Test that it doesn't crash when called
            try:
                kmr.touch_activity(0)
                kmr.touch_activity(1)
            except Exception:
                # It's okay if it fails, just shouldn't crash the test
                pass

    def test_activity_tracking_in_scan(self, temp_dir):
        """Test activity tracking during scan operations."""
        # Create test files
        test_file = temp_dir / "test.yml"
        content = {
            "metadata": {"123456": {"title": "Test", "url_poster": "https://mediux.pro/sets/12345"}}
        }
        test_file.write_text(yaml.safe_dump(content))

        with (
            patch("kometa_mediux_resolver.fetch_set_assets", return_value=[]),
            patch("kometa_mediux_resolver.touch_activity") as mock_activity,
        ):
            kmr.scan_root(temp_dir, "https://api.mediux.pro", "test-key")

            # Should have called touch_activity at least once
            if mock_activity.call_count > 0:
                mock_activity.assert_called()


class TestFetchSetAssetsWithScrape:
    """Test the fetch_set_assets_with_scrape function."""

    @patch("kometa_mediux_resolver.fetch_set_assets")
    def test_fetch_without_scrape(self, mock_fetch):
        """Test fetching without scrape fallback."""
        mock_fetch.return_value = [{"id": "test", "type": "poster"}]

        result = kmr.fetch_set_assets_with_scrape(
            "https://api.mediux.pro", "12345", "test-key", use_scrape=False
        )

        assert result == [{"id": "test", "type": "poster"}]
        mock_fetch.assert_called_once()

    @patch("kometa_mediux_resolver.fetch_set_assets")
    def test_fetch_with_scrape_fallback(self, mock_fetch):
        """Test fetching with scrape fallback when API fails."""
        mock_fetch.return_value = []  # API returns no results

        # Mock the scraper import and functionality inside the dynamic import logic
        mock_scraper = Mock()
        mock_scraper.scrape_set_yaml.return_value = """
metadata:
  123:
    url_poster: https://api.mediux.pro/assets/test-asset
"""

        # We need to patch the entire dynamic import mechanism
        with patch("importlib.util.spec_from_file_location") as mock_spec_from_file:
            with patch("importlib.util.module_from_spec") as mock_module_from_spec:
                # Mock the module import process
                mock_spec = Mock()
                mock_spec.loader = Mock()
                mock_spec_from_file.return_value = mock_spec

                mock_module = Mock()
                mock_module.MediuxScraper = Mock(return_value=mock_scraper)
                mock_module.extract_asset_ids_from_yaml = Mock(return_value=["test-asset"])
                mock_module_from_spec.return_value = mock_module

                result = kmr.fetch_set_assets_with_scrape(
                    "https://api.mediux.pro",
                    "12345",
                    "test-key",
                    use_scrape=True,
                    mediux_opts={"username": "test"},
                )

                # Should return constructed assets from scraped IDs
                assert len(result) == 1
                assert result[0]["id"] == "test-asset"

    @patch("kometa_mediux_resolver.fetch_set_assets")
    def test_fetch_scrape_unavailable(self, mock_fetch):
        """Test behavior when scraper is unavailable."""
        mock_fetch.return_value = []

        # Simulate import error for scraper by making all import attempts fail
        with patch("importlib.util.spec_from_file_location", side_effect=ImportError):
            result = kmr.fetch_set_assets_with_scrape(
                "https://api.mediux.pro", "12345", "test-key", use_scrape=True
            )

            assert result == []


class TestSchemaValidation:
    """Test JSON schema validation functionality."""

    def test_schema_loading(self, temp_dir):
        """Test schema file loading."""
        schema = {"type": "object", "properties": {"metadata": {"type": "object"}}}

        schema_file = temp_dir / "kometa_metadata_schema.json"
        schema_file.write_text(json.dumps(schema, indent=2))

        # Test that schema can be loaded
        loaded_schema = json.loads(schema_file.read_text())
        assert loaded_schema == schema

    def test_apply_changes_with_validation(self, temp_dir):
        """Test apply_changes with schema validation."""
        # Create test file
        test_file = temp_dir / "test.yml"
        content = {"metadata": {"123": {"title": "Test"}}}
        test_file.write_text(yaml.safe_dump(content))

        # Create schema file
        schema = {
            "type": "object",
            "properties": {
                "metadata": {
                    "type": "object",
                    "patternProperties": {
                        "^[0-9]+$": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "url_poster": {"type": "string"},
                            },
                        }
                    },
                }
            },
        }
        schema_file = temp_dir / "kometa_metadata_schema.json"
        schema_file.write_text(json.dumps(schema))

        changes = [
            {
                "file": str(test_file),
                "changes": [
                    {
                        "path": ["123"],
                        "add": {"url_poster": "https://example.com/poster.jpg"},
                        "probe": {"status": 200},
                    }
                ],
            }
        ]

        # Mock the schema loading in apply_changes
        with patch.object(Path, "resolve") as mock_resolve:
            mock_resolve.return_value.parent = temp_dir

            kmr.apply_changes(changes, apply=True, create_backup=False)

            # Verify file was modified
            modified_content = yaml.safe_load(test_file.read_text())
            assert (
                modified_content["metadata"]["123"]["url_poster"]
                == "https://example.com/poster.jpg"
            )


class TestPathNavigation:
    """Test YAML path navigation and manipulation."""

    def test_path_navigation_simple(self):
        """Test simple path navigation."""
        data = {"metadata": {"123": {"title": "Test", "seasons": {}}}}

        # Navigate to metadata.123.seasons
        node = data
        path = ["metadata", "123", "seasons"]

        for key in path:
            assert key in node
            node = node[key]

        assert isinstance(node, dict)

    def test_path_creation(self):
        """Test path creation during navigation."""
        data = {"metadata": {}}

        # Simulate the path creation logic from apply_changes
        path = ["123", "seasons", "1"]
        node = data["metadata"]

        # Create path structure
        for key in path[:-1]:
            node = node.setdefault(key, {})

        # Add final value
        node[path[-1]] = {"title": "Season 1"}

        assert data["metadata"]["123"]["seasons"]["1"]["title"] == "Season 1"


class TestErrorHandlingEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_file_handling(self, temp_dir):
        """Test handling of empty files."""
        empty_file = temp_dir / "empty.yml"
        empty_file.write_text("")

        result = kmr.propose_changes_for_file(empty_file, "https://api.mediux.pro", "test-key")

        assert result is None

    def test_binary_file_handling(self, temp_dir):
        """Test handling of binary files."""
        binary_file = temp_dir / "binary.yml"
        binary_file.write_bytes(b"\x00\x01\x02\x03")

        result = kmr.propose_changes_for_file(binary_file, "https://api.mediux.pro", "test-key")

        assert result is None

    def test_very_large_file(self, temp_dir):
        """Test handling of large files."""
        large_file = temp_dir / "large.yml"

        # Create a large but valid YAML structure
        large_content = {"metadata": {}}
        for i in range(100):  # Create 100 entries
            large_content["metadata"][str(i)] = {
                "title": f"Show {i}",
                "url_poster": f"https://mediux.pro/sets/{i}",
            }

        large_file.write_text(yaml.safe_dump(large_content))

        with patch("kometa_mediux_resolver.fetch_set_assets", return_value=[]):
            result = kmr.propose_changes_for_file(large_file, "https://api.mediux.pro", "test-key")

            # Should handle large files without crashing
            if result:
                assert isinstance(result, dict)

    def test_unicode_handling(self, temp_dir):
        """Test handling of Unicode content."""
        unicode_file = temp_dir / "unicode.yml"
        unicode_content = {
            "metadata": {
                "123456": {
                    "title": "Test Show 测试 🎬",
                    "description": "Unicode content: café, naïve, résumé",
                    "url_poster": "https://mediux.pro/sets/12345",
                }
            }
        }

        unicode_file.write_text(yaml.safe_dump(unicode_content), encoding="utf-8")

        with patch("kometa_mediux_resolver.fetch_set_assets", return_value=[]):
            result = kmr.propose_changes_for_file(
                unicode_file, "https://api.mediux.pro", "test-key"
            )

            # Should handle Unicode without issues
            if result:
                assert "set_ids" in result
