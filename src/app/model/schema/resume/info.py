from typing import Optional

from pydantic import BaseModel, Field

from app.model.schema.resume.link import ResumeWebLinkPlatform
from app.model.schema.resume.location import ResumeLocation


class ResumePersonalInfo(BaseModel):
    name: str
    home_address: Optional[ResumeLocation] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    links: list[ResumeWebLinkPlatform] = Field(default_factory=list)
