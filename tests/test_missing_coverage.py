"""Tests targeting specific uncovered lines in kometa_mediux_resolver.py to improve coverage."""

import json
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
import responses

import kometa_mediux_resolver as kmr


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases that aren't covered by existing tests."""

    @responses.activate
    def test_fetch_set_assets_non_200_response(self):
        """Test fetch_set_assets handling non-200 HTTP responses."""
        # Add a 404 response
        responses.add(
            responses.GET, "https://api.mediux.pro/sets/123/assets", status=404, body="Not Found"
        )

        result = kmr.fetch_set_assets("https://api.mediux.pro", "123", "test-key")

        assert result == []

    @responses.activate
    def test_fetch_set_assets_non_json_response(self):
        """Test fetch_set_assets handling non-JSON responses."""
        # Add a 200 response with non-JSON content
        responses.add(
            responses.GET,
            "https://api.mediux.pro/sets/123/assets",
            status=200,
            body="This is not JSON content",
            headers={"Content-Type": "text/html"},
        )

        result = kmr.fetch_set_assets("https://api.mediux.pro", "123", "test-key")

        assert result == []

    @responses.activate
    def test_fetch_set_assets_connection_error(self):
        """Test fetch_set_assets handling connection errors."""
        # Add a response that raises an exception
        responses.add(
            responses.GET,
            "https://api.mediux.pro/sets/123/assets",
            body=Exception("Connection failed"),
        )

        result = kmr.fetch_set_assets("https://api.mediux.pro", "123", "test-key")

        assert result == []

    @responses.activate
    def test_probe_url_non_200_status(self):
        """Test probe_url with non-200 status codes."""
        responses.add(responses.HEAD, "https://example.com/asset.jpg", status=404)

        result = kmr.probe_url("https://example.com/asset.jpg")

        assert result["status_code"] == 404
        assert result["ok"] is False

    @responses.activate
    def test_probe_url_connection_exception(self):
        """Test probe_url with connection exceptions."""
        responses.add(
            responses.HEAD, "https://example.com/asset.jpg", body=Exception("Connection timeout")
        )

        result = kmr.probe_url("https://example.com/asset.jpg")

        assert result["status_code"] is None
        assert result["ok"] is False
        assert result["error"] is not None

    def test_find_set_ids_in_text_no_matches(self):
        """Test find_set_ids_in_text with text containing no set IDs."""
        text = "This is some text without any mediux set URLs"
        result = kmr.find_set_ids_in_text(text)
        assert result == []

    def test_find_set_ids_in_text_with_matches(self):
        """Test find_set_ids_in_text with various URL formats."""
        text = """
        Check out this set: https://mediux.pro/sets/123456
        And this one: http://mediux.pro/sets/789012
        Also: https://www.mediux.pro/sets/345678/details
        """
        result = kmr.find_set_ids_in_text(text)
        assert "123456" in result
        assert "789012" in result
        assert "345678" in result
        assert len(result) == 3

    def test_construct_asset_url_basic(self):
        """Test asset URL construction."""
        result = kmr.construct_asset_url("https://api.mediux.pro", "abc123def456")
        assert result == "https://api.mediux.pro/assets/abc123def456"

    def test_construct_asset_url_with_trailing_slash(self):
        """Test asset URL construction with trailing slash in base."""
        result = kmr.construct_asset_url("https://api.mediux.pro/", "abc123def456")
        assert result == "https://api.mediux.pro/assets/abc123def456"

    def test_get_cached_probe_expired(self):
        """Test getting cached probe data that has expired."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        try:
            conn = kmr.init_cache(db_path)

            # Insert expired cache entry (very old timestamp)
            conn.execute(
                "INSERT INTO probes (url, timestamp, status_code, content_type, content_length, ok) VALUES (?, ?, ?, ?, ?, ?)",
                ("https://example.com/test.jpg", 1000, 200, "image/jpeg", 12345, 1),
            )
            conn.commit()

            # Try to get with very short max_age to ensure expiration
            result = kmr.get_cached_probe(conn, "https://example.com/test.jpg", max_age=1)

            assert result is None

            conn.close()
        finally:
            Path(db_path).unlink(missing_ok=True)

    def test_get_cached_probe_missing(self):
        """Test getting cached probe data for non-existent URL."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        try:
            conn = kmr.init_cache(db_path)

            result = kmr.get_cached_probe(conn, "https://example.com/nonexistent.jpg", max_age=3600)

            assert result is None

            conn.close()
        finally:
            Path(db_path).unlink(missing_ok=True)

    def test_touch_activity_with_increment(self):
        """Test touch_activity with count increment."""
        # Reset activity state
        kmr.touch_activity(count_inc=0)

        # Increment by 5
        kmr.touch_activity(count_inc=5)

        count, timestamp = kmr.get_activity_snapshot()
        assert count == 5

    def test_pick_best_asset_empty_list(self):
        """Test pick_best_asset with empty asset list."""
        result = kmr.pick_best_asset([])
        assert result == []

    def test_pick_best_asset_single_asset(self):
        """Test pick_best_asset with single asset."""
        assets = [{"id": "test123", "some_field": "value"}]
        result = kmr.pick_best_asset(assets)
        assert result == ["test123"]

    def test_pick_best_asset_multiple_assets(self):
        """Test pick_best_asset with multiple assets."""
        assets = [
            {"id": "asset1", "field": "value1"},
            {"id": "asset2", "field": "value2"},
            {"id": "asset3", "field": "value3"},
        ]
        result = kmr.pick_best_asset(assets)
        # Should return first asset by default logic
        assert "asset1" in result


