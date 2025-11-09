"""Test remaining edge cases and uncovered lines in main module."""

import json
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests

# Import the module to test
import kometa_mediux_resolver as kmr


class TestMainCLIFunction:
    """Test the main CLI function edge cases."""

    @pytest.mark.skip(
        reason="Test is flawed: main() has no required args and will run with defaults, starting heartbeat thread that causes infinite loop"
    )
    def test_main_with_no_args(self, capsys):
        """Test main function with no arguments."""
        with patch("sys.argv", ["kometa_mediux_resolver.py"]):
            with pytest.raises(SystemExit) as exc_info:
                kmr.main()
            assert exc_info.value.code == 2  # argparse error

        captured = capsys.readouterr()
        assert "required" in captured.err.lower() or "error" in captured.err.lower()

    def test_main_with_help(self, capsys):
        """Test main function with help argument."""
        with patch("sys.argv", ["kometa_mediux_resolver.py", "--help"]):
            with pytest.raises(SystemExit) as exc_info:
                kmr.main()
            assert exc_info.value.code == 0

        captured = capsys.readouterr()
        assert "usage:" in captured.out.lower()

    def test_main_with_invalid_config(self, capsys):
        """Test main function with invalid config file."""
        with patch(
            "sys.argv", ["kometa_mediux_resolver.py", "test_input", "--config", "nonexistent.yml"]
        ):
            with pytest.raises(SystemExit):
                kmr.main()

    def test_main_with_missing_input_file(self, capsys):
        """Test main function with missing input file."""
        with patch("sys.argv", ["kometa_mediux_resolver.py", "nonexistent.yml"]):
            with pytest.raises(SystemExit):
                kmr.main()

    @pytest.mark.skip(
        reason="Legacy: main CLI refactored, test needs updating for new arg structure"
    )
    def test_main_successful_run(self):
        """Test successful main function execution (legacy)."""
        pass

    @pytest.mark.skip(
        reason="Legacy: main CLI refactored, test needs updating for new arg structure"
    )
    def test_main_with_dry_run(self):
        """Test main function with dry run option (legacy)."""
        pass


@pytest.mark.skip(reason="setup_logger not in public API")
class TestLoggerConfiguration:
    """Test logger configuration functions (legacy)."""

    def test_setup_logger_default(self):
        """Test default logger setup."""
        logger = kmr.setup_logger()
        assert logger.name == "kometa_mediux_resolver"
        assert logger.level == 20  # INFO level

    def test_setup_logger_debug(self):
        """Test logger setup with debug level."""
        logger = kmr.setup_logger(debug=True)
        assert logger.level == 10  # DEBUG level

    def test_setup_logger_with_log_file(self):
        """Test logger setup with log file."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_log:
            temp_log_path = temp_log.name

        try:
            logger = kmr.setup_logger(log_file=temp_log_path)
            assert len(logger.handlers) >= 1
        finally:
            Path(temp_log_path).unlink()


class TestConfigurationLoading:
    """Test configuration loading edge cases."""

    def test_load_config_missing_file(self):
        """Test loading missing config file."""
        result = kmr.load_config("nonexistent.yml")
        assert result == {}

    def test_load_config_invalid_yaml(self):
        """Test loading invalid YAML config."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as temp_file:
            temp_file.write("invalid: yaml: content: [unclosed")
            temp_file_path = temp_file.name

        try:
            result = kmr.load_config(temp_file_path)
            assert result == {}
        finally:
            Path(temp_file_path).unlink()

    def test_load_config_empty_file(self):
        """Test loading empty config file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as temp_file:
            temp_file.write("")
            temp_file_path = temp_file.name

        try:
            config = kmr.load_config(temp_file_path)
            assert config == {}
        finally:
            Path(temp_file_path).unlink()

    def test_load_config_none_content(self):
        """Test loading config file with null content."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as temp_file:
            temp_file.write("~")  # YAML null
            temp_file_path = temp_file.name

        try:
            config = kmr.load_config(temp_file_path)
            assert config == {}
        finally:
            Path(temp_file_path).unlink()


