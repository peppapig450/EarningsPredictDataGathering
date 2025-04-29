from .project_base_exception import EarningsPredictError


class NoUpcomingEarningsError(EarningsPredictError):
    """
    Exception raised when there is an error retrieving the upcoming earnings list.
    """

    def __init__(
        self,
        message: str | None = None,
        notes: str | None = None,
        include_traceback: bool = False,
    ) -> None:

        super().__init__(message, notes, include_traceback)

class UpcomingEarningCreationError(EarningsPredictError):
    """
    Exception raised when an error occurs while creating an UpcomingEarning instance.
    This is suppressed and just serves to prevent UpcomingEarning.from_dict to return None
    """
    pass