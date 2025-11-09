"""Test the main kometa_mediux_resolver module."""

import json
import sqlite3
from unittest.mock import Mock, patch

import pytest
import yaml

# Import the module under test
import kometa_mediux_resolver as kmr


class TestSetIdExtraction:
    """Test set ID extraction from text."""

    def test_find_set_ids_in_text_single(self):
        """Test finding a single set ID."""
        text = "url_poster: https://mediux.pro/sets/12345"
        result = kmr.find_set_ids_in_text(text)
        assert result == ["12345"]

    def test_find_set_ids_in_text_multiple(self):
        """Test finding multiple set IDs."""
        text = """
        url_poster: https://mediux.pro/sets/12345
        url_backdrop: https://mediux.pro/sets/67890
        """
        result = kmr.find_set_ids_in_text(text)
        assert set(result) == {"12345", "67890"}

    def test_find_set_ids_in_text_none(self):
        """Test finding no set IDs."""
        text = "url_poster: https://example.com/poster.jpg"
        result = kmr.find_set_ids_in_text(text)
        assert result == []

    def test_find_set_ids_in_text_duplicates(self):
        """Test deduplication of set IDs."""
        text = """
        url_poster: https://mediux.pro/sets/12345
        url_title_card: https://mediux.pro/sets/12345
        """
        result = kmr.find_set_ids_in_text(text)
        assert result == ["12345"]


class TestAssetUrl:
    """Test asset URL construction."""

    def test_construct_asset_url(self):
        """Test constructing asset URL."""
        api_base = "https://api.mediux.pro"
        asset_id = "test-asset-123"
        result = kmr.construct_asset_url(api_base, asset_id)
        assert result == "https://api.mediux.pro/assets/test-asset-123"

    def test_construct_asset_url_trailing_slash(self):
        """Test with trailing slash in API base."""
        api_base = "https://api.mediux.pro/"
        asset_id = "test-asset-123"
        result = kmr.construct_asset_url(api_base, asset_id)
        assert result == "https://api.mediux.pro/assets/test-asset-123"


