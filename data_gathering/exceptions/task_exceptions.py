from .project_base_exception import EarningsPredictError


class TaskCreationError(EarningsPredictError):
    """
    Exception raised for exceptions that occur when creating a Task.
    """

    def __init__(
        self,
        message: str | None = None,
        notes: str | None = None,
        include_traceback: bool = False,
    ) -> None:
        super().__init__(message, notes, include_traceback)
