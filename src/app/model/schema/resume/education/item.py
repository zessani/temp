from typing import Optional, Union

from pydantic import BaseModel, Field

from app.model.schema.resume.education.course import ResumeEducationCourse
from app.model.schema.resume.education.degree import ResumeEducationDegree
from app.model.schema.resume.location import ResumeLocation
from app.model.schema.resume.skills import ResumeSkillsList
from app.model.schema.resume.time import ResumeTimeMonthYear


class ResumeEducationItem(BaseModel):
    school_name: str
    degree: Union[ResumeEducationDegree]
    gpa: Optional[float] = None
    start_date: Optional[ResumeTimeMonthYear] = None
    end_date: Optional[ResumeTimeMonthYear] = None
    location: ResumeLocation
    relevant_coursework: list[ResumeEducationCourse] = Field(default_factory=list)
    skills: list[ResumeSkillsList] = Field(default_factory=list)
