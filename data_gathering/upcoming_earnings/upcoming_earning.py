import logging
from dataclasses import InitVar, dataclass, fields
from datetime import datetime
from typing import Any

from ..exceptions import UpcomingEarningCreationError
from ..models import DateTuple

logger = logging.getLogger(__name__)

type StringOrOther = str | Any
type CsvRowData = dict[StringOrOther, StringOrOther]


# XXX: Maybe use InitVar for the initial report_date and fiscal_year_date with kw args or something
@dataclass
class UpcomingEarning:
    symbol: str
    company_name: str
    report_date: str | DateTuple
    fiscal_year_end: str | DateTuple
    currency: str
    date_format: InitVar[str] = "%Y-%m-%d"

    @classmethod
    def from_dict(cls, data: CsvRowData):
        # Map expected dictionary keys to class attributes
        try:
            mapped_data: dict[str, str] = {
                "symbol": data["symbol"],
                "company_name": data["name"],
                "report_date": data["reportDate"],
                "fiscal_year_end": data["fiscalDateEnding"],
                "currency": data["currency"],
            }
            # Check if all required keys are present before creating the instance
            if not all(key.name in mapped_data for key in fields(cls)):
                missing_keys = [key.name for key in fields(cls) if key.name not in mapped_data]
                raise ValueError(f"Missing required keys: {', '.join(missing_keys)}")
            
            return cls(**mapped_data)
        except KeyError as exc:
            logger.warning(
                f"Missing key in data from the CSV returned: {exc.args[0]}",
                exc_info=True,
            )
            raise UpcomingEarningCreationError # avoid returning None
        except ValueError as exc:
            logging.warning(
                f"Value error while creating UpcomingEarning instance: {exc}",
                exc_info=True
            )
            raise UpcomingEarningCreationError # avoid returning None

    def _create_date_tuple(self, date_value: str | DateTuple, date_format: str):
        if isinstance(date_value, str):
            date_obj = datetime.strptime(date_value, date_format)
            date_str = date_value
        else:
            date_obj = date_value.date
            date_str = date_value.date_str
        return DateTuple(date_obj, date_str)

    def __post_init__(self, date_format: str):
        self.report_date = self._create_date_tuple(self.report_date, date_format)
        self.fiscal_year_end = self._create_date_tuple(
            self.fiscal_year_end, date_format
        )

    def __str__(self):
        return self.symbol

    