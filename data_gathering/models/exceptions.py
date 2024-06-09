# Custom exceptions


def requires_message(warning_class):
    """
    Decorator to enforce message attribute in warning classes.
    """
    orig_init = warning_class.__init__

    def wrapper_init(self, message):
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
        __init__(self, message="Error occured while retrieving upcoming earnings list. parsed_data empty."):
            Initializes the NoUpcomingEarningsError with a specific error message.
            Raises a RuntimeError chained from this exception.
    """

    def __init__(
        self,
        message="Error occured while retrieving upcoming earnings list. parsed_data empty.",
    ):
        """
        Constructs the NoUpcomingEarningsError with the given error message.

        Parameters:
            message (str): Explanation of the error. Defaults to "Error occured while retrieving
                           upcoming earnings list. parsed_data empty."

        Raises:
            RuntimeError: An exception that is raised from this NoUpcomingEarningsError.
        """
        super().__init__(message)
        raise RuntimeError from self