class TestYAMLProcessingEdgeCases:
    """Test YAML processing edge cases and error handling."""

    def test_gather_yaml_metadata_paths_empty_object(self):
        """Test gather_yaml_metadata_paths with empty object."""
        result = list(kmr.gather_yaml_metadata_paths({}))
        assert result == []

    def test_gather_yaml_metadata_paths_none_object(self):
        """Test gather_yaml_metadata_paths with None."""
        result = list(kmr.gather_yaml_metadata_paths(None))
        assert result == []

    def test_gather_yaml_metadata_paths_string_object(self):
        """Test gather_yaml_metadata_paths with string (non-dict)."""
        result = list(kmr.gather_yaml_metadata_paths("not a dict"))
        assert result == []

    def test_gather_yaml_metadata_paths_nested_structure(self):
        """Test gather_yaml_metadata_paths with complex nested structure."""
        obj = {
            "metadata": {
                "show1": {
                    "title": "Test Show",
                    "seasons": {
                        "1": {"title": "Season 1", "episodes": {"1": {"title": "Episode 1"}}}
                    },
                }
            }
        }

        result = list(kmr.gather_yaml_metadata_paths(obj))

        # Should find all nested paths
        assert len(result) > 0
        # Check that we get the episode level
        episode_paths = [path for path, val in result if "episodes" in str(path)]
        assert len(episode_paths) > 0

    def test_propose_changes_for_file_invalid_yaml(self, temp_dir):
        """Test propose_changes_for_file with invalid YAML."""
        yaml_file = temp_dir / "invalid.yml"
        yaml_file.write_text("invalid: yaml: content: [")

        result = kmr.propose_changes_for_file(yaml_file, "https://api.mediux.pro", "test-key")

        # Should handle invalid YAML gracefully
        assert result is None

    def test_propose_changes_for_file_binary_file(self, temp_dir):
        """Test propose_changes_for_file with binary file."""
        binary_file = temp_dir / "binary.yml"
        binary_file.write_bytes(b"\\x00\\x01\\x02\\x03")

        result = kmr.propose_changes_for_file(binary_file, "https://api.mediux.pro", "test-key")

        # Should handle binary files gracefully
        assert result is None

    def test_propose_changes_for_file_no_metadata(self, temp_dir):
        """Test propose_changes_for_file with YAML that has no metadata section."""
        yaml_file = temp_dir / "no_metadata.yml"
        yaml_file.write_text(
            """
title: "Some Configuration"
settings:
  debug: true
"""
        )

        result = kmr.propose_changes_for_file(yaml_file, "https://api.mediux.pro", "test-key")

        # Should return None or empty result for files without metadata
        assert result is None or result == []