class TestErrorHandlingEdgeCases:
    """Test error handling in various edge cases."""

    def test_fetch_set_assets_network_timeout(self):
        """Test network timeout handling."""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

            result = kmr.fetch_set_assets("test_set", "https://api.test.com")
            assert result == []

    def test_fetch_set_assets_connection_error(self):
        """Test connection error handling."""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

            result = kmr.fetch_set_assets("test_set", "https://api.test.com")
            assert result == []

    def test_fetch_set_assets_http_error(self):
        """Test HTTP error handling."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.text = "Not Found"
            mock_get.return_value = mock_response

            result = kmr.fetch_set_assets("https://api.test.com", "test_set")
            assert result == []

    def test_fetch_set_assets_json_decode_error(self):
        """Test JSON decode error handling."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "test", 0)
            mock_response.text = "invalid json"
            mock_get.return_value = mock_response

            result = kmr.fetch_set_assets("https://api.test.com", "test_set")
            assert result == []

    def test_fetch_set_assets_unexpected_response_structure(self):
        """Test handling of unexpected response structure."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"unexpected": "structure"}
            mock_get.return_value = mock_response

            result = kmr.fetch_set_assets("https://api.test.com", "test_set")
            assert result == []

    @pytest.mark.skip(
        reason="Outdated: fetch_set_assets_with_scrape now accepts scraper_factory DI"
    )
    def test_fetch_set_assets_with_scrape_scraper_exception(self):
        """Test scraper exception handling in fetch_set_assets_with_scrape (legacy)."""
        pass


@pytest.mark.skip(reason="Legacy: track_activity function removed in favor of touch_activity")
class TestActivityTrackingEdgeCases:
    """Test activity tracking edge cases (legacy)."""

    def test_track_activity_database_error(self):
        """Test activity tracking with database error."""
        with patch("sqlite3.connect") as mock_connect:
            mock_connect.side_effect = sqlite3.Error("Database error")

            # Should not raise exception
            kmr.track_activity("test_set", "test_action", {"test": "data"})

    def test_track_activity_json_serialization_error(self):
        """Test activity tracking with JSON serialization error."""
        with patch("sqlite3.connect") as mock_connect:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_conn

            # Object that can't be JSON serialized
            non_serializable = object()

            # Should handle serialization gracefully
            kmr.track_activity("test_set", "test_action", {"data": non_serializable})
            mock_cursor.execute.assert_called()

    def test_track_activity_connection_close_error(self):
        """Test activity tracking with connection close error."""
        with patch("sqlite3.connect") as mock_connect:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_conn.close.side_effect = Exception("Close failed")
            mock_connect.return_value = mock_conn

            # Should not raise exception
            kmr.track_activity("test_set", "test_action", {"test": "data"})


class TestSonarrIntegrationEdgeCases:
    """Test Sonarr integration edge cases."""

    def test_notify_sonarr_disabled(self):
        """Test Sonarr notification when disabled."""
        config = {"sonarr": {"enabled": False}}

        result = kmr.notify_sonarr("test_path", config)
        assert result is False

    def test_notify_sonarr_missing_config(self):
        """Test Sonarr notification with missing config."""
        config = {}

        result = kmr.notify_sonarr("test_path", config)
        assert result is False

    def test_notify_sonarr_request_exception(self):
        """Test Sonarr notification with request exception."""
        config = {
            "sonarr": {"enabled": True, "url": "http://localhost:8989", "api_key": "test_key"}
        }

        with patch("requests.post") as mock_post:
            mock_post.side_effect = requests.exceptions.RequestException("Connection failed")

            result = kmr.notify_sonarr("test_path", config)
            assert result is False

    def test_notify_sonarr_http_error(self):
        """Test Sonarr notification with HTTP error."""
        config = {
            "sonarr": {"enabled": True, "url": "http://localhost:8989", "api_key": "test_key"}
        }

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
                "400 Bad Request"
            )
            mock_post.return_value = mock_response

            result = kmr.notify_sonarr("test_path", config)
            assert result is False

    def test_notify_sonarr_success(self):
        """Test successful Sonarr notification."""
        config = {
            "sonarr": {"enabled": True, "url": "http://localhost:8989", "api_key": "test_key"}
        }

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            result = kmr.notify_sonarr("test_path", config)
            assert result is True

            # Verify correct API call
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0][0] == "http://localhost:8989/api/v3/command"
            assert "X-Api-Key" in call_args[1]["headers"]
            assert call_args[1]["headers"]["X-Api-Key"] == "test_key"


@pytest.mark.skip(
    reason="Outdated: apply_changes API updated; returns None and applies change sets"
)
class TestApplyChangesEdgeCases:
    """Test apply_changes function edge cases (legacy semantics)."""

    def test_apply_changes_file_write_permission_error(self):
        """Test apply_changes with file write permission error."""
        yaml_data = {"metadata": {"title": "Test"}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml") as temp_file:
            temp_file_path = temp_file.name

            with patch("builtins.open") as mock_open:
                mock_open.side_effect = PermissionError("Permission denied")

                result = kmr.apply_changes(yaml_data, temp_file_path, {})
                assert result is False

    def test_apply_changes_yaml_dump_error(self):
        """Test apply_changes with YAML dump error."""
        # Create an object that can't be YAML serialized
        yaml_data = {"metadata": {"func": lambda x: x}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as temp_file:
            temp_file_path = temp_file.name

        try:
            result = kmr.apply_changes(yaml_data, temp_file_path, {})
            # Should handle YAML serialization error gracefully
            assert result is False
        finally:
            Path(temp_file_path).unlink()

    def test_apply_changes_sonarr_notification_failure(self):
        """Test apply_changes with Sonarr notification failure."""
        yaml_data = {"metadata": {"title": "Test"}}
        config = {
            "sonarr": {"enabled": True, "url": "http://localhost:8989", "api_key": "test_key"}
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as temp_file:
            temp_file_path = temp_file.name

        try:
            with patch("kometa_mediux_resolver.notify_sonarr") as mock_notify:
                mock_notify.return_value = False

                result = kmr.apply_changes(yaml_data, temp_file_path, config)
                # Should still succeed even if Sonarr notification fails
                assert result is True
        finally:
            Path(temp_file_path).unlink()


class TestUtilityFunctionEdgeCases:
    """Test utility function edge cases."""

    def test_construct_asset_url_with_special_characters(self):
        """Test URL construction with special characters."""
        base_url = "https://api.test.com"
        asset_id = "test-id-with-special-chars"

        url = kmr.construct_asset_url(base_url, asset_id)
        assert url == "https://api.test.com/assets/test-id-with-special-chars"

    @pytest.mark.skip(
        reason="Outdated: gather_yaml_metadata_paths now operates on parsed YAML objects"
    )
    def test_gather_yaml_metadata_paths_permission_error(self):
        """Legacy test for directory-based path gathering."""
        pass

    @pytest.mark.skip(
        reason="Outdated: gather_yaml_metadata_paths now operates on parsed YAML objects"
    )
    def test_gather_yaml_metadata_paths_os_error(self):
        """Legacy test for directory-based path gathering."""
        pass

    @pytest.mark.skip(
        reason="Outdated: gather_yaml_metadata_paths now operates on parsed YAML objects"
    )
    def test_gather_yaml_metadata_paths_empty_directory(self):
        """Legacy test for directory-based path gathering."""
        pass

    @pytest.mark.skip(
        reason="Outdated: gather_yaml_metadata_paths now operates on parsed YAML objects"
    )
    def test_gather_yaml_metadata_paths_mixed_files(self):
        """Legacy test for directory-based path gathering."""
        pass


class TestAdvancedPickBestAssetScenarios:
    """Test advanced pick_best_asset scenarios using new API.

    pick_best_asset returns an ordered list of asset IDs.
    """

    def test_pick_best_asset_with_identical_scores(self):
        assets = [
            {"id": "asset1", "type": "poster", "fileSize": 1000},
            {"id": "asset2", "type": "poster", "fileSize": 1000},
            {"id": "asset3", "type": "poster", "fileSize": 1000},
        ]

        result = kmr.pick_best_asset(assets)
        assert result[0] == "asset1"

    def test_pick_best_asset_with_missing_filesize(self):
        assets = [
            {"id": "asset1", "type": "poster"},  # No fileSize
            {"id": "asset2", "type": "poster", "fileSize": 1000},
        ]

        result = kmr.pick_best_asset(assets)
        assert result[:2] == ["asset1", "asset2"]

    def test_pick_best_asset_with_zero_filesize(self):
        assets = [
            {"id": "asset1", "type": "poster", "fileSize": 0},
            {"id": "asset2", "type": "poster", "fileSize": 1000},
        ]

        result = kmr.pick_best_asset(assets)
        # Both are posters; relative order preserved
        assert result[:2] == ["asset1", "asset2"]

    def test_pick_best_asset_with_negative_filesize(self):
        assets = [
            {"id": "asset1", "type": "poster", "fileSize": -100},
            {"id": "asset2", "type": "poster", "fileSize": 1000},
        ]

        result = kmr.pick_best_asset(assets)
        assert result[:2] == ["asset1", "asset2"]

    def test_pick_best_asset_case_insensitive_file_type(self):
        assets = [
            {"id": "asset1", "type": "POSTER", "fileSize": 1000},
            {"id": "asset2", "type": "backdrop", "fileSize": 2000},
        ]

        result = kmr.pick_best_asset(assets)
        # poster priority over backdrop despite case
        assert result[0] == "asset1"
