"""Test asset picking and utility functions."""
import re
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

import kometa_mediux_resolver as kmr


class TestPickBestAsset:
    """Test pick_best_asset function."""

    def test_pick_best_asset_empty_list(self):
        """Test with empty asset list."""
        result = kmr.pick_best_asset([])
        assert result == []

    def test_pick_best_asset_no_ids(self):
        """Test with assets that have no IDs."""
        assets = [{"name": "test.jpg", "type": "poster"}, {"name": "test2.jpg"}]
        result = kmr.pick_best_asset(assets)
        assert result == []

    def test_pick_best_asset_priority_order(self):
        """Test that assets are returned in priority order."""
        assets = [
            {"id": "backdrop-1", "type": "backdrop", "name": "bg.jpg"},
            {"id": "title-1", "type": "title_card", "name": "title.jpg"},
            {"id": "poster-1", "type": "poster", "name": "poster.jpg"},
            {"id": "title-2", "type": "title-card", "name": "title2.jpg"},
        ]
        result = kmr.pick_best_asset(assets)

        # title_card should come first, then poster, then backdrop
        assert result[0] in ["title-1", "title-2"]  # Both title cards
        assert "poster-1" in result
        assert "backdrop-1" in result
        assert result.index("poster-1") < result.index("backdrop-1")

    def test_pick_best_asset_name_matching(self):
        """Test priority matching by name when type is missing."""
        assets = [
            {"id": "asset-1", "name": "backdrop image.jpg"},
            {"id": "asset-2", "name": "titlecard special.jpg"},
            {"id": "asset-3", "name": "poster main.jpg"},
        ]
        result = kmr.pick_best_asset(assets)

        # Should prioritize by name content
        title_idx = next(i for i, aid in enumerate(result) if aid == "asset-2")
        poster_idx = next(i for i, aid in enumerate(result) if aid == "asset-3")
        backdrop_idx = next(i for i, aid in enumerate(result) if aid == "asset-1")

        assert title_idx < poster_idx < backdrop_idx

    def test_pick_best_asset_unknown_types_last(self):
        """Test that unknown types come after priority types."""
        assets = [
            {"id": "unknown-1", "type": "unknown", "name": "unknown.jpg"},
            {"id": "poster-1", "type": "poster", "name": "poster.jpg"},
            {"id": "weird-1", "type": "weird_type", "name": "weird.jpg"},
        ]
        result = kmr.pick_best_asset(assets)

        assert result[0] == "poster-1"  # Poster should be first
        assert "unknown-1" in result[1:]  # Unknown types should be after
        assert "weird-1" in result[1:]

    def test_pick_best_asset_fallback_to_uuid_search(self):
        """Test fallback to searching raw data for UUIDs when no IDs found."""
        assets = [
            {
                "name": "test.jpg",
                "raw": {
                    "metadata": {"uuid": "12345678-1234-1234-1234-123456789abc"},
                    "other": "data",
                },
            },
            {
                "name": "test2.jpg",
                "raw": {"info": {"id_value": "abcdef12-3456-7890-abcd-ef1234567890"}},
            },
        ]
        result = kmr.pick_best_asset(assets)

        assert "12345678-1234-1234-1234-123456789abc" in result
        assert "abcdef12-3456-7890-abcd-ef1234567890" in result

    def test_pick_best_asset_case_insensitive_matching(self):
        """Test that type/name matching is case insensitive."""
        assets = [
            {"id": "asset-1", "type": "POSTER", "name": "Main POSTER.jpg"},
            {"id": "asset-2", "type": "Title_Card", "name": "TITLECARD.jpg"},
        ]
        result = kmr.pick_best_asset(assets)

        # Title card should come first despite case differences
        assert result[0] == "asset-2"
        assert result[1] == "asset-1"


