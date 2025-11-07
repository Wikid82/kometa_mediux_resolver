"""Test configuration and fixtures."""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest
import yaml

# Add project root to Python path so modules can be imported
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_yaml_content():
    """Sample YAML content for testing."""
    return {
        "metadata": {
            "123456": {
                "title": "Sample Show",
                "seasons": {
                    "1": {"episodes": {"1": {"title": "Episode 1"}, "2": {"title": "Episode 2"}}}
                },
            }
        }
    }


@pytest.fixture
def sample_yaml_file(temp_dir, sample_yaml_content):
    """Create a sample YAML file for testing."""
    yaml_file = temp_dir / "sample.yml"
    yaml_file.write_text(yaml.safe_dump(sample_yaml_content))
    return yaml_file


@pytest.fixture
def yaml_with_mediux_urls(temp_dir):
    """Create a YAML file with MediUX URLs."""
    content = {
        "metadata": {
            "123456": {
                "title": "Test Show",
                "url_poster": "https://mediux.pro/sets/12345",
                "seasons": {
                    "1": {
                        "url_poster": "https://mediux.pro/sets/12345",
                        "episodes": {"1": {"title": "Episode 1"}},
                    }
                },
            }
        }
    }
    yaml_file = temp_dir / "mediux_test.yml"
    yaml_file.write_text(yaml.safe_dump(content))
    return yaml_file


@pytest.fixture
def config_file(temp_dir):
    """Create a sample config file."""
    config_content = {
        "logging": True,
        "root": ".",
        "apply": False,
        "backup": True,
        "log_file": "config/logs/test.log",
        "api_base": "https://api.mediux.pro",
        "cache_db": "config/test_cache.db",
        "cache_ttl_seconds": 3600,
    }
    config_dir = temp_dir / "config"
    config_dir.mkdir()
    config_file = config_dir / "config.yml"
    config_file.write_text(yaml.safe_dump(config_content))
    return config_file


@pytest.fixture
def mock_response():
    """Mock HTTP response."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "assets": [
            {"id": "asset-1", "type": "poster", "url": "https://api.mediux.pro/assets/asset-1"}
        ]
    }
    response.headers = {"Content-Type": "application/json"}
    return response


@pytest.fixture
def mock_assets_response():
    """Mock MediUX assets API response."""
    return [
        {
            "id": "test-asset-1",
            "type": "poster",
            "url": "https://api.mediux.pro/assets/test-asset-1",
            "title": "Test Poster 1",
        },
        {
            "id": "test-asset-2",
            "type": "backdrop",
            "url": "https://api.mediux.pro/assets/test-asset-2",
            "title": "Test Backdrop 1",
        },
    ]


@pytest.fixture
def central_mapping_file(temp_dir):
    """Create a central mapping file."""
    mapping_content = {
        "set": {"12345": "metadata.123456.seasons"},
        "tvdb": {"123456": "metadata.123456.seasons"},
        "filename": {"sample.yml": "metadata.123456.seasons"},
    }
    central_dir = temp_dir / "central_mapping"
    central_dir.mkdir()
    mapping_file = central_dir / "write_path_map.yml"
    mapping_file.write_text(yaml.safe_dump(mapping_content))
    return mapping_file


@pytest.fixture
def metadata_schema():
    """Sample JSON schema for metadata validation."""
    return {
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
                            "seasons": {"type": "object"},
                        },
                    }
                },
            }
        },
    }


@pytest.fixture
def schema_file(temp_dir, metadata_schema):
    """Create a JSON schema file."""
    schema_file = temp_dir / "kometa_metadata_schema.json"
    schema_file.write_text(json.dumps(metadata_schema, indent=2))
    return schema_file
