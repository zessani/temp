from pydantic import BaseModel

from app.model.schema.resume.together import Resume


class ApiResumeParseRequest(BaseModel):
    pass


class ApiResumeParseResponse(BaseModel):
    resume: Resume
