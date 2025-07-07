# TODO: Find a better time library that needs only month and year.
from typing import Optional

from pydantic import BaseModel


class ResumeTimeMonthYear(BaseModel):
    year: Optional[int] = None

    # Ranges from 1 to 12, where 1 is January, 12 is December.
    month: Optional[int] = None
