from typing import Optional

from pydantic import BaseModel, Field

from app.model.schema.resume.link import ResumeWebLinkPlatform
from app.model.schema.resume.location import ResumeLocation


class ResumePersonalInfo(BaseModel):
    name: str
    home_address: Optional[ResumeLocation] = None

    # TODO: find library for validation of phone numbers.
    phone_number: Optional[str] = None

    # TODO: find library for validation of emails.
    email: Optional[str] = None
    links: list[ResumeWebLinkPlatform] = Field(default_factory=list)
