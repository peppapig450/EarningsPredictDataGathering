import argparse
import os
import threading
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import yaml

from data_gathering.models.yaml_objects import CurrentDate
from data_gathering.models.date_range import TimeUnit
from data_gathering.models.exceptions import ConfigLoadError
from data_gathering.utils.file_utils import get_file_path_in_project

from .api_keys import APIKeys


# TODO: look into using pydantic
class Config:
    _instance = None
    _lock = threading.Lock()
    _config: dict[str, Any] = {}
    _api_keys: APIKeys = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                cls._instance = super().__new__(cls)
                cls._instance._config = cls._load_config()
                cls._instance._api_keys = (
                    APIKeys()
                )  # TODO: figure out how to change init of api keys
                cls._instance._parse_args()
        return cls._instance

    @property
    def config(self):
        """Property to easily access the full config dictionary"""
        return self._config

    @property
    def api_keys(self):
        """Property to access the API Keys"""
        return self._api_keys

    @property
    def upcoming_earnings_dates(self):
        upcoming_earnings_config: dict[str, int | TimeUnit | None] = self.config[
            "date_variables"
        ].get("upcoming_earnings", None)

        # Convert the unit strings into TimeUnit enum values
        upcoming_earnings_config["init_unit"] = TimeUnit(
            upcoming_earnings_config["init_unit"]
        )
        upcoming_earnings_config["date_window_unit"] = TimeUnit(
            upcoming_earnings_config["date_window_unit"]
        )

        return upcoming_earnings_config

    @property
    def historical_gathering_dates(self) -> dict[str, str]:
        """Propery to return the to_date of yesterday for HistoricalDataGathering"""
        return {
            "from_date": "1983-01-01",
            "to_date": (date.today() - timedelta(days=1)).strftime("%Y-%m-%d"),
        }

    @classmethod
    def _load_config(cls) -> dict[str, Any]:
        """
        Load configuration data from a YAML file.

        This method attempts to load configuration data from a YAML file specified
        by the environment variable `CONFIG_FILE`. If the environment variable is
        not set, it defaults to `config.yaml`. The method supports a custom YAML
        tag `!TODAY` to dynamically insert the current date.

        Returns:
        --------
        dict
            A dictionary containing the configuration data.

        Raises:
        -------
        ConfigLoadError
            If the configuration file cannot be found or there is an error parsing the YAML file.

        Exceptions Raised:
        ------------------
        - FileNotFoundError: Raised when the specified configuration file is not found.
        - yaml.YAMLError: Raised when there is an error parsing the YAML file, with additional
                          context provided if the error location is known.
        """
        # XXX: more robust path handling ?
        config_data: dict[str, Any] = {}
        # First check for a config file environment variable
        config_file = Path(os.getenv("CONFIG_FILE", "config.yaml"))

        try:
            config_file_path = Config._get_config_file_path(config_file)
            with open(config_file_path, "r", encoding="utf-8") as file:
                # Custom yaml object for today's date
                yaml.SafeLoader.add_constructor("!TODAY", CurrentDate.from_yaml)
                config_data.update(yaml.safe_load(file))
        except FileNotFoundError as exc:
            raise ConfigLoadError(f"Config file '{config_file}' not found.") from exc
        except yaml.YAMLError as exc:
            message = str(exc)
            if hasattr(exc, "problem_mark"):
                mark = exc.problem_mark  # type: ignore
                exc.add_note(
                    f"Error parsing at line {mark.line+1}, column {mark.column+1}."
                )
            raise ConfigLoadError(message) from exc
        return config_data

    @staticmethod
    def _get_config_file_path(config_file: Path):
        config_file = get_file_path_in_project("config", config_file)

        if config_file.exists():
            return config_file.resolve()
        raise ConfigLoadError(
            f"Something went wrong getting the path to {config_file}."
        ) from FileNotFoundError

    def _parse_args(self):
        pass
