from typing import Optional

from pydantic import BaseModel


# TODO: find library for validation detailed location.
class ResumeLocation(BaseModel):
    city: Optional[str] = None

    # TODO: Need a better, more general name (i.e. countries that do not have states, like provinces)
    state: Optional[str] = None

    zip_code: Optional[str] = None
