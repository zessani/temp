from typing import Optional

from pydantic import BaseModel


class ResumeEducationCourseCode(BaseModel):
    prefix: str
    number: str


class ResumeEducationCourse(BaseModel):
    code: Optional[ResumeEducationCourseCode] = None
    name: Optional[str] = None
