from beanie import Document
from pydantic import Field

from app.model.schema.resume.education.course import ResumeEducationCourse
from app.model.schema.resume.education.item import ResumeEducationItem
from app.model.schema.resume.experience import ResumeExperienceItem
from app.model.schema.resume.info import ResumePersonalInfo
from app.model.schema.resume.skills import ResumeSkillsList


class Resume(Document):
    personal_info: ResumePersonalInfo
    education_items: list[ResumeEducationItem] = Field(default_factory=list)

    # Include skills here that are not associated with any particular education, work experience, etc.
    skills: list[ResumeSkillsList] = Field(default_factory=list)

    # Include coursework in this list that are not associated with any particular university.
    relevant_coursework: list[ResumeEducationCourse] = Field(default_factory=list)

    experience_items: list[ResumeExperienceItem] = Field(default_factory=list)

    # Include additional written paragraphs that are not associated with any other information field.
    paragraphs: list[str] = Field(default_factory=list)
