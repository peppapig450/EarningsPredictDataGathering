import pytest
import yaml
from unittest import mock
from pathlib import Path
from datetime import date

from data_gathering.config.config import Config, ConfigLoadError, CurrentDate


# Helper function to create a temporary file with the given content
@pytest.fixture
def create_temp_file(tmp_path):
    def _create_temp_file(content, filename="config.yaml"):
        file_path = tmp_path / filename
        file_path.write_text(content)
        return file_path

    return _create_temp_file


@pytest.fixture(autouse=True)
def reset_config_instance():
    """
    Fixture to reset the Config instance before and after each test.
    """
    # Before each test
    Config._instance = None
    yield
    # After each test
    Config._instance = None


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


def test_load_full_config(mocker):
    # Mock the file resolution and file reading
    mocker.patch("pathlib.Path.resolve", return_value=Path("config.yaml"))
    yaml_content = """
    date_variables:
      upcoming_earnings:
        init_offset: 1
        date_window: 14
        init_unit: DAYS
        date_window_unit: DAYS
      historical_data:
        from_date: "1983-01-01"
        to_date: !TODAY 'CURRENT_DATE'
    """
    mocker.patch("builtins.open", mocker.mock_open(read_data=yaml_content))

    # Backup the original yaml.safe_load function
    original_safe_load = yaml.safe_load

    # Mock yaml.safe_load to call the actual safe_load with the constructor in place
    def safe_load_with_constructor(*args, **kwargs):
        yaml.SafeLoader.add_constructor("!TODAY", CurrentDate.from_yaml)
        return original_safe_load(*args, **kwargs)

    mocker.patch("yaml.safe_load", side_effect=safe_load_with_constructor)

    # Initialize the Config class to trigger the _load_config method
    config_instance = Config()

    # Access the config to trigger the loading
    config_data = config_instance.config

    expected_date = date.today().strftime("%Y-%m-%d")

    # Verify the config structure
    assert "date_variables" in config_data
    assert "upcoming_earnings" in config_data["date_variables"]
    assert config_data["date_variables"]["upcoming_earnings"]["init_offset"] == 1
    assert config_data["date_variables"]["upcoming_earnings"]["date_window"] == 14
    assert config_data["date_variables"]["upcoming_earnings"]["init_unit"] == "DAYS"
    assert (
        config_data["date_variables"]["upcoming_earnings"]["date_window_unit"] == "DAYS"
    )
    assert "historical_data" in config_data["date_variables"]
    assert config_data["date_variables"]["historical_data"]["from_date"] == "1983-01-01"
    assert (
        config_data["date_variables"]["historical_data"]["to_date"].current_date
        == expected_date
    )


# Test the replacement of the !TODAY tag with the current date
def test_today_tag_replacement(mocker):
    yaml_input = """
    to_date: !TODAY 'CURRENT_DATE'
    """
    expected_date = date.today().strftime("%Y-%m-%d")

    # Register the custom constructor manually in the test environment
    yaml.SafeLoader.add_constructor("!TODAY", CurrentDate.from_yaml)

    # Load the YAML input using the safe_load method
    data = yaml.safe_load(yaml_input)

    # Verify that the placeholder is replaced with the current date
    assert data["to_date"].current_date == expected_date


# Test the behavior when the config file is not found
def test_load_config_file_not_found(mocker):
    mock_resolve = mocker.patch("pathlib.Path.resolve", side_effect=FileNotFoundError)

    with pytest.raises(ConfigLoadError, match="Config file 'config.yaml' not found."):
        Config()


# Test the behavior when the YAML file has an error
def test_load_config_yaml_error(mocker):
    mock_resolve = mocker.patch(
        "pathlib.Path.resolve", return_value=Path("config.yaml")
    )
    mock_open = mocker.patch(
        "builtins.open", mocker.mock_open(read_data=": invalid yaml")
    )
    mock_safe_load = mocker.patch(
        "yaml.safe_load", side_effect=yaml.YAMLError("Error parsing YAML")
    )

    with pytest.raises(ConfigLoadError, match="Error parsing YAML"):
        Config()
