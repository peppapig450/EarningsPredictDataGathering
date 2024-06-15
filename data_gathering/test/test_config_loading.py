import pytest
import yaml
from unittest import mock
from pathlib import Path
from datetime import date
from data_gathering.models.exceptions import ConfigLoadError
from data_gathering.models.yaml_objects import CurrentDate
from data_gathering.config.config import Config


# Helper function to create a temporary file with the given content
@pytest.fixture
def create_temp_file(tmp_path):
    def _create_temp_file(content, filename="config.yaml"):
        file_path = tmp_path / filename
        file_path.write_text(content)
        return file_path

    return _create_temp_file


def test_load_valid_config(create_temp_file, monkeypatch):
    # Create a valid YAML config file
    yaml_content = """
    database_url: "your_database_url"
    api_key: "your_api_key"
    """

    config_file = create_temp_file(yaml_content)

    # Mock the environment variable to point to the temp config file
    monkeypatch.setenv("CONFIG_FILE", str(config_file))

    # Create a config instance and check if the data is loaded correctly
    config = Config().config
    assert config["database_url"] == "your_database_url"
    assert config["api_key"] == "your_api_key"


def test_missing_config_file(monkeypatch):
    # Mock the environment variable to point to a non-existing file
    monkeypatch.setenv("CONFIG_FILE", "non_existing_config.yaml")

    with pytest.raises(ConfigLoadError) as exc_info:
        Config().config
    assert "Config file 'non_existing_config.yaml' not found." in str(exc_info.value)


def test_invalid_yaml_content(create_temp_file, monkeypatch):
    # Create an invalid YAML config file
    invalid_yaml_content = """
    database_url: "your_database_url"
    api_key: "your_api_key
    """  # Missing closing quote for api_key
    config_file = create_temp_file(invalid_yaml_content)

    # Mock the environment variable to point to the temp config file
    monkeypatch.setenv("CONFIG_FILE", str(config_file))

    # Ensure ConfigLoaderError is raised
    with pytest.raises(ConfigLoadError) as exc_info:
        Config().config
    assert "while parsing a quoted scalar" in str(exc_info.value)