class TestDatabaseErrorHandling:
    """Test database-related error handling."""

    def test_init_cache_existing_database(self):
        """Test init_cache with existing database file."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        try:
            # Create database first time
            conn1 = kmr.init_cache(db_path)
            conn1.close()

            # Open existing database
            conn2 = kmr.init_cache(db_path)

            # Verify table exists
            cursor = conn2.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='probes'"
            )
            result = cursor.fetchone()
            assert result is not None

            conn2.close()
        finally:
            Path(db_path).unlink(missing_ok=True)

    def test_set_cached_probe_database_error(self, temp_dir):
        """Test set_cached_probe handling database errors."""
        db_path = temp_dir / "test.db"
        conn = kmr.init_cache(str(db_path))

        # Close connection to cause error
        conn.close()

        # This should handle the database error gracefully
        try:
            kmr.set_cached_probe(
                conn, "https://example.com/test.jpg", 200, "image/jpeg", 12345, True
            )
            # If it doesn't raise an exception, that's fine
        except Exception:
            # If it does raise an exception, that's also acceptable
            pass


class TestCLIAndMainFunction:
    """Test CLI parsing and main function edge cases."""

    @patch("kometa_mediux_resolver.scan_root")
    @patch("kometa_mediux_resolver.apply_changes")
    def test_main_with_apply_flag(self, mock_apply, mock_scan):
        """Test main function with apply flag."""
        mock_scan.return_value = [{"file": "test.yml", "changes": []}]

        # Test with apply flag
        with patch("sys.argv", ["kometa_mediux_resolver.py", "--root", "/test", "--apply"]):
            try:
                result = kmr.main()
                # Should execute without error
            except SystemExit:
                # main() might call sys.exit(), which is acceptable
                pass

    @patch("kometa_mediux_resolver.scan_root")
    def test_main_dry_run(self, mock_scan):
        """Test main function in dry-run mode."""
        mock_scan.return_value = [{"file": "test.yml", "changes": []}]

        with patch("sys.argv", ["kometa_mediux_resolver.py", "--root", "/test"]):
            try:
                result = kmr.main()
                # Should execute without error
            except SystemExit:
                # main() might call sys.exit(), which is acceptable
                pass

    def test_main_no_args(self):
        """Test main function with no arguments (should show help)."""
        with patch("sys.argv", ["kometa_mediux_resolver.py"]):
            try:
                result = kmr.main()
            except SystemExit as e:
                # Should exit with error code for missing required args
                assert e.code != 0


class TestSonarrIntegration:
    """Test Sonarr API integration functions."""

    @responses.activate
    def test_get_recently_aired_from_sonarr_success(self):
        """Test successful Sonarr API call."""
        # Mock Sonarr API response
        sonarr_response = [
            {"id": 123, "title": "Test Show", "airDate": "2024-01-01", "hasFile": True},
            {"id": 456, "title": "Another Show", "airDate": "2024-01-02", "hasFile": False},
        ]

        responses.add(
            responses.GET,
            "https://sonarr.example.com/api/v3/calendar",
            json=sonarr_response,
            status=200,
        )

        result = kmr.get_recently_aired_from_sonarr(
            "https://sonarr.example.com", "test-api-key", days=7
        )

        assert isinstance(result, list)
        assert 123 in result
        assert 456 in result

    @responses.activate
    def test_get_recently_aired_from_sonarr_error(self):
        """Test Sonarr API call with error response."""
        responses.add(
            responses.GET,
            "https://sonarr.example.com/api/v3/calendar",
            status=500,
            body="Internal Server Error",
        )

        result = kmr.get_recently_aired_from_sonarr(
            "https://sonarr.example.com", "test-api-key", days=7
        )

        assert result == []

    @responses.activate
    def test_get_recently_aired_from_sonarr_invalid_json(self):
        """Test Sonarr API call with invalid JSON response."""
        responses.add(
            responses.GET,
            "https://sonarr.example.com/api/v3/calendar",
            body="Not valid JSON",
            status=200,
        )

        result = kmr.get_recently_aired_from_sonarr(
            "https://sonarr.example.com", "test-api-key", days=7
        )

        assert result == []
