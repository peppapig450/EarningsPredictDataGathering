import configparser
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Self


# XXX: Set properties for each type of api and if there is more than one return tuple
@dataclass
class APIKeys:
    """
    A class to manage API keys for various financial services.

    Attributes:
        fmp_api_key (str): API key for Financial Modeling Prep.
        finnhub_api_key (str): API key for Finnhub.
        alpha_vantage_api_key (str): API key for Alpha Vantage.
        apca_key_id (str): Key ID for Alpaca API.
        apca_api_secret_key (str): Secret key for Alpaca API.
    """

    fmp_api_key: str
    finnhub_api_key: str
    alpha_vantage_api_key: str
    apca_key_id: str
    apca_api_secret_key: str

    @classmethod
    def from_config_file(cls, config_file_name: str = "api_keys.ini") -> Self:
        """
        Creates an APIKeys instance from a configuration file.

        Args:
            config_file_name (str, optional): Path to the configuration file. If not provided, defaults to "api_keys.ini".

        Returns:
            APIKeys: An instance of the APIKeys class with keys loaded from the config file.
        """
        config_file_path = Path(__file__).resolve().parent / config_file_name

        config = configparser.ConfigParser()
        config.read(config_file_path)

        return cls(
            fmp_api_key=config["API_KEYS"]["fmp-api-key"],
            finnhub_api_key=config["API_KEYS"]["finnhub-api-key"],
            alpha_vantage_api_key=config["API_KEYS"]["alpha-vantage-api-key"],
            apca_key_id=config["API_KEYS"]["apca-key-id"],
            apca_api_secret_key=config["API_KEYS"]["apca-api-secret-key"],
        )

    @classmethod
    def from_environment_variables(cls) -> Self:
        """
        Creates an APIKeys instance from environment variables.

        Returns:
            APIKeys: An instance of the APIKeys class with keys loaded from environment variables.
        """
        environment_variables = {
            "fmp_api_key": os.getenv("FMP_API_KEY", ""),
            "finnhub_api_key": os.getenv("FINNHUB_API_KEY", ""),
            "alpha_vantage_api_key": os.getenv("ALPHA_VANTAGE_API_KEY", ""),
            "apca_key_id": os.getenv("APCA_KEY_ID", ""),
            "apca_api_secret_key": os.getenv("APCA_API_SECRET_KEY", ""),
        }
        # Use dictionary unpacking with type annotations for clarity
        return cls(**environment_variables)
