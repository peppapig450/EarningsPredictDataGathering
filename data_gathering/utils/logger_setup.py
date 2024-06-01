import logging
import logging.config
import tomllib as toml
import os


def setup_logging(
    default_path: str = "data_gathering/config/logging.toml",
    default_level=logging.INFO,
    env_key="LOG_CFG",
):
    """Setup logging configuration"""
    # Determine the absolute path to the logging configuration file
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    path = os.path.join(base_dir, default_path)

    # Check if environment variable overrides the path
    if value := os.getenv(env_key, None):
        path = value

    # Load and apply logging configuration
    try:
        if os.path.exists(path):
            with open(path, "rb", encoding="utf-8") as config_file:
                config = toml.load(config_file)
            logging.config.dictConfig(config)
        else:
            logging.basicConfig(level=default_level)
            logging.warning(
                f"Logging configuration file not found at {path}. Using basic configuration."
            )
    except (FileNotFoundError, toml.TOMLDecodeError) as e:
        logging.basicConfig(level=default_level)
        logging.error(
            f"Error: {e} loading logging configuration from {path}. Using basic configuration.",
            exc_info=True,
        )
    except Exception as e:
        logging.basicConfig(level=default_level)
        logging.error(
            f"Unexpected error: {e} loading loading configuration file from {path}. Using basic configuration.",
            exc_info=True,
        )