class TestProbeUrl:
    """Test URL probing functionality."""

    @patch("kometa_mediux_resolver.requests.get")
    def test_probe_url_success(self, mock_get):
        """Test successful URL probe."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "image/jpeg"}
        mock_response.text = "OK"
        mock_get.return_value = mock_response

        result = kmr.probe_url("https://example.com/test.jpg")

        assert result["status"] == 200
        assert result["body"] == "OK"
        assert result["url"] == "https://example.com/test.jpg"

    @patch("kometa_mediux_resolver.requests.get")
    def test_probe_url_failure(self, mock_get):
        """Test failed URL probe."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        result = kmr.probe_url("https://example.com/missing.jpg")

        assert result["status"] == 404
        assert result["body"] == "Not Found"

    @patch("kometa_mediux_resolver.requests.get")
    def test_probe_url_exception(self, mock_get):
        """Test URL probe with exception."""
        mock_get.side_effect = Exception("Connection error")

        result = kmr.probe_url("https://example.com/test.jpg")

        assert result["status"] is None
        assert "Connection error" in result["error"]

    @patch("kometa_mediux_resolver.requests.get")
    def test_probe_url_with_api_key(self, mock_get):
        """Test URL probe with API key."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        kmr.probe_url(
            "https://example.com/test.jpg", api_key="test-key"
        )  # pragma: allowlist secret

        mock_get.assert_called_once()
        call_kwargs = mock_get.call_args[1]
        assert (
            call_kwargs["headers"]["Authorization"] == "Bearer test-key"
        )  # pragma: allowlist secret


class TestFetchSetAssets:
    """Test fetching assets for a set."""

    @patch("kometa_mediux_resolver.requests.get")
    def test_fetch_set_assets_success(self, mock_get):
        """Test successful asset fetching."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "assets": [{"id": "asset1", "type": "poster"}, {"id": "asset2", "type": "backdrop"}]
        }
        mock_get.return_value = mock_response

        result = kmr.fetch_set_assets("https://api.mediux.pro", "12345")

        assert len(result) == 2
        assert result[0]["id"] == "asset1"
        assert result[1]["id"] == "asset2"

    @patch("kometa_mediux_resolver.requests.get")
    def test_fetch_set_assets_api_failure(self, mock_get):
        """Test asset fetching with API failure."""
        mock_get.side_effect = Exception("API Error")

        result = kmr.fetch_set_assets("https://api.mediux.pro", "12345")

        assert result == []

    @patch("kometa_mediux_resolver.requests.get")
    def test_fetch_set_assets_with_api_key(self, mock_get):
        """Test asset fetching with API key."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"assets": []}
        mock_get.return_value = mock_response

        kmr.fetch_set_assets("https://api.mediux.pro", "12345", api_key="test-key")

        mock_get.assert_called()
        call_kwargs = mock_get.call_args[1]
        assert call_kwargs["headers"]["Authorization"] == "Bearer test-key"


class TestCollectNodes:
    """Test YAML node collection."""

    @pytest.mark.skip(reason="collect_nodes function not implemented yet")
    def test_collect_nodes_simple(self, sample_yaml_content):
        """Test collecting nodes from simple YAML."""
        metadata = sample_yaml_content["metadata"]
        result = list(kmr.collect_nodes(metadata))

        # Should find nodes at various levels
        assert len(result) > 0

        # Check that we get path tuples and node dictionaries
        for path, node in result:
            assert isinstance(path, tuple)
            assert isinstance(node, dict)

    @pytest.mark.skip(reason="collect_nodes function not implemented yet")
    def test_collect_nodes_with_existing_url_poster(self):
        """Test that nodes with existing url_poster are excluded."""
        metadata = {
            "123456": {
                "title": "Test",
                "url_poster": "https://example.com/existing.jpg",
                "seasons": {"1": {"title": "Season 1"}},
            }
        }

        result = list(kmr.collect_nodes(metadata))

        # Should find season node but not the root node (has url_poster)
        paths = [path for path, _ in result]
        assert any("seasons" in str(path) for path in paths)


class TestCacheOperations:
    """Test cache operations."""

    def test_init_cache(self, temp_dir):
        """Test cache initialization."""
        cache_path = temp_dir / "test_cache.db"
        conn = kmr.init_cache(str(cache_path))

        assert isinstance(conn, sqlite3.Connection)

        # Check that table was created
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='probe_cache'")
        result = cursor.fetchone()
        assert result is not None

        conn.close()

    def test_cache_operations(self, temp_dir):
        """Test cache set and get operations."""
        cache_path = temp_dir / "test_cache.db"
        conn = kmr.init_cache(str(cache_path))

        # Test setting cache
        url = "https://example.com/test.jpg"
        status = 200
        body = "OK"
        kmr.set_cached_probe(conn, url, status, body)

        # Test getting cache
        cached = kmr.get_cached_probe(conn, url, 3600)
        assert cached is not None
        assert cached["status"] == status
        assert cached["body"] == body

        conn.close()

    @patch("kometa_mediux_resolver.time.time")
    def test_cache_expiry(self, mock_time, temp_dir):
        """Test cache TTL expiry."""
        cache_path = temp_dir / "test_cache.db"
        conn = kmr.init_cache(str(cache_path))

        # Mock time for consistent testing
        mock_time.return_value = 1000.0

        # Set cache
        url = "https://example.com/test.jpg"
        kmr.set_cached_probe(conn, url, 200, "OK")

        # Advance time and check with TTL = 0 (immediate expiry)
        mock_time.return_value = 1001.0
        cached = kmr.get_cached_probe(conn, url, 0)
        assert cached is None

        conn.close()


class TestMainFunction:
    """Test main function and argument parsing."""

    @patch("kometa_mediux_resolver.scan_root")
    @patch("kometa_mediux_resolver.apply_changes")
    def test_main_basic_execution(self, mock_apply, mock_scan, temp_dir, monkeypatch):
        """Test basic main function execution."""
        # Change to temp directory
        monkeypatch.chdir(temp_dir)

        # Create required files
        (temp_dir / "config").mkdir()
        (temp_dir / "config" / "config.yml").write_text("logging: true")

        mock_scan.return_value = []

        # Test dry run with no --apply flag
        result = kmr.main(["--root", str(temp_dir)])

        assert result == 0
        mock_scan.assert_called_once()
        # apply_changes should NOT be called in dry-run mode
        mock_apply.assert_not_called()

    def test_main_probe_asset(self, temp_dir, monkeypatch):
        """Test main function with probe-asset option."""
        monkeypatch.chdir(temp_dir)

        with patch("kometa_mediux_resolver.probe_url") as mock_probe:
            mock_probe.return_value = {"status": 200, "body": "OK"}

            result = kmr.main(
                [
                    "--probe-asset",
                    "https://example.com/test.jpg",
                    "--output",
                    str(temp_dir / "probe.json"),
                ]
            )

            assert result == 0
            mock_probe.assert_called_once()

            # Check output file
            output_file = temp_dir / "probe.json"
            assert output_file.exists()
            data = json.loads(output_file.read_text())
            assert data["probe_asset"] == "https://example.com/test.jpg"

    def test_main_probe_set(self, temp_dir, monkeypatch):
        """Test main function with probe-set option."""
        monkeypatch.chdir(temp_dir)

        with patch("kometa_mediux_resolver.fetch_set_assets") as mock_fetch:
            mock_fetch.return_value = [{"id": "test", "type": "poster"}]

            result = kmr.main(["--probe-set", "12345", "--output", str(temp_dir / "probe.json")])

            assert result == 0
            mock_fetch.assert_called_once()


class TestProposeChanges:
    """Test change proposal functionality."""

    @patch("kometa_mediux_resolver.fetch_set_assets")
    @patch("kometa_mediux_resolver.probe_url")
    def test_propose_changes_for_file(self, mock_probe, mock_fetch, yaml_with_mediux_urls):
        """Test proposing changes for a file."""
        # Mock successful asset fetch and probe
        mock_fetch.return_value = [{"id": "test-asset", "type": "poster"}]
        mock_probe.return_value = {"status": 200, "body": "OK"}

        result = kmr.propose_changes_for_file(
            yaml_with_mediux_urls, "https://api.mediux.pro", "test-api-key"
        )

        assert result is not None
        assert result["file"] == str(yaml_with_mediux_urls)
        assert "set_ids" in result
        assert "changes" in result

    def test_propose_changes_no_mediux_urls(self, sample_yaml_file):
        """Test proposing changes for file without MediUX URLs."""
        result = kmr.propose_changes_for_file(
            sample_yaml_file, "https://api.mediux.pro", "test-api-key"
        )

        assert result is None


class TestApplyChanges:
    """Test applying changes to files."""

    def test_apply_changes_dry_run(self, temp_dir):
        """Test dry run (apply=False)."""
        # Create test file
        test_file = temp_dir / "test.yml"
        content = {"metadata": {"123": {"title": "Test"}}}
        test_file.write_text(yaml.safe_dump(content))

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

        # Should not modify file in dry run
        original_content = test_file.read_text()
        kmr.apply_changes(changes, apply=False)
        assert test_file.read_text() == original_content

    def test_apply_changes_with_backup(self, temp_dir):
        """Test applying changes with backup."""
        # Create test file
        test_file = temp_dir / "test.yml"
        content = {"metadata": {"123": {"title": "Test"}}}
        test_file.write_text(yaml.safe_dump(content))

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

        kmr.apply_changes(changes, apply=True, create_backup=True)

        # Check that backup was created
        backup_files = list(temp_dir.glob("test.yml.bak.*"))
        assert len(backup_files) == 1

        # Check that file was modified
        modified_content = yaml.safe_load(test_file.read_text())
        assert modified_content["metadata"]["123"]["url_poster"] == "https://example.com/poster.jpg"


@pytest.mark.integration
class TestIntegration:
    """Integration tests."""

    def test_full_workflow(self, temp_dir, monkeypatch):
        """Test complete workflow from scan to apply."""
        monkeypatch.chdir(temp_dir)

        # Create directory structure
        (temp_dir / "config").mkdir()
        config_content = {"logging": True, "apply": False, "api_base": "https://api.mediux.pro"}
        (temp_dir / "config" / "config.yml").write_text(yaml.safe_dump(config_content))

        # Create test YAML with MediUX URL
        test_content = {
            "metadata": {
                "123456": {
                    "title": "Test Show",
                    "url_poster": "https://mediux.pro/sets/12345",
                    "seasons": {"1": {"title": "Season 1"}},
                }
            }
        }
        test_file = temp_dir / "test.yml"
        test_file.write_text(yaml.safe_dump(test_content))

        with (
            patch("kometa_mediux_resolver.fetch_set_assets") as mock_fetch,
            patch("kometa_mediux_resolver.probe_url") as mock_probe,
        ):
            mock_fetch.return_value = [{"id": "test-asset", "type": "poster"}]
            mock_probe.return_value = {"status": 200, "body": "OK"}

            result = kmr.main(["--root", str(temp_dir), "--output", str(temp_dir / "output.json")])

            assert result == 0

            # Check output file was created
            output_file = temp_dir / "output.json"
            assert output_file.exists()

            # Verify output content
            output_data = json.loads(output_file.read_text())
            assert isinstance(output_data, list)


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_invalid_yaml_file(self, temp_dir):
        """Test handling of invalid YAML file."""
        invalid_file = temp_dir / "invalid.yml"
        invalid_file.write_text("invalid: yaml: content: [")

        result = kmr.propose_changes_for_file(invalid_file, "https://api.mediux.pro", "test-key")

        assert result is None

    def test_missing_file(self, temp_dir):
        """Test handling of missing file."""
        missing_file = temp_dir / "missing.yml"

        # Should raise FileNotFoundError for missing files
        with pytest.raises(FileNotFoundError):
            kmr.propose_changes_for_file(missing_file, "https://api.mediux.pro", "test-key")

    @patch("kometa_mediux_resolver.Path.exists")
    def test_missing_root_directory(self, mock_exists, temp_dir):
        """Test handling of missing root directory."""
        mock_exists.return_value = False

        result = kmr.main(["--root", str(temp_dir / "missing")])

        assert result == 2  # Error exit code
