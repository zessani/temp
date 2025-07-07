from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ResumeEducationDegreeType(str, Enum):
    HIGH_SCHOOL = "high_school"
    GED = "ged"
    BACHELORS = "bachelors"
    MASTERS = "masters"
    PHD = "phd"
    OTHER_COLLEGE_LEVEL = "other_college_level"
    OTHER_HIGH_SCHOOL_LEVEL = "other_high_school_level"
    OTHER = "other"


class ResumeEducationDegree(BaseModel):
    study: Optional[str] = None
    type: ResumeEducationDegreeType
