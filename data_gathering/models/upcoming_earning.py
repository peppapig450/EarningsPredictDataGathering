from datetime import date

from pydantic import BaseModel, Field, ValidationError


class UpcomingEarning(BaseModel):
    symbol: str = Field(pattern=r"^[^\.]+\w*$")
    date: date
