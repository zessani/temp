from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.model.schema.resume.link import ResumeWebLink
from app.model.schema.resume.location import ResumeLocation
from app.model.schema.resume.time import ResumeTimeMonthYear


class ResumeExperienceType(str, Enum):
    WORK = "work"
    VOLUNTEER = "volunteer"
    PROJECT = "project"
    OTHER = "other"


class ResumeExperienceItem(BaseModel):
    type: ResumeExperienceType
    organization: Optional[str] = None
    role: Optional[str] = None
    location: Optional[ResumeLocation] = None
    start_date: Optional[ResumeTimeMonthYear] = None
    end_date: Optional[ResumeTimeMonthYear] = None
    paragraphs: list[str] = Field(default_factory=list)
    links: list[ResumeWebLink] = Field(default_factory=list)
