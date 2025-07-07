from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ResumeSkillsType(str, Enum):
    TECHNICAL = "technical"  # More formal name for "hard skills."
    TRANSFERABLE = "transferable"  # More formal name for "soft skills."
    OTHER = "other"


class ResumeSkillsList(BaseModel):
    type: ResumeSkillsType
    category: Optional[str] = None
    keywords: list[str] = Field(default_factory=list)