class TestConstructAssetUrl:
    """Test construct_asset_url function."""

    def test_construct_asset_url_basic(self):
        """Test basic URL construction."""
        result = kmr.construct_asset_url("https://api.example.com", "asset-123")
        assert result == "https://api.example.com/assets/asset-123"

    def test_construct_asset_url_trailing_slash(self):
        """Test URL construction with trailing slash on base."""
        result = kmr.construct_asset_url("https://api.example.com/", "asset-123")
        assert result == "https://api.example.com/assets/asset-123"

    def test_construct_asset_url_complex_base(self):
        """Test URL construction with complex base URL."""
        result = kmr.construct_asset_url("https://api.example.com/v1/mediux", "asset-123")
        assert result == "https://api.example.com/v1/mediux/assets/asset-123"


class TestGatherYamlMetadataPaths:
    """Test gather_yaml_metadata_paths function."""

    def test_gather_simple_dict(self):
        """Test gathering paths from simple dictionary."""
        obj = {"key1": "value1", "key2": {"nested": "value"}}
        result = kmr.gather_yaml_metadata_paths(obj)

        assert len(result) == 2
        # Root object and nested dict
        paths = [path for path, _ in result]
        assert () in paths  # Root
        assert ("key2",) in paths  # Nested

    def test_gather_nested_dicts(self):
        """Test gathering paths from deeply nested dictionaries."""
        obj = {
            "metadata": {"123456": {"title": "Test Show", "seasons": {"1": {"title": "Season 1"}}}}
        }
        result = kmr.gather_yaml_metadata_paths(obj)

        paths = [path for path, _ in result]
        assert () in paths
        assert ("metadata",) in paths
        assert ("metadata", "123456") in paths
        assert ("metadata", "123456", "seasons") in paths
        assert ("metadata", "123456", "seasons", "1") in paths

    def test_gather_with_lists_skipped(self):
        """Test that lists are skipped in path gathering."""
        obj = {
            "dict_key": {"nested": "value"},
            "list_key": [{"item1": "value"}, {"item2": "value"}],
        }
        result = kmr.gather_yaml_metadata_paths(obj)

        paths = [path for path, _ in result]
        assert () in paths
        assert ("dict_key",) in paths
        # List items should not be included
        assert ("list_key", 0) not in paths

    def test_gather_non_dict_input(self):
        """Test gathering from non-dict input."""
        result = kmr.gather_yaml_metadata_paths("not a dict")
        assert result == []

        result = kmr.gather_yaml_metadata_paths(["list", "items"])
        assert result == []

        result = kmr.gather_yaml_metadata_paths(None)
        assert result == []


class TestActivityTracking:
    """Test activity tracking functions."""

    def test_touch_activity_basic(self):
        """Test basic activity touching."""
        # Reset activity
        kmr.touch_activity(0)
        initial_count, initial_time = kmr.get_activity_snapshot()

        # Touch activity with increment
        kmr.touch_activity(5)
        new_count, new_time = kmr.get_activity_snapshot()

        assert new_count == initial_count + 5
        assert new_time >= initial_time

    def test_touch_activity_no_increment(self):
        """Test activity touch without count increment."""
        initial_count, initial_time = kmr.get_activity_snapshot()

        kmr.touch_activity(0)
        new_count, new_time = kmr.get_activity_snapshot()

        assert new_count == initial_count  # No change in count
        assert new_time >= initial_time  # Time should be updated

    def test_get_activity_snapshot(self):
        """Test getting activity snapshot."""
        count, timestamp = kmr.get_activity_snapshot()

        assert isinstance(count, int)
        assert isinstance(timestamp, float)
        assert count >= 0
        assert timestamp > 0


class TestFindSetIdsInText:
    """Test find_set_ids_in_text function."""

    def test_find_set_ids_basic(self):
        """Test finding basic set IDs in text."""
        text = "url_poster: https://mediux.pro/sets/12345"
        result = kmr.find_set_ids_in_text(text)
        assert "12345" in result

    def test_find_set_ids_multiple(self):
        """Test finding multiple set IDs."""
        text = """
        url_poster: https://mediux.pro/sets/12345
        url_background: https://mediux.pro/sets/67890
        """
        result = kmr.find_set_ids_in_text(text)
        assert "12345" in result
        assert "67890" in result

    def test_find_set_ids_with_trailing_slash(self):
        """Test finding set IDs with trailing slash."""
        text = "url_poster: https://mediux.pro/sets/12345/"
        result = kmr.find_set_ids_in_text(text)
        assert "12345" in result

    def test_find_set_ids_none_found(self):
        """Test when no set IDs are found."""
        text = "url_poster: https://example.com/image.jpg"
        result = kmr.find_set_ids_in_text(text)
        assert result == []

    def test_find_set_ids_duplicates(self):
        """Test that duplicate set IDs are not repeated."""
        text = """
        url_poster: https://mediux.pro/sets/12345
        url_background: https://mediux.pro/sets/12345
        """
        result = kmr.find_set_ids_in_text(text)
        assert result == ["12345"]


