from typing import Optional

from pydantic import BaseModel


class ResumeLocation(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
