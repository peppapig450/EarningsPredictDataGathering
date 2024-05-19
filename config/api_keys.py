import os
import configparser


class APIKeys:
    def __init__(self, fmp_api_key, apca_key_id, apca_api_secret_key):
        self.fmp_api_key = fmp_api_key
        self.apca_key_id = apca_key_id
        self.apca_api_secret_key = apca_api_secret_key

    @classmethod
    def from_config_file(cls, config_file_path=None):
        config = configparser.ConfigParser()

        if config_file_path:
            config.read(config_file_path)
        else:
            config.read("api_keys.ini")
        return cls(
            fmp_api_key=config["API_KEYS"]["FMP_API_KEY"],
            apca_key_id=config["API_KEYS"]["APCA_KEY_ID"],
            apca_api_secret_key=config["API_KEYS"]["APCA_API_SECRET_KEY"],
        )

    @classmethod
    def from_environment_variables(cls):
        return cls(
            fmp_api_key=os.getenv("FMP_API_KEY"),
            apca_key_id=os.getenv("APCA_KEY_ID"),
            apca_api_secret_key=os.getenv("APCA_API_SECRET_KEY"),
        )

    def __getattribute__(self, name: str):
        if name in ("fmp_api_key", "apca_key_id", "apca_api_secret_key"):
            return getattr(self, name)
        raise AttributeError(f"'APIKeys' object has no attribute '{name}'")