class TestSonarrIntegration:
    """Test Sonarr integration functions."""

    @patch("kometa_mediux_resolver.requests.get")
    def test_get_recently_aired_success(self, mock_get):
        """Test successful Sonarr calendar query."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"series": {"tvdbId": 12345}},
            {"series": {"tvdbId": 67890}},
            {"series": {"tvdbId": "12345"}},  # Duplicate, should be deduplicated
            {"series": {}},  # No tvdbId
            {"other": "data"},  # No series
        ]
        mock_get.return_value = mock_response

        result = kmr.get_recently_aired_from_sonarr("http://sonarr.local:8989", "api-key", 7)

        assert 12345 in result
        assert 67890 in result
        assert len(result) == 2  # Duplicates removed

    @patch("kometa_mediux_resolver.requests.get")
    def test_get_recently_aired_no_url(self, mock_get):
        """Test with empty Sonarr URL."""
        result = kmr.get_recently_aired_from_sonarr("", "api-key", 7)
        assert result == []
        mock_get.assert_not_called()

    @patch("kometa_mediux_resolver.requests.get")
    def test_get_recently_aired_http_error(self, mock_get):
        """Test with HTTP error response."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = kmr.get_recently_aired_from_sonarr("http://sonarr.local:8989", "api-key", 7)
        assert result == []

    @patch("kometa_mediux_resolver.requests.get")
    def test_get_recently_aired_connection_error(self, mock_get):
        """Test with connection error."""
        mock_get.side_effect = Exception("Connection failed")

        result = kmr.get_recently_aired_from_sonarr("http://sonarr.local:8989", "api-key", 7)
        assert result == []

    @patch("kometa_mediux_resolver.requests.get")
    def test_get_recently_aired_with_api_key(self, mock_get):
        """Test that API key is properly included in headers."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        kmr.get_recently_aired_from_sonarr("http://sonarr.local:8989", "test-key", 7)

        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]["headers"]["X-Api-Key"] == "test-key"

    @patch("kometa_mediux_resolver.requests.get")
    def test_get_recently_aired_without_api_key(self, mock_get):
        """Test without API key."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        kmr.get_recently_aired_from_sonarr("http://sonarr.local:8989", None, 7)

        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]["headers"] == {}


