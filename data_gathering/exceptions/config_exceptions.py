from .project_base_exception import EarningsPredictError


class ConfigLoadError(EarningsPredictError):
    """
    Exception raised for errors occurring during the loading of configuration files.

    This exception is specifically raised in response to:
    - FileNotFoundError: When the configuration file cannot be found.
    - yaml.YAMLError: When there is an error parsing the YAML configuration file.
    """

    def __init__(
        self,
        message: str = "Error occured while loading the config.",
        notes: str | None = None,
        include_traceback: bool = False,
    ) -> None:
        super().__init__(message, notes, include_traceback)
