# Custom exceptions
# TODO: https://stackoverflow.com/questions/1319615/proper-way-to-declare-custom-exceptions-in-modern-python#answer-60465422
class MissingMessageError(Exception):
    """
    Exception raised when a warning class is instantiated without a message argument.
    """

    pass


def requires_message(warning_class):
    """
    Decorator to enforce message attribute in warning classes.
    """
    orig_init = warning_class.__init__

    def wrapper_init(self, message):
        if not message:
            raise MissingMessageError(
                "Custom Exception classes require a message argument."
            )
        orig_init(self, message)

    wrapper_init.__qualname__ = orig_init.__qualname__
    warning_class.__init__ = wrapper_init
    return warning_class


@requires_message
class NoUpcomingEarningsError(Exception):
    """
    Exception raised when there is an error retrieving the upcoming earnings list.

    Attributes:
        message (str): Explanation of the error. Defaults to a standard error message indicating
                       that the parsed data is empty.

    Methods:
        __init__(self, message):
            Initializes the NoUpcomingEarningsError with a specific error message.
            Raises a RuntimeError chained from this exception.
    """

    def __init__(
        self,
        message=None,
    ):
        """
        Constructs the NoUpcomingEarningsError with the given error message.

        Parameters:
            message (str): Explanation of the error. Defaults to "Error occured while retrieving
                           upcoming earnings list. parsed_data empty."

        Raises:
            RuntimeError: An exception that is raised from this NoUpcomingEarningsError.
        """
        if message is None:
            self.message = "Error occured while retrieving upcoming earnings list. parsed_data empty."
        else:
            self.message = message

        super().__init__(message)
        raise RuntimeError from self


class ConfigLoadError(Exception):
    """
    Exception raised for errors occurring during the loading of configuration files.

    This exception is specifically raised in response to:
    - FileNotFoundError: When the configuration file cannot be found.
    - yaml.YAMLError: When there is an error parsing the YAML configuration file.

    Attributes:
    -----------
    message : str
        The error message describing the cause of the exception.
    """

    pass


# TODO: expand this doc string
class TaskCreationError(Exception):
    """
    Exception raised for errors that occur when creating a subclass of Task for data gathering.
    """

    pass