class TestApplyChangesAdvanced:
    """Test advanced apply_changes scenarios."""

    def test_apply_changes_with_schema_validation_failure(self, temp_dir):
        """Test apply_changes with schema validation failure."""
        # Create a test file
        test_file = temp_dir / "test.yml"
        test_file.write_text("metadata:\n  123456:\n    title: Test Show")

        # Mock schema loading and validation
        mock_schema = {"type": "object", "required": ["invalid_field"]}

        changes = [
            {
                "file": str(test_file),
                "changes": [
                    {"path": ["123456"], "add": {"url_poster": "https://example.com/poster.jpg"}}
                ],
            }
        ]

        with patch("builtins.open", create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = '{"type": "object"}'
            with patch("kometa_mediux_resolver.Path") as mock_path:
                mock_path(__file__).resolve.return_value.parent = temp_dir
                schema_path = temp_dir / "kometa_metadata_schema.json"
                schema_path.write_text('{"type": "object", "required": ["invalid_field"]}')
                mock_path.return_value = schema_path
                mock_path.return_value.exists.return_value = True

                with patch("kometa_mediux_resolver._validate") as mock_validate:
                    mock_validate.side_effect = Exception("Validation failed")

                    # Should not raise exception, just log warning and skip
                    kmr.apply_changes(changes, apply=True)

        # File should not have been modified due to validation failure
        content = test_file.read_text()
        assert "url_poster" not in content

    def test_apply_changes_backup_failure_recovery(self, temp_dir):
        """Test apply_changes with backup failure and recovery."""
        test_file = temp_dir / "test.yml"
        test_file.write_text("metadata:\n  123456:\n    title: Test Show")

        changes = [
            {
                "file": str(test_file),
                "changes": [
                    {"path": ["123456"], "add": {"url_poster": "https://example.com/poster.jpg"}}
                ],
            }
        ]

        # Mock Path.rename to fail (backup failure)
        with patch.object(Path, "rename", side_effect=Exception("Backup failed")):
            # Should continue and attempt write anyway
            kmr.apply_changes(changes, apply=True, create_backup=True)

        # File should still be modified despite backup failure
        content = test_file.read_text()
        assert "url_poster" in content

    def test_apply_changes_write_failure_with_restore(self, temp_dir):
        """Test apply_changes with write failure and backup restore."""
        test_file = temp_dir / "test.yml"
        original_content = "metadata:\n  123456:\n    title: Test Show"
        test_file.write_text(original_content)

        changes = [
            {
                "file": str(test_file),
                "changes": [
                    {"path": ["123456"], "add": {"url_poster": "https://example.com/poster.jpg"}}
                ],
            }
        ]

        # Track if backup was created and restored
        backup_created = False
        original_rename = Path.rename
        original_write_text = Path.write_text

        def mock_rename(self, target):
            nonlocal backup_created
            if str(target).endswith(".bak."):
                backup_created = True
            return original_rename(self, target)

        def mock_write_text(self, data, **kwargs):
            if "url_poster" in data:
                raise Exception("Write failed")
            return original_write_text(self, data, **kwargs)

        with patch.object(Path, "rename", side_effect=mock_rename):
            with patch.object(Path, "write_text", side_effect=mock_write_text):
                kmr.apply_changes(changes, apply=True, create_backup=True)

        # Original content should be restored
        assert test_file.read_text() == original_content

    def test_apply_changes_missing_file(self, temp_dir):
        """Test apply_changes with missing file."""
        missing_file = temp_dir / "missing.yml"

        changes = [
            {
                "file": str(missing_file),
                "changes": [
                    {"path": ["123456"], "add": {"url_poster": "https://example.com/poster.jpg"}}
                ],
            }
        ]

        # Should not raise exception, just log warning and continue
        kmr.apply_changes(changes, apply=True)

    def test_apply_changes_invalid_yaml_parse(self, temp_dir):
        """Test apply_changes with invalid YAML file."""
        test_file = temp_dir / "invalid.yml"
        test_file.write_text("invalid: yaml: content: [")

        changes = [
            {
                "file": str(test_file),
                "changes": [
                    {"path": ["123456"], "add": {"url_poster": "https://example.com/poster.jpg"}}
                ],
            }
        ]

        # Should not raise exception, just log warning and continue
        kmr.apply_changes(changes, apply=True)

    def test_apply_changes_no_metadata(self, temp_dir):
        """Test apply_changes with file that has no metadata."""
        test_file = temp_dir / "no_metadata.yml"
        test_file.write_text("config:\n  setting: value")

        changes = [
            {
                "file": str(test_file),
                "changes": [
                    {"path": ["123456"], "add": {"url_poster": "https://example.com/poster.jpg"}}
                ],
            }
        ]

        # Should not raise exception, just log warning and continue
        kmr.apply_changes(changes, apply=True)

    def test_apply_changes_probe_failure_with_require_ok(self, temp_dir):
        """Test apply_changes with probe failure when require_probe_ok=True."""
        test_file = temp_dir / "test.yml"
        test_file.write_text("metadata:\n  123456:\n    title: Test Show")

        changes = [
            {
                "file": str(test_file),
                "changes": [
                    {
                        "path": ["123456"],
                        "add": {"url_poster": "https://example.com/poster.jpg"},
                        "probe": {"status": 404},  # Failed probe
                    }
                ],
            }
        ]

        kmr.apply_changes(changes, apply=True, require_probe_ok=True)

        # Change should not be applied due to failed probe
        content = test_file.read_text()
        assert "url_poster" not in content
