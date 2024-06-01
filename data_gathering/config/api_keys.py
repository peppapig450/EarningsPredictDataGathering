import configparser
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Tuple, Optional
from enum import Enum, auto


class APIService(Enum):
    FMP = auto()  # Finacial Modeling Prep
    FINNHUB = auto()  # Finnhub
    ALPHA_VANTAGE = auto()  # Alpha Vantage
    ALPACA = auto()  # Alpaca


type ApiKey = str | Tuple[str, str]
type APIKeysDict = Dict[APIService, ApiKey]


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

    _keys: APIKeysDict = field(default_factory=dict)

    def __init__(
        self, load_from: str = "config", config_file: Optional[str] = "api_keys.ini"
    ) -> None:
        """
        Initializes an APIKeys instance.

        Args:
            load_from (str, optional): Specifies where to load API keys from. Can be 'env' for environment variables or 'config' for a configuration file. Defaults to 'config'.
            config_file (str, optional): Path to the configuration file. Defaults to 'api_keys.ini'.
        """
        if load_from == "env":
            self._keys = self._load_keys_from_environment_variables()
        elif load_from == "config":
            self._keys = self._load_keys_from_config_file(config_file)
        else:
            raise ValueError(
                "Invalid value for 'load_from'. Must be 'env' or 'config'."
            )

    def _load_keys_from_config_file(
        self, config_file_name: str = "api_keys.ini"
    ) -> APIKeysDict:
        """
        Creates an APIKeys instance from a configuration file.

        Args:
            config_file_name (str, optional): Path to the configuration file. If not provided, defaults to "api_keys.ini".

        Returns:
            APIKeysDict: A dictionary containing API keys loaded from the configuration file.
        """
        config_file_path = Path(__file__).resolve().parent / config_file_name

        if not config_file_path.exists():
            raise FileNotFoundError(
                "Configuration file '${config_file_name}' not found."
            )

        config = configparser.ConfigParser()
        config.read(config_file_path)

        keys = {
            APIService.FMP: config["API_KEYS"]["fmp-api-key"],
            APIService.FINNHUB: config["API_KEYS"]["finnhub-api-key"],
            APIService.ALPHA_VANTAGE: config["API_KEYS"]["alpha-vantage-api-key"],
            APIService.ALPACA: (
                config["API_KEYS"]["apca-key-id"],
                config["API_KEYS"]["apca-api-secret-key"],
            ),
        }

        return keys

    def _load_keys_from_environment_variables(
        self,
    ) -> APIKeysDict:
        """
        Loads API keys from environment variables.

        Returns:
            APIKeysDict: A dictionary containing API keys loaded from environment variables.
        """
        keys = {
            APIService.FMP: os.getenv("FMP_API_KEY", ""),
            APIService.FINNHUB: os.getenv("FINNHUB_API_KEY", ""),
            APIService.ALPHA_VANTAGE: os.getenv("ALPHA_VANTAGE_API_KEY", ""),
            APIService.ALPACA: (
                os.getenv("APCA_KEY_ID", ""),
                os.getenv("APCA_API_SECRET_KEY", ""),
            ),
        }

        return keys

    def get_key(self, service: APIService) -> ApiKey:
        """
        Retrieve the API key(s) for a specific service.

        Args:
            service (APIService): The service for which to retrieve the key.

        Returns:
            ApiKey: The API key or tuple containing Key ID and Secret Key if it exists, otherwise an empty string.
        """
        return self._keys.get(service, "")

    def get_keys(self, *services: APIService) -> APIKeysDict:
        """
        Retrieve the API keys for multiple services.

        Args:
            services (APIService): The services for which to retrieve the keys.

        Returns:
            Dict[APIService, APiKey: A dictionary containing the API keys for each requested service.
        """
        return {service: self.get_key(service) for service in services}

    def all_keys(self) -> APIKeysDict:
        """
        Retrieve all stored API keys.

        Returns:
            Dict[APIService, ApiKey]: A dictionary containing all API keys.
        """
        return self._keys
