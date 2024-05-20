import os
import pytest

from data_gathering.config.api_keys import APIKeys


@pytest.fixture
def config_file(tmp_path):
    config_file_path = tmp_path / "test_config.ini"

    config_content = """
    [API_KEYS]
    fmp-api-key = test_fmp_api_key
    finnhub-api-key = test_finnhub_api_key
    alpha-vantage-api-key = test_alpha_vantage_api_key
    apca-key-id = test_apca_key_id
    apca-api-secret-key = test_apca_api_secret_key
    """

    with open(config_file_path, "w") as f:
        f.write(config_content)

    return config_file_path


def test_from_config_file(config_file):
    api_keys = APIKeys.from_config_file(config_file)
    assert api_keys.fmp_api_key == "test_fmp_api_key"
    assert api_keys.finnhub_api_key == "test_finnhub_api_key"
    assert api_keys.alpha_vantage_api_key == "test_alpha_vantage_api_key"
    assert api_keys.apca_key_id == "test_apca_key_id"
    assert api_keys.apca_api_secret_key == "test_apca_api_secret_key"


@pytest.mark.parametrize(
    "env_vars",
    [
        {
            "FMP_API_KEY": "test_fmp_api_key",
            "FINNHUB_API_KEY": "test_finnhub_api_key",
            "ALPHA_VANTAGE_API_KEY": "test_alpha_vantage_api_key",
            "APCA_KEY_ID": "test_apca_key_id",
            "APCA_API_SECRET_KEY": "test_apca_api_secret_key",
        }
    ],
)
def test_from_environment_variables(env_vars, monkeypatch):
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    api_keys = APIKeys.from_environment_variables()
    assert api_keys.fmp_api_key == "test_fmp_api_key"
    assert api_keys.finnhub_api_key == "test_finnhub_api_key"
    assert api_keys.alpha_vantage_api_key == "test_alpha_vantage_api_key"
    assert api_keys.apca_key_id == "test_apca_key_id"
    assert api_keys.apca_api_secret_key == "test_apca_api_secret_key"
