# Base custom exceptions for the project
# TODO: https://stackoverflow.com/questions/1319615/proper-way-to-declare-custom-exceptions-in-modern-python#answer-60465422
# XXX: use of 'atexit' here for cleanup is also possible, so is 'warnings'.
import traceback


class EarningsPredictError(Exception):
    """Base class for exceptions for the Earnings Predict Data Gathering project"""

    def __init__(
        self,
        message: str | None = None,
        notes: str | None = None,
        include_traceback: bool = False,
    ) -> None:
        super().__init__(message)
        if notes is not None:
            self.add_note(notes)
        self.traceback = traceback.format_exc() if include_traceback else None
