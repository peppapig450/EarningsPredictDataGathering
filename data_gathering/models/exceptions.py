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


# TODO: expand this doc string
class TaskCreationError(Exception):
    """
    Exception raised for errors that occur when creating a subclass of Task for data gathering.
    """

    pass


# TODO: base custom exceptions for Data Gathering and for Data Processing